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

## Fatia T4

- Feito: cadeia com design entre spec e plan somente com UI visível e N/A explícito sem tela, com handoff da spec para vibe-design e da design para vibe-plan. Plan exige design.md aprovado com UI visível, analyze no max cruza design, e ESCOPO registra vibe-design pendente sem mudar a contagem da distribuição. Reutilizados bloco cadeia existente, gate de plan e varredura de analyze, sem motor novo e sem dependência nova.
- Marcado: T4 em `plan.md` com aceite e verificação em `[x]`, mais `Prova` sob a seção. `spec.md` não marcado, A4 e C1 seguem pendentes de fechamento na review.
- Prova: `python "docs/tests/test-mvp-flow.py" -v` -> 2 testes OK
- Prova: `python "docs/tests/test-visual-contract.py" -v` -> 4 testes OK
- Prova extra: `python "docs/tests/test-distribuicao.py" -v` -> 12 testes OK, contagem em 7 skills preservada
- Arquivos: `.vibeflow/REGRAS.md`, `vibe-plan/SKILL.md`, `vibe-analyze/SKILL.md`, `docs/ESCOPO.md`
- Commit da task: pendente até o commit isolado, mensagem e hash serão registrados no resultado e no chat sem reabrir este artefato
- Decisões críticas: omitir quando N/A

### Feedback +

- Suítes de fluxo MVP e contrato visual passaram de primeira, sem diagnóstico de causa raiz. Distribuição confirmou 7 skills, sem toque na contagem.

### Feedback -

- `rg --files` e `rg -n` indisponíveis no host Windows. Seleção por leitura direta dos 4 paths da T4 e das suítes, sem varredura cega.
- Bloco `VIBEFLOW:CADEIA` preservado dentro dos marcadores para o init não reverter; nota condicional gravada fora dos marcadores.

### Para a review

- T4 prova contrato transversal, não pacote vibe-design. A4 e C1 finais dependem de T5 e T6 permanecerem verdes.

## Fatia T5

- Feito: três motores com inventário, resolução de alvo por spec pendente, relatório design-report.json gitignored e preservação do vivo byte a byte, com gate de plan DESIGN_JA_PLANEJADO e pré-requisito de spec DESIGN_SEM_SPEC. Suíte nova de contrato com 15 casos Python e 4 de paridade PowerShell, mais launcher sh com 6 passos. Reutilizados helpers de slug, inventário, relatório e harness dos motores irmãos, sem dependência nova.
- Marcado: T5 em `plan.md` com aceite e verificação em `[x]`, mais `Prova` sob a seção. `spec.md` não marcado, A3 e C1 seguem pendentes de fechamento na review, pois SKILL, template e references ficam para T6.
- Prova: `python "docs/vibe-design/tests/test-design.py" -v` -> 19 testes OK
- Prova: `bash "docs/vibe-design/tests/test-design.sh"` -> pass=6 fail=0
- Prova: `python "docs/tests/test-reparse-safety.py" -v` -> 12 testes OK
- Prova extra: `python "docs/tests/test-distribuicao.py" -v` -> 12 testes OK, contagem em 7 skills preservada
- Arquivos: `vibe-design/scripts/design.py`, `vibe-design/scripts/design.ps1`, `vibe-design/scripts/design.sh`, `docs/vibe-design/tests/test-design.py`, `docs/vibe-design/tests/test-design.sh`
- Commit da task: pendente até o commit isolado, mensagem e hash serão registrados no resultado e no chat sem reabrir este artefato
- Decisões críticas: omitir quando N/A

### Feedback +

- Suíte Python passou com 19 testes e launcher sh com 6 passos, com paridade PowerShell verde, sem diagnóstico de causa raiz. Reparse safety e distribuição permaneceram verdes.

### Feedback -

- `rg --files` e `rg -n` indisponíveis no host Windows. Seleção por leitura direta dos motores irmãos e das suítes, sem varredura cega.
- Correção única de sintaxe no teste novo antes do verde, aspas em `report["actions"]`, sem impacto no motor.

### Para a review

- T5 prova motor e preservação, não pacote operacional. A3 e C1 finais dependem de T6 permanecer verde.

## Fatia T6

