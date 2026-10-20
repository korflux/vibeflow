# Spec: conferência obrigatória do líder a cada devolutiva
# Alvo: phase-3-conferencia-do-lider
# Status: aprovado
# Rota: high

## Objetivo

O líder da skill `vibeflow` passa a fazer uma conferência barata e obrigatória de forma e direção antes de aceitar cada devolutiva que muda o estado da phase. A conferência diz com o que o líder confronta cada tipo de entrega (artefato de prosa, código, evidência visual, evidência de API ou CLI, Express e medium, onda paralela) e o que ele não faz. Sucesso é o líder detectar no momento da devolutiva uma entrega fora do pedido ou do planejado, em vez de descobri-la só na review, sem assumir correção técnica nem execução de prova, e com a regra morando numa única casa da skill.

## Cobertura da origem

Sem interview (rota `high`). Itens da entrega que poderiam ficar esquecidos:

| Origem | Destino na spec | Motivo se fora/N/A |
|---|---|---|
| Etapas de planejamento (interview, spec, design, plan) e texto avulso | F1 | N/A |
| T* em execução serial e onda paralela | F2 | N/A |
| Entrega com aceite visual | F3 | N/A |
| Entrega de API ou CLI | F4 | N/A |
| Express e medium | F5 | N/A |
| Reprovação na conferência | F6 | N/A |
| Analyze e review | Fora | Escritos pelo revisor de contexto limpo, que já é o certificador independente; a conferência do líder não julga o veredito |
| Scripts `skills/vibeflow/scripts/` | Fora | A conferência não muda estado de disco nem a tabela de estados |

## Suposições e decisões

1. A cada devolutiva que muda o estado (cada etapa de planejamento, cada T* em execução serial, cada onda), o líder faz uma conferência barata e obrigatória antes de aceitar. (processo; já fechado, D1)
2. O líder confere forma e direção, isto é, se a entrega é o que o humano pediu e o que foi planejado; correção técnica continua com o verificador e o revisor. (processo; já fechado, D2)
3. A conferência é definida por tipo de entrega, nos fluxos F1 a F5. (processo; já fechado, D3)
4. A conferência só lê disco, Git e evidência anexada; não executa comando de prova nem cria evidência. Não cria seção nova em artefato nem registro quando passa; reprovação usa a devolução já existente. (processo; já fechado, D4)
5. A conferência não ganha linha própria no chat: aprovação aparece na linha de progresso já existente da devolutiva (`SKILL.md`, seção 9), e reprovação aparece como a devolução ao dono. (processo; já fechado, D5)
6. A mudança resolve a contradição entre o contrato do repo e `references/delegation.md`, deixando uma única casa para a regra. Semver: minor. (escopo; já fechado, D6)
7. Contexto do problema, sem decidir o texto do patch:
   - `skills/vibeflow/SKILL.md`, seção 5, item 4, manda confrontar cada devolutiva com o objetivo da phase sem dizer com o quê; o item 5 condena tanto refazer conferência já certificada quanto aceitar entrega sem confrontá-la; o item 3 diz que o líder nunca certifica o próprio ajuste.
   - `skills/vibeflow/references/delegation.md`, seção "Delegar e colaborar", manda consumir resultado, cobertura, exceções e próximo responsável e não repetir certificação rotineira; o relatório fixo tem o campo `prova`.
   - `skills/vibeflow/references/implement.md`, seção 1, passo 5, repete o confronto com o objetivo apontando para o `SKILL.md`; a tabela da Entrada (Express) e a seção 8 (medium) não citam conferência do líder; a seção 9, passo 4, manda seguir `references/chrome-devtools.md` quando o aceite depende da UI renderizada.
   - `AGENTS.md` da raiz, seção 4 de "Regras deste repo", diz que a IA audita o resultado no disco e no Git.
   - O `docs/` foi removido do repositório em `ca2c3a9`; o contrato vive no `AGENTS.md` e em `skills/vibeflow/references/disco.md`, e a ordem para mudar a skill (`AGENTS.md`, seção 9) começa por `disco.md`. O fato de contrato sobre o papel do líder fica, portanto, no `AGENTS.md`.
8. A superfície de cada passo usa a superfície real do agente: chat do líder com o humano, relatório fixo do subagente, arquivo no disco ou Git. A skill não tem UI visível. (processo; já fechado)
9. Em chat novo, a evidência visual gravada fora do repositório pode ter sumido; com `Visual: necessária` no plan, a review recaptura quando a evidência citada sumiu ou os inputs renderizados mudaram. Limitação aceita. (processo; já fechado, D3)

## Escopo e comportamento

### 1. Fluxo F1: conferir artefato de prosa

