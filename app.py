import csv

from datetime import datetime, date
from pathlib import Path
from uuid import uuid4

import streamlit as st


from agent import (
    Servicos,
    processar_mensagem
)

from catalogo import (
    buscar_imoveis
)

from llm_client import (
    OllamaClient
)

from scoring import (
    calcular_score
)

from database import (
    criar_tabelas,
    salvar_agendamento,
    salvar_conversa,
    salvar_mensagem,
    carregar_conversa,
    carregar_ultima_conversa,
    obter_metricas_dashboard,
    listar_ultimos_agendamentos,
    listar_conversas_recentes,
    obter_classificacao_leads,
    listar_leads_prioritarios,
    listar_followups_pendentes,
    registrar_followup,
    listar_followups,
    obter_metricas_followup,
    obter_ultimo_agendamento_conversa,
    obter_ultimo_followup_conversa,
    obter_distribuicao_intencao
)


# ==================================================
# CONFIGURAÇÃO DA PÁGINA
# ==================================================

st.set_page_config(
    page_title="Agente SDR Imobiliário",
    page_icon="🏠",
    layout="wide"
)


# ==================================================
# FUNÇÕES AUXILIARES
# ==================================================

def formatar_reais(valor):

    if valor is None:
        return "Não informado"

    valor_formatado = f"{float(valor):,.2f}"

    valor_formatado = (
        valor_formatado
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"R$ {valor_formatado}"


def formatar_data_hora(texto):

    if not texto:
        return "-"

    try:

        data_obj = datetime.fromisoformat(
            texto
        )

        return data_obj.strftime(
            "%d/%m/%Y %H:%M"
        )

    except Exception:

        return str(texto)


# ==================================================
# BUSCAR IMÓVEL POR ID
# ==================================================

def buscar_imovel_por_id(id_imovel):

    caminho = (
        Path(__file__).parent
        / "data"
        / "imoveis.csv"
    )

    if not caminho.exists():
        return None

    with open(
        caminho,
        encoding="utf-8-sig",
        newline=""
    ) as arquivo:

        leitor = csv.DictReader(
            arquivo,
            delimiter=";"
        )

        for row in leitor:

            if row.get("id_imovel") == id_imovel:

                return row

    return None


# ==================================================
# NOVA CONVERSA
# ==================================================

def nova_conversa():

    st.session_state.id_lead = str(
        uuid4()
    )

    st.session_state.id_conversa = str(
        uuid4()
    )

    st.session_state.estado = None

    st.session_state.historico = []

    st.session_state.imovel_selecionado = None

    st.session_state.mostrar_agendamento = False

    st.session_state.agendamento_confirmado = None

    st.session_state.aviso_retomada = None

    st.session_state.resumo_corretor = None


# ==================================================
# ABRIR CONVERSA
# ==================================================

def abrir_conversa(id_conversa):

    conversa = carregar_conversa(
        id_conversa
    )

    if not conversa:
        return

    st.session_state.id_lead = (
        conversa["id_lead"]
    )

    st.session_state.id_conversa = (
        conversa["id_conversa"]
    )

    st.session_state.estado = (
        conversa["estado"]
    )

    st.session_state.historico = (
        conversa["historico"]
    )

    st.session_state.imovel_selecionado = None

    st.session_state.mostrar_agendamento = False

    st.session_state.agendamento_confirmado = None

    st.session_state.resumo_corretor = None

    st.session_state.aviso_retomada = (
        "✅ Conversa retomada com sucesso."
    )

    st.session_state.pagina = (
        "💬 Atendimento"
    )


# ==================================================
# RETOMAR ÚLTIMA CONVERSA
# ==================================================

def retomar_ultima_conversa():

    conversa = carregar_ultima_conversa()

    if conversa:

        st.session_state.id_lead = (
            conversa["id_lead"]
        )

        st.session_state.id_conversa = (
            conversa["id_conversa"]
        )

        st.session_state.estado = (
            conversa["estado"]
        )

        st.session_state.historico = (
            conversa["historico"]
        )

        st.session_state.imovel_selecionado = None

        st.session_state.mostrar_agendamento = False

        st.session_state.agendamento_confirmado = None

        st.session_state.resumo_corretor = None

        st.session_state.aviso_retomada = (
            "✅ Última conversa retomada com sucesso."
        )

        st.session_state.pagina = (
            "💬 Atendimento"
        )

    else:

        st.session_state.aviso_retomada = (
            "⚠️ Nenhuma conversa salva."
        )


# ==================================================
# GERAR MENSAGEM DE FOLLOW-UP
# ==================================================

def gerar_mensagem_followup(estado):

    if not estado:

        return (
            "Olá! 😊 Gostaria de continuar "
            "nosso atendimento imobiliário?"
        )

    perfil = estado.get(
        "perfil",
        {}
    )

    intencao = perfil.get(
        "intencao"
    )

    regiao = perfil.get(
        "regiao_bairro"
    )

    tipo = perfil.get(
        "tipo_imovel_interesse"
    )

    orcamento = perfil.get(
        "orcamento_ticket"
    )

    quartos = perfil.get(
        "quartos"
    )

    perfil_investidor = perfil.get(
        "perfil_investidor"
    )

    retorno = perfil.get(
        "retorno_esperado_pct"
    )

    partes = []


    # ----------------------------------------------
    # COMPRA
    # ----------------------------------------------

    if intencao == "Compra":

        partes.append(
            "você estava procurando "
            "um imóvel para comprar"
        )


    # ----------------------------------------------
    # ALUGUEL
    # ----------------------------------------------

    elif intencao == "Aluguel":

        partes.append(
            "você estava procurando "
            "um imóvel para alugar"
        )


    # ----------------------------------------------
    # INVESTIMENTO
    # ----------------------------------------------

    elif intencao == "Investimento":

        partes.append(
            "você estava avaliando "
            "oportunidades de investimento imobiliário"
        )


    # ----------------------------------------------
    # DETALHES COMPRA / ALUGUEL
    # ----------------------------------------------

    if intencao in [
        "Compra",
        "Aluguel"
    ]:

        if tipo:

            partes.append(
                f"do tipo {tipo.lower()}"
            )

        if regiao:

            partes.append(
                f"na região de {regiao}"
            )

        if quartos is not None:

            partes.append(
                f"com {quartos} quarto(s)"
            )


    # ----------------------------------------------
    # DETALHES INVESTIMENTO
    # ----------------------------------------------

    if intencao == "Investimento":

        if perfil_investidor:

            partes.append(
                f"com perfil {perfil_investidor.lower()}"
            )

        if retorno is not None:

            partes.append(
                f"buscando retorno de "
                f"{retorno}% ao ano"
            )


    # ----------------------------------------------
    # ORÇAMENTO / TICKET
    # ----------------------------------------------

    if orcamento is not None:

        if intencao == "Investimento":

            partes.append(
                f"com ticket de até "
                f"{formatar_reais(orcamento)}"
            )

        else:

            partes.append(
                f"com orçamento de até "
                f"{formatar_reais(orcamento)}"
            )


    if partes:

        contexto = ", ".join(
            partes
        )

        return (
            "Olá! 😊 Na nossa última conversa, "
            f"{contexto}. "
            "Gostaria de continuar seu atendimento?"
        )


    return (
        "Olá! 😊 Nossa conversa ficou em aberto. "
        "Gostaria de continuar seu "
        "atendimento imobiliário?"
    )


# ==================================================
# PROCESSAR FOLLOW-UPS AUTOMATICAMENTE
# ==================================================

def processar_followups_automaticos(
    horas=24,
    modo_demo=False
):

    """
    Processa automaticamente conversas elegíveis.

    Em produção:
    - considera conversas inativas há pelo menos
      a quantidade de horas informada.

    Em demonstração:
    - ignora o tempo de espera.

    A própria consulta do banco impede novo envio
    quando já existe follow-up com status "Enviado".
    """

    pendentes = listar_followups_pendentes(
        horas=horas,
        modo_demo=modo_demo
    )

    enviados = 0

    for item in pendentes:

        estado_followup = item.get(
            "estado"
        )

        if not estado_followup:
            continue

        mensagem = gerar_mensagem_followup(
            estado_followup
        )

        registrar_followup(
            id_lead=item[
                "id_lead"
            ],
            id_conversa=item[
                "id_conversa"
            ],
            mensagem=mensagem
        )

        salvar_mensagem(
            id_mensagem=str(
                uuid4()
            ),
            id_conversa=item[
                "id_conversa"
            ],
            role="assistant",
            content=mensagem
        )

        enviados += 1

    return enviados


# ==================================================
# RESUMO PARA CORRETOR / ESPECIALISTA
# ==================================================

def gerar_resumo_corretor(
    estado,
    id_conversa
):

    if not estado:

        return (
            "Ainda não há informações "
            "suficientes sobre o lead."
        )

    perfil = estado.get(
        "perfil",
        {}
    )

    intencao = (
        perfil.get("intencao")
        or "Não informada"
    )

    regiao = (
        perfil.get("regiao_bairro")
        or "Não informada"
    )

    tipo = (
        perfil.get(
            "tipo_imovel_interesse"
        )
        or "Não informado"
    )

    orcamento = perfil.get(
        "orcamento_ticket"
    )

    quartos = perfil.get(
        "quartos"
    )

    urgencia = (
        perfil.get("urgencia")
        or "Não informada"
    )

    perfil_investidor = (
        perfil.get(
            "perfil_investidor"
        )
        or "Não informado"
    )

    retorno = perfil.get(
        "retorno_esperado_pct"
    )

    score = estado.get(
        "score"
    )

    classificacao = (
        estado.get(
            "classificacao"
        )
        or "Não classificado"
    )


    # ----------------------------------------------
    # IMÓVEIS
    # ----------------------------------------------

    imoveis = estado.get(
        "imoveis_ids",
        []
    )

    if imoveis:

        texto_imoveis = ", ".join(
            imoveis
        )

    else:

        texto_imoveis = (
            "Nenhum imóvel apresentado"
        )


    # ----------------------------------------------
    # AGENDAMENTO
    # ----------------------------------------------

    agendamento = (
        obter_ultimo_agendamento_conversa(
            id_conversa
        )
    )

    if agendamento:

        try:

            data_agendamento = (
                datetime.strptime(
                    agendamento[
                        "data_visita"
                    ],
                    "%Y-%m-%d"
                )
                .strftime(
                    "%d/%m/%Y"
                )
            )

        except Exception:

            data_agendamento = (
                agendamento[
                    "data_visita"
                ]
            )

        hora_agendamento = (
            agendamento[
                "hora_visita"
            ][:5]
        )

        texto_agendamento = (
            f"Sim — imóvel "
            f"{agendamento['id_imovel']}, "
            f"{data_agendamento} às "
            f"{hora_agendamento}"
        )

    else:

        texto_agendamento = (
            "Não realizado"
        )


    # ----------------------------------------------
    # FOLLOW-UP
    # ----------------------------------------------

    followup = (
        obter_ultimo_followup_conversa(
            id_conversa
        )
    )

    if followup:

        if followup[
            "status"
        ] == "Respondido":

            texto_followup = (
                "Enviado e respondido"
            )

        else:

            texto_followup = (
                "Enviado — aguardando resposta"
            )

    else:

        texto_followup = (
            "Não realizado"
        )


    # ----------------------------------------------
    # FORMATAÇÃO
    # ----------------------------------------------

    texto_orcamento = (
        formatar_reais(
            orcamento
        )
    )

    texto_quartos = (
        str(quartos)
        if quartos is not None
        else "Não informado"
    )

    texto_score = (
        str(score)
        if score is not None
        else "Não calculado"
    )

    texto_retorno = (
        f"{retorno}% ao ano"
        if retorno is not None
        else "Não informado"
    )


    # ----------------------------------------------
    # OBSERVAÇÕES
    # ----------------------------------------------

    observacoes = []

    if classificacao == "Quente":

        observacoes.append(
            "lead com alta qualificação comercial"
        )

    elif classificacao == "Morno":

        observacoes.append(
            "lead com qualificação intermediária"
        )

    elif classificacao == "Frio":

        observacoes.append(
            "lead ainda em estágio inicial "
            "de qualificação"
        )


    if (
        perfil.get(
            "aceitou_visita_reuniao"
        )
        == "Sim"
    ):

        observacoes.append(
            "demonstrou interesse em avançar "
            "para visita ou reunião"
        )


    if agendamento:

        observacoes.append(
            "possui visita agendada"
        )


    if (
        followup
        and
        followup[
            "status"
        ] == "Respondido"
    ):

        observacoes.append(
            "retomou o contato após follow-up"
        )


    if intencao == "Investimento":

        observacoes.append(
            "perfil direcionado para análise "
            "de investimento imobiliário"
        )


    if observacoes:

        resumo_comercial = "; ".join(
            observacoes
        )

        resumo_comercial = (
            resumo_comercial[0].upper()
            + resumo_comercial[1:]
            + "."
        )

    else:

        resumo_comercial = (
            "Lead ainda em processo de "
            "qualificação."
        )


    # ----------------------------------------------
    # INVESTIMENTO
    # ----------------------------------------------

    if intencao == "Investimento":

        return f"""
RESUMO DO LEAD

Intenção: Investimento
Ticket de investimento: {texto_orcamento}
Perfil do investidor: {perfil_investidor}
Retorno esperado: {texto_retorno}
Urgência: {urgencia}

QUALIFICAÇÃO

Score: {texto_score}
Classificação: {classificacao}

OPORTUNIDADES APRESENTADAS

{texto_imoveis}

FOLLOW-UP

{texto_followup}

RESUMO COMERCIAL

{resumo_comercial}
""".strip()


    # ----------------------------------------------
    # COMPRA / ALUGUEL
    # ----------------------------------------------

    return f"""
RESUMO DO LEAD

Intenção: {intencao}
Região: {regiao}
Tipo de imóvel: {tipo}
Orçamento: {texto_orcamento}
Quartos: {texto_quartos}
Urgência: {urgencia}

QUALIFICAÇÃO

Score: {texto_score}
Classificação: {classificacao}

IMÓVEIS APRESENTADOS

{texto_imoveis}

AGENDAMENTO

{texto_agendamento}

FOLLOW-UP

{texto_followup}

RESUMO COMERCIAL

{resumo_comercial}
""".strip()


# ==================================================
# BANCO
# ==================================================

criar_tabelas()


# ==================================================
# SERVIÇOS
# ==================================================

cliente_llm = OllamaClient()

servicos = Servicos(
    llm=cliente_llm,
    buscar_imoveis=buscar_imoveis,
    calcular_score=calcular_score
)


# ==================================================
# SESSION STATE
# ==================================================

if "id_lead" not in st.session_state:

    st.session_state.id_lead = str(
        uuid4()
    )


if "id_conversa" not in st.session_state:

    st.session_state.id_conversa = str(
        uuid4()
    )


if "estado" not in st.session_state:

    st.session_state.estado = None


if "historico" not in st.session_state:

    st.session_state.historico = []


if "imovel_selecionado" not in st.session_state:

    st.session_state.imovel_selecionado = None


if "mostrar_agendamento" not in st.session_state:

    st.session_state.mostrar_agendamento = False


if "agendamento_confirmado" not in st.session_state:

    st.session_state.agendamento_confirmado = None


if "pagina" not in st.session_state:

    st.session_state.pagina = (
        "💬 Atendimento"
    )


if "aviso_retomada" not in st.session_state:

    st.session_state.aviso_retomada = None


if "resumo_corretor" not in st.session_state:

    st.session_state.resumo_corretor = None


if "followups_automaticos" not in st.session_state:

    st.session_state.followups_automaticos = 0


# ==================================================
# MOTOR AUTOMÁTICO DE FOLLOW-UP
# ==================================================

try:

    quantidade_followups = (
        processar_followups_automaticos(
            horas=24,
            modo_demo=False
        )
    )

    if quantidade_followups > 0:

        st.session_state.followups_automaticos += (
            quantidade_followups
        )

except Exception:

    # Follow-up não deve impedir
    # a aplicação principal de funcionar.
    pass


# ==================================================
# CABEÇALHO
# ==================================================

st.title(
    "🏠 Agente SDR Imobiliário"
)

st.caption(
    "Assistente inteligente para compra, "
    "aluguel e investimento em imóveis."
)


# ==================================================
# AVISO DE FOLLOW-UP AUTOMÁTICO
# ==================================================

if (
    st.session_state
    .followups_automaticos
    > 0
):

    st.success(
        f"🤖 "
        f"{st.session_state.followups_automaticos} "
        f"follow-up(s) processado(s) "
        f"automaticamente."
    )

    st.session_state.followups_automaticos = 0


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.header(
        "👤 Perfil do Lead"
    )

    estado = (
        st.session_state.estado
    )


    if estado:

        perfil = estado.get(
            "perfil",
            {}
        )

        intencao = perfil.get(
            "intencao"
        )


        st.write(
            "**Intenção:**",
            intencao
            or "Não informada"
        )


        # ------------------------------------------
        # INVESTIMENTO
        # ------------------------------------------

        if intencao == "Investimento":

            st.write(
                "**Ticket de investimento:**",
                formatar_reais(
                    perfil.get(
                        "orcamento_ticket"
                    )
                )
            )

            st.write(
                "**Perfil do investidor:**",
                perfil.get(
                    "perfil_investidor"
                )
                or "Não informado"
            )

            retorno = perfil.get(
                "retorno_esperado_pct"
            )

            if retorno is not None:

                st.write(
                    "**Retorno esperado:**",
                    f"{retorno}% ao ano"
                )

            else:

                st.write(
                    "**Retorno esperado:**",
                    "Não informado"
                )

            st.write(
                "**Urgência:**",
                perfil.get(
                    "urgencia"
                )
                or "Não informada"
            )


        # ------------------------------------------
        # COMPRA / ALUGUEL
        # ------------------------------------------

        else:

            st.write(
                "**Região:**",
                perfil.get(
                    "regiao_bairro"
                )
                or "Não informada"
            )

            st.write(
                "**Tipo de imóvel:**",
                perfil.get(
                    "tipo_imovel_interesse"
                )
                or "Não informado"
            )

            if intencao == "Aluguel":

                st.write(
                    "**Orçamento mensal:**",
                    formatar_reais(
                        perfil.get(
                            "orcamento_ticket"
                        )
                    )
                )

            else:

                st.write(
                    "**Orçamento:**",
                    formatar_reais(
                        perfil.get(
                            "orcamento_ticket"
                        )
                    )
                )

            st.write(
                "**Quartos:**",
                (
                    perfil.get(
                        "quartos"
                    )
                    if perfil.get(
                        "quartos"
                    )
                    is not None
                    else "Não informado"
                )
            )

            st.write(
                "**Urgência:**",
                perfil.get(
                    "urgencia"
                )
                or "Não informada"
            )


        # ------------------------------------------
        # SCORE
        # ------------------------------------------

        st.divider()

        score = estado.get(
            "score"
        )

        st.write(
            "**Score:**",
            (
                score
                if score is not None
                else "Pendente"
            )
        )

        classificacao = (
            estado.get(
                "classificacao"
            )
            or "Pendente"
        )

        if classificacao == "Quente":

            st.success(
                "🔥 Lead Quente"
            )

        elif classificacao == "Morno":

            st.warning(
                "🟡 Lead Morno"
            )

        elif classificacao == "Frio":

            st.info(
                "🔵 Lead Frio"
            )

        else:

            st.write(
                "**Classificação:** Pendente"
            )


    else:

        st.info(
            "O atendimento ainda não começou."
        )


    st.divider()


    st.button(
        "💬 Retomar última conversa",
        use_container_width=True,
        on_click=retomar_ultima_conversa
    )


    if st.button(
        "🔄 Nova conversa",
        use_container_width=True
    ):

        nova_conversa()

        st.session_state.pagina = (
            "💬 Atendimento"
        )

        st.rerun()


# ==================================================
# AVISO
# ==================================================

if st.session_state.aviso_retomada:

    mensagem_aviso = (
        st.session_state.aviso_retomada
    )

    if mensagem_aviso.startswith(
        "✅"
    ):

        st.success(
            mensagem_aviso
        )

    else:

        st.warning(
            mensagem_aviso
        )

    st.session_state.aviso_retomada = None


# ==================================================
# NAVEGAÇÃO
# ==================================================

pagina = st.radio(
    "Navegação",
    [
        "💬 Atendimento",
        "📊 Dashboard"
    ],
    key="pagina",
    horizontal=True,
    label_visibility="collapsed"
)

st.divider()


# ==================================================
# ATENDIMENTO
# ==================================================

if pagina == "💬 Atendimento":

    st.subheader(
        "💬 Atendimento"
    )


    # ==================================================
    # HISTÓRICO
    # ==================================================

    for mensagem in (
        st.session_state.historico
    ):

        with st.chat_message(
            mensagem[
                "role"
            ]
        ):

            st.write(
                mensagem[
                    "content"
                ]
            )


    # ==================================================
    # IMÓVEIS
    # ==================================================

    estado = (
        st.session_state.estado
    )


    if (
        estado
        and
        estado.get(
            "imoveis_ids"
        )
    ):

        intencao_atual = (
            estado.get(
                "perfil",
                {}
            ).get(
                "intencao"
            )
        )


        if intencao_atual == "Investimento":

            st.subheader(
                "📈 Oportunidades encontradas"
            )

            st.caption(
                "Oportunidades compatíveis "
                "com o perfil de investimento."
            )

        else:

            st.subheader(
                "🏘️ Imóveis encontrados"
            )

            st.caption(
                "Selecionamos opções compatíveis "
                "com o seu perfil."
            )


        ids_imoveis = estado[
            "imoveis_ids"
        ]


        colunas = st.columns(
            len(
                ids_imoveis
            )
        )


        for coluna, id_imovel in zip(
            colunas,
            ids_imoveis
        ):

            imovel = buscar_imovel_por_id(
                id_imovel
            )

            if not imovel:
                continue


            with coluna:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"### 🏠 "
                        f"{imovel['id_imovel']}"
                    )

                    st.write(
                        f"**"
                        f"{imovel['tipo_imovel']} "
                        f"em {imovel['bairro']}"
                        f"**"
                    )

                    st.write(
                        f"🛏️ "
                        f"{imovel['quartos']} "
                        f"quarto(s)"
                    )


                    if imovel.get(
                        "area_m2"
                    ):

                        st.write(
                            f"📐 "
                            f"{imovel['area_m2']} m²"
                        )


                    preco = float(
                        imovel[
                            "preco"
                        ]
                    )


                    st.markdown(
                        f"### "
                        f"{formatar_reais(preco)}"
                    )


                    if st.button(
                        "❤️ Tenho interesse",
                        key=(
                            "interesse_"
                            + id_imovel
                        ),
                        use_container_width=True
                    ):

                        st.session_state[
                            "imovel_selecionado"
                        ] = id_imovel

                        st.session_state[
                            "mostrar_agendamento"
                        ] = False

                        st.session_state[
                            "agendamento_confirmado"
                        ] = None

                        st.session_state[
                            "resumo_corretor"
                        ] = None

                        st.rerun()


    # ==================================================
    # IMÓVEL SELECIONADO
    # ==================================================

    if (
        st.session_state
        .imovel_selecionado
    ):

        id_imovel = (
            st.session_state
            .imovel_selecionado
        )

        imovel = buscar_imovel_por_id(
            id_imovel
        )


        if imovel:

            st.divider()

            st.subheader(
                "❤️ Imóvel selecionado"
            )

            st.success(
                f"Você demonstrou interesse "
                f"no imóvel {id_imovel} — "
                f"{imovel['tipo_imovel']} "
                f"em {imovel['bairro']}."
            )


            intencao = (
                st.session_state
                .estado
                .get(
                    "perfil",
                    {}
                )
                .get(
                    "intencao"
                )
                if st.session_state.estado
                else None
            )


            # --------------------------------------
            # INVESTIMENTO
            # --------------------------------------

            if intencao == "Investimento":

                if st.button(
                    "📈 Falar com especialista em investimentos",
                    use_container_width=True
                ):

                    st.session_state[
                        "mensagem_automatica"
                    ] = (
                        f"Tenho interesse no imóvel "
                        f"{id_imovel} e gostaria de "
                        "falar com um especialista "
                        "em investimentos imobiliários."
                    )

                    st.rerun()


            # --------------------------------------
            # COMPRA / ALUGUEL
            # --------------------------------------

            else:

                col1, col2 = (
                    st.columns(2)
                )


                with col1:

                    if st.button(
                        "📅 Agendar visita",
                        use_container_width=True
                    ):

                        st.session_state[
                            "mostrar_agendamento"
                        ] = True

                        st.rerun()


                with col2:

                    if st.button(
                        "👤 Falar com corretor",
                        use_container_width=True
                    ):

                        st.session_state[
                            "mensagem_automatica"
                        ] = (
                            f"Tenho interesse no imóvel "
                            f"{id_imovel} e gostaria de "
                            "falar com um corretor."
                        )

                        st.rerun()


    # ==================================================
    # AGENDAMENTO
    # ==================================================

    if (
        st.session_state.imovel_selecionado
        and
        st.session_state.mostrar_agendamento
    ):

        st.subheader(
            "📅 Agendar visita"
        )

        id_imovel = (
            st.session_state
            .imovel_selecionado
        )


        with st.form(
            "form_agendamento"
        ):

            data_visita = st.date_input(
                "Data da visita",
                min_value=date.today()
            )

            horario_visita = st.time_input(
                "Horário"
            )

            observacao = st.text_area(
                "Observação",
                placeholder=(
                    "Ex.: irei acompanhado..."
                )
            )

            confirmar = (
                st.form_submit_button(
                    "✅ Confirmar agendamento",
                    use_container_width=True
                )
            )


            if confirmar:

                id_agendamento = (
                    salvar_agendamento(
                        id_lead=(
                            st.session_state.id_lead
                        ),
                        id_conversa=(
                            st.session_state.id_conversa
                        ),
                        id_imovel=(
                            id_imovel
                        ),
                        data_visita=(
                            data_visita
                        ),
                        hora_visita=(
                            horario_visita
                        ),
                        observacao=(
                            observacao
                        )
                    )
                )


                if st.session_state.estado:

                    perfil = (
                        st.session_state
                        .estado[
                            "perfil"
                        ]
                    )

                    perfil[
                        "aceitou_visita_reuniao"
                    ] = "Sim"


                    resultado_score = (
                        calcular_score(
                            perfil
                        )
                    )


                    st.session_state.estado[
                        "score"
                    ] = resultado_score[
                        "score"
                    ]

                    st.session_state.estado[
                        "classificacao"
                    ] = resultado_score[
                        "classificacao"
                    ]


                    salvar_conversa(
                        id_conversa=(
                            st.session_state.id_conversa
                        ),
                        id_lead=(
                            st.session_state.id_lead
                        ),
                        estado=(
                            st.session_state.estado
                        )
                    )


                st.session_state[
                    "agendamento_confirmado"
                ] = {

                    "id":
                        id_agendamento,

                    "id_imovel":
                        id_imovel,

                    "data":
                        str(
                            data_visita
                        ),

                    "hora":
                        str(
                            horario_visita
                        ),

                    "observacao":
                        observacao
                }


                st.session_state[
                    "mostrar_agendamento"
                ] = False

                st.session_state[
                    "resumo_corretor"
                ] = None

                st.rerun()


    # ==================================================
    # AGENDAMENTO CONFIRMADO
    # ==================================================

    if (
        st.session_state
        .agendamento_confirmado
    ):

        agendamento = (
            st.session_state
            .agendamento_confirmado
        )


        data_formatada = (
            datetime.strptime(
                agendamento[
                    "data"
                ],
                "%Y-%m-%d"
            )
            .strftime(
                "%d/%m/%Y"
            )
        )


        st.success(
            "✅ Sua visita está agendada!"
        )


        st.info(
            f"📌 Código: "
            f"{agendamento['id']}\n\n"

            f"📍 Imóvel: "
            f"{agendamento['id_imovel']}\n\n"

            f"📅 Data: "
            f"{data_formatada}\n\n"

            f"🕐 Horário: "
            f"{agendamento['hora'][:5]}"
        )


    # ==================================================
    # RESUMO
    # ==================================================

    st.divider()


    estado_atual = (
        st.session_state.estado
    )


    intencao_atual = (
        estado_atual.get(
            "perfil",
            {}
        ).get(
            "intencao"
        )
        if estado_atual
        else None
    )


    if intencao_atual == "Investimento":

        st.subheader(
            "📋 Resumo para o Especialista"
        )

        st.caption(
            "Consolidação automática do perfil "
            "de investimento do lead."
        )

        texto_botao_resumo = (
            "📋 Gerar resumo para o especialista"
        )


    else:

        st.subheader(
            "📋 Resumo para o Corretor"
        )

        st.caption(
            "Consolidação automática das principais "
            "informações comerciais do lead."
        )

        texto_botao_resumo = (
            "📋 Gerar resumo para o corretor"
        )


    if not st.session_state.estado:

        st.info(
            "Inicie o atendimento para gerar "
            "o resumo do lead."
        )


    else:

        if st.button(
            texto_botao_resumo,
            use_container_width=True
        ):

            st.session_state.resumo_corretor = (
                gerar_resumo_corretor(
                    estado=(
                        st.session_state.estado
                    ),
                    id_conversa=(
                        st.session_state.id_conversa
                    )
                )
            )


        if st.session_state.resumo_corretor:

            st.success(
                "✅ Resumo comercial gerado."
            )

            st.code(
                st.session_state.resumo_corretor,
                language=None
            )


            if intencao_atual == "Investimento":

                st.caption(
                    "O resumo pode ser encaminhado "
                    "ao especialista em investimentos "
                    "imobiliários."
                )

            else:

                st.caption(
                    "O resumo pode ser encaminhado "
                    "ao corretor responsável."
                )


    # ==================================================
    # MENSAGEM AUTOMÁTICA
    # ==================================================

    mensagem_automatica = None


    if (
        "mensagem_automatica"
        in st.session_state
    ):

        mensagem_automatica = (
            st.session_state.pop(
                "mensagem_automatica"
            )
        )


    # ==================================================
    # CHAT
    # ==================================================

    mensagem_digitada = (
        st.chat_input(
            "Digite sua mensagem..."
        )
    )


    mensagem_usuario = (
        mensagem_automatica
        or mensagem_digitada
    )


    # ==================================================
    # PROCESSAMENTO IA
    # ==================================================

    if mensagem_usuario:

        historico_anterior = (
            st.session_state
            .historico
            .copy()
        )

        id_mensagem_usuario = str(
            uuid4()
        )


        entrada = {

            "id_lead":
                st.session_state.id_lead,

            "id_conversa":
                st.session_state.id_conversa,

            "id_mensagem":
                id_mensagem_usuario,

            "mensagem":
                mensagem_usuario,

            "estado":
                st.session_state.estado,

            "historico":
                historico_anterior,

            "data_hora_atual":
                datetime.now()
                .astimezone()
                .isoformat()
        }


        with st.spinner(
            "Analisando sua solicitação..."
        ):

            resultado = (
                processar_mensagem(
                    entrada,
                    servicos
                )
            )


        st.session_state.estado = (
            resultado[
                "estado_atualizado"
            ]
        )

        st.session_state.resumo_corretor = None


        # ------------------------------------------
        # APRESENTAÇÃO DE IMÓVEIS
        # ------------------------------------------

        if (
            resultado.get(
                "acao"
            )
            == "apresentar_imoveis"
        ):

            intencao_resultado = (
                st.session_state
                .estado
                .get(
                    "perfil",
                    {}
                )
                .get(
                    "intencao"
                )
            )


            if (
                intencao_resultado
                == "Investimento"
            ):

                resposta_exibida = (
                    "Encontrei algumas oportunidades "
                    "compatíveis com o seu perfil "
                    "de investimento. "
                    "Veja abaixo 👇"
                )

            else:

                resposta_exibida = (
                    "Encontrei algumas opções "
                    "compatíveis com o seu perfil. "
                    "Veja os imóveis abaixo 👇"
                )


        else:

            resposta_exibida = (
                resultado[
                    "resposta"
                ]
            )


        # ------------------------------------------
        # HISTÓRICO
        # ------------------------------------------

        st.session_state.historico.append(
            {
                "role": "user",
                "content":
                    mensagem_usuario
            }
        )


        st.session_state.historico.append(
            {
                "role": "assistant",
                "content":
                    resposta_exibida
            }
        )


        # ------------------------------------------
        # SALVAR CONVERSA
        # ------------------------------------------

        salvar_conversa(
            id_conversa=(
                st.session_state.id_conversa
            ),
            id_lead=(
                st.session_state.id_lead
            ),
            estado=(
                st.session_state.estado
            )
        )


        # ------------------------------------------
        # SALVAR USUÁRIO
        # ------------------------------------------

        salvar_mensagem(
            id_mensagem=(
                id_mensagem_usuario
            ),
            id_conversa=(
                st.session_state.id_conversa
            ),
            role="user",
            content=(
                mensagem_usuario
            )
        )


        # ------------------------------------------
        # SALVAR ASSISTENTE
        # ------------------------------------------

        salvar_mensagem(
            id_mensagem=str(
                uuid4()
            ),
            id_conversa=(
                st.session_state.id_conversa
            ),
            role="assistant",
            content=(
                resposta_exibida
            )
        )


        st.rerun()


