# Poda de testes

Leia só no pedido de poda. A política de testes mora em `references/testes.md`.

A suíte cresce a cada phase; a poda tira o que não prova mais nada, sem perder prova de critério vigente. Ela é um pedido medium próprio (`SKILL.md`, seção 2), nunca parte de outro passo, com estes critérios no brief e no corpo do commit:

- A1: cada teste removido ou fundido cita no relatório o teste que fica e prova a mesma propriedade, ou a decisão aprovada que removeu o comportamento.
- A2: a regressão completa passa depois da poda, com a duração de cada nível antes e depois.

Gatilho: a regressão completa acima do orçamento (`references/review/passos.md`, Orçamento de duração) ou o pedido do humano. O implementador roda a suíte uma vez com o reporter de duração do runner, lista os candidatos com o motivo e remove só os desta tabela:

| Candidato | Fica no lugar |
|---|---|
| Teste da tabela O que não testar de `references/testes.md` | O teste do comportamento que ele tentava observar, se existe; senão, o critério dele entra no relatório para o líder decidir |
| Duplicata da mesma propriedade em outro arquivo ou nível | A prova principal, no nível mais barato que observa o resultado |
| E2E que repete o que a integração ou o teste que renderiza a tela já provam | O teste do nível mais barato; o E2E fica só para a jornada |
| Teste de comportamento que uma spec aprovada removeu ou substituiu | Nada; o relatório cita a decisão e a spec |
| Teste lento por espera fixa, pilha própria ou login pela interface fora do teste do login | O mesmo teste, reescrito por `references/testes.md` (Execução) |

Nunca entram na poda: a prova principal de critério vigente sem substituto, caso adversarial de `references/testes.md`, Desenho de casos (equivalência, borda, negado, concorrência), teste de autorização, de dinheiro ou de dado pessoal e critério de preservação. Teste instável não sai pela poda: segue o registro de flake (`references/disco.md`, Glossário).
