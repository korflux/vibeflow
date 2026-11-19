# Changelog

O que mudou em cada versão do vibeflow, da mais nova para a mais antiga. Quebra de contrato é major, acréscimo sem quebra é minor e correção é patch.

## 6.7.0

A 6.7.0 é uma versão minor, sem migração de artefato e com mudança no perfil do verificador, com base na palestra "Rethinking Claude Code Best Practices" (Lydia Hallie, Anthropic): o que não se desfaz sai da prosa e vai para o host. O bloco `VIBEFLOW:CADEIA` não muda. O re-init (`/vibeflow init`) é o que oferece os bloqueios a um projeto já inicializado e o que relata o perfil global do verificador como diferente da fonte; a troca dele pede a sua decisão, como toda substituição de perfil.

- O verificador sobe de modelo nos dois hosts (`haiku` para `sonnet` no Claude Code; o nível equivalente no Codex), porque é ele quem julga se a asserção do teste afirma o texto do critério. O checkpoint fica mais caro por despacho.
- Segunda leitura de Critical (`skills/vibeflow/references/review.md`): antes da rodada de correção, um segundo revisor de contexto limpo tenta derrubar cada Critical. Confirmado, a correção segue; refutado, o revisor que abriu o achado decide uma vez se mantém ou retira. O resultado fica na linha `- Segunda leitura:` da etapa do `review.md`, que `scripts/estado.mjs` lê para indicar a etapa. Required e Nit não passam por ela, e o Modo B a dispensa.
- O README passa a recomendar, para o chat do líder, o modelo mais forte de julgamento do host.

- O init ganha o passo Bloqueios do host: no Claude Code, propõe gravar em `.claude/settings.json` as regras `deny` de `skills/vibeflow/templates/claude-settings.json`, com o seu aceite e a decisão registrada em Ambiente no `AGENTS.md`. Recusa registrada não é perguntada de novo.
- A lista de bloqueios cresce: além de staging amplo, amend e force push, entram os comandos que descartam trabalho não commitado e a leitura dos arquivos `.env` de segredo, cada comando com a regra para `Bash` e para `PowerShell`. Antes, a lista só existia no README, só para `Bash`, e no Windows o mesmo comando passava pela outra ferramenta.
- Hook opcional `scripts/encerrar.mjs` (`SubagentStop`), que segura o implementador com caixa sem commit, commit sem caixa ou alteração fora do recorte (Apoios opcionais do host).
- `scripts/conferir.mjs --commit` acusa marca de exclusividade nova em arquivo de teste (`.only` ou equivalente) e avisa marca de pulo nova e arquivo de teste apagado, que só entram com o motivo no relatório (`skills/vibeflow/references/testes.md`, Política de testes). O commit `chore(init): ...` passa a aceitar `.claude/settings.json`.
- `scripts/estado.mjs --json` devolve `semDono`, a lista dos paths não commitados sem dono.
- Nota sobre sandbox e sessão na nuvem nos apoios opcionais, com o limite do Windows nativo.
- O template do `AGENTS.md` passa a guardar só a convenção que o código não mostra. Saem as regras que o modelo já segue sem serem ditas (reuso antes de código novo, causa raiz, validação de entrada, segredo fora do repositório, autorização no servidor) e a seção Segurança por Padrão; as duas regras de erro dela (envelope na borda e exceção de domínio no núcleo) vão para Padrões de Código e Engenharia. A cobertura de segurança continua na interview das phases com `# Risco:` e na review, que abre `skills/vibeflow/references/review/security-and-hardening.md` quando o diff toca essas superfícies. Em projeto existente, o re-init propõe o patch e só aplica o que você aprovar.
- O líder deixa de sugerir, no início, um chat para planejar e outro para implementar em host de contexto curto; a recomendação de chat novo continua quando o contexto pesa (`skills/vibeflow/references/retomada.md`).

## 6.6.0

A 6.6.0 é uma versão minor, sem migração de artefato e sem mudança de perfil. O bloco `VIBEFLOW:CADEIA` não muda e o re-init não é necessário; basta reinstalar o pacote.

