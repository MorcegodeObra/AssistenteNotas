import customtkinter as ctk


class SectionCard(ctk.CTkFrame):
    """Card container padrão com inner frame de padding já configurado.

    Uso:
        card = SectionCard(parent)
        widget = ctk.CTkLabel(card.inner, text="Olá")
        widget.pack(anchor="w")
        card.pack(fill="x", pady=(0, 12))
    """

    def __init__(self, master, padx: int = 20, pady: int = 16, **kwargs):
        kwargs.setdefault("corner_radius", 10)
        super().__init__(master, **kwargs)
        self.inner = ctk.CTkFrame(self, fg_color="transparent")
        self.inner.pack(padx=padx, pady=pady, fill="both")