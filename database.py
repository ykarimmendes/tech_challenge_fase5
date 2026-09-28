import sqlite3
import json

from pathlib import Path
from datetime import datetime, timedelta


# ==================================================
# CAMINHO DO BANCO
# ==================================================

CAMINHO_BANCO = (
    Path(__file__).parent
    / "data"
    / "sdr_imobiliario.db"
)


# ==================================================
# CONEXÃO
# ==================================================

def conectar():

    return sqlite3.connect(
        CAMINHO_BANCO
    )


# ==================================================
# CRIAÇÃO DAS TABELAS
# ==================================================

def criar_tabelas():

    conexao = conectar()
    cursor = conexao.cursor()

    # ----------------------------------------------
    # LEADS
    # ----------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id_lead TEXT PRIMARY KEY,
            criado_em TEXT NOT NULL,
            atualizado_em TEXT NOT NULL
        )
        """
    )

    # ----------------------------------------------
    # CONVERSAS
    # ----------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversas (
            id_conversa TEXT PRIMARY KEY,
            id_lead TEXT NOT NULL,
            estado_json TEXT,
            status TEXT,
            criado_em TEXT NOT NULL,
            atualizado_em TEXT NOT NULL,

            FOREIGN KEY (id_lead)
            REFERENCES leads(id_lead)
        )
        """
    )

    # ----------------------------------------------
    # MENSAGENS
    # ----------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS mensagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_mensagem TEXT UNIQUE NOT NULL,
            id_conversa TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            criado_em TEXT NOT NULL,

            FOREIGN KEY (id_conversa)
            REFERENCES conversas(id_conversa)
        )
        """
    )

    # ----------------------------------------------
    # AGENDAMENTOS
    # ----------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_lead TEXT NOT NULL,
            id_conversa TEXT NOT NULL,
            id_imovel TEXT NOT NULL,
            data_visita TEXT NOT NULL,
            hora_visita TEXT NOT NULL,
            observacao TEXT,
            status TEXT NOT NULL DEFAULT 'Agendado',
            criado_em TEXT NOT NULL
        )
        """
    )

    # ----------------------------------------------
    # FOLLOW-UPS
    # ----------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS followups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_lead TEXT NOT NULL,
            id_conversa TEXT NOT NULL,
            mensagem TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Enviado',
            criado_em TEXT NOT NULL,
            respondido_em TEXT
        )
        """
    )

    conexao.commit()
    conexao.close()


# ==================================================
# SALVAR LEAD
# ==================================================

def salvar_lead(id_lead):

    agora = (
        datetime.now()
        .astimezone()
        .isoformat()
    )

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT id_lead
        FROM leads
        WHERE id_lead = ?
        """,
        (id_lead,)
    )

    existe = cursor.fetchone()

    if existe:

        cursor.execute(
            """
            UPDATE leads
            SET atualizado_em = ?
            WHERE id_lead = ?
            """,
            (
                agora,
                id_lead
            )
        )

    else:

        cursor.execute(
            """
            INSERT INTO leads (
                id_lead,
                criado_em,
                atualizado_em
            )
            VALUES (?, ?, ?)
            """,
            (
                id_lead,
                agora,
                agora
            )
        )

    conexao.commit()
    conexao.close()


# ==================================================
# SALVAR CONVERSA
# ==================================================

def salvar_conversa(
    id_conversa,
    id_lead,
    estado
):

    salvar_lead(
        id_lead
    )

    agora = (
        datetime.now()
        .astimezone()
        .isoformat()
    )

    estado_json = json.dumps(
        estado,
        ensure_ascii=False
    )

    status = None

    if estado:

        status = estado.get(
            "status"
        )

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT id_conversa
        FROM conversas
        WHERE id_conversa = ?
        """,
        (id_conversa,)
    )

    existe = cursor.fetchone()

    if existe:

        cursor.execute(
            """
            UPDATE conversas
            SET
                estado_json = ?,
                status = ?,
                atualizado_em = ?
            WHERE id_conversa = ?
            """,
            (
                estado_json,
                status,
                agora,
                id_conversa
            )
        )

    else:

        cursor.execute(
            """
            INSERT INTO conversas (
                id_conversa,
                id_lead,
                estado_json,
                status,
                criado_em,
                atualizado_em
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                id_conversa,
                id_lead,
                estado_json,
                status,
                agora,
                agora
            )
        )

    conexao.commit()
    conexao.close()


# ==================================================
# SALVAR MENSAGEM
# ==================================================

