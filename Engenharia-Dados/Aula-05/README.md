# Aula 05: Pipeline de recomendação

Pipeline baseado no roteiro da Aula 05: carrega produtos de CSV, guarda avaliações brutas em `JSONB`, classifica sentimentos e recomenda produtos pela similaridade cosseno usando `pgvector`. O schema segue as tabelas e campos do PDF complementar.

## Preparação

1. Instale as dependências: `pip install -r requirements.txt`.
2. Use PostgreSQL com a extensão `vector` instalada.
3. Configure, se necessário, `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` e `DB_PASSWORD`.

## Execução

Na pasta desta aula, rode:

```bash
python3 pipeline_recomendacao.py 1
```

O número final é o ID do produto usado como semente. A execução recria os dados das três tabelas para evitar duplicação durante o exercício.

## Estrutura

- `produtos.csv`: catálogo estruturado.
- `avaliacoes.json`: avaliações semiestruturadas.
- `schema.sql`: tabelas relacionais, `JSONB` e `vector(3)`.
- `pipeline_recomendacao.py`: ingestão, transformação e recomendação.

## Atividade extra: triagem da Ouvidoria

O projeto extra do PDF está implementado separadamente:

- `servicos_municipais.csv`: carta de serviços das secretarias.
- `manifestacoes_cidadao.json`: relatos brutos dos cidadãos.
- `schema_governo.sql`: tabelas `servicos_master`, `ouvidoria_raw` e `ouvidoria_processada`.
- `pipeline_ouvidoria.py`: ingestão, classificação de prioridade, roteamento por `pgvector` e mapa de demandas críticas.

Execute com:

```bash
python3 pipeline_ouvidoria.py
```
