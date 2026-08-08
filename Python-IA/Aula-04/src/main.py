def validar_nome(nome: str) -> str:
    nome = nome.capitalize().strip()

    if not nome:
        raise ValueError("O nome não pode ser vazio.")

    if not nome.isalpha():
        raise ValueError("O nome não pode conter números ou caracteres especiais.")

    return nome


def validar_peso(peso: float) -> float:
    if peso <= 0 or peso > 500:
        raise ValueError("O peso deve ser maior que 0 e menor ou igual a 500.")

    return peso


def validar_altura(altura: float) -> float:
    if altura <= 0 or altura > 3:
        raise ValueError("A altura deve ser maior que 0 e menor ou igual a 3 metros.")

    return altura


def calcular_imc(peso: float, altura: float) -> float:
    return peso / (altura**2)


def classificar_imc(imc: float) -> str:
    if imc < 18.5:
        return "Abaixo do peso"
    elif 18.5 <= imc < 24.9:
        return "Peso normal"
    elif 25 <= imc < 29.9:
        return "Sobrepeso"
    elif 30 <= imc < 34.9:
        return "Obesidade grau I"
    elif 35 <= imc < 39.9:
        return "Obesidade grau II"
    else:
        return "Obesidade grau III"


def main():
    try:
        nome = input("Digite seu nome: ")
        nome = validar_nome(nome)

        peso = float(input("Digite seu peso (kg): "))
        peso = validar_peso(peso)

        altura = float(input("Digite sua altura (m): "))
        altura = validar_altura(altura)

        imc = calcular_imc(peso, altura)
        classificacao = classificar_imc(imc)

        print(f"\nOi, {nome}!")
        print(f"Seu IMC é: {imc:.2f}")
        print(f"Classificação: {classificacao}")

    except ValueError as e:
        print(f"Erro: {e}")


if __name__ == "__main__":
    main()
