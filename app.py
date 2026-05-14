import threading
import customtkinter as ctk

from ui.screens.login import TelaLogin
from ui.screens.prestador import TelaPrestador
from ui.screens.tomadores import TelaTomadores
from ui.screens.emitirNota import TelaEmitir
from ui.screens.sideBar import Sidebar
from ui.router import Router
from functions.dadosPrestador import DadosPrestador
from config.api import api

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NFS-e Emissor")
        self.geometry("900x580")
        self.minsize(700, 480)
        self._tomadores: list = []
        self._mostrar_login()

    # ── Login ─────────────────────────────────────────────

    def _mostrar_login(self) -> None:
        if hasattr(self, "_main_frame"):
            self._main_frame.destroy()
        self._tomadores.clear()

        self._login_frame = TelaLogin(self, on_success=self._apos_login)
        self._login_frame.pack(fill="both", expand=True)

    def _apos_login(self, _dados_login: dict) -> None:
        self._mostrar_aguarde()
        threading.Thread(target=self._carregar_prestador, daemon=True).start()

    def _mostrar_aguarde(self) -> None:
        self._login_frame.destroy()
        self._aguarde_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._aguarde_frame.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(self._aguarde_frame, width=360, corner_radius=12)
        inner.pack(expand=True, pady=60)
        ctk.CTkLabel(
            inner,
            text="🔄  Acessando as informações do sistema",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(padx=36, pady=(32, 8))
        ctk.CTkLabel(
            inner,
            text="Aguarde, isso pode levar alguns instantes...",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).pack(padx=36, pady=(0, 32))

    def _carregar_prestador(self) -> None:
        try:
            dados = api.buscar_prestador()
        except Exception:
            dados = {}
        self.after(0, lambda: self._montar_app(dados))

    # ── App principal ─────────────────────────────────────

    def _montar_app(self, dados_api: dict) -> None:
        if hasattr(self, "_aguarde_frame"):
            self._aguarde_frame.destroy()

        if isinstance(dados_api, list):
            dados_api = dados_api[0] if dados_api else {}

        prestador = self._montar_prestador(dados_api)

        self._main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._main_frame.pack(fill="both", expand=True)

        # Sidebar fica à esquerda
        usuario_label = f"{dados_api.get('nomeEmpresa', 'Empresa')}\n{dados_api.get('cnpj', '')}"
        self._sidebar = Sidebar(
            self._main_frame,
            usuario=usuario_label,
            on_navigate=self._navegar,
            on_logout=self._mostrar_login,
        )
        self._sidebar.pack(side="left", fill="y")

        # Área de conteúdo + router ficam à direita
        area = ctk.CTkFrame(self._main_frame, fg_color="transparent")
        area.pack(side="left", fill="both", expand=True, padx=16, pady=16)

        self._router = Router(area)
        self._router.pack(fill="both", expand=True)

        self._router.registrar("prestador", TelaPrestador(self._router, dados=prestador))
        self._router.registrar(
            "tomadores", TelaTomadores(self._router, tomadores=self._tomadores)
        )
        self._router.registrar(
            "emitir",
            TelaEmitir(self._router, tomadores=self._tomadores, prestador=prestador),
        )

        self._navegar("tomadores")

    # ── Helpers ───────────────────────────────────────────

    @staticmethod
    def _montar_prestador(dados_api: dict) -> DadosPrestador:
        def _str(val):
            return str(val) if val not in (None, "", False) else ""

        return DadosPrestador(
            cnpj=_str(dados_api.get("cnpj")),
            porcentagemTributacao=_str(dados_api.get("porcentagemTributacao")),
            pisCofinsSituacao=_str(dados_api.get("pisCofinsSituacao")),
            pisCofinsRetencao=_str(dados_api.get("pisCofinsRetencao")),
            porcentagemPis=_str(dados_api.get("porcentagemPis")),
            porcentagemCofins=_str(dados_api.get("porcentagemCofins")),
            valorCsll=_str(dados_api.get("valorCsll")),
        )

    # ── Navegação ─────────────────────────────────────────

    def _navegar(self, chave: str) -> None:
        self._router.navegar(chave)
        self._sidebar.marcar_ativo(chave)


if __name__ == "__main__":
    App().mainloop()