# Etapa review

O revisor de contexto limpo julga o produto e grava o `review.md`; ele não edita código, teste nem lockfile. O líder não escreve `review.md`, salvo a etapa de ajuste de phase fechada (`references/implement.md`, Ajuste de phase), as marcações e a finalização. Aprovar, publicar decisões vigentes e fazer push exigem confirmação humana.

## Entrada

- Gate: em `high` e `mvp`, todos os passos do plan marcados com commit e todos os checkpoints marcados, com a marcação do checkpoint no commit seguinte da phase (`references/disco.md`, Checkpoint); em medium, o commit `task(medium): ...` da entrega.
- Sem alvo e sem diff, peça path, branch ou PR. Não grude review nova no `n` de outro pedido.
- Medium: o líder fixa o alvo de uma phase nova e o `review.md` nasce com `# Rota: medium`. `review.md` existente recebe a próxima etapa no mesmo arquivo.
- O revisor lê os critérios de aceite da `spec.md` (em medium, o brief), o `plan.md`, o `AGENTS.md`, o `git log` com os commits do alvo e o diff. O diff vai do commit anterior ao primeiro `task(<alvo>:...)` até `HEAD`, ou da base que o líder informar; em medium, do commit anterior ao `task(medium): ...` registrado como base.

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

## Passos

### 1. Disparar a regressão completa

Ao abrir a review final, o revisor dispara a regressão completa uma vez, em segundo plano, sobre o `HEAD` da entrega, e lê o diff enquanto ela roda.

- Comandos: os de regressão registrados no plan ou, sem eles, os Comandos do projeto no `AGENTS.md`. Sem nenhum, devolva ao líder sem aprovar.
- Ordem: do mais barato ao mais caro (lint e tipos, unitários, E2E), parando na primeira falha.
- Árvore suja em path de código ou teste (tudo fora de `.vibeflow/` e `.erros-encontrados/`) impede a execução: devolva `estado: bloqueado` pedindo o isolamento.
- Falha que passa ao reexecutar o mesmo comando é flake: o revisor grava o registro em `.erros-encontrados/`, cita-o em Notas e segue, sem bloquear. Falha reproduzível abre R* Required com o comando.
- Registre na etapa os comandos, o resultado e o `HEAD`.

A execução registrada vale para o Approve enquanto as correções posteriores não tocarem código compartilhado. Esta é a única execução da regressão completa na review; a re-review só a repete na exceção do passo 4.

### 2. Julgar o produto

1. **Critérios de aceite:** cada critério da spec, ou item do brief em medium, está atendido e provado por ao menos um teste. Preencha a tabela de critérios com o teste e o resultado. Critério não atendido ou sem teste que o prove abre R* Required; só o humano retira um critério, com a decisão citada.
2. **Defeitos no código alterado:** correção, bordas e erros das superfícies tocadas; testes falsos (sem asserção real ou que só exercitam mock); teste enfraquecido, pulado ou apagado (`references/implement.md`, Política de testes); barra de `references/definition-of-done.md`.
3. **Segurança:** só quando o diff toca input, auth, sessão, permissão, segredo, upload, integração externa ou dado pessoal, conforme `references/review/security-and-hardening.md`.
4. **Banco e precisão:** só quando o diff toca persistência ou valor monetário, conforme `references/database-and-migrations.md`.
5. **Visual:** quando um critério depende da interface renderizada, conforme `references/review/ui-visual-quality.md`, reaproveitando a evidência válida.

Notas, nunca achado: path alterado fora dos `Arquivos:` do plan, coerência dos commits com os passos e commits de outro alvo no intervalo. Defeito fora dos critérios e do diff é achado fora do recorte: o revisor grava um arquivo por achado em `.erros-encontrados/`, cita em Notas e não bloqueia.

Achado: path, severidade (`Critical`, `Required` ou `Nit`), remédio, prova e `papel: implementador` (código e testes) ou `papel: redator` (prosa); remédio em `review.md` é do revisor, sem `papel`. Achado novo recebe o próximo R* livre, sem renumerar fechados. Preferência sem fundamento não é achado; informação sem remédio vai para Notas.

### 3. Gravar

O revisor cria o `review.md` a partir de `templates/review.md`, ou acrescenta `### Etapa N` sem apagar etapas anteriores, e marca o veredito:

- **Approve:** critérios atendidos e provados, regressão verde e nenhum Critical ou Required aberto; status `rascunho`. Nit aberto não impede a proposta, mas precisa ser fechado antes da confirmação.
- **Request changes:** há Critical ou Required aberto; status `request-changes`.

Só o líder grava `aprovado`, na finalização.

### 4. Re-review

Todo achado é resolvido. Só Critical e Required passam por re-review; Nit fecha quando o líder confere os testes afetados verdes no relatório da correção e marca o `[x]`.

1. Confira que o commit `task(<alvo>:Rn,...)` existe e que seus IDs são exatamente os R* marcados `[x]` desde a etapa anterior; divergência volta ao líder.
2. Julgue só o diff da correção contra os R* que ela fecha.
3. Se a regressão falhou na etapa anterior, rerode primeiro só o comando que falhou e, verde, os níveis que não chegaram a rodar.
4. Rerode a regressão completa só quando a correção tocou código compartilhado: módulo, contrato, componente ou configuração usado fora dos paths dos R*.

No máximo duas rodadas de correção. Na segunda sem convergência, o revisor devolve os R* restantes e o líder os traz ao humano com recomendação.

## Saída

O relatório fixo de `references/delegation.md` acrescenta `veredito`, `abertos`, `fechados`, `critical_encontrados`, `decisoes_vigencia`, a regressão (comandos, resultado, `HEAD`) e os registros gravados em `.erros-encontrados/`. O revisor não pergunta ao humano: veredito que depende dele volta como `estado: pergunta`. O revisor não commita, não faz push, não edita `AGENTS.md`, não marca aprovação humana nem `[x]` e não corrige código.

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
