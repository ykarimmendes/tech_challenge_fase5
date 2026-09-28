# Explicação da IA Utilizada

## 1. Visão Geral

O projeto **Agente SDR Imobiliário com Inteligência Artificial** utiliza um modelo de linguagem para interpretar mensagens em linguagem natural e transformar a conversa com o lead em informações estruturadas que possam ser utilizadas pelas regras de negócio da aplicação.

A solução foi construída com uma arquitetura híbrida, combinando:

- Inteligência Artificial para interpretação da linguagem natural;
- regras determinísticas em Python para controle do fluxo;
- persistência de contexto em SQLite;
- catálogo imobiliário simulado;
- scoring e classificação de leads;
- agendamento;
- follow-up contextualizado;
- dashboard comercial.

O princípio adotado pela solução é:

> **O LLM interpreta; o código decide.**

Isso significa que o modelo de linguagem auxilia na compreensão da mensagem, mas as principais decisões comerciais e operacionais permanecem sob controle da aplicação.

---

## 2. Modelo de Linguagem Utilizado

O modelo utilizado no projeto é:

**Qwen2.5:3b**

A execução é realizada localmente por meio do:

**Ollama**

O Ollama disponibiliza o modelo através de uma API local, utilizada pela aplicação Python para enviar as mensagens e receber a extração estruturada.

Essa abordagem permite que a prova de conceito funcione localmente, sem depender obrigatoriamente de serviços externos de IA.

---

## 3. Papel da Inteligência Artificial

A principal responsabilidade do LLM é compreender as mensagens enviadas pelo lead.

O usuário pode escrever de forma natural, por exemplo:

> Quero investir até 800 mil reais e busco um retorno de 8% ao ano.

A aplicação utiliza o modelo para identificar informações como:

```json
{
  "intencao": "Investimento",
  "orcamento_ticket": 800000,
  "retorno_esperado_pct": 8
}
```

Outro exemplo:

> Procuro um apartamento em Moema, com dois quartos, por até 2 milhões.

A mensagem pode ser interpretada como:

```json
{
  "tipo_imovel_interesse": "Apartamento",
  "regiao_bairro": "Moema",
  "quartos": 2,
  "orcamento_ticket": 2000000
}
```

Assim, o usuário não precisa preencher formulários rígidos para iniciar o atendimento.

---

## 4. Dados Extraídos pela IA

Entre os principais campos que podem ser identificados durante a conversa estão:

- intenção do lead;
- orçamento ou ticket;
- região ou bairro;
- zona preferida;
- tipo de imóvel;
- quantidade de quartos;
- urgência;
- perfil do investidor;
- retorno esperado;
- preferência por imóvel mobiliado;
- proximidade ao metrô;
- preferência por imóvel novo;
- informações relacionadas à visita ou reunião.

A IA não é responsável pelo armazenamento definitivo desses dados. As informações passam por validação antes de serem incorporadas ao estado da conversa.

---

## 5. Prompt Engineering

O projeto utiliza instruções específicas para orientar o comportamento do modelo.

O prompt define regras para:

- identificar intenção de compra, aluguel ou investimento;
- interpretar valores monetários;
- interpretar quantidade de quartos;
- identificar bairros e regiões;
- reconhecer perfil de investimento;
- reconhecer retorno percentual anual;
- compreender respostas curtas;
- utilizar a última pergunta como contexto;
- evitar a criação de dados não informados;
- identificar solicitações de atendimento humano;
- identificar pedidos de encerramento;
- identificar pedidos de resumo.

O modelo recebe não apenas a mensagem atual, mas também informações do estado existente da conversa.

---

## 6. Extração Estruturada com JSON Schema

A aplicação não utiliza diretamente uma resposta textual livre do LLM.

A saída esperada segue um **JSON Schema**, que determina os campos e os formatos aceitos.

Isso permite transformar linguagem natural em dados estruturados de maneira padronizada.

Fluxo simplificado:

```text
Mensagem do usuário
        ↓
Prompt + contexto
        ↓
Qwen2.5:3b
        ↓
JSON estruturado
        ↓
Validação
        ↓
Estado da conversa
```

Essa estrutura facilita a integração entre o modelo de linguagem e as demais partes do sistema.

---

## 7. Contexto e Continuidade da Conversa

A continuidade da conversa não depende apenas da memória interna do modelo.

A aplicação mantém um **estado estruturado do lead**, que contém os dados já coletados durante o atendimento.

