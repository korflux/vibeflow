# Etapa implement

Sem integração verde e commit real, nenhuma T* é concluída. Push e decisões vigentes exigem review independente e confirmação humana. O plan define o trabalho e guarda as linhas `Estado:` e `Resumo:`; a review guarda os achados; o Git guarda o histórico.

## Entrada

- Gate (`SKILL.md`, seção 3): em `high` ou acima, plan aprovado; em `max` e MVP, também analyze aprovado e limpo. Low (inclusive Express) e medium não exigem plan.
- Leia o `plan.md` (caixas, linhas `Estado:`, `Deps`, `Arquivos:`, `Prova afetada:`), o `review.md` quando existir, `git status` e o `git log` com os commits do alvo (`references/disco.md`, Commits).

| Situação | Como conduzir |
|---|---|
| Low sem phase de origem (Express, definido no `AGENTS.md` do projeto) | Ajuste direto do líder quando cabe nos limites do `SKILL.md`, seção 5, item 3; senão, brief curto ao implementador e prova proporcional (seção 9); com a prova verde, o finalizador faz staging explícito dos paths entregues e cria `task(express): <resultado>`, sem push, sem init, `.vibeflow/`, phase ou artefato |
| Ajuste de uma phase ou do MVP | Ajuste de phase, abaixo |
| Medium | Seção 8 |
| Plan aprovado e perfis exigidos carregados | Modo A: seções 1 a 6 |
| Sem subagentes, perfil exigido ausente ou humano pede uma T* por run | Modo B: seção 7 |

O modo é decidido na run pela capacidade do host e pelo pedido do humano, sem marcador no plan. Plan em rascunho segue a aprovação implícita do `SKILL.md`, seção 3.

### Ajuste de phase

Ajuste é o pedido low ou medium que corrige, completa ou alinha o que uma phase ou o MVP entregou ou está entregando, sem mudar decisão, banco, autenticação ou autorização da spec. Inclui corrigir um registro de `.erros-encontrados/` que caia nesse escopo. Ajuste volta à phase de origem, aberta ou fechada, e nunca abre phase nova; pedido high ou acima, ou que muda o que a spec decidiu, abre phase nova com substituição explícita. O líder identifica a origem pelo assunto e pelos paths e a anuncia em uma linha; na dúvida entre duas phases, pergunte.

| Situação da phase de origem | Como o ajuste entra |
|---|---|
| Planejamento, antes do gate de implement | Vira insumo do artefato vivo da etapa, gravado pelo dono dela; nenhum código antes do plan |
| Gate de implement satisfeito e sem `review.md` | O redator acrescenta ao `plan.md` uma T* curta com `Arquivos:` e `Prova afetada:`; o pedido do humano vale como aprovação dessa T*, sem novo analyze. A T* segue as seções 1 a 3; ajuste visual segue o `design.md` existente |
| `review.md` aberto | O líder pede ao revisor que registre o ajuste como R* na etapa vigente, com `papel:`; segue a seção 5 |
| Fechada | O líder acrescenta ao `review.md` uma etapa `### Ajuste N - <pedido>`, com o pedido e `Abriu: Rn`, e um R* de ajuste por item no grupo Required da Checklist de correções; segue a seção 5. Low: o `# Status: aprovado` é mantido e não há re-review; o finalizador marca o `[x]` somente no handoff do commit `task(<alvo>:Rn,...)`, que inclui o `review.md` da phase, os paths do R* e o registro apagado, e desfaz o `[x]` se o commit falhar. Medium: ao abrir a etapa, o finalizador muda o status para `request-changes` e desmarca o Approve do Veredito vigente e a Aprovação humana; o ajuste segue a seção 5, a re-review de ajuste (`references/review.md`) e a confirmação da seção 6 |

R* de ajuste, no grupo Required:

```text
- [ ] Rn: **Required** - `path` - <pedido do humano> - remédio: <o pedido> - prova: <Prova afetada derivada, seção 9> - source: <pedido humano | path do registro de .erros-encontrados/> - gap: missing - papel: <corretor | redator>
```

Entrega medium ainda sem `review.md`: antes do commit `task(medium): ...`, o ajuste entra no recorte da própria entrega; depois dele, o líder passa o ajuste ao revisor, que o registra como R* na review que abre a phase. Sem phase de origem, o ajuste low segue Express.

