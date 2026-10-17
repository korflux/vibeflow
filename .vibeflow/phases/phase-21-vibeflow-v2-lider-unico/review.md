# Review: VibeFlow V2, skill única só texto com coordenador-líder
# Alvo: phase-21-vibeflow-v2-lider-unico
# Status: request-changes

## Contexto

- Alvo: fase `phase-21-vibeflow-v2-lider-unico`, branch `v2`, diff `07466e6..790f887` (HEAD `790f887`).
- Cadeia: interview.md / spec.md (com a Revisão de escopo S1 a S9) / plan.md / analyze.md.
- O que muda: as oito skills `vibe-*` com motores dão lugar a um pacote único só texto, `skills/vibeflow/` (SKILL.md do líder, referências por etapa, `disco.md`, `delegation.md`, templates de artefato, `templates/AGENTS.md` e 12 perfis). Docs, `AGENTS.md`, README, ESCOPO e manifestos passam a 10.0.0.

## Tipo de review

- Tipo: final
- Marco e justificativa: integração final; T1, T2 e T3 com caixa marcada e commit `task(T1,T2,T3)` (`790f887`).
- T* abertas fora do marco: nenhuma
- Provas reaproveitadas: nenhuma; a regressão completa cobre as provas afetadas de T2 e T3.
- Provas executadas: regressão completa do plan em HEAD `790f887`: `git diff --check 07466e6 790f887` (sem achado) e `git diff --check` na árvore (sem achado); P-REF sobre `skills/vibeflow/` (todos os paths `references/...` e `templates/...` citados existem, salvo placeholders `<...>`; nenhuma ocorrência de `/vibe-`, `vibe-<etapa>`, `scripts/`, `execution.json`, `--etapa` ou `-Etapa`); paths citados em `AGENTS.md`, `README.md` e `docs/` existem; os seis manifestos são JSON válido com somente `vibeflow` 10.0.0 onde há versão; `gitleaks detect --source . --redact --no-banner` (8.30.1): 83 commits, nenhum vazamento. Todos verdes.

## Cobertura da solicitação

- Origem e limites: solicitação original e trilha em `interview.md`; revisão de escopo S1 a S9 do humano em `spec.md`; plan aprovado. C1, C2 e C6 dependem de uso real, fora desta phase por decisão registrada. A simulação de condução dos cenários (a) a (j) pedida pelo líder foi feita só com o pacote.

