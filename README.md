# Tech Challenge Fase 5 - Agente SDR Imobiliário com Inteligência Artificial

## 📌 Descrição do Projeto

Este projeto foi desenvolvido como parte do **Tech Challenge - Fase 5 da Pós Tech FIAP**.

O objetivo é construir uma Prova de Conceito (POC) de um **Agente SDR Imobiliário com Inteligência Artificial**, capaz de automatizar as primeiras etapas do atendimento comercial no setor imobiliário.

A solução simula um assistente comercial inteligente que conversa com potenciais clientes, identifica suas necessidades, coleta informações relevantes, qualifica leads, busca imóveis compatíveis, realiza follow-ups, registra agendamentos e gera informações estruturadas para apoio ao corretor.

O sistema foi projetado para atuar nos principais cenários imobiliários:

- compra de imóvel;
- aluguel;
- investimento imobiliário.

Além do atendimento conversacional, a aplicação possui memória persistente, dashboard comercial, classificação de leads e mecanismos de acompanhamento do relacionamento com o cliente.

> ⚠️ Este projeto possui finalidade acadêmica. Os dados utilizados são simulados e não representam uma operação imobiliária real.

---

## 👥 Integrantes e Responsabilidades

| **Integrante** | **Responsabilidade Principal** |
| -------------- | ------------------------------ |
| Karim          | Núcleo de IA, integração com LLM, prompts, definição do estado e contrato de entrada/saída do agente |
| Michele        | Interface em Streamlit, integração dos módulos, persistência em SQLite, follow-up, dashboard e consolidação da demonstração final |
| Wellington     | Fluxos funcionais, regras conversacionais, cenários de atendimento, testes e documentação funcional |
| Rúben          | Bases de dados, regras de qualificação, scoring, dashboard e apoio ao fluxo de agendamento |


## Arquitetura da Solução

A solução utiliza uma arquitetura modular, separando a interface, o núcleo do agente, a inteligência artificial, as regras de negócio, a persistência e o acompanhamento comercial.

![Arquitetura da Solução](docs/arquitetura_sdr.png)


### Visão geral

O fluxo da solução funciona da seguinte forma:

- o usuário interage com a aplicação por meio da interface desenvolvida em Streamlit;
- o Agente SDR controla o estado da conversa e as regras de negócio;
- o modelo Qwen2.5:3b, executado via Ollama, interpreta a linguagem natural;
- os dados extraídos passam por validações determinísticas antes de serem incorporados ao estado da conversa;
- o motor comercial executa scoring, qualificação, busca de imóveis, agendamento e follow-up;
- os dados são persistidos em SQLite;
- o dashboard apresenta os principais indicadores comerciais.

> **Princípio da solução:** o LLM interpreta; o código decide.

## 🎯 Objetivos

- Automatizar o atendimento inicial de leads imobiliários.
- Criar uma experiência de conversa natural e contextual.
- Identificar automaticamente a intenção do cliente.
- Coletar informações importantes para qualificação comercial.
- Diferenciar fluxos de compra, aluguel e investimento.
- Calcular score de qualificação do lead.
- Classificar leads como frio, morno ou quente.
- Consultar uma base simulada de imóveis.
- Recomendar imóveis compatíveis com o perfil informado.
- Permitir manifestação de interesse em imóveis.
- Registrar visitas e reuniões.
- Persistir conversas e estado do atendimento.
- Retomar conversas interrompidas.
- Realizar follow-ups de leads sem interação.
- Registrar resposta a follow-ups.
- Gerar resumo comercial para o corretor.
- Disponibilizar indicadores em um dashboard.
- Manter rastreabilidade das interações realizadas pela aplicação.

---

## 🧠 Contexto do Desafio

O desafio propõe um cenário no qual uma empresa do setor imobiliário deseja automatizar parte de sua operação comercial utilizando Inteligência Artificial.

Tradicionalmente, equipes comerciais recebem grande volume de leads provenientes de diferentes canais. Nem todos esses contatos possuem o mesmo nível de interesse ou maturidade para avançar no processo de compra, aluguel ou investimento.

Nesse contexto, um SDR — **Sales Development Representative** — atua na primeira etapa do relacionamento comercial, buscando compreender as necessidades do cliente e determinar se existe uma oportunidade qualificada para encaminhamento ao corretor.

A solução desenvolvida neste projeto automatiza parte desse processo.

O agente é responsável por:

