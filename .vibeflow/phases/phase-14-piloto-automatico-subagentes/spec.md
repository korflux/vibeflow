# Spec: Piloto automático de implementação com subagentes
# Alvo: phase-14-piloto-automatico-subagentes
# Status: aprovado

## Objetivo

Quem conduz uma phase VibeFlow num host com subagentes passa a implementar a fila inteira num único chat: um coordenador delega cada T* a um subagente, confere, commita, envia a review a outro subagente, corrige e só volta ao humano no fim, para confirmar push e decisões vigentes, ou quando houver ambiguidade material ou impedimento real. O analyze passa a rodar em subagente a partir do chat do plan. Hosts sem subagentes continuam com a execução de uma T* por run. Sucesso é uma phase com plan aprovado terminar com um `/vibe-implement` e uma pergunta final, com o `plan.md` sempre suficiente para retomar a run em outro chat.

## Cobertura da origem

| Origem | Destino na spec | Motivo se fora/N/A |
|---|---|---|
| Fluxo de chats: interview → spec → design no mesmo chat; novo chat recomendado para o plan | Decisão 2 | Comportamento atual mantido; spec não vai para subagente |
| Analyze em subagente | F1, A1 | N/A |
| Recomendação forte de chat novo para o implement | F1, A2 | N/A |
| Modo A: coordenador e implementador por T* | F2, A3 | N/A |
| Review em subagente, corretor e limite de 2 rodadas | F3, A4 | N/A |
| Pergunta única de push e decisões vigentes | F4, A5 | N/A |
| Paradas, instalação e prova vermelha | F5, A6, A10 | N/A |
| Mapeamento contínuo e retomada pelo disco | F5, A7 | N/A |
| Modo B e fallback sem subagentes | F6, A8 | N/A |
| Papéis em `references/delegation.md` | Decisões 1, 6; A9 | N/A |
| Regra de onde a delegação vive nos repos dos usuários | Decisão 1 | Seam fechado nesta spec |
| Versão major | A11 | N/A |
| Paralelismo, `Arquivos:`, disjunção, worktree, pacote de contexto por T* | Fora | Phase seguinte |
| Fan-out da review por dimensão | Fora | Decidido no debate |

## Suposições e decisões

