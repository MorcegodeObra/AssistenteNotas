def primeiraPagina(page,dadosNota,tomador):
    page.locator("#DataCompetencia").click()
    page.locator("#DataCompetencia").fill(dadosNota.dataCompetencia)
    page.locator("#DataCompetencia").press("Tab")
    page.locator("#SimplesNacional_RegimeApuracaoTributosSN_chosen a").filter(has_text="Selecione...").click()
    page.locator("#SimplesNacional_RegimeApuracaoTributosSN_chosen").get_by_text("Regime de apuração dos tributos federais e municipal pelo Simples Nacional").click()
    page.locator(".form-group.form-group-lg > .radio-options > div:nth-child(2) > label > .cr > .cr-icon").first.click()
    page.locator("#Tomador_Inscricao").click()
    page.locator("#Tomador_Inscricao").fill(tomador.cpfCnpj)
    page.locator("#Tomador_Inscricao").press("Tab")
    page.locator("#Tomador_Telefone").click()
    page.locator("#Tomador_Telefone").fill(tomador.telefone)
    page.locator("#Tomador_Telefone").press("Tab")
    page.locator("#Tomador_Email").fill(tomador.email)
    page.locator("#pnlTomador").get_by_text("Brasil").click()
    if tomador.cep and tomador.cep.strip():
        page.locator("#pnlTomadorInformarEnderecoCheck").get_by_text("Informar endereço").click()
        page.locator("#pnlTomadorEnderecoBrasil > div > .col-md-3 > .form-group").first.click()
        
        page.locator("#Tomador_EnderecoNacional_CEP").click()
        page.locator("#Tomador_EnderecoNacional_CEP").fill(tomador.cep)
        page.locator("#btn_Tomador_EnderecoNacional_CEP").click()
        
        page.locator("#Tomador_EnderecoNacional_Numero").click()
        page.locator("#Tomador_EnderecoNacional_Numero").fill(tomador.enderecoNumero or "")
        page.locator("#Tomador_EnderecoNacional_Numero").press("Tab")
        
        page.locator("#Tomador_EnderecoNacional_Complemento").fill(tomador.enderecoComplemento or "")

    # sempre avança, independente de ter endereço ou não
    page.get_by_role("button", name="Avançar").click()