# Integração da primeira versão

O núcleo está implementado. Os 11 testes passaram com modelo simulado; o Qwen 2.5 3B já está instalado e foi escolhido por Karim; sua qualidade ainda precisa ser avaliada. O cliente segue a documentação de [chat](https://docs.ollama.com/api/chat) e [saída estruturada](https://docs.ollama.com/capabilities/structured-outputs).

## Exemplo para Michele

```python
from datetime import datetime
from uuid import uuid4
from agent import Servicos, processar_mensagem
from catalogo import buscar_imoveis
from llm_client import OllamaClient

servicos = Servicos(OllamaClient(), buscar_imoveis=buscar_imoveis)
entrada = {
    'id_lead': 'L1', 'id_conversa': 'C1', 'id_mensagem': str(uuid4()),
    'mensagem': 'Quero comprar um apartamento em Moema até 900 mil',
    'estado': None, 'historico': [],
    'data_hora_atual': datetime.now().astimezone().isoformat(),
}
resultado = processar_mensagem(entrada, servicos)
print(resultado['resposta'])
```

Na próxima mensagem enviar `resultado['estado_atualizado']` como estado. Adicionar as mensagens e respostas ao histórico no formato `{'role': 'user' ou 'assistant', 'content': texto}`. A aplicação fornece os IDs, persiste os dados e evita duplicar `id_mensagem`. O núcleo não mantém estado global nem implementa deduplicação.

O perfil fica dentro de `estado['perfil']`; não passar uma linha CSV diretamente como estado. Para importar, usar `schemas.novo_estado`, converter números e transformar vazios em nulos. Os identificadores do estado devem corresponder ao lead/conversa da entrada.

## Serviços

- `llm.extrair(mensagens, schema)` retorna a extração estruturada.
- `buscar_imoveis(perfil)` retorna registros confiáveis e filtrados, com `id_imovel`, `disponivel`, `preco` numérico, `tipo_imovel`, `bairro` e `quartos`. `catalogo.py` é a implementação inicial para demonstração.
- `calcular_score(perfil)` retorna `{'score': inteiro, 'classificacao': texto}`. Sem esse serviço, a classificação permanece pendente. O módulo de Rúben deve ser conectado aqui.

Entrada inválida levanta `ValueError`. Falha de extração retorna `falha_extracao` e preserva o estado anterior. Falhas de busca/score preservam os dados coletados e devolvem código de erro. Os resultados contêm resposta, estado atualizado, campos alterados/faltantes, ação, IDs apresentados e resumo determinístico.

## Limites desta entrega

Perguntas e resumo são montados pelo código; Qwen interpreta a mensagem. Naturalidade e precisão precisam de testes com o modelo real. O terminal usa memória somente durante sua execução.

Agendamento, persistência SQLite, disparo de follow-up e scoring oficial continuam pendentes. `solicitacao_agendamento` está reservado e retorna nulo. Encaminhamento humano é uma ação solicitada à aplicação, não um contato efetivamente enviado.

Os testes cobrem coleta, correção, mudança de intenção, isolamento, saída inválida, falha de modelo, desistência/humano, investidor incompleto, ausência de opções, catálogo e formato da chamada Ollama. Não substituem os 20 testes funcionais de Wellington.