Por exemplo:

```text
Intenção: Investimento
Ticket: R$ 800.000,00
Perfil do investidor: Moderado
Retorno esperado: 8% ao ano
Urgência: Média
```

Esse estado é armazenado em SQLite.

Quando o usuário envia uma nova mensagem, o modelo recebe contexto suficiente para compreender respostas curtas.

Exemplo:

```text
Agente:
Seu perfil de investimento é conservador, moderado ou arrojado?

Usuário:
Moderado.
```

A aplicação consegue associar a resposta ao campo:

```text
perfil_investidor = Moderado
```

---

## 8. Validação Anti-Alucinação

Durante os testes foi identificado que um modelo de linguagem pode, em alguns casos, sugerir ou preencher informações que não foram explicitamente fornecidas pelo usuário.

Por exemplo, diante da mensagem:

> Quero investir em imóveis para renda.

o modelo poderia inferir incorretamente:

```text
Tipo de imóvel = Apartamento
Urgência = Alta
Perfil do investidor = Moderado
```

Mesmo sem essas informações terem sido declaradas.

Para reduzir esse problema, foi implementada uma camada de **validação determinística em Python**.

Antes que uma informação extraída pelo LLM seja incorporada ao perfil, a aplicação verifica se existe evidência suficiente na mensagem atual ou no contexto da pergunta anterior.

Com isso, a solução aceita:

```text
Intenção = Investimento
```

mas rejeita atributos não informados pelo usuário.

Essa estratégia reduz a possibilidade de alucinações afetarem as regras de negócio.

---

## 9. Arquitetura Híbrida

A solução separa claramente as responsabilidades entre IA e código.

### Responsabilidades do LLM

O modelo de linguagem é utilizado para:

- compreender linguagem natural;
- interpretar a intenção do usuário;
- identificar informações relevantes;
- interpretar respostas contextuais;
- transformar texto em dados estruturados.

### Responsabilidades do código Python

O código da aplicação é responsável por:

- validar os dados extraídos;
- controlar o estado da conversa;
- determinar quais informações ainda faltam;
- calcular o score;
- classificar o lead;
- consultar o catálogo imobiliário;
- realizar agendamentos;
- controlar follow-ups;
- persistir dados;
- controlar encaminhamento para corretor ou especialista;
- alimentar o dashboard.

Essa divisão aumenta a previsibilidade e a confiabilidade da solução.

---

## 10. Qualificação e Scoring

O modelo de linguagem não decide diretamente se um lead é frio, morno ou quente.

Após a coleta dos dados, o sistema utiliza regras determinísticas de scoring.

O resultado é armazenado como:

```text
Score: valor entre 0 e 100
Classificação: Frio, Morno ou Quente
```

Assim, a IA fornece os dados necessários para a qualificação, mas o cálculo final permanece sob controle da aplicação.

---

## 11. Fluxos de Atendimento

A solução possui fluxos específicos para diferentes intenções.

### Compra

O agente pode coletar:

- orçamento;
- bairro ou região;
- tipo de imóvel;
- quantidade de quartos;
- urgência.

Após a qualificação, o sistema pode consultar o catálogo e apresentar imóveis compatíveis.

### Aluguel

O fluxo considera informações semelhantes ao de compra, com tratamento específico para orçamento mensal.

### Investimento

O agente coleta:

- ticket de investimento;
- perfil do investidor;
- retorno anual esperado;
- urgência.

Após a qualificação, o sistema consulta as oportunidades disponíveis e pode encaminhar o lead para um especialista em investimentos imobiliários.

---

## 12. Busca no Catálogo

A base de imóveis utilizada na prova de conceito é simulada por meio de um arquivo CSV.

O LLM não inventa imóveis.

Depois que o perfil do lead está suficientemente preenchido, a busca é realizada pelo código da aplicação.

A aplicação retorna apenas imóveis existentes na base simulada e disponíveis para apresentação.

Caso não exista uma opção compatível, o sistema informa ao usuário e pode oferecer flexibilização dos critérios ou encaminhamento para atendimento especializado.

---

## 13. Agendamento

O sistema permite registrar agendamentos associados ao lead e à conversa.

O agendamento inclui informações como:

- imóvel;
- data;
- horário;
- observação.

Os dados são persistidos no SQLite e ficam disponíveis no dashboard e no resumo comercial.

---

