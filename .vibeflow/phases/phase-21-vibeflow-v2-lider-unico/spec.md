# Spec: VibeFlow V2, skill única com coordenador-líder
# Alvo: phase-21-vibeflow-v2-lider-unico
# Status: aprovado

## Revisão de escopo: skill só texto (2026-10-16)

Decisão do humano durante a implement, com estas palavras: "Só texto, tira todos esses motores, foca BEM, na qualidade e organização da skill, para funcionar bem o coordenador previsto". Esta revisão substitui explicitamente os trechos da spec indicados abaixo. O comportamento do líder (F1 a F8, decisões 2 a 8, 10 e 11) continua valendo; onde o texto original cita o motor, o líder obtém a mesma informação lendo o disco.

| ID | Decisão vigente | Substitui |
|---|---|---|
| S1 | A skill `vibeflow` é só texto: `skills/vibeflow/` com `SKILL.md`, `references/` e `templates/`. Sem scripts, sem Python ou PowerShell, sem testes de código. Pasta real, sem symlink; os manifestos apontam para ela. | Contratos (pacote com `scripts/`, `skills/vibeflow` como symlink, relatório JSON, flags, códigos `CODIGO: mensagem`), tecnologia imposta, C3, C4, C5 |
| S2 | O estado vive no disco legível: pastas `.vibeflow/phases/phase-N-slug/` e `.vibeflow/mvp/`, linha `# Status:` de cada artefato, caixas e resumo do `plan.md`, e o Git como histórico. Não existe `execution.json` nem relatório operacional na V2. | A5, decisão 12, partes de F3, F5, F6 e A9 que citam `execution.json` |
| S3 | O líder classifica a rota pela tabela de esforço do `AGENTS.md` e grava `# Rota: <rota>` no cabeçalho do primeiro artefato da phase. A rota não muda; pedido maior abre nova phase. | Decisão 12 |
| S4 | As operações mecânicas viram regras escritas: `n` é o maior número existente mais um, em ordem numérica; slug com `a-z0-9` e hífen, de 2 a 48 caracteres; artefato existente é editado, nunca recriado; arquivo de regra do usuário só é substituído depois de commit ou cópia conferida em `.vibeflow/old/`. | Contratos de motor de F1, F2 e F3 |
| S5 | Os gates viram uma checagem do líder antes de cada etapa, a partir das linhas `# Status:` e da rota gravada. Etapa pedida sem pré-requisito é recusada com o pré-requisito nomeado. | F7 (validação pelo motor), A10 |
| S6 | Papéis, ondas por `Arquivos:` disjuntos, prova afetada por T*, regressão completa na review, até duas rodadas de correção e confirmação humana final continuam. O finalizador registra estado no `plan.md` e opera Git; não há registro estruturado. | Decisão 9 (protocolo com `execution.json`) |
| S7 | Phases v1 são lidas como estão: o estado vem das linhas de status e das caixas do `plan.md`; `execution.json` antigo é preservado e não é interpretado. | F10 e A13 (leitura pelo motor) |
| S8 | A distribuição entrega somente `vibeflow` 10.0.0; `vibe-*/`, `skills/vibe-*`, `docs/vibe-*/` e `docs/tests/` são removidos. | F9 e A12 (symlink) |
| S9 | A prova da entrega é a review independente de consistência e qualidade da skill e o uso real (C1, C2, C6). | Como provar (linhas de motor), Boundaries "testes somente sobre motores" |

## Objetivo

Quem instala o VibeFlow passa a operar uma única skill, `vibeflow`, conduzida por um coordenador-líder. O líder faz o briefing, entende o projeto, escolhe a rota proporcional ao pedido, planeja, delega toda execução aos analistas, critica, reconhece e decide. Analyze e review continuam sempre com visão de fora. Sucesso é conduzir de uma troca de cor a uma rota max com um único `/vibeflow`, sem perda de estado e com eficiência percebida no mínimo igual à da v1, entregue como versão major 10.0.0 na branch `v2`.

## Cobertura da origem

