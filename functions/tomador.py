class Tomador:
    def __init__(self, cpfCnpj, telefone, email,cep, nome):
        self.cpfCnpj = cpfCnpj
        self.telefone = telefone
        self.email = email
        self.cep = cep
        self.nome = nome
        self.uuid = None
        self.dadosNotas: list = []
