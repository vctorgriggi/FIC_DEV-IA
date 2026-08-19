# baixar_pdf.py — Downloader robusto de PDF com streaming
"""
Baixa um arquivo PDF de uma URL pública usando streaming,
exibe progresso, valida o arquivo e informa o tamanho final.
Funciona com qualquer URL pública que retorne um PDF.
"""

from __future__ import annotations

import os
import sys
from urllib.parse import urlparse

import requests

# Constantes
# PDF da Pesquisa Nacional por Amostra de Domicílios — IBGE
URL_PDF = "https://biblioteca.ibge.gov.br/visualizacao/livros/liv101957_informativo.pdf"
CHUNK_KB = 512  # tamanho de cada chunk em KB
TIMEOUT = 60  # segundos


def inferir_nome(url: str, resp: requests.Response) -> str:
    """Infere o nome do arquivo a partir do header Content-Disposition ou da URL."""
    cd = resp.headers.get("Content-Disposition", "")
    # Tenta extrair filename com e sem aspas
    if "filename=" in cd:
        part = cd.split("filename=")[-1].strip()
        return part.strip('"').strip("'")
    nome = os.path.basename(urlparse(url).path)
    return nome if (nome and "." in nome) else "arquivo.pdf"


def barra_progresso(atual: int, total: int, largura: int = 36) -> str:
    """Retorna uma string de barra de progresso simples."""
    if total <= 0:
        return f"{atual / 1024:.0f} KB baixados"
    pct = float(atual) / float(total)
    cheio = int(pct * largura)
    cheio = max(0, min(cheio, largura))
    vazio = largura - cheio
    return f"[{'#' * cheio}{'.' * vazio}] {pct * 100:5.1f}% ({atual / (1024**2):.1f}/{total / (1024**2):.1f} MB)"


def validar_pdf(caminho: str) -> bool:
    """Verifica se o arquivo começa com a assinatura binária de PDF."""
    try:
        with open(caminho, "rb") as arq:
            cabecalho = arq.read(5)
        return cabecalho == b"%PDF-"
    except OSError:
        return False


def baixar_pdf(url: str, destino_dir: str = ".") -> str | None:
    """Baixa um PDF usando streaming e salva em destino_dir.

    Args:
        url: URL do PDF a baixar.
        destino_dir: Diretório onde salvar o arquivo.

    Returns:
        Caminho do arquivo salvo, ou ``None`` em caso de falha.
    """
    print(f"URL: {url}")
    print("Conectando...")

    # Cabeçalho User-Agent para evitar erro HTTP 403
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    try:
        with requests.get(url, headers=headers, stream=True, timeout=TIMEOUT) as resp:
            resp.raise_for_status()

            # Verificar Content-Type antes de baixar
            ct = resp.headers.get("Content-Type", "")
            if "html" in ct.lower():
                print("Erro: o servidor retornou HTML em vez de PDF.")
                print("Verifique se a URL está correta e acessível.")
                return None

            nome = inferir_nome(url, resp)
            destino = os.path.join(destino_dir, nome)
            total = int(resp.headers.get("Content-Length") or 0)
            chunk_sz = CHUNK_KB * 1024
            if total:
                print(f"Arquivo: {nome} ({total / (1024**2):.1f} MB)")
            else:
                print(f"Arquivo: {nome} (tamanho desconhecido)")

            baixado = 0
            with open(destino, "wb") as arq:
                for chunk in resp.iter_content(chunk_size=chunk_sz):
                    if not chunk:
                        continue
                    arq.write(chunk)
                    baixado += len(chunk)
                    print(f"\r{barra_progresso(baixado, total)}", end="", flush=True)

            print()  # quebra de linha após a barra
            return destino

    except requests.exceptions.HTTPError as e:
        status = getattr(e.response, "status_code", "?")
        print(f"\nErro HTTP {status}: acesso negado ou arquivo não existe.")
    except requests.exceptions.ConnectionError:
        print("\nErro de conexão. Verifique sua internet.")
    except requests.exceptions.Timeout:
        print(f"\nTimeout após {TIMEOUT}s. Tente novamente.")
    except requests.exceptions.RequestException as e:
        print(f"\nErro inesperado: {e}")

    return None


def main() -> None:
    print("=" * 52)
    print(" DOWNLOADER DE PDF — IBGE (público)")
    print("=" * 52)

    caminho = baixar_pdf(URL_PDF, destino_dir=".")
    if caminho is None:
        print("Download falhou.")
        sys.exit(1)

    # Validação pós-download
    tamanho_kb = os.path.getsize(caminho) / 1024
    if validar_pdf(caminho):
        print("Validacao: arquivo PDF valido.")
    else:
        print("Validacao: FALHOU — o arquivo nao parece ser um PDF valido.")

    print(f"Salvo em: {os.path.abspath(caminho)}")
    print(f"Tamanho: {tamanho_kb:.1f} KB")
    print("Concluido!")


if __name__ == "__main__":
    main()
