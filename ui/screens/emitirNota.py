import threading
import customtkinter as ctk

from ui.helper import make_label
from ui.widgets import SectionCard, LabeledEntry, LabeledDropdown, StatusLabel
from utils.mapas import construir_mapa
from functions.dadosPrestador import DadosPrestador
from functions.funcaoMontarEmitir import emitir_nota_service
from functions.dadosNota import DadosNota
from functions.tomador import Tomador
from config.api import api
from utils.formatarData import formatar_data_para_ui, formatar_data_para_bd
from utils.acessarMunicipios import buscar_municipios_pr


class TelaEmitir(ctk.CTkScrollableFrame):
    def __init__(
        self,
        master,
        tomadores: list,
        prestador: DadosPrestador = None,
    ):
        super().__init__(master, fg_color="transparent")
        self.tomadores = tomadores  # lista compartilhada com TelaTomadores
        self.prestador = prestador
        self.map_servicos: dict = {}
        self.map_nbs: dict = {}
        self.tomador_selecionado: Tomador = None
        self._municipio_pendente: str = None
        self._carregado = False
        self._build()

    # ── Lazy loading ──────────────────────────────────────

    def on_show(self) -> None:
        self.atualizar_tomadores()
        if not self._carregado:
            threading.Thread(target=self._carregar_listas, daemon=True).start()

    def _carregar_listas(self) -> None:
        try:
            raw_servicos = api.listar_servicos()
            raw_nbs = api.listar_nbs()
            municipios = buscar_municipios_pr() or ["Erro ao carregar municípios"]

            self.map_servicos = construir_mapa(raw_servicos, "descricao", "uuid")
            self.map_nbs = construir_mapa(raw_nbs, "descricao", "uuid")
            self._carregado = True
            self.after(0, lambda: self._atualizar_dropdowns(municipios))
        except Exception as exc:
            self.after(0, lambda: self.lbl_status.error(f"Erro ao carregar listas: {exc}"))

    def _atualizar_dropdowns(self, municipios: list) -> None:
        self.dd_servico.configure(values=list(self.map_servicos.keys()) or ["(sem opções)"])
        self.dd_nbs.configure(values=list(self.map_nbs.keys()) or ["(sem opções)"])
        self.dd_municipio.configure(values=municipios)

        if self._municipio_pendente and self._municipio_pendente in municipios:
            self.dd_municipio.set(self._municipio_pendente)
        else:
            self.dd_municipio.set(municipios[0] if municipios else "")

        # reaplicar seleção de serviço/nbs se tomador já estiver escolhido
        nota = getattr(self.tomador_selecionado, "dadosNota", None)
        if nota:
            self.dd_servico.set_from_map(self.map_servicos, nota.codigoTributacao)
            self.dd_nbs.set_from_map(self.map_nbs, nota.nbsServicoPrestado)

    # ── Construção ────────────────────────────────────────

    def _build(self) -> None:
        make_label(self, "Emitir Nota Fiscal", size=18, bold=True).pack(
            anchor="w", pady=(0, 2)
        )
        make_label(
            self,
            "Selecione o tomador, revise os dados e confirme a emissão.",
            size=12,
            color="gray",
        ).pack(anchor="w", pady=(0, 12))

        # ── Tomador ───────────────────────────────────────
        card_tomador = SectionCard(self)
        card_tomador.pack(fill="x", pady=(0, 12))

        make_label(card_tomador.inner, "Tomador", size=13, bold=True).pack(
            anchor="w", pady=(0, 6)
        )
        self.dd_tomador = ctk.CTkOptionMenu(
            card_tomador.inner,
            values=["(nenhum tomador cadastrado)"],
            width=340,
            command=self._on_selecionar_tomador,
        )
        self.dd_tomador.pack(anchor="w")

        # ── Dados da nota ─────────────────────────────────
        make_label(self, "Dados da Nota", size=14, bold=True).pack(
            anchor="w", pady=(8, 4)
        )
        card_nota = SectionCard(self)
        card_nota.pack(fill="x", pady=(0, 12))

        self.e_data = LabeledEntry(
            card_nota.inner, "Data de Competência", "DD/MM/AAAA", width=340
        )
        self.e_data.pack(anchor="w")

        self.dd_municipio = LabeledDropdown(
            card_nota.inner, "Local de Prestação", ["Carregando..."]
        )
        self.dd_municipio.pack(anchor="w")

        self.e_desc = LabeledEntry(card_nota.inner, "Descrição da Nota", width=340)
        self.e_desc.pack(anchor="w")

        self.e_valor = LabeledEntry(
            card_nota.inner, "Valor do Serviço (R$)", "0,00", width=340
        )
        self.e_valor.pack(anchor="w")
        self.e_valor.bind("<KeyRelease>", self._formatar_valor)

        self.e_resp = LabeledEntry(card_nota.inner, "Nº Resp. Técnica", width=340)
        self.e_resp.pack(anchor="w")

        self.e_docref = LabeledEntry(card_nota.inner, "Documento de Referência", width=340)
        self.e_docref.pack(anchor="w")

        self.e_info = LabeledEntry(
            card_nota.inner, "Informações Complementares", width=340
        )
        self.e_info.pack(anchor="w")

        self.dd_servico = LabeledDropdown(
            card_nota.inner, "Código de Tributação", ["Carregando..."]
        )
        self.dd_servico.pack(anchor="w")

        self.dd_nbs = LabeledDropdown(
            card_nota.inner, "NBS / Serviço Prestado", ["Carregando..."]
        )
        self.dd_nbs.pack(anchor="w")

        # ── Aviso e ações ─────────────────────────────────
        aviso = ctk.CTkFrame(self, corner_radius=8, fg_color=("gray90", "#3D2E00"))
        aviso.pack(fill="x", pady=(0, 12))
        make_label(
            aviso,
            "⚠️  Após a emissão, a nota não poderá ser cancelada por aqui.",
            size=12,
        ).pack(padx=16, pady=10)

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(anchor="e")
        ctk.CTkButton(
            row,
            text="💾  Salvar dados padrão",
            width=160,
            fg_color="transparent",
            border_width=1,
            command=self._salvar_nota_padrao,
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(row, text="✓  Emitir Nota", width=140, command=self._emitir).pack(
            side="left"
        )

        self.lbl_status = StatusLabel(self, font=ctk.CTkFont(size=13))
        self.lbl_status.pack(anchor="w", pady=(12, 0))

    # ── Atualização de tomadores ──────────────────────────

    def atualizar_tomadores(self) -> None:
        nomes = [t.nome or t.cpfCnpj or "Sem nome" for t in self.tomadores]
        self.dd_tomador.configure(values=nomes or ["(nenhum tomador cadastrado)"])

        if self.tomador_selecionado and self.tomador_selecionado in self.tomadores:
            self.dd_tomador.set(
                self.tomador_selecionado.nome or self.tomador_selecionado.cpfCnpj or "Sem nome"
            )
        elif nomes:
            self._on_selecionar_tomador(nomes[0])

    # ── Eventos ───────────────────────────────────────────

    def _on_selecionar_tomador(self, valor: str) -> None:
        for t in self.tomadores:
            if (t.nome or t.cpfCnpj or "Sem nome") == valor:
                self.tomador_selecionado = t
                break
        self._preencher_campos()

    def _formatar_valor(self, _event) -> None:
        valor = self.e_valor.get()
        pos = self.e_valor.index(ctk.INSERT)
        formatado = self._moeda_input(valor)
        self.e_valor.delete(0, "end")
        self.e_valor.insert(0, formatado)
        try:
            self.e_valor.icursor(pos)
        except Exception:
            pass

    def _preencher_campos(self) -> None:
        for campo in (self.e_data, self.e_desc, self.e_valor, self.e_resp, self.e_docref, self.e_info):
            campo.delete(0, "end")

        nota = getattr(self.tomador_selecionado, "dadosNota", None)
        if not nota:
            return

        self.dd_municipio.set("")
        self.e_data.insert(
            0, formatar_data_para_ui(nota.dataCompetencia) if nota.dataCompetencia else ""
        )
        self._municipio_pendente = nota.local or None
        self.e_desc.insert(0, nota.descricao or "")
        if nota.valorServico:
            centavos = int(float(nota.valorServico) * 100)
            self.e_valor.insert(0, self._moeda_input(str(centavos)))
        self.e_resp.insert(0, nota.numeroRespTecnica or "")
        self.e_docref.insert(0, nota.documentoReferencia or "")
        self.e_info.insert(0, nota.informacoesComplementares or "")

        # maps podem ainda não estar carregados; set_from_map ignora silenciosamente
        self.dd_servico.set_from_map(self.map_servicos, nota.codigoTributacao)
        self.dd_nbs.set_from_map(self.map_nbs, nota.nbsServicoPrestado)

    # ── Utilitários de moeda ──────────────────────────────

    def _moeda_input(self, valor: str) -> str:
        digitos = "".join(filter(str.isdigit, valor))
        if not digitos:
            return ""
        return (
            f"{int(digitos) / 100:,.2f}"
            .replace(",", "X").replace(".", ",").replace("X", ".")
        )

    def _moeda_para_float(self, valor: str) -> float:
        if not valor:
            return 0.0
        return float(valor.replace(".", "").replace(",", "."))

    # ── Salvar nota padrão ────────────────────────────────

    def _salvar_nota_padrao(self) -> None:
        if not self.tomador_selecionado:
            self.lbl_status.error("Selecione um tomador primeiro.")
            return

        t = self.tomador_selecionado
        nota_existente = getattr(t, "dadosNota", None)

        t.dadosNota = DadosNota(
            dataCompetencia=formatar_data_para_bd(self.e_data.get()),
            local=self.dd_municipio.get(),
            codigoTributacao=self.map_servicos.get(self.dd_servico.get(), ""),
            descricao=self.e_desc.get(),
            nbsServicoPrestado=self.map_nbs.get(self.dd_nbs.get(), ""),
            valorServico=self._moeda_para_float(self.e_valor.get()),
            numeroRespTecnica=self.e_resp.get(),
            documentoReferencia=self.e_docref.get(),
            informacoesComplementares=self.e_info.get(),
            tomadorId=t.uuid or "",
            uuid=nota_existente.uuid if nota_existente else "",
        )

        try:
            payload = t.dadosNota.para_api()
            if t.dadosNota.uuid:
                api.salvar_nota(t.dadosNota.uuid, payload)
            else:
                resposta = api.criar_nota(payload)
                t.dadosNota.uuid = resposta.get("uuid", "")
            self.lbl_status.success("✓ Dados padrão salvos.")
        except Exception as exc:
            self.lbl_status.error(f"Erro ao salvar: {str(exc)[:60]}")

    # ── Emitir ────────────────────────────────────────────

    def _emitir(self) -> None:
        if not self.tomador_selecionado:
            self.lbl_status.error("Selecione um tomador.")
            return
        if not self.e_valor.get():
            self.lbl_status.error("Preencha o valor.")
            return

        try:
            form_data = {
                "data": self.e_data.get(),
                "local": self.dd_municipio.get(),
                "descricao": self.e_desc.get(),
                "valor": self._moeda_para_float(self.e_valor.get()),
                "resp": self.e_resp.get(),
                "docref": self.e_docref.get(),
                "info": self.e_info.get(),
                "servico": self.dd_servico.get(),
                "nbs": self.dd_nbs.get(),
            }
            emitir_nota_service(
                form_data,
                self.tomador_selecionado,
                self.map_servicos,
                self.map_nbs,
                self.prestador,
            )
            self.lbl_status.success("✓ Nota enviada para processamento!")
        except Exception as exc:
            self.lbl_status.error(f"Erro ao emitir nota: {exc}")