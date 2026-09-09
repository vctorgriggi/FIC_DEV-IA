CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS servicos_master (
    id SERIAL PRIMARY KEY,
    secretaria VARCHAR(100) NOT NULL,
    servico VARCHAR(100) NOT NULL,
    descricao TEXT,
    prazo_dias INT,
    embedding vector(3)
);

CREATE TABLE IF NOT EXISTS ouvidoria_raw (
    id SERIAL PRIMARY KEY,
    dados JSONB,
    data_recebimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ouvidoria_processada (
    id SERIAL PRIMARY KEY,
    protocolo VARCHAR(50) UNIQUE,
    bairro VARCHAR(100),
    relato TEXT,
    nivel_prioridade VARCHAR(20),
    servico_sugerido_id INT REFERENCES servicos_master(id),
    distancia_confianca FLOAT
);
