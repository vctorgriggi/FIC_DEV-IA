"""Motor de OCR para imagens e PDFs escaneados."""

import os
from typing import Any

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

try:
    from pdf2image import convert_from_path
    from pdf2image.pdf2image import pdfinfo_from_path
except ImportError:
    convert_from_path = None
    pdfinfo_from_path = None

CONFIG_TESS = "--oem 3 --psm 6 -l por"
DPI_PADRAO = 300


def _prep_pillow(img: Image.Image) -> Image.Image:
    """Aplica pre-processamento leve para imagens limpas."""
    img = img.convert("L")
    img = ImageEnhance.Contrast(img).enhance(2.0)
    img = ImageEnhance.Sharpness(img).enhance(2.0)
    img = img.filter(ImageFilter.SHARPEN)

    largura, altura = img.size
    if largura < 2000:
        fator = 2000 / largura
        img = img.resize(
            (int(largura * fator), int(altura * fator)),
            Image.Resampling.LANCZOS,
        )
    return img


def _prep_opencv(img: Image.Image) -> Image.Image:
    """Aplica pre-processamento robusto para imagens dificeis."""
    arr = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2GRAY)
    arr = cv2.fastNlMeansDenoising(arr, h=10)
    arr = cv2.adaptiveThreshold(
        arr,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        10,
    )
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    arr = cv2.morphologyEx(arr, cv2.MORPH_OPEN, kernel)
    return Image.fromarray(arr)


def _ler_imagem(caminho: str) -> Image.Image:
    if not os.path.isfile(caminho):
        raise FileNotFoundError(f"arquivo nao encontrado: {caminho}")
    with Image.open(caminho) as img:
        return img.convert("RGB")


def ocr_imagem(caminho: str, modo: str = "auto") -> dict[str, Any]:
    """Extrai texto de uma imagem usando Pillow, OpenCV ou fallback automatico."""
    if modo not in ("pillow", "opencv", "auto"):
        raise ValueError("modo deve ser 'pillow', 'opencv' ou 'auto'")

    img_original = _ler_imagem(caminho)
    if modo == "opencv":
        texto = pytesseract.image_to_string(
            _prep_opencv(img_original), config=CONFIG_TESS
        )
        modo_usado = "opencv"
    else:
        texto = pytesseract.image_to_string(
            _prep_pillow(img_original), config=CONFIG_TESS
        )
        modo_usado = "pillow"
        if modo == "auto" and len(texto.strip()) < 200:
            texto = pytesseract.image_to_string(
                _prep_opencv(img_original), config=CONFIG_TESS
            )
            modo_usado = "opencv (fallback)"

    texto = texto.strip()
    return {
        "arquivo": os.path.basename(caminho),
        "modo_usado": modo_usado,
        "texto": texto,
        "caracteres": len(texto),
    }


def ocr_pdf(caminho: str, dpi: int = DPI_PADRAO) -> dict[str, Any]:
    """Extrai texto de todas as paginas de um PDF escaneado."""
    if convert_from_path is None:
        raise ImportError("pdf2image nao instalado. Execute: pip install pdf2image")
    if not os.path.isfile(caminho):
        raise FileNotFoundError(f"arquivo nao encontrado: {caminho}")
    if dpi <= 0:
        raise ValueError("dpi deve ser maior que zero")

    total_paginas = int(pdfinfo_from_path(caminho)["Pages"])
    paginas = []
    for numero in range(1, total_paginas + 1):
        imagens = convert_from_path(
            caminho,
            dpi=dpi,
            fmt="png",
            first_page=numero,
            last_page=numero,
        )
        img = imagens[0]
        texto = pytesseract.image_to_string(
            _prep_pillow(img), config=CONFIG_TESS
        ).strip()
        paginas.append({"pagina": numero, "texto": texto, "caracteres": len(texto)})
        print(f"OCR pagina {numero}/{total_paginas}: {len(texto)} caracteres")

    texto_completo = "\n\n".join(pagina["texto"] for pagina in paginas)
    return {
        "arquivo": os.path.basename(caminho),
        "total_paginas": len(paginas),
        "paginas": paginas,
        "texto_completo": texto_completo,
        "caracteres": len(texto_completo),
    }


def extrair_texto(caminho: str, **kwargs: Any) -> dict[str, Any]:
    """Detecta o tipo do arquivo e chama o extrator correspondente."""
    extensao = os.path.splitext(caminho)[1].lower()
    if extensao == ".pdf":
        resultado = ocr_pdf(caminho, **kwargs)
        resultado["texto"] = resultado["texto_completo"]
        return resultado
    return ocr_imagem(caminho, **kwargs)
