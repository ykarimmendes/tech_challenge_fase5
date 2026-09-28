"""Núcleo sem estado global: a aplicação fornece e persiste cada conversa."""

from copy import deepcopy
from dataclasses import dataclass
from typing import Callable
import re
import unicodedata

from rag import buscar_contexto, formatar_contexto
from llm_client import LLMError
from prompts import mensagens_extracao
from schemas import (
    EXTRACAO_SCHEMA,
    validar_entrada,
    validar_extracao
)


# ==================================================
# PERGUNTAS PADRÃO
# ==================================================

PERGUNTAS = {

    "intencao":
        "Você procura um imóvel para comprar, alugar ou investir?",

    "orcamento_ticket":
        "Qual é o seu orçamento máximo?",

    "regiao_bairro":
        "Em qual bairro ou região você procura?",

    "tipo_imovel_interesse":
        (
            "Que tipo de imóvel você procura: "
            "apartamento, casa, studio ou cobertura?"
        ),

    "quartos":
        "Quantos quartos você precisa?",

    "urgencia":
        (
            "Como você considera sua urgência: "
            "alta, média ou baixa?"
        ),

    "perfil_investidor":
        (
            "Seu perfil de investimento é "
            "conservador, moderado ou arrojado?"
        ),

    "retorno_esperado_pct":
        "Qual retorno percentual anual você espera?"
}


# ==================================================
# SERVIÇOS
# ==================================================

@dataclass
class Servicos:

    llm: object

    buscar_imoveis: Callable | None = None

    calcular_score: Callable | None = None


# ==================================================
# NORMALIZAÇÃO
# ==================================================

def _normalizar_texto(texto):

    if texto is None:
        return ""

    return "".join(

        c

        for c in unicodedata.normalize(
            "NFD",
            str(texto).casefold()
        )

        if unicodedata.category(c) != "Mn"
    )


# ==================================================
# REMOÇÃO EXPLÍCITA
# ==================================================

def _remocao_explicita(mensagem):

    texto = _normalizar_texto(
        mensagem
    )

    return bool(

        re.search(

            r"\b("
            r"remov\w*|"
            r"apag\w*|"
            r"esquec\w*|"
            r"retir\w*|"
            r"desconsider\w*"
            r")\b"

            r"|"

            r"\b("
            r"sem preferencia|"
            r"nao (tenho|quero) (mais )?preferencia|"
            r"qualquer bairro|"
            r"tanto faz|"
            r"indiferente"
            r")\b",

            texto
        )
    )


# ==================================================
# VERIFICAR SE A RESPOSTA É DA ÚLTIMA PERGUNTA
# ==================================================

def _respondendo_campo(
    estado,
    campo
):

    ultima = estado.get(
        "ultima_pergunta"
    )

    if not ultima:
        return False

    pergunta_padrao = (
        PERGUNTAS.get(
            campo
        )
    )

    if (
        pergunta_padrao
        and
        ultima == pergunta_padrao
    ):

        return True


    # ----------------------------------------------
    # ORÇAMENTO DE ALUGUEL
    # ----------------------------------------------

    if (
        campo == "orcamento_ticket"
        and
        "orcamento mensal" in _normalizar_texto(
            ultima
        )
    ):

        return True


    # ----------------------------------------------
    # TICKET DE INVESTIMENTO
    # ----------------------------------------------

    if (
        campo == "orcamento_ticket"
        and
        "valor voce pretende investir" in
        _normalizar_texto(
            ultima
        )
    ):

        return True


    return False


# ==================================================
# VALIDAÇÃO DE INTENÇÃO
# ==================================================

def _intencao_explicita(
    mensagem,
    estado
):

    texto = _normalizar_texto(
        mensagem
    )

    if _respondendo_campo(
        estado,
        "intencao"
    ):

        return True

    termos = [

        "comprar",
        "compra",

        "alugar",
        "aluguel",

        "investir",
        "investimento"
    ]

    return any(
        termo in texto
        for termo in termos
    )


# ==================================================
# VALIDAÇÃO DO TIPO DE IMÓVEL
# ==================================================