def salvar_mensagem(
    id_mensagem,
    id_conversa,
    role,
    content
):

    agora = (
        datetime.now()
        .astimezone()
        .isoformat()
    )

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO mensagens (
            id_mensagem,
            id_conversa,
            role,
            content,
            criado_em
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            id_mensagem,
            id_conversa,
            role,
            content,
            agora
        )
    )

    # ----------------------------------------------
    # SE USUÁRIO RESPONDEU FOLLOW-UP
    # ----------------------------------------------

    if role == "user":

        cursor.execute(
            """
            SELECT id
            FROM followups
            WHERE
                id_conversa = ?
                AND status = 'Enviado'
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                id_conversa,
            )
        )

        followup = (
            cursor.fetchone()
        )

        if followup:

            cursor.execute(
                """
                UPDATE followups
                SET
                    status = 'Respondido',
                    respondido_em = ?
                WHERE id = ?
                """,
                (
                    agora,
                    followup[0]
                )
            )

    conexao.commit()
    conexao.close()


# ==================================================
# CARREGAR CONVERSA
# ==================================================

def carregar_conversa(
    id_conversa
):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT
            id_lead,
            estado_json
        FROM conversas
        WHERE id_conversa = ?
        """,
        (
            id_conversa,
        )
    )

    conversa = (
        cursor.fetchone()
    )

    if not conversa:

        conexao.close()

        return None

    id_lead = conversa[0]
    estado_json = conversa[1]

    estado = (
        json.loads(
            estado_json
        )
        if estado_json
        else None
    )

    cursor.execute(
        """
        SELECT
            role,
            content
        FROM mensagens
        WHERE id_conversa = ?
        ORDER BY id ASC
        """,
        (
            id_conversa,
        )
    )

    mensagens = (
        cursor.fetchall()
    )

    historico = [
        {
            "role":
                role,

            "content":
                content
        }

        for role, content
        in mensagens
    ]

    conexao.close()

    return {
        "id_lead":
            id_lead,

        "id_conversa":
            id_conversa,

        "estado":
            estado,

        "historico":
            historico
    }


# ==================================================
# CARREGAR ÚLTIMA CONVERSA
# ==================================================

def carregar_ultima_conversa():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT id_conversa
        FROM conversas
        ORDER BY atualizado_em DESC
        LIMIT 1
        """
    )

    resultado = (
        cursor.fetchone()
    )

    conexao.close()

    if not resultado:

        return None

    return carregar_conversa(
        resultado[0]
    )


# ==================================================
# SALVAR AGENDAMENTO
# ==================================================

def salvar_agendamento(
    id_lead,
    id_conversa,
    id_imovel,
    data_visita,
    hora_visita,
    observacao=""
):

    conexao = conectar()
    cursor = conexao.cursor()

    data_visita = str(
        data_visita
    )

    hora_visita = str(
        hora_visita
    )

    # ----------------------------------------------
    # VERIFICAR DUPLICIDADE
    # ----------------------------------------------

    cursor.execute(
        """
        SELECT id
        FROM agendamentos
        WHERE
            id_lead = ?
            AND id_conversa = ?
            AND id_imovel = ?
            AND data_visita = ?
            AND hora_visita = ?
            AND status = 'Agendado'
        LIMIT 1
        """,
        (
            id_lead,
            id_conversa,
            id_imovel,
            data_visita,
            hora_visita
        )
    )

    existente = (
        cursor.fetchone()
    )

    # ----------------------------------------------
    # SE JÁ EXISTIR
    # ----------------------------------------------

    if existente:

        conexao.close()

        return existente[0]


    # ----------------------------------------------
    # NOVO AGENDAMENTO
    # ----------------------------------------------

    criado_em = (
        datetime.now()
        .astimezone()
        .isoformat()
    )

    cursor.execute(
        """
        INSERT INTO agendamentos (
            id_lead,
            id_conversa,
            id_imovel,
            data_visita,
            hora_visita,
            observacao,
            status,
            criado_em
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            id_lead,
            id_conversa,
            id_imovel,
            data_visita,
            hora_visita,
            observacao,
            "Agendado",
            criado_em
        )
    )

    id_agendamento = (
        cursor.lastrowid
    )

    conexao.commit()
    conexao.close()

    return id_agendamento


# ==================================================
# LISTAR AGENDAMENTOS
# ==================================================