1. A regra de delegação vive nas skills que delegam: `vibe-plan` (delega o analyze) e `vibe-implement` (delega implementador, verificador, revisor e corretor). Cada uma carrega uma cópia idêntica de `references/delegation.md`. A tabela "Continuidade entre chats" do `AGENTS.md` deste repo é atualizada só para documentar o fluxo; o template do `vibe-init` não muda, para não criar segunda fonte nos repos dos usuários. — (processo; fechado nesta spec)
2. Interview, spec e design continuam podendo seguir no mesmo chat, e o plan continua com recomendação de chat novo, como hoje. A spec não é delegada. — (processo; fechado na interview e corrigido no analyze, que citava o plan no mesmo chat por engano)
3. Separar chats continua sendo recomendação, nunca gate. O fechamento do plan recomenda com ênfase um chat novo para o implement; se o humano insistir em continuar, o agente segue. — (processo; fechado na interview)
4. `/vibe-implement` num host com subagentes e com `plan.md` aprovado inicia o Modo A sem perguntar o modo. O Modo B entra quando o humano pede execução de uma T* por vez, nomeia uma T* específica ou o host não oferece subagentes; nesse último caso o agente avisa o motivo em uma linha. — (processo; fechado na interview)
5. No Modo A, o coordenador não escreve código. Ele seleciona a T*, delega, confere o diff e o relatório, registra artefatos e opera o Git. Toda mudança de código passa por um subagente, inclusive correções pequenas, para manter um único dono de cada papel. — (processo)
6. Papéis são descritos por perfil, nunca por nome de modelo: `explorador` (leitura e busca, perfil rápido e barato), `verificador` (executa provas e devolve resumo, perfil barato), `implementador`/`corretor` (escreve código da T* ou do R*, perfil padrão do host), `revisor` (executa a review, perfil forte). Host que não permite escolher modelo por subagente usa o padrão. Subagente que não consegue abrir outro subagente executa explorador e verificador inline. — (processo)
7. Relatório de subagente é evidência a conferir, nunca autoridade. O coordenador confere paths citados, diff real e saída da prova antes de registrar. — (processo; já é regra para saída de script no `AGENTS.md`)
8. Escritor único: somente o coordenador altera `plan.md`, `spec.md`, `review.md`, `AGENTS.md` e o índice Git e cria commits. Subagentes devolvem relatório. O subagente revisor é a exceção controlada: ele escreve o `review.md` vivo, porque esse é o artefato da própria skill, e não toca Git nem `AGENTS.md`. O subagente de analyze escreve `analyze.md` e aplica as correções diretas que a skill de analyze já prevê em spec, design e plan. — (processo)
9. A prova da T* executada pelo implementador vale como prova do estado integrado, porque no Modo A sequencial ele trabalha na mesma árvore. O coordenador não repete a prova; ele confere a saída devolvida e repete só quando o relatório não traz evidência suficiente ou o diff contradiz o relatório. — (processo; fechado no debate)
10. O ciclo review → correção tem no máximo 2 rodadas de correção. Cada rodada termina com nova review. Se a review seguinte à 2ª correção ainda tiver Critical ou Required em aberto, o coordenador para e relata. Ajustes pedidos pelo humano na pergunta final não contam para o limite. — (processo; fechado no debate)
11. Não há regra especial para R* Critical: o corretor resolve como qualquer R*. Se a correção exigir decisão, ela cai na parada por ambiguidade material. O relatório final destaca os Critical encontrados e corrigidos. — (processo; fechado no debate)
12. Hash de commit não é registrado no `plan.md`. O Git é a fonte: cada commit de task segue `task(Tn): <outcome>`, e a retomada localiza o commit pela mensagem. O coordenador informa os hashes no relatório final. Isso mantém a decisão 5 da phase 13 e evita residual fora do commit da task. — (processo; resolve o ponto deixado para a spec na interview)
13. Instalar ferramenta ausente necessária à prova é permitido em plan, implement e review, pelo gerenciador do projeto ou fonte oficial, quando o ambiente e as permissões permitirem. O plan registra a ausência e a ação de instalar na T* que depende dela. Instalação que exija credencial, criação de conta, pagamento, elevação administrativa ou configuração persistente de integração (por exemplo, registrar um MCP) é impedimento real e vai ao humano. — (segurança / processo; fechado no debate)
14. Prova vermelha não é impedimento. O agente corrige a causa raiz sem limite numérico de tentativas e só pergunta quando a solução depende do humano ou muda um aceite da spec. Enfraquecer, pular ou apagar teste para obter verde é proibido; mudar uma asserção exige justificativa ligada ao aceite. — (processo; fechado no debate)
15. O motor do implement passa a informar a etapa da phase lida do disco, para que retomada e coordenação não dependam da memória do chat. A etapa é derivada de `plan.md` e `review.md`; o motor não decide semântica nem escreve artefato. — (processo)
16. Grupos paralelos já registrados em plans continuam válidos só no Modo B, com o comportamento atual de oferecer o grupo ao humano. O Modo A desta phase é sequencial e ignora o grupo até a phase de paralelismo. — (escopo)
17. Quando a rota exige analyze (MVP ou phase max), o handoff do plan é `vibe-analyze`, também em phase max. Hoje o plan só cita o MVP e o implement redireciona depois; a delegação do analyze precisa saber disso no próprio chat do plan. — (processo)
18. A mudança altera comportamento que o humano já usa (Modo A e Modo B atuais), então é versão major. — (versionamento)

## Escopo e comportamento

### 1. Fluxo F1: analyze delegado no chat do plan

