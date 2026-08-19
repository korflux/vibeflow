---
name: vibe-implement
description: >
  Executa a próxima fatia da fase com prova e marca [x] no plan/spec/review. Use when the user runs /vibe-implement, pede implementar, código, build, faz a T*, pode seguir, ou a rota é low/medium/high/xhigh/max com código de comportamento — mesmo que não diga vibe-implement.
---

# vibe-implement

Não invente `n`. Sem artefato próprio: marca o disco da fase. Sem prova, sem `[x]`.
Sem `.vibeflow/`: `/vibe-init`. Open Questions no markdown = defeito. Não commita.

## 0. Script primeiro

1. Resolva o diretório desta skill.
2. No cwd do repo:
   - Windows: `pwsh "<skill>/scripts/implement.ps1"`
   - Unix: `bash "<skill>/scripts/implement.sh"` (Python 3, senão pwsh 7)
3. Leia `.vibeflow/implement-report.json`. Se `alvo`, leia o que `files` listar nessa pasta. Leia `.vibeflow/REGRAS.md`. Paths só os citados. Não varrer a árvore.

`INIT_AUSENTE` → init. `FASE_AUSENTE` / `PHASES_INESPERADO` / `FLAG_DESCONHECIDA` → não contorne.
Sem `--apply`. Sem `--slug`.

## 1. Abrir (5 linhas)

ROUTE · modo A/B · alvo · fila · plan

```
ROUTE: high · modo: A · alvo: phase-1-lock-bloco · fila: T2 · plan: sim
```

`modo_sugerido=criar` = não há fase com `plan.md`. Não invente pasta.

## 2. Gate

Declare `ROUTE: low|medium|high|xhigh|max` e modo A ou B. Default = **A**.

| | Ação |
|---|---|
| Typo / rename / uma linha sem runtime | **Não** usar |
| `high+` sem `plan.md` | **Para.** `/vibe-plan` |
| `max` sem `analyze.md` | **Para.** `/vibe-analyze` |
| Analyze veredito `bloqueado` | **Para.** Mostre os F* CRITICAL. Não flipa |
| Plan/analyze `# Status: rascunho` e o humano pediu **esta** skill | Flip para `aprovado` (1 linha) e siga, se o veredito não for `bloqueado` |
| `low`/`medium` claro sem plan | Avulso: prova mínima; sem inventar T* nem pasta |
| `review.md` com R* Critical/Required em `[ ]` | Fila = R* primeiro |
| Intenção/sucesso/fora frouxos | Devolve interview/spec |
| Travou ferramenta, teste ou visual | **Para.** Q+RECOMENDO. Não pule em silêncio |

```
Q: <o que trava>
RECOMENDO: <opção> — <1 linha>
(ok / outra?)
```

Modo B só se o humano pediu: `auto`, “faz o todo”, “não para”, “run completa”.
“Pode seguir” no modo A = próxima fase até o checkpoint (ou próxima T* se não houver agrupamento).

## 3. Ciclo da fatia

1. Descubra o test runner do **repo** (manifest, wrapper, CI). Não assuma `npm test`.
2. `RED → GREEN → REFACTOR` (bug: teste que reproduz, depois o fix). Teste que passa de primeira não prova.
3. Verify: teste da fatia, suite relevante, build/typecheck/lint se existirem.
4. UI web user-visible: leia `references/chrome-devtools.md`. Default = Chrome DevTools (screenshot + leitura da IA). Playwright/E2E do repo se a T* já manda ou o humano pediu. Sem nenhuma prova de browser possível → Q (ligar MCP / E2E do repo / humano valida). Não adicione lib de browser sem pedido.
5. DoD: `references/definition-of-done.md` no que couber. Aceite da T* **e** DoD.
6. Verde → marque disco **na mesma resposta**, sem perguntar.
7. Vermelho → deixe `[ ]` e reporte.

## 4. Marcar (disco manda)

| Arquivo | O que marcar |
|---|---|
| `plan.md` | `- [x] T{n} concluída` + aceite + verificação da T*; checkpoint da fase se fechou o grupo |
| `spec.md` | `A*` / `C*` **só** os que a fatia provou |
| `review.md` | `R*` Critical/Required que o fix provou |
| `interview.md` | **Não** |

Chat: ids + paths + comandos/provas. Sem reimprimir o plan.

## 5. Modos

**A (default):** uma fase até o próximo checkpoint, ou uma T*/R* se não houver agrupamento. Para. Espera ok.

**B:** percorre a fila. Para em checkpoint vermelho ou bloqueio. Marca a cada item.

Fila zerada (T* da run, ou R* bloqueantes) → handoff `vibe-review`. **Não** dispare.

## 6. Fechar

Não commita. Avise o que entra no git (código + vivos da fase). Fora: `implement-report.json`.
Handoff no chat. Não invente work extra.

## Fora (v1)

`implement.md`, wip, `--apply`, `--slug`, `todo.md`/`tasks.md`, path `docs/`/`specs/`/`fluxline`, inventar `n`, ignore de stack, hooks spec-kit, marcar `[x]` sem prova, pular visual em silêncio, adicionar Playwright sem pedido, commit, disparar review, Open Questions no `.md`, dump do plan no chat.
