CREATE TABLE IF NOT EXISTS produtos_story (
    id SERIAL PRIMARY KEY,
    nome_produto VARCHAR(100) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    preco_unitario NUMERIC(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS clientes_story (
    id SERIAL PRIMARY KEY,
    nome_cliente VARCHAR(100) NOT NULL,
    regiao VARCHAR(50) NOT NULL,
    canal VARCHAR(30) NOT NULL
);

CREATE TABLE IF NOT EXISTS vendas_story (
    id SERIAL PRIMARY KEY,
    produto_id INT NOT NULL REFERENCES produtos_story(id),
    cliente_id INT NOT NULL REFERENCES clientes_story(id),
    data_venda DATE NOT NULL,
    valor NUMERIC(10,2) NOT NULL,
    quantidade INT NOT NULL,
    regiao VARCHAR(50) NOT NULL,
    canal VARCHAR(30) NOT NULL
);

INSERT INTO produtos_story (nome_produto, categoria, preco_unitario)
VALUES
    ('CRM Pro', 'Software', 899.00),
    ('Dashboard Plus', 'Analytics', 1299.00),
    ('DataFlow', 'ETL', 1199.00),
    ('Marketing AI', 'IA', 1599.00),
    ('Support Cloud', 'Serviço', 499.00)
ON CONFLICT DO NOTHING;

INSERT INTO clientes_story (nome_cliente, regiao, canal)
VALUES
    ('Alpha Tech', 'Sudeste', 'Digital'),
    ('Beta Log', 'Sul', 'Direto'),
    ('Celta SA', 'Nordeste', 'Revenda'),
    ('Delta Ltda', 'Norte', 'Digital'),
    ('Eco Move', 'Centro-Oeste', 'Direto'),
    ('Foco Group', 'Sudeste', 'Digital'),
    ('Geral Ops', 'Sul', 'Revenda'),
    ('Helix S/A', 'Nordeste', 'Digital'),
    ('Innova Corp', 'Norte', 'Direto'),
    ('Jupiter One', 'Centro-Oeste', 'Digital')
ON CONFLICT DO NOTHING;

INSERT INTO vendas_story (produto_id, cliente_id, data_venda, valor, quantidade, regiao, canal)
VALUES
    (1, 1, '2025-01-12', 1798.00, 2, 'Sudeste', 'Digital'),
    (2, 2, '2025-01-15', 2598.00, 2, 'Sul', 'Direto'),
    (3, 3, '2025-02-04', 2398.00, 2, 'Nordeste', 'Revenda'),
    (4, 4, '2025-02-18', 3198.00, 2, 'Norte', 'Digital'),
    (5, 5, '2025-03-10', 998.00, 2, 'Centro-Oeste', 'Direto'),
    (1, 6, '2025-03-20', 899.00, 1, 'Sudeste', 'Digital'),
    (2, 7, '2025-04-05', 3897.00, 3, 'Sul', 'Revenda'),
    (3, 8, '2025-04-22', 2398.00, 2, 'Nordeste', 'Digital'),
    (4, 9, '2025-05-15', 7995.00, 5, 'Norte', 'Direto'),
    (5, 10, '2025-05-29', 1497.00, 3, 'Centro-Oeste', 'Digital'),
    (1, 1, '2025-06-02', 2697.00, 3, 'Sudeste', 'Digital'),
    (2, 3, '2025-06-18', 5196.00, 4, 'Nordeste', 'Revenda'),
    (3, 5, '2025-07-10', 2398.00, 2, 'Centro-Oeste', 'Direto'),
    (4, 2, '2025-07-20', 6396.00, 4, 'Sul', 'Direto'),
    (5, 8, '2025-08-03', 1996.00, 4, 'Nordeste', 'Digital'),
    (1, 7, '2025-08-12', 1798.00, 2, 'Sul', 'Revenda'),
    (2, 9, '2025-09-07', 3897.00, 3, 'Norte', 'Direto'),
    (3, 10, '2025-09-26', 3597.00, 3, 'Centro-Oeste', 'Digital'),
    (4, 6, '2025-10-11', 1599.00, 1, 'Sudeste', 'Digital'),
    (5, 4, '2025-10-30', 2495.00, 5, 'Norte', 'Digital');

CREATE INDEX IF NOT EXISTS idx_vendas_data ON vendas_story(data_venda);
CREATE INDEX IF NOT EXISTS idx_vendas_regiao ON vendas_story(regiao);
CREATE INDEX IF NOT EXISTS idx_vendas_canal ON vendas_story(canal);