def _tipo_explicito(
    mensagem,
    estado
):

    if _respondendo_campo(
        estado,
        "tipo_imovel_interesse"
    ):

        return True

    texto = _normalizar_texto(
        mensagem
    )

    tipos = [

        "apartamento",
        "casa",
        "studio",
        "estudio",
        "cobertura"
    ]

    return any(
        re.search(
            rf"\b{tipo}\b",
            texto
        )
        for tipo in tipos
    )


# ==================================================
# VALIDAÇÃO DE URGÊNCIA
# ==================================================

def _urgencia_explicita(
    mensagem,
    estado
):

    texto = _normalizar_texto(
        mensagem
    ).strip()

    if _respondendo_campo(
        estado,
        "urgencia"
    ):

        return (
            texto
            in [
                "alta",
                "media",
                "baixa"
            ]
            or
            "urgencia" in texto
        )

    return bool(
        re.search(
            r"\burgencia\s+"
            r"(alta|media|baixa)\b",
            texto
        )
    )


# ==================================================
# VALIDAÇÃO DO PERFIL INVESTIDOR
# ==================================================

def _perfil_investidor_explicito(
    mensagem,
    estado
):

    texto = _normalizar_texto(
        mensagem
    )

    perfis = [

        "conservador",
        "conservadora",

        "moderado",
        "moderada",

        "arrojado",
        "arrojada"
    ]


    if _respondendo_campo(
        estado,
        "perfil_investidor"
    ):

        return any(
            re.search(
                rf"\b{perfil}\b",
                texto
            )
            for perfil in perfis
        )


    return any(
        re.search(
            rf"\b{perfil}\b",
            texto
        )
        for perfil in perfis
    )


# ==================================================
# VALIDAÇÃO DO RETORNO
# ==================================================

def _retorno_explicito(
    mensagem,
    estado
):

    texto = _normalizar_texto(
        mensagem
    )

    if _respondendo_campo(
        estado,
        "retorno_esperado_pct"
    ):

        return bool(
            re.search(
                r"\d+(?:[.,]\d+)?\s*%",
                texto
            )
            or
            "por cento" in texto
        )


    return bool(
        re.search(
            r"\d+(?:[.,]\d+)?\s*%",
            texto
        )
        or
        "por cento" in texto
    )


# ==================================================
# VALIDAÇÃO DO ORÇAMENTO
# ==================================================

def _orcamento_explicito(
    mensagem,
    estado
):

    texto = _normalizar_texto(
        mensagem
    )

    if _respondendo_campo(
        estado,
        "orcamento_ticket"
    ):

        return bool(
            re.search(
                r"\d",
                texto
            )
            or
            re.search(
                r"\b("
                r"mil|"
                r"milhao|"
                r"milhoes|"
                r"reais"
                r")\b",
                texto
            )
        )


    return bool(

        re.search(
            r"\d",
            texto
        )

        and

        re.search(
            r"\b("
            r"real|"
            r"reais|"
            r"mil|"
            r"milhao|"
            r"milhoes|"
            r"orcamento|"
            r"investir|"
            r"gastar|"
            r"ate"
            r")\b",
            texto
        )
    )


# ==================================================
# VALIDAÇÃO DE QUARTOS
# ==================================================

def _quartos_explicito(
    mensagem,
    estado
):

    texto = _normalizar_texto(
        mensagem
    )


    if _respondendo_campo(
        estado,
        "quartos"
    ):

        return bool(
            re.search(
                r"\d",
                texto
            )
        )


    return bool(

        re.search(
            r"\b("
            r"quarto|"
            r"quartos|"
            r"dormitorio|"
            r"dormitorios"
            r")\b",
            texto
        )
    )


# ==================================================
# VALIDAÇÃO DE REGIÃO
# ==================================================

def _regiao_explicita(
    mensagem,
    estado,
    valor_extraido
):

    if _respondendo_campo(
        estado,
        "regiao_bairro"
    ):

        return True


    texto = _normalizar_texto(
        mensagem
    )


    valor = _normalizar_texto(
        valor_extraido
    )


    if (
        valor
        and
        valor in texto
    ):

        return True


    return False


# ==================================================
# VALIDAÇÃO DE ZONA
# ==================================================