- iniciar e conduzir a conversa;
- identificar o objetivo do cliente;
- coletar informações progressivamente;
- manter contexto entre mensagens;
- qualificar o lead;
- recomendar imóveis;
- apoiar o agendamento;
- realizar follow-up;
- preparar um resumo comercial antes do repasse ao corretor.

---

# 🏗️ Arquitetura Geral da Solução

A aplicação foi organizada de forma modular para separar interface, regras de negócio, IA, catálogo e persistência.

```text
Usuário / Lead
      ↓
Interface Streamlit
      ↓
     app.py
      ↓
Contrato de entrada do agente
      ↓
    agent.py
      ↓
┌─────────────────────────────┐
│ Extração de dados com LLM   │
│ prompts.py + llm_client.py  │
└─────────────────────────────┘
      ↓
Atualização do estado
      ↓
Qualificação / Scoring
      ↓
   scoring.py
      ↓
Perfil completo?
 ┌────┴─────┐
 │          │
Não        Sim
 │          │
Nova       Busca no catálogo
pergunta   catalogo.py
            ↓
      Imóveis compatíveis
            ↓
  Interesse / Agendamento
            ↓
Persistência em SQLite
      database.py
            ↓
Dashboard / Follow-up /
Resumo para o corretor
```

A aplicação também utiliza arquivos CSV como base simulada para imóveis, leads, interações, regras de qualificação e agendamentos históricos.

---

## Explicação da IA Utilizada

A solução utiliza o modelo **Qwen2.5:3b**, executado localmente por meio do **Ollama**, para interpretar as mensagens dos leads e extrair informações estruturadas a partir da linguagem natural.

Entre os dados identificados pelo modelo estão:

- intenção de compra, aluguel ou investimento;
- orçamento ou ticket;
- região ou bairro;
- tipo de imóvel;
- quantidade de quartos;
- urgência;
- perfil do investidor;
- retorno esperado;
- preferências relacionadas ao imóvel.

A extração é realizada de forma estruturada por meio de **Prompt Engineering + JSON Schema**, permitindo que as informações interpretadas pelo modelo sejam utilizadas pelas regras de negócio da aplicação.

### Arquitetura híbrida

A solução adota uma abordagem híbrida entre inteligência artificial e regras determinísticas.

O LLM é responsável por:

- compreender a linguagem natural;
- interpretar a intenção do usuário;
- extrair informações da conversa;
- considerar o contexto das mensagens anteriores.

O código Python é responsável por:

- validar os dados extraídos;
- controlar o estado da conversa;
- calcular o score;
- classificar o lead;
- buscar imóveis;
- realizar agendamentos;
- controlar follow-ups;
- persistir os dados no SQLite.

> **Princípio da solução:** o LLM interpreta; o código decide.

### Controle de alucinações

Para aumentar a confiabilidade da solução, as informações extraídas pelo modelo passam por validações determinísticas antes de serem adicionadas ao perfil do lead.

Dessa forma, o sistema evita aceitar automaticamente informações que não tenham sido efetivamente fornecidas pelo usuário.

### Memória e continuidade

O estado da conversa é armazenado pela aplicação e persistido em SQLite.

Isso permite que o agente mantenha informações já fornecidas pelo lead e retome conversas interrompidas sem solicitar novamente todos os dados.

### Fluxo da IA

```text
Mensagem do usuário
        ↓
Contexto da conversa
        ↓
Prompt
        ↓
Qwen2.5:3b / Ollama
        ↓
Extração estruturada em JSON
        ↓
Validação determinística
        ↓
Estado do lead
        ↓
Regras de negócio
        ↓
Resposta do agente

# 🔄 Fluxo Principal do Atendimento

O fluxo conversacional segue a lógica:

```text
Lead inicia a conversa
        ↓
Mensagem enviada ao agente
        ↓
LLM identifica intenção e entidades
        ↓
Estado da conversa é atualizado
        ↓
Verificação de campos faltantes
        ↓
Agente realiza nova pergunta
        ↓
Perfil torna-se suficientemente completo
        ↓
Score do lead é calculado
        ↓
Catálogo de imóveis é consultado
        ↓
Imóveis compatíveis são apresentados
        ↓
Cliente demonstra interesse
        ↓
Agendamento ou encaminhamento ao corretor
        ↓
Persistência do atendimento
        ↓
Follow-up quando necessário
        ↓
