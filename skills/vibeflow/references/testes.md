# Testes

Casa única das regras de teste do projeto consumidor: o que testar, onde rodar, como desenhar o E2E e quanto a suíte pode durar. A mecânica de cada etapa fica na referência dela: passo e checkpoint em `references/implement.md`, regressão completa em `references/review.md`.

## Política de testes

- Cada critério de aceite tem ao menos um teste que o prova, de preferência percorrendo o fluxo com resultado observável.
- Teste novo só para critério não coberto ou risco concreto: erro, borda, segurança ou dinheiro. Antes de criar, procure um teste existente do fluxo e estenda-o.
- No passo, rode só os testes afetados, pelo grafo de imports da ferramenta do projeto (por exemplo, `vitest run --changed <base>` ou `playwright test --only-changed=<ref>`), sem E2E. Sem esse recurso, rode a `Prova:` do passo; sem plan, os testes do módulo tocado e dos consumidores diretos.
- O E2E dos critérios com tela roda no checkpoint; a regressão completa roda uma vez, na review.
- Nunca enfraqueça, pule ou apague teste para obter verde. Mudança de asserção exige justificativa pelo critério de aceite.
- Teste falso, sem asserção real ou que só exercita mock, não prova critério nem passo.
- Passo só de prosa prova com uma checagem mecânica do que o texto alimenta, nunca com teste de presença de palavras.

## Ambiente local

- Prefira serviços nativos (instalação oficial do sistema) ou embutidos no processo de teste (binário como dependência de desenvolvimento, como `embedded-postgres`) a containers. Docker fica para o CI.
- Banco limpo vem de banco por arquivo, por worker ou por template, de reset de schema ou de transação com rollback, nunca de recriar container.
- Quando o projeto já usa Docker nos testes (comando de teste que chama `docker`, `docker compose` no setup de teste, arquivo de compose do projeto como `docker-compose.yml`, `compose.yaml` e variantes, ou documentação que o prefere) e o `AGENTS.md` do projeto não registra a decisão, o líder pergunta ao humano uma vez, com recomendação, se prefere migrar para uma forma mais leve, e registra a resposta na seção Ambiente do `AGENTS.md` do projeto. Com a decisão registrada, não pergunte de novo.
- A pergunta acontece no init e no plan, quando a decisão não está registrada. No init, o registro entra no commit de governança; no plan, vira o primeiro passo do plan, conforme `references/plan.md` (passo 2).

## Pirâmide

- Prove regra de negócio, validação, autorização e cálculo em teste unitário ou de integração sem navegador: API ou serviço com banco real de teste.
- O E2E só confirma a jornada do critério com tela.

## Desenho do E2E

O E2E é leve e roda em paralelo.

| Regra | Motivo |
|---|---|
| Só jornadas de critério com tela | Regra sem tela já tem prova mais barata na Pirâmide |
| Isolamento por worker, escolhido no plan entre (a) dados ou banco por worker, (b) a pilha inteira por worker quando o app tem estado global, ou (c) descer a regra para integração | Sem isolamento, os workers disputam o mesmo estado e a suíte vira serial |
| Nenhuma cadeia de dependência de estado global entre arquivos | Arquivo encadeado não roda sozinho nem em paralelo, e uma falha derruba os seguintes |
| Autenticação feita uma vez por worker e reaproveitada (estado de sessão salvo), sem login pela interface em cada teste, exceto no teste do próprio login | Login pela interface repete o mesmo custo em todo teste |
| Nenhuma espera fixa, só esperas por condição | Espera fixa é lenta quando sobra e instável quando falta |
| Build feito uma vez e reaproveitado enquanto os inputs não mudam, com build de produção só na regressão completa | Rebuild a cada execução domina o tempo do passo e do checkpoint |
| Poucos workers quando a máquina é limitada, sem compensar com esperas | Espera mascara a falta de recurso e torna a suíte lenta e instável |

## Orçamento de duração

- O `AGENTS.md` do projeto declara o orçamento da regressão completa; sem declaração, o orçamento é de 10 minutos.
- A review mede a duração por nível: lint e tipos, unitários, E2E.
- Acima do orçamento, o revisor grava em `.erros-encontrados/` o tempo total, o nível mais lento e a causa provável, sem bloquear. A mecânica da medição fica em `references/review.md`.
