# Testes

Regras de teste do projeto consumidor: o que testar e como desenhar os casos. Fora daqui: ambiente local em `references/ambiente.md`; checkpoint e Desenho do E2E em `references/verificador.md`; regressão completa e Orçamento de duração em `references/review/passos.md`.

## Política de testes

- Cada critério de aceite tem ao menos um teste que o prova, de preferência percorrendo o fluxo com resultado observável.
- Regra de negócio, validação, autorização e cálculo se provam sem navegador, em teste unitário ou de integração (API ou serviço com banco real de teste); o E2E só confirma a jornada do critério com tela.
- Teste novo só para critério não coberto ou risco concreto (erro, borda, segurança, dinheiro); antes, estenda o teste existente do fluxo, se houver.
- Vermelho antes do verde: o teste que prova um critério, ou reproduz um bug, falha antes da mudança pelo motivo esperado e passa depois; o campo `prova` traz as duas execuções. Teste que já passa antes não prova o critério. Isentos, com o motivo no relatório: refatoração sem mudança de comportamento, critério de preservação (passa antes e depois), passo de infraestrutura e passo de prosa.
- No passo, rode só os testes afetados pelo grafo de imports da ferramenta (por exemplo, `vitest run --changed <base>` ou `playwright test --only-changed=<ref>`), sem E2E; sem esse recurso, a `Prova:` do passo; sem plan, os testes do módulo tocado e dos consumidores diretos.
- No checkpoint, o verificador roda o E2E dos critérios com tela do grupo, sem rerodar os testes dos passos. O E2E das demais telas, inclusive em phase sem checkpoint, entra na regressão completa, que roda uma vez, na review.
- Nunca enfraqueça, pule ou apague teste para obter verde; mudar asserção exige justificativa pelo critério. Teste falso, sem asserção real ou que só exercita mock, não prova critério nem passo.
- Passo só de prosa prova com checagem mecânica do que o texto alimenta, nunca com teste de presença de palavras.

## Desenho de casos

Os casos saem do critério de aceite, não do código: para cada critério, só as técnicas que a regra aciona. A tabela é teto, não piso. A severidade de caso ausente segue `references/review/passos.md` (Julgar o produto).

| Quando a regra tem | Casos |
|---|---|
| Faixa ou limite (valor, tamanho, data, quantidade) | O próprio limite e o primeiro valor recusado |
| Classes de entrada com o mesmo tratamento | Um caso por classe, válida e inválida, sem repetir a classe |
| Estados e transições (pedido, reserva, assinatura) | Cada transição permitida e a principal proibida |
| Autorização | O dono, outro usuário (anti-IDOR) e quem não está autenticado |
| Tabela de exemplos na spec | Uma linha da tabela por caso, de preferência num teste parametrizado |
| Critério de preservação | Um teste do comportamento existente, rodado antes e depois da mudança |

- O nome do teste descreve o comportamento do critério ("recusa horário ocupado"), não a função chamada.
- Mock só na fronteira: rede externa, relógio, aleatoriedade e serviço pago. Código do projeto e banco de teste rodam reais.
- Teste determinístico: relógio e semente fixos, sem depender da ordem de execução nem de dado de outro teste.
- Dados montados pelo próprio teste ou por fábrica do projeto, só com os campos que o caso exige.
