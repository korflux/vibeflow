---
name: vibe-implement
description: >
  Implementa e prova mudanças em código de software, registra cada T* concluída no plan.md e cria seu commit local; num host com subagentes, conduz a fila inteira da phase (implementação, review e correção) com uma única confirmação final. Use when the user runs /vibe-implement, pede código, build, correção de bug, alteração de UI em código ou execução de T* de software, mesmo que não diga vibe-implement. Não se aplica a redação ou edição apenas de texto e documentos.
---

# vibe-implement

Sem prova verde, não marque `[x]` nem faça commit. No protocolo `etapas-v1`, o Modo A cria um commit integrado das T* comprovadas; Modo B e plans sem marcador mantêm commit por task, sem push; no Modo A, o push só ocorre na finalização confirmada pelo humano (§6). `plan.md` é o registro único; não crie `implement.md`, `todo.md` ou `tasks.md`. No fluxo padrão, sem `.vibeflow/`: `/vibe-init`. No MVP, código exige analyze aprovado e limpo.

## 0. Classificar Express e usar o script

1. Antes de exigir `.vibeflow/` ou rodar script, separe texto/documento avulso de código de software. Texto puro segue edição direta, fora desta skill. Express é mudança de código clara e localizada, sem comportamento novo, como cor ou espaçamento na UI. Faça patch e checagem proporcionais; não rode `vibe-init` nem crie ou exija `.vibeflow/`. Na entrega atual, atualize a T* aberta ou acrescente uma T* curta ao plan existente; achado de review atualiza o R* existente. Reuse o design existente quando couber. Alterar comportamento, rota, interação, aceite, acessibilidade ou tocar privacidade, obrigação jurídica, autenticação, autorização, pagamento, segredo, persistência ou perda de dados sai do Express e segue a cadeia aplicável.
2. Fora do Express, se encontrar `.vibeflow/REGRAS.md`, `REGRAS.md` ou `CLAUDE.md` de uma instalação anterior, execute `vibe-init` para migrar as regras e retome a implementação. Fontes divergentes continuam para consolidação. Leia o motor antes de executá-lo: `scripts/implement.ps1` no Windows ou `scripts/implement.py` no Unix. Ele seleciona alvo e fila e deriva a etapa da phase; não cria artefato. Execute no repo com `pwsh "<skill>/scripts/implement.ps1"` ou `bash "<skill>/scripts/implement.sh"`. Para MVP, acrescente `-Mvp` ou `--mvp`.
3. Leia o JSON no stdout: `alvo`, `fila`, `etapa`, `rodadas_correcao` e `avisos` (`analyze_gate` no MVP). `etapa` é `implementar`, `testar`, `validar`, `corrigir_validacao`, `commitar_integracao`, `revisar`, `corrigir`, `confirmar`, `bloqueada` ou `concluida`, e é `null` quando o disco não permite derivá-la; nesse caso leia os `avisos`, o plan e o review, e não invente a etapa. Escolha pela `fila.elegiveis`. Localize regras, paths e símbolos com `rg --files` e `rg -n`; abra apenas o fluxo relevante, não a árvore inteira.

No fluxo padrão, `INIT_AUSENTE` exige init. `IMPLEMENT_SEM_ALVO`, `IMPLEMENT_SEM_PLAN`, `IMPLEMENT_ANALYZE_AUSENTE`, `IMPLEMENT_ANALYZE_RASCUNHO`, `IMPLEMENT_ANALYZE_BLOQUEADO`, `MVP_INESPERADO`, `MODO_INVALIDO`, `FASE_AUSENTE` e `PHASES_INESPERADO` não são contornados.

## 1. Selecionar o modo

Escolha internamente a rota `low|medium|high|xhigh|max`; não anuncie rota, alvo ou fila na abertura do chat. “Ok” ou “aprovado”, isoladamente, não autoriza avançar.

