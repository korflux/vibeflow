# Plan: fluxo enxuto com aprovação única, plan como tracking e testes por critério
# Alvo: phase-4-fluxo-enxuto-v5
# Status: aprovado
# Spec: spec.md (mesma pasta)

## Overview

Reescreve o pacote `skills/vibeflow/` para o contrato 5.0.0 descrito na spec: aprovação única na spec, plan como checklist ordenado, analyze silencioso, implement com checkpoints, testes por critério, review focada em produto, rotas `low`, `medium` e `high` com marcador `risco`, e skill só por chamada explícita. Este plan ainda segue o contrato vigente (T*, `Estado:`, ondas), porque a phase roda com a skill atual; o formato novo vale a partir da próxima phase.

- **Design:** N/A, a entrega não tem UI.
- **Decisão técnica do líder:** o marcador `risco` é gravado como linha opcional `# Risco: <motivo>` no cabeçalho da `spec.md`, logo após `# Rota: high`. Reversível no T1 se a redação do contrato pedir outra forma.
- **Versão:** o repo não tem arquivo de versão nem tag. A 5.0.0 fica registrada no `AGENTS.md` e no `README.md` (T8), sem criar arquivo novo.

## Prontidão das provas

- Node 18+ para `node --test`: local · ok (v24.22.1)
- gitleaks para a varredura de segredos: local · ok (8.30.1)
- Git: local · ok

### Regressão completa

- `node --test`
- `git diff --check`
- `gitleaks detect --source . --redact --no-banner`
- Revisão de consistência dos Comandos do projeto (`AGENTS.md`): todo path deste repo citado em `skills/vibeflow/`, `README.md` e `AGENTS.md` existe; nenhum arquivo cita a v1, `interview.md`, `design.md` ou `analyze.md` como artefato vivo, as rotas `xhigh`, `max` ou Express, ou os papéis corretor e finalizador.

## Tasks

### T1: contrato de disco 5.0.0
- [x] T1 concluída
- **Estado:** concluída
- **Resumo:** disco.md com três artefatos, três rotas, passo numerado, checkpoint, achados do analyze, commits do líder, compatibilidade e glossário; próximo: onda 2
- **Spec:** A2, A3, A9, decisões 1 a 3, 8, suposição 12
- **Deps:** nenhuma
- **O quê:** Resultado principal: prosa (redator). `references/disco.md` passa a ter: artefatos vivos `spec.md`, `plan.md` e `review.md`; `# Rota:` com `medium`, `high` e `mvp`, e `# Risco:` opcional na spec; formato do passo do plan (número na ordem de execução, letra para paralelos, `Arquivos:`, prova, critério, caixa como estado) e seção de achados do analyze no fim do plan; tabela de estados da phase reescrita para essas etapas; commits `task(phase-N:2a,2b)` e `task(phase-N:Rn)` feitos pelo líder; finalização pelo líder; phase fechada no formato antigo reconhecida como fechada; glossário curto dos termos que as demais T* usam (passo, checkpoint, risco, achado fora do recorte).
- **Aceite:** o disco descreve só os três artefatos e as três rotas, e toda regra mecânica que os scripts e as referências vão citar tem casa única nele.
- **Arquivos:** `skills/vibeflow/references/disco.md`
- **Prova afetada:** `git diff --check`; verificador confere que cada regra mecânica citada nas decisões 1 a 3 e 8 e na suposição 12 tem casa no `disco.md` e que nenhum path citado inexiste

### T2: scripts leem o contrato 5.0.0
- [x] T2 concluída
- **Estado:** concluída
- **Resumo:** estado.mjs lê passos, checkpoint e achados do analyze, progresso em cinco etapas, filtra .erros-encontrados/; ondas.mjs removido; 60 testes verdes; checkpoint da onda verde
- **Spec:** A3, A11, C1
- **Deps:** T1
- **O quê:** `_disco.mjs` e `estado.mjs` leem os passos numerados do plan novo (caixa, número, letra, `Arquivos:`), calculam etapa e progresso sobre spec, plan e review, informam o próximo passo ou grupo paralelo e acusam sobreposição de `Arquivos:` entre passos irmãos. `ondas.mjs` é removido, porque a ordem e os grupos passam a estar no próprio plan. Phase fechada no formato antigo é reconhecida como fechada; phase aberta no formato antigo é relatada como inconsistência. Os testes de comportamento cobrem o plan novo, a phase antiga fechada, a antiga aberta e a sobreposição entre irmãos.
- **Aceite:** `estado.mjs --json` devolve etapa, progresso e próximo passo corretos nos cenários de disco temporário, e `node --test` passa.
- **Arquivos:** `skills/vibeflow/scripts/`, `tests/scripts/`
- **Prova afetada:** `node --test`

