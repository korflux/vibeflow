# Review: Cadeia alinhada ao implement
# Alvo: phase-20-cadeia-alinhada-ao-implement
# Status: request-changes

## Contexto

- Alvo: fase `phase-20-cadeia-alinhada-ao-implement`, commit integrado `8d1e6e5` (`task(T1,...,T9)`) sobre `7cdc1b5` (`integracao.origem`).
- Cadeia: spec.md / plan.md (`# Protocolo: coordenacao-v1`, `# Modo: A`); sem interview, sem analyze (rota high), design N/A.
- O que muda: init, spec, design, plan e analyze passam a preparar o terreno do coordenador do Modo A; a implement confere a capacidade de delegação antes da primeira onda e roteia R* por `papel`; a review audita o executado pelo `execution.json`. Nenhum motor muda; versão 9.0.0.

## Tipo de review

- Tipo: final
- Marco e justificativa: integração final; fila concluída (T1 a T9 com `local_valida`, `integracao.prova_valida` verdadeiro e `commit_encontrado` = `8d1e6e5`).
- T* abertas fora do marco: nenhuma
- Provas reaproveitadas: `Prova afetada:` de T1 a T9 e a união na integração, registradas em `execution.json` (inputs inalterados no HEAD).
- Provas executadas: regressão completa do plan, jornada do init (A1, A2, A5), varredura gitleaks do intervalo da phase e consulta ao CI; detalhes na Etapa 1.

## Cobertura da solicitação

- Origem e limites: a origem disponível é a tabela "Cobertura da origem" e as decisões 1 a 16 da `spec.md`, aprovada pelo humano (decisão 14). Os relatórios de auditoria que originaram a phase não estão no disco; a matriz confia que a tabela da spec os transcreve por inteiro. Sem interview.