- O progresso deixa de dar parte igual a cada etapa e passa a pesar pelo tempo medido (`skills/vibeflow/SKILL.md`, seção 9). Em `high` e `mvp`, spec, plan e analyze valem 5 cada, o implement 70 e a review 15; em medium, implement 75 e review 25. Antes, o fim do analyze já marcava 60%, quando a medição de uma phase real deu cerca de 16% do tempo.
- O checkpoint entra no implement valendo dois passos, e `scripts/estado.mjs` passa a devolver `checkpoints` ao lado de `passos`.
- O líder copia a linha de progresso do `estado.mjs` rodado no momento do informe, sem estimar nem reaproveitar valor anterior.

## 6.5.0

A 6.5.0 é uma versão minor, sem migração de artefato e sem mudança de perfil. O bloco `VIBEFLOW:CADEIA` não muda e o re-init não é necessário; basta reinstalar o pacote.

- A interview propõe dividir a phase quando o pedido junta assuntos independentes ou o mapa indica mais de 20 passos, além da spec que não cabe no limite sem perder critério (`skills/vibeflow/references/disco.md`, Tamanho). O número de critérios deixa de dividir, porque phases de tela passam de 12 critérios com frequência e as phases maiores medidas não tiveram mais achados de review que as menores.
- Limites de tamanho: `spec.md` até 16 KiB e `plan.md` até 24 KiB, ainda como aviso.
- A `spec.md` de `high` e `mvp` entra no Git pelo primeiro commit do alvo, e `scripts/conferir.mjs --commit` acusa a spec fora do Git. Antes, nenhum papel tinha esse staging e ela podia ficar sem commit até o fim da phase.
- `scripts/estado.mjs` não confere de novo o plan de phase fechada, que antes deixava o estado em inconsistência permanente.
- Segunda suíte do benchmark, `tools/bench/divisao.json`, para a decisão de divisão na interview.

## 6.4.1

A 6.4.1 é uma versão patch, sem migração de artefato e sem mudança de perfil. O bloco `VIBEFLOW:CADEIA` não muda e o re-init não é necessário.

- Rota nomeada pelo humano no pedido é a que o líder segue, mesmo abaixo da que a tabela de esforço indica e sem pedir confirmação; abaixo dela, o líder avisa em uma linha qual sinal de risco fica sem cobertura. Sem rota nomeada, vale a tabela (`SKILL.md`, seção 2).
- `tools/bench.mjs`, fora do pacote, roda casos de situação num modelo isolado (`claude -p`), corrige a resposta e compara duas rodadas, para medir se uma mudança na prosa mantém a taxa de acerto. A primeira suíte, `tools/bench/rota.json`, cobre a classificação de rota.

## 6.4.0

A 6.4.0 é uma versão minor, sem migração de artefato e sem mudança de perfil, com base na avaliação do workflow e dos testes de 2026-11-09. O bloco `VIBEFLOW:CADEIA` não muda e o re-init não é necessário.

- A seleção de testes do passo tem uma regra só: em passo de plan vale a `Prova:`, que nomeia os testes, sem somar a seleção por grafo de imports; sem plan (low, medium e correção), vale a seleção por grafo de imports e, quando ela cai na suíte inteira ou não existe, os testes do módulo tocado e dos consumidores diretos.
- A poda de testes sai de `references/testes.md` para `skills/vibeflow/references/testes/poda.md`, lida só no pedido de poda.
- Hook opcional `scripts/barrar.mjs` para o Claude Code, que nega espera por loop e gate recursivo do monorepo no implementador (Apoios opcionais do host).
- `tools/tempo-transcripts.mjs`, fora do pacote, mede o tempo de teste por papel nos transcripts do Claude Code.
- `references/disco.md` abre com a lista das seções e grava o push adiado em `## Aprovação humana` do `review.md`, como o template já dizia.

## 6.3.0

A 6.3.0 é uma versão minor, sem migração de artefato e sem mudança de perfil, com base na revisão dos testes contra os guias da Anthropic, da OpenAI e do GitHub. O bloco `VIBEFLOW:CADEIA` não muda; o re-init só é útil para receber o comentário novo de Comandos do projeto no template do `AGENTS.md`.

