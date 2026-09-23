# Plan: enxugar plan e implement com execução paralela
# Alvo: phase-11-fluxo-enxuto-plan-implement-paralelo
# Status: aprovado
# Spec: spec.md (mesma pasta)

## Overview

Atualizar o contrato de `plan`, `implement` e `review` para trabalhar por resultados verificáveis, com prova proporcional e delegação portátil. Preservar os gates de segurança, seleção de alvo e histórico vivo. Design: N/A, não há UI visível.

## Preparo

- [x] `gitleaks`, Python 3, PowerShell 7 e `rg` disponíveis; nenhuma T* de instalação.
- [x] Não há navegador/MCP visual exigido para esta fase documental e de scripts.
- [x] Baseline de plan, implement e analyze passou antes do código; não cria uma task própria.

## Paralelização

- T1, T2 e T3 podem avançar juntas somente com worktrees isolados ou ownership sem sobreposição; o coordenador integra mudanças e serializa atualizações dos artefatos vivos e do índice Git.

## Checkpoint de review

- Após T1–T3, conferir compatibilidade do formato de `plan.md`, fila da implement e recorte da review antes da mudança transversal dos relatórios. Achados bloqueantes voltam à T* responsável.

## Tasks

### T1: Publicar plan compacto por resultado

- [x] T1 concluída
- **Spec:** A1, A2, A3, C3
- **O quê:** Enxugar `vibe-plan/SKILL.md`, template e documentação. Substituir quebras automáticas por divisão baseada em resultado e dependência real; checklist de preparo sem T* artificial. Manter vínculo A*/C*, aceite, comando de prova e `Deps`, com indicação curta de paralelismo e checkpoint somente quando aplicável.
- **Aceite:**
  - [x] Plano exemplo cobre um resultado por T*, sem repetir ordem e dependências em seções diferentes; preparo local simples não vira task.
  - [x] O formato continua legível pelo parser da implement e registra N/A de design quando não há UI.
- **Verificação:**
  - [x] `python docs/vibe-plan/tests/test-plan.py -v`
  - [x] `python docs/vibe-implement/tests/test-implement.py -v`
  - [x] `python docs/vibe-analyze/tests/test-analyze.py -v`
- **Prova:** 21 plan, 34 implement e 18 analyze passaram; parser manteve T2/T3 elegíveis e T4 bloqueada por T2/T3.
- **Deps:** nenhuma
- **Arquivos:** `vibe-plan/SKILL.md`, `vibe-plan/templates/plan.md`, `docs/vibe-plan/`, `README.md`, `docs/ESCOPO.md`, `vibe-analyze/SKILL.md`, `vibe-analyze/references/coverage.md`, `vibe-analyze/templates/analyze.md`, `docs/vibe-analyze/tests/test-analyze.py`, `docs/vibe-implement/tests/test-implement.py`.
- **Risk:** `medium, formato consumido por implement e analyze`

### T2: Executar e integrar fatias com prova proporcional

- [x] T2 concluída
- **Spec:** A4, A5, A6, C1, C2, C3
- **O quê:** Atualizar `vibe-implement` para investigar o fluxo da T*, implementar e simplificar antes da prova final. Definir delegação por capacidade do host, isolamento de edição, entrega delimitada ao subagente e integração exclusiva pelo coordenador. Testar novamente só após edição posterior ou falha.
- **Aceite:**
  - [x] Fixture com duas T* independentes e uma dependente preserva a mesma fila e resultado em execução sequencial ou delegada.
  - [x] Contrato impede escrita concorrente nos artefatos vivos e no índice Git; commit da T* inclui apenas alterações integradas e provadas.
  - [x] Sem edição posterior à prova, a verificação roda uma vez; com edição posterior, roda novamente.
- **Verificação:**
  - [x] `python docs/vibe-implement/tests/test-implement.py -v`
  - [x] `python docs/tests/test-mvp-flow.py -v`
