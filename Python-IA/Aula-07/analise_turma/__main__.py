# analise_turma/__main__.py
# Executado quando o usuário roda: python -m analise_turma

import sys
from pathlib import Path

from analise_turma.relatorio import processar_e_exibir


def main() -> None:
    """Ponto de entrada do pacote analise_turma."""
    if len(sys.argv) < 2:
        # Caminho padrão se nenhum argumento for informado
        caminho = Path("data") / "turma.json"
    else:
        caminho = Path(sys.argv[1])

    processar_e_exibir(caminho)


if __name__ == "__main__":
    main()
