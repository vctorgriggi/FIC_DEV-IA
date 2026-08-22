"""Pipeline de NLP para limpeza e analise de texto OCR."""

import re
from collections import Counter
from typing import Any

import spacy

_nlp: spacy.Language | None = None


def _carregar_modelo() -> spacy.Language:
    """Carrega o modelo spaCy uma unica vez."""
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("pt_core_news_sm")
        except OSError as erro:
            raise OSError(
                "Modelo spaCy nao encontrado. Execute: "
                "python -m spacy download pt_core_news_sm"
            ) from erro
    return _nlp


def limpar_ocr(texto: str) -> str:
    """Remove artefatos tipicos de OCR e normaliza o texto."""
    texto = re.sub(r"-(\n)(\w)", r"\2", texto)
    texto = re.sub(r"(?<!\n)\n(?!\n)", " ", texto)
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", texto)
    texto = re.sub(r"\.{3,}", "...", texto)
    texto = re.sub(r",{2,}", ",", texto)

    linhas = texto.split("\n")
    linhas = [
        linha
        for linha in linhas
        if len(re.findall(r"[a-záéíóúàâêôãõüç]", linha, re.IGNORECASE)) >= 3
        or linha.strip() == ""
    ]
    return "\n".join(linhas).strip()


def tokenizar(texto: str, tamanho_min: int = 3) -> list[str]:
    """Tokeniza, remove stopwords e lematiza o texto."""
    if tamanho_min < 1:
        raise ValueError("tamanho_min deve ser maior que zero")
    doc = _carregar_modelo()(texto.lower())
    return [
        token.lemma_
        for token in doc
        if token.is_alpha and not token.is_stop and len(token.text) >= tamanho_min
    ]


def extrair_entidades(texto: str) -> dict[str, list[str]]:
    """Reconhece entidades nomeadas e agrupa valores unicos por tipo."""
    entidades: dict[str, list[str]] = {}
    for entidade in _carregar_modelo()(texto).ents:
        entidades.setdefault(entidade.label_, [])
        if entidade.text not in entidades[entidade.label_]:
            entidades[entidade.label_].append(entidade.text)
    return entidades


def analisar(texto_bruto: str, top_n: int = 20) -> dict[str, Any]:
    """Executa limpeza, tokenizacao, frequencia e reconhecimento de entidades."""
    if top_n < 0:
        raise ValueError("top_n nao pode ser negativo")
    texto_limpo = limpar_ocr(texto_bruto)
    tokens = tokenizar(texto_limpo)
    return {
        "texto_limpo": texto_limpo,
        "total_tokens": len(tokens),
        "vocabulario_unico": len(set(tokens)),
        "top_termos": Counter(tokens).most_common(top_n),
        "entidades": extrair_entidades(texto_limpo),
        "total_caracteres": len(texto_limpo),
        "total_palavras": len(texto_limpo.split()),
    }
