"""Demonstração local. Memória somente durante a execução."""
from datetime import datetime
from uuid import uuid4

from agent import Servicos, processar_mensagem
from catalogo import buscar_imoveis
from llm_client import OllamaClient


def main():
    cliente = OllamaClient()
    servicos = Servicos(cliente, buscar_imoveis=buscar_imoveis)
    lead, conversa = str(uuid4()), str(uuid4())
    estado, historico = None, []
    print(f'SDR Imobiliário — modelo {cliente.model}. /sair encerra. /resumo mostra os dados.')
    while True:
        try:
            mensagem = input('Você: ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nAtendimento encerrado.')
            break
        if mensagem == '/sair':
            break
        if not mensagem:
            continue
        if mensagem == '/resumo':
            from agent import gerar_resumo
            print(gerar_resumo(estado) if estado else 'Nenhuma informação coletada.')
            continue
        entrada = {'id_lead': lead, 'id_conversa': conversa, 'id_mensagem': str(uuid4()),
                   'mensagem': mensagem, 'estado': estado, 'historico': historico,
                   'data_hora_atual': datetime.now().astimezone().isoformat()}
        resultado = processar_mensagem(entrada, servicos)
        estado = resultado['estado_atualizado']
        print('Agente:', resultado['resposta'])
        if resultado['erro'] == 'falha_extracao':
            print('Verifique se o Ollama está iniciado e o modelo configurado foi baixado.')
        else:
            historico += [{'role': 'user', 'content': mensagem},
                          {'role': 'assistant', 'content': resultado['resposta']}]
        if estado['status'] != 'ativo':
            break


if __name__ == '__main__':
    main()
