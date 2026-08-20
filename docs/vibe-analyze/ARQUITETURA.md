# vibe-analyze — arquitetura

`/vibe-analyze` cruza interview, spec e plan da **mesma** pasta e grava **um** relatório. O script inventaria e promove o wip. A IA não edita `interview.md`, `spec.md` nem `plan.md`.

```
.vibeflow/phases/phase-<n>-<slug>/analyze.md
```

Mesma pasta do plan. Esta skill **não** aloca `n` novo. Sem `plan.md` (e `spec.md`) na pasta, não há analyze.

---

## 1. Papéis

| Peça | Onde | Faz |
|---|---|---|
| Skill | `vibe-analyze/SKILL.md` | Gate, varredura cruzada, até 5 Q, veredito, handoff |
| Scripts | `vibe-analyze/scripts/analyze.ps1`, `analyze.py`, `analyze.sh` | Inventário, alvo, promove wip → `analyze.md` |
| Template | `vibe-analyze/templates/analyze.md` | Esqueleto. Script não preenche prosa |
| Referência | `vibe-analyze/references/coverage.md` | Taxonomia e passes. Abrir só na varredura |
| Relatório | `.vibeflow/analyze-report.json` | Contrato script → IA (gitignored) |
| Wip | `.vibeflow/analyze-wip.md` | Rascunho até o apply (gitignored) |
| Vivo | `.vibeflow/phases/phase-N-slug/analyze.md` | Depois do apply. Commitável |

Install: `npx skills` ou marketplace (README). Pacote sem `docs/`. Fonte canônica: `vibe-analyze/`.

---

## 2. Dependência

Sem `.vibeflow/` → `INIT_AUSENTE`. `/vibe-init` primeiro.

`phases/` falta → cria + `.gitkeep`. Não mexe em `REGRAS.md` nem symlink.

---

## 3. Alvo do analyze

Pasta que bate `^phase-(\d+)-([a-z0-9]+(?:-[a-z0-9]+)*)$`.

| Campo | Significa |
|---|---|
| `alvo` | Destino preferido do apply sem `--dir` |
| `plan_pendente` | Maior `n` com `spec.md` + `plan.md` e sem `analyze.md` |
| `rascunho` | Maior `n` com `analyze.md` (plan já existe) |

Resolução de `alvo` (primeira que existir):

1. `plan_pendente`
2. `rascunho`
3. `null` → apply sem `--dir` falha `ANALYZE_SEM_PLAN`

`--dir phase-N-slug` força o destino. A pasta tem de existir **e** ter `spec.md` **e** `plan.md`.

`interview.md` é opcional. Ausência vira aviso no relatório da skill (artefato), não erro do script.

Não existe modo `criar` de fase. Analyze não abre pasta.

---

## 4. Fluxo

```
[1] SCRIPT inventário → analyze-report.json
[2] IA lê relatório + spec.md + plan.md da alvo (+ interview.md se houver) + REGRAS.md
[3] Gate + flip do plan se rascunho + pedido de analyze
[4] Mapa interno (references/coverage.md). Até 5 Q só se o disco não fecha
[5] Wip com achados + cobertura + veredito
[6] SCRIPT apply
[7] Humano lê o arquivo → ajuste ou aprovado
[8] Fecha. Não commita. Não dispara implement. Não pisa interview/spec/plan
```

Depois do `analyze.md` existir, ajuste e flip de Status editam o vivo. Sem apply de novo, salvo re-run que promove wip por cima do rascunho.

---

## 5. Inventário

Zero prosa.