| Modo | Quando | O que executa |
|---|---|---|
| A (padrão) | rota `high`, `xhigh` ou `max`, `plan.md` aprovado, host com subagentes e nenhum pedido de Modo B | a fila inteira da phase, do plan à confirmação final (§3 e §6) |
| B | o humano pede uma T* por vez ou nomeia uma T*; o host não oferece subagentes; ou a rota é `low` ou `medium` | uma T* por run, com o ciclo da fatia inline (§4) |
| Avulso | `low` ou `medium` sem plan | uma mudança inline com prova proporcional, sem fila e sem coordenação |

Entre no Modo A sem perguntar o modo. Quando o Modo B vier da falta de subagentes, avise o motivo em uma linha. Um pedido de executar tudo, sem subagentes, executa a próxima T* em Modo B e informa a limitação. No Modo B, “pode seguir” executa a próxima T*.

Para plan novo com `# Protocolo: etapas-v1`, registre `# Modo: A` ou `# Modo: B` conforme seleção acima. Não acrescente marcador nem migre uma run histórica implicitamente. No A inicialize `Execução` por T* e `Integração` conforme §3; no B os registros do novo A não são exigidos. Reexecute o motor e confira `execucao`, inclusive seus avisos. Protocolo desconhecido ou modo inválido não autoriza fallback.

Priorize R* Critical ou Required aberto (`etapa` `corrigir`). No Modo B, se o humano nomeou uma T* elegível, execute-a; caso contrário, escolha a elegível de menor número, inclusive quando houver várias. Se nenhuma estiver elegível, mostre as dependências que faltam ou encaminhe para `vibe-review` quando todas estiverem concluídas.

Grupo paralelo registrado no plan vale só no Modo B: informe os IDs e o motivo do agrupamento e pergunte se o humano prefere paralelo ou sequência. Sem resposta afirmativa, execute em sequência. Paralelo exige isolamento e ownership seguros; a autorização vale apenas para o grupo nomeado. O Modo A é sequencial e ignora o grupo. No Modo B, recomende chat novo por T* e para review sem transformar essa recomendação em gate.

## 2. Impedimentos, instalação e paradas

Para `high+` sem plan, execute o handoff para `vibe-plan`; para `max` sem analyze aprovado e limpo, execute o handoff para `vibe-analyze`. No MVP, analyze ausente, rascunho ou bloqueado impede código. Se o humano pediu esta skill e o único pendente for `# Status: rascunho` do plan, aprove essa linha e prossiga. Nunca contorne erros de proteção do script.

Antes de declarar bloqueio, resolva o que está sob controle do agente: diagnostique a falha, use outro motor compatível ou escolha uma prova equivalente. Verificação descrita só manualmente pede uma checagem executável ou inspeção direta quando possível; se depender do humano, peça apenas a validação que falta. Ambiguidade material exige a decisão específica, depois de investigar o fluxo real.

**Regra de instalação:** instale a ferramenta ausente necessária à prova pelo gerenciador do projeto ou por fonte oficial, quando o ambiente e as permissões permitirem, e registre a ausência e a instalação sob a T* que depende dela. Instalação que exija credencial, criação de conta, pagamento, elevação administrativa ou configuração persistente de integração (por exemplo, registrar um MCP) é impedimento real e vai ao humano.

**Prova vermelha:** não é impedimento. Corrija a causa raiz, sem limite de tentativas, e só pergunte quando a solução depender do humano ou mudar um aceite da spec. Nunca enfraqueça, pule ou apague teste para obter verde; mudar uma asserção exige justificativa ligada ao aceite.

| Situação | Ação |
|---|---|
| Ferramenta ausente instalável pela regra | Instale, registre sob a T* e siga |
| Prova vermelha | Corrija a causa raiz e siga |
| Impedimento real: credencial ou segredo ausente, serviço externo indisponível, permissão negada pelo humano, ação proibida, erro de proteção do motor, instalação fora da regra | Grave o checkpoint de retomada, relate a tentativa, o impedimento e a recomendação, e aguarde |
| Ambiguidade material: muda arquitetura, comportamento do produto, custo, segurança, dados, UX ou compatibilidade externa | Grave o checkpoint, faça a pergunta específica com recomendação e aguarde |
| Review sem convergência: `etapa` `corrigir` com `rodadas_correcao` 2 | Pare e relate os R* restantes |