Resumo comercial para o corretor
```

---

# 💬 Módulo de Atendimento Conversacional

A interface principal foi desenvolvida em **Streamlit**.

O usuário pode conversar com o agente em linguagem natural.

Exemplo:

```text
Quero comprar um apartamento em Moema por até R$ 2 milhões.
```

A partir da mensagem, o agente pode identificar automaticamente:

```text
Intenção: Compra
Região: Moema
Tipo: Apartamento
Orçamento: R$ 2.000.000,00
```

Caso ainda existam dados necessários, o agente continua a conversa.

Exemplo:

```text
Quantos quartos você procura?
```

O atendimento não depende de um formulário rígido. As informações são extraídas progressivamente da conversa.

---

## 🧾 Contrato de Entrada do Agente

A integração entre interface e núcleo conversacional utiliza um contrato estruturado.

Exemplo:

```python
entrada = {
    "id_lead": "LED001",
    "id_conversa": "CONV001",
    "id_mensagem": "MSG001",
    "mensagem": "Quero comprar um apartamento em Moema",
    "estado": None,
    "historico": [],
    "data_hora_atual": "2026-09-27T10:00:00-03:00"
}
```

### Campos

| Campo | Descrição |
|---|---|
| `id_lead` | Identificador do potencial cliente |
| `id_conversa` | Identificador da conversa |
| `id_mensagem` | Identificador único da mensagem |
| `mensagem` | Texto enviado pelo usuário |
| `estado` | Estado atual da conversa |
| `historico` | Histórico anterior da conversa |
| `data_hora_atual` | Data e hora da interação |

Na primeira mensagem:

```python
"estado": None
```

Após o processamento do agente, o estado retornado é reutilizado nas mensagens seguintes.

Na interface Streamlit, os identificadores são gerados utilizando UUID.

---

# 🎯 Identificação de Intenção

O agente reconhece três intenções comerciais principais:

```text
Compra
Aluguel
Investimento
```

O tipo de intenção influencia quais informações serão solicitadas durante a conversa.

---

## 🏠 Fluxo de Compra

Entre os principais dados coletados estão:

- intenção;
- orçamento;
- região;
- tipo de imóvel;
- número de quartos;
- urgência.

Exemplo:

```text
Cliente:
Quero comprar um apartamento em Moema.

Agente:
Qual é o seu orçamento aproximado?

Cliente:
Até R$ 2 milhões.

Agente:
Quantos quartos você procura?
```

---

## 🔑 Fluxo de Aluguel

O fluxo de aluguel utiliza dados semelhantes ao de compra, porém a busca é realizada somente em imóveis disponíveis para locação.

Dados relevantes:

- orçamento;
- região;
- tipo de imóvel;
- quartos;
- urgência;
- preferências adicionais quando disponíveis.

---

## 📈 Fluxo de Investimento

O atendimento de investidores inclui informações específicas.

Entre elas:

- ticket disponível;
- perfil de investidor;
- expectativa de retorno;
- urgência;
- características do investimento.

Exemplo:

```text
Cliente:
Tenho R$ 1,5 milhão e quero investir em imóvel.

Agente:
Qual é o seu perfil de investimento?

Cliente:
Busco renda com aluguel e valorização.