### T3: líder, delegação e chamada explícita
- [x] T3 concluída
- **Estado:** concluída
- **Resumo:** SKILL.md com chamada explícita, aprovação única e cinco papéis; delegation.md; agents/openai.yaml; checkpoint da onda verde
- **Spec:** A1, A4, A5, A9, A10, decisões 1, 4, 5, 8, 9, suposições 11 e 13
- **Deps:** T1
- **O quê:** Resultado principal: prosa (redator), mais um arquivo de configuração. `SKILL.md` com frontmatter `disable-model-invocation: true` e `description` sem gatilhos de comportamento; abertura, classificação nas três rotas, gates com a aprovação única, roteamento sem design e com analyze em toda rota com plan; líder que não coda nem roda teste e que marca, commita e finaliza; Modo B, interrupção e progresso ajustados. `references/delegation.md` com os cinco papéis (explorador, implementador, redator, verificador só no checkpoint, revisor), sem corretor nem finalizador, e conferência do líder sem execução de prova. `skills/vibeflow/agents/openai.yaml` com `policy.allow_implicit_invocation: false`.
- **Aceite:** o `SKILL.md` e a delegação descrevem a aprovação única, as três rotas, os cinco papéis e o líder sem código nem teste, e o Codex tem a política de invocação explícita.
- **Arquivos:** `skills/vibeflow/SKILL.md`, `skills/vibeflow/references/delegation.md`, `skills/vibeflow/agents/openai.yaml`
- **Prova afetada:** `git diff --check`; verificador confere o frontmatter, o YAML e que todo path citado existe ou é criado por outra T* deste plan

### T4: interview que explora o código e escreve a spec
- [x] T4 concluída
- **Estado:** concluída
- **Resumo:** interview explora o código e grava a spec de cinco seções; templates/interview.md removido; checkpoint da onda verde
- **Spec:** A2, decisões 2 e 8, suposição 10
- **Deps:** T1
- **O quê:** Resultado principal: prosa (redator). `references/interview.md` começa pela exploração do código que o pedido toca, pergunta a partir dos pontos encontrados, inclui as decisões visuais do humano, cobre modelo de ameaça e rollback quando há `risco`, tem tamanho proporcional à clareza do pedido e grava direto na `spec.md`. `references/spec.md` e `templates/spec.md` com as cinco seções da decisão 2. `templates/interview.md` é removido. Os catálogos de `references/interview/` e `references/spec/ui-visual-direction.md` perdem as menções a `interview.md` e ao design como etapa.
- **Aceite:** a interview e a spec produzem um único arquivo com objetivo, pontos do projeto, decisões, critérios de aceite e fora do escopo.
- **Arquivos:** `skills/vibeflow/references/interview.md`, `skills/vibeflow/references/interview/`, `skills/vibeflow/references/spec.md`, `skills/vibeflow/references/spec/`, `skills/vibeflow/templates/spec.md`, `skills/vibeflow/templates/interview.md`
- **Prova afetada:** `git diff --check`; verificador confere as cinco seções no template e que todo path citado existe

### T5: plan como checklist e analyze silencioso
- [x] T5 concluída
- **Estado:** concluída
- **Resumo:** plan como checklist sem aprovação; analyze silencioso com achados no plan; templates/analyze.md removido; checkpoint da onda verde
- **Spec:** A3, A4, decisões 3, 4 e 5
- **Deps:** T1
- **O quê:** Resultado principal: prosa (redator). `references/plan.md` e `templates/plan.md` com o checklist na ordem de execução, paralelos por letra, checkpoints marcados, sem aprovação humana e sem `Estado:`, `Resumo:`, IDs T* nem seções de risco e cobertura. `references/analyze.md` e `references/analyze/coverage.md` com o analyze em contexto limpo em toda phase com plan, correção direta do plan, seção de achados no fim do `plan.md` e parada só quando um achado muda decisão da spec. `templates/analyze.md` é removido.
- **Aceite:** o plan é um tracking ordenado sem aprovação, e o analyze não grava artefato próprio nem pede aprovação.
- **Arquivos:** `skills/vibeflow/references/plan.md`, `skills/vibeflow/templates/plan.md`, `skills/vibeflow/references/analyze.md`, `skills/vibeflow/references/analyze/`, `skills/vibeflow/templates/analyze.md`
- **Prova afetada:** `git diff --check`; verificador confere que o formato do passo bate com o `disco.md` do T1 e com o que o `estado.mjs` do T2 lê

