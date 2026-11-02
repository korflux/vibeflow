# Etapa review

O revisor de contexto limpo julga o produto e grava o `review.md`, sem editar código, teste nem lockfile. O líder não escreve `review.md`, salvo a etapa de ajuste de phase fechada (`references/ajuste.md`), as marcações e a finalização.

## Entrada

- Gate: em `high` e `mvp`, todos os passos e checkpoints do plan concluídos (`references/disco.md`, Estado da phase e Plan > Checkpoint); em medium, o commit `task(medium): ...` da entrega.
- Sem alvo e sem diff, peça path, branch ou PR. Não grude review nova no `n` de outro pedido.
- Medium: o líder fixa o alvo de uma phase nova e o `review.md` nasce com `# Rota: medium`. `review.md` existente recebe a próxima etapa no mesmo arquivo.

O revisor lê as fontes, classifica o tipo da review e declara rota, tipo, alvo e diff por `references/review/passos.md` (Fontes e Tipo).

## Rodadas de correção

O revisor executa os passos e a saída de `references/review/passos.md`. Todo achado é resolvido. Só Critical e Required passam por re-review; Nit fecha quando o líder confere os testes afetados verdes no relatório da correção e marca o `[x]`. No máximo duas rodadas de correção; na segunda sem convergência, o revisor devolve os R* restantes e o líder os leva ao humano com recomendação.

## Confirmar

Com Approve proposto e nenhum R* aberto, o líder resume no chat, em poucas linhas, o entregue, o corrigido na review, os Critical encontrados e as decisões propostas para vigência, e pede uma única confirmação para aprovar, publicar essas decisões e fazer push, sem exigir a leitura do `review.md`. Ajuste pedido na resposta vira correção e volta à review. Sem confirmação, nada é aprovado, publicado ou enviado.

## Finalizar

Depois da confirmação humana explícita, com o gate da Entrada atendido e nenhum R* aberto, o líder:

1. Marca `# Status: aprovado` e a aprovação humana no `review.md`, sem mudar o veredito do revisor.
2. Com Decisões para vigência preenchida, aplica patch mínimo em `AGENTS.md`: uma única seção `## Decisões vigentes` com a tabela `ID | Decisão vigente | Fonte`, atualizada por ID, com as linhas não citadas preservadas e o review aprovado como fonte; relê e confirma que só os IDs aprovados mudaram. Sem decisões, não toca regras.
3. Confere, sem executar prova, que a regressão registrada no `review.md` cobre o HEAD final, inclusive `git diff --check` e gitleaks quando o repo prevê.
4. Compara `git status` com o estado registrado: registro novo em `.erros-encontrados/` é aceito; outro path fora da phase, das decisões aprovadas e das correções interrompe e pede isolamento.
5. Commita `chore(<alvo>): finalize review` (`references/disco.md`, Commits) só com os paths residuais, registros novos incluídos (`git add -- <path da phase> AGENTS.md <registros>`); sem residual, não cria commit vazio.
6. Confere o intervalo como no passo 2 da retomada abaixo e executa `git push` para o upstream do branch atual, sem `--force`. Push recusado ou adiado pelo humano: grave a linha de push adiado (`references/disco.md`, Estado da phase) e commite `chore(<alvo>): push adiado`, sem push. Sem upstream ou com falha de push, a phase fica fechada com push pendente e a causa segura é relatada.
7. Relata o hash final, o resultado do push e os paths enviados.

Retomada de push pendente, com a confirmação humana:

1. Residual da finalização ainda não commitado é commitado como no passo 5.
2. Confira `git log @{u}..HEAD` ou, sem upstream, os commits desde a base da phase. Commits de alvo fechado e de entrega low podem seguir; commit de phase ou MVP aberto, ou `task(medium): ...` sem phase fechada que o registre, nunca entra: havendo um, pare e relate.
3. Execute `git push` sem `--force`; sem upstream, `git push -u origin <branch>`.