Agente:
Qual retorno anual você espera?
```

---

# 🧠 Inteligência Artificial

O núcleo de IA utiliza um modelo executado localmente por meio do **Ollama**.

Modelo utilizado atualmente:

```text
qwen2.5:3b
```

A IA é utilizada principalmente para:

- interpretação de mensagens;
- extração estruturada das informações;
- identificação de intenção;
- interpretação de alterações no perfil;
- reconhecimento de eventos conversacionais;
- manutenção do contexto.

A aplicação utiliza saída estruturada para reduzir respostas inconsistentes e facilitar a integração com as regras de negócio.

---

## 🧩 Arquivos relacionados à IA

```text
agent.py
llm_client.py
prompts.py
schemas.py
```

### `agent.py`

Responsável pela lógica principal do agente.

Entre suas funções:

- processar mensagens;
- atualizar o estado;
- identificar campos faltantes;
- selecionar próxima pergunta;
- controlar mudança de intenção;
- chamar mecanismos externos de scoring e catálogo;
- gerar respostas comerciais.

### `llm_client.py`

Responsável pela comunicação com o Ollama.

Configura:

- endereço do servidor;
- modelo;
- timeout;
- chamadas à API;
- saída estruturada.

### `prompts.py`

Contém instruções utilizadas pela IA para:

- interpretação das mensagens;
- extração dos campos;
- tratamento de ambiguidades;
- remoção ou alteração de dados.

### `schemas.py`

Define os formatos esperados para:

- perfil;
- estado;
- dados extraídos;
- eventos conversacionais.

---

# 🔥 Qualificação de Leads

O agente calcula uma pontuação comercial conforme as informações coletadas.

O score varia entre:

```text
0 e 100
```

A classificação adotada é:

| Score | Classificação |
|---:|---|
| 0 a 39 | 🔵 Frio |
| 40 a 69 | 🟡 Morno |
| 70 a 100 | 🔥 Quente |

---

## Critérios para Compra e Aluguel

Entre os critérios considerados estão:

| Critério | Pontuação |
|---|---:|
| Intenção identificada | 10 |
| Orçamento informado | 20 |
| Região definida | 15 |
| Tipo de imóvel definido | 10 |
| Quantidade de quartos | 10 |
| Urgência alta | 15 |
| Urgência média | 10 |
| Urgência baixa | 5 |
| Aceitou visita ou reunião | 20 |

A pontuação máxima é limitada a 100.

---

## Critérios para Investimento

| Critério | Pontuação |
|---|---:|
| Intenção identificada | 10 |
| Ticket informado | 20 |
| Região definida | 10 |
| Perfil de investidor | 15 |
| Retorno esperado | 15 |
| Urgência alta | 10 |
| Urgência média | 7 |
| Urgência baixa | 3 |
| Aceitou reunião ou visita | 20 |

Caso informações essenciais de investimento ainda não tenham sido fornecidas, a pontuação pode ser limitada até a conclusão da qualificação.

---

## 📁 Arquivos relacionados

```text
scoring.py
data/regras_qualificacao.csv
```

---

# 🏘️ Catálogo e Recomendação de Imóveis

A base simulada de imóveis está armazenada em:

```text
data/imoveis.csv
```

O módulo responsável pela consulta é:

```text
catalogo.py
```

Os filtros podem considerar:

- finalidade;
- disponibilidade;
- orçamento;
- região;
- zona;
- tipo do imóvel;
- quantidade mínima de quartos;
- características adicionais;
- retorno esperado em cenários de investimento.

Quando o perfil está suficientemente completo, o sistema seleciona imóveis compatíveis e apresenta até três opções ao usuário.

---

## Exemplo de resultado

```text
IMV0130
Apartamento em Moema
2 quartos
87 m²
R$ 995.000,00
```

Na interface, cada imóvel é apresentado em um card contendo:

- código;
- tipo;
- bairro;
- quartos;
- área;
- preço.

O cliente pode selecionar:

```text
❤️ Tenho interesse
```

---

# 📅 Agendamento de Visitas

Após demonstrar interesse em um imóvel, o usuário pode selecionar:

```text
📅 Agendar visita
```

A interface solicita:

- data;
- horário;
- observação opcional.

O agendamento é armazenado no SQLite.

Exemplo:

```text
Imóvel: IMV0130
Data: 27/09/2026
Horário: 18:00
Status: Agendado
```

Após o aceite da visita, o campo:

```text
aceitou_visita_reuniao
```

é atualizado e o score é recalculado.

A implementação também realiza verificação para evitar agendamentos duplicados com os mesmos dados.

---

# 💾 Persistência e Memória Conversacional

A POC utiliza **SQLite** para persistência local das interações realizadas na interface.

Banco:

```text
data/sdr_imobiliario.db
```

A persistência é responsável por manter:

- leads;
- conversas;
- mensagens;
- estado do agente;
- agendamentos;
- follow-ups.

---

## Tabela `leads`

Armazena:

```text
id_lead
criado_em
atualizado_em
```

---

## Tabela `conversas`

Armazena:

- identificador da conversa;
- lead;
- estado em JSON;
- status;
- timestamps.

---

## Tabela `mensagens`

Registra o histórico completo da conversa.

Principais campos:

```text
id_mensagem
id_conversa
role
content
criado_em
```

---

## Tabela `agendamentos`

Armazena:

- lead;
- conversa;
- imóvel;
- data;
- horário;
- observação;
- status.

---

## Tabela `followups`

Armazena:

- lead;
- conversa;
- mensagem enviada;
- status;
- data de envio;
- data de resposta.

---

# 🧠 Retomada de Conversa

Como o estado e as mensagens são persistidos, é possível interromper o atendimento e retomá-lo posteriormente.

A interface possui:

```text
💬 Retomar última conversa
```

Além disso, conversas relacionadas a follow-ups podem ser abertas individualmente.

```text
💬 Abrir conversa
```

Ao retomar uma conversa, são recuperados:

- histórico;
- perfil;
- score;
- classificação;
- imóveis apresentados;
- estado conversacional.

---

# 🔔 Módulo de Follow-up

O sistema possui um mecanismo de follow-up para leads que interromperam a conversa.

Fluxo:

```text
Atendimento iniciado
        ↓