def _zona_explicita(
    mensagem,
    estado,
    valor_extraido
):

    texto = _normalizar_texto(
        mensagem
    )

    valor = _normalizar_texto(
        valor_extraido
    )


    if (
        valor
        and
        valor in texto
    ):

        return True


    return bool(
        re.search(
            r"\bzona\s+"
            r"(norte|sul|leste|oeste|central)\b",
            texto
        )
    )


# ==================================================
# VALIDAÇÃO DE PREFERÊNCIAS
# ==================================================

def _preferencia_explicita(
    mensagem,
    campo
):

    texto = _normalizar_texto(
        mensagem
    )


    termos_por_campo = {

        "aceita_pet": [
            "pet",
            "animal",
            "cachorro",
            "gato"
        ],

        "prefere_mobiliado": [
            "mobiliado",
            "mobiliada",
            "mobília",
            "mobilia"
        ],

        "prefere_proximo_metro": [
            "metro",
            "metrô"
        ],

        "prefere_imovel_novo": [
            "imovel novo",
            "imóvel novo",
            "novo",
            "nova"
        ]
    }


    termos = (
        termos_por_campo.get(
            campo,
            []
        )
    )


    return any(
        _normalizar_texto(
            termo
        )
        in texto
        for termo in termos
    )


# ==================================================
# VALIDAÇÃO DE PRAZO
# ==================================================

def _prazo_explicito(
    mensagem,
    valor_extraido
):

    texto = _normalizar_texto(
        mensagem
    )

    valor = _normalizar_texto(
        valor_extraido
    )


    if (
        valor
        and
        valor in texto
    ):

        return True


    return bool(
        re.search(
            r"\b\d+\s*"
            r"(dia|dias|semana|semanas|mes|meses)\b",
            texto
        )
    )


# ==================================================
# VALIDAÇÃO DE ACEITE
# ==================================================

def _aceite_explicito(
    mensagem,
    estado
):

    ultima = _normalizar_texto(
        estado.get(
            "ultima_pergunta"
        )
    )


    texto = _normalizar_texto(
        mensagem
    ).strip()


    contexto_agendamento = any(

        termo in ultima

        for termo in [

            "visita",
            "reuniao",
            "corretor",
            "especialista",
            "conversar"
        ]
    )


    if not contexto_agendamento:
        return False


    respostas = [

        "sim",
        "quero",
        "aceito",
        "pode",
        "gostaria",

        "nao",
        "não",
        "nao quero"
    ]


    return any(
        _normalizar_texto(
            resposta
        )
        in texto
        for resposta in respostas
    )


# ==================================================
# FILTRAR ATUALIZAÇÕES DA LLM
# ==================================================

