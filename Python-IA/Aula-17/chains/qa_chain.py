"""Chain de perguntas e respostas usando Gemini via LangChain."""

from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

PROMPT_SISTEMA = """Voce e um assistente educacional especializado em Python.
Responda sempre em portugues, com clareza e exemplos curtos quando ajudarem.
Se houver contexto adicional, use-o como fonte principal e nao invente fatos.
Se a resposta nao estiver no contexto, diga honestamente que nao localizou essa
informacao. Contexto adicional:
{contexto}"""

_prompt = ChatPromptTemplate.from_messages(
    [("system", PROMPT_SISTEMA), ("human", "{pergunta}")]
)


@lru_cache(maxsize=1)
def _obter_chain():
    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError(
            "GOOGLE_API_KEY nao configurada. Copie .env.example para .env "
            "e informe sua chave do Google AI Studio."
        )
    modelo = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        temperature=0.7,
        max_output_tokens=1500,
    )
    return _prompt | modelo | StrOutputParser()


def responder(pergunta: str, contexto: str = "") -> str:
    """Envia uma pergunta ao Gemini e retorna somente o texto da resposta."""
    return _obter_chain().invoke(
        {"pergunta": pergunta.strip(), "contexto": contexto.strip() or "(nenhum)"}
    )


def nome_modelo() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
