# Review: UX detalhado e vibe-design
# Alvo: phase-10-ux-detalhado-e-vibe-design
# Status: rascunho

<!-- Escreva diretamente neste artefato vivo; o status permanece rascunho até o veredito e a confirmação humana. -->

## Contexto

- Alvo: phase-10-ux-detalhado-e-vibe-design
- Cadeia: interview.md / spec.md / plan.md / implement.md (sem analyze.md, rota sem analyze)
- O que muda: UX genérica detalhada nos templates de interview e spec, cadeia com design condicional a UI visível, skill nova vibe-design com três motores, template, references, docs e distribuição em 8 skills.

## Cobertura

| Chave | Código | Notas |
|---|---|---|
| A1 | ok | `vibe-spec/templates/spec.md`, molde F* com superfície por passo, mais `vibe-interview/templates/interview.md` com jornadas |
| A2 | ok | `vibe-interview/templates/interview.md`, tabela de 8 colunas e checklist de acesso com N/A explícito, `vibe-spec/templates/spec.md` com N/A |
| A3 | ok | `vibe-design/SKILL.md`, `vibe-design/templates/design.md`, `vibe-design/references/modos-entrada.md`, `vibe-design/references/kit-e-tokens.md`, `vibe-design/scripts/design.py`, `vibe-design/scripts/design.ps1`, `vibe-design/scripts/design.sh`, `docs/vibe-design/ARQUITETURA.md`, `docs/vibe-design/ANALISE.md` |
| A4 | ok | `.vibeflow/REGRAS.md`, linha 14 com design condicional, mais `vibe-plan/SKILL.md` e `vibe-analyze/SKILL.md` com conferência de design |
| C1 | ok | Suítes reexecutadas nesta review, 22 interview, 22 spec, 19 design, 12 distribuicao, 4 visual, 2 mvp, 12 reparse, sh design 6/0, gitleaks 18 commits sem leaks |
| C2 | ok | `plan.md` T6 referencia spec e design sem criar comportamento ou token novo, distribuição em 8 preservada |

## Checklist de correções

nenhum bloqueio

### Optional / Nit

- [x] R1: **Nit** - `.vibeflow/phases/phase-10-ux-detalhado-e-vibe-design/plan.md` - Conferência com `# Status: aprovado` no cabeçalho mas item `Aprovação humana` em `[ ]` na linha 171, spec.md já tem `[x]` - remédio: vibe-implement marca `[x]` ou registra motivo em 1 linha - prova: leitura de `plan.md:4,171` e `spec.md:176` - source: plan.md - gap: nenhum

## Segurança

- Entrada externa no diff: apenas flags locais `--slug`, `--dir`, `--root`, `--mvp` dos motores `vibe-design/scripts/design.py` e `design.ps1`. Sanitização com `sanitize_slug` e `ConvertTo-Slug` (ASCII, 2 a 48 chars), `--dir` reduzido a `basename` via `Path(args.dir).name` e `GetFileName`, `LiteralPath` em todo acesso, guarda de reparse point antes de escrita, `subprocess` em array sem shell, sem SQL, sem auth, sem segredo, sem log sensível. Nada explorável no que o diff tocou.

## DoD

- [x] Suítes de contrato verdes reexecutadas nesta review
- [x] `git diff --check` limpo
- [x] `gitleaks detect --source . --verbose --redact --no-banner` sem leaks
- [x] Sem edição de source, teste ou lockfile nesta skill
- [x] `review-report.json` fora do git, `review.md` vivo entra no git

## Notas

- `interview.md` e `spec.md` da phase 10 estão untracked no working tree, resíduo esperado de skills de definição, entra no commit final da phase.
- `plan.md` T1 a T6 em `[x]` com prova por task, `implement.md` com 6 fatias e arquivos por fatia.
- Visual omitido, diff sem UI web. Banco omitido, repo sem persistência.

## Veredito vigente

- [x] **Approve**: nenhum Critical/Required em `[ ]`
- [ ] **Request changes**: há Critical/Required em `[ ]`
- [ ] **Approve com defer**: nenhum

## Handoff

finalização Git da phase

- [ ] Aprovação humana (leu o arquivo e confirmou)

- Chat: a review recomenda novo chat para correções em `vibe-implement` se R1 virar bloqueio, o que não é o caso. Após Approve e confirmação humana, o handoff é a finalização Git da phase. O `review.md` vivo e o diff são a ponte.

## Finalização Git da phase

- Pré-condições: Approve confirmado, todas as `T*` concluídas, Critical/Required fechados, suíte final verde, `git diff --check` e gitleaks quando previsto.
- Commit final: `chore(phase-N): finalize review`, somente com paths residuais autorizados e sem `Co-Authored-By`; sem mudanças residuais, manter o último commit da task.
- Push: `git push` para o upstream atual, sem `--force`. Registrar hash/HEAD, paths e resultado; falha mantém o handoff bloqueado.

## Etapas

### Etapa 1 - first-pass - T1 a T6, diff ce7d859..5303864 mais untracked, provas reexecutadas

- Leu: plan.md sim
- Abriu: R1 (Nit, sem bloqueio)
- Fechou: nenhum
- Veredito desta etapa: Approve
