def formatar_percentual(valor):
    if valor is None or valor == "":
        return ""

    # garante float
    valor = float(valor)

    # converte para padrão BR
    return f"{valor:.2f}".replace(".", ",")