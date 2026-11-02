# Etapa spec

A `spec.md` é o único documento que o humano aprova antes do código. Só o decidido entra: pergunta aberta no arquivo é defeito. A meta é caber em uma ou duas telas.

## Entrada

- Gate: rota `high` ou `mvp`, com as decisões fechadas pela interview (`references/interview.md`), mesmo em pedido claro.
- Spec aprovada que precisa mudar segue `references/disco.md` (Escrever artefato); pedido novo abre outra phase.
- Leia a `spec.md` viva, `## Decisões vigentes` do `AGENTS.md` quando existir e os contratos citados.

## Gravação

O redator cria a `spec.md` de `templates/spec.md` ou edita a viva, com o cabeçalho de `references/disco.md` (Cabeçalho) e `# Status: rascunho`.

| Seção | Regra |
|---|---|
| Objetivo | Quem opera, o que a entrega resolve e o que é sucesso, em duas a quatro frases |
| Pontos do projeto | Um ponto por linha, com path ou fluxo e o que implica; fato sondado traz a evidência (comando ou fonte e resultado), sem copiar o mapa inteiro do explorador |
| Decisões | Numeradas, cada uma com a pergunta que a originou e o motivo em uma linha; decisão assumida pelo líder diz `assumida` no motivo. Valor leva a origem abaixo. Decisão transversal leva ID por dimensão, como `AUTH-01`, e `mantém`, `cria` ou `substitui` contra as decisões vigentes, sem publicar em `AGENTS.md`. No MVP, cada módulo acionado entra como decisão ou em Fora do escopo, sem pendente |
| Critérios de aceite | `A1`, `A2` em diante, na forma abaixo: resultado observável que um teste prova; com tela, o que aparece renderizado e em qual estado. Sem adjetivo como "rápido" ou "bonito" e sem comando, path de teste ou ferramenta |
| Fora do escopo | Recusa real e tentadora, com motivo em uma linha |

Não entram user stories, CSS, paleta, token visual, lista de arquivos, tarefas nem comandos.

### Origem dos valores

- Todo valor numérico, prazo, limite ou comportamento externo numa linha de Decisões ou de Critérios de aceite traz na mesma linha um destes marcadores, com a fonte não vazia; palavra solta, como `humano` no texto, não vale:

| Marcador | Quando |
|---|---|
| `(origem: verificado <fonte>)` | O explorador provou o fato por sondagem, com a evidência em Pontos do projeto |
| `(origem: humano)` | O humano deu o valor |
| `(origem: assumida)` | Nem fonte verificada nem o humano sustentam o valor |

- A origem `assumida` de um valor difere da decisão assumida pelo líder, marcada no motivo.
- Fato que só se prova implementando, ou que o explorador devolveu como "não verificado", leva `(origem: assumida)` e vira o passo de verificação do plan (`references/plan.md`, Fatiar e ordenar); "verifico depois" sem esse passo é proibido.
- Decisão de preferência (cor, nome, ordem) e linha de tabela de exemplos não levam marcador.
- Vale para spec nova; spec aprovada não é revalidada.

## Critérios de aceite

Cada critério é uma linha `- A1: <contexto ou estado>; quando <ação ou evento>, <resultado observável>.` Critério sobre estado estático, como documento ou configuração, omite o "quando". A mesma forma vale para os critérios do brief medium (`references/implement.md`, Rota medium).

| Regra | Exemplo |
|---|---|
| Um resultado observável por critério, nunca "funciona bem e permite editar" | "Com 10h livre; quando o cliente reserva 10h, a reserva aparece na agenda do profissional (origem: humano)" |
| Entrada externa, autorização ou dinheiro: ao menos um critério de falha (negado, inválido, vazio ou limite), com o que o usuário vê e o que não é gravado | "Com 10h ocupado; quando outro cliente reserva 10h, vê 'horário indisponível' e nenhuma reserva é gravada (origem: humano)" |
| Cálculo exato ou regra com várias combinações: tabela de exemplos logo abaixo do critério, com entrada e resultado esperado, bordas incluídas | "A4: o desconto segue a tabela", seguido da tabela |
| Comportamento existente que a mudança arrisca entra como critério de preservação | "Reservas feitas antes da mudança continuam na agenda com o mesmo horário" |

## Fechar

O líder confere a entrega por `references/delegation.md` (Conferência do líder) e contra Critérios de aceite. Com Node, roda antes `scripts/plan.mjs --spec` no alvo, que aponta a parte mecânica. Achado de forma volta ao redator; achado que exige decisão do humano vira pergunta da interview. Só então responde:

```text
Spec gravada: <alvo>/spec.md

- Objetivo: <1 linha>
- Decisões: <2 a 4 bullets>
- Aceite: <A1 a An em 1 linha>
- Fora: <1 linha>
- Assumidas: <cada valor com `(origem: assumida)` e cada decisão assumida, com o número da decisão ou do critério, ou nenhuma>

Responda "aprovado" para seguir até a review, ou indique os ajustes.
```

| Resposta | Ação |
|---|---|
| Aprovado, ou pedido direto do plan aceito como aprovação (`SKILL.md`, seção 3) | O líder marca `# Status: aprovado` e a aprovação humana, com data e a frase do humano, e segue para o plan |
| Pedido de ajuste | O redator aplica o patch; o líder resume em até cinco bullets e pede nova leitura |
| "Parece bom" ou "ok" isolado | Perguntar: "Aprovado no arquivo ou deseja algum ajuste?" |
| Intenção quebrou | Voltar à interview |

Sem commit. O que a aprovação encadeia segue o topo do `SKILL.md`.
