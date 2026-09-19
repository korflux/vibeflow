# Plan: UX detalhado e vibe-design
# Alvo: phase-10-ux-detalhado-e-vibe-design
# Status: aprovado
# Spec: spec.md (mesma pasta)

<!-- Escreva diretamente neste artefato vivo; o status permanece rascunho durante a elaboração. -->

## Overview

Entrega o pacote completo da spec com UX genérica nos templates, cadeia com design condicional e skill nova vibe-design com motores e testes, em fatias verticais que mantêm as suítes verdes a cada commit.

## Ordem

### Fase 1: Baseline

- T1 (corpo em Tasks; cada task tem sua própria verificação e commit)

### Fase 2: Templates de UX

- T2, T3 em paralelo após T1

### Fase 3: Cadeia transversal

- T4 após T2 e T3

### Fase 4: Pacote vibe-design

- T5 após T4, T6 após T4 e T5

## Riscos

| Risco | Impacto | Mitigação |
|---|---|---|
| Teste de distribuição quebrado no meio da fase | médio | Atualizar teste de 7 para 8 skills junto do pacote em T6, nunca antes |
| Paridade PowerShell do motor novo | médio | Espelhar spec.py e provar com suíte do motor quando pwsh existir, skip sem pwsh |
| Escopo puxando Figma automático | baixo | Manter Figma como leitura e recusar sync automático na review da fase |

## Paralelização

- Paralelo ok: T2 e T3 após T1
- Sequencial: T1 primeiro, T4 após T2 e T3, T5 após T4, T6 após T4 e T5
- Contrato primeiro, depois paralelo: T4 fecha cadeia antes do pacote, T5 fecha motor antes da SKILL

## Tasks

### T1: Baseline verde do contrato

- [x] T1 concluída
- **Spec:** C1
- **Decisões:** N/A, baseline sem decisão de produto
- **O quê:** Executa as suítes existentes de interview, spec e distribuição mais gitleaks para fixar o verde antes de qualquer edição.
- **Aceite:**
  - [x] Suítes de interview e spec passam sem alteração no disco
  - [x] Distribuição passa e gitleaks não acusa segredo
- **Verificação:**
  - [x] `python "docs/vibe-interview/tests/test-interview.py" -v`
  - [x] `python "docs/vibe-spec/tests/test-spec.py" -v`
  - [x] `python "docs/tests/test-distribuicao.py" -v`
  - [x] `gitleaks detect --source . --verbose --redact --no-banner`
- **Deps:** nenhuma
- **Prova:** `python "docs/vibe-interview/tests/test-interview.py" -v` -> 19 testes OK; `python "docs/vibe-spec/tests/test-spec.py" -v` -> 19 testes OK; `python "docs/tests/test-distribuicao.py" -v` -> 12 testes OK; `gitleaks detect --source . --verbose --redact --no-banner` -> 12 commits, no leaks found
- **Arquivos:** `.vibeflow/phases/phase-10-ux-detalhado-e-vibe-design/plan.md`, `.vibeflow/phases/phase-10-ux-detalhado-e-vibe-design/implement.md` (sem edição em código)
- **Size:** `low, 1/10, execução de suítes existentes sem edição`
- **Risk:** `low`

### T2: Jornadas genéricas na interview

- [x] T2 concluída
- **Spec:** A2, C1
- **Decisões:** N/A, ajuste de template sem decisão de produto
- **O quê:** Torna a tabela de jornadas e o checklist de acesso obrigatórios no template da interview, com N/A explícito, e ajusta arquitetura e testes da skill.
- **Aceite:**
  - [x] Template exige Jornada, Ator, Gatilho, Objetivo, Telas, Entrada, Saída e Estado crítico
  - [x] Checklist de acesso cobre login, cadastro, recuperação, sessão, papéis, primeiro usuário, bloqueio e logout
  - [x] Casos novos de template passam e antigos continuam verdes
- **Verificação:**
  - [x] `python "docs/vibe-interview/tests/test-interview.py" -v`
  - [x] `bash "docs/vibe-interview/tests/test-interview.sh"`
- **Deps:** T1
- **Prova:** `python "docs/vibe-interview/tests/test-interview.py" -v` -> 22 testes OK (19 anteriores + 3 novos de template); `bash "docs/vibe-interview/tests/test-interview.sh"` -> pass=6 fail=0
- **Arquivos:** `vibe-interview/templates/interview.md`, `vibe-interview/SKILL.md`, `docs/vibe-interview/ARQUITETURA.md`, `docs/vibe-interview/tests/test-interview.py`
- **Size:** `low, 3/10, vários arquivos do mesmo módulo com contrato interno e verificação por suíte`
- **Risk:** `low`

### T3: Molde F* na spec com handoff condicional

- [x] T3 concluída
- **Spec:** A1, A2, C1
- **Decisões:** omitir quando N/A
- **O quê:** Troca área genérica por fluxo F* com superfície por passo e handoff condicional para design ou plan, e ajusta SKILL, referência e testes.
- **Aceite:**
  - [x] Cada F* tem Jornada, Rota, Gatilho, Pré-condição, Superfície por passo, Passos, Validações, Erros, Estados e Aceite
  - [x] Passo sem superfície é defeito e plan existente bloqueia nova escrita
  - [x] Handoff aponta vibe-design com UI visível e vibe-plan sem UI
