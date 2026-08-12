# extrator.py
"""
Extrator de Dados com Regex
Pipeline: TXT → Extração (CPF/Telefone/Email) → CSV + JSON
Trilha Python para IA - Aula 06
"""

import csv
import json
import re
from datetime import datetime
from pathlib import Path

# ─── Configuração de caminhos ────────────────────────────────
# __file__ é o caminho do script atual
RAIZ = Path(__file__).parent
ENTRADA = RAIZ / "contatos.txt"
SAIDA = RAIZ / "saida"


# ─── Padrões regex compilados (reutilização eficiente) ───────
# CPF: 123.456.789-09 ou 12345678909
# Grupos de captura: (3 dígitos)(3 dígitos)(3 dígitos)(2 dígitos)
PADRAO_CPF = re.compile(r"\b(\d{3})[.\s]?(\d{3})[.\s]?(\d{3})[-\s]?(\d{2})\b")

# Telefone: (11) 9 8765-4321, (21)98765-1234, 11 987654321, 11912345678
PADRAO_TEL = re.compile(r"\(?\d{2}\)?[\s.-]?9?[\s.-]?\d{4}[\s.-]?\d{4}")

# E-mail: ana@email.com, ana.paula@empresa.com.br, carla.mendes1990@hotmail.com
PADRAO_EMAIL = re.compile(
    r"[\w.+_-]+@[\w-]+(?:\.[\w-]+)*\.[a-zA-Z]{2,}",
    re.IGNORECASE,
)


# ─── Funções de arquivo ──────────────────────────────────────
def ler_arquivo(caminho: Path) -> str:
    """
    Lê o conteúdo de um arquivo de texto.

    Args:
        caminho: Path para o arquivo.

    Returns:
        Conteúdo do arquivo como string.

    Raises:
        FileNotFoundError: Se o arquivo não existir.
    """
    print(f"\n📖 Lendo arquivo: {caminho.name}")

    try:
        # read_text() do pathlib abre e fecha o arquivo automaticamente
        conteudo = caminho.read_text(encoding="utf-8")
        print(f"✅ {len(conteudo)} caracteres lidos")
        return conteudo
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {caminho}")
        raise
    except UnicodeDecodeError:
        print("❌ Erro de encoding. Tentando com 'latin-1'...")
        return caminho.read_text(encoding="latin-1")


