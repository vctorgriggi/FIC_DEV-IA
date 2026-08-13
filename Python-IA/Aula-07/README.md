# Mini-lab Aula 07 — Pacote `analise_turma`

Pacote Python completo, com três módulos organizados por responsabilidade
(`calculos.py`, `validacao.py`, `relatorio.py`), um `__init__.py` que define a
API pública e um `__main__.py` que torna o pacote executável via `python -m`.
Lê os dados de `data/turma.json`, calcula médias, valida as notas e exibe um
relatório no terminal.

## Como executar

```bash
# Criar e ativar o ambiente virtual
python -m venv .venv
source .venv/bin/activate

# Instalar o pacote em modo editável
pip install -e .

# Executar (usa data/turma.json por padrão)
python -m analise_turma

# Ou com caminho explícito
python -m analise_turma data/turma.json
```

## Estrutura

```
analise_turma/
├── __init__.py     ← API pública do pacote
├── __main__.py     ← ponto de entrada via python -m
├── calculos.py     ← funções de cálculo (media, aprovado)
├── validacao.py    ← funções de validação (nota_valida, validar_aluno)
└── relatorio.py    ← leitura do JSON e exibição do relatório
data/
└── turma.json      ← dados de entrada
```
