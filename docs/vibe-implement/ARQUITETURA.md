# vibe-implement — arquitetura

`/vibe-implement` executa a fatia elegível da fase, marca o disco da cadeia e grava a trilha em `implement.md`. O script inventaria, projeta `fila` e promove o wip. A IA escreve código, marca checkboxes e preenche o template.

```
.vibeflow/phases/phase-<n>-<slug>/implement.md   ← trilha da run (prova + feedback)
.vibeflow/phases/phase-<n>-<slug>/plan.md        ← fila (T* + checkpoints)
.vibeflow/phases/phase-<n>-<slug>/spec.md        ← A*/C* quando a fatia prova
.vibeflow/phases/phase-<n>-<slug>/review.md      ← R* se existir e estiver aberto
```

Mesma pasta do plan. Esta skill **não** aloca `n` novo se já há alvo. Sem `plan.md`, o script devolve `alvo` nulo (ou a fase com `implement.md`, se for avulsa em andamento); a skill decide se a rota `low`/`medium` abre pasta com `--slug` ou se `high+` manda `/vibe-plan`.

---

## 1. Papéis

| Peça | Onde | Faz |
|---|---|---|
| Skill | `vibe-implement/SKILL.md` | Gate, TDD, prova visual, marcar disco, wip, modo A/B, Q+RECOMENDO |
| Scripts | `vibe-implement/scripts/implement.ps1`, `implement.py`, `implement.sh` | Inventário, alvo, `fila` do plan, `--slug`, promove wip → `implement.md` |
| Template | `vibe-implement/templates/implement.md` | Esqueleto. Script não preenche prosa |
| Referências | `vibe-implement/references/chrome-devtools.md`, `definition-of-done.md` | Sob demanda. Script não lê |
| Relatório | `.vibeflow/implement-report.json` | Contrato script → IA (gitignored) |
| Wip | `.vibeflow/implement-wip.md` | Rascunho até o apply (gitignored) |
| Vivo | `.vibeflow/phases/phase-N-slug/implement.md` | Depois do apply. Commitável |

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
| `alvo` | Destino preferido do apply sem `--dir` |
| `plan_pendente` | Maior `n` com `plan.md` e sem `implement.md` |
| `rascunho` | Maior `n` com `implement.md` |

Resolução de `alvo` (primeira que existir):

1. `--dir` (pasta existente e com nome válido)
2. maior `n` com `plan.md` (`reuse` se ainda não há `implement.md`, `atualizar` se já há)
3. maior `n` com `implement.md` (`atualizar`, avulsa em andamento)
4. `null` (`criar`)

`--dir` inexistente ou fora do padrão → `FASE_AUSENTE`. `--dir` **não** exige `plan.md` (rota `low` pode apontar uma fase sem fila).

Sem alvo e sem `--slug` no apply → `IMPLEMENT_SEM_ALVO`.

`interview.md`, `analyze.md` e `review.md` são opcionais. O script só lista o que existir.

---

## 4. Fluxo

```
[1] SCRIPT inventário → implement-report.json
[2] IA lê relatório + o que a alvo tiver + REGRAS.md
[3] Gate (rota, modo A/B, analyze bloqueado, R* vs `fila` do relatório)
[4] Descobre test runner do repo. RED→GREEN→REFACTOR → verify
[5] UI web: Chrome DevTools por padrão (ref). E2E se T* ou humano mandar
[6] Prova verde → marca [x] nos vivos da cadeia
[7] Wip no template (fatias anteriores copiadas + fatia nova + feedback)
[8] SCRIPT apply
[9] Sem prova → [ ] intacto, sem apply, Q+RECOMENDO
[10] Modo A: para. Não commita. Não dispara review
```

Checkbox é patch no vivo. `implement.md` só entra por apply.

Fatia nova **não** apaga as anteriores: a IA lê o vivo, escreve o wip completo (histórico + fatia desta run) e o apply substitui o arquivo inteiro.

---

## 5. Inventário

Zero prosa. Não interpreta `# Status:`, aceite, verificação, checkpoint nem prosa da T*. Lê só três âncoras no `plan.md` da alvo: `### T{n}:`, `- [ ] T{n} concluída` / `[x]` / `[X]`, `- **Deps:**`.

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
| `actions[]` | ex. `criar_phases`, `promover_wip` |
| `avisos[]` | nomes fora do padrão |
| `fila` | objeto da fila ou `null` (sem `plan.md` na alvo) |

`files` só: `interview.md`, `spec.md`, `plan.md`, `analyze.md`, `implement.md`, `review.md`.

`fila` quando não é `null`:

| Campo | Significa |
|---|---|
| `parse` | `ok` / `parcial` / `ausente` (nenhum `### T{n}:`) |
| `concluidas` | T* com `[x]` / `[X]` na linha `concluída`, ordem numérica |
| `abertas` | T* com `[ ]` na linha `concluída` |
| `elegiveis` | abertas cujas deps estão em `concluidas` |
| `bloqueadas` | `{ id, deps }` — `deps` = ids ainda não concluídos, ou a lista declarada se a dep não existe |
| `avisos` | linha `concluída` faltando, T* duplicada, dep inexistente |

Sem linha `concluída` a T* some das listas e `parse` vira `parcial`. Deps ausente ou `nenhuma` = `[]`. Parse falho não derruba o inventário.

---

