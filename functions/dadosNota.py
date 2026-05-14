class DadosNota:
    def __init__(
        self,
        dataCompetencia: str = "",
        local: str = "",
        codigoTributacao: str = "",      # uuid → listaServico
        descricao: str = "",
        nbsServicoPrestado: str = "",    # uuid → listaNbs
        valorServico: str = "",
        numeroRespTecnica: str = "",
        documentoReferencia: str = "",
        informacoesComplementares: str = "",
        tomadorId: str = "",
        uuid: str = "",
    ):
        self.dataCompetencia = dataCompetencia
        self.local = local
        self.codigoTributacao = codigoTributacao        # uuid do serviço (listaServico)
        self.descricao = descricao
        self.nbsServicoPrestado = nbsServicoPrestado    # uuid do NBS (listaNbs)
        self.valorServico = valorServico
        self.numeroRespTecnica = numeroRespTecnica
        self.documentoReferencia = documentoReferencia
        self.informacoesComplementares = informacoesComplementares
        self.tomadorId = tomadorId
        self.uuid = uuid                                 # uuid da nota padrão (PK)

    def para_api(self) -> dict:
        """Serializa para o payload esperado pela API (POST/PUT /notaPadrao)."""
        return {
            "dataCompetencia": self.dataCompetencia,
            "local": self.local,
            "codigoTributacao": self.codigoTributacao or None,
            "descricao": self.descricao,
            "nbsServicoPrestado": self.nbsServicoPrestado or None,
            "valorServico": self.valorServico or None,
            "numeroRespTecnica": self.numeroRespTecnica or None,
            "documentoReferencia": self.documentoReferencia or None,
            "informacoesComplementares": self.informacoesComplementares or None,
            "tomadorId": self.tomadorId,
        }

    @staticmethod
    def do_json(dados: dict, tomador_uuid: str = "") -> "DadosNota":
        """Cria um DadosNota a partir do dict retornado pela API."""
        return DadosNota(
            dataCompetencia=dados.get("dataCompetencia", ""),
            local=dados.get("local", ""),
            codigoTributacao=dados.get("codigoTributacao", ""),
            descricao=dados.get("descricao", ""),
            nbsServicoPrestado=dados.get("nbsServicoPrestado", ""),
            valorServico=str(dados.get("valorServico", "")),
            numeroRespTecnica=dados.get("numeroRespTecnica", ""),
            documentoReferencia=dados.get("documentoReferencia", ""),
            informacoesComplementares=dados.get("informacoesComplementares", ""),
            tomadorId=tomador_uuid or dados.get("tomadorId", ""),
            uuid=dados.get("uuid", ""),
        )
