# consulta_cep.py — Consultor de CEP via API ViaCEP
# API pública, gratuita e sem autenticação
# Documentação: https://viacep.com.br
"""Consulta endereços brasileiros a partir de CEPs usando a API ViaCEP.
Suporta múltiplas consultas em sequência e trata os erros comuns:
CEP inválido, não encontrado, timeout e erro de rede.
"""

from __future__ import annotations

import re

import requests

# Constantes
BASE_URL = "https://viacep.com.br/ws/{cep}/json/"
TIMEOUT = 8  # segundos


def limpar_cep(cep_raw: str) -> str:
    """Remove traços, pontos e espaços do CEP, retornando apenas dígitos."""
    return re.sub(r"\D", "", cep_raw)


def validar_cep(cep: str) -> bool:
    """Verifica se o CEP tem exatamente 8 dígitos numéricos."""
    return len(cep) == 8 and cep.isdigit()


def consultar_cep(cep: str) -> dict | None:
    """Consulta a API ViaCEP e retorna os dados do endereço.

    Args:
            cep: CEP com 8 dígitos numéricos (sem formatação).

    Returns:
            Dicionário com os campos do endereço, ou ``None`` em caso de erro.
    """
    url = BASE_URL.format(cep=cep)
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        dados = resp.json()
        # ViaCEP retorna {"erro": true} para CEPs válidos mas inexistentes
        if dados.get("erro"):
            return None
        return dados
    except requests.exceptions.HTTPError as e:
        status = getattr(e.response, "status_code", "?")
        print(f"Erro HTTP {status}: {e}")
    except requests.exceptions.ConnectionError:
        print("Erro de conexão: verifique sua internet.")
    except requests.exceptions.Timeout:
        print(f"Timeout: servidor demorou mais de {TIMEOUT}s.")
    except requests.exceptions.RequestException as e:
        print(f"Erro inesperado: {e}")
    return None


def exibir_endereco(dados: dict) -> None:
    """Exibe os dados do endereço de forma formatada no terminal."""
    cep_fmt = dados.get("cep", "—")
    linhas = [
        ("CEP", cep_fmt),
        ("Logradouro", dados.get("logradouro", "—")),
        ("Complemento", dados.get("complemento") or "—"),
        ("Bairro", dados.get("bairro", "—")),
        ("Cidade", dados.get("localidade", "—")),
        ("Estado", dados.get("uf", "—")),
        ("IBGE", dados.get("ibge", "—")),
        ("DDD", dados.get("ddd", "—")),
    ]

    print()
    print(" " + "=" * 44)
    for campo, valor in linhas:
        print(f" {campo:<14}: {valor}")
    print(" " + "=" * 44)


def main() -> None:
    """Loop principal: aceita múltiplas consultas até o usuário sair."""
    print("=" * 48)
    print(" CONSULTOR DE CEP — ViaCEP")
    print(" Digite um CEP para buscar o endereço.")
    print(" Formatos aceitos: 01310-100 ou 01310100")
    print(" Digite 'sair' para encerrar.")
    print("=" * 48)

    while True:
        entrada = input("\nCEP: ").strip()
        if entrada.lower() in ("sair", "exit", "q"):
            print("Encerrando. Até logo!")
            break

        cep = limpar_cep(entrada)
        if not validar_cep(cep):
            print(f'CEP inválido: "{entrada}" — informe 8 dígitos numéricos.')
            continue

        print(f"Consultando CEP {cep[:5]}-{cep[5:]}...", end="", flush=True)
        dados = consultar_cep(cep)
        if dados:
            exibir_endereco(dados)
        else:
            print()
            print(f"CEP {cep[:5]}-{cep[5:]} não encontrado na base dos Correios.")


if __name__ == "__main__":
    main()