## 3. Modo A: coordenação da phase

Com `# Protocolo: etapas-v1` use o piloto por etapas abaixo; sem marcador use o piloto legado mais adiante. Nunca troque o protocolo de uma run em andamento. Ambos mantêm um escritor de código por vez, review independente, confirmação humana final e o limite de duas rodadas de correção de review.

Este chat é o coordenador: seleciona, delega, confere, registra e opera o Git. Não escreve código; toda mudança de código, inclusive correção pequena, passa por um subagente. Leia `references/delegation.md` antes da primeira delegação (papéis, pedido, relatório fixo, escritor único, conferência). Sem subagentes, volte ao Modo B (§1).

### Piloto por etapas (`etapas-v1`)

1. Antes de delegar, confira os cinco papéis disponíveis nas ferramentas da sessão. Arquivos de perfil no disco não certificam disponibilidade; papel/modelo ausente não autoriza substituição silenciosa. Leia `references/delegation.md`. Selecione ownership e aceite, preservando trabalho alheio.
2. Inicialize no plan, antes de `## Tasks`, `- **Integração:** {"testes":"pendentes","prova":null,"commit":"pendente"}`. Sob cada T* ainda não executada, registre `- **Execução:** {"estado":"pendente","local":null}`. Não sobrescreva registros existentes na retomada.
3. Cada snapshot é JSON com `head`, `inputs` (mapa path relativo → hash de `git hash-object -- <path>`), `comando` e `resultado` (`verde` ou `falha`). Fotografe HEAD real e todos os inputs relevantes de código/teste/configuração, após a última edição. O motor confere hashes e ancestralidade Git; comando é evidência de execução, nunca autorização para executar conteúdo não confiável. Snapshot sem inputs completos não certifica cobertura semântica: confira-os contra o aceite e o diff.
4. Reexecute o motor a cada transição. Confira `execucao.avisos`, registros por T*, validade dos snapshots, fila, Git e etapa. Use a tabela. Registre estado/próximo passo e evidência no próprio plan antes de pausa, sem criar outro arquivo de estado.

| Etapa | Ação do coordenador |
|---|---|
| `implementar` | Delegue código e checagens locais proporcionais da menor elegível. O implementador reconhece o fluxo, implementa, simplifica e executa sintaxe/tipos/teste direcionado; não executa a matriz completa por task. Confira relatório e diff. Registre `estado: implementada` com snapshot local verde, mantendo `[ ] Tn concluída`. Dependentes podem avançar com essa prova. Reuse o mesmo implementador para tasks relacionadas quando ajudar o contexto; mantenha ownership explícito. Snapshot local invalidado exige revalidar/corrigir o código existente, sem reimplementar código válido automaticamente. |
| `testar` | Depois de todo código integrado, delegue ao implementador a conferência do pedido original, spec, aceite e testes existentes, e a criação somente dos testes faltantes. Preserve cenários relevantes, evite espelhar implementação e não crie testes redundantes. Confira mudanças/checagens direcionadas e registre `testes: prontos`; mantenha conclusões abertas. |
| `validar` | Delegue ao verificador a suíte relevante, build, auditorias e provas renderizadas exigidas. Consolide comandos que cobrem várias T*. Verificador não escreve testes nem corrige código. Confira saída e cobertura; registre um snapshot integrado com a união dos inputs relevantes e resultado real. Preserve provas independentes não invalidadas; não repita a matriz completa sem motivo. |
| `corrigir_validacao` | Delegue falhas reais ao corretor com comando, erro, causa investigada e paths autorizados, sem inventar R*. Confira a correção e execute por verificador somente provas afetadas, completando lacunas da integração. Atualize snapshots locais invalidados e prova final. Falha pré-review não consome rodada de review. |
| `commitar_integracao` | Com provas verdes, marque somente T* efetivamente comprovadas, atualize A*/C* provados e registre `commit: registrado` e `origem` com o HEAD da primeira prova integrada, somente quando ainda ausente. Preserve essa origem nas correções futuras, mesmo ao renovar o HEAD do snapshot. Faça staging explícito e commit `task(T1,T2,...): <resultado>`, com IDs numéricos ordenados. Confira paths e hash no Git. Se falhar, mantenha finalização pendente; registro sem commit real não libera review. Não escreva o hash no plan após o commit. |
| `revisar`, `corrigir`, `confirmar` | Execute passos R/C e §6 abaixo. Correções de review mantêm commit próprio depois da prova afetada verde e nova review; o limite de duas rodadas permanece. |
| `bloqueada`, `null` | Leia avisos/dependências/snapshots, corrija o registro que o disco não sustenta ou relate o impedimento concreto; nunca adivinhe a etapa. |
| `concluida` | Confira estado real de Git e pendências antes do fechamento descrito no piloto legado. |

