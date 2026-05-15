import threading
import customtkinter as ctk

from ui.helper import make_label
from ui.widgets import SectionCard, LabeledEntry, StatusLabel
from utils import mascaras
from functions.tomador import Tomador
from functions.dadosNota import DadosNota
from config.api import api


class TelaTomadores(ctk.CTkFrame):
    def __init__(self, master, tomadores: list):
        super().__init__(master, fg_color="transparent")
        self.tomadores = tomadores  # lista compartilhada com TelaEmitir
        self.selecionado: Tomador = None
        self._carregado = False
        self._build()

    # ── Lazy loading ──────────────────────────────────────

    def on_show(self) -> None:
        if not self._carregado:
            self._mostrar_carregando()
            threading.Thread(target=self._carregar_dados, daemon=True).start()

    def _mostrar_carregando(self) -> None:
        for w in self.frame_lista.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.frame_lista,
            text="Carregando...",
            text_color="gray",
            font=ctk.CTkFont(size=11),
        ).pack(pady=12)

    def _carregar_dados(self) -> None:
        try:
            lista_api = api.listar_tomadores()
            notas_api = api.listar_notas()

            notas_por_tomador: dict[str, list] = {}
            for n in notas_api:
                tid = n.get("tomadorId")
                if tid:
                    notas_por_tomador.setdefault(tid, []).append(n)

            carregados: list[Tomador] = []
            for item in lista_api:
                t = Tomador(
                    cpfCnpj=item.get("documentoId", ""),
                    telefone=item.get("telefone", ""),
                    email=item.get("email", ""),
                    nome=item.get("nome", ""),
                    cep=item.get("cep", ""),
                )
                t.uuid = item.get("uuid")
                t.dadosNotas = [
                    DadosNota.do_json(n, t.uuid)
                    for n in notas_por_tomador.get(t.uuid, [])
                ]
                carregados.append(t)

            self.tomadores.clear()
            self.tomadores.extend(carregados)
            self._carregado = True
            self.after(0, self._on_dados_carregados)
        except Exception as exc:
            self.after(
                0,
                lambda: ctk.CTkLabel(
                    self.frame_lista,
                    text=f"Erro: {str(exc)[:40]}",
                    text_color="#E24B4A",
                ).pack(pady=8),
            )

    def _on_dados_carregados(self) -> None:
        self._render_lista()
        if self.tomadores:
            self._selecionar(self.tomadores[0])

    # ── Layout principal ──────────────────────────────────

    def _build(self) -> None:
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        left = ctk.CTkFrame(self, width=220, corner_radius=10)
        left.grid(row=0, column=0, sticky="ns", padx=(0, 8))
        left.pack_propagate(False)

        header = ctk.CTkFrame(left, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(12, 8))
        make_label(header, "Tomadores", size=14, bold=True).pack(side="left")
        ctk.CTkButton(
            header, text="+", width=28, height=28, command=self._novo_tomador
        ).pack(side="right")

        self.frame_lista = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.frame_lista.pack(fill="both", expand=True, padx=4)

        self.right = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.right.grid(row=0, column=1, sticky="nsew")

    # ── Lista ─────────────────────────────────────────────

    def _render_lista(self) -> None:
        for w in self.frame_lista.winfo_children():
            w.destroy()
        for t in self.tomadores:
            nome = t.nome or t.cpfCnpj or "Sem nome"
            ctk.CTkButton(
                self.frame_lista,
                text=nome,
                anchor="w",
                height=36,
                fg_color="transparent",
                hover_color=("gray80", "gray25"),
                text_color=("gray20", "gray80"),
                command=lambda tom=t: self._selecionar(tom),
            ).pack(fill="x", pady=2)

    def _selecionar(self, tomador: Tomador) -> None:
        self.selecionado = tomador
        self._render_formulario(tomador)

    # ── Formulário ────────────────────────────────────────

    def _render_formulario(self, tomador: Tomador) -> None:
        for w in self.right.winfo_children():
            w.destroy()

        make_label(self.right, "Dados do Tomador", size=16, bold=True).pack(
            anchor="w", pady=(0, 4)
        )

        card = SectionCard(self.right)
        card.pack(fill="x", pady=(0, 12))

        self.e_nome = LabeledEntry(card.inner, "Nome / Razão Social", "Nome do tomador", width=340)
        self.e_nome.pack(anchor="w")
        self.e_nome.set(tomador.nome or "")

        # CPF/CNPJ — máscara em tempo real, máx. 14 dígitos (CNPJ)
        self.e_cpfcnpj = LabeledEntry(card.inner, "CPF / CNPJ", "000.000.000-00", width=340)
        self.e_cpfcnpj.pack(anchor="w")
        self.e_cpfcnpj.set(mascaras.cpf_cnpj(tomador.cpfCnpj or ""))
        self.e_cpfcnpj.bind(
            "<KeyRelease>",
            lambda _: mascaras.aplicar(self.e_cpfcnpj, mascaras.cpf_cnpj),
            "+",
        )

        # Telefone — máscara em tempo real, máx. 11 dígitos
        self.e_tel = LabeledEntry(card.inner, "Telefone", "(44) 9 9999-9999", width=340)
        self.e_tel.pack(anchor="w")
        self.e_tel.set(mascaras.telefone(tomador.telefone or ""))
        self.e_tel.bind(
            "<KeyRelease>",
            lambda _: mascaras.aplicar(self.e_tel, mascaras.telefone),
            "+",
        )

        self.e_email = LabeledEntry(card.inner, "E-mail", "email@email.com", width=340)
        self.e_email.pack(anchor="w")
        self.e_email.set(tomador.email or "")

        row = ctk.CTkFrame(card.inner, fg_color="transparent")
        row.pack(anchor="e", pady=(16, 0))

        ctk.CTkButton(
            row,
            text="Excluir",
            fg_color="transparent",
            border_width=1,
            text_color="#E24B4A",
            border_color="#E24B4A",
            width=100,
            command=self._excluir_tomador,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(row, text="Salvar", width=100, command=self._salvar).pack(side="left")

        self.lbl_status = StatusLabel(card.inner)
        self.lbl_status.pack(anchor="w", pady=(8, 0))

    # ── Ações ─────────────────────────────────────────────

    def _salvar(self) -> None:
        if not self.selecionado:
            return
        t = self.selecionado
        t.nome = self.e_nome.get()
        # remove máscara antes de salvar
        t.cpfCnpj  = "".join(filter(str.isdigit, self.e_cpfcnpj.get()))
        t.telefone = "".join(filter(str.isdigit, self.e_tel.get()))
        t.email    = self.e_email.get()

        try:
            if t.uuid:
                api.salvar_tomador(t.uuid, {
                    "nome":        t.nome,
                    "documentoId": t.cpfCnpj,
                    "telefone":    t.telefone,
                    "email":       t.email,
                })
            else:
                resposta = api.criar_tomador({
                    "nome":        t.nome,
                    "documentoId": t.cpfCnpj,
                    "telefone":    t.telefone,
                    "email":       t.email,
                })
                t.uuid = resposta.get("uuid", "")
            self.lbl_status.success("✓ Tomador salvo.")
        except Exception as exc:
            self.lbl_status.error(f"Erro: {str(exc)[:60]}")

        self._render_lista()

    def _excluir_tomador(self) -> None:
        if not self.selecionado:
            return
        try:
            if self.selecionado.uuid:
                api.deletar_tomador(self.selecionado.uuid)
            self.tomadores.remove(self.selecionado)
            self.selecionado = None
            self._render_lista()
            for w in self.right.winfo_children():
                w.destroy()
        except Exception as exc:
            self.lbl_status.error(f"Erro ao excluir: {str(exc)[:60]}")

    def _novo_tomador(self) -> None:
        novo = Tomador("", "", "", "", "Novo Tomador")
        self.tomadores.append(novo)
        self._render_lista()
        self._selecionar(novo)