def listar_agendamentos():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT
            id,
            id_lead,
            id_conversa,
            id_imovel,
            data_visita,
            hora_visita,
            observacao,
            status,
            criado_em
        FROM agendamentos
        ORDER BY id DESC
        """
    )

    registros = (
        cursor.fetchall()
    )

    conexao.close()

    return registros


# ==================================================
# MÉTRICAS DO DASHBOARD
# ==================================================

def obter_metricas_dashboard():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM leads"
    )

    total_leads = (
        cursor.fetchone()[0]
    )

    cursor.execute(
        "SELECT COUNT(*) FROM conversas"
    )

    total_conversas = (
        cursor.fetchone()[0]
    )

    cursor.execute(
        "SELECT COUNT(*) FROM mensagens"
    )

    total_mensagens = (
        cursor.fetchone()[0]
    )

    cursor.execute(
        "SELECT COUNT(*) FROM agendamentos"
    )

    total_agendamentos = (
        cursor.fetchone()[0]
    )

    conexao.close()

    return {
        "leads":
            total_leads,

        "conversas":
            total_conversas,

        "mensagens":
            total_mensagens,

        "agendamentos":
            total_agendamentos
    }


# ==================================================
# CLASSIFICAÇÃO DOS LEADS
# ==================================================

def obter_classificacao_leads():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT estado_json
        FROM conversas
        WHERE estado_json IS NOT NULL
        """
    )

    registros = (
        cursor.fetchall()
    )

    conexao.close()

    quentes = 0
    mornos = 0
    frios = 0

    scores = []

    for linha in registros:

        estado_json = linha[0]

        if not estado_json:

            continue

        try:

            estado = json.loads(
                estado_json
            )

        except json.JSONDecodeError:

            continue

        classificacao = (
            estado.get(
                "classificacao"
            )
        )

        score = (
            estado.get(
                "score"
            )
        )

        if score is not None:

            scores.append(
                score
            )

        if classificacao == "Quente":

            quentes += 1

        elif classificacao == "Morno":

            mornos += 1

        elif classificacao == "Frio":

            frios += 1

    score_medio = (
        sum(scores) / len(scores)
        if scores
        else 0
    )

    return {
        "quentes":
            quentes,

        "mornos":
            mornos,

        "frios":
            frios,

        "score_medio":
            round(
                score_medio,
                1
            )
    }


# ==================================================
# LEADS PRIORITÁRIOS
# ==================================================

def listar_leads_prioritarios(
    limite=10
):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT
            id_lead,
            estado_json,
            atualizado_em
        FROM conversas
        WHERE estado_json IS NOT NULL
        ORDER BY atualizado_em DESC
        """
    )

    registros = (
        cursor.fetchall()
    )

    conexao.close()

    leads = []

    for linha in registros:

        id_lead = linha[0]
        estado_json = linha[1]
        atualizado_em = linha[2]

        try:

            estado = json.loads(
                estado_json
            )

        except json.JSONDecodeError:

            continue

        perfil = (
            estado.get(
                "perfil",
                {}
            )
        )

        score = (
            estado.get(
                "score"
            )
        )

        classificacao = (
            estado.get(
                "classificacao"
            )
        )

        if score is None:

            continue

        leads.append(
            {
                "Lead":
                    id_lead,

                "Intenção":
                    perfil.get(
                        "intencao"
                    ),

                "Região":
                    perfil.get(
                        "regiao_bairro"
                    ),

                "Urgência":
                    perfil.get(
                        "urgencia"
                    ),

                "Score":
                    score,

                "Classificação":
                    classificacao,

                "Atualizado em":
                    atualizado_em
            }
        )

    leads.sort(
        key=lambda x: x["Score"],
        reverse=True
    )

    return leads[:limite]


# ==================================================
# ÚLTIMOS AGENDAMENTOS
# ==================================================

def listar_ultimos_agendamentos(
    limite=10
):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT
            id,
            id_imovel,
            data_visita,
            hora_visita,
            status,
            criado_em
        FROM agendamentos
        ORDER BY id DESC
        LIMIT ?
        """,
        (
            limite,
        )
    )

    registros = (
        cursor.fetchall()
    )

    conexao.close()

    return [
        {
            "Código":
                linha[0],

            "Imóvel":
                linha[1],

            "Data":
                linha[2],

            "Horário":
                linha[3][:5],

            "Status":
                linha[4],

            "Registrado em":
                linha[5]
        }

        for linha in registros
    ]


# ==================================================
# CONVERSAS RECENTES
# ==================================================

