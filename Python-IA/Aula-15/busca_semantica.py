from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import numpy as np

MODELO_NOME = "paraphrase-multilingual-MiniLM-L12-v2"
PASTA_INDICE = Path("indice")
TOP_K_PADRAO = 5

CORPUS: list[dict[str, Any]] = [
    {
        "chunk_id": "contrato_c001",
        "fonte": "contrato_servicos.pdf",
        "pagina": 1,
        "texto": (
            "O presente contrato de prestacao de servicos tem vigencia de 24 "
            "meses, contados a partir da data de assinatura. Qualquer rescisao "
            "antecipada por parte do contratante implicara multa equivalente a "
            "20% do valor total remanescente do contrato."
        ),
    },
    {
        "chunk_id": "contrato_c002",
        "fonte": "contrato_servicos.pdf",
        "pagina": 1,
        "texto": (
            "O pagamento devera ser efetuado mensalmente, ate o dia 10 de cada "
            "mes, mediante emissao de nota fiscal. O atraso no pagamento "
            "acarretara juros de 1% ao mes e multa moratoria de 2% sobre o valor "
            "em atraso."
        ),
    },
    {
        "chunk_id": "contrato_c003",
        "fonte": "contrato_servicos.pdf",
        "pagina": 2,
        "texto": (
            "As partes elegem o foro da comarca de Sao Paulo para dirimir "
            "quaisquer litigios decorrentes deste instrumento, com renuncia "
            "expressa a qualquer outro, por mais privilegiado que seja."
        ),
    },
    {
        "chunk_id": "manual_c001",
        "fonte": "manual_produto.pdf",
        "pagina": 3,
        "texto": (
            "Para instalar o software, execute o instalador como administrador e "
            "siga as instrucoes na tela. O sistema requer Windows 10 ou superior, "
            "com minimo de 8 GB de RAM e 20 GB de espaco em disco."
        ),
    },
    {
        "chunk_id": "manual_c002",
        "fonte": "manual_produto.pdf",
        "pagina": 5,
        "texto": (
            "Em caso de falha durante a instalacao, verifique se o antivirus esta "
            "desativado temporariamente. Erros comuns incluem permissao negada, "
            "porta em uso e dependencia ausente. Consulte o log em "
            "C:\\Temp\\install.log."
        ),
    },
    {
        "chunk_id": "relatorio_c001",
        "fonte": "relatorio_q1.pdf",
        "pagina": 1,
        "texto": (
            "A receita liquida do primeiro trimestre de 2025 atingiu R$ 42,3 "
            "milhoes, representando crescimento de 18% em relacao ao mesmo "
            "periodo do ano anterior. O resultado operacional foi de R$ 8,7 "
            "milhoes, com margem de 20,6%."
        ),
    },
    {
        "chunk_id": "relatorio_c002",
        "fonte": "relatorio_q1.pdf",
        "pagina": 2,
        "texto": (
            "Os custos operacionais cresceram 12% no trimestre, principalmente "
            "devido ao aumento nos precos de materia-prima e ao reajuste salarial "
            "aplicado em janeiro. A empresa implementou medidas de eficiencia que "
            "devem gerar economia de R$ 2 milhoes anuais a partir do segundo "
            "semestre."
        ),
    },
    {
        "chunk_id": "relatorio_c003",
        "fonte": "relatorio_q1.pdf",
        "pagina": 3,
        "texto": (
            "As vendas no canal digital cresceram 45% no trimestre, respondendo "
            "agora por 32% da receita total. O aplicativo mobile registrou 1,2 "
            "milhao de downloads e avaliacao media de 4,7 estrelas nas lojas de "
            "aplicativos."
        ),
    },
]


