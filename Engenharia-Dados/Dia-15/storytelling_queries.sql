-- Resumo geral
SELECT
    SUM(valor) AS faturamento_total,
    ROUND(AVG(valor), 2) AS ticket_medio,
    COUNT(*) AS total_vendas
FROM vendas_story;

-- Faturamento por região
SELECT
    regiao,
    ROUND(SUM(valor), 2) AS faturamento
FROM vendas_story
GROUP BY regiao
ORDER BY faturamento DESC;

-- Produtos com maior faturamento
SELECT
    p.nome_produto,
    SUM(v.valor) AS faturamento,
    SUM(v.quantidade) AS unidades_vendidas
FROM vendas_story v
JOIN produtos_story p ON p.id = v.produto_id
GROUP BY p.nome_produto
ORDER BY faturamento DESC;

-- Evolução mensal
SELECT
    TO_CHAR(data_venda, 'YYYY-MM') AS mes,
    ROUND(SUM(valor), 2) AS faturamento
FROM vendas_story
GROUP BY TO_CHAR(data_venda, 'YYYY-MM')
ORDER BY mes;

-- Performance por canal
SELECT
    canal,
    ROUND(SUM(valor), 2) AS faturamento,
    COUNT(*) AS numero_vendas
FROM vendas_story
GROUP BY canal
ORDER BY faturamento DESC;

-- Comparativo de clientes por região
SELECT
    c.regiao,
    COUNT(DISTINCT c.id) AS clientes_ativos,
    ROUND(SUM(v.valor), 2) AS faturamento
FROM clientes_story c
LEFT JOIN vendas_story v ON v.cliente_id = c.id
GROUP BY c.regiao
ORDER BY faturamento DESC;

-- Exemplo de filtro para RLS (Região Sudeste)
SELECT *
FROM vendas_story
WHERE regiao = 'Sudeste';

-- Exemplo de alerta: regiões que ficaram abaixo de 30% da média
WITH media AS (
    SELECT AVG(faturamento) AS valor_medio
    FROM (
        SELECT SUM(valor) AS faturamento
        FROM vendas_story
        GROUP BY regiao
    ) t
)
SELECT
    regiao,
    ROUND(SUM(valor), 2) AS faturamento
FROM vendas_story
GROUP BY regiao
HAVING SUM(valor) < (SELECT valor_medio * 0.7 FROM media)
ORDER BY faturamento;
