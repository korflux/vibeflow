# Implement: interoperabilidade, escrita direta e isolamento de etapas
# Alvo: phase-8-interoperabilidade-skills
# Status: concluído

## Fatia T2

- Feito: `plugin.json` agora segue o manifest mínimo do Antigravity, com `$schema`, `name` e `description`, sem campos de outros hosts nem aliases de `commands/`. O README separa os escopos project-local e global do `npx skills`, os diretórios de plugin e skills da IDE e do CLI Antigravity, os caminhos de regras globais do Codex e do Antigravity, os fallbacks do Windows e as verificações de descoberta. O teste de distribuição valida esse contrato e mantém a prova dos sete ponteiros `skills/`.
- Marcado: T2 no `plan.md`; A2 e C2 na `spec.md`.
- Prova: `python docs/tests/test-distribuicao.py -v` -> 8 testes, OK; `python docs/vibe-init/tests/test-init.py -v` -> 32 testes, OK; `git diff --check` -> sem erros.
- Arquivos: `plugin.json`, `README.md`, `docs/tests/test-distribuicao.py`, `.vibeflow/phases/phase-8-interoperabilidade-skills/plan.md`, `.vibeflow/phases/phase-8-interoperabilidade-skills/spec.md`.
- Base externa: [manifest e caminhos de plugin do Antigravity](https://www.antigravity.google/docs/cli/plugins/), [plugins da IDE](https://www.antigravity.google/docs/ide/plugins/) e [CLI npx skills](https://github.com/vercel-labs/skills).

### Feedback +

- O manifest raiz continua usando `skills/` por convenção do host; a lista de skills não foi duplicada em `plugin.json`.
- A ponte `.agents/rules/vibeflow.md` continua curta e aponta para a única fonte `.vibeflow/REGRAS.md`; a T2 apenas documenta e testa esse contrato, sem criar uma segunda fonte.

### Para a review

- Conferir a compatibilidade do manifest mínimo com a versão do Antigravity usada no host e se os caminhos project-local/global documentados continuam distintos dos diretórios de regras.

## Fatia T3

- Feito: `vibe-interview`, `vibe-spec` e `vibe-plan` agora executam os gates, resolvem o alvo e preparam o arquivo vivo vazio apenas quando ele não existe. Arquivos vivos existentes são preservados byte a byte; os relatórios mantêm seleção, `created`, `modo`, `actions` e avisos, sem estado WIP, promoção, cópia ou hash. Os testes Python e os pares PowerShell cobrem criação, reexecução, MVP, `--dir`, colisões e gates sem rascunho temporário.
- Marcado: T3 no `plan.md`. A3 e C3 permanecem pendentes na `spec.md` porque também dependem de T4, que cobre analyze, implement e review, além do fluxo MVP completo.
- Prova: `python docs/vibe-interview/tests/test-interview.py -v` -> 19 testes, OK; `python docs/vibe-spec/tests/test-spec.py -v` -> 17 testes, OK; `python docs/vibe-plan/tests/test-plan.py -v` -> 21 testes, OK; `bash docs/vibe-interview/tests/test-interview.sh` -> pass=6 fail=0; `bash docs/vibe-spec/tests/test-spec.sh` -> pass=6 fail=0; `bash docs/vibe-plan/tests/test-plan.sh` -> pass=6 fail=0.
- Arquivos: os seis motores Python/PowerShell do grupo, os seis testes Python/Bash, os três launchers Bash e `docs/tests/launcher-harness.sh`. Os arquivos Bash foram normalizados para LF porque o CRLF impedia a execução real no Bash.

### Para a review

- Confirmar que `--apply` continua apenas preparando ou validando o vivo e que a semântica será replicada em analyze, implement e review na T4.

## Fatia T4

- Feito: `vibe-analyze`, `vibe-implement` e `vibe-review` agora mantêm os gates de seleção, a fila do plan, o gate de analyze do MVP e o re-review, mas `--apply` somente prepara o artefato vivo vazio quando ele não existe. Arquivos `analyze.md`, `implement.md` e `review.md` existentes são preservados byte a byte; os relatórios mantêm alvo, ações e erros úteis sem campo `wip`, promoção, cópia ou hash. O helper do launcher passou a ignorar aliases quebrados de Python 3 no Windows ao ler relatórios.
- Marcado: T4 no `plan.md`; A3 e C3 na `spec.md`.
- Prova: `python docs/vibe-analyze/tests/test-analyze.py -v` -> 18 testes, OK; `python docs/vibe-implement/tests/test-implement.py -v` -> 32 testes, OK; `python docs/vibe-review/tests/test-review.py -v` -> 19 testes, OK; `python docs/tests/test-mvp-flow.py -v` -> 2 testes, OK; launchers Git Bash -> analyze 7/7, implement 8/8, review 7/7. As suítes Python incluem paridade PowerShell 7.
- Arquivos: os seis motores Python/PowerShell dos três pacotes, os seis testes Python/Bash, `docs/tests/test-mvp-flow.py` e `docs/tests/launcher-harness.sh`.

### Para a review

- Confirmar que a criação concorrente do arquivo vivo preserva bytes existentes e que a fila, o gate MVP e os estados de re-review continuam idênticos ao contrato anterior, sem depender de WIP.

<!-- fatia seguinte: copie o bloco ## Fatia abaixo, não apague as anteriores -->

## Fatia T5

- Feito: as sete `SKILL.md` agora começam pela pergunta da etapa, usam `rg --files` e `rg -n` para localizar evidências, abrem somente as entradas e dependências do fluxo e deixam explícito que inventário não é leitura da árvore inteira. Os seis templates aplicáveis registram escrita direta no artefato vivo, `# Status: rascunho` durante elaboração e a política de chat por porta, incluindo um chat por T* no implement. Nenhuma skill ou template orienta preencher ou promover WIP.
- Marcado: T5 no `plan.md`; A4, A5 e C4 na `spec.md`. C5 permanece para T7, que atualiza arquitetura e análise canônicas.
- Prova: `python docs/tests/test-distribuicao.py -v` -> 9 testes, OK; `python docs/vibe-init/tests/test-init.py -v` -> 32 testes, OK; `python docs/vibe-interview/tests/test-interview.py -v` -> 19 testes, OK; `python docs/vibe-spec/tests/test-spec.py -v` -> 17 testes, OK; `python docs/vibe-plan/tests/test-plan.py -v` -> 21 testes, OK; `python docs/vibe-analyze/tests/test-analyze.py -v` -> 18 testes, OK; `python docs/vibe-implement/tests/test-implement.py -v` -> 32 testes, OK; `python docs/vibe-review/tests/test-review.py -v` -> 19 testes, OK.
- Arquivos: as sete `SKILL.md`, os seis templates aplicáveis e `docs/tests/test-distribuicao.py`.

### Para a review

- Confirmar que o contrato textual de investigação dirigida e isolamento de chat está alinhado com as arquiteturas e análises canônicas da T7, sem tornar a troca de chat um gate mecânico.

## Fatia T6

- Feito: `vibe-implement/references/chrome-devtools.md` e `vibe-review/references/ui-visual-quality.md` agora formam uma checklist renderizada objetiva, com geometria, viewport, estados, acessibilidade e console/rede/assets. As três skills relevantes selecionam navegador integrado primeiro, MCP Server `chrome-devtools` para inspeção e Playwright somente quando já existir ou for solicitado; ausência de capacidade fica como limitação explícita. A orientação de controles mantém `icon-only` apenas para ações universalmente reconhecíveis, como lixeira para apagar, com nome acessível, foco visível, área de interação adequada, tooltip quando aplicável e texto para ações ambíguas. O teste textual cobre C6-C7 sem instalar navegador ou dependência nova.
- Marcado: T6 no `plan.md`; A6, A7, C6 e C7 na `spec.md`.
- Prova: `python docs/tests/test-visual-contract.py -v` -> 4 testes, OK; `python docs/vibe-plan/tests/test-plan.py -v` -> 21 testes, OK; `python docs/vibe-implement/tests/test-implement.py -v` -> 32 testes, OK; `python docs/vibe-review/tests/test-review.py -v` -> 19 testes, OK; `git diff --check` -> exit 0, sem erros de whitespace.
- Arquivos: `vibe-implement/references/chrome-devtools.md`, `vibe-review/references/ui-visual-quality.md`, `vibe-plan/SKILL.md`, `vibe-implement/SKILL.md`, `vibe-review/SKILL.md`, `docs/tests/test-visual-contract.py`, `.vibeflow/phases/phase-8-interoperabilidade-skills/plan.md` e `.vibeflow/phases/phase-8-interoperabilidade-skills/spec.md`.
- Limitação de escopo: a fatia altera documentação e teste de contrato, não uma interface web; portanto não há rota renderizada para abrir nesta execução. A validação de navegador permanece obrigatória para futuras tasks que toquem UI, conforme o contrato registrado.

### Para a review

- Confirmar a cobertura textual da checklist, a ordem navegador integrado → Chrome DevTools MCP → Playwright existente/solicitado e a recusa de passe visual sem evidência ou capacidade.

## Fatia T7

- Feito: a documentação canônica agora descreve `.vibeflow/REGRAS.md` como fonte única, a ponte relativa `.agents/rules/vibeflow.md` do Antigravity, os caminhos globais separados de Codex e Antigravity, o apply como preparação/preservação do arquivo vivo, investigação dirigida, política de chat e prova visual condicional. As arquiteturas e análises das sete skills foram alinhadas sem publicar `UI-01` na tabela de decisões vigentes.
- Marcado: T7 no `plan.md`; C5 na `spec.md`.
- Prova: `python docs/tests/test-distribuicao.py -v` -> 9 testes, OK; `python docs/tests/test-visual-contract.py -v` -> 4 testes, OK; `git diff --check` -> exit 0, sem erros de whitespace.
- Arquivos: `.vibeflow/REGRAS.md`, `README.md`, `docs/ESCOPO.md`, os pares `ARQUITETURA.md`/`ANALISE.md` de `vibe-init`, `vibe-interview`, `vibe-spec`, `vibe-plan`, `vibe-analyze`, `vibe-implement` e `vibe-review`, `.vibeflow/phases/phase-8-interoperabilidade-skills/plan.md`, `.vibeflow/phases/phase-8-interoperabilidade-skills/spec.md` e este arquivo.
- Decisões: HOST-01 documentada; UI-01 permanece nas skills e referências até o pós-review com confirmação humana.

### Para a review

- Conferir que os sete contratos não reintroduzem transporte temporário de conteúdo, que a ponte Antigravity continua sendo somente uma inclusão e que C5 está marcado sem alterar o histórico das phases fechadas.

## Fatia T8

- Feito: o `.vibeflow/.gitignore` deixou de ignorar artefatos WIP, o `implement-wip.md` operacional existente foi removido e os relatórios foram preservados. O CI passou a executar o contrato visual e usa gitleaks 8.30.1. O teste de distribuição protege a presença dos fluxos MVP e visual no CI.
- Feito: `vibe-init/scripts/init.sh` agora valida que `python3`, `python` e `pwsh` realmente executam antes de selecioná-los. O harness dos launchers usa wrapper para o PowerShell real, evitando a quebra de resolução de `pwsh.dll` causada por symlink no Windows.
- Marcado: T8 no `plan.md`; checkpoint após T8 concluído.
- Prova: 32 testes init, 9 distribuição, 19 interview, 17 spec, 21 plan, 18 analyze, 32 implement, 19 review, 2 MVP e 4 visuais, todos OK; `pwsh -NoProfile -File docs/vibe-init/tests/test-init.ps1` -> `pass=28 fail=0`; launchers Git Bash -> init 5/5, interview 6/6, spec 6/6, plan 6/6, analyze 7/7, implement 8/8, review 7/7; `gitleaks version` -> 8.30.1; gitleaks sem leaks; `git diff --check` -> exit 0.
- Busca canônica: os hits restantes são asserts negativos dos testes, instruções explícitas de investigação dirigida e hashes de backup legítimos do init; não há operação runtime de preencher/promover WIP nem cópia/hash de promoção.
- Arquivos: `.vibeflow/.gitignore`, `.vibeflow/implement-wip.md`, `docs/tests/test-distribuicao.py`, `docs/tests/test-mvp-flow.py`, `docs/tests/test-visual-contract.py`, `docs/tests/launcher-harness.sh`, `.github/workflows/contrato.yml`, `vibe-init/scripts/init.sh`, `.vibeflow/phases/phase-8-interoperabilidade-skills/plan.md` e este arquivo.

### Para a review

- Confirmar o contrato final sem WIP, a entrada do teste visual no CI, a seleção robusta de runtimes nos launchers e a limpeza somente do artefato operacional, sem alteração de reports ou phases históricas.

## Correção pós-review, R1-R3

- Feito: removida a entrada `review-wip.md` do `.vibeflow/.gitignore`; os seis motores agora rejeitam symlink, junction e reparse point em `.vibeflow`, `phases`, `mvp`, `--dir` e inventário de fases; o PowerShell passou a rejeitar o mesmo tipo de link em todo `New-LiveFile`, antes de aceitar `PathType Leaf`. A rejeição preserva o alvo externo e impede escrita fora da raiz permitida.
- Marcado: R1, R2 e R3 no `review.md` como corrigidos por prova; T8 mantém a cobertura de escrita direta e isolamento de caminhos.
- Prova: `python docs/tests/test-reparse-safety.py -v` -> 6 testes, OK, cobrindo os seis motores Python e PowerShell para MVP linkado, diretório de fase linkado e arquivo vivo linkado; suítes Python completas OK; `pwsh -NoProfile -File docs/vibe-init/tests/test-init.ps1` -> `pass=28 fail=0`; launchers Git Bash real -> init 5/5, interview 6/6, spec 6/6, plan 6/6, analyze 7/7, implement 8/8 e review 7/7; gitleaks sem leaks; `git diff --check` -> exit 0.
- Arquivos: `vibe-interview/scripts/interview.py`, `vibe-interview/scripts/interview.ps1`, `vibe-spec/scripts/spec.py`, `vibe-spec/scripts/spec.ps1`, `vibe-plan/scripts/plan.py`, `vibe-plan/scripts/plan.ps1`, `vibe-analyze/scripts/analyze.py`, `vibe-analyze/scripts/analyze.ps1`, `vibe-implement/scripts/implement.py`, `vibe-implement/scripts/implement.ps1`, `vibe-review/scripts/review.py`, `vibe-review/scripts/review.ps1`, `docs/tests/test-reparse-safety.py`, `docs/tests/test-distribuicao.py`, `.github/workflows/contrato.yml` e `.vibeflow/.gitignore`.
- Limite: R4 permanece como nit de aprovação humana do `plan.md`; os checkboxes de aceite que têm prova técnica podem ser sincronizados, mas a confirmação humana não deve ser inventada por implementação.

## Correção pós-review, R5-R6

- Feito: adicionadas barreiras de escrita nos seis pares de motores Python/PowerShell para `.vibeflow/.gitignore` e `.vibeflow/<skill>-report.json`, com recusa de symlink, junction, reparse point e diretório. O `vibe-init` também valida `.vibeflow`, `old`, `phases`, `.gitignore`, `.gitkeep`, `init-pending.json`, `init-report.json` e regras antes de mutar o disco, preservando a paridade entre os motores.
- Feito: `docs/tests/test-reparse-safety.py` passou a provar sentinel para relatório, `.gitignore` e `.vibeflow` linkados, em Python e PowerShell.
- Marcado: R5 e R6 como corrigidos por prova no `review.md`; R4 segue pendente por depender de aprovação humana do plano.
- Prova: 12 testes de reparse, todas as suítes Python, PowerShell init `pass=28 fail=0`, sete launchers Git Bash real, gitleaks e `git diff --check` passaram.
- Handoff: `vibe-review`, para re-review final. Não houve commit.

### Handoff

vibe-review