Cliente deixa de interagir
        ↓
Sistema identifica conversa elegível
        ↓
Follow-up é gerado
        ↓
Mensagem é armazenada
        ↓
Cliente responde
        ↓
Follow-up passa para Respondido
        ↓
Atendimento continua com o contexto anterior
```

---

## Exemplo de mensagem

```text
Olá! 😊 Na nossa última conversa, você estava procurando
um imóvel para comprar, do tipo apartamento, na região de
Moema, com 2 quartos e orçamento de até R$ 2.000.000,00.

Gostaria de continuar sua busca?
```

---

## Status do Follow-up

A interface apresenta visualmente:

```text
📨 Enviado → ⏳ Aguardando resposta
```

ou:

```text
📨 Enviado → ✅ Respondido
```

---

## 🧪 Modo Demonstração

Por padrão, o sistema pode considerar uma conversa elegível após um período de inatividade.

Como seria inviável aguardar esse período durante a apresentação, foi incluído:

```text
🧪 Modo demonstração
```

Esse modo permite testar o comportamento imediatamente.

---

# 📋 Resumo para o Corretor

Após a qualificação, o sistema pode gerar um resumo consolidado para facilitar o repasse ao corretor.

Exemplo:

```text
RESUMO DO LEAD

Intenção: Compra
Região: Moema
Tipo de imóvel: Apartamento
Orçamento: R$ 2.000.000,00
Quartos: 2
Urgência: Baixa

QUALIFICAÇÃO

Score: 90
Classificação: Quente

IMÓVEIS APRESENTADOS

IMV0130, IMV0371, IMV0077

AGENDAMENTO

Sim — imóvel IMV0130, 27/09/2026 às 18:00

FOLLOW-UP

Enviado e respondido

RESUMO COMERCIAL

Lead com alta qualificação comercial;
demonstrou interesse em avançar para visita;
possui visita agendada;
retomou o contato após follow-up.
```

Esse resumo pode ser copiado diretamente pela interface.

---

# 📊 Dashboard Comercial

A solução possui um dashboard desenvolvido em Streamlit para acompanhamento dos atendimentos realizados pela POC.

---

## 📈 Indicadores Executivos

O dashboard apresenta indicadores como:

- percentual de leads quentes;
- taxa de agendamento;
- score médio;
- taxa de resposta de follow-up.

---

## 📌 Visão Geral

Indicadores apresentados:

```text
Leads
Conversas
Mensagens
Agendamentos
```

---

## 🎯 Qualificação dos Leads

O dashboard apresenta:

```text
🔥 Quentes
🟡 Mornos
🔵 Frios
⭐ Score médio
```

Também é exibido gráfico de distribuição das classificações.

---

## 🏠 Intenção dos Leads

O sistema apresenta a distribuição entre:

```text
🏠 Compra
🔑 Aluguel
📈 Investimento
❔ Não definido
```

Também é exibido gráfico comparativo.

---

## 🔥 Leads Prioritários

Os leads são apresentados em ordem de score para facilitar a priorização comercial.

A tabela apresenta:

- lead;
- intenção;
- região;
- urgência;
- score;
- classificação;
- última atualização.

---

## 📨 Indicadores de Follow-up

O dashboard exibe:

- follow-ups enviados;
- respostas recebidas;
- taxa de resposta.

Também é possível visualizar o histórico de cada follow-up e abrir diretamente a conversa relacionada.

---

## 📅 Agendamentos

O dashboard apresenta os últimos agendamentos registrados.

Informações exibidas:

- código;
- imóvel;
- data;
- horário;
- status.

---

## 💬 Conversas Recentes

A área de conversas recentes apresenta:

- lead;
- conversa;
- status;
- última atualização.

---

# 📁 Bases de Dados Simuladas

O projeto contém as seguintes bases principais:

```text
data/
├── agendamentos.csv
├── imoveis.csv
├── interacoes.csv
├── leads.csv
└── regras_qualificacao.csv
```

---

## `imoveis.csv`

Base simulada contendo o catálogo imobiliário utilizado pelo agente.

---

## `leads.csv`

Base histórica simulada de leads.

---

## `interacoes.csv`

Histórico simulado de interações comerciais.

---

## `agendamentos.csv`

Dados simulados de agendamentos.

---

## `regras_qualificacao.csv`

Contém as regras utilizadas para o cálculo do score.

---

# 📁 Estrutura do Repositório

```text
tech_challenge_fase5/
│
├── app.py
├── agent.py
├── catalogo.py
├── chat_cli.py
├── database.py
├── llm_client.py
├── prompts.py
├── schemas.py
├── scoring.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── data/
│   ├── agendamentos.csv
│   ├── imoveis.csv
│   ├── interacoes.csv
│   ├── leads.csv
│   ├── regras_qualificacao.csv
│   └── sdr_imobiliario.db
│
├── docs/
│   │
│   ├── dados/
│   │   ├── bases_consolidadas.xlsx
│   │   └── documentacao_dados.md
│   │
│   ├── dashboard/
│   │   ├── especificacao_dashboard.md
│   │   └── indicadores_dashboard.xlsx
│   │
│   ├── desafio/
│   │   └── enunciado_fase_5.pdf
│   │
│   ├── funcional/
│   │   ├── conteudo_funcional_readme.md
│   │   ├── fluxos_funcionais.md
│   │   └── regras_conversacionais.md
│   │
│   ├── organizacao/
│   │   ├── arquivos_recebidos.json
│   │   ├── definicoes_tecnicas.md
│   │   ├── integracao_v1.md
│   │   ├── lgpd_privacidade.md
│   │   ├── matriz_rastreabilidade.xlsx
│   │   ├── plano_karim.md
│   │   └── status_projeto.md
│   │
│   └── testes/
│       ├── casos_de_teste_iniciais.xlsx
│       ├── criterios_de_aceite.md
│       ├── leitura_inicial.md
│       ├── regressao_aluguel.md
│       ├── regressao_orcamento.md
│       └── roteiro_validacao_demo.md
│
└── tests/
    ├── test_agent.py
    └── test_ollama_live.py
