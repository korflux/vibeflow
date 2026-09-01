# Plan: Size por complexidade e risco separado
# Alvo: phase-7-size-complexity
# Status: aprovado
# Spec: spec.md (mesma pasta)

## Overview

Atualizar o contrato do `vibe-plan` para classificar cada T* por score de complexidade observável, separar `Risk` do tamanho e alinhar template, documentação e testes, sem alterar o parser mecânico nem os plans existentes.

## Ordem

### Fase 1: Contrato operacional

- T1 (contrato canônico e template)

### Fase 2: Documentação e prova

- T2-T3 (documentação secundária e testes semânticos)

### Checkpoint: após T1-T2

- [x] `python docs/vibe-plan/tests/test-plan.py -v`
- [x] Busca confirma que a regra antiga de arquivos não permanece na documentação operacional.

### Checkpoint: após T3

- [x] `python docs/vibe-plan/tests/test-plan.py -v`
- [x] `python docs/tests/test-distribuicao.py -v` em checkout com symlinks habilitados.

## Riscos

| Risco | Impacto | Mitigação |
|---|---|---|
| Regra duplicada divergir entre skill, arquitetura, template e README | alto | Manter a matriz canônica na skill e testar os termos essenciais em conjunto. |
| Score virar falsa precisão ou estimativa de duração | médio | Declarar que é classificação ordinal, exigir justificativa curta e excluir tempo do cálculo. |
| Suíte de distribuição falhar no checkout por `core.symlinks=false` | médio | Habilitar `core.symlinks` no checkout e validar os ponteiros reais antes de fechar a entrega. |

## Paralelização

- Paralelo ok: T2 e T3 podem ser preparados depois que T1 fechar os nomes e intervalos, mas T3 deve testar a redação final.
- Sequencial: T1 antes de T2 e T3; T2 antes do checkpoint final.
- Contrato primeiro, depois paralelo: skill e template definem a nomenclatura que a documentação e os testes reutilizam.

## Tasks

### T1: Definir score de Size e Risk no contrato operacional

- [x] T1 concluída
- **Spec:** A1, A2, A5
- **O quê:** Substituir a tabela baseada em quantidade de arquivos por cinco dimensões pontuadas de 0 a 2, intervalos de classificação e gate de quebra. Atualizar o template para registrar score, justificativa curta e `Risk` separado.
- **Aceite:**
  - [x] `vibe-plan/SKILL.md` define superfície, acoplamento, verificação, incerteza e coordenação com níveis 0, 1 e 2.
  - [x] `vibe-plan/SKILL.md` define `0–3 = low`, `4–6 = medium`, `7–8 = high` e score `9–10` como quebra obrigatória.
  - [x] O template não permite `xhigh` ou `max` como `Size` final e contém campo separado para `Risk`.
- **Verificação:**
  - [x] `python docs/vibe-plan/tests/test-plan.py -v`
- **Deps:** nenhuma
- **Arquivos:** `vibe-plan/SKILL.md`, `vibe-plan/templates/plan.md`
- **Size:** low, 3/10 (superfície 1, acoplamento 1, verificação 1, incerteza 0, coordenação 0)
- **Risk:** medium, altera o contrato operacional usado por agentes.

### T2: Alinhar documentação de arquitetura e uso

- [x] T2 concluída
- **Spec:** A3
- **O quê:** Atualizar a arquitetura e a análise do `vibe-plan`, o README e o escopo para distinguir `Size`, `Risk` e esforço da rota, mantendo arquivos como evidência de superfície e sem introduzir duração estimada.
- **Aceite:**
  - [x] Os documentos repetem os mesmos intervalos, limite de quebra e distinção entre os três conceitos.
  - [x] Nenhum documento de uso define `Size` diretamente por `5+ arquivos` ou `alto risco`.
  - [x] O README explica que uma rota `high` pode conter tasks `low` ou `medium`.
- **Verificação:**
  - [x] `python docs/vibe-plan/tests/test-plan.py -v`
  - [x] `rg -n "Size|Risk|superfície|acoplamento|verificação|incerteza|coordenação|tempo|rota" vibe-plan docs/vibe-plan README.md docs/ESCOPO.md`
- **Deps:** T1
- **Arquivos:** `docs/vibe-plan/ARQUITETURA.md`, `docs/vibe-plan/ANALISE.md`, `README.md`, `docs/ESCOPO.md`
- **Size:** medium, 4/10 (superfície 2, acoplamento 1, verificação 1, incerteza 0, coordenação 0)
- **Risk:** low, somente documentação derivada do contrato canônico.

### T3: Provar a regra semântica e preservar os contratos mecânicos

- [x] T3 concluída
- **Spec:** A4, A5
- **O quê:** Adicionar testes textuais que detectem as cinco dimensões, os intervalos, o limite de quebra, o campo `Risk` e a remoção da regra antiga. Rerodar a suíte existente do motor, o launcher e a distribuição sem alterar seus contratos.
- **Aceite:**
  - [x] Os testes falham se a tabela antiga baseada em arquivos voltar para a skill ou se os campos novos desaparecerem do template.
  - [x] Os testes existentes de inventário, apply, paridade PowerShell e launcher continuam passando.
  - [x] A suíte de distribuição passa no checkout principal com symlinks habilitados.
- **Verificação:**
  - [x] `python docs/vibe-plan/tests/test-plan.py -v`
  - [x] `C:\Program Files\Git\bin\bash.exe docs/vibe-plan/tests/test-plan.sh`
  - [x] `python docs/tests/test-distribuicao.py -v` no checkout principal com symlinks reais.
- **Deps:** T1, T2
- **Arquivos:** `docs/vibe-plan/tests/test-plan.py`
- **Size:** low, 2/10 (superfície 0, acoplamento 1, verificação 1, incerteza 0, coordenação 0)
- **Risk:** low, amplia somente a cobertura do contrato documental.

### Checkpoint: após T3

- [x] `python docs/vibe-plan/tests/test-plan.py -v`
- [x] `C:\Program Files\Git\bin\bash.exe docs/vibe-plan/tests/test-plan.sh`
- [x] `python docs/tests/test-distribuicao.py -v` em checkout com symlinks habilitados.

## Conferência

- [x] Spec aprovada como fonte; mesma pasta
  - [x] Fatias verticais; score de Size ≤ 8
- [x] Toda T* tem aceite + verificação + Spec: A*/C* quando couber
- [x] Ferramentas essenciais (gitleaks, chrome-devtools) validadas ou com task de setup
- [x] T1 estabelece ponto de entrada real (suíte de contrato do plan)
- [x] UI greenfield/sem DS → T* de kit antes das telas (N/A)
- [x] Checkpoints a cada 2–3 T*
- [x] Aprovação humana (leu o arquivo e confirmou)

## Handoff

vibe-implement
