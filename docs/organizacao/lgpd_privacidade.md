# LGPD e Privacidade — Agente SDR Imobiliário

## Objetivo
Definir cuidados mínimos de privacidade, segurança e uso responsável dos dados na POC do Agente SDR Imobiliário.

> Este documento complementa o desafio com boas práticas de privacidade e segurança. O enunciado cita **Segurança** como diferencial técnico, mas não define uma implementação específica de LGPD. Portanto, os pontos abaixo funcionam como orientação para a POC e para a documentação final.

## 1. Premissa da POC
As bases preparadas para o projeto são **sintéticas** e destinadas exclusivamente à demonstração acadêmica.

Consequências práticas:
- não utilizar nomes, telefones, e-mails ou documentos reais de clientes;
- não inserir dados reais de corretores ou colaboradores;
- não copiar conversas reais de atendimento;
- não utilizar informações sensíveis desnecessárias para testar o agente.

## 2. Minimização de dados
O agente deve coletar somente informações necessárias para qualificar o lead e conduzir o atendimento.

### Dados adequados ao fluxo
- intenção: compra, aluguel ou investimento;
- orçamento ou ticket;
- região/bairro;
- tipo de imóvel;
- quantidade de quartos;
- urgência;
- preferências relevantes;
- perfil do investidor;
- expectativa de retorno;
- interesse em visita/reunião;
- informações necessárias ao follow-up.

### Dados que não devem ser solicitados sem necessidade
- CPF/RG;
- dados bancários;
- informações de saúde;
- religião;
- opinião política;
- dados de crianças/adolescentes;
- informações pessoais sem relação com a negociação imobiliária.

## 3. Transparência
Na demonstração, o usuário deve conseguir entender que está interagindo com um agente automatizado.

Recomendação de mensagem inicial:
> “Olá! Sou o assistente virtual da imobiliária. Posso ajudar a entender o tipo de imóvel ou investimento que você procura e organizar as informações para nosso time comercial.”

Não é necessário reproduzir exatamente esse texto; o importante é evitar induzir o usuário a acreditar que está falando com uma pessoa quando isso não for verdade.

## 4. Finalidade
Os dados coletados durante a POC devem ser usados somente para:
- qualificação do lead;
- recomendação de imóveis;
- continuidade do atendimento;
- follow-up;
- agendamento;
- encaminhamento ao corretor/especialista;
- geração de resumo comercial;
- indicadores do dashboard.

## 5. Histórico e memória conversacional
O histórico deve conter somente o necessário para preservar contexto.

Boas práticas:
- evitar registrar informações irrelevantes;
- não expor histórico de um lead para outro;
- vincular as interações corretamente ao `id_lead`;
- não repetir informações já coletadas;
- permitir que a informação mais recente substitua preferências antigas quando o lead alterar sua decisão.

## 6. Credenciais e segredos
Caso sejam utilizadas APIs externas ou LLMs:
- nunca salvar chave de API diretamente no código;
- utilizar variáveis de ambiente ou mecanismo equivalente;
- não versionar arquivos `.env`;
- manter `.env` no `.gitignore`;
- remover tokens, chaves e segredos de prints e vídeos.

Exemplo:
```text
OPENAI_API_KEY=...
```

O valor real não deve aparecer no GitHub, README, vídeo ou evidências.

## 7. Logs
Os logs devem apoiar testes e observabilidade sem expor dados desnecessários.

Registrar, quando útil:
- identificador sintético do lead;
- data/hora;
- etapa do fluxo;
- ação executada;
- resultado;
- erro técnico.

Evitar:
- chaves de API;
- prompts contendo segredos;
- conteúdo pessoal desnecessário;
- dados que não tenham função para teste ou auditoria.

## 8. Encaminhamento para humano
O agente deve permitir encaminhamento quando:
- o usuário pedir atendimento humano;
- houver situação não coberta pelo fluxo;
- houver dúvida que o agente não consiga resolver com segurança;
- for necessário especialista em investimento;
- houver conflito ou inconsistência relevante nos dados.

O agente não deve inventar uma resposta apenas para evitar a transferência.

## 9. Recomendação de imóveis
O agente deve recomendar somente imóveis existentes na base simulada.

Quando não houver opção compatível:
1. informar que não encontrou correspondência com os critérios atuais;
2. sugerir flexibilizar um critério, quando fizer sentido;
3. não criar endereço, preço, imóvel ou disponibilidade inexistente.

## 10. Retenção e descarte na POC
Como o projeto utiliza dados sintéticos, não há necessidade de política complexa de retenção. Mesmo assim:
- manter no repositório apenas arquivos necessários para a demonstração;
- remover arquivos temporários e versões contendo credenciais;
- evitar disponibilizar exports desnecessários;
- excluir logs de teste com informações inadequadas antes da entrega.

## 11. Checklist antes de publicar o repositório
- [ ] Todas as bases são sintéticas.
- [ ] Nenhuma credencial está no código.
- [ ] `.env` não foi versionado.
- [ ] O histórico é separado por lead.
- [ ] O agente não solicita dados desnecessários.
- [ ] O agente não inventa imóveis.
- [ ] Existe possibilidade de encaminhamento para humano/especialista.
- [ ] Prints e vídeo não mostram chaves ou segredos.
- [ ] README informa que a solução é uma POC acadêmica.
- [ ] Limitações da solução estão descritas.

## 12. O que validar após a integração
Depois que Karim e Michele concluírem o agente e a aplicação, Wellington deverá verificar:
- se o agente coleta apenas os campos previstos;
- se o histórico não mistura leads;
- se credenciais estão protegidas;
- se os logs não expõem segredos;
- se o atendimento permite encaminhamento;
- se imóveis não são inventados;
- se as informações apresentadas no vídeo são inteiramente sintéticas.

O resultado dessa validação poderá ser incorporado ao README e às evidências finais.
