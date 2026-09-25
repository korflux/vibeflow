# vibe-implement, análise

## Problema

A implementação precisava executar uma fila verificável sem perder histórico quando a execução mudasse de chat. O plan já continha tasks e dependências, então um segundo registro acumulativo duplicava status, paths e provas e podia divergir da fila.

## Decisão de desenho

```text
JSON compacto → alvo, fila.elegiveis e avisos
  → apply valida o alvo sem criar artefato de execução
  → investigação dirigida da T* e do fluxo real
  → execução sequencial ou delegação isolada por capacidade do host
  → integração pelo coordenador e simplificação
  → prova proporcional após a última edição de código/teste, com repetição somente após falha ou invalidação dos inputs
  → IA registra status, paths, prova e bloqueios sob a T* no plan
  → spec/review recebem somente marcações provadas
  → staging explícito e commit da T* sem push
  → handoff vibe-review ou próxima T*
```

O parser continua deliberadamente pequeno. A ordem sai do plan, as dependências saem de `Deps` e o significado de aceite continua na IA. Assim, não há reimplementação do parser em cada chat.

## Delegação e integração

Delegação é opcional e depende de capacidade nativa do host. O coordenador confere elegibilidade e independência, entrega a cada agente um resultado, aceite, dependências, paths exclusivos e comando de verificação, e integra os retornos. Sem isolamento por worktree/branch ou ownership sem sobreposição, a execução continua sequencial.

Só o coordenador altera `plan.md`, `spec.md` e `review.md`, opera o índice Git, decide os paths do commit e registra a conclusão. Um agente retorna paths, resumo do diff, prova executada e pendências. Essa prova é evidência auxiliar; a task só fecha depois da verificação do estado integrado e simplificado. A fila é recalculada após cada task concluída, então uma dependente só se torna elegível depois que suas dependências foram provadas e registradas.

## Investigação e prova

A IA formula a pergunta da T*, usa `rg --files` e `rg -n` para localizar pontos de entrada, chamadas, helpers, testes e referências, e expande a leitura apenas quando uma lacuna bloqueia a prova. O inventário seleciona o alvo, mas não autoriza ler a árvore inteira.

Para UI, o contrato escolhe navegador integrado, depois MCP Chrome DevTools, depois Playwright existente ou solicitado. A prova começa pela tela, estado e viewport afetados; só amplia quando o diff alcança layout, responsividade, interação, componente compartilhado ou risco adicional. Uma task documental, de script ou de contrato não ganha exigência artificial de navegador.

## Escrita direta

O apply valida o alvo e não cria `implement.md`. Depois da prova verde, a IA registra status, comando/resultado da prova, paths e bloqueios diretamente sob a T* no plan. O teste verde é condição para marcar `[x]`; atualizar plan, spec ou review depois da prova não exige outro teste porque não muda os inputs de código/teste validados. Smoke Test acompanha a alteração do ponto de entrada real, não a posição da T* no plan.

## Retomada sem segunda trilha

Uma T* que continua incompleta pode carregar um checkpoint curto no próprio plan: estado, próximo passo, paths que alimentam a prova, `HEAD`, hash Git por path e última prova. Esse registro só existe enquanto a task está aberta e é removido quando ela fecha. Na retomada, a IA compara `git status --short`, `HEAD` e os hashes com o checkpoint; se um input mudou ou faltar snapshot, invalida apenas a prova afetada. Sem mudança nos inputs, reaproveita o resultado e continua do próximo passo. O checkpoint orienta a retomada, mas não substitui a inspeção do diff, os gates da rota nem a fila do plan.

Arquivos `implement.md` de execuções anteriores permanecem byte a byte intactos, mas não entram na seleção do alvo nem são necessários para review. Isso remove uma fonte duplicada sem migrar ou apagar histórico.

## Chat e modos

Implement recomenda um chat por T* na execução em sequência e um novo chat para review. Com várias T*s elegíveis, escolhe a menor sem pedir seleção. Se o plan apontar um grupo independente, o agente mostra as tasks e pergunta antes de paralelizá-las. Com autorização, um chat coordenador conduz apenas aquele grupo, com isolamento, prova e commit próprios por task. A resposta final concentra o estado verificável, inclusive total e concluídas da fase e hash do commit; a abertura dispensa relatório de rota, modo e fila.

## MVP

O gate de analyze continua separado para a rota max. A existência de plan não basta: o analyze precisa estar aprovado e limpo antes do código. A implementação não altera `REGRAS.md`; vigência é uma decisão pós-review.

## Cortes

| Corte | Motivo |
|---|---|
| Documento de tasks paralelo | A fila já está no plan. |
| Documento acumulativo de implementação | O plan já é a fila e o registro durável da execução. |
| Inspeção renderizada em toda mudança de UI | Só é exigida quando o aceite depende da renderização; o plan justifica a dispensa nos outros casos e a review reaproveita evidência válida. |
| Push por task | Mantém o remoto estável durante a implementação; o push fica para a phase aprovada. |
| Bloqueio imediato por ferramenta ausente | Antes de parar, o agente tenta disponibilizar a ferramenta necessária ou uma prova equivalente, respeitando permissões e o aceite. |

## Impacto

A próxima review lê status, dependências/bloqueios, paths e provas no plan e confere tudo contra o diff integrado. A troca de chat deixa de ser uma perda de contexto porque o disco mantém uma trilha única e verificável.
