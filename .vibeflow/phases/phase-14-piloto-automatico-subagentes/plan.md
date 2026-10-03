# Plan: Piloto automático de implementação com subagentes
# Alvo: phase-14-piloto-automatico-subagentes
# Status: aprovado
# Spec: spec.md (mesma pasta)

## Overview

Entrega o Modo A do `vibe-implement` como piloto automático da phase (coordenador, implementador por T*, revisor, corretor e confirmação única), o Modo B como execução de uma T* por run e fallback, a delegação do analyze no chat do plan e a regra única de instalação de ferramentas, conforme `spec.md`. A base mecânica é a etapa da phase informada pelo motor do implement; a base de contrato é `references/delegation.md`, copiado de forma idêntica em `vibe-plan` e `vibe-implement`. A prova de ponta a ponta é uma execução piloto headless num repo descartável.
- **Design:** N/A, sem UI visível.

## Prontidão das provas

- **Requisitos verificados:** Python 3.13 e PowerShell 7.6 locais (CI usa Python 3.12 e pwsh em `.github/workflows/contrato.yml`); suítes `docs/vibe-*/tests/test-*.py` e `docs/tests/test-distribuicao.py` locais e no CI; `gitleaks` 8.30 local e no CI; Claude Code CLI 2.1 local, com `-p`, `--plugin-dir` e `--permission-mode`, para a execução piloto da T6.
- **Ausências e ação na fila:** nenhuma. A execução piloto da T6 consome tokens da conta do humano e roda só localmente; não entra no CI.

## Tasks

### T1: Motor do implement informa a etapa da phase e as rodadas de correção

- [x] T1 concluída
- **Spec:** A4, A7, C1; decisão 15
- **O quê:** o JSON de `implement.py` e `implement.ps1` ganha `etapa` e `rodadas_correcao`, derivados só de `plan.md` e `review.md` do alvo, sem alterar `alvo`, `fila`, `avisos` e `analyze_gate`.
- **Aceite:**
  - [x] `etapa` segue esta precedência: `concluida` (review `# Status: aprovado`), `corrigir` (há `- [ ] Rn: **Critical**` ou `**Required**` em aberto), `confirmar` (fila concluída, status ainda não aprovado e `- [x] **Approve**` ou `- [x] **Approve com defer**` marcado em Veredito vigente), `implementar` (há T* elegível), `bloqueada` (há T* aberta sem elegível), `revisar` (fila concluída sem veredito final de aprovação, inclusive depois de bloqueios fechados).
  - [x] `rodadas_correcao` conta as correções já aplicadas, não as reviews que pediram mudança: cada etapa cuja linha `- Veredito desta etapa: Request changes` tem o valor exato (a lista de alternativas do template não conta) soma 1, exceto a última etapa quando ainda há Critical ou Required em `[ ]`, cuja correção está pendente. Sem `review.md`, vale 0. O coordenador para quando `etapa` é `corrigir` e `rodadas_correcao` já é 2.
  - [x] Sem `plan.md` ou com fila ilegível, `etapa` é `null`; `review.md` existente sem `# Status:` gera aviso e não inventa etapa.
  - [x] Os dois motores produzem os mesmos valores para as mesmas fixtures; nenhum motor escreve arquivo para calcular a etapa.
- **Verificação:**
  - [x] `python docs/vibe-implement/tests/test-implement.py -v` (inclui as fixtures de C1 na classe de paridade PowerShell)
  - [x] `bash docs/vibe-implement/tests/test-implement.sh`
- **Deps:** nenhuma
- **Prova:**
  - `python docs/vibe-implement/tests/test-implement.py -v` -> Ran 36 tests, OK (28,8s; inclui `PowershellParity` com `pwsh` 7, 18 fixtures de etapa em cada motor)
  - `bash docs/vibe-implement/tests/test-implement.sh` -> pass=8 fail=0
  - Regressão: `docs/tests/test-mvp-flow.py` (1 OK), `docs/tests/test-reparse-safety.py` (12 OK), `docs/tests/test-distribuicao.py` (7 OK); `git diff --check` sem achados