- O título do E2E também começa pelo ID do critério, e o checkpoint roda só o E2E do grupo, filtrado pelo título (`--grep`). E2E antigo sem ID roda num segundo comando, pelo path dos arquivos de teste E2E que o diff do grupo toca.
- Falha se confirma rerodando só os arquivos de teste que falharam, pelo path e com os mesmos workers, no checkpoint, na regressão e na re-review, nunca o comando inteiro nem o cache de última execução do runner (`skills/vibeflow/references/testes.md`, Execução).
- A checagem de console em dev roda uma vez, no nível E2E da regressão completa (em low, na prova do brief), e sai do checkpoint.
- Equivalência (caixa, espaços, forma canônica) em teste novo se prova em teste unitário parametrizado da normalização, com uma variante por contexto na integração; caso adversarial existente não conta como duplicata.
- Banco limpo de teste com ordem de preferência: banco modelo migrado uma vez e clonado por arquivo, depois transação com rollback, depois volta ao estado migrado sem migrar de novo.
- Gate de tipos com só a forma recursiva declarada: filtro do gerenciador no pacote tocado, com a recomendação de declarar o comando por pacote.
- `playwright test --only-changed` fica restrito a teste de componente, porque não seleciona E2E pelo código do app alterado.

## 6.2.0

A 6.2.0 é uma versão minor, sem migração de artefato e sem mudança de perfil, com base no relatório sobre testes como gargalo. O bloco `VIBEFLOW:CADEIA` não muda; o re-init só é útil para receber o comentário novo de Comandos do projeto no template do `AGENTS.md`.

- Saída curta em toda execução de teste: reporter mínimo e só falhas e totais no contexto.
- Avaliação com modelo real, benchmark ou medição longa nunca é prova de passo: vira passo próprio de medição, rodado uma vez em segundo plano, com repetições e corte da spec.
- Gate de tipos no pacote tocado e incremental, nunca na forma recursiva do monorepo.
- A execução vermelha roda só o teste novo.
- Poda de testes (`skills/vibeflow/references/testes/poda.md`): pedido medium próprio, proposto quando a regressão passa do orçamento, que remove duplicata, E2E repetido, teste proibido e teste de comportamento removido, sempre citando o teste que fica, e nunca toca prova de critério vigente, caso adversarial, autorização, dinheiro, dado pessoal ou preservação.

## 6.1.0

A 6.1.0 é uma versão minor, sem migração de artefato, com base no relatório de papers sobre workflow com agentes de código. O bloco `VIBEFLOW:CADEIA` não muda. Rode `/vibeflow init` para receber os perfis novos de implementador, explorador e verificador (o init mostra os globais como diferentes da fonte e pede a sua decisão) e recarregue o host.

- Esforço de raciocínio menor: implementador em `medium`, explorador e verificador em `high`. O líder sobe o implementador para `high` só em phase com `# Risco:` ou na segunda prova vermelha do mesmo passo, nunca acima disso.
- `medir.mjs` mede a phase pelo Git: horas de relógio e ativas, passos com retrabalho, intervalo mediano e passo mais lento, R* por severidade. O líder grava a linha em `## Medição` do `review.md` na finalização, para comparar phases e versões.
- O plan vai ao redator que gravou a spec, continuado na mesma thread quando o host permite, com brief só do que mudou e do fatiamento.
- A review julga o diff: o revisor lê do `plan.md` e do `AGENTS.md` só o que a review usa, abre arquivo fora do diff só para seguir um consumidor ou um teste citado, e usa a saída de lint, tipos e testes como prova do achado.

## 6.0.0

A 6.0.0 é uma versão major: muda quem commita o passo, a tabela de rotas e o limite de checkpoints. Artefatos existentes seguem válidos: plan com 3 ou 4 checkpoints só gera aviso, e o formato de commit é o mesmo. Rode `/vibeflow init` em cada projeto consumidor para receber o bloco `VIBEFLOW:CADEIA` novo do `AGENTS.md` e os perfis novos do implementador (o init mostra os perfis globais como diferentes da fonte e pede a sua decisão); depois, recarregue o host.

