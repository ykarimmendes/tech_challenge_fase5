"""Adaptador de leitura para demonstrar o agente com os CSVs recebidos."""
import csv
from pathlib import Path
import unicodedata


def normalizar(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto or '')
                   if unicodedata.category(c) != 'Mn').casefold().strip()


def buscar_imoveis(perfil, caminho=None):
    caminho = caminho or Path(__file__).parent / 'data' / 'imoveis.csv'
    negocio = 'Aluguel' if perfil['intencao'] == 'Aluguel' else 'Venda'
    encontrados = []
    with open(caminho, encoding='utf-8-sig', newline='') as arquivo:
        for row in csv.DictReader(arquivo, delimiter=';'):
            if row['disponivel'] != 'Sim' or row['tipo_negocio'] != negocio:
                continue
            if perfil.get('orcamento_ticket') is None or float(row['preco']) > perfil['orcamento_ticket']:
                continue
            if any(perfil.get(k) and normalizar(perfil[k]) != normalizar(row[col])
                   for k, col in [('regiao_bairro', 'bairro'), ('zona_preferida', 'zona'),
                                  ('tipo_imovel_interesse', 'tipo_imovel')]):
                continue
            if perfil.get('quartos') is not None and int(row['quartos']) < perfil['quartos']:
                continue
            if any(perfil.get(k) == 'Sim' and row[col] != 'Sim' for k, col in [
                ('aceita_pet', 'aceita_pet'), ('prefere_mobiliado', 'mobiliado'),
                ('prefere_proximo_metro', 'proximo_metro'), ('prefere_imovel_novo', 'imovel_novo')]):
                continue
            if perfil['intencao'] == 'Investimento' and perfil.get('retorno_esperado_pct') is not None:
                if not row['yield_anual_pct'] or float(row['yield_anual_pct']) < perfil['retorno_esperado_pct']:
                    continue
            row['preco'], row['quartos'] = float(row['preco']), int(row['quartos'])
            encontrados.append(row)
    return sorted(encontrados, key=lambda r: (r['preco'], r['id_imovel']))[:3]
