# leitor_robusto.py
# Conceitos: try/except/finally, exceções customizadas, logging, Ruff

import csv
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# ─── Constantes ──────────────────────────────────────────────
ARQUIVO_CSV = "alunos.csv"
PASTA_LOGS = Path("logs")
ARQUIVO_LOG = PASTA_LOGS / "app.log"
NOTA_MIN = 0.0
NOTA_MAX = 10.0
MEDIA_APROVACAO = 7.0


# ─── Exceções customizadas ───────────────────────────────────
class DadosAlunoError(Exception):
    """Classe base para erros de validação de dados de alunos."""


class CampoObrigatorioError(DadosAlunoError):
    """Campo obrigatório ausente ou vazio."""

    def __init__(self, campo: str, linha: int):
        self.campo = campo
        self.linha = linha
        super().__init__(f"Linha {linha}: campo '{campo}' é obrigatório")


class NotaForaDoIntervaloError(DadosAlunoError):
    """Nota fora do intervalo permitido."""

    def __init__(self, campo: str, valor: float, linha: int):
        self.campo = campo
        self.valor = valor
        self.linha = linha
        super().__init__(
            f"Linha {linha}: '{campo}' = {valor} fora do intervalo "
            f"[{NOTA_MIN}, {NOTA_MAX}]"
        )


# ─── Configuração do logger ─────────────────────────────────
def configurar_logger() -> logging.Logger:
    """
    Logger com dois handlers:
    - Console: INFO e acima (sem DEBUG)
    - Arquivo rotativo: DEBUG e acima (histórico completo)
    """
    PASTA_LOGS.mkdir(exist_ok=True)  # cria pasta logs/ se não existir

    logger = logging.getLogger("leitor_robusto")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Handler 1: Console (INFO+)
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)

    # Handler 2: Arquivo rotativo (DEBUG+) — máx. 500 KB, 3 backups
    arquivo = RotatingFileHandler(
        ARQUIVO_LOG, maxBytes=500_000, backupCount=3, encoding="utf-8"
    )
    arquivo.setLevel(logging.DEBUG)
    arquivo.setFormatter(fmt)

    logger.addHandler(console)
    logger.addHandler(arquivo)
    return logger


logger = configurar_logger()


# ─── Validação de um registro ───────────────────────────────
def validar_aluno(row: dict, num_linha: int) -> dict:
    """
    Valida e converte um registro CSV em dicionário de aluno.
    Lança DadosAlunoError (ou filhas) se o registro for inválido.
    """
    logger.debug("Validando linha %d: %s", num_linha, row)

    # Validar campo 'nome'
    nome = (row.get("nome") or "").strip()
    if not nome:
        raise CampoObrigatorioError("nome", num_linha)

    # Validar campo 'curso'
    curso = (row.get("curso") or "").strip()
    if not curso:
        raise CampoObrigatorioError("curso", num_linha)

    # Converter e validar notas
    notas: list[float] = []
    for campo in ("nota1", "nota2", "nota3"):
        valor_str = (row.get(campo) or "").strip()

        if not valor_str:
            raise CampoObrigatorioError(campo, num_linha)

        try:
            nota = float(valor_str)
        except ValueError:
            raise ValueError(
                f"Linha {num_linha}: '{campo}' = '{valor_str}' não é numérico"
            ) from None

        if not (NOTA_MIN <= nota <= NOTA_MAX):
            raise NotaForaDoIntervaloError(campo, nota, num_linha)

        notas.append(nota)

    media = round(sum(notas) / len(notas), 2)

    return {
        "nome": nome,
        "curso": curso,
        "notas": notas,
        "media": media,
        "status": "Aprovado" if media >= MEDIA_APROVACAO else "Reprovado",
    }