- Um implementador recebe o trecho inteiro, os passos abertos até o próximo checkpoint ou o fim, e faz os passos em ordem na mesma thread, com um commit por passo: marca a caixa do passo, faz staging só dos `Arquivos:` dele, roda `conferir.mjs --commit` e commita. O líder confere os commits do trecho e continua dono dos demais commits e do push.
- No máximo 2 checkpoints por phase. Phase sem `# Risco:` com até 8 passos não tem checkpoint; o E2E dela roda na regressão completa da review.
- Analyze só com `# Risco:` na spec (sempre no MVP) ou com plan acima de 8 passos. Nos demais casos, com `plan.mjs` sem achado, o líder grava a dispensa em `## Achados do analyze`.
- O plan reaproveita o mapa do explorador feito na interview; o explorador só volta para o critério que o mapa não confirma.
- Tabela de rotas: `high` para pedido ambíguo, migration de schema, autenticação, autorização, pagamento, dado pessoal, segredo, risco de perda de dados, backend cujo fluxo tocado não tem testes ou tela nova sem design system. Backend e banco sem migration, com testes no fluxo tocado, ficam em `medium`.

## 5.7.0

A 5.7.0 é uma versão minor, sem migração de artefato, com foco em tempo por phase. O bloco `VIBEFLOW:CADEIA` e os perfis de subagente não mudam; o re-init só é útil para receber a proposta de enxugar um `AGENTS.md` acima do limite.

- Limites de tamanho em `skills/vibeflow/references/disco.md` (Tamanho): `AGENTS.md` até 32 KiB, `spec.md` até 8 KiB, `plan.md` até 12 KiB e linha de passo até 400 caracteres sem contar `Arquivos:`, sem campo `Nota:`. Desde a 6.5.0, `spec.md` até 16 KiB e `plan.md` até 24 KiB. São avisos de `governanca.mjs` e `plan.mjs`, sem mudar o código de saída; artefato antigo segue válido.
- A pasta da phase guarda só `spec.md`, `plan.md` e `review.md`; `estado.mjs` avisa arquivo a mais, como `passo-<n>.md` ou `baseline.md`.
- Decisão vigente em até 200 caracteres no `AGENTS.md`, com o detalhe no artefato da Fonte. Com `AGENTS.md` acima do limite, o re-init propõe mover para `docs/` o que não é regra, núcleo, comando nem decisão vigente.
- O relatório fixo mora em `skills/vibeflow/references/relatorio.md`, e o brief do implementador traz a linha do passo e o texto dos critérios: o implementador deixa de abrir `delegation.md`, `plan.md` e `spec.md` inteiros a cada passo.
- No passo: um comando de prova só com os testes que o passo cria, altera ou quebra; sem suíte inteira, E2E nem loop de espera; comando longo em segundo plano; cada gate estático uma vez, no fim do passo; varredura de segredos na review.
- Um assunto por phase: com assuntos independentes, ou mais de 8 passos ou 12 critérios previstos, a interview propõe dividir. Desde a 6.5.0, o gatilho de tamanho é mais de 20 passos, e o número de critérios não divide.

## 5.6.0

A 5.6.0 é uma versão minor, sem migração de artefato. Rode `/vibeflow init` em cada projeto consumidor para receber o bloco `VIBEFLOW:CADEIA` novo do `AGENTS.md`: o init acusa o bloco diferente do template e o substitui, com backup. O mesmo comando entrega os perfis atualizados de subagente, entre eles o do verificador: o init mostra os perfis globais instalados como diferentes da fonte e pede a sua decisão, com backup em `~/.vibeflow/old/`. Depois de atualizar os perfis, recarregue o host.

