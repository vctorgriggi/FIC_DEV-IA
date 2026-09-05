import psycopg2
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("clip-ViT-B-32")

# Texto de busca digitado pelo usuário
termo_busca = "um felino doméstico preguiçoso"
print(f"Buscando imagens para: '{termo_busca}'...")

# O modelo transforma o TEXTO em um vetor de 512 números!
vetor_texto = model.encode(termo_busca).tolist()

conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="postgres",
    host="localhost",
)
cur = conn.cursor()

# Consulta SQL no pgvector usando Distância Cosseno (<=>)
query = """
SELECT titulo, url_ou_caminho, embedding <=> %s AS distancia
FROM catalogo_imagens
ORDER BY distancia ASC
LIMIT 2;
"""
cur.execute(query, (str(vetor_texto),))
resultados = cur.fetchall()

print("\n--- Resultados mais semelhantes ---")
for titulo, url, distancia in resultados:
    print(f"Foto: {titulo} | Distância Cosseno: {distancia:.4f}")

cur.close()
conn.close()
