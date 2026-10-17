# Analyze: VibeFlow V2, skill única com coordenador-líder
# Alvo: phase-21-vibeflow-v2-lider-unico
# Status: aprovado
# Plan: plan.md (mesma pasta)

## Fontes

| Arquivo | Estado |
|---|---|
| interview.md | presente, aprovado |
| spec.md | presente, aprovado (correções diretas F4 e F5 e resposta de F8 aplicadas nesta análise) |
| design.md | N/A sem UI visível (spec Handoff e plan Overview) |
| plan.md | presente, aprovado, `# Protocolo: coordenacao-v1` (correções diretas F1, F2, F3, F6, F7 e F9 e resposta de F8 aplicadas nesta análise) |
| AGENTS.md | lido |

Evidências mecânicas consultadas: motor da implement v1 em leitura (`implement.py --dir phase-21-vibeflow-v2-lider-unico`) com `fila.parse = ok`, elegível T1 e Deps coerentes; `plan_wave` do mesmo motor sobre os conjuntos {T2,T6}, {T3,T4}, {T3,T4,T6}, {T4,T6} e {T7,T8}, todos disjuntos e sem T* em `sem_arquivos`; prontidão conferida no host (Python 3.13.14, PowerShell 7.6.6, bash 5.3.15, gitleaks 8.30.1, criação de symlink por Python confirmada em pasta isolada); perfis explorador, implementador, verificador, corretor, revisor e redator disponíveis no host, além de agente genérico.

## Cobertura e Rastreabilidade

### Interview → spec

| Origem (interview) | Destino na spec | Situação |
|---|---|---|
| Skill única `vibeflow` no lugar das 8 `vibe-*`, major na branch `v2` | Objetivo, decisões 1 e 10, F1, F9, A12 | coberto |
| Essência do líder (briefing, macro, delegar, criticar, reconhecer, decidir) | Decisões 3 a 6, F3, F5, A7 | coberto |
| Decisão 1: analyze e review por visão de fora | Decisão 7, F4, A6, Never | coberto |
| Decisão 2: host sem subagentes degradado com aviso | Decisão 8, F8, A11 | coberto; C2 e Never ajustados (F5) |
| Decisão 3: contrato de disco mantido; `execution.json` desde a interview | F3, F10, A5, A13, Contratos | coberto |
| Decisão 4: líder num chat; dois chats em contexto curto | Decisão 4, F6, A9 | coberto |
| Decisão 5: `plan.md` sempre atualizado, inclusive na interrupção | F5, F6, A8, A9 | coberto |
| Decisão 6: init como etapa 0 com recarga do host | F2, A3 | coberto; a spec restringe a recarga a perfis criados ou alterados, refinamento compatível |
| Decisão 7: `/vibeflow` com etapa opcional, sem aliases | F1, F7, A1, A10, Fora | coberto |
| Sucesso: rota max sem perda, líder fora do micro, motores sem duplicação, phases antigas retomáveis | C1 a C5 | coberto |
| Sucesso: eficiência no mínimo igual à v1, medida pelo humano | C6, decisão 2 | coberto, jornada humana |
| Limite: testes só de motores e efeitos no disco | Boundaries Always e Never | coberto |
| Fora: fragmentos de instrução, worktree por T*, fan-out da review, benchmark | Fora | coberto |
| Visual N/A | Design N/A | coberto |

### Spec → plan

| Chave | Origem | T* | Notas |
|---|---|---|---|
| A1 | spec.md | T1, T2, T6 | etapa derivada pelo motor (T2) e roteamento do líder (T6) |
| A2 | spec.md | T2, T6 | T2 aceite cobre leitura sem `.vibeflow/` e sem relatório (F2, F4) |
| A3 | spec.md | T1, T4 | |
| A4 | spec.md | T6 | jornada (Overview); papel do redator alinhado em T6 (F6) |
| A5 | spec.md | T1, T3 | |
| A6 | spec.md | T6 | jornada |
| A7 | spec.md | T6 | jornada |
| A8 | spec.md | T3, T6 | |
| A9 | spec.md | T3, T6 | |
| A10 | spec.md | T1, T2, T3 | gates por rota em T2; gravação da rota em T3 (F8 resolvido) |
| A11 | spec.md | T6 | jornada |
| A12 | spec.md | T1, T7, T8 | |
| A13 | spec.md | T1, T2, T3 | |
| C1 | spec.md | T8 | jornada; T8 só documenta, evidência na primeira phase real |
| C2 | spec.md | T6 | jornada; escopo por host ajustado (F5) |
| C3 | spec.md | T1, T2, T5 | |
| C4 | spec.md | T1, T5 | |
| C5 | spec.md | T2 | |
| C6 | spec.md | nenhuma | avaliação humana no uso, justificada no Overview do plan |

