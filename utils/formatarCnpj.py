def formatar_cpf_cnpj(valor: str) -> str:
    if not valor:
        return ""

    numeros = "".join(filter(str.isdigit, valor))

    if len(numeros) == 11:  # CPF
        return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
    
    elif len(numeros) == 14:  # CNPJ
        return f"{numeros[:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:12]}-{numeros[12:]}"
    
    return valor  # fallback se vier estranho