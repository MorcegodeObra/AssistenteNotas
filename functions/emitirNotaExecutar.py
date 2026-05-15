import re
from playwright.sync_api import sync_playwright

from functions.dadosNota import DadosNota
from functions.tomador import Tomador
from functions.dadosPrestador import DadosPrestador
from functions.pages.primeira import primeiraPagina
from functions.pages.segunda import segundaPagina
from functions.pages.terceira import terceiraPagina
from utils.limparCnpj import *


def _iniciar_browser(playwright):
    for channel in ("msedge", "chrome"):
        try:
            return playwright.chromium.launch(channel=channel, headless=False)
        except Exception:
            continue
    raise RuntimeError(
        "Nenhum navegador compatível encontrado.\n"
        "Instale o Microsoft Edge ou Google Chrome para usar esta funcionalidade."
    )


def _verificar_cnpj(page, dadosPrestador) -> None:
    """Verifica se o CNPJ autenticado no gov.br corresponde ao prestador cadastrado."""
    if not dadosPrestador or not dadosPrestador.cnpj:
        return
    cnpj_esperado = "".join(filter(str.isdigit, str(dadosPrestador.cnpj)))
    if not cnpj_esperado:
        return
    conteudo = page.content()
    cnpjs = re.findall(r'\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}', conteudo)
    cnpjs_digits = ["".join(filter(str.isdigit, c)) for c in cnpjs]
    if cnpjs_digits and cnpj_esperado not in cnpjs_digits:
        raise RuntimeError(
            f"CNPJ autenticado ({cnpjs_digits[0]}) não corresponde ao prestador "
            f"cadastrado ({cnpj_esperado}). Verifique o certificado digital utilizado."
        )


def executar_automacao(dadosNota, tomador, dadosPrestador):
    with sync_playwright() as playwright:
        browser = _iniciar_browser(playwright)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://www.nfse.gov.br/EmissorNacional/Login?ReturnUrl=%2fEmissorNacional")
        page.get_by_role("link", name="Acesso via certificado digital").click()

        botao_acesso = page.locator(".btnAcesso").first
        botao_acesso.wait_for(state="visible", timeout=10000)
        botao_acesso.click()

        # Aguarda o formulário carregar após o usuário autenticar com certificado
        page.wait_for_selector("#DataCompetencia", timeout=120000)

        # Verifica se o CNPJ logado corresponde ao prestador
        _verificar_cnpj(page, dadosPrestador)

        primeiraPagina(page, dadosNota, tomador)
        segundaPagina(page, dadosNota)
        terceiraPagina(page, dadosNota, dadosPrestador)

        # terceiraPagina clica "Avançar" → aguarda carregamento da página de revisão
        page.wait_for_load_state("networkidle", timeout=30000)

        # Localiza e clica no botão "Emitir NFS-e" na página de revisão
        btn_emitir = page.get_by_role("button", name=re.compile(r"emitir", re.IGNORECASE))
        btn_emitir.wait_for(state="visible", timeout=30000)
        btn_emitir.click()

        # Aguarda confirmação de emissão
        page.wait_for_load_state("networkidle", timeout=60000)
        print("✅ Nota fiscal emitida com sucesso!")

        context.close()
        browser.close()