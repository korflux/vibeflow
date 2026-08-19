# vibe-implement — arquitetura

`/vibe-implement` executa a próxima fatia da fase e **marca o disco que já existe**. Não grava `implement.md`. O script só inventaria. A IA escreve código no app e edita checkboxes em `plan.md` / `spec.md` / `review.md`.

```
.vibeflow/phases/phase-<n>-<slug>/plan.md   ← fila (T* + checkpoints)
.vibeflow/phases/phase-<n>-<slug>/spec.md   ← A*/C* quando a fatia prova
.vibeflow/phases/phase-<n>-<slug>/review.md ← R* se existir e estiver aberto
```

Mesma pasta do plan. Esta skill **não** aloca `n` novo. Sem `plan.md`, o script devolve `alvo` nulo; a skill decide se a rota `low`/`medium` segue avulsa ou se manda `/vibe-plan`.

---

## 1. Papéis

| Peça | Onde | Faz |
|---|---|---|
| Skill | `vibe-implement/SKILL.md` | Gate, TDD, prova visual, marcar disco, modo A/B, Q+RECOMENDO |
| Scripts | `vibe-implement/scripts/implement.ps1`, `implement.py`, `implement.sh` | Inventário, alvo, gitignore, relatório |
| Referências | `vibe-implement/references/chrome-devtools.md`, `definition-of-done.md` | Sob demanda. Script não lê |
| Relatório | `.vibeflow/implement-report.json` | Contrato script → IA (gitignored) |

Sem template. Sem wip. Sem artefato vivo próprio.

Install: user-scope, pacote sem `docs/`. Fonte canônica: `vibe-implement/`.

---

## 2. Dependência

Sem `.vibeflow/` → `INIT_AUSENTE`. `/vibe-init` primeiro.

`phases/` falta → cria + `.gitkeep`. Não mexe em `REGRAS.md` nem symlink.

---

## 3. Alvo do implement

Pasta que bate `^phase-(\d+)-([a-z0-9]+(?:-[a-z0-9]+)*)$`.

| Campo | Significa |
|---|---|
| `alvo` | Fase que a IA deve ler. Sem `--dir`: maior `n` que tem `plan.md`. Com `--dir`: essa pasta, se existir |

`--dir phase-N-slug` força pasta existente e com nome válido. Inexistente ou fora do padrão → `FASE_AUSENTE`. `--dir` **não** exige `plan.md` (rota `low` pode apontar uma fase sem fila).

Sem `plan.md` em pasta alguma e sem `--dir` → `alvo` nulo, `modo_sugerido=criar`. O script **não** cria pasta e **não** falha. A skill interpreta.

Não existe `--apply` nem `--slug`. Implement não abre fase.

`interview.md`, `analyze.md` e `review.md` são opcionais. O script só lista o que existir.

---

## 4. Fluxo

```
[1] SCRIPT inventário → implement-report.json
[2] IA lê relatório + o que a alvo tiver (interview/spec/plan/analyze/review) + REGRAS.md
[3] Gate (rota, modo A/B, analyze bloqueado, fila R* vs T*)
[4] Descobre test runner do repo. RED→GREEN→REFACTOR → verify
[5] UI web: Chrome DevTools por padrão (ref). Playwright/E2E se T* ou humano mandar
[6] Prova verde → marca [x] nos vivos da cadeia, na mesma resposta
[7] Sem prova → [ ] intacto, Q+RECOMENDO
[8] Modo A: para. Não commita. Não dispara review
```

Ajuste de checkbox é patch no vivo. Sem apply.

---

## 5. Inventário

Zero prosa. Zero interpretação de checkbox ou `# Status:`.

| Campo | Significa |
|---|---|
| `vibeflow` | `ausente` / `ok` / `inesperado` |
| `phases` | `ausente` / `ok` / `inesperado` |
| `next_n` | max n + 1, ou 1 (informativo; apply não existe) |
| `existing[]` | `{ dir, n, slug, path, files }` |
| `alvo` | objeto ou `null` |
| `modo_sugerido` | `reuse` (há alvo) / `criar` (não há fase com plan e não veio `--dir`) |
| `actions[]` | ex. `criar_phases` |
| `avisos[]` | nomes fora do padrão |

`files` só: `interview.md`, `spec.md`, `plan.md`, `analyze.md`, `review.md`.

`modo_sugerido=criar` significa “não há fase com plan para executar”. O script **não** cria.