- Checkpoint só por um motivo da tabela fechada de `skills/vibeflow/references/disco.md` (Plan > Checkpoint): caminho fino ou primeiro grupo de risco, segundo grupo de risco, tela e integração, no máximo quatro por phase. Phase com até 5 passos continua sem checkpoint. `plan.mjs` acusa o 5º checkpoint, o motivo fora da tabela e o checkpoint em plan de até 5 passos; checkpoint sem motivo, em plan anterior à tabela, é só aviso.
- Trabalho alheio declarado por você vai para a seção `## Trabalho alheio` do `plan.md`, gravada pelo líder. A phase não para por esses paths, `estado.mjs` e `conferir.mjs --passo` não os acusam, e o staging deles continua acusado.
- Um R* pode listar vários paths entre crases, separados por vírgula, logo depois da severidade; `conferir.mjs` aceita o commit que traz todos eles. R* antigo, de um path, é lido como antes.
- A política de testes de `skills/vibeflow/references/testes.md` passa a ser por qualidade: uma prova principal por critério no nível mais barato que observa o resultado, ID do critério no título do teste quando o brief ou a spec o tem, asserção conferida contra o texto do critério pelo verificador e pelo revisor, remoção de teste duplicado e a seção O que não testar. O E2E fica para critério com tela ou jornada, roda sobre build de produção com uma pilha por execução, e a captura de tela sai da execução de quem o roda.
- O analyze aponta critério cujo passo não tem prova que o teste e, ao fechar, o líder mostra o plan como guia, com um tópico por passo e por checkpoint.
- Cada passo que toca código roda, sobre os arquivos alterados, os gates estáticos declarados nos Comandos do projeto do `AGENTS.md` e os cita no campo `prova`.
- Decisão de autenticação, autorização, segurança ou dados é sempre perguntada a você na interview e no MVP, nunca assumida.
- O `# Status:` do `review.md` tem regra única: o revisor grava `rascunho` ou `request-changes`, e só o líder grava `aprovado`.

## 5.5.0

A 5.5.0 é uma versão minor, sem migração de artefato. Rode `/vibeflow init` em cada projeto consumidor para receber o bloco `VIBEFLOW:CADEIA` novo do `AGENTS.md`: o init acusa o bloco diferente do template e o substitui, com backup. O mesmo comando entrega os perfis novos de subagente: o init mostra os perfis globais instalados como diferentes da fonte e pede a sua decisão, com backup em `~/.vibeflow/old/`. Depois de atualizar os perfis, recarregue o host.

- Explorador, redator, verificador e revisor leem só a referência do próprio papel (`references/<papel>.md`), como o implementador, em vez do `SKILL.md` inteiro.
- O `SKILL.md` fica enxuto para o líder: Interromper, retomada e Modo B passam para `references/retomada.md`, e Ajuste de phase para `references/ajuste.md`.
- O bloco `VIBEFLOW:CADEIA` fica com a tabela de esforço, os sinais que tiram do low e um ponteiro para a skill.
- Cada regra tem uma casa só: commits, staging, posição e marcação do checkpoint em `references/disco.md`; ambiente local e Docker nos testes em `references/ambiente.md`; backup de arquivo de regra em `references/init.md`; execução do checkpoint e Desenho do E2E em `references/verificador.md`; regressão completa e Orçamento de duração em `references/review/passos.md`; checklist do analyze em `references/analyze/coverage.md`.
- Gates, regras de commit, encadeamento, checkpoint e Modo B não mudam de comportamento, e o contrato de disco segue igual.

## 5.4.0

A 5.4.0 é uma versão minor, sem migração. Rode `/vibeflow init` para atualizar os perfis globais de subagente e montar a seção `## Núcleo do projeto` do `AGENTS.md`.

