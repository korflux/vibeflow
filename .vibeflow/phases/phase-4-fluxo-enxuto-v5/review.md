# Review: fluxo enxuto com aprovação única, plan como tracking e testes por critério
# Alvo: phase-4-fluxo-enxuto-v5
# Status: aprovado

## Veredito

- [x] **Approve**: critérios atendidos e provados, regressão verde e nenhum Critical ou Required aberto
- [ ] **Request changes**: há Critical ou Required aberto

## Critérios de aceite

| Critério | Evidência (teste e resultado) | Situação |
|---|---|---|
| A1 | `SKILL.md:11` e `:67` (aprovação da spec encadeia plan, analyze, implement e review); `references/plan.md:41` e `references/analyze.md:95` (sem pedido de aprovação); `references/disco.md:53`. Prosa: prova pela revisão de consistência | atendido |
| A2 | `references/disco.md:21-27` (só `spec.md`, `plan.md`, `review.md`); `references/interview.md:3` (sem artefato próprio); `templates/spec.md` com Objetivo, Pontos do projeto, Decisões (com a pergunta), Critérios de aceite e Fora do escopo; templates de interview, design e analyze removidos | atendido |
| A3 | `references/disco.md:61-73` (ID numérico na ordem, letra para paralelo, estado só na caixa); `templates/plan.md:12`; `tests/scripts/disco.test.mjs` (lê o passo, agrupa, numeração) e `tests/scripts/estado.test.mjs` (próximo passo e grupo), 60/60 verdes | atendido |
| A4 | `references/analyze.md:3`, `:64-65`, `:84-85`; `references/disco.md:93-102`; teste `plan sem Achados do analyze` e `a seção Achados do analyze marca o analyze como rodado` verdes | atendido |
| A5 | `SKILL.md:10`, `references/delegation.md:131` e `:154`, `references/implement.md:28` e `:39-46`; verificador só no checkpoint. Ressalva: Modo B (`SKILL.md:117`) mantido pela suposição 13, e R2 abaixo (finalização) | atendido, com R2 como Nit |
| A6 | `references/review.md:31-41` e `:70-71` (uma execução; re-review só reroda o que falhou ou com código compartilhado); `references/disco.md:178` | atendido; R1 bloqueia o caminho até a review |
| A7 | `references/implement.md:98-106` (Política de testes, casa única); `references/plan.md:24`; perfil implementador | atendido |
| A8 | `references/review.md:38` e `:51`; `references/disco.md:176-177`; `templates/review.md` (Notas) | atendido |
| A9 | `templates/AGENTS.md:59-67` e `AGENTS.md:8-16` com `low`, `medium`, `high` e `# Risco:`; `references/disco.md:49-50`; `_disco.mjs:45` (`ROTAS`) e teste `rota fora de medium, high e mvp` verde | atendido |
| A10 | `SKILL.md:5` (`disable-model-invocation: true`) e `:4` (description sem gatilho); `agents/openai.yaml` com `policy.allow_implicit_invocation: false`, formato conferido na documentação do Codex (`codex-rs/skills/.../agents/openai.yaml`); `templates/AGENTS.md:57` | atendido |
| A11 | `scripts/estado.mjs` substitui `ondas.mjs` (próximo passo ou grupo, sobreposição de `Arquivos:`); compatibilidade em `_disco.mjs:76-80`; testes de phase antiga fechada e aberta verdes. Execução real neste repo: phase-4 (plan com T*) relatada como formato antigo aberto, código 1, conforme a suposição 12 | atendido |
| A12 | `AGENTS.md:57` (versão 5.0.0), estrutura sem design, analyze e `ondas.mjs`; `README.md:97-103` (migração) | atendido |
| C1 | `node --test`: 60 testes, 60 verdes; revisão de consistência: nenhum path deste repo citado inexiste e as citações ao contrato anterior estão só em Compatibilidade, init (perfil `corretor` obsoleto) e migração do README | atendido |
| C2 | Depende da primeira phase real num projeto consumidor | limitação declarada pelo líder; não verificável nesta review |
| C3 | `wc -w` sobre `.md`, `.yaml` e `.toml` do pacote: 30368 em `f26cb61`, 21467 em `HEAD` | atendido |

