# analise_turma/__init__.py
# Re-exporta os nomes que o usuário do pacote vai precisar.
# Quem importar 'analise_turma' não precisa saber em qual
# módulo interno cada função está definida.

from analise_turma.calculos import aprovado, media
from analise_turma.relatorio import processar_e_exibir
from analise_turma.validacao import validar_aluno

__version__ = "1.0.0"

__all__ = [
    "media",
    "aprovado",
    "validar_aluno",
    "processar_e_exibir",
]