- Jornada: transição plan → analyze → implement.
- Rota: max (MVP ou phase).
- Gatilho: humano aprova o plan e pede a próxima porta ("pode ir pro analyze", "pode ir para a próxima fase").
- Pré-condição: `plan.md` aprovado; rota exige analyze.
- Superfície por passo: N/A, fluxo operacional de agente; superfícies são chat e arquivos vivos.
- Passos:
  1. O agente do plan verifica se o host oferece subagentes [superfície: N/A].
  2. Com suporte, delega a `vibe-analyze` a um subagente com o alvo da phase; o subagente grava `analyze.md`, aplica correções diretas previstas pela skill e devolve veredito, correções aplicadas e perguntas em aberto [superfície: arquivo `analyze.md`].
  3. O agente do plan faz as perguntas em aberto ao humano, uma por vez, aplica as respostas nos artefatos e registra em `analyze.md` [superfície: chat e arquivos vivos].
  4. O humano aprova o analyze no chat do plan; o agente marca o status conforme a skill de analyze [superfície: arquivo `analyze.md`].
  5. O agente fecha recomendando com ênfase um chat novo com `/vibe-implement` e informa que ele rodará em Modo A [superfície: chat].
  6. Sem suporte a subagentes, o comportamento atual se mantém: recomendação de chat novo para o analyze [superfície: chat].
- Validações: subagente de analyze não implementa código e não cria commit; veredito bloqueado impede recomendar o implement.
- Erros: erros do motor de analyze seguem os códigos da skill e não são contornados.
- Estados: analyze delegado, aguardando clarificação, aprovado limpo, bloqueado, fallback sem subagente.
- Aceite: A1, A2.
- Reutilizar: `vibe-analyze` sem mudança de contrato de disco.

### 2. Fluxo F2: Modo A, coordenação das T*

- Jornada: implementação da fila inteira.
- Rota: high, xhigh e max com `plan.md` aprovado (e analyze aprovado e limpo quando a rota exige).
- Gatilho: `/vibe-implement` num host com subagentes, sem pedido de Modo B.
- Pré-condição: gates atuais do implement satisfeitos.
- Superfície por passo: N/A, fluxo operacional de agente.
- Passos:
  1. O coordenador executa o motor, lê alvo, fila e etapa, e confere `plan.md`, `review.md` e Git [superfície: N/A].
  2. Seleciona a T* elegível de menor número e registra no `plan.md` o checkpoint de retomada da T* em execução [superfície: arquivo `plan.md`].
  3. Delega a T* a um subagente implementador com: ID, aceite, `Spec:`, `Deps`, verificação planejada, `Visual`, paths conhecidos, regras do ciclo da fatia do `vibe-implement` (reconhecer, codar, simplificar, provar) e proibições da decisão 8 [superfície: N/A].
  4. O implementador devolve relatório fixo: estado (`verde`, `bloqueado` ou `pergunta`), paths alterados, prova (comando e resultado), pendências e, se houver, a pergunta [superfície: N/A].
  5. O coordenador confere o relatório contra `git status`, o diff e a saída da prova. Divergência gera nova delegação da mesma T* com o problema descrito [superfície: N/A].
  6. Com prova verde conferida, o coordenador registra a T* no `plan.md` (status, paths, prova), marca A*/C* provados na spec, remove o checkpoint e cria o commit `task(Tn): <outcome>` com staging explícito [superfície: arquivos vivos e Git].
  7. Repete a partir do passo 2 enquanto houver T* elegível; com fila concluída segue para F3 [superfície: N/A].
  8. Relatório `pergunta`: o coordenador pergunta ao humano e segue com T*s elegíveis que não dependem da T* parada; sem elegível independente, aguarda a resposta [superfície: chat].
- Validações: subagente não altera artefatos vivos, índice Git nem commits; paths fora da T* no diff bloqueiam o commit até serem atribuídos ou removidos; uma T* por commit.
- Erros: códigos atuais do motor (`IMPLEMENT_*`, `INIT_AUSENTE`, `MVP_INESPERADO` etc.) não são contornados.
- Estados: delegando, conferindo, registrada, aguardando humano, parada.
- Aceite: A3, A6.
- Reutilizar: ciclo da fatia e commit da task do `vibe-implement`; checkpoint de retomada existente.

### 3. Fluxo F3: review e correção no piloto

- Jornada: fechamento da fila.
- Rota: a mesma do F2.
- Gatilho: fila concluída no Modo A.
- Pré-condição: todas as T* concluídas com commit.
- Superfície por passo: N/A, fluxo operacional de agente.
- Passos:
  1. O coordenador delega a review final a um subagente revisor, que executa `vibe-review` no alvo, grava a etapa em `review.md` e devolve veredito, R* abertos e fechados, Critical encontrados, decisões para vigência e perguntas [superfície: arquivo `review.md`].
  2. Approve: segue para F4 [superfície: N/A].
  3. Request changes: o coordenador delega os R* Critical e Required abertos a um subagente corretor, confere como no F2, marca os R* provados em `review.md` e cria o commit da correção [superfície: arquivos vivos e Git].
  4. Delega nova review (passo 1). Após a 2ª rodada de correção, se a review seguinte ainda tiver bloqueio, para e relata os R* restantes [superfície: chat].
  5. Pergunta do revisor que define o veredito é feita ao humano pelo coordenador [superfície: chat].