- **Arquivos:** `vibe-implement/scripts/implement.py`, `vibe-implement/scripts/implement.ps1`, `docs/vibe-implement/tests/test-implement.py`, `docs/vibe-implement/ARQUITETURA.md`
- **Risco:** campo novo no relatório é contrato público (minor isolado, absorvido pelo major da phase); fixtures de paridade PowerShell são puladas quando `pwsh` falta, como hoje.
- **Decisões:** spec 15 implementada. `etapa` também é `null` com T* sem linha `concluída` no plan, porque ela some da fila e a conclusão ficaria falsa; `Request changes.` com ponto final conta como o valor exato, pois reviews reais o escrevem assim; a paridade compara a contagem de avisos, não o texto, por causa de `.erros-encontrados/2026-10-03-motores-stdout-codificacao-divergente.md`

### T2: Contrato de delegação distribuído em plan e implement

- [x] T2 concluída
- **Spec:** A9, C2; decisões 1, 6, 7, 8
- **O quê:** `references/delegation.md` idêntico em `vibe-plan` e `vibe-implement`, com papéis por perfil (explorador, verificador, implementador/corretor, revisor), quando delegar e quando não, formato fixo do relatório de subagente (`verde | bloqueado | pergunta`, paths, prova, pendências, pergunta), escritor único, proibições herdadas, conferência do relatório pelo coordenador e fallback inline sem subagentes ou sem aninhamento. Sem nome de modelo.
- **Aceite:**
  - [x] As duas cópias têm os mesmos bytes.
  - [x] O teste de distribuição falha com cópias divergentes e passa com cópias idênticas.
- **Verificação:**
  - [x] `python docs/tests/test-distribuicao.py -v`
- **Deps:** nenhuma
- **Prova:**
  - `python docs/tests/test-distribuicao.py -v` -> Ran 9 tests, OK; `DelegacaoContracts` compara bytes, e o caso divergente, de fim de linha, ausente e vazio roda em pasta temporária removida no tearDown
  - Controle negativo nos arquivos reais: um byte a mais em `vibe-plan/references/delegation.md` fez `test_repo_copies_are_identical` falhar; restaurado com `cp`, `cmp` idêntico e suíte verde
  - Regressão: suítes de plan (16), implement (36), analyze (16) e review (19), `test-mvp-flow.py` e `test-reparse-safety.py` OK; `gitleaks detect --source . --redact --no-banner` sem achados; `git diff --check` limpo
- **Arquivos:** `vibe-plan/references/delegation.md`, `vibe-implement/references/delegation.md`, `docs/tests/test-distribuicao.py`
- **Risco:** o teste compara bytes, nunca texto; precisa usar pasta isolada para o caso divergente e removê-la no tearDown.

### T3: Modo A como piloto da phase e Modo B como fallback no implement

- [x] T3 concluída
- **Spec:** A3, A4, A5, A6, A7, A8, A10; decisões 4, 5, 9, 10, 11, 12, 13, 14, 16
- **O quê:** `vibe-implement/SKILL.md` passa a ter: seleção de modo (Modo A padrão com subagentes; Modo B por pedido, T* nomeada ou falta de subagentes, com aviso de uma linha); coordenação do Modo A guiada pela `etapa` do motor (delegar T*, conferir, registrar, commitar, revisar, corrigir até 2 rodadas, confirmar); pergunta única final com relatório de T*s, hashes, rodadas, Critical corrigidos e decisões; execução da finalização da `vibe-review` após confirmação; tabela de paradas; regra de instalação; prova vermelha sem enfraquecer teste; retomada pela etapa e checkpoint; Modo B com o comportamento atual de uma T* e grupo paralelo; remoção do antigo plano inteiro inline. `vibe-review/SKILL.md` ganha o modo subagente revisor (grava a etapa, devolve relatório e perguntas, não finaliza Git nem sincroniza `AGENTS.md`) e a regra de instalação na prova visual; as três referências que hoje proíbem instalar (`vibe-implement/references/chrome-devtools.md`, `vibe-review/references/ui-visual-quality.md` e `vibe-design/references/kit-e-tokens.md`) passam a apontar a regra única da decisão 13, mantendo a seleção navegador integrado, `chrome-devtools` e Playwright. `ARQUITETURA.md` e `ANALISE.md` de implement e review refletem o contrato.
- **Aceite:**
  - [x] Nenhuma referência ao antigo Modo B de plano inteiro inline permanece nas skills e docs de implement.
  - [x] O contrato de commit (`task(Tn)`, staging explícito, sem push) e os códigos de erro dos motores permanecem iguais.
  - [x] Nenhum arquivo de implement, review ou das referências de prova visual proíbe instalar ferramenta necessária à prova fora das exceções da decisão 13.
  - [x] Suítes de implement e review continuam verdes.
