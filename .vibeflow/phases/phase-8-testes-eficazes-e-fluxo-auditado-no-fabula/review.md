# Review: Testes eficazes e fluxo auditado no fabula
# Alvo: phase-8-testes-eficazes-e-fluxo-auditado-no-fabula
# Status: request-changes

## Veredito

- [ ] **Approve**: critérios atendidos e provados, regressão verde e nenhum Critical ou Required aberto
- [x] **Request changes**: há Critical ou Required aberto

## Critérios de aceite

| Critério | Evidência (teste e resultado) | Situação |
|---|---|---|
| A1 | `tests/scripts/plan.test.mjs`: "até 4 checkpoints, cada um com motivo da tabela, são aceitos (A1)", "o 5º checkpoint é achado, mesmo com motivo da tabela (A1)", "motivo fora da tabela é achado (A1)", "checkpoint sem motivo é aviso e não muda o código de saída (A1, A5)" e "A<n> no texto do motivo não entra no aceite do checkpoint (A1)", sobre plan de 10 passos; asserções conferidas contra o texto ajustado com aceite humano (contagem, motivo da tabela, aviso sem motivo). Parte do analyze: `analyze/coverage.md`, linha Checkpoint fora da regra, acusa `tela` antes do passo que fecha o visual e critério de tela em checkpoint anterior. `node --test` verde | atendido |
| A2 | `plan.test.mjs`: "checkpoint em plan de até 5 passos é achado; com 6 passos não (A7)" (teste da phase-6, mantido), asserção igual ao texto de A2; `plan.mjs --alvo phase-5` sai 1 pelo mesmo achado, como na 5.5.0 | atendido |
| A3 | Prosa: `implementador.md` (Codar e provar, Gate estático) manda rodar sobre os arquivos alterados os gates declarados no `AGENTS.md`, inclusive seção equivalente como Comandos do painel, e citar cada um no `prova`; `delegation.md` (Relatório fixo, campo `prova`, e Conferência do líder, linha Passo) pede e confere o gate. Haiku S11: gate presente em 9 de 9 briefs, PASSA em v2 (2 de 3) | atendido |
| A4 | `estado.test.mjs`: "path declarado em ## Trabalho alheio não para a phase: segue o passo aberto" e casos de sobreposição, pasta e duas phases; `conferir.test.mjs`: "passo: path declarado em ## Trabalho alheio não é acusado nem entra nos alterados" e "commit: o staging de trabalho alheio declarado continua acusado, com a marca da declaração". `node --test` verde | atendido |
| A5 | Comparação desta review entre os scripts de `eaa2f3d` e do `HEAD` nas phases 1 a 7: `lerRs`, itens de `lerPlan`, `estado.mjs --alvo phase-N --json` e `plan.mjs --alvo phase-N --json` (sem o campo novo `avisos`) idênticos, com os mesmos códigos de saída (2, 2, 2, 2, 1, 0, 0); `plan.test.mjs` "checkpoint sem motivo é aviso..."; `estado.test.mjs` "plan sem ## Trabalho alheio mantém a linha sem dono" | atendido |
| A6 | `conferir.test.mjs`: "R* com vários paths: todos entram no recorte; o que está fora de todos é achado" e "commit de R* com vários paths aceita todos; R* antigo de um path segue aceito"; `disco.test.mjs`: "R* com vários paths lê todos, na ordem, até o primeiro \" - \"" | atendido |
| A7 | `disco.test.mjs`: "R* antigo de um path: crase da descrição, do remédio e da prova não vira path (linha real da phase-1)"; comparação desta review: `lerRs` dá os mesmos paths da 5.5.0 nos 26 R* das phases 1 a 7 | atendido |
| A8 | `testes.md` como casa única (cabeçalho e ponteiros de `verificador.md`, `implementador.md`, `chrome-devtools.md`, `review/passos.md`, `definition-of-done.md`, `analyze/coverage.md`): prova principal por critério com ID no título quando o brief ou a spec o tem, asserção contra o texto, casos adversariais obrigatórios, E2E só para tela ou jornada, seção Execução (build de produção, console em dev, pilha única, sessão reaproveitada), remoção de duplicata e seção O que não testar. Nenhuma regra antiga contradiz (pilha por worker, letras do isolamento, build só na regressão, captura do implementador em `high`, "teto, não piso" ausentes) | atendido |
| A9 | `verificador.md` (Checkpoint, item 3) e `review/passos.md` (Julgar o produto, item 1) mandam comparar a asserção com o texto do critério; `testes.md` (Política de testes) é a casa | atendido |
| A10 | `interview.md` (Perguntar) e `interview/mvp-discovery.md` (Módulos de completude e Registro): decisão de autenticação, autorização, segurança ou dados é sempre perguntada; nenhuma outra regra do pacote permite assumi-la | atendido |
| A11 | Reclassificação e mapa dos defeitos (Reclassificação da suíte do fabula, abaixo). Contagem conferida nesta review sobre `parcial/consolidado.json`: 1.248 + 33 + 52 = 1.333 casos. O defeito 5 (`ui/` do passo 1) não tem regra que o pegue: a regra nova de componente compartilhado exige renderizar "uma tela que o usa", e no passo 1 nenhuma tela usava o `ui/` (R1) | parcial |
| A12 | Comparação Haiku, abaixo: dos 8 cenários que passam na base pelo gabarito base, 8 passam na 5.6.0, com S4 em fixture v4 (decisão do humano) e S5 em fixture v3; S9 a S12 passam no gabarito 5.6.0 | atendido |
| A13 | `grep` de `# Status:` no pacote: `disco.md` (Cabeçalho) é a regra única (revisor grava `rascunho` ou `request-changes`, só o líder grava `aprovado`, exceção do ajuste medium em `ajuste.md`); `review/passos.md`, `revisor.md`, `redator.md` e `SKILL.md` apontam para ela; `retomada.md` diz "no analyze"; registro `status-do-review-revisor-ou-lider.md` apagado | atendido |
| A14 | Medição por papel, abaixo; `medir.mjs` reproduzido nesta review sobre `skills/vibeflow` do `HEAD` com `papeis-5.6.0.json`: valores idênticos a `medicao-5.6.0.txt`; `final-5.6.0/` igual ao `HEAD` por `diff -r` | atendido |
| A15 | `AGENTS.md` (Versão): 5.6.0; `README.md` com Novidades da 5.6.0 e tabela de rotas com até quatro checkpoints; bloco CADEIA igual no template e na raiz | atendido |
| A16 | `analyze.md` (Saída): ao fechar o analyze, o líder mostra o plan como guia, um tópico curto por passo e por checkpoint, na ordem do plan | atendido |

