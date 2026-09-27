"""Regressão com Qwen real. Ativar explicitamente com RUN_OLLAMA_TESTS=1."""
import os
import unittest
from agent import Servicos, processar_mensagem
from catalogo import buscar_imoveis
from llm_client import OllamaClient


@unittest.skipUnless(os.getenv('RUN_OLLAMA_TESTS') == '1', 'Requer Ollama e ativação explícita')
class OllamaLiveTests(unittest.TestCase):
    def test_aluguel_completo_e_variacao(self):
        casos = [
            ('Quero alugar um apartamento mobiliado no Tatuapé, até 4 mil por mês, com 2 quartos. Minha urgência é alta.',
             'Tatuapé', 4000, 2, 'Alta'),
            ('Busco alugar apartamento mobiliado em Santana por até 3500 reais mensais, com 1 quarto e urgência baixa.',
             'Santana', 3500, 1, 'Baixa'),
        ]
        for mensagem, bairro, valor, quartos, urgencia in casos:
            with self.subTest(bairro=bairro):
                r = processar_mensagem({
                    'id_lead': 'aluguel', 'id_conversa': 'aluguel', 'id_mensagem': '1',
                    'mensagem': mensagem, 'historico': [],
                    'data_hora_atual': '2026-09-27T12:00:00-03:00',
                }, Servicos(OllamaClient(), buscar_imoveis))
                self.assertIsNone(r['erro'])
                esperado = dict(intencao='Aluguel', tipo_imovel_interesse='Apartamento',
                                regiao_bairro=bairro, orcamento_ticket=valor, quartos=quartos,
                                urgencia=urgencia, prefere_mobiliado='Sim')
                for campo, valor in esperado.items():
                    self.assertEqual(r['estado_atualizado']['perfil'][campo], valor, campo)
                self.assertEqual(r['campos_faltantes'], [])

    def test_resposta_curta_bairro_preserva_memoria(self):
        from schemas import novo_estado
        from agent import PERGUNTAS
        estado = novo_estado('aluguel', 'aluguel')
        estado['perfil'].update(intencao='Aluguel', tipo_imovel_interesse='Apartamento',
                                orcamento_ticket=4000, quartos=2, urgencia='Alta', prefere_mobiliado='Sim')
        estado['ultima_pergunta'] = PERGUNTAS['regiao_bairro']
        r = processar_mensagem({
            'id_lead': 'aluguel', 'id_conversa': 'aluguel', 'id_mensagem': '2',
            'mensagem': 'Tatuapé', 'estado': estado, 'historico': [],
            'data_hora_atual': '2026-09-27T12:00:00-03:00',
        }, Servicos(OllamaClient(), buscar_imoveis))
        self.assertIsNone(r['erro'])
        self.assertEqual(r['estado_atualizado']['perfil']['regiao_bairro'], 'Tatuapé')
        for campo, valor in estado['perfil'].items():
            if campo != 'regiao_bairro':
                self.assertEqual(r['estado_atualizado']['perfil'][campo], valor, campo)
        self.assertNotEqual(r['resposta'], PERGUNTAS['regiao_bairro'])

    def test_compra_com_aumento_de_orcamento_composto(self):
        estado, historico = None, []
        servicos = Servicos(OllamaClient(), buscar_imoveis)
        mensagens = ['Quero comprar um apartamento em Moema', '900 mil', '3',
                     'Média', 'Posso aumentar meu orçamento para 1 milhão e 100 mil']
        for indice, mensagem in enumerate(mensagens):
            resultado = processar_mensagem({
                'id_lead': 'teste-real', 'id_conversa': 'regressao-orcamento',
                'id_mensagem': str(indice), 'mensagem': mensagem,
                'estado': estado, 'historico': historico,
                'data_hora_atual': '2026-09-26T12:00:00-03:00',
            }, servicos)
            self.assertIsNone(resultado['erro'])
            estado = resultado['estado_atualizado']
            historico += [{'role': 'user', 'content': mensagem},
                          {'role': 'assistant', 'content': resultado['resposta']}]
            if indice == 3:
                self.assertEqual(estado['perfil']['orcamento_ticket'], 900000)
                self.assertEqual(resultado['imoveis_ids'], [])
        self.assertEqual(estado['perfil']['orcamento_ticket'], 1100000)
        self.assertEqual(estado['perfil']['regiao_bairro'], 'Moema')
        self.assertEqual(estado['perfil']['quartos'], 3)
        self.assertEqual(estado['perfil']['urgencia'], 'Média')
        self.assertEqual(resultado['acao'], 'apresentar_imoveis')
        self.assertIn('IMV0371', resultado['imoveis_ids'])