| Item da solicitação e fonte (A*/C* quando houver) | Implementação | Evidência | Situação |
|---|---|---|---|
| Bloqueante init: correção fora do recorte (A1) | `vibe-init/templates/AGENTS.md:52` | T1 `test-init.py`/`test-init.ps1`; jornada do init: `AGENTS.md` gerado proíbe corrigir, manda registrar e reportar | atendido |
| SLOT de comandos (A2) | `vibe-init/templates/AGENTS.md:22` | T1; jornada do init: SLOT pede recorte, suíte, E2E, segredos, CI e onde roda | atendido |
| Perfis alinhados e relatório de oito campos (A3) | `vibe-init/templates/agents/claude/*.md`, `codex/*.toml` | T1; jornada: os doze perfis instalados iguais em bytes aos templates | atendido |
| Re-init: perfil desatualizado, customização e patch Git (A4) | `vibe-init/SKILL.md` §1 (passos 1 a 4 e re-init de `AGENTS.md`) | T1 `test-init.py` (preserva conflito); substituição é passo da IA, risco aceito no plan T1 | atendido |
| Regra de testes do VibeFlow fora, Git em frases curtas, justificativa de esforços (A5) | `vibe-init/templates/AGENTS.md`, `docs/vibe-init/ARQUITETURA.md:27` | T1; jornada: regra de testes de skills ausente, seção Git em frases curtas | atendido |
| Spec: Como provar por jornada e nível, evidência renderizada sem ferramenta, consumidores (A6) | `vibe-spec/SKILL.md` passo 3, `templates/spec.md`, `references/ui-visual-direction.md` | T2 `test-spec.py` (19 OK); regressão | atendido |
| Design: commit, prova visual por tela, superfícies, viewport, precedência do kit (A7) | `vibe-design/SKILL.md`, `templates/design.md`, `references/kit-e-tokens.md` | T3 `test-design.py` (19 OK); regressão | atendido |
| Plan: formato literal de `Arquivos:`, path incomparável, placeholder comparável (A8) | `vibe-plan/SKILL.md` regras 3 e 4, `templates/plan.md` | T4 `test-plan.py` + checagem mecânica do placeholder pelo parser do motor | atendido |
| Prontidão com local e destino (A9) | `vibe-plan/SKILL.md` §3 itens 2 e 3, `templates/plan.md` | T4; regressão | atendido |
| Arquivo compartilhado e prosa separada (A10) | `vibe-plan/SKILL.md:94` | T4; regressão. Lacuna de roteamento de `AGENTS.md` em R2 | parcial |
| `Prova afetada:` com evidência visual e prova de prosa (A11) | `vibe-plan/SKILL.md` regra 7 | T4; regressão | atendido |
| Plan sem checkpoint no Modo A, docs do parser (A12) | `vibe-plan/SKILL.md` regra 10, `docs/vibe-plan/` | T4; regressão | atendido |
| Analyze confere o contrato da implement com gravidades da F5 (A13) | `vibe-analyze/SKILL.md` item 6, `references/coverage.md` §3 a §5 | T5 `test-analyze.py` (16 OK); regressão | atendido |
| Analyze sem "provas proporcionais", passes, `design.md` nas fontes (A14) | `vibe-analyze/SKILL.md`, `templates/analyze.md`, `coverage.md` §1 e §2 | T5; `rg` sem ocorrência de "proporcionais" no pacote e nos docs do analyze | atendido |
| Implement confere capacidade e roteia por `papel` (A15) | `vibe-implement/SKILL.md` §2 e tabela de etapas; `delegation.md` | T6 `distribuicao` + `test-implement.py`; cópias de `delegation.md` idênticas (`cmp`) | atendido |
| Auditoria do executado (A16) | `vibe-review/SKILL.md` §3 "Auditar o executado" | T7 `test-review.py` (25 OK); exercida nesta review. Regra 2 conflita com a decisão 4 em R1 | parcial |
| Cobertura por prova, regressão com HEAD, árvore suja (A17) | `vibe-review/SKILL.md` §3 item 4 e "Selecionar e executar provas" | T7; exercida nesta review | atendido |
| Re-review por `correcao.commit` e `papel` no R* (A18) | `vibe-review/SKILL.md` §3 item 3 e parágrafo Finding | T7; regressão | atendido |
| Finalização ignora patch em `## Decisões vigentes` (A19) | `vibe-review/SKILL.md` §3 "Paths de código e teste" e §5 passo 1 | T7; regressão. Ambiguidade de "snapshot da review" em R3 | atendido |
| Modo A sem checkpoint, §0 delegado sem correção, docs e template por protocolo (A20) | `vibe-review/SKILL.md` §0, §2, §3, §6; `docs/vibe-review/`; `templates/review.md` | T7; regressão | atendido |
| C1: suítes verdes e cópias de `delegation.md` idênticas | suítes de todas as skills | regressão local com exceções conhecidas; CI `contrato` do commit com job `segredos` em falha (R4) | parcial |
| C2: 9.0.0 nos manifestos | cinco manifestos e `CONTRACT_VERSION` | T8 `distribuicao`; regressão | atendido |
| C3: docs sem `REGRAS.md` como fonte viva, diagrama com ramo design | `docs/vibe-spec/`, `docs/vibe-design/`, `docs/vibe-analyze/` | `rg REGRAS` sem ocorrência nesses docs; `docs/vibe-spec/ANALISE.md:16` com o ramo design | atendido |
| C4: Modo B, `etapas-v1` e sem marcador inalterados | qualificação por protocolo em plan, analyze, implement e review | T7/T9; regressão (suítes de implement e execution) | atendido |
| Decisão 15: checkpoint ainda possível no Modo B de `coordenacao-v1` | `vibe-plan/SKILL.md` regra 10; `templates/plan.md` | leitura; coerente com `vibe-review/SKILL.md` §3 (checkpoint em B) | atendido |
| Decisão 16: `Prova afetada:` derivada de Como provar; plan lê o design | `vibe-plan/SKILL.md` regra 7 e §3 item 4 | leitura; nomes de seção iguais no template do design | atendido |
| Decisão 4: erro fora do recorte registrado, nunca corrigido | template do init; `.erros-encontrados/` com dois registros novos | registros criados pelos agentes; conflito com a auditoria da review em R1 | parcial |
| Decisão 9: redator nunca edita `AGENTS.md` | `delegation.md:13`, perfis do redator | T9 do plan delegou `AGENTS.md` a redator (`execution.json` actor `redator-t9`); R2 | parcial |
| Decisão 13: push ao final com confirmação | finalização pendente | fora desta etapa | atendido (pendente de confirmação humana) |
| Fora: worktree, fan-out, troca de esforço, `strip()`/`Trim()`, motor e schema | nenhum motor alterado no diff | `git diff --name-only 7cdc1b5 HEAD` sem `scripts/` | atendido |

