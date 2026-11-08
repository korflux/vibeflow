# Testes

Casa única da política de testes do projeto consumidor: o que testar, como desenhar os casos, como executar e o que não testar. Fora daqui: ambiente local em `references/ambiente.md`; execução do checkpoint e Desenho do E2E em `references/verificador.md`; regressão completa e Orçamento de duração em `references/review/passos.md`.

## Política de testes

- No passo, rode só os testes afetados pelo grafo de imports da ferramenta (por exemplo, `vitest run --changed <base>` ou `playwright test --only-changed=<ref>`), num comando, sem E2E e sem suíte inteira; sem esse recurso, a `Prova:` do passo; sem plan, os testes do módulo tocado e dos consumidores diretos.
- Uma prova principal por critério de aceite, no nível mais barato que observa o resultado visível do critério: critério de tela se prova na tela, não na API que a alimenta; regra de negócio, validação, autorização e cálculo sem tela se provam sem navegador, em teste unitário ou de integração (API ou serviço com banco real de teste).
- O título do teste da prova principal começa pelo ID do critério que ele prova, quando o brief ou a spec o tem, e descreve o comportamento, não a função chamada (`A3: recusa horário ocupado`). Quando o projeto tem mais de uma spec com IDs repetidos, o título leva o alvo junto do ID (`phase-1:A3: recusa horário ocupado`).
- A asserção segue o texto do critério, não a interpretação de quem implementa. Critério ambíguo, que admite mais de uma asserção, volta ao líder como `estado: pergunta`, com recomendação, devolvido por quem escreve ou nomeia o teste, antes de o teste existir. Verificador e revisor comparam a asserção com o texto do critério.
- Critério de tela: a prova principal, no passo ou, em low e medium, na prova do brief, é um teste no nível mais barato que renderiza a tela (componente ou página) e asserta o resultado visível do critério, com vermelho e verde. E2E só para critério com tela ou jornada, sem repetir o que a integração ou o teste que renderiza a tela já provam; ele não é prova principal.
- Passo que cria ou altera componente para uso compartilhado (por mais de uma tela) leva, no próprio passo, um teste que renderiza ao menos uma tela que o usa ou, sem tela que o use ainda, uma página de amostra dele, com vermelho e verde, mesmo que o critério de tela seja de outro passo; assim o defeito do componente aparece onde nasce, não no passo que o usa primeiro.
- Teste novo só para critério não coberto ou risco concreto (erro, borda, segurança, dinheiro); antes, estenda o teste existente do fluxo, se houver.
- Vermelho antes do verde: o teste da prova principal de um critério, ou o que reproduz um bug, falha antes da mudança pelo motivo esperado e passa depois. O campo `prova` traz a saída das duas execuções (as linhas da falha e o resumo de cada uma), não só o relato. Teste que já passa antes não prova o critério. Isentos, com o motivo no relatório: refatoração sem mudança de comportamento, critério de preservação (passa antes e depois), passo de infraestrutura e passo de prosa.
- No checkpoint, o verificador roda o E2E dos critérios com tela ou jornada do grupo, sem rerodar os testes dos passos. A regressão completa, que roda uma vez, na review, roda de novo o E2E de todas as telas e jornadas, inclusive as do checkpoint e as de phase sem checkpoint, porque pega o que um passo posterior quebrou.
- Nunca enfraqueça, pule ou apague teste para obter verde; mudar asserção exige justificativa pelo critério. Teste da seção O que não testar não prova critério nem passo.
- Passo só de prosa prova com checagem mecânica do que o texto alimenta, nunca com teste de presença de palavras.

## Desenho de casos

Os casos saem do critério de aceite, não do código. Os casos adversariais são obrigatórios sempre que o tipo de entrada do critério os aciona, mesmo que o critério e a spec não os citem; as demais técnicas entram só quando a regra as tem. Quando não está dito se duas entradas são o mesmo valor (por exemplo, `Ana@x.com` e `ana@x.com`), o caso entra com a asserção que o texto do critério sustenta (o mesmo valor conta como um) e a dúvida vai em `pendencias`; omitir o caso não resolve a dúvida. A severidade de caso ausente segue `references/review/passos.md` (Julgar o produto).

| Caso adversarial, obrigatório quando se aplica | Quando a entrada tem | Casos |
|---|---|---|
| Equivalência | Valores que o sistema deve tratar como iguais (e-mail, nome de usuário, código, identificador) | Variantes de caixa, de espaços nas pontas e de forma canônica do mesmo valor, todas com o mesmo resultado, inclusive em limite, unicidade e permissão |
| Borda | Faixa ou limite (valor, tamanho, data, quantidade) | O próprio limite e o primeiro valor recusado |
| Negado ou inválido | Classe de entrada recusada ou autorização | Um caso por classe inválida; na autorização, o dono, outro usuário (anti-IDOR) e quem não está autenticado |
| Concorrência | Recurso disputado (estoque, cupom, saldo, crédito, vaga, convite) | Duas requisições simultâneas sobre o mesmo recurso, com o resultado que o critério admite |

| Demais técnicas, quando a regra tem | Casos |
|---|---|
| Classes válidas com o mesmo tratamento | Um caso por classe, sem repetir a classe |
| Estados e transições (pedido, reserva, assinatura) | Cada transição permitida e a principal proibida |
| Tabela de exemplos na spec | Uma linha da tabela por caso, de preferência num teste parametrizado |
| Critério de preservação | Um teste do comportamento existente, rodado antes e depois da mudança |

- Teste determinístico: relógio e semente fixos, sem depender da ordem de execução nem de dado de outro teste.
- Dados montados pelo próprio teste ou por fábrica do projeto, só com os campos que o caso exige.

## Execução

- E2E roda sobre build de produção, o modo que o usuário recebe, no checkpoint e na regressão completa.
- Critério que toca o cliente (código que roda no navegador) tem também uma checagem de console no modo de desenvolvimento, rodada por quem roda o E2E dele: abre a tela do critério e falha com erro ou aviso novo no console, porque parte dos avisos só existe em dev.
- Uma pilha por execução: a suíte sobe o app e os serviços uma vez, e todo arquivo e todo worker a usam; nenhum arquivo nem worker sobe pilha própria.
- Sessão reaproveitada: autenticação uma vez por usuário de teste em cada execução, por worker quando os dados são por worker, com o estado de sessão salvo; login pela interface só no teste do próprio login.
- A captura de tela do critério com tela é saída da execução do E2E de quem o roda, sem passo de captura separado. Quem roda em cada rota, a exceção de low e medium e o reaproveitamento seguem `references/chrome-devtools.md` (Captura e reaproveitamento).

## O que não testar

| Não teste | Faça no lugar |
|---|---|
| Varredura de código-fonte por regex (ler o fonte e procurar texto) | Observe o comportamento que o texto produziria |
| Mock de módulo ou API do próprio projeto | Mock só na fronteira externa (rede externa, relógio, aleatoriedade e serviço pago); código do projeto e banco de teste rodam reais |
| Espera fixa por tempo | Espera por condição; espera fixa é lenta quando sobra e instável quando falta |
| A mesma propriedade em vários arquivos (teste duplicado sem ganho) | O dono do passo que tem a duplicata no recorte a remove, e o relatório cita o teste que fica: sai a cópia no mesmo nível ou num nível mais caro, fica a prova principal. Não é apagar teste para obter verde: o teste que fica prova a propriedade antes e depois |
| Teste que não pode falhar no modo em que roda: asserção sobre o que só existe em outro modo, sem asserção real ou que só exercita mock | Rode no modo em que o defeito aparece (seção Execução) e afirme o resultado do critério |