Checagem local verde comprova somente a etapa delegada, não toda a T* ou integração. Retomada conserva código implementado com snapshot válido e continua em testes, validação, correção ou commit conforme o motor. HEAD ancestral com inputs idênticos permite preservar evidência depois de commit; hash divergente invalida somente a prova afetada. Dependência inexistente, ciclo ou campo inválido não libera fila.

### Piloto legado (plan sem marcador)

Reexecute o motor a cada transição, confira `plan.md`, `review.md` e `git status --short`, e aja pela `etapa`:

| `etapa` | Ação |
|---|---|
| `implementar` | Execute o ciclo da T* abaixo para a elegível de menor número e recalcule |
| `revisar` | Delegue a review final (passo R) |
| `corrigir` | Com `rodadas_correcao` já em 2, pare e relate os R* restantes; senão, delegue a correção (passo C) |
| `confirmar` | Faça a confirmação única (§6) |
| `bloqueada` | Nenhuma T* elegível: relate as dependências ou o ciclo e pare |
| `concluida` | O status aprovado não prova que o push ocorreu nem que o plan está fechado. Confira `git status -sb`, `git log @{u}..` e as T* abertas do plan. Commit à frente do upstream ou residual da phase: peça confirmação e retome o commit residual e o push do §6. T* aberta num plan aprovado: relate-a e peça a decisão do humano (nova T* em Modo B ou nova phase). Sem pendência, informe o estado e não execute nada |
| `null` | Leia os `avisos`, corrija o artefato que o motor não leu ou pergunte; não adivinhe a etapa |

**Ciclo da T*:**

1. Selecione a T* elegível de menor número e grave sob ela o checkpoint de retomada: estado `delegada ao implementador`, próximo passo `conferir o relatório`, `HEAD` de `git rev-parse HEAD`. Antes de qualquer pausa, complete-o com os paths que alimentam a prova e o `git hash-object -- <path>` de cada um.
2. Delegue a um `implementador` com: ID, aceite, `Spec:`, `Deps`, verificação planejada, `Visual`, paths conhecidos, as etapas Reconhecer, Codar, Simplificar e Provar do §4 e as proibições de `references/delegation.md`.
3. Confira o relatório contra `git status`, o diff e a saída da prova. Divergência entre relatório e disco, ou path fora da T* no diff, volta ao implementador com o problema descrito; nada é registrado antes. A prova do implementador vale como prova do estado integrado, porque ele trabalhou nesta árvore em sequência; repita-a só se o relatório não trouxer evidência suficiente ou o diff o contradisser. Prova visual necessária que o implementador não pôde executar fica com o coordenador antes do registro.
4. Com a prova verde conferida, registre a T* e crie o commit (§5), removendo o checkpoint. Informe ao humano uma linha curta com a T* e o hash, sem pedir resposta.
5. Relatório `pergunta`: pergunte ao humano e siga com as T* elegíveis que não dependem da T* parada; sem elegível independente, aguarde. Relatório `bloqueado`: aplique a tabela do §2.

