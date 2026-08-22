import os

import nltk
import pytesseract


def configurar_recursos() -> None:
    """Garante que os recursos usados pelo projeto estejam disponíveis."""
    recursos = {
        "stopwords": "corpora/stopwords",
        "punkt": "tokenizers/punkt",
    }

    for recurso, caminho in recursos.items():
        try:
            nltk.data.find(caminho)
        except LookupError:
            nltk.download(recurso)

    if os.name == "nt":
        pytesseract.pytesseract.tesseract_cmd = (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )


configurar_recursos()
