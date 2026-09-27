# Especificação do Dashboard — Agente SDR Imobiliário

## Objetivo
Definir como os principais indicadores da POC do Agente SDR Imobiliário deverão ser apresentados. O dashboard servirá para acompanhamento operacional, priorização de leads e validação do comportamento do agente.

## 1. Público-alvo
- Corretor / especialista comercial.
- Equipe responsável pela POC.
- Avaliadores da solução.

## 2. Indicadores principais
O topo do dashboard deve apresentar cards com:
- **Total de leads:** 600
- **Leads Quentes:** 331
- **Leads Mornos:** 220
- **Leads Frios:** 49
- **Agendamentos:** 183
- **Leads que aceitaram visita/reunião:** 183
- **Score médio:** 67.6

Os números acima são referências calculadas sobre a massa sintética atual e podem ser usados para validar a implementação.

## 3. Filtros recomendados
O dashboard deve permitir filtrar, quando viável:
- Classificação: Frio, Morno, Quente.
- Intenção: Compra, Aluguel, Investimento, Não definida.
- Status do lead.
- Urgência.
- Canal de entrada.
- Zona/região preferida.
- Tipo de imóvel.
- Período de entrada do lead.

## 4. Visualizações recomendadas

### 4.1 Distribuição por classificação
Gráfico de colunas ou rosca:
- Quente
- Morno
- Frio

### 4.2 Distribuição por intenção
Gráfico de barras:
- Compra
- Aluguel
- Investimento
- Não definida

### 4.3 Regiões mais procuradas
Gráfico de barras horizontais com Top 10 bairros/regiões informados pelos leads.

### 4.4 Agendamentos
Exibir:
- total de agendamentos;
- tipo de agendamento;
- status do agendamento;
- próximos compromissos.

### 4.5 Follow-up
Exibir:
- leads com follow-up;
- quantidade total de follow-ups;
- quantidade de leads que responderam ao follow-up;
- taxa de resposta quando aplicável.

### 4.6 Leads prioritários
Tabela com:
- nome;
- intenção;
- score;
- classificação;
- urgência;
- região/bairro;
- orçamento/ticket;
- status;
- próximo follow-up;
- aceite de visita/reunião.

Ordenação sugerida: maior score primeiro.

## 5. Wireframe sugerido

```text
+------------------------------------------------------------------+
|                   DASHBOARD SDR IMOBILIÁRIO                      |
+------------------------------------------------------------------+
| Total Leads | Quentes | Mornos | Frios | Agendamentos | Score   |
+------------------------------------------------------------------+
| Classificação dos Leads        | Intenção dos Leads              |
| [gráfico]                      | [gráfico]                       |
+------------------------------------------------------------------+
| Regiões mais procuradas        | Follow-ups / Agendamentos       |
| [gráfico Top 10]               | [indicadores/gráfico]           |
+------------------------------------------------------------------+
| Leads Prioritários                                                |
| Nome | Intenção | Score | Região | Urgência | Status | Próx. ação |
+------------------------------------------------------------------+
```

## 6. Regras de cálculo
- **Total de leads:** quantidade de registros da base `leads.csv`.
- **Classificação:** utilizar o campo `classificacao`.
- **Score:** utilizar o campo `score`; não recalcular no dashboard se a aplicação já tiver aplicado a regra oficial.
- **Agendamentos:** contar registros de `agendamentos.csv`.
- **Follow-ups:** utilizar `quantidade_followups`, `proximo_followup` e `respondeu_followup`.
- **Leads prioritários:** priorizar classificação Quente e maior score.

## 7. Critérios para validação da implementação
A implementação será considerada coerente quando:
1. Os cards refletirem os valores da base carregada.
2. A soma de Frio + Morno + Quente for igual ao total de leads classificados.
3. Os filtros alterarem apenas os dados exibidos, sem modificar a base original.
4. A tabela de leads prioritários apresentar os leads de maior score.
5. Agendamentos estiverem vinculados aos leads existentes.
6. O dashboard não criar informações inexistentes nas bases.


## 8. Aderência ao desafio
O desafio exige um **dashboard mínimo de acompanhamento**. Esta especificação atende ao planejamento desse requisito ao definir:
- acompanhamento da qualificação dos leads;
- priorização de leads quentes;
- distribuição por intenção;
- acompanhamento de agendamentos;
- acompanhamento de follow-ups;
- regiões mais procuradas;
- visão dos leads prioritários.

O dashboard também apoia o contexto de negócio descrito no desafio, especialmente a dificuldade de priorizar leads quentes e a necessidade de reduzir perda de oportunidades por falta de acompanhamento.

> Importante: este documento é a **especificação funcional do dashboard**. O requisito do desafio somente estará completamente atendido quando a tela estiver implementada e integrada à aplicação.

## 9. Observação
Esta especificação é independente da tecnologia de interface. Michele poderá implementá-la em Streamlit ou outra alternativa escolhida pelo grupo, mantendo os indicadores e conceitos descritos aqui.
