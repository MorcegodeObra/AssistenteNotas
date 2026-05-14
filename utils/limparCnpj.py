import re

def limpar_cnpj(cnpj):
    return re.sub(r"\D", "", cnpj or "")

def verificarCnpj(cnpjPrestador,cnpjPagina):
    cnpj_backend = limpar_cnpj(cnpjPrestador)
    cnpjPagina_limpo = limpar_cnpj(cnpjPagina)

    if cnpj_backend != cnpjPagina_limpo:
        raise Exception(f"CNPJ divergente! Tela: {cnpjPagina} | Backend: {cnpjPrestador}")

    print("✅ CNPJ validado com sucesso")