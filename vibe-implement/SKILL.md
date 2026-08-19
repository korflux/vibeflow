---
name: vibe-implement
description: >
  Executa a próxima fatia da fase com prova, marca [x] no plan/spec/review e
  grava .vibeflow/phases/phase-N-slug/implement.md. Use when the user runs
  /vibe-implement, pede implementar, código, build, faz a T*, pode seguir, ou
  a rota é low/medium/high/xhigh/max com código de comportamento — mesmo que
  não diga vibe-implement.
---

# vibe-implement

Não invente `n` se há plan. Sem prova, sem `[x]` e sem apply. Sem `todo.md` nem `tasks.md`.
Sem `.vibeflow/`: `/vibe-init`. Open Questions no markdown = defeito. Não commita.

## 0. Script primeiro

1. Resolva o diretório desta skill.
2. No cwd do repo:
   - Windows: `pwsh "<skill>/scripts/implement.ps1"`
   - Unix: `bash "<skill>/scripts/implement.sh"` (Python 3, senão pwsh 7)
3. Leia `.vibeflow/implement-report.json`. Se `alvo`, leia o que `files` listar nessa pasta. Leia `.vibeflow/REGRAS.md`. Paths só os citados. Não varrer a árvore.

`INIT_AUSENTE` → init. `IMPLEMENT_SEM_ALVO` / `FASE_AUSENTE` / `WIP_AUSENTE` / `SLUG_INVALIDO` / `PHASES_INESPERADO` → não contorne.

Apply:
- reuse/atualizar: `pwsh "<skill>/scripts/implement.ps1" -Apply` (`--dir` se o alvo errar)
- avulsa `low`/`medium` sem pasta: `… -Apply -Slug "<frase curta>"`
- Unix: `implement.sh --apply` / `--apply --slug "…"`

## 1. Abrir (5 linhas)

ROUTE · modo A/B · alvo · fila · plan · wip

```
ROUTE: high · modo: A · alvo: phase-1-lock-bloco · fila: T2 · plan: sim · wip: ausente
```

`modo_sugerido=criar` = não há fase com `plan.md` nem `implement.md`. Não invente pasta. `high+` para e manda `/vibe-plan`. `low`/`medium` avulso usa `--slug` no apply.

## 2. Gate

Declare `ROUTE: low|medium|high|xhigh|max` e modo A ou B. Default = **A**.

| | Ação |
|---|---|
| Typo / rename / uma linha sem runtime | **Não** usar |
| `high+` sem `plan.md` | **Para.** `/vibe-plan` |
| `max` sem `analyze.md` | **Para.** `/vibe-analyze` |
| Analyze veredito `bloqueado` | **Para.** Mostre os F* CRITICAL. Não flipa |
| Plan/analyze `# Status: rascunho` e o humano pediu **esta** skill | Flip para `aprovado` (1 linha) e siga, se o veredito não for `bloqueado` |
| `low`/`medium` claro sem plan | Avulso: prova mínima; pasta só no apply com `--slug` se ainda não houver alvo |
| `review.md` com R* Critical/Required em `[ ]` | Fila = R* primeiro |
| Intenção/sucesso/fora frouxos | Devolve interview/spec |
| Travou ferramenta, teste ou visual | **Para.** Q+RECOMENDO. Não pule em silêncio. Sem apply |

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
4. UI web user-visible: leia `references/chrome-devtools.md`. Default = Chrome DevTools (screenshot + leitura da IA). E2E do repo se a T* já manda ou o humano pediu. Sem nenhuma prova de browser possível → Q (ligar MCP / E2E do repo / humano valida). Não adicione lib de browser sem pedido.
5. DoD: `references/definition-of-done.md` no que couber. Aceite da T* **e** DoD.
6. Verde → marque disco **na mesma resposta**, sem perguntar, e grave o wip (§5).
7. Vermelho → deixe `[ ]`, sem apply, reporte.

## 4. Marcar (disco manda)

| Arquivo | O que marcar |
|---|---|
| `plan.md` | `- [x] T{n} concluída` + aceite + verificação da T*; checkpoint da fase se fechou o grupo |
| `spec.md` | `A*` / `C*` **só** os que a fatia provou |
| `review.md` | `R*` Critical/Required que o fix provou |
| `interview.md` | **Não** |

Chat: ids + paths + comandos/provas. Sem reimprimir o plan.

## 5. Escrever e salvar já

Wip = `.vibeflow/implement-wip.md`. Molde: `templates/implement.md`.

Se já existe `implement.md` na alvo: leia o vivo e copie as fatias anteriores no wip. Acrescente **uma** `## Fatia` nova. Não apague histórico.

Omita `Feedback +`, `Feedback −` e `Para a review` se vazios. Sem prova, não grave wip.

Não pergunte se pode salvar. Não cole o corpo no chat.

1. Preencha o wip.
2. Apply (§0).
3. Chat, **só**:

```
Implement gravado: .vibeflow/phases/phase-N-slug/implement.md

- Fatia: <T* | R* | avulsa>
- Marcado: <ids>
- Prova: <comando>
- Feedback: <+ / − / nenhum>
- Handoff: vibe-review | próxima T* | Q

Leia o arquivo. Não reimprimo o implement aqui.
```

## 6. Modos

**A (default):** uma fase até o próximo checkpoint, ou uma T*/R* se não houver agrupamento. Para. Espera ok.

**B:** percorre a fila. Para em checkpoint vermelho ou bloqueio. Marca e aplica o wip a cada item (histórico acumula no mesmo `implement.md`).

Fila zerada (T* da run, ou R* bloqueantes) → handoff `vibe-review`. **Não** dispare.

## 7. Fechar

Não commita. Avise o que entra no git (código + vivos da fase, inclusive `implement.md`). Fora: `implement-report.json`, `implement-wip.md`.
Handoff no chat e no arquivo. Não invente work extra.
