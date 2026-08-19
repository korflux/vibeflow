# vibe-plan — arquitetura

`/vibe-plan` fatia a spec em tasks verificáveis e grava **um** arquivo. O script inventaria e promove o wip. A IA não escreve código.

```
.vibeflow/phases/phase-<n>-<slug>/plan.md
```

Mesma pasta da spec. Esta skill **não** aloca `n` novo. Sem spec na pasta, não há plan.

---

## 1. Papéis

| Peça | Onde | Faz |
|---|---|---|
| Skill | `vibe-plan/SKILL.md` | Gate, Q+RECOMENDO, fatiamento, aprovação, handoff |
| Scripts | `vibe-plan/scripts/plan.ps1`, `plan.py`, `plan.sh` | Inventário, alvo, promove wip → `plan.md` |
| Template | `vibe-plan/templates/plan.md` | Esqueleto. Script não preenche prosa |
| Relatório | `.vibeflow/plan-report.json` | Contrato script → IA (gitignored) |
| Wip | `.vibeflow/plan-wip.md` | Rascunho até o apply (gitignored) |
| Vivo | `.vibeflow/phases/phase-N-slug/plan.md` | Depois do apply. Commitável |

Install: user-scope, pacote sem `docs/`. Fonte canônica: `vibe-plan/`. Sem `references/` no v1.

---

## 2. Dependência

Sem `.vibeflow/` → `INIT_AUSENTE`. `/vibe-init` primeiro.

`phases/` falta → cria + `.gitkeep`. Não mexe em `REGRAS.md` nem symlink.

---

## 3. Alvo do plan

Pasta que bate `^phase-(\d+)-([a-z0-9]+(?:-[a-z0-9]+)*)$`.

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

```
[1] SCRIPT inventário → plan-report.json
[2] IA lê relatório + spec.md da alvo (+ interview.md se houver)
[3] Gate + flip da spec se rascunho + pedido de plan
[4] Conferência + fatiamento no wip
[5] SCRIPT apply
[6] Humano lê o arquivo → ajuste ou aprovado
[7] Fecha. Não commita. Não dispara implement
```

Depois do `plan.md` existir, ajuste e flip de Status editam o vivo. Sem apply de novo.

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

`files` só: `interview.md`, `spec.md`, `plan.md`, `analyze.md`.

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
  "actions": [],
  "avisos": []
}
```

A IA não varre o repo. Lê este JSON, `spec.md` / `plan.md` / `interview.md` da alvo, `REGRAS.md`, paths citados na spec.

---

## 8. Artefato vivo

Template: `vibe-plan/templates/plan.md`.

Status: `rascunho` | `aprovado`.

Seções (omitir a que não se aplica):

- Overview
- Ordem (fases + checkpoints; índice, não recópia o corpo)
- Riscos
- Paralelização
- Tasks (corpo T1…; aceite, verificação, deps, Spec: A*/C*)
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

Suíte: `docs/vibe-plan/tests/test-plan.py`. Launcher: `docs/vibe-plan/tests/test-plan.sh`.

---

## 10. Limites de contrato

- Grava um arquivo só: `.vibeflow/phases/phase-N-slug/plan.md`. Sem `todo.md`, `tasks.md`, `checklists/`, `docs/`, `specs/`.
- Sem `next_n`, sem `--slug`, sem pasta nova: plan entra na pasta da spec.
- Não pisa pasta com `analyze.md`. Não apaga `spec.md`.
- IDs `T1`, `T2`… Sem `T001`, `[P]`, `[US1]`.
- Zero código nesta porta.

Backlog e decisões de escopo: [`docs/ESCOPO.md`](../ESCOPO.md).

---

## 11. Assumido

- Init e spec já rodaram (ou o humano aceita o recado `PLAN_SEM_SPEC`).
- Uma fase = um pedido. Plan entra na pasta da spec.
- Status `aprovado` é patch no vivo.
- Sem backup em `old/`. Wip some após hash ok.
