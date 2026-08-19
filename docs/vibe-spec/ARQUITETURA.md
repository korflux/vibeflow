# vibe-spec — arquitetura

`/vibe-spec` grava o **decidido** em disco para o plan não inventar comportamento. O script inventaria e promove o wip. A IA fecha seams no chat e escreve o markdown.

```
.vibeflow/phases/phase-<n>-<slug>/spec.md
```

Mesma pasta da interview quando ela existir. Esta skill **não** aloca `n` novo se já há alvo. `next_n` só na abertura de pedido sem fase.

---

## 1. Papéis

| Peça | Onde | Faz |
|---|---|---|
| Skill | `vibe-spec/SKILL.md` | Gate, Q+RECOMENDO, texto da spec, aprovação, handoff |
| Scripts | `vibe-spec/scripts/spec.ps1`, `spec.py`, `spec.sh` | Inventário, alvo, promove wip → `spec.md` |
| Template | `vibe-spec/templates/spec.md` | Esqueleto. Script não preenche prosa |
| Referência | `vibe-spec/references/ui-visual-direction.md` | Só se UI user-visible |
| Relatório | `.vibeflow/spec-report.json` | Contrato script → IA (gitignored) |
| Wip | `.vibeflow/spec-wip.md` | Rascunho até o apply (gitignored) |
| Vivo | `.vibeflow/phases/phase-N-slug/spec.md` | Depois do apply. Commitável |

Install: user-scope, pacote sem `docs/`. Fonte canônica: `vibe-spec/`.

---

## 2. Dependência

Sem `.vibeflow/` → `INIT_AUSENTE`. `/vibe-init` primeiro.

`phases/` falta → cria + `.gitkeep`. Não mexe em `REGRAS.md` nem symlink.

---

## 3. Alvo da spec

Pasta que bate `^phase-(\d+)-([a-z0-9]+(?:-[a-z0-9]+)*)$`.

O relatório expõe três ponteiros:

| Campo | Significa |
|---|---|
| `alvo` | Destino preferido do apply sem `--dir` |
| `interview_pendente` | Maior `n` com `interview.md` e sem `spec.md` |
| `rascunho` | Maior `n` com `spec.md` e sem `plan.md` |

Resolução de `alvo` (primeira que existir):

1. `interview_pendente`
2. `rascunho`
3. `null` (precisa criar fase com slug)

`--dir phase-N-slug` força o destino. A pasta tem de existir.

`plan.md` no destino → `SPEC_JA_PLANEJADA`. Não pisa. Pedido novo = outra pasta.

---

## 4. Fluxo

```
[1] SCRIPT inventário → spec-report.json
[2] IA lê relatório + interview.md da alvo (se houver) + spec.md se rascunho
[3] Gate + seams no chat
[4] Wip completo (template)
[5] SCRIPT apply
[6] Humano lê o arquivo → ajuste ou aprovado
[7] Fecha. Não commita. Não dispara plan
```

Depois do spec.md existir, ajuste e flip de Status editam o vivo. Sem apply de novo.

---

## 5. Inventário

Zero prosa.

| Campo | Significa |
|---|---|
| `vibeflow` | `ausente` / `ok` / `inesperado` |
| `phases` | `ausente` / `ok` / `inesperado` |
| `next_n` | max n + 1, ou 1 |
| `existing[]` | `{ dir, n, slug, path, files }` |
| `interview_pendente` | objeto da fase ou `null` |
| `rascunho` | objeto da fase ou `null` |
| `alvo` | objeto ou `null` |
| `modo_sugerido` | `reuse` / `atualizar` / `criar` |
| `wip` | `ausente` / `presente` |
| `actions[]` | ex. `criar_phases` |
| `avisos[]` | nomes fora do padrão |

`files` só: `interview.md`, `spec.md`, `plan.md`, `analyze.md`.

---

## 6. Apply

```
pwsh "<skill>/scripts/spec.ps1" -Apply [-Dir "phase-1-slug"] [-Slug "frase"]
bash "<skill>/scripts/spec.sh" --apply [--dir phase-1-slug] [--slug frase]
```

Ordem:

1. Inventário de novo.
2. Sem wip → `WIP_AUSENTE`.
3. Resolve destino:
   - `--dir` se veio;
   - senão `alvo` do inventário;
   - senão cria `phase-<next_n>-<slug>`. Sem slug → `SPEC_SEM_ALVO`.
