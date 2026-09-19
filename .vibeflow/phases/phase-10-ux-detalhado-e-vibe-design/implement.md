# Implement: UX detalhado e vibe-design, baseline T1
# Alvo: phase-10-ux-detalhado-e-vibe-design
# Status: aprovado

<!-- Escreva diretamente neste artefato vivo; feche o status somente após a prova da fatia. -->

## Fatia T1

- Feito: baseline verde fixado sem edição em código. `rg` indisponível no host Windows, seleção feita por `glob` de `docs/**/test-*.py` e leitura direta dos vivos da phase. Nenhum source, template ou teste foi alterado.
- Marcado: T1 em `plan.md` com aceite e verificação em `[x]`, mais `Prova` e `Arquivos` sob a seção. `spec.md` não marcado, C1 segue como baseline pendente de fechamento na review.
- Prova: `python "docs/vibe-interview/tests/test-interview.py" -v` -> 19 testes OK
- Prova: `python "docs/vibe-spec/tests/test-spec.py" -v` -> 19 testes OK
- Prova: `python "docs/tests/test-distribuicao.py" -v` -> 12 testes OK
- Prova: `gitleaks detect --source . --verbose --redact --no-banner` -> 12 commits, no leaks found
- Commit da task: pendente até o commit isolado, mensagem e hash serão registrados no resultado e no chat sem reabrir este artefato
- Decisões críticas: N/A, baseline sem decisão de produto

### Feedback +

- As três suítes Python e o gitleaks passaram de primeira, sem necessidade de diagnóstico de causa raiz.

### Feedback -

- `rg --files` e `rg -n` indisponíveis no shell do host. Uso de `glob` como mapa de seleção, sem varredura cega da árvore.
- `plan.md` estava com `# Status: rascunho`. Flip para `aprovado` em 1 linha, pois o humano pediu esta skill e não há veredito de bloqueio.

### Para a review

- T1 não prova comportamento novo, só fixa o verde. C1 final depende das tasks T2 a T6 permanecerem verdes.

## Fatia T2

- Feito: tabela de jornadas com 8 colunas e checklist de acesso com 8 itens tornados obrigatórios no template da interview, com N/A explícito e invariante de defeito. Ajuste mínimo em SKILL e arquitetura, mais 3 casos novos de template sem quebrar os 19 existentes. Reutilizados estrutura atual do template e catálogo de descoberta como referência interna, sem despejar catálogo no chat e sem dependência nova.
- Marcado: T2 em `plan.md` com aceite e verificação em `[x]`, mais `Prova` e `Decisões` sob a seção. `spec.md` não marcado, A2 e C1 seguem pendentes de fechamento na review.
- Prova: `python "docs/vibe-interview/tests/test-interview.py" -v` -> 22 testes OK (19 anteriores + 3 novos de template)
- Prova: `bash "docs/vibe-interview/tests/test-interview.sh"` -> pass=6 fail=0
- Arquivos: `vibe-interview/templates/interview.md`, `vibe-interview/SKILL.md`, `docs/vibe-interview/ARQUITETURA.md`, `docs/vibe-interview/tests/test-interview.py`
- Commit da task: pendente até o commit isolado, mensagem e hash serão registrados no resultado e no chat sem reabrir este artefato
- Decisões críticas: N/A, ajuste de template sem decisão de produto

### Feedback +

- Suíte Python passou com 22 testes e launcher sh com 6 passos, sem diagnóstico de causa raiz.

### Feedback -

- `rg --files` e `rg -n` indisponíveis no host Windows. Seleção por leitura direta dos 4 paths da T2 e das suítes, sem varredura cega.

### Para a review

- T2 prova contrato de template, não comportamento de motor. A2 e C1 finais dependem de T3 a T6 permanecerem verdes.

## Fatia T3

- Feito: área genérica trocada por molde F* com Jornada, Rota, Gatilho, Pré-condição, Superfície por passo, Passos com ação e resposta, Validações, Erros com código e mensagem segura, Estados e Aceite A*, com invariante de passo sem superfície como defeito. Handoff condicional para vibe-design com UI visível e vibe-plan sem UI, com token visual como dono da design e bloqueio de nova escrita com plan existente. Reutilizados estrutura atual do template, catálogo de erros SPEC_JA_PLANEJADA e padrão TemplateContracts da T2, sem motor novo e sem dependência nova.
- Marcado: T3 em `plan.md` com aceite e verificação em `[x]`, mais `Prova` sob a seção. `spec.md` não marcado, A1, A2 e C1 seguem pendentes de fechamento na review.
- Prova: `python "docs/vibe-spec/tests/test-spec.py" -v` -> 22 testes OK (19 anteriores + 3 novos de template)
- Prova: `bash "docs/vibe-spec/tests/test-spec.sh"` -> pass=6 fail=0
- Arquivos: `vibe-spec/templates/spec.md`, `vibe-spec/SKILL.md`, `vibe-spec/references/ui-visual-direction.md`, `docs/vibe-spec/ARQUITETURA.md`, `docs/vibe-spec/tests/test-spec.py`
- Commit da task: pendente até o commit isolado, mensagem e hash serão registrados no resultado e no chat sem reabrir este artefato
- Decisões críticas: omitir quando N/A

### Feedback +

- Suíte Python passou com 22 testes e launcher sh com 6 passos, sem diagnóstico de causa raiz. Motor já bloqueava SPEC_JA_PLANEJADA, sem correção de causa raiz necessária.

### Feedback -

- `rg --files` e `rg -n` indisponíveis no host Windows. Seleção por `glob` dos 5 paths da T3 e leitura direta das suítes, sem varredura cega.

### Para a review

- T3 prova contrato de template, não comportamento de motor. A1, A2 e C1 finais dependem de T4 a T6 permanecerem verdes.

## Handoff

próxima T*

- Chat: recomende um novo chat focado na próxima T* elegível (T4). O `plan.md` e este `implement.md` vivos são a ponte. O commit da task já foi criado, sem push aqui.

<!-- fatia seguinte: copie o bloco ## Fatia abaixo, não apague as anteriores -->
