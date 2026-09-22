# Plan: <frase curta>
# Alvo: <phase-<n>-<slug> ou mvp>
# Status: rascunho
# Spec: spec.md (mesma pasta)

<!-- Escreva diretamente neste artefato vivo; o status permanece rascunho durante a elaboração. -->

## Overview

<1 parágrafo: o que esta entrega realiza, apontando a spec>
- **Design:** <path aprovado ou N/A>

## Preparo (opcional, checklist curta, não é task)

- [ ] <comandos e ferramentas necessários à prova: disponíveis, limitação ou bloqueio>

## Tasks

### T1: <verbo + resultado coeso>

- [ ] T1 concluída
- **Spec:** A1, C1
- **O quê:** <resultado observável>
- **Aceite:**
  - [ ] <condição testável>
- **Verificação:**
  - [ ] `<comando do repo>`
- **Deps:** nenhuma
- **Decisões:** <ID (ação); omitir quando N/A>
- **Arquivos:** `path/...` <!-- opcional, quando orientar execução ou ownership -->
- **Risco:** <somente se alterar isolamento, verificação ou review>

## Paralelização (opcional, omitir quando não aplicável)

- T* que podem executar juntas: <grupo e condição de isolamento, sem repetir a fila de Deps>

## Checkpoint de review (opcional, omitir quando não houver justificativa)

- <marco, superfície a revisar e risco ou contrato compartilhado que justifica o checkpoint>

## Handoff

<vibe-implement no phase sem analyze obrigatório; vibe-analyze no MVP>
<!-- No MVP, acrescentar: rota: max -->

- Chat: recomende novo chat para `vibe-implement` ou `vibe-analyze` no MVP; continuidade no mesmo chat só por escolha consciente. O `plan.md` vivo é a ponte.
