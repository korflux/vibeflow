---
name: vibe-analyze
description: >
  Cruza interview, spec e plan da mesma fase e grava o relatório em .vibeflow/phases/phase-N-slug/analyze.md. Use when the user runs /vibe-analyze, pede análise cruzada, consistência, cobertura, gaps, contradição entre artefatos, clarify depois do plan, ou a rota é max com plan em disco — mesmo que não diga vibe-analyze.
---

# vibe-analyze

Não invente `n`. Sem plan na pasta, não há analyze. Sem `.vibeflow/`: `/vibe-init`.
Não edite `interview.md`, `spec.md` nem `plan.md`. Open Questions no disco = defeito.

## 0. Script primeiro

1. Resolva o diretório desta skill.
2. No cwd do repo:
   - Windows: `pwsh "<skill>/scripts/analyze.ps1"`
   - Unix: `bash "<skill>/scripts/analyze.sh"` (Python 3, senão pwsh 7)
3. Leia `.vibeflow/analyze-report.json`. Se `alvo`, leia `spec.md` e `plan.md` (obrigatórios), `interview.md` se houver, `analyze.md` se rascunho. Leia `.vibeflow/REGRAS.md`. Paths só os citados.

`INIT_AUSENTE` → init. `ANALYZE_SEM_PLAN` → `/vibe-plan`. `ANALYZE_SEM_SPEC` / `FASE_AUSENTE` → não contorne.

## 1. Abrir (5 linhas)

modo · alvo · plan · interview · wip

```
modo: reuse · alvo: phase-1-lock-bloco · plan: sim · interview: sim · wip: ausente
```

`modo_sugerido=criar` = não há pasta com plan. Não invente fase.

## 2. Gate

| | Ação |
|---|---|
| Typo / uma linha óbvia | **Não** usar |
| Sem `plan.md` na alvo | **Para.** Mande `/vibe-plan` |
| Destino sem `spec.md` | **Para.** Não contorne `ANALYZE_SEM_SPEC` |
| Plan `# Status: rascunho` e o humano pediu **esta** skill | Flip o plan para `aprovado` (1 linha no chat) e siga |
| Plan rascunho **sem** pedido de analyze | **Para.** Peça leitura do plan |
| Intenção/sucesso/fora frouxos de verdade | Devolve interview/spec. Não “complete” no chute |
| Buraco pontual que só o humano fecha | Q+RECOMENDO, uma por vez, máx. 5 no total da run |

```
Q: <decisão que muda o veredito>
RECOMENDO: <opção> — <1 linha>
(ok / outra?)
```

## 3. Varredura (antes de gravar)

Leia `references/coverage.md`. Mapa interno. Não despeje a taxonomia no chat.

Cruze, nesta ordem:

1. **Interview → spec** (se `interview.md` existir): Resultado (o quê, sucesso, fora) contra Objetivo, A*/C*, Fora.
2. **Spec → plan:** cada A*/C* tem T* com `Spec:` apontando; cada T* aponta A*/C* ou é infra justificada.
3. **Plan → spec:** T* que inventa comportamento, path ou módulo que a spec não topou.
4. **REGRAS.md:** choque com MUST / Never / política do repo = `CRITICAL`.
5. Passes em `coverage.md`: duplicação, ambiguidade, furo, cobertura, inconsistência.

Gravidade: `CRITICAL` (bloqueia implement) · `HIGH` · `MEDIUM` · `LOW`.
IDs: `F1`, `F2`… na ordem da tabela. Teto 50; o resto é overflow nas Métricas.
Achado sem evidência (arquivo + trecho ou id A*/T*) não entra.

## 4. Clarificar (só se o disco não fecha)

Clarify do spec-kit vira **chat**, não patch na spec. Máx. 5 perguntas na run. Uma por vez. Resposta vai para **Clarificações** no `analyze.md`.

Não pergunte estilo, stack “tanto faz”, nem o que a spec/plan já fecharam. Se a resposta exige mudar spec ou plan: grave o F* com remédio `volta vibe-spec` ou `volta vibe-plan`. Esta skill não aplica o remédio.

Zero pergunta válida → siga. Não invente Q para preencher cota.

## 5. Escrever e salvar já

Wip = `.vibeflow/analyze-wip.md`. Molde: `templates/analyze.md`. Status `rascunho`.
Não pergunte se pode salvar. Não cole o corpo no chat.

1. Preencha o wip. Omita seção N/A. Veredito: `bloqueado` se algum `CRITICAL` aberto; senão `limpo`.
2. `pwsh "<skill>/scripts/analyze.ps1" -Apply` (Unix: `analyze.sh --apply`). `--dir` só se o relatório não acertar a pasta.
3. Chat, **só**:

```
Analyze gravado: .vibeflow/phases/phase-N-slug/analyze.md

- Veredito: limpo | bloqueado
- Cobertura: <A*/C* com T* / total>
- CRITICAL/HIGH: <F1… ou nenhum>
- Handoff: vibe-implement | volta vibe-spec | volta vibe-plan | volta vibe-interview

Leia o arquivo. Ok: **aprovado** (ou “pode ir pro implement”).
Ajuste: diga o que mudar. Não reimprimo o analyze aqui.
```

## 6. Ajuste ou aprovação

| Resposta | Ação |
|---|---|
| aprovado / “pode ir pro implement” / pede código | `# Status: aprovado` no vivo **só se** veredito `limpo`; §7 |
| pedido de alteração | Patch **só** no arquivo; ≤5 bullets; re-peça leitura |
| “parece bom” sem pedir implement | “Aprovado no arquivo, ou quer ajustar?” |
| veredito `bloqueado` e pede implement | Recuse. Mostre os F* CRITICAL e o handoff `volta` |
| spec/plan/intenção quebrou | Devolve a skill dona. Não force implement |

Rascunho sem “aprovado” e sem pedido da próxima porta **não** autoriza código.

## 7. Fechar

Não commita. Avise: commitar `.vibeflow/phases/phase-N-slug/analyze.md`. Não commitar `analyze-report.json` nem `analyze-wip.md`.
Handoff no arquivo. **Não** dispare a skill. Zero implementação e zero patch nas fontes nesta run.

