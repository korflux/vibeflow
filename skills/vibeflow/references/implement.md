# Etapa implement

Sem integração verde e commit real, nenhuma T* é concluída. Push e decisões vigentes exigem review independente e confirmação humana. O plan define o trabalho e guarda o resumo curto; a review guarda os achados; o Git guarda o histórico.

## Entrada

- Gate (`SKILL.md`, seção 3): em `high` ou acima, plan aprovado; em `max` e MVP, também analyze aprovado e limpo. Low (inclusive Express) e medium não exigem plan.
- Leia o `plan.md` (caixas, `Deps`, `Arquivos:`, `Prova afetada:`), o `review.md` quando existir, `git status` e o `git log` com os commits `task(...)`. Phase da v1 segue `references/disco.md`, Phases da v1.

| Situação | Como conduzir |
|---|---|
| Low sem phase ativa (Express, definido em `templates/AGENTS.md`) | Brief curto ao implementador, prova proporcional e fechamento, sem init, `.vibeflow/`, phase ou artefato |
| Low com phase ativa | O redator atualiza a T* aberta ou acrescenta uma T* curta no plan; ajuste visual segue o design existente; depois, a T* segue as seções 1 a 3 |
| Medium | Seção 8 |
| Plan aprovado e perfis exigidos carregados | Modo A: seções 1 a 6 |
| Sem subagentes, perfil exigido ausente ou humano pede uma T* por run | Modo B: seção 7 |

O modo é decidido na run pela capacidade do host e pelo pedido do humano, sem marcador no plan. Plan em rascunho segue a aprovação implícita do `SKILL.md`, seção 3.

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

Antes da primeira onda, confira nas ferramentas do host os perfis registrados na prontidão do plan: explorador, implementador, verificador, corretor, revisor, agente genérico apto a Git e, com T* de prosa, redator. Perfil ausente ou não carregado leva ao Modo B (seção 7), com aviso de uma linha e a sugestão de rodar `/vibeflow init` e recarregar o host.

## Passos (Modo A)

### 1. Implementar por ondas

1. Liste as T* elegíveis: caixa aberta e todas as `Deps` concluídas.
2. Monte a onda percorrendo as elegíveis em ordem numérica e incluindo cada T* cujos `Arquivos:` não se sobrepõem aos das já incluídas, pelas regras de `references/plan.md`. T* sem `Arquivos:` comparáveis roda sozinha: só entra quando a onda está vazia e a encerra.
3. Despache todas as T* da onda numa única rodada, em chamadas paralelas, cada responsável com ownership exclusivo dos `Arquivos:` da sua T*. T* que precise de path fora do recorte volta ao líder antes de editar e é serializada.
4. Enquanto a onda trabalha, o explorador prepara em leitura as T* que ela libera.
5. Confronte cada devolutiva com o objetivo da phase (`SKILL.md`, seção 5). Cada T* verde vai ao verificador com sua `Prova afetada:`, sem esperar a onda; falha vai ao corretor sem bloquear as demais.
6. Com a onda verificada, o finalizador atualiza no `plan.md`, num único handoff, o resumo curto de cada T* e o estado da fila: pronto, em andamento e pendente. A caixa só é marcada no commit.
7. Monte a próxima onda. Sem T* pendente, siga para validar.

### 2. Validar

O verificador confere diff, ownership, aceite e cobertura e executa a união das `Prova afetada:` das T* da phase no estado integrado, cada comando uma vez, sem ampliar para a suíte completa. Prova verde de inputs inalterados é reaproveitada. Falha vai ao corretor, que resolve pela causa raiz, sem R* artificial; o verificador renova só a prova afetada, incluindo consumidores. Essa correção não conta rodada de review.

### 3. Commitar

Com a integração verde, o finalizador marca as caixas das T* comprovadas e os critérios provados no `spec.md`, faz staging explícito dos paths certificados, confere `git diff --cached --check` e a lista de paths e cria `task(T1,T2,...): <resultado>`, com IDs em ordem numérica e sem `Co-Authored-By`. Falha mantém o commit pendente; caixa marcada sem commit real não libera a review.

### 4. Revisar

O revisor de contexto limpo executa `references/review.md` no alvo, incluindo a `Regressão completa` do plan, grava `review.md` e devolve veredito, cobertura, R* e decisões propostas.

### 5. Corrigir