| Origem | Destino na spec | Motivo se fora/N/A |
|---|---|---|
| Skill única `vibeflow` substitui as 8 `vibe-*` | F1, F9 | N/A |
| Essência do líder (briefing, macro, delegar, criticar, elogiar, decidir) | F1, F3, F5, decisões 3 a 6 | N/A |
| Analyze e review nunca feitos pelo coordenador | F4 | N/A |
| Host sem subagentes degradado com aviso | F8 | N/A |
| Contrato de disco mantido; `execution.json` desde a interview | F3, F10, Contratos | N/A |
| Contexto do líder; dois chats em contexto curto | F6 | N/A |
| `plan.md` sempre atualizado, inclusive na interrupção | F5, F6 | N/A |
| Init como etapa 0 com recarga do host | F2 | N/A |
| Entrada `/vibeflow` com etapa opcional, sem aliases | F1, F7 | N/A |
| Sucesso: rota max sem perda, líder fora do micro, motores sem duplicação, phases antigas retomáveis | Checklist C1 a C5 | N/A |
| Eficiência mínima igual à v1, medida pelo humano | C6, decisão 2 | Sem benchmark automatizado (Fora) |
| Testes só de código e efeitos no disco | Boundaries | N/A |
| Fragmentos de instrução, worktree por T*, fan-out da review, benchmark | Fora | Decididos como posteriores na interview |

## Suposições e decisões

1. A V2 é a versão 10.0.0, desenvolvida na branch `v2` e construída pela cadeia v1 (dogfooding). A `main` continua recebendo correções da v1 até a V2 ser integrada. (processo; já fechado)
2. Rota proporcional ao pedido, com a tabela de esforço atual (Express, low, medium, high, xhigh, max, MVP) como única fonte. Pedido pequeno, como trocar a cor de um botão ou fazer uma página HTML/CSS, não passa por spec, plan, analyze nem review e não exige `.vibeflow/` quando não há phase ativa. A cadeia completa só aparece quando o tamanho do pedido justifica. (produto; já fechado)
3. O líder delega sempre, inclusive em Express e low: entrega um brief curto ao analista, recebe a prova e fecha. Ele não executa o micro; faz no máximo pequenos ajustes finais, como um typo ou uma linha de fechamento. Em host sem subagentes vale a degradação de F8. (produto; já fechado)
4. O líder conduz diretamente a conversa com o humano (briefing, perguntas, restate, aprovações e confirmação final). Redação de artefatos vai ao redator; leitura ampla ao explorador; código, testes, provas, registros e Git aos papéis atuais (implementador, verificador, corretor, redator, finalizador). O líder recebe resumos e vereditos. (produto; já fechado)
5. Crítica e reconhecimento acontecem na devolutiva de cada delegação. Crítica confronta a entrega com o objetivo da phase e devolve ao dono um apontamento específico, sem refazer o trabalho. Reconhecimento marca a entrega como referência de padrão para as próximas delegações e reaproveita o analista que acertou, com seu contexto. Nenhum dos dois cria artefato ou seção nova; o `plan.md` registra só o estado resultante. (produto; assumido pela IA a partir da essência pedida)
6. O líder evita dois desvios: microgerência (refazer conferência, diff ou prova já certificados) e distância (aceitar entrega sem confrontá-la com o objetivo). (produto; já fechado)
7. Analyze e review são sempre executados por revisor de contexto limpo. O líder entrega o alvo, recebe veredito, cobertura e R* e encaminha as correções; não altera `analyze.md` nem `review.md`. (produto; já fechado)
8. Modo B existe somente para host sem subagentes ou quando o humano pede explicitamente uma T* por run. (processo; assumido pela IA)
9. Os papéis e o protocolo `coordenacao-v1` (ondas por `Arquivos:` disjuntos, provas em dois níveis, finalizador, até duas rodadas de correção) são preservados como o núcleo da implementação da V2. (escopo; assumido pela IA)
10. Os comandos `/vibe-*` e os pacotes `vibe-*` deixam de existir na V2, sem aliases nem convivência. (produto; já fechado)
11. A tabela de decisões vigentes em `AGENTS.md` só muda após implementação, review aprovada e confirmação humana, como hoje. (processo; já fechado)
12. A IA (líder) classifica a rota pelo pedido e o motor a grava no `execution.json` na abertura da phase, validada contra a allowlist de rotas. O motor não decide a rota; aplica com ela os bloqueios de F7. Phase v1 sem rota registrada mantém o gate v1. (arquitetura; decidido pelo humano no analyze, F8)