## Achados

### Required

- [x] R1: **Required** - `skills/vibeflow/references/testes.md` - A11 e o Objetivo da spec pedem, para cada defeito real auditado, a regra ou o gate da política nova que o pegaria; o defeito 5 (componentes de `ui/` criados no passo 1 do fabula sem tela que os usasse, defeito visto só no 5a) continua sem regra. A regra nova da Política de testes ("Passo que altera componente compartilhado (usado por mais de uma tela) leva [...] um teste que renderiza ao menos uma tela que o usa") declara a intenção de pegar o defeito "onde nasce", mas não se aplica ao passo que cria o componente antes de qualquer tela; `defeitos.md` registra o 5 como parcial - remédio: estender a regra ao componente criado para uso compartilhado que ainda não tem tela, com um teste que renderiza uma página de amostra dele no próprio passo (recomendação de `defeitos.md`), ou o humano aceita a cobertura parcial do defeito 5 e ajusta A11 - prova: releitura do defeito 5 de `defeitos.md` contra a regra corrigida; `git diff --check` - papel: redator

### Nit

- [x] R2: **Nit** - `skills/vibeflow/references/testes.md` - a frase de critério ambíguo traz uma regra do líder ("o líder não reabre critério aprovado antes de despachar o passo") num arquivo que o líder não lê em `high` e que o implementador e o verificador leem inteiro; a comparação Haiku registra que ela não mudou o resultado de S4. A mesma frase diz que o redator do plan "vai escrever o teste", e o redator não escreve teste - remédio: tirar a oração do líder de `testes.md` ou, se o humano a quiser, levá-la a `references/implement.md` (Executar o passo); trocar "quem vai escrever o teste (implementador do passo ou redator do plan)" por quem escreve ou nomeia o teste - prova: `git diff --check`; ponteiros resolvem - papel: redator
- [x] R3: **Nit** - `README.md` - Novidades da 5.6.0 diz "ID do critério no título do teste" sem a condição "quando o brief ou a spec o tem", que o humano aprovou no ajuste de A8 - remédio: acrescentar a condição - prova: `git diff --check` - papel: redator

