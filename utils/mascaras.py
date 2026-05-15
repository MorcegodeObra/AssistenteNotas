"""Funções puras de formatação para UI.
Nenhuma delas altera valores do banco — apenas transformam strings de exibição.
"""


# ── CPF / CNPJ ────────────────────────────────────────────────────────────────

def cpf_cnpj(texto: str) -> str:
    """Formata como CPF (xxx.xxx.xxx-xx) ou CNPJ (xx.xxx.xxx/xxxx-xx)
    dependendo do número de dígitos digitados (máx. 14)."""
    d = "".join(filter(str.isdigit, texto))[:14]
    n = len(d)
    if n <= 11:
        if n > 9:  return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"
        if n > 6:  return f"{d[:3]}.{d[3:6]}.{d[6:]}"
        if n > 3:  return f"{d[:3]}.{d[3:]}"
        return d
    else:
        if n > 12: return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"
        if n > 8:  return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:]}"
        if n > 5:  return f"{d[:2]}.{d[2:5]}.{d[5:]}"
        if n > 2:  return f"{d[:2]}.{d[2:]}"
        return d


# ── Telefone ──────────────────────────────────────────────────────────────────

def telefone(texto: str) -> str:
    """(xx) x xxxx-xxxx para celular ou (xx) xxxx-xxxx para fixo (máx. 11 dígitos)."""
    d = "".join(filter(str.isdigit, texto))[:11]
    n = len(d)
    if n > 10: return f"({d[:2]}) {d[2:3]} {d[3:7]}-{d[7:]}"
    if n > 6:  return f"({d[:2]}) {d[2:6]}-{d[6:]}"
    if n > 2:  return f"({d[:2]}) {d[2:]}"
    if n > 0:  return f"({d}"
    return d


# ── Porcentagem ───────────────────────────────────────────────────────────────

def porcentagem_fmt(texto: str) -> str:
    """'15' ou '15.5' ou '15,5' → '15,50 %'"""
    limpo = texto.replace(" %", "").replace("%", "").strip().replace(".", ",")
    if not limpo:
        return ""
    partes = limpo.split(",")
    inteiro = partes[0] or "0"
    decimal = (partes[1][:2].ljust(2, "0")) if len(partes) > 1 else "00"
    return f"{inteiro},{decimal} %"


def porcentagem_strip(texto: str) -> str:
    """'15,50 %' → '15,50'  (para edição no campo)"""
    return texto.replace(" %", "").replace("%", "").strip()


def porcentagem_para_float(texto: str) -> float:
    """'15,50 %' ou '15.5' → 15.5"""
    try:
        return float(porcentagem_strip(texto).replace(",", "."))
    except ValueError:
        return 0.0


# ── Data ──────────────────────────────────────────────────────────────────────

def data(texto: str) -> str:
    """Formata DD/MM/AAAA, máx. 8 dígitos."""
    d = "".join(filter(str.isdigit, texto))[:8]
    n = len(d)
    if n > 4: return f"{d[:2]}/{d[2:4]}/{d[4:]}"
    if n > 2: return f"{d[:2]}/{d[2:]}"
    return d


# ── Moeda ─────────────────────────────────────────────────────────────────────

def moeda(texto: str) -> str:
    """Qualquer string com dígitos → 'R$ x.xxx,xx'"""
    d = "".join(filter(str.isdigit, texto))
    if not d:
        return ""
    valor = int(d) / 100
    fmt = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {fmt}"


def moeda_para_float(texto: str) -> float:
    """'R$ 1.234,56' → 1234.56"""
    if not texto:
        return 0.0
    try:
        return float(
            texto.replace("R$", "").strip().replace(".", "").replace(",", ".")
        )
    except ValueError:
        return 0.0


# ── Helper de aplicação ───────────────────────────────────────────────────────

def aplicar(entry, fn_mascara) -> None:
    """Aplica fn_mascara ao valor de um LabeledEntry, preservando o cursor no fim."""
    atual = entry.get()
    novo = fn_mascara(atual)
    if novo != atual:
        entry.delete(0, "end")
        entry.insert(0, novo)
    try:
        entry.icursor(len(entry.get()))
    except Exception:
        pass