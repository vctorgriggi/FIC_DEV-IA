"""Interface de linha de comando do digitalizador."""

import argparse
import os
import sys

import pipeline

EXTENSOES_SUPORTADAS = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".pdf")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Digitaliza documentos escaneados via OCR + NLP."
    )
    parser.add_argument(
        "arquivo", help="Caminho para imagem PNG/JPEG/TIFF ou PDF escaneado."
    )
    parser.add_argument(
        "--saida",
        default="resultados",
        help="Diretorio de saida (padrao: resultados/).",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Quantidade de termos frequentes (padrao: 20).",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.arquivo):
        parser.error(f"arquivo nao encontrado: {args.arquivo}")
    extensao = os.path.splitext(args.arquivo)[1].lower()
    if extensao not in EXTENSOES_SUPORTADAS:
        parser.error(f"formato nao suportado: {extensao}")
    if args.top < 0:
        parser.error("--top nao pode ser negativo")

    try:
        resultado = pipeline.processar_documento(
            args.arquivo, dir_saida=args.saida, top_n=args.top
        )
        pipeline.exibir_resumo(resultado)
    except (FileNotFoundError, ImportError, OSError, ValueError) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
