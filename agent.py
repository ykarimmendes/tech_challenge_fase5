"""Núcleo sem estado global: a aplicação fornece e persiste cada conversa."""
from copy import deepcopy
from dataclasses import dataclass
from typing import Callable
import re
import unicodedata

from llm_client import LLMError
from prompts import mensagens_extracao
from schemas import EXTRACAO_SCHEMA, validar_entrada, validar_extracao

PERGUNTAS = {
    'intencao': 'Você procura um imóvel para comprar, alugar ou investir?',
    'orcamento_ticket': 'Qual é o seu orçamento máximo?',
    'regiao_bairro': 'Em qual bairro ou região você procura?',
    'tipo_imovel_interesse': 'Que tipo de imóvel você procura: apartamento, casa, studio ou cobertura?',
    'quartos': 'Quantos quartos você precisa?',
    'urgencia': 'Como você considera sua urgência: alta, média ou baixa?',
    'perfil_investidor': 'Seu perfil de investimento é conservador, moderado ou arrojado?',
    'retorno_esperado_pct': 'Qual retorno percentual anual você espera?',
}


@dataclass
class Servicos:
    llm: object
    buscar_imoveis: Callable | None = None
    calcular_score: Callable | None = None


def _remocao_explicita(mensagem):
    """Não permitir que ausência de menção seja interpretada como remoção."""
    texto = ''.join(c for c in unicodedata.normalize('NFD', mensagem.casefold())
                    if unicodedata.category(c) != 'Mn')
    return bool(re.search(r'\b(remov\w*|apag\w*|esquec\w*|retir\w*|desconsider\w*)\b|'
                          r'\b(sem preferencia|nao (tenho|quero) (mais )?preferencia|'
                          r'qualquer bairro|tanto faz|indiferente)\b', texto))


def campos_faltantes(perfil):
    if perfil['intencao'] is None:
        return ['intencao']
    campos = (['orcamento_ticket', 'perfil_investidor', 'retorno_esperado_pct', 'urgencia']
              if perfil['intencao'] == 'Investimento' else
              ['orcamento_ticket', 'regiao_bairro', 'tipo_imovel_interesse', 'quartos', 'urgencia'])
    return [k for k in campos if perfil[k] is None]


def gerar_resumo(estado):
    linhas = [f'{k}: {"não informado" if v is None else v}' for k, v in estado['perfil'].items()]
    linhas += [f'Score: {estado.get("score") if estado.get("score") is not None else "pendente"}',
               f'Classificação: {estado.get("classificacao") or "pendente"}',
               f'Situação: {estado["status"]}',
               'Agendamento: nenhum registro confirmado pelo núcleo.']
    return '\n'.join(linhas)


def _resultado(estado, resposta, acao, alterados=None, erro=None):
    return {'resposta': resposta, 'estado_atualizado': estado,
            'campos_alterados': alterados or [], 'campos_faltantes': campos_faltantes(estado['perfil']),
            'acao': acao, 'imoveis_ids': list(estado['imoveis_ids']),
            'solicitacao_agendamento': None, 'resumo_corretor': gerar_resumo(estado), 'erro': erro}