### T6: implement, testes e review
- [x] T6 concluída
- **Estado:** concluída
- **Resumo:** implement com checkpoints e política de testes; review focada em produto com regressão única; checkpoint da onda verde
- **Spec:** A5 a A8, decisões 5, 6 e 7
- **Deps:** T1
- **O quê:** Resultado principal: prosa (redator). `references/implement.md` com implementador que coda e prova o passo, falha que volta a ele, líder que confere, marca e commita, checkpoints com verificador de contexto limpo e a política de testes (teste por critério, reaproveitar antes de criar, testes afetados pelo grafo de imports, sem E2E no passo). `references/review.md` e `templates/review.md` com a review focada em produto, regressão única em segundo plano e do mais barato ao mais caro, re-review só para Critical e Required, Nit fechado com testes afetados, flake e achado fora do recorte em `.erros-encontrados/`, auditoria de processo como nota, duas rodadas no máximo e resumo no chat para a confirmação do push. `references/definition-of-done.md`, `references/chrome-devtools.md` e `references/review/` ajustados ao que essas regras tocam.
- **Aceite:** um passo sem falha passa só pelo implementador e pelo líder, e uma review sem Critical nem Required roda a regressão completa uma vez.
- **Arquivos:** `skills/vibeflow/references/implement.md`, `skills/vibeflow/references/review.md`, `skills/vibeflow/references/review/`, `skills/vibeflow/templates/review.md`, `skills/vibeflow/references/definition-of-done.md`, `skills/vibeflow/references/chrome-devtools.md`
- **Prova afetada:** `git diff --check`; verificador confere que nenhum trecho manda o líder rodar teste e que a review cita a regressão uma única vez fora da re-review com código compartilhado

### T7: design removido, perfis e init com cinco papéis
- [x] T7 concluída
- **Estado:** concluída
- **Resumo:** design removido; cinco perfis idênticos nos dois hosts; init com redator e commit do líder; checkpoint da onda verde
- **Spec:** A5, suposições 10 e 11
- **Deps:** T1
- **O quê:** Remove `references/design.md`, `references/design/` e `templates/design.md`. Remove os perfis `corretor` dos dois hosts e ajusta implementador (corrige falha de passo e achado de código, política de testes), verificador (só checkpoint), redator (achado de prosa), revisor (analyze silencioso e review nova) e explorador. `references/init.md` instala e confere cinco perfis.
- **Aceite:** não existe referência nem template de design, os dois hosts têm os mesmos cinco perfis e o init os instala.
- **Arquivos:** `skills/vibeflow/references/design.md`, `skills/vibeflow/references/design/`, `skills/vibeflow/templates/design.md`, `skills/vibeflow/templates/agents/`, `skills/vibeflow/references/init.md`
- **Prova afetada:** `git diff --check`; verificador confere que os perfis Claude e Codex de cada papel dizem a mesma coisa e que o init lista exatamente os cinco

### T8: regras do projeto, README e versão 5.0.0
- [x] T8 concluída
- **Estado:** concluída
- **Resumo:** AGENTS.md, template e README no contrato 5.0.0, versão registrada; pacote de 30368 para 21467 palavras; próximo: review
- **Spec:** A9, A10, A12, C1, C3
- **Deps:** T2, T3, T4, T5, T6, T7
- **O quê:** Resultado principal: prosa (redator). `templates/AGENTS.md` com a tabela de três rotas e o marcador `risco`, e o bloco da cadeia valendo só com `/vibeflow`. `AGENTS.md` deste repo com o mesmo bloco, a estrutura do pacote sem design, analyze e `ondas.mjs`, a regra da `description` trocada pela chamada explícita e o registro da versão 5.0.0. `README.md` com instalação, uso e a mudança major para quem tem phases antigas. Medição do tamanho do pacote antes e depois, por ferramenta, para o C3.
- **Aceite:** as regras e o README descrevem o contrato 5.0.0 sem citar o antigo como vigente, e o pacote tem menos palavras que antes.
- **Arquivos:** `skills/vibeflow/templates/AGENTS.md`, `AGENTS.md`, `README.md`
- **Prova afetada:** `node --test`; `git diff --check`; revisão de consistência da Regressão completa sobre o pacote inteiro

## Colaboração

- Ondas: onda 1 com T1; onda 2 com T2, T3, T4, T5, T6 e T7 em paralelo; onda 3 com T8.
- Benefício: depois que o T1 fixa o contrato e o glossário, as seis frentes tocam arquivos disjuntos e podem andar juntas; o T8 consolida o que é compartilhado.
- Ownership: o vocabulário comum mora no glossário do `disco.md` (T1); uma T* da onda 2 que precise mudar um termo volta ao líder antes de editar.

## Handoff

implement

- Chat: com a aprovação, `/vibeflow implement` segue neste chat, ou num chat novo, que retoma pelo disco.

- [x] Aprovação humana (leu o arquivo e confirmou), 24/10/2026: "Plan aprovado. Pode ir pro implement."