## Notas

- Regressão, item 7 (revisão de consistência): gates (`SKILL.md` seção 3, `review.md` Entrada), commits (`disco.md` Commits e conferência por `conferir.mjs`), encadeamento (topo do `SKILL.md`), checkpoint (`disco.md` Plan > Checkpoint, `implement.md` passo 2, `verificador.md`, `analyze/coverage.md`), Modo B (`retomada.md`) e `# Status:` conferidos entre si sem contradição. Todo path do repo citado em `skills/vibeflow/`, `README.md` e `AGENTS.md` existe (fora o exemplo de consumidor `tests/a.test.ts` em `disco.md`); nenhum arquivo cita v1 do VibeFlow nem contrato anterior à 5.0.0 como vigente.
- Regras acrescentadas no passo 11 além da lista da decisão 6, vindas da reclassificação: teste de tela no passo que altera componente compartilhado, alvo junto do ID quando há IDs repetidos entre specs, dúvida de equivalência em `pendencias` e a nova redação da remoção de duplicata. A spec não registra decisão humana sobre as duas primeiras; o líder confirma com o humano antes da confirmação final. O passo 11 tinha como recorte corrigir regressão de cenário Haiku, e o commit `cff4584` declara os "ajustes da reclassificação".
- Crescimento de `testes.md` (3.432 para 8.410 caracteres, a causa do +73% do implementador e do verificador): a maior parte é regra nova da decisão 6. Cópia removível sem perder regra, cerca de 460 caracteres (5,6% do arquivo): o resumo do conteúdo de `verificador.md` no cabeçalho ("(isolamento entre workers, encadeamento, build e workers)") e "As demais referências apontam para cá."; "; ele cobre a jornada no checkpoint e na regressão completa", que repete o bullet do checkpoint; "O E2E de jornada não é prova principal [...]", implicado pelo bullet de critério de tela; a oração do líder (R2); e a linha "A mesma propriedade em vários arquivos" de O que não testar, que repete o bullet Remoção (fica uma das duas). O verificador abre só Política de testes e Execução (cerca de 4.800 de 8.200 caracteres); a medição, pelo método da phase-7, conta o arquivo inteiro.
- "Jornada" não é definida em `testes.md`; "critério com tela ou jornada" admite ler um fluxo só de API com vários passos como jornada e dar E2E a ele, contra o primeiro bullet da Política de testes. Sem achado: a expressão vem da decisão 6 da spec.
- Haiku: S4 nos fixtures v1 a v3 e S5 no fixture v1 divergem na 5.6.0 (o líder para antes de despachar ou abre os testes vazios e devolve o passo); passam com S4 v4, decisão do humano, e S5 v3, relatório conforme à 5.6.0. Fica o risco de o líder Haiku auditar a base do grupo ou abrir teste, contra a conferência sem microgerência de `SKILL.md` (seção 5, item 4); a frase tentada em `delegation.md` foi revertida sem efeito medido. S12 passa por maioria (2 de 3; a terceira resposta propõe chave exata e normalização como decisão separada).
- A reclassificação cobriu a suíte atual do fabula, 1.333 casos em 860 itens, e não os 438 da decisão 7: os 438 eram a suíte da phase-1, contida nos 546 do painel; o restante veio da phase-2 do fabula (+108 no painel e 787 do site), conforme `inventario.md`. `git status` do fabula igual antes e depois (`git-status-antes.txt`, `git-status-depois.txt`), com `painel/w.html` e `next-env.d.ts` do humano.
- Testes de A4, A6 e A7 têm título sem o ID do critério, e os de A1 trazem o ID no fim: foram escritos nos passos 2 a 4, antes da regra do passo 6. Sem achado.
- Coerência dos commits: todo path dos 19 commits `task(phase-8:...)` está nos `Arquivos:` dos IDs da mensagem (conferido por script desta review). Passos 3, 4, 5, 6 e 8 têm commits posteriores aos checkpoints, no formato de passo, como `implement.md` (Checkpoint) pede para correção. O passo 11 tem `skills/vibeflow/references/` inteiro em `Arquivos:`.
- Achado fora do recorte: `.erros-encontrados/disco-push-adiado-cita-secao-finalizacao-git-inexistente.md`.

