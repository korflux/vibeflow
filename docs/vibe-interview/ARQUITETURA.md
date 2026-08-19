# vibe-interview — arquitetura

`/vibe-interview` fecha intenção ambígua **antes** de spec, plan ou código. O script **inventaria o disco**; a IA **entrevista**; o artefato vivo vai para a pasta da fase.

```
.vibeflow/phases/phase-<n>-<slug>/interview.md
```

`n` é inteiro crescente (1, 2, 3…). `slug` é a frase curta da fase, só `a-z0-9` e hífen. Dentro da mesma pasta as skills seguintes gravam o próprio arquivo (`spec.md`, `plan.md`, …). Esta skill só cria `interview.md`.

---

## 1. Papéis

| Peça | Onde | Faz |
|---|---|---|
| Skill | `vibe-interview/SKILL.md` | Gate, hipóteses, perguntas, restate, Fase 2, grava o wip, dispara apply |
| Scripts | `vibe-interview/scripts/interview.ps1`, `interview.py`, `interview.sh` | Inventário de fases, próximo `n`, slug, promove wip → `interview.md` |
| Template | `vibe-interview/templates/interview.md` | Esqueleto do artefato (a IA preenche; o script não inventa prosa) |
| Referências | `vibe-interview/references/` | Lentes (Fase 2), critérios, calibração. Sob demanda |
| Relatório | `.vibeflow/interview-report.json` | Contrato script → IA (gitignored) |
| Wip | `.vibeflow/interview-wip.md` | Trilha da sessão até o sim (gitignored) |
| Vivo | `.vibeflow/phases/phase-N-slug/interview.md` | Depois do sim. Commitável |

Install recomendado: user-scope (`<grok-home>/skills/vibe-interview`) — `SKILL.md`, `scripts/`, `templates/`, `references/`. Fonte canônica: `vibe-interview/`. Este doc fica em `docs/vibe-interview/` e não vai no install.

---

## 2. Dependência do init

Sem `.vibeflow/` o script para com `INIT_AUSENTE`. Rode `/vibe-init` antes.

`.vibeflow/` existe e `phases/` falta → o script cria `phases/` + `.gitkeep`. Não reescreve `REGRAS.md`. Não cria symlink.

---

## 3. Pasta da fase

Padrão do diretório:

```
^phase-(\d+)-([a-z0-9]+(?:-[a-z0-9]+)*)$
```

Exemplos válidos: `phase-1-dashboard-standup`, `phase-12-lock-por-bloco`.

Regras:

- `n` = máximo `n` já existente + 1. Pastas que não batem no padrão são ignoradas na conta.
- Ordenação é **numérica** (`phase-10` depois de `phase-2`), não lexical.
- Sem zero à esquerda. O script grava `phase-1-…`, não `phase-01-…`.
- `slug`: minúsculas, 2–48 caracteres, hífens simples. Acentos viram ASCII (`métricas` → `metricas`). Lixo vira hífen. O script sanitiza; se o resultado for inválido → `SLUG_INVALIDO`.
- Não renomeia pasta depois de criada. Continuar a mesma fase = editar `interview.md` no lugar.
- Pedido novo = pasta nova com o próximo `n`.
- O script **não apaga** arquivo que já estiver na pasta.

Arquivos previstos na pasta (esta skill só o primeiro):

| Arquivo | Skill |
|---|---|
| `interview.md` | vibe-interview |
| `spec.md` | vibe-spec (depois) |
| `plan.md` | vibe-plan (depois) |
| `analyze.md` | vibe-analyze (depois) |

---

## 4. Fluxo

```
[1] SCRIPT inventário  →  interview-report.json
[2] IA lê o relatório + (se houver) interview.md da fase aberta
[3] Gate + HIPÓTESE/CONFIDENCE
[4] Fase 1 (e Fase 2 se a forma estiver aberta)
    — cada Q/GUESS/R entra no wip na hora
[5] Restate curto no chat + sim explícito
[6] Wip completo (Solicitação, Trilha, Resultado)
[7] SCRIPT apply -Slug <slug>  →  cria phase-N-slug/interview.md, apaga wip
[8] Fecha. Não commita. Não dispara spec.
```

Continuar uma fase **já promovida** (há `interview.md`, não há `spec.md`): a IA edita `interview.md`. Não chama apply de novo.

---

## 5. Inventário (sempre o primeiro passo)

Zero prosa. Classifica o disco e grava o relatório.

| Campo | Significa |
|---|---|
| `vibeflow` | `ausente` / `ok` / `inesperado` |
| `phases` | `ausente` / `ok` / `inesperado` |
| `next_n` | max n + 1, ou 1 se não houver fase válida |
| `existing[]` | `{ dir, n, slug, path, files }` por pasta que bate o padrão |
| `aberta` | fase de maior `n` com `interview.md` e **sem** `spec.md`; senão `null` |
| `wip` | `ausente` / `presente` |
| `actions[]` | ex. `criar_phases` |
| `avisos[]` | pastas em `phases/` que não batem o padrão |

