# vibe-analyze, análise

## Problema

Analyze precisava certificar consistência entre interview, spec e plan sem criar uma segunda porta de clarificação nem exigir um arquivo de tarefas separado. O contrato também precisava deixar explícito que o certificado é vivo e que o apply não promove um rascunho intermediário.

## Decisão de desenho

```text
relatório do mesmo alvo
  → cruzamento dirigido de fontes e decisões
  → correção de lacunas óbvias ou pergunta real
  → apply prepara analyze.md
  → IA grava cobertura, achados e veredito diretamente
  → humano lê o certificado
  → handoff vibe-implement ou retorno à skill dona
```

A IA começa pelas perguntas de consistência, usa `rg --files` e `rg -n` para localizar somente as âncoras do fluxo e registra cada finding com evidência. A lista do inventário seleciona o alvo; não autoriza um dump da árvore.

## Por que manter um certificado vivo

O `analyze.md` é a ponte entre o plan aprovado e o código. Se o arquivo fica preso no chat, uma implementação posterior pode perder a cobertura, o veredito ou os achados resolvidos. Preparar o vivo antes da escrita permite que a IA edite o mesmo documento em reexecuções e preserve o histórico relevante.

Correções óbvias em spec ou plan continuam permitidas porque são parte da consistência; elas são semânticas da IA e devem ser apontadas no certificado. O motor permanece sem interpretação.

## MVP e decisões

No MVP, a interview é obrigatória e IDs críticos precisam atravessar spec e plan com ação explícita. Mudança sem `substitui` é finding crítico. A tabela vigente de `REGRAS.md` permanece fora da análise até o ciclo implementação → review → confirmação humana.

## Chat

Analyze recomenda novo chat porque cruza vários documentos e pode corrigir decisões. Continuidade no mesmo chat é permitida, mas o arquivo vivo, não a memória do chat, é a fonte de verdade.

## Cortes

| Corte | Motivo |
|---|---|
| `vibe-clarify` separado | Perguntas de intenção já pertencem a interview/spec; analyze certifica o cruzamento. |
| `tasks.md` | As tasks estão no `plan.md`. |
| Relatório apenas no chat | O veredito e os achados precisam sobreviver à troca de contexto. |
| Aplicação automática de decisões vigentes | Evita publicar sem review e confirmação. |
| Leitura integral do repo | O fluxo real e a busca dirigida são suficientes. |

## Impacto

A implementação recebe um veredito rastreável e um path estável. Reexecuções atualizam `analyze.md` sem apagar fontes nem depender de uma etapa de transporte de conteúdo.
