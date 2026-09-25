# vibe-design, análise

## Problema

A spec fechava comportamento clique a clique com F, mas a UI continuava variável sem dono. DS, DESIGN.md ou Figma existiam como leitura solta, e cada run redesenhava tokens, hierarquia e estados de um jeito. O plan fatiava sobre fluxo aprovado sem restrição executável de apresentação, e a review julgava tela sem contrato textual para cobrar.

## Decisão de desenho

```text
spec aprovada mais interview
  → inventário e gate de predecessor
  → escolha do modo de entrada
  → apply prepara design.md
  → IA redige telas, kit, tokens e prova diretamente
  → humano lê o arquivo
  → handoff vibe-plan
```

O script continua determinístico. A decisão semântica de phase ou MVP, de modo com referência ou greenfield, e de criar, corrigir ou analisar, é da IA e é expressa por flags e pelo conteúdo do vivo. O apply só resolve o destino e garante que o arquivo vivo exista, sem etapa de promoção.

## Investigação e continuidade

A IA começa pela pergunta de apresentação que a spec deixou aberta, localiza `spec.md`, `interview.md`, `REGRAS.md`, DS, DESIGN.md ou referência Figma com `rg --files`, confirma telas, componentes, tokens e comandos com `rg -n`, e abre somente as dependências do fluxo. O inventário não autoriza leitura integral da árvore.

`interview → spec → design` pode seguir no mesmo chat. Recomende novo chat ao iniciar `plan`; a separação não é gate e o arquivo vivo permite continuar sem depender do histórico como autoridade.

O pedido explícito de iniciar o plan aprova o `design.md` do mesmo alvo ao atualizar seu status, inclusive quando chega em um chat novo. Sem esse pedido, o rascunho continua aguardando aprovação.

## MVP

O baseline MVP usa o mesmo template, com o alvo fixo em `.vibeflow/mvp/`. Isso evita que a apresentação de produto novo se misture à numeração cronológica de features. Spec, design e decisões de reuso ficam na mesma pasta.

Decisões de reuso não viram cópia da fonte. O vivo registra o que foi reusado e o que foi adaptado, com motivo, e a fonte continua fora do repo como leitura.

## O que foi cortado

| Corte | Motivo |
|---|---|
| Escrita semântica no motor | Mantém o script verificável e sem interpretação de linguagem natural. |
| Arquivo temporário como requisito de apply | A IA já edita o vivo e o apply deve preservar histórico existente. |
| Open Questions no documento | Ambiguidades são resolvidas no chat e registradas como decisão. |
| Mockup em imagem como verdade | A verdade versionada é o texto do design.md, auditável no diff. |
| Sincronização automática com Figma | A entrada é leitura com decisão registrada, sem cópia silenciosa. |
| Paleta fechada na spec | Token visual pertence à design, após o comportamento estar aprovado. |
| Template MVP separado | Uma única forma reduz divergência entre rotas. |
| Atualização automática de `REGRAS.md` | Vigência depende de review e confirmação humana. |

## Impacto

Spec, design, plan, implement e review compartilham o mesmo alvo e arquivos vivos separados por tipo. Isso reduz a chance de uma tela nascer de texto preso no chat e permite que o próximo chat confira entrada, telas, tokens, responsivo, estados e handoff diretamente no disco.