- Jornada: N/A, rota `high` sem interview
- Rota: todas as rotas com etapa de planejamento (`high`, `xhigh`, `max`, MVP) e texto avulso
- Gatilho: o redator devolve o relatório fixo de uma etapa de planejamento (interview, spec, design, plan) ou de texto avulso
- Pré-condição: decisões e respostas do humano já fechadas no chat e entregues ao redator no brief
- Superfície por passo: relatório fixo do subagente; arquivo no disco; chat do líder com o humano
- Passos:
  1. O líder lê o relatório fixo do redator -> obtém os paths gravados [superfície: relatório fixo do subagente]
  2. O líder lê o arquivo gravado e o confronta com as decisões tomadas com o humano -> confirma que cada decisão está presente e que nada foi decidido além delas [superfície: arquivo no disco]
  3. Conferência passa -> o líder apresenta o artefato ao humano pela saída da etapa, com a linha de progresso existente [superfície: chat do líder com o humano]
- Validações: o líder não reescreve o artefato; divergência segue F6
- Erros: N/A, a conferência não tem erro próprio; divergência é tratada em F6
- Estados: conferência aprovada; conferência reprovada (F6)
- Aceite: A1
- Reutilizar: saída de cada etapa em `references/<etapa>.md`; devolução ao dono em `SKILL.md`, seção 5

### 2. Fluxo F2: conferir código de T* ou onda

- Jornada: N/A
- Rota: `high`, `xhigh`, `max` e MVP, no implement
- Gatilho: em execução serial, o implementador, o redator ou o corretor devolve o relatório fixo de uma T*; em onda paralela, o verificador devolve a integração da onda
- Pré-condição: T* com `Arquivos:` no `plan.md`, ou recorte do brief
- Superfície por passo: relatório fixo do subagente; Git; chat do líder com o humano
- Passos:
  1. O líder lê o relatório fixo -> obtém paths, prova relatada e pendências [superfície: relatório fixo do subagente]
  2. O líder roda `git diff --stat` e compara os paths alterados com os `Arquivos:` da T* ou com o recorte do brief -> confirma que nenhum path ficou fora do recorte [superfície: Git]
  3. Quando o relatório cita algo estranho, o líder lê só o trecho correspondente do diff -> confirma ou descarta a divergência de direção [superfície: Git]
  4. Conferência passa -> a devolutiva segue o fluxo existente (verificador, finalizador) e o progresso aparece na linha existente [superfície: chat do líder com o humano]
- Validações: em onda paralela, a conferência acontece uma vez na integração da onda, não por T* isolada; o líder não roda testes nem revisa linha a linha
- Erros: N/A, divergência segue F6
- Estados: conferência aprovada; conferência reprovada (F6)
- Aceite: A2, A3
- Reutilizar: `Arquivos:` da T* em `plan.md`; ondas em `references/implement.md`, seção 1

### 3. Fluxo F3: conferir evidência visual

- Jornada: N/A
- Rota: qualquer rota cujo aceite dependa da UI renderizada (`Visual: necessária` no plan, ou brief com aceite visual em low e medium)
- Gatilho: o implementador devolve o relatório fixo de uma entrega com aceite visual
- Pré-condição: viewports e estados definidos no `design.md` ou no brief
- Superfície por passo: arquivo fora do repositório (pasta temporária da sessão); relatório fixo do subagente; chat do líder com o humano
- Passos:
  1. O implementador captura screenshots nos viewports e estados definidos no `design.md` ou no brief e grava as imagens fora do repositório, na pasta temporária da sessão [superfície: arquivo fora do repositório]
  2. O implementador informa os paths das imagens no campo `prova` do relatório fixo [superfície: relatório fixo do subagente]
  3. O verificador reaproveita essa evidência na sua certificação, sem nova captura enquanto os inputs renderizados não mudarem [superfície: relatório fixo do subagente]
  4. O líder abre as imagens e as confronta com o `design.md` ou o brief -> confirma direção visual [superfície: arquivo fora do repositório]
  5. Conferência passa -> progresso na linha existente [superfície: chat do líder com o humano]
- Validações: o implementador é o dono da captura da entrega, e o corretor recaptura quando a correção altera a UI renderizada; o líder não sobe servidor, não navega e não captura; paths de imagem ausentes no campo `prova` reprovam a conferência (F6)
- Erros: evidência ausente ou ilegível volta ao implementador por F6
- Estados: evidência presente e conferida; evidência ausente (F6); evidência sumida, por exemplo em chat novo, ou inputs renderizados alterados (a review recaptura quando `Visual: necessária`)
- Aceite: A4, A5
- Reutilizar: `references/chrome-devtools.md` para a captura; campo `prova` do relatório fixo em `references/delegation.md`

### 4. Fluxo F4: conferir evidência de API ou CLI

