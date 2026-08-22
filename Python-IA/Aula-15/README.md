# Mini-lab Aula 15 - Embeddings e busca semantica

Motor de busca semantica para chunks de documentos usando
`sentence-transformers`, similaridade cosseno e um indice persistido com
NumPy.

## Requisitos

```bash
python3 -m pip install numpy sentence-transformers
```

Na primeira execucao, o modelo multilingue e baixado e armazenado no cache
local do `sentence-transformers`.

## Uso

Com o corpus demonstrativo embutido:

```bash
python3 main.py
```

Com os chunks gerados na Aula 13 (`lista` ou `{"chunks": [...]}`):

```bash
python3 main.py ../Aula-13/documento_chunks.json
```

O programa demonstra tres consultas, executa a avaliacao qualitativa e abre
um modo interativo. Digite `sair` ou use `Ctrl+D` para encerrar. Para limitar
os resultados, acrescente `k=N`, por exemplo `contrato k=3`.

Na primeira execucao, os arquivos `indice/embeddings.npy` e
`indice/metadados.json` sao criados. Nas execucoes seguintes, eles sao
reutilizados e o modelo nao precisa reprocessar o corpus.

## Funcoes principais

- `similaridade_cosseno`: calcula o cosseno entre dois vetores.
- `carregar_corpus`: le chunks JSON ou usa o corpus interno.
- `indexar`: gera e persiste embeddings normalizados.
- `buscar`: retorna os chunks mais similares em ordem decrescente.
- `avaliar`: executa casos diretos, sinonimos, perguntas e caso negativo.