## Checklist de correções

### Required

- [x] R1: **Required** - `vibe-review/SKILL.md:98` - A auditoria "Diff na união" abre R* Required para todo path fora de `.vibeflow/` e da união dos `Arquivos:`, mas a regra de erros fora do escopo (decisão 4, `vibe-init/templates/AGENTS.md:52`) obriga quem encontra um erro a criar arquivo em `.erros-encontrados/`, path que nenhuma T* declara. Nesta phase o diff traz `.erros-encontrados/2026-10-14-init-ps1-regex-split-limite.md` e `.erros-encontrados/2026-10-14-test-implement-sandbox-na-raiz.md`, autorizados pela Colaboração do plan mas fora de `Arquivos:`; toda phase do Modo A que achar um erro cai no mesmo R*. - remédio: `vibe-implement` (redator) acrescenta ao item 2 da auditoria, e ao trecho equivalente de `docs/vibe-review/ARQUITETURA.md:85`, que arquivo novo em `.erros-encontrados/` criado pela regra de erros fora do escopo é registrado em Notas e não abre R*, enquanto edição ou remoção de registro existente continua contando; com isso os dois registros desta phase ficam cobertos. - prova: `py -3 docs/vibe-review/tests/test-review.py -v` e releitura do item 2 contra a decisão 4. - source: decisão 4, A16 - gap: contradicts - papel: redator
- [x] R2: **Required** - `vibe-implement/references/delegation.md:13` - O contrato desta phase proíbe o redator de editar `AGENTS.md` (decisão 9, `delegation.md:13` e as duas cópias, perfis do redator), e nenhum outro papel do Modo A tem `AGENTS.md` como escrita autorizada fora da sincronização de `## Decisões vigentes`. Ao mesmo tempo, `vibe-plan/SKILL.md:94` manda declarar T* de texto como `Resultado principal: prosa (redator)` sem tratar `AGENTS.md`, e a T9 deste plan declarou `AGENTS.md` em `Arquivos:` e foi executada por `redator-t9`, contrariando a decisão 9. Uma T* que precisa mudar `AGENTS.md` (comum neste repo e em re-init) fica sem dono válido. - remédio: decisão do humano entre (a) permitir ao redator editar `AGENTS.md` somente quando declarado em `Arquivos:` da T* aprovada, nunca a seção `## Decisões vigentes`, ajustando `delegation.md` (duas cópias), os perfis do redator e `vibe-plan/SKILL.md` regra 5 (redator), com a decisão 9 da spec atualizada pelo finalizador; ou (b) atribuir mudança de `AGENTS.md` em T* ao finalizador, ajustando os mesmos paths. Recomendação: (a). - prova: `py -3 docs/tests/test-distribuicao.py -v` (cópias idênticas) e `py -3 docs/vibe-init/tests/test-init.py -v` (perfis). - source: decisão 9, A10, plan T9 - gap: contradicts - papel: redator
- [x] R4: **Required** - `.vibeflow/phases/phase-20-cadeia-alinhada-ao-implement/execution.json:53` - O job `segredos` do CI `contrato` (run 38615291800, commit `8d1e6e5`) falhou: `gitleaks` classifica como `generic-api-key` o hash de blob registrado para `vibe-design/references/kit-e-tokens.md` (linhas 53 e 181 do commit), porque a chave do JSON contém "tokens". É falso positivo, mas o plan exige o workflow `contrato` verde, e qualquer input futuro com "token", "key" ou "secret" no nome repete a falha; o histórico não pode ser reescrito. - remédio: `vibe-implement` (corretor) adiciona `.gitleaks.toml` na raiz com `[extend] useDefault = true` e allowlist restrita a `.vibeflow/**/execution.json` para valores hexadecimais de 40 caracteres (ou, se o humano preferir o recorte mínimo, `.gitleaksignore` com os dois fingerprints), sem afrouxar as demais regras. - prova: `gitleaks detect --source . --redact --no-banner` verde localmente e job `segredos` verde no CI do commit da correção. - source: plan Regressão completa (CI obrigatório), C1 - gap: partial - papel: corretor