## 6. Apply

```
pwsh "<skill>/scripts/implement.ps1" -Apply [-Dir "phase-1-slug"] [-Slug "frase"]
bash "<skill>/scripts/implement.sh" --apply [--dir phase-1-slug] [--slug frase]
```

Ordem:

1. Inventário de novo.
2. Sem wip → `WIP_AUSENTE`.
3. Resolve destino:
   - `--dir` se veio;
   - senão `alvo` do inventário;
   - senão cria `phase-<next_n>-<slug>`. Sem slug → `IMPLEMENT_SEM_ALVO`.
4. `--dir` apontando pasta inexistente ou fora do padrão → `FASE_AUSENTE`.
5. Destino a criar já existe → `FASE_EXISTE`.
6. Slug sanitizado se for criar. Inválido → `SLUG_INVALIDO`.
7. Cria a pasta só se for `criar`.
8. Cópia binária `implement-wip.md` → `implement.md` (pode sobrescrever o vivo).
9. Tamanho + SHA-256. Falha: apaga só o `implement.md` **novo** desta run se a pasta foi criada vazia. `COPY_HASH_MISMATCH`. Wip permanece.
10. Apaga o wip.
11. Garante `.gitignore`: `implement-report.json`, `implement-wip.md`. Não remove entradas das outras skills.
12. Relatório com `created` e `modo` (`reuse` / `atualizar` / `criar`).

Script não escreve prosa. Não escolhe slug. Não pergunta. Não recusa pasta que já tem `plan.md`: essa é a rota normal.

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
  "avisos": [],
  "fila": {
    "parse": "ok",
    "concluidas": ["T1"],
    "abertas": ["T2"],
    "elegiveis": ["T2"],
    "bloqueadas": [],
    "avisos": []
  }
}
```

A IA não varre o repo. Lê este JSON, os `.md` da alvo que o relatório listou, `REGRAS.md`. Paths só os que esses arquivos citaram.

---

## 8. Artefato vivo

`implement.md` guarda a lógica da run (fatia → feito → prova → feedback), não só o recap. Uma seção `## Fatia` por T*/R* concluída. Feedback + / − / para a review omitidos quando vazios.

O script **não** preenche markdown. A IA copia a forma do template.

---

## 9. Contratos de teste

1. Sem `.vibeflow/` → `INIT_AUSENTE`.
2. Sem `phases/` → cria; `modo_sugerido=criar`; `alvo` nulo.
3. `phase-1-a` com `plan.md` → `alvo` é essa pasta; não cria `phase-2`.
4. Duas fases com plan: `alvo` é a de maior `n`.
5. Fase sem plan e outra com plan: `alvo` é a que tem plan.
6. `--dir` em pasta existente sem plan → `alvo` é essa pasta (sem erro).
7. `--dir` inexistente ou nome inválido → `FASE_AUSENTE`.
8. `review.md` e `implement.md` na fase entram em `files`.
9. `.gitignore` ganha `implement-report.json` e `implement-wip.md`, preserva `plan-report.json`.
10. `--apply` sem wip → `WIP_AUSENTE`.
11. `--apply` com wip e alvo com plan → promove `implement.md`, apaga wip, `modo=reuse` ou `atualizar`.
12. Sem alvo, `--apply --slug` cria `phase-N-slug/implement.md`.
13. Sem alvo, `--apply` sem slug → `IMPLEMENT_SEM_ALVO`.
14. `phases` é arquivo → `PHASES_INESPERADO`.
15. Paridade pwsh: apply reuse grava o mesmo path; `fila` de duas T* (uma bloqueada por dep) bate com o Python.
16. Sem `plan.md` na alvo → `fila` nulo.
17. Uma T* `[x]` e a seguinte aberta com essa dep → só a aberta em `elegiveis`.
18. Duas T* abertas com `Deps: nenhuma` → as duas em `elegiveis`.
19. T* com dep aberta → `bloqueadas` com essa dep; não entra em `elegiveis`.
20. Sem linha `T{n} concluída` → T* omitida, `parse=parcial`, aviso.
21. `plan.md` sem `### T{n}:` → `parse=ausente`, listas vazias.

Suíte: `docs/vibe-implement/tests/test-implement.py`. Launcher: `docs/vibe-implement/tests/test-implement.sh`.

---

## 10. Limites de contrato

- Um `implement.md` por fase. Fatia nova é seção no mesmo arquivo, via wip completo + apply.
- Não grava `todo.md`, `tasks.md`, `checklists/` nem path fora de `.vibeflow/phases/phase-N-slug/`.
- O script não interpreta `# Status:`, aceite, verificação nem prosa. A fila no relatório sai só de `### T{n}:`, da linha `concluída` e de `Deps`.
- Não cria ignore de stack (`.npmignore`, `.dockerignore`…).
- Não adiciona lib de browser como dependência nova sem o humano pedir.

Backlog e decisões de escopo: [`docs/ESCOPO.md`](../ESCOPO.md).

---

## 11. Assumido

- Init já rodou (ou o humano aceita `INIT_AUSENTE`).
- Uma fase = um pedido. Implement reusa a pasta do plan.
- Status `aprovado` do plan/analyze é patch da IA no vivo, não do script.
- Review ainda pode não existir: `review.md` é opcional no inventário.
- Rota e veredito `bloqueado` são semântica da skill, não do script.