def salvar_csv(registros: list, caminho: Path) -> None:
    """
    Salva registros em arquivo CSV.

    Args:
        registros: Lista de dicionários com os dados.
        caminho: Path para o arquivo CSV.
    """
    if not registros:
        print("⚠ Nenhum registro para salvar em CSV")
        return

    # Criar diretório pai se não existir
    caminho.parent.mkdir(parents=True, exist_ok=True)

    # Definir campos na ordem desejada
    campos = ["cpf", "telefone", "email"]

    with open(caminho, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(registros)

    print(f"✅ CSV salvo: {caminho} ({len(registros)} registros)")


def salvar_json(dados: dict, caminho: Path) -> None:
    """
    Salva dados em arquivo JSON.

    Args:
        dados: Dicionário com os dados a serializar.
        caminho: Path para o arquivo JSON.
    """
    caminho.parent.mkdir(parents=True, exist_ok=True)

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    print(f"✅ JSON salvo: {caminho}")


def salvar_metadados(dados: dict, caminho: Path) -> None:
    """
    Salva um resumo dos dados em formato texto.

    Args:
        dados: Dicionário com os dados.
        caminho: Path para o arquivo de metadados.
    """
    caminho.parent.mkdir(parents=True, exist_ok=True)

    with open(caminho, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("RELATÓRIO DE EXTRAÇÃO\n")
        f.write("=" * 60 + "\n\n")

        f.write(f"Data da extração: {datetime.now()}\n\n")

        f.write(f"Total de CPFs: {dados['total_cpfs']}\n")
        f.write(f"Total de Telefones: {dados['total_telefones']}\n")
        f.write(f"Total de E-mails: {dados['total_emails']}\n\n")

        f.write("CPFs encontrados:\n")
        for cpf in dados["cpfs"]:
            f.write(f"  • {cpf}\n")

        f.write("\nTelefones encontrados:\n")
        for tel in dados["telefones"]:
            f.write(f"  • {tel}\n")

        f.write("\nE-mails encontrados:\n")
        for email in dados["emails"]:
            f.write(f"  • {email}\n")

    print(f"✅ Metadados salvos: {caminho}")


# ─── Funções de extração ─────────────────────────────────────
def extrair_cpfs(texto: str) -> list:
    """
    Extrai CPFs e normaliza para o formato NNN.NNN.NNN-NN.

    Args:
        texto: Texto desestruturado de entrada.

    Returns:
        Lista de CPFs únicos normalizados.
    """
    cpfs = []

    for match in PADRAO_CPF.finditer(texto):
        d1, d2, d3, d4 = match.groups()
        cpf_normalizado = f"{d1}.{d2}.{d3}-{d4}"

        if cpf_normalizado not in cpfs:
            cpfs.append(cpf_normalizado)

    return cpfs


def extrair_telefones(texto: str) -> list:
    """
    Extrai telefones únicos do texto.

    Args:
        texto: Texto desestruturado de entrada.

    Returns:
        Lista de telefones únicos.
    """
    telefones = []

    for match in PADRAO_TEL.finditer(texto):
        tel = match.group().strip()

        if tel not in telefones:
            telefones.append(tel)

    return telefones


def extrair_emails(texto: str) -> list:
    """
    Extrai e-mails únicos em letras minúsculas.

    Args:
        texto: Texto desestruturado de entrada.

    Returns:
        Lista de e-mails únicos em minúsculas.
    """
    emails = []

    for match in PADRAO_EMAIL.finditer(texto):
        email = match.group().lower()

        if email not in emails:
            emails.append(email)

    return emails


def processar_texto(texto: str) -> dict:
    """
    Processa o texto extraindo todos os dados estruturados.

    Args:
        texto: Texto completo do arquivo.

    Returns:
        Dicionário com todos os dados extraídos.
    """
    print("\n🔎 Processando texto...")

    # Extrair dados do texto inteiro
    cpfs = extrair_cpfs(texto)
    telefones = extrair_telefones(texto)
    emails = extrair_emails(texto)

    # Criar registros alinhados (um registro por pessoa),
    # dividindo o texto por blocos numerados (1., 2., ...)
    registros = []
    blocos = re.split(r"\n\d+\.\s+", texto)

    for bloco in blocos[1:]:  # o primeiro pedaço é o cabeçalho
        registro = {"cpf": None, "telefone": None, "email": None}

        cpfs_bloco = extrair_cpfs(bloco)
        if cpfs_bloco:
            registro["cpf"] = cpfs_bloco[0]

        # Um CPF sem pontuação (11 dígitos) também casa com PADRAO_TEL,
        # então o trecho do CPF sai do bloco antes de procurar o telefone.
        match_cpf = PADRAO_CPF.search(bloco)
        bloco_sem_cpf = bloco.replace(match_cpf.group(), "", 1) if match_cpf else bloco

        tels_bloco = extrair_telefones(bloco_sem_cpf)
        if tels_bloco:
            registro["telefone"] = tels_bloco[0]

        emails_bloco = extrair_emails(bloco)
        if emails_bloco:
            registro["email"] = emails_bloco[0]

        if any([registro["cpf"], registro["telefone"], registro["email"]]):
            registros.append(registro)

    return {
        "total_cpfs": len(cpfs),
        "total_telefones": len(telefones),
        "total_emails": len(emails),
        "cpfs": cpfs,
        "telefones": telefones,
        "emails": emails,
        "registros": registros,
    }


def exibir_resumo(dados: dict) -> None:
    """
    Exibe um resumo formatado dos dados extraídos.

    Args:
        dados: Dicionário com os dados extraídos.
    """
    print("\n" + "=" * 60)
    print("  RELATÓRIO DE EXTRAÇÃO - REGEX PIPELINE")
    print("=" * 60)

    print("\n📊 ESTATÍSTICAS:")
    print(f"  • CPFs encontrados:      {dados['total_cpfs']}")
    print(f"  • Telefones encontrados: {dados['total_telefones']}")
    print(f"  • E-mails encontrados:   {dados['total_emails']}")

    print(f"\n🆔 CPFs ({dados['total_cpfs']}):")
    for cpf in dados["cpfs"]:
        print(f"  • {cpf}")

    print(f"\n📞 Telefones ({dados['total_telefones']}):")
    for tel in dados["telefones"]:
        print(f"  • {tel}")

    print(f"\n✉ E-mails ({dados['total_emails']}):")
    for email in dados["emails"]:
        print(f"  • {email}")

    print(f"\n👥 Registros agrupados ({len(dados['registros'])}):")
    for i, reg in enumerate(dados["registros"], 1):
        print(f"\n  {i}. CPF:      {reg['cpf'] or 'N/A'}")
        print(f"     Telefone: {reg['telefone'] or 'N/A'}")
        print(f"     Email:    {reg['email'] or 'N/A'}")

    print("\n" + "=" * 60)


# ─── Desafios extras ─────────────────────────────────────────
def validar_cpf(cpf: str) -> bool:
    """
    Valida matematicamente um CPF.

    Args:
        cpf: CPF no formato NNN.NNN.NNN-NN ou NNNNNNNNNNN.

    Returns:
        True se os dígitos verificadores estiverem corretos.
    """
    # Remover pontuação
    cpf = re.sub(r"[^0-9]", "", cpf)

    # Verificar tamanho e dígitos repetidos
    if len(cpf) != 11 or len(set(cpf)) == 1:
        return False

    # Calcular primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = 11 - (soma % 11)
    if digito1 >= 10:
        digito1 = 0

    # Calcular segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = 11 - (soma % 11)
    if digito2 >= 10:
        digito2 = 0

    return digito1 == int(cpf[9]) and digito2 == int(cpf[10])


def extrair_cpfs_validos(texto: str) -> list:
    """
    Extrai e valida CPFs matematicamente.

    Args:
        texto: Texto desestruturado.

    Returns:
        Lista de CPFs válidos normalizados.
    """
    cpfs = []

    for match in PADRAO_CPF.finditer(texto):
        d1, d2, d3, d4 = match.groups()
        cpf_normalizado = f"{d1}.{d2}.{d3}-{d4}"

        if validar_cpf(cpf_normalizado) and cpf_normalizado not in cpfs:
            cpfs.append(cpf_normalizado)

    return cpfs


def normalizar_telefone(telefone: str) -> str:
    """
    Normaliza um telefone para o formato padrão.

    Args:
        telefone: Telefone em qualquer formato.

    Returns:
        Telefone normalizado no formato (XX) XXXXX-XXXX.
    """
    # Remover tudo que não é dígito
    digitos = re.sub(r"[^0-9]", "", telefone)

    if len(digitos) == 10:  # Fixo: (XX) XXXX-XXXX
        return f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"
    elif len(digitos) == 11:  # Celular: (XX) XXXXX-XXXX
        return f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"
    else:
        return telefone  # Retorna original se não reconhecer


def processar_texto_normalizado(texto: str) -> dict:
    """Versão de processar_texto() com normalização dos telefones."""
    dados = processar_texto(texto)

    # Normalizar a lista geral de telefones (sem duplicar)
    telefones = []
    for tel in dados["telefones"]:
        normalizado = normalizar_telefone(tel)
        if normalizado not in telefones:
            telefones.append(normalizado)

    dados["telefones"] = telefones
    dados["total_telefones"] = len(telefones)

    # Normalizar os telefones dentro de cada registro
    for registro in dados["registros"]:
        if registro["telefone"]:
            registro["telefone"] = normalizar_telefone(registro["telefone"])

    return dados


# ─── Função principal ────────────────────────────────────────
def main():
    """Função principal do pipeline."""
    print("\n🚀 INICIANDO PIPELINE DE EXTRAÇÃO DE DADOS")
    print("=" * 60)
    print(f"📁 Diretório do script: {RAIZ}")
    print(f"📄 Arquivo de entrada:  {ENTRADA}")
    print(f"📁 Pasta de saída:      {SAIDA}")

    # 1. Ler arquivo
    try:
        texto = ler_arquivo(ENTRADA)
    except FileNotFoundError:
        print("❌ Pipeline interrompido: arquivo não encontrado")
        return

    # 2. Processar e extrair dados (com telefones normalizados)
    dados = processar_texto_normalizado(texto)

    # 3. Exibir resumo
    exibir_resumo(dados)

    # 4. Salvar resultados
    print("\n💾 SALVANDO RESULTADOS...")
    salvar_csv(dados["registros"], SAIDA / "contatos.csv")
    salvar_json(dados, SAIDA / "contatos_completo.json")
    salvar_metadados(dados, SAIDA / "relatorio.txt")

    print("\n✅ Pipeline concluído com sucesso!")


if __name__ == "__main__":
    main()
