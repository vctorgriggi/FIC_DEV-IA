# =============================================================
# benchmark_numpy.py — Normalização e benchmark NumPy vs listas
# Trilha Python para IA — Aula 08
# Autor: Pedro Clarindo da Silva Neto
# =============================================================
"""
Pipeline de normalização de dados numéricos com NumPy.
Compara desempenho de operações vetoriais vs listas Python.
"""

import timeit
from pathlib import Path

import numpy as np

# ── Configuração ─────────────────────────────────────────
np.random.seed(42)  # reprodutibilidade
N_AMOSTRAS = 100_000  # 100 mil amostras
N_FEATURES = 50  # 50 features por amostra
N_REPETICOES = 10  # repetições para o benchmark


# ── 1. Gerar dataset sintético ────────────────────────────
def gerar_dataset(n: int, f: int) -> np.ndarray:
    """Gera dataset sintético simulando features de ML.

    Combina distribuições distintas para simular
    a variedade de escalas comum em dados reais.

    Args:
        n: Número de amostras.
        f: Número de features.

    Returns:
        Array (n, f) com os dados gerados.
    """
    # Features em escalas muito diferentes (problema real)
    parte1 = np.random.randn(n, f // 2) * 100  # escala ~100
    parte2 = np.random.rand(n, f - f // 2) * 0.01  # escala ~0.01
    return np.hstack([parte1, parte2])


# ── 2. Funções de normalização ────────────────────────────
def normalizar_minmax(arr: np.ndarray) -> np.ndarray:
    """Normaliza cada coluna para o intervalo [0, 1].

    Args:
        arr: Array 2D (amostras, features).

    Returns:
        Array normalizado com os mesmos shape e dtype.
    """
    col_min = arr.min(axis=0)  # mínimo de cada coluna
    col_max = arr.max(axis=0)  # máximo de cada coluna
    amplitude = col_max - col_min
    # Evitar divisão por zero em colunas constantes
    amplitude[amplitude == 0] = 1
    return (arr - col_min) / amplitude


def padronizar_zscore(arr: np.ndarray) -> np.ndarray:
    """Padroniza cada coluna para média 0 e desvio padrão 1.

    Args:
        arr: Array 2D (amostras, features).

    Returns:
        Array padronizado com os mesmos shape e dtype.
    """
    media = arr.mean(axis=0)
    dp = arr.std(axis=0)
    dp[dp == 0] = 1  # evitar divisão por zero
    return (arr - media) / dp


# ── 3. Validação dos resultados ───────────────────────────
def validar_normalizacao(arr_norm: np.ndarray, nome: str) -> None:
    """Exibe estatísticas de validação de um array normalizado.

    Args:
        arr_norm: Array após normalização.
        nome: Nome da técnica para exibição.
    """
    print(f"\n {nome}")
    print(f" Shape : {arr_norm.shape}")
    print(f" Min : {arr_norm.min():.6f}")
    print(f" Max : {arr_norm.max():.6f}")
    print(f" Média : {arr_norm.mean():.6f}")
    print(f" Desvio : {arr_norm.std():.6f}")


# ── 4. Benchmark: NumPy vs lista Python ───────────────────
def benchmark_soma(n: int, repeticoes: int) -> dict:
    """Compara tempo de soma vetorial entre NumPy e lista Python.

    Args:
        n: Número de elementos.
        repeticoes: Quantas vezes repetir para a média.

    Returns:
        Dict com tempos em segundos para cada abordagem.
    """
    arr_np = np.random.rand(n)
    lista_py = arr_np.tolist()  # converte para lista Python
    # Soma com NumPy — vetorizada, em C
    t_numpy = (
        timeit.timeit(
            stmt=lambda: arr_np.sum(),
            number=repeticoes,
        )
        / repeticoes
    )
    # Soma com lista Python — loop interpretado
    t_lista = (
        timeit.timeit(
            stmt=lambda: sum(lista_py),
            number=repeticoes,
        )
        / repeticoes
    )
    return {
        "numpy_s": t_numpy,
        "lista_s": t_lista,
        "speedup": t_lista / t_numpy,
    }


def benchmark_operacao_vetorial(n: int, repeticoes: int) -> dict:
    """Compara multiplicação elemento a elemento: NumPy vs lista.

    Args:
        n: Número de elementos.
        repeticoes: Quantas vezes repetir para a média.

    Returns:
        Dict com tempos e fator de aceleração.
    """
    a_np = np.random.rand(n)
    b_np = np.random.rand(n)
    a_py = a_np.tolist()
    b_py = b_np.tolist()
    # NumPy: vetorizado
    t_numpy = (
        timeit.timeit(
            stmt=lambda: a_np * b_np,
            number=repeticoes,
        )
        / repeticoes
    )
    # Python: list comprehension (a forma mais rápida com listas)
    t_lista = (
        timeit.timeit(
            stmt=lambda: [a_py[i] * b_py[i] for i in range(n)],
            number=repeticoes,
        )
        / repeticoes
    )
    return {
        "numpy_s": t_numpy,
        "lista_s": t_lista,
        "speedup": t_lista / t_numpy,
    }


# ── 5. Pipeline principal ─────────────────────────────────
def main() -> None:
    """Executa o pipeline completo de normalização e benchmark."""
    print("=" * 55)
    print(" PIPELINE: NORMALIZAÇÃO + BENCHMARK NUMPY vs LISTAS")
    print("=" * 55)
    # Gerar dados
    print(f"\nGerando dataset: {N_AMOSTRAS:,} amostras × {N_FEATURES} features...")
    dados = gerar_dataset(N_AMOSTRAS, N_FEATURES)
    print(f"Shape : {dados.shape}")
    print(f"dtype : {dados.dtype}")
    print(f"Memória : {dados.nbytes / 1024 / 1024:.1f} MB")
    print(f"Min original: {dados.min():.4f}")
    print(f"Max original: {dados.max():.4f}")
    # Normalizar
    print("\n" + "-" * 55)
    print("VALIDAÇÃO DAS NORMALIZAÇÕES (valores por coluna)")
    print("-" * 55)
    norm_mm = normalizar_minmax(dados)
    validar_normalizacao(norm_mm, "Min-Max")
    norm_zs = padronizar_zscore(dados)
    validar_normalizacao(norm_zs, "Z-Score")
    # Benchmark
    print("\n" + "-" * 55)
    print(f"BENCHMARK ({N_AMOSTRAS:,} elementos, {N_REPETICOES} repetições)")
    print("-" * 55)
    print("\n Teste 1: soma vetorial (np.sum vs sum())")
    r1 = benchmark_soma(N_AMOSTRAS, N_REPETICOES)
    print(f" NumPy : {r1['numpy_s'] * 1000:.3f} ms")
    print(f" Lista : {r1['lista_s'] * 1000:.3f} ms")
    print(f" NumPy é {r1['speedup']:.1f}x mais rápido")
    print("\n Teste 2: multiplicação elemento a elemento")
    r2 = benchmark_operacao_vetorial(N_AMOSTRAS, N_REPETICOES)
    print(f" NumPy : {r2['numpy_s'] * 1000:.3f} ms")
    print(f" Lista : {r2['lista_s'] * 1000:.3f} ms")
    print(f" NumPy é {r2['speedup']:.1f}x mais rápido")
    # Salvar resultado normalizado
    saida = Path("dados_normalizados.npy")
    np.save(saida, norm_zs)
    print(f"\nArray normalizado salvo em: {saida.resolve()}")
    print("(Use np.load('dados_normalizados.npy') para carregar)")
    print("\n" + "=" * 55)
    print("Pipeline concluído com sucesso!")
    print("=" * 55)


if __name__ == "__main__":
    main()
