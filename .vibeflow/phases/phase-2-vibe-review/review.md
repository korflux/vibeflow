# Review: skill vibe-review
# Pasta: phase-2-vibe-review
# Status: request-changes

## Contexto

- Alvo: phase-2-vibe-review (working tree)
- Cadeia: spec.md / plan.md (sem interview, sem analyze)
- O que muda: pacote `vibe-review` (SKILL, scripts com apply, template, refs, testes, README)
- Rodada: first-pass

## Cobertura

| Chave | Código | Notas |
|---|---|---|
| A1 | ok | `review.py` apply reuse; `test_reuse_plan_folder` |
| A2 | ok | Scripts só escrevem `review.md`; SKILL proíbe source |
| A3 | ok | Template + SKILL §3; este arquivo tem a tabela; plan intocado |
| A4 | ok | `REVIEW_SEM_ALVO`; `test_slug_creates_avulsa` |
| A5 | partial | Overwrite no mesmo path testado; ciclo re-review+Approve só no SKILL |
| A6 | ok | N/A neste diff (sem UI). Refs DevTools default existem |
| C1 | ok | `python docs/vibe-review/tests/test-review.py` 10/10 |
| C2 | ok | `vibe-review/SKILL.md` |
| C3 | ok | Este `review.md` |
| C4 | ok | Checklist `R*` no template; implement já consome `review.md` |

## Checklist de correções

### Required

- [x] R1 — **Required** — `.vibeflow/REGRAS.md` (lista “já estão prontas”) — constituição cita até `vibe-analyze`; `vibe-implement` e `vibe-review` já são pacotes prontos — remédio: acrescentar os dois nomes na lista, sem outro texto — prova: grep da linha — source: REGRAS — gap: partial

### Optional / Nit

- [x] R2 — **Nit** — `vibe-spec`/`vibe-plan`/`vibe-analyze` `CHAIN_FILES` — inventário das irmãs não lista `review.md` depois deste apply — remédio: incluir `review.md` no tuple, sem mudar apply — prova: inventário da fase mostra `review.md`
- [x] R3 — **Nit** — `docs/vibe-review/tests/test-review.py` — arquitetura permite `--dir` em pasta sem plan; a suíte não cobre o sucesso — remédio: um caso — prova: `python docs/vibe-review/tests/test-review.py`

## Notas

Working tree mistura analyze/implement/review. Esta review julga só a fatia phase-2 (`vibe-review/`, `docs/vibe-review/`, linha do README).

## Verificação conferida

- [x] Testes do diff: `python docs/vibe-review/tests/test-review.py` — 10/10 OK
- [x] Browser (se UI): N/A
- [x] Screenshot: N/A — leitura: N/A
- [x] Build do autor: N/A (scripts + unittest)

## DoD

- [x] Aceite A1/A4/C1/C2 evidenciado no disco
- [x] Sem source editado nesta skill
- [x] Testes da suíte passam
- [x] Sem UI user-visible neste diff

## Veredito

- [ ] **Approve** — nenhum Critical/Required em `[ ]`
- [x] **Request changes** — há Critical/Required em `[ ]`
- [ ] **Approve com defer** — <qual R* e por quê>

## Handoff

vibe-implement

- [ ] Aprovação humana (leu o arquivo e confirmou)