def _filtrar_atualizacoes(
    updates,
    mensagem,
    estado
):

    filtrados = {}


    for campo, valor in updates.items():

        if valor is None:
            continue


        # ------------------------------------------
        # REMOÇÃO EXPLÍCITA
        # ------------------------------------------

        if (
            valor == "__REMOVER__"
        ):

            if _remocao_explicita(
                mensagem
            ):

                filtrados[
                    campo
                ] = valor

            continue


        # ------------------------------------------
        # INTENÇÃO
        # ------------------------------------------

        if campo == "intencao":

            if _intencao_explicita(
                mensagem,
                estado
            ):

                filtrados[
                    campo
                ] = valor

            continue


        # ------------------------------------------
        # TIPO
        # ------------------------------------------

        if campo == "tipo_imovel_interesse":

            if _tipo_explicito(
                mensagem,
                estado
            ):

                filtrados[
                    campo
                ] = valor

            continue


        # ------------------------------------------
        # URGÊNCIA
        # ------------------------------------------

        if campo == "urgencia":

            if _urgencia_explicita(
                mensagem,
                estado
            ):

                filtrados[
                    campo
                ] = valor

            continue


        # ------------------------------------------
        # PERFIL INVESTIDOR
        # ------------------------------------------

        if campo == "perfil_investidor":

            if _perfil_investidor_explicito(
                mensagem,
                estado
            ):

                filtrados[
                    campo
                ] = valor

            continue


        # ------------------------------------------
        # RETORNO
        # ------------------------------------------

        if campo == "retorno_esperado_pct":

            if _retorno_explicito(
                mensagem,
                estado
            ):

                filtrados[
                    campo
                ] = valor

            continue


        # ------------------------------------------
        # ORÇAMENTO
        # ------------------------------------------

        if campo == "orcamento_ticket":

            if _orcamento_explicito(
                mensagem,
                estado
            ):

                filtrados[
                    campo
                ] = valor

            continue


        # ------------------------------------------
        # QUARTOS
        # ------------------------------------------

        if campo == "quartos":

            if _quartos_explicito(
                mensagem,
                estado
            ):

                filtrados[
                    campo
                ] = valor

            continue


        # ------------------------------------------
        # REGIÃO
        # ------------------------------------------

        if campo == "regiao_bairro":

            if _regiao_explicita(
                mensagem,
                estado,
                valor
            ):

                filtrados[
                    campo
                ] = valor

            continue


        # ------------------------------------------
        # ZONA
        # ------------------------------------------

        if campo == "zona_preferida":

            if _zona_explicita(
                mensagem,
                estado,
                valor
            ):

                filtrados[
                    campo
                ] = valor

            continue


        # ------------------------------------------
        # PRAZO
        # ------------------------------------------

        if campo == "prazo_declarado":

            if _prazo_explicito(
                mensagem,
                valor
            ):

                filtrados[
                    campo
                ] = valor

            continue


        # ------------------------------------------
        # PREFERÊNCIAS
        # ------------------------------------------

        if campo in [

            "aceita_pet",

            "prefere_mobiliado",

            "prefere_proximo_metro",

            "prefere_imovel_novo"

        ]:

            if _preferencia_explicita(
                mensagem,
                campo
            ):

                filtrados[
                    campo
                ] = valor

            continue


        # ------------------------------------------
        # ACEITE
        # ------------------------------------------

        if campo == "aceitou_visita_reuniao":

            if _aceite_explicito(
                mensagem,
                estado
            ):

                filtrados[
                    campo
                ] = valor

            continue


    return filtrados


# ==================================================
# VALIDAR EVENTO
# ==================================================

def _validar_evento(
    evento,
    mensagem
):

    texto = _normalizar_texto(
        mensagem
    )


    if evento == "humano":

        termos = [

            "corretor",
            "especialista",
            "atendente",
            "pessoa",
            "humano"
        ]

        if any(
            termo in texto
            for termo in termos
        ):

            return "humano"

        return "continuar"


    if evento == "desistir":

        termos = [

            "parar",
            "desistir",
            "encerrar",
            "nao quero mais",
            "nao me contate"
        ]

        if any(
            termo in texto
            for termo in termos
        ):

            return "desistir"

        return "continuar"


    if evento == "resumo":

        if "resumo" in texto:

            return "resumo"

        return "continuar"


    return "continuar"


# ==================================================
# CAMPOS FALTANTES
# ==================================================

def campos_faltantes(
    perfil
):

    if perfil[
        "intencao"
    ] is None:

        return [
            "intencao"
        ]


    # ----------------------------------------------
    # INVESTIMENTO
    # ----------------------------------------------

    if (
        perfil[
            "intencao"
        ]
        == "Investimento"
    ):

        campos = [

            "orcamento_ticket",

            "perfil_investidor",

            "retorno_esperado_pct",

            "urgencia"
        ]


    # ----------------------------------------------
    # COMPRA / ALUGUEL
    # ----------------------------------------------

    else:

        campos = [

            "orcamento_ticket",

            "regiao_bairro",

            "tipo_imovel_interesse",

            "quartos",

            "urgencia"
        ]


    return [

        campo

        for campo in campos

        if perfil[
            campo
        ] is None
    ]


# ==================================================
# GERAR RESUMO DO ESTADO
# ==================================================

def gerar_resumo(
    estado
):

    linhas = [

        f'{k}: '
        f'{"não informado" if v is None else v}'

        for k, v
        in estado[
            "perfil"
        ].items()
    ]


    score = estado.get(
        "score"
    )


    linhas.append(
        "Score: "
        + (
            str(score)
            if score is not None
            else "pendente"
        )
    )


    linhas.append(
        "Classificação: "
        + (
            estado.get(
                "classificacao"
            )
            or "pendente"
        )
    )


    linhas.append(
        f'Situação: {estado["status"]}'
    )


    linhas.append(
        "Agendamento: nenhum registro "
        "confirmado pelo núcleo."
    )


    return "\n".join(
        linhas
    )


