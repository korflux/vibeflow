# vibe-spec, análise

## Problema

A spec precisa ser uma fonte executável do decidido, não um rascunho preso ao chat nem um contrato de user stories copiado de outro produto. O contrato também precisava refletir que o arquivo vivo já é editado diretamente depois da primeira preparação.

## Decisão de desenho

```text
interview.md ou pedido claro
  → inventário e gate de predecessor
  → perguntas pontuais, se necessário
  → apply prepara spec.md
  → IA escreve comportamento, aceite e boundaries diretamente
  → humano lê o arquivo
  → handoff vibe-plan
```

O script continua determinístico. A decisão semântica de phase ou MVP é da IA e é expressa pela flag. `--apply` só resolve o destino e garante que o arquivo vivo exista; não é uma etapa de promoção.

## Investigação e continuidade

A IA começa pela pergunta que a spec precisa responder, localiza `interview.md`, `REGRAS.md`, entradas e testes com `rg --files`, confirma IDs, símbolos e comandos com `rg -n` e abre somente as dependências do fluxo. O inventário não autoriza leitura integral da árvore.

A escrita segue cobertura da origem → comportamento → aceite → contratos necessários. Essa ordem impede que uma spec detalhada ignore uma página ou jornada da interview e evita antecipar lista de arquivos, comandos e tarefas que pertencem ao plan. Para página informativa, o `F*` continua rastreável, mas usa somente o detalhe real do comportamento e N/A fundamentado para regras inexistentes.
O aceite é agrupado pelo resultado da capacidade, não pela futura quantidade de testes. O plan escolhe uma prova relevante, que pode cobrir vários `A*` ou ser reutilizada entre tasks.

`init → interview → spec` pode seguir no mesmo chat, e `design` também pode continuar nele quando houver UI. Recomende novo chat para iniciar `plan`; se o humano preferir ficar, prossiga e use o arquivo vivo sem tratar o histórico como autoridade.

## MVP

O baseline MVP usa o mesmo template, com seções exclusivas marcadas para omissão em phase. Isso evita que a rota de produto novo se misture à numeração cronológica de features. Entrevista, spec e decisões críticas permanecem no mesmo `.vibeflow/mvp/`.

Decisões históricas não viram vigentes automaticamente. A tabela compacta de `REGRAS.md` só muda depois de implementação, review aprovada e confirmação humana.

## O que foi cortado

| Corte | Motivo |
|---|---|
| Escrita semântica no motor | Mantém o script verificável e sem interpretação de linguagem natural. |
| Arquivo temporário como requisito de apply | A IA já edita o vivo e o apply deve preservar histórico existente. |
| Open Questions no documento | Ambiguidades são resolvidas no chat e registradas como decisão. |
| Mural de user stories e FR-00N | A cadeia usa comportamento observável, A*/C* e T*. |
| Template MVP separado | Uma única forma reduz divergência entre rotas. |
| Atualização automática de `REGRAS.md` | Vigência depende de review e confirmação humana. |

## Impacto

Spec, plan, analyze e implement compartilham o mesmo path e o mesmo arquivo vivo. Isso reduz a chance de uma execução partir de texto que ficou preso no chat e permite que o próximo chat confira status, aceite e handoff diretamente no disco.
