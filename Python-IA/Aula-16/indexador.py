"""Indexa PDFs no ChromaDB persistente."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pdfplumber
import rag_utils as ru


def extrair_paginas(caminho_pdf: str | Path) -> list[dict[str, Any]]:
    """Extrai texto pagina a pagina, ignorando paginas quase vazias."""
    paginas = []
    with pdfplumber.open(caminho_pdf) as pdf:
        for numero, pagina in enumerate(pdf.pages, 1):
            texto = (pagina.extract_text() or "").strip()
            if len(texto.split()) >= 10:
                paginas.append({"pagina": numero, "texto": texto})
    return paginas


def indexar_arquivo(caminho: str | Path) -> int:
    """Indexa um PDF e retorna a quantidade de chunks inseridos."""
    caminho = Path(caminho)
    nome = caminho.name
    modelo = ru.obter_modelo()
    colecao = ru.obter_colecao()
    paginas = extrair_paginas(caminho)
    print(f"\nIndexando: {nome}")
    print(f" Paginas com texto: {len(paginas)}")

    ids: list[str] = []
    documentos: list[str] = []
    metadados: list[dict[str, Any]] = []
    for pagina in paginas:
        for indice, texto in enumerate(ru.chunkar(pagina["texto"])):
            ids.append(ru.id_chunk(f"{nome}:{pagina['pagina']}:{indice}:{texto}"))
            documentos.append(texto)
            metadados.append(
                {"arquivo": nome, "pagina": pagina["pagina"], "chunk_local": indice}
            )

    existentes = set(colecao.get(ids=ids)["ids"]) if ids else set()
    novos = [
        item for item in zip(ids, documentos, metadados) if item[0] not in existentes
    ]
    print(f" Chunks gerados: {len(documentos)}")
    if not novos:
        print(" Nenhum chunk novo - arquivo ja estava indexado.")
        return 0

    ids_novos, docs_novos, metas_novas = zip(*novos)
    print(f" Gerando embeddings para {len(docs_novos)} chunks...")
    embeddings = modelo.encode(
        list(docs_novos),
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
    ).tolist()
    colecao.add(
        ids=list(ids_novos),
        documents=list(docs_novos),
        embeddings=embeddings,
        metadatas=list(metas_novas),
    )
    print(f" Inseridos: {len(docs_novos)} chunks")
    print(f" Total na colecao: {colecao.count()}")
    return len(docs_novos)


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python indexador.py <arquivo.pdf|diretorio/>")
        raise SystemExit(1)
    alvo = Path(sys.argv[1])
    pdfs = sorted(alvo.glob("*.pdf")) if alvo.is_dir() else [alvo]
    if not pdfs or any(not pdf.is_file() for pdf in pdfs):
        print(f"Nenhum PDF encontrado em: {alvo}")
        raise SystemExit(1)
    total = sum(indexar_arquivo(pdf) for pdf in pdfs)
    print(f"\nConcluido: {total} chunks novos.")


if __name__ == "__main__":
    main()
