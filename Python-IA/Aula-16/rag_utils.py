"""Funcoes compartilhadas do sistema de perguntas sobre PDFs."""

from __future__ import annotations

import hashlib
from typing import Any

import chromadb
from sentence_transformers import SentenceTransformer

MODELO_NOME = "paraphrase-multilingual-MiniLM-L12-v2"
DB_PATH = "./banco"
COLECAO_NOME = "pdf_chunks"
CHUNK_PALAVRAS = 400
CHUNK_OVERLAP = 80
N_RESULTADOS = 5
LIMIAR_DISTANCIA = 0.65
MAX_PALAVRAS_CTX = 1500

_modelo: SentenceTransformer | None = None
_colecao: Any = None


def obter_modelo() -> SentenceTransformer:
    global _modelo
    if _modelo is None:
        print("Carregando modelo de embedding...")
        _modelo = SentenceTransformer(MODELO_NOME)
        print(f"Modelo pronto: {MODELO_NOME}")
    return _modelo


def obter_colecao() -> Any:
    global _colecao
    if _colecao is None:
        cliente = chromadb.PersistentClient(path=DB_PATH)
        _colecao = cliente.get_or_create_collection(
            name=COLECAO_NOME,
            metadata={"hnsw:space": "cosine", "modelo": MODELO_NOME},
        )
    return _colecao


def chunkar(
    texto: str,
    tamanho: int = CHUNK_PALAVRAS,
    sobreposicao: int = CHUNK_OVERLAP,
) -> list[str]:
    """Divide um texto em janelas de palavras com sobreposicao."""
    if tamanho < 1 or sobreposicao < 0 or sobreposicao >= tamanho:
        raise ValueError("Use tamanho > sobreposicao >= 0.")

    palavras = texto.split()
    passo = tamanho - sobreposicao
    chunks = []
    for inicio in range(0, len(palavras), passo):
        chunk = " ".join(palavras[inicio : inicio + tamanho])
        if len(chunk.split()) >= 20:
            chunks.append(chunk)
        if inicio + tamanho >= len(palavras):
            break
    return chunks


def id_chunk(texto: str) -> str:
    """Gera um identificador estavel a partir do conteudo do chunk."""
    return hashlib.md5(texto.encode("utf-8")).hexdigest()[:16]


def montar_contexto(
    chunks: list[dict[str, Any]], max_palavras: int = MAX_PALAVRAS_CTX
) -> str:
    """Monta um bloco delimitado de contexto para uma futura LLM."""
    partes = []
    total = 0
    for chunk in chunks:
        palavras = len(chunk["texto"].split())
        if total + palavras > max_palavras:
            break
        fonte = f"[{chunk['arquivo']} - p. {chunk['pagina']}]"
        partes.append(f"{fonte}\n{chunk['texto']}")
        total += palavras
    return "\n\n---\n\n".join(partes)


def exibir_chunks(pergunta: str, chunks: list[dict[str, Any]]) -> None:
    print("\n" + "=" * 62)
    print(f"PERGUNTA : {pergunta}")
    print(f"CHUNKS   : {len(chunks)} recuperados")
    print("=" * 62)
    if not chunks:
        print("Nenhum chunk dentro do limiar de relevancia.")
        return
    for chunk in chunks:
        relevancia = 1 - chunk["distancia"]
        barra = "#" * int(relevancia * 20)
        print(f"\n #{chunk['rank']} [{barra:<20}] rel={relevancia:.3f}")
        print(f"      {chunk['arquivo']} - pagina {chunk['pagina']}")
        print(f"      {chunk['texto'][:180].strip()}...")
    print("=" * 62)
