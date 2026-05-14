import customtkinter as ctk


def make_label(parent, text: str, size: int = 12, bold: bool = False, color=None):
    """Label simples. Use diretamente para títulos e subtítulos de seção."""
    weight = "bold" if bold else "normal"
    kw = dict(text=text, font=ctk.CTkFont(size=size, weight=weight))
    if color:
        kw["text_color"] = color
    return ctk.CTkLabel(parent, **kw)


def truncar_texto(texto: str, limite: int = 40) -> str:
    if not texto:
        return ""
    return texto if len(texto) <= limite else texto[: limite - 1] + "…"


def to_float(valor: str) -> float:
    try:
        return float(valor.replace(",", "."))
    except Exception:
        return 0.0