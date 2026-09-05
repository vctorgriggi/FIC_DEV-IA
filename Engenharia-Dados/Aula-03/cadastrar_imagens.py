import urllib.request

import psycopg2
from PIL import Image
from sentence_transformers import SentenceTransformer

# 1. Carrega o modelo multimodal CLIP
print("Carregando modelo CLIP...")
model = SentenceTransformer("clip-ViT-B-32")

# 2. Imagens de exemplo com URLs públicas
imagens_exemplo = [
    {
        "titulo": "Gato siamês descansando",
        "url": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=400",
    },
    {
        "titulo": "Cachorro golden retriever correndo",
        "url": "https://images.unsplash.com/photo-1552053831-71594a27632d?w=400",
    },
    {
        "titulo": "Carro esportivo vermelho",
        "url": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=400",
    },
    {
        "titulo": "Bicicleta vintage na cidade",
        "url": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=400",
    },
    {
        "titulo": "Praia paradisíaca com coqueiros",
        "url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400",
    },
]

# 3. Conexão com o PostgreSQL
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="postgres",
    host="localhost",
)
cur = conn.cursor()

print("Processando imagens e inserindo no pgvector...")
for item in imagens_exemplo:
    # Baixa a imagem temporariamente
    urllib.request.urlretrieve(item["url"], "temp.jpg")
    img = Image.open("temp.jpg")

    # O modelo CLIP transforma a imagem em um vetor de 512 números
    embedding_vetor = model.encode(img).tolist()

    # Insere no PostgreSQL
    cur.execute(
        "INSERT INTO catalogo_imagens (titulo, url_ou_caminho, embedding) VALUES (%s, %s, %s);",
        (item["titulo"], item["url"], str(embedding_vetor)),
    )

conn.commit()
cur.close()
conn.close()
print("Imagens cadastradas com sucesso!")
