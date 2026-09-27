# Agente SDR Imobiliário — Núcleo de IA do Karim

Parte de Karim no projeto POSTECH Fase 5: identificação de intenção, extração de informações, memória básica da conversa, condução das perguntas e resumo para o corretor.

O modelo utilizado é **Qwen 2.5 3B**, executado localmente pelo **Ollama**. O Qwen interpreta as mensagens; o código Python valida os dados, atualiza o estado e decide a próxima ação. A demonstração usa o terminal e um adaptador de consulta ao catálogo de imóveis.

## 1. Pré-requisitos

- **Python 3.10 ou superior**. Python 3.11 é utilizado por Karim.
- **Ollama** instalado e em execução.
- Modelo **qwen2.5:3b** baixado no Ollama.
- Arquivos deste projeto, incluindo `data/imoveis.csv`.

Downloads oficiais: [Python](https://www.python.org/downloads/) e [Ollama](https://ollama.com/download).

Não é necessário instalar pacotes com `pip`: o núcleo e os testes usam somente a biblioteca padrão do Python. Não é necessária chave de API para executar o modelo localmente. O download inicial do modelo requer internet; o atendimento local utiliza o modelo já baixado. A velocidade depende dos recursos da máquina.

Os comandos abaixo são para **PowerShell no Windows**, executados na pasta do projeto.

## 2. Abrir a pasta e conferir o Python

Na máquina do Karim:

```powershell
Set-Location 'C:\yehia\dev\fiap\fase_5'
python --version
```

Em outro computador, substitua o caminho pela pasta em que o projeto foi salvo.

Se `python` não for reconhecido, tente:

```powershell
py -3 --version
```

Nos próximos comandos, use `py -3` no lugar de `python`, se necessário. Também é possível usar o executável completo. Na instalação do Karim:

```powershell
& 'C:\Users\karim\AppData\Local\Programs\Python\Python311\python.exe' --version
```

## 3. Preparar o Ollama e o Qwen

Abra o aplicativo Ollama. Confira os modelos instalados:

```powershell
ollama list
```

Se `qwen2.5:3b` não aparecer, baixe o modelo:

```powershell
ollama pull qwen2.5:3b
```

Na máquina do Karim, esse modelo já foi instalado. Não é necessário baixá-lo novamente para cada execução.

Para conferir se o serviço está respondendo:

```powershell
Invoke-RestMethod -Uri 'http://localhost:11434/api/tags'
```

Se o aplicativo não tiver iniciado o serviço, execute em **outro terminal**:

```powershell
ollama serve
```

Deixe esse terminal aberto. Se a porta já estiver ocupada pelo Ollama, utilize a instância existente.

## 4. Executar o chat

Configure explicitamente o modelo e o endereço na sessão do PowerShell:

```powershell
$env:OLLAMA_MODEL = 'qwen2.5:3b'
$env:OLLAMA_BASE_URL = 'http://localhost:11434'
python chat_cli.py
```

Esses já são os valores padrão do código. Defini-los explicitamente evita utilizar configurações antigas da sessão.

Alternativa com o Python instalado na máquina do Karim:

```powershell
& 'C:\Users\karim\AppData\Local\Programs\Python\Python311\python.exe' .\chat_cli.py
```

A tela inicial deve mostrar:

```text
SDR Imobiliário — modelo qwen2.5:3b. /sair encerra. /resumo mostra os dados.
Você:
```

O arquivo `.env.example` serve como referência. **O código não carrega arquivos `.env` automaticamente**; copiar ou editar esse arquivo não altera as variáveis da sessão.

## 5. Fazer uma primeira conversa

Digite uma mensagem por vez:

```text
Quero comprar uma casa em Moema, até 3 milhões, com 2 quartos. Minha urgência é baixa.
Na verdade o orçamento é 2 milhões e meio.
/resumo
```

Confira se o resumo mostra Compra, Casa, Moema, orçamento 2500000, 2 quartos e urgência Baixa. A alteração de orçamento deve preservar os demais dados.

Outros exemplos para testar em conversas novas:

**Aluguel:**

```text
Quero alugar um apartamento mobiliado no Tatuapé, até 4 mil por mês, com 2 quartos. Minha urgência é alta.
/resumo
```

Esperado: Aluguel, Apartamento, Tatuapé, orçamento 4000, 2 quartos, mobiliado Sim e urgência Alta.

**Investimento:**

```text
Quero investir 800 mil em imóveis. Meu perfil é moderado, espero retorno de 6% ao ano e minha urgência é média.
/resumo
```

Esperado: Investimento, ticket 800000, perfil Moderado, retorno esperado 6 e urgência Média.

O resultado depende da interpretação do modelo. Conferir os campos no resumo é parte da validação. Ausência de imóveis compatíveis não significa, por si só, falha de extração.

### Comandos durante o atendimento

| Comando | Resultado |
| --- | --- |
| `/resumo` | Exibe o perfil coletado, situação e qualificação disponível |
| `/sair` | Encerra o programa |
| `Ctrl+C` | Interrompe o atendimento |

Para uma conversa nova, saia e execute o programa novamente. **A memória fica apenas durante a execução**: fechar ou reiniciar o chat apaga o estado daquela sessão. Após alterar o código, reinicie para carregar as mudanças.

## 6. Executar os testes

### Testes isolados, sem depender do Ollama

```powershell
Remove-Item Env:RUN_OLLAMA_TESTS -ErrorAction SilentlyContinue
python -m unittest discover -s tests -v
```

Os testes com IA real aparecem como ignorados (`skipped`). Isso é esperado nesse modo.

### Testes com o Qwen real

Com Ollama ativo e modelo baixado:

```powershell
$env:OLLAMA_MODEL = 'qwen2.5:3b'
$env:OLLAMA_BASE_URL = 'http://localhost:11434'
$env:RUN_OLLAMA_TESTS = '1'
python -m unittest discover -s tests -v
```

Depois, para voltar ao modo sem IA real:

```powershell
Remove-Item Env:RUN_OLLAMA_TESTS -ErrorAction SilentlyContinue
```

A última execução registrada aprovou **17 testes**, sendo 14 isolados e 3 métodos com Qwen real. A suíte real inclui aluguel e uma variação, resposta curta de bairro e compra com alteração de orçamento. Os tempos podem variar por máquina.

Evidências: [regressão de aluguel](docs/testes/regressao_aluguel.md) e [regressão de orçamento](docs/testes/regressao_orcamento.md). Esses testes não equivalem à aprovação de todos os 20 casos integrados de Wellington.

## 7. Arquivos da implementação

| Arquivo | Responsabilidade |
| --- | --- |
| `agent.py` | Orquestra o atendimento pela função `processar_mensagem(entrada, servicos)` |
| `prompts.py` | Define instruções e prepara mensagens para extração pela IA |
| `llm_client.py` | Conecta ao Qwen pela API local do Ollama |
| `schemas.py` | Define o formato dos dados e valida entradas e extrações |
| `chat_cli.py` | Interface de demonstração no terminal e memória durante a sessão |
| `catalogo.py` | Adaptador de leitura e filtro de imóveis para demonstração |
| `data/imoveis.csv` | Catálogo sintético consultado pela demonstração |
| `tests/test_agent.py` | Testes da lógica com serviços simulados |
| `tests/test_ollama_live.py` | Testes opcionais com o modelo real |
| `.env.example` | Referência das variáveis de configuração |

O catálogo utiliza CSV UTF-8 com BOM, separado por ponto e vírgula. Filtra por tipo, negócio, localização, orçamento e preferências. Quartos são tratados como **quantidade mínima**; apresenta até três opções em ordem crescente de preço. A urgência não altera essa ordenação. A aplicação de demonstração não modifica os CSVs.

## 8. Entrega para Michele

O ponto de integração é:

```python
resultado = processar_mensagem(entrada, servicos)
```

A aplicação envia identificadores, mensagem, estado anterior, histórico e data/hora com fuso. Recebe resposta, estado atualizado, campos alterados/faltantes, ação, imóveis apresentados e resumo. Ela deve guardar o estado devolvido e enviá-lo na próxima chamada.

Consulte o [exemplo completo de integração](docs/organizacao/integracao_v1.md).

### Limites desta entrega

- O Qwen interpreta as mensagens; perguntas e resumo são majoritariamente montados pelo Python.
- Score e classificação permanecem pendentes enquanto o serviço de Rúben não estiver conectado.
- Pedido de humano devolve uma ação para a aplicação; não envia contato a um corretor real.
- O núcleo não confirma nem registra agendamentos. O campo de solicitação está reservado.
- Interface final, armazenamento permanente, dashboard e disparo automático de follow-up pertencem à integração do projeto.

## 9. Problemas comuns

| Problema | Como verificar |
| --- | --- |
| `python` não reconhecido | Use `py -3` ou o caminho completo do executável |
| `ollama` não reconhecido | Confira a instalação e reabra o terminal após instalar |
| Não foi possível interpretar a mensagem | Confira o serviço, `ollama list` e o modelo configurado; a mensagem também pode indicar saída inválida da IA |
| A resposta demora | O primeiro uso pode carregar o modelo; o cliente tem limite padrão de 60 segundos por chamada |
| O modelo exibido não é Qwen | Defina `OLLAMA_MODEL=qwen2.5:3b` na sessão e reinicie o chat |
| Não encontrou imóveis | Confira `/resumo`; todos os filtros precisam corresponder a registros disponíveis |
| Alterações no código não aparecem | Encerre e execute novamente o programa |
| Conversa desapareceu após fechar | A versão de terminal não possui persistência |

## Materiais do grupo

- [Fluxos funcionais](docs/funcional/fluxos_funcionais.md) e [regras conversacionais](docs/funcional/regras_conversacionais.md).
- [Documentação das bases](docs/dados/documentacao_dados.md).
- [Casos de teste de Wellington](docs/testes/casos_de_teste_iniciais.xlsx).
- [Inventário dos arquivos recebidos](docs/organizacao/arquivos_recebidos.json).
- [Enunciado do desafio](docs/desafio/enunciado_fase_5.pdf).

Código, testes, bases sintéticas e documentação devem ser versionados. O `.gitignore` exclui ambientes locais, credenciais, caches, modelos e futuros dados de execução em `runtime/`.
