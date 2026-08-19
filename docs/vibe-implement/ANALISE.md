# vibe-implement — mapeamento e fluxo

Fontes:

- [fluxline-build](https://github.com/korflux/fluxline/blob/main/skills/fluxline-build/SKILL.md)
- [spec-kit implement](https://github.com/github/spec-kit/blob/main/templates/commands/implement.md)
- [spec-kit converge](https://github.com/github/spec-kit/blob/main/templates/commands/converge.md) (ideia; não vira porta)
- Contrato `.vibeflow/REGRAS.md` e as skills `vibe-spec`, `vibe-plan`, `vibe-analyze`

Pedido: **uma** skill. Executa a fila do `plan.md`. Sem artefato próprio.

---

## O que cada fonte é

| | Fluxline build | Spec-kit implement | Spec-kit converge | Cadeia vibe |
|---|---|---|---|---|
| Papel | Porta obrigatória de código; TDD; marca A*/T*/R* | Executor de `tasks.md` | Lacuna código × spec/plan; anexa T* | Código com prova; marca o `plan.md` |
| Disco | todo + plan + spec + review | Só `[X]` em `tasks.md` | Append no `tasks.md` | Checkboxes no `plan.md` / spec / review |
| Script | `fluxline-run`: n + `chain.*` | `check_prerequisites`: FEATURE_DIR | Idem | Inventário; alvo = maior n com plan |
| Teste | TDD obrigatório | Opcional (se a task de teste existir) | Não executa | TDD / prove-it obrigatório |
| Visual | Playwright + print lido | Sem | Sem | Chrome DevTools **default**; Playwright se T* ou humano |
| Parada | Modo A default | Corre a fila; para em falha | Não executa | Modo A default |
| Depois | Handoff review | Relatório; converge à parte | Devolve para implement | Handoff `vibe-review` (não dispara) |

Spec-kit implement é motor de fila rasa. Fluxline build é protocolo de sessão. Converge é reconciliação *depois*. Analyze desta cadeia já cobre o cruzamento *antes*. Implement não absorve analyze nem converge.

---

## Síntese (uma skill, zero arquivo novo)

```
.vibeflow/phases/phase-N-slug/plan.md
```

A IA lê a fase, executa a próxima T* (ou R*), prova, marca. O script não promove wip.

| Entra | De onde | Como |
|---|---|---|
| Sem plan, script não inventa fase | Fluxline + plan | `alvo` nulo; skill manda `/vibe-plan` se `high+` |
| Pedido desta porta aprova plan rascunho | Spec/plan/analyze | Flip no `plan.md` |
| TDD / prove-it | Fluxline | Ciclo no SKILL |
| Modo A / B | Fluxline + pedido | Default A |
| Parar se a prova não fecha | Pedido | Q+RECOMENDO; opções concretas |
| Marcar disco na hora | Fluxline | T* / checkpoint / A* / C* / R* |
| Fila R* manda na T* | Fluxline | Se `review.md` existir |
| Gate `max` + analyze `bloqueado` | Cadeia + analyze | Skill, não script |
| Avulso `low`/`medium` | Cadeia | Sem pasta nova |
| DevTools default | Pedido | Ref `chrome-devtools.md` |
| Playwright permitido | Pedido (ajuste da spec) | T*, humano, ou Q quando DevTools falta |
| Constitution | Spec-kit (traduzido) | `REGRAS.md` |
| Handoff sem disparar | REGRAS | `vibe-review` |

---

## O que foi cortado

| Corte | Motivo |
|---|---|
| `implement.md` / wip / `--apply` | REGRAS: um arquivo por skill que grava. Fila já é o plan |
| `todo.md` / `tasks.md` / T001 `[P]` `[US1]` | Plan já fatia |
| `docs/fluxline/`, `specs/NNN-slug/` | Contrato `phase-N-slug` |
| Playwright **proibido** | Ajuste da spec: default é DevTools, não recusa |
| Playwright como dependência nova sem pedido | Não instalar lib para o que o MCP do host cobre |
| Ignore files de stack no implement | Efeito colateral do spec-kit; mistura setup com feature |
| Hooks / `extensions.yml` | Outro produto |
| `analyze` / `converge` dentro da build | Analyze já é porta; converge vira review/analyze se um dia precisar |
| Teste opcional | Sem prova não marca |
| Run completa como default | Modo A |
| Commit | Irmãs não commitam |
| Disparar review | Handoff é linha |
| Pack de 12 refs Fluxline | v1: DevTools + DoD |
| Script lendo Status/checkbox | Semântica é da IA |

---

## Fluxo de uma run

```
[1] Script inventário → implement-report.json
[2] IA lê relatório + vivos da alvo + REGRAS.md
[3] high+ sem plan → para, /vibe-plan. max sem analyze → /vibe-analyze
    analyze bloqueado → recusa
[4] Plan rascunho + humano pediu implement → flip plan, segue
[5] Fila: R* abertos primeiro, senão próxima T*
[6] Test runner do repo. RED→GREEN→REFACTOR. UI: DevTools (ou E2E se mandado)
[7] Verde → [x] no disco. Vermelho → [ ] + Q
[8] Modo A para. Chat: ids, paths, provas. Não commita. Não dispara review
```

---

## Assumido

- Sem `.vibeflow/` a skill para. Init primeiro.
- Rota é declaração da IA. Script não conhece `low`/`max`.
- `review.md` pode não existir. Inventário lista se houver.
- Comando E2E já na T* roda como verificação de código, mesmo com DevTools no visual.
- A primeira run desta skill contra a própria fase (T2+) só acontece depois do pacote existir.
