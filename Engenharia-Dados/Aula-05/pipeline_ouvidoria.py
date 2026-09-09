import csv
import hashlib
import json
import os
from pathlib import Path

import psycopg2
from psycopg2.extras import Json

BASE_DIR = Path(__file__).parent
SERVICOS_PATH = BASE_DIR / "servicos_municipais.csv"
MANIFESTACOES_PATH = BASE_DIR / "manifestacoes_cidadao.json"
SCHEMA_PATH = BASE_DIR / "schema_governo.sql"


def conectar():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )


def gerar_embedding(texto):
    texto_normalizado = texto.lower()
    dominios = {
        "obras": ([1.0, 0.0, 0.0], ("buraco", "cratera", "pista", "asfalto")),
        "saude": ([0.0, 1.0, 0.0], ("consulta", "medica", "exame", "saude")),
        "educacao": ([0.0, 0.0, 1.0], ("creche", "matricular", "vaga")),
        "ambiente": ([-1.0, 0.0, 0.0], ("arvore", "galho", "vegetacao")),
        "transito": ([0.0, -1.0, 0.0], ("semaforo", "cruzamento", "transito")),
    }
    for vetor, termos in dominios.values():
        if any(termo in texto_normalizado for termo in termos):
            return vetor

    digest = hashlib.sha256(texto.encode("utf-8")).digest()
    valores = [
        int.from_bytes(digest[i : i + 2], "big") / 32767.5 - 1 for i in (0, 2, 4)
    ]
    norma = sum(valor * valor for valor in valores) ** 0.5
    return [round(valor / norma, 6) for valor in valores]


def vetor_sql(embedding):
    return "[" + ",".join(str(valor) for valor in embedding) + "]"


def preparar_banco(conn):
    with conn.cursor() as cur:
        cur.execute(
            "DROP TABLE IF EXISTS ouvidoria_processada, ouvidoria_raw, servicos_master CASCADE"
        )
        cur.execute(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()


def ingerir_servicos(conn):
    with SERVICOS_PATH.open(newline="", encoding="utf-8") as arquivo:
        servicos = csv.DictReader(arquivo)
        with conn.cursor() as cur:
            for servico in servicos:
                texto = f"{servico['servico']} {servico['descricao']}"
                cur.execute(
                    """
                    INSERT INTO servicos_master
                        (id, secretaria, servico, descricao, prazo_dias, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        int(servico["id"]),
                        servico["secretaria"],
                        servico["servico"],
                        servico["descricao"],
                        int(servico["prazo_dias"]),
                        vetor_sql(gerar_embedding(texto)),
                    ),
                )
    conn.commit()


def ingerir_manifestacoes(conn):
    manifestacoes = json.loads(MANIFESTACOES_PATH.read_text(encoding="utf-8"))
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO ouvidoria_raw (dados) VALUES (%s)",
            [(Json(manifestacao),) for manifestacao in manifestacoes],
        )
    conn.commit()


def classificar_prioridade(texto, severidade):
    termos_criticos = ["acidente", "risco", "desabamento", "urgente", "queda", "morte"]
    if any(termo in texto.lower() for termo in termos_criticos) or severidade >= 5:
        return "CRÍTICA"
    if severidade >= 4:
        return "ALTA"
    return "NORMAL"


def processar_manifestacoes(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT dados FROM ouvidoria_raw ORDER BY id")
        manifestacoes = [linha[0] for linha in cur.fetchall()]
        for manifestacao in manifestacoes:
            relato = manifestacao["texto_relato"]
            embedding = vetor_sql(gerar_embedding(relato))
            cur.execute(
                """
                SELECT id, embedding <=> %s AS distancia
                FROM servicos_master
                ORDER BY distancia ASC
                LIMIT 1
                """,
                (embedding,),
            )
            servico_id, distancia = cur.fetchone()
            prioridade = classificar_prioridade(
                relato, int(manifestacao["severidade_declarada"])
            )
            cur.execute(
                """
                INSERT INTO ouvidoria_processada
                    (protocolo, bairro, relato, nivel_prioridade,
                     servico_sugerido_id, distancia_confianca)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    manifestacao["protocolo"],
                    manifestacao["bairro"],
                    relato,
                    prioridade,
                    servico_id,
                    float(distancia),
                ),
            )
    conn.commit()


def consultar_mapa_criticas(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT op.bairro, sm.secretaria, COUNT(*) AS total_demandas_criticas
            FROM ouvidoria_processada AS op
            JOIN servicos_master AS sm ON op.servico_sugerido_id = sm.id
            WHERE op.nivel_prioridade = 'CRÍTICA'
            GROUP BY op.bairro, sm.secretaria
            ORDER BY total_demandas_criticas DESC
            """
        )
        return cur.fetchall()


def executar():
    conn = conectar()
    try:
        preparar_banco(conn)
        ingerir_servicos(conn)
        ingerir_manifestacoes(conn)
        processar_manifestacoes(conn)
        mapa = consultar_mapa_criticas(conn)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT op.protocolo, op.nivel_prioridade, sm.secretaria,
                       sm.servico, op.distancia_confianca
                FROM ouvidoria_processada AS op
                JOIN servicos_master AS sm ON op.servico_sugerido_id = sm.id
                ORDER BY op.id
                """
            )
            resultados = cur.fetchall()
    finally:
        conn.close()

    print("Triagem das manifestações:")
    for protocolo, prioridade, secretaria, servico, distancia in resultados:
        print(
            f"- {protocolo}: {prioridade} | {secretaria} / {servico} "
            f"| distância={distancia:.4f}"
        )
    print("\nMapa de demandas críticas:")
    for bairro, secretaria, total in mapa:
        print(f"- {bairro}: {secretaria} ({total})")


if __name__ == "__main__":
    executar()
