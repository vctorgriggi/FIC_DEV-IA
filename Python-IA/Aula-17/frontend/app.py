"""Interface Streamlit para o assistente Python."""

from __future__ import annotations

import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Assistente Python", page_icon="PY", layout="centered")

if "historico" not in st.session_state:
    st.session_state.historico = []


def chamar_backend(pergunta: str) -> str:
    try:
        resposta = requests.post(
            f"{BACKEND_URL}/ask", json={"texto": pergunta}, timeout=60
        )
        resposta.raise_for_status()
        return resposta.json()["resposta"]
    except requests.exceptions.ConnectionError:
        return "Backend offline. Execute: uvicorn backend.main:app --reload"
    except requests.exceptions.Timeout:
        return "O backend demorou para responder. Tente novamente."
    except requests.exceptions.HTTPError as exc:
        detalhe = exc.response.json().get("detail", str(exc))
        return f"Erro do backend: {detalhe}"
    except requests.RequestException as exc:
        return f"Erro de comunicacao: {exc}"


col_titulo, col_limpar = st.columns([3, 1])
with col_titulo:
    st.title("Assistente Python")
    st.caption("Gemini + LangChain + FastAPI")
with col_limpar:
    if st.button("Limpar", use_container_width=True):
        st.session_state.historico = []
        st.rerun()

st.divider()
for mensagem in st.session_state.historico:
    with st.chat_message(mensagem["role"]):
        st.markdown(mensagem["content"])

if pergunta := st.chat_input("Qual e a sua duvida sobre Python?"):
    st.session_state.historico.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)
    with st.chat_message("assistant"):
        with st.spinner("Consultando o Gemini..."):
            resposta = chamar_backend(pergunta)
        st.markdown(resposta)
    st.session_state.historico.append({"role": "assistant", "content": resposta})
