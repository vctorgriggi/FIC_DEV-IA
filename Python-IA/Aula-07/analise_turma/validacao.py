# analise_turma/validacao.py
# Responsabilidade: validar os dados antes do processamento.


def nota_valida(nota: float) -> bool:
    """Retorna True se a nota estiver no intervalo [0.0, 10.0]."""
    return 0.0 <= nota <= 10.0


def validar_aluno(aluno: dict) -> list[str]:
    """Valida os campos de um aluno e retorna uma lista de erros encontrados.

    Args:
        aluno: Dicionário com os dados do aluno.

    Returns:
        Lista de strings descrevendo os erros. Vazia se o aluno for válido.
    """
    erros = []

    if not aluno.get("nome", "").strip():
        erros.append('campo "nome" ausente ou vazio')

    notas = aluno.get("notas", [])
    if not notas:
        erros.append('campo "notas" ausente ou vazio')
    else:
        for i, nota in enumerate(notas):
            if not nota_valida(nota):
                erros.append(f"nota[{i}] = {nota} fora do intervalo [0, 10]")

    return erros


if __name__ == "__main__":
    # Teste rápido do módulo
    aluno_ok = {"nome": "Ana", "notas": [8.0, 9.0]}
    aluno_ruim = {"nome": "", "notas": [8.0, 12.0]}

    print("Aluno OK:", validar_aluno(aluno_ok))  # []
    print("Aluno ruim:", validar_aluno(aluno_ruim))  # ['nome vazio', 'nota fora']
