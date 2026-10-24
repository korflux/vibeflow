# Etapa spec

A `spec.md` é o único documento que o humano aprova antes do código. Só o decidido entra: pergunta aberta no arquivo é defeito. A meta é caber em uma ou duas telas.

## Entrada

- Gate: rota `high` ou `mvp`, com as decisões fechadas pela interview (`references/interview.md`). Pedido claro também passa pela interview, com uma ou duas perguntas.
- Spec aprovada que precisa mudar segue `references/disco.md`, Escrever artefato. Pedido novo abre outra phase.
- Leia a `spec.md` viva, a seção `## Decisões vigentes` do `AGENTS.md`, quando existir, e os contratos citados.

## Gravação

O redator cria a `spec.md` a partir de `templates/spec.md` ou edita a viva, grava o cabeçalho conforme `references/disco.md`, Cabeçalho, e mantém `# Status: rascunho`.

| Seção | Regra |
|---|---|
| Objetivo | Quem opera, o que a entrega resolve e o que é sucesso, em duas a quatro frases |
| Pontos do projeto | Um ponto por linha, com path ou fluxo e o que implica para a entrega. Não copie o mapa inteiro do explorador |
| Decisões | Numeradas, cada uma com a pergunta que a originou e o motivo em uma linha; decisão assumida pelo líder diz `assumida` e também traz a pergunta que ela resolve. Decisão transversal leva ID por dimensão, como `AUTH-01`, e `mantém`, `cria` ou `substitui` contra as decisões vigentes; a spec não publica em `AGENTS.md`. No MVP, cada módulo acionado entra como decisão ou em Fora do escopo, sem pendente |
| Critérios de aceite | `A1`, `A2` em diante, na forma da seção Critérios de aceite abaixo: resultado observável e verificável, que um teste consegue provar. Com tela, diz o que aparece renderizado e em qual estado. Sem adjetivo como "rápido" ou "bonito" e sem comando, path de teste ou ferramenta, que ficam para o plan |
| Fora do escopo | Recusa real e tentadora, com motivo em uma linha |

Não entram user stories, CSS, paleta, token visual, lista de arquivos, tarefas nem comandos.

## Critérios de aceite

Cada critério é uma linha `- A1: <contexto ou estado>; quando <ação ou evento>, <resultado observável>.` Critério sobre estado estático, como documento ou configuração, omite o "quando". A mesma forma vale para os critérios do brief medium (`references/implement.md`, Rota medium).

| Regra | Fraco | Forte |
|---|---|---|
| Um resultado observável por critério | "A agenda funciona bem e permite editar" | "Com 10h livre; quando o cliente reserva 10h, a reserva aparece na agenda do profissional" |
| Entrada externa, autorização ou dinheiro: ao menos um critério de falha (negado, inválido, vazio ou limite), com o que o usuário vê e o que não é gravado | Só o caminho feliz | "Com 10h ocupado; quando outro cliente reserva 10h, vê 'horário indisponível' e nenhuma reserva é gravada" |
| Cálculo exato ou regra com várias combinações: tabela de exemplos logo abaixo do critério, com entrada e resultado esperado, bordas incluídas | "O desconto é calculado corretamente" | "A4: o desconto segue a tabela", seguido da tabela |
| Comportamento existente que a mudança arrisca entra como critério de preservação | Nada sobre o que já funciona | "Reservas feitas antes da mudança continuam na agenda com o mesmo horário" |

## Fechar

O líder confere a entrega conforme `references/delegation.md`, Conferência do líder, e contra a seção Critérios de aceite. Com Node, roda antes `scripts/plan.mjs --spec` no alvo, que aponta seção ausente, decisão sem pergunta ou motivo, critério repetido, adjetivo vago e placeholder esquecido. Achado de forma volta ao redator; achado que exige decisão do humano vira pergunta da interview. Só então responde:

```text
Spec gravada: <alvo>/spec.md

- Objetivo: <1 linha>
- Decisões: <2 a 4 bullets>
- Aceite: <A1 a An em 1 linha>
- Fora: <1 linha>

Responda "aprovado" para seguir até a review, ou indique os ajustes.
```

| Resposta | Ação |
|---|---|
| Aprovado, ou pedido direto do plan que o `SKILL.md` (Aprovação da spec) aceita como aprovação | O líder marca `# Status: aprovado` e a linha de aprovação humana, com data e a frase do humano, e segue para o plan |
| Pedido de ajuste | O redator aplica o patch; o líder resume em até cinco bullets e pede nova leitura |
| "Parece bom" ou "ok" isolado | Perguntar: "Aprovado no arquivo ou deseja algum ajuste?" |
| Intenção quebrou | Voltar à interview |

A aprovação da spec autoriza seguir até a review sem nova aprovação; a regra e suas exceções moram no `SKILL.md`. Sem commit nesta etapa.
