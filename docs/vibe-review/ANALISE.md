# vibe-review — mapeamento e fluxo

Fontes:

- [fluxline-review](https://github.com/korflux/fluxline/blob/main/skills/fluxline-review/SKILL.md)
- [spec-kit converge](https://github.com/github/spec-kit/blob/main/templates/commands/converge.md)
- Contrato `.vibeflow/REGRAS.md` e as skills `vibe-implement`, `vibe-analyze`, `vibe-plan`

Pedido: **uma** skill. Veredito em disco + passe de cobertura pós-código. Sem segunda porta `vibe-converge`.

---

## O que cada fonte é

| | Fluxline review | Spec-kit converge | Cadeia vibe |
|---|---|---|---|
| Pergunta | O **diff** está bom para merge? | O **código** cobre spec/plan/tasks? | As duas, no mesmo `review.md` |
| Disco | `docs/fluxline/review/review-fase-N-…` | Append em `tasks.md` | `.vibeflow/phases/phase-N-slug/review.md` |
| Código da app | Proibido editar | Proibido editar | Proibido editar |
| Fila de remédio | `R*` no review | T* novas no tasks | `R*` no review. Plan intocado |
| Quando | Pediu review / handoff build | Depois do implement, se alguém rodar | `medium+` ou pedido; handoff da implement |
| Qualidade do patch | Cinco eixos | Quase zero | Cinco eixos |
| Cobertura pós-código | Informal (aceite) | Formal (FR/SC × código) | Formal (A*/C* × código) |

Spec-kit não tem review no core. Converge não julga XSS, slop nem arquivo inchado. Fluxline não tem passe “marquei T* e o A* não está no código”. Juntar sem regra faria a review reescrever o plan, ou o converge fingir code review.

---

## Síntese (uma skill, um arquivo)

```
.vibeflow/phases/phase-N-slug/review.md
```

A IA lê a fase e o diff. Julga. Cruza A*/C* com o código. Grava `R*`. **Não** pisa plan/spec. Remédio = handoff `vibe-implement`.

| Entra | De onde | Como |
|---|---|---|
| Read-only no source | Os dois | Script e skill não editam app |
| Artefato + `R*` | Fluxline | Checklist é a fila da implement |
| Mesma pasta, sem `n` novo se há plan | Irmãs | `plan_pendente` / `rascunho` |
| Avulsa `--slug` | Fluxline (N novo) traduzido | Só se `alvo` nulo |
| Cinco eixos + severidade | Fluxline | Critical/Required bloqueiam |
| Testes primeiro + visual | Fluxline; DevTools da implement | Playwright só se T*/humano |
| Passe cobertura | Converge | Seção Cobertura; gap = `R*` com `source`/`gap` |
| `unrequested` | Converge | FYI ou Required se inflar |
| Constitution | Converge + analyze | `REGRAS.md` MUST = Critical |
| Re-review no mesmo arquivo | Fluxline | Não abre fase nova |
| Approve sem perfeição | Fluxline | Não bloquear gosto |
| Apply + wip | Analyze/spec | Review tem artefato; implement não |
| Handoff sem disparar | REGRAS | `vibe-implement` / `volta vibe-spec` / fechada |

---

## O que foi cortado

| Corte | Motivo |
|---|---|
| Skill `vibe-converge` à parte | Pedido: uma. Analyze já cruzou spec×plan *antes* |
| Append T* no `plan.md` | Dono do plan é `vibe-plan`. Misturar dívida com fila nova apaga trilha |
| `docs/fluxline/`, `specs/`, `tasks.md` | Contrato `phase-N-slug` |
| 16 classes + `security-map` + shipping/CI/ADR | v1: uma ref de hardening; o resto quando o diff gritar e a casa existir |
| Playwright default | Mesma regra da implement: DevTools; E2E se mandado |
| Hooks / `extensions.yml` | Outro produto |
| Review que “já corrige” | Julgamento ≠ patch. Implement marca `R*` |
| Open Questions no `.md` | Chat |
| LGTM só no chat | Disco completo |
| Disparar implement | Handoff é linha |

---

## Fluxo de uma run

```
[1] Script inventário → review-report.json
[2] IA lê relatório + vivos da alvo + REGRAS.md + diff
[3] Sem alvo e sem diff → para. T* abertas + “pronto da feature” → recusa Approve de feature
[4] Testes → cobertura A*/C* × código → cinco eixos
[5] Wip = review.md (veredito + R*)
[6] Apply promove
[7] Chat: path + veredito + contagem R*. Humano lê o arquivo
[8] Request changes → handoff implement. Re-review no mesmo path
[9] Fecha. Não commita. Não dispara. Não pisa plan/spec
```

---

## Assumido

- Sem `.vibeflow/` a skill para.
- Review da cadeia reusa a pasta do plan. Avulsa é pedido **outro**.
- `vibe-analyze` não é substituída: ela é spec×plan antes; o passe aqui é código×A* depois.
- Implement já declara: se `review.md` tem `R*` em `[ ]`, essa fila manda.
- Re-run de apply por cima de `review.md` é first-pass de novo. Re-review consciente edita o vivo.
