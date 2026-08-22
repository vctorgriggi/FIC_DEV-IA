# Digitalizador de documentos

Projeto da Aula 14 para extrair texto de imagens e PDFs escaneados com Tesseract e analisar o resultado com spaCy.

## Dependencias

```bash
python -m pip install -r requirements.txt
python -m spacy download pt_core_news_sm
```

No Linux, instale tambem o executavel do Tesseract e o Poppler pelo gerenciador do sistema. No Windows, o caminho padrao do Tesseract configurado em `init.py` e `C:\Program Files\Tesseract-OCR\tesseract.exe`.

## Uso

Inicialize os recursos do NLTK uma vez:

```bash
python init.py
```

Processe uma imagem:

```bash
python main.py exemplos/contrato.png
```

Processe um PDF e escolha a pasta de saida:

```bash
python main.py exemplos/relatorio.pdf --saida resultados --top 30
```

O programa gera texto bruto, texto limpo e metadados JSON na pasta indicada.

## Modulos

- `ocr_engine.py`: pre-processamento com Pillow/OpenCV e OCR de imagens/PDFs.
- `nlp_engine.py`: limpeza, lematizacao, frequencia e entidades nomeadas.
- `pipeline.py`: orquestracao e salvamento dos resultados.
- `main.py`: interface de linha de comando.