def listar_conversas_recentes(
    limite=10
):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT
            id_conversa,
            id_lead,
            status,
            atualizado_em
        FROM conversas
        ORDER BY atualizado_em DESC
        LIMIT ?
        """,
        (
            limite,
        )
    )

    registros = (
        cursor.fetchall()
    )

    conexao.close()

    return [
        {
            "Lead":
                linha[1],

            "Conversa":
                linha[0],

            "Status":
                linha[2],

            "Última atualização":
                linha[3]
        }

        for linha in registros
    ]


# ==================================================
# FOLLOW-UPS PENDENTES
# ==================================================

def listar_followups_pendentes(
    horas=24,
    modo_demo=False
):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT
            c.id_conversa,
            c.id_lead,
            c.estado_json,
            c.atualizado_em,
            c.status
        FROM conversas c
        WHERE
            c.estado_json IS NOT NULL
            AND NOT EXISTS (
                SELECT 1
                FROM followups f
                WHERE
                    f.id_conversa = c.id_conversa
                    AND f.status = 'Enviado'
            )
        ORDER BY c.atualizado_em ASC
        """
    )

    registros = (
        cursor.fetchall()
    )

    conexao.close()

    agora = (
        datetime.now()
        .astimezone()
    )

    pendentes = []

    for linha in registros:

        id_conversa = linha[0]
        id_lead = linha[1]
        estado_json = linha[2]
        atualizado_em = linha[3]
        status = linha[4]

        if status != "ativo":

            continue

        try:

            estado = json.loads(
                estado_json
            )

            data_atualizacao = (
                datetime.fromisoformat(
                    atualizado_em
                )
            )

        except (
            json.JSONDecodeError,
            ValueError,
            TypeError
        ):

            continue

        tempo_sem_interacao = (
            agora
            - data_atualizacao
        )

        if (
            modo_demo
            or
            tempo_sem_interacao
            >= timedelta(
                hours=horas
            )
        ):

            pendentes.append(
                {
                    "id_lead":
                        id_lead,

                    "id_conversa":
                        id_conversa,

                    "estado":
                        estado,

                    "ultima_interacao":
                        atualizado_em
                }
            )

    return pendentes


# ==================================================
# REGISTRAR FOLLOW-UP
# ==================================================

def registrar_followup(
    id_lead,
    id_conversa,
    mensagem
):

    agora = (
        datetime.now()
        .astimezone()
        .isoformat()
    )

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO followups (
            id_lead,
            id_conversa,
            mensagem,
            status,
            criado_em
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            id_lead,
            id_conversa,
            mensagem,
            "Enviado",
            agora
        )
    )

    id_followup = (
        cursor.lastrowid
    )

    # IMPORTANTE:
    # NÃO atualizamos atualizado_em da conversa.
    # Follow-up não é uma nova interação do cliente.

    conexao.commit()
    conexao.close()

    return id_followup


# ==================================================
# MARCAR FOLLOW-UP COMO RESPONDIDO
# ==================================================

def marcar_followup_respondido(
    id_conversa
):

    agora = (
        datetime.now()
        .astimezone()
        .isoformat()
    )

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT id
        FROM followups
        WHERE
            id_conversa = ?
            AND status = 'Enviado'
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            id_conversa,
        )
    )

    resultado = (
        cursor.fetchone()
    )

    if resultado:

        cursor.execute(
            """
            UPDATE followups
            SET
                status = 'Respondido',
                respondido_em = ?
            WHERE id = ?
            """,
            (
                agora,
                resultado[0]
            )
        )

    conexao.commit()
    conexao.close()


# ==================================================
# LISTAR FOLLOW-UPS
# ==================================================