Campos das irmãs que não se aplicam ficam fixos no JSON para a IA não achar schema partido:

| Campo | Valor nesta skill |
|---|---|
| `wip` | sempre `ausente` |
| `rascunho` | sempre `null` |
| `created` | sempre `null` |
| `modo` | sempre `null` |
| `plan_pendente` | sempre `null` |

---

## 6. Flags e apply

```
pwsh "<skill>/scripts/implement.ps1" [-Root <path>] [-Dir "phase-1-slug"]
bash "<skill>/scripts/implement.sh" [--root <path>] [--dir phase-1-slug]
```

Ordem:

1. Sem `.vibeflow/` → `INIT_AUSENTE`.
2. `phases/` inesperado → `PHASES_INESPERADO`.
3. `phases/` ausente → cria + `.gitkeep`.
4. Garante `.gitignore`: só `implement-report.json`. Não remove entradas das outras skills.
5. Lista fases. Resolve `alvo` ( `--dir` ou maior n com `plan.md` ).
6. Grava o relatório. Stdout = path do relatório.

`--apply`, `--slug`, `-Apply`, `-Slug` **não existem**. Argparse/parameter recusa flag desconhecida (`CODIGO:` no stderr). Sem wip. Sem cópia. Sem escrever `plan.md` / `spec.md`.

---

## 7. Relatório

`.vibeflow/implement-report.json`:

```json
{
  "root": "...",
  "vibeflow": "ok",
  "phases": "ok",
  "next_n": 2,
  "existing": [],
  "plan_pendente": null,
  "rascunho": null,
  "alvo": {
    "dir": "phase-1-vibe-implement",
    "n": 1,
    "slug": "vibe-implement",
    "path": ".vibeflow/phases/phase-1-vibe-implement",
    "files": ["spec.md", "plan.md"]
  },
  "modo_sugerido": "reuse",
  "wip": "ausente",
  "created": null,
  "modo": null,
  "actions": [],
  "avisos": []
}
```

A IA não varre o repo. Lê este JSON, os `.md` da alvo que o relatório listou, `REGRAS.md`. Paths só os que esses arquivos citaram.

---

## 8. Sem artefato vivo

Progresso = checkbox nos arquivos da cadeia. Dono do `plan.md` continua sendo o plan; implement só marca o que a prova cobriu.

A skill **não** preenche markdown de template. Sem `templates/`.

---

## 9. Contratos de teste

1. Sem `.vibeflow/` → `INIT_AUSENTE`.
2. Sem `phases/` → cria; `modo_sugerido=criar`; `alvo` nulo.
3. `phase-1-a` com `plan.md` → `alvo` é essa pasta; não cria `phase-2`.
4. Duas fases com plan: `alvo` é a de maior `n`.
5. Fase sem plan e outra com plan: `alvo` é a que tem plan.
6. `--dir` em pasta existente sem plan → `alvo` é essa pasta (sem erro).
7. `--dir` inexistente ou nome inválido → `FASE_AUSENTE`.
8. `review.md` na fase entra em `files`.
9. `.gitignore` ganha `implement-report.json` e preserva `plan-report.json`.
10. `--apply` / `--slug` → saída ≠ 0 (flag desconhecida). Sem wip criado.
11. `phases` é arquivo → `PHASES_INESPERADO`.
12. Paridade pwsh: inventário reuse aponta o mesmo `alvo.path`.

Suíte: `docs/vibe-implement/tests/test-implement.py`.

---

## 10. Fora (v1)

- Artefato `implement.md`, wip, `--apply`, `--slug`, `--force`.
- Path `docs/fluxline/`, `specs/`, `todo.md`, `tasks.md`, `checklists/`.
- Pasta nova. Inventar `n`.
- Interpretar checkbox ou Status no script.
- Criar ignore de stack (`.npmignore`, `.dockerignore`…).
- Hooks / `extensions.yml` do spec-kit.
- Adicionar Playwright (ou outra lib de browser) como dependência nova sem o humano pedir.
- Open Questions no `.md`. Dump do plan no chat. Commit. Disparar review.

---

## 11. Assumido

- Init já rodou (ou o humano aceita `INIT_AUSENTE`).
- Uma fase = um pedido. Implement reusa a pasta do plan.
- Status `aprovado` do plan/analyze é patch da IA no vivo, não do script.
- Review ainda pode não existir: `review.md` é opcional no inventário.
- Rota e veredito `bloqueado` são semântica da skill, não do script.
