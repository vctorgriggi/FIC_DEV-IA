# analise_turma/relatorio.py
# Responsabilidade: leitura dos dados e exibição do relatório.

import json
from pathlib import Path

# Importações absolutas dos outros módulos do pacote
from analise_turma.calculos import aprovado, media
from analise_turma.validacao import validar_aluno


def carregar_turma(caminho: Path) -> dict:
    """Lê o arquivo JSON e retorna o dicionário de dados da turma.

    Args:
        caminho: Caminho do arquivo JSON.

    Returns:
        Dicionário com os dados da turma.

    Raises:
        FileNotFoundError: Se o arquivo não existir.
        json.JSONDecodeError: Se o JSON for inválido.
    """
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def processar_e_exibir(caminho: Path) -> None:
    """Carrega a turma, valida os dados, calcula as médias e exibe o relatório."""
    # 1. Carregar dados
    try:
        dados = carregar_turma(caminho)
    except FileNotFoundError:
        print(f"Erro: arquivo não encontrado: {caminho}")
        return
    except json.JSONDecodeError as e:
        print(f"Erro: JSON inválido em {caminho}: {e}")
        return

    nome_turma = dados["turma"]
    nota_aprovacao = dados.get("nota_aprovacao", 7.0)
    alunos = dados["alunos"]

    # 2. Processar cada aluno
    resultados = []
    for aluno in alunos:
        erros = validar_aluno(aluno)
        if erros:
            print(f"  Aviso: {aluno.get('nome', '?')} ignorado — {erros}")
            continue

        m = media(aluno["notas"])
        status = "Aprovado" if aprovado(m, nota_aprovacao) else "Reprovado"
        resultados.append(
            {
                "nome": aluno["nome"],
                "curso": aluno["curso"],
                "media": round(m, 2),
                "status": status,
            }
        )

    # 3. Exibir relatório
    sep = "=" * 55
    print(f"\n{sep}")
    print(f"  {nome_turma}")
    print(sep)
    print(f"  {'ALUNO':<22} {'CURSO':<22} {'MÉDIA':>6}  STATUS")
    print(f"  {'-' * 22} {'-' * 22} {'-' * 6}  {'-' * 9}")

    for r in sorted(resultados, key=lambda x: x["media"], reverse=True):
        icone = "✓" if r["status"] == "Aprovado" else "✗"
        print(
            f"  {r['nome']:<22} {r['curso']:<22} {r['media']:>6.2f}  {icone} {r['status']}"
        )

    aprovados = [r for r in resultados if r["status"] == "Aprovado"]
    reprovados = [r for r in resultados if r["status"] == "Reprovado"]
    print(
        f"\n  Total: {len(resultados)} | Aprovados: {len(aprovados)} | Reprovados: {len(reprovados)}"
    )
    print(f"{sep}\n")
