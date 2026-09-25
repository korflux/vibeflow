# vibe-plan, análise

## Problema

Os modelos históricos descreviam plan técnico, tasks e checklists como arquivos separados. No Vibeflow, a fila, o corpo das tasks, a prova e o handoff precisam permanecer em um único `plan.md`, e o arquivo precisa continuar sendo a fonte depois que a IA fecha a etapa.

## Decisão de desenho

```text
spec.md aprovado
  → design.md aprovado quando há UI
  → inventário do mesmo alvo
  → preparo curto das ferramentas exigidas pelas provas
  → fatiamento por resultados e dependências reais
  → apply prepara plan.md
  → IA escreve tasks diretamente, cada uma com sua prova
  → humano aprova o arquivo
  → handoff vibe-implement ou vibe-analyze
```

`--apply` não transporta a prosa do plan. Ele garante o path e evita sobrescrever um arquivo vivo. Isso deixa o parser mecânico restrito a `### T*`, à linha de conclusão e a `Deps`, enquanto a IA continua dona do significado de aceite, ordem e prova.

O pedido explícito de plan também fecha a aprovação pendente do `design.md` do mesmo alvo: em chat novo, a IA altera somente `# Status` para `aprovado` antes de continuar. Um design ausente ainda exige `vibe-design`, e um rascunho sem pedido explícito ainda exige aprovação humana.

## Investigação e ferramentas

A investigação começa pela pergunta de fatiamento e pela dependência que precisa ser provada. A IA usa `rg --files` para localizar spec, regras, entradas e testes, e `rg -n` para localizar A*/C*, decisões, símbolos e comandos. Só abre as entradas e dependências do fluxo. Para cada verificação, confirma a disponibilidade dos runtimes, comandos, serviços e capacidades necessários com manifests, workflows de CI e ferramentas disponíveis.

Uma T* com UI declara se precisa de inspeção renderizada e por quê. O gatilho é o aceite depender da aparência, layout, responsividade, estado ou interação visíveis no navegador; tocar HTML, DOM ou arquivo de componente não basta. Se um comando ou teste existente prova o aceite e não há saída renderizada a julgar, a prova visual pode ser dispensada. Quando necessária, a ordem é navegador integrado, MCP Server `chrome-devtools`, Playwright existente ou explicitamente solicitado.

## Resultados, dependências e fila

Cada T* reúne um resultado coeso verificável. Uma nova T* só aparece para um resultado separado, uma dependência real de execução, isolamento de risco ou impossibilidade de verificar a fatia como unidade. Número de arquivos, sessões, critérios de aceite, uma pontuação ou a conjunção no título não acionam quebras automáticas. Arquivos e risco são registrados quando ajudam a executar, isolar ou revisar.

O plan registra os requisitos exigidos pelas provas, onde estão disponíveis (local ou CI) e como cada ausência no ambiente de execução escolhido será resolvida. Uma dependência compartilhada ausente nesse ambiente entra na T1; se só for necessária depois, entra na primeira T* que a usa. Ausência local não exige setup quando a prova roda no CI e os requisitos estão atendidos lá. Não fica como checklist opcional e não vira uma T* isolada, salvo quando setup persistente for resultado do projeto. Bloqueios externos são registrados sem fingir prova verde nem instalar ferramentas automaticamente. `Deps` contém apenas dependências de execução e define a fila. Paralelização e checkpoint de review são omitidos quando não alteram execução ou review. Checkpoint de retomada é um registro temporário sob uma T* aberta, diferente do checkpoint de review, e sai quando a task conclui. Se uma T* criar ou alterar um ponto de entrada executável, o smoke test fica na prova dessa mesma T*.

A prova planejada roda depois da última edição de código/teste e é reaproveitada se os inputs permanecerem iguais. Falha ou alteração em um input invalida somente as verificações afetadas. A review consome evidência renderizada válida do plan em vez de abrir o navegador de novo. Uma tarefa sem T* de review final encerra no handoff da implementação para `vibe-review`.

## Chat e continuidade

Plan recomenda um novo chat quando começa após spec/design e no handoff para analyze (MVP) ou implement. Quando identifica tasks paralelizáveis, lista os IDs e o motivo; ao iniciar implement, o agente pergunta se o humano quer usar o grupo. Separar chats não é gate. O `plan.md` vivo, o status e a linha de handoff são a ponte; o histórico da conversa não é prova.

## Cortes

| Corte | Motivo |
|---|---|
| `todo.md` ou `tasks.md` | Uma casa por fato: índice e corpo ficam no plan. |
| Escrita do plan pelo script | Mantém o motor mecânico e a prosa sob responsabilidade da IA. |
| Verificação somente manual | A implement precisa de comando executável. |
| Instalação automática de navegador | Não adiciona dependência apenas para preencher um gate. |
| Checklist opcional ou T* de preparo isolada | As ausências necessárias são resolvidas dentro da T1 ou da primeira T* que as usa; setup persistente só é resultado quando faz parte do projeto. |
| Quebra por score, sessão, tamanho da lista ou título | A unidade vem do resultado e das dependências reais. |
| Disparo automático de implement | Handoff é explícito e fica no arquivo. |

## Impacto

O implement consegue projetar a fila de T* a partir do vivo, sem depender de uma pasta auxiliar. O contrato de distribuição, os templates e os motores ficam alinhados: um arquivo por etapa, uma entrada viva e uma prova executável.
