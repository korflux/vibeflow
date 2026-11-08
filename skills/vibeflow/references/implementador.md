# Implementador

Única leitura do implementador num trecho de passos, numa entrega low ou medium e numa correção do checkpoint ou da review. Abra as referências apontadas aqui só quando o trabalho chegar a elas.

## Proibido no passo

Vale no passo do plan e na correção de checkpoint ou de R*. Em low e medium, a prova do brief e a captura de `references/chrome-devtools.md` (Captura e reaproveitamento) seguem como estão; os demais itens valem também lá.

- Rodar a suíte inteira, o E2E ou a regressão completa: são do checkpoint e da review (`references/delegation.md`, Níveis de prova). E2E de critério com tela é escrito no passo e rodado pelo verificador.
- Rodar comandos além da `Prova:` do brief e dos gates estáticos, ou rodar de novo um comando já verde sem o código ter mudado depois dele.
- Esperar por loop (`until`, `while`, `sleep`, `for` com pausa) ou ler log de comando em andamento repetidas vezes. Comando que passa de cerca de 2 minutos roda em segundo plano, com o aviso de término do host; sem esse recurso, roda em primeiro plano com o tempo limite do host.
- Abrir `plan.md` ou `spec.md` inteiros: o brief traz a linha do passo, o texto dos critérios do `Aceite:` e o mapa. Abra-os só para a dúvida que o brief não resolve, e só a seção dela.
- Gravar arquivo na pasta da phase ou editar `spec.md`, `plan.md` e `review.md`, salvo a caixa do próprio passo no `plan.md` (Commit do passo): medição e evidência vão no relatório (`references/relatorio.md`).

## Recorte

- Escreva só nos `Arquivos:` do passo, no recorte do brief ou nos paths do R*; path fora dele volta ao líder antes de editar.
- Credencial, conta, pagamento, elevação administrativa ou integração persistente são impedimento real: relate a tentativa, o impedimento e a recomendação. Ferramenta ausente segue `references/delegation.md` (Pedido autocontido).

## Antes de editar

1. Confirme o mapa do brief abrindo os paths citados, sem reexplorar a árvore. Mapa que não bate: leia só o necessário para corrigi-lo e relate em `pendencias`; correção fora do recorte volta ao líder.
2. Abra os itens de `## Núcleo do projeto` citados no brief, sem resumo e inclusive as imagens, e trabalhe sobre eles.

## Codar e provar

- Reutilize o que existe (projeto, standard library, plataforma, dependências instaladas), sem abstração especulativa nem limpeza fora do recorte. Documente semanticamente responsabilidades e decisões não óbvias.
- Acabamento: `references/definition-of-done.md`; banco ou dinheiro: `references/database-and-migrations.md`.
- Testes e prova por `references/testes.md` (Política de testes, Desenho de casos, Execução e O que não testar): a `Prova:` do passo, os testes afetados da correção ou, em low ou medium, a prova do brief, com saída resumida (só falhas e totais).
- Teste com banco ou serviço: `references/ambiente.md`, nativo ou embutido, banco limpo sem recriar container, nunca Docker sem decisão registrada. E2E de critério com tela ou jornada: `references/verificador.md` (Desenho do E2E). Prova visual e captura por rota: `references/chrome-devtools.md` (Captura e reaproveitamento).
- Gate estático: em passo que toca código, rode também, sobre os arquivos alterados, os gates estáticos (lint, tipos, segurança) que o `AGENTS.md` declara na seção de comandos do projeto, seja Comandos do projeto ou equivalente, como Comandos do painel, e cite no campo `prova` cada gate rodado com o resultado. Cada gate roda uma vez, no fim do passo, depois da prova verde, e de novo só se o código mudou depois dele; com comando por pacote ou por arquivo declarado, use-o em vez do comando do repositório inteiro. Varredura de segredos é da review. Projeto sem gate declarado não roda nada a mais; a regressão completa da review não muda.
- Prova vermelha: corrija pela causa raiz e rode de novo, até verde ou impedimento real.

## Trecho

Faça os passos do trecho na ordem do brief, cada um inteiro (codar, provar, commitar) antes do seguinte. Pare e devolva o relatório ao fim do trecho, ou antes, em impedimento real, pergunta material ou path fora do recorte; os passos já commitados ficam, e o relatório diz em que passo parou e por quê. O relatório traz, em `prova`, a prova e os gates de cada passo pelo ID, e em `paths`, o hash do commit de cada passo.

## Commit do passo

Com a prova e os gates verdes, commite o passo antes de começar o seguinte. Em entrega low ou medium, na correção de R* e no passo de prosa, quem commita é o líder.

1. Marque `- [x]` só na caixa do passo no `plan.md`; não toque outra caixa nem outra linha.
2. Faça staging explícito dos paths alterados do passo, todos dentro de `Arquivos:`, e do `plan.md`: `git add -- <paths> <pasta da phase>/plan.md`. Nunca `git add -A`, `git add .`, amend, squash, force push nem push.
3. Com Node, rode `node <pasta da skill>/scripts/conferir.mjs --commit "task(<alvo>:<id>): <resultado>"`; achado se resolve no staging, na caixa ou na mensagem antes do commit.
4. Commite com a mensagem conferida, no formato de `references/disco.md` (Commits), sem `Co-Authored-By`. Correção devolvida pelo checkpoint ou pela conferência do líder é um commit novo do mesmo ID.
5. Falha de commit ou de hook: corrija a causa e commite de novo; sem saída, desfaça só a marcação da caixa e relate como impedimento.

## Relatório

Devolva o relatório fixo de `references/relatorio.md`.