# ==================================================
# RESULTADO PADRÃO
# ==================================================

def _resultado(
    estado,
    resposta,
    acao,
    alterados=None,
    erro=None
):

    return {

        "resposta":
            resposta,

        "estado_atualizado":
            estado,

        "campos_alterados":
            alterados or [],

        "campos_faltantes":
            campos_faltantes(
                estado[
                    "perfil"
                ]
            ),

        "acao":
            acao,

        "imoveis_ids":
            list(
                estado[
                    "imoveis_ids"
                ]
            ),

        "solicitacao_agendamento":
            None,

        "resumo_corretor":
            gerar_resumo(
                estado
            ),

        "erro":
            erro
    }


def _parece_pergunta_informativa(mensagem):
    """
    Identifica perguntas que podem ser respondidas pela
    base de conhecimento do RAG.
    """

    texto = _normalizar_texto(mensagem).strip()

    inicios = (
        "o que e ",
        "o que sao ",
        "como funciona ",
        "como funciona o ",
        "como funciona a ",
        "quais sao ",
        "quais os ",
        "quais as ",
        "qual e ",
        "qual a ",
        "qual o ",
        "por que ",
        "porque ",
        "para que serve ",
        "como posso ",
        "como faco ",
        "que documentos ",
        "quais documentos ",
        "que custos ",
        "quais custos ",
    )

    if texto.startswith(inicios):
        return True

    if "?" in mensagem:
        return True

    return False


def _respondendo_qualificacao(estado):
    """
    Evita que uma resposta curta à pergunta de qualificação
    seja enviada ao RAG.
    """

    ultima = estado.get("ultima_pergunta")

    if not ultima:
        return False

    perguntas_qualificacao = set(PERGUNTAS.values())

    perguntas_qualificacao.update({
        "Qual é seu orçamento mensal máximo para o aluguel?",
        "Qual valor você pretende investir em imóveis?",
    })

    return ultima in perguntas_qualificacao


def _tentar_responder_com_rag(mensagem, estado, servicos):
    """
    Tenta responder uma dúvida imobiliária usando RAG.

    Retorna None quando a mensagem deve continuar
    pelo fluxo SDR normal.
    """

    # Se o agente acabou de fazer uma pergunta de qualificação,
    # priorizamos a resposta do lead.
    if _respondendo_qualificacao(estado):
        return None

    if not _parece_pergunta_informativa(mensagem):
        return None

    try:
        resultados = buscar_contexto(
            mensagem,
            top_k=3,
            limite_similaridade=0.08
        )
    except (OSError, ValueError, TypeError):
        return None

    if not resultados:
        return None

    contexto = formatar_contexto(
        resultados
    )

    if not contexto:
        return None

    try:
        resposta = servicos.llm.responder_com_contexto(
            mensagem,
            contexto
        )
    except (LLMError, ValueError, TypeError):
        return None

    fontes = [
        item["titulo"]
        for item in resultados
    ]

    return {
        "resposta": resposta,
        "fontes": fontes
    }

# ==================================================
# PROCESSAR MENSAGEM
# ==================================================