### Nit

- [x] R3: **Nit** - `vibe-review/SKILL.md:227` - O passo 2 da finalização manda comparar o estado atual "com o snapshot da review", mas no Modo A a review não grava snapshot: registra HEAD e resultado em "Provas executadas", e o `execution.json` guarda os snapshots das provas. O finalizador pode procurar um artefato inexistente. - remédio: `vibe-implement` (redator) qualifica o passo por protocolo: no `coordenacao-v1` A, comparar `git status` e o diff desde o HEAD registrado na última etapa da review; nos históricos, manter o snapshot registrado no plan. - prova: `py -3 docs/vibe-review/tests/test-review.py -v` e releitura do §5 contra o §3. - source: A19 - gap: partial - papel: redator

## Notas

- Auditoria (a): a re-review exige IDs de `task(Rn,...)` iguais aos R* marcados desde a etapa anterior, e o motor (`execution.py:181`) aceita subconjunto ordenado dos R* existentes. A regra da review é mais estrita e compatível: o motor é condição necessária e não contradiz o fluxo do corretor, que atende todos os R* da rodada.
- Auditoria (c): as gravidades acrescentadas em `coverage.md` §3 fora da lista da F5 (MEDIUM para `Regressão completa` duplicada, HIGH para `Prova afetada:` que deixa A*/C* sem prova, MEDIUM para paralelismo perdido relevante) são coerentes com a F5 e com a tabela geral; sem achado.
- Inputs fora do recorte: nenhum; todo input de `tasks.Tn.proof.inputs` está no `Arquivos:` da Tn (T1 sob os diretórios de perfis declarados; T6 inclui a cópia de `vibe-plan/references/delegation.md`, declarada).
- `execution.json` modificado na árvore é o residual previsto do registro do commit (`commit: null` para `8d1e6e5`), sem input provado alterado.

## Veredito vigente

- [ ] **Approve**: origem suficiente, obrigações atendidas ou retiradas explicitamente pelo humano e nenhum R* de correção em `[ ]`
- [x] **Request changes**: há R* de correção em `[ ]`

## Handoff

vibe-implement

- [ ] Aprovação humana (leu o arquivo e confirmou)

- Chat: no Modo A, o coordenador delega R1, R2 e R3 ao redator e R4 ao corretor, depois de levar ao humano a escolha de R2 e, se desejar, o recorte de R4. O `review.md` vivo e o diff são a ponte.

## Etapas

### Etapa 1 - first-pass - T1 a T9, diff `7cdc1b5..8d1e6e5`, regressão completa

