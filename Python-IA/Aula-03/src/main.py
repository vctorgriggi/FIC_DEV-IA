# Conceitos: listas, dicts, sets, JSON, iteração, comprehensions

import json
import sys

ARQUIVO_JSON = "src/data/db.json"
ARQUIVO_SAIDA = "src/data/out.json"

# ─── 1. Leitura do arquivo JSON ─────────────────────────────
# Conceito: json.load(), with open(), try/except
try:
    with open(ARQUIVO_JSON, "r", encoding="utf-8") as f:
        dados = json.load(f)
except FileNotFoundError:
    print(f'Erro: arquivo "{ARQUIVO_JSON}" não encontrado.')
    print("Crie o arquivo src/data/db.json na pasta do projeto.")
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"Erro: JSON inválido — {e}")
    sys.exit(1)

# Extrair os campos principais do dicionário raiz
nome_turma = dados["turma"]
professor = dados["professor"]
nota_aprovacao = dados["nota_aprovacao"]
alunos = dados["alunos"]  # lista de dicionários

# ─── 2. Processamento ───────────────────────────────────────
# Conceito: list, dict, set, for, operador ternário
resultados = []  # lista de dicts com dados processados
todas_medias = []  # lista de floats para calcular estatísticas
cursos_vistos = set()  # set: cada curso aparece apenas uma vez

for aluno in alunos:  # itera sobre lista de dicts
    notas = aluno["notas"]  # lista de floats
    media = sum(notas) / len(notas)  # média aritmética simples
    status = "Aprovado" if media >= nota_aprovacao else "Reprovado"
    curso = aluno["curso"]

    # Acumular resultado deste aluno como dicionário
    resultados.append(
        {
            "id": aluno["id"],
            "nome": aluno["nome"],
            "curso": curso,
            "media": round(media, 2),
            "status": status,
        }
    )

    todas_medias.append(media)  # acumula para estatísticas
    cursos_vistos.add(curso)  # set ignora duplicatas

# ─── 3. Estatísticas ────────────────────────────────────────
# Conceito: sum/max/min em listas, list comprehension, lambda
media_turma = sum(todas_medias) / len(todas_medias)
nota_max = max(todas_medias)
nota_min = min(todas_medias)

# List comprehensions para filtrar aprovados e reprovados
aprovados = [r for r in resultados if r["status"] == "Aprovado"]
reprovados = [r for r in resultados if r["status"] == "Reprovado"]

# max/min com key=lambda: critério de comparação customizado
melhor = max(resultados, key=lambda r: r["media"])
pior = min(resultados, key=lambda r: r["media"])

# ─── 4. Exibição do relatório ───────────────────────────────
# Conceito: f-strings com formatação de largura e casas decimais
sep = "=" * 57
print(f"\n{sep}")
print(" RELATÓRIO DE TURMA")
print(f" {nome_turma}")
print(f" Professor: {professor}")
print(f" Nota de aprovação: {nota_aprovacao}")
print(sep)

# 4.1 — Tabela de alunos ordenada por média (maior → menor)
print(f"\n {'ALUNO':<22} {'CURSO':<26} {'MÉDIA':>6} STATUS")
print(f" {'-' * 22} {'-' * 26} {'-' * 6} {'-' * 9}")

# sorted() com lambda: ordena lista de dicts por um campo específico
for r in sorted(resultados, key=lambda r: r["media"], reverse=True):
    icone = "✓" if r["status"] == "Aprovado" else "✗"
    print(f" {r['nome']:<22} {r['curso']:<26} {r['media']:>6.2f} {icone} {r['status']}")

# 4.2 — Estatísticas gerais
print(f"\n{sep}")
print(" ESTATÍSTICAS DA TURMA")
print(sep)
print(f" Total de alunos : {len(alunos)}")
print(f" Aprovados : {len(aprovados)} ({len(aprovados) / len(alunos) * 100:.0f}%)")
print(f" Reprovados : {len(reprovados)} ({len(reprovados) / len(alunos) * 100:.0f}%)")
print(f" Média da turma : {media_turma:.2f}")
print(f" Maior média : {nota_max:.2f} — {melhor['nome']}")
print(f" Menor média : {nota_min:.2f} — {pior['nome']}")

# 4.3 — Distribuição por curso (usando o set de cursos)
print(f"\n Cursos na turma ({len(cursos_vistos)}):")
for curso in sorted(cursos_vistos):  # sorted() aceita set
    qtd = sum(1 for r in resultados if r["curso"] == curso)
    aprov_curso = sum(1 for r in aprovados if r["curso"] == curso)
    print(f" • {curso}: {qtd} aluno(s) | {aprov_curso} aprovado(s)")

# ─── 5. Exportar relatório como JSON ────────────────────────
# Conceito: json.dump(), dict aninhado, ensure_ascii=False
relatorio = {
    "turma": nome_turma,
    "professor": professor,
    "total_alunos": len(alunos),
    "aprovados": len(aprovados),
    "reprovados": len(reprovados),
    "media_turma": round(media_turma, 2),
    "melhor_aluno": melhor["nome"],
    "pior_aluno": pior["nome"],
    "cursos": sorted(cursos_vistos),
    "resultados": resultados,
}

with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
    json.dump(relatorio, f, indent=2, ensure_ascii=False)

print(f"\n{sep}")
print(f" Relatório exportado → {ARQUIVO_SAIDA}")
print(f"{sep}\n")