4. `--dir` apontando pasta inexistente ou fora do padrão → `FASE_AUSENTE`.
5. Destino existente com `plan.md` → `SPEC_JA_PLANEJADA`.
6. Destino a criar já existe → `FASE_EXISTE`.
7. Slug sanitizado se for criar. Inválido → `SLUG_INVALIDO`.
8. Cria a pasta só se for `criar`.
9. Cópia binária `spec-wip.md` → `spec.md` (pode sobrescrever rascunho).
10. Tamanho + SHA-256. Falha: apaga só o `spec.md` **novo** desta run se a pasta foi criada vazia; **não** apaga pasta que já tinha `interview.md`. `COPY_HASH_MISMATCH`. Wip permanece.
11. Apaga o wip.
12. Garante `.gitignore`: `spec-report.json`, `spec-wip.md`. Não remove entradas das outras skills.
13. Relatório com `created` e `modo` (`reuse` / `atualizar` / `criar`).

Script não escreve prosa. Não escolhe slug. Não pergunta.

---

## 7. Relatório

`.vibeflow/spec-report.json`:

```json
{
  "root": "...",
  "vibeflow": "ok",
  "phases": "ok",
  "next_n": 2,
  "existing": [],
  "interview_pendente": null,
  "rascunho": null,
  "alvo": {
    "dir": "phase-1-dashboard-standup",
    "n": 1,
    "slug": "dashboard-standup",
    "path": ".vibeflow/phases/phase-1-dashboard-standup",
    "files": ["interview.md"]
  },
  "modo_sugerido": "reuse",
  "wip": "ausente",
  "created": null,
  "modo": null,
  "actions": [],
  "avisos": []
}
```

Depois do apply, `created` é a fase com `spec.md` em `files`. `modo` é o que rodou.

A IA não varre o repo. Lê este JSON, `interview.md` / `spec.md` da alvo, `REGRAS.md`, paths citados.

---

## 8. Artefato vivo

Template: `vibe-spec/templates/spec.md`.

Status no cabeçalho: `rascunho` | `aprovado`.

Seções (omitir a que não se aplica; não inventar):

- Objetivo
- Inventário (só lista multi-item)
- Suposições e decisões
- Escopo e comportamento + Fora
- Direção visual (só UI)
- Checklist de entrega (`A*` aceite, `C*` sucesso)
- Implementação (delta)
- Como provar
- Boundaries (Always / Ask first / Never)
- Handoff (`vibe-plan`)

Sem Open Questions. Sem mural de user story. Sem FR-00N.

---

## 9. Contratos de teste

1. Sem `.vibeflow/` → `INIT_AUSENTE`.
2. Sem `phases/` → cria; `next_n=1`; `modo_sugerido=criar`.
3. `phase-1-a` com `interview.md` → `alvo` é essa pasta; apply **sem** slug grava `spec.md` nela; não cria `phase-2`.
4. Apply sem alvo e sem slug → `SPEC_SEM_ALVO`.
5. Apply sem alvo com slug `Dashboard!!` → `phase-1-dashboard/spec.md`; wip some.
6. Destino com `plan.md` → `SPEC_JA_PLANEJADA`; wip permanece; spec antiga intacta.
7. Rascunho existente: apply sobrescreve `spec.md` com o wip novo.
8. `.gitignore` ganha as duas entradas e preserva `init-report.json` e `interview-report.json`.
9. Hash da cópia ≠ wip → `COPY_HASH_MISMATCH` (coberto pelo fluxo de falha se simulável; apply feliz confere igualdade).
10. `phases` é arquivo → `PHASES_INESPERADO`.
11. Paridade pwsh: apply reuse grava o mesmo path.

Suíte: `docs/vibe-spec/tests/test-spec.py`.

---

## 10. Fora (v1)

- Outras `vibe-*` (plan, analyze, implement, review), CI, hook, `--force`.
- Path `docs/fluxline/`, `specs/`, branch `###-feature`.
- `next_n` quando existe `interview_pendente`.
- Apagar `interview.md`. Pisar pasta com `plan.md`.
- Open Questions no `.md`. Dump da spec no chat. Commit. Disparar plan.

---

## 11. Assumido

- Init já rodou.
- Uma fase = um pedido. Spec entra na pasta do pedido.
- Status `aprovado` é patch no vivo, não segundo apply.
- Sem backup em `old/`: o vivo é a spec. Wip some após hash ok.
