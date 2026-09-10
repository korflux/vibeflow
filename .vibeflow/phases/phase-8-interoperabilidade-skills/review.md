# Review: interoperabilidade, escrita direta e isolamento de etapas
# Alvo: phase-8-interoperabilidade-skills
# Status: rascunho

## Contexto

- Alvo: `phase-8-interoperabilidade-skills`, working tree local, incluindo arquivos não versionados da própria phase.
- Cadeia: `spec.md` / `plan.md` / `analyze.md` / `implement.md`, `interview.md` ausente por escolha da phase.
- O que muda: ponte Antigravity, distribuição, escrita direta dos artefatos vivos, investigação dirigida, isolamento de chat e contrato de prova visual.

## Cobertura

| Chave | Código | Notas |
|---|---|---|
| A1 | ok | `vibe-init` cria e repara `.agents/rules/vibeflow.md` e rejeita `.vibeflow` ou filhos mutáveis linkados antes da escrita; R6 corrigido por teste. |
| A2 | ok | `plugin.json`, README e sete ponteiros passaram `test-distribuicao.py`; o manifest segue o schema oficial documentado. |
| A3 | ok | Os seis motores não criam WIP, preservam o vivo em paths regulares e rejeitam reparse points nos arquivos operacionais de relatório e ignore; R5 corrigido por teste. |
| A4 | ok | As sete skills usam investigação dirigida; `test-distribuicao.py` passou. |
| A5 | ok | Handoffs e templates registram novo chat e isolamento por T*; `test-distribuicao.py` passou. |
| A6 | ok | Referências documentam `icon-only` somente para ações reconhecíveis, com requisitos de acessibilidade. |
| A7 | ok | O contrato visual define seleção de ferramenta, contexto renderizado e fallback explícito; quatro testes visuais passaram. |
| C1 | ok | Fixtures cobrem ausência, reparo, conflito, ponte sem cópia e `.vibeflow` como link, preservando o sentinel externo; R6 corrigido por teste. |
| C2 | ok | Manifest, sete pacotes, ponteiros e comandos documentados foram verificados. |
| C3 | ok | Suítes Python, paridade PowerShell do init, sete launchers Git Bash e a cobertura de reparse para relatório, `.gitignore` e `.vibeflow` passaram; R5 e R6 corrigidos por teste. |
| C4 | ok | A asserção de distribuição e a busca final não encontram entrada `*-wip.md` no ignore operacional. |
| C5 | ok | Arquiteturas, análises, README e `REGRAS.md` foram cruzados com a spec. |
| C6 | ok | A checklist visual cobre geometria, responsividade, estados, acessibilidade e runtime. |
| C7 | ok | A seleção navegador integrado, Chrome DevTools MCP e Playwright existente ou solicitado está documentada. |

## Checklist de correções

### Critical

- [x] R2: **Critical** - diretórios `phase-*`, `mvp` e `--dir` agora rejeitam symlink, junction ou reparse point nos seis motores; o inventário ignora links e não seleciona destino externo - remédio aplicado nos motores Python/PowerShell - prova: `python docs/tests/test-reparse-safety.py -v` -> o caso de diretório linkado passou para os seis motores, sem escrita no diretório externo - source: diff|segurança - gap: closed, re-review confirmado
- [x] R3: **Critical** - `New-LiveFile` nos seis motores PowerShell agora detecta `ReparsePoint`/`LinkType` antes de aceitar `PathType Leaf`; a proteção permanece alinhada ao Python - remédio aplicado nos motores Python/PowerShell - prova: `python docs/tests/test-reparse-safety.py -v` -> o caso de arquivo vivo linkado passou para os seis motores, preservando o sentinel externo - source: diff|segurança - gap: closed, re-review confirmado
- [x] R5: **Critical** - os seis motores agora validam `.vibeflow/<skill>-report.json` e `.vibeflow/.gitignore` antes de escrever, rejeitando symlink, junction, reparse point e diretório - remédio aplicado nos seis pares Python/PowerShell - prova: `python docs/tests/test-reparse-safety.py -v` -> 12 testes, OK; os sentinels externos permaneceram intactos para relatório e ignore - source: diff|segurança - gap: closed, re-review confirmado
- [x] R6: **Critical** - `vibe-init` agora rejeita `.vibeflow` e os filhos mutáveis linkados antes da primeira escrita, com paridade Python/PowerShell - remédio aplicado em `vibe-init/scripts/init.py` e `vibe-init/scripts/init.ps1` - prova: `python docs/tests/test-reparse-safety.py -v` -> o caso de `.vibeflow` linkado passou nos dois motores, sem criar `phases` ou relatório no alvo externo - source: A1|C1|diff|segurança - gap: closed, re-review confirmado

### Required

- [x] R1: **Required** - removida a entrada `review-wip.md` do `.vibeflow/.gitignore`, com asserção de contrato que impede qualquer entrada `*-wip.md` no ignore operacional - remédio aplicado e coberto em `docs/tests/test-distribuicao.py` - prova: `python docs/tests/test-distribuicao.py -v` -> 10 testes, OK; a busca não retorna `review-wip.md` - source: C4|plan.md|diff - gap: closed, re-review confirmado

### Optional / Nit

- [ ] R4: **Nit** - T1 teve os três itens de aceite técnico sincronizados com as provas; permanece pendente somente a aprovação humana do `plan.md` - remédio: confirmação humana deve marcar a aprovação antes de fechar a phase - prova: `rg -n "T1 concluída|Aprovação humana" .vibeflow/phases/phase-8-interoperabilidade-skills/plan.md` - source: plan.md - gap: decisão humana

