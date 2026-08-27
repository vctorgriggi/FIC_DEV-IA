# Aula 17 - Assistente Python com Gemini

MVP de chat educacional com FastAPI, Streamlit e LangChain. A implementacao usa
Gemini no lugar da OpenAI: o modelo e configurado por `GEMINI_MODEL` e a chave
fica somente em `GOOGLE_API_KEY` no arquivo local `.env`.

## Configuracao

```bash
cd Python-IA/Aula-17
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
```

Preencha `GOOGLE_API_KEY` com uma chave criada no Google AI Studio. Nunca
versione `.env`.

## Execucao

Em um terminal:

```bash
.venv/bin/uvicorn backend.main:app --reload --port 8000
```

Em outro terminal:

```bash
.venv/bin/streamlit run frontend/app.py
```

Abra `http://localhost:8501`. A API e documentada em
`http://localhost:8000/docs`.

## Teste rapido da API

```bash
curl http://localhost:8000/
curl -X POST http://localhost:8000/ask \\
	-H 'Content-Type: application/json' \\
	-d '{"texto":"O que e uma funcao lambda?"}'
```
