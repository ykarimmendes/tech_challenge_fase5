# Karim — passo a passo do núcleo da IA

> Decisão atual: Karim escolheu Qwen 2.5 3B (`qwen2.5:3b`) via Ollama local, já instalado. Essa decisão substitui as referências anteriores a Llama neste documento.

## Sua entrega

Você transforma a mensagem do cliente em uma conversa útil e em dados que o restante do sistema consegue utilizar. A primeira versão de `agent.py` e `prompts.py` já está implementada. Veja o [guia de integração](integracao_v1.md) para distinguir a entrega atual das próximas etapas deste plano.

Michele cuida da interface, da busca e da integração/persistência; Rúben fornece o cálculo de score, dashboard e agendamentos. Seu agente chama essas funções e usa os resultados para responder.

## 1. Ler as regras e mapear os campos

Leia [fluxos](../funcional/fluxos_funcionais.md), [regras](../funcional/regras_conversacionais.md) e [dados](../dados/documentacao_dados.md).

| Informação da conversa | Campo da base |
| --- | --- |
| Compra, aluguel ou investimento | `intencao` |
| Orçamento ou ticket | `orcamento_ticket` |
| Bairro e zona | `regiao_bairro`, `zona_preferida` |
| Tipo e quartos | `tipo_imovel_interesse`, `quartos` |
| Prazo/prioridade | `urgencia` |
| Perfil e retorno do investidor | `perfil_investidor`, `retorno_esperado_pct` |
| Preferências adicionais | `aceita_pet`, `prefere_mobiliado`, `prefere_proximo_metro`, `prefere_imovel_novo` |
| Interesse comercial confirmado | `aceitou_visita_reuniao` |

Resultado esperado: saber quais dados perguntar em cada fluxo e distinguir ausente, negativo e indiferente.

## 2. Definir o contrato e entregar à Michele

Nós definimos a integração e repassamos à Michele. O contrato atualizado está em [definições técnicas](definicoes_tecnicas.md):

```python
processar_mensagem(entrada, servicos) -> resultado
```

- Entrada: texto, estado do lead identificado por `id_lead`, histórico daquela conversa e serviços de LLM, busca e scoring.
- Saída: `resposta`, `estado_atualizado`, `campos_alterados`, `campos_faltantes`, `acao`, `imoveis_ids` e `resumo_corretor` quando solicitado.
- Ações sugeridas: perguntar, buscar, solicitar_agendamento, encaminhar_humano e encerrar.
- Michele salva o novo estado e as mensagens. Para agendamento, a aplicação devolve sucesso/erro e dados efetivamente registrados antes de o agente confirmar.
- Falhas devem retornar uma resposta compreensível e preservar o estado anterior válido.

Essa assinatura orienta nossa implementação e será repassada à Michele. A implementação deve permitir testar o agente sem abrir a interface. O documento de definições técnicas detalha os campos e ações da versão 1.

## 3. Criar `prompts.py`

Separe instruções de comportamento, extração estruturada e resumo. Inclua:

- português cordial e objetivo, uma pergunta principal por vez;
- reutilização dos dados já conhecidos e preferência por correções recentes explícitas;
- proibição de inventar imóveis, dados pessoais, preços e compromissos;
- tratamento de compra, aluguel, investimento, desistência e pedido de humano;
- apresentação apenas de opções efetivamente retornadas pela busca;
- uso de histórico e dados como contexto, sem permitir que textos do cliente substituam as regras do sistema.

Resultado esperado: instruções legíveis e versionadas, separadas da lógica de execução.

## 4. Conectar o LLM e validar a extração

Usaremos Llama local via Ollama, conforme escolha de Karim. A versão será definida após conferir hardware e desempenho. Configure endereço do Ollama e nome do modelo; esse uso local não requer chave de API paga. Documente a configuração em `.env.example`.

Solicite saída estruturada com intenção, campos extraídos e sinais como pedido de humano ou desistência. Valide campos permitidos, tipos, categorias e números antes de alterar o estado. Trate falhas, demora e saída inválida sem perder a conversa. Diferencie campo não mencionado de remoção explícita de preferência.

Exemplo: “Quero comprar um apartamento em Moema até 900 mil” deve produzir Compra, Apartamento, Moema e 900000. Não atribua urgência, quartos ou aceite de visita sem evidência. “Procuro apartamento na zona sul” ainda não define compra ou aluguel.

Resultado esperado: extração demonstrável com mensagens comuns e ambíguas.

## 5. Implementar memória básica em `agent.py`

