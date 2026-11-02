# Etapa review

O revisor de contexto limpo julga o produto e grava o `review.md`; ele não edita código, teste nem lockfile. O líder não escreve `review.md`, salvo a etapa de ajuste de phase fechada (`references/ajuste.md`), as marcações e a finalização. Aprovar, publicar decisões vigentes e fazer push exigem confirmação humana.

## Entrada

- Gate: em `high` e `mvp`, todos os passos do plan marcados com commit e todos os checkpoints marcados, com a marcação do checkpoint no commit seguinte da phase (`references/disco.md`, Checkpoint); em medium, o commit `task(medium): ...` da entrega.
- Sem alvo e sem diff, peça path, branch ou PR. Não grude review nova no `n` de outro pedido.
- Medium: o líder fixa o alvo de uma phase nova e o `review.md` nasce com `# Rota: medium`. `review.md` existente recebe a próxima etapa no mesmo arquivo.
- O revisor lê os critérios de aceite da `spec.md` (em medium, os do corpo do commit `task(medium): ...`, com `git log -1 --format=%B <commit>`; commit sem eles volta ao líder, que informa os critérios do brief), o `plan.md`, o `AGENTS.md`, o `git log` com os commits do alvo e o diff. O diff vai do commit anterior ao primeiro `task(<alvo>:...)` até `HEAD`, ou da base que o líder informar; em medium, do commit anterior ao `task(medium): ...` registrado como base.

Declare em uma linha: rota, tipo, alvo e diff.

```text
rota: high · final · alvo: .vibeflow/phases/phase-2-agenda-online/ · diff: a1b2c3d..HEAD
```

## Tipo

| Sinal | Ação |
|---|---|
| Passo ou checkpoint aberto | Não revise; devolva ao implement com o que falta |
| Todos marcados, ou entrega medium commitada | Review final |
| Correção de Critical ou Required commitada com `task(<alvo>:Rn,...)` | Re-review |
| Etapa `### Ajuste N` medium com os R* `[x]` e commit | Re-review de ajuste: só o diff desses commits, contra o pedido do ajuste |
| Critério de aceite não verificável | Devolva à spec |
| MVP sem `# Risco:` na spec ou sem `## Achados do analyze` no plan | Recuse e aponte a etapa ausente |

## Rodadas de correção

O revisor executa os passos e a saída de `references/review/passos.md`. Todo achado é resolvido. Só Critical e Required passam por re-review; Nit fecha quando o líder confere os testes afetados verdes no relatório da correção e marca o `[x]`. No máximo duas rodadas de correção. Na segunda sem convergência, o revisor devolve os R* restantes e o líder os traz ao humano com recomendação.

## Confirmar

Com Approve proposto e nenhum R* aberto, o líder resume no chat, em poucas linhas, o que foi entregue, o que foi corrigido na review, os Critical encontrados e as decisões propostas para vigência, e pede uma única confirmação para aprovar, publicar essas decisões e fazer push. O humano não precisa ler o `review.md`. Ajuste pedido na resposta vira correção e volta à review. Sem confirmação, nada é aprovado, publicado ou enviado.

## Finalizar

Depois da confirmação humana explícita, com todos os passos marcados com commit, todos os checkpoints marcados (`references/disco.md`, Checkpoint) e nenhum R* aberto, o líder:

1. Marca `# Status: aprovado` e a aprovação humana no `review.md`; o veredito do revisor não muda.
2. Com Decisões para vigência preenchida, aplica patch mínimo em `AGENTS.md`: uma única seção `## Decisões vigentes` com a tabela `ID | Decisão vigente | Fonte`, atualizada por ID, preservando linhas não citadas e usando como fonte o review aprovado. Relê e confirma que só os IDs aprovados mudaram. Sem decisões, não toca regras.
3. Confere no `review.md` que a regressão registrada pelo revisor cobre o HEAD final, inclusive `git diff --check` e gitleaks quando o repo prevê; não executa prova. A única checagem que executa é o `git diff --cached --check` do passo 5, como operação de Git do commit.
4. Compara `git status` com o estado registrado; registro novo em `.erros-encontrados/` é aceito, e path fora da phase, das decisões aprovadas, das correções e desses registros interrompe e pede isolamento.
5. Faz staging explícito só dos paths residuais, registros novos em `.erros-encontrados/` incluídos (`git add -- <path da phase> AGENTS.md <registros>`; `references/disco.md`, Glossário), confere `git diff --cached --check` e commita `chore(<alvo>): finalize review`; sem residual, não cria commit vazio.
6. Confere o intervalo como no passo 2 da retomada abaixo e executa `git push` para o upstream do branch atual, sem `--force`. Humano que recusa ou adia o push: grave a linha de push adiado (`references/disco.md`, Estado da phase) e commite `chore(<alvo>): push adiado`, sem push. Sem upstream ou com falha de push, a phase fica fechada com push pendente e a causa segura é relatada.
7. Relata o hash final, o resultado do push e os paths enviados.

Retomada de push pendente, com a confirmação humana:

1. Residual da finalização ainda não commitado é commitado como no passo 5.
2. Confira `git log @{u}..HEAD` ou, sem upstream, os commits desde a base da phase. Commits de alvo fechado e de entrega low podem seguir; commit de phase ou MVP aberto, ou `task(medium): ...` sem phase fechada que o registre, nunca entra: havendo um, pare e relate.
3. Execute `git push` sem `--force`; sem upstream, `git push -u origin <branch>`.
