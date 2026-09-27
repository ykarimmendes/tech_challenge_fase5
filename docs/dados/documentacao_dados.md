# Documentação dos Dados — Agente SDR Imobiliário

## Objetivo
Documentar as bases sintéticas preparadas para a POC, explicando a finalidade de cada arquivo, seus relacionamentos e como os dados devem ser consumidos pela aplicação.

## 1. Visão geral
A massa atual contém:
- **500 imóveis**
- **600 leads**
- **183 agendamentos**
- **2088 interações**
- arquivo específico com regras de qualificação

Todos os dados foram criados para fins acadêmicos e de demonstração.

## 2. Arquivos

### `imoveis.csv`
Base de imóveis disponível para consulta pelo agente.

Campos principais:
- `id_imovel`: identificador único.
- `tipo_negocio`: **Venda** ou **Aluguel**, conforme os valores existentes na base.
- `tipo_imovel`: apartamento, casa etc.
- `cidade`, `zona`, `bairro`: localização.
- `preco`: valor do imóvel.
- `quartos`, `banheiros`, `area_m2`, `vagas`: características.
- `mobiliado`, `aceita_pet`, `proximo_metro`, `imovel_novo`: atributos utilizados em preferências.
- `disponivel`: indica se o imóvel pode ser ofertado.
- `aluguel_estimado` e `yield_anual_pct`: apoio ao cenário de investimento.
- `descricao`: texto descritivo para apresentação ao lead.

Uso esperado:
- filtrar imóveis compatíveis com o perfil do lead;
- nunca apresentar imóvel inexistente na base;
- considerar apenas registros disponíveis quando a regra da aplicação assim exigir.

### `leads.csv`
Base principal de leads.

Campos principais:
- `id_lead`: identificador único.
- `nome`, `email_ficticio`, `canal`: identificação sintética e origem.
- `intencao`: Compra, Aluguel ou Investimento. Quando ainda não identificada, o campo permanece vazio; no dashboard essa situação pode ser exibida como **Não definida**.
- `orcamento_ticket`: orçamento de compra/aluguel ou ticket de investimento.
- `zona_preferida`, `regiao_bairro`: localização desejada.
- `tipo_imovel_interesse`, `quartos`: preferências.
- `urgencia`: prioridade temporal.
- `perfil_investidor`, `retorno_esperado_pct`: cenário de investimento.
- `aceita_pet`, `prefere_mobiliado`, `prefere_proximo_metro`, `prefere_imovel_novo`: preferências adicionais.
- `aceitou_visita_reuniao`: avanço comercial.
- `ultimo_contato`, `proximo_followup`, `quantidade_followups`, `respondeu_followup`: acompanhamento.
- `status`, `score`, `classificacao`: qualificação do lead.

Uso esperado:
- armazenar/consultar o estado atual da qualificação;
- alimentar score, priorização, follow-up e dashboard;
- permitir continuidade da conversa.

### `regras_qualificacao.csv`
Contém os critérios utilizados na pontuação dos leads.

#### Compra/Aluguel
- intenção identificada: +10
- orçamento: +20
- região: +15
- tipo de imóvel: +10
- quartos: +10
- urgência: Alta +15 / Média +10 / Baixa +5
- aceitou visita/reunião: +20

#### Investimento
- intenção: +10
- ticket: +20
- região: +10
- perfil do investidor: +15
- retorno esperado: +15
- urgência: Alta +10 / Média +7 / Baixa +3
- aceitou reunião/visita: +20

Classificação:
- 0 a 39: Frio
- 40 a 69: Morno
- 70 a 100: Quente

Regra complementar:
- investidor sem `perfil_investidor` ou `retorno_esperado_pct` não deve ser classificado como Quente; o score deve permanecer limitado a 69 enquanto esses dados estiverem ausentes.

### `agendamentos.csv`
Registra visitas e reuniões.

Campos:
- `id_agendamento`
- `id_lead`
- `id_imovel`
- `tipo_agendamento`
- `data_agendamento`
- `hora_agendamento`
- `status_agendamento`
- `responsavel`
- `observacao`

Relacionamentos:
- `id_lead` → `leads.csv`
- `id_imovel` → `imoveis.csv` quando o compromisso estiver associado a um imóvel.

### `interacoes.csv`
Histórico sintético utilizado para continuidade e contextualização.

Campos:
- `id_interacao`
- `id_lead`
- `data_hora`
- `origem`
- `tipo_interacao`
- `mensagem_resumida`
- `intencao_detectada`
- `campo_atualizado`

Uso esperado:
- recuperar contexto;
- evitar perguntas repetidas;
- demonstrar memória conversacional;
- apoiar geração de resumo para o corretor.

## 3. Relacionamentos

```text
leads.csv
   |
   | id_lead
   +--------------------> agendamentos.csv
   |
   +--------------------> interacoes.csv

imoveis.csv
   |
   | id_imovel
   +--------------------> agendamentos.csv
```

## 4. Fluxo de uso sugerido
1. Receber mensagem do lead.
2. Identificar intenção e extrair informações.
3. Consultar/atualizar o registro em `leads.csv`.
4. Aplicar as regras de qualificação.
5. Consultar `imoveis.csv` quando houver critérios suficientes.
6. Registrar histórico em `interacoes.csv`.
7. Registrar visita/reunião em `agendamentos.csv`, quando aceita.
8. Atualizar dashboard.
9. Gerar resumo para corretor/especialista.

## 5. Formato técnico dos CSVs
- Codificação: UTF-8 com BOM.
- Delimitador: ponto e vírgula (`;`).

Exemplo em Python:

```python
import pandas as pd

leads = pd.read_csv("data/leads.csv", sep=";")
imoveis = pd.read_csv("data/imoveis.csv", sep=";")
```

## 6. Cuidados de implementação
- Não substituir IDs existentes.
- Não inventar valores ausentes.
- Preservar histórico de interações.
- Tratar campos vazios como informação ainda não coletada.
- Validar IDs antes de criar relacionamentos.
- Manter o cálculo de score consistente com `regras_qualificacao.csv`.
- Utilizar a informação mais recente quando o lead alterar uma preferência.


## 7. Aderência ao desafio
Esta documentação e as bases apoiam diretamente requisitos obrigatórios da POC:
- **Qualificação de leads:** campos estruturados, score e classificação.
- **Compra, aluguel e investimento:** intenção e atributos específicos para cada fluxo.
- **Follow-up automático:** campos de último contato, próximo follow-up, quantidade e resposta.
- **Agendamento de reuniões/visitas:** base `agendamentos.csv`.
- **Integração com base simulada de imóveis:** base `imoveis.csv`.
- **Continuidade da conversa:** histórico em `interacoes.csv`.
- **Resumo para corretor/especialista:** os dados estruturados e o histórico fornecem os insumos para geração do resumo.
- **Dashboard mínimo:** os mesmos dados alimentam os indicadores definidos na segunda entrega.

> Observação: estes arquivos fornecem dados, regras e especificações. O atendimento conversacional, o follow-up automático, a geração do resumo e o dashboard precisam estar efetivamente implementados na aplicação final para que os requisitos funcionais sejam demonstrados.

## 8. Observação
As bases são sintéticas e destinadas à demonstração acadêmica. Alterações de estrutura devem ser combinadas com o grupo para evitar quebra na integração.
