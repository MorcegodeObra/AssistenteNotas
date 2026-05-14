from utils.formatarPocentagens import *

def terceiraPagina(page, dadosNota, dadosPrestador):
    page.locator("#Valores_ValorServico").fill(dadosNota.valorServico)
    page.locator("#Valores_ValorServico").press("Tab")
    page.locator("div:nth-child(3) > div:nth-child(2) > .radiobutton > label > .cr > .cr-icon").click()
    page.locator("#pnlRetencao > .form-group > .radio-options > div > .radiobutton > label > .cr > .cr-icon").first.click()
    page.get_by_role("button", name="Fechar").click()
    page.locator("div:nth-child(3) > .inline-block > .radiobutton > label > .cr > .cr-icon").click()
    page.wait_for_timeout(1000)

    # Situação tributária PIS/COFINS
    page.locator("#TributacaoFederal_PISCofins_SituacaoTributaria_chosen a").filter(has_text="Selecione...").click()
    page.locator("#TributacaoFederal_PISCofins_SituacaoTributaria_chosen > .chosen-drop > .chosen-search > input").fill(dadosPrestador.pisCofinsSituacao[:2])
    page.locator("#TributacaoFederal_PISCofins_SituacaoTributaria_chosen").get_by_text(dadosPrestador.pisCofinsSituacao[3:]).click()
    page.locator("#TributacaoFederal_PISCofins_BaseDeCalculo").fill(dadosNota.valorServico)
    
    if dadosPrestador.porcentagemPis:
        page.locator("#TributacaoFederal_PISCofins_AliquotaPIS")\
            .fill(formatar_percentual(dadosPrestador.porcentagemPis))

    if dadosPrestador.porcentagemCofins:
        page.locator("#TributacaoFederal_PISCofins_AliquotaCOFINS")\
            .fill(formatar_percentual(dadosPrestador.porcentagemCofins))
        
    # Tipo de retenção PIS/COFINS
    dropdown = page.locator("#TributacaoFederal_PISCofins_TipoRetencao_chosen a")

    dropdown.scroll_into_view_if_needed()
    dropdown.wait_for(state="visible")

    dropdown.click(force=True)
    
    page.locator("#TributacaoFederal_PISCofins_TipoRetencao_chosen").get_by_text(dadosPrestador.pisCofinsRetencao).click()

    if dadosPrestador.valorCsll:
        page.locator("#TributacaoFederal_ValorCSLL").fill(dadosPrestador.valorCsll)

    # Alíquota do Simples Nacional
    page.get_by_text("Informar alíquota do Simples").click()
    page.locator("#ValorTributos_AliquotaSN").click()
    page.locator("#ValorTributos_AliquotaSN").fill(dadosPrestador.porcentagemTributacao)
    btn_avancar = page.get_by_role("button", name="Avançar")

    btn_avancar.wait_for(state="visible")

    if btn_avancar.is_enabled():
        btn_avancar.click()
    else:
        raise Exception("Botão Avançar desabilitado - provavelmente erro nos campos")