## Reclassificação da suíte do fabula

Fonte: `phase8-fabula/` no scratchpad da sessão (`inventario.md`, `reclassificacao.md`, `tempo.md`, `defeitos.md`, `parcial/`), só leitura, HEAD `86353b3` do fabula. Contagem conferida nesta review sobre `parcial/consolidado.json`.

| Pacote e nível | Casos | Fica | Funde | Sai |
|---|---|---|---|---|
| painel unitário | 211 | 209 | 1 | 1 |
| painel integração | 184 | 173 | 5 | 6 |
| painel E2E | 151 | 136 | 8 | 7 |
| site unitário | 56 | 50 | 0 | 6 |
| site integração | 670 | 625 | 17 | 28 |
| site E2E | 61 | 55 | 2 | 4 |
| Total | 1.333 | 1.248 | 33 | 52 |

Em itens declarados: 790 ficam, 30 fundem e 40 saem (860). Dos que ficam, 374 itens carregam ajuste, cerca de 285 deles só pelo título sem ID.

Tempo estimado (`tempo.md`, taxas medidas nas reviews do fabula, nada executado): a primeira onda tira 85 casos e cerca de 28 a 43 s da regressão completa de 533,4 s (5 a 8%), com o E2E firme em 18 s e a incerteza na integração do site; com a segunda onda, 28 a 66 s (5 a 12%). Fora da contagem, sem soma: pilha única por execução (GUESS de 52 a 140 s de relógio), até 12 checkpoints a menos nas três phases e a suíte de captura separada.

| Defeito | Regra ou gate da política nova | Quando pegaria |
|---|---|---|
| R1 do MVP, limite de login por variante de e-mail | `testes.md`, Desenho de casos, Equivalência obrigatória, com vermelho antes do verde | No passo que entrega A31; antes, só se o analyze antecipar o critério |
| Nonce da CSP público | `testes.md`, Execução (E2E sobre build de produção no checkpoint), com `verificador.md` (Checkpoint, item 2) | Checkpoint depois do passo 2 |
| A14 da phase-1, prova só da API | `analyze/coverage.md`, Critério sem prova; `testes.md`, Política de testes (critério de tela se prova na tela) | Analyze, antes do código |
| A39, asserção da interpretação do implementador | `testes.md`, Política de testes (asserção segue o texto; ambíguo volta como pergunta); `verificador.md` (Checkpoint, item 3); `review/passos.md` (Julgar o produto, item 1) | Passo 5a ou checkpoint seguinte |
| `ui/` do passo 1 visto só no 5a | Nenhuma: a regra de componente compartilhado pede tela que o use, e não havia (R1) | Continua no 5a |
| R3 da phase-1, aviso de console só em dev | `testes.md`, Execução (checagem de console em dev); `verificador.md` (Checkpoint, item 2) | Checkpoint depois do 4b |
| R1 da phase-1, OpenGrep em `editable-cell.tsx` | `implementador.md` (Codar e provar, Gate estático), que aceita a seção Comandos do painel do fabula | No passo 9 |

## Comparação Haiku

Fonte: `phase8-haiku/comparacao.md` e `placar-5.5.0.md`, base em `eaa2f3d`, mesmo prompt nas duas versões, modelo haiku, respostas em `exec/respostas/`. Respostas de S12 (r4 a r6) conferidas nesta review contra o gabarito 5.6.0.

