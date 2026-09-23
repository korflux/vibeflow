# Review: fluxo enxuto de plan e implement com execução paralela
# Alvo: phase-11-fluxo-enxuto-plan-implement-paralelo
# Status: request-changes

## Contexto

- Alvo: integração final da fase 11.
- Cadeia: interview N/A / spec.md / plan.md / implement.md / analyze.md N/A.
- O que muda: compactação do plan, delegação opcional com integração pelo coordenador, reviews por marco e inventários transitórios em stdout.

## Tipo de review

- Tipo: final
- Marco e justificativa: integração final, T1–T4 estão marcadas concluídas no plan.
- T* abertas fora do marco: nenhuma
- Provas reaproveitadas: nenhuma; reexecutei as suítes afetadas pela fase.
- Provas executadas:
  - python docs/vibe-plan/tests/test-plan.py -v → 21 testes OK.
  - python docs/vibe-implement/tests/test-implement.py -v → 37 testes OK, incluindo paridade PowerShell.
  - python docs/vibe-review/tests/test-review.py -v → 21 testes OK, incluindo paridade PowerShell.
  - python docs/vibe-analyze/tests/test-analyze.py -v → 18 testes OK.
  - python docs/vibe-interview/tests/test-interview.py -v → 22 testes OK.
  - python docs/vibe-spec/tests/test-spec.py -v → 22 testes OK.
  - python docs/vibe-design/tests/test-design.py -v → 19 testes OK.
  - python docs/vibe-init/tests/test-init.py -v → 32 testes OK.
  - python docs/tests/test-mvp-flow.py -v → 2 testes OK.
  - python docs/tests/test-distribuicao.py -v → 13 testes OK.
  - python docs/tests/test-reparse-safety.py -v → 12 testes OK, incluindo paridade PowerShell.
  - bash docs/vibe-interview/tests/test-interview.sh → 6/6.
  - bash docs/vibe-implement/tests/test-implement.sh → 8/8.
  - git diff 771532e..HEAD --check → OK.

## Cobertura

| Chave | Código | Notas |
|---|---|---|
| A1 | ok | vibe-plan/SKILL.md, template e contrato de teste cobrem tasks por resultado e formato compatível com a fila. |
| A2 | ok | Checklist de preparo sem task artificial, coberta pelo plan e pelos testes. |
| A3 | ok | Paralelismo e checkpoint são condicionais e têm critérios registrados no plan. |
| A4 | ok | vibe-implement/SKILL.md define simplificação antes da prova e reexecução após falha ou edição posterior. |
| A5 | ok | A skill define delegação opcional, entregas delimitadas, fallback sequencial e integração pelo coordenador. |
| A6 | ok | A regra de ownership está documentada e a fixture agora confere commits Git path-scoped por task nas duas ordens. |
| A7 | partial | A avaliação retrospectiva encontrou compatibilidade entre os contratos T1–T3 e T4, mas ocorreu após T4 e não satisfaz o checkpoint na ordem planejada. Aguarda a decisão documentada em R1. |
| A8 | ok | Motores e testes confirmam inventário em stdout sem relatórios redundantes; init-report.json permanece pelo motivo documentado. |
| C1 | ok | A fixture compara o estado final e os paths/mensagens lidos de commits Git reais nas duas ordens. |
| C2 | ok | O ciclo exige uma prova final por estado e reexecução após mudança ou falha. |
| C3 | ok | A fixture atualiza o plan sequencialmente, cria commits reais somente com o plan e o path exclusivo da task, e verifica árvore limpa. |

## Checklist de correções

### Required

- [ ] R1: **Required** - .vibeflow/phases/phase-11-fluxo-enxuto-plan-implement-paralelo/implement.md - O checkpoint exigido entre T1–T3 e T4 não ocorreu naquele ponto. A avaliação retrospectiva está registrada abaixo e encontrou contratos compatíveis; ela foi feita depois de T4 e não recupera a ordem planejada. - remédio: decidir explicitamente se aceita a exceção de sequência; recomendação: aceitar o desvio documentado, pois o snapshot e o diff não mostraram incompatibilidade no formato do plan, na fila ou nos gates da review. - prova: snapshot `b32d2e3` após T1–T3, plan 21, implement 37, review 21 e MVP flow 2 testes OK; diff `b32d2e3..96dcb52` confirma que T4 alterou a emissão do inventário sem alterar a fila nem os gates de checkpoint. - source: A7 / plan.md - gap: decisão humana pendente
- [x] R2: **Required** - docs/vibe-implement/tests/test-implement.py:368 - A fixture agora cria um repositório Git temporário por ordem, grava arquivos reais por task, atualiza o plan pelo coordenador, cria commits path-scoped e lê paths/mensagens de git show. Compara o estado final das execuções sequencial e delegada e exige árvore limpa. - remédio: aplicado em vibe-implement. - prova: python docs/vibe-implement/tests/test-implement.py -v → 37 testes OK; a fixture falha se path ou mensagem de commit divergirem. - source: C1 / C3 / plan.md - gap: none

## Veredito vigente

- [ ] **Approve**: nenhum Critical/Required em [ ]
- [x] **Request changes**: há Required em [ ]
- [ ] **Approve com defer**: indisponível enquanto R1 Required estiver aberto.

## Handoff

R2 corrigido. Falta a decisão humana sobre o desvio documentado em R1; depois, executar nova vibe-review.

## Avaliação retrospectiva de R1

- Marco planejado: após T1–T3 e antes de T4, verificar compatibilidade do formato de `plan.md`, da fila da implement e do recorte da review.
- Estado avaliado: snapshot `b32d2e3`, com T1–T3 concluídas e T4 ainda ausente; comparação posterior com T4 no intervalo `b32d2e3..96dcb52`.
- Resultado: não foi encontrada incompatibilidade nesses contratos. No diff de T4, os motores `plan`, `implement` e `review` passaram a emitir o inventário em stdout; a projeção da fila e os gates de checkpoint/final permaneceram preservados.
- Provas no snapshot T1–T3: plan 21, implement 37, review 21 e MVP flow 2 testes OK. A fixture de commits daquela versão era sintética e não foi usada como evidência de atribuição Git; R2 foi fechado separadamente com Git real.
- Limitação temporal: esta auditoria ocorreu após T4. Ela avalia os artefatos e a compatibilidade do marco, mas não substitui o checkpoint exigido antes de T4.
- Decisão humana: pendente. Recomendação: aceitar a exceção documentada; responda “aceito” ou “não aceito”.

## Etapas

### Etapa 1 - final - integração T1–T4

- Tipo: final
- Marco e justificativa: integração final; todas as T* do plan estão concluídas.
- T* abertas fora do marco: nenhuma
- Provas reaproveitadas: nenhuma.
- Provas executadas: matriz das suítes de contrato e launchers listada acima; executada porque a fase altera contratos e motores de sete skills. git diff --check passou.
- Leu: plan.md, spec.md e implement.md.
- Abriu: R1, R2
- Fechou: nenhum
- Veredito desta etapa: Request changes