### Plan → spec

Nenhuma T* entrega item de Fora. T6 (cópia única das referências duplicadas) e T7 (remoção de `docs/vibe-*` e adaptação do piloto E2E) decorrem da decisão 10 e de C3; o piloto continua fora da `Regressão completa`, como já era na v1. Os módulos `nucleo`, `etapa`, `fila`, `execution` e `governanca` são paths internos do pacote `vibeflow/` previsto em Contratos.

## Achados e Resoluções

| ID | Categoria | Gravidade | Onde | Problema | Resolução Aplicada |
|---|---|---|---|---|---|
| F1 | qualidade_teste | HIGH | plan.md | `P-DIFF` (`git diff --check -- <arquivos>`) sai verde sem checar arquivo não rastreado; T1 e T6 só criam arquivos novos | `P-DIFF` redefinido: rastreado com `git diff --check`, novo com `git diff --no-index --check -- /dev/null <arquivo>`, verde por saída sem achado |
| F2 | qualidade_teste | HIGH | plan.md | T2 aceite não cobria os invariantes de Contratos da spec que as suítes v1 removidas pela T7 provam hoje | Aceite de T2 ampliado com `n`, slug, `FASE_EXISTE`, `--dir`, reparse point, preservação byte a byte, MVP único, códigos por etapa, stderr, `.gitignore` e leitura sem relatório |
| F3 | furo | MEDIUM | plan.md | T3 aceite omitia o contrato de segurança "`--command` nunca executado" e as validações atuais do registro | Aceite de T3 ampliado |
| F4 | inconsistencia | MEDIUM | spec.md | Relatório fixo em `.vibeflow/vibeflow-report.json` contradiz A2 (leitura sem `.vibeflow/` não pode criá-lo) | Contratos: sem `.vibeflow/`, a leitura não grava relatório nem cria a pasta e entrega o JSON pelo stdout |
| F5 | inconsistencia | MEDIUM | spec.md | C2, decisão 3 e Never proibiam o líder de escrever código e Git em qualquer host, contra F8 (Modo B inline) | C2, decisão 3 e Never passam a valer em host com subagentes; `analyze.md` e `review.md` seguem proibidos ao líder em qualquer host |
| F6 | inconsistencia | MEDIUM | plan.md | `delegation.md` v1 proíbe o redator de gravar `plan.md` e `spec.md`, mas F3 entrega ao redator `interview.md`, `spec.md`, `design.md` e `plan.md` | T6 alinha a tabela de papéis da cópia única de `delegation.md` a F3 e F4 |
| F7 | inconsistencia | MEDIUM | plan.md | Templates de artefato, de `AGENTS.md` e de perfis citam `/vibe-*`; T4 e T6 só os moviam, contra a decisão 10 | T4 e T6 adaptam a prosa para `/vibeflow`, com a continuidade de F6 no template de `AGENTS.md` |
| F8 | furo | HIGH | spec.md, plan.md | F7 e A10 pedem ao motor gates dependentes de rota ("implement high+ sem plan", "max exige analyze limpo"), mas nenhum artefato diz de onde o motor obtém a rota; o motor v1 só aplica o gate de analyze no MVP | Resolvido pelo humano: rota classificada pela IA e gravada pelo motor no `execution.json`; spec decisão 12, F7 e Contratos; plan T1, T2 e T3 |
| F9 | qualidade_teste | MEDIUM | plan.md | `gitleaks` da Regressão completa tende a repetir o falso positivo da phase 20 (hash no `execution.json` para path com `token`), sem destino previsto | Prontidão registra o risco e o destino: R* da review com fingerprint proposto, sem dispensa automática |

### F1: `P-DIFF` vazio para arquivo novo

- **Gravidade:** HIGH
- **Categoria:** qualidade_teste
- **Onde:** `plan.md`, Prontidão das provas
- **Evidência:** em repo isolado, `git diff --check -- d/novo.md` com espaço final em arquivo não rastreado saiu com exit 0 e sem saída; `git diff --no-index --check -- /dev/null d/novo.md` apontou o achado (exit 3) e saiu limpo (exit 1, sem saída) para arquivo correto, também com CRLF e em PowerShell. T1 cria `docs/vibeflow/ARQUITETURA.md` e `ANALISE.md`; T6 cria todo `vibeflow/SKILL.md`, `references/` e templates.
- **Resolução:** definição de `P-DIFF` reescrita na prontidão, sem tocar o índice. T8 continua com `git diff --check` porque altera arquivos rastreados.