| Campo | Significa |
|---|---|
| `vibeflow` | `ausente` / `ok` / `inesperado` |
| `phases` | `ausente` / `ok` / `inesperado` |
| `next_n` | max n + 1, ou 1 (informativo; apply não usa) |
| `existing[]` | `{ dir, n, slug, path, files }` |
| `plan_pendente` | objeto ou `null` |
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
pwsh "<skill>/scripts/analyze.ps1" -Apply [-Dir "phase-1-slug"]
bash "<skill>/scripts/analyze.sh" --apply [--dir phase-1-slug]
```

Ordem:

1. Inventário de novo.
2. Sem wip → `WIP_AUSENTE`.
3. Resolve destino: `--dir` se veio; senão `alvo`. Sem destino → `ANALYZE_SEM_PLAN`.
4. `--dir` inexistente ou fora do padrão → `FASE_AUSENTE`.
5. Destino sem `plan.md` → `ANALYZE_SEM_PLAN`.
6. Destino sem `spec.md` → `ANALYZE_SEM_SPEC`.
7. Cópia binária `analyze-wip.md` → `analyze.md` (pode sobrescrever rascunho).
8. Tamanho + SHA-256. Falha: apaga só o `analyze.md` se **esta** run o criou. `COPY_HASH_MISMATCH`. Wip permanece.
9. Apaga o wip.
10. Garante `.gitignore`: `analyze-report.json`, `analyze-wip.md`. Não remove entradas das outras skills.
11. Relatório com `created` e `modo` (`reuse` / `atualizar`).

Sem `--slug`. Script não escreve prosa. Não pergunta. Não toca `interview.md` / `spec.md` / `plan.md`.

---

## 7. Relatório

`.vibeflow/analyze-report.json`:

```json
{
  "root": "...",
  "vibeflow": "ok",
  "phases": "ok",
  "next_n": 2,
  "existing": [],
  "plan_pendente": {
    "dir": "phase-1-lock-bloco",
    "n": 1,
    "slug": "lock-bloco",
    "path": ".vibeflow/phases/phase-1-lock-bloco",
    "files": ["interview.md", "spec.md", "plan.md"]
  },
  "rascunho": null,
  "alvo": { "dir": "phase-1-lock-bloco", "n": 1, "slug": "lock-bloco", "path": ".vibeflow/phases/phase-1-lock-bloco", "files": ["interview.md", "spec.md", "plan.md"] },
  "modo_sugerido": "reuse",
  "wip": "ausente",
  "created": null,
  "modo": null,
  "actions": [],
  "avisos": []
}
```

A IA não varre o repo. Lê este JSON, `spec.md` / `plan.md` / `interview.md` / `analyze.md` da alvo, `REGRAS.md`. Paths só os que esses arquivos citaram.

---

## 8. Artefato vivo

Template: `vibe-analyze/templates/analyze.md`.

Status: `rascunho` | `aprovado`.

Seções (omitir a que não se aplica):

- Fontes (o que o disco tinha nesta pasta)
- Cobertura (A*/C*/Resultado da interview × T*)
- Achados (tabela + corpo F1…)
- Clarificações (só o que o humano respondeu nesta run)
- Constituição (choque com `REGRAS.md`)
- Métricas
- Veredito (`limpo` | `bloqueado`)
- Handoff (`vibe-implement` se limpo; senão `volta vibe-spec` / `volta vibe-plan` / `volta vibe-interview`)

Sem Open Questions. Achado sem evidência de path/trecho = defeito. Sem editar as fontes.

IDs estáveis: `F1`, `F2`… na ordem da tabela. Gravidade: `CRITICAL` | `HIGH` | `MEDIUM` | `LOW`.

Teto: 50 achados. O resto vira uma linha de overflow nas Métricas.

---

## 9. Contratos de teste

1. Sem `.vibeflow/` → `INIT_AUSENTE`.
2. Sem `phases/` → cria; `modo_sugerido=criar`; `alvo` nulo.
3. `phase-1-a` com `spec.md` + `plan.md` → `alvo` é essa pasta; apply grava `analyze.md` nela; não cria `phase-2`.
4. Apply sem plan em pasta alguma → `ANALYZE_SEM_PLAN`.
5. `--dir` sem `plan.md` → `ANALYZE_SEM_PLAN`.
6. `--dir` com plan e sem `spec.md` → `ANALYZE_SEM_SPEC`.
7. Rascunho existente: apply sobrescreve `analyze.md`.
8. `.gitignore` ganha as duas entradas e preserva `plan-report.json`.
9. `phases` é arquivo → `PHASES_INESPERADO`.
10. Paridade pwsh: apply reuse grava o mesmo path.

Suíte: `docs/vibe-analyze/tests/test-analyze.py`. Launcher: `docs/vibe-analyze/tests/test-analyze.sh`.

---

## 10. Limites de contrato

- Grava um arquivo só: `.vibeflow/phases/phase-N-slug/analyze.md`. Sem `tasks.md`, `checklists/`, `docs/`, `specs/`.
- Não edita `interview.md`, `spec.md` nem `plan.md`. Achado vira `F*` com remédio, não patch na fonte.
- Sem `next_n`, sem `--slug`, sem pasta nova: analyze entra na pasta do plan.
- Veredito e gravidade são semântica da skill; o script não os interpreta.

Backlog e decisões de escopo: [`docs/ESCOPO.md`](../ESCOPO.md).

---

## 11. Assumido

- Init, spec e plan já rodaram (ou o humano aceita o recado `ANALYZE_SEM_PLAN`).
- Uma fase = um pedido. Analyze entra na pasta do plan.
- Status `aprovado` é patch no vivo.
- Sem backup em `old/`. Wip some após hash ok.
- Implement ainda não existe: analyze pode ser refeito na mesma pasta.