| Item da solicitação e fonte (A*/C* quando houver) | Implementação | Evidência | Situação |
|---|---|---|---|
| Skill única `vibeflow` no lugar das oito `vibe-*`, sem aliases (interview, decisão 10, S8, A12) | `skills/vibeflow/`, manifestos, remoção de `vibe-*/`, `skills/vibe-*`, `docs/vibe-*`, `docs/tests/` | `git show --stat 790f887`; manifestos JSON; P-REF sem `vibe-*` | atendido |
| Líder macro: briefing, planeja, delega, critica, reconhece, decide; sem microgerência nem distância (decisões 3 a 6, A7) | `SKILL.md` seções 5 e 6, `references/delegation.md` | leitura cruzada; cenários (c) e (d) | atendido |
| Analyze e review nunca pelo coordenador (decisão 7, F4, A6) | `SKILL.md:10`, `references/analyze.md`, `references/review.md`, `delegation.md:16` | leitura cruzada | atendido |
| Host sem subagentes degradado com aviso; perfis não carregados degradam (F8, A11) | `SKILL.md` seção 7 | cenários (a) e (i): ausência de perfil vira pergunta para init, não Modo B (R1) | parcial |
| Rota proporcional; pedido pequeno sem cadeia nem `.vibeflow/` (decisão 2, F1, A2) | `SKILL.md` seção 2, `implement.md:12-14`, `review.md:9` | cenários (a) e (b): Express indefinido e contraditório (R2); medium sem commit nem review viável (R3) | parcial |
| Init como etapa 0, legado migrado, recarga do host (F2, A3) | `references/init.md` | cenário (g): bloco da cadeia não é inserido; CLAUDE.md preservado reabre o init (R4) | parcial |
| Phases antigas legíveis sem migração (S7, A13) | `disco.md:46-50`, `SKILL.md:61` | cenário (h): phase-20 `coordenacao-v1` não tem caixas e trava (R5) | parcial |
| `plan.md` atualizado inclusive na interrupção; retomada pelo disco (F5, F6, A8, A9) | `SKILL.md` seção 6, `implement.md` passo 1 | cenário (f): commit na parada contradiz a implement (R6); subestados de retomada sem derivação escrita (R7) | parcial |
| Papéis: redator grava artefatos de planejamento; finalizador só marca (decisão 4, S6) | `delegation.md:13-17` | `implement.md:13`, `implement.md:60`, `review.md:78` dão prosa ao finalizador (R8) | parcial |
| `/vibeflow <etapa>` com allowlist e gates (F7, S5, A10) | `SKILL.md` seção 3; `ARQUITETURA.md:22` | cenário (j) ok; argumento fora da allowlist sem regra operacional (R9) | parcial |
| Só texto, sem motores nem testes de código (S1, S9) | pacote só com `SKILL.md`, `references/`, `templates/` | `find skills -type f`; P-REF | atendido |
| Rota em `# Rota:` no primeiro artefato (S3) | `disco.md:38`, templates de interview, spec e review | leitura cruzada | atendido |
| Regras mecânicas escritas: `n`, slug, preservação, backup (S4) | `references/disco.md` | leitura | atendido |
| Ondas por `Arquivos:` disjuntos, prova afetada, regressão na review, duas rodadas, confirmação final (S6, decisão 9) | `implement.md`, `plan.md` passo 1.3, `review.md` | cenário (d) | atendido |
| Docs, `AGENTS.md`, README, ESCOPO e manifestos coerentes (plan T3) | `docs/vibeflow/`, `AGENTS.md`, `README.md`, `docs/ESCOPO.md` | paths existem; `ANALISE.md:62` e `ARQUITETURA.md:22` divergem do pacote (R5, R9); `AGENTS.md:33` (R2) | parcial |
| `execution.json` desde a interview (interview decisão 3 e 5, A5) | removido | S2: "Não existe `execution.json` nem relatório operacional na V2" | retirado explicitamente pelo humano |
| Motores únicos e paridade (C3, C4, C5) | removidos | S1, coluna Substitui | retirado explicitamente pelo humano |
| Rota max real sem perda, líder fora do micro, eficiência percebida (C1, C2, C6) | fora desta phase | S9 e plan Overview aprovado: evidência na primeira phase real com `/vibeflow` | retirado explicitamente pelo humano desta phase |

## Checklist de correções

### Required

