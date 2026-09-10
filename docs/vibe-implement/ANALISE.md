# vibe-implement, análise

## Problema

A implementação precisava executar uma fila verificável sem perder histórico quando a execução mudasse de chat. O contrato anterior tratava o apply como transporte de um documento acumulativo; isso duplicava responsabilidade e permitia que o arquivo vivo ficasse desatualizado.

## Decisão de desenho

```text
relatório → fila.elegiveis
  → investigação dirigida da T* e do fluxo real
  → código, teste, simplificação e re-teste
  → apply garante implement.md
  → IA registra a fatia diretamente no vivo
  → plan/spec/review recebem somente marcações provadas
  → staging explícito e commit da T* sem push
  → handoff vibe-review ou próxima T*
```

O parser continua deliberadamente pequeno. A ordem sai do plan, as dependências saem de `Deps` e o significado de aceite continua na IA. Assim, não há reimplementação do parser em cada chat.

## Investigação e prova

A IA formula a pergunta da T*, usa `rg --files` e `rg -n` para localizar pontos de entrada, chamadas, helpers, testes e referências, e expande a leitura apenas quando uma lacuna bloqueia a prova. O inventário seleciona o alvo, mas não autoriza ler a árvore inteira.

Para UI, o contrato escolhe navegador integrado, depois MCP Chrome DevTools, depois Playwright existente ou solicitado. Uma task documental, de script ou de contrato não ganha exigência artificial de navegador.

## Escrita direta

O motor prepara um `implement.md` vazio quando necessário e preserva um arquivo já existente. A IA acrescenta uma seção por fatia diretamente no vivo, com prova, feedback e handoff. O teste verde é condição para marcar `[x]`; a persistência da trilha não depende de um segundo arquivo.

Essa decisão reduz cópia e estados concorrentes. A limitação é que a IA precisa manter o histórico ao editar o vivo; o template e a revisão devem conferir essa continuidade.

## Chat e modos

Implement recomenda um chat focado por T* quando há fila. O modo A para após uma task e seu commit; o modo B exige autorização explícita para percorrer a fila e ainda cria um commit por task. O plan e o implement carregam o contexto verificável para um novo chat.

## MVP

O gate de analyze continua separado para a rota max. A existência de plan não basta: o analyze precisa estar aprovado e limpo antes do código. A implementação não altera `REGRAS.md`; vigência é uma decisão pós-review.

## Cortes

| Corte | Motivo |
|---|---|
| Documento de tasks paralelo | A fila já está no plan. |
| Cópia acumulativa pelo script | O vivo é editado diretamente pela IA. |
| Teste visual silencioso | Sem evidência renderizada, a validação não fecha. |
| Push por task | Mantém o remoto estável durante a implementação; o push fica para a phase aprovada. |
| Instalação de navegador | Ferramenta nova só entra por necessidade real ou pedido. |

## Impacto

A próxima review lê `implement.md`, o plan marcado e as provas no mesmo alvo. A troca de chat deixa de ser uma perda de contexto porque o disco mantém a trilha completa.
