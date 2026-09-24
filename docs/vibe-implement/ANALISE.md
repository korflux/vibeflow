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
  → prova final no estado integrado, com repetição somente após falha ou edição de código/teste
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

Para UI, o contrato escolhe navegador integrado, depois MCP Chrome DevTools, depois Playwright existente ou solicitado. Uma task documental, de script ou de contrato não ganha exigência artificial de navegador.

## Escrita direta

O apply valida o alvo e não cria `implement.md`. Depois da prova verde, a IA registra status, comando/resultado da prova, paths e bloqueios diretamente sob a T* no plan. O teste verde é condição para marcar `[x]`; atualizar os artefatos depois da prova não exige outro teste porque não muda o código ou o teste validado.

Arquivos `implement.md` de execuções anteriores permanecem byte a byte intactos, mas não entram na seleção do alvo nem são necessários para review. Isso remove uma fonte duplicada sem migrar ou apagar histórico.

## Chat e modos

Implement recomenda um chat por T* na execução em sequência e um novo chat para review. Se o plan apontar um grupo independente, o agente mostra as tasks e pergunta antes de paralelizá-las. Com autorização, um chat coordenador conduz apenas aquele grupo, com isolamento, prova e commit próprios por task. A recomendação de chat não bloqueia a preferência do humano; o plan e o diff carregam o contexto verificável.

## MVP

O gate de analyze continua separado para a rota max. A existência de plan não basta: o analyze precisa estar aprovado e limpo antes do código. A implementação não altera `REGRAS.md`; vigência é uma decisão pós-review.

## Cortes

| Corte | Motivo |
|---|---|
| Documento de tasks paralelo | A fila já está no plan. |
| Documento acumulativo de implementação | O plan já é a fila e o registro durável da execução. |
| Teste visual silencioso | Sem evidência renderizada, a validação não fecha. |
| Push por task | Mantém o remoto estável durante a implementação; o push fica para a phase aprovada. |
| Instalação de navegador | Ferramenta nova só entra por necessidade real ou pedido. |

## Impacto

A próxima review lê status, dependências/bloqueios, paths e provas no plan e confere tudo contra o diff integrado. A troca de chat deixa de ser uma perda de contexto porque o disco mantém uma trilha única e verificável.
