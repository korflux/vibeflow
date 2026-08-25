# vibe-plan, arquitetura

`/vibe-plan` fatia a spec em tasks verificáveis e grava **um** arquivo. A IA pilota a run, valida pré-requisitos e ferramentas essenciais de teste (`gitleaks`, MCPs como `chrome-devtools`), define a ordem técnica e o smoke test inicial; o script inventaria evidências e promove bytes de forma determinística e verificada.

```
.vibeflow/phases/phase-<n>-<slug>/plan.md
.vibeflow/mvp/plan.md
```

Mesmo alvo da spec. A rota MVP é explícita e não usa `n` ou `--dir`. Sem spec no alvo, não há plan.

---

## 1. Papéis

| Peça | Onde | Faz |
|---|---|---|
| IA | Piloto | Entende o motor, valida ferramentas de teste (`gitleaks`, `chrome-devtools`), define walking skeleton / smoke test, fatia em tasks verticais e fecha a ordem técnica |
| Skill | `vibe-plan/SKILL.md` | Orienta a IA com regras de fatiamento, gates, conferência de ferramentas e handoff |
| Scripts | `vibe-plan/scripts/plan.ps1`, `plan.py`, `plan.sh` | Ferramenta determinística: inventário mecânico, resolução de alvo e promoção atômica do wip |
| Template | `vibe-plan/templates/plan.md` | Esqueleto do artefato. O script não preenche prosa |
| Relatório | `.vibeflow/plan-report.json` | Evidência operacional estruturada (gitignored) |
| Wip | `.vibeflow/plan-wip.md` | Rascunho temporário até o apply (gitignored) |
| Vivo | `.vibeflow/phases/phase-N-slug/plan.md` ou `.vibeflow/mvp/plan.md` | Artefato permanente pós-apply. Commitável |

Install: `npx skills` ou marketplace (README). Pacote sem `docs/`. Fonte canônica: `vibe-plan/`. Sem `references/` no v1.

---

## 2. Dependência

Sem `.vibeflow/` → `INIT_AUSENTE`. `/vibe-init` primeiro.

`phases/` falta → cria + `.gitkeep`. Não mexe em `REGRAS.md` nem symlink.

---

## 3. Alvo do plan

Pasta que bate `^phase-(\d+)-([a-z0-9]+(?:-[a-z0-9]+)*)$`.

O relatório expõe os ponteiros como evidência:

| Campo | Significa |
|---|---|
| `alvo` | Destino preferido do apply sem `--dir` |
| `spec_pendente` | Maior `n` com `spec.md` e sem `plan.md` |
| `rascunho` | Maior `n` com `plan.md` e sem `analyze.md` |

Resolução de `alvo` (primeira que existir):

1. `spec_pendente`
2. `rascunho`
3. `null` → apply sem `--dir` falha `PLAN_SEM_SPEC`

`--dir phase-N-slug` força o destino. A pasta tem de existir **e** ter `spec.md`.

`analyze.md` no destino → `PLAN_JA_ANALISADO`. Não pisa.

Não existe modo `criar`. Plan não abre fase.

---

## 4. Fluxo

A IA inicia compreendendo a spec aprovada, os arquivos do codebase, a disponibilidade das ferramentas necessárias (`gitleaks`, `chrome-devtools`) e o motor determinístico.

### 4.1 Alvo MVP

`--mvp` ou `-Mvp` fixa o alvo em `.vibeflow/mvp/`. A IA escolhe a rota; o script não infere intenção.

- Exige `mvp/spec.md`; ausência gera `PLAN_SEM_SPEC`.
- Recusa `--dir` com `MODO_INVALIDO`.
- Recusa `mvp/analyze.md` existente com `PLAN_JA_ANALISADO`.
- Apply promove `plan-wip.md` para `mvp/plan.md`, com verificação atômica de tamanho e SHA-256, sem criar `phase-N`.
- Relatório acrescenta `rota`, `mvp`, `alvo.kind` e objetos phase com `kind: phase`.

O artefato MVP preserva IDs e ações críticas da spec nas tasks correspondentes. O handoff é `vibe-analyze`, nunca implementação direta.

```
[1] IA entende o motor de plan, suas entradas e proteções determinísticas
[2] SCRIPT executa inventário → plan-report.json
[3] IA audita o relatório, lê spec.md, interview.md (se houver), REGRAS.md e verifica dependências no host (gitleaks, chrome-devtools)
[4] IA valida Gate e confere viabilidade da spec
[5] IA realiza o fatiamento vertical no wip garantindo smoke test / walking skeleton na T1
[6] SCRIPT apply promove wip → plan.md com verificação atômica de integridade
[7] Humano lê o arquivo vivo → solicitação de ajuste ou aprovação
[8] IA fecha a run. Não commita. Não dispara implementação automaticamente
```

Depois do `plan.md` existir, ajuste e flip de Status editam o vivo diretamente. Sem apply de novo.


---

## 5. Inventário

Zero prosa.

| Campo | Significa |
|---|---|
| `vibeflow` | `ausente` / `ok` / `inesperado` |
| `phases` | `ausente` / `ok` / `inesperado` |
| `next_n` | max n + 1, ou 1 (informativo; apply não usa) |
| `existing[]` | `{ dir, n, slug, path, files }` |
| `spec_pendente` | objeto ou `null` |
| `rascunho` | objeto ou `null` |
| `alvo` | objeto ou `null` |
| `modo_sugerido` | `reuse` / `atualizar` / `criar` (`criar` = sem alvo) |
| `wip` | `ausente` / `presente` |
| `actions[]` | ex. `criar_phases` |
| `avisos[]` | nomes fora do padrão |

