CREATE TABLE IF NOT EXISTS vendas_teste (
    id SERIAL PRIMARY KEY,
    data_venda DATE NOT NULL,
    produto VARCHAR(50) NOT NULL,
    valor NUMERIC(10, 2) NOT NULL CHECK (valor >= 0)
);

INSERT INTO vendas_teste (data_venda, produto, valor)
SELECT dados.data_venda, dados.produto, dados.valor
FROM (VALUES
    (DATE '2023-10-01', 'Produto A', 150.00::NUMERIC),
    (DATE '2023-10-02', 'Produto B', 200.50::NUMERIC),
    (DATE '2023-10-03', 'Produto A', 120.00::NUMERIC)
) AS dados(data_venda, produto, valor)
WHERE NOT EXISTS (SELECT 1 FROM vendas_teste);
