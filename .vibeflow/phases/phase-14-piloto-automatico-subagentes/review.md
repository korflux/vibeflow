# Review: Piloto automático de implementação com subagentes
# Alvo: phase-14-piloto-automatico-subagentes
# Status: request-changes

## Contexto

- Alvo: phase-14-piloto-automatico-subagentes (commits `dbcfea9..3e2cfef`, T1 a T6, 6 commits à frente de `origin/main`, sem push)
- Cadeia: interview.md / spec.md / plan.md / analyze.md (limpo, aprovado)
- O que muda: o motor do `vibe-implement` passa a informar `etapa` e `rodadas_correcao`; `vibe-implement` ganha o Modo A (piloto com subagentes) e o Modo B (uma T* por run); `vibe-plan` delega o analyze; `vibe-review` e `vibe-analyze` ganham o modo subagente; `references/delegation.md` idêntico em plan e implement; regra única de instalação; versão 4.0.0.

## Tipo de review

- Tipo: final
- Marco e justificativa: integração final. T1 a T6 estão `[x]` no plan; a T6 foi encerrada por dispensa do humano, sem a execução piloto (plan.md, T6, Prova e Decisões).
- T* abertas fora do marco: nenhuma
- Provas reaproveitadas: nenhuma. Nenhum código ou teste mudou desde as provas da T5 além do `piloto-modo-a.py` da T6, mas a matriz agregada foi reexecutada por cobrir a integração.
- Provas executadas: laço do plan (`test-init`, `interview`, `spec`, `design`, `plan`, `analyze`, `implement`, `review`) -> init 8, interview 19, spec 19, design 19, plan 16, analyze 16, implement 36 (inclui `PowershellParity` com `pwsh` 7), review 19, todos OK; `test-distribuicao.py` 9 OK; `test-mvp-flow.py` 1 OK; `test-reparse-safety.py` 12 OK; `gitleaks detect --source . --redact --no-banner` -> no leaks found (50 commits); `git diff --check` limpo; `piloto-modo-a.py --prepare-only` -> 6 conferências PASS, sem sobras na pasta temporária. Motor do implement lido contra reviews reais de phases anteriores (somente leitura, `git status` inalterado): ver R1.

## Cobertura

| Chave | Código | Notas |
|---|---|---|
| A1 | partial | `vibe-plan/SKILL.md` §7 e §8 e `templates/plan.md` (handoff `vibe-analyze` em phase max, delegação, perguntas no chat do plan); sem execução da rodada 0 |
| A2 | partial | `vibe-plan/SKILL.md` §8, `vibe-analyze/SKILL.md` §7 e templates (chat novo com ênfase, anúncio do Modo A); sem execução |
| A3 | partial | `vibe-implement/SKILL.md` §3 (ciclo da T*, commit `task(Tn)`, escritor único); T1 a T6 desta phase foram executadas uma por run, antes de o Modo A existir; sem execução do Modo A |
| A4 | partial | `vibe-implement/SKILL.md` §3 (passos R e C), `vibe-review/SKILL.md` §6; limite de 2 rodadas depende do contador, ver R1 |
| A5 | partial | `vibe-implement/SKILL.md` §6 (pergunta única, finalização, hashes, Critical corrigidos); sem execução |
| A6 | partial | `vibe-implement/SKILL.md` §2 (tabela de paradas, instalação, prova vermelha); sem execução |
| A7 | partial | motor informa a etapa (C1 ok) e `vibe-implement/SKILL.md` §3 descreve a retomada; sem sessão retomada |
| A8 | partial | `vibe-implement/SKILL.md` §1 (Modo B e fallback); `rg` confirma que o plano inteiro inline só aparece em registros de remoção (`docs/ESCOPO.md:117`, `docs/vibe-implement/ANALISE.md:55,73`) |
| A9 | ok | `cmp` idêntico; `docs/tests/test-distribuicao.py` (`DelegacaoContracts`) |
| A10 | partial | regra uniforme em `vibe-plan/SKILL.md` §3.3, `vibe-implement/SKILL.md` §2, `vibe-review/SKILL.md` §3.4, `vibe-analyze/SKILL.md` §3.5 e nas três referências; `rg` não acha proibição restante fora dessas; instalação real não executada |
| A11 | ok | docs das quatro skills, `AGENTS.md`, `docs/ESCOPO.md`, README; 4.0.0 nos cinco manifestos e em `CONTRACT_VERSION`; nenhuma ocorrência de 3.1.0 fora de `.vibeflow/` |
| C1 | ok | 18 fixtures de `ETAPA_CASES` nos dois motores, sem escrita em disco (`docs/vibe-implement/tests/test-implement.py`); contador com ressalva em R1 |
| C2 | ok | `test_check_fails_on_divergent_missing_or_empty_copies` cobre um byte, fim de linha, ausente e vazio |
| C3 | missing | `piloto-modo-a.py` existe e as fixtures são válidas, mas as rodadas 0 a 3 nunca rodaram (CLI sem login); dispensa do humano em 2026-10-03 |
| C4 | ok | todas as suítes de contrato verdes na execução desta etapa |

