"""Extração de PDF e geração de JSON de chunks."""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

import pdfplumber
from pypdf import PdfReader


def limpar_texto(texto: str) -> str:
    if not texto or not texto.strip():
        return ""

    texto = unicodedata.normalize("NFC", texto)
    texto = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", texto)
    texto = re.sub(r"(\w+)-\n(\w+)", r"\1\2", texto)
    texto = re.sub(r"(?<!\n)\n(?!\n)", " ", texto)
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    texto = re.sub(r" +([.,;:!?])", r"\1", texto)
    return texto.strip()


def preprocessar_para_embedding(texto: str) -> str:
    texto = limpar_texto(texto)
    texto = re.sub(r"https?://\S+|www\.\S+", "[URL]", texto)
    texto = re.sub(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b", "[EMAIL]", texto)
    texto = re.sub(r"\b\d{6,}\b", "[NUM]", texto)
    return re.sub(r"[ \t]+", " ", texto).strip()


def estimar_tokens(texto: str) -> int:
    return max(1, int(len(texto) / 4))


def chunks_por_tamanho(
    texto: str,
    tamanho_max: int = 1000,
    overlap: int = 200,
    origem: str = "",
) -> list[dict]:
    texto = limpar_texto(texto)
    if not texto:
        return []

    chunks, inicio, idx = [], 0, 0
    while inicio < len(texto):
        fim = inicio + tamanho_max
        trecho = texto[inicio:fim]
        if fim < len(texto):
            ultimo_espaco = trecho.rfind(" ")
            if ultimo_espaco > tamanho_max * 0.6:
                trecho = trecho[:ultimo_espaco]
                fim = inicio + ultimo_espaco

        trecho = trecho.strip()
        if trecho:
            chunks.append(
                {
                    "chunk_id": f"{origem}_c{idx:03d}" if origem else f"c{idx:03d}",
                    "texto": trecho,
                    "texto_embed": preprocessar_para_embedding(trecho),
                    "n_chars": len(trecho),
                    "n_tokens_est": estimar_tokens(trecho),
                    "inicio_char": inicio,
                }
            )

        idx += 1
        inicio = fim - overlap

    return chunks


def extrair_pdf(
    caminho: str | Path,
    tamanho_chunk: int = 1000,
    overlap: int = 200,
) -> dict:
    """Inspeciona, extrai, limpa e divide um PDF em chunks."""
    caminho = Path(caminho)
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    reader = PdfReader(str(caminho))
    meta = reader.metadata or {}
    n_pags = len(reader.pages)

    doc_meta = {
        "arquivo": caminho.name,
        "n_paginas": n_pags,
        "titulo": getattr(meta, "title", None) or caminho.stem,
        "autor": getattr(meta, "author", None) or "Desconhecido",
        "produtor": getattr(meta, "producer", None) or "",
        "extraido_em": datetime.now().isoformat(timespec="seconds"),
        "biblioteca": "pdfplumber",
        "metodo_chunk": "tamanho_fixo",
        "chunk_size": tamanho_chunk,
        "chunk_overlap": overlap,
    }

    paginas: list[dict] = []
    chunks_total: list[dict] = []
    origem = caminho.stem

    with pdfplumber.open(str(caminho)) as pdf:
        for i, pag in enumerate(pdf.pages):
            num_pag = i + 1
            texto_bruto = pag.extract_text() or ""
            texto_limpo = limpar_texto(texto_bruto)

            paginas.append(
                {
                    "pagina": num_pag,
                    "texto": texto_limpo,
                    "n_chars": len(texto_limpo),
                    "n_tokens_est": estimar_tokens(texto_limpo),
                    "vazia": len(texto_limpo.strip()) == 0,
                }
            )

            if texto_limpo.strip():
                chunks_pag = chunks_por_tamanho(
                    texto_limpo,
                    tamanho_max=tamanho_chunk,
                    overlap=overlap,
                    origem=f"{origem}_p{num_pag:03d}",
                )
                for chunk in chunks_pag:
                    chunk["pagina"] = num_pag
                chunks_total.extend(chunks_pag)

    return {
        "documento": doc_meta,
        "paginas": paginas,
        "chunks": chunks_total,
    }


def imprimir_resumo(resultado: dict) -> None:
    doc = resultado["documento"]
    pags = resultado["paginas"]
    chunks = resultado["chunks"]

    separador = "=" * 55
    print(f"\n{separador}")
    print(" EXTRAÇÃO DE PDF")
    print(separador)
    print(f" Arquivo : {doc['arquivo']}")
    print(f" Título  : {doc['titulo']}")
    print(f" Autor   : {doc['autor']}")
    print(f" Páginas : {doc['n_paginas']}")
    print(f" Extraído: {doc['extraido_em']}")

    vazias = sum(1 for pagina in pags if pagina["vazia"])
    total_chars = sum(pagina["n_chars"] for pagina in pags)
    total_tokens = sum(pagina["n_tokens_est"] for pagina in pags)
    print(f"\n Páginas com texto : {doc['n_paginas'] - vazias}")
    print(f" Páginas vazias    : {vazias}")
    print(f" Total de chars    : {total_chars:,}")
    print(f" Tokens estimados  : {total_tokens:,}")

    print(f"\n Chunks gerados : {len(chunks)}")
    if chunks:
        tamanhos = [chunk["n_chars"] for chunk in chunks]
        print(
            " Chunk mín/méd/máx : "
            f"{min(tamanhos)} / {sum(tamanhos) // len(tamanhos)} / {max(tamanhos)} chars"
        )
        tokens = [chunk["n_tokens_est"] for chunk in chunks]
        print(
            " Tokens mín/méd/máx: "
            f"{min(tokens)} / {sum(tokens) // len(tokens)} / {max(tokens)}"
        )

        print("\n Prévia (primeiros 3 chunks):")
        for chunk in chunks[:3]:
            preview = chunk["texto"][:120].replace("\n", " ")
            print(
                f" [{chunk['chunk_id']}] "
                f"({chunk['n_chars']} chars, p.{chunk['pagina']})"
            )
            print(f" {preview}...")

    print(f"\n{separador}\n")


def salvar_json(dados: dict, caminho: str | Path) -> None:
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)
    print(f" Salvo: {caminho}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python extrator_pdf.py <arquivo.pdf> [chunk_size] [overlap]")
        print("Ex: python extrator_pdf.py documento.pdf 1000 200")
        sys.exit(1)

    caminho = Path(sys.argv[1])
    chunk_size = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    overlap = int(sys.argv[3]) if len(sys.argv) > 3 else 200

    print(f"Processando: {caminho.name} ...")
    resultado = extrair_pdf(caminho, chunk_size, overlap)
    imprimir_resumo(resultado)

    salvar_json(
        {
            "documento": resultado["documento"],
            "paginas": resultado["paginas"],
        },
        caminho.stem + "_paginas.json",
    )
    salvar_json(
        {
            "documento": resultado["documento"],
            "chunks": resultado["chunks"],
        },
        caminho.stem + "_chunks.json",
    )

    print(f"Concluído! {len(resultado['chunks'])} chunks exportados.")


if __name__ == "__main__":
    main()