`files` lista só nomes conhecidos da cadeia (`interview.md`, `spec.md`, `plan.md`, `analyze.md`) que existem. Outros arquivos na pasta não são apagados nem inventariados.

---

## 6. Apply

```
pwsh "<skill>/scripts/interview.ps1" -Apply -Slug "<slug>"
bash "<skill>/scripts/interview.sh" --apply --slug "<slug>"
```

Ordem:

1. Inventário de novo (disco pode ter mudado).
2. Recusa sem wip → `WIP_AUSENTE`.
3. Sanitiza o slug.
4. Destino = `.vibeflow/phases/phase-<next_n>-<slug>/`.
5. Se o destino já existe → `FASE_EXISTE`. Não pisa.
6. Cria a pasta. Cópia binária `interview-wip.md` → `interview.md`.
7. Confere tamanho + SHA-256. Se não bater: apaga só o `interview.md` novo, pasta vazia some, wip permanece, `COPY_HASH_MISMATCH`.
8. Só então apaga o wip.
9. Garante `.gitignore` com `interview-report.json` e `interview-wip.md` (não remove entradas do init).
10. Regrava o relatório com `created`.

O script não preenche markdown. Não escolhe slug. Não pergunta.

---

## 7. Relatório

`.vibeflow/interview-report.json` (gitignored):

```json
{
  "root": "...",
  "vibeflow": "ok",
  "phases": "ok",
  "next_n": 2,
  "existing": [
    {
      "dir": "phase-1-dashboard-standup",
      "n": 1,
      "slug": "dashboard-standup",
      "path": ".vibeflow/phases/phase-1-dashboard-standup",
      "files": ["interview.md"]
    }
  ],
  "aberta": {
    "dir": "phase-1-dashboard-standup",
    "n": 1,
    "slug": "dashboard-standup",
    "path": ".vibeflow/phases/phase-1-dashboard-standup",
    "files": ["interview.md"]
  },
  "wip": "ausente",
  "created": null,
  "actions": [],
  "avisos": []
}
```

Depois do apply, `created` é o objeto da fase nova (com `files: ["interview.md"]`) e `aberta` passa a apontar para ela.

A IA lê este JSON. Não varre a árvore do repo à procura de “contexto”. Só abre `interview.md` da `aberta` (continuar) ou paths que o humano citar.

---

## 8. Artefato vivo

O template está em `vibe-interview/templates/interview.md`. Seções:

- **Solicitação** — pedido original, sem reescrever
- **Hipótese inicial** — HIPÓTESE + CONFIDENCE da abertura
- **Trilha** — cada Q / GUESS / R na ordem; correção do chute permanece
- **Resultado** — o mesmo bloco do restate (incluindo Fora; Visual só se fechou)
- **Direção** — só Fase 2; omitir a seção se não houve
- **Handoff** — `vibe-spec` se a forma está fechada; `precisa-forma` se Fase 2 ainda cabe

Chat sozinho não conta. Wip durante a sessão; vivo depois do sim.

---

## 9. Contratos de teste (script, sem framework)

1. Sem `.vibeflow/` → `INIT_AUSENTE`; não cria pasta.
2. `.vibeflow/` sem `phases/` → cria `phases/` + `.gitkeep`; `next_n=1`.
3. `phase-1-a` e `phase-10-b` → `next_n=11` (numérico).
4. Pasta `notes` em `phases/` → aviso; não entra em `existing`.
5. Apply sem wip → `WIP_AUSENTE`.
6. Apply slug `Dashboard Standup!!` → `phase-1-dashboard-standup/interview.md` = bytes do wip; wip some.
7. Segundo apply com outro slug → `phase-2-…`.
8. Slug que sanitiza para vazio → `SLUG_INVALIDO`.
9. Destino já existe → `FASE_EXISTE`; wip permanece.
10. `.gitignore` ganha as duas entradas operacionais e preserva `init-report.json`.
11. Com `interview.md` sem `spec.md` → `aberta` preenchida.
12. Com `spec.md` na mesma pasta → essa fase não é `aberta`.
13. `phases` é arquivo → `PHASES_INESPERADO`.

Suíte em `docs/vibe-interview/tests/`. `test-interview.py` cobre o motor Python e compara o apply essencial com PowerShell quando `pwsh` está disponível.

---

## 10. Fora (v1)

- Outras `vibe-*` (spec, plan, analyze, implement, review), CI, hook, `--force`.
- Inventar `n` ou slug no chat sem passar pelo script.
- Gravar em `docs/`, raiz do repo, ou `interview-fase-N-…md`.
- Escolher a solução na Fase 1. Fechar CSS/paleta. Commit.

---

## 11. Assumido até você contradizer

- Init já rodou (ou o humano roda quando o script recusar).
- Uma fase = um pedido. Spec/plan entram na **mesma** pasta, não numa pasta nova.
- Fase 2 atualiza o mesmo `interview.md`; não cria `refine.md`.
- `aberta` = entrevista ainda sem spec. Continuar = editar o vivo. Pedido diferente = apply novo.
- Old/backup do interview não existe: o vivo é a trilha. Wip some só depois da cópia verificada.
- `old/` do init não é tocado.