- **Prova:** `test-implement.py` -> 37 testes OK, incluindo fixture com conclusão delegada fora de ordem; `test-mvp-flow.py` -> 2 testes OK.
- **Deps:** nenhuma
- **Arquivos:** `vibe-implement/SKILL.md`, `vibe-implement/templates/implement.md`, `docs/vibe-implement/ANALISE.md`, `docs/vibe-implement/ARQUITETURA.md`, `docs/vibe-implement/tests/test-implement.py`.
- **Risk:** `medium, concorrência pode misturar prova ou commit`

### T3: Limitar review aos marcos e riscos relevantes

- [x] T3 concluída
- **Spec:** A3, A7, C3
- **O quê:** Definir review intermediária do diff de um marco justificado e review final da integração, sem repetir por padrão todas as verificações de cada T*. Preservar achados bloqueantes e o gate humano para o push final.
- **Aceite:**
  - [x] Checkpoint com T* ainda abertas não declara a feature concluída nem publica a fase.
  - [x] Review final julga aceite, código integrado e riscos alterados; executa a prova necessária sem matriz automática redundante.
- **Verificação:**
  - [x] `python docs/vibe-review/tests/test-review.py -v`
  - [x] `python docs/tests/test-mvp-flow.py -v`
  - [x] `python docs/tests/test-distribuicao.py -v` (contrato de distribuição afetado)
- **Prova:** `test-review.py` -> 21 testes OK; `test-mvp-flow.py` -> 2 testes OK; `test-distribuicao.py` -> 12 testes OK.
- **Deps:** nenhuma
- **Arquivos:** `vibe-review/SKILL.md`, `vibe-review/templates/review.md`, `docs/vibe-review/ARQUITETURA.md`, `docs/vibe-review/ANALISE.md`, `docs/vibe-review/tests/test-review.py`, `docs/tests/test-mvp-flow.py`, `docs/tests/test-distribuicao.py`.
- **Risk:** `medium, review parcial não pode disparar fechamento Git`

### T4: Reduzir relatórios operacionais e provar a cadeia

- [x] T4 concluída
- **Spec:** A8, C1, C3
- **O quê:** Inventariar consumidores dos `*-report.json` da cadeia e manter apenas dados operacionais necessários. Onde couber, entregar inventário e fila pela saída transitória dos motores sem gravar JSON no workspace; ajustar Python, PowerShell, skill e testes consumidores juntos. Preservar init ou outro relatório cuja persistência seja necessária, registrando o motivo. Consolidar o exemplo de três T* e a versão do contrato.
- **Aceite:**
  - [x] Nenhum relatório redundante permanece; o `init-report.json` mantido tem motivo documentado.
  - [x] Seleção de alvo, recusas, fila, preservação do vivo e paridade dos motores continuam provadas.
  - [x] Exemplo sequencial e paralelo isolado termina com mesma cobertura e commits atribuíveis; suítes da cadeia passam.
- **Verificação:**
  - [x] `python docs/vibe-plan/tests/test-plan.py -v`
  - [x] `python docs/vibe-implement/tests/test-implement.py -v`
  - [x] `python docs/vibe-review/tests/test-review.py -v`
  - [x] `python docs/tests/test-mvp-flow.py -v`
- **Prova:** plan 21, implement 37, review 21 e MVP-flow 2 testes passaram. Interview 22, spec 22, design 19, analyze 18, distribuição 13, reparse-safety 12 e init 32 também passaram. Os launchers Unix passaram com 6 casos de interview e 8 de implement. Somente `init-report.json` permaneceu em `.vibeflow/`; ele carrega o `apply_token` necessário para retomar um merge pendente.
- **Deps:** T1, T2, T3
- **Arquivos:** motores Python/PowerShell e skills de interview, spec, design, plan, analyze, implement e review; arquiteturas, testes, README, manifests, `.vibeflow/.gitignore`, template de design e artefatos desta phase; sem criar novo arquivo de estado.
- **Risk:** `medium, regressão de inventário, fila ou path público`

## Handoff

Fila concluída. Handoff para `vibe-review`; `plan.md` é a fonte da fila e o inventário de plan é JSON transitório no stdout.
