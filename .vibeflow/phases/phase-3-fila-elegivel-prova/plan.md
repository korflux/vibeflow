# Plan: fila elegível e prova em três andares
# Pasta: phase-3-fila-elegivel-prova
# Status: aprovado
# Spec: spec.md (mesma pasta)

## Overview

Entrega o delta da spec: o script da implement projeta a fila do `plan.md` no relatório (`elegiveis` / `bloqueadas`), a skill só pergunta quando há mais de uma T* pronta, e a prova da fatia fica amarrada em três andares (C* na spec já existente, comando no plan, RED-GREEN na implement). Esta run só fatia. A IA futura marca `[x]` neste arquivo.

## Ordem

### Fase 1: Disco da fila

- T1 (schema + parser Python + suíte C1)

### Checkpoint: após T1

- [x] `python docs/vibe-implement/tests/test-implement.py` passa com os casos de `fila`

### Fase 2: Porta e paridade

- T2 (SKILL + DoD)
- T3 (gêmeo PowerShell + C2)

### Checkpoint: após T2–T3

- [x] `python docs/vibe-implement/tests/test-implement.py` passa (parser + trechos da skill + paridade pwsh)

### Fase 3: Plan e escopo

- T4 (template, SKILL e docs do plan + ESCOPO)

### Checkpoint: após T4

- [x] `python docs/vibe-plan/tests/test-plan.py` passa com o freeze do template

## Riscos

| Risco | Impacto | Mitigação |
|---|---|---|
| Parser frouxo trata prosa como T* | alto | Regex só em `### T{n}:`, `concluída` e `Deps`; testes de linha faltando e dep fantasma |
| SKILL continua escolhendo “próxima T*” no feeling | alto | T2 depois de T1; teste de contrato lê o SKILL e exige `fila` / Q de 2+ |
| Plan novo ainda aceita Verificação só manual | médio | T4 congela template e SKILL; teste lê o template |
| Paridade ps1 diverge do Python | médio | T3 gêmeo + um caso C2 na suíte, skip se não houver pwsh |

## Paralelização

- Paralelo ok: T4 com T1 (pacotes distintos, `Deps: nenhuma` nos dois). T2 e T3 entre si depois de T1.
- Sequencial: T2 e T3 depois de T1 (citam o schema `fila`).
- Contrato primeiro, depois lados: T1 trava o parser antes da prosa da skill e do motor gêmeo.

## Tasks

### T1: Parser Python e schema `fila`

- [x] T1 concluída
- **Spec:** A1, A2, A3, A6, C1
- **O quê:** Atualiza ARQUITETURA e ANALISE da implement (campo `fila`, parse `ok|parcial|ausente`, cai o limite “script não interpreta checkbox”). Implementa o parser no `implement.py` e os casos Python de C1 na suíte isolada.
- **Aceite:**
  - [x] Inventário com `plan.md` devolve `fila` no JSON; sem `plan.md` na alvo, `fila` é `null`
  - [x] Duas T* com `Deps: nenhuma` entram em `elegiveis`; T* com dep aberta entra só em `bloqueadas`
  - [x] Sem linha `T{n} concluída`, a T* some da fila, `parse=parcial`, aviso
- **Verificação:**
  - [x] `python docs/vibe-implement/tests/test-implement.py`
- **Deps:** nenhuma
- **Arquivos:** `docs/vibe-implement/ARQUITETURA.md`, `docs/vibe-implement/ANALISE.md`, `vibe-implement/scripts/implement.py`, `docs/vibe-implement/tests/test-implement.py`
- **Size:** high

### Checkpoint: após T1

- [x] `python docs/vibe-implement/tests/test-implement.py` passa com os casos de `fila`

### T2: Skill implement lê `fila` e endurece prova

- [x] T2 concluída
- **Spec:** A1, A2, A4, C3
- **O quê:** SKILL deixa de assumir “próxima T*”. Lê `fila` do relatório: 0/1/2+ elegíveis, R* na frente, humano nomeou T*, modo A no grupo da escolhida. Ciclo da fatia exige RED-GREEN no comando da Verificação; DoD não rebaixa essa barra.
- **Aceite:**
  - [x] Abrir declara `fila` a partir do relatório, não de varredura do plan
  - [x] 2+ elegíveis e T* não nomeada → Q, sem código
  - [x] Sem RED-GREEN não marca `[x]` e não aplica
- **Verificação:**
  - [x] `python docs/vibe-implement/tests/test-implement.py`
- **Deps:** T1
- **Arquivos:** `vibe-implement/SKILL.md`, `vibe-implement/references/definition-of-done.md`
- **Size:** medium

### T3: Gêmeo PowerShell e paridade C2

- [x] T3 concluída
- **Spec:** C2
- **O quê:** `implement.ps1` emite o mesmo `fila` que o Python no caso essencial (duas T*, uma bloqueada por dep). Suíte Python ganha o caso de paridade; skip se não houver pwsh 7.
- **Aceite:**
  - [x] Mesmo `plan.md` de fixture: `elegiveis` e `bloqueadas` iguais nos dois motores
- **Verificação:**
  - [x] `python docs/vibe-implement/tests/test-implement.py`
- **Deps:** T1
- **Arquivos:** `vibe-implement/scripts/implement.ps1`, `docs/vibe-implement/tests/test-implement.py`
- **Size:** medium

### Checkpoint: após T2–T3

- [x] `python docs/vibe-implement/tests/test-implement.py` passa (parser + trechos da skill + paridade pwsh)

### T4: Freeze do plan e linha no ESCOPO

- [x] T4 concluída
- **Spec:** A5, C4
- **O quê:** Template e SKILL do plan congelam `concluída`, `Deps` e Verificação como comando (não “passo manual” sozinho). Checkpoint: suite do grupo; fluxo extra só se o caminho atravessa T*. ARQUITETURA e ANALISE do plan registram o freeze (script do plan continua sem parser). ESCOPO ganha o que entrou.
- **Aceite:**
  - [x] Template não oferece “passo manual” como único exemplo de Verificação
  - [x] SKILL do plan manda Deps reais e recusa Verificação só manual
  - [x] `docs/vibe-plan/tests/test-plan.py` falha se o template perder as linhas congeladas
- **Verificação:**
  - [x] `python docs/vibe-plan/tests/test-plan.py`
- **Deps:** nenhuma
- **Arquivos:** `vibe-plan/SKILL.md`, `vibe-plan/templates/plan.md`, `docs/vibe-plan/ARQUITETURA.md`, `docs/vibe-plan/ANALISE.md`, `docs/vibe-plan/tests/test-plan.py`
- **Size:** high

ESCOPO: uma linha em `docs/ESCOPO.md` no fechamento desta T* (não é fatia extra).

### Checkpoint: após T4

- [x] `python docs/vibe-plan/tests/test-plan.py` passa com o freeze do template

## Conferência

- [x] Spec aprovada como fonte; mesma pasta
- [x] Fatias verticais; size ≤ high
- [x] Toda T* tem aceite + verificação + Spec: A*/C* quando couber
- [x] UI greenfield/sem DS → T* de kit antes das telas (N/A)
- [x] Checkpoints a cada 2–3 T*
- [x] Aprovação humana (leu o arquivo e confirmou)

## Handoff

vibe-implement
