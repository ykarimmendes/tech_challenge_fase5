# Diagnóstico das entregas — 26/09/2026

> Decisão atual: Karim escolheu Qwen 2.5 3B (`qwen2.5:3b`) via Ollama local, já instalado. Essa decisão substitui as referências anteriores a Llama neste documento.

Recebimento posterior: a planilha dos 20 testes de Wellington foi adicionada em `docs/testes/casos_de_teste_iniciais.xlsx`. Todos estão “Não executado”. Veja a [leitura dos cenários](../testes/leitura_inicial.md). O Ollama está ativo, mas só contém Qwen 2.5 3B; o Llama configurado ainda não foi baixado. As referências abaixo a planilha não recebida descrevem o inventário original e estão superadas por esta atualização.

Atualização: após o inventário abaixo, foi implementada a primeira versão do núcleo de Karim, com 11 testes aprovados usando modelo simulado. Veja [integração v1](integracao_v1.md). A avaliação com Llama real permanece pendente. As tabelas abaixo registram o material recebido antes desse desenvolvimento.

## O que foi conferido

Diagnóstico restrito aos arquivos desta pasta e à divisão de responsabilidades informada por Karim. “Não recebido” não significa que a pessoa não tenha feito o trabalho em outro local.

| Responsável | Evidência recebida | O que ainda falta nesta pasta |
| --- | --- | --- |
| Wellington | Fluxos funcionais e 18 regras conversacionais em Markdown | `casos_de_teste.xlsx` com os 20 casos mencionados, checklist LGPD, desenho de arquitetura, roteiro do pitch e resultados de testes |
| Rúben | Cinco CSVs, XLSX consolidado, documentação dos dados, especificação do dashboard e XLSX de indicadores | `lead_scoring.py`, `dashboard.py` e implementação do registro de agendamentos |
| Karim | Requisitos e dados suficientes para iniciar o núcleo | `agent.py`, `prompts.py`, integração com LLM, extração, memória e resumo |
| Michele | Responsabilidades descritas na mensagem do grupo | `app.py`, interface, pesquisa de imóveis, persistência, follow-up, integração e demonstração |

O README da raiz e este diagnóstico foram produzidos na organização atual. Não representam uma entrega anterior de Wellington. Nenhum código funcional foi criado nesta etapa.

## O que o sistema precisa fazer

1. A interface recebe uma mensagem e identifica o lead e sua conversa.
2. O núcleo de Karim recupera o contexto, reconhece a intenção e extrai informações declaradas.
3. O agente pergunta o próximo dado necessário, uma pergunta principal por vez.
4. O módulo de Rúben calcula score e classificação com regras explícitas.
5. A busca integrada por Michele filtra imóveis reais e disponíveis na base.
6. O agente apresenta opções retornadas pela busca ou propõe flexibilizar critérios.
7. O registro de agendamento confirma os dados e persiste o compromisso antes de anunciar sucesso.
8. A aplicação salva o histórico, suporta retomada e follow-up e atualiza o dashboard.
9. Karim gera o resumo comercial com os dados confirmados para corretor ou especialista.

Essa sequência descreve a arquitetura funcional pretendida, ainda não implementada.

## Verificações dos dados

Contagens recalculadas diretamente nos CSVs:

| Indicador | Resultado |
| --- | ---: |
| Imóveis / disponíveis | 500 / 452 |
| Leads | 600 |
| Quentes / Mornos / Frios | 331 / 220 / 49 |
| Compra / Aluguel / Investimento / intenção vazia | 274 / 172 / 111 / 43 |
| Score médio | 67,57 (67,6 arredondado) |
| Agendamentos | 183 |
| Interações | 2.088 |
| Leads com quantidade de follow-ups maior que zero | 311 |
| Soma de follow-ups | 804 |
| Campo respondeu_followup igual a Sim | 175 |