Registro de `.erros-encontrados/`: a correção apaga o arquivo do registro no mesmo commit, e o Git guarda o histórico; esta é a casa da regra.

## Quem faz

| Passo | Responsável |
|---|---|
| Implementar por ondas | Implementador; redator nas T* de prosa; explorador prepara as próximas |
| Validar | Verificador |
| Corrigir falha de validação | Corretor |
| Commitar | Finalizador |
| Revisar | Revisor de contexto limpo, conforme `references/review.md` |
| Corrigir achados | Corretor ou redator, pelo `papel:` de cada R* |
| Confirmar e finalizar | Líder pergunta; finalizador executa |

Antes da primeira onda, confira nas ferramentas do host os perfis exigidos pela rota (`SKILL.md`, seção 5). Perfil ausente ou não carregado leva ao Modo B (seção 7), com aviso de uma linha e a sugestão de rodar `/vibeflow init` e recarregar o host.

## Passos (Modo A)

### 1. Implementar por ondas

1. Liste as T* elegíveis: `Estado: pendente` e todas as `Deps` concluídas. Com Node, `node <pasta da skill>/scripts/ondas.mjs --json` devolve as elegíveis e a onda dos passos 1 e 2.
2. Monte a onda percorrendo as elegíveis em ordem numérica e incluindo cada T* cujos `Arquivos:` não se sobrepõem aos das já incluídas, pelas regras de `references/plan.md`. T* sem `Arquivos:` comparáveis roda sozinha: só entra quando a onda está vazia e a encerra.
3. O finalizador marca `Estado: em andamento` nas T* da onda. Despache todas elas numa única rodada, em chamadas paralelas, cada responsável com ownership exclusivo dos `Arquivos:` da sua T*. T* que precise de path fora do recorte volta ao líder antes de editar e é serializada.
4. Enquanto a onda trabalha, o explorador prepara em leitura as T* que ela libera.
5. Confronte cada devolutiva com o objetivo da phase (`SKILL.md`, seção 5). Cada T* verde vai ao verificador com sua `Prova afetada:`, sem esperar a onda; falha vai ao corretor sem bloquear as demais. Impedimento real que o corretor não resolve deixa a T* `bloqueada` e vai ao humano.
6. Com a onda verificada, o finalizador atualiza no `plan.md`, num único handoff, as linhas `Estado:` e `Resumo:` de cada T* da onda. A caixa só é marcada no commit.

### 2. Validar a onda

O verificador confere diff, ownership, aceite e cobertura e executa a união das `Prova afetada:` das T* da onda no estado integrado, sobre os commits das ondas anteriores, cada comando uma vez, sem ampliar para a suíte completa. Prova verde de inputs inalterados é reaproveitada. Falha vai ao corretor, que resolve pela causa raiz, sem R* artificial; o verificador renova só a prova afetada, incluindo consumidores. Essa correção não conta rodada de review.

### 3. Commitar a onda

Com a integração da onda verde, o finalizador marca as caixas e o `Estado: concluída` das T* comprovadas e os critérios provados no `spec.md`, faz staging explícito dos paths certificados, confere `git diff --cached --check` e a lista de paths e cria `task(<alvo>:T1,T2,...): <resultado>` (`references/disco.md`, Commits). Falha mantém o commit pendente; caixa marcada sem commit real não libera a review. Volte à seção 1 para a próxima onda; sem T* pendente nem bloqueada, siga para revisar.

### 4. Revisar

O revisor de contexto limpo executa `references/review.md` no alvo, incluindo a `Regressão completa` do plan, grava `review.md` e devolve veredito, cobertura, R* e decisões propostas.

### 5. Corrigir

Roteie cada R* aberto: `papel: redator` vai ao redator e `papel: corretor` ao corretor; sem `papel`, remédio de prosa em `plan.md`, `spec.md` ou `AGENTS.md` vai ao redator e remédio em `review.md` ao revisor; o finalizador só faz as marcações. Todos os R* abertos são atendidos na rodada. O verificador certifica as correções e as provas afetadas; o finalizador marca `[x]` somente nos R* comprovados e commita `task(<alvo>:Rn,...): <resultado>`; o revisor faz nova review. São no máximo duas rodadas de correção: na segunda sem convergência, pare e relate os R* restantes.

### 6. Confirmar