## Escopo e comportamento

### 1. Fluxo F1: entrada e classificação

- Jornada: humano pede algo ao VibeFlow.
- Rota: todas.
- Gatilho: `/vibeflow` sem argumento ou auto-invoke pela description única.
- Pré-condição: skill `vibeflow` instalada no host.
- Superfície por passo: inline (chat) em todos os passos.
- Passos:
  1. Líder executa o motor em leitura -> relatório com estado do repo, phase aberta, etapa atual e avisos [superfície: inline].
  2. Com phase aberta do mesmo assunto, líder retoma a etapa indicada pelo motor -> anuncia em uma linha a etapa e o próximo responsável [superfície: inline].
  3. Sem phase aberta, líder classifica o pedido (texto avulso, Express, low a max, MVP) -> anuncia a rota em uma linha e as etapas que ela inclui [superfície: inline].
  4. Rota Express ou low sem phase ativa -> líder delega a um analista com brief curto, recebe prova proporcional e fecha, sem criar `.vibeflow/`, phase ou artefato [superfície: inline].
  5. Rota com cadeia -> segue para F3 ou F5 conforme a etapa [superfície: inline].
- Validações: texto ou documento avulso segue edição direta, fora da cadeia de código; assunto diferente da phase aberta abre nova phase.
- Erros: `INIT_AUSENTE` (sem `.vibeflow/` numa rota que exige cadeia; segue para F2), `PHASES_INESPERADO`, `MVP_INESPERADO` (estrutura inesperada; não contornados).
- Estados: sem init, phase aberta, sem phase, Express.
- Aceite: A1, A2.
- Reutilizar: tabela de esforço do `AGENTS.md`; seleção de alvo dos motores atuais.

### 2. Fluxo F2: etapa 0, init

- Jornada: primeiro uso no repo ou repo quebrado.
- Rota: init.
- Gatilho: `INIT_AUSENTE`, instalação legada (`.vibeflow/REGRAS.md`, `REGRAS.md`, `CLAUDE.md`) ou `/vibeflow init`.
- Pré-condição: repositório de software.
- Superfície por passo: inline.
- Passos:
  1. Líder delega o init ao analista apto -> `AGENTS.md`, ponte `.agents/rules/vibeflow.md`, perfis por host e backup verificado em `.vibeflow/old/` [superfície: inline].
  2. Líder confere o relatório e o commit de governança -> informa paths e hash [superfície: inline].
  3. Perfis novos ou alterados -> líder para e pede recarga do host antes da primeira delegação [superfície: inline].
- Validações: backup com tamanho e hash antes de substituir regra; sem `CLAUDE.md` nem `REGRAS.md` criados.
- Erros: falha de backup (nenhuma substituição ocorre).
- Estados: novo, legado migrado, reparo, aguardando recarga.
- Aceite: A3.
- Reutilizar: contrato atual de `vibe-init`.

### 3. Fluxo F3: planejamento conduzido pelo líder

- Jornada: pedido com rota xhigh, max ou MVP.
- Rota: interview -> spec -> design (com UI) -> plan.
- Gatilho: rota com cadeia e etapa de planejamento pendente.
- Pré-condição: init válido.
- Superfície por passo: inline.
- Passos:
  1. Interview: líder pergunta uma coisa por vez no formato Anotei/Pergunta/Guess e confirma o restate -> redator grava `interview.md` [superfície: inline].
  2. Spec e design: líder fecha seams com o humano -> redator grava `spec.md` e `design.md` -> humano aprova [superfície: inline].
  3. Plan: líder define resultados, responsáveis, dependências e ondas -> redator grava `plan.md` com `Arquivos:`, `Prova afetada:` e `Regressão completa` -> humano aprova [superfície: inline].
  4. A cada artefato aprovado, o motor registra a etapa no `execution.json` da phase [superfície: inline].
- Validações: gates atuais (spec sem aberto, design só com UI visível e N/A explícito sem UI, plan não sobrescrito); "ok" isolado não aprova outra porta.
- Erros: códigos atuais de cada etapa (`SPEC_JA_PLANEJADA`, `FASE_EXISTE`, `SLUG_INVALIDO` etc.).
- Estados: rascunho, aprovado, bloqueado por aprovação.
- Aceite: A4, A5.
- Reutilizar: templates e critérios das skills interview, spec, design e plan, convertidos em referências por etapa.

