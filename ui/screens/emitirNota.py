import re
import threading
import customtkinter as ctk

from ui.helper import make_label
from ui.widgets import SectionCard, LabeledEntry, LabeledDropdown, StatusLabel
from utils.mapas import construir_mapa
from utils import mascaras
from utils.acessarMunicipios import buscar_municipios, ESTADOS_BR, SIGLA_TO_ESTADO
from functions.dadosPrestador import DadosPrestador
from functions.funcaoMontarEmitir import emitir_nota_service
from functions.dadosNota import DadosNota
from functions.tomador import Tomador
from config.api import api
from utils.formatarData import formatar_data_para_ui, formatar_data_para_bd


class TelaEmitir(ctk.CTkScrollableFrame):
    def __init__(
        self,
        master,
        tomadores: list,
        prestador: DadosPrestador = None,
    ):
        super().__init__(master, fg_color="transparent")
        self.tomadores = tomadores
        self.prestador = prestador
        self.map_servicos: dict = {}
        self.map_nbs: dict = {}
        self.tomador_selecionado: Tomador = None
        self._nota_selecionada: DadosNota = None
        self._municipio_pendente: str = None
        self._uf_carregada: str = None
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
            self.map_servicos = construir_mapa(raw_servicos, "descricao", "uuid")
            self.map_nbs = construir_mapa(raw_nbs, "descricao", "uuid")
            self._carregado = True
            self.after(0, self._atualizar_maps_dropdowns)
        except Exception as exc:
            self.after(0, lambda: self.lbl_status.error(f"Erro ao carregar listas: {exc}"))

        estado_atual = self.dd_estado.get()
        sigla = ESTADOS_BR.get(estado_atual, "PR")
        self._carregar_municipios(sigla)

    def _atualizar_maps_dropdowns(self) -> None:
        self.dd_servico.configure(values=list(self.map_servicos.keys()) or ["(sem opções)"])
        self.dd_nbs.configure(values=list(self.map_nbs.keys()) or ["(sem opções)"])
        if self._nota_selecionada:
            self.dd_servico.set_from_map(self.map_servicos, self._nota_selecionada.codigoTributacao)
            self.dd_nbs.set_from_map(self.map_nbs, self._nota_selecionada.nbsServicoPrestado)

    def _carregar_municipios(self, sigla_uf: str) -> None:
        def _tarefa():
            lista = buscar_municipios(sigla_uf) or [f"Erro ao carregar municípios de {sigla_uf}"]
            self.after(0, lambda: self._atualizar_municipios(lista, sigla_uf))
        threading.Thread(target=_tarefa, daemon=True).start()

    def _atualizar_municipios(self, municipios: list, sigla_uf: str) -> None:
        self._uf_carregada = sigla_uf
        self.dd_municipio.configure(values=municipios)
        if self._municipio_pendente and self._municipio_pendente in municipios:
            self.dd_municipio.set(self._municipio_pendente)
            self._municipio_pendente = None
        else:
            self.dd_municipio.set(municipios[0] if municipios else "")

    # ── Construção ────────────────────────────────────────

    def _build(self) -> None:
        make_label(self, "Emitir Nota Fiscal", size=18, bold=True).pack(
            anchor="w", pady=(0, 2)
        )
        make_label(
            self,
            "Selecione o tomador, revise os dados e confirme a emissão.",
            size=12, color="gray",
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

        # ── Modelo de nota ────────────────────────────────
        card_modelo = SectionCard(self)
        card_modelo.pack(fill="x", pady=(0, 12))

        make_label(card_modelo.inner, "Modelo de nota", size=13, bold=True).pack(
            anchor="w", pady=(0, 6)
        )
        row_modelo = ctk.CTkFrame(card_modelo.inner, fg_color="transparent")
        row_modelo.pack(fill="x")
        self.dd_template = ctk.CTkOptionMenu(
            row_modelo,
            values=["Nova nota"],
            width=260,
            command=self._on_selecionar_template,
        )
        self.dd_template.pack(side="left", padx=(0, 8))
        self.btn_excluir_template = ctk.CTkButton(
            row_modelo,
            text="Excluir modelo",
            width=130,
            fg_color="transparent",
            border_width=1,
            text_color="#E24B4A",
            border_color="#E24B4A",
            state="disabled",
            command=self._excluir_template,
        )
        self.btn_excluir_template.pack(side="left")

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
        self.e_data.bind("<KeyRelease>", lambda _: mascaras.aplicar(self.e_data, mascaras.data), "+")

        self.dd_estado = LabeledDropdown(
            card_nota.inner,
            "Estado da Prestação",
            list(ESTADOS_BR.keys()),
            width=340,
        )
        self.dd_estado.pack(anchor="w")
        self.dd_estado.set("Paraná")
        self.dd_estado.configure(command=self._on_estado_change)

        self.dd_municipio = LabeledDropdown(
            card_nota.inner, "Município da Prestação", ["Carregando..."], width=340
        )
        self.dd_municipio.pack(anchor="w")

        self.e_desc = LabeledEntry(card_nota.inner, "Descrição da Nota", width=340)
        self.e_desc.pack(anchor="w")

        self.e_valor = LabeledEntry(
            card_nota.inner, "Valor do Serviço", "R$ 0,00", width=340
        )
        self.e_valor.pack(anchor="w")
        self.e_valor.bind("<KeyRelease>", lambda _: mascaras.aplicar(self.e_valor, mascaras.moeda), "+")

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
            text="💾  Salvar modelo",
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

    def _on_estado_change(self, nome_estado: str) -> None:
        sigla = ESTADOS_BR.get(nome_estado, "PR")
        if sigla == self._uf_carregada:
            return
        self.dd_municipio.set("Carregando...")
        self._carregar_municipios(sigla)

    def _on_selecionar_tomador(self, valor: str) -> None:
        for t in self.tomadores:
            if (t.nome or t.cpfCnpj or "Sem nome") == valor:
                self.tomador_selecionado = t
                break
        self._atualizar_templates()

    # ── Templates (modelos de nota) ───────────────────────

    def _atualizar_templates(self, selecionar: DadosNota = None) -> None:
        notas = getattr(self.tomador_selecionado, "dadosNotas", []) if self.tomador_selecionado else []
        opcoes = ["Nova nota"]
        for i, n in enumerate(notas, 1):
            desc = (n.descricao or "")[:28]
            opcoes.append(f"Modelo {i}: {desc}" if desc else f"Modelo {i}")
        self.dd_template.configure(values=opcoes)

        alvo = selecionar if selecionar in notas else (notas[0] if notas else None)
        if alvo:
            idx = notas.index(alvo)
            self.dd_template.set(opcoes[idx + 1])
            self._nota_selecionada = alvo
            self.btn_excluir_template.configure(state="normal")
            self._preencher_campos()
        else:
            self.dd_template.set("Nova nota")
            self._nota_selecionada = None
            self.btn_excluir_template.configure(state="disabled")
            self._limpar_campos()

    def _on_selecionar_template(self, label: str) -> None:
        if label == "Nova nota":
            self._nota_selecionada = None
            self.btn_excluir_template.configure(state="disabled")
            self._limpar_campos()
            return
        notas = getattr(self.tomador_selecionado, "dadosNotas", []) if self.tomador_selecionado else []
        m = re.match(r"Modelo (\d+)", label)
        if m:
            idx = int(m.group(1)) - 1
            if 0 <= idx < len(notas):
                self._nota_selecionada = notas[idx]
                self.btn_excluir_template.configure(state="normal")
                self._preencher_campos()

    def _excluir_template(self) -> None:
        if not self._nota_selecionada:
            return
        try:
            if self._nota_selecionada.uuid:
                api.deletar_nota(self._nota_selecionada.uuid)
            notas = getattr(self.tomador_selecionado, "dadosNotas", [])
            if self._nota_selecionada in notas:
                notas.remove(self._nota_selecionada)
            self._nota_selecionada = None
            self._atualizar_templates()
            self.lbl_status.success("✓ Modelo excluído.")
        except Exception as exc:
            self.lbl_status.error(f"Erro ao excluir: {str(exc)[:60]}")

    # ── Preenchimento de campos ───────────────────────────

    def _limpar_campos(self) -> None:
        for campo in (self.e_data, self.e_desc, self.e_valor, self.e_resp, self.e_docref, self.e_info):
            campo.delete(0, "end")
        self._municipio_pendente = None

    def _preencher_campos(self) -> None:
        self._limpar_campos()
        nota = self._nota_selecionada
        if not nota:
            return

        self.e_data.insert(
            0, formatar_data_para_ui(nota.dataCompetencia) if nota.dataCompetencia else ""
        )

        if nota.local:
            partes = nota.local.rsplit("/", 1)
            if len(partes) == 2:
                _, sigla = partes
                nome_estado = SIGLA_TO_ESTADO.get(sigla)
                if nome_estado:
                    self.dd_estado.set(nome_estado)
                    if sigla == self._uf_carregada:
                        self.dd_municipio.set(nota.local)
                    else:
                        self._municipio_pendente = nota.local
                        self._carregar_municipios(sigla)

        self.e_desc.insert(0, nota.descricao or "")
        if nota.valorServico:
            centavos = int(round(float(nota.valorServico) * 100))
            self.e_valor.insert(0, mascaras.moeda(str(centavos)))
        self.e_resp.insert(0, nota.numeroRespTecnica or "")
        self.e_docref.insert(0, nota.documentoReferencia or "")
        self.e_info.insert(0, nota.informacoesComplementares or "")
        self.dd_servico.set_from_map(self.map_servicos, nota.codigoTributacao)
        self.dd_nbs.set_from_map(self.map_nbs, nota.nbsServicoPrestado)

    # ── Salvar modelo ─────────────────────────────────────

    def _salvar_nota_padrao(self) -> None:
        if not self.tomador_selecionado:
            self.lbl_status.error("Selecione um tomador primeiro.")
            return

        t = self.tomador_selecionado
        nota_existente = self._nota_selecionada

        nova_nota = DadosNota(
            dataCompetencia=formatar_data_para_bd(self.e_data.get()),
            local=self.dd_municipio.get(),
            codigoTributacao=self.map_servicos.get(self.dd_servico.get(), ""),
            descricao=self.e_desc.get(),
            nbsServicoPrestado=self.map_nbs.get(self.dd_nbs.get(), ""),
            valorServico=mascaras.moeda_para_float(self.e_valor.get()),
            numeroRespTecnica=self.e_resp.get(),
            documentoReferencia=self.e_docref.get(),
            informacoesComplementares=self.e_info.get(),
            tomadorId=t.uuid or "",
            uuid=nota_existente.uuid if nota_existente else "",
        )

        try:
            payload = nova_nota.para_api()
            if nova_nota.uuid:
                api.salvar_nota(nova_nota.uuid, payload)
                notas = t.dadosNotas
                try:
                    notas[notas.index(nota_existente)] = nova_nota
                except ValueError:
                    notas.append(nova_nota)
            else:
                resposta = api.criar_nota(payload)
                nova_nota.uuid = resposta.get("uuid", "")
                t.dadosNotas.append(nova_nota)
            self._atualizar_templates(selecionar=nova_nota)
            self.lbl_status.success("✓ Modelo salvo.")
        except Exception as exc:
            self.lbl_status.error(f"Erro ao salvar: {str(exc)[:60]}")

    # ── Validação ─────────────────────────────────────────

    def _validar(self) -> str | None:
        if not self.tomador_selecionado:
            return "Selecione um tomador."

        digitos_doc = "".join(filter(str.isdigit, self.tomador_selecionado.cpfCnpj or ""))
        if len(digitos_doc) not in (11, 14):
            return "CPF/CNPJ do tomador inválido (deve ter 11 ou 14 dígitos)."

        if len(self.e_data.get().strip()) != 10:
            return "Preencha a data de competência (DD/MM/AAAA)."

        municipio = self.dd_municipio.get()
        if not municipio or municipio in ("Carregando...", ""):
            return "Aguarde o carregamento dos municípios."

        if not self.e_desc.get().strip():
            return "Preencha a descrição da nota."

        if mascaras.moeda_para_float(self.e_valor.get()) <= 0:
            return "Preencha o valor do serviço."

        if self.dd_servico.get() not in self.map_servicos:
            return "Selecione o código de tributação."

        if self.dd_nbs.get() not in self.map_nbs:
            return "Selecione o NBS / Serviço Prestado."

        return None

    # ── Emitir ────────────────────────────────────────────

    def _emitir(self) -> None:
        erro = self._validar()
        if erro:
            self.lbl_status.error(erro)
            return

        try:
            form_data = {
                "data":    self.e_data.get(),
                "local":   self.dd_municipio.get(),
                "descricao": self.e_desc.get(),
                "valor":   mascaras.moeda_para_float(self.e_valor.get()),
                "resp":    self.e_resp.get(),
                "docref":  self.e_docref.get(),
                "info":    self.e_info.get(),
                "servico": self.dd_servico.get(),
                "nbs":     self.dd_nbs.get(),
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