Os principais totais conferem com o material de indicadores. Não foram encontrados IDs duplicados nas quatro bases de entidades, referências inválidas de leads em agendamentos/interações ou referências inválidas de imóveis preenchidos em agendamentos. Todos os 183 leads com aceite possuem agendamento. Nenhum investidor Quente está sem perfil ou retorno esperado.

O recálculo dos scores dos **557 leads com intenção definida** coincidiu com a base, usando orçamento, bairro, campos específicos, urgência e aceite conforme a documentação. A regra para os **43 leads sem intenção** não está documentada: extrapolar a regra de compra/aluguel não reproduz seus scores. Preservar os valores recebidos e pedir a Rúben a fórmula desse caso antes de implementar o recálculo geral.

Estas verificações cobrem contagens, vínculos e os cálculos descritos. Não demonstram que cada agendamento corresponde às preferências do lead, que os dados simulam conversas reais completas ou que a aplicação funciona. Os XLSX foram lidos para conferência de conteúdo; não foram editados nem revalidados visualmente.

## Pontos de integração a resolver

- **Intenção desconhecida:** Rúben deve especificar a pontuação. Karim deve perguntar a intenção sem presumir compra.
- **Urgência:** existem Alta/Média/Baixa, mas faltam limites para transformar “em 30 dias” nessas categorias. Wellington e Rúben devem definir essa conversão.
- **Região de investimento:** o fluxo diz “quando houver”, enquanto o score concede pontos quando preenchida. Confirmar se sua ausência impede busca; não bloquear por uma regra inventada.
- **Troca de intenção:** definir quais campos devem ser reconfirmados. Um orçamento de compra não pode virar automaticamente orçamento mensal de aluguel.
- **Retorno esperado:** confirmar a unidade com o usuário. O catálogo contém yield anual; não comparar uma taxa mensal com uma anual sem conversão explícita.
- **Memória:** `interacoes.csv` contém mensagens resumidas; não substitui sozinho um histórico completo com papéis e sessão. A aplicação precisará persistir as novas mensagens.
- **Follow-up:** faltam prazo, quantidade máxima de tentativas, condição de parada e mecanismo de disparo automático. Michele implementa; Wellington define comportamento; Karim redige a retomada contextual.
- **Agendamento:** definir confirmação, disponibilidade, responsável e prevenção de duplicidade. Dizer “sim” a uma visita não define data e horário.
- **Tecnologia (atualização):** Karim escolheu Llama, com execução local via Ollama. Python, contrato do agente e proposta de persistência foram registrados em [definições técnicas](definicoes_tecnicas.md) para repasse à Michele. A versão do modelo ainda depende de avaliação do hardware; a interface ainda não foi implementada.

## Ordem das próximas entregas

1. Wellington fornece a planilha de testes; Rúben esclarece scoring sem intenção e as ambiguidades de dados.
2. Karim define e entrega à Michele o contrato de entrada e saída do agente. Karim já pode iniciar prompts e estado da conversa com os campos existentes.
3. Karim entrega o núcleo demonstrável; Rúben entrega scoring; Michele conecta interface, busca e armazenamento.
4. Rúben completa dashboard e agendamentos; Michele implementa o disparo de follow-up e integra os módulos.
5. Wellington executa os 20 cenários, registra resultados e completa documentação/LGPD/pitch.
6. Michele consolida demonstração e vídeo, com instruções de execução reproduzíveis.

## Critério de conclusão

A POC precisa demonstrar compra, aluguel e investimento; perguntas sem repetição; atualização de preferências; busca sem imóveis inventados; continuidade; qualificação; follow-up automático; agendamento persistido; resumo e dashboard.

RAG, WhatsApp, multiagentes, voz, CRM e cloud aparecem como diferenciais no enunciado. Priorizar primeiro o fluxo obrigatório completo. A planilha que marca campos de dados como “Atendido” comprova preparação dos dados, não implementação desses requisitos.
