# Review: <frase curta>
# Pasta: phase-<n>-<slug>
# Status: rascunho

## Contexto

- Alvo: <fase | branch | PR | local>
- Cadeia: interview? / spec.md / plan.md / analyze.md / implement.md
- O que muda: <1–3 frases>

## Cobertura

<!-- omitir se não houver spec.md -->

| Chave | Código | Notas |
|---|---|---|
| A1 | ok \| missing \| partial \| contradicts | <path ou —> |
| C1 | ok \| … | … |

## Checklist de correções

<!-- Só Critical e Required bloqueiam. Implement marca [x] no vivo. -->
<!-- Sem bloqueio: uma linha “nenhum bloqueio” e omitir as listas vazias. -->
<!-- Achado novo em etapa posterior: próximo número livre. Não renumerar fechados. -->

### Critical

- [ ] R1 — **Critical** — `path` — <o que está errado> — remédio: <movimento> — prova: <comando> — source: <A*|C*|diff|implement.md> — gap: <missing|partial|contradicts|—>

### Required

- [ ] R2 — **Required** — `path` — <…> — remédio: … — prova: …

### Optional / Nit

<!-- omitir se vazio -->

- [ ] R3 — **Nit** — …

## Visual

<!-- omitir se o diff desta etapa não toca UI -->

- Browser: <DevTools | E2E do repo>
- Screenshot: <path> — leitura: <ok | falhas>

## Segurança

<!-- omitir se o diff não toca input, auth, segredo, upload, pagamento, LLM ou dado pessoal -->
<!-- ref: references/security-and-hardening.md. Sem catálogo fixo. -->

- <achado ou “nada no que o diff tocou”>

## DoD

<!-- omitir se tudo N/A -->

- [ ] <item aplicável>

## Notas

<!-- omitir se vazio; teto 5 linhas -->

## Veredito vigente

- [ ] **Approve** — nenhum Critical/Required em `[ ]`
- [ ] **Request changes** — há Critical/Required em `[ ]`
- [ ] **Approve com defer** — <qual R* e por quê>

## Handoff

vibe-implement

<!-- ou: volta vibe-spec | cadeia fechada -->

- [ ] Aprovação humana (leu o arquivo e confirmou)

## Etapas

### Etapa 1 — first-pass — <o que olhou: T* / diff / fatia>

- Leu: implement.md <sim | não havia>
- Abriu: R1, R2 (ou nenhum)
- Fechou: —
- Veredito desta etapa: Request changes | Approve | Approve com defer

<!-- etapa seguinte: copie ### Etapa N abaixo. Não apague as anteriores. -->
