# Agente SDR Imobiliário — POSTECH Fase 5

POC acadêmica de atendimento imobiliário com IA generativa: identificar compra, aluguel ou investimento, coletar preferências, qualificar leads, consultar imóveis, retomar conversas, apoiar agendamentos e entregar resumos ao corretor.

## Estado atual

Em 27/09/2026, foram corrigidas omissões de bairro/orçamento no aluguel e adicionada proteção da memória durante atualizações. A suíte passou com 17 testes, incluindo aluguel completo, resposta curta de bairro e compra com Qwen real. Veja a [regressão de aluguel](docs/testes/regressao_aluguel.md).

Atualização de validação: após corrigir a extração de orçamento composto e a resposta curta de urgência, passaram 13 testes, incluindo uma conversa completa com Qwen real. Veja a [evidência de regressão](docs/testes/regressao_orcamento.md). Isso substitui a indicação anterior de ausência de teste real para esse cenário específico; a avaliação dos demais cenários continua pendente.

Em 26/09/2026, foi implementada a primeira versão do núcleo de Karim: cliente Ollama, extração estruturada, validação, memória por conversa, próximos campos, resumo e demonstração por terminal com consulta aos CSVs. Os 11 testes automatizados passaram com modelo simulado; o Qwen real ainda precisa de avaliação funcional. Dashboard, persistência, scoring oficial, agendamento e follow-up automático continuam pendentes.

## Por onde começar

1. [Situação das entregas e pendências](docs/organizacao/status_projeto.md).
2. [Passo a passo do Karim](docs/organizacao/plano_karim.md).
3. [Fluxos funcionais](docs/funcional/fluxos_funcionais.md) e [regras da conversa](docs/funcional/regras_conversacionais.md).
4. [Documentação dos dados](docs/dados/documentacao_dados.md).
5. [Especificação do dashboard](docs/dashboard/especificacao_dashboard.md).
6. [Enunciado oficial](docs/desafio/enunciado_fase_5.pdf).
7. [Definições técnicas e contrato para Michele](docs/organizacao/definicoes_tecnicas.md).

## Organização

```text
data/                      CSVs para consumo pela aplicação
docs/
  desafio/                 Enunciado oficial
  funcional/               Fluxos e regras de Wellington
  dados/                   Documentação e XLSX consolidado de Rúben
  dashboard/               Especificação e indicadores de Rúben
  organizacao/             Diagnóstico, plano de trabalho e inventário
```

Os 14 arquivos recebidos foram preservados sem alterar seu conteúdo, incluindo a [planilha dos 20 testes de Wellington](docs/testes/casos_de_teste_iniciais.xlsx), recebida posteriormente. O [inventário](docs/organizacao/arquivos_recebidos.json) registra origens, destinos e hashes SHA-256. Os dois PDFs eram idênticos; a segunda cópia está em `recebidos_duplicados/`, ignorada pelo Git.

## Dados disponíveis

| Base | Registros | Finalidade |
| --- | ---: | --- |
| `data/imoveis.csv` | 500 | Catálogo, com 452 imóveis disponíveis |
| `data/leads.csv` | 600 | Perfil, score, classificação e acompanhamento |
| `data/agendamentos.csv` | 183 | Exemplos de visitas e reuniões |
| `data/interacoes.csv` | 2.088 | Histórico sintético resumido |
| `data/regras_qualificacao.csv` | 18 | Critérios e faixas de qualificação |

CSV em UTF-8 com BOM, separado por `;`. Campos vazios representam informação ausente. A base usa `Venda` para imóveis e `Compra` para intenção do lead. Os XLSX são materiais de conferência; os CSVs serão a entrada da aplicação. Preservar os dados sintéticos e utilizar `runtime/` para cópias alteradas nas demonstrações.

## Responsabilidades

| Pessoa | Responsabilidade |
| --- | --- |
| Wellington | Fluxos, regras, testes, LGPD, arquitetura documental, README e pitch |
| Rúben | Bases, regras e implementação de scoring, dashboard e registro de agendamentos |
| Karim | `agent.py`, `prompts.py`, integração com LLM, intenção, extração, memória e resumo |
| Michele | `app.py`, interface, busca, persistência e integração dos módulos, follow-up e entrega final |

Rúben implementa o dashboard; Michele integra e valida a arquitetura. Essa divisão segue a distribuição informada pelo grupo e deve orientar a integração, mesmo que a especificação do dashboard também mencione Michele como possível implementadora.

## Execução e entrega

O núcleo usa Python 3.10 ou superior e somente a biblioteca padrão, sem instalação de pacotes Python. O modelo inicial configurável é `qwen2.5:3b`; ainda precisa de avaliação no hardware de execução.

Qwen 2.5 3B já está instalado no Ollama desta máquina. Em outra máquina, baixar o modelo uma vez:

```powershell
ollama pull qwen2.5:3b
```

Com Ollama em execução, abrir o terminal na raiz do projeto:

```powershell
$env:OLLAMA_MODEL = "qwen2.5:3b"
python chat_cli.py
```

Se a instalação do Windows disponibilizar apenas o lançador `py`, usar `py -3 chat_cli.py`. `.env.example` é referência; o programa lê variáveis do ambiente, não carrega `.env` automaticamente. Não é necessária chave de API para o Ollama local.

Experimente: “Quero comprar um apartamento em Moema até 900 mil”, responda sobre quartos e urgência, e depois diga “Meu limite agora é 750 mil”. `/resumo` mostra o perfil e `/sair` encerra. A memória do terminal termina ao fechar o processo.

Para executar os testes:

```powershell
python -m unittest discover -s tests -v
```

Leia o [guia de integração da primeira versão](docs/organizacao/integracao_v1.md). O adaptador de catálogo demonstra busca local por bairro exato (ignorando acentos), preço máximo, mínimo de quartos e preferências positivas. Não interpreta endereços livres ou proximidade geográfica.

O Qwen extrai os dados; nesta primeira versão as perguntas e o resumo são montados pelo código para manter fidelidade ao estado. A naturalidade e a extração precisam ser avaliadas com o modelo real. Não há confirmação ou registro de agendamento nesta versão.

A pasta ainda não é um repositório Git. Para aproveitar o histórico do grupo, incorporar esta estrutura ao clone do repositório compartilhado. Se este for o início oficial do projeto, inicializar o Git aqui e configurar o remoto correto. Nenhum commit ou envio foi realizado nesta organização.

Mensagem sugerida para o primeiro commit desses materiais: `docs: organiza bases e especificacoes iniciais do SDR imobiliario`.

A entrega final deverá incluir repositório, README com instruções reais, arquitetura, demonstração funcional, pitch técnico e explicação da IA utilizada, conforme o enunciado.
