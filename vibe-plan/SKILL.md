---
name: vibe-plan
description: >
  Fatia a spec em tasks verificáveis e grava .vibeflow/phases/phase-N-slug/plan.md.
  Use when the user runs /vibe-plan, pede plan, fatiar a spec, criar tasks,
  todo, ordem de execução, ou a rota é high/xhigh/max com spec em disco —
  mesmo que não diga vibe-plan.
---

# vibe-plan

Não invente `n`. Sem spec na pasta, não há plan. Sem `.vibeflow/`: `/vibe-init`.
Um arquivo. Não escreva código. Open Questions no disco = defeito.

## 0. Script primeiro

1. Resolva o diretório desta skill.
2. No cwd do repo:
   - Windows: `pwsh "<skill>/scripts/plan.ps1"`
   - Unix: `bash "<skill>/scripts/plan.sh"` (Python 3, senão pwsh 7)
3. Leia `.vibeflow/plan-report.json`. Se `alvo`, leia `spec.md` (obrigatório), `interview.md` se houver, `plan.md` se rascunho. Leia `.vibeflow/REGRAS.md`. Paths só os que a spec citou.

`INIT_AUSENTE` → init. `PLAN_SEM_SPEC` → `/vibe-spec`. `PLAN_JA_ANALISADO` / `FASE_AUSENTE` → não contorne.

## 1. Abrir (5 linhas)

modo · alvo · spec · status-spec · wip

```
modo: reuse · alvo: phase-1-lock-bloco · spec: sim · spec-status: aprovado · wip: ausente
```

`modo_sugerido=criar` = não há pasta com spec. Não invente fase.

## 2. Gate

| | Ação |
|---|---|
| Typo / uma linha óbvia | **Não** usar |
| Sem `spec.md` na alvo | **Para.** Mande `/vibe-spec` |
| Spec `# Status: rascunho` e o humano pediu **esta** skill / o plan | Flip a spec para `aprovado` (1 linha no chat) e siga |
| Spec rascunho **sem** pedido de plan | **Para.** Peça leitura da spec |
| Intenção/sucesso/fora frouxos | Devolve interview/spec. Não complete no chute |
| Buraco pontual de ordem | Q+RECOMENDO, uma por vez |
| `analyze.md` na alvo | Não pisa |

```
Q: <decisão que trava o fatiamento>
RECOMENDO: <opção> — <1 linha>
(ok / outra?)
```

## 3. Conferência (antes de fatiar)

A spec aguenta? Se faltar, Q+RECOMENDO ou devolve spec. Não crie `checklists/`.

- A*/C* observáveis, não adjetivo
- Fora real
- UI user-visible → direção visual fechada
- Paths/comandos da spec existem ou foram topados

## 4. Fatiar

Fatia **vertical** (um caminho usável), não horizontal (DB inteiro → API inteira → UI).

| Size | Files | Ação |
|---|---|---|
| low | 1 | Uma T* |
| medium | 1–2 | Uma T* |
| high | 3–5 | Uma T* |
| xhigh / max | 5+ ou risco alto | Quebrar agora |

Quebre se: >1 sessão focada; aceite >3 bullets; 2+ subsistemas independentes; “e” no título.

Cada T*: o quê, `Spec: A*/C*`, aceite testável, verificação (comando do repo), deps, arquivos prováveis, size.

Verificação só manual recusa: Q ou volte a fatiar. Pelo menos um comando do repo (já existe ou topado na spec). Leitura de arquivo não conta.

Deps reais. Fatias independentes: `Deps: nenhuma` nas duas. Ordem de id não substitui Deps.

Checkpoint: suite das T* do grupo; fluxo extra só se o caminho observável atravessa mais de uma T*; senão omita o segundo bullet.

Ordem: deps primeiro; alto risco cedo; checkpoint a cada 2–3 T*.

UI greenfield / sem DS na spec: uma T* de tokens/kit **antes** das telas. Reuso de DS → não crie essa T*.

Paralelo: fatias independentes. Sequencial: migration, estado compartilhado. Contrato primeiro, depois lados.

IDs `T1`, `T2`… na ordem de execução. Sem `T001`, `[P]`, `[US1]`, `tasks.md` ou mural de user story.

Não copie a spec. Não invente módulo.

## 5. Escrever e salvar já

Wip = `.vibeflow/plan-wip.md`. Molde: `templates/plan.md`. Status `rascunho`.
Não pergunte se pode salvar. Não cole o corpo no chat.

1. Preencha o wip. Omita seção N/A.
2. `pwsh "<skill>/scripts/plan.ps1" -Apply` (Unix: `plan.sh --apply`). `--dir` só se o relatório não acertar a pasta.
3. Chat, **só**:

```
Plan gravado: .vibeflow/phases/phase-N-slug/plan.md

- Overview: <1 linha>
- Ordem: Fase 1 … → Fase 2 … (N tasks, checkpoints em …)
- Riscos altos: <0–2 linhas ou nenhum>
- Primeira T*: <título>

Leia o arquivo. Ok: **aprovado** (ou “pode ir pro implement”).
Ajuste: diga o que mudar. Não reimprimo o plan aqui.
```

## 6. Ajuste ou aprovação

| Resposta | Ação |
|---|---|
| aprovado / “pode ir pro implement” / pede código / `vibe-implement` | `# Status: aprovado` no vivo; §7 |
| pedido de alteração | Patch **só** no arquivo; ≤5 bullets; re-peça leitura |
| “parece bom” sem pedir implement | “Aprovado no arquivo, ou quer ajustar?” |
| spec/intenção quebrou | Devolve spec/interview. Não force implement |

Rascunho sem “aprovado” e sem pedido da próxima porta **não** autoriza código.

## 7. Fechar

Não commita. Avise: commitar `.vibeflow/phases/phase-N-slug/plan.md`. Não commitar `plan-report.json` nem `plan-wip.md`.
Handoff no arquivo: `vibe-implement`. **Não** dispare a skill. Zero implementação nesta run.

