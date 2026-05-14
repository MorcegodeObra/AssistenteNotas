from playwright.sync_api import sync_playwright
import re

from functions.dadosNota import DadosNota
from functions.tomador import Tomador
from functions.dadosPrestador import DadosPrestador
from functions.pages.primeira import primeiraPagina
from functions.pages.segunda import segundaPagina
from functions.pages.terceira import terceiraPagina
from utils.limparCnpj import *


def _iniciar_browser(playwright):
    # Usa Edge (sempre presente no Windows) ou Chrome instalado pelo usuário.
    # Nenhum Chromium adicional precisa ser instalado.
    for channel in ("msedge", "chrome"):
        try:
            return playwright.chromium.launch(channel=channel, headless=False)
        except Exception:
            continue
    raise RuntimeError(
        "Nenhum navegador compatível encontrado.\n"
        "Instale o Microsoft Edge ou Google Chrome para usar esta funcionalidade."
    )


def executar_automacao(dadosNota, tomador, dadosPrestador):
    with sync_playwright() as playwright:
        browser = _iniciar_browser(playwright)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://www.nfse.gov.br/EmissorNacional/Login?ReturnUrl=%2fEmissorNacional")
        page.get_by_role("link", name="Acesso via certificado digital").click()

        # espera botão ficar disponível
        botao_acesso = page.locator(".btnAcesso").first
        botao_acesso.wait_for(state="visible", timeout=10000)

        # só clica DEPOIS da validação
        botao_acesso.click()

        primeiraPagina(page, dadosNota, tomador)
        segundaPagina(page, dadosNota)
        terceiraPagina(page, dadosNota, dadosPrestador)

        print("👤 Revise e clique em Avançar...")

        url_atual = page.url
        while page.url == url_atual:
            page.wait_for_timeout(500)

        print("✅ Finalizando preenchimento da nota...")

        context.close()
        browser.close()
