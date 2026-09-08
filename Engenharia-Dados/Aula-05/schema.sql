CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS produtos_master (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255),
    descricao TEXT,
    categoria VARCHAR(100),
    embedding vector(3)
);

CREATE TABLE IF NOT EXISTS avaliacoes_raw (
    id SERIAL PRIMARY KEY,
    dados JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS avaliacoes_processadas (
    id SERIAL PRIMARY KEY,
    produto_id INT REFERENCES produtos_master(id),
    cliente_id VARCHAR(50),
    avaliacao INT,
    comentario TEXT,
    sentimento VARCHAR(20)
);

CREATE INDEX IF NOT EXISTS produtos_master_embedding_idx
    ON produtos_master USING ivfflat (embedding vector_cosine_ops);
