# vibe-analyze, arquitetura

`/vibe-analyze` cruza interview, spec e plan do **mesmo alvo**, corrige inconsistências óbvias nos artefatos, esclarece ambiguidades reais com o usuário e grava **um** relatório de certificação de consistência. A IA pilota a análise semântica e a resolução de qualidade (consistência, decisões críticas, smoke test na T1, comandos executáveis de teste e ferramentas essenciais); o script inventaria evidências e promove bytes de forma determinística e verificada.

```
.vibeflow/phases/phase-<n>-<slug>/analyze.md
.vibeflow/mvp/analyze.md
```

Mesma pasta do plan. Esta skill **não** aloca `n` novo. Sem `plan.md` (e `spec.md`) na pasta, não há analyze.

---

## 1. Papéis

| Peça | Onde | Faz |
|---|---|---|
| IA | Piloto | Entende o motor, cruza interview, spec e plan, corrige erros óbvios nos artefatos, esclarece ambiguidades com o usuário, define veredito limpo e handoff para implementação |
| Skill | `vibe-analyze/SKILL.md` | Orienta a IA com regras de varredura cruzada, resolução de achados, critérios de certificação e handoff |
| Scripts | `vibe-analyze/scripts/analyze.ps1`, `analyze.py`, `analyze.sh` | Ferramenta determinística: inventário mecânico, validação de predecessores e promoção atômica do wip |
| Template | `vibe-analyze/templates/analyze.md` | Esqueleto do artefato. O script não preenche prosa |
| Referência | `vibe-analyze/references/coverage.md` | Taxonomia de passes e severidades. Abrir só na varredura |
| Relatório | `.vibeflow/analyze-report.json` | Evidência operacional estruturada (gitignored) |
| Wip | `.vibeflow/analyze-wip.md` | Rascunho temporário até o apply (gitignored) |
| Vivo | `.vibeflow/phases/phase-N-slug/analyze.md` ou `.vibeflow/mvp/analyze.md` | Artefato permanente pós-apply. Commitável |

Install: `npx skills` ou marketplace (README). Pacote sem `docs/`. Fonte canônica: `vibe-analyze/`.

---

## 2. Dependência

Sem `.vibeflow/` → `INIT_AUSENTE`. `/vibe-init` primeiro.

`phases/` falta → cria + `.gitkeep`. Não mexe em `REGRAS.md` nem symlink.

---

## 3. Alvo do analyze

Pasta que bate `^phase-(\d+)-([a-z0-9]+(?:-[a-z0-9]+)*)$`.

O relatório expõe os ponteiros como evidência:

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

`interview.md` é opcional no modo phase. Ausência vira aviso no relatório da skill (artefato), não erro do script.

Não existe modo `criar` de fase. Analyze não abre pasta.

---

## 4. Fluxo

A IA inicia compreendendo a spec, o plan, o histórico de interview, o ambiente e o motor determinístico.

### 4.1 Alvo MVP

`--mvp` ou `-Mvp` fixa o alvo em `.vibeflow/mvp/` e exige `interview.md`, `spec.md` e `plan.md`. Ausências geram `ANALYZE_SEM_INTERVIEW`, `ANALYZE_SEM_SPEC` ou `ANALYZE_SEM_PLAN`. `--dir` combinado gera `MODO_INVALIDO`.

Apply promove `analyze-wip.md` para `mvp/analyze.md`, sem criar `phase-N`, com verificação atômica de tamanho e SHA-256.

A análise MVP cruza IDs críticos nos três artefatos. Se houver divergência sem declaração de `substitui`, alinha a consistência ou esclarece com o usuário. Analyze nunca publica decisões em `REGRAS.md`.

```
[1] IA entende o motor de analyze, suas entradas e invariantes de segurança
[2] SCRIPT executa inventário → analyze-report.json
[3] IA audita o relatório, lê spec.md, plan.md, interview.md (se houver) e REGRAS.md
[4] IA executa a varredura cruzada (references/coverage.md), corrigindo erros óbvios diretamente em spec.md / plan.md
[5] Perguntas diretas no chat para clarificar ambiguidades reais com o usuário, aplicando as respostas nos artefatos
[6] IA redige analyze-wip.md com cobertura, correções aplicadas e veredito limpo
[7] SCRIPT apply promove wip → analyze.md com verificação atômica de integridade
[8] Humano lê o arquivo vivo → solicitação de ajuste ou aprovação
[9] IA fecha a run com handoff para vibe-implement. Não commita. Não inicia código nesta run
```

Depois do `analyze.md` existir, ajuste e flip de Status editam o vivo diretamente.



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

`files` só: `interview.md`, `spec.md`, `plan.md`, `analyze.md`, `implement.md`, `review.md`.

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

Modo MVP: `analyze.py --apply --mvp`, `analyze.ps1 -Apply -Mvp` ou `analyze.sh --apply --mvp`.

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
O relatório serve como evidência operacional. A IA lê o JSON, `spec.md`, `plan.md`, `interview.md` (se houver), `analyze.md`, `REGRAS.md` e os arquivos de código necessários de forma direcionada, sem varredura cega da árvore.

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

- Grava um arquivo só no alvo explícito phase ou MVP. Sem `tasks.md`, `checklists/`, `docs/`, `specs/`.
- Aplica patches corretivos diretamente em `spec.md` ou `plan.md` para sanar lacunas e inconsistências óbvias identificadas no cruzamento.
- Sem `next_n`, sem `--slug`, sem pasta nova: analyze entra na pasta do plan.
- Veredito e gravidade são semântica da skill; o script não os interpreta.
- No MVP, interview é obrigatória e decisões críticas inconsistentes são resolvidas antes do veredito limpo.


Backlog e decisões de escopo: [`docs/ESCOPO.md`](../ESCOPO.md).

---

## 11. Assumido

- Init, spec e plan já rodaram (ou o humano aceita o recado `ANALYZE_SEM_PLAN`).
- Uma fase = um pedido. Analyze entra na pasta do plan.
- Status `aprovado` é patch no vivo.
- Sem backup em `old/`. Wip some após hash ok.
- Implement ainda não existe: analyze pode ser refeito na mesma pasta.
