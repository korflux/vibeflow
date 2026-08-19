# Spec: skill vibe-review
# Pasta: phase-2-vibe-review
# Status: aprovado

## Objetivo

O agente no repo do app precisa de uma porta que **só julga** o que foi implementado e grava o veredito. Esta entrega cria a skill `vibe-review`: lê a fase (e o diff), aplica cinco eixos, confere se o código ainda deve algo à spec (passe converge), e grava `.vibeflow/phases/phase-N-slug/review.md` com fila `R*`. Sucesso é o humano ver Approve ou Request changes no arquivo, sem a review ter editado source, e o implement conseguir consumir só a checklist.

## Inventário

1. Pacote `vibe-review/` (SKILL, scripts gêmeos, template, refs sob demanda).
2. `docs/vibe-review/` (ARQUITETURA, ANALISE, testes de contrato).
3. Relatório `.vibeflow/review-report.json` e wip `.vibeflow/review-wip.md` (gitignored).
4. Vivo `review.md` na pasta da fase.
5. Uma linha no `README.md`.

## Suposições e decisões

1. Há artefato próprio. REGRAS autorizam se a arquitetura mandar. Chat não fecha merge. — (processo)
2. Script **com** `--apply`: promove wip → `review.md`. Igual analyze. Sem apply a review não “existe” no disco. — (processo)
3. Mesma pasta do plan quando a cadeia existe. Não aloca `n` novo se há `plan.md` alvo. Re-review = **mesmo** `review.md`. — (processo)
4. Review avulsa (diff/PR sem fase): apply com `--slug` cria `phase-<next_n>-<slug>` só com `review.md`. Sem alvo e sem slug → `REVIEW_SEM_ALVO`. Não gruda review nova num N de pedido já fechado. — (processo)
5. Read-only no código da app. Achou problema → `R*` + remédio + handoff `vibe-implement`. Mesmo se o humano disser “já corrige”: esta skill grava o veredito; a implement, depois, patcha. — (processo; Fluxline)
6. Não edita `interview.md` / `spec.md` / `plan.md` / `analyze.md`. Não anexa T* no plan (converge do spec-kit misturava fila). Gap de cobertura vira `R*` com `source: A*`/`C*` e `gap: missing|partial|contradicts|unrequested`. Se o gap é spec errada → handoff `volta vibe-spec`, não inventa requisito. — (processo)
7. Cinco eixos no diff: corretude, clareza, arquitetura, segurança, performance. Severidade: Critical / Required bloqueiam; Nit / Optional / FYI não. Sem prefixo = defeito. — (produto; Fluxline)
8. Passe converge **dentro** da mesma run: código atual × A*/C* da spec (+ decisões da spec que imponham trabalho). Não substitui `vibe-analyze` (essa é spec×plan **antes**). — (produto; spec-kit)
9. UI web: julgamento visual com a mesma regra da implement (Chrome DevTools default; Playwright/E2E se a T* ou o humano mandar). Print sem leitura = gap Required se a mudança for user-visible. — (produto)
10. Refs v1: pointer DoD (`vibe-implement/references/definition-of-done.md`), `ui-visual-quality.md` (curta), `security-and-hardening.md` (uma). Sem 16 classes, sem security-map, sem shipping/CI/ADR no pack. Abrir só o domínio do diff. — (escopo)
11. Barra de Approve: melhora a saúde e segue o repo. Não bloquear gosto. Sem Critical/Required → Approve (checklist pode ser “nenhum bloqueio”). — (processo)
12. Status do vivo: `rascunho` | `request-changes` | `aprovado` | `aprovado-com-defer`. Pedido desta porta não flipa plan. T* ainda `[ ]` + humano pediu “pronto da feature” → recusa Approve de feature; pode revisar o diff e dizer o que falta no plan. — (processo)
13. Não commita. Não dispara implement. Handoff é linha. — (processo)
14. Constitution = `REGRAS.md`. Choque MUST = Critical. — (processo)

## Escopo e comportamento

### 1. Script (disco)

