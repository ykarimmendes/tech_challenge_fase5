# Recebimento dos testes de Wellington

Planilha: [casos_de_teste_iniciais.xlsx](casos_de_teste_iniciais.xlsx). Cópia íntegra do arquivo recebido em Downloads, sem alterar células. São 20 casos: 14 Compra, 2 Aluguel, 3 Investimento e 1 intenção não definida. Todos possuem Status “Não executado” e Resultado obtido vazio. Esta leitura não é execução dos testes.

## Pontos para a execução

- CT-002: a frase inicial não explicita compra. Testar com intenção previamente definida no estado ou ajustar o esperado para perguntar a intenção; não deduzi-la do título da linha.
- CT-004 e CT-006: esperam busca sem urgência preenchida. O núcleo atual coleta urgência antes da busca final. Decidir se a busca preliminar deve acontecer antes de completar a qualificação.
- CT-007: “6%” não informa periodicidade. Confirmar anual/mensal antes de comparar com o yield anual do catálogo.
- CT-009, CT-010, CT-012 a CT-015, CT-018 e CT-020 descrevem sequências ou pré-condições. Preparar mensagens e estado inicial para reproduzi-los; não enviar a descrição do teste como se fosse fala literal do cliente.
- CT-011: a frase não explicita intenção, quartos ou urgência. Preparar o contexto de compra e decidir se a busca pode antecipar a conclusão da coleta.
- CT-012, CT-014 e CT-018 dependem de serviços ainda pendentes: agendamento, follow-up e scoring. CT-020 só estará completo quando houver esses resultados reais para resumir.
- CT-017: “Quero ver imóveis” também não define compra. A classificação de intenção desconhecida depende da regra ainda pendente de Rúben.

## Verificação do Ollama

O serviço local respondeu aos endpoints de versão e modelos. Apenas `qwen2.5:3b` estava instalado. A consulta de `llama3.2:3b` retornou HTTP 404 (modelo não encontrado). Não houve troca automática para Qwen nem teste de inferência com Llama. É necessário baixar o modelo definido antes de executar os testes reais do agente.