### 4. Fluxo F4: analyze e review com visão de fora

- Jornada: rota max (analyze) e rotas com review.
- Rota: analyze, review.
- Gatilho: etapa `analisar` ou `revisar` indicada pelo motor.
- Pré-condição: artefatos de entrada aprovados ou integração commitada.
- Superfície por passo: inline.
- Passos:
  1. Líder delega ao revisor de contexto limpo o alvo e os artefatos -> revisor grava `analyze.md` ou `review.md` e devolve veredito, cobertura, R* e perguntas [superfície: inline].
  2. Líder leva perguntas materiais ao humano e encaminha R* pelo `papel:` -> corretor ou redator corrige [superfície: inline].
  3. Sem subagentes, líder grava checkpoint e instrui abrir chat novo com `/vibeflow analyze` ou `/vibeflow review` [superfície: inline].
- Validações: o líder não escreve `analyze.md` nem `review.md`; revisor não certifica código próprio nem toca Git.
- Erros: perfil revisor ausente ou não carregado (pergunta ao humano com recomendação; nada é despachado).
- Estados: pendente, Request changes, Approve, rodada 2 sem convergência (para e relata).
- Aceite: A6.
- Reutilizar: contrato atual de `vibe-analyze` e `vibe-review`, roteamento de R* por `papel:`.

### 5. Fluxo F5: implementação por ondas com crítica e reconhecimento

- Jornada: plan aprovado (e analyze limpo no max).
- Rota: implement -> validar -> commitar -> revisar -> corrigir -> confirmar.
- Gatilho: etapa `implementar` ou posterior indicada pelo motor.
- Pré-condição: plan aprovado em `coordenacao-v1`.
- Superfície por passo: inline.
- Passos:
  1. Líder confere a capacidade de delegação e despacha a onda (`fila.onda`) -> analistas entregam código, testes e `Prova afetada:` [superfície: inline].
  2. Líder avalia cada devolutiva contra o objetivo -> devolve com apontamento específico ou marca como referência de padrão [superfície: inline].
  3. Verificador certifica; finalizador registra a onda e atualiza o `plan.md` com pronto, em andamento e pendente [superfície: inline].
  4. Integração verde -> commit `task(T*...)`; review e correções seguem F4 [superfície: inline].
  5. Fechamento -> líder apresenta resultado, commits, Critical e decisões propostas e pede uma confirmação para aprovar review, publicar decisões e fazer push [superfície: inline].
- Validações: contratos atuais de `coordenacao-v1` (ondas disjuntas, provas em dois níveis, até duas rodadas de correção).
- Erros: códigos atuais do motor da implement (`IMPLEMENT_SEM_PLAN`, `IMPLEMENT_ANALYZE_*`, `EXECUTION_INVALIDO` etc.).
- Estados: as etapas atuais de `implementar` a `concluida`, mais `bloqueada`.
- Aceite: A7, A8.
- Reutilizar: motor e referências atuais da implement (`delegation.md`, `execution.md`).

### 6. Fluxo F6: interrupção e retomada

- Jornada: humano interrompe ou o contexto pesa.
- Rota: qualquer rota com phase.
- Gatilho: humano pede para parar, contexto do chat pesado, ou host de contexto curto.
- Pré-condição: phase aberta.
- Superfície por passo: inline.
- Passos:
  1. Pedido de interrupção -> líder delega a atualização do `plan.md` (pronto, em andamento, pendente) e do `execution.json` antes de parar -> confirma o estado gravado [superfície: inline].
  2. Contexto pesado -> líder grava checkpoint e recomenda chat novo [superfície: inline].
  3. Host de contexto curto -> líder explica no início que um chat para todo o planejamento e outro para a implementação resolve boa parte dos problemas [superfície: inline].
  4. Chat novo com `/vibeflow` -> motor devolve a etapa e o líder retoma sem refazer trabalho válido [superfície: inline].