- Validações: revisor não toca Git nem `AGENTS.md`; corretor não edita `review.md`; R* só recebe `[x]` com prova.
- Erros: códigos atuais do motor de review não são contornados.
- Estados: revisando, corrigindo (rodada 1 ou 2), aprovado aguardando confirmação, parado sem convergência.
- Aceite: A4.
- Reutilizar: `vibe-review` (review final, etapas no mesmo arquivo, severidades) sem mudança de contrato de disco.

### 4. Fluxo F4: confirmação única e fechamento

- Jornada: encerramento da phase.
- Rota: a mesma do F2.
- Gatilho: review final com Approve.
- Pré-condição: fila concluída, sem Critical ou Required em `[ ]`.
- Superfície por passo: chat e arquivos vivos.
- Passos:
  1. O coordenador apresenta um relatório curto: T*s e hashes, rodadas de correção, Critical encontrados e corrigidos, decisões para vigência e o pedido único de confirmação (aprovar a review, publicar as decisões listadas e fazer push) [superfície: chat].
  2. Confirmação: executa a finalização da `vibe-review` (status aprovado, sync de decisões vigentes, commit residual quando houver, `git push` sem `--force`) e informa hash, paths e resultado [superfície: arquivos vivos, Git e chat].
  3. Ajuste pedido pelo humano: trata como correção (F3 passo 3) e volta ao passo 1, sem contar para o limite de rodadas [superfície: chat].
- Validações: sem confirmação explícita, nenhuma sincronização de `AGENTS.md`, commit residual ou push.
- Erros: falha de commit ou push mantém a phase aberta e é informada com causa segura.
- Estados: aguardando confirmação, finalizada, ajuste em andamento, push falhou.
- Aceite: A5.
- Reutilizar: finalização Git da phase da `vibe-review`.

### 5. Fluxo F5: paradas e retomada

- Jornada: interrupção e continuidade da run.
- Rota: Modo A e Modo B.
- Gatilho: impedimento, ambiguidade, queda do chat ou novo `/vibe-implement` com phase em andamento.
- Pré-condição: phase com `plan.md`.
- Superfície por passo: chat e arquivos vivos.
- Passos:
  1. Ferramenta ausente: instala conforme decisão 13 e segue [superfície: N/A].
  2. Impedimento real (credencial ou segredo ausente, serviço externo indisponível, permissão negada pelo humano, ação proibida, erro de proteção do motor) ou ambiguidade material: grava o checkpoint de retomada, relata a tentativa, o impedimento e a recomendação, e aguarda [superfície: arquivo `plan.md` e chat].
  3. Prova vermelha: corrige a causa raiz conforme decisão 14 e segue [superfície: N/A].
  4. Retomada: um chat novo com `/vibe-implement` lê a etapa informada pelo motor, o checkpoint, o `review.md` e o Git, valida o snapshot da prova e continua do ponto correto sem repetir T* concluída [superfície: N/A].
- Validações: checkpoint com `HEAD` e hashes dos inputs da prova, como hoje; prova sem snapshot suficiente é invalidada.
- Erros: etapa que o motor não consegue derivar vira aviso, não chute.
- Estados: em execução, parado por impedimento, aguardando decisão, retomado.
- Aceite: A6, A7, A10.
- Reutilizar: checkpoint de retomada atual do `vibe-implement`.

### 6. Fluxo F6: Modo B e fallback