- [x] R1: **Required** - `skills/vibeflow/SKILL.md:80` - Perfil ausente vira pergunta ao humano para rodar `/vibeflow init`, e `SKILL.md:96` só ativa o Modo B sem subagentes ou a pedido. A spec F8 (gatilho: "ausência de subagentes ou perfis exigidos não carregados") manda degradar para o Modo B. Cenário (a): troca de cor num repo sem init e com subagentes genéricos faz o líder pedir init, que cria `.vibeflow/`, `AGENTS.md`, perfis e commit, contra A2 e decisão 2; `delegation.md:7` ainda proíbe usar outro papel. Também não está escrito quais perfis são exigidos em Express, low e medium. - remédio: alinhar `SKILL.md` seções 5 e 7, `delegation.md` (Papéis e Host limitado) e `implement.md:32` a F8: perfis exigidos ausentes ou não carregados levam ao Modo B com aviso de uma linha, com a recomendação de init e recarga apenas quando a rota tem phase; declarar os perfis exigidos por rota. - prova: releitura do cenário (a) e (i) contra F8 e A2; P-REF e `git diff --check`. - source: F8, A2, A11 - gap: contradicts - papel: redator
- [x] R2: **Required** - `skills/vibeflow/SKILL.md:40` - "Express" é usado como rota (`SKILL.md:40-41,44,58,81`, `disco.md:38`, `implement.md:12-13,78`, `review.md:43`, `delegation.md:12`, perfis do implementador), mas a tabela de esforço de `templates/AGENTS.md:6-13`, declarada "única fonte da rota", não tem Express. O `AGENTS.md` raiz (`AGENTS.md:33`) define "Faixa Express (low ou medium)" sem phase nem artefato, o que contradiz o medium que abre phase no `review.md` (`implement.md:14`, `review.md:9`) e o "Express e low nunca abrem phase" de `disco.md:38`; `review.md:43` julga "review no Express", que não existe se Express é low. Sem `AGENTS.md`, a seção 2 também não diz de onde vem a tabela para classificar um pedido sem phase. O líder adivinharia nos cenários (a) e (b). - remédio: definir Express numa única casa (recomendação: sinônimo de low, sem phase nem review, com o critério de saída de `SKILL.md:44`), retirar a review "no Express" de `review.md:43` ou reescrevê-la para medium, alinhar `AGENTS.md:33` raiz e o perfil do implementador (`Express, low ou medium sem plan`, como `delegation.md:12`), e dizer em `SKILL.md` seção 2 que, sem `AGENTS.md`, a tabela vem de `templates/AGENTS.md`. - prova: releitura dos cenários (a) e (b); P-REF e `git diff --check`. - source: decisão 2, F1, A2 - gap: contradicts - papel: redator
- [x] R3: **Required** - `skills/vibeflow/references/implement.md:14` - A rota medium não fecha. O implementador entrega "sem plan" e nenhum passo manda commitar o código; a review então: bloqueia com árvore suja em path de código (`review.md:61`), abre R* para todo path fora da união dos `Arquivos:` porque não há T* (`review.md:53`), não tem diff de phase porque não há `task(...)` (`review.md:10`), e a finalização só faz staging de `<path da phase> AGENTS.md` e interrompe com path fora da phase (`review.md:99-100`). Cenário (b) para na review ou no push sem o código. - remédio: escrever o fluxo medium em `implement.md` (quem commita, com que mensagem e quando: recomendação, finalizador commita a entrega com prova proporcional verde antes da review) e em `review.md` (base do diff, auditoria do diff sem T* contra o brief, finalização), mantendo `SKILL.md:59` coerente. Formato da mensagem de commit é decisão do humano (Decisões abaixo). - prova: releitura do cenário (b) de ponta a ponta até o push. - source: decisão 2, AGENTS.md tabela de esforço (medium: implement → review) - gap: missing - papel: redator
- [x] R4: **Required** - `skills/vibeflow/references/init.md:24` - O init só atualiza o bloco `VIBEFLOW:CADEIA` "entre" os delimitadores e não diz o que fazer quando eles não existem: `AGENTS.md` existente de outro projeto, `AGENTS.md` nascido de `CLAUDE.md` (`init.md:23`) ou o próprio `AGENTS.md` raiz deste repo, que não tem delimitadores. Nesses casos a tabela de esforço nunca entra, e `SKILL.md` seção 2 fica sem fonte de rota. A v1 inseria bloco e aviso depois do título (`07466e6:vibe-init/scripts/init.py`, `update_header`). Além disso, `CLAUDE.md` do usuário preservado por decisão humana (`init.md:27`) continua presente, e `SKILL.md:17` manda a rota com phase passar pelo init a cada run: laço no cenário (g). - remédio: em `init.md` passo 2, inserir aviso e bloco logo após o título quando não houver nenhum delimitador, como na v1; em `SKILL.md:17` e `init.md` Entrada, disparar o init por legado somente quando o legado ainda não foi tratado (`AGENTS.md` ausente, sem o bloco, ou `REGRAS.md`/`.vibeflow/REGRAS.md` do antigo VibeFlow), não por `CLAUDE.md` mantido pelo humano. - prova: releitura do cenário (g) com `CLAUDE.md` legado e com `AGENTS.md` sem bloco. - source: F2, A3 - gap: partial - papel: redator
- [x] R5: **Required** - `skills/vibeflow/references/disco.md:46` - T* concluída exige caixa `[x]` confirmada por commit, e caixa ausente com commit é "inconsistência a diagnosticar". Phases `coordenacao-v1` não marcavam caixas: `phase-20-cadeia-alinhada-ao-implement/plan.md:44` (e T2 a T9) estão `[ ]` com `task(T1,...,T9)` em `8d1e6e5`, e a phase-19 também não tem caixa marcada. Com `disco.md:50` e o gate de review (`SKILL.md:59`), a re-review pendente da phase-20 trava no cenário (h). `ANALISE.md:62` afirma que caixas "existem em todas as phases", e `ARQUITETURA.md:102` repete a premissa. - remédio: em `disco.md` (Phases da v1), declarar que em `coordenacao-v1` a conclusão de T* vem do ID no commit `task(...)` do `git log`, sem caixa, e que isso não é inconsistência; ajustar `ANALISE.md:62` e `ARQUITETURA.md:102`. - prova: releitura do cenário (h) sobre a phase-20 real. - source: S7, A13 - gap: partial - papel: redator
- [x] R6: **Required** - `skills/vibeflow/SKILL.md:90` - Na parada, o líder delega ao finalizador "o commit do que já tem prova verde". `implement.md:43` diz que a caixa só é marcada no commit, e `implement.md:52` só permite o commit com a integração verde, depois da validação; `ANALISE.md:58` e a spec F6 descrevem a parada só com o estado no `plan.md`. Commitar T* com prova afetada verde na parada conclui T* sem validação integrada (cenário f). - remédio: em `SKILL.md:90`, limitar o checkpoint ao estado no `plan.md` (pronto, em andamento, pendente) e permitir commit somente quando a integração já estiver verde, como `implement.md:52`. - prova: releitura do cenário (f) contra `implement.md` passos 1 a 3. - source: F6, A9 - gap: contradicts - papel: redator
- [x] R7: **Required** - `skills/vibeflow/references/disco.md:41` - Sem o motor, a derivação "estado do disco → etapa atual" não está escrita. `SKILL.md:19-21` lista o que ler e `disco.md:41-46` define etapa e T* concluídas, mas não há regra para os subestados da implementação e da review que a retomada encontra: plan aprovado com T* parcialmente concluídas e código não commitado na árvore; todas as T* concluídas sem `review.md`; `review.md` `request-changes` com todos os R* `[x]` (re-review); `review.md` `rascunho` com Approve proposto (aguarda confirmação); phase medium com só `review.md`. No cenário (f) o líder adivinharia a etapa, o que `SKILL.md:76` proíbe. - remédio: acrescentar em `disco.md` (Estado da phase) uma tabela curta estado → etapa e próximo responsável, cobrindo esses casos, e referenciá-la de `SKILL.md` seção 1. - prova: releitura do cenário (f) com cada subestado. - source: F6, S2, S5, A1, A9 - gap: missing - papel: redator
- [x] R8: **Required** - `skills/vibeflow/references/implement.md:60` - R* sem `papel` com remédio em `plan.md`, `spec.md` ou `AGENTS.md` vai ao finalizador (também `review.md:78` e `templates/review.md:38`), e `implement.md:13` manda o finalizador acrescentar T* no plan. `delegation.md:17` só autoriza o finalizador a marcar status, aprovação, caixas, `[x]`, resumo curto e critérios; `delegation.md:13` tira `plan.md` e `spec.md` do redator durante a implementação. Um remédio como "declarar o path em `Arquivos:`" (exigido por `review.md:53`) ou uma T* nova fica sem dono autorizado, e o finalizador escreveria prosa contra a decisão 4 e a divisão de papéis pedida. - remédio: rotear prosa de `plan.md`, `spec.md` e `AGENTS.md` (fora de `## Decisões vigentes`) ao redator com `papel: redator`, com a exceção explícita em `delegation.md:13` e nos dois perfis do redator; manter o finalizador só nas marcações; ajustar `implement.md:13,60`, `review.md:78` e `templates/review.md:38`. - prova: releitura do roteamento de R* e do Express com phase ativa contra `delegation.md`. - source: decisão 4, S6 - gap: contradicts - papel: redator
- [x] R9: **Required** - `docs/vibeflow/ARQUITETURA.md:22` - O contrato diz que argumento fora da allowlist é recusado com a allowlist nomeada, mas `SKILL.md` não tem essa regra nem diz como tratar `/vibeflow <texto livre>`, como "/vibeflow troque a cor do botão". O líder se contradiz entre recusar (ARQUITETURA, spec F7) e classificar o texto como pedido (description e seção 2). - remédio: colocar em `SKILL.md` seção 3 a regra de entrada (primeira palavra na allowlist seleciona a etapa; demais casos conforme a decisão do humano abaixo) e alinhar `ARQUITETURA.md:22`. - prova: releitura do cenário (j) e de `/vibeflow` com texto livre. - source: F7, A10 - gap: partial - papel: redator

