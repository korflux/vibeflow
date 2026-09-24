# Plan: Implement enxuto
# Alvo: phase-13-vibe-implement-enxuto
# Status: aprovado
# Spec: spec.md (mesma pasta)

## Overview

Reduzir o custo de implementação com Express sem fase, registro único no plan, saída menor e retomada confiável, preservando provas e gates conforme o risco.
- **Design:** N/A, sem UI do produto.

## Preparo

- Python 3.13.14 e PowerShell 7.6.6 disponíveis. CI roda suítes de contrato, launchers em Linux e gitleaks. Bash não está disponível neste host. Sem navegador ou banco necessários.

## Tasks

### T1: Executar Express e ajustes na phase de origem

- [x] T1 concluída
- **Spec:** A1, A2, C1, C5
- **O quê:** inserir a classificação Express antes dos gates VibeFlow e orientar correções de validação humana na T*/R* da phase existente.
- **Aceite:**
  - [x] Pedido claro, localizado e sem comportamento novo funciona sem `.vibeflow/`, `vibe-init`, phase ou artefato novo.
  - [x] Correção da entrega atual atualiza a task existente ou cria T* curta no plan da mesma phase; finding formal atualiza R*.
  - [x] Mudança de comportamento ou risco de privacidade, jurídico, autenticação, dados ou pagamento encaminha ao fluxo aplicável.
- **Verificação:**
  - [x] `python docs/vibe-implement/tests/test-implement.py -v` -> 38 testes OK, incluindo paridade PowerShell.
  - [x] `python docs/tests/test-mvp-flow.py -v` -> 2 testes OK.
- **Deps:** nenhuma
- **Arquivos:** `vibe-implement/SKILL.md`, `docs/vibe-implement/tests/test-implement.py`, `.vibeflow/REGRAS.md`, artefatos da phase 13.
- **Decisões:** motores sem alteração; o Express é classificado antes de chamá-los.

### T2: Usar plan como registro e reduzir o inventário operacional

- [x] T2 concluída
- **Spec:** A3, A4, C2, C3, C4
- **O quê:** remover criação e dependência de `implement.md` nas novas execuções, mover prova e paths para o plan, fazer review consumir o plan e limitar stdout ao alvo, fila e avisos necessários.
- **Aceite:**
  - [x] Apply não cria `implement.md`; seleção da implementação não depende dele; arquivos históricos permanecem intactos.
  - [x] Review encontra no plan status, paths, prova e bloqueios sem exigir novo `implement.md`.
  - [x] Motores Python e PowerShell emitem os dados necessários sem serializar todas as phases.
- **Verificação:**
  - [x] `python docs/vibe-implement/tests/test-implement.py -v`
  - [x] `python docs/vibe-review/tests/test-review.py -v`
- **Prova:** `python docs/vibe-implement/tests/test-implement.py -v` -> 39 testes OK, incluindo paridade PowerShell; `python docs/vibe-review/tests/test-review.py -v` -> 24 testes OK, incluindo paridade PowerShell; `git diff --check` -> OK.
- **Deps:** T1
- **Arquivos:** `vibe-implement/SKILL.md`, `vibe-implement/scripts/implement.py`, `vibe-implement/scripts/implement.ps1`, remoção de `vibe-implement/templates/implement.md`, `vibe-review/SKILL.md`, `docs/vibe-implement/`, `docs/vibe-review/`, `README.md`
- **Decisões:** `plan.md` é o registro único da execução; stdout da phase contém alvo, fila e avisos, com `analyze_gate` adicional para MVP.

### T3: Fazer prova proporcional e permitir retomada curta

- [x] T3 concluída
- **Spec:** A5, A6, C5
- **O quê:** consolidar edições antes de uma prova final proporcional; registrar checkpoint mínimo no plan apenas para task incompleta e reaproveitar provas válidas após retomada.
- **Aceite:**
  - [x] Uma prova final cobre o estado integrado; só falha ou edição posterior de código/teste invalida a prova afetada.
  - [x] Smoke acompanha alteração real do ponto de entrada; UI limita a checagem à tela/estado/viewport afetados, ampliando quando necessário.
  - [x] Checkpoint opcional informa estado, próximo passo, paths e validade da prova; retomada confere o Git antes de continuar.
  - [x] Segurança, privacidade, jurídico, dados e gates MVP continuam cobertos conforme o diff.
- **Verificação:**
  - [x] `python docs/vibe-implement/tests/test-implement.py -v`
  - [x] `python docs/vibe-plan/tests/test-plan.py -v`
  - [x] `python docs/vibe-review/tests/test-review.py -v`
  - [x] `python docs/tests/test-distribuicao.py -v`
- **Prova:** implement -> 40 testes OK, incluindo paridade PowerShell; plan -> 21 testes OK; review -> 24 testes OK após ajuste da referência visual; distribuição -> 13 testes OK após ajustes dos contratos review; manifests em 2.2.0; `git diff --check` -> OK.
- **Deps:** T2
- **Arquivos:** `vibe-implement/SKILL.md`, `vibe-implement/references/`, `vibe-plan/SKILL.md`, `vibe-plan/templates/plan.md`, `vibe-review/SKILL.md`, `vibe-review/references/ui-visual-quality.md`, manifests versionáveis, `README.md`, `docs/ESCOPO.md`, `docs/tests/test-distribuicao.py`, `docs/vibe-implement/`, `docs/vibe-plan/`, `docs/vibe-review/`

## Handoff

vibe-implement

- Chat: recomende um chat novo para iniciar a implementação e um chat por T* em sequência. Se o humano preferir continuar aqui, não bloqueie. Sem grupo paralelo seguro porque as tasks editam arquivos compartilhados de skill, motores e contratos.
