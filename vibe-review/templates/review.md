# Review: <frase curta>
# Alvo: <phase-<n>-<slug> ou mvp>
# Status: rascunho

<!-- Escreva diretamente neste artefato vivo; o status permanece rascunho até o veredito e a confirmação humana. -->

## Contexto

- Alvo: <fase | branch | PR | local>
- Cadeia: interview? / spec.md / plan.md / analyze.md
- O que muda: <1-3 frases>

## Cobertura

<!-- omitir se não houver spec.md -->

| Chave | Código | Notas |
|---|---|---|
| A1 | ok | missing | partial | contradicts | <path ou -> |
| C1 | ok | ... | ... |

## Checklist de correções

<!-- Só Critical e Required bloqueiam. Implement marca [x] no vivo. -->
<!-- Sem bloqueio: uma linha "nenhum bloqueio" e omitir as listas vazias. -->
<!-- Achado novo em etapa posterior: próximo número livre. Não renumerar fechados. -->

### Critical

- [ ] R1: **Critical** - `path` - <o que está errado> - remédio: <movimento> - prova: <comando> - source: <A*|C*|diff|plan.md> - gap: <missing|partial|contradicts|nenhum>

### Required

- [ ] R2: **Required** - `path` - <...> - remédio: ... - prova: ...

### Optional / Nit

<!-- omitir se vazio -->

- [ ] R3: **Nit** - ...

## Visual

<!-- omitir se o diff desta etapa não toca UI -->

- Browser: <DevTools | E2E do repo>
- Screenshot: <path> - leitura: <ok | falhas>

## Segurança

<!-- omitir se o diff não toca input, auth, segredo, upload, pagamento, LLM ou dado pessoal -->
<!-- ref: references/security-and-hardening.md. Sem catálogo fixo. -->

- <achado ou "nada no que o diff tocou">

## DoD

<!-- omitir se tudo N/A -->

- [ ] <item aplicável>

## Notas

<!-- omitir se vazio; teto 5 linhas -->

## Veredito vigente

- [ ] **Approve**: nenhum Critical/Required em `[ ]`
- [ ] **Request changes**: há Critical/Required em `[ ]`
- [ ] **Approve com defer**: <qual R* e por quê>

## Decisões para vigência

<!-- Omitir se a entrega não cria nem substitui decisão crítica. Esta tabela é proposta até aprovação humana. -->

| ID | Ação | Decisão aprovada | Fonte da decisão | Evidência de implementação |
|---|---|---|---|---|
| <DOMINIO-01> | <cria ou substitui> | <decisão compacta> | <spec.md ID> | <plan.md T* e prova> |

## Handoff

vibe-implement | finalização Git da phase

<!-- ou: volta vibe-spec | cadeia fechada -->

- [ ] Aprovação humana (leu o arquivo e confirmou)

- Chat: a review deve recomendar novo chat para correções em `vibe-implement`; após Approve e confirmação humana, o handoff é a finalização Git da phase. O `review.md` vivo e o diff são a ponte.

## Finalização Git da phase

- Pré-condições: Approve confirmado, todas as `T*` concluídas, Critical/Required fechados, suíte final verde, `git diff --check` e gitleaks quando previsto.
- Commit final: `chore(phase-N): finalize review`, somente com paths residuais autorizados e sem `Co-Authored-By`; sem mudanças residuais, manter o último commit da task.
- Push: `git push` para o upstream atual, sem `--force`. Registrar hash/HEAD, paths e resultado; falha mantém o handoff bloqueado.

## Etapas

### Etapa 1 - first-pass - <o que olhou: T* / diff / provas>

- Leu: plan.md <sim | não havia>
- Abriu: R1, R2 (ou nenhum)
- Fechou: nenhum
- Veredito desta etapa: Request changes | Approve | Approve com defer

<!-- etapa seguinte: copie ### Etapa N abaixo. Não apague as anteriores. -->