- Validações: retomada parte do disco, nunca do histórico do chat; evidência inalterada é preservada.
- Erros: registro inconsistente (`EXECUTION_INVALIDO`; diagnóstico delegado, sem chute).
- Estados: em execução, interrompida, retomada.
- Aceite: A9.
- Reutilizar: retomada atual do Modo A.

### 7. Fluxo F7: entrada com argumento de etapa

- Jornada: humano quer ir direto a uma etapa.
- Rota: a da etapa pedida.
- Gatilho: `/vibeflow <etapa>` com `init`, `interview`, `spec`, `design`, `plan`, `analyze`, `implement` ou `review`.
- Pré-condição: nenhuma além dos gates da etapa.
- Superfície por passo: inline.
- Passos:
  1. Motor valida o argumento contra a allowlist e os pré-requisitos -> segue a etapa ou recusa [superfície: inline].
- Validações: gates preservados (plan sem spec aprovada bloqueia; implement high+ sem plan bloqueia; max exige analyze limpo). Os gates dependentes de rota usam a rota gravada no `execution.json` da phase (decisão 12): implement sem plan aprovado em high ou acima e implement sem analyze aprovado e limpo em max e MVP são recusados com `ETAPA_BLOQUEADA`. Phase v1 sem rota registrada mantém o gate v1 (motor bloqueia analyze só no MVP; nas demais rotas o gate é do líder).
- Erros: `ETAPA_INVALIDA` (argumento fora da allowlist), `ETAPA_BLOQUEADA` (pré-requisito ausente, com o pré-requisito nomeado, nas recusas novas da V2); recusa que a v1 já aplicava conserva o código v1, como `PLAN_SEM_SPEC` (ARQUITETURA §7).
- Estados: aceita, recusada.
- Aceite: A10.
- Reutilizar: gates atuais de cada skill.

### 8. Fluxo F8: host sem subagentes

- Jornada: host que não delega.
- Rota: qualquer.
- Gatilho: ausência de subagentes ou perfis exigidos não carregados.
- Pré-condição: nenhuma.
- Superfície por passo: inline.
- Passos:
  1. Líder informa a limitação em uma linha -> opera em Modo B: uma etapa ou T* por run, executada inline, e o motor indica a próxima [superfície: inline].
  2. Analyze e review -> instrução para chat novo, que atua como visão de fora [superfície: inline].
- Validações: perfil presente só em disco não conta como carregado.
- Erros: N/A, a degradação é o comportamento.
- Estados: degradado.
- Aceite: A11.
- Reutilizar: Modo B atual.

### 9. Fluxo F9: distribuição da V2

- Jornada: instalar ou atualizar o VibeFlow.
- Rota: N/A, distribuição.
- Gatilho: `npx skills add korflux/vibeflow` ou marketplace nativo.
- Pré-condição: versão 10.0.0 publicada.
- Superfície por passo: inline (CLI do host).
- Passos:
  1. Instalação -> host recebe somente a skill `vibeflow` nos marketplaces Claude, Codex, Grok e Antigravity [superfície: inline].
- Validações: nenhum manifesto, symlink ou README referencia `vibe-*` como skill instalável.
- Erros: N/A.
- Estados: instalada.
- Aceite: A12.
- Reutilizar: manifestos e contrato de `docs/tests/test-distribuicao.py`.

### 10. Fluxo F10: phases antigas

- Jornada: repo com phases criadas pela v1.
- Rota: retomada.
- Gatilho: `/vibeflow` com phase aberta em `etapas-v1`, legado ou `coordenacao-v1`.
- Pré-condição: phase v1 em disco.
- Superfície por passo: inline.
- Passos:
  1. Motor lê a phase sem migrar nem reescrever artefatos -> etapa derivada como na v1 [superfície: inline].
  2. Phase sem `execution.json` de planejamento -> etapa derivada dos artefatos presentes e de suas linhas de status [superfície: inline].
- Validações: artefato existente preservado byte a byte; protocolo histórico mantém seu contrato.
- Erros: `MODO_INVALIDO` ou protocolo desconhecido bloqueiam sem fallback.
- Estados: v1 retomada, histórica concluída.
- Aceite: A13.
- Reutilizar: `references/protocolos-historicos.md`.

### Fora

