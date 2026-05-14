import customtkinter as ctk


class StatusLabel(ctk.CTkLabel):
    """Label de feedback com métodos semânticos de sucesso/erro/limpeza.

    Substitui o padrão repetido:
        label.configure(text_color="#3B6D11", text="✓ ok")
    por:
        label.success("✓ ok")
    """

    _COLOR_SUCCESS = "#3B6D11"
    _COLOR_ERROR = "#E24B4A"

    def __init__(self, master, **kwargs):
        kwargs.setdefault("text", "")
        kwargs.setdefault("font", ctk.CTkFont(size=12))
        super().__init__(master, **kwargs)

    def success(self, msg: str) -> None:
        self.configure(text_color=self._COLOR_SUCCESS, text=msg)

    def error(self, msg: str) -> None:
        self.configure(text_color=self._COLOR_ERROR, text=msg)

    def clear(self) -> None:
        self.configure(text="")