`files` só: `interview.md`, `spec.md`, `plan.md`, `analyze.md`, `implement.md`, `review.md`.

`modo_sugerido=criar` no inventário significa “não há pasta para gravar”. O apply **não** cria.

---

## 6. Apply

```
pwsh "<skill>/scripts/plan.ps1" -Apply [-Dir "phase-1-slug"]
bash "<skill>/scripts/plan.sh" --apply [--dir phase-1-slug]
```

Ordem:

1. Inventário de novo.
2. Sem wip → `WIP_AUSENTE`.
3. Resolve destino: `--dir` se veio; senão `alvo`. Sem destino → `PLAN_SEM_SPEC`.
4. `--dir` inexistente ou fora do padrão → `FASE_AUSENTE`.
5. Destino sem `spec.md` → `PLAN_SEM_SPEC`.
6. Destino com `analyze.md` → `PLAN_JA_ANALISADO`.
7. Cópia binária `plan-wip.md` → `plan.md` (pode sobrescrever rascunho).
8. Tamanho + SHA-256. Falha: apaga só o `plan.md` se **esta** run o criou e a pasta já tinha outros arquivos (não apaga a pasta). `COPY_HASH_MISMATCH`. Wip permanece.
9. Apaga o wip.
10. Garante `.gitignore`: `plan-report.json`, `plan-wip.md`. Não remove entradas das outras skills.
11. Relatório com `created` e `modo` (`reuse` / `atualizar`).

Sem `--slug`. Script não escreve prosa. Não pergunta.

Modo MVP: `plan.py --apply --mvp`, `plan.ps1 -Apply -Mvp` ou `plan.sh --apply --mvp`.

---

## 7. Relatório

`.vibeflow/plan-report.json`:

```json
{
  "root": "...",
  "vibeflow": "ok",
  "phases": "ok",
  "next_n": 2,
  "existing": [],
  "spec_pendente": {
    "dir": "phase-1-lock-bloco",
    "n": 1,
    "slug": "lock-bloco",
    "path": ".vibeflow/phases/phase-1-lock-bloco",
    "files": ["interview.md", "spec.md"]
  },
  "rascunho": null,
  "alvo": { "dir": "phase-1-lock-bloco", "n": 1, "slug": "lock-bloco", "path": ".vibeflow/phases/phase-1-lock-bloco", "files": ["interview.md", "spec.md"] },
  "modo_sugerido": "reuse",
  "wip": "ausente",
  "created": null,
  "modo": null,
  "avisos": []
}
```

O relatório serve como evidência operacional. A IA lê o JSON, `spec.md`, `plan.md` e `interview.md` (se houver), `REGRAS.md` e os arquivos do código necessários de forma direcionada, sem varredura cega da árvore.

---

## 8. Artefato vivo

Template: `vibe-plan/templates/plan.md`.

Status: `rascunho` | `aprovado`.

Seções (omitir a que não se aplica):

- Overview
- Ordem (fases + checkpoints; índice, não recópia o corpo)
- Riscos
- Paralelização
- Tasks (corpo T1…; aceite; Verificação = comando do repo; `Deps`; linha `T{n} concluída`; Spec: A*/C*)
- Conferência (cobertura da spec, não fila da build)
- Handoff (`vibe-implement`)

Sem Open Questions. Sem `todo.md`. Sem `checklists/`. Sem T001/[P]/[US1].

---

## 9. Contratos de teste

1. Sem `.vibeflow/` → `INIT_AUSENTE`.
2. Sem `phases/` → cria; `modo_sugerido=criar`; `alvo` nulo.
3. `phase-1-a` com `spec.md` → `alvo` é essa pasta; apply grava `plan.md` nela; não cria `phase-2`.
4. Apply sem spec em pasta alguma → `PLAN_SEM_SPEC`.
5. `--dir` sem `spec.md` → `PLAN_SEM_SPEC`.
6. Destino com `analyze.md` → `PLAN_JA_ANALISADO`; wip permanece; plan antigo intacto se já existia.
7. Rascunho existente: apply sobrescreve `plan.md`.
8. `.gitignore` ganha as duas entradas e preserva `spec-report.json`.
9. `phases` é arquivo → `PHASES_INESPERADO`.
10. Paridade pwsh: apply reuse grava o mesmo path.
11. Template congela `- [ ] T1 concluída`, `- **Deps:**`, Verificação como `comando do repo` (sem “passo manual”), checkpoint com omitir fluxo se não atravessa T*.

Suíte: `docs/vibe-plan/tests/test-plan.py`. Launcher: `docs/vibe-plan/tests/test-plan.sh`.

---

## 10. Limites de contrato

- Grava um arquivo só no alvo explícito phase ou MVP. Sem `todo.md`, `tasks.md`, `checklists/`, `docs/`, `specs/`.
- Sem `next_n`, sem `--slug`, sem pasta nova: plan entra na pasta da spec.
- Não pisa pasta com `analyze.md`. Não apaga `spec.md`.
- IDs `T1`, `T2`… Sem `T001`, `[P]`, `[US1]`.
- Linhas congeladas por T* (`concluída`, `Deps`) são contrato da implement. Este script **não** as parseia.
- Verificação da T* é comando. Só manual não fecha o fatiamento.
- Zero código nesta porta.
- No MVP, exige spec, preserva IDs críticos e encaminha para analyze.

Backlog e decisões de escopo: [`docs/ESCOPO.md`](../ESCOPO.md).

---

## 11. Assumido

- Init e spec já rodaram (ou o humano aceita o recado `PLAN_SEM_SPEC`).
- Uma fase = um pedido. Plan entra na pasta da spec.
- Status `aprovado` é patch no vivo.
- Sem backup em `old/`. Wip some após hash ok.