### Nit

- [x] R10: **Nit** - `skills/vibeflow/references/plan.md:8` - A aprovação implícita por pedido direto tem quatro casas com redações diferentes: `SKILL.md:61` (artefato anterior completo e único pendente), `plan.md:8` (spec ou design, sem condição de completude; aprovaria os dois), `design.md:8` e `implement.md:18`. - remédio: manter a regra só em `SKILL.md:61` e fazer as referências apontarem para ela. - prova: releitura das quatro casas. - papel: redator
- [x] R11: **Nit** - `AGENTS.md:73` - "Não commitar: `init-report.json`, `init-pending.json`, `*-report.json` e `*-pending.json`" descreve relatórios que a V2 não gera (S2, `ARQUITETURA.md:55`). - remédio: remover a linha ou reescrevê-la como regra histórica das phases v1. - prova: `git diff --check` e releitura da seção Git. - papel: redator
- [x] R12: **Nit** - `skills/vibeflow/references/review.md:61` - "Árvore suja em path de código ou teste" bloqueia a regressão, e `review.md:62` define código como todo path fora de `.vibeflow/`; um registro novo em `.erros-encontrados/`, exigido pelas regras do projeto, bloquearia a review, enquanto `review.md:53` o trata como Nota. Nesta review, `.erros-encontrados/2026-10-14-init-ps1-symlink-encadeado-hash-mismatch.md` estava não rastreado e não é input de nenhuma prova. - remédio: excluir `.erros-encontrados/` de "path de código ou teste" em `review.md:62`, como em `review.md:53`. - prova: releitura do passo 4 contra o passo 3.1. - papel: redator