- Jornada: N/A
- Rota: qualquer rota cuja entrega exponha API ou CLI
- Gatilho: o implementador ou o verificador devolve o relatório fixo com evidência anexada
- Pré-condição: evidência de chamada real com resposta ou saída de comando anexada no relatório
- Superfície por passo: relatório fixo do subagente; chat do líder com o humano
- Passos:
  1. O líder lê a evidência anexada (chamada real com resposta, saída de comando) e a confronta com o aceite do plan ou do brief -> confirma direção [superfície: relatório fixo do subagente]
  2. Conferência passa -> progresso na linha existente [superfície: chat do líder com o humano]
- Validações: o líder não executa a chamada nem o comando; evidência ausente reprova a conferência (F6)
- Erros: evidência ausente volta ao dono da prova por F6
- Estados: conferência aprovada; conferência reprovada (F6)
- Aceite: A6
- Reutilizar: relatório fixo de `references/delegation.md`

### 5. Fluxo F5: conferir Express e medium

- Jornada: N/A
- Rota: low sem phase (Express) e medium
- Gatilho: o implementador devolve o relatório fixo da mudança do brief
- Pré-condição: brief curto entregue ao implementador
- Superfície por passo: relatório fixo do subagente; Git; chat do líder com o humano
- Passos:
  1. O líder compara o diff com o brief pelo mesmo procedimento de F2 -> confirma recorte e direção [superfície: Git]
  2. Com aceite visual, o líder confere o screenshot anexado pelo procedimento de F3 [superfície: relatório fixo do subagente]
  3. Conferência passa -> o fluxo existente segue (verificador, finalizador) [superfície: chat do líder com o humano]
- Validações: Express feito inteiro pelo próprio líder por ajuste direto não tem conferência própria, porque o líder não certifica o próprio trabalho; vale a prova proporcional já existente
- Erros: N/A, divergência segue F6
- Estados: conferência aprovada; conferência reprovada (F6); Express inteiro do líder sem conferência
- Aceite: A7, A8
- Reutilizar: Express e medium em `references/implement.md` (Entrada e seção 8); ajuste direto em `SKILL.md`, seção 5, item 3

### 6. Fluxo F6: tratar divergência

- Jornada: N/A
- Rota: todas
- Gatilho: a conferência de F1 a F5 encontra divergência
- Pré-condição: divergência identificada pelo líder a partir de disco, Git ou evidência anexada
- Superfície por passo: chat do líder com o humano; relatório fixo do subagente
- Passos:
  1. Divergência de direção (entrega fora do pedido ou do planejado) -> volta ao dono da entrega com apontamento específico [superfície: relatório fixo do subagente]
  2. Divergência técnica (prova, correção, integração) -> volta ao verificador [superfície: relatório fixo do subagente]
  3. A reprovação aparece no chat como a devolução ao dono, sem linha própria de conferência [superfície: chat do líder com o humano]
- Validações: o líder não é desempate técnico; não refaz o trabalho; não cria seção nova em artefato nem registro
- Erros: N/A
- Estados: devolvida ao dono; devolvida ao verificador
- Aceite: A9, A10
- Reutilizar: crítica com apontamento específico em `SKILL.md`, seção 5, item 4

### Fora

- Líder subir servidor, navegar ou capturar evidência: a captura pertence a quem altera a UI renderizada (implementador e, na correção, corretor), e o líder não executa prova fora do Modo B.
- Novo path contratual de evidência: a evidência visual fica fora do repositório e é citada só no campo `prova` do relatório fixo.
- Mudança em `skills/vibeflow/scripts/`: a conferência não muda estado de disco nem a tabela de estados que os scripts aplicam.
- Conferência do analyze e da review: o revisor de contexto limpo já é o certificador independente.
- Linha própria de conferência no chat ou registro em artefato: aprovação usa a linha de progresso existente e reprovação usa a devolução existente.

## Checklist de entrega

### Aceite

- [x] A1: a skill instrui o líder a ler o artefato de prosa gravado e confrontá-lo com as decisões tomadas com o humano antes de apresentá-lo, sem reescrevê-lo.
- [x] A2: a skill instrui o líder a conferir código por `git diff --stat` e paths alterados contra `Arquivos:` da T* ou o recorte do brief, com leitura de trecho do diff só quando o relatório citar algo estranho, sem rodar testes nem revisar linha a linha.
- [x] A3: a skill diz que, em onda paralela, a conferência acontece uma vez na integração da onda.
- [x] A4: a skill atribui ao implementador a captura dos screenshots nos viewports e estados do `design.md` ou do brief, gravados fora do repositório e citados no campo `prova` do relatório fixo, e manda o verificador reaproveitá-los.
- [x] A5: a skill instrui o líder a abrir as imagens anexadas e confrontá-las com o `design.md` ou o brief, sem subir servidor nem navegar, e registra que, com `Visual: necessária`, a review recaptura quando a evidência sumiu, por exemplo em chat novo, ou os inputs renderizados mudaram.
- [x] A6: a skill instrui o líder a conferir a evidência de API ou CLI anexada sem executá-la.
- [x] A7: a skill descreve a conferência de Express e medium como diff contra o brief e, se visual, o screenshot anexado.
- [x] A8: a skill diz que Express feito inteiro pelo líder por ajuste direto não tem conferência própria e segue a prova proporcional existente.
- [x] A9: a skill manda divergência de direção ao dono com apontamento específico e divergência técnica ao verificador, sem o líder desempatar tecnicamente.
- [x] A10: a skill diz que a conferência aprovada aparece só na linha de progresso existente e a reprovada só como a devolução ao dono, sem seção nova nem registro.