# ─── Leitura do arquivo CSV ─────────────────────────────────
def ler_alunos(caminho: str) -> tuple[list[dict], list[dict]]:
    """
    Lê o CSV e retorna (registros_validos, erros).
    Cada erro é um dict com 'linha', 'tipo' e 'mensagem'.
    """
    validos: list[dict] = []
    erros: list[dict] = []

    logger.info("Iniciando leitura de '%s'", caminho)

    try:
        arquivo = open(caminho, newline="", encoding="utf-8")
    except FileNotFoundError:
        logger.error("Arquivo não encontrado: '%s'", caminho)
        return [], []
    except PermissionError:
        logger.error("Sem permissão para ler: '%s'", caminho)
        return [], []

    try:
        reader = csv.DictReader(arquivo)
        for num_linha, row in enumerate(reader, start=2):  # linha 1 = cabeçalho
            # Ignorar linhas completamente vazias
            if not any((v or "").strip() for v in row.values()):
                logger.debug("Linha %d ignorada (vazia)", num_linha)
                continue

            try:
                aluno = validar_aluno(row, num_linha)

            except CampoObrigatorioError as e:
                logger.warning("%s", e)
                erros.append(
                    {"linha": num_linha, "tipo": "CampoObrigatorio", "mensagem": str(e)}
                )

            except NotaForaDoIntervaloError as e:
                logger.warning("%s", e)
                erros.append(
                    {"linha": num_linha, "tipo": "NotaInvalida", "mensagem": str(e)}
                )

            except ValueError as e:
                logger.warning("%s", e)
                erros.append(
                    {"linha": num_linha, "tipo": "ValueError", "mensagem": str(e)}
                )

            except DadosAlunoError as e:
                # Captura qualquer outra filha de DadosAlunoError
                logger.error("Erro de validação inesperado: %s", e)
                erros.append(
                    {"linha": num_linha, "tipo": "Validacao", "mensagem": str(e)}
                )

            except Exception:
                logger.exception("Erro inesperado na linha %d", num_linha)
                erros.append(
                    {"linha": num_linha, "tipo": "Inesperado", "mensagem": "Ver log"}
                )

            else:
                # Só executa se validar_aluno() NÃO lançou exceção
                logger.debug(
                    "Linha %d OK: %s — média %.2f",
                    num_linha,
                    aluno["nome"],
                    aluno["media"],
                )
                validos.append(aluno)

    finally:
        arquivo.close()  # garante fechamento mesmo com exceção
        logger.debug("Arquivo '%s' fechado", caminho)

    logger.info("Leitura concluída: %d válidos, %d erros", len(validos), len(erros))
    return validos, erros


# ─── Relatório final ────────────────────────────────────────
def exibir_relatorio(validos: list[dict], erros: list[dict]) -> None:
    sep = "=" * 55
    print(f"\n{sep}")
    print(" RELATÓRIO — LEITOR ROBUSTO DE DADOS")
    print(sep)

    # Registros válidos
    print(f"\n {'ALUNO':<22} {'CURSO':<26} {'MÉDIA':>6} STATUS")
    print(f" {'-' * 22} {'-' * 26} {'-' * 6} {'-' * 9}")
    for a in sorted(validos, key=lambda x: x["media"], reverse=True):
        icone = "✓" if a["status"] == "Aprovado" else "✗"
        print(
            f" {a['nome']:<22} {a['curso']:<26} {a['media']:>6.2f} {icone} {a['status']}"
        )

    # Resumo
    total = len(validos) + len(erros)
    print(f"\n{sep}")
    print(" RESUMO DE QUALIDADE")
    print(sep)
    print(f" Total de linhas processadas : {total}")
    print(f" Registros válidos           : {len(validos)} ({len(validos) / total:.0%})")
    print(f" Registros com erro          : {len(erros)} ({len(erros) / total:.0%})")

    # Erros encontrados
    if erros:
        print("\n ERROS ENCONTRADOS:")
        for e in erros:
            print(f" Linha {e['linha']:>2} [{e['tipo']:>16}] {e['mensagem']}")

    print("\n Logs detalhados gravados em: logs/app.log")
    print(f"{sep}\n")


# ─── Ponto de entrada ───────────────────────────────────────
if __name__ == "__main__":
    logger.info("=== Início da execução ===")
    try:
        validos, erros = ler_alunos(ARQUIVO_CSV)
        if validos or erros:
            exibir_relatorio(validos, erros)
        else:
            logger.warning("Nenhum dado processado — verifique o arquivo CSV")
    except Exception:
        logger.exception("Erro fatal na execução principal")
        sys.exit(1)
    finally:
        logger.info("=== Fim da execução ===")
