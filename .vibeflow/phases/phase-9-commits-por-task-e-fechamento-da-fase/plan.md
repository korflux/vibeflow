# Plan: commits por task e fechamento da fase
# Alvo: phase-9-commits-por-task-e-fechamento-da-fase
# Status: aprovado
# Spec: spec.md (mesma pasta)

## Overview

Migrar o contrato operacional para que a task seja a única unidade de execução e commit, remover agrupamentos intermediários das instruções canônicas, proteger commits contra mistura com trabalho pré-existente e transformar o fechamento pós-review no único push da fase. A mudança inclui a correção de seleção de nova phase por slug explícito e testes de contrato para Python e PowerShell.

## Ordem

### Fase 1: ciclo Git por task e fechamento da phase

- T1

## Riscos

| Risco | Impacto | Mitigação |
|---|---|---|
| A orientação de commit misturar alterações pré-existentes | alto | snapshot de estado, staging explícito por path, diff indexado obrigatório e bloqueio quando houver sobreposição |
| Skills divergirem entre si após remover agrupamentos intermediários | médio | atualizar pacote, arquitetura, análise, README, escopo, templates e testes na mesma fatia |
| Push final ocorrer antes do veredito humano | alto | precondições explícitas no review, sem push por task, sem force e upstream obrigatório |

## Paralelização

- Paralelo ok: não há, a mudança é um contrato transversal único.
- Sequencial: confirmar que a fila não depende de agrupamento intermediário, atualizar as orientações, atualizar testes, executar a regressão completa.
- Contrato primeiro, depois paralelo: a semântica de commit por task e finalização deve estar fechada antes da documentação secundária e dos testes textuais.

## Tasks

### T1: Migrar o fluxo Git para commits isolados por task

- [ ] T1 concluída
- **Spec:** A1, A2, A3, A4, A5, A6, C1, C2, C3, C4, C5
- **O quê:** Remover agrupamentos intermediários da superfície operacional e documentar a task como unidade de execução, prova e parada. Após cada task verde, orientar commit path-scoped sem push; após review aprovada, orientar commit residual e push final da phase. Corrigir a seleção de slug explícito nos dois motores de spec e cobrir o contrato com testes.
- **Aceite:**
  - [x] Pacotes, templates, docs canônicos, README, escopo e regras não usam agrupamento intermediário como gate, agrupamento ou verificação, e a fila continua dependendo somente de `T* concluída` e `Deps`.
  - [x] `vibe-implement` instrui teste verde, atualização dos vivos, validação do diff indexado, staging explícito e commit por task sem push, `git add -A` ou `Co-Authored-By`, incluindo bloqueio para path pré-existente alterado.
  - [x] `vibe-review` instrui commit/push final somente após Approve, confirmação humana, R* bloqueantes fechados, suíte final, `git diff --check` e gitleaks quando previsto, sem force; os dois motores de spec respeitam slug explícito com rascunho antigo.
- **Verificação:**
  - [x] `python docs/vibe-spec/tests/test-spec.py -v`
  - [x] `python docs/vibe-plan/tests/test-plan.py -v`
  - [x] `python docs/vibe-implement/tests/test-implement.py -v`
  - [x] `python docs/vibe-review/tests/test-review.py -v`
  - [x] `python docs/tests/test-distribuicao.py -v`
  - [x] `git diff --check`
  - [x] `gitleaks detect --source . --verbose --redact --no-banner`
- **Prova:** implementação e regressão final verdes. O commit da task não foi criado nesta sessão porque o worktree já tinha alterações anteriores nos mesmos paths; o isolamento é pré-condição para concluir T1 sem mistura.
- **Deps:** nenhuma
- **Arquivos:** `vibe-plan/SKILL.md`, `vibe-plan/templates/plan.md`, `vibe-implement/SKILL.md`, `vibe-implement/templates/implement.md`, `vibe-implement/scripts/implement.py`, `vibe-implement/scripts/implement.ps1`, `vibe-review/SKILL.md`, `vibe-review/templates/review.md`, `vibe-spec/scripts/spec.py`, `vibe-spec/scripts/spec.ps1`, `docs/vibe-plan/`, `docs/vibe-implement/`, `docs/vibe-review/`, `docs/vibe-spec/tests/test-spec.py`, `docs/vibe-implement/tests/test-implement.py`, `docs/tests/test-distribuicao.py`, `README.md`, `docs/ESCOPO.md`, `.vibeflow/REGRAS.md`
- **Size:** high, 8/10, contrato transversal em quatro skills, documentação e testes, com verificação de fila, paridade de motores e operação Git controlada
- **Risk:** high, muda commit e push automáticos e pode misturar trabalho local se o escopo não for validado

## Conferência

- [x] Spec aprovada como fonte; mesma pasta
- [x] Fatia vertical; score de Size ≤ 8; Risk separado
- [x] T1 tem aceite + verificação + Spec: A*/C* quando couber
- [x] Ferramentas essenciais, gitleaks e Git, validadas; não há UI
- [x] T1 estabelece smoke test real com `python vibe-spec/scripts/spec.py --help`
- [x] UI greenfield/sem DS: N/A
- [x] Nenhum agrupamento especial entre tasks
- [x] Aprovação humana, o pedido explicitamente autoriza seguir para implementação

## Handoff

vibe-implement

- Chat: abrir novo chat para a implementação é recomendado; continuidade nesta sessão foi escolhida conscientemente para concluir a mudança.
