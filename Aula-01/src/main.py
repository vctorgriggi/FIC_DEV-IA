# Mini-lab Aula 01 — Demonstração com a biblioteca rich
from rich import box
from rich.console import Console
from rich.table import Table

console = Console()

# ---- Título ----
console.print()
console.print("[bold blue]Curso Python para IA[/bold blue] — Aula 01", justify="center")
console.print(
    "[italic]Principais bibliotecas Python para Machine Learning[/italic]",
    justify="center",
)
console.print()

# ---- Tabela ----
tabela = Table(
    box=box.ROUNDED, show_header=True, header_style="bold white on dark_blue"
)
tabela.add_column("Biblioteca", style="bold cyan", width=14)
tabela.add_column("Categoria", width=20)
tabela.add_column("Para que serve", width=38)
tabela.add_row(
    "NumPy", "Computação numérica", "Arrays multidimensionais e álgebra linear"
)
tabela.add_row(
    "Pandas", "Manipulação de dados", "DataFrames para análise e limpeza de dados"
)
tabela.add_row("Matplotlib", "Visualização", "Gráficos 2D estáticos e interativos")
tabela.add_row(
    "scikit-learn", "Machine Learning", "Algoritmos clássicos de ML prontos para uso"
)
tabela.add_row("TensorFlow", "Deep Learning", "Redes neurais em larga escala (Google)")
tabela.add_row("PyTorch", "Deep Learning", "Redes neurais flexíveis (Meta AI)")

console.print(tabela)
console.print()
console.print(
    "[green]Ambiente configurado com sucesso![/green] Bem-vindo ao Curso Python para IA."
)
console.print()