- Sem `.vibeflow/` → `INIT_AUSENTE`.
- `phases/` ausente → cria + `.gitkeep`.
- Inventário: `vibeflow`, `phases`, `next_n`, `existing[]` (`interview.md`, `spec.md`, `plan.md`, `analyze.md`, `review.md`), `alvo`, `modo_sugerido`, `wip`, `actions`, `avisos`, mais `created`/`modo` depois do apply.
- Resolução de `alvo` (sem `--dir`):
  1. maior `n` com `plan.md` e sem `review.md` (`plan_pendente` no relatório)
  2. maior `n` com `review.md` (`rascunho`)
  3. `null`
- `--dir phase-N-slug` força pasta existente. Sem `plan.md` e sem `review.md` na pasta, apply ainda pode gravar `review.md` (review avulsa apontada). Pasta inexistente → `FASE_AUSENTE`.
- Apply sem destino: se `alvo` nulo e veio `--slug`, cria `phase-<next_n>-<slug>`. Slug inválido → `SLUG_INVALIDO`. Sem alvo e sem slug → `REVIEW_SEM_ALVO`.
- Destino com `review.md` → overwrite do rascunho/re-run (`modo=atualizar`). Re-review consciente edita o vivo **depois**; apply de wip por cima é re-run da primeira passagem.
- Cópia binária wip → `review.md`, tamanho + SHA-256. `COPY_HASH_MISMATCH` se falhar. Apaga o wip se ok.
- Gitignore: `review-report.json`, `review-wip.md`. Não remove irmãs.
- Flags: `--root`/`-Root`, `--dir`/`-Dir`, `--apply`/`-Apply`, `--slug`/`-Slug`. Sem `--force`.
- Três motores, um contrato. Stdout = path do relatório. Erro: `CODIGO: …` no stderr.

### 2. Skill (semântica)

1. Roda o script. Lê o relatório + `REGRAS.md` + o que a alvo tiver. Diff: o que o humano apontou, ou working tree / branch da sessão, sem varrer a árvore além dos paths da spec/plan/diff.
2. Sem alvo e sem diff → para. Peça path, branch, PR ou `--dir`.
3. Declara: first-pass ou re-review; alvo; se há plan/spec.
4. Contexto: o que a mudança alega (spec/T* se existirem).
5. Testes primeiro: existem? testam comportamento? UI: prova de browser segundo a regra da implement. Sem editar testes.
6. Passe converge: cada A*/C* tem evidência no código (não só checkbox `[x]`). Plan T* marcada sem código que cumpra o aceite → `R*` `gap: partial`/`missing`. Código fora da spec → `unrequested` (FYI ou Required se inflar).
7. Diff nos cinco eixos. Finding = evidência (path) + severidade + remédio nomeado + prova sugerida. Sem evidência não entra.
8. Wip no template. Status `rascunho`. Apply. Chat: path + veredito + contagem R* + handoff. Sem dump.

### 3. Artefato vivo

Template `vibe-review/templates/review.md`. Seções (omitir N/A):

- Contexto (alvo, cadeia, first-pass/re-review)
- Cobertura (A*/C* × código; tabela curta)
- Checklist de correções (`R1…`; Critical/Required/Nit)
- Notas (opcional, ≤5 linhas)
- Verificação conferida (testes, visual, build)
- DoD aplicável
- Veredito (Approve / Request changes / Approve com defer)
- Handoff (`vibe-implement` | `volta vibe-spec` | cadeia fechada)
- Re-review (só nas rodadas seguintes)

IDs `R*` estáveis. Build/implement marca `[x]` no vivo. Review de re-passagem atualiza a seção Re-review e o veredito; não renumera R* fechados.

### 4. Avulsa e re-review

- Avulsa: `--slug` curto do tema (`diff-local`, `pr-42`). Sem misturar com fase de outro pedido.
- Re-review: mesmo path. Lê `R*` que a implement marcou. Foca remédios abertos + regressão. Não abre `phase-N+1`.

### Fora

- Editar source, testes ou lockfile nesta skill — julgamento ≠ patch
- Anexar T* no `plan.md` / criar `tasks.md` — fila de correção é `R*`
- Path `docs/fluxline/`, `specs/`
- 16 classes de security, `security-map`, shipping, CI, ADR no v1
- Playwright como default visual
- Hooks spec-kit, `--force`
- Open Questions no `.md`, dump no chat, commit, disparar implement
- Approve de feature com T* obrigatórias ainda `[ ]`
- Segundo `review.md` na mesma fase

