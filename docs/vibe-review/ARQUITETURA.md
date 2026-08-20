# vibe-review — arquitetura

`/vibe-review` julga o patch e a cobertura pós-código e grava **um** veredito. O script inventaria e promove o wip. A IA não edita source da app nem `interview.md` / `spec.md` / `plan.md` / `analyze.md`.

```
.vibeflow/phases/phase-<n>-<slug>/review.md
```

Mesma pasta do plan quando a cadeia existe. Etapa nova = o mesmo arquivo. Sem plan, apply só cria fase nova se veio `--slug` (review avulsa).

---

## 1. Papéis

| Peça | Onde | Faz |
|---|---|---|
| Skill | `vibe-review/SKILL.md` | Gate, eixos, passe cobertura, wip, handoff |
| Scripts | `vibe-review/scripts/review.ps1`, `review.py`, `review.sh` | Inventário, alvo, `--slug`, promove wip → `review.md` |
| Template | `vibe-review/templates/review.md` | Esqueleto. Script não preenche prosa |
| Referências | `references/definition-of-done.md` (pointer), `ui-visual-quality.md`, `security-and-hardening.md` | Sob demanda |
| Relatório | `.vibeflow/review-report.json` | Contrato script → IA (gitignored) |
| Wip | `.vibeflow/review-wip.md` | Rascunho até o apply (gitignored) |
| Vivo | `.vibeflow/phases/phase-N-slug/review.md` | Depois do apply. Commitável |

Install: `npx skills` ou marketplace (README). Pacote sem `docs/`. Fonte canônica: `vibe-review/`.

---

## 2. Dependência

Sem `.vibeflow/` → `INIT_AUSENTE`. `/vibe-init` primeiro.

`phases/` falta → cria + `.gitkeep`. Não mexe em `REGRAS.md` nem symlink.

---

## 3. Alvo da review

Pasta que bate `^phase-(\d+)-([a-z0-9]+(?:-[a-z0-9]+)*)$`.

| Campo | Significa |
|---|---|
| `alvo` | Destino preferido do apply sem `--dir` |
| `plan_pendente` | Maior `n` com `plan.md` e sem `review.md` |
| `rascunho` | Maior `n` com `review.md` |

Resolução de `alvo` (primeira que existir):

1. `plan_pendente`
2. `rascunho`
3. `null`

`--dir phase-N-slug` força pasta existente e com nome válido. Inexistente → `FASE_AUSENTE`. `--dir` **não** exige `plan.md` (review avulsa apontada para uma pasta já criada).

Não pisa `interview.md` / `spec.md` / `plan.md` / `analyze.md` / `implement.md`. Lê `implement.md` se o inventário listar.

---

## 4. Fluxo

```
[1] SCRIPT inventário → review-report.json
[2] IA lê relatório + vivos da alvo + REGRAS.md + diff apontado
[3] Gate (alvo/diff, T* abertas vs “pronto da feature”, etapa 1 vs etapa N)
[4] Testes → cobertura A*/C* × código (se há spec) → eixos; visual/segurança só se o diff pedir
[5] Etapa 1: wip no template + apply. Etapa N: patch no vivo (acrescenta ### Etapa N)
[6] Humano lê o arquivo. Request changes → handoff implement (não dispara)
[7] Etapa seguinte no mesmo arquivo. Não apaga etapa antiga. Não renumerar R* fechados
```

---

## 5. Inventário

Zero prosa. Zero interpretação de checkbox, Status ou diff.

| Campo | Significa |
|---|---|
| `vibeflow` | `ausente` / `ok` / `inesperado` |
| `phases` | `ausente` / `ok` / `inesperado` |
| `next_n` | max n + 1, ou 1 |
| `existing[]` | `{ dir, n, slug, path, files }` |
| `plan_pendente` | objeto ou `null` |
| `rascunho` | objeto ou `null` |
| `alvo` | objeto ou `null` |
| `modo_sugerido` | `reuse` / `atualizar` / `criar` |
| `wip` | `ausente` / `presente` |
| `actions[]` | ex. `criar_phases`, `promover_wip`, `criar_fase` |
| `avisos[]` | nomes fora do padrão |

`files` só: `interview.md`, `spec.md`, `plan.md`, `analyze.md`, `implement.md`, `review.md`.

`modo_sugerido=criar` = não há pasta com plan nem review. Apply **só** cria se veio `--slug`.

---

## 6. Apply

```
pwsh "<skill>/scripts/review.ps1" -Apply [-Dir "phase-1-slug"] [-Slug "frase"]
bash "<skill>/scripts/review.sh" --apply [--dir phase-1-slug] [--slug frase]
```

Ordem:

1. Inventário de novo.
2. Sem wip → `WIP_AUSENTE`.
3. Resolve destino:
   - `--dir` se veio (pasta tem de existir);
   - senão `alvo`;
   - senão `--slug` → cria `phase-<next_n>-<slug>`;
   - senão `REVIEW_SEM_ALVO`.
