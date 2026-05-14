_MAX_CHARS = 48


def _truncar(texto: str, max_chars: int = _MAX_CHARS) -> str:
    return texto if len(texto) <= max_chars else texto[: max_chars - 1] + "…"


def construir_mapa(lista: list, campo_label: str, campo_id: str) -> dict:
    """Converte lista da API em { label_truncado: uuid }.
    Pula itens onde label ou id sejam None/vazios.
    """
    mapa: dict = {}
    for item in lista:
        try:
            label = item[campo_label]
            id_ = item[campo_id]
            if label and id_:
                mapa[_truncar(str(label))] = str(id_)
        except (KeyError, TypeError):
            pass
    return mapa