```

> O arquivo `sdr_imobiliario.db` é criado durante a execução da aplicação e pode ser mantido fora do controle de versão.

---

# 👥 Integrantes e Responsabilidades

| Integrante | Responsabilidade Principal |
|---|---|
| Wellington | Fluxos funcionais, regras conversacionais, cenários e documentação |
| Rúben | Bases de dados, regras de qualificação, dashboard e apoio ao agendamento |
| Karim | Núcleo de IA, integração com LLM, prompts, estado e contrato do agente |
| Michele | Interface Streamlit, integração dos módulos, persistência, follow-up, dashboard e consolidação da demonstração |

> Adicionar os nomes completos e RMs antes da entrega final.

---

# ⚙️ Configuração do Ambiente

O projeto utiliza variáveis de ambiente para configuração do Ollama.

O arquivo de referência é:

```text
.env.example
```

Conteúdo:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
```

A implementação atual lê essas variáveis do ambiente do sistema.

---

# 🧰 Tecnologias Utilizadas

- Python 3.10+
- Streamlit
- SQLite
- Ollama
- Qwen 2.5 3B
- Git
- GitHub
- CSV
- JSON
- unittest

Bibliotecas padrão utilizadas incluem:

- `sqlite3`
- `json`
- `csv`
- `datetime`
- `pathlib`
- `uuid`

---

# ⚙️ Como Executar o Projeto

## 1. Clonar o repositório

```bash
git clone https://github.com/ykarimmendes/tech_challenge_fase5.git
cd tech_challenge_fase5
```

---

## 2. Criar ambiente virtual

```bash
python -m venv .venv
```

### Windows

