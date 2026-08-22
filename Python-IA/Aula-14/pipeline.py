"""Orquestracao do OCR, NLP e salvamento dos resultados."""

import json
import os
from datetime import datetime
from typing import Any

import nlp_engine
import ocr_engine


def processar_documento(
    caminho_entrada: str, dir_saida: str = ".", top_n: int = 20
) -> dict[str, Any]:
    """Executa OCR, analise NLP e salva textos e metadados em JSON."""
    os.makedirs(dir_saida, exist_ok=True)
    nome_base = os.path.splitext(os.path.basename(caminho_entrada))[0]
    prefixo = f"{nome_base}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    resultado_ocr = ocr_engine.extrair_texto(caminho_entrada)
    texto_bruto = resultado_ocr["texto"]
    resultado_nlp = nlp_engine.analisar(texto_bruto, top_n=top_n)

    arq_bruto = os.path.join(dir_saida, f"{prefixo}_bruto.txt")
    arq_limpo = os.path.join(dir_saida, f"{prefixo}_limpo.txt")
    arq_json = os.path.join(dir_saida, f"{prefixo}_metadados.json")

    with open(arq_bruto, "w", encoding="utf-8") as arquivo:
        arquivo.write(texto_bruto)
    with open(arq_limpo, "w", encoding="utf-8") as arquivo:
        arquivo.write(resultado_nlp["texto_limpo"])

    metadados = {
        "arquivo_origem": caminho_entrada,
        "processado_em": datetime.now().isoformat(),
        "ocr": {
            "caracteres_brutos": resultado_ocr["caracteres"],
            "modo_usado": resultado_ocr.get("modo_usado", "n/a"),
        },
        "nlp": {
            "total_palavras": resultado_nlp["total_palavras"],
            "total_tokens": resultado_nlp["total_tokens"],
            "vocabulario_unico": resultado_nlp["vocabulario_unico"],
            "top_termos": resultado_nlp["top_termos"],
            "entidades": resultado_nlp["entidades"],
        },
        "saidas": {"texto_bruto": arq_bruto, "texto_limpo": arq_limpo},
    }
    with open(arq_json, "w", encoding="utf-8") as arquivo:
        json.dump(metadados, arquivo, ensure_ascii=False, indent=2)

    return {**resultado_ocr, **resultado_nlp, "metadados": metadados}


def exibir_resumo(resultado: dict[str, Any]) -> None:
    """Imprime um resumo legivel do processamento."""
    print("\n" + "=" * 56)
    print("  RESUMO DO PROCESSAMENTO")
    print("=" * 56)
    print(f"  Arquivo       : {resultado['arquivo']}")
    print(f"  Caracteres    : {resultado['caracteres']}")
    print(f"  Palavras      : {resultado['total_palavras']}")
    print(f"  Tokens unicos : {resultado['vocabulario_unico']}\n")
    print("  Top 10 termos mais frequentes:")
    for indice, (termo, frequencia) in enumerate(resultado["top_termos"][:10], 1):
        print(f"    {indice:2}. {termo:<20} {frequencia}x")
    if resultado["entidades"]:
        print("\n  Entidades reconhecidas:")
        for tipo, lista in sorted(resultado["entidades"].items()):
            print(f"    {tipo:<8}: {', '.join(lista[:5])}")
    print("=" * 56)