### F2: invariantes de risco sem aceite em T2

- **Gravidade:** HIGH
- **Categoria:** qualidade_teste
- **Onde:** `plan.md`, T2 Aceite
- **Evidência:** Contratos da spec exigem `n` pelo motor, slug sanitizado de 2 a 48, `--dir` restrito, recusa de reparse point, preservação byte a byte, um MVP por repo e erro `CODIGO: mensagem`; F3 preserva os códigos atuais de cada etapa (`SPEC_JA_PLANEJADA`, `FASE_EXISTE`, `SLUG_INVALIDO` e outros). As suítes `docs/vibe-{interview,spec,design,plan,analyze,review}/tests/` que provam isso hoje são removidas por T7, e AGENTS.md §9 exige um caso por invariante de risco.
- **Resolução:** Aceite de T2 lista esses invariantes nos mesmos cenários das suítes v1. `Prova afetada:` de T2 não muda: `test-nucleo.py` e `test-etapa.py` são os módulos tocados.

### F3: segurança do registro sem aceite em T3

- **Gravidade:** MEDIUM
- **Categoria:** furo
- **Onde:** `plan.md`, T3 Aceite
- **Evidência:** Contratos da spec: "`--command` recebido pelo registro nunca é executado". O `execution.py` v1 já valida paths, tamanho e schema.
- **Resolução:** Aceite de T3 inclui `--command` como dado e as validações atuais com `EXECUTION_INVALIDO`.

### F4: relatório contra A2

- **Gravidade:** MEDIUM
- **Categoria:** inconsistencia
- **Onde:** `spec.md`, Contratos e restrições necessárias
- **Evidência:** F1 passo 1 exige relatório de leitura também sem init (estado "sem init"); A2 proíbe criar `.vibeflow/`. Gravar `.vibeflow/vibeflow-report.json` nesse estado é impossível sem violar A2.
- **Resolução:** frase acrescentada em Contratos. A forma exata do stdout nos demais estados fica para T1 (`ARQUITETURA.md`).

### F5: escopo de C2 e Never em host sem subagentes

- **Gravidade:** MEDIUM
- **Categoria:** inconsistencia
- **Onde:** `spec.md`, decisão 3, C2 e Boundaries Never
- **Evidência:** interview decisão 2 e F8 definem Modo B inline, com o próprio chat executando código e Git; C2 e Never proibiam isso sem ressalva.
- **Resolução:** ressalva "em host com subagentes; sem subagentes vale F8" aplicada; a proibição de o líder escrever `analyze.md` e `review.md` ficou explícita para qualquer host.

### F6: papel do redator em `delegation.md`

- **Gravidade:** MEDIUM
- **Categoria:** inconsistencia
- **Onde:** `plan.md`, T6 O quê e Aceite
- **Evidência:** `vibe-plan/references/delegation.md`, linha do redator: "nunca código de motor, testes, plan.md, spec.md nem review.md"; spec F3 passos 1 a 3 e decisão 4 entregam esses artefatos ao redator.
- **Resolução:** T6 ajusta a tabela de papéis da cópia única; revisor mantém exclusividade de `analyze.md` e `review.md`.

### F7: templates com `/vibe-*`

- **Gravidade:** MEDIUM
- **Categoria:** inconsistencia
- **Onde:** `plan.md`, T4 e T6
- **Evidência:** `vibe-*/templates/*.md`, `vibe-init/templates/AGENTS.md` e `vibe-init/templates/agents/{claude,codex}/*` citam `vibe-*`; T4 e T6 apenas moviam os templates "sem mudar a forma", e o `AGENTS.md` gerado em outros repos continuaria instruindo comandos removidos pela decisão 10.
- **Resolução:** T4 e T6 adaptam a prosa e mantêm as seções que os motores leem (`# Status`, `## Veredito`, linhas de T*). A conferência desse aceite é semântica pelo verificador e pela review; não cabe teste de presença de texto.

### F8: origem da rota para os gates do motor