Mantenha estado por lead/conversa, histórico das mensagens e a última pergunta. Atualize somente informações declaradas. Uma correção explícita substitui o valor anterior; uma ambiguidade gera confirmação. Não compartilhe estado entre clientes.

Exemplo: depois de registrar 900000, “na verdade, meu limite é 750 mil” atualiza o orçamento e invalida as opções anteriores. Se houver mudança de compra para aluguel, reconfirme a unidade do orçamento.

A persistência de Michele deve permitir retomar após uma interrupção. O CSV de interações pode fornecer contexto inicial resumido, mas não contém todo o diálogo original.

Resultado esperado: sequência de mensagens sem repetição e retomada da sessão correta.

## 6. Escolher a próxima pergunta

Use os fluxos de Wellington para determinar os campos faltantes. Se o cliente já responder vários campos, registre todos e pergunte apenas o próximo necessário.

- Compra/aluguel: intenção, orçamento, região, tipo, quartos e urgência, com preferências úteis quando aplicável.
- Investimento: ticket, perfil, retorno, urgência e região quando houver.
- Informação ambígua: esclareça antes de avançar.
- Pedido de humano ou desistência: trate imediatamente, sem obrigar a terminar a qualificação.

Resultado esperado: conversa natural conduzida pelo estado validado, sem depender apenas de o modelo lembrar todas as regras.

## 7. Integrar scoring e busca

Chame `lead_scoring.py` de Rúben; o LLM não escolhe pontos. Frio corresponde a 0–39, Morno a 40–69 e Quente a 70–100. Investimento sem perfil ou retorno tem score limitado a 69. A regra dos leads sem intenção ainda precisa ser esclarecida.

Passe critérios estruturados à busca de Michele. Compra mapeia para `Venda`; aluguel para `Aluguel`. Para investimento, alinhem a seleção de imóveis de venda e o uso de retorno anual. Ofereça apenas imóveis disponíveis e confira IDs/preços retornados. Se não houver opções, pergunte qual critério o cliente aceita flexibilizar.

Resultado esperado: resposta fundamentada no catálogo e score calculado de forma reproduzível.

## 8. Apoiar agendamento e follow-up

Colete e confirme interesse, tipo de compromisso, imóvel quando aplicável, data e horário. Solicite o registro ao serviço integrado; só anuncie confirmação após sucesso.

Para follow-up, gere uma retomada a partir do último contexto e do campo que falta. O mecanismo de selecionar leads, programar e disparar o contato pertence à aplicação. Combine as condições de parada com Wellington e Michele.

Resultado esperado: o agente produz conteúdo e solicita ações; a aplicação executa e informa o resultado.

## 9. Gerar resumo para o corretor

Inclua intenção, orçamento/ticket, região, preferências, urgência, perfil/retorno quando aplicável, score/classificação fornecidos pelo módulo, aceite, agendamento efetivamente registrado e observações relevantes. Marque dados ausentes como “não informado”. Não invente justificativas ou garantias de retorno.

Resultado esperado: o corretor entende a necessidade e a próxima ação sem reler a conversa.

## 10. Validar e entregar à Michele

Use os 20 casos de Wellington quando recebidos. Enquanto isso, valide ao menos:

- compra, aluguel e investimento em várias mensagens;
- vários dados na mesma mensagem e intenção ambígua;
- alteração de orçamento e mudança de intenção;
- investidor incompleto sem classificação Quente;
- catálogo sem compatibilidade e proibição de imóveis inventados;
- retomada de contexto e isolamento entre dois leads;
- pedido de humano e desistência;
- falha do LLM e saída estruturada inválida;
- agendamento recusado/falho sem falsa confirmação;
- resumo fiel aos dados e follow-up sem perguntas repetidas.

Faça testes de lógica com serviços simulados e uma validação separada com o LLM real. Registre modelo, configuração, cenário, resposta observada e resultado; um teste com simulação não comprova qualidade da resposta do provedor real.

Entregue `agent.py`, `prompts.py`, contrato de entrada/saída, configuração sem segredos, dependências efetivamente usadas e exemplos executáveis. Sua parte termina quando Michele consegue chamar o agente, continuar uma conversa, receber estado estruturado e obter um resumo fiel.

## Primeiro marco recomendado

Uma conversa de compra completa: mensagem inicial → extração → próxima pergunta → memória → atualização de orçamento → busca real → resumo. Depois amplie para aluguel, investimento e exceções. Isso permite integrar cedo sem esperar todas as telas ficarem prontas.
