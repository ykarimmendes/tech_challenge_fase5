def calcular_score(perfil):
    """
    Calcula o score do lead conforme as regras oficiais
    documentadas no projeto.
    """

    score = 0

    intencao = perfil.get("intencao")


    # ==================================================
    # COMPRA / ALUGUEL
    # ==================================================

    if intencao in ["Compra", "Aluguel"]:

        # Intenção identificada
        score += 10

        # Orçamento
        if perfil.get("orcamento_ticket") is not None:
            score += 20

        # Região
        if perfil.get("regiao_bairro"):
            score += 15

        # Tipo de imóvel
        if perfil.get("tipo_imovel_interesse"):
            score += 10

        # Quartos
        if perfil.get("quartos") is not None:
            score += 10

        # Urgência
        urgencia = perfil.get("urgencia")

        if urgencia == "Alta":
            score += 15

        elif urgencia == "Média":
            score += 10

        elif urgencia == "Baixa":
            score += 5

        # Visita / reunião
        if perfil.get("aceitou_visita_reuniao") == "Sim":
            score += 20


    # ==================================================
    # INVESTIMENTO
    # ==================================================

    elif intencao == "Investimento":

        # Intenção identificada
        score += 10

        # Ticket
        if perfil.get("orcamento_ticket") is not None:
            score += 20

        # Região
        if perfil.get("regiao_bairro"):
            score += 10

        # Perfil do investidor
        if perfil.get("perfil_investidor"):
            score += 15

        # Retorno esperado
        if perfil.get("retorno_esperado_pct") is not None:
            score += 15

        # Urgência
        urgencia = perfil.get("urgencia")

        if urgencia == "Alta":
            score += 10

        elif urgencia == "Média":
            score += 7

        elif urgencia == "Baixa":
            score += 3

        # Reunião / visita
        if perfil.get("aceitou_visita_reuniao") == "Sim":
            score += 20

        # Regra de completude
        if (
            perfil.get("perfil_investidor") is None
            or perfil.get("retorno_esperado_pct") is None
        ):
            score = min(score, 69)


    # ==================================================
    # INTENÇÃO NÃO DEFINIDA
    # ==================================================

    else:

        score = 0


    # ==================================================
    # GARANTIR LIMITE
    # ==================================================

    score = max(
        0,
        min(score, 100)
    )


    # ==================================================
    # CLASSIFICAÇÃO
    # ==================================================

    if score < 40:

        classificacao = "Frio"

    elif score < 70:

        classificacao = "Morno"

    else:

        classificacao = "Quente"


    return {
        "score": score,
        "classificacao": classificacao
    }