| Cenário | Base 5.5.0 | 5.6.0 | Observação |
|---|---|---|---|
| S1 high com seis etapas | PASSA | PASSA | |
| S2 gate do analyze | PASSA | PASSA | |
| S3 phase-11 e slug | PASSA | PASSA | |
| S4 grupo 2a e 2b | PASSA (v4, 3 de 3) | PASSA (v4, 5 de 6) | Fixture v4 por decisão do humano; em v1 a v3 a 5.6.0 não passava por maioria |
| S5 commit do grupo | PASSA (v3, 3 de 3) | PASSA (v3, 3 de 3) | Em v1 a 5.6.0 devolve os passos sem a saída vermelha (0 de 6) |
| S6 caixa marcada sem commit | FALHA (1 de 3) | PASSA (3 de 3) | Melhora |
| S7 Modo B | PASSA | PASSA | |
| S8 low | PASSA | PASSA | |
| S9 checkpoint por motivo | FALHA no gabarito 5.6.0 (esperado) | PASSA | |
| S10 trabalho alheio | FALHA no gabarito 5.6.0 (esperado) | PASSA | |
| S11 gate no passo | FALHA no gabarito 5.6.0 (esperado) | PASSA (v2, 2 de 3) | |
| S12 caso adversarial | FALHA no gabarito 5.6.0 (esperado) | PASSA (2 de 3, 1 parcial) | Depois da correção de Desenho de casos no passo 11 |

## Medição por papel

Tokens estimados (caracteres/4) por `medir.mjs`, método da phase-7, base `eaa2f3d`, sem teto (decisão 5). Valores da 5.6.0 reproduzidos nesta review.

| Papel | 5.5.0 | 5.6.0 | Variação |
|---|---|---|---|
| lider-sempre | 2.217 | 2.265 | +48 (2,2%) |
| lider-com-delegation | 4.439 | 4.628 | +189 (4,3%) |
| explorador | 671 | 706 | +35 (5,2%) |
| implementador | 1.886 | 3.264 | +1.378 (73,1%) |
| verificador | 1.730 | 2.993 | +1.263 (73,0%) |
| redator-spec | 6.204 | 7.091 | +887 (14,3%) |
| redator-plan | 6.625 | 8.886 | +2.261 (34,1%) |
| revisor-analyze | 6.301 | 8.650 | +2.349 (37,3%) |
| revisor-review | 8.625 | 10.937 | +2.312 (26,8%) |
| lider-high-completa | 14.477 | 16.963 | +2.486 (17,2%) |
| templates/AGENTS.md | 1.450 | 1.451 | +1 (0,1%) |
| bloco CADEIA | 341 | 341 | 0 |
| AGENTS.md raiz | 2.096 | 2.126 | +30 (1,4%) |

## Aprovação humana

- [ ] Aprovação humana (confirmou no chat o resumo do líder)

## Etapas

### Etapa 1 - review - eaa2f3d..HEAD

- Regressão: `## Regressão completa` do plan, sobre o `HEAD` `cff4584`, árvore limpa, em ordem e sem falha: 1 `git diff --check` (árvore e `eaa2f3d..HEAD`) sem achado; 2 `node --test` código 0 (143 testes declarados); 3 `estado.mjs --json` com `inconsistencias: []`; 4 `governanca.mjs --raiz .` só com os 10 achados `perfil global <host>/<papel> diferente`; 5 `plan.mjs --alvo phase-N` com os códigos 2, 2, 2, 2, 1, 0 e 0 nas phases 1 a 7; 6 `gitleaks detect` sem vazamento (153 commits); 7 revisão de consistência sem contradição (Notas). Nenhum flake
- Duração: lint e tipos (`git diff --check`) 0,09 s; unitários (`node --test`) 44,46 s; scripts de leitura (itens 3 a 5) 0,80 s; gitleaks 2,37 s; E2E não há; total 47,73 s pelo relógio da execução (o item 7 é leitura, fora da conta) · orçamento: 10 minutos, padrão (o `AGENTS.md` não declara)
- Abriu: R1, R2, R3
- Veredito: Request changes