- Feito: pacote operacional com SKILL de dois modos e três usos, template design.md com telas e prova, dois references como catálogo, ARQUITETURA e ANALISE, symlink skills/vibe-design, manifests Claude e Codex e Grok em 8 skills, workflow com design nos loops, teste de distribuição em 8, ESCOPO marcado e README com linha da skill. Reutilizados forma das SKILLs irmãs, molde de template, harness de launcher e contrato de manifests, sem dependência nova. `.agents/plugins/marketplace.json` e `plugin.json` da raiz precisaram de zero toque, pois não listam skills.
- Marcado: T6 em `plan.md` com aceite e verificação em `[x]`, mais `Prova` e `Arquivos` reais sob a seção. `spec.md` não marcado, A3, A4, C1 e C2 seguem pendentes de fechamento na review.
- Prova: `python "docs/tests/test-distribuicao.py" -v` -> 12 testes OK
- Prova: `python "docs/tests/test-visual-contract.py" -v` -> 4 testes OK
- Prova extra: `python "docs/vibe-design/tests/test-design.py" -v` -> 19 testes OK
- Prova extra: `bash "docs/vibe-design/tests/test-design.sh"` -> pass=6 fail=0
- Prova extra: `python "docs/tests/test-reparse-safety.py" -v` -> 12 testes OK
- Arquivos: `vibe-design/SKILL.md`, `vibe-design/templates/design.md`, `vibe-design/references/modos-entrada.md`, `vibe-design/references/kit-e-tokens.md`, `docs/vibe-design/ARQUITETURA.md`, `docs/vibe-design/ANALISE.md`, `skills/vibe-design`, `.claude-plugin/marketplace.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.grok-plugin/marketplace.json`, `.github/workflows/contrato.yml`, `docs/tests/test-distribuicao.py`, `docs/ESCOPO.md`, `README.md`
- Commit da task: pendente até o commit isolado, mensagem e hash serão registrados no resultado e no chat sem reabrir este artefato
- Decisões críticas: omitir quando N/A

### Feedback +

- Distribuição, visual, motor design e reparse passaram de primeira após a virada para 8, sem diagnóstico de causa raiz. Paridade PowerShell do motor seguiu verde.

### Feedback -

- `rg --files` e `rg -n` indisponíveis no host Windows. Seleção por leitura direta dos pacotes irmãos, manifests, README, ESCOPO, workflow e suítes, sem varredura cega.
- Linha nova no ESCOPO usou vírgula em vez de travessão longo, por regra de tom do repo.

### Para a review

- T6 fecha o pacote e a contagem em 8. A3, A4, C1 e C2 finais dependem da review conferir SKILL, template, references, manifests e README no diff.

## Fatia R1

- Feito: fechado o Nit da review Etapa 1. Conferência do `plan.md` alinhada ao estado real, item `Aprovação humana` em `[x]`, coerente com `# Status: aprovado`, T1 a T6 concluídas com prova e `spec.md` com aprovação em `[x]`. Nenhum source, template, teste ou lockfile tocado.
- Marcado: R1 em `review.md` com `[x]`, Conferência em `plan.md` com `[x]`. `spec.md` não marcado.
- Prova: `git diff --check` -> limpo
- Prova: `python "docs/tests/test-distribuicao.py" -v` -> 12 testes OK
- Arquivos: `.vibeflow/phases/phase-10-ux-detalhado-e-vibe-design/plan.md`, `.vibeflow/phases/phase-10-ux-detalhado-e-vibe-design/review.md`, `.vibeflow/phases/phase-10-ux-detalhado-e-vibe-design/implement.md`
- Commit da task: pendente até o commit isolado, mensagem e hash serão registrados no resultado e no chat sem reabrir este artefato
- Decisões críticas: N/A, ajuste processual sem decisão de produto

### Feedback +

- Correção de 1 caractere mais trilha, sem regressão na suíte de distribuição.

### Feedback -

- Nada a registrar.

### Para a review

- R1 fechado como Nit sem bloqueio. Veredito Approve da Etapa 1 permanece válido. Re-review confirma `plan.md:171` em `[x]` e R1 em `[x]`.

## Handoff

vibe-review

- Chat: recomende um novo chat focado em `vibe-review`. O `plan.md` e este `implement.md` vivos são a ponte. O commit da task já foi criado, sem push aqui.

<!-- fatia seguinte: copie o bloco ## Fatia abaixo, não apague as anteriores -->