4. `--dir` inválido → `FASE_AUSENTE`.
5. Destino a criar já existe → `FASE_EXISTE`.
6. Slug sanitizado se for criar. Inválido → `SLUG_INVALIDO`.
7. Cria a pasta só no modo `criar`.
8. Cópia binária `review-wip.md` → `review.md` (pode sobrescrever).
9. Tamanho + SHA-256. Falha: apaga só o `review.md` se **esta** run o criou. `COPY_HASH_MISMATCH`. Wip permanece.
10. Apaga o wip.
11. Garante `.gitignore`: `review-report.json`, `review-wip.md`. Não remove irmãs.
12. Relatório com `created` e `modo` (`reuse` / `atualizar` / `criar`).

Script não escreve prosa. Não julga diff. Não pergunta. Não toca source da app.

---

## 7. Relatório

`.vibeflow/review-report.json`:

```json
{
  "root": "...",
  "vibeflow": "ok",
  "phases": "ok",
  "next_n": 3,
  "existing": [],
  "plan_pendente": {
    "dir": "phase-2-vibe-review",
    "n": 2,
    "slug": "vibe-review",
    "path": ".vibeflow/phases/phase-2-vibe-review",
    "files": ["spec.md", "plan.md"]
  },
  "rascunho": null,
  "alvo": { "dir": "phase-2-vibe-review", "n": 2, "slug": "vibe-review", "path": ".vibeflow/phases/phase-2-vibe-review", "files": ["spec.md", "plan.md"] },
  "modo_sugerido": "reuse",
  "wip": "ausente",
  "created": null,
  "modo": null,
  "actions": [],
  "avisos": []
}
```

A IA não varre o repo. Lê este JSON, os `.md` da alvo, `REGRAS.md`, e o diff que o humano (ou o git da sessão) apontou.

---

## 8. Artefato vivo

Template: `vibe-review/templates/review.md`.

Status: `rascunho` | `request-changes` | `aprovado` | `aprovado-com-defer`.

Seções fixas: Contexto, Checklist de correções (`R*`), Veredito vigente, Handoff, Etapas.

Seções que abrem só se a etapa precisar: Cobertura (há spec), Visual (diff toca UI), Segurança (diff toca input/auth/segredo/upload/pagamento/LLM/dado pessoal), DoD, Notas.

`## Re-review` no rodapé não existe. Cada run acrescenta `### Etapa N` em `## Etapas`. O veredito vigente é o da última etapa.

Sem Open Questions. `R*` bloqueante sem evidência (path) = defeito. Sem editar as fontes da cadeia.

---

## 9. Contratos de teste

1. Sem `.vibeflow/` → `INIT_AUSENTE`.
2. Sem `phases/` → cria; `modo_sugerido=criar`; `alvo` nulo.
3. `phase-1-a` com `plan.md` → `alvo` é essa pasta; apply grava `review.md` nela; não cria `phase-2`.
4. Apply sem alvo e sem `--slug` → `REVIEW_SEM_ALVO`.
5. Apply sem alvo com `--slug x` → cria `phase-<next_n>-x` só com `review.md`.
6. `--dir` inexistente → `FASE_AUSENTE`.
7. Rascunho existente: apply sobrescreve `review.md`.
8. `.gitignore` ganha as duas entradas e preserva `plan-report.json`.
9. `phases` é arquivo → `PHASES_INESPERADO`.
10. `implement.md` na fase entra em `files`.
11. Paridade pwsh: apply reuse grava o mesmo path.

Suíte: `docs/vibe-review/tests/test-review.py`. Launcher: `docs/vibe-review/tests/test-review.sh`.

---

## 10. Limites de contrato

- Não edita source, teste, lockfile, `interview.md`, `spec.md`, `plan.md` nem `analyze.md`. Remédio aponta `vibe-implement`.
- Não anexa T* no plan. Sem `tasks.md`, `docs/`, `specs/`.
- Um `review.md` por fase. Etapa nova é `### Etapa N` no vivo, não segundo arquivo.
- Prova visual default é Chrome DevTools; E2E só quando o repo já tem ou o humano pede. Seção Visual some se o diff não toca UI.
- Sem catálogo fixo de classes de segurança: a seção só abre se o diff toca a superfície listada na skill.

Backlog e decisões de escopo: [`docs/ESCOPO.md`](../ESCOPO.md).

---

## 11. Assumido

- Init já rodou (ou o humano aceita `INIT_AUSENTE`).
- Uma fase = um pedido. Review da cadeia entra na pasta do plan.
- Status do veredito é patch no vivo (e no wip da primeira passagem).
- Sem backup em `old/`. Wip some após hash ok.
- Implement já consome `R*` se o arquivo existir.