def similaridade_cosseno(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Calcula a similaridade cosseno entre dois vetores."""
    if vec_a.shape != vec_b.shape:
        raise ValueError("Os vetores devem ter a mesma dimensao.")

    norma_a = np.linalg.norm(vec_a)
    norma_b = np.linalg.norm(vec_b)
    if norma_a == 0 or norma_b == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norma_a * norma_b))


def carregar_corpus(caminho_json: str | Path | None = None) -> list[dict[str, Any]]:
    """Carrega chunks da Aula 13 ou usa o corpus demonstrativo."""
    if caminho_json is not None and Path(caminho_json).exists():
        with Path(caminho_json).open(encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        chunks = dados.get("chunks", dados) if isinstance(dados, dict) else dados
        if not isinstance(chunks, list) or not chunks:
            raise ValueError("O JSON deve conter uma lista de chunks nao vazia.")
        print(f"Corpus carregado de {caminho_json}: {len(chunks)} chunks")
        return chunks

    print(f"Usando corpus interno: {len(CORPUS)} chunks")
    return CORPUS.copy()


def salvar_indice(
    embeddings: np.ndarray, metadados: list[dict[str, Any]], pasta: str | Path
) -> None:
    """Persiste os vetores em NPY e os metadados em JSON."""
    destino = Path(pasta)
    destino.mkdir(parents=True, exist_ok=True)
    np.save(destino / "embeddings.npy", embeddings)
    with (destino / "metadados.json").open("w", encoding="utf-8") as arquivo:
        json.dump(metadados, arquivo, ensure_ascii=False, indent=2)
    print(f"Indice salvo: {len(embeddings)} vetores em {destino}/")


def carregar_indice(pasta: str | Path) -> tuple[np.ndarray, list[dict[str, Any]]]:
    """Carrega embeddings e metadados persistidos."""
    origem = Path(pasta)
    embeddings = np.load(origem / "embeddings.npy")
    with (origem / "metadados.json").open(encoding="utf-8") as arquivo:
        metadados = json.load(arquivo)
    if embeddings.ndim != 2 or len(embeddings) != len(metadados):
        raise ValueError("Embeddings e metadados nao correspondem.")
    print(f"Indice carregado: {len(embeddings)} vetores ({embeddings.shape[1]}d)")
    return embeddings, metadados


def indexar(
    corpus: list[dict[str, Any]], modelo: Any, forcar: bool = False
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    """Gera o indice ou reutiliza os arquivos existentes."""
    arquivos = (PASTA_INDICE / "embeddings.npy", PASTA_INDICE / "metadados.json")
    if not forcar and all(arquivo.exists() for arquivo in arquivos):
        return carregar_indice(PASTA_INDICE)

    textos = [chunk.get("texto_embed", chunk["texto"]) for chunk in corpus]
    inicio = time.perf_counter()
    embeddings = np.asarray(
        modelo.encode(
            textos,
            batch_size=32,
            normalize_embeddings=True,
            show_progress_bar=True,
            convert_to_numpy=True,
        ),
        dtype=np.float32,
    )
    duracao = time.perf_counter() - inicio
    print(f"Indexados {len(corpus)} chunks em {duracao:.1f}s")
    salvar_indice(embeddings, corpus, PASTA_INDICE)
    return embeddings, corpus


def buscar(
    query: str,
    modelo: Any,
    embeddings: np.ndarray,
    metadados: list[dict[str, Any]],
    k: int = TOP_K_PADRAO,
) -> list[dict[str, Any]]:
    """Retorna os chunks mais similares em ordem decrescente."""
    if not query.strip():
        return []
    if k < 1:
        raise ValueError("k deve ser maior que zero.")
    query_embedding = np.asarray(
        modelo.encode(query, normalize_embeddings=True, convert_to_numpy=True),
        dtype=np.float32,
    )
    scores = embeddings @ query_embedding
    indices = np.argsort(scores)[::-1][: min(k, len(metadados))]
    return [{**metadados[index], "score": float(scores[index])} for index in indices]


def exibir_resultados(query: str, resultados: list[dict[str, Any]]) -> None:
    print(f'\nQuery: "{query}"\n' + "-" * 55)
    for posicao, resultado in enumerate(resultados, 1):
        fonte = resultado.get("fonte", resultado.get("chunk_id", "?"))
        pagina = resultado.get("pagina", "?")
        texto = resultado["texto"].replace("\n", " ")
        print(f"{posicao}. [{resultado['score']:.3f}] {fonte} (p.{pagina})")
        print(f"   {texto[:180]}...")


CASOS_TESTE = [
    ("Direto", "rescisao antecipada do contrato", "multa"),
    ("Sinonimo", "encerramento do acordo antes do prazo", "rescisao"),
    ("Pergunta", "Qual e a penalidade por cancelar o contrato?", "multa"),
    ("Pagamento", "data de vencimento e juros por atraso", "pagamento"),
    ("Tecnico", "requisitos minimos para instalar o software", "windows"),
    ("Financeiro", "crescimento da receita no trimestre", "receita"),
    ("Digital", "desempenho do canal online e aplicativo", "digital"),
    ("Negativo", "previsao do tempo para amanha", ""),
]


def avaliar(
    modelo: Any, embeddings: np.ndarray, metadados: list[dict[str, Any]], k: int = 3
) -> None:
    """Executa os casos qualitativos e imprime o resultado."""
    acertos = 0
    verificaveis = 0
    print("\n" + "=" * 55 + "\n      AVALIACAO QUALITATIVA\n" + "=" * 55)
    for categoria, query, esperado in CASOS_TESTE:
        resultados = buscar(query, modelo, embeddings, metadados, k)
        textos = " ".join(resultado["texto"].lower() for resultado in resultados)
        if esperado:
            verificaveis += 1
            acertou = esperado in textos
            acertos += int(acertou)
            status = "OK" if acertou else "ERRO"
        else:
            max_score = max((resultado["score"] for resultado in resultados), default=0)
            status = "OK" if max_score < 0.5 else "REVISAR"
        top = resultados[0] if resultados else {"score": 0, "fonte": "-"}
        print(f"{status:7} [{categoria:10}] {query[:42]}")
        print(f"         top-1: [{top['score']:.3f}] {top.get('fonte', '-')}")
    print(f"\nAcertos verificaveis: {acertos}/{verificaveis} (top-{k})")


def loop_interativo(
    modelo: Any, embeddings: np.ndarray, metadados: list[dict[str, Any]]
) -> None:
    """Permite consultar o indice ate receber 'sair' ou EOF."""
    print('\nModo interativo: digite uma query ou "sair" para encerrar.')
    while True:
        try:
            entrada = input("\n> ").strip()
        except EOFError:
            break
        if not entrada or entrada.lower() == "sair":
            break
        k = TOP_K_PADRAO
        if " k=" in entrada:
            entrada, valor_k = entrada.rsplit(" k=", 1)
            try:
                k = int(valor_k)
            except ValueError:
                pass
        exibir_resultados(entrada, buscar(entrada, modelo, embeddings, metadados, k))


def main() -> None:
    import sys

    from sentence_transformers import SentenceTransformer

    modelo = SentenceTransformer(MODELO_NOME)
    corpus = carregar_corpus(sys.argv[1] if len(sys.argv) > 1 else None)
    embeddings, metadados = indexar(corpus, modelo)
    for query in (
        "Qual e a multa por rescisao antecipada?",
        "requisitos para instalar o sistema",
        "resultado financeiro do trimestre",
    ):
        exibir_resultados(query, buscar(query, modelo, embeddings, metadados, k=2))
    avaliar(modelo, embeddings, metadados)
    loop_interativo(modelo, embeddings, metadados)


if __name__ == "__main__":
    main()