- Jornada: implementação acompanhada T* a T*.
- Rota: a mesma do F2.
- Gatilho: humano pede uma T* por vez, nomeia uma T* ou o host não oferece subagentes.
- Pré-condição: gates atuais do implement.
- Superfície por passo: chat.
- Passos:
  1. Executa uma T* com o comportamento do Modo A atual: ciclo da fatia inline, registro, commit e resposta final [superfície: chat e Git].
  2. "Pode seguir" executa a próxima T* no mesmo chat; a recomendação de chat novo por T* e para review continua consultiva [superfície: chat].
  3. Grupo paralelo registrado no plan continua sendo oferecido ao humano como hoje [superfície: chat].
- Validações: o antigo Modo B (plano inteiro inline num único contexto) deixa de existir; pedido de "executar tudo" sem subagentes executa a próxima T* em Modo B e informa a limitação.
- Erros: os mesmos do implement atual.
- Estados: T* concluída, aguardando "pode seguir", handoff para review.
- Aceite: A8.
- Reutilizar: Modo A atual do `vibe-implement`.

### Fora

- Paralelismo no Modo A, contrato `Arquivos:` obrigatório, checagem de disjunção no `plan.py`, worktree por T* e pacote de contexto por T* — phase seguinte, depende do piloto sequencial estável.
- Fan-out da review por dimensão — custo de tokens maior sem necessidade comprovada.
- Delegação de spec, design ou interview e explorador nessas etapas — decidido no debate; spec fica no chat.
- Regra de delegação no template `AGENTS.md` do `vibe-init` — criaria segunda fonte concorrendo com as skills.
- Nomes de modelo em skill ou referência — envelhecem e variam por host.
- Skill nova de orquestração — opção 2 descartada no debate.

## Checklist de entrega

### Aceite

- [ ] A1: Com rota que exige analyze e host com subagentes, o chat do plan delega o analyze, conduz as clarificações e a aprovação no próprio chat; sem subagentes, mantém a recomendação atual. O handoff do plan aponta `vibe-analyze` também em phase max.
- [ ] A2: O fechamento do plan (e do analyze, quando houver) recomenda com ênfase um chat novo para `/vibe-implement` e informa que ele rodará em Modo A, sem bloquear a continuidade.
- [ ] A3: No Modo A, cada T* é implementada por subagente, conferida pelo coordenador e registrada com um commit `task(Tn)` próprio; apenas o coordenador altera artefatos vivos e Git.
- [ ] A4: Com a fila concluída, a review roda em subagente; Request changes aciona corretor e nova review, com no máximo 2 rodadas de correção antes de parar e relatar.
- [ ] A5: O piloto termina com uma única pergunta de confirmação (review, decisões vigentes e push) e, confirmado, executa a finalização da `vibe-review`; o relatório final destaca os Critical corrigidos e lista os hashes.
- [ ] A6: O piloto só interrompe por ambiguidade material ou impedimento real; ferramenta ausente é instalada e prova vermelha é corrigida sem enfraquecer teste.
- [ ] A7: Uma run interrompida retoma num chat novo a partir de `plan.md`, `review.md`, Git e da etapa informada pelo motor, sem refazer T* concluída nem prova ainda válida.
- [ ] A8: O Modo B executa uma T* por run, entra por pedido ou por falta de subagentes, e o antigo modo de plano inteiro inline não existe mais.
- [x] A9: `vibe-plan` e `vibe-implement` contêm `references/delegation.md` idênticos, com papéis por perfil, formato de relatório, regras de escritor único e fallback.
- [ ] A10: Plan, implement e review seguem a mesma regra de instalação de ferramentas, com as exceções de credencial, conta, pagamento, elevação e configuração persistente.
- [x] A11: `ARQUITETURA.md` e `ANALISE.md` das skills alteradas, a tabela de continuidade do `AGENTS.md` deste repo e `docs/ESCOPO.md` refletem o novo fluxo, e a versão publicada sobe como major.

### Critérios de sucesso

- [x] C1: Os motores Python e PowerShell do implement informam a mesma etapa e o mesmo número de rodadas de correção para fixtures de: T* abertas elegíveis, T* abertas bloqueadas, fila concluída sem review, review com bloqueio aberto, review com bloqueios fechados aguardando nova review, Approve aguardando confirmação e phase finalizada; `review.md` ilegível gera aviso sem etapa inventada.
- [x] C2: O teste de distribuição falha quando as cópias de `references/delegation.md` divergem e passa quando são idênticas.
- [ ] C3: Execução piloto real num repo de teste descartável, com plan aprovado de pelo menos 3 T*s e ao menos uma prova inicialmente vermelha, termina com um único `/vibe-implement` e uma única pergunta final; uma segunda execução interrompida no meio retoma em chat novo do ponto correto. A evidência fica registrada no plan desta phase.
- [x] C4: As suítes existentes de contrato das skills e de distribuição continuam verdes.

