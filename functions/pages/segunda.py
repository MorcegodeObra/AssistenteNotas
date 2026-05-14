def segundaPagina(page,dadosNota):
    page.locator("#pnlLocalPrestacao").get_by_label("").click()
    page.get_by_role("searchbox", name="Search").fill(dadosNota.local[:-3])
    page.get_by_role("option", name=dadosNota.local).click()
    page.get_by_label("", exact=True).locator("b").click()
    page.get_by_role("searchbox", name="Search").fill(dadosNota.codigoTributacao[:8])
    page.get_by_role("option", name=dadosNota.codigoTributacao[8:]).click()
    page.locator("i").nth(1).click()
    page.wait_for_timeout(1000)
    page.locator("#ServicoPrestado_Descricao").fill(dadosNota.descricao)
    page.locator("#ServicoPrestado_Descricao").click()
    page.locator("#ServicoPrestado_CodigoNBS_chosen a").filter(has_text="Selecione...").click()
    page.locator("#ServicoPrestado_CodigoNBS_chosen").get_by_text(dadosNota.nbsServicoPrestado).click()

    if dadosNota.numeroRespTecnica:
        page.locator("#Complemento_NumeroRespTecnica").fill(dadosNota.numeroRespTecnica)

    if dadosNota.documentoReferencia:
        page.locator("#Complemento_DocumentoReferencia").fill(dadosNota.documentoReferencia)

    if dadosNota.informacoesComplementares:
        page.locator("#Complemento_InformacoesComplementares").click()
        page.locator("#Complemento_InformacoesComplementares").fill(dadosNota.informacoesComplementares)

    page.get_by_role("button", name="Avançar").click()