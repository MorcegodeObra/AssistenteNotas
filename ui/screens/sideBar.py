import customtkinter as ctk

from ui.helper import make_label, truncar_texto


class Sidebar(ctk.CTkFrame):
    ITENS = [
        ("prestador", "🏢  Meus dados"),
        ("tomadores", "👥  Clientes"),
        ("emitir",    "📄  Emitir Nota"),
    ]

    def __init__(self, master, usuario: str, on_navigate, on_logout):
        super().__init__(master, width=200, corner_radius=0)
        self.pack_propagate(False)
        self.on_navigate = on_navigate
        self._botoes: dict = {}
        self._build(usuario, on_logout)

    def _build(self, usuario: str, on_logout) -> None:
        # ── Cabeçalho ─────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(20, 10))
        make_label(header, "NFS-e", size=18, bold=True).pack(anchor="w")
        make_label(header, "Emissor de Notas", size=11, color="gray").pack(anchor="w")

        ctk.CTkFrame(self, height=1, fg_color=("gray75", "gray30")).pack(
            fill="x", padx=12, pady=8
        )

        # ── Navegação ─────────────────────────────────────
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", padx=8)

        for key, texto in self.ITENS:
            btn = ctk.CTkButton(
                nav,
                text=texto,
                anchor="w",
                height=36,
                fg_color="transparent",
                hover_color=("gray80", "gray25"),
                text_color=("gray20", "gray80"),
                command=lambda k=key: self.on_navigate(k),
            )
            btn.pack(fill="x", pady=2)
            self._botoes[key] = btn

        # ── Rodapé ────────────────────────────────────────
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(side="bottom", fill="x", padx=12, pady=12)
        ctk.CTkFrame(footer, height=1, fg_color=("gray75", "gray30")).pack(
            fill="x", pady=(0, 8)
        )

        linhas = usuario.split("\n")
        make_label(footer, "👋 Bem-vindo", size=11, color="gray").pack(anchor="w")

        if linhas:
            make_label(footer, truncar_texto(linhas[0], 20), size=13, bold=True).pack(
                anchor="w"
            )
        if len(linhas) > 1:
            make_label(footer, linhas[1], size=11, color="gray").pack(anchor="w")

        ctk.CTkButton(
            footer,
            text="Sair",
            height=28,
            fg_color="transparent",
            hover_color=("gray80", "gray25"),
            text_color="gray",
            command=on_logout,
        ).pack(anchor="w", pady=(4, 0))

    def marcar_ativo(self, chave: str) -> None:
        for key, btn in self._botoes.items():
            if key == chave:
                btn.configure(
                    fg_color=("gray85", "gray20"),
                    text_color=("black", "white"),
                    font=ctk.CTkFont(weight="bold"),
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=("gray20", "gray80"),
                    font=ctk.CTkFont(weight="normal"),
                )