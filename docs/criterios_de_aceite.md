# Critérios de Aceite — Agente SDR Imobiliário

## Objetivo
Transformar os requisitos funcionais do desafio e os fluxos definidos pelo grupo em condições objetivas para validar a solução após a integração.

## Regra geral
Um item deve ser marcado como **Aprovado** somente quando houver evidência observável na aplicação, no log, no arquivo gerado ou no dashboard.

Status sugeridos:
- **Não executado**
- **Aprovado**
- **Reprovado**
- **Bloqueado**

---

## CA-01 — Atendimento conversacional
**Critério:** o usuário consegue iniciar e continuar uma conversa pela interface da POC.

**Aceite quando:**
- a mensagem do usuário é recebida;
- o agente responde de forma compreensível;
- o fluxo continua sem exigir manipulação manual de arquivos.

**Evidência:** print ou gravação da conversa.

## CA-02 — Identificação da intenção
**Critério:** o agente identifica Compra, Aluguel ou Investimento.

**Aceite quando:**
- uma intenção explícita é registrada corretamente;
- quando a intenção estiver indefinida, o agente solicita esclarecimento;
- o agente não assume intenção sem evidência suficiente.

**Evidência:** conversa + estado do lead.

## CA-03 — Qualificação para Compra
**Critério:** o agente coleta os principais dados do cenário de compra.

**Aceite quando coleta, conforme necessário:**
- orçamento;
- região;
- tipo de imóvel;
- quartos;
- urgência.

**Evidência:** conversa + registro atualizado.

## CA-04 — Qualificação para Aluguel
**Critério:** o agente conduz o fluxo de aluguel.

**Aceite quando coleta, conforme necessário:**
- orçamento mensal;
- região;
- tipo de imóvel;
- quartos;
- urgência;
- preferências adicionais quando aplicáveis.

**Evidência:** conversa + registro atualizado.

## CA-05 — Qualificação para Investimento
**Critério:** o agente conduz o cenário de investimento.

**Aceite quando coleta:**
- ticket;
- perfil do investidor;
- expectativa de retorno;
- região, quando aplicável;
- urgência/prazo.

**Evidência:** conversa + registro atualizado.

## CA-06 — Score e classificação
**Critério:** score e classificação são atualizados conforme os dados coletados.

**Aceite quando:**
- o score permanece de 0 a 100;
- a classificação segue Frio 0–39, Morno 40–69 e Quente 70–100;
- investidor sem perfil ou expectativa de retorno não fica classificado como Quente;
- mudanças de dados refletem na qualificação.

**Evidência:** lead antes/depois ou log da regra.

## CA-07 — Consulta à base de imóveis
**Critério:** o agente consulta somente a base simulada.

**Aceite quando:**
- opções apresentadas existem em `imoveis.csv`;
- critérios relevantes do lead são considerados;
- imóveis indisponíveis não são apresentados como disponíveis;
- nenhum imóvel é inventado.

**Evidência:** resposta do agente comparada à base.

## CA-08 — Nenhum imóvel compatível
**Critério:** o agente trata ausência de correspondência sem alucinação.

**Aceite quando:**
- informa que não encontrou opção compatível;
- não inventa imóvel;
- oferece ajuste razoável de critérios, quando aplicável.

**Evidência:** cenário específico de teste.

## CA-09 — Continuidade da conversa
**Critério:** o agente mantém contexto.

**Aceite quando:**
- não repete perguntas já respondidas;
- utiliza respostas anteriores;
- considera a informação mais recente quando o usuário altera uma preferência.

**Evidência:** conversa com mudança de orçamento/região.

## CA-10 — Follow-up
**Critério:** o sistema consegue retomar um lead sem resposta mantendo contexto.

**Aceite quando:**
- identifica que o lead precisa de retomada;
- mantém as informações já conhecidas;
- não reinicia a qualificação do zero;
- registra o follow-up.

**Evidência:** execução do cenário de follow-up + atualização dos dados.

## CA-11 — Agendamento
**Critério:** visita ou reunião pode ser registrada quando o lead aceitar.

**Aceite quando:**
- tipo do compromisso é definido;
- lead é associado corretamente;
- imóvel é associado quando aplicável;
- data/hora são registradas;
- o agente confirma o agendamento.

**Evidência:** conversa + registro em agendamentos.

## CA-12 — Encaminhamento comercial
**Critério:** o lead é encaminhado quando apropriado.

**Aceite quando:**
- comprador/locatário qualificado pode ser encaminhado para corretor;
- investidor pode ser direcionado para especialista;
- solicitação explícita de atendimento humano é respeitada.

**Evidência:** conversa e status/ação de encaminhamento.

## CA-13 — Resumo inteligente
**Critério:** o agente gera resumo útil para corretor/especialista.

**Aceite quando contém, quando disponíveis:**
- intenção;
- orçamento/ticket;
- região;
- preferências;
- urgência;
- score/classificação;
- interesse em visita/reunião;
- observações relevantes.

**Evidência:** resumo gerado.

## CA-14 — Dashboard mínimo
**Critério:** a aplicação apresenta acompanhamento dos leads.

**Aceite quando exibe pelo menos:**
- total de leads;
- distribuição por classificação;
- distribuição por intenção;
- agendamentos;
- visão de leads prioritários.

**Evidência:** print ou gravação do dashboard.

## CA-15 — Conversa natural e humanizada
**Critério:** o diálogo não se comporta como formulário rígido.

**Aceite quando:**
- respostas são coerentes com a mensagem anterior;
- o agente faz preferencialmente uma pergunta principal por vez;
- evita repetições;
- linguagem é clara e cordial.

**Evidência:** exemplos completos de conversa.

## CA-16 — Tratamento de alteração de preferência
**Critério:** novos dados substituem os anteriores quando o lead muda de ideia.

**Aceite quando:**
- orçamento, região ou outra preferência atualizada passa a ser utilizada;
- recomendação posterior utiliza a informação nova.

**Evidência:** cenário de teste com alteração.

## CA-17 — Privacidade e segurança básica
**Critério:** a demonstração não expõe informação inadequada.

**Aceite quando:**
- dados são sintéticos;
- credenciais não aparecem no repositório ou vídeo;
- `.env` não é versionado;
- históricos permanecem separados por lead.

**Evidência:** inspeção do repositório e execução.

## CA-18 — Tratamento de erro
**Critério:** falhas não encerram a POC de forma incompreensível.

**Aceite quando:**
- erro é tratado com mensagem adequada;
- aplicação não exibe segredo/credencial;
- quando possível, o usuário pode tentar novamente.

**Evidência:** teste controlado ou log.

---

## Critério de encerramento da validação
A validação funcional deverá ocorrer **após Karim concluir o comportamento do agente e Michele concluir a integração da aplicação**.

Antes da gravação do vídeo:
1. executar os casos de teste;
2. preencher Resultado obtido e Status;
3. corrigir itens críticos;
4. registrar evidências;
5. atualizar README;
6. selecionar os cenários que serão demonstrados.

Os diferenciais técnicos do desafio, como RAG, WhatsApp, multiagentes, Voice AI, CRM, observabilidade e cloud, só devem ser marcados como atendidos se estiverem realmente implementados.