## Checklist de correções

### Required

- [x] R1: **Required** - `vibe-implement/scripts/implement.py:48` e `vibe-implement/scripts/implement.ps1:26` - `rodadas_correcao` só conta o veredito escrito exatamente como `Request changes` (ponto final opcional). Reviews reais variam: `.vibeflow/phases/phase-10-ux-detalhado-e-vibe-design/review.md:94` registra `**Request changes**. As inconsistências...` e o motor informa `rodadas_correcao = 0` para essa phase, cuja review teve uma etapa `Request changes`. O limite de 2 rodadas (A4, Never da spec) falha aberto: se o revisor escrever o veredito com negrito ou texto adicional, o coordenador não para na 2ª correção e a `etapa` `corrigir` com `rodadas_correcao` abaixo de 2 repete o ciclo sem teto. - remédio: `vibe-implement` torna o casamento tolerante nos dois motores, aceitando `Request changes` no início do valor, com marcação `**` ou `_` opcional antes e texto depois, sem casar a lista de alternativas do template (que começa com `Marco aprovado`); acrescentar fixtures `**Request changes**. texto` e `Request changes, R2 aberto` a `ETAPA_CASES` e atualizar a seção 3 de `docs/vibe-implement/ARQUITETURA.md` - prova: `python docs/vibe-implement/tests/test-implement.py -v` verde com as fixtures novas nos dois motores, e `python vibe-implement/scripts/implement.py --root . --dir phase-10-ux-detalhado-e-vibe-design` informando `rodadas_correcao` 1 - source: A4 - gap: partial - fechado: `REQUEST_CHANGES_RE` e `RequestChangesRe` casam por prefixo (`^[*_]*Request changes(?![^\W_])`) nos dois motores; 3 fixtures novas em `ETAPA_CASES` (negrito com texto, formatos variados com bloqueio aberto, menção no meio); `test-implement.py -v` -> 36 OK com a paridade PowerShell (antes do ajuste de `_` a fixture falhava nos dois motores) e `implement.py` e `implement.ps1` sobre a phase 10 informam `rodadas_correcao` 1

### Optional / Nit

