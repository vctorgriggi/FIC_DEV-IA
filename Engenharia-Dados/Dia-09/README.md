# Dia 09 - Atividade prática

Material: `Conceitos e Técnicas de Visualização de Dados.pdf`.

## Itens 12 e 21: PostgreSQL

Pré-requisito: Docker instalado e o usuário atual autorizado a acessar o
socket do Docker. Para corrigir a permissão no Ubuntu, execute no terminal:

```bash
sudo usermod -aG docker "$USER"
```

Depois, encerre a sessão e entre novamente. Não é necessário instalar o Docker
novamente: ele já está disponível nesta máquina.

Suba o banco a partir desta pasta:

```bash
docker compose -f docker-compose-db.yml up -d
docker compose -f docker-compose-db.yml ps
```

A tabela `vendas_teste` é criada e preenchida automaticamente pelo arquivo
`init.sql`. Para conferir os dados:

```bash
docker compose -f docker-compose-db.yml exec postgres_db \
  psql -U superset_user -d superset_data -c \
  'SELECT * FROM vendas_teste ORDER BY data_venda;'
```

## Itens 17 a 20 e 22: Superset

Clone o Superset em uma pasta de laboratório fora deste repositório e inicie
os serviços conforme a documentação oficial:

```bash
mkdir -p "$HOME/superset_lab"
cd "$HOME/superset_lab"
git clone https://github.com/apache/superset.git
cd superset
docker compose -f docker-compose-non-dev.yml pull
docker compose -f docker-compose-non-dev.yml up -d
```

Acesse `http://localhost:8088` e entre com `admin` / `admin`.

No cadastro do banco, use esta URI. Neste Linux, o gateway Docker `172.17.0.1`
alcança o PostgreSQL publicado no host:

```text
postgresql://superset_user:superset_password@172.17.0.1:5433/superset_data
```

Em `Datasets`, selecione o banco, schema `public` e tabela `vendas_teste`, e
clique em `Create Dataset and Create Chart`.

## Item 23: gráfico e dashboard

1. Escolha `Pie Chart`.
2. Em `Dimensions`, selecione `produto`.
3. Em `Metric`, selecione `valor` com agregação `SUM`.
4. Ative os rótulos e, se desejar, o formato donut.
5. Clique em `Update Chart`.
6. Salve como `Vendas por Produto` no dashboard `Painel de Vendas - Aula 9`.

O resultado esperado é Produto A com `270,00` e Produto B com `200,50`.

## Depois do item 23

No dashboard salvo, clique em `Edit Dashboard`, ajuste o tamanho e a posição
do gráfico e clique em `Save`. Ao lado do título, mude o status de `Draft` para
`Published`.

Para apresentar sem as barras do Superset, abra o dashboard publicado e acrescente
`?standalone=true` ao final da URL. Exemplo:

```text
http://localhost:8088/superset/dashboard/1/?standalone=true
```

O arquivo `portal_cliente.html` nesta pasta é um exemplo de portal com iframe.
Troque o `1` pelo ID real do seu dashboard salvo. O override
`~/superset_lab/superset/docker/pythonpath_dev/superset_config_docker.py` já
habilita o modo embed para este laboratório local.
