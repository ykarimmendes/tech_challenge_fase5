# Correção da extração de aluguel — 27/09/2026

Resultado: 17 testes aprovados em 38,724 segundos, incluindo 3 métodos de teste com Qwen real (aluguel e sua variação, conversa de compra e resposta curta de bairro). Os demais 14 verificam a lógica isoladamente. Isso não equivale à aprovação dos 20 casos completos de Wellington.

Falha reproduzida com Qwen 2.5 3B: a mensagem de aluguel completo retornava intenção, tipo, mobília, quartos e urgência, mas omitia orçamento e bairro. O agente repetia perguntas já respondidas.

O schema enviado ao modelo passou a exigir avaliação de todos os campos. Na resposta completa, null significa não mencionado e é descartado antes de atualizar o estado. O marcador interno `__REMOVER__` representa remoção explícita e é convertido em null. O agente exige também linguagem de remoção na mensagem para aceitar exclusões; simples mudanças de orçamento não devem apagar preferências. Essa proteção usa reconhecimento textual conservador e não cobre todas as formas possíveis de pedir remoção.

O contrato externo da aplicação permanece igual. Extratores simulados podem fornecer atualizações parciais; o transporte real do Ollama usa o objeto completo exigido pelo schema.

Casos adicionados em `tests/test_ollama_live.py`: frase de aluguel enviada por Karim, uma variação com outro bairro/valor/quartos/urgência e resposta curta “Tatuapé” preservando o perfil anterior. A regressão de compra com orçamento composto também é executada.

Para repetir a suíte real:

```powershell
$env:RUN_OLLAMA_TESTS = "1"
python -m unittest discover -s tests -v
```

Reiniciar o chat após alterações para carregar o código novo. A memória do terminal não sobrevive ao reinício. A extração correta pode resultar em ausência de imóveis: esse resultado não é falha de extração se os sete campos estiverem corretos e não houver perguntas repetidas.