- Cada phase tem no máximo dois checkpoints: um depois do primeiro grupo de risco e, se a phase tem tela, um depois do primeiro grupo que entrega tela. Phase com até 5 passos não tem checkpoint. Desde a 5.6.0, o checkpoint segue a tabela de motivos, até quatro por phase.
- O verificador não reroda a prova dos passos: roda o E2E dos critérios com tela ou jornada do grupo e confere o diff do grupo contra os critérios. O E2E das demais telas e jornadas fica para a regressão completa da review.
- Um passo tem no máximo 12 entradas de código em `Arquivos:`, sem contar testes; acima disso, o plan divide o passo. `plan.mjs` aponta o passo acima do teto e o excesso de checkpoints.
- Fato verificável é conferido pelo explorador antes da spec, e todo valor em Decisões e Critérios de aceite traz a origem (`humano`, `assumida` ou `verificado`). O fechamento da spec lista as assumidas, e `plan.mjs --spec` aponta valor sem origem em spec nova.
- Na interview, tela nova, site ou fluxo novo cobre navegação, páginas e jornada; o limite de duas perguntas vale só para ajuste de tela.
- O implementador lê só a referência própria, `references/implementador.md`, e recebe no brief o mapa do explorador e os itens do núcleo que abre. O líder escolhe o esforço de raciocínio do implementador a cada despacho, até `xhigh`. Desde a 6.1.0, o padrão é `medium` e o teto é `high`.
- O `AGENTS.md` ganha a seção `## Núcleo do projeto`, que o líder abre ele mesmo quando o pedido a toca e usa para conferir a direção das entregas; `governanca.mjs` avisa quando ela falta.

## 5.3.0

A 5.3.0 é uma versão minor, sem migração. Rode `/vibeflow init` para atualizar os perfis globais de subagente.

- Critérios de aceite com forma fixa (contexto, ação e resultado observável), critério de falha quando há entrada externa, autorização ou dinheiro, tabela de exemplos para cálculo exato e critério de preservação do que já funciona.
- `plan.mjs --spec` confere a forma da spec antes da aprovação, inclusive adjetivo vago no critério.
- Testes com vermelho antes do verde: o teste do critério falha antes da mudança e passa depois, com as duas execuções no relatório.
- Nova seção Desenho de casos em `references/testes.md`: limites, classes, transições, autorização e determinismo. Desde a 5.6.0, a regra de mock só na fronteira fica na seção O que não testar.
- Na rota medium, os critérios do brief vão no corpo do commit `task(medium): ...`, e a review os lê de lá; `conferir.mjs` acusa o commit sem eles.
- O plan começa pelo caminho mais fino de ponta a ponta ou pela suposição mais arriscada.
- O perfil revisor sobe para esforço alto nos dois hosts.

## 5.2.0

A 5.2.0 é uma versão minor, sem migração.

- Três scripts de leitura novos apoiam o líder e o revisor sem conduzir etapa: `conferir.mjs` (recorte do passo e conferência antes do commit), `plan.mjs` (forma do plan e cobertura dos critérios) e `governanca.mjs` (resultado do init e backup).
- O `estado.mjs` ganhou `--slug`, que aplica a regra do slug, e `--linha`, para a statusline.
- O init passa a tratar como idêntico o perfil global que difere da fonte só na quebra de linha (CRLF ou LF) ou no BOM.
- Hook `commit-msg`, bloqueios e statusline do Claude Code ficam documentados como apoios opcionais.

## 5.1.0

A 5.1.0 é uma versão minor, sem migração.

- As regras de teste ficam numa referência única, `skills/vibeflow/references/testes.md`.
- Os testes locais preferem serviços nativos ou embutidos a containers; em projeto que já usa Docker nos testes, o líder pergunta uma vez se você prefere migrar para uma forma mais leve. Desde a 5.5.0, essa regra vive em `skills/vibeflow/references/ambiente.md`.
- O E2E é leve e roda em paralelo.
- A regressão completa tem orçamento de duração, de 10 minutos por padrão; acima dele, o revisor registra um alarme sem bloquear a entrega.

## Migração para a 5.0.0

A 5.0.0 é uma versão major: muda artefatos, rotas e papéis.

- Phases fechadas no formato antigo (com `interview.md`, `design.md`, `analyze.md`, rotas `xhigh` ou `max`, ou tasks `T*`) ficam como estão e são reconhecidas como fechadas.
- Uma phase aberta no formato antigo deve ser fechada com a versão anterior da skill antes de atualizar; a 5.0.0 a relata como inconsistência e não a conduz.
- O perfil global `corretor` de versões anteriores é relatado pelo init como obsoleto e preservado; removê-lo exige a sua decisão.
