# Conteúdo Funcional para o README — Agente SDR Imobiliário

> Este arquivo é um **rascunho funcional** para ser incorporado ao README principal.  
> A arquitetura definitiva, tecnologias, comandos de instalação/execução e detalhes da IA deverão ser completados após a implementação de Karim e Michele.

## Visão geral
Este projeto apresenta uma Prova de Conceito de um **Agente SDR Imobiliário com Inteligência Artificial Generativa**, capaz de apoiar o atendimento inicial de leads de uma imobiliária.

A solução foi planejada para conversar com potenciais clientes, identificar suas necessidades, qualificar oportunidades, consultar uma base simulada de imóveis, apoiar follow-ups, registrar agendamentos e preparar informações para o time comercial.

## Objetivos funcionais
A POC busca demonstrar:
- atendimento automatizado de leads;
- conversa natural e humanizada;
- identificação de intenção de compra, aluguel ou investimento;
- coleta progressiva das informações necessárias;
- qualificação e priorização dos leads;
- continuidade da conversa;
- follow-up;
- consulta a uma base simulada de imóveis;
- agendamento de visitas/reuniões;
- geração de resumo para corretor ou especialista;
- dashboard mínimo de acompanhamento.

## Cenários principais

### Compra
O agente identifica a intenção e busca informações como orçamento, região, tipo de imóvel, quartos e urgência. Com dados suficientes, consulta a base simulada, apresenta opções compatíveis e pode encaminhar o lead para visita ou reunião.

### Aluguel
O fluxo considera orçamento mensal, região, tipo do imóvel, quartos, urgência e preferências complementares, como imóvel mobiliado, aceitação de pets, proximidade de metrô e imóvel novo.

### Investimento
O agente identifica ticket disponível, perfil do investidor, expectativa de retorno, região e urgência. O objetivo é qualificar o interesse e encaminhar o lead para um especialista quando apropriado.

### Follow-up
Quando uma conversa fica sem resposta, a solução deve recuperar o contexto, retomar o contato sem repetir toda a qualificação e seguir a partir da próxima informação necessária.

## Qualificação de leads
Os leads são classificados em:
- **Frio:** 0 a 39 pontos;
- **Morno:** 40 a 69 pontos;
- **Quente:** 70 a 100 pontos.

As regras são diferentes para Compra/Aluguel e Investimento.

Para investimento, perfil do investidor e expectativa de retorno são informações essenciais. Enquanto uma delas estiver ausente, o lead não deve ser classificado como Quente.

## Dados da POC
A solução utiliza dados sintéticos.

Base preparada:
- 500 imóveis;
- 600 leads;
- 183 agendamentos;
- 2.088 interações históricas;
- regras de qualificação.

Arquivos principais:
```text
data/
├── imoveis.csv
├── leads.csv
├── regras_qualificacao.csv
├── agendamentos.csv
└── interacoes.csv
```

## Continuidade e histórico
A base de interações permite representar histórico conversacional para que a solução:
- recupere contexto;
- evite repetir perguntas;
- registre mudanças de preferência;
- apoie follow-ups;
- gere resumo comercial.

## Dashboard
Foi especificado um dashboard mínimo com:
- total de leads;
- distribuição por Frio/Morno/Quente;
- intenção dos leads;
- regiões mais procuradas;
- agendamentos;
- follow-ups;
- leads prioritários.

A implementação deve consumir os dados da aplicação e refletir o estado atual dos leads.

## Privacidade e segurança
A POC utiliza dados sintéticos.

Boas práticas previstas:
- minimização de dados;
- não utilização de dados reais;
- proteção de credenciais;
- variáveis de ambiente para segredos;
- não versionamento de `.env`;
- logs sem credenciais;
- possibilidade de encaminhamento para atendimento humano;
- recomendação somente de imóveis existentes na base.

## Testes
A validação funcional considera cenários de:
- compra;
- aluguel;
- investimento;
- ausência de informações;
- mudança de orçamento/região;
- falta de imóvel compatível;
- aceite ou recusa de visita;
- conversa interrompida;
- follow-up;
- intenção indefinida;
- leads Frios/Quentes;
- solicitação de humano;
- geração de resumo.

Os resultados reais serão preenchidos após a integração completa da solução.

## Limitações da POC
- dados utilizados são sintéticos;
- a solução é acadêmica e não representa sistema imobiliário produtivo;
- integrações externas opcionais só devem ser descritas como implementadas quando efetivamente estiverem funcionando;
- recomendações dependem da base simulada disponível;
- decisões comerciais finais permanecem com o corretor/especialista.

## Estrutura de documentação sugerida
```text
docs/
├── ruben/
│   ├── especificacao_dashboard.md
│   ├── documentacao_dados.md
│   └── indicadores_dashboard.xlsx
└── wellington/
    ├── fluxos_funcionais.md
    ├── regras_conversacionais.md
    ├── casos_de_teste_iniciais.xlsx
    ├── lgpd_privacidade.md
    ├── criterios_de_aceite.md
    ├── matriz_rastreabilidade.xlsx
    ├── conteudo_funcional_readme.md
    └── roteiro_validacao_demo.md
```

## Seções a completar após desenvolvimento
Karim e Michele deverão fornecer informações para completar no README:
- arquitetura técnica final;
- modelo/LLM utilizado;
- estratégia de prompt;
- bibliotecas e versões;
- instalação;
- variáveis de ambiente;
- comando para executar;
- interface escolhida;
- mecanismo de persistência;
- integrações efetivamente implementadas;
- prints da solução;
- exemplos reais de execução;
- limitações técnicas;
- possíveis evoluções.

## Entrega final
Antes da submissão, o README principal deve ser consolidado para refletir **somente o que estiver realmente implementado**, incluindo instruções reproduzíveis de execução da POC.
