DROP TABLE IF EXISTS chamados_servicos;

CREATE TABLE chamados_servicos (
    id SERIAL PRIMARY KEY,
    protocolo VARCHAR(20) NOT NULL UNIQUE,
    cidadao_nome VARCHAR(100) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    regiao VARCHAR(30) NOT NULL,
    bairro VARCHAR(60) NOT NULL,
    data_abertura DATE NOT NULL,
    data_limite_sla DATE NOT NULL,
    data_conclusao DATE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('Concluido', 'Em Andamento', 'Pendente')),
    nota_avaliacao INTEGER CHECK (nota_avaliacao BETWEEN 1 AND 5),
    custo_reparo NUMERIC(10, 2)
);

INSERT INTO chamados_servicos
    (protocolo, cidadao_nome, categoria, regiao, bairro, data_abertura,
     data_limite_sla, data_conclusao, status, nota_avaliacao, custo_reparo)
VALUES
    ('2024-00101', 'Carlos Eduardo Lima', 'Iluminacao Publica', 'Zona Norte', 'Santana', '2024-01-05', '2024-01-10', '2024-01-08', 'Concluido', 5, 250.00),
    ('2024-00102', 'Beatriz Ferreira', 'Pavimentacao', 'Zona Leste', 'Itaquera', '2024-01-07', '2024-01-17', '2024-01-14', 'Concluido', 4, 1850.00),
    ('2024-00103', 'Renato Vieira', 'Limpeza Urbana', 'Centro', 'Se', '2024-01-08', '2024-01-11', '2024-01-09', 'Concluido', 5, 180.00),
    ('2024-00104', 'Juliana Rocha', 'Poda de Arvores', 'Zona Sul', 'Santo Amaro', '2024-01-10', '2024-01-20', '2024-01-16', 'Concluido', 5, 450.00),
    ('2024-00105', 'Fernando Dias', 'Drenagem', 'Zona Oeste', 'Lapa', '2024-01-12', '2024-01-22', '2024-01-19', 'Concluido', 4, 2100.00),
    ('2024-00106', 'Aline Morales', 'Iluminacao Publica', 'Centro', 'Republica', '2024-01-14', '2024-01-19', '2024-01-16', 'Concluido', 5, 120.00),
    ('2024-00107', 'Marcos Aurelio', 'Pavimentacao', 'Zona Norte', 'Tucuruvi', '2024-01-15', '2024-01-25', '2024-01-22', 'Concluido', 4, 3200.00),
    ('2024-00108', 'Camila Nogueira', 'Limpeza Urbana', 'Zona Sul', 'Vila Mariana', '2024-01-18', '2024-01-21', '2024-01-20', 'Concluido', 5, 200.00),
    ('2024-00109', 'Diego Fagundes', 'Iluminacao Publica', 'Zona Leste', 'Tatuape', '2024-01-20', '2024-01-25', '2024-01-23', 'Concluido', 4, 310.00),
    ('2024-00110', 'Patricia Mendes', 'Poda de Arvores', 'Zona Oeste', 'Pinheiros', '2024-01-22', '2024-02-01', '2024-01-28', 'Concluido', 5, 520.00),
    ('2024-00111', 'Lucas Silveira', 'Pavimentacao', 'Zona Sul', 'Grajau', '2024-01-03', '2024-01-13', '2024-01-22', 'Concluido', 2, 4500.00),
    ('2024-00112', 'Tatiane Castro', 'Drenagem', 'Zona Leste', 'Sao Mateus', '2024-01-06', '2024-01-16', '2024-01-27', 'Concluido', 3, 5800.00),
    ('2024-00113', 'Roberto Guimaraes', 'Iluminacao Publica', 'Zona Norte', 'Brasilândia', '2024-01-09', '2024-01-14', '2024-01-20', 'Concluido', 3, 340.00),
    ('2024-00114', 'Vanessa Ribeiro', 'Limpeza Urbana', 'Zona Leste', 'Guaianases', '2024-01-11', '2024-01-14', '2024-01-19', 'Concluido', 2, 600.00),
    ('2024-00115', 'Rodrigo Ramos', 'Pavimentacao', 'Centro', 'Bela Vista', '2024-01-13', '2024-01-23', '2024-01-30', 'Concluido', 3, 1900.00),
    ('2024-00116', 'Claudia Peixoto', 'Pavimentacao', 'Zona Oeste', 'Butanta', '2024-01-26', '2024-02-05', NULL, 'Em Andamento', NULL, 2800.00),
    ('2024-00117', 'Thiago Barbosa', 'Drenagem', 'Zona Sul', 'Campo Limpo', '2024-01-27', '2024-02-06', NULL, 'Em Andamento', NULL, 3900.00),
    ('2024-00118', 'Sandra Helena', 'Poda de Arvores', 'Centro', 'Consolacao', '2024-01-28', '2024-02-07', NULL, 'Em Andamento', NULL, 480.00),
    ('2024-00119', 'Felipe Fontana', 'Iluminacao Publica', 'Zona Leste', 'Penha', '2024-01-29', '2024-02-03', NULL, 'Em Andamento', NULL, 290.00),
    ('2024-00120', 'Adriana Paiva', 'Limpeza Urbana', 'Zona Norte', 'Jacana', '2024-01-29', '2024-02-01', NULL, 'Pendente', NULL, NULL),
    ('2024-00121', 'Gustavo Siqueira', 'Pavimentacao', 'Zona Leste', 'Sapopemba', '2024-01-30', '2024-02-09', NULL, 'Pendente', NULL, NULL),
    ('2024-00122', 'Monique Farias', 'Iluminacao Publica', 'Zona Oeste', 'Perdizes', '2024-01-30', '2024-02-04', NULL, 'Pendente', NULL, NULL),
    ('2024-00123', 'Sergio Antunes', 'Drenagem', 'Zona Norte', 'Vila Nova Cachoeirinha', '2024-01-31', '2024-02-10', NULL, 'Pendente', NULL, NULL),
    ('2024-00124', 'Priscila Prado', 'Poda de Arvores', 'Zona Sul', 'Jabaquara', '2024-01-31', '2024-02-10', NULL, 'Pendente', NULL, NULL);

CREATE OR REPLACE VIEW kpis_atendimento AS
SELECT
    COUNT(*) AS total_chamados,
    COUNT(*) FILTER (WHERE status = 'Concluido') AS total_concluidos,
    ROUND(COUNT(*) FILTER (WHERE status = 'Concluido') * 100.0 / COUNT(*), 2) AS taxa_resolucao_pct,
    ROUND(AVG(data_conclusao - data_abertura) FILTER (WHERE status = 'Concluido'), 1) AS tma_dias,
    ROUND(COUNT(*) FILTER (WHERE status = 'Concluido' AND data_conclusao <= data_limite_sla) * 100.0 /
          NULLIF(COUNT(*) FILTER (WHERE status = 'Concluido'), 0), 2) AS aderencia_sla_pct,
    ROUND(AVG(nota_avaliacao) FILTER (WHERE nota_avaliacao IS NOT NULL), 1) AS satisfacao_media,
    ROUND(COUNT(*) FILTER (WHERE status IN ('Pendente', 'Em Andamento')) * 100.0 / COUNT(*), 2) AS taxa_backlog_pct
FROM chamados_servicos;