```powershell
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

---

## 3. Instalar dependências

```bash
pip install -r requirements.txt
```

---

# 🤖 Instalação do Ollama

Instale o Ollama na máquina.

Depois baixe o modelo:

```bash
ollama pull qwen2.5:3b
```

Verifique os modelos instalados:

```bash
ollama list
```

O servidor padrão utilizado pela aplicação é:

```text
http://localhost:11434
```

---

# ▶️ Executando a Interface

Execute:

```bash
streamlit run app.py
```

O Streamlit normalmente disponibilizará a aplicação em:

```text
http://localhost:8501
```

---

# 💻 Executando pelo Terminal

O projeto também possui uma versão simplificada de demonstração por terminal:

```bash
python chat_cli.py
```

---

# 🧪 Testes Automatizados

Os testes estão armazenados em:

```text
tests/
```

Arquivos principais:

```text
tests/test_agent.py
tests/test_ollama_live.py
```

Para executar os testes unitários:

```bash
python -m unittest discover tests
```

O teste `test_ollama_live.py` depende de:

- Ollama instalado;
- servidor Ollama ativo;
- modelo configurado disponível localmente.

---

# 📚 Documentação do Projeto

A pasta `docs/` contém materiais utilizados no desenvolvimento e validação da solução.

| Documento | Descrição |
|---|---|
| `docs/desafio/enunciado_fase_5.pdf` | Enunciado oficial do Tech Challenge |
| `docs/dados/documentacao_dados.md` | Documentação das bases utilizadas |
| `docs/dados/bases_consolidadas.xlsx` | Consolidação das bases de dados |
| `docs/dashboard/especificacao_dashboard.md` | Especificação funcional do dashboard |
| `docs/dashboard/indicadores_dashboard.xlsx` | Indicadores planejados para o dashboard |
| `docs/funcional/fluxos_funcionais.md` | Fluxos de atendimento |
| `docs/funcional/regras_conversacionais.md` | Regras da conversa |
| `docs/funcional/conteudo_funcional_readme.md` | Conteúdo funcional de referência |
| `docs/organizacao/definicoes_tecnicas.md` | Decisões técnicas do projeto |
| `docs/organizacao/integracao_v1.md` | Definição inicial da integração |
| `docs/organizacao/lgpd_privacidade.md` | Considerações de privacidade e LGPD |
| `docs/organizacao/matriz_rastreabilidade.xlsx` | Relação entre requisitos e implementação |
| `docs/organizacao/status_projeto.md` | Acompanhamento do desenvolvimento |
| `docs/testes/criterios_de_aceite.md` | Critérios utilizados para validação |
| `docs/testes/casos_de_teste_iniciais.xlsx` | Casos de teste |
| `docs/testes/regressao_aluguel.md` | Testes do fluxo de aluguel |
| `docs/testes/regressao_orcamento.md` | Testes relacionados ao orçamento |
| `docs/testes/roteiro_validacao_demo.md` | Roteiro de validação da demonstração |

---

# 🔐 Segurança, Privacidade e LGPD

Como o projeto simula o atendimento de clientes imobiliários, informações pessoais poderiam existir em um ambiente real.

Nesta POC:

- são utilizados dados simulados;
- não é necessário armazenar dados pessoais reais;
- o banco SQLite é utilizado apenas como persistência local;
- credenciais e configurações sensíveis não devem ser versionadas.

Para um ambiente produtivo, seriam necessárias medidas adicionais como:

- consentimento;
- autenticação;
- controle de acesso;
- criptografia;
- política de retenção;
- minimização de dados;
- anonimização;
- exclusão de dados mediante solicitação;
- trilha de auditoria;
- adequação formal à LGPD.

---

# ⚠️ Limitações da POC

A solução foi construída para demonstração acadêmica e possui algumas limitações.

- O catálogo de imóveis é simulado.
- O banco SQLite é local.
- O atendimento não está integrado diretamente ao WhatsApp.
- Não existe integração com CRM real.
- O agendamento não utiliza agenda externa de corretores.
- O follow-up é persistido localmente.
- O disparo automático de mensagens não utiliza um serviço externo.
- O modo de demonstração permite antecipar o follow-up.
- A IA utiliza um modelo local relativamente pequeno.
- O sistema não possui autenticação de usuários.
- Não existe deploy em nuvem nesta versão.
- O dashboard utiliza principalmente os dados produzidos pela POC em execução.
- A qualificação segue regras determinísticas definidas para o projeto.

---

# 🚀 Possíveis Evoluções

A arquitetura permite futuras evoluções como:

- integração com WhatsApp;
- integração com e-mail;
- CRM imobiliário;
- Google Calendar ou agenda corporativa;
- API REST;
- banco PostgreSQL;
- deploy em cloud;
- autenticação;
- perfis de usuário;
- múltiplos corretores;
- RAG para documentação e imóveis;
- busca semântica;
- recomendação personalizada;
- multiagentes;
- voz;
- observabilidade;
- métricas de conversão;
- relatórios comerciais;
- integração com portais imobiliários;
- automação real de follow-ups.

---

# 🎬 Roteiro Sugerido de Demonstração

## 1. Iniciar novo atendimento

Exemplo:

```text
Quero comprar um apartamento em Moema por até R$ 2 milhões.
```

---

## 2. Demonstrar extração automática

Mostrar na lateral:

```text
Intenção: Compra
Região: Moema
Tipo: Apartamento
Orçamento: R$ 2.000.000,00
```

---

## 3. Responder às perguntas restantes

Exemplo:

```text
Quero 2 quartos.
```

```text
Minha urgência é baixa.
```

---

## 4. Mostrar o score

Exemplo:

```text
Score: 70
🔥 Lead Quente
```

---

## 5. Apresentar imóveis

Mostrar os cards encontrados.

Selecionar:

```text
❤️ Tenho interesse
```

---

## 6. Realizar agendamento

Selecionar:

```text
📅 Agendar visita
```

Informar:

```text
Data
Horário
Observação
```

Após confirmar, mostrar o score atualizado.

---

## 7. Gerar resumo para o corretor

Selecionar:

```text
📋 Gerar resumo para o corretor
```

Mostrar:

- perfil;
- score;
- imóveis;
- agendamento;
- follow-up;
- resumo comercial.

---

## 8. Abrir o Dashboard

Demonstrar:

```text
📈 Indicadores Executivos
📌 Visão Geral
🎯 Qualificação dos Leads
🏠 Intenção dos Leads
🔥 Leads Prioritários
```

---

## 9. Demonstrar o Follow-up

Ativar:

```text
🧪 Modo demonstração
```

Selecionar:

```text
📨 Enviar follow-up
```

---

## 10. Abrir a conversa

Selecionar:

```text
💬 Abrir conversa
```

Responder:

```text
Sim, quero continuar.
```

---

## 11. Mostrar o resultado

Retornar ao Dashboard e mostrar:

```text
📨 Enviado → ✅ Respondido
```

Também demonstrar a alteração dos indicadores:

```text
Follow-ups enviados
Respostas
Taxa de resposta
```

---

# ✅ Status Atual

| Item | Status |
|---|---|
| Estrutura do repositório | ✅ Implementado |
| Base simulada de imóveis | ✅ Implementado |
| Base simulada de leads | ✅ Implementado |
| Fluxos de Compra | ✅ Implementado |
| Fluxos de Aluguel | ✅ Implementado |
| Fluxo de Investimento | ✅ Implementado |
| Integração com Ollama | ✅ Implementado |
| Extração estruturada com IA | ✅ Implementado |
| Memória durante conversa | ✅ Implementado |
| Persistência em SQLite | ✅ Implementado |
| Retomada de conversa | ✅ Implementado |
| Qualificação de leads | ✅ Implementado |
| Classificação Frio/Morno/Quente | ✅ Implementado |
| Busca de imóveis | ✅ Implementado |
| Interface Streamlit | ✅ Implementado |
| Cards de imóveis | ✅ Implementado |
| Registro de interesse | ✅ Implementado |
| Agendamento | ✅ Implementado |
| Prevenção de agendamento duplicado | ✅ Implementado |
| Follow-up | ✅ Implementado |
| Modo demonstração de follow-up | ✅ Implementado |
| Identificação de resposta ao follow-up | ✅ Implementado |
| Dashboard | ✅ Implementado |
| Indicadores executivos | ✅ Implementado |
| Gráfico de classificação | ✅ Implementado |
| Gráfico por intenção | ✅ Implementado |
| Leads prioritários | ✅ Implementado |
| Resumo para corretor | ✅ Implementado |
| Testes automatizados do agente | ✅ Implementado |
| Integração com WhatsApp | ⏳ Evolução futura |
| Integração com CRM | ⏳ Evolução futura |
| Deploy em nuvem | ⏳ Evolução futura |

---

# 📌 Considerações Finais

A POC demonstra um fluxo completo de atendimento imobiliário utilizando Inteligência Artificial.

A solução não se limita a responder perguntas. O agente mantém um estado estruturado do cliente, conduz a qualificação de forma progressiva e integra diferentes componentes comerciais.

O fluxo desenvolvido permite representar:

```text
Atendimento
   ↓
Qualificação
   ↓
Recomendação
   ↓
Interesse
   ↓
Agendamento
   ↓
Follow-up
   ↓
Retomada
   ↓
Resumo para corretor
   ↓
Acompanhamento pelo Dashboard
```

Essa arquitetura possibilita evoluir a aplicação para cenários reais, integrando canais externos, CRMs, calendários, bancos de dados corporativos e serviços em nuvem.

---

## FIAP - Pós Tech

### Tech Challenge - Fase 5

**Agente SDR Imobiliário com Inteligência Artificial**