- Testes de comportamento de fragmentos de instrução: decidido como posterior.
- Benchmark automatizado de eficiência: a eficiência é medida pelo humano no uso.
- Worktree por T* e pacote de contexto por T*: isolamento continua pela disjunção de `Arquivos:`.
- Fan-out da review por dimensão: review segue com um revisor.
- Aliases `/vibe-*` ou convivência com os pacotes v1: contraria a decisão de skill única.
- Migração automática de phases antigas: são lidas como estão.

## Checklist de entrega

### Aceite

- [ ] A1: `/vibeflow` sem argumento retoma a phase aberta na etapa indicada pelo motor ou anuncia a rota classificada para um pedido novo.
- [ ] A2: Pedido Express ou low sem phase ativa é delegado e fechado sem criar `.vibeflow/`, phase, spec, plan, analyze ou review.
- [ ] A3: Repo sem init ou legado passa pela etapa 0, com backup verificado, sem `CLAUDE.md` ou `REGRAS.md` criados, e o líder para pedindo recarga quando os perfis mudam.
- [ ] A4: Na rota com cadeia, o líder conduz as perguntas e aprovações, e os artefatos são escritos por analista nos mesmos paths da v1.
- [ ] A5: O `execution.json` da phase registra a etapa desde a interview.
- [ ] A6: `analyze.md` e `review.md` são escritos somente pelo revisor de contexto limpo; sem subagentes, o líder instrui chat novo.
- [ ] A7: Cada devolutiva de analista recebe do líder aceite como referência ou devolução com apontamento específico, sem o líder refazer o trabalho.
- [ ] A8: O `plan.md` reflete pronto, em andamento e pendente ao fim de cada onda.
- [ ] A9: Após pedido de interrupção, `plan.md` e `execution.json` estão atualizados antes de parar, e um chat novo com `/vibeflow` retoma na etapa correta.
- [ ] A10: `/vibeflow <etapa>` aceita somente a allowlist de etapas e recusa pré-requisito ausente com o código v1 quando a v1 já recusava e `ETAPA_BLOQUEADA` nomeando o que falta nas recusas novas (ARQUITETURA §7).
- [ ] A11: Host sem subagentes opera em Modo B com aviso de uma linha.
- [ ] A12: A instalação entrega somente a skill `vibeflow` nos quatro hosts.
- [ ] A13: Phases v1 (`etapas-v1`, legado, `coordenacao-v1`) são lidas e retomadas sem alteração dos artefatos existentes.

### Critérios de sucesso

- [ ] C1: Uma rota max completa, da interview ao push, roda com um único `/vibeflow` (ou dois chats) sem perda de estado.
- [ ] C2: Em host com subagentes, nenhuma escrita de código, artefato ou Git é feita pelo líder além de pequenos ajustes finais; sem subagentes vale F8.
- [ ] C3: Alvo, slug, inventário, relatório e `.gitignore` têm uma única implementação por motor (Python e PowerShell).
- [ ] C4: Os motores Python e PowerShell expõem as mesmas flags e o mesmo JSON operacional.
- [ ] C5: Phases 1 a 20 deste repositório continuam inventariadas sem erro pelo motor da V2.
- [ ] C6: O humano percebe eficiência no mínimo igual à da v1, com mais praticidade, no uso real.

## Contratos e restrições necessárias

