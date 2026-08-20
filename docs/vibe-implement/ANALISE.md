# vibe-implement — mapeamento e fluxo

Fontes:

- [fluxline-build](https://github.com/korflux/fluxline/blob/main/skills/fluxline-build/SKILL.md)
- [spec-kit implement](https://github.com/github/spec-kit/blob/main/templates/commands/implement.md)
- [spec-kit converge](https://github.com/github/spec-kit/blob/main/templates/commands/converge.md) (ideia; não vira porta)
- Contrato `.vibeflow/REGRAS.md` e as skills `vibe-spec`, `vibe-plan`, `vibe-analyze`, `vibe-review`

Pedido: **uma** skill. Executa a fila do `plan.md`, marca o disco e deixa trilha própria.

---

## O que cada fonte é

| | Fluxline build | Spec-kit implement | Cadeia vibe |
|---|---|---|---|
| Papel | Porta de código; TDD; marca A*/T*/R* | Executor de `tasks.md` | Código com prova; marca a cadeia; grava `implement.md` |
| Disco | todo + plan + spec + review | Só `[X]` em `tasks.md` | Checkboxes + `implement.md` na mesma pasta |
| Script | `fluxline-run`: n + `chain.*` | `check_prerequisites` | Inventário + apply do wip |
| Teste | TDD obrigatório | Opcional | TDD / prove-it obrigatório |
| Visual | Playwright + print lido | Sem | Chrome DevTools **default**; E2E se T* ou humano |
| Depois | Handoff review | Relatório | Handoff `vibe-review` (não dispara) |

---

## Síntese (uma skill, um arquivo)

```
.vibeflow/phases/phase-N-slug/implement.md
```

A IA lê a fase e o `fila` do relatório, executa a T* (ou R*) elegível, prova, marca, escreve o wip (histórico + fatia nova). O script promove bytes.

| Entra | De onde | Como |
|---|---|---|
| Sem plan, script não inventa fase no inventário | Irmãs | `alvo` nulo; skill manda `/vibe-plan` se `high+` |
| Avulsa `low`/`medium` | Pedido + ESCOPO | `--apply --slug` abre pasta só para a trilha |
| TDD / prove-it | Fluxline | Ciclo no SKILL |
| Marcar disco na hora | Fluxline | T* / A* / C* / R* |
| Trilha + feedback | Pedido (ESCOPO 3.1) | Template: feito, marcado, prova, + / − / para a review |
| Apply + wip | Spec/plan/review | Mesmo contrato de cópia + hash |
| Handoff sem disparar | REGRAS | `vibe-review` |

---

## O que foi cortado

| Corte | Motivo |
|---|---|
| `todo.md` / `tasks.md` / T001 `[P]` `[US1]` | Plan já fatia |
| `docs/fluxline/`, `specs/NNN-slug/` | Contrato `phase-N-slug` |
| Lib de browser nova sem pedido | MCP do host cobre o default |
| Ignore files de stack | Mistura setup com feature |
| Teste opcional | Sem prova não marca e não aplica |
| Run completa como default | Modo A |
| Commit | Irmãs não commitam |
| Disparar review | Handoff é linha |
| Script lendo Status, aceite ou prosa | Semântica é da IA; a fila usa só duas linhas congeladas |
| Apagar fatia anterior no apply | O wip traz o histórico; o script só copia bytes |

---

## Fluxo de uma run

```
[1] Script inventário → implement-report.json
[2] IA lê relatório + vivos da alvo + REGRAS.md
[3] high+ sem plan → para. max sem analyze → /vibe-analyze
[4] Fila: R* abertos primeiro, senão `fila.elegiveis` do relatório (Q se 2+)
[5] Test runner. RED→GREEN→REFACTOR. UI: DevTools
[6] Verde → [x] + wip (fatias antigas + fatia nova + feedback)
[7] Apply promove. Vermelho → [ ] + Q, sem apply
[8] Modo A para. Não commita. Não dispara review
```

---

## Assumido

- Sem `.vibeflow/` a skill para. Init primeiro.
- Rota é declaração da IA. Script não conhece `low`/`max`.
- `review.md` pode não existir. Inventário lista se houver.
- A review lê `implement.md` quando o arquivo existir (a porta da review ainda mapeia o checklist vivo).
- `fila` no relatório é acréscimo (minor). A skill antiga que ignora o campo continua; a nova não monta a fila no feeling se o campo veio preenchido.