## Checklist de entrega

### Aceite

- [x] A1: Com fase+plan, apply grava `review.md` nessa pasta; não cria fase nova
- [ ] A2: Skill não edita source; Critical/Required viram `- [ ] R*` com remédio e prova
- [ ] A3: Passe cobertura A*/C* × código aparece no artefato; gap vira `R*`, não T* no plan
- [x] A4: Sem alvo e sem `--slug`, apply falha `REVIEW_SEM_ALVO`; avulsa com `--slug` cria `phase-N-slug` só com `review.md`
- [ ] A5: Re-review reusa o mesmo arquivo; veredito Approve só sem Critical/Required em `[ ]`
- [ ] A6: Visual user-visible julgado (DevTools default); sem evidência visual em UI = Required, não Approve silencioso

### Critérios de sucesso

- [x] C1: Suíte `docs/vibe-review/tests/test-review.py` cobre init ausente, reuse da pasta do plan, `--slug` avulsa, `REVIEW_SEM_ALVO`, overwrite de rascunho, gitignore, `FASE_AUSENTE`
- [x] C2: `SKILL.md` operacional (gate, eixos, cobertura, marcar R*, handoff, Fora) sem narrar o produto
- [ ] C3: Humano lê o `review.md` e sabe o veredito e a fila sem o chat
- [ ] C4: Implement consegue consumir só a Checklist de correções (contrato já previsto na `vibe-implement`)

## Implementação

### Stack

| Área | Escolha |
|---|---|
| Pacote | `vibe-review/` na raiz, igual às irmãs |
| Motor | Python 3 + ps1 + sh |
| Apply | Sim (diferente da implement) |
| Dependências novas | Nenhuma |
| DoD | Pointer para `vibe-implement/references/definition-of-done.md` |

### Estrutura tocada

```text
vibe-review/SKILL.md
vibe-review/scripts/review.py
vibe-review/scripts/review.ps1
vibe-review/scripts/review.sh
vibe-review/templates/review.md
vibe-review/references/definition-of-done.md   # pointer
vibe-review/references/ui-visual-quality.md
vibe-review/references/security-and-hardening.md
docs/vibe-review/ARQUITETURA.md
docs/vibe-review/ANALISE.md
docs/vibe-review/tests/test-review.py
README.md
```

### Estilo e padrões

- reutilizar: inventário/apply de `vibe-analyze` (PHASE_RE, hash do wip, gitignore append-only)
- alvo default = pasta do plan, não `next_n` cego
- SKILL na ordem das irmãs
- testes: `unittest`, pasta isolada; paridade pwsh skip se não houver

### Contratos e módulos

- limites: script não julga diff nem lê checkbox; não escreve source
- schema do relatório estável (breaking = major)
- `R*` é o contrato implement ↔ review

## Como provar

### Seams

- Review da fase errada — `--dir` e regra “plan sem review, senão rascunho”
- Avulsa grudada no N da implement — `--slug` só quando não há cadeia deste pedido
- Converge virando rewrite do plan — proibido no SKILL e no Fora
- Review que edita código — red flag; testes de contrato não pegam semântica

### Estratégia

- Unitário: script em temp dir
- Manual: first-pass nesta fase `phase-2` depois de pronta, e um re-review simulado na `phase-1-vibe-implement` com `--dir` (opcional)

### Comandos

```bash
python docs/vibe-review/tests/test-review.py
pwsh vibe-review/scripts/review.ps1
```

## Boundaries

### Always

- Gravar `review.md` antes de declarar veredito
- Read-only no source
- Evidência em todo R* bloqueante
- Passe cobertura se houver spec
- Português do Brasil

### Ask first

- Approve com defer (item que o humano topa deixar)
- Review avulsa: confirmar que não é a fase do plan aberto
- Pular prova visual (mesma Q da implement)

### Never

- Editar app nesta skill
- Inventar `n` se há plan alvo
- Anexar T* no plan
- Carregar pasta security inteira
- Playwright como plano B silencioso
- Commit, disparar implement
- Open Questions no markdown
- LGTM sem arquivo

## Handoff

vibe-plan

- [x] Aprovação humana (leu o arquivo e confirmou)