- Dados e invariantes: paths `.vibeflow/phases/phase-N-slug/` e `.vibeflow/mvp/` e nomes de artefato inalterados; `n` calculado pelo motor; artefato existente preservado byte a byte; backup com hash antes de substituir arquivo do usuário; um baseline MVP por repo. O `execution.json` ganha versão de schema nova que cobre etapas de planejamento e a rota da phase; registros da versão anterior continuam válidos. A rota é classificada pela IA (líder) a partir do pedido e gravada pelo motor no `execution.json` na abertura da phase, validada contra a allowlist (Express, low, medium, high, xhigh, max, MVP); valor fora da allowlist é recusado. O motor não decide nem infere a rota; ele a usa para os gates de F7.
- Integrações e interfaces: um pacote `vibeflow/` com `SKILL.md`, `scripts/vibeflow.py`, `scripts/vibeflow.ps1`, `scripts/vibeflow.sh`, `templates/` e `references/`; `skills/vibeflow` como symlink; relatório em `.vibeflow/vibeflow-report.json` (gitignored, sem apagar entradas existentes); sem `.vibeflow/`, a leitura não grava relatório nem cria `.vibeflow/` (A2) e entrega o JSON operacional pelo stdout; flags públicas iguais nos dois motores, incluindo a etapa opcional; erro previsto no formato `CODIGO: mensagem` no stderr; documentação em `docs/vibeflow/ARQUITETURA.md` e `ANALISE.md`.
- Segurança e operação: entrada externa é a linha de comando. Etapa aceita apenas a allowlist de F7; rota aceita apenas a allowlist de rotas (decisão 12); slug sanitizado para `a-z0-9` e hífen com 2 a 48 caracteres; `--dir` restrito a uma pasta existente sob `.vibeflow/phases/`; symlink, junction ou reparse point em `.vibeflow/`, `phases/` ou `mvp/` é recusado; `--command` recebido pelo registro nunca é executado. Push, aprovação de review e decisões vigentes exigem confirmação humana explícita. Sem segredo, dado pessoal, rede ou rota autenticada: CORS, CSRF, rate limit e CSP N/A.
- Tecnologia imposta: Python 3 e PowerShell 7, sem dependência nova; testes com `unittest` e asserts PowerShell.
- Consumidores: o contrato do motor único é consumido por F1, F3, F4, F5, F6, F7 e F10; o `AGENTS.md` gerado pelo init é consumido por todos os fluxos.

## Como provar

| Aceite | F* ou jornada | Nível | Evidência esperada |
|---|---|---|---|
| A1, A10 | F1, F7 | local | Relatório do motor com etapa correta para cada estado de disco preparado; recusa com o código e o pré-requisito nomeado |
| A2 | F1 | local | Repo isolado sem `.vibeflow/` permanece sem `.vibeflow/` após a classificação Express |
| A3 | F2 | local | Init em repo isolado gera os arquivos esperados, backup com hash conferido e nenhum `CLAUDE.md` ou `REGRAS.md` |
| A5, A9 | F3, F6 | local | `execution.json` contém a etapa de planejamento após o registro; retomada devolve a mesma etapa |
| A12 | F9 | local | Manifestos e symlinks listam somente `vibeflow` |
| A13, C5 | F10 | local | Motor inventaria fixtures v1 e as phases 1 a 20 sem erro e sem alterar bytes |
| C3, C4 | motores | local | Funções comuns existem uma vez por motor; paridade de flags e JSON entre Python e PowerShell |
| A4, A6, A7, A8, A11, C1, C2 | rota max completa | jornada | Uma phase real conduzida com `/vibeflow`: artefatos escritos por analistas, `analyze.md`/`review.md` pelo revisor, `plan.md` atualizado por onda, commits pelo finalizador |
| C6 | uso real | jornada | Avaliação do humano após uso da V2 |

## Boundaries

### Always

- Rota proporcional ao pedido; pedido pequeno não ganha cadeia.
- Líder delega a execução, inclusive em pedidos pequenos, e conversa diretamente com o humano.
- Analyze e review por revisor de contexto limpo.
- `plan.md` atualizado ao fim de cada onda e antes de parar por interrupção.
- Testes somente sobre motores e seus efeitos no disco, em pasta isolada removida ao final.

### Ask first

- Qualquer mudança de path ou nome de artefato em `.vibeflow/`.
- Aprovação de review, publicação de decisões vigentes e push.
- Dependência nova.

### Never

- Líder escrevendo `analyze.md` ou `review.md`, em qualquer host.
- Líder escrevendo código ou Git em host com subagentes; sem subagentes vale F8.
- Teste que verifica presença de texto em `SKILL.md`, referências, templates ou documentação.
- Aliases `/vibe-*` ou pacotes v1 mantidos em paralelo.
- Migração ou reescrita implícita de phase antiga.
- Criar `CLAUDE.md`, `REGRAS.md` ou `GEMINI.md` como fonte de regras.

## Handoff

vibe-plan

- Chat: sem UI visível, `design` é N/A. Recomende novo chat para `vibe-plan`; se o humano preferir, continuar no mesmo chat não bloqueia. O `spec.md` vivo é a ponte.

- [x] Aprovação humana (leu o arquivo e confirmou)
