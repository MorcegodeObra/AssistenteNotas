import threading
import customtkinter as ctk

from ui.helper import make_label, to_float
from ui.widgets import SectionCard, LabeledEntry, LabeledDropdown, StatusLabel
from utils.mapas import construir_mapa
from utils.mascaras import porcentagem_fmt, porcentagem_strip, porcentagem_para_float, moeda, moeda_para_float, aplicar
from config.api import api


def _bind_pct(entry: LabeledEntry) -> None:
    """Configura FocusIn (strip %) e FocusOut (formata %) em um LabeledEntry."""
    entry.bind("<FocusOut>", lambda e: entry.set(porcentagem_fmt(entry.get())), "+")
    entry.bind("<FocusIn>",  lambda e: entry.set(porcentagem_strip(entry.get())), "+")


class TelaPrestador(ctk.CTkScrollableFrame):
    def __init__(self, master, dados=None):
        super().__init__(master, fg_color="transparent")
        self.dados = dados
        self.map_situacao: dict = {}
        self.map_retencao: dict = {}
        self._carregado = False
        self._build()

    # ── Lazy loading ──────────────────────────────────────

    def on_show(self) -> None:
        if not self._carregado:
            threading.Thread(target=self._carregar_listas, daemon=True).start()

    def _carregar_listas(self) -> None:
        try:
            raw_sit = api.listar_pis_situacoes()
            raw_ret = api.listar_pis_retencoes()
            self.map_situacao = construir_mapa(raw_sit, "descricao", "uuid")
            self.map_retencao = construir_mapa(raw_ret, "descricao", "uuid")
            self._carregado = True
            self.after(0, self._preencher_dropdowns)
        except Exception as exc:
            self.after(0, lambda: self.lbl_status.error(f"Erro ao carregar listas: {exc}"))

    def _preencher_dropdowns(self) -> None:
        self.dd_pis_situacao.configure(
            values=list(self.map_situacao.keys()) or ["(sem opções)"]
        )
        self.dd_pis_retencao.configure(
            values=list(self.map_retencao.keys()) or ["(sem opções)"]
        )
        if self.dados:
            self.dd_pis_situacao.set_from_map(self.map_situacao, self.dados.pisCofinsSituacao)
            self.dd_pis_retencao.set_from_map(self.map_retencao, self.dados.pisCofinsRetencao)

    # ── Construção da UI ──────────────────────────────────

    def _build(self) -> None:
        make_label(self, "Dados do Prestador", size=18, bold=True).pack(
            anchor="w", pady=(0, 4)
        )

        card = SectionCard(self)
        card.pack(fill="x", pady=(0, 12))

        self.e_tributacao = LabeledEntry(card.inner, "% Tributação", width=320)
        self.e_tributacao.pack(anchor="w")
        _bind_pct(self.e_tributacao)

        self.e_pis = LabeledEntry(card.inner, "% PIS", width=320)
        self.e_pis.pack(anchor="w")
        _bind_pct(self.e_pis)

        self.e_cofins = LabeledEntry(card.inner, "% COFINS", width=320)
        self.e_cofins.pack(anchor="w")
        _bind_pct(self.e_cofins)

        self.e_csll = LabeledEntry(card.inner, "Valor CSLL (R$)", width=320)
        self.e_csll.pack(anchor="w")
        self.e_csll.bind("<KeyRelease>", lambda _: aplicar(self.e_csll, moeda), "+")

        self.dd_pis_situacao = LabeledDropdown(
            card.inner, "PIS/COFINS Situação", [], width=320
        )
        self.dd_pis_situacao.pack(anchor="w")

        self.dd_pis_retencao = LabeledDropdown(
            card.inner, "PIS/COFINS Retenção", [], width=320
        )
        self.dd_pis_retencao.pack(anchor="w")

        # Preenche valores numéricos já formatados como percentual
        if self.dados:
            self.e_tributacao.set(porcentagem_fmt(str(self.dados.porcentagemTributacao or "")))
            self.e_pis.set(porcentagem_fmt(str(self.dados.porcentagemPis or "")))
            self.e_cofins.set(porcentagem_fmt(str(self.dados.porcentagemCofins or "")))
            try:
                self.e_csll.set(moeda(str(int(round(float(self.dados.valorCsll) * 100)))))
            except (TypeError, ValueError):
                pass

        row = ctk.CTkFrame(card.inner, fg_color="transparent")
        row.pack(anchor="e", pady=(16, 0))
        self.btn_salvar = ctk.CTkButton(
            row, text="Salvar", width=120, command=self._salvar
        )
        self.btn_salvar.pack(side="left")

        self.lbl_status = StatusLabel(card.inner)
        self.lbl_status.pack(anchor="w", pady=(8, 0))

    # ── Persistência ──────────────────────────────────────

    def _salvar(self) -> None:
        payload = {
            "porcentagemTributacao": porcentagem_para_float(self.e_tributacao.get()),
            "porcentagemPis":        porcentagem_para_float(self.e_pis.get()),
            "porcentagemCofins":     porcentagem_para_float(self.e_cofins.get()),
            "valorCsll":             moeda_para_float(self.e_csll.get()),
            "pisCofinsSituacao":     self.map_situacao.get(self.dd_pis_situacao.get()),
            "pisCofinsRetencao":     self.map_retencao.get(self.dd_pis_retencao.get()),
        }
        try:
            api.salvar_prestador(payload)
            self.lbl_status.success("✓ Dados atualizados com sucesso")
        except Exception as exc:
            self.lbl_status.error(f"Erro: {str(exc)[:60]}")