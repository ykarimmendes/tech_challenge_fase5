# Fluxos Funcionais — Agente SDR Imobiliário

## Objetivo
Definir os principais fluxos de atendimento que o agente deverá seguir durante a POC, considerando os cenários de compra, aluguel, investimento, follow-up, agendamento e encaminhamento comercial.

## 1. Fluxo de Compra
1. Identificar que o lead deseja comprar um imóvel.
2. Perguntar faixa de orçamento.
3. Perguntar região/bairro de interesse.
4. Perguntar tipo de imóvel desejado.
5. Perguntar quantidade de quartos.
6. Identificar urgência da compra.
7. Consultar a base de imóveis disponíveis.
8. Apresentar opções compatíveis.
9. Confirmar interesse em visita ou reunião.
10. Registrar agendamento quando aceito.
11. Atualizar score/classificação do lead.
12. Gerar resumo para o corretor.

**Sequência resumida:**  
Intenção → Orçamento → Região → Tipo de imóvel → Quartos → Urgência → Busca → Opções → Visita/Reunião → Resumo.

## 2. Fluxo de Aluguel
1. Identificar que o lead deseja alugar um imóvel.
2. Perguntar orçamento mensal.
3. Perguntar região/bairro.
4. Perguntar tipo de imóvel.
5. Perguntar quantidade de quartos.
6. Coletar preferências úteis, quando aplicável: mobiliado, pet, proximidade de metrô, imóvel novo.
7. Identificar urgência da mudança.
8. Consultar imóveis disponíveis para aluguel.
9. Apresentar opções compatíveis.
10. Confirmar interesse em visita.
11. Registrar agendamento.
12. Atualizar qualificação e gerar resumo.

**Sequência resumida:**  
Intenção → Orçamento mensal → Região → Tipo → Quartos → Preferências → Urgência → Busca → Visita → Resumo.

## 3. Fluxo de Investimento
1. Identificar intenção de investimento.
2. Perguntar valor/ticket disponível.
3. Perguntar região de interesse, quando houver.
4. Identificar perfil do investidor: conservador, moderado ou arrojado.
5. Perguntar expectativa de retorno.
6. Identificar urgência/prazo para investir.
7. Consultar oportunidades compatíveis.
8. Apresentar alternativas com informações relevantes de retorno.
9. Confirmar interesse em reunião.
10. Encaminhar para especialista.
11. Atualizar score/classificação.
12. Gerar resumo para o especialista.

**Sequência resumida:**  
Intenção → Ticket → Região → Perfil → Retorno esperado → Urgência → Oportunidades → Reunião → Resumo.

## 4. Fluxo de Follow-up
1. Identificar lead sem resposta ou com conversa interrompida.
2. Recuperar contexto da última interação.
3. Evitar repetir perguntas já respondidas.
4. Retomar a conversa de forma cordial e objetiva.
5. Perguntar apenas a próxima informação necessária.
6. Atualizar data e quantidade de follow-ups.
7. Se o lead responder, continuar do ponto em que parou.
8. Se houver avanço, atualizar score/classificação.
9. Se houver interesse, encaminhar para visita, reunião ou corretor.

## 5. Fluxo de Agendamento
1. Confirmar que o lead aceitou visita ou reunião.
2. Identificar tipo de compromisso:
   - visita ao imóvel;
   - reunião com corretor;
   - reunião com especialista de investimento.
3. Registrar lead, imóvel quando aplicável, data, horário e responsável.
4. Confirmar o agendamento ao lead.
5. Atualizar status do lead.
6. Disponibilizar a informação para dashboard e resumo comercial.

## 6. Encaminhamento Comercial
O agente deve encaminhar o lead quando houver:
- interesse claro e dados suficientes para atendimento comercial;
- aceite de visita/reunião;
- lead classificado como quente;
- necessidade de especialista;
- situação fora do escopo do agente.

## 7. Tratamento de Exceções
### Nenhum imóvel encontrado
- Não inventar opções.
- Informar que não foram encontrados imóveis totalmente compatíveis.
- Perguntar se o lead aceita ampliar região, orçamento ou características.

### Informação alterada durante a conversa
- Considerar sempre a informação mais recente.
- Atualizar o contexto e refazer a busca quando necessário.

### Informação ausente
- Perguntar apenas o próximo dado necessário.
- Não preencher informações por suposição.

### Lead não responde
- Registrar a interrupção.
- Programar follow-up.
- Retomar mantendo o contexto anterior.