## Notas

- Severidade: o líder pediu Critical, Important e Suggestion; esta review usa as seções do template (Critical, Required, Nit). Required corresponde a Important e Nit a Suggestion. Não houve Critical.
- Organização: `SKILL.md` (100 linhas) segue o corpo do AGENTS.md §7; as oito referências de etapa têm o mesmo esqueleto (Entrada, Quem faz, Passos, Saída, Fechar); nenhuma referência órfã ou faltante; `disco.md` concentra as regras mecânicas.
- Os perfis carregados neste host ainda são os da v1 (citam `vibe-review` e `coordenacao-v1`); o uso real da V2 aqui exige reinstalar os perfis e recarregar o host.
- `.erros-encontrados/` guarda registros sobre motores e testes da v1 já removidos; não são path desta phase.

## Veredito vigente

- [ ] **Approve**: origem suficiente, obrigações atendidas ou retiradas explicitamente pelo humano e nenhum R* de correção em `[ ]`
- [x] **Request changes**: há R* de correção em `[ ]`

## Handoff

implement

- [ ] Aprovação humana (leu o arquivo e confirmou)

- Chat: no Modo A, esta review roda em revisor de contexto limpo, a pedido do líder; sem subagentes, roda num chat novo com `/vibeflow review`. As correções seguem pela etapa implement, com corretor ou redator conforme o `papel` de cada R*; sem subagentes, num chat novo com `/vibeflow implement`. Após Approve e confirmação humana, o handoff é a finalização Git da phase. O `review.md` vivo e o diff são a ponte.

## Finalização Git da phase

- Pré-condições: Approve final confirmado, todas as `T*` concluídas, todos os R* de correção fechados, prova necessária da integração verde, `git diff --check` e gitleaks quando previsto.
- Commit final: `chore(phase-N): finalize review`, somente com paths residuais autorizados e sem `Co-Authored-By`; sem mudanças residuais, manter o último commit integrado ou da task.
- Push: `git push` para o upstream atual, sem `--force`. Registrar hash/HEAD, paths e resultado; falha mantém o handoff bloqueado.

## Etapas

### Etapa 1 - first-pass - T1 a T3, diff 07466e6..790f887, regressão completa, simulação dos cenários (a) a (j)

- Tipo: final
- Marco e justificativa: integração final
- T* abertas fora do marco: nenhuma
- Provas reaproveitadas: nenhuma
- Provas executadas: regressão completa do plan em HEAD `790f887` (P-DIFF, P-REF, paths de docs, JSON dos manifestos, gitleaks 8.30.1), todas verdes
- Execução: todo path do diff fora de `.vibeflow/` está na união dos `Arquivos:` (T1 cobre a raiz pelo curinga `vibe-*/` e rodou sozinha na onda 1; T2 `skills/vibeflow/` e T3 docs, `AGENTS.md`, README, ESCOPO e manifestos são disjuntas); commit `task(T1,T2,T3)` com caixas marcadas e sem `Co-Authored-By`; consumidores compartilhados entre T2 e T3 conferidos, com divergências em `ARQUITETURA.md:22`, `ARQUITETURA.md:102` e `ANALISE.md:62` (R5, R9)
- Leu: solicitação e trilha de `interview.md`, `spec.md` (S1 a S9, F1 a F10, decisões), `plan.md`, `analyze.md`, `AGENTS.md`, todo o pacote `skills/vibeflow/`, `docs/vibeflow/`, `README.md`, `docs/ESCOPO.md`, manifestos, phases 18 a 20 como fixtures v1 e o init da v1 em `07466e6` para comparação
- Cobertura: matriz criada; 9 itens parciais
- Abriu: R1, R2, R3, R4, R5, R6, R7, R8, R9, R10, R11, R12
- Fechou: nenhum
- Veredito desta etapa: Request changes

<!-- etapa seguinte: copie ### Etapa N abaixo. Não apague as anteriores. -->
