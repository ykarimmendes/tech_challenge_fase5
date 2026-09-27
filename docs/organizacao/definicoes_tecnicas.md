# Definições do núcleo da IA

> Decisão atual: Karim escolheu Qwen 2.5 3B (`qwen2.5:3b`) via Ollama local, já instalado. Essa decisão substitui as referências anteriores a Llama neste documento.

Decisões de implementação de Karim para repasse à Michele. Llama foi escolhido por Karim. A [primeira versão](integracao_v1.md) já foi implementada. SQLite, agendamento e follow-up abaixo continuam como desenho alvo.

## Tecnologia e organização

- Linguagem: Python.
- Modelo: família Llama, executada localmente via Ollama. Versão/tamanho serão escolhidos após verificar o hardware e medir qualidade e tempo de resposta.
- A aplicação acessa o serviço local do Ollama. Não requer chave de um provedor pago para esse uso local.
- Configuração: `OLLAMA_BASE_URL` e `OLLAMA_MODEL`, com exemplo documentado. Não instalar ou baixar modelos nesta etapa de definições.
- `agent.py`: coordena extração, validação, atualização do estado e próxima ação.
- `prompts.py`: instruções de extração, conversa e resumo.
- `llm_client.py`: comunicação isolada com Ollama, limites de tempo e tratamento de falha.
- `schemas.py`: formatos e validação de entradas, estado e resultados.
- Integração por funções Python. Não criar um servidor web separado para o agente na primeira versão.

## Contrato versão 1

`processar_mensagem(entrada, servicos) -> resultado`

A entrada contém `id_lead`, `id_conversa`, `id_mensagem`, `mensagem`, `estado`, `historico` e `data_hora_atual` com fuso. A aplicação fornece os identificadores; a IA não os inventa. O histórico contém mensagens com papel e conteúdo. O horário é fornecido para interpretar datas relativas de forma reproduzível.

Os serviços fornecem a chamada ao modelo, a busca de imóveis e o cálculo de score. O núcleo pode ser testado com implementações simuladas desses serviços.

O resultado contém:

| Campo | Conteúdo |
| --- | --- |
| `resposta` | Texto para o cliente |
| `estado_atualizado` | Dados validados após a mensagem |
| `campos_alterados` | Campos modificados neste turno |
| `campos_faltantes` | Informações necessárias ainda ausentes |
| `acao` | `perguntar`, `apresentar_imoveis`, `solicitar_agendamento`, `encaminhar_humano`, `encerrar` ou `tentar_novamente` |
| `imoveis_ids` | IDs validados dos imóveis apresentados |
| `solicitacao_agendamento` | Dados confirmados para registro, ou nulo |
| `resumo_corretor` | Resumo quando necessário, ou nulo |
| `erro` | Código de falha controlada, ou nulo |

Michele persiste estado e histórico. A aplicação deve evitar processar duas vezes o mesmo `id_mensagem`. O agente solicita o agendamento; a aplicação executa o registro e devolve o resultado para uma etapa de confirmação. Antes de sucesso do registro, a resposta nunca afirma que o compromisso está agendado.

## Estado e memória

Usar os nomes dos campos de `leads.csv`. Campos desconhecidos são nulos. Ausência de menção mantém o valor existente; remoção explícita limpa o valor; correção explícita substitui o anterior. Valores ambíguos aguardam esclarecimento.

Além do perfil, guardar última pergunta, pendências de confirmação, intenção anterior quando alterada, imóveis apresentados e estado de encerramento/encaminhamento. Trocar compra por aluguel exige reconfirmar o orçamento. Novos filtros invalidam resultados de busca anteriores.

Proposta para persistência da POC integrada: SQLite em `runtime/`, administrado pela aplicação. CSVs de `data/` permanecem como massa inicial; não sobrescrever os originais. Memória em processo basta para os primeiros testes do núcleo, mas a retomada após reinício exige a persistência integrada. Não misturar conversas de leads diferentes.

## Divisão entre IA e código

O Llama interpreta linguagem e produz texto e extrações estruturadas. O código valida os campos, determina pendências, aplica regras e controla ações. Scoring pertence ao módulo de Rúben. A busca utiliza filtros sobre o catálogo e apresenta somente registros disponíveis. Não é necessário adicionar RAG vetorial ou multiagentes à primeira versão.

Compra usa imóveis de Venda; aluguel usa Aluguel. Investimento busca imóveis de Venda e utiliza retorno anual estimado, sem prometer rentabilidade. A região do investidor pode ficar sem preferência. Não converter retorno mensal para anual sem esclarecer a unidade e a hipótese de cálculo.

Pedido de humano e desistência interrompem a sequência de qualificação. Falha ou resposta inválida do modelo preserva o estado válido anterior e produz uma mensagem de tentativa posterior. O resumo usa dados confirmados e o score fornecido pelo serviço, com dados ausentes explicitados.

## Responsabilidades da integração

| Entrega | Responsável |
| --- | --- |
| Contrato do agente, prompts, extração, memória lógica, respostas e resumo | Karim |
| Interface, busca, persistência e integração do contrato | Michele |
| Fórmula e módulo de score, dashboard, registro de agendamento | Rúben |
| Regras de negócio e validação dos cenários | Wellington |
| Disparo automático de follow-up | Michele, com regras de Wellington e texto contextual do agente |

## Pendências delimitadas

1. Identificar RAM/GPU e escolher a versão do Llama. A consulta de hardware nesta sessão recebeu acesso negado; nenhum dimensionamento foi confirmado.
2. Rúben: fórmula para leads sem intenção. Até ser definida, não recalcular esses casos com uma fórmula inventada; novos leads ficam com qualificação pendente.
3. Wellington/Rúben: conversão de prazos para urgência Alta/Média/Baixa. Preservar prazo declarado sem inventar a categoria.
4. Wellington/Michele: prazos, limite de tentativas e condições de parada de follow-up. Encerramento explícito impede retomada automática.
5. Serviço de agendamento: horários disponíveis, responsável e resultado do registro. Sem essa integração não há confirmação de agenda real.

## Sequência de implementação

1. Schemas e contrato com exemplos.
2. Cliente Ollama e configuração de modelo local.
3. Prompts e extração validada.
4. Memória e conversa de compra.
5. Aluguel, investimento e exceções.
6. Integração de busca, score e resumo.
7. Solicitação de agendamento e geração de follow-up.
8. Testes com serviços simulados e avaliação separada com Llama real.

O primeiro marco é conversar por uma interface de teste simples, guardar dados e corrigir o orçamento sem perder contexto. A demonstração integrada acrescenta busca real, scoring e persistência.