## Segurança

- Foram auditados `--root`, `--dir`, `--slug`, seleção de phase/MVP, criação do artefato vivo e arquivos operacionais. Não há autenticação, banco, upload, segredo ou interface web nesta entrega. R2, R3, R5 e R6 foram corrigidos por teste; os quatro bloqueios de integridade de caminho não permanecem abertos. R4 continua sendo uma decisão humana de aprovação do plano.

## DoD

- [x] Suítes Python: init 32, distribuição 10, interview 19, spec 17, plan 21, analyze 18, implement 32, review 19, MVP 2, visual 4 e reparse 12, todas OK.
- [x] PowerShell do init: `pass=28 fail=0`.
- [x] Sete launchers pelo Git Bash real: init 5/5, interview 6/6, spec 6/6, plan 6/6, analyze 7/7, implement 8/8 e review 7/7.
- [x] `gitleaks detect --source . --verbose --redact --no-banner` sem leaks.
- [x] `git diff --check` sem erros.
- [x] Reexecutar a prova após corrigir R1, R2, R3, R5 e R6: teste de reparse com 12 casos, suítes Python, PowerShell init, launchers Git Bash real, gitleaks e `git diff --check` verdes.

## Notas

- A documentação do manifest Antigravity está alinhada ao schema e aos caminhos oficiais consultados.
- `docs/tests/test-visual-contract.py`, `docs/tests/test-reparse-safety.py` e os artefatos da phase 8 estão não versionados; devem entrar no commit para que as provas do CI existam no checkout.
- A execução do Git Bash dentro do sandbox falhou por `E_ACCESSDENIED`; com o Git Bash real e permissão elevada, os sete launchers passaram.
- Não houve mudança de UI; a validação visual renderizada não se aplica a esta phase.
- R5 e R6 estão corrigidos por prova e aguardam re-review. R4 ainda exige aprovação humana do `plan.md` antes de considerar a phase pronta.

## Veredito vigente

- [ ] **Approve**: proposta técnica sem bloqueios Critical/Required, aguardando confirmação humana.
- [ ] **Request changes**: não há Critical/Required aberto após o re-review.
- [x] **Approve com defer**: R4, porque a aprovação humana do `plan.md` ainda não foi confirmada; não há pendência técnica bloqueante.

## Handoff

aguarda aprovação humana do `plan.md`; depois, cadeia fechada sem pendências técnicas

- [ ] Aprovação humana (leu o arquivo e confirmou)

## Etapas

### Etapa 1 - first-pass - T1-T8, diff, código e provas

- Leu: `plan.md`, `spec.md`, `analyze.md`, `implement.md` e `REGRAS.md`
- Abriu: R1, R2, R3 e R4
- Fechou: nenhum
- Veredito desta etapa: Request changes

<!-- etapa seguinte: copie ### Etapa N abaixo. Não apague as anteriores. -->

### Etapa 2 - correção R1-R3 - pós-implementação

- Leu: achados R1-R3, seis pares de motores, testes de contrato e `.vibeflow/.gitignore`
- Abriu: R1, R2 e R3
- Fechou: R1, R2 e R3 por prova; R4 continua como nit de aprovação humana do plan
- Veredito desta etapa: correções provadas; re-review semântico pendente

### Etapa 3 - re-review pós-R1-R3 - T1-T8, suíte completa e hardening de paths

- Leu: `spec.md`, `plan.md`, `analyze.md`, `implement.md`, `REGRAS.md`, seis pares de motores, `vibe-init`, testes de contrato e diff da sessão
- Executou: 11 suítes Python, PowerShell init, sete launchers Git Bash real, gitleaks, `git diff --check` e reproduções isoladas de symlink em relatório e `.vibeflow`
- Abriu: R5 e R6; R1-R3 permanecem fechados; R4 permanece como nit de aprovação humana do plan
- Fechou: nenhum; R5 e R6 são novos bloqueios Critical
- Veredito desta etapa: Request changes

### Etapa 4 - correção pós-R5-R6 - barreiras operacionais e regressão

- Leu: R5 e R6, os doze motores Python/PowerShell, `vibe-init`, `docs/tests/test-reparse-safety.py` e os artefatos vivos da phase
- Executou: 12 testes de reparse, suítes Python, PowerShell init, sete launchers Git Bash real, gitleaks e `git diff --check`
- Fechou: R5 e R6 por prova; os sentinels externos permaneceram intactos e `.vibeflow` linkado não recebeu escrita; R4 permanece como nit de aprovação humana do plan
- Veredito desta etapa: correções provadas; re-review final pendente

### Etapa 5 - re-review final pós-R5-R6

- Leu: `spec.md`, `plan.md`, `analyze.md`, `implement.md`, o diff dos doze motores, `vibe-init` e `docs/tests/test-reparse-safety.py`
- Executou: motor local de `vibe-review` no alvo `phase-8-interoperabilidade-skills`, 12 testes de reparse, suítes Python, PowerShell init, sete launchers Git Bash real, gitleaks e `git diff --check`
- Abriu: nenhum Critical ou Required novo; R4 permanece como Nit de aprovação humana do `plan.md`
- Fechou: R5 e R6 confirmados; R1-R3 permanecem fechados por prova
- Veredito desta etapa: Approve com defer, sem pendência técnica bloqueante; aguarda confirmação humana
