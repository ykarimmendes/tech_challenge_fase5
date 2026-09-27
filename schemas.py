"""Contrato e validação do núcleo, sem dependências externas."""
from copy import deepcopy
from datetime import datetime
import math


ENUMS = {
    'intencao': ['Compra', 'Aluguel', 'Investimento'],
    'tipo_imovel_interesse': ['Apartamento', 'Casa', 'Studio', 'Cobertura'],
    'urgencia': ['Alta', 'Média', 'Baixa'],
    'perfil_investidor': ['Conservador', 'Moderado', 'Arrojado'],
    **{k: ['Sim', 'Não', 'Indiferente'] for k in (
        'aceita_pet', 'prefere_mobiliado', 'prefere_proximo_metro', 'prefere_imovel_novo')},
    'aceitou_visita_reuniao': ['Sim', 'Não'],
}
TEXTOS = ['regiao_bairro', 'zona_preferida', 'prazo_declarado']
NUMEROS = ['orcamento_ticket', 'retorno_esperado_pct', 'quartos']
CAMPOS = list(ENUMS) + TEXTOS + NUMEROS
PROPRIEDADES = {
    **{k: {'enum': v + [None]} for k, v in ENUMS.items()},
    **{k: {'type': ['string', 'null'], 'minLength': 1, 'maxLength': 300} for k in TEXTOS},
    **{k: {'type': ['number', 'null'], 'minimum': 0} for k in NUMEROS},
}
PROPRIEDADES['quartos'] = {'type': ['integer', 'null'], 'minimum': 0}
PROPRIEDADES['regiao_bairro']['description'] = 'Bairro ou região explicitamente solicitado, por exemplo Tatuapé, Moema ou Vila Mariana.'
PROPRIEDADES['orcamento_ticket']['description'] = 'Limite monetário em reais. 4 mil por mês = 4000; 2 milhões = 2000000.'
PROPRIEDADES = {k: {'anyOf': [v, {'const': '__REMOVER__'}]} for k, v in PROPRIEDADES.items()}
EXTRACAO_SCHEMA = {
    'type': 'object', 'additionalProperties': False,
    'properties': {
        'atualizacoes': {'type': 'object', 'properties': PROPRIEDADES,
                        'additionalProperties': False, 'required': CAMPOS},
        'evento': {'enum': ['continuar', 'humano', 'desistir', 'resumo']},
        'esclarecimento': {'type': ['string', 'null'], 'maxLength': 300},
    },
    'required': ['atualizacoes', 'evento', 'esclarecimento'],
}


def validar_campos(dados):
    if not isinstance(dados, dict) or set(dados) - set(CAMPOS):
        raise ValueError('Campos de perfil inválidos')
    for campo, valor in dados.items():
        if valor is None:
            continue
        if campo in ENUMS and valor not in ENUMS[campo]:
            raise ValueError(f'Categoria inválida: {campo}')
        if campo in TEXTOS and (not isinstance(valor, str) or not valor.strip() or len(valor) > 300):
            raise ValueError(f'Texto inválido: {campo}')
        if campo in NUMEROS:
            if type(valor) not in (int, float) or not math.isfinite(valor) or valor < 0:
                raise ValueError(f'Número inválido: {campo}')
            if campo == 'orcamento_ticket' and valor == 0:
                raise ValueError('Orçamento deve ser positivo')
            if campo == 'quartos' and type(valor) is not int:
                raise ValueError('Quartos deve ser inteiro')
    return deepcopy(dados)


def validar_extracao(dados):
    obrigatorios = {'atualizacoes', 'evento', 'esclarecimento'}
    if not isinstance(dados, dict) or not obrigatorios <= set(dados) or set(dados) - set(EXTRACAO_SCHEMA['required']):
        raise ValueError('Formato de extração inválido')
    dados = deepcopy(dados)
    campos = dados['atualizacoes']
    if not isinstance(campos, dict):
        raise ValueError('Atualizações inválidas')
    if set(campos) == set(CAMPOS):
        dados['atualizacoes'] = {k: None if v == '__REMOVER__' else v
                                 for k, v in campos.items() if v is not None}
    validar_campos(dados['atualizacoes'])
    if dados['evento'] not in EXTRACAO_SCHEMA['properties']['evento']['enum']:
        raise ValueError('Evento inválido')
    pergunta = dados['esclarecimento']
    if pergunta is not None and (not isinstance(pergunta, str) or not pergunta.strip() or len(pergunta) > 300):
        raise ValueError('Esclarecimento inválido')
    return dados


def novo_estado(id_lead, id_conversa):
    return {'id_lead': id_lead, 'id_conversa': id_conversa,
            'perfil': dict.fromkeys(CAMPOS), 'status': 'ativo',
            'ultima_pergunta': None, 'imoveis_ids': [],
            'score': None, 'classificacao': None}


def validar_entrada(entrada):
    for campo in ['id_lead', 'id_conversa', 'id_mensagem', 'mensagem']:
        if not isinstance(entrada.get(campo), str) or not entrada[campo].strip():
            raise ValueError(f'Entrada obrigatória: {campo}')
    if len(entrada['mensagem']) > 8000:
        raise ValueError('Mensagem excede 8000 caracteres')
    agora = datetime.fromisoformat(entrada['data_hora_atual'])
    if agora.utcoffset() is None:
        raise ValueError('data_hora_atual precisa de fuso')
    estado = deepcopy(entrada.get('estado'))
    if estado is None:
        estado = novo_estado(entrada['id_lead'], entrada['id_conversa'])
    if any(estado.get(k) != entrada[k] for k in ['id_lead', 'id_conversa']):
        raise ValueError('Estado pertence a outro lead ou conversa')
    validar_campos(estado['perfil'])
    if set(estado['perfil']) != set(CAMPOS):
        raise ValueError('Perfil incompleto no contrato')
    for mensagem in entrada.get('historico', []):
        if mensagem.get('role') not in ['user', 'assistant'] or not isinstance(mensagem.get('content'), str):
            raise ValueError('Histórico inválido')
    return estado
