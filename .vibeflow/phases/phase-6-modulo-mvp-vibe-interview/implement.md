# Implement: rota MVP no vibe-interview
# Pasta: phase-6-modulo-mvp-vibe-interview
# Status: concluído

## Fatia T1

- Feito: `.vibeflow/REGRAS.md`, `docs/ESCOPO.md`, `vibe-init/templates/REGRAS.md` e `README.md` agora reconhecem o baseline único `.vibeflow/mvp/`, a rota max obrigatória e a publicação compacta de decisões vigentes após review aprovada.
- Marcado: T1 e seus critérios em `plan.md`.
- Prova: `git diff --check -- .vibeflow/REGRAS.md docs/ESCOPO.md vibe-init/templates/REGRAS.md README.md` passou; `python docs/tests/test-distribuicao.py -v` executou 7 testes com resultado OK.

### Feedback +

- O patch no template do init acrescentou apenas o contrato MVP sobre a versão local existente, preservando as alterações anteriores do usuário.

### Para a review

- Confirmar que a exceção `.vibeflow/mvp/` não enfraquece a proibição de paths arbitrários e que nenhuma decisão ainda não revisada foi publicada como vigente.

## Fatia T2

- Feito: o prompt do interview agora mantém a IA como piloto, classifica produto novo versus feature e carrega o catálogo `references/mvp-discovery.md` somente no modo MVP.
- Feito: o catálogo cobre produto, jornadas, acesso, usuários, dados, visual, stack, infraestrutura, segurança e operação, com recomendações contextuais e estados explícitos de cobertura.
- Feito: o template único ganhou seções MVP omitíveis e decisões críticas com IDs estáveis.
- Marcado: T2 e seus critérios em `plan.md`.
- Prova: `python docs/tests/test-distribuicao.py -v` passou 7 testes; `git diff --check -- vibe-interview docs/vibe-interview` não encontrou erros.

### Feedback +

- A descoberta aceita falta de resposta sem perder cobertura: decisões reversíveis podem ser assumidas e informadas; pendências críticas continuam exigindo o humano.

### Para a review

- Verificar que o catálogo funciona como referência interna e não induz o agente a despejar um questionário extenso no chat.

## Fatia T3

- Feito: `--mvp` e `-Mvp` promovem o mesmo wip para `.vibeflow/mvp/interview.md`, preservando o modo phase e acrescentando `modo`, `kind`, `mvp` e `alvo` ao relatório.
- Feito: o apply MVP confere tamanho e SHA-256, remove o wip somente após sucesso e recusa sobrescrita com `MVP_EXISTE`.
- Feito: motores Python e PowerShell e o launcher Unix receberam o contrato explícito; a suíte inclui regressão phase, MVP único, path inesperado e combinação inválida de flags.
- Marcado: T3 e o checkpoint T1-T3 em `plan.md`, com a indisponibilidade do launcher registrada.
- Prova: `python docs/vibe-interview/tests/test-interview.py -v` passou 18 testes, incluindo 2 testes reais de paridade PowerShell.

### Feedback +

- O modo MVP não cria `phase-N`; apenas o diretório estrutural `phases/.gitkeep` continua sendo garantido pelo inventário comum.

### Bloqueio de ambiente

- `bash docs/vibe-interview/tests/test-interview.sh` não pôde executar: o `bash.exe` deste Windows encaminha para WSL e o ambiente não possui `/bin/bash`. O launcher foi coberto por inspeção e pela suíte foi atualizado, mas sua execução fica pendente para host Unix.

### Para a review

- Conferir o schema aditivo do relatório e a preservação byte a byte do wip no segundo apply MVP.

## Fatias T4-T5

- Feito: `vibe-spec` entende o motor, aceita alvo MVP explícito e consolida as decisões críticas com `mantém`, `cria` ou `substitui`, sem publicar em `REGRAS.md`.
- Feito: os motores exigem `mvp/interview.md`, recusam slug/dir no modo especial e impedem atualização depois de `plan.md`.
- Feito: a promoção da spec passou a usar arquivo temporário verificado antes da substituição, preservando inclusive um rascunho anterior se a cópia falhar.
- Marcado: T4, T5 e checkpoint correspondente em `plan.md`.
- Prova: `python docs/vibe-spec/tests/test-spec.py -v` passou 16 testes, com paridade real PowerShell e regressão phase.

### Feedback +

- Interview e spec coexistem no alvo MVP e nenhum diretório `phase-N` é criado pelo modo especial.

### Bloqueio de ambiente

- A suíte `test-spec.sh` recebeu cobertura `--mvp`, mas não pode rodar neste host sem `/bin/bash`.

### Para a review

- Verificar que a substituição atômica do rascunho não altera o contrato público e elimina a janela de perda da spec anterior.

## Fatias T6-T7