def listar_followups(
    limite=20
):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT
            id,
            id_lead,
            id_conversa,
            mensagem,
            status,
            criado_em,
            respondido_em
        FROM followups
        ORDER BY id DESC
        LIMIT ?
        """,
        (
            limite,
        )
    )

    registros = (
        cursor.fetchall()
    )

    conexao.close()

    return [
        {
            "id":
                linha[0],

            "id_lead":
                linha[1],

            "id_conversa":
                linha[2],

            "mensagem":
                linha[3],

            "status":
                linha[4],

            "criado_em":
                linha[5],

            "respondido_em":
                linha[6]
        }

        for linha in registros
    ]


# ==================================================
# MÉTRICAS DE FOLLOW-UP
# ==================================================

def obter_metricas_followup():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM followups
        """
    )

    total = (
        cursor.fetchone()[0]
    )

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM followups
        WHERE status = 'Respondido'
        """
    )

    respondidos = (
        cursor.fetchone()[0]
    )

    conexao.close()

    taxa = (
        round(
            (
                respondidos
                / total
                * 100
            ),
            1
        )
        if total
        else 0
    )

    return {
        "total":
            total,

        "respondidos":
            respondidos,

        "taxa_resposta":
            taxa
    }

# ==================================================
# ÚLTIMO AGENDAMENTO DA CONVERSA
# ==================================================

def obter_ultimo_agendamento_conversa(
    id_conversa
):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT
            id,
            id_imovel,
            data_visita,
            hora_visita,
            observacao,
            status,
            criado_em
        FROM agendamentos
        WHERE id_conversa = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            id_conversa,
        )
    )

    resultado = (
        cursor.fetchone()
    )

    conexao.close()

    if not resultado:

        return None

    return {
        "id":
            resultado[0],

        "id_imovel":
            resultado[1],

        "data_visita":
            resultado[2],

        "hora_visita":
            resultado[3],

        "observacao":
            resultado[4],

        "status":
            resultado[5],

        "criado_em":
            resultado[6]
    }


# ==================================================
# ÚLTIMO FOLLOW-UP DA CONVERSA
# ==================================================

def obter_ultimo_followup_conversa(
    id_conversa
):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT
            id,
            mensagem,
            status,
            criado_em,
            respondido_em
        FROM followups
        WHERE id_conversa = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            id_conversa,
        )
    )

    resultado = (
        cursor.fetchone()
    )

    conexao.close()

    if not resultado:

        return None

    return {
        "id":
            resultado[0],

        "mensagem":
            resultado[1],

        "status":
            resultado[2],

        "criado_em":
            resultado[3],

        "respondido_em":
            resultado[4]
    }


# ==================================================
# ÚLTIMO AGENDAMENTO DA CONVERSA
# ==================================================

def obter_ultimo_agendamento_conversa(
    id_conversa
):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT
            id,
            id_imovel,
            data_visita,
            hora_visita,
            observacao,
            status,
            criado_em
        FROM agendamentos
        WHERE id_conversa = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            id_conversa,
        )
    )

    resultado = (
        cursor.fetchone()
    )

    conexao.close()

    if not resultado:
        return None

    return {
        "id":
            resultado[0],

        "id_imovel":
            resultado[1],

        "data_visita":
            resultado[2],

        "hora_visita":
            resultado[3],

        "observacao":
            resultado[4],

        "status":
            resultado[5],

        "criado_em":
            resultado[6]
    }


# ==================================================
# ÚLTIMO FOLLOW-UP DA CONVERSA
# ==================================================

def obter_ultimo_followup_conversa(
    id_conversa
):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT
            id,
            mensagem,
            status,
            criado_em,
            respondido_em
        FROM followups
        WHERE id_conversa = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            id_conversa,
        )
    )

    resultado = (
        cursor.fetchone()
    )

    conexao.close()

    if not resultado:
        return None

    return {
        "id":
            resultado[0],

        "mensagem":
            resultado[1],

        "status":
            resultado[2],

        "criado_em":
            resultado[3],

        "respondido_em":
            resultado[4]
    }


# ==================================================
# DISTRIBUIÇÃO POR INTENÇÃO
# ==================================================

def obter_distribuicao_intencao():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT
            id_lead,
            estado_json,
            atualizado_em
        FROM conversas
        WHERE estado_json IS NOT NULL
        ORDER BY atualizado_em DESC
        """
    )

    registros = cursor.fetchall()

    conexao.close()

    # Guarda somente a conversa mais recente
    # de cada lead.
    leads_processados = set()

    compra = 0
    aluguel = 0
    investimento = 0
    nao_definido = 0

    for linha in registros:

        id_lead = linha[0]
        estado_json = linha[1]

        # Se já usamos a conversa mais recente
        # desse lead, ignoramos as anteriores.
        if id_lead in leads_processados:
            continue

        leads_processados.add(
            id_lead
        )

        try:

            estado = json.loads(
                estado_json
            )

        except (
            json.JSONDecodeError,
            TypeError
        ):
            continue

        perfil = estado.get(
            "perfil",
            {}
        )

        intencao = perfil.get(
            "intencao"
        )

        if intencao == "Compra":

            compra += 1

        elif intencao == "Aluguel":

            aluguel += 1

        elif intencao == "Investimento":

            investimento += 1

        else:

            nao_definido += 1

    return {
        "Compra": compra,
        "Aluguel": aluguel,
        "Investimento": investimento,
        "Não definido": nao_definido
    }