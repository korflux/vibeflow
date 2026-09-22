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

- [ ] T2 concluída
- **Spec:** A4, A5, A6, C1, C2, C3
- **O quê:** Atualizar `vibe-implement` para investigar o fluxo da T*, implementar e simplificar antes da prova final. Definir delegação por capacidade do host, isolamento de edição, entrega delimitada ao subagente e integração exclusiva pelo coordenador. Testar novamente só após edição posterior ou falha.
- **Aceite:**
  - [ ] Fixture com duas T* independentes e uma dependente preserva a mesma fila e resultado em execução sequencial ou delegada.
  - [ ] Contrato impede escrita concorrente nos artefatos vivos e no índice Git; commit da T* inclui apenas alterações integradas e provadas.
  - [ ] Sem edição posterior à prova, a verificação roda uma vez; com edição posterior, roda novamente.
- **Verificação:**
  - [ ] `python docs/vibe-implement/tests/test-implement.py -v`
  - [ ] `python docs/tests/test-mvp-flow.py -v`
- **Deps:** nenhuma
- **Arquivos:** `vibe-implement/SKILL.md`, `vibe-implement/templates/implement.md`, `docs/vibe-implement/`, testes de contrato afetados.
- **Risk:** `medium, concorrência pode misturar prova ou commit`

### T3: Limitar review aos marcos e riscos relevantes

- [ ] T3 concluída
- **Spec:** A3, A7, C3
- **O quê:** Definir review intermediária do diff de um marco justificado e review final da integração, sem repetir por padrão todas as verificações de cada T*. Preservar achados bloqueantes e o gate humano para o push final.
- **Aceite:**
  - [ ] Checkpoint com T* ainda abertas não declara a feature concluída nem publica a fase.
  - [ ] Review final julga aceite, código integrado e riscos alterados; executa a prova necessária sem matriz automática redundante.
- **Verificação:**
  - [ ] `python docs/vibe-review/tests/test-review.py -v`
  - [ ] `python docs/tests/test-mvp-flow.py -v`
- **Deps:** nenhuma
- **Arquivos:** `vibe-review/SKILL.md`, `vibe-review/templates/review.md`, `docs/vibe-review/`, testes de contrato afetados.
- **Risk:** `medium, review parcial não pode disparar fechamento Git`

### T4: Reduzir relatórios operacionais e provar a cadeia

- [ ] T4 concluída
- **Spec:** A8, C1, C3
- **O quê:** Inventariar consumidores dos `*-report.json` da cadeia e manter apenas dados operacionais necessários. Onde couber, entregar inventário e fila pela saída transitória dos motores sem gravar JSON no workspace; ajustar Python, PowerShell, skill e testes consumidores juntos. Preservar init ou outro relatório cuja persistência seja necessária, registrando o motivo. Consolidar o exemplo de três T* e a versão do contrato.
- **Aceite:**
  - [ ] Nenhum relatório redundante permanece; os mantidos têm motivo documentado.
  - [ ] Seleção de alvo, recusas, fila, preservação do vivo e paridade dos motores continuam provadas.
  - [ ] Exemplo sequencial e paralelo isolado termina com mesma cobertura e commits atribuíveis; suítes da cadeia passam.
- **Verificação:**
  - [ ] `python docs/vibe-plan/tests/test-plan.py -v`
  - [ ] `python docs/vibe-implement/tests/test-implement.py -v`
  - [ ] `python docs/vibe-review/tests/test-review.py -v`
  - [ ] `python docs/tests/test-mvp-flow.py -v`
- **Deps:** T1, T2, T3
- **Arquivos:** motores e testes dos relatórios efetivamente removidos, documentação e consumidores da cadeia; sem criar novo arquivo de estado.
- **Risk:** `medium, regressão de inventário, fila ou path público`

## Handoff

`vibe-implement` após aprovação. `plan.md` é a fila; `plan-report.json` permanece fora do Git.
