# Review: <frase curta>
# Pasta: phase-<n>-<slug>
# Status: rascunho

## Contexto

- Alvo: <fase | branch | PR | local>
- Cadeia: interview? / spec.md / plan.md / analyze.md
- O que muda: <1–3 frases>
- Rodada: first-pass | re-review

## Cobertura

| Chave | Código | Notas |
|---|---|---|
| A1 | ok \| missing \| partial \| contradicts | <path ou —> |
| C1 | ok \| … | … |

<!-- omitir se não houver spec -->

## Checklist de correções

<!-- Só Critical e Required bloqueiam. Implement marca [x] no vivo. -->

### Critical

- [ ] R1 — **Critical** — `path` — <o que está errado> — remédio: <movimento> — prova: <comando> — source: <A*|C*|diff> — gap: <missing|partial|contradicts|—>

### Required

- [ ] R2 — **Required** — `path` — <…> — remédio: … — prova: …

### Optional / Nit

- [ ] R3 — **Nit** — …

<!-- se zero bloqueio: uma linha “nenhum bloqueio” e omitir as listas vazias -->

## Notas

<!-- omitir se vazio; teto 5 linhas -->

## Verificação conferida

- [ ] Testes do diff: <comando / resultado | N/A>
- [ ] Browser (se UI): <DevTools | E2E do repo | N/A>
- [ ] Screenshot: <path | N/A> — leitura: <ok | falhas | N/A>
- [ ] Build do autor: <… | N/A>

## DoD

- [ ] <item aplicável> / N/A

## Veredito

- [ ] **Approve** — nenhum Critical/Required em `[ ]`
- [ ] **Request changes** — há Critical/Required em `[ ]`
- [ ] **Approve com defer** — <qual R* e por quê>

## Handoff

vibe-implement

<!-- ou: volta vibe-spec | cadeia fechada -->

- [ ] Aprovação humana (leu o arquivo e confirmou)

## Re-review

<!-- omitir na first-pass -->
