# analise_turma/calculos.py
# Responsabilidade: cálculos sobre listas de notas.
# Este módulo não lê arquivos, não imprime nada, não interage com o usuário.


def media(notas: list[float]) -> float:
    """Calcula a média aritmética de uma lista de notas.

    Args:
        notas: Lista de notas em ponto flutuante.

    Returns:
        A média aritmética das notas.

    Raises:
        ValueError: Se a lista de notas estiver vazia.
    """
    if not notas:
        raise ValueError("A lista de notas não pode ser vazia.")
    return sum(notas) / len(notas)


def aprovado(media: float, minimo: float = 7.0) -> bool:
    """Retorna True se a média for igual ou superior ao mínimo.

    Args:
        media:  Média calculada do aluno.
        minimo: Nota mínima para aprovação (padrão: 7.0).

    Returns:
        True se aprovado, False caso contrário.
    """
    return media >= minimo


if __name__ == "__main__":
    # Testes rápidos — executados só ao rodar: python calculos.py
    notas_teste = [8.0, 9.0, 6.5]
    m = media(notas_teste)
    print(f"Média de teste: {m:.2f}")
    print(f"Aprovado: {aprovado(m)}")