- **Verificação:**
  - [x] `python "docs/vibe-spec/tests/test-spec.py" -v`
  - [x] `bash "docs/vibe-spec/tests/test-spec.sh"`
- **Deps:** T1
- **Prova:** `python "docs/vibe-spec/tests/test-spec.py" -v` -> 22 testes OK (19 anteriores + 3 novos de template); `bash "docs/vibe-spec/tests/test-spec.sh"` -> pass=6 fail=0
- **Arquivos:** `vibe-spec/templates/spec.md`, `vibe-spec/SKILL.md`, `vibe-spec/references/ui-visual-direction.md`, `docs/vibe-spec/ARQUITETURA.md`, `docs/vibe-spec/tests/test-spec.py`
- **Size:** `medium, 4/10, template mais SKILL e referência com investigação pequena de handoff`
- **Risk:** `low`

### T4: Contrato transversal com design condicional

- [ ] T4 concluída
- **Spec:** A4, C1
- **Decisões:** omitir quando N/A
- **O quê:** Atualiza cadeia, handoffs e conferências para design entre spec e plan somente com UI visível, sem tocar na contagem de skills da distribuição.
- **Aceite:**
  - [ ] Cadeia registra design condicional e N/A explícito sem tela
  - [ ] Plan exige design.md aprovado com UI visível e analyze cruza design no max
  - [ ] Fluxo MVP e contrato visual continuam verdes
- **Verificação:**
  - [ ] `python "docs/tests/test-mvp-flow.py" -v`
  - [ ] `python "docs/tests/test-visual-contract.py" -v`
- **Deps:** T2, T3
- **Arquivos:** `.vibeflow/REGRAS.md`, `vibe-plan/SKILL.md`, `vibe-analyze/SKILL.md`, `docs/ESCOPO.md`
- **Size:** `medium, 6/10, vários subsistemas com contrato compartilhado e verificação por integração`
- **Risk:** `medium, contrato compartilhado com regressão relevante em cadeia`

### T5: Motor executável da vibe-design

- [ ] T5 concluída
- **Spec:** A3, C1
- **Decisões:** omitir quando N/A
- **O quê:** Cria os três motores com inventário, resolução de alvo, relatório gitignored e preservação do vivo, mais a suíte de contrato da skill.
- **Aceite:**
  - [ ] Flags públicas iguais nos dois motores com launcher sem versão degradada
  - [ ] Apply prepara design.md só quando ausente e preserva bytes existentes
  - [ ] Suíte nova passa incluindo preservação e paridade quando pwsh existir
- **Verificação:**
  - [ ] `python "docs/vibe-design/tests/test-design.py" -v`
  - [ ] `bash "docs/vibe-design/tests/test-design.sh"`
  - [ ] `python "docs/tests/test-reparse-safety.py" -v`
- **Deps:** T4
- **Arquivos:** `vibe-design/scripts/design.py`, `vibe-design/scripts/design.ps1`, `vibe-design/scripts/design.sh`, `docs/vibe-design/tests/test-design.py`, `docs/vibe-design/tests/test-design.sh`
- **Size:** `medium, 4/10, módulo novo com contrato interno e investigação pequena de alvo`
- **Risk:** `medium, escrita em disco com proteções que exige prova de preservação`

### T6: Pacote operacional da vibe-design

- [ ] T6 concluída
- **Spec:** A3, A4, C1, C2
- **Decisões:** omitir quando N/A
- **O quê:** Publica SKILL, template de design.md, references, arquitetura, análise e distribuição em 8 skills com o mesmo install das demais.
- **Aceite:**
  - [ ] SKILL descreve dois modos de entrada, três usos e handoff para plan sem editar código
  - [ ] Template de design.md traz telas, disposição técnica, tokens, iconografia, responsivo, estados e prova visual
  - [ ] Distribuição reconhece 8 skills com ponteiros, manifests e README atualizados
- **Verificação:**
  - [ ] `python "docs/tests/test-distribuicao.py" -v`
  - [ ] `python "docs/tests/test-visual-contract.py" -v`
- **Deps:** T4, T5
- **Arquivos:** `vibe-design/SKILL.md`, `vibe-design/templates/design.md`, `vibe-design/references/`, `docs/vibe-design/ARQUITETURA.md`, `docs/vibe-design/ANALISE.md`, `skills/vibe-design`, `.claude-plugin/`, `.codex-plugin/`, `.agents/plugins/`, `.grok-plugin/`, `plugin.json`, `README.md`
- **Size:** `medium, 5/10, pacote novo com contrato compartilhado e dependência de motor pronto`
- **Risk:** `medium, superfície instalável com regressão relevante em distribuição`

## Conferência

- [x] Spec aprovada como fonte; mesma pasta
- [x] Fatias verticais; score de Size ≤ 8; Risk separado
- [x] Toda T* tem aceite + verificação + Spec: A*/C* quando couber
- [x] Ferramentas essenciais (gitleaks, chrome-devtools) validadas ou com task de setup
- [x] T1 estabelece ponto de entrada real (smoke test / walking skeleton)
- [x] UI greenfield/sem DS → T* de kit antes das telas (ou N/A)
- [x] Cada T* possui unidade de execução, verificação e commit própria
- [ ] Aprovação humana (leu o arquivo e confirmou)

## Handoff

vibe-implement

- Chat: recomende novo chat para `vibe-implement`; continuidade no mesmo chat só por escolha consciente. O `plan.md` vivo é a ponte.
