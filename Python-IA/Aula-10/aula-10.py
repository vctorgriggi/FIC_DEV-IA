# ============================================================
# PASSO 0 — Criação dos dados (em um projeto real, seriam lidos
# de arquivos: pd.read_csv('cadastro.csv'), etc.)
# ============================================================

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

plt.rcParams["figure.dpi"] = 120
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False

# --- cadastro.csv ---
cadastro = pd.DataFrame(
    {
        "id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "nome": [
            "Ana",
            "Bruno",
            "Carla",
            "Diego",
            "Elena",
            "Fabio",
            "Gabi",
            "Hugo",
            "Ines",
            "Joao",
        ],
        "turma": ["A", "A", "A", "A", "B", "B", "B", "B", "C", "C"],
        "idade": [15, 16, 15, 16, 15, 17, 15, 16, 16, 15],
    }
)

# --- notas.csv (uma linha por aluno por bimestre) ---
notas = pd.DataFrame(
    {
        "id": [
            1,
            1,
            1,
            1,
            2,
            2,
            2,
            2,
            3,
            3,
            3,
            3,
            4,
            4,
            4,
            4,
            5,
            5,
            5,
            5,
            6,
            6,
            6,
            6,
            7,
            7,
            7,
            7,
            8,
            8,
            8,
            8,
            9,
            9,
            9,
            9,
            10,
            10,
            10,
            10,
        ],
        "bimestre": ["1B", "2B", "3B", "4B"] * 10,
        "nota": [
            8.0,
            8.5,
            7.5,
            9.0,
            5.0,
            5.5,
            6.0,
            5.0,
            9.5,
            9.0,
            9.5,
            10.0,
            4.0,
            4.5,
            5.0,
            4.0,
            7.0,
            7.5,
            8.0,
            7.5,
            6.5,
            7.0,
            6.0,
            7.5,
            8.5,
            9.0,
            8.5,
            9.5,
            3.5,
            4.0,
            4.5,
            3.0,
            7.5,
            8.0,
            7.0,
            8.5,
            6.0,
            6.5,
            5.5,
            7.0,
        ],
    }
)

# --- frequencia.csv ---
frequencia = pd.DataFrame(
    {
        "id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "total_aulas": [80] * 10,
        "faltas": [2, 15, 0, 20, 5, 10, 3, 25, 4, 12],
    }
)

# ============================================================
# PASSO 1 — Combinar os três DataFrames e calcular indicadores
# ============================================================

# 1a. Média final por aluno (pivot da tabela de notas)
media_por_aluno = notas.groupby("id")["nota"].mean().reset_index()
media_por_aluno.columns = ["id", "media_final"]
media_por_aluno["media_final"] = media_por_aluno["media_final"].round(2)

# 1b. Merge: cadastro + média + frequência
df = cadastro.merge(media_por_aluno, on="id", how="left").merge(
    frequencia, on="id", how="left"
)

# 1c. Calcular percentual de presença
df["presenca_pct"] = (
    (df["total_aulas"] - df["faltas"]) / df["total_aulas"] * 100
).round(1)

# 1d. Determinar situação do aluno (regra: média >= 7.0 E presença >= 75%)
df["situacao"] = df.apply(
    lambda row: (
        "Aprovado"
        if row["media_final"] >= 7.0 and row["presenca_pct"] >= 75
        else "Reprovado"
    ),
    axis=1,
)

print("=== Dataset Consolidado ===")
print(
    df[["nome", "turma", "media_final", "presenca_pct", "situacao"]].to_string(
        index=False
    )
)
print(f"\nAprovados: {(df.situacao == 'Aprovado').sum()}")
print(f"Reprovados: {(df.situacao == 'Reprovado').sum()}")

# ============================================================
# PASSO 2 — Reshape da tabela de notas para gráfico de linhas
# ============================================================

# Juntar turma ao DataFrame de notas
notas_turma = notas.merge(cadastro[["id", "turma"]], on="id")

# Média por turma e bimestre (formato longo — ideal para plot)
media_bim = (
    notas_turma.groupby(["turma", "bimestre"])["nota"].mean().round(2).reset_index()
)

# pivot_table: bimestres viram colunas
media_bim_wide = media_bim.pivot_table(
    values="nota", index="turma", columns="bimestre", aggfunc="mean"
).round(2)

print("=== Média por Turma e Bimestre ===")
print(media_bim_wide)

# ============================================================
# PASSO 3 — Figura com três subplots
# ============================================================

bimestres_ordem = ["1B", "2B", "3B", "4B"]
cores_turma = {"A": "#2E86C1", "B": "#E67E22", "C": "#27AE60"}
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("Análise de Desempenho Escolar", fontsize=15, fontweight="bold", y=1.02)

