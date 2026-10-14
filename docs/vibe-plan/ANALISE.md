# vibe-plan, análise

## Problema

Os modelos históricos descreviam plan técnico, tasks e checklists como arquivos separados. No Vibeflow, a fila, o corpo das tasks, a prova e o handoff precisam permanecer em um único `plan.md`, e o arquivo precisa continuar sendo a fonte depois que a IA fecha a etapa.

## Decisão de desenho

```text
spec.md aprovado
  → design.md aprovado quando há UI
  → inventário do mesmo alvo
  → prontidão das provas: uma linha por requisito com local e destino
  → fatiamento por resultados e dependências reais
  → apply prepara plan.md
  → IA escreve tasks diretamente, cada uma com Arquivos e prova afetada, e a regressão completa uma única vez
  → humano aprova o arquivo
  → rota max: analyze delegado a subagente, perguntas e aprovação no chat do plan
  → handoff vibe-implement (chat novo, Modo A) ou vibe-analyze sem subagentes
```

`--apply` não transporta a prosa do plan. Ele garante o path e evita sobrescrever um arquivo vivo. Quem lê o plan mecanicamente é o motor da implement: `### T*`, a linha de conclusão, `Deps` e, no Modo A de `coordenacao-v1`, a linha `Arquivos:` de cada T* para calcular as ondas. A IA continua dona do significado de aceite, ordem e prova.

O plan escreve `Arquivos:` no formato que esse parser já lê (uma linha física, cada path entre crases) em vez de o parser aprender formatos novos. Os dois desvios têm efeitos diferentes. Lista quebrada em várias linhas ou path fora das crases some da declaração sem erro: a T* parece escrever menos do que escreve, e uma sobreposição real pode ficar escondida, pondo duas T* que escrevem o mesmo arquivo na mesma onda. Path incomparável é o caso seguro: a T* inteira fica sem arquivos comparáveis e roda sozinha, e só o paralelismo se perde. Por isso o formato é exigido literalmente, o plan avisa o path incomparável e recomenda renomear ou isolar, e o placeholder do template é comparável, para que um plan copiado sem ajuste não serialize todas as T*.

O pedido explícito de plan também fecha a aprovação pendente do `design.md` do mesmo alvo: em chat novo, a IA altera somente `# Status` para `aprovado` antes de continuar. Um design ausente ainda exige `vibe-design`, e um rascunho sem pedido explícito ainda exige aprovação humana.

## Investigação e ferramentas

O custo de fechamento depende tanto dos comandos quanto da coordenação. Com T* executadas em ondas paralelas, repetir a suíte inteira em cada T* multiplicaria o custo e a contenção sobre os mesmos recursos, e a validade de cada execução dependeria do que as T* vizinhas estão escrevendo. Por isso as provas ficam em dois níveis: cada T* declara a `Prova afetada:` (módulo tocado, consumidores diretos e, no E2E, só o cenário cuja entrada mudou), e a suíte inteira com o E2E completo é declarada uma única vez como `Regressão completa`, executada pela review final no estado integrado. As válvulas de ampliação por risco ou lacuna saíram dos papéis de implementação e verificação porque a regressão completa é o lugar único dessa cobertura; segurança, paridade e CI obrigatório entram nela. Os comandos compartilhados têm uma única definição na prontidão das provas, e cada task os referencia.

A investigação começa pela pergunta de fatiamento e pela dependência que precisa ser provada. A IA usa `rg --files` para localizar spec, regras, entradas e testes, e `rg -n` para localizar A*/C*, decisões, símbolos e comandos. Só abre as entradas e dependências do fluxo. Para cada verificação, confirma a disponibilidade dos runtimes, comandos, serviços e capacidades necessários com manifests, workflows de CI e ferramentas disponíveis.

Uma T* com UI declara se precisa de inspeção renderizada e por quê. O gatilho é o aceite depender da aparência, layout, responsividade, estado ou interação visíveis no navegador; tocar HTML, DOM ou arquivo de componente não basta. Se um comando ou teste existente prova o aceite e não há saída renderizada a julgar, a prova visual pode ser dispensada. Quando necessária, a ordem é navegador integrado, MCP Server `chrome-devtools`, Playwright existente ou explicitamente solicitado.

## Resultados, dependências e fila

O marcador `coordenacao-v1` separa trabalho planejado de execução. Plan contém objetivo, resultado/aceite/Deps, `Arquivos:` e `Prova afetada:` por T*, a `Regressão completa` e resumo curto; execution.json mantém estado atual mecanicamente validado. Isso reduz contexto e evita status concorrentes. Implementador entrega código/testes juntos; verificador certifica integração; finalizador registra e opera Git. Dependentes podem avançar com prova local válida e conclusão espera integração/commit reais. Etapas-v1/legado e B seguem contratos anteriores, sem migração.

Cada T* reúne um resultado coeso verificável. Uma nova T* só aparece para um resultado separado, uma dependência real de execução, isolamento de risco ou impossibilidade de verificar a fatia como unidade. Número de arquivos, sessões, critérios de aceite, uma pontuação ou a conjunção no título não acionam quebras automáticas. `Arquivos:` é obrigatório porque é o mecanismo de isolamento do paralelismo: sem worktree, a disjunção dos paths que cada T* pode escrever garante um dono por arquivo, e o motor calcula as ondas de forma determinística a partir dela e de `Deps`. T* sem `Arquivos:` não bloqueia a fase, apenas roda sozinha. Risco é registrado quando ajuda a isolar ou revisar.

