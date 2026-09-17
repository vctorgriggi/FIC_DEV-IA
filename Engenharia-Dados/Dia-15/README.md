# Dia 15 - Atividade extra: Storytelling com Dados e SQL Lab

Este material foi preparado com base no PDF "Storytelling com Dados, SQL Lab e Funcionalidades Avançadas" e segue o formato de laboratório para a pasta de Engenharia de Dados.

## Objetivo

Aplicar os conceitos de storytelling, análise exploratória com SQL Lab e recursos avançados do Apache Superset para transformar dados de vendas em uma narrativa orientada à decisão.

## Cenário de negócio

A empresa fictícia "NorthOne" está analisando o desempenho de vendas em diferentes regiões e produtos. O objetivo é:

- identificar padrões de comportamento;
- detectar oportunidades de crescimento;
- apontar riscos de queda;
- transformar os dados em uma recomendação com ação clara para a equipe comercial.

## 1) Subir o banco de dados

Na pasta desta atividade, execute:

```bash
docker compose -f docker-compose-db.yml up -d
```

Verifique o container:

```bash
docker compose -f docker-compose-db.yml ps
```

A conexão esperada para o Superset é:

```text
postgresql://superset_user:superset_password@172.17.0.1:5433/superset_data
```

## 2) Estrutura do banco

A partir do arquivo `init.sql`, o banco cria as tabelas:

- `vendas_story`
- `produtos_story`
- `clientes_story`

Essas tabelas simulam dados reais de vendas por produto, região, canal e período.

## 3) Consultas essenciais para o SQL Lab

As queries principais estão no arquivo `storytelling_queries.sql` e podem ser copiadas diretamente para o SQL Lab do Superset.

### 3.1 Resumo financeiro

```sql
SELECT
    SUM(valor) AS faturamento_total,
    AVG(valor) AS ticket_medio,
    COUNT(*) AS total_vendas
FROM vendas_story;
```

### 3.2 Faturamento por região

```sql
SELECT
    regiao,
    ROUND(SUM(valor), 2) AS faturamento
FROM vendas_story
GROUP BY regiao
ORDER BY faturamento DESC;
```

### 3.3 Produtos mais vendidos

```sql
SELECT
    p.nome_produto,
    SUM(v.valor) AS faturamento
FROM vendas_story v
JOIN produtos_story p ON p.id = v.produto_id
GROUP BY p.nome_produto
ORDER BY faturamento DESC
LIMIT 5;
```

### 3.4 Tendência mensal

```sql
SELECT
    TO_CHAR(data_venda, 'YYYY-MM') AS mes,
    ROUND(SUM(valor), 2) AS faturamento
FROM vendas_story
GROUP BY TO_CHAR(data_venda, 'YYYY-MM')
ORDER BY mes;
```

## 4) Storytelling do resultado

Use os dados para estruturar uma narrativa com os elementos pedidos no PDF:

### Contexto

A empresa tem crescido no canal digital e um movimento dos clientes indica uma mudança no comportamento de compra.

### Desafio

A equipe precisa entender onde o faturamento está concentrado, quais regiões estão abaixo da meta e onde há melhor potencial de expansão.

### Desenvolvimento

- analisar a receita por região;
- comparar os produtos com maior volume;
- verificar a evolução mensal;
- observar o canal de origem da compra.

### Insight principal

O faturamento é concentrado em poucas regiões e produtos, enquanto outras áreas ainda têm potencial de crescimento. O canal digital tem forte contribuição, mas a retenção e a diversificação de portfólio ainda podem ser melhoradas.

### Chamada para ação

- aumentar investimento em campanhas para a região Norte;
- incentivar a expansão de produtos com alto ticket e boa conversão;
- criar alertas de faturamento em dashboard para acompanhar quedas importantes.

## 5) Recursos avançados do Superset

### Alertas

Configure alertas para monitorar:

- queda de faturamento mensal superior a 15%;
- regiões com vendas abaixo da média;
- produtos com desempenho inferior ao trimestre anterior.

### RLS (Row-Level Security)

Exemplo de regra de segurança por região:

```sql
regiao = 'Sudeste'
```

Isso garante que um usuário com perfil regional veja apenas os dados de sua área.

### Cache

Ative cache em dashboards de alta recorrência para reduzir carga de consultas e melhorar a performance.

## 6) Entrega esperada

O aluno deve entregar:

1. uma análise mínima em SQL;
2. pelo menos um gráfico montado a partir do SQL Lab;
3. uma narrativa em formato de storytelling;
4. uma recomendação clara com chamada para ação.

## 7) Execução final

Para finalizar a atividade, abra o Superset, conecte ao banco e monte os gráficos abaixo:

- faturamento por região;
- produtos com maior receita;
- evolução mensal do faturamento.

Depois, salve o dashboard com um nome como:

```text
Dashboard de Storytelling - NorthOne
```

Esse passo consolida a conexão entre SQL, visualização e comunicação de insights.