- Tipo: final
- Marco e justificativa: integração final
- T* abertas fora do marco: nenhuma
- Provas reaproveitadas: `Prova afetada:` de T1 a T9 e união na integração (`execution.json`, inputs inalterados).
- Provas executadas:
  - Regressão completa do plan, uma vez, HEAD `8d1e6e5b9dff2d64375ad3c0ab13f1f8d8e78cd5`, árvore sem modificação fora de `.vibeflow/` antes e depois (somente o residual de `execution.json`). Verdes: `py -3` das suítes interview, spec, design, plan, analyze, review, `test-execution.py` (22, 2 skips), mvp-flow, reparse-safety, runtime-discovery e stream-encoding; launchers `bash docs/vibe-<skill>/tests/test-<skill>.sh` de interview, spec, design, plan, analyze, implement e review. Falhas somente nas exceções conhecidas deste host sem symlink: `test-init.py` (12 casos, 22 erros WinError 1314), `test-init.ps1` (`ponte-legada`), `test-implement.py` (69; `test_integration_snapshot_types_and_old_commit` e 2 skips), `test-distribuicao.py` (`test_skills_pointers` e `test_unique_names_under_skills`), `test-init.sh` (alias `skills/vibe-init` não é symlink). Falha real: `gitleaks detect --source . --redact --no-banner` com 2 achados `generic-api-key` em `execution.json` (R4).
  - CI `contrato`, run 38615291800, commit `8d1e6e5`: conclusão `failure`. Job `testes` `success` (suítes Python, paridade PowerShell e launchers, cobrindo as exceções locais de symlink); job `segredos` `failure` na varredura (R4).
  - `gitleaks detect --log-opts="7cdc1b5..HEAD"`: 2 achados, linhas 53 e 181 de `execution.json` no commit `8d1e6e5`, hash do blob de `vibe-design/references/kit-e-tokens.md`.
  - Jornada do init (A1, A2, A5, A3): `py -3 vibe-init/scripts/init.py --root <pasta isolada no scratchpad>`, saída 0; `AGENTS.md` gerado com a regra de erro fora do recorte (registrar e reportar, sem corrigir), SLOT de comandos com recorte, suíte, E2E, segredos, CI e onde roda, sem a regra de testes de skills do VibeFlow e com a seção Git em frases curtas; os doze perfis iguais em bytes aos templates. Pasta removida.
  - Excluído pelo plan: `docs/vibe-implement/tests/piloto-modo-a.py` (não determinístico, consome tokens, fora do CI).
- Execução: inputs por T* dentro dos `Arquivos:`; diff fora de `.vibeflow/` na união, exceto os dois arquivos novos em `.erros-encontrados/` (R1); consumidores compartilhados entre T1 a T8 (sem `Deps`) coerentes: lista de perfis igual em plan, analyze, implement e delegation; `papel` da review igual ao roteamento da implement; `Superfícies compartilhadas` e `Prova visual esperada` com o mesmo nome no design, no plan e na review; nível de Como provar consumido pelo plan; versão 9.0.0 igual em T8 e README (T9). Conflito de `AGENTS.md` entre T6 (contrato do redator) e T9 em R2.
- Leu: spec.md, plan.md, execution.json pelo motor da implement, diff da phase, motores de review, implement e init nos trechos usados, CI público do commit.
- Cobertura: matriz gravada; parciais em A10, A16, C1 e decisões 4 e 9.
- Abriu: R1, R2, R3, R4
- Fechou: nenhum
- Veredito desta etapa: Request changes

## Publicação autorizada pelo humano

- Data: 2026-10-14.
- Autorização (texto do humano): "já não ta tudo certo, acho que pode fazer commit/push, preciso dar andamento, atualiza minhas skills locais e afins, depois reviso"; confirmação direta: "confirmo as 5 ações".
- Commits publicados: 8d1e6e5 (T1 a T9), b1d8067 (R1 a R4 e remoção do CI do GitHub, decisão 18), a042604 (dispensa de falso positivo do gitleaks) e o commit residual desta seção.
- Re-review pendente: R1 a R4 estão marcados como corrigidos pelo finalizador, mas não foram confirmados por nova review. O humano revisará depois. Esta review não está aprovada.
- Registro de integração: ficou desatualizado apenas pelo `.gitleaksignore` (fingerprints de falso positivo commitados em a042604, depois do commit R*); nenhum código ou teste mudou. Revalidar na re-review.
