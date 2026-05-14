import customtkinter as ctk

from ui.helper import make_label
from ui.widgets import LabeledEntry, StatusLabel
from config.api import api


class TelaLogin(ctk.CTkFrame):
    def __init__(self, master, on_success):
        super().__init__(master, fg_color="transparent")
        self.on_success = on_success
        self._build()

    def _build(self):
        card = ctk.CTkFrame(self, width=340, corner_radius=12)
        card.pack(expand=True, pady=60)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=32, pady=28, fill="both", expand=True)

        make_label(inner, "NFS-e Emissor", size=22, bold=True).pack(anchor="w")
        make_label(inner, "Faça login com sua conta", size=13, color="gray").pack(
            anchor="w", pady=(2, 8)
        )

        self.e_usuario = LabeledEntry(inner, "Usuário", placeholder="Digite seu usário aqui")
        self.e_usuario.pack(anchor="w")

        self.e_senha = LabeledEntry(inner, "Senha", placeholder="Digite sua senha aqui", show="*")
        self.e_senha.pack(anchor="w")

        self.lbl_erro = StatusLabel(inner)
        self.lbl_erro.pack(pady=(8, 0), anchor="w")

        self.btn_entrar = ctk.CTkButton(
            inner, text="Entrar", width=300, command=self._login
        )
        self.btn_entrar.pack(pady=(8, 0))

        make_label(
            inner, "Não tem conta? Fale com o administrador.", size=11, color="gray"
        ).pack(pady=(10, 0))

    def _login(self):
        usuario = self.e_usuario.get().strip()
        senha = self.e_senha.get().strip()

        if not usuario or not senha:
            self.lbl_erro.error("Preencha usuário e senha.")
            return

        self.btn_entrar.configure(state="disabled", text="Entrando...")
        self.lbl_erro.clear()

        try:
            dados = api.login(usuario, senha)
            self.on_success(dados)
        except Exception as exc:
            if not self.winfo_exists():
                return
            msg = str(exc)
            if "401" in msg or "403" in msg:
                self.lbl_erro.error("Usuário ou senha incorretos.")
            elif "ConnectionError" in type(exc).__name__ or "Timeout" in type(exc).__name__:
                self.lbl_erro.error("Sem conexão com o servidor.")
            else:
                self.lbl_erro.error(f"Erro: {msg[:60]}")
            self.btn_entrar.configure(state="normal", text="Entrar")