**Passo R (review):** delegue a um `revisor` a `vibe-review` no alvo, em modo subagente (§6 da skill `vibe-review`). O revisor grava a etapa em `review.md` e devolve veredito, R* abertos e fechados, Critical encontrados, decisões para vigência e perguntas; não toca Git nem `AGENTS.md`. A pergunta do revisor que define o veredito é feita por você ao humano. O Modo A não executa checkpoints de review declarados no plan; a review final cobre a integração.

**Passo C (correção):** delegue ao `corretor` os R* Critical e Required abertos, com o remédio e a prova de cada um no `review.md`. Não há regra especial para Critical: se a correção exigir uma decisão, aplique a parada por ambiguidade material do §2. Confira como no passo 3 da T*, marque `[x]` em `review.md` apenas os R* provados (o corretor não edita o review), crie o commit `task(Rn): <outcome curto>` com os R* da rodada e staging explícito, e delegue nova review (passo R). Cada rodada de correção termina com nova review.

**Retomada:** um chat novo com `/vibe-implement` lê a etapa do motor, o checkpoint sob a T* aberta, o `review.md` e o Git. Compare `HEAD`, `git status --short` e os hashes do checkpoint; prova sem snapshot suficiente ou com hash divergente é invalidada e refeita. Nunca refaça T* concluída: o `[x]` no plan e o commit `task(Tn)` são a fonte. Árvore suja numa T* aberta volta ao implementador com o diff existente como ponto de partida.

## 4. Ciclo da fatia

Execute cada task seguindo as 6 etapas. No Modo B, o agente executa as seis. No Modo A legado, o implementador executa 1, 3, 4 e 5 sobre a T* delegada, e o coordenador executa 2 e 6 (§3). No Modo A por etapas, esses passos se aplicam ao recorte delegado de código, testes ou correção; registro e commit aguardam a integração do §3. O coordenador responde pela integração final, pelos artefatos vivos e pelo índice Git.

1. **Reconhecer:**
   Trace o fluxo real da T* com `rg --files` e `rg -n`: entrada, chamadas, código compartilhado e testes. Reuse helpers, componentes, tipos, biblioteca padrão e recursos nativos existentes. Com UI, siga tokens, motion e provas por tela do `design.md` aprovado quando aplicáveis. No Express, use só o recorte alterado, sem criar artefatos. Na retomada, confira `git status --short`, `HEAD` e `git hash-object -- <path>` do checkpoint; invalide apenas provas com inputs alterados ou sem snapshot suficiente. Revalide a fila e os gates, inclusive analyze aprovado e limpo no MVP.
2. **Escolher execução:**
   Recalcule a fila e respeite `Deps`. No Modo A, delegue como no §3. No Modo B, execute inline; só depois de o humano aprovar a execução paralela de um grupo registrado, delegue as T* do grupo conforme `references/delegation.md`, se o host oferecer e houver worktree/branch isolada ou ownership sem sobreposição; caso contrário, siga em sequência. Delimite cada entrega por resultado, aceite, dependências, paths exclusivos e comando de verificação. Agentes não alteram os artefatos vivos `plan.md`, `spec.md` ou `review.md`, nem operam o índice Git ou criam commits. Peça paths, diff, prova e pendências; o coordenador integra e libera dependentes após a conclusão registrada.