- **Verificação:**
  - [x] `python docs/vibe-implement/tests/test-implement.py -v`
  - [x] `python docs/vibe-review/tests/test-review.py -v`
- **Deps:** T1, T2
- **Prova:**
  - `python docs/vibe-implement/tests/test-implement.py -v` -> Ran 36 tests, OK; `python docs/vibe-review/tests/test-review.py -v` -> Ran 19 tests, OK; `test-implement.sh` pass=8 e `test-review.sh` pass=7
  - Regressão: design (19), plan (16), analyze (16), spec (19), interview (19), init (8), `test-distribuicao.py` (9), `test-mvp-flow.py` e `test-reparse-safety.py` OK; `git diff --check` sem achados
  - Conferência por leitura e `grep`, sem teste textual por regra do repo: nenhum arquivo de implement, review, design ou das três referências proíbe instalar fora da decisão 13; nenhuma instrução do antigo modo de plano inteiro inline permanece, restando só a linha da tabela de Cortes e um parágrafo em `docs/vibe-implement/ANALISE.md` que registram a remoção; motores, códigos de erro e o formato `task(Tn)` não foram tocados nesta T*
  - Nenhum A*/C* marcado na spec por esta T*: A3 a A8 só são provados pela execução piloto da T6, e A10 ainda depende da T4
- **Arquivos:** `vibe-implement/SKILL.md`, `vibe-review/SKILL.md`, `vibe-review/templates/review.md` (campo do relatório do revisor e linha de Chat, que hoje exige chat novo), `vibe-implement/references/chrome-devtools.md`, `vibe-review/references/ui-visual-quality.md`, `vibe-design/references/kit-e-tokens.md`, `docs/vibe-implement/ARQUITETURA.md`, `docs/vibe-implement/ANALISE.md`, `docs/vibe-review/ARQUITETURA.md`, `docs/vibe-review/ANALISE.md`
- **Risco:** prosa de skill não tem teste textual; a prova comportamental é a T6.
- **Decisões:** commit de correção do Modo A no formato `task(Rn): <outcome>`, como já usado em `task(R4)` na phase 13; o Modo A não executa checkpoints de review declarados no plan, porque o motor não deriva marcos e a re-review parcial não tem etapa própria (registrado em `ARQUITETURA.md` e nos Cortes de `ANALISE.md`); o relatório do revisor acrescenta `veredito`, `abertos`, `fechados`, `critical_encontrados` e `decisoes_vigencia` e o template de review não ganhou campo novo, pois R*, etapas e a tabela de decisões já são o registro e perguntas não podem ficar no arquivo; a instalação de ferramenta pela review não altera manifesto nem lockfile, para respeitar a regra de que a review não edita lockfile

### T4: Analyze delegado, handoff forte para o implement e instalação no plan

