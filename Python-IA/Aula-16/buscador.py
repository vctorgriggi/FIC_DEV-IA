"""Interface interativa para buscar chunks de PDFs indexados."""

from __future__ import annotations

import argparse
from typing import Any

import rag_utils as ru


def recuperar(
    pergunta: str,
    n: int,
    limiar: float,
    arquivo: str | None = None,
) -> list[dict[str, Any]]:
    """Busca os chunks mais proximos e aplica o limiar de distancia."""
    if not pergunta.strip():
        return []
    if n < 1:
        raise ValueError("n deve ser maior que zero.")
    modelo = ru.obter_modelo()
    colecao = ru.obter_colecao()
    embedding = modelo.encode(pergunta, normalize_embeddings=True).tolist()
    filtros = {"arquivo": arquivo} if arquivo else None
    resultado = colecao.query(
        query_embeddings=[embedding],
        n_results=n,
        where=filtros,
        include=["documents", "metadatas", "distances"],
    )
    chunks = []
    for rank, (texto, meta, distancia) in enumerate(
        zip(
            resultado["documents"][0],
            resultado["metadatas"][0],
            resultado["distances"][0],
        ),
        1,
    ):
        if distancia <= limiar:
            chunks.append(
                {
                    "rank": rank,
                    "texto": texto,
                    "arquivo": meta.get("arquivo", "?"),
                    "pagina": meta.get("pagina", "?"),
                    "distancia": round(distancia, 4),
                }
            )
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description="Busca semantica em PDFs indexados.")
    parser.add_argument("--arquivo", help="Restringe a busca a um PDF.")
    parser.add_argument("--n", type=int, default=ru.N_RESULTADOS)
    parser.add_argument("--limiar", type=float, default=ru.LIMIAR_DISTANCIA)
    parser.add_argument("--contexto", action="store_true")
    args = parser.parse_args()

    colecao = ru.obter_colecao()
    if colecao.count() == 0:
        print("Banco vazio. Execute primeiro: python indexador.py <arquivo.pdf>")
        raise SystemExit(1)

    print("=" * 62)
    print(" BUSCADOR SEMANTICO DE PDFs - ChromaDB + sentence-transformers")
    print(f" Documentos indexados: {colecao.count()} chunks")
    print(" Digite 'sair' para encerrar.")
    print("=" * 62)
    while True:
        try:
            pergunta = input("\nPergunta: ").strip()
        except EOFError:
            print("\nEncerrando.")
            break
        if not pergunta:
            continue
        if pergunta.lower() in {"sair", "exit", "q"}:
            print("Encerrando.")
            break
        chunks = recuperar(pergunta, args.n, args.limiar, args.arquivo)
        if args.contexto:
            print("\n=== CONTEXTO MONTADO ===")
            print(ru.montar_contexto(chunks) or "(nenhum chunk dentro do limiar)")
        else:
            ru.exibir_chunks(pergunta, chunks)


if __name__ == "__main__":
    main()
