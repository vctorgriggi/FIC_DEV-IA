"""Recuperacao simples de contexto local para o assistente."""

from __future__ import annotations

from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "docs" / "base_conhecimento.txt"


def recuperar(pergunta: str, limite: int = 3) -> str:
    """Seleciona trechos locais que compartilham termos com a pergunta."""
    termos = {termo.lower() for termo in pergunta.split() if len(termo) > 2}
    trechos = [
        trecho.strip() for trecho in BASE.read_text(encoding="utf-8").split("\n\n")
    ]
    pontuados = sorted(
        trechos,
        key=lambda trecho: sum(termo in trecho.lower() for termo in termos),
        reverse=True,
    )
    relevantes = [
        trecho
        for trecho in pontuados[:limite]
        if any(t in trecho.lower() for t in termos)
    ]
    return "\n\n---\n\n".join(relevantes)
