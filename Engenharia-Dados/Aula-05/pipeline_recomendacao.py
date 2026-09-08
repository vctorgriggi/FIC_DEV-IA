import argparse
import csv
import hashlib
import json
import os
from pathlib import Path

import psycopg2
from psycopg2.extras import Json

BASE_DIR = Path(__file__).parent
PRODUTOS_PATH = BASE_DIR / "produtos.csv"
AVALIACOES_PATH = BASE_DIR / "avaliacoes.json"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def conectar():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )


def gerar_embedding(texto):
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
            "DROP TABLE IF EXISTS avaliacoes_processadas, avaliacoes_raw, produtos_master CASCADE"
        )
        cur.execute(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()


def ingest_produtos_csv(conn, caminho=PRODUTOS_PATH):
    with caminho.open(newline="", encoding="utf-8") as arquivo, conn.cursor() as cur:
        for produto in csv.DictReader(arquivo):
            texto = f"{produto['nome']} {produto['descricao']} {produto['categoria']}"
            cur.execute(
                """
                INSERT INTO produtos_master (id, nome, descricao, categoria, embedding)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    int(produto["id"]),
                    produto["nome"],
                    produto["descricao"],
                    produto["categoria"],
                    vetor_sql(gerar_embedding(texto)),
                ),
            )
    conn.commit()


def ingest_avaliacoes_json(conn, caminho=AVALIACOES_PATH):
    avaliacoes = json.loads(caminho.read_text(encoding="utf-8"))
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO avaliacoes_raw (dados) VALUES (%s)",
            [(Json(avaliacao),) for avaliacao in avaliacoes],
        )
    conn.commit()


def classificar_sentimento(nota):
    if nota >= 4:
        return "positivo"
    if nota <= 2:
        return "negativo"
    return "neutro"


def processar_avaliacoes(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
                     INSERT INTO avaliacoes_processadas
                      (produto_id, cliente_id, avaliacao, comentario, sentimento)
            SELECT (dados->>'produto_id')::integer,
                         dados->>'cliente_id',
                         (dados->>'avaliacao')::integer,
                         dados->>'comentario',
                   CASE
                       WHEN (dados->>'avaliacao')::numeric >= 4 THEN 'positivo'
                       WHEN (dados->>'avaliacao')::numeric <= 2 THEN 'negativo'
                       ELSE 'neutro'
                   END
            FROM avaliacoes_raw
            """
        )
    conn.commit()


def recomendar(conn, produto_id, limite=3):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT recomendado.id,
                   recomendado.nome,
                   ROUND((1 - (recomendado.embedding <=> origem.embedding))::numeric, 4) AS similaridade,
                   ROUND(AVG(avaliacoes.avaliacao), 2) AS media_avaliacoes,
                   COUNT(*) FILTER (WHERE avaliacoes.sentimento = 'positivo') AS avaliacoes_positivas
            FROM produtos_master AS origem
            CROSS JOIN produtos_master AS recomendado
            LEFT JOIN avaliacoes_processadas AS avaliacoes
                ON avaliacoes.produto_id = recomendado.id
            WHERE origem.id = %s AND recomendado.id <> origem.id
            GROUP BY origem.embedding, recomendado.id, recomendado.nome, recomendado.embedding
            ORDER BY similaridade DESC
            LIMIT %s
            """,
            (produto_id, limite),
        )
        return cur.fetchall()


def executar(produto_id):
    conn = conectar()
    try:
        preparar_banco(conn)
        ingest_produtos_csv(conn)
        ingest_avaliacoes_json(conn)
        processar_avaliacoes(conn)
        resultados = recomendar(conn, produto_id)
    finally:
        conn.close()

    print(f"Recomendações para o produto {produto_id}:")
    for item_id, nome, similaridade, media, positivas in resultados:
        print(
            f"- {item_id}: {nome} | similaridade={similaridade} "
            f"| média={media or 'sem avaliações'} "
            f"| avaliações positivas={positivas}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline de recomendação com PostgreSQL e pgvector"
    )
    parser.add_argument("produto_id", type=int, help="ID do produto usado como semente")
    args = parser.parse_args()
    executar(args.produto_id)


if __name__ == "__main__":
    main()