- [x] T4 concluída
- **Spec:** A1, A2, A10; decisões 3, 13, 17
- **O quê:** `vibe-plan/SKILL.md` passa a: apontar `vibe-analyze` no handoff de MVP e de phase max; delegar o analyze a subagente quando o host oferecer, conduzir clarificações e aprovação no próprio chat e manter o fallback atual; fechar recomendando com ênfase um chat novo com `/vibe-implement` em Modo A; trocar a proibição de instalar (passo 3.3) pela regra única; ajustar a frase de paralelizáveis para valer só no Modo B. `vibe-plan/templates/plan.md` acompanha o handoff. `vibe-analyze/SKILL.md` ganha o modo subagente (devolve veredito, correções e perguntas) e o fechamento com a mesma recomendação de chat novo em Modo A; `vibe-analyze/templates/analyze.md` troca a linha de Chat que hoje manda abrir o analyze em chat novo. `ARQUITETURA.md` e `ANALISE.md` de plan e analyze refletem o contrato.
- **Aceite:**
  - [x] O handoff de phase max no plan aponta `vibe-analyze`.
  - [x] Nenhum arquivo de plan ou analyze (SKILL, template e docs) proíbe instalar ferramenta necessária à prova fora das exceções da decisão 13; as referências de implement, review e design são da T3.
  - [x] Suítes de plan e analyze continuam verdes.
- **Verificação:**
  - [x] `python docs/vibe-plan/tests/test-plan.py -v`
  - [x] `python docs/vibe-analyze/tests/test-analyze.py -v`
- **Deps:** T2
- **Prova:**
  - `python docs/vibe-plan/tests/test-plan.py -v` -> Ran 16 tests, OK; `python docs/vibe-analyze/tests/test-analyze.py -v` -> Ran 16 tests, OK; `test-plan.sh` pass=6 e `test-analyze.sh` pass=7
  - Regressão: implement (36), review (19), design (19), spec (19), interview (19), init (8), `test-distribuicao.py` (9, inclui as cópias idênticas de `delegation.md`), `test-mvp-flow.py` e `test-reparse-safety.py` OK; `git diff --check` sem achados
  - Conferência por leitura e `grep`, sem teste textual por regra do repo: nenhum arquivo de plan ou analyze (SKILL, templates, referências e docs) proíbe instalar fora da decisão 13; o handoff de phase max no plan (SKILL §8 e template) aponta `vibe-analyze`; nenhum motor foi tocado nesta T*
  - Nenhum A* marcado na spec por esta T*: A1 e A2 só são provados pela rodada 0 da T6 e A10 pela execução piloto
- **Arquivos:** `vibe-plan/SKILL.md`, `vibe-plan/templates/plan.md`, `vibe-analyze/SKILL.md`, `vibe-analyze/templates/analyze.md`, `docs/vibe-plan/ARQUITETURA.md`, `docs/vibe-plan/ANALISE.md`, `docs/vibe-analyze/ARQUITETURA.md`, `docs/vibe-analyze/ANALISE.md`
- **Decisões:** o subagente de analyze mantém `# Status: rascunho` e grava o veredito `bloqueado` enquanto houver pergunta bloqueante pendente; o chat do plan aplica as respostas, registra as Clarificações, atualiza o veredito para `limpo` e marca a aprovação quando o humano aprova; a linha de instalação do `vibe-analyze` (§3.5), que era permissiva mas divergia da regra, foi alinhada à regra única; o `vibe-plan` ganhou a nova §7 (analyze delegado) e o Fechar passou a §8; o checkpoint de review do plan vale só quando o humano conduz a review à parte, pois o Modo A não o executa (decisão da T3)

### T5: Regras do repo, escopo e versão major

- [ ] T5 concluída
- **Spec:** A11, C4; decisão 18
- **O quê:** tabela "Continuidade entre chats" do `AGENTS.md` deste repo documenta delegação de analyze e review, Modo A e Modo B, a frase de grupo paralelo passa a valer só no Modo B e a linha de Git registra que, no Modo A, o coordenador executa a finalização da `vibe-review` após a confirmação humana; `docs/ESCOPO.md` marca o que esta phase entregou e registra a phase de paralelismo como pendente; `README.md` cita os modos em uma linha se já descrever o implement e atualiza a linha de versão dos manifests; versão 4.0.0 nos cinco manifestos versionáveis e em `CONTRACT_VERSION` de `docs/tests/test-distribuicao.py`, que hoje fixa `3.1.0`.
- **Aceite:**
  - [ ] Os cinco manifestos versionáveis e `CONTRACT_VERSION` declaram 4.0.0; o `plugin.json` da raiz (Antigravity) continua sem campo de versão.
  - [ ] Todas as suítes de contrato, de distribuição, de MVP e de reparse passam.
  - [ ] `gitleaks detect --source . --redact --no-banner` sem achados.
