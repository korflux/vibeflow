# vibe-implement, mapeamento e fluxo

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
| Teste | TDD obrigatório | Opcional | Ciclo em 6 passos com comandos reais de teste |
| Visual | Playwright + print lido | Sem | MCP Server `chrome-devtools` default; E2E se T* ou humano |
| Depois | Handoff review | Relatório | Handoff `vibe-review` (não dispara) |

---

## Síntese (uma skill, um arquivo)

```
.vibeflow/phases/phase-N-slug/implement.md
```

A IA lê a fase e o `fila` do relatório, executa a T* (ou R*) elegível seguindo o ciclo de 6 passos (reconhecer, codar, testar, simplificar, re-testar, entregar), prova a execução no disco e escreve o wip (histórico + fatia nova). O script promove bytes com integridade verificada.

| Entra | De onde | Como |
|---|---|---|
| Sem plan, script não inventa fase no inventário | Irmãs | `alvo` nulo; skill manda `/vibe-plan` se `high+` |
| Avulsa `low`/`medium` | Pedido + ESCOPO | `--apply --slug` abre pasta só para a trilha |
| Ciclo de implementação em 6 passos | Vibe | Reconhecer -> Codar -> Testar -> Simplificar -> Re-testar -> Entregar |
| Diagnóstico sem desistência | Vibe | Trata causa raiz de erros; nunca pula tasks sem teste verde |
| Marcar disco na hora | Fluxline | T* / A* / C* / R* |
| Trilha + feedback | Pedido (ESCOPO 3.1) | Template: feito, marcado, prova, + / - / para a review |
| Apply + wip | Spec/plan/review | Mesmo contrato de cópia + hash |
| Handoff sem disparar | REGRAS | `vibe-review` |

---

## O que foi cortado

| Corte | Motivo |
|---|---|
| `todo.md` / `tasks.md` / T001 `[P]` `[US1]` | Plan já fatia |
| `docs/fluxline/`, `specs/NNN-slug/` | Contrato `phase-N-slug` |
| Lib de browser nova sem pedido | MCP Server `chrome-devtools` do host cobre o default |
| Desistir ou pular tarefas com erro | Regra estrita: diagnosticar causa raiz e corrigir no código |
| Ignore files de stack | Mistura setup com feature |
| Teste opcional | Sem teste verde executável não marca e não aplica |
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
[4] Fila: R* abertos primeiro, senão fila.elegiveis do relatório (Q se 2+)
[5] Ciclo da fatia:
    a. Reconhece código existente no repositório
    b. Coda a implementação direta e enxuta
    c. Testa com comando real do repo (ou MCP Server chrome-devtools para UI)
    d. Simplifica o código recém-escrito
    e. Re-testa para garantir integridade
    f. Entrega, marca vivos e grava no wip
[6] Verde → [x] + wip (fatias antigas + fatia nova + feedback)
[7] Apply promove com verificação atômica
[8] Se falhar: investiga log, corrige a causa raiz e retesta
[9] Modo A para. Não commita. Não dispara review
```

---

## Assumido

### Extensão MVP

No MVP, a implementação não pode começar apenas porque existe um plan. O motor projeta a fila exclusivamente do alvo especial e expõe um gate mínimo do analyze. Ausência, rascunho ou veredito bloqueado impedem o apply, enquanto a skill impede o código antes disso. O histórico acumulativo continua sendo escrito pela IA; o script só promove bytes verificados e nunca publica decisões vigentes.

- Sem `.vibeflow/` a skill para. Init primeiro.
- Rota é declaração da IA. O script não infere `low`/`max`; apenas obedece ao alvo explícito `--mvp`.
- `review.md` pode não existir. Inventário lista se houver.
- A review lê `implement.md` quando o arquivo existir (a porta da review ainda mapeia o checklist vivo).
- `fila` no relatório é acréscimo (minor). A skill antiga que ignora o campo continua; a nova não monta a fila no feeling se o campo veio preenchido.