def processar_mensagem(
    entrada,
    servicos
):

    """
    Entrada inválida gera ValueError.

    Falha do LLM retorna erro sem alterar
    o estado da conversa.
    """


    estado = validar_entrada(
        entrada
    )


    # ==================================================
    # CONVERSA JÁ ENCERRADA
    # ==================================================

    if (
        estado[
            "status"
        ]
        != "ativo"
    ):

        return _resultado(

            estado,

            (
                "Este atendimento já foi encerrado "
                "ou encaminhado. "
                "Inicie uma nova conversa para retomar."
            ),

            "encerrar"
        )
        # ==================================================
    # RAG - PERGUNTAS INFORMATIVAS
    # ==================================================

    resultado_rag = _tentar_responder_com_rag(
        entrada["mensagem"],
        estado,
        servicos
    )

    if resultado_rag is not None:

        resposta = resultado_rag["resposta"]

        fontes = resultado_rag["fontes"]

        if fontes:
            resposta += (
                "\n\n📚 Base consultada: "
                + ", ".join(fontes)
            )

        return _resultado(
            estado,
            resposta,
            "responder_rag"
        )


    # ==================================================
    # EXTRAÇÃO
    # ==================================================

    try:

        # ------------------------------------------
        # URGÊNCIA: RESPOSTA CURTA
        # ------------------------------------------

        urgencias = {

            "alta":
                "Alta",

            "média":
                "Média",

            "media":
                "Média",

            "baixa":
                "Baixa"
        }


        escolha = (
            entrada[
                "mensagem"
            ]
            .strip()
            .rstrip(
                ".!"
            )
            .casefold()
        )


        if (
            estado[
                "ultima_pergunta"
            ]
            == PERGUNTAS[
                "urgencia"
            ]

            and

            escolha
            in urgencias
        ):

            extracao = {

                "atualizacoes": {

                    "urgencia":
                        urgencias[
                            escolha
                        ]
                },

                "evento":
                    "continuar",

                "esclarecimento":
                    None
            }


        # ------------------------------------------
        # LLM
        # ------------------------------------------

        else:

            extracao = (

                validar_extracao(

                    servicos.llm.extrair(

                        mensagens_extracao(
                            entrada,
                            estado
                        ),

                        EXTRACAO_SCHEMA
                    )
                )
            )


        # ------------------------------------------
        # FILTRO ANTI-HALLUCINAÇÃO
        # ------------------------------------------

        extracao[
            "atualizacoes"
        ] = _filtrar_atualizacoes(

            extracao.get(
                "atualizacoes",
                {}
            ),

            entrada[
                "mensagem"
            ],

            estado
        )


        # ------------------------------------------
        # EVENTO TAMBÉM É VALIDADO
        # ------------------------------------------

        extracao[
            "evento"
        ] = _validar_evento(

            extracao.get(
                "evento",
                "continuar"
            ),

            entrada[
                "mensagem"
            ]
        )


    except (
        LLMError,
        ValueError,
        TypeError
    ):

        return _resultado(

            estado,

            (
                "Não consegui interpretar "
                "sua mensagem agora. "
                "Pode tentar novamente?"
            ),

            "tentar_novamente",

            erro="falha_extracao"
        )


    # ==================================================
    # PERFIL ANTERIOR
    # ==================================================

    anterior = deepcopy(
        estado[
            "perfil"
        ]
    )


    updates = (
        extracao[
            "atualizacoes"
        ]
    )


    # ==================================================
    # MUDANÇA DE INTENÇÃO
    # ==================================================

    mudou_intencao = (

        "intencao"
        in updates

        and

        updates[
            "intencao"
        ]
        != anterior[
            "intencao"
        ]
    )


    if (
        mudou_intencao

        and

        anterior[
            "intencao"
        ]
        is not None
    ):

        for campo in [

            "orcamento_ticket",

            "aceitou_visita_reuniao",

            "perfil_investidor",

            "retorno_esperado_pct"

        ]:

            estado[
                "perfil"
            ][
                campo
            ] = None


    # ==================================================
    # APLICAR ATUALIZAÇÕES
    # ==================================================

    estado[
        "perfil"
    ].update(
        updates
    )


    alterados = [

        campo

        for campo
        in anterior

        if (
            anterior[
                campo
            ]
            !=
            estado[
                "perfil"
            ][
                campo
            ]
        )
    ]


    if alterados:

        estado[
            "imoveis_ids"
        ] = []

        estado[
            "score"
        ] = None

        estado[
            "classificacao"
        ] = None


    # ==================================================
    # EVENTOS
    # ==================================================

    evento = (
        extracao[
            "evento"
        ]
    )


    # ----------------------------------------------
    # HUMANO
    # ----------------------------------------------

    if evento == "humano":

        estado[
            "status"
        ] = (
            "encaminhamento_solicitado"
        )


        estado[
            "ultima_pergunta"
        ] = None


        # ------------------------------------------
        # INVESTIMENTO
        # ------------------------------------------

        if (
            estado[
                "perfil"
            ][
                "intencao"
            ]
            == "Investimento"
        ):

            return _resultado(

                estado,

                (
                    "Perfeito. Vou encaminhar "
                    "seu perfil para um especialista "
                    "em investimentos imobiliários."
                ),

                "encaminhar_especialista",

                alterados
            )


        # ------------------------------------------
        # COMPRA / ALUGUEL
        # ------------------------------------------

        return _resultado(

            estado,

            (
                "Vou solicitar atendimento "
                "de um corretor para você."
            ),

            "encaminhar_humano",

            alterados
        )


    # ----------------------------------------------
    # DESISTÊNCIA
    # ----------------------------------------------

    if evento == "desistir":

        estado[
            "status"
        ] = "encerrado"


        estado[
            "ultima_pergunta"
        ] = None


        return _resultado(

            estado,

            (
                "Tudo bem. "
                "Encerrei este atendimento "
                "e não solicitarei novos contatos."
            ),

            "encerrar",

            alterados
        )


    # ==================================================
    # SCORE
    # ==================================================

    if (
        servicos.calcular_score

        and

        estado[
            "perfil"
        ][
            "intencao"
        ]
    ):

        try:

            score = (
                servicos.calcular_score(

                    deepcopy(
                        estado[
                            "perfil"
                        ]
                    )
                )
            )


            pontos = (
                score[
                    "score"
                ]
            )


            if (
                type(
                    pontos
                )
                is not int

                or

                not 0
                <= pontos
                <= 100
            ):

                raise ValueError(
                    "Score inválido"
                )


            classe = (

                "Frio"

                if pontos < 40

                else "Morno"

                if pontos < 70

                else "Quente"
            )


            if (
                score[
                    "classificacao"
                ]
                != classe
            ):

                raise ValueError(
                    "Classificação inconsistente"
                )


            perfil = (
                estado[
                    "perfil"
                ]
            )


            # --------------------------------------
            # INVESTIDOR INCOMPLETO
            # --------------------------------------

            if (
                perfil[
                    "intencao"
                ]
                == "Investimento"

                and

                (
                    perfil[
                        "perfil_investidor"
                    ]
                    is None

                    or

                    perfil[
                        "retorno_esperado_pct"
                    ]
                    is None
                )

                and

                pontos > 69
            ):

                raise ValueError(
                    "Investidor incompleto"
                )


            estado[
                "score"
            ] = pontos


            estado[
                "classificacao"
            ] = classe


        except (
            ValueError,
            TypeError,
            KeyError,
            RuntimeError
        ):

            estado[
                "score"
            ] = None

            estado[
                "classificacao"
            ] = None


            return _resultado(

                estado,

                (
                    "Registrei seus dados, "
                    "mas a qualificação está "
                    "temporariamente indisponível."
                ),

                "tentar_novamente",

                alterados,

                "falha_score"
            )


    # ==================================================
    # RESUMO
    # ==================================================

    if evento == "resumo":

        return _resultado(

            estado,

            gerar_resumo(
                estado
            ),

            "perguntar",

            alterados
        )


    # ==================================================
    # ESCLARECIMENTO
    # ==================================================

    if (
        extracao.get(
            "esclarecimento"
        )
    ):

        estado[
            "ultima_pergunta"
        ] = (
            extracao[
                "esclarecimento"
            ]
        )


        return _resultado(

            estado,

            extracao[
                "esclarecimento"
            ],

            "perguntar",

            alterados
        )


    # ==================================================
    # PRÓXIMO CAMPO
    # ==================================================

    faltantes = (
        campos_faltantes(
            estado[
                "perfil"
            ]
        )
    )


    if faltantes:

        campo = (
            faltantes[
                0
            ]
        )


        pergunta = (
            PERGUNTAS[
                campo
            ]
        )


        # ------------------------------------------
        # ALUGUEL
        # ------------------------------------------

        if (
            campo
            == "orcamento_ticket"

            and

            estado[
                "perfil"
            ][
                "intencao"
            ]
            == "Aluguel"
        ):

            pergunta = (
                "Qual é seu orçamento mensal "
                "máximo para o aluguel?"
            )


        # ------------------------------------------
        # INVESTIMENTO
        # ------------------------------------------

        elif (
            campo
            == "orcamento_ticket"

            and

            estado[
                "perfil"
            ][
                "intencao"
            ]
            == "Investimento"
        ):

            pergunta = (
                "Qual valor você pretende "
                "investir em imóveis?"
            )


        estado[
            "ultima_pergunta"
        ] = pergunta


        return _resultado(

            estado,

            pergunta,

            "perguntar",

            alterados
        )


    # ==================================================
    # PERFIL COMPLETO
    # ==================================================

    estado[
        "ultima_pergunta"
    ] = None


    # ==================================================
    # BUSCA NÃO CONFIGURADA
    # ==================================================

    if (
        servicos.buscar_imoveis
        is None
    ):

        return _resultado(

            estado,

            (
                "Já organizei seu perfil. "
                "A consulta ao catálogo ainda "
                "precisa ser conectada."
            ),

            "tentar_novamente",

            alterados,

            "busca_nao_configurada"
        )


    # ==================================================
    # BUSCAR IMÓVEIS
    # ==================================================

    try:

        imoveis = (
            servicos.buscar_imoveis(

                deepcopy(
                    estado[
                        "perfil"
                    ]
                )
            )
        )


        for imovel in imoveis:

            if (
                not isinstance(
                    imovel[
                        "id_imovel"
                    ],
                    str
                )

                or

                imovel[
                    "disponivel"
                ]
                != "Sim"
            ):

                raise ValueError(
                    "Resultado inválido"
                )


            if (
                type(
                    imovel[
                        "preco"
                    ]
                )
                not in (
                    int,
                    float
                )

                or

                imovel[
                    "preco"
                ]
                <= 0
            ):

                raise ValueError(
                    "Preço inválido"
                )


        estado[
            "imoveis_ids"
        ] = [

            imovel[
                "id_imovel"
            ]

            for imovel
            in imoveis[
                :3
            ]
        ]


        # ==================================================
        # SEM RESULTADOS
        # ==================================================

        if not imoveis:

            # ------------------------------------------
            # INVESTIMENTO
            # ------------------------------------------

            if (
                estado[
                    "perfil"
                ][
                    "intencao"
                ]
                == "Investimento"
            ):

                pergunta = (
                    "Não encontrei oportunidades "
                    "que atendam exatamente ao seu "
                    "ticket e retorno esperado. "
                    "Podemos flexibilizar algum critério "
                    "ou posso encaminhar seu perfil para "
                    "um especialista em investimentos "
                    "imobiliários."
                )


            # ------------------------------------------
            # COMPRA / ALUGUEL
            # ------------------------------------------

            else:

                pergunta = (
                    "Não encontrei imóveis compatíveis. "
                    "Qual critério você aceita flexibilizar: "
                    "região, orçamento ou características?"
                )


            estado[
                "ultima_pergunta"
            ] = pergunta


            return _resultado(

                estado,

                pergunta,

                "perguntar",

                alterados
            )


        # ==================================================
        # FORMATAR IMÓVEIS
        # ==================================================

        linhas = [

            (
                f"{imovel['id_imovel']}: "
                f"{imovel['tipo_imovel']} "
                f"em {imovel['bairro']}, "
                f"{imovel['quartos']} quarto(s), "
                f"R$ {imovel['preco']:,.2f}."
            )

            for imovel
            in imoveis[
                :3
            ]
        ]


    except (
        ValueError,
        TypeError,
        KeyError,
        RuntimeError,
        OSError
    ):

        estado[
            "imoveis_ids"
        ] = []


        return _resultado(

            estado,

            (
                "A consulta aos imóveis "
                "está indisponível no momento."
            ),

            "tentar_novamente",

            alterados,

            "falha_busca"
        )


    # ==================================================
    # FINAL DO FLUXO
    # ==================================================

    # ----------------------------------------------
    # INVESTIMENTO
    # ----------------------------------------------

    if (
        estado[
            "perfil"
        ][
            "intencao"
        ]
        == "Investimento"
    ):

        pergunta = (
            "Você gostaria de conversar com "
            "um especialista em investimentos "
            "imobiliários sobre alguma dessas "
            "oportunidades?"
        )


    # ----------------------------------------------
    # COMPRA / ALUGUEL
    # ----------------------------------------------

    else:

        pergunta = (
            "Você tem interesse em conversar "
            "com um corretor sobre alguma "
            "dessas opções?"
        )


    estado[
        "ultima_pergunta"
    ] = pergunta


    return _resultado(

        estado,

        "\n".join(
            linhas
        )
        + "\n"
        + pergunta,

        "apresentar_imoveis",

        alterados
    )