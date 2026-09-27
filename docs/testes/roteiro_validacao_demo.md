# Roteiro de Validação e Demonstração — Agente SDR Imobiliário

## Objetivo
Definir uma sequência prática para testar e demonstrar a solução depois que o agente e a interface estiverem integrados.

Este roteiro não representa resultado de teste. Ele deve ser executado quando a aplicação estiver funcional.

## Pré-requisitos
Antes de iniciar:
- aplicação executando;
- modelo/LLM configurado;
- bases de imóveis e leads acessíveis;
- histórico de interações disponível;
- mecanismo de agendamento integrado;
- dashboard acessível;
- nenhuma credencial visível na tela;
- base de teste restaurada ou em estado conhecido.

---

## Cenário 1 — Compra
### Mensagem inicial sugerida
> “Estou procurando um apartamento na zona sul.”

### O que deve ser observado
1. agente identifica Compra;
2. pergunta orçamento;
3. pergunta quantidade de quartos;
4. confirma/refina região;
5. identifica urgência;
6. coleta outras informações necessárias sem transformar a conversa em formulário rígido;
7. consulta imóveis reais da base;
8. apresenta opção compatível;
9. oferece visita/reunião;
10. atualiza score/classificação;
11. gera ou disponibiliza resumo.

### Evidências
- print da conversa;
- imóvel apresentado e respectivo `id_imovel`;
- lead atualizado;
- score/classificação;
- agendamento, caso aceito.

---

## Cenário 2 — Investimento
### Mensagem inicial sugerida
> “Quero investir em imóveis para renda.”

### O que deve ser observado
1. agente identifica Investimento;
2. pergunta ticket;
3. identifica perfil do investidor;
4. pergunta expectativa de retorno;
5. identifica região/prazo quando necessário;
6. evita classificar como Quente antes de preencher perfil e retorno;
7. apresenta informações coerentes com a base;
8. direciona para especialista/reunião.

### Evidências
- conversa;
- dados coletados;
- score antes/depois;
- encaminhamento;
- resumo para especialista.

---

## Cenário 3 — Aluguel
### Mensagem inicial sugerida
> “Preciso alugar um apartamento e tenho um cachorro.”

### O que deve ser observado
1. identifica Aluguel;
2. coleta orçamento mensal;
3. região;
4. quartos/tipo;
5. considera preferência por pet;
6. consulta somente imóveis adequados existentes;
7. oferece visita.

### Evidências
- conversa;
- imóvel recomendado;
- dados atualizados;
- agendamento, se aceito.

---

## Cenário 4 — Mudança de preferência
### Sequência sugerida
1. informar orçamento inicial;
2. responder outras perguntas;
3. depois dizer que o orçamento mudou;
4. alterar também região, se desejado.

### Resultado esperado
- informação mais recente prevalece;
- agente não continua recomendando com o valor/região antigos;
- não reinicia a conversa do zero.

---

## Cenário 5 — Nenhum imóvel compatível
Usar uma combinação de critérios que não encontre correspondência.

### Resultado esperado
- agente informa ausência de opção;
- não inventa imóvel;
- sugere flexibilizar um critério quando apropriado.

---

## Cenário 6 — Follow-up
### Preparação
Utilizar lead com conversa anterior e pendência de retorno.

### Resultado esperado
- sistema retoma o contato;
- preserva intenção, orçamento e preferências;
- não repete toda a qualificação;
- registra o follow-up;
- continua do ponto pendente.

---

## Cenário 7 — Solicitação de humano
### Mensagem
> “Quero falar com um corretor.”

### Resultado esperado
- agente respeita o pedido;
- não tenta impedir encaminhamento;
- registra ou sinaliza a transferência.

---

## Cenário 8 — Agendamento
Durante um cenário de compra/aluguel:
> “Gostei. Quero visitar.”

### Resultado esperado
- solicita/confirma informações necessárias;
- registra lead;
- registra imóvel;
- registra data/hora;
- confirma o compromisso.

Para investimento:
> “Quero conversar com um especialista.”

O agendamento pode não possuir imóvel vinculado.

---

## Cenário 9 — Resumo para corretor/especialista
Ao concluir uma qualificação relevante, solicitar/exibir o resumo.

### Conferir
- intenção;
- orçamento/ticket;
- região;
- preferências;
- urgência;
- score;
- classificação;
- visita/reunião;
- observações relevantes.

O resumo deve ser curto e útil para continuidade humana.

---

## Cenário 10 — Dashboard
Abrir o dashboard após as interações.

### Conferir
- total de leads;
- classificação;
- intenção;
- agendamentos;
- leads prioritários;
- atualização coerente após mudanças realizadas nos testes.

Comparar os indicadores com os dados armazenados.

---

## Cenário 11 — Privacidade e segurança
Antes da gravação final:
- abrir o repositório;
- verificar ausência de chave/API;
- conferir `.gitignore`;
- verificar que dados são sintéticos;
- observar logs;
- confirmar que nenhum segredo aparece em tela.

---

## Ordem sugerida para demonstração no vídeo
Para uma demonstração curta e clara:

1. **Apresentar a proposta** — problema e objetivo.
2. **Mostrar rapidamente a arquitetura/interface**.
3. **Demonstrar Compra** — conversa, qualificação e imóvel.
4. **Demonstrar Investimento** — qualificação específica e especialista.
5. **Demonstrar Follow-up** — continuidade de contexto.
6. **Demonstrar Agendamento**.
7. **Mostrar Resumo Inteligente**.
8. **Mostrar Dashboard**.
9. **Explicar dados sintéticos e segurança**.
10. **Encerrar com arquitetura/IA, limitações e possíveis evoluções**.

## Registro da execução
Durante os testes, Wellington deve preencher a planilha de casos de teste já criada:
- Resultado obtido;
- Status;
- Observação.

Também deve salvar evidências com nomes padronizados, por exemplo:

```text
outputs/evidencias/
├── CT-001_compra.png
├── CT-006_investimento.png
├── CT-015_followup.png
├── CT-012_agendamento.png
├── CT-020_resumo.png
└── dashboard_final.png
```

## Momento de execução
Este roteiro deve ser usado **depois da integração de Karim e Michele e antes da gravação definitiva do vídeo/pitch**.

Se algum cenário falhar:
1. registrar como Reprovado ou Bloqueado;
2. informar ao responsável técnico;
3. repetir somente após correção;
4. guardar a evidência final aprovada.
