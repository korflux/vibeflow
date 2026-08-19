# Plan: skill vibe-review
# Pasta: phase-2-vibe-review
# Status: aprovado
# Spec: spec.md (mesma pasta)

## Overview

Entrega o pacote `vibe-review` no contrato das irmãs que gravam artefato: contrato de disco, porta + template + refs, script com apply, suíte. A implement futura marca `R*` no `review.md`. Esta run só fatia.

## Ordem

### Fase 1: Contrato

- T1 (ARQUITETURA + ANALISE)

### Checkpoint: após T1

- [x] Paths, apply, alvo, avulsa `--slug` e Fora batem com a spec
- [x] ANALISE separa Fluxline review de spec-kit converge e registra o corte do plan

### Fase 2: Porta e refs

- T2 (SKILL + template)
- T3 (três refs)

### Checkpoint: após T2–T3

- [x] SKILL aponta script, template e refs; read-only no source
- [x] Template tem Checklist de correções `R*` + cobertura + veredito

### Fase 3: Disco

- T4 (scripts py / ps1 / sh)

### Checkpoint: após T4

- [x] Inventário+apply no contrato (reuse da pasta com plan; sem alvo+slug falha)

### Fase 4: Prova

- T5 (testes + README)

## Riscos

| Risco | Impacto | Mitigação |
|---|---|---|
| Script copia analyze e exige plan sempre | alto | Avulsa `--slug`; `REVIEW_SEM_ALVO` só sem alvo e sem slug |
| Converge vira append no `plan.md` | alto | Fora na arquitetura e na skill |
| Review aloca N novo com plan aberto | alto | Alvo = plan sem review, senão rascunho |
| Pack de security inchado | médio | T3 só as três refs da spec |

## Paralelização

- Paralelo ok: T2 e T3 depois de T1 (refs não dependem do texto final do SKILL).
- Sequencial: T1 → (T2 ∥ T3) → T4 → T5.
- Contrato primeiro.

## Tasks

### T1: Fechar o contrato de disco

- [x] T1 concluída
- **Spec:** A1, A4, C2
- **O quê:** `ARQUITETURA.md` (papéis, alvo, apply, `--slug` avulsa, hash do wip, relatório, erros, Fora) e `ANALISE.md` (Fluxline review + spec-kit converge; corte: T* no plan, 16 classes, Playwright default).
- **Aceite:**
  - [x] Arquitetura descreve apply + `REVIEW_SEM_ALVO` + reuse da pasta do plan
  - [x] Análise deixa explícito: gap de cobertura = `R*`, não append no plan
- **Verificação:**
  - [x] Os dois arquivos existem em `docs/vibe-review/` e não contradizem A1/A4
- **Deps:** nenhuma
- **Arquivos:** `docs/vibe-review/ARQUITETURA.md`, `docs/vibe-review/ANALISE.md`
- **Size:** medium

### Checkpoint: após T1

- [x] Testes da fatia passam
- [x] Fluxo central da fatia ok

### T2: Escrever a porta e o molde

- [x] T2 concluída
- **Spec:** A2, A3, A5, A6, C2, C3, C4
- **O quê:** SKILL na ordem das irmãs (script primeiro, gate, testes, cobertura, cinco eixos, wip/apply, re-review, Fora). Template com as seções da spec.
- **Aceite:**
  - [x] Read-only no source; handoff implement; Approve sem Critical/Required abertos
  - [x] Passe cobertura e Checklist `R*` estão no SKILL e no template
- **Verificação:**
  - [x] Leitura: seções 0–Fora; template sem prosa de exemplo colável
- **Deps:** T1
- **Arquivos:** `vibe-review/SKILL.md`, `vibe-review/templates/review.md`
- **Size:** high

### T3: Refs sob demanda

- [x] T3 concluída
- **Spec:** A6
- **O quê:** Pointer DoD para a implement; `ui-visual-quality.md` curta (julgamento, DevTools default); `security-and-hardening.md` uma peça. Sem pasta `security/`.
- **Aceite:**
  - [x] DoD não duplica o checklist da implement
  - [x] Visual e security são apontados pelo SKILL, não copiados nele
- **Verificação:**
  - [x] Os três arquivos existem; pointer resolve para `vibe-implement/references/definition-of-done.md`
- **Deps:** T1
- **Arquivos:** `vibe-review/references/definition-of-done.md`, `vibe-review/references/ui-visual-quality.md`, `vibe-review/references/security-and-hardening.md`
- **Size:** medium

### Checkpoint: após T2–T3

- [x] Testes da fatia passam
- [x] Fluxo central da fatia ok

### T4: Script nos três motores

- [x] T4 concluída
- **Spec:** A1, A4
- **O quê:** `review.py` + `.ps1` + `.sh`. Inventário, apply, gitignore, hash. Reuse pasta com plan. `--slug` só se não há alvo. Sem `--force`.
- **Aceite:**
  - [x] Fase com plan e sem review → apply grava nela; não cria `phase-N+1`
  - [x] Sem alvo e sem slug → `REVIEW_SEM_ALVO`
  - [x] `--slug` sem alvo cria fase só com `review.md`
- **Verificação:**
  - [x] `pwsh vibe-review/scripts/review.ps1` neste repo: `alvo` = `phase-2-vibe-review` (após este plan existir) ou a regra da arquitetura
- **Deps:** T1
- **Arquivos:** `vibe-review/scripts/review.py`, `vibe-review/scripts/review.ps1`, `vibe-review/scripts/review.sh`
- **Size:** high

### Checkpoint: após T4

- [x] Testes da fatia passam
- [x] Fluxo central da fatia ok

### T5: Suíte de contrato e README

- [x] T5 concluída
- **Spec:** C1, A1, A4
- **O quê:** `unittest` isolado: init, reuse plan, slug avulsa, `REVIEW_SEM_ALVO`, overwrite, gitignore, `FASE_AUSENTE`, paridade pwsh skip. Linha no README.
- **Aceite:**
  - [x] Casos C1 passam
  - [x] README lista `vibe-review` no formato das irmãs
- **Verificação:**
  - [x] `python docs/vibe-review/tests/test-review.py`
- **Deps:** T4
- **Arquivos:** `docs/vibe-review/tests/test-review.py`, `README.md`
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
