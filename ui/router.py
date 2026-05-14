import customtkinter as ctk


class Router(ctk.CTkFrame):
    """Gerencia qual tela está visível na área de conteúdo.

    Cada tela é registrada com uma chave string. Ao navegar, a tela
    anterior é ocultada (pack_forget) e a nova é exibida. Se a tela
    tiver um método `on_show`, ele é chamado após a exibição — ideal
    para acionar carregamentos lazy de dados.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._telas: dict = {}
        self._ativa = None

    def registrar(self, chave: str, tela) -> None:
        self._telas[chave] = tela

    def navegar(self, chave: str) -> None:
        if self._ativa is not None:
            self._ativa.pack_forget()

        tela = self._telas.get(chave)
        if tela is None:
            return

        tela.pack(fill="both", expand=True)
        self._ativa = tela

        if hasattr(tela, "on_show"):
            tela.on_show()