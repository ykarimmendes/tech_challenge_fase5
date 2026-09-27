import unittest
from copy import deepcopy
from unittest.mock import patch, MagicMock
import json

from agent import Servicos, processar_mensagem
from catalogo import buscar_imoveis
from llm_client import OllamaClient, LLMError
from schemas import novo_estado


class ModeloSimulado:
    def __init__(self, updates=None, evento='continuar', esclarecer=None):
        self.resultado = {'atualizacoes': updates or {}, 'evento': evento, 'esclarecimento': esclarecer}

    def extrair(self, mensagens, schema):
        return deepcopy(self.resultado)


def entrada(estado=None):
    return {'id_lead': 'L1', 'id_conversa': 'C1', 'id_mensagem': 'M1',
            'mensagem': 'Mensagem de teste', 'estado': estado, 'historico': [],
            'data_hora_atual': '2026-09-26T12:00:00-03:00'}


class AgentTests(unittest.TestCase):
    def test_extracao_completa_nulos_nao_apagam_memoria(self):
        from schemas import CAMPOS
        e = novo_estado('L1', 'C1')
        e['perfil'].update(intencao='Aluguel', orcamento_ticket=4000)
        campos = dict.fromkeys(CAMPOS)
        campos['regiao_bairro'] = 'Tatuapé'
        r = processar_mensagem(entrada(e), Servicos(ModeloSimulado(campos)))
        self.assertEqual(r['estado_atualizado']['perfil']['orcamento_ticket'], 4000)
        self.assertEqual(r['estado_atualizado']['perfil']['intencao'], 'Aluguel')
        self.assertEqual(r['estado_atualizado']['perfil']['regiao_bairro'], 'Tatuapé')

    def test_remocao_explicita_em_extracao_completa(self):
        from schemas import CAMPOS
        e = novo_estado('L1', 'C1')
        e['perfil'].update(intencao='Investimento', regiao_bairro='Moema')
        campos = dict.fromkeys(CAMPOS)
        campos['regiao_bairro'] = '__REMOVER__'
        en = entrada(e)
        en['mensagem'] = 'Não tenho mais preferência por bairro'
        r = processar_mensagem(en, Servicos(ModeloSimulado(campos)))
        self.assertIsNone(r['estado_atualizado']['perfil']['regiao_bairro'])
        self.assertEqual(r['estado_atualizado']['perfil']['intencao'], 'Investimento')

    def test_urgencia_literal_nao_depende_de_inferencia(self):
        from agent import PERGUNTAS
        e = novo_estado('L1', 'C1')
        e['ultima_pergunta'] = PERGUNTAS['urgencia']
        llm = MagicMock()
        en = entrada(e)
        en['mensagem'] = 'Média'
        r = processar_mensagem(en, Servicos(llm))
        self.assertEqual(r['estado_atualizado']['perfil']['urgencia'], 'Média')
        llm.extrair.assert_not_called()

    def test_coleta_varios_campos_e_pergunta_so_proximo(self):
        r = processar_mensagem(entrada(), Servicos(ModeloSimulado({
            'intencao': 'Compra', 'orcamento_ticket': 900000,
            'regiao_bairro': 'Moema', 'tipo_imovel_interesse': 'Apartamento'})))
        self.assertEqual(r['campos_faltantes'], ['quartos', 'urgencia'])
        self.assertIn('quartos', r['resposta'])

    def test_correcao_preserva_outros_campos_e_nao_muta_entrada(self):
        e = novo_estado('L1', 'C1')
        e['perfil'].update(intencao='Compra', orcamento_ticket=900000, regiao_bairro='Moema')
        e['imoveis_ids'] = ['IMV0001']
        original = deepcopy(e)
        r = processar_mensagem(entrada(e), Servicos(ModeloSimulado({'orcamento_ticket': 750000})))
        self.assertEqual(e, original)
        self.assertEqual(r['estado_atualizado']['perfil']['regiao_bairro'], 'Moema')
        self.assertEqual(r['estado_atualizado']['perfil']['orcamento_ticket'], 750000)
        self.assertEqual(r['imoveis_ids'], [])

    def test_mudar_para_aluguel_reconfirma_orcamento(self):
        e = novo_estado('L1', 'C1')
        e['perfil'].update(intencao='Compra', orcamento_ticket=900000)
        r = processar_mensagem(entrada(e), Servicos(ModeloSimulado({'intencao': 'Aluguel'})))
        self.assertIsNone(r['estado_atualizado']['perfil']['orcamento_ticket'])
        self.assertIn('mensal', r['resposta'])

    def test_estado_de_outro_cliente_rejeitado(self):
        with self.assertRaises(ValueError):
            processar_mensagem(entrada(novo_estado('OUTRO', 'C1')), Servicos(ModeloSimulado()))

    def test_saida_invalida_preserva_estado(self):
        e = novo_estado('L1', 'C1')
        for updates in [{'score': 100}, {'orcamento_ticket': -1}, {'quartos': True}, {'urgencia': 'Amanhã'}]:
            with self.subTest(updates=updates):
                r = processar_mensagem(entrada(e), Servicos(ModeloSimulado(updates)))
                self.assertEqual(r['erro'], 'falha_extracao')
                self.assertEqual(r['estado_atualizado'], e)

    def test_falha_modelo_preserva_estado(self):
        llm = MagicMock()
        llm.extrair.side_effect = LLMError('offline')
        e = novo_estado('L1', 'C1')
        r = processar_mensagem(entrada(e), Servicos(llm))
        self.assertEqual(r['estado_atualizado'], e)
        self.assertEqual(r['acao'], 'tentar_novamente')

    def test_humano_e_desistencia_sem_terminar_coleta(self):
        for evento, acao in [('humano', 'encaminhar_humano'), ('desistir', 'encerrar')]:
            r = processar_mensagem(entrada(), Servicos(ModeloSimulado(evento=evento)))
            self.assertEqual(r['acao'], acao)
            self.assertNotEqual(r['estado_atualizado']['status'], 'ativo')

    def test_investidor_incompleto_nao_recebe_score_quente(self):
        r = processar_mensagem(entrada(), Servicos(ModeloSimulado({'intencao': 'Investimento'}),
            calcular_score=lambda p: {'score': 80, 'classificacao': 'Quente'}))
        self.assertEqual(r['erro'], 'falha_score')
        self.assertIsNone(r['estado_atualizado']['score'])

    def test_ausencia_de_opcoes(self):
        e = novo_estado('L1', 'C1')
        e['perfil'].update(intencao='Compra', orcamento_ticket=1, regiao_bairro='Moema',
                          tipo_imovel_interesse='Apartamento', quartos=2, urgencia='Alta')
        r = processar_mensagem(entrada(e), Servicos(ModeloSimulado(), buscar_imoveis))
        self.assertEqual(r['imoveis_ids'], [])
        self.assertIn('flexibilizar', r['resposta'])

    def test_catalogo_retorna_somente_disponiveis_no_orcamento(self):
        p = novo_estado('L1', 'C1')['perfil']
        p.update(intencao='Compra', orcamento_ticket=10000000)
        rows = buscar_imoveis(p)
        self.assertTrue(rows)
        self.assertTrue(all(r['disponivel'] == 'Sim' and r['tipo_negocio'] == 'Venda'
                            and r['preco'] <= p['orcamento_ticket'] for r in rows))

    def test_schema_enviado_ao_ollama(self):
        response = MagicMock()
        response.read.return_value = json.dumps({'done': True, 'message': {'content': '{"ok": true}'}}).encode()
        response.__enter__.return_value = response
        with patch('llm_client.urlopen', return_value=response) as call:
            self.assertEqual(OllamaClient().extrair([], {'type': 'object'}), {'ok': True})
            body = json.loads(call.call_args.args[0].data)
            self.assertFalse(body['stream'])
            self.assertEqual(body['format'], {'type': 'object'})


if __name__ == '__main__':
    unittest.main()