# ==================================================
# DASHBOARD
# ==================================================

elif pagina == "📊 Dashboard":

    st.subheader(
        "📊 Dashboard Comercial"
    )

    st.caption(
        "Acompanhamento da qualificação, "
        "interações, agendamentos e follow-ups."
    )


    # ==================================================
    # MÉTRICAS
    # ==================================================

    metricas = (
        obter_metricas_dashboard()
    )

    classificacao = (
        obter_classificacao_leads()
    )

    metricas_followup = (
        obter_metricas_followup()
    )


    total_leads = metricas[
        "leads"
    ]

    total_quentes = classificacao[
        "quentes"
    ]

    total_agendamentos = metricas[
        "agendamentos"
    ]


    percentual_quentes = (

        round(
            total_quentes
            / total_leads
            * 100,
            1
        )

        if total_leads

        else 0
    )


    taxa_agendamento = (

        round(
            total_agendamentos
            / total_leads
            * 100,
            1
        )

        if total_leads

        else 0
    )


    # ==================================================
    # INDICADORES EXECUTIVOS
    # ==================================================

    st.subheader(
        "📈 Indicadores Executivos"
    )


    col1, col2, col3, col4 = (
        st.columns(4)
    )


    with col1:

        st.metric(
            "🔥 Leads Quentes",
            f"{percentual_quentes}%"
        )


    with col2:

        st.metric(
            "📅 Taxa de Agendamento",
            f"{taxa_agendamento}%"
        )


    with col3:

        st.metric(
            "⭐ Score Médio",
            classificacao[
                "score_medio"
            ]
        )


    with col4:

        st.metric(
            "📨 Resposta Follow-up",
            f"{metricas_followup['taxa_resposta']}%"
        )


    st.divider()


    # ==================================================
    # VISÃO GERAL
    # ==================================================

    st.subheader(
        "📌 Visão Geral"
    )


    col1, col2, col3, col4 = (
        st.columns(4)
    )


    with col1:

        st.metric(
            "👥 Leads",
            metricas[
                "leads"
            ]
        )


    with col2:

        st.metric(
            "💬 Conversas",
            metricas[
                "conversas"
            ]
        )


    with col3:

        st.metric(
            "✉️ Mensagens",
            metricas[
                "mensagens"
            ]
        )


    with col4:

        st.metric(
            "📅 Agendamentos",
            metricas[
                "agendamentos"
            ]
        )


    st.divider()


    # ==================================================
    # QUALIFICAÇÃO
    # ==================================================

    st.subheader(
        "🎯 Qualificação dos Leads"
    )


    col1, col2, col3, col4 = (
        st.columns(4)
    )


    with col1:

        st.metric(
            "🔥 Quentes",
            classificacao[
                "quentes"
            ]
        )


    with col2:

        st.metric(
            "🟡 Mornos",
            classificacao[
                "mornos"
            ]
        )


    with col3:

        st.metric(
            "🔵 Frios",
            classificacao[
                "frios"
            ]
        )


    with col4:

        st.metric(
            "⭐ Score médio",
            classificacao[
                "score_medio"
            ]
        )


    dados_classificacao = {

        "Quentes":
            classificacao[
                "quentes"
            ],

        "Mornos":
            classificacao[
                "mornos"
            ],

        "Frios":
            classificacao[
                "frios"
            ]
    }


    st.bar_chart(
        dados_classificacao
    )


    st.divider()


    # ==================================================
    # DISTRIBUIÇÃO POR INTENÇÃO
    # ==================================================

    st.subheader(
        "🏠 Intenção dos Leads"
    )

    st.caption(
        "Distribuição dos leads conforme "
        "o objetivo identificado."
    )


    distribuicao_intencao = (
        obter_distribuicao_intencao()
    )


    col1, col2, col3, col4 = (
        st.columns(4)
    )


    with col1:

        st.metric(
            "🏠 Compra",
            distribuicao_intencao[
                "Compra"
            ]
        )


    with col2:

        st.metric(
            "🔑 Aluguel",
            distribuicao_intencao[
                "Aluguel"
            ]
        )


    with col3:

        st.metric(
            "📈 Investimento",
            distribuicao_intencao[
                "Investimento"
            ]
        )


    with col4:

        st.metric(
            "❔ Não definido",
            distribuicao_intencao[
                "Não definido"
            ]
        )


    dados_intencao = {

        "Compra":
            distribuicao_intencao[
                "Compra"
            ],

        "Aluguel":
            distribuicao_intencao[
                "Aluguel"
            ],

        "Investimento":
            distribuicao_intencao[
                "Investimento"
            ],

        "Não definido":
            distribuicao_intencao[
                "Não definido"
            ]
    }


    st.bar_chart(
        dados_intencao
    )


    st.divider()


    # ==================================================
    # LEADS PRIORITÁRIOS
    # ==================================================

    st.subheader(
        "🔥 Leads Prioritários"
    )


    leads_prioritarios = (
        listar_leads_prioritarios()
    )


    if leads_prioritarios:

        st.dataframe(
            leads_prioritarios,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Nenhum lead qualificado ainda."
        )


    st.divider()


    # ==================================================
    # FOLLOW-UP AUTOMÁTICO
    # ==================================================

    st.subheader(
        "🤖 Follow-up Automático"
    )

    st.caption(
        "O sistema identifica automaticamente "
        "conversas sem interação há 24 horas "
        "e envia uma mensagem contextual."
    )


    pendentes_reais = (
        listar_followups_pendentes(
            horas=24,
            modo_demo=False
        )
    )


    if pendentes_reais:

        st.warning(
            f"Existem "
            f"{len(pendentes_reais)} "
            f"conversa(s) aguardando processamento."
        )

    else:

        st.success(
            "Nenhum follow-up automático pendente."
        )


    # ==================================================
    # MODO DEMONSTRAÇÃO
    # ==================================================

    st.markdown(
        "### 🧪 Demonstração"
    )

    st.caption(
        "Use este modo para demonstrar a automação "
        "sem esperar 24 horas."
    )


    modo_demo = st.checkbox(
        "Ativar modo demonstração"
    )


    if modo_demo:

        pendentes_demo = (
            listar_followups_pendentes(
                horas=24,
                modo_demo=True
            )
        )


        if pendentes_demo:

            st.info(
                f"{len(pendentes_demo)} "
                f"conversa(s) podem receber "
                f"follow-up agora."
            )


            if st.button(
                "⚙️ Processar follow-ups agora",
                use_container_width=True,
                type="primary"
            ):

                quantidade = (
                    processar_followups_automaticos(
                        horas=24,
                        modo_demo=True
                    )
                )


                if quantidade > 0:

                    st.success(
                        f"✅ {quantidade} "
                        f"follow-up(s) enviado(s) "
                        f"automaticamente."
                    )

                else:

                    st.info(
                        "Nenhum follow-up precisava "
                        "ser enviado."
                    )


                st.rerun()


        else:

            st.success(
                "Nenhuma conversa disponível "
                "para demonstração."
            )


    st.divider()


    # ==================================================
    # MÉTRICAS FOLLOW-UP
    # ==================================================

    metricas_followup = (
        obter_metricas_followup()
    )


    st.subheader(
        "📨 Indicadores de Follow-up"
    )


    col1, col2, col3 = (
        st.columns(3)
    )


    with col1:

        st.metric(
            "Follow-ups enviados",
            metricas_followup[
                "total"
            ]
        )


    with col2:

        st.metric(
            "Respostas",
            metricas_followup[
                "respondidos"
            ]
        )


    with col3:

        st.metric(
            "Taxa de resposta",
            f"{metricas_followup['taxa_resposta']}%"
        )


    # ==================================================
    # HISTÓRICO
    # ==================================================

    historico_followups = (
        listar_followups()
    )


    if historico_followups:

        st.markdown(
            "### 📋 Histórico de Follow-ups"
        )


        for followup in historico_followups:

            with st.container(
                border=True
            ):

                col_info, col_botao = (
                    st.columns(
                        [4, 1]
                    )
                )


                with col_info:

                    st.markdown(
                        f"#### Follow-up "
                        f"#{followup['id']}"
                    )


                    st.write(
                        "**Lead:**",
                        followup[
                            "id_lead"
                        ]
                    )


                    if (
                        followup[
                            "status"
                        ]
                        == "Respondido"
                    ):

                        st.success(
                            "📨 Enviado → ✅ Respondido"
                        )

                    else:

                        st.warning(
                            "📨 Enviado → "
                            "⏳ Aguardando resposta"
                        )


                    st.write(
                        "**Enviado em:**",
                        formatar_data_hora(
                            followup[
                                "criado_em"
                            ]
                        )
                    )


                    if followup[
                        "respondido_em"
                    ]:

                        st.write(
                            "**Respondido em:**",
                            formatar_data_hora(
                                followup[
                                    "respondido_em"
                                ]
                            )
                        )

                    else:

                        st.write(
                            "**Respondido em:**",
                            "Aguardando resposta"
                        )


                    with st.expander(
                        "📩 Ver mensagem"
                    ):

                        st.write(
                            followup[
                                "mensagem"
                            ]
                        )


                with col_botao:

                    st.button(
                        "💬 Abrir conversa",
                        key=(
                            "abrir_followup_"
                            + str(
                                followup[
                                    "id"
                                ]
                            )
                        ),
                        use_container_width=True,
                        on_click=abrir_conversa,
                        args=(
                            followup[
                                "id_conversa"
                            ],
                        )
                    )


    else:

        st.info(
            "Nenhum follow-up enviado ainda."
        )


    st.divider()


    # ==================================================
    # AGENDAMENTOS
    # ==================================================

    st.subheader(
        "📅 Últimos agendamentos"
    )


    agendamentos = (
        listar_ultimos_agendamentos()
    )


    if agendamentos:

        st.dataframe(
            agendamentos,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Nenhum agendamento registrado."
        )


    st.divider()


    # ==================================================
    # CONVERSAS RECENTES
    # ==================================================

    st.subheader(
        "💬 Conversas recentes"
    )


    conversas = (
        listar_conversas_recentes()
    )


    if conversas:

        st.dataframe(
            conversas,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Nenhuma conversa registrada."
        )