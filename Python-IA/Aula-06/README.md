# Mini-lab Aula 06 — Extrator de Dados com Regex e Arquivos

Pipeline que lê um arquivo de texto desestruturado (`contatos.txt`), extrai CPFs,
telefones e e-mails com expressões regulares e exporta os resultados em CSV, JSON
e TXT na pasta `saida/`.

## Como executar

```bash
python extrator.py
```

## Arquivos gerados

- `saida/contatos.csv` — dados estruturados em formato tabular
- `saida/contatos_completo.json` — dados completos em JSON
- `saida/relatorio.txt` — metadados e estatísticas em texto
