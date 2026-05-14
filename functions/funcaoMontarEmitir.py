from config.api import api
from functions.dadosNota import DadosNota
from functions.tomador import Tomador
from functions.dadosPrestador import DadosPrestador
from functions.emitirNotaExecutar import executar_automacao
from utils.formatarData import formatar_data_para_ui


def somente_numeros(valor: str) -> str:
    return "".join(filter(str.isdigit, valor or ""))

def formatar_para_automacao(valor: float) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def emitir_nota_service(form_data: dict, tomador_raw, map_servicos, map_nbs,prestador):
    """
    Regra principal de emissão (SEM UI).
    """
    valor_formatado = formatar_para_automacao(form_data["valor"])

    # 🔹 Buscar serviço
    servicos = api.buscar_servico_por_uuid(
        map_servicos.get(form_data["servico"], "")
    )

    if not servicos:
        raise Exception("Serviço não encontrado")

    servico = servicos[0]

    # 🔹 Buscar NBS
    nbs = api.buscar_nbs_por_uuid(
        map_nbs.get(form_data["nbs"], "")
    )

    if not nbs:
        raise Exception("NBS não encontrado")

    nbsFiltrado = nbs[0]

    codigoNbs = somente_numeros(nbsFiltrado.get("codigo", ""))

    # 🔹 Buscar PisRetencao
    pisCofinsRetencao = api.buscar_pisRetencoes_por_uuid(
        prestador.pisCofinsRetencao)

    if not pisCofinsRetencao:
        raise Exception("pisCofinsRetencao não encontrado")

    pisCofinsRetencaoFiltrado = pisCofinsRetencao[0]

    # 🔹 Buscar PisSituação
    pisCofinsSituacao = api.buscar_pisSituacao_por_uuid(
        prestador.pisCofinsSituacao)

    if not pisCofinsSituacao:
        raise Exception("pisCofinsSituacao não encontrado")

    pisCofinsSituacaoFiltrado = pisCofinsSituacao[0]


    # 🔹 Montar dados da nota
    dadosNota = DadosNota(
        dataCompetencia=formatar_data_para_ui(form_data["data"]),
        local=form_data["local"],
        codigoTributacao=f"{servico.get('codigo')} - {servico.get('descricao')}",
        descricao=form_data["descricao"],
        nbsServicoPrestado=f"{codigoNbs} - {nbsFiltrado.get('descricao')}",
        valorServico=valor_formatado,
        numeroRespTecnica=form_data["resp"],
        documentoReferencia=form_data["docref"],
        informacoesComplementares=form_data["info"],
    )

    # 🔹 Tomador
    tomador = Tomador(
        cpfCnpj=tomador_raw.cpfCnpj,
        telefone=tomador_raw.telefone,
        email=tomador_raw.email,
        nome=tomador_raw.nome,
        cep=tomador_raw.cep,
    )

    # 🔹 Prestador (AGORA DECENTE)
    dadosPrestador = DadosPrestador(
        cnpj=prestador.cnpj,
        porcentagemTributacao=prestador.porcentagemTributacao,
        pisCofinsSituacao=f"{pisCofinsSituacaoFiltrado.get('codigo')} - {pisCofinsSituacaoFiltrado.get('descricao')}",
        pisCofinsRetencao=pisCofinsRetencaoFiltrado.get('descricao'),
        porcentagemPis=prestador.porcentagemPis,
        porcentagemCofins=prestador.porcentagemCofins,
        valorCsll=prestador.valorCsll,
        )
    
    # 🔹 Executa automação
    executar_automacao(dadosNota, tomador, dadosPrestador)