## Achados

### Required

- [x] R1: **Required** - `skills/vibeflow/SKILL.md` - o gate da review (`SKILL.md:65`) e o da Entrada de `references/review.md:7`, repetido na Finalização (`references/review.md:85`, "com o gate da Entrada satisfeito"), exigem passos e checkpoints "marcados com commit", mas `references/disco.md:90` e `references/implement.md:46` dizem que a caixa do checkpoint não tem commit próprio e entra no commit seguinte da phase. Como o checkpoint vem logo depois do último passo do grupo, o último checkpoint de uma phase normalmente só é commitado no `chore(<alvo>): finalize review`; lido ao pé da letra, o líder não pode abrir a review nem finalizar (o gate da finalização depende do commit que a própria finalização cria). O `estado.mjs` (linha "Todos os passos e checkpoints marcados") já segue o `disco.md` e não exige commit da caixa do checkpoint - remédio: em `SKILL.md:65` e `references/review.md:7`, exigir passos marcados com commit e checkpoints marcados, com a marcação do checkpoint entrando no commit seguinte da phase conforme `references/disco.md` (Checkpoint), sem nova regra de commit - prova: revisão de consistência entre `SKILL.md`, `references/review.md`, `references/implement.md` e `references/disco.md` - papel: redator

### Nit

- [x] R2: **Nit** - `skills/vibeflow/references/review.md` - Finalizar, passo 3 (`references/review.md:89`), manda o líder executar `git diff --check` e gitleaks, enquanto `SKILL.md:10` e `references/delegation.md:131` e `:154` proíbem o líder de executar comando de prova fora do Modo B; quando esses comandos estão na Regressão completa, a finalização ainda repete parte dela - remédio: dizer em `references/review.md` que a checagem de pré-push é exceção nomeada do líder (ou exigir que conste na regressão registrada do revisor e só ser conferida pelo líder), e citar a exceção em `SKILL.md`, seção 5, item 3 - prova: revisão de consistência entre `SKILL.md`, `references/delegation.md` e `references/review.md` - papel: redator
- [x] R3: **Nit** - `skills/vibeflow/templates/agents/claude/revisor.md` - o perfil (linha 10) autoriza no analyze só o `plan.md` e reserva `.erros-encontrados/` à review, mas `references/delegation.md:15` autoriza o revisor a gravar `.erros-encontrados/` "nos dois" (analyze e review); o mesmo texto está em `templates/agents/codex/revisor.toml` - remédio: alinhar os dois perfis à delegação ("no analyze, o `plan.md`; na review, o `review.md`; nos dois, `.erros-encontrados/`") - prova: comparação dos corpos Claude e Codex do revisor e revisão de consistência com `references/delegation.md` - papel: redator
- [x] R4: **Nit** - `tests/scripts/disco.test.mjs` - a linha 104 ("Mesmo número em dois trechos do arquivo") só afirma `length > 0`, sem dizer qual achado espera; passaria com qualquer achado do plan - remédio: afirmar o achado esperado (numeração fora de sequência no passo 1b, esperado 3) com `deepEqual` ou `match` - prova: `node --test` - papel: implementador

## Notas