## Contratos e restrições necessárias

- Dados e invariantes: escritor único dos artefatos vivos e do Git (decisão 8); uma T* por commit; hash fora do `plan.md` (decisão 12); checkpoint de retomada com snapshot Git como hoje.
- Integrações e interfaces: o JSON do motor do implement ganha a etapa da phase e as rodadas de correção usadas, com os mesmos nomes nos motores Python e PowerShell; campos existentes (`alvo`, `fila`, `avisos`, `analyze_gate`) não mudam. Relatório de subagente segue formato fixo definido em `references/delegation.md`.
- Segurança e operação: subagentes herdam as proibições do implement (sem push, sem `git add -A`, sem enfraquecer teste, sem segredos em código); instalação segue a decisão 13; push e sync de `AGENTS.md` só com confirmação humana. Entrada externa: N/A, o motor lê apenas arquivos da própria phase.
- Tecnologia imposta: motores em Python 3 e PowerShell 7 com flags públicas iguais; testes só com `unittest`; testes não verificam texto de `SKILL.md`, templates ou referências, exceto igualdade de bytes entre cópias distribuídas.

## Como provar

| Aceite | Evidência esperada |
|---|---|
| A1 | Na execução piloto de rota max, o chat do plan delega o analyze e o `analyze.md` aparece gravado pelo subagente, com clarificações registradas |
| A2 | Mensagem de fechamento do plan na execução piloto contém a recomendação de chat novo e o anúncio do Modo A |
| A3 | `git log` do repo piloto mostra um commit `task(Tn)` por T*, e o `plan.md` registra cada T* com paths e prova |
| A4 | `review.md` do repo piloto mostra etapas de review e correção dentro do limite; fixture de motor com 2 rodadas usadas informa parada |
| A5 | Transcript do piloto mostra uma única pergunta final; após confirmação, `review.md` aprovado e push registrado (ou remoto local de teste) |
| A6 | Transcript do piloto mostra a prova vermelha corrigida sem pergunta ao humano e sem asserção enfraquecida no diff |
| A7 | Segunda execução piloto interrompida retoma em chat novo pela etapa do motor, sem novo commit para T* já concluída |
| A8 | Execução com pedido de uma T* por vez conclui só uma T*; não existe mais caminho de plano inteiro inline nas skills |
| A9 | Teste de distribuição compara os bytes das duas cópias de `delegation.md` |
| A10 | Na execução piloto, ferramenta ausente necessária à prova é instalada e registrada no plan |
| A11 | Diff da phase contém os documentos e a versão major; suítes de contrato verdes |

## Boundaries

### Always

- Conferir relatório de subagente contra diff, `git status` e saída da prova antes de registrar.
- Registrar cada transição no `plan.md` antes de seguir para a próxima.
- Manter um commit por T* e staging explícito por path.
- Avisar em uma linha quando o Modo A não estiver disponível e o Modo B for usado.

### Ask first

- Instalação que exija credencial, conta, pagamento, elevação administrativa ou configuração persistente de integração.
- Mudança de aceite da spec para resolver prova vermelha.
- Confirmação final de review, sync de decisões vigentes e push.

### Never

- Subagente alterar artefatos vivos fora do seu papel, índice Git, commit ou `AGENTS.md`.
- Enfraquecer, pular ou apagar teste para obter verde.
- Push, `git add -A`, amend, squash ou force push.
- Exceder 2 rodadas de correção sem parar e relatar.
- Nome de modelo em skill ou referência.

## Handoff

vibe-plan
rota: max

- Design: N/A, a entrega não tem UI visível.
- Chat: `interview`, `spec` e, com UI, `design` podem continuar no mesmo chat. Recomende novo chat para `vibe-plan`; se o humano preferir, continuar no mesmo chat não bloqueia. O `spec.md` vivo é a ponte.

- [x] Aprovação humana (leu o arquivo e confirmou)