3. **Codar e integrar:**
   Implemente só o aceite da T*. Localize primeiro a prova da jornada afetada, como login, cadastro ou recuperação de acesso. Prefira um teste que percorra o fluxo completo e afirme seus resultados observáveis; inclua erros e limites materiais como cenários desse fluxo quando isso mantiver a prova legível. Não crie um teste por campo, função auxiliar, T* ou critério. Separe um teste somente quando houver comportamento independente, risco que precise de isolamento ou uma prova conjunta difícil de diagnosticar. O coordenador integra os paths autorizados e resolve conflitos. No grupo paralelo do Modo B, a prova de um agente não substitui a prova do estado integrado; no Modo A sequencial, vale a regra do §3.
4. **Simplificar antes da prova:**
   Remova duplicação e verbosidade no código tocado sem perder validação, segurança ou comportamento. Ao tocar testes, procure casos fragmentados da mesma jornada e consolide-os em uma prova de fluxo quando cada cenário e afirmação relevante continuar coberto. Mantenha testes separados para erros, bordas, permissões ou integrações que precisem de diagnóstico próprio. Não limpe a suíte fora da fatia. Deixe comentários semânticos em cada função criada ou alterada.
5. **Executar a prova final:**
   Rode cada prova necessária uma vez, no estado integrado, após simplificar. Smoke Test / Walking Skeleton entra somente quando o ponto de entrada real foi criado ou alterado. Se a prova falhar, corrija a causa raiz e repita a prova afetada (§2). Edição posterior em código ou teste invalida apenas as provas cujos inputs mudaram; edição de plan, spec, review ou outro registro não invalida a prova.
   Inspecione a UI renderizada quando `Visual: necessária` ou quando surgir impacto visual relevante; atualize a classificação nesse caso. `Visual: dispensada` exige prova executável sem resultado visual a julgar. Tocar arquivo de UI, HTML ou DOM, sozinho, não abre navegador. Siga `references/chrome-devtools.md`: navegador integrado, depois `chrome-devtools`, depois Playwright existente ou necessário. Comece pela tela, estado e viewport afetados; amplie se layout, responsividade, interação ou componente compartilhado exigirem. Registre rota, viewport, estado, ações e evidência. Se faltar ferramenta, aplique a regra de instalação (§2) antes de declarar limitação. Quando a prova visual for necessária, não marque conclusão sem executá-la. A review reaproveita essa evidência enquanto seus inputs permanecerem válidos. Preserve nome acessível, área de interação, foco e tooltip dos controles compactos; ações ambíguas mantêm texto.
6. **Registrar e fechar:**
   Depois da prova verde, registre no `plan.md` status, paths, prova e bloqueios sob a T*; marque `spec.md`/`review.md` só nos critérios provados. Mantenha `# Status: rascunho` enquanto o registro estiver incompleto; não crie `implement.md` nem altere arquivos históricos. No B/legado faça o commit da task antes da resposta final; no novo A, aguarde a integração verde e o commit integrado do §3.
   Se a T* permanecer incompleta ou entrar em handoff, adicione sob ela um checkpoint de retomada curto com estado, próximo passo, paths relevantes à prova, `HEAD` de `git rev-parse HEAD` e o hash de `git hash-object -- <path>` para cada input, além do comando e validade da prova. Na retomada, compare `HEAD`, hashes e status do Git; prova sem snapshot suficiente fica inválida. Remova o checkpoint ao concluir a T*, mantendo a prova final e os paths no próprio plan.

Critérios adicionais:
- DoD: `references/definition-of-done.md` no que couber.
- Banco de dados: Se a fatia tocar banco de dados ou dinheiro, siga `references/database-and-migrations.md` (DECIMAL/NUMERIC para valores monetários, queries parametrizadas obrigatórias, sem N+1, índices em FKs, transações ACID curtas).
- Sem teste verde executável, sem marcação de conclusão no disco.

## 5. Marcar e Registrar no plan.md

Após a aprovação do teste da task, a IA aplica o patch diretamente no `plan.md` vivo sob a seção da task `### T{n}:`:

```markdown
### T1: Ponto de entrada e Smoke Test
- [x] T1 concluída
- **Spec:** A1
- **Deps:** nenhuma
- **Verificação:** `npm test -- --grep "smoke"`
- **Prova:** `npm test` -> 1 passing (115ms)
- **Arquivos:** `src/index.ts`, `tests/smoke.test.ts`
- **Decisões:** AUTH-01 (implementada)
```

Outros arquivos marcados:
| Arquivo | O que marcar |
|---|---|
| `spec.md` | `A*` / `C*` **só** os que a fatia provou |
| `review.md` | `R*` Critical/Required que o fix provou |
| `interview.md` | **Não** |

No MVP, certifique-se de registrar quais IDs críticos foram implementados. Não publique essas decisões em `AGENTS.md`; isso pertence ao pós-review aprovado.

### Commit da task (Modo B ou protocolo legado)

Depois de atualizar os artefatos e antes de declarar a fatia concluída:

1. Compare o Git com o snapshot anterior. Se um path da task já estava alterado, separe o diff preexistente do seu; peça decisão só se não conseguir atribuir as mudanças com segurança.
2. Em execução delegada, somente o coordenador altera artefatos vivos e o índice Git. Liste os paths integrados e provados pela task e adicione-os explicitamente, por exemplo `git add -- path/da/task outro/path`. Nunca use `git add -A` ou `git add .`; o inventário é transitório no stdout e não cria arquivo no workspace.
3. Confira `git diff --cached --check` e `git diff --cached --name-only`. Se o diff indexado contiver path fora da task, remova-o do índice e pare se a origem não for clara.
4. Crie um commit sem `Co-Authored-By`, com mensagem no formato `task(Tn): <outcome curto>`. Não faça `git push` nesta etapa.
5. Registre a mensagem e o hash retornado por `git rev-parse HEAD` no resultado da execução e no chat. Não reabra o `plan.md` apenas para anexar o hash, pois isso criaria um residual fora do commit da task, e o Git é a fonte do hash. O próximo estado começa no commit criado.

## 6. Fechamento e resposta final

Antes da resposta final, confirme que cada T* concluída aparece em seu commit próprio (Modo B/legado) ou no commit integrado do Modo A por etapas e que `git show --format= --name-only HEAD` contém somente seus paths. Se o commit falhar, resolva a causa e tente novamente; não declare a T* concluída com trabalho verde sem commit.

**Modo A, confirmação única:** com `etapa` `confirmar`, apresente um relatório curto e um único pedido de confirmação. O relatório traz as T*s com o hash do commit integrado ou de seus commits individuais conforme o protocolo (`git log --grep '^task('`), as rodadas de correção usadas, os Critical encontrados e corrigidos (R* Critical do `review.md`), as decisões para vigência propostas na review, e o pedido: aprovar a review, publicar as decisões listadas e fazer push.

Sem confirmação explícita, não marque a review aprovada, não sincronize `AGENTS.md`, não faça commit residual nem push. Com confirmação, execute a finalização do §5 da skill `vibe-review`: status aprovado, sync das decisões vigentes por patch mínimo, prova final necessária, commit residual quando houver, e `git push` sem `--force`. Informe o hash, os paths e o resultado. Falha de commit ou push mantém a phase aberta; informe a causa segura. Um ajuste pedido pelo humano na resposta é tratado como correção (passo C) e volta à review, sem contar para o limite de 2 rodadas.

**Modo B e avulso:** não faça push; ele pertence ao fechamento aprovado em `vibe-review`. Responda de forma curta, com: T*/R*/avulsa executada; **total de T*s da fase e quantas estão concluídas** (conte os cabeçalhos `### T{n}:` do plan, não os itens elegíveis); IDs marcados; prova e resultado; paths no commit; mensagem e hash do commit; próximo passo ou impedimento concreto. Para execução avulsa sem plan, informe que não há contagem de T*. Recomende novo chat para a próxima T* ou review sem bloquear a continuidade aqui. Handoff no chat e no arquivo; não invente trabalho extra.
