"""API HTTP do assistente educacional."""

from __future__ import annotations

from chains.qa_chain import nome_modelo, responder
from chains.retriever_chain import recuperar
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Assistente Python API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Pergunta(BaseModel):
    texto: str = Field(..., min_length=3, max_length=1000)
    contexto: str = Field(default="", max_length=10000)


class Resposta(BaseModel):
    resposta: str
    modelo: str


@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "ok", "modelo": nome_modelo()}


@app.post("/ask", response_model=Resposta)
def ask(pergunta: Pergunta) -> Resposta:
    contexto = pergunta.contexto or recuperar(pergunta.texto)
    try:
        texto = responder(pergunta.texto, contexto)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return Resposta(resposta=texto, modelo=nome_modelo())