Apresente resultado, commits, correções, Critical encontrados e decisões propostas, e peça uma única confirmação para aprovar a review, publicar essas decisões e fazer push. Com ela, delegue ao finalizador a finalização de `references/review.md` (seção Finalizar), com o texto humano e o escopo exatos. Ajuste pedido na resposta é tratado como correção e volta à review. Sem confirmação, nada é aprovado, publicado ou enviado.

## Passos (Modo B)

### 7. Uma T* por run

Informe a limitação em uma linha quando vier da falta de subagentes. Execute inline a elegível de menor número, ou a T* que o humano nomeou, seguindo a seção 9. Com a prova verde, marque a caixa e as linhas `Estado:` e `Resumo:` e crie `task(<alvo>:Tn): <resultado>` com staging explícito, sem push. Responda com a T* executada, a linha de progresso do `SKILL.md`, seção 9, a prova, o hash e a próxima T*. Grupo de T* paralelas registrado no plan só roda em paralelo depois de o humano aceitar; senão, segue em sequência. Com todas concluídas, a review roda em chat novo com `/vibeflow review`. Correção de R* no Modo B segue a seção 5 inline, numa rodada por run, com commit `task(<alvo>:Rn,...)`; medium no Modo B segue a seção 8 inline, com o líder nos papéis.

## Rota medium

### 8. Implement e review sem plan

1. O implementador entrega a mudança do brief com prova proporcional (seção 9).
2. O verificador certifica a prova; falha vai ao corretor.
3. Com a prova verde, o finalizador faz staging explícito dos paths entregues, confere `git diff --cached --check` e cria `task(medium): <resultado>`.
4. A review abre a phase: o líder fixa o alvo (`references/disco.md`), e o revisor cria o `review.md` com `# Rota: medium`, registra no Contexto o commit `task(medium): ...` como base, usa como início do diff o commit anterior a ele e julga o diff contra o brief, sem T*.
5. Correções seguem a seção 5, com commit `task(<alvo>:Rn,...): <resultado>`; a confirmação segue a seção 6.

## Trabalho de quem implementa

### 9. Reconhecer, codar e provar

1. **Reconhecer:** trace entrada, chamadas, consumidores, padrões compartilhados e a prova da jornada antes de editar, sem varredura cega. Edite somente os `Arquivos:` da T* ou o recorte do brief. UI segue design, tokens e motion aprovados quando existirem.
2. **Codar e simplificar:** reutilize o que existe no projeto, na standard library, na plataforma e nas dependências instaladas. Código e testes acompanham a entrega; complemente só lacunas concretas de comportamento, erro ou risco. Prefira um teste que percorra a jornada com resultados observáveis; não crie um teste por função, campo ou T*. Remova duplicação no recorte, sem abstração especulativa nem limpeza externa. Documente semanticamente decisões e responsabilidades.
3. **Provar:** execute a `Prova afetada:` da T*. Sem ela (low ou medium), derive o recorte: testes do módulo tocado e dos consumidores diretos, e E2E só do cenário cuja entrada mudou, com o smoke da entrada alterada. Os níveis de prova estão em `references/delegation.md`.
4. **Visual:** quando o aceite depender da UI renderizada, siga `references/chrome-devtools.md`. Limitação visual necessária impede certificação.
5. **Entregar:** relatório fixo com paths, inputs reais, comando e resultado da prova e pendências. Barra de acabamento em `references/definition-of-done.md`; banco ou dinheiro exige `references/database-and-migrations.md`.

Prova vermelha exige correção da causa, sem limite de tentativas antes da review; não enfraqueça, pule ou apague teste para obter verde, e mudança de asserção exige justificativa pelo aceite. Credencial, conta, pagamento, elevação administrativa ou integração persistente são impedimentos reais: relate a tentativa, o impedimento e a recomendação.

## Saída

Caixas e linhas `Estado:` e `Resumo:` no `plan.md`, critérios provados no `spec.md`, commits `task(...)` e `review.md` do revisor. Nunca copie hashes, logs ou histórico de comandos para Markdown; não crie `implement.md`, `todo.md` nem `tasks.md`.

## Fechar e próxima etapa

Responda com resultado, a linha de progresso do `SKILL.md`, seção 9, provas, commits e paths, pendências e próximo passo. Pergunta material vai ao humano com recomendação, e trabalho elegível independente segue enquanto ela está pendente. Na retomada, o disco indica o passo; evidência inalterada é preservada e implementação válida não é refeita.