### Critérios de sucesso

- [x] C1: a contradição entre o `AGENTS.md` (a IA audita o resultado no disco e no Git) e `references/delegation.md` (consumir o relatório) desaparece; a regra da conferência tem uma única casa no pacote e as demais casas apontam para ela.
- [x] C2: nenhum papel ganha execução de prova pelo líder; nenhuma frase da skill manda o líder executar comando de prova, subir servidor ou criar evidência.
- [x] C3: a captura da evidência visual pertence a quem altera a UI renderizada: o implementador e, na correção, o corretor; fora do Modo B, verificador e líder só a reaproveitam.
- [x] C4: correção técnica continua exclusiva do verificador e do revisor; nenhuma frase da conferência atribui ao líder julgamento técnico de código ou prova.
- [x] C5: nenhum path contratual novo surge em `references/disco.md` e nenhum script de `skills/vibeflow/scripts/` muda.
- [x] C6: a mudança é classificada como minor; o repo não declara versão (`plugin.json` sem campo `version`, sem tags), então nenhum arquivo de versão muda.

## Contratos e restrições necessárias

- Dados e invariantes: a conferência não muda estado de disco; `plan.md`, `review.md` e as linhas `# Status:` seguem com os donos atuais.
- Integrações e interfaces: o relatório fixo mantém os mesmos campos; o campo `prova` passa a carregar os paths das imagens quando há aceite visual.
- Segurança e operação: N/A, a mudança é texto operacional da skill, sem entrada externa, segredo ou rota autenticada; screenshots ficam fora do repositório e não entram em commit.
- Tecnologia imposta: N/A.
- Consumidores: F2, F3, F4 e F5 dependem do campo `prova` do relatório fixo; F1 a F5 dependem da devolução de F6.

## Como provar

| Aceite | F* ou jornada | Nível | Evidência esperada |
|---|---|---|---|
| A1 | F1 | local | Revisão de consistência do texto da skill mostra a regra de prosa na casa única; uso real numa phase com `/vibeflow` mostra o líder lendo o artefato gravado antes de apresentá-lo |
| A2, A3 | F2 | jornada | Revisão de consistência mostra o procedimento de código e a regra de onda; uso real mostra o líder conferindo `git diff --stat` contra `Arquivos:` antes de aceitar a T* serial ou a integração da onda |
| A4, A5 | F3 | jornada | Revisão de consistência mostra a captura atribuída só ao implementador e o líder só abrindo imagens; uso real com aceite visual mostra paths de imagem fora do repositório no campo `prova` e o líder sem servidor nem navegação |
| A6 | F4 | local | Revisão de consistência mostra o líder conferindo evidência anexada sem executar |
| A7, A8 | F5 | local | Revisão de consistência mostra a conferência de Express e medium e a exceção do Express inteiro do líder |
| A9, A10 | F6 | local | Revisão de consistência mostra o roteamento da divergência e a ausência de linha própria; uso real mostra aprovação só na linha de progresso e reprovação como devolução ao dono |

A skill não tem testes automatizados; não se cria teste de presença de palavras, frases ou seções.

## Boundaries

### Always

- Conferir forma e direção a cada devolutiva que muda o estado, lendo só disco, Git e evidência anexada.
- Manter uma única casa para a regra da conferência e fazer as demais casas apontarem para ela.

### Ask first

- Qualquer mudança que dê ao líder execução de prova, captura de evidência ou path contratual novo.

### Never

- Líder rodar testes, subir servidor, navegar, capturar ou reescrever o artefato conferido.
- Criar seção, registro ou linha de chat própria para a conferência.

## Handoff

plan

- Design: N/A, porque a mudança é no texto da skill, sem UI visível.
- Chat: o planejamento segue neste chat com `/vibeflow plan`. Em chat pesado ou host de contexto curto, um chat novo com `/vibeflow` retoma pela etapa gravada. O `spec.md` vivo é a ponte.

- [x] Aprovação humana (leu o arquivo e confirmou)
