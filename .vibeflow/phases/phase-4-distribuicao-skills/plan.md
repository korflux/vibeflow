# Plan: distribuição das skills para Codex, Claude, Grok e Antigravity
# Pasta: phase-4-distribuicao-skills
# Status: aprovado
# Spec: spec.md (mesma pasta)

## Overview

Deixa o repo `korflux/vibeflow` instalável pelas sete `vibe-*` via `npx skills` e via marketplace nativo de Claude, Codex, Grok e Antigravity, sem mover os pacotes canônicos e sem aliases de slash.

## Ordem

### Fase 1: plugin instalável

- T1–T2 (corpo em Tasks)

### Checkpoint: após T1–T2

- [x] `python docs/tests/test-distribuicao.py`

### Fase 2: docs e CI

- T3

### Checkpoint: após T3

- [x] `python docs/tests/test-distribuicao.py`

## Riscos

| Risco | Impacto | Mitigação |
|---|---|---|
| `npx skills` lista 14 nomes (`vibe-*` na raiz + `skills/`) | alto | `skills/` no local padrão do CLI; C1 falha se `name` duplicar |
| Claude carrega `skills/` e `./vibe-*` | médio | manifest Claude lista só `./vibe-*`, source `./` |
| Checkout Windows com symlink falso | médio | git mode 120000 + teste C2; mesmo aviso do init |

## Paralelização

- Paralelo ok: nenhuma. T3 lê strings que T1–T2 ainda não gravaram.
- Sequencial: T1 → T2 → T3
- Contrato primeiro, depois paralelo: o teste nasce em T1 (RED) e fica verde em T2

## Tasks

### T1: teste de contrato da distribuição (RED)

- [x] T1 concluída
- **Spec:** C1, C2, C3, C4, C5
- **O quê:** Nasce `docs/tests/test-distribuicao.py` cobrindo os sete ponteiros, os manifests JSON, a ausência de `commands/` de alias, as strings de install no README e a suíte no workflow. Sem os arquivos da T2/T3 o teste falha.
- **Aceite:**
  - [x] O arquivo existe e `python docs/tests/test-distribuicao.py` termina com FAIL (ainda não há `skills/` nem manifests)
- **Verificação:**
  - [x] `python docs/tests/test-distribuicao.py`
- **Deps:** nenhuma
- **Arquivos:** `docs/tests/test-distribuicao.py`
- **Size:** medium

### T2: `skills/` e manifests nativos (GREEN de C1–C3)

- [x] T2 concluída
- **Spec:** A1, C1, C2, C3
- **O quê:** Sete symlinks git `skills/vibe-<nome>` → `../vibe-<nome>`. Manifests Claude, Codex, Grok e Antigravity com plugin `vibeflow` 1.0.0, sem `commands/`.
- **Aceite:**
  - [x] Cada symlink resolve para pacote com `SKILL.md`
  - [x] Os quatro agentes têm JSON válido apontando as sete skills
  - [x] Frontmatters em `skills/` dão sete `name` únicos
- **Verificação:**
  - [x] `python docs/tests/test-distribuicao.py`
- **Deps:** T1
- **Arquivos:** `skills/vibe-*`, `.claude-plugin/marketplace.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `.grok-plugin/marketplace.json`, `plugin.json`
- **Size:** high

### Checkpoint: após T1–T2

- [x] `python docs/tests/test-distribuicao.py`

### T3: README, regras, escopo, CI (GREEN de C4–C5)

- [x] T3 concluída
- **Spec:** A1, A2, C4, C5
- **O quê:** Quick Start no README (CLI global/projeto + quatro nativos). Bloco Estrutura em `REGRAS.md`. ESCOPO marca a rodada. Uma linha de install nas sete `ARQUITETURA.md`. CI passa a rodar `docs/tests/test-distribuicao.py`. Sem aliases de slash.
- **Aceite:**
  - [x] README contém os comandos da spec
  - [x] Workflow executa a suíte nova
  - [x] A suíte inteira passa
- **Verificação:**
  - [x] `python docs/tests/test-distribuicao.py`
- **Deps:** T2
- **Arquivos:** `README.md`, `.vibeflow/REGRAS.md`, `docs/ESCOPO.md`, `docs/vibe-*/ARQUITETURA.md`, `.github/workflows/contrato.yml`
- **Size:** medium

### Checkpoint: após T3

- [x] `python docs/tests/test-distribuicao.py`

## Conferência

- [x] Spec aprovada como fonte; mesma pasta
- [x] Fatias verticais; size ≤ high
- [x] Toda T* tem aceite + verificação + Spec: A*/C* quando couber
- [x] UI greenfield/sem DS → T* de kit antes das telas (ou N/A)
- [x] Checkpoints a cada 2–3 T*
- [x] Aprovação humana (leu o arquivo e confirmou)

## Handoff

vibe-implement
