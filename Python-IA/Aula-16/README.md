# Mini-lab Aula 16 - Pergunte ao seu PDF

Sistema offline de busca semantica em PDFs. O indexador extrai as paginas,
divide o texto em chunks, gera embeddings locais e persiste tudo no ChromaDB.
O buscador recupera os trechos mais relevantes para cada pergunta. A geracao
de respostas com LLM fica para a proxima aula.

## Instalacao

```bash
.venv/bin/pip install -r requirements.txt
```

Na primeira execucao, `sentence-transformers` baixa o modelo
`paraphrase-multilingual-MiniLM-L12-v2` e o deixa em cache.

## Uso

Coloque um ou mais PDFs em `pdfs/` e indexe um arquivo:

```bash
.venv/bin/python indexador.py pdfs/documento.pdf
```

Ou indexe todos os PDFs de uma pasta:

```bash
.venv/bin/python indexador.py pdfs/
```

Depois, inicie o buscador:

```bash
.venv/bin/python buscador.py
```

Opcoes uteis:

```bash
.venv/bin/python buscador.py --arquivo documento.pdf --n 8 --limiar 0.5
.venv/bin/python buscador.py --contexto
```

Digite `sair`, `exit` ou `q` para encerrar. O banco persistente e criado em
`banco/`; IDs determinísticos tornam a indexacao idempotente.

## Modulos

- `rag_utils.py`: modelo, colecao, chunking, IDs, contexto e exibicao.
- `indexador.py`: extracao por pagina e indexacao de PDFs.
- `buscador.py`: perguntas, filtro de relevancia e modo interativo.
