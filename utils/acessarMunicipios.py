import requests

# Nome completo → sigla UF
ESTADOS_BR: dict[str, str] = {
    "Acre": "AC", "Alagoas": "AL", "Amapá": "AP", "Amazonas": "AM",
    "Bahia": "BA", "Ceará": "CE", "Distrito Federal": "DF", "Espírito Santo": "ES",
    "Goiás": "GO", "Maranhão": "MA", "Mato Grosso": "MT", "Mato Grosso do Sul": "MS",
    "Minas Gerais": "MG", "Pará": "PA", "Paraíba": "PB", "Paraná": "PR",
    "Pernambuco": "PE", "Piauí": "PI", "Rio de Janeiro": "RJ",
    "Rio Grande do Norte": "RN", "Rio Grande do Sul": "RS",
    "Rondônia": "RO", "Roraima": "RR", "Santa Catarina": "SC",
    "São Paulo": "SP", "Sergipe": "SE", "Tocantins": "TO",
}

# Sigla → nome completo (inverso)
SIGLA_TO_ESTADO: dict[str, str] = {v: k for k, v in ESTADOS_BR.items()}


def buscar_municipios(sigla_uf: str) -> list[str]:
    """Retorna lista de 'Município/UF' para o estado informado via API IBGE."""
    url = (
        f"https://servicodados.ibge.gov.br/api/v1"
        f"/localidades/estados/{sigla_uf}/municipios"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        municipios: list[str] = []
        for item in resp.json():
            nome = item.get("nome")
            uf = (
                item.get("microrregiao", {})
                    .get("mesorregiao", {})
                    .get("UF", {})
                    .get("sigla", sigla_uf)
            )
            if nome:
                municipios.append(f"{nome}/{uf}")
        return sorted(municipios)
    except Exception as exc:
        print(f"[ERRO] IBGE ({sigla_uf}): {exc}")
        return []