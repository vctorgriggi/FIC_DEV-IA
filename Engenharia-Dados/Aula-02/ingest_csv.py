import csv

import psycopg2

DB_HOST = "localhost"
DB_NAME = "Aula02"
DB_USER = "postgres"
DB_PASSWORD = "postgres"


def ingest_csv_to_postgres(csv_file_path, table_name):
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )
        cur = conn.cursor()

        # Criar tabela se não existir
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INT PRIMARY KEY,
                nome VARCHAR(100),
                preco NUMERIC(10, 2)
            );
        """)
        conn.commit()

        with open(csv_file_path, "r") as f:
            reader = csv.reader(f)
            header = next(reader)  # Pula o cabeçalho
            for row in reader:
                cur.execute(
                    f"INSERT INTO {table_name} (id, nome, preco) VALUES (%s, %s, %s)",
                    row,
                )
        conn.commit()
        print(
            f"Dados do CSV '{csv_file_path}' ingeridos com sucesso na tabela '{table_name}'."
        )

    except Exception as e:
        print(f"Erro ao ingerir dados CSV: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()


if __name__ == "__main__":
    ingest_csv_to_postgres("produtos.csv", "produtos_csv")
