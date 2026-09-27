# Regressão: aumento de orçamento com Qwen real

Modelo: `qwen2.5:3b`, via Ollama local. Cenário reportado por Karim.

## Falha reproduzida

Com perfil Compra, apartamento, Moema, R$ 900.000, 3 quartos e urgência Média, a extração de “Posso aumentar meu orçamento para 1 milhão e 100 mil” retornou orçamento 1000000 em vez de 1100000. Também produziu esclarecimento indevido sobre retorno anual. Não foi inspecionado o estado da sessão original do usuário; esta é a reprodução local da falha.

## Correções

- Prompt com valores monetários compostos e exemplos de extração completa.
- Mensagem atual separada do contexto e histórico em mensagens próprias.
- Esclarecimento restrito à ambiguidade da mensagem atual; perguntas de investimento restritas ao fluxo correspondente.
- Resposta literal à pergunta fechada de urgência é reconhecida pelo código, evitando omissão de “Média” pelo modelo observada durante a regressão.

## Validação executada

13 testes passaram, incluindo 12 testes isolados e 1 teste de conversa completa com Qwen real (`tests/test_ollama_live.py`). O teste real percorre:

1. “Quero comprar um apartamento em Moema”.
2. “900 mil”.
3. “3”.
4. “Média”.
5. “Posso aumentar meu orçamento para 1 milhão e 100 mil”.

Asserções finais: orçamento 1100000, bairro Moema, 3 quartos, urgência Média, ação apresentar_imoveis e imóvel IMV0371 presente. Antes do aumento, nenhuma opção encontrada. O catálogo trata quartos como quantidade mínima.

Para repetir, com Python e Ollama configurados:

```powershell
$env:RUN_OLLAMA_TESTS = "1"
python -m unittest discover -s tests -v
```

Sem a variável, o teste de Ollama é ignorado. Esta execução não representa aprovação dos 20 casos de Wellington nem garante todas as variações de linguagem.

Reiniciar `chat_cli.py` para carregar o código corrigido. O CLI não persiste a sessão anterior.