- Feito: o plan usa alvo MVP explícito, exige spec aprovada semanticamente e encaminha para `vibe-analyze` em vez de permitir implementação direta.
- Feito: tasks que realizam decisões críticas citam ID e ação, mantendo rastreabilidade desde a spec.
- Feito: motores recusam ausência de spec, combinação com dir e plan já analisado; a promoção também passou a preservar o rascunho anterior por substituição temporária verificada.
- Marcado: T6, T7 e checkpoint correspondente em `plan.md`.
- Prova: `python docs/vibe-plan/tests/test-plan.py -v` passou 17 testes, incluindo paridade PowerShell, fluxo MVP e regressão phase; `git diff --check` passou.

### Feedback +

- Interview, spec e plan coexistem no mesmo alvo MVP sem alocar número de phase.

### Para a review

- Confirmar que decisões críticas aparecem apenas nas tasks que efetivamente as criam, substituem ou usam como limite de aceite.

## Fatias T8-T9

- Feito: o analyze MVP exige interview, spec e plan, cruza IDs críticos e classifica como `CRITICAL` qualquer mudança material sem `substitui`, ID órfão ou task divergente.
- Feito: o relatório semântico permanece read-only sobre as fontes e não publica decisões em `REGRAS.md`.
- Feito: motores promovem somente para `.vibeflow/mvp/analyze.md`, com alvo explícito e substituição temporária verificada do próprio rascunho.
- Marcado: T8, T9 e checkpoint correspondente em `plan.md`.
- Prova: `python docs/vibe-analyze/tests/test-analyze.py -v` passou 14 testes, incluindo paridade PowerShell e regressão phase; `git diff --check` passou.

### Feedback +

- A rota MVP não aceita ausência de interview, eliminando a possibilidade de analisar apenas spec e plan como se fossem uma feature normal.

### Para a review

- Validar que a taxonomia `decisao` produz bloqueio apenas para divergência material e não para detalhes cosméticos reversíveis.

## Fatias T10-T11

- Feito: implement MVP usa somente a fila de `.vibeflow/mvp/plan.md` e expõe `analyze_gate` no relatório.
- Feito: apply recusa analyze ausente, rascunho ou bloqueado e preserva o wip; apenas `aprovado` e `limpo` libera a promoção.
- Feito: o histórico acumulativo de fatias é promovido para `mvp/implement.md` com substituição temporária verificada, sem publicar decisões críticas.
- Marcado: T10, T11 e checkpoint correspondente em `plan.md`.
- Prova: `python docs/vibe-implement/tests/test-implement.py -v` passou 31 testes, incluindo gate em três estados, fila isolada, acúmulo, paridade PowerShell e regressão phase.

### Feedback +

- O motor continua sem interpretar o conteúdo geral do analyze; lê apenas status e veredito como gate determinístico de segurança do modo MVP.

### Para a review

- Confirmar que a skill impede o código antes do apply, enquanto o motor fornece a segunda barreira no momento da promoção.

## Fatias T12-T13

- Feito: review MVP exige os cinco predecessores, julga decisões críticas e impede Approve quando há conflito não declarado.
- Feito: `Decisões para vigência` permanece proposta até confirmação humana; depois disso, a IA atualiza por ID somente a tabela compacta em `REGRAS.md`.
- Feito: motores não têm flag de sync, promovem para `mvp/review.md` e preservam `REGRAS.md` byte a byte em rascunho, request-changes e aprovado.
- Marcado: T12 e T13 em `plan.md`.
- Prova: `python docs/vibe-review/tests/test-review.py -v` passou 17 testes, incluindo cadeia incompleta, três estados de review, paridade PowerShell, ausência de flag de sync e regressão phase.

### Feedback +

- A separação entre promoção mecânica e publicação semântica torna impossível que o script publique uma decisão apenas porque o review foi salvo.

### Para a review

- Verificar se o patch por ID preserva decisões vigentes não citadas e se a fonte aponta para o review humano aprovado.

## Fatia T14

- Feito: teste integrado isolado `docs/tests/test-mvp-flow.py` executando a cadeia max completa nas seis portas no alvo `.vibeflow/mvp/`.
- Feito: inclusão do teste no workflow `.github/workflows/contrato.yml`.
- Marcado: T14 e checkpoint correspondente em `plan.md`.
- Prova: `python docs/tests/test-mvp-flow.py -v` passou 2 testes com sucesso; `python docs/tests/test-distribuicao.py -v` passou 7 testes; todas as suítes de contrato de skills passaram; `git diff --check` passou sem divergências.

### Feedback +

- Nenhuma pasta `phase-N` é criada durante a rota MVP e as decisões vigentes permanecem isoladas até a aprovação formal humana.

### Para a review

- Conferir a execução integrada de ponta a ponta no CI e a cobertura completa das suítes de contrato.