A prontidão das provas virou uma linha por requisito com local (local, CI ou host) e destino (`ok`, `ação em Tn`, `pergunta ao humano` ou `bloqueio`). A forma anterior, em prosa, deixava passar o que o coordenador do Modo A descobria só ao despachar a primeira onda: perfil de subagente ausente, privilégio do SO como symlink no Windows, ferramenta da prova visual. Com destino obrigatório, o coordenador recebe o terreno conferido e não pede execução sem o básico verificado; requisito sem destino mantém o plan em rascunho. Os destinos seguem a regra única de instalação: o que se instala ou configura no próprio projeto sem credencial, conta, pagamento ou elevação vira ação na primeira T* dependente; perfil, MCP ou integração persistente registrada no host, privilégio do SO e credencial voltam ao humano com recomendação; o que não tem equivalente é bloqueio, nunca verde. Ausência local não exige setup quando a prova roda no CI e o requisito está atendido lá. Não fica como checklist opcional e não vira uma T* isolada, salvo quando setup persistente for resultado do projeto. `Deps` contém apenas dependências de execução e define a fila. Arquivo compartilhado entre T* sem `Deps` (versão, README, índices) vai para uma T* final com `Deps`, porque duas T* da mesma onda não podem escrever o mesmo path; prosa se separa de código para que o coordenador entregue cada T* ao redator ou ao implementador certo. Paralelização é omitida quando não altera a execução. No Modo A o plan não promete checkpoint de review, porque a review final cobre a phase inteira; o checkpoint só cabe quando o handoff anuncia Modo B e um risco ou contrato exige julgamento antes de outra T*. No novo A, andamento é resumo curto e evidência fica em execution.json; checkpoint extenso permanece somente nos protocolos históricos. Se uma T* criar ou alterar um ponto de entrada executável, o smoke test fica na prova dessa mesma T*.

A prova afetada roda depois da última edição de código/teste e é reaproveitada se os inputs permanecerem iguais. Em T* só de prosa, ela é a suíte do consumidor contratual do texto ou uma checagem mecânica do que o texto alimenta, porque teste de presença de palavras não prova comportamento e é proibido pelas regras do repo. Falha ou alteração em um input invalida somente as verificações afetadas. A review consome evidência renderizada válida no registro do protocolo em vez de abrir o navegador de novo. Uma tarefa sem T* de review final encerra no handoff da implementação para `vibe-review`.

## Chat e continuidade

Plan recomenda um novo chat quando começa após spec/design, e a spec não vai para subagente. Na rota max, o plan delega o analyze a um subagente de contexto limpo e conduz as perguntas e a aprovação no próprio chat, porque só ele pode conversar com o humano; o subagente só grava e devolve o relatório. Como o handoff era `vibe-analyze` apenas no MVP e o implement redirecionava depois, o handoff passou a apontar o analyze também em phase max, que é onde a delegação precisa saber disso. O fechamento recomenda com ênfase um chat novo com `/vibe-implement`, que rodará em Modo A, porque o ganho do piloto está no implement; sem subagentes no host, o handoff anuncia Modo B. Quando identifica tasks paralelizáveis, lista as ondas previstas e o motivo; no novo A o coordenador despacha cada onda calculada pelo motor, com isolamento por `Arquivos:` disjuntos, e a colaboração de leitura/preparação é escolhida pelo benefício. B oferece grupo ao humano antes de paralelizar. Separar chats não é gate. O `plan.md` vivo, o status e a linha de handoff são a ponte; o histórico da conversa não é prova.

## Cortes

| Corte | Motivo |
|---|---|
| `todo.md` ou `tasks.md` | Uma casa por fato: índice e corpo ficam no plan. |
| Escrita do plan pelo script | Mantém o motor mecânico e a prosa sob responsabilidade da IA. |
| Verificação somente manual | A implement precisa de comando executável. |
| Suíte completa por T* ou válvula de ampliação nos papéis de implementação e verificação | Em ondas paralelas multiplica custo e contenção; a regressão completa é única e pertence à review final. |
| Worktree por T* | A disjunção de `Arquivos:` basta para isolar a escrita; worktree fica como evolução futura. |
| Instalação fora da regra única | Instalar é permitido quando o gerenciador do projeto ou uma fonte oficial resolve e o ambiente permite; credencial, conta, pagamento, elevação e registro de integração persistente, como um MCP, vão ao humano. |
| Teste de presença de palavras como prova de T* de prosa | Não prova comportamento; a prova é a suíte do consumidor contratual ou uma checagem mecânica. |
| Checkpoint de review no Modo A | A review final cobre a phase inteira; o checkpoint fica restrito ao Modo B e aos protocolos históricos. |
| Spec e design em subagente | A spec e o design dependem de conversa com o humano; só o analyze, que grava e devolve perguntas, foi delegado. |
| Checklist opcional ou T* de preparo isolada | As ausências necessárias são resolvidas dentro da T1 ou da primeira T* que as usa; setup persistente só é resultado quando faz parte do projeto. |
| Quebra por score, sessão, tamanho da lista ou título | A unidade vem do resultado e das dependências reais. |
| Disparo automático de implement | Handoff é explícito e fica no arquivo. |

## Impacto

O implement consegue projetar a fila e as ondas de T* a partir do vivo, sem depender de uma pasta auxiliar. O contrato de distribuição, os templates e os motores ficam alinhados: uma fonte por fato, estado operacional separado da definição de trabalho e provas executáveis.
