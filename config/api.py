import requests

# ── Altere para a URL da sua API ──────────────────────────
BASE_URL = "https://sistemanotas-goba.onrender.com"
# ─────────────────────────────────────────────────────────


class ApiClient:
    """Centraliza todas as chamadas HTTP para a API."""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.prestador_id: str = None  # preenchido após login

    # ── Auth ──────────────────────────────────────────────

    def login(self, usuario: str, senha: str) -> dict:
        resp = requests.post(
            f"{self.base_url}/auth/login",
            json={"usuario": usuario, "senha": senha},
            timeout=10,
        )
        resp.raise_for_status()
        dados = resp.json()
        self.prestador_id = dados["prestadorId"]
        return dados

    # ── Prestador ─────────────────────────────────────────

    def buscar_prestador(self) -> dict:
        resp = requests.get(
            f"{self.base_url}/prestador/{self.prestador_id}",
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def salvar_prestador(self, dados: dict) -> dict:
        resp = requests.patch(
            f"{self.base_url}/prestador/{self.prestador_id}",
            json=dados,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    # ── Tomadores ─────────────────────────────────────────

    def listar_tomadores(self) -> list:
        resp = requests.get(
            f"{self.base_url}/tomador/prestador/{self.prestador_id}",
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def criar_tomador(self, dados: dict) -> dict:
        dados["prestadorId"] = self.prestador_id
        resp = requests.post(f"{self.base_url}/tomador", json=dados, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def salvar_tomador(self, uuid: str, dados: dict) -> dict:
        resp = requests.patch(
            f"{self.base_url}/tomador/{uuid}", json=dados, timeout=10
        )
        resp.raise_for_status()
        return resp.json()

    def deletar_tomador(self, uuid: str) -> None:
        resp = requests.delete(f"{self.base_url}/tomador/{uuid}", timeout=10)
        resp.raise_for_status()

    # ── Notas Padrão ──────────────────────────────────────

    def listar_notas(self) -> list:
        resp = requests.get(
            f"{self.base_url}/notaPadrao/prestador/{self.prestador_id}",
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def criar_nota(self, dados: dict) -> dict:
        resp = requests.post(f"{self.base_url}/notaPadrao", json=dados, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def salvar_nota(self, uuid: str, dados: dict) -> dict:
        resp = requests.patch(
            f"{self.base_url}/notaPadrao/{uuid}", json=dados, timeout=10
        )
        resp.raise_for_status()
        return resp.json()

    def deletar_nota(self, uuid: str) -> None:
        resp = requests.delete(f"{self.base_url}/notaPadrao/{uuid}", timeout=10)
        resp.raise_for_status()

    # ── Listas de referência (dropdowns) ──────────────────
    # Atenção: os nomes dos endpoints devem bater exatamente com a API.
    # Corrija aqui caso o servidor use outro caminho.

    def listar_pis_situacoes(self) -> list:
        """GET /pisCofinsSituacao → lista de { uuid, descricao }"""
        resp = requests.get(f"{self.base_url}/pisCofinsSituacao", timeout=10)
        resp.raise_for_status()
        return resp.json()

    def listar_pis_retencoes(self) -> list:
        """GET /pisCofinsRetencao → lista de { uuid, descricao }
        Se continuar dando 404, verifique o nome exato da rota na sua API
        e ajuste o path abaixo.
        """
        resp = requests.get(f"{self.base_url}/pisCofinsRetencoes", timeout=10)
        resp.raise_for_status()
        return resp.json()

    def listar_servicos(self) -> list:
        resp = requests.get(f"{self.base_url}/listaServico", timeout=10)
        resp.raise_for_status()
        return resp.json()
    
    def buscar_servico_por_uuid(self,uuid: str) -> list:
        resp = requests.get(f"{self.base_url}/listaServico/{uuid}", timeout=10)
        resp.raise_for_status()
        return resp.json()
    
    def buscar_nbs_por_uuid(self,uuid: str) -> list:
        resp = requests.get(f"{self.base_url}/listaNbs/{uuid}", timeout=10)
        resp.raise_for_status()
        return resp.json()
    
    def buscar_pisSituacao_por_uuid(self,uuid: str) -> list:
        resp = requests.get(f"{self.base_url}/pisCofinsSituacao/{uuid}", timeout=10)
        resp.raise_for_status()
        return resp.json()
    
    def buscar_pisRetencoes_por_uuid(self,uuid: str) -> list:
        resp = requests.get(f"{self.base_url}/pisCofinsRetencoes/{uuid}", timeout=10)
        resp.raise_for_status()
        return resp.json()

    def listar_nbs(self) -> list:
        """GET /listaNbs → lista de { uuid, descricao } (nbsServicoPrestado)"""
        resp = requests.get(f"{self.base_url}/listaNbs", timeout=10)
        resp.raise_for_status()
        return resp.json()


# Instância global — importada por toda a aplicação
api = ApiClient()
