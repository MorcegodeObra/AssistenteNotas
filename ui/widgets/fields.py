import customtkinter as ctk

_DROPDOWN_MAX_CHARS = 48


def _truncar(texto: str, max_chars: int = _DROPDOWN_MAX_CHARS) -> str:
    return texto if len(texto) <= max_chars else texto[: max_chars - 1] + "…"


class LabeledEntry(ctk.CTkFrame):
    """Label + Entry empilhados como um widget atômico reutilizável.

    Interface pública espelha CTkEntry para que telas possam substituir
    make_field() sem alterar a lógica de leitura/escrita.
    """

    def __init__(
        self,
        master,
        label: str,
        placeholder: str = "",
        width: int = 300,
        show=None,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        ctk.CTkLabel(self, text=label, font=ctk.CTkFont(size=12)).pack(
            anchor="w", pady=(8, 2)
        )
        entry_kw: dict = dict(placeholder_text=placeholder, width=width)
        if show is not None:
            entry_kw["show"] = show
        self._entry = ctk.CTkEntry(self, **entry_kw)
        self._entry.pack(anchor="w")

    # ── Delegação de interface ────────────────────────────

    def get(self) -> str:
        return self._entry.get()

    def set(self, value: str) -> None:
        self._entry.delete(0, "end")
        self._entry.insert(0, value or "")

    def delete(self, first, last=None) -> None:
        self._entry.delete(first, last)

    def insert(self, index, string: str) -> None:
        self._entry.insert(index, string)

    def bind(self, sequence=None, func=None, add=None):
        # CTkEntry só aceita add='+' ou add=True; None causaria ValueError
        if add is None:
            return self._entry.bind(sequence, func)
        return self._entry.bind(sequence, func, add)

    def index(self, index):
        return self._entry.index(index)

    def icursor(self, index) -> None:
        self._entry.icursor(index)

    def configure(self, **kwargs) -> None:
        state = kwargs.pop("state", None)
        if state is not None:
            self._entry.configure(state=state)
        if kwargs:
            super().configure(**kwargs)


class LabeledDropdown(ctk.CTkFrame):
    """Label + OptionMenu empilhados. Textos longos são truncados automaticamente.

    Interface pública expõe get/set/configure(values/state/command) para
    que as telas não dependam do CTkOptionMenu interno diretamente.
    """

    def __init__(
        self,
        master,
        label: str,
        opcoes: list,
        width: int = 320,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        ctk.CTkLabel(self, text=label, font=ctk.CTkFont(size=12)).pack(
            anchor="w", pady=(8, 2)
        )
        opcoes_limpas = [
            _truncar(str(o))
            for o in (opcoes or [])
            if o is not None and str(o).strip()
        ]
        self._dropdown = ctk.CTkOptionMenu(
            self,
            values=opcoes_limpas or ["(sem opções)"],
            width=width,
            dynamic_resizing=False,
        )
        self._dropdown.pack(anchor="w", pady=(0, 4))

    # ── Delegação de interface ────────────────────────────

    def get(self) -> str:
        return self._dropdown.get()

    def set(self, value: str) -> None:
        self._dropdown.set(value)

    def set_from_map(self, mapa: dict, uuid: str) -> None:
        """Seleciona a opção cujo uuid corresponde ao valor informado."""
        if not uuid:
            return
        for label, id_ in mapa.items():
            if id_ == uuid:
                self._dropdown.set(_truncar(label))
                return

    def configure(self, **kwargs) -> None:
        dropdown_keys = {"values", "state", "command"}
        dd_kw = {k: kwargs.pop(k) for k in list(kwargs) if k in dropdown_keys}
        if dd_kw:
            self._dropdown.configure(**dd_kw)
        if kwargs:
            super().configure(**kwargs)