- Commits da phase: `328f13a` (T1), `90db230` (T2 a T7) e `3e4ec33` (T8), todos `task(phase-4:...)` e sem `Co-Authored-By`. Nenhum path alterado fora de `skills/vibeflow/`, `AGENTS.md`, `README.md`, `tests/scripts/` e da pasta da phase; os paths batem com os `Arquivos:` das T*.
- Esta phase usa o formato antigo (plan com `### T<n>:`), por decisão registrada no plan. O `estado.mjs` da 5.0.0 a relata como "formato antigo aberto" (código 1) até o `review.md` ficar `aprovado` sem R* aberto; depois disso ela conta como antiga fechada (`references/disco.md`, Compatibilidade). A review seguiu as regras novas de `references/review.md` com a adaptação do cabeçalho pedida pelo líder.
- Status: na etapa 1 o veredito foi Request changes, e o líder passou o status a `request-changes`. Na etapa 2 o veredito proposto é Approve; pela regra nova (`references/review.md:59`), o status correspondente é `rascunho`, e a troca fica com o líder.
- A5 e Modo B: no Modo B o próprio chat executa a prova do passo (`references/implement.md:58`). A spec manteve o Modo B sem mudança de regra (suposição 13); não é achado.
- `references/interview/refinement-criteria.md:53` cita "a v1" de um produto, não a v1 do VibeFlow; arquivo fora do diff.
- Scripts: Git chamado só por `execFileSync('git', [...])` com argumentos em lista e sem shell (`_disco.mjs:333-339`); somente leitura; nenhuma divergência material encontrada entre `_disco.mjs`/`estado.mjs` e a tabela de estados de `references/disco.md`. Segurança e banco: N/A, o diff não toca entrada externa, segredo nem persistência.
- Nenhum achado fora do recorte; nenhum registro novo em `.erros-encontrados/`.

## Aprovação humana

- [x] Aprovação humana (confirmou no chat o resumo do líder), 24/10/2026: "Aprovo a review da phase-4 e autorizo o push."

## Etapas

### Etapa 1 - review - f26cb61..3e4ec33

- Regressão: em `HEAD` 3e4ec334409a456b9063e0ccf3be88106c8f5b9e, árvore limpa, em segundo plano e do mais barato ao mais caro: `git diff --check f26cb61..HEAD` e `git diff --check` limpos; `node --test` (Node v24.22.1) com 60 testes, 60 verdes, 0 falhas; `gitleaks detect --source . --redact --no-banner` com 102 commits varridos e nenhum vazamento; revisão de consistência sem path ausente nem contrato anterior citado como vigente. Nenhum flake.
- Abriu: R1, R2, R3, R4
- Veredito: Request changes

### Etapa 2 - re-review - R1

- Diff da correção: `3e4ec33..642290d`, commit `task(phase-4:R1,R2,R3,R4)`. Os IDs do commit são exatamente os R* marcados `[x]` desde a etapa 1 (R1 a R4); nenhum R* aberto.
- R1: `SKILL.md:65` e `references/review.md:7` exigem agora passos marcados com commit e checkpoints marcados, com a marcação do checkpoint no commit seguinte da phase, apontando para `references/disco.md` (Checkpoint); a Finalização (`references/review.md:85`) deixou de depender do gate da Entrada e usa a mesma regra. Não resta "marcados com commit" aplicado a checkpoint no pacote. A regra fica coerente com `references/disco.md:90`, `references/implement.md:46` e o `estado.mjs`. Fechado.
- Nits, conferidos só pela prova afetada, sem novo julgamento: R2 com `git diff --check 3e4ec33..642290d` e `git diff --check` limpos; R3 com os corpos dos perfis revisor Claude e Codex idênticos; R4 com `node --test tests/scripts/disco.test.mjs`, 16 testes, 16 verdes.
- Regressão: não reexecutada por completo. A correção toca prosa da skill, dois perfis e uma asserção de teste, sem script nem módulo compartilhado; a regressão da etapa 1 continua válida (`references/review.md`, Re-review, passo 4). HEAD 642290d22e53a58eeef8972f925b0d3741fe53ca, árvore limpa fora deste `review.md`.
- Fechou: R1 (R2 a R4 conferidos pela prova afetada)
- Abriu: nenhum
- Veredito: Approve (proposto; o status `rascunho` correspondente e a aprovação ficam com o líder)