# ── Gráfico 1: Evolução das médias por turma (linha) ─────────
ax1 = axes[0]
for turma in ["A", "B", "C"]:
    dados = media_bim[media_bim["turma"] == turma]
    dados = dados.set_index("bimestre").reindex(bimestres_ordem)
    ax1.plot(
        bimestres_ordem,
        dados["nota"],
        marker="o",
        linewidth=2,
        color=cores_turma[turma],
        label=f"Turma {turma}",
    )

ax1.axhline(y=7.0, color="gray", linestyle="--", linewidth=1.2, label="Mín. aprovação")
ax1.set_title("Evolução por Bimestre", fontweight="bold")
ax1.set_xlabel("Bimestre")
ax1.set_ylabel("Média")
ax1.set_ylim(4, 10)
ax1.legend(fontsize=8)
ax1.grid(axis="y", alpha=0.35)

# ── Gráfico 2: Média final por aluno (barras horizontais) ─────
ax2 = axes[1]
df_sorted = df.sort_values("media_final")
cores_sit = df_sorted["situacao"].map({"Aprovado": "#27AE60", "Reprovado": "#E74C3C"})

barras = ax2.barh(
    df_sorted["nome"], df_sorted["media_final"], color=cores_sit, edgecolor="white"
)
ax2.axvline(x=7.0, color="gray", linestyle="--", linewidth=1.2)
ax2.set_title("Média Final por Aluno", fontweight="bold")
ax2.set_xlabel("Média Final")
ax2.set_xlim(0, 10)

for barra in barras:
    largura = barra.get_width()
    ax2.text(
        largura + 0.1,
        barra.get_y() + barra.get_height() / 2,
        f"{largura:.1f}",
        va="center",
        fontsize=8,
    )

# ── Gráfico 3: Distribuição das notas (histograma) ────────────
ax3 = axes[2]
# todas_notas = notas["nota"].values
todas_notas = notas["nota"].to_numpy()
n, bins, patches = ax3.hist(
    todas_notas, bins=12, color="#2E86C1", edgecolor="white", alpha=0.85
)
for patch, left_edge in zip(patches, bins[:-1]):
    if left_edge < 7.0:
        patch.set_facecolor("#E74C3C")

ax3.axvline(
    x=todas_notas.mean(),
    color="#1F3864",
    linewidth=2,
    label=f"Média: {todas_notas.mean():.2f}",
)
ax3.axvline(x=7.0, color="gray", linestyle="--", linewidth=1.5, label="Mín. aprovação")
ax3.set_title("Distribuição das Notas", fontweight="bold")
ax3.set_xlabel("Nota")
ax3.set_ylabel("Frequência")
ax3.legend(fontsize=8)

plt.tight_layout()
plt.savefig("analise_alunos.png", dpi=150, bbox_inches="tight", facecolor="white")
plt.show()
print("Gráfico salvo em: analise_alunos.png")

# ============================================================
# PASSO 4 — Preparar dataset para modelagem
# Meta: prever 'situacao' a partir de media_final, presenca e idade
# ============================================================

# 4a. Selecionando colunas relevantes
df_modelo = df[["turma", "idade", "media_final", "presenca_pct", "situacao"]].copy()

# 4b. One-Hot Encoding da variável categórica 'turma'
df_modelo = pd.get_dummies(df_modelo, columns=["turma"], prefix="turma", dtype=int)

# 4c. Label Encoding da variável alvo: Aprovado=1, Reprovado=0
df_modelo["alvo"] = df_modelo["situacao"].map({"Aprovado": 1, "Reprovado": 0})
df_modelo = df_modelo.drop(columns=["situacao"])

# 4d. Normalização das variáveis numéricas
colunas_num = ["idade", "media_final", "presenca_pct"]
scaler = StandardScaler()
df_modelo[colunas_num] = scaler.fit_transform(df_modelo[colunas_num])

# 4e. Separação features / alvo
X = df_modelo.drop(columns=["alvo"])
y = df_modelo["alvo"]

# 4f. Divisão treino/teste (80/20)
X_treino, X_teste, y_treino, y_teste = train_test_split(
    X, y, test_size=0.20, random_state=42
)

print("=== Dataset Preparado para IA ===")
print(f"Features: {X.columns.tolist()}")
print(f"Total amostras: {len(X)}")
print(f"Treino: {len(X_treino)} amostras")
print(f"Teste: {len(X_teste)} amostras")
print("\nPrimeiras linhas de X_treino:")
print(X_treino.round(3))

# 4g. Salvando dataset final
X_treino.to_csv("X_treino.csv", index=False)
X_teste.to_csv("X_teste.csv", index=False)
y_treino.to_csv("y_treino.csv", index=False, header=True)
y_teste.to_csv("y_teste.csv", index=False, header=True)
print("\nDatasets salvos: X_treino.csv, X_teste.csv, y_treino.csv, y_teste.csv")