## 14. Follow-up Contextualizado

A solução possui um mecanismo de follow-up para conversas interrompidas.

Quando uma conversa permanece sem interação pelo período configurado, o sistema pode gerar uma mensagem de retomada utilizando as informações já armazenadas.

Exemplo:

> Olá! 😊 Na nossa última conversa, você estava avaliando oportunidades de investimento imobiliário, com perfil moderado, buscando retorno de 8% ao ano e com ticket de até R$ 800.000,00. Gostaria de continuar seu atendimento?

O follow-up preserva o contexto do atendimento sem exigir que o usuário repita todas as informações.

Na prova de conceito também existe um **modo de demonstração**, que permite testar esse comportamento sem aguardar o período completo de inatividade.

Quando o lead responde, o follow-up é marcado como respondido.

---

## 15. Resumo Comercial

A aplicação gera automaticamente um resumo estruturado para apoiar o trabalho do corretor ou especialista.

O resumo pode incluir:

- intenção;
- orçamento ou ticket;
- região;
- tipo de imóvel;
- quantidade de quartos;
- urgência;
- perfil do investidor;
- retorno esperado;
- score;
- classificação;
- imóveis apresentados;
- agendamento;
- status do follow-up.

No fluxo de investimento, o resumo é direcionado ao especialista em investimentos imobiliários.

---

## 16. Persistência

A aplicação utiliza **SQLite** para armazenar dados da prova de conceito.

Entre os dados persistidos estão:

- leads;
- conversas;
- mensagens;
- estado da conversa;
- agendamentos;
- follow-ups.

A persistência permite recuperar conversas e manter a continuidade do atendimento.

---

## 17. Fluxo Completo da IA

O fluxo de processamento pode ser resumido da seguinte maneira:

```text
Usuário envia uma mensagem
        ↓
Interface Streamlit
        ↓
Estado atual + histórico da conversa
        ↓
Prompt estruturado
        ↓
Qwen2.5:3b via Ollama
        ↓
Extração em JSON
        ↓
Validação anti-alucinação
        ↓
Atualização do perfil
        ↓
Regras de negócio
        ↓
Scoring / Catálogo / Agendamento / Follow-up
        ↓
Persistência SQLite
        ↓
Resposta ao usuário
```

---

## 18. Benefícios da Abordagem

A arquitetura adotada apresenta os seguintes benefícios:

- interação natural com o usuário;
- menor dependência de formulários;
- continuidade da conversa;
- extração estruturada;
- controle de alucinações;
- regras comerciais previsíveis;
- separação entre interpretação e decisão;
- execução local do modelo;
- modularidade;
- facilidade de evolução da prova de conceito.

---

## 19. Limitações da Prova de Conceito

A solução atual é uma prova de conceito e possui algumas limitações.

O modelo é executado localmente e o tempo de resposta depende do hardware disponível.

O catálogo imobiliário é simulado e não está conectado a uma plataforma imobiliária real.

O follow-up automático é processado pela própria aplicação quando ela está em execução. Em um ambiente de produção, o ideal seria utilizar um scheduler ou worker independente para executar tarefas em segundo plano continuamente.

Também não existe, nesta versão, integração real com WhatsApp, CRM ou serviços externos de agenda.

Esses pontos podem ser tratados em evoluções futuras da solução.

---

## 20. Possíveis Evoluções

Como próximos passos, a solução pode ser expandida com:

- integração com WhatsApp;
- integração com CRM;
- integração com Google Calendar ou Microsoft Outlook;
- uso de RAG para consulta a documentos e informações dos imóveis;
- banco de dados em nuvem;
- autenticação e controle de acesso;
- observabilidade e monitoramento;
- scheduler ou worker para follow-up 24/7;
- integração com APIs reais de imóveis;
- implantação em ambiente cloud;
- suporte a voz;
- arquitetura multiagente.

---

## 21. Conclusão

A solução utiliza Inteligência Artificial como uma camada de compreensão da linguagem natural, enquanto mantém as decisões críticas sob controle do código da aplicação.

Essa arquitetura híbrida permite aproveitar a flexibilidade dos modelos de linguagem sem depender deles para regras comerciais determinísticas.

O resultado é um agente SDR imobiliário capaz de conversar, qualificar leads, manter contexto, consultar imóveis, realizar follow-ups, apoiar agendamentos e gerar informações comerciais estruturadas.

> **O LLM interpreta; o código decide.**
