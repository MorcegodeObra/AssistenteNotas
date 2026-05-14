import requests

def buscar_municipios_pr():
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/PR/municipios"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        municipios = []

        for item in data:
            nome = item.get("nome")
            uf = item.get("microrregiao", {}).get("mesorregiao", {}).get("UF", {}).get("sigla", "PR")

            if nome:
                municipios.append(f"{nome}/{uf}")

        return sorted(municipios)

    except Exception as e:
        print(f"[ERRO] IBGE: {e}")
        return []