# Plan: rota MVP no vibe-interview
# Pasta: phase-6-modulo-mvp-vibe-interview
# Status: aprovado
# Spec: spec.md (mesma pasta)

## Overview

Implementar a rota MVP aprovada em `spec.md` sem quebrar o fluxo atual por phases. O trabalho fecha primeiro o contrato global, adapta cada porta da cadeia com alvo explícito `--mvp`/`-Mvp`, adiciona descoberta condicional no interview e termina com uma prova integrada das seis portas em `.vibeflow/mvp/`.

## Ordem

### Fase 1: contrato e porta de entrada

- T1-T3 (contrato global, prompt do interview e motores do interview)

### Checkpoint: após T1-T3

- [x] `python docs/vibe-interview/tests/test-interview.py -v`
- [ ] `bash docs/vibe-interview/tests/test-interview.sh`, bloqueado neste host: WSL não possui `/bin/bash`
- [x] Fluxo: interview normal continua em phase e interview MVP promove somente `.vibeflow/mvp/interview.md`.

### Fase 2: especificação no alvo MVP

- T4-T5 (contrato e motores da spec)

### Checkpoint: após T4-T5

- [x] `python docs/vibe-spec/tests/test-spec.py -v`
- [x] Fluxo: interview e spec coexistem em `.vibeflow/mvp/`, sem criar phase.

### Fase 3: planejamento no alvo MVP

- T6-T7 (contrato e motores do plan)

### Checkpoint: após T6-T7

- [x] `python docs/vibe-plan/tests/test-plan.py -v`
- [x] Fluxo: interview, spec e plan coexistem em `.vibeflow/mvp/`, sem criar phase.

### Fase 4: análise obrigatória

- T8-T9 (contrato e motores do analyze)

### Checkpoint: após T8-T9

- [x] `python docs/vibe-analyze/tests/test-analyze.py -v`
- [x] Fluxo: analyze cruza interview, spec e plan no alvo MVP e bloqueia conflito implícito.

### Fase 5: implementação no alvo MVP

- T10-T11 (contrato e motores da implement)

### Checkpoint: após T10-T11

- [x] `python docs/vibe-implement/tests/test-implement.py -v`
- [x] Fluxo: implement MVP recusa ausência de analyze aprovado e usa a fila do plan no alvo especial.

### Fase 6: review, decisões vigentes e regressão integral

- T12-T14 (contrato e motores da review, sincronização e teste ponta a ponta)

### Checkpoint: após T12-T14

- [x] `python docs/vibe-review/tests/test-review.py -v`
- [x] `python docs/tests/test-mvp-flow.py -v`
- [x] `python docs/tests/test-distribuicao.py -v`
- [ ] `gitleaks detect --source . --verbose --redact --no-banner` quando o executável estiver disponível
- [x] `git diff --check`
- [x] Fluxo: cadeia max completa em `.vibeflow/mvp/`, decisão vigente sincronizada somente após review aprovada e fluxo phase sem regressão.

## Riscos

| Risco | Impacto | Mitigação |
|---|---|---|
| Uma porta continuar aceitando apenas `phase-N-slug` | alto | Teste integrado atravessa as seis portas no mesmo alvo MVP |
| Seleção automática capturar phase antiga durante modo MVP | alto | Flag explícita e relatório com `kind`, sem inferência do script |
| Review publicar decisão antes da aprovação | alto | Teste de estados rascunho, request-changes e aprovado |
| Novo modo alterar o comportamento phase | alto | Reexecutar contratos existentes em todas as portas |
| Sobreposição com a diff local do `vibe-init` | alto | Patch mínimo no template atual, sem restaurar conteúdo anterior |
| Catálogo virar formulário extenso | médio | Referência condicional e regra explícita de blocos pequenos no SKILL |

## Paralelização

- Paralelo ok: contratos T2, T4, T6, T8, T10 e T12 depois de T1, pois pertencem a portas distintas.
- Sequencial: cada motor depende do contrato da própria porta; T14 depende de todos os motores.
- Contrato primeiro, depois paralelo: T1 fixa path, flag, ordem e schema aditivo antes das implementações.

## Tasks

### T1: Fixar o contrato global da rota MVP

- [x] T1 concluída
- **Spec:** A4, A9, A10, A12
- **O quê:** Atualizar as regras canônicas, limites de escopo, template do init e README para reconhecer `.vibeflow/mvp/`, rota max obrigatória e tabela compacta de decisões vigentes. Preservar a diff local do `vibe-init`.
- **Aceite:**
  - [x] `.vibeflow/mvp/` é a única exceção ao path `phase-N-slug`.
  - [x] Regras definem baseline histórico, substituição explícita e sincronização somente após review aprovada.
  - [x] O template atual do init recebe apenas a seção opcional necessária, sem perda das alterações do usuário.
- **Verificação:**
  - [x] `git diff --check -- .vibeflow/REGRAS.md docs/ESCOPO.md vibe-init/templates/REGRAS.md README.md`
- **Deps:** nenhuma
- **Arquivos:** `.vibeflow/REGRAS.md`, `docs/ESCOPO.md`, `vibe-init/templates/REGRAS.md`, `README.md`
- **Size:** high

### T2: Especificar a descoberta adaptativa no interview

- [x] T2 concluída
- **Spec:** A1, A2, A6, A7, A8, A9, C5
- **O quê:** Reescrever o prompt operacional do interview conforme IA piloto, criar o catálogo condicional de MVP, estender o template único e atualizar arquitetura e análise da skill.
- **Aceite:**
  - [x] A IA distingue produto novo de feature e usa blocos pequenos somente no modo MVP.
  - [x] Cobertura, recomendações, stack, visual, infraestrutura, acesso e break-glass seguem as decisões aprovadas.
  - [x] Template normal permanece utilizável e omite todas as seções MVP quando não aplicáveis.
- **Verificação:**
  - [x] `python docs/tests/test-distribuicao.py -v`
- **Deps:** T1
- **Arquivos:** `vibe-interview/SKILL.md`, `vibe-interview/references/mvp-discovery.md`, `vibe-interview/templates/interview.md`, `docs/vibe-interview/ARQUITETURA.md`, `docs/vibe-interview/ANALISE.md`
- **Size:** high

### T3: Promover o interview para o alvo MVP com paridade

- [x] T3 concluída
- **Spec:** A3, A5, A11, C1, C2, C3
- **O quê:** Adicionar `--mvp`/`-Mvp` aos motores e launcher do interview, relatório aditivo com alvo explícito e contratos RED/GREEN para criação única e preservação do modo phase.
- **Aceite:**
  - [x] Apply MVP promove bytes para `.vibeflow/mvp/interview.md`, confere tamanho e hash e remove wip somente depois.
  - [x] Segundo apply MVP recusa sobrescrita e preserva wip.
  - [x] Python e PowerShell encaminham o mesmo contrato; launcher foi atualizado, mas a execução do teste Unix depende de `/bin/bash`, ausente neste host.
- **Verificação:**
  - [x] `python docs/vibe-interview/tests/test-interview.py -v`
  - [ ] `bash docs/vibe-interview/tests/test-interview.sh`, indisponível neste host
- **Deps:** T2
- **Arquivos:** `vibe-interview/scripts/interview.py`, `vibe-interview/scripts/interview.ps1`, `vibe-interview/scripts/interview.sh`, `docs/vibe-interview/tests/test-interview.py`, `docs/vibe-interview/tests/test-interview.sh`
- **Size:** high

### T4: Definir o contrato da spec no alvo MVP

- [x] T4 concluída
- **Spec:** A4, A9, A12, C5
- **O quê:** Atualizar prompt, template, arquitetura e análise da spec para consumir interview MVP, registrar decisões críticas e usar alvo explícito sem slug.
- **Aceite:**
  - [x] Spec MVP exige `mvp/interview.md` e grava na mesma pasta.
  - [x] Seções de decisão declaram `mantém`, `cria` ou `substitui` sem atualizar `REGRAS.md`.
  - [x] Spec phase mantém comportamento atual.
- **Verificação:**
  - [x] `git diff --check -- vibe-spec docs/vibe-spec`
- **Deps:** T1
- **Arquivos:** `vibe-spec/SKILL.md`, `vibe-spec/templates/spec.md`, `docs/vibe-spec/ARQUITETURA.md`, `docs/vibe-spec/ANALISE.md`
- **Size:** high

### T5: Implementar os motores MVP da spec

- [x] T5 concluída
- **Spec:** A4, A5, A11, C1, C2, C3
- **O quê:** Adicionar alvo `--mvp`/`-Mvp`, validação de predecessor, promoção verificada, relatório aditivo e testes de regressão na spec.
- **Aceite:**
  - [x] Apply MVP promove `spec-wip.md` para `.vibeflow/mvp/spec.md` sem criar phase.
  - [x] Ausência de interview ou presença de plan gera erro curto e preserva wip.
  - [x] Paridade essencial e contratos phase passam.
- **Verificação:**
  - [x] `python docs/vibe-spec/tests/test-spec.py -v`
  - [ ] `bash docs/vibe-spec/tests/test-spec.sh`, indisponível neste host
- **Deps:** T3, T4
- **Arquivos:** `vibe-spec/scripts/spec.py`, `vibe-spec/scripts/spec.ps1`, `vibe-spec/scripts/spec.sh`, `docs/vibe-spec/tests/test-spec.py`, `docs/vibe-spec/tests/test-spec.sh`
- **Size:** high

### T6: Definir o contrato do plan no alvo MVP

- [x] T6 concluída
- **Spec:** A4, A9, A12, C5
- **O quê:** Atualizar prompt, template e documentos do plan para fatiar a spec MVP na pasta especial e preservar referências de decisões críticas.
- **Aceite:**
  - [x] Plan MVP exige spec aprovada no alvo especial.
  - [x] Tasks apontam decisões críticas quando a fatia cria ou substitui uma delas.
  - [x] Plan phase permanece inalterado.
- **Verificação:**
  - [x] `git diff --check -- vibe-plan docs/vibe-plan`
- **Deps:** T1
- **Arquivos:** `vibe-plan/SKILL.md`, `vibe-plan/templates/plan.md`, `docs/vibe-plan/ARQUITETURA.md`, `docs/vibe-plan/ANALISE.md`
- **Size:** high

### T7: Implementar os motores MVP do plan

- [x] T7 concluída
- **Spec:** A4, A5, A11, C1, C2, C3
- **O quê:** Adicionar alvo explícito, validação da spec, promoção verificada, relatório aditivo e testes ao plan.
- **Aceite:**
  - [x] Apply MVP grava `.vibeflow/mvp/plan.md` e não usa `next_n`.
  - [x] Ausência de spec e tentativa de sobrescrever analyze são recusadas.
  - [x] Python e PowerShell passam com regressão phase; launcher atualizado aguarda host Unix.
- **Verificação:**
  - [x] `python docs/vibe-plan/tests/test-plan.py -v`
  - [ ] `bash docs/vibe-plan/tests/test-plan.sh`, indisponível neste host
- **Deps:** T5, T6
- **Arquivos:** `vibe-plan/scripts/plan.py`, `vibe-plan/scripts/plan.ps1`, `vibe-plan/scripts/plan.sh`, `docs/vibe-plan/tests/test-plan.py`, `docs/vibe-plan/tests/test-plan.sh`
- **Size:** high

### T8: Definir análise obrigatória e precedência explícita

- [x] T8 concluída
- **Spec:** A4, A9, A10, A12, C5
- **O quê:** Atualizar prompt, template, catálogo de cobertura e documentos do analyze para cruzar decisões MVP, detectar conflito implícito e bloquear implementação quando necessário.
- **Aceite:**
  - [x] Analyze MVP sempre lê interview, spec e plan do alvo especial.
  - [x] Divergência crítica sem `substitui` gera finding bloqueante.
  - [x] Analyze não atualiza decisões vigentes nem edita artefatos anteriores.
- **Verificação:**
  - [x] `git diff --check -- vibe-analyze docs/vibe-analyze`
- **Deps:** T1, T6
- **Arquivos:** `vibe-analyze/SKILL.md`, `vibe-analyze/templates/analyze.md`, `vibe-analyze/references/coverage.md`, `docs/vibe-analyze/ARQUITETURA.md`, `docs/vibe-analyze/ANALISE.md`
- **Size:** high

### T9: Implementar os motores MVP do analyze

- [x] T9 concluída
- **Spec:** A4, A5, A11, C1, C2, C3
- **O quê:** Adicionar alvo explícito, ordem obrigatória, promoção verificada, relatório aditivo e contratos de analyze MVP.
- **Aceite:**
  - [x] Apply MVP grava `.vibeflow/mvp/analyze.md` somente com interview, spec e plan presentes.
  - [x] Erros preservam wip e não criam phase.
  - [x] Paridade e regressão phase passam.
- **Verificação:**
  - [x] `python docs/vibe-analyze/tests/test-analyze.py -v`
  - [ ] `bash docs/vibe-analyze/tests/test-analyze.sh`, indisponível neste host
- **Deps:** T7, T8
- **Arquivos:** `vibe-analyze/scripts/analyze.py`, `vibe-analyze/scripts/analyze.ps1`, `vibe-analyze/scripts/analyze.sh`, `docs/vibe-analyze/tests/test-analyze.py`, `docs/vibe-analyze/tests/test-analyze.sh`
- **Size:** high

### T10: Definir implementação MVP com analyze obrigatório

- [x] T10 concluída
- **Spec:** A4, A8, A9, A12, C5
- **O quê:** Atualizar prompt, template e documentos da implement para selecionar fila do plan MVP, exigir analyze limpo e registrar prova das decisões críticas sem publicá-las ainda.
- **Aceite:**
  - [x] Implement MVP não executa sem analyze aprovado e limpo.
  - [x] Break-glass e outras decisões sensíveis mantêm critérios de segurança da spec.
  - [x] Implement phase continua com fila e modos atuais.
- **Verificação:**
  - [x] `git diff --check -- vibe-implement docs/vibe-implement`
- **Deps:** T1, T8
- **Arquivos:** `vibe-implement/SKILL.md`, `vibe-implement/templates/implement.md`, `docs/vibe-implement/ARQUITETURA.md`, `docs/vibe-implement/ANALISE.md`
- **Size:** high

### T11: Implementar os motores MVP da implement

- [x] T11 concluída
- **Spec:** A4, A5, A11, C1, C2, C3
- **O quê:** Adicionar alvo explícito, fila no diretório MVP, gate de analyze, promoção acumulativa de implement e testes.
- **Aceite:**
  - [x] Relatório `--mvp` calcula fila somente de `.vibeflow/mvp/plan.md`.
  - [x] Apply acumula fatias em `.vibeflow/mvp/implement.md` com cópia verificada.
  - [x] Analyze ausente, bloqueado ou rascunho impede execução e preserva wip.
- **Verificação:**
  - [x] `python docs/vibe-implement/tests/test-implement.py -v`
  - [ ] `bash docs/vibe-implement/tests/test-implement.sh`, indisponível neste host
- **Deps:** T9, T10
- **Arquivos:** `vibe-implement/scripts/implement.py`, `vibe-implement/scripts/implement.ps1`, `vibe-implement/scripts/implement.sh`, `docs/vibe-implement/tests/test-implement.py`, `docs/vibe-implement/tests/test-implement.sh`
- **Size:** high