Roteie cada R* aberto: `papel: redator` vai ao redator e `papel: corretor` ao corretor; sem `papel`, remédio de prosa em `plan.md`, `spec.md` ou `AGENTS.md` vai ao redator e remédio em `review.md` ao revisor; o finalizador só faz as marcações. Todos os R* abertos são atendidos na rodada. O verificador certifica as correções e as provas afetadas; o finalizador marca `[x]` somente nos R* comprovados e commita `task(Rn,...): <resultado>`; o revisor faz nova review. São no máximo duas rodadas de correção: na segunda sem convergência, pare e relate os R* restantes.

### 6. Confirmar

Apresente resultado, commits, correções, Critical encontrados e decisões propostas, e peça uma única confirmação para aprovar a review, publicar essas decisões e fazer push. Com ela, delegue ao finalizador a finalização de `references/review.md` (seção Finalizar), com o texto humano e o escopo exatos. Ajuste pedido na resposta é tratado como correção e volta à review. Sem confirmação, nada é aprovado, publicado ou enviado.

## Passos (Modo B)

### 7. Uma T* por run

Informe a limitação em uma linha quando vier da falta de subagentes. Execute inline a elegível de menor número, ou a T* que o humano nomeou, seguindo a seção 9. Com a prova verde, marque a caixa, escreva o resumo curto e crie `task(Tn): <resultado>` com staging explícito, sem push. Responda com a T* executada, o total de T* do plan e quantas estão concluídas, a prova, o hash e a próxima T*. Grupo de T* paralelas registrado no plan só roda em paralelo depois de o humano aceitar; senão, segue em sequência. Com todas concluídas, a review roda em chat novo com `/vibeflow review`.

## Rota medium

### 8. Implement e review sem plan

1. O implementador entrega a mudança do brief com prova proporcional (seção 9).
2. O verificador certifica a prova; falha vai ao corretor.
3. Com a prova verde, o finalizador faz staging explícito dos paths entregues, confere `git diff --cached --check` e cria `task(medium): <resultado>`, sem `Co-Authored-By`.
4. A review abre a phase: o líder fixa o alvo (`references/disco.md`), e o revisor cria o `review.md` com `# Rota: medium`, usando como base do diff o commit anterior a `task(medium): ...` e julgando o diff contra o brief, sem T*.
5. Correções seguem a seção 5, com commit `task(Rn,...): <resultado>`; a confirmação segue a seção 6.

## Trabalho de quem implementa

### 9. Reconhecer, codar e provar

1. **Reconhecer:** trace entrada, chamadas, consumidores, padrões compartilhados e a prova da jornada antes de editar, sem varredura cega. Edite somente os `Arquivos:` da T* ou o recorte do brief. UI segue design, tokens e motion aprovados quando existirem.
2. **Codar e simplificar:** reutilize o que existe no projeto, na standard library, na plataforma e nas dependências instaladas. Código e testes acompanham a entrega; complemente só lacunas concretas de comportamento, erro ou risco. Prefira um teste que percorra a jornada com resultados observáveis; não crie um teste por função, campo ou T*. Remova duplicação no recorte, sem abstração especulativa nem limpeza externa. Documente semanticamente decisões e responsabilidades.
3. **Provar:** execute a `Prova afetada:` da T*. Sem ela (low, medium ou plan antigo), derive o recorte: testes do módulo tocado e dos consumidores diretos, e E2E só do cenário cuja entrada mudou, com o smoke da entrada alterada. Os níveis de prova estão em `references/delegation.md`.
4. **Visual:** quando o aceite depender da UI renderizada, siga `references/chrome-devtools.md`. Limitação visual necessária impede certificação.
5. **Entregar:** relatório fixo com paths, inputs reais, comando e resultado da prova e pendências. Barra de acabamento em `references/definition-of-done.md`; banco ou dinheiro exige `references/database-and-migrations.md`.

Prova vermelha exige correção da causa, sem limite de tentativas antes da review; não enfraqueça, pule ou apague teste para obter verde, e mudança de asserção exige justificativa pelo aceite. Credencial, conta, pagamento, elevação administrativa ou integração persistente são impedimentos reais: relate a tentativa, o impedimento e a recomendação.

## Saída

Caixas e resumo curto no `plan.md`, critérios provados no `spec.md`, commits `task(...)` e `review.md` do revisor. Nunca copie hashes, logs ou histórico de comandos para Markdown; não crie `implement.md`, `todo.md` nem `tasks.md`.

## Fechar e próxima etapa

Responda com resultado, T* comprovadas sobre o total, provas, commits e paths, pendências e próximo passo. Pergunta material vai ao humano com recomendação, e trabalho elegível independente segue enquanto ela está pendente. Na retomada, o disco indica o passo; evidência inalterada é preservada e implementação válida não é refeita.
