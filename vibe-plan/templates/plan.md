# Plan: <frase curta>
# Alvo: <phase-<n>-<slug> ou mvp>
# Status: rascunho
# Spec: spec.md (mesma pasta)

## Overview

<1 parágrafo: o que esta entrega realiza, apontando a spec>

## Ordem

### Fase 1: <nome>

- T1-T2 (corpo em Tasks)

### Checkpoint: após T1-T2

- [ ] `<comando da suite do grupo>`
- [ ] <fluxo do grupo, omitir se o caminho não atravessa T*>

### Fase 2: <nome>

- T3-...

## Riscos

| Risco | Impacto | Mitigação |
|---|---|---|
| ... | alto / médio / baixo | ... |

## Paralelização

- Paralelo ok: ...
- Sequencial: ...
- Contrato primeiro, depois paralelo: ...

## Tasks

### T1: <verbo + outcome (smoke test / walking skeleton ou setup de ferramentas)>

- [ ] T1 concluída
- **Spec:** A1, C1
- **Decisões:** <AUTH-01 (mantém), INFRA-01 (cria); omitir quando N/A>
- **O quê:** <1–3 frases>
- **Aceite:**
  - [ ] <condição testável>
- **Verificação:**
  - [ ] `<comando do repo>`
- **Deps:** nenhuma
- **Arquivos:** `path/...`
- **Size:** `<low | medium | high>, <score>/10, <justificativa curta>`
- **Risk:** `<low | medium | high>, <motivo curto quando não for low>`

### Checkpoint: após T1-T2

- [ ] `<comando da suite do grupo>`
- [ ] <fluxo do grupo, omitir se o caminho não atravessa T*>

## Conferência

- [x] Spec aprovada como fonte; mesma pasta
- [x] Fatias verticais; score de Size ≤ 8; Risk separado
- [x] Toda T* tem aceite + verificação + Spec: A*/C* quando couber
- [x] Ferramentas essenciais (gitleaks, chrome-devtools) validadas ou com task de setup
- [x] T1 estabelece ponto de entrada real (smoke test / walking skeleton)
- [x] UI greenfield/sem DS → T* de kit antes das telas (ou N/A)
- [x] Checkpoints a cada 2–3 T*
- [ ] Aprovação humana (leu o arquivo e confirmou)

## Handoff

<vibe-implement no phase sem analyze obrigatório; vibe-analyze no MVP>
<!-- No MVP, acrescentar: rota: max -->
