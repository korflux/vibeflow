# Plan: skill vibe-implement
# Pasta: phase-1-vibe-implement
# Status: aprovado
# Spec: spec.md (mesma pasta)

## Overview

Entrega o pacote `vibe-implement` no contrato das irmãs: contrato de disco primeiro, depois o prompt operacional, depois o script de inventário (sem artefato próprio), depois a suíte que trava os invariantes. A IA futura marca `[x]` neste `plan.md` e na spec. Esta run do plan só fatia.

## Ordem

### Fase 1: Contrato

- T1 (ARQUITETURA + ANALISE)

### Checkpoint: após T1

- [x] Paths, schema do relatório, flags e Fora batem com a spec
- [x] ANALISE registra o que veio de Fluxline/spec-kit e o que foi cortado

### Fase 2: Porta operacional

- T2 (SKILL + refs)

### Fase 3: Disco

- T3 (scripts py / ps1 / sh)

### Checkpoint: após T2–T3

- [x] Inventário roda neste repo e grava `implement-report.json`
- [x] SKILL aponta para o script e para as duas refs; sem `--apply`

### Fase 4: Prova de contrato

- T4 (testes + README)

## Riscos

| Risco | Impacto | Mitigação |
|---|---|---|
| SKILL escrita antes do contrato inventa path | alto | T1 primeiro, como as irmãs |
| Script ganha `--apply` por copiar plan/analyze | alto | Spec: inventário só; testes recusam apply |
| Alvo pega fase sem plan ou a fase velha | médio | Maior `n` **com** `plan.md`; `--dir` força |

## Paralelização

- Paralelo ok: nenhum no caminho crítico. T2 e T3 poderiam avançar em paralelo depois de T1, mas o SKILL cita flags do script: sequencial T2 → T3 reduz retrabalho de prosa.
- Sequencial: T1 → T2 → T3 → T4.
- Contrato primeiro, depois lados: T1 é o contrato.

## Tasks

### T1: Fechar o contrato de disco

- [x] T1 concluída
- **Spec:** A6, C2
- **O quê:** Gravar `ARQUITETURA.md` (papéis, inventário, alvo = maior n com plan, relatório, sem apply/slug, files incluindo `review.md`, erros, Fora) e `ANALISE.md` (Fluxline build + spec-kit implement/converge; cortes: implement.md, Playwright proibido, ignore files, hooks).
- **Aceite:**
  - [x] Arquitetura descreve script sem `--apply` e sem artefato `implement.md`
  - [x] Análise deixa explícito DevTools como default e Playwright como opção do humano/T*
- **Verificação:**
  - [ ] Os dois arquivos existem em `docs/vibe-implement/` e não contradizem a spec (leitura cruzada A6 / flags)
- **Deps:** nenhuma
- **Arquivos:** `docs/vibe-implement/ARQUITETURA.md`, `docs/vibe-implement/ANALISE.md`
- **Size:** medium

### Checkpoint: após T1

- [x] Testes da fatia passam
- [x] Fluxo central da fatia ok

### T2: Escrever a porta (SKILL + refs)

- [x] T2 concluída
- **Spec:** A1, A2, A3, A4, A5, C2, C4
- **O quê:** SKILL operacional na ordem das irmãs (invariante, script primeiro, abrir, gate, ciclo TDD, marcar disco, modo A/B, DevTools default, parar com Q, avulso low/medium, Fora). Refs sob demanda: Chrome DevTools (fluxo + leitura do print; Playwright só quando T*/humano mandar) e DoD enxuta.
- **Aceite:**
  - [x] Gate recusa `high+` sem plan, `max` sem analyze, analyze `bloqueado`
  - [x] Default visual é DevTools; Playwright não está no Fora
  - [x] Modo A para; marcar `[x]` só com prova, na mesma resposta
- **Verificação:**
  - [x] Leitura do SKILL: seções 0–Fora presentes; refs existem e são apontadas, não copiadas
- **Deps:** T1
- **Arquivos:** `vibe-implement/SKILL.md`, `vibe-implement/references/chrome-devtools.md`, `vibe-implement/references/definition-of-done.md`
- **Size:** high

### T3: Script de inventário nos três motores

- [x] T3 concluída
- **Spec:** A6
- **O quê:** `implement.py` + gêmeo `.ps1` + launcher `.sh`. Inventário, alvo, gitignore `implement-report.json`, stdout = path do relatório. Sem `--apply` / `--slug`. Sem criar fase. Sem escrever plan/spec.
- **Aceite:**
  - [x] Sem `.vibeflow/` → `INIT_AUSENTE`
  - [x] Sem plan → `alvo` nulo; com plan → maior n; `--dir` força pasta existente
  - [x] `review.md` aparece em `files` se existir
- **Verificação:**
  - [x] `pwsh vibe-implement/scripts/implement.ps1` neste repo imprime o path do relatório e `alvo` aponta `phase-1-vibe-implement` (terá `plan.md` após este apply)
- **Deps:** T1
- **Arquivos:** `vibe-implement/scripts/implement.py`, `vibe-implement/scripts/implement.ps1`, `vibe-implement/scripts/implement.sh`
- **Size:** high

### Checkpoint: após T2–T3

- [x] Testes da fatia passam
- [x] Fluxo central da fatia ok

### T4: Suíte de contrato e linha no README

- [x] T4 concluída
- **Spec:** C1, A6
- **O quê:** `unittest` em pasta isolada: init ausente, cria phases, alvo com plan, `--dir`, gitignore preserva irmãs, `--apply`/`--slug` recusados ou inexistentes, não cria `phase-2`. Paridade pwsh skip se não houver. Uma linha no README.
- **Aceite:**
  - [x] Casos da spec C1 passam
  - [x] README lista `vibe-implement` com o mesmo formato das irmãs
- **Verificação:**
  - [x] `python docs/vibe-implement/tests/test-implement.py`
- **Deps:** T3
- **Arquivos:** `docs/vibe-implement/tests/test-implement.py`, `README.md`
- **Size:** medium

## Conferência

- [x] Spec aprovada como fonte; mesma pasta
- [x] Fatias verticais; size ≤ high
- [x] Toda T* tem aceite + verificação + Spec: A*/C* quando couber
- [x] UI greenfield/sem DS → T* de kit antes das telas (ou N/A)
- [x] Checkpoints a cada 2–3 T*
- [x] Aprovação humana (leu o arquivo e confirmou)

## Handoff

vibe-implement