### T12: Definir review MVP e sincronização de decisões

- [x] T12 concluída
- **Spec:** A4, A9, A10, A12, C5
- **O quê:** Atualizar prompt, template e documentos da review para julgar a cadeia MVP completa. Após aprovação humana, a IA aplica patch mínimo na tabela compacta; os motores não editam `REGRAS.md`.
- **Aceite:**
  - [x] Review rascunho ou request-changes nunca altera `REGRAS.md`.
  - [x] Aprovação humana autoriza a IA a atualizar por ID somente decisão e fonte vigentes, preservando outras regras.
  - [x] O contrato não cria flag de sincronização nem atribui mutação de regras ao script.
  - [x] Conflito não declarado bloqueia Approve.
- **Verificação:**
  - [x] `git diff --check -- vibe-review docs/vibe-review`
- **Deps:** T1, T10
- **Arquivos:** `vibe-review/SKILL.md`, `vibe-review/templates/review.md`, `docs/vibe-review/ARQUITETURA.md`, `docs/vibe-review/ANALISE.md`
- **Size:** high

### T13: Implementar os motores MVP da review

- [x] T13 concluída
- **Spec:** A4, A5, A11, C1, C2, C3
- **O quê:** Adicionar alvo explícito, validação da cadeia max, promoção da review e testes que provem que o motor nunca altera `REGRAS.md`.
- **Aceite:**
  - [x] Apply MVP grava `.vibeflow/mvp/review.md` sem criar phase.
  - [x] Promoção da review preserva `REGRAS.md` byte a byte em qualquer estado.
  - [x] Python e PowerShell mantêm paridade e o fluxo phase continua verde; launcher atualizado aguarda host Unix.
- **Verificação:**
  - [x] `python docs/vibe-review/tests/test-review.py -v`
  - [ ] `bash docs/vibe-review/tests/test-review.sh`, indisponível neste host
- **Deps:** T11, T12
- **Arquivos:** `vibe-review/scripts/review.py`, `vibe-review/scripts/review.ps1`, `vibe-review/scripts/review.sh`, `docs/vibe-review/tests/test-review.py`, `docs/vibe-review/tests/test-review.sh`
- **Size:** high

### T14: Provar a cadeia MVP completa e a regressão

- [x] T14 concluída
- **Spec:** A3, A4, A5, A10, A11, C1, C2, C3, C4, C6
- **O quê:** Criar teste integrado isolado para as seis portas, incluir no gate de CI e executar todas as suítes, launchers e verificações disponíveis.
- **Aceite:**
  - [x] Teste promove interview, spec, plan, analyze, implement e review no mesmo `.vibeflow/mvp/`.
  - [x] Nenhuma `phase-N` é criada durante o fluxo MVP.
  - [x] Fluxo phase existente, distribuição, diff check e gitleaks quando disponível permanecem verdes.
- **Verificação:**
  - [x] `python docs/tests/test-mvp-flow.py -v`
  - [x] `python docs/tests/test-distribuicao.py -v`
  - [ ] `gitleaks detect --source . --verbose --redact --no-banner` quando disponível
  - [x] `git diff --check`
- **Deps:** T3, T5, T7, T9, T11, T13
- **Arquivos:** `docs/tests/test-mvp-flow.py`, `.github/workflows/contrato.yml`
- **Size:** high

## Conferência

- [x] Spec aprovada como fonte; mesma pasta
- [x] Fatias verticais; size no máximo high
- [x] Toda T* tem aceite, verificação e referências à spec
- [x] UI greenfield, direção visual pertence ao catálogo do interview; código de UI não entra nesta entrega
- [x] Checkpoints a cada duas ou três T*
- [x] Aprovação humana (leu o arquivo e confirmou)

## Handoff

vibe-analyze
