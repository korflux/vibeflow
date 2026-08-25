# vibe-spec, arquitetura

`/vibe-spec` grava o **decidido** em disco para o plan não inventar comportamento. A IA pilota a run, entende o motor, escolhe a rota e fecha seams; o script inventaria evidências e promove bytes de forma determinística e verificada.

```
.vibeflow/phases/phase-<n>-<slug>/spec.md
.vibeflow/mvp/spec.md
```

O alvo phase mantém o contrato atual. O alvo MVP é explícito, exige `.vibeflow/mvp/interview.md`, não usa `n`, slug ou dir e nunca cria phase.

---

## 1. Papéis

| Peça | Onde | Faz |
|---|---|---|
| IA | Piloto | Entende o motor, conduz o gate, fecha seams pontuais, audita resultados e decide a semântica |
| Skill | `vibe-spec/SKILL.md` | Orienta a IA com invariantes, gates, critério de aprovação e handoff |
| Scripts | `vibe-spec/scripts/spec.ps1`, `spec.py`, `spec.sh` | Ferramenta determinística: inventário mecânico, resolução de alvo e promoção atômica do wip |
| Template | `vibe-spec/templates/spec.md` | Esqueleto do artefato. O script não preenche prosa |
| Referência | `vibe-spec/references/ui-visual-direction.md` | Guia de direção visual consultado apenas se houver UI |
| Relatório | `.vibeflow/spec-report.json` | Evidência operacional estruturada (gitignored) |
| Wip | `.vibeflow/spec-wip.md` | Rascunho temporário até o apply (gitignored) |
| Vivo | `.vibeflow/phases/phase-N-slug/spec.md` ou `.vibeflow/mvp/spec.md` | Artefato permanente pós-apply. Commitável |

Install: `npx skills` ou marketplace (README). Pacote sem `docs/`. Fonte canônica: `vibe-spec/`.

---

## 2. Dependência

Sem `.vibeflow/` → `INIT_AUSENTE`. `/vibe-init` primeiro.

`phases/` falta → cria + `.gitkeep`. Não mexe em `REGRAS.md` nem symlink.

---

## 3. Alvo da spec

Pasta que bate `^phase-(\d+)-([a-z0-9]+(?:-[a-z0-9]+)*)$`.

O relatório expõe três ponteiros como evidência:

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

A IA inicia entendendo o pedido, os arquivos relevantes do projeto e o motor que executará.

### 4.1 Alvo MVP

`--mvp` no Python/launcher e `-Mvp` no PowerShell selecionam `.vibeflow/mvp/`. A flag representa decisão semântica da IA; o script não tenta detectar um MVP por conta própria.

- `mvp` ausente ou arquivo: `MVP_INTERVIEW_AUSENTE` ou `MVP_INESPERADO`.
- `mvp/interview.md` ausente: `MVP_INTERVIEW_AUSENTE`.
- `mvp/plan.md` presente: `SPEC_JA_PLANEJADA`.
- `--mvp` combinado com slug ou dir: `MODO_INVALIDO`.
- Apply grava `mvp/spec.md` com substituição temporária verificada, confere tamanho e SHA-256 e remove o wip apenas no sucesso.
- O relatório acrescenta `rota: "mvp"`, `mvp.kind: "mvp"` e `alvo` apontando o objeto MVP. Objetos phase recebem `kind: "phase"`.

No artefato MVP, decisões críticas preservam IDs da interview e declaram `mantém`, `cria` ou `substitui`. A spec não altera `REGRAS.md`; publicação só ocorre depois da review humana aprovada.

```
[1] IA entende o motor, seus parâmetros e invariantes
[2] SCRIPT executa inventário → spec-report.json
[3] IA audita relatório, lê interview.md da alvo (se houver), spec.md se rascunho, REGRAS.md e caminhos necessários
[4] IA valida Gate e resolve dúvidas pontuais de desenho via chat (Q + RECOMENDO)
[5] IA grava spec-wip.md conforme templates/spec.md (Status: rascunho)
[6] SCRIPT apply promove wip → spec.md com verificação atômica de integridade
[7] Humano lê o arquivo vivo → solicitação de ajuste ou aprovação
[8] IA fecha a run. Não commita. Não dispara plan automaticamente
```

Depois do `spec.md` existir, ajuste e flip de Status editam o vivo diretamente. Sem apply de novo.


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

`files` só: `interview.md`, `spec.md`, `plan.md`, `analyze.md`, `implement.md`, `review.md`.

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

Modo MVP:

```text
pwsh "<skill>/scripts/spec.ps1" -Apply -Mvp
bash "<skill>/scripts/spec.sh" --apply --mvp
```

Script não escreve prosa, não escolhe rota ou slug e não pergunta.

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

O relatório serve como evidência operacional. A IA lê o JSON, `interview.md` e/ou `spec.md` do alvo, `REGRAS.md` e os arquivos do código necessários de forma direcionada, sem varredura cega da árvore.

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

Suíte: `docs/vibe-spec/tests/test-spec.py`. Launcher: `docs/vibe-spec/tests/test-spec.sh`.

---

## 10. Limites de contrato

- Grava um arquivo só no alvo explícito: `.vibeflow/phases/phase-N-slug/spec.md` ou `.vibeflow/mvp/spec.md`. Sem `docs/`, `specs/`, sem branch `###-feature`.
- `next_n` é proibido enquanto houver `interview_pendente`.
- Não apaga `interview.md`. Não pisa pasta com `plan.md`.
- Fecha comportamento e aceite, não forma: sem `FR-00N`, mural de user story ou CSS/paleta.
- No MVP, exige interview anterior, preserva IDs críticos e nunca atualiza decisões vigentes.

Backlog e decisões de escopo: [`docs/ESCOPO.md`](../ESCOPO.md).

---

## 11. Assumido

- Init já rodou.
- Uma fase = um pedido. Spec entra na pasta do pedido.
- Status `aprovado` é patch no vivo, não segundo apply.
- Sem backup em `old/`: o vivo é a spec. Wip some após hash ok.