def processar_mensagem(entrada, servicos):
    """Entrada inválida gera ValueError; falha do LLM retorna erro sem alterar estado."""
    estado = validar_entrada(entrada)
    if estado['status'] != 'ativo':
        return _resultado(estado, 'Este atendimento já foi encerrado ou encaminhado. Inicie uma nova conversa para retomar.', 'encerrar')
    try:
        # Uma escolha literal da pergunta fechada não precisa de inferência do modelo.
        urgencias = {'alta': 'Alta', 'média': 'Média', 'media': 'Média', 'baixa': 'Baixa'}
        escolha = entrada['mensagem'].strip().rstrip('.!').casefold()
        if estado['ultima_pergunta'] == PERGUNTAS['urgencia'] and escolha in urgencias:
            extracao = {'atualizacoes': {'urgencia': urgencias[escolha]},
                        'evento': 'continuar', 'esclarecimento': None}
        else:
            extracao = validar_extracao(servicos.llm.extrair(mensagens_extracao(entrada, estado), EXTRACAO_SCHEMA))
            if not _remocao_explicita(entrada['mensagem']):
                extracao['atualizacoes'] = {k: v for k, v in extracao['atualizacoes'].items() if v is not None}
    except (LLMError, ValueError, TypeError):
        return _resultado(estado, 'Não consegui interpretar sua mensagem agora. Pode tentar novamente?',
                          'tentar_novamente', erro='falha_extracao')

    anterior = deepcopy(estado['perfil'])
    updates = extracao['atualizacoes']
    mudou_intencao = ('intencao' in updates and updates['intencao'] != anterior['intencao'])
    if mudou_intencao and anterior['intencao'] is not None:
        # Valores monetários e aceite não podem migrar silenciosamente entre fluxos.
        for campo in ['orcamento_ticket', 'aceitou_visita_reuniao', 'perfil_investidor', 'retorno_esperado_pct']:
            estado['perfil'][campo] = None
    estado['perfil'].update(updates)
    alterados = [k for k in anterior if anterior[k] != estado['perfil'][k]]
    if alterados:
        estado['imoveis_ids'] = []
        estado['score'] = estado['classificacao'] = None

    evento = extracao['evento']
    if evento in ['humano', 'desistir']:
        estado['status'] = 'encaminhamento_solicitado' if evento == 'humano' else 'encerrado'
        estado['ultima_pergunta'] = None
        return _resultado(estado, 'Vou solicitar atendimento humano para você.' if evento == 'humano'
                          else 'Tudo bem. Encerrei este atendimento e não solicitarei novos contatos.',
                          'encaminhar_humano' if evento == 'humano' else 'encerrar', alterados)

    if servicos.calcular_score and estado['perfil']['intencao']:
        try:
            score = servicos.calcular_score(deepcopy(estado['perfil']))
            pontos = score['score']
            if type(pontos) is not int or not 0 <= pontos <= 100:
                raise ValueError('Score inválido')
            classe = 'Frio' if pontos < 40 else 'Morno' if pontos < 70 else 'Quente'
            if score['classificacao'] != classe:
                raise ValueError('Classificação inconsistente')
            p = estado['perfil']
            if p['intencao'] == 'Investimento' and (p['perfil_investidor'] is None or p['retorno_esperado_pct'] is None) and pontos > 69:
                raise ValueError('Investidor incompleto')
            estado['score'], estado['classificacao'] = pontos, classe
        except (ValueError, TypeError, KeyError, RuntimeError):
            estado['score'] = estado['classificacao'] = None
            return _resultado(estado, 'Registrei seus dados, mas a qualificação está temporariamente indisponível.',
                              'tentar_novamente', alterados, 'falha_score')

    if evento == 'resumo':
        return _resultado(estado, gerar_resumo(estado), 'perguntar', alterados)
    if extracao['esclarecimento']:
        estado['ultima_pergunta'] = extracao['esclarecimento']
        return _resultado(estado, extracao['esclarecimento'], 'perguntar', alterados)
    faltantes = campos_faltantes(estado['perfil'])
    if faltantes:
        pergunta = PERGUNTAS[faltantes[0]]
        if faltantes[0] == 'orcamento_ticket' and estado['perfil']['intencao'] == 'Aluguel':
            pergunta = 'Qual é seu orçamento mensal máximo para o aluguel?'
        estado['ultima_pergunta'] = pergunta
        return _resultado(estado, pergunta, 'perguntar', alterados)

    estado['ultima_pergunta'] = None
    if servicos.buscar_imoveis is None:
        return _resultado(estado, 'Já organizei seu perfil. A consulta ao catálogo ainda precisa ser conectada.',
                          'tentar_novamente', alterados, 'busca_nao_configurada')
    try:
        imoveis = servicos.buscar_imoveis(deepcopy(estado['perfil']))
        for imovel in imoveis:
            if not isinstance(imovel['id_imovel'], str) or imovel['disponivel'] != 'Sim':
                raise ValueError('Resultado inválido')
            if type(imovel['preco']) not in (int, float) or imovel['preco'] <= 0:
                raise ValueError('Preço inválido')
        estado['imoveis_ids'] = [i['id_imovel'] for i in imoveis[:3]]
        if not imoveis:
            pergunta = 'Não encontrei imóveis compatíveis. Qual critério você aceita flexibilizar: região, orçamento ou características?'
            estado['ultima_pergunta'] = pergunta
            return _resultado(estado, pergunta, 'perguntar', alterados)
        linhas = [f"{i['id_imovel']}: {i['tipo_imovel']} em {i['bairro']}, {i['quartos']} quarto(s), R$ {i['preco']:,.2f}." for i in imoveis[:3]]
    except (ValueError, TypeError, KeyError, RuntimeError, OSError):
        estado['imoveis_ids'] = []
        return _resultado(estado, 'A consulta aos imóveis está indisponível no momento.',
                          'tentar_novamente', alterados, 'falha_busca')
    pergunta = 'Você tem interesse em conversar com um corretor sobre alguma dessas opções?'
    estado['ultima_pergunta'] = pergunta
    return _resultado(estado, '\n'.join(linhas) + '\n' + pergunta, 'apresentar_imoveis', alterados)