- [ ] R2: **Optional** - `docs/vibe-implement/tests/piloto-modo-a.py` e `docs/vibe-implement/ARQUITETURA.md:113` - os fluxos delegados (A1 a A8, A10, C3) não têm prova comportamental: o piloto nunca foi executado além de `--prepare-only`, a CLI `claude` está sem login (`claude auth status` -> `loggedIn: false`) e o humano dispensou a execução em 2026-10-03. A severidade é Optional somente por essa dispensa registrada em `plan.md` T6 (Decisões); sem ela seria Required. O comando do piloto também não aparece na `ARQUITETURA.md`, então só o `plan.md` o aponta. - remédio: `claude auth login`, `python docs/vibe-implement/tests/piloto-modo-a.py --rounds 3` e depois `--rounds 0,1,2`; registrar a evidência sob a T6 e marcar A1 a A8, A10 e C3 na spec; acrescentar uma linha com o comando, o custo e a ausência do CI em `docs/vibe-implement/ARQUITETURA.md` §7 - prova: `summary.md` do piloto com todas as conferências PASS - source: C3 - gap: partial - parcial: o comando, o custo, a exigência de login e a ausência do CI entraram em `docs/vibe-implement/ARQUITETURA.md` §7; a execução do piloto segue pendente (CLI sem login), por dispensa do humano
- [x] R3: **Optional** - `vibe-implement/SKILL.md:66` e `vibe-implement/scripts/implement.py:380` - `concluida` tem precedência sobre a fila e o push. A `vibe-review` grava `# Status: aprovado` antes do commit residual e do push (`vibe-review/SKILL.md` §5, passo 1 e Finalização Git). Se o push falhar, como na phase 13 (`291cae9`), um chat novo com `/vibe-implement` lê `concluida` e a skill manda não executar nada, deixando os commits sem push; o mesmo ocorre se uma T* for acrescentada ao plan de uma phase aprovada. A spec F4 diz que a falha de push "mantém a phase aberta". - remédio: na linha `concluida` do §3, mandar conferir `git status -sb` e `git log @{u}..` e oferecer a retomada do push ou do commit residual pendente, e conferir se há T* aberta antes de declarar a phase finalizada - prova: leitura da linha `concluida` com a conferência de Git descrita - source: spec F4, F5 - gap: partial - fechado: linha `concluida` de `vibe-implement/SKILL.md` §3 e de `docs/vibe-implement/ARQUITETURA.md` manda conferir `git status -sb`, `git log @{u}..` e as T* abertas, retomar commit residual e push com confirmação e relatar T* aberta em plan aprovado
- [x] R4: **Nit** - `vibe-implement/references/delegation.md:40` e a cópia em `vibe-plan/references/delegation.md:40` - a lista do escritor único omite `review.md`, que a decisão 8 da spec (`spec.md:37`) inclui entre os arquivos só do coordenador; o texto só impede o corretor de editá-lo. Um implementador não é nomeado. - remédio: acrescentar `review.md` à lista e às duas exceções, nas duas cópias ao mesmo tempo - prova: `cmp` das duas cópias e `python docs/tests/test-distribuicao.py -v` - source: A9, decisão 8 - gap: partial - fechado: `review.md` entrou na lista do escritor único e o implementador na proibição de editá-lo, nas duas cópias de `delegation.md` (`cmp` idêntico, `test-distribuicao.py` 9 OK), em `docs/ESCOPO.md` e em `docs/vibe-implement/ARQUITETURA.md`

## Segurança

- Nada no que o diff tocou: o motor lê só arquivos da própria phase, sem entrada externa, shell ou rede. O `piloto-modo-a.py` usa `subprocess` sem shell, pasta temporária removida no `finally`, teto de custo por chamada e `bypassPermissions` atrás de `--confirmado-pelo-humano`; ele libera `Bash(git *)` e `Bash(python *)`, que aceitam comandos arbitrários, e o cabeçalho do script declara isso. Gitleaks sem achados.

## Notas

- A prosa das skills é o produto desta phase e a regra do repo proíbe teste textual; o código verificável (motores, paridade, distribuição, versão, commits por T*) está sólido. As conclusões sobre o Modo A, o analyze delegado, a retomada e o Modo B vêm de leitura cruzada com a spec, não de execução.
- Commits conferidos: um `task(Tn)` por T*, paths dentro de `Arquivos:` de cada T*, sem `Co-Authored-By`, sem travessão longo nas linhas adicionadas.
- Fora de escopo, registrados em `.erros-encontrados/`: stdout dos motores em codificações diferentes no Windows, `Approve com defer` sem regra no `vibe-review` e comentários órfãos em `docs/tests/test-distribuicao.py`.
- `analyze.md` e `interview.md` da phase seguem sem commit; entram no commit residual da finalização, junto do `review.md`.

## Veredito vigente

- [ ] **Approve**: nenhum Critical/Required em `[ ]`
- [x] **Request changes**: há Critical/Required em `[ ]` (R1)
- [ ] **Approve com defer**: <qual R* e por quê>

## Handoff

vibe-implement

- [ ] Aprovação humana (leu o arquivo e confirmou)

- Chat: recomende novo chat para a correção do R1; se o humano preferir continuar aqui, siga sem bloquear. O R2 pode ser deferido pelo humano sem bloquear o Approve, porque ele já dispensou a execução do piloto. O `review.md` vivo e o diff são a ponte.

## Etapas

### Etapa 1 - first-pass - T1 a T6, diff `dbcfea9..3e2cfef`, suítes de contrato, motor contra reviews reais

- Tipo: final
- Marco e justificativa: integração final, fila T1 a T6 concluída no plan
- T* abertas fora do marco: nenhuma
- Provas reaproveitadas: nenhuma
- Provas executadas: suítes das oito skills, distribuição, MVP, reparse, gitleaks, `git diff --check` e `piloto-modo-a.py --prepare-only`, todos verdes; motor do implement lido contra as reviews das phases 8, 10, 11 e 13, que revelou o R1
- Leu: plan.md sim
- Abriu: R1, R2, R3, R4
- Fechou: nenhum
- Veredito desta etapa: Request changes