- **Gravidade:** HIGH
- **Categoria:** furo
- **Onde:** `spec.md` F7 e A10; `plan.md` T1 a T3
- **Evidência:** F7 Validações listam "implement high+ sem plan bloqueia" e "max exige analyze limpo" como pré-requisitos que o motor recusa com `ETAPA_BLOQUEADA`. O motor v1 (`implement.py`, `analyze_gate`) só bloqueia por analyze no MVP; nas phases, a rota é decisão da IA e não está em disco. Sem a origem da rota, T1 não fecha o schema e T2 não consegue escrever o caso de teste de A10 para max e high.
- **Resolução:** resposta do humano aplicada (ver Clarificações). Spec: decisão 12, Validações de F7, Dados e invariantes e Segurança e operação de Contratos. Plan: T1 fixa o campo de rota, a allowlist e os gates no schema; T2 aplica os gates por rota em `etapa.py`, com o caso v1 sem rota; T3 grava a rota validada pelo `execution.py`, que passa a ser o único leitor do registro (C3).

### F9: falso positivo previsível do gitleaks

- **Gravidade:** MEDIUM
- **Categoria:** qualidade_teste
- **Onde:** `plan.md`, Prontidão das provas
- **Evidência:** `.gitleaksignore` dispensa três achados `generic-api-key` em `execution.json` da phase 20 pelo hash de `vibe-design/references/kit-e-tokens.md`; T6 move esse arquivo para `vibeflow/references/` e o `execution.json` da phase 21 registrará inputs com o mesmo padrão, em commits novos.
- **Resolução:** risco e destino registrados na linha do gitleaks; dispensa continua sendo decisão da review e do humano, sem `.gitleaksignore` em `Arquivos:` de nenhuma T*.

## Clarificações com o Usuário

- Q (F8): de onde o motor obtém a rota para aplicar os gates de F7? -> A: o humano aceitou a recomendação: "ok, a IA escolhe a rota e registra no execution.json; o motor aplica os bloqueios". (aplicado em spec.md, decisão 12, F7 e Contratos, e em plan.md, T1, T2 e T3). Recomendação apresentada: o líder informa a rota classificada e o motor a registra no `execution.json` na abertura da phase, validada contra a allowlist (Express, low, medium, high, xhigh, max, MVP); o motor recusa com `ETAPA_BLOQUEADA` implement sem plan aprovado em high ou acima e implement sem analyze aprovado e limpo em max e MVP; phase v1 sem rota registrada mantém o gate v1. Alternativa: manter o comportamento v1 e retirar de F7 os gates dependentes de rota, que voltam a ser aplicados só pelo líder.

## Métricas

- A*/C* na spec: 19 (A1 a A13, C1 a C6)
- T* no plan: 8
- Cobertura (A*/C* com >= 1 T*): 18 de 19; C6 é jornada humana justificada no Overview
- Qualidade de Testes: `Prova afetada:` restrita ao recorte em todas as T*; T2, T3, T4, T5 e T7 com suítes do módulo tocado; T1 e T6 com `P-DIFF` corrigido para arquivo novo (F1); T8 com `P-DIFF` e o consumidor de distribuição; smoke do ponto de entrada em T2 (`vibeflow.py`) e T5 (`vibeflow.ps1`, `vibeflow.sh`); `Regressão completa` única, com piloto E2E fora e justificado; ferramentas conferidas no host
- Contrato da implement: `coordenacao-v1`; `Arquivos:` em uma linha, entre crases e comparáveis em T1 a T8; nenhuma sobreposição entre T* sem `Deps` (T2 e T3 compartilham `etapa.py` e `test-etapa.py` com `Deps: T2`); prontidão com local e destino por requisito, perfis do Modo A e agente genérico para o finalizador verificados
- Achados corrigidos / resolvidos: 9 de 9 (F1 a F7 e F9 por correção direta; F8 pela resposta do humano)
- Achados bloqueantes pendentes: 0

## Veredito

limpo

Todos os achados foram corrigidos ou resolvidos; a aprovação deste arquivo continua com o humano.

## Handoff

vibe-implement
rota: max

- Chat: com subagentes, o `vibe-analyze` roda a partir do chat do plan; sem eles, recomende chat novo para iniciar a análise. Recomende com ênfase um chat novo com `/vibe-implement`, que rodará em Modo A num host com subagentes e em Modo B sem eles. Se o humano preferir continuar no mesmo chat, isso não bloqueia. O `analyze.md` e os artefatos vivos são a ponte.

- [x] Aprovação humana (leu o arquivo e confirmou)
