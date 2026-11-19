# Gravação da spec

Leitura do redator de spec, depois de `references/spec.md` (Gravação), e do líder ao escrever os critérios do brief medium. O líder confere a spec por `references/spec.md` (Fechar).

## Seções

| Seção | Regra |
|---|---|
| Objetivo | Quem opera, o que a entrega resolve e o que é sucesso, em duas a quatro frases |
| Pontos do projeto | Um ponto por linha, com path ou fluxo e o que implica; fato sondado traz a evidência (comando ou fonte e resultado), sem copiar o mapa inteiro do explorador |
| Decisões | Numeradas, cada uma com a pergunta que a originou e o motivo em uma linha; decisão assumida pelo líder diz `assumida` no motivo. Valor leva a origem de `references/spec.md` (Origem dos valores). Decisão transversal leva ID por dimensão, como `AUTH-01`, e `mantém`, `cria` ou `substitui` contra as decisões vigentes, sem publicar em `AGENTS.md`. No MVP, cada módulo acionado entra como decisão ou em Fora do escopo, sem pendente |
| Critérios de aceite | `A1`, `A2` em diante, na forma de Critérios de aceite, abaixo |
| Fora do escopo | Recusa real e tentadora, com motivo em uma linha |

Não entram user stories, CSS, paleta, token visual, lista de arquivos, tarefas nem comandos.

## Critérios de aceite

Forma: `references/spec.md` (Critérios de aceite). Cada critério é resultado observável que um teste prova; com tela, o que aparece renderizado e em qual estado. Sem adjetivo como "rápido" ou "bonito" e sem comando, path de teste ou ferramenta.

| Regra | Exemplo |
|---|---|
| Um resultado observável por critério, nunca "funciona bem e permite editar" | "Com 10h livre; quando o cliente reserva 10h, a reserva aparece na agenda do profissional (origem: humano)" |
| Entrada externa, autorização ou dinheiro: ao menos um critério de falha (negado, inválido, vazio ou limite), com o que o usuário vê e o que não é gravado | "Com 10h ocupado; quando outro cliente reserva 10h, vê 'horário indisponível' e nenhuma reserva é gravada (origem: humano)" |
| Cálculo exato ou regra com várias combinações: tabela de exemplos logo abaixo do critério, com entrada e resultado esperado, bordas incluídas | "A4: o desconto segue a tabela", seguido da tabela |
| Comportamento existente que a mudança arrisca entra como critério de preservação | "Reservas feitas antes da mudança continuam na agenda com o mesmo horário" |