- **Verificação:**
  - [ ] `python docs/tests/test-distribuicao.py -v`
  - [ ] `for s in init interview spec design plan analyze implement review; do python docs/vibe-$s/tests/test-$s.py || exit 1; done; python docs/tests/test-mvp-flow.py && python docs/tests/test-reparse-safety.py`
  - [ ] `gitleaks detect --source . --redact --no-banner`
- **Deps:** T3, T4
- **Arquivos:** `AGENTS.md`, `docs/ESCOPO.md`, `README.md`, `docs/tests/test-distribuicao.py`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `.grok-plugin/marketplace.json`

### T6: Execução piloto do Modo A num repo descartável

- [ ] T6 concluída
- **Spec:** A1–A8, A10, C3
- **O quê:** um gerador de fixture cria, numa pasta temporária fora do repo, um projeto Git mínimo já inicializado com `.vibeflow/` e uma phase max com spec, plan aprovado de 3 T*s e analyze aprovado e limpo, em que a prova de uma T* começa vermelha por defeito real e um requisito de prova está ausente mas instalável sem credencial; e um remoto bare local para o push. A execução usa `claude -p --plugin-dir <repo>` na pasta temporária. Rodada 0 (A1 e A2): fixture separada com plan aprovado, sem `analyze.md` e com um achado determinístico plantado no plan; sessão no papel do chat do plan, com o pedido da próxima porta; o teste afirma `analyze.md` gravado e o achado corrigido no `plan.md`, e o transcript do fechamento (recomendação de chat novo e anúncio do Modo A) é registrado como evidência. Rodada 1: `/vibe-implement` até a pergunta final, depois confirmação em nova chamada da mesma sessão. Rodada 2: fixture nova, execução interrompida após a primeira T* e retomada em sessão nova. A evidência (commits, `plan.md`, `review.md`, trechos do transcript, número de perguntas ao humano) é registrada sob esta T*; a pasta temporária é removida ao final.
- **Aceite:**
  - [ ] Rodada 0: o analyze é delegado e gravado em subagente, o achado plantado é corrigido no plan e o fechamento recomenda chat novo com Modo A.
  - [ ] Rodada 1: um commit `task(Tn)` por T*, review em subagente, no máximo 2 rodadas de correção, uma única pergunta ao humano antes do push e push registrado no remoto local.
  - [ ] A prova vermelha é corrigida sem pergunta e sem asserção enfraquecida; o requisito ausente é instalado e registrado.
  - [ ] Rodada 2: a sessão nova retoma pela etapa do motor sem novo commit para a T* já concluída.
  - [ ] Pedido explícito de uma T* por vez conclui só uma T* (Modo B).
- **Verificação:**
  - [ ] `python docs/vibe-implement/tests/piloto-modo-a.py` (prepara a fixture, executa as rodadas com `claude -p` e afirma commits, etapa final do motor, contagem de perguntas e limpeza)
- **Deps:** T3, T4
- **Arquivos:** `docs/vibe-implement/tests/piloto-modo-a.py`
- **Risco:** execução não determinística e com custo de tokens; não entra no CI. O modo de permissão do `claude -p` não confina o agente à pasta temporária: preferir o menor modo que a fixture permita, com `--allowedTools` para Git, Python e o gerenciador de pacotes da fixture, e confirmar o modo com o humano antes da primeira execução. Falha do piloto por comportamento da skill volta para T3 ou T4 como correção, não para o script do piloto.

## Handoff

vibe-analyze
rota: max

- Chat: recomende novo chat para `vibe-analyze`; ele valida a coerência entre interview, spec e plan antes do código. Recomende um chat por T* em sequência, porque o Modo A ainda não existe enquanto esta phase não for implementada; o humano pode continuar no chat atual e o `plan.md` vivo é a ponte.
