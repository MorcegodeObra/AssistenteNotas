class DadosPrestador:
    def __init__(self, cnpj, porcentagemTributacao, pisCofinsSituacao, pisCofinsRetencao,
                 porcentagemPis=None, porcentagemCofins=None, valorCsll=None):
        self.cnpj = cnpj
        self.porcentagemTributacao = porcentagemTributacao
        self.pisCofinsSituacao = pisCofinsSituacao
        self.pisCofinsRetencao = pisCofinsRetencao
        self.porcentagemPis = porcentagemPis or ""
        self.porcentagemCofins = porcentagemCofins or ""
        self.valorCsll = valorCsll or ""
