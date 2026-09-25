---
name: vibe-implement
description: >
  Implementa e prova mudanças em código de software, registra a T* concluída no plan.md e cria seu commit local. Use when the user runs /vibe-implement, pede código, build, correção de bug, alteração de UI em código ou execução de T* de software, mesmo que não diga vibe-implement. Não se aplica a redação ou edição apenas de texto e documentos.
---

# vibe-implement

Sem prova verde, não marque `[x]` nem faça commit. Cada T* concluída gera um commit isolado, sem push. `plan.md` é o registro único; não crie `implement.md`, `todo.md` ou `tasks.md`. No fluxo padrão, sem `.vibeflow/`: `/vibe-init`. No MVP, código exige analyze aprovado e limpo.

## 0. Classificar Express e usar o script

1. Antes de exigir `.vibeflow/` ou rodar script, separe texto/documento avulso de código de software. Texto puro segue edição direta, fora desta skill. Express é mudança de código clara e localizada, sem comportamento novo, como cor ou espaçamento na UI. Faça patch e checagem proporcionais; não rode `vibe-init` nem crie ou exija `.vibeflow/`. Na entrega atual, atualize a T* aberta ou acrescente uma T* curta ao plan existente; achado de review atualiza o R* existente. Reuse o design existente quando couber. Alterar comportamento, rota, interação, aceite, acessibilidade ou tocar privacidade, obrigação jurídica, autenticação, autorização, pagamento, segredo, persistência ou perda de dados sai do Express e segue a cadeia aplicável.
2. Fora do Express, leia o motor antes de executá-lo: `scripts/implement.ps1` no Windows ou `scripts/implement.py` no Unix. Ele seleciona alvo e fila; não cria artefato. Execute no repo com `pwsh "<skill>/scripts/implement.ps1"` ou `bash "<skill>/scripts/implement.sh"`. Para MVP, acrescente `-Mvp` ou `--mvp`.
3. Leia o JSON no stdout, restrito a `alvo`, `fila` e `avisos` (`analyze_gate` no MVP). Escolha pela `fila.elegiveis`. Localize regras, paths e símbolos com `rg --files` e `rg -n`; abra apenas o fluxo relevante, não a árvore inteira.

No fluxo padrão, `INIT_AUSENTE` exige init. `IMPLEMENT_SEM_ALVO`, `IMPLEMENT_SEM_PLAN`, `IMPLEMENT_ANALYZE_AUSENTE`, `IMPLEMENT_ANALYZE_RASCUNHO`, `IMPLEMENT_ANALYZE_BLOQUEADO`, `MVP_INESPERADO`, `MODO_INVALIDO`, `FASE_AUSENTE` e `PHASES_INESPERADO` não são contornados.

## 1. Selecionar a execução

Escolha internamente a rota `low|medium|high|xhigh|max`; não anuncie modo, alvo ou fila na abertura do chat. Modo A é o padrão: execute uma T* elegível. “Pode seguir” escolhe a próxima. Modo B percorre o plano inteiro somente se o humano pedir execução completa. “Ok” ou “aprovado”, isoladamente, não autoriza avançar.

Priorize R* Critical/Required aberto em `review.md`. Se o humano nomeou uma T* elegível, execute-a; caso contrário, escolha a elegível de menor número, inclusive quando houver várias. Se nenhuma estiver elegível, mostre as dependências que faltam ou encaminhe para `vibe-review` quando todas estiverem concluídas. `low`/`medium` sem plan pode ser avulso, com prova proporcional.

Quando o plan registrar grupo paralelo elegível, informe os IDs e o motivo do agrupamento e pergunte se o humano prefere paralelo ou sequência. Sem resposta afirmativa, execute em sequência. Paralelo exige isolamento e ownership seguros; a autorização vale apenas para o grupo nomeado. Recomende chat novo por T* e para review sem transformar essa recomendação em gate.

## 2. Verificar impedimentos reais

Para `high+` sem plan, execute o handoff para `vibe-plan`; para `max` sem analyze aprovado e limpo, execute o handoff para `vibe-analyze`. No MVP, analyze ausente, rascunho ou bloqueado impede código. Se o humano pediu esta skill e o único pendente for `# Status: rascunho` do plan, aprove essa linha e prossiga. Nunca contorne erros de proteção do script.

Antes de declarar bloqueio, tente resolver o que está sob controle do agente: diagnostique a falha, use outro motor compatível, instale uma ferramenta necessária quando o ambiente e as permissões permitirem, ou escolha uma prova equivalente. Verificação descrita só manualmente pede uma checagem executável ou inspeção direta quando possível; se depender do humano, peça apenas a validação que falta. Ambiguidade material exige a decisão específica, depois de investigar o fluxo real. Só pare por dependência indisponível, proteção explícita ou decisão que não possa ser inferida com segurança; informe a tentativa, o impedimento e a recomendação.

## 3. Ciclo da fatia

Execute cada task seguindo as 6 etapas. O coordenador responde pela integração final, pelos artefatos vivos e pelo índice Git.

1. **Reconhecer:**
   Trace o fluxo real da T* com `rg --files` e `rg -n`: entrada, chamadas, código compartilhado e testes. Reuse helpers, componentes, tipos, biblioteca padrão e recursos nativos existentes. Com UI, siga tokens, motion e provas por tela do `design.md` aprovado quando aplicáveis. No Express, use só o recorte alterado, sem criar artefatos. Na retomada, confira `git status --short`, `HEAD` e `git hash-object -- <path>` do checkpoint; invalide apenas provas com inputs alterados ou sem snapshot suficiente. Revalide a fila e os gates, inclusive analyze aprovado e limpo no MVP.
2. **Escolher execução e delegar quando fizer sentido:**
   Recalcule a fila e respeite `Deps`. Só após o humano aprovar a execução paralela, use delegação nativa se o host oferecer e houver worktree/branch isolada ou ownership sem sobreposição; caso contrário, siga em sequência. Delimite cada entrega por resultado, aceite, dependências, paths exclusivos e comando de verificação. Agentes não alteram os artefatos vivos `plan.md`, `spec.md` ou `review.md`, nem operam o índice Git ou criam commits. Peça paths, diff, prova e pendências; o coordenador integra e libera dependentes após a conclusão registrada.
3. **Codar e integrar:**
   Implemente só o aceite da T*. Localize primeiro as provas da capacidade ou jornada afetada; estenda-as apenas para comportamento, regressão, borda ou risco sem cobertura. Não crie um teste por T* ou critério quando a mesma prova já detecta a falha. O coordenador integra os paths autorizados e resolve conflitos; prova de agente não substitui prova do estado integrado.
4. **Simplificar antes da prova:**
   Remova duplicação e verbosidade no código tocado sem perder validação, segurança ou comportamento. Una testes redundantes somente se outra prova executável preservar cada cenário e afirmação relevante; mantenha erro, borda, permissão e integração. Não limpe a suíte fora da fatia. Deixe comentários semânticos em cada função criada ou alterada.
5. **Executar a prova final:**
   Rode cada prova necessária uma vez, no estado integrado, após simplificar. Smoke Test / Walking Skeleton entra somente quando o ponto de entrada real foi criado ou alterado. Se a prova falhar, corrija a causa raiz e repita a prova afetada. Edição posterior em código ou teste invalida apenas as provas cujos inputs mudaram; edição de plan, spec, review ou outro registro não invalida a prova.
   Inspecione a UI renderizada quando `Visual: necessária` ou quando surgir impacto visual relevante; atualize a classificação nesse caso. `Visual: dispensada` exige prova executável sem resultado visual a julgar. Tocar arquivo de UI, HTML ou DOM, sozinho, não abre navegador. Siga `references/chrome-devtools.md`: navegador integrado, depois `chrome-devtools`, depois Playwright existente ou necessário. Comece pela tela, estado e viewport afetados; amplie se layout, responsividade, interação ou componente compartilhado exigirem. Registre rota, viewport, estado, ações e evidência. Se faltar ferramenta, tente disponibilizá-la antes de declarar limitação. Quando a prova visual for necessária, não marque conclusão sem executá-la. A review reaproveita essa evidência enquanto seus inputs permanecerem válidos. Preserve nome acessível, área de interação, foco e tooltip dos controles compactos; ações ambíguas mantêm texto.
6. **Registrar e fechar:**
   Depois da prova verde, registre no `plan.md` status, paths, prova e bloqueios sob a T*; marque `spec.md`/`review.md` só nos critérios provados. Mantenha `# Status: rascunho` enquanto o registro estiver incompleto; não crie `implement.md` nem altere arquivos históricos. Faça o commit da task antes da resposta final.
   Se a T* permanecer incompleta ou entrar em handoff, adicione sob ela um checkpoint de retomada curto com estado, próximo passo, paths relevantes à prova, `HEAD` de `git rev-parse HEAD` e o hash de `git hash-object -- <path>` para cada input, além do comando e validade da prova. Na retomada, compare `HEAD`, hashes e status do Git; prova sem snapshot suficiente fica inválida. Remova o checkpoint ao concluir a T*, mantendo a prova final e os paths no próprio plan.

Critérios adicionais:
- DoD: `references/definition-of-done.md` no que couber.
- Banco de dados: Se a fatia tocar banco de dados ou dinheiro, siga `references/database-and-migrations.md` (DECIMAL/NUMERIC para valores monetários, queries parametrizadas obrigatórias, sem N+1, índices em FKs, transações ACID curtas).
- Sem teste verde executável, sem marcação de conclusão no disco.

## 4. Marcar e Registrar no plan.md

Após a aprovação do teste da task, a IA aplica o patch diretamente no `plan.md` vivo sob a seção da task `### T{n}:`:

```markdown
### T1: Ponto de entrada e Smoke Test
- [x] T1 concluída
- **Spec:** A1
- **Deps:** nenhuma
- **Verificação:** `npm test -- --grep "smoke"`
- **Prova:** `npm test` -> 1 passing (115ms)
- **Arquivos:** `src/index.ts`, `tests/smoke.test.ts`
- **Decisões:** AUTH-01 (implementada)
```

Outros arquivos marcados:
| Arquivo | O que marcar |
|---|---|
| `spec.md` | `A*` / `C*` **só** os que a fatia provou |
| `review.md` | `R*` Critical/Required que o fix provou |
| `interview.md` | **Não** |

No MVP, certifique-se de registrar quais IDs críticos foram implementados. Não publique essas decisões em `REGRAS.md`; isso pertence ao pós-review aprovado.

### Commit da task

Depois de atualizar os artefatos e antes de declarar a fatia concluída:

1. Compare o Git com o snapshot anterior. Se um path da task já estava alterado, separe o diff preexistente do seu; peça decisão só se não conseguir atribuir as mudanças com segurança.
2. Em execução delegada, somente o coordenador altera artefatos vivos e o índice Git. Liste os paths integrados e provados pela task e adicione-os explicitamente, por exemplo `git add -- path/da/task outro/path`. Nunca use `git add -A` ou `git add .`; o inventário é transitório no stdout e não cria arquivo no workspace.
3. Confira `git diff --cached --check` e `git diff --cached --name-only`. Se o diff indexado contiver path fora da task, remova-o do índice e pare se a origem não for clara.
4. Crie um commit sem `Co-Authored-By`, com mensagem no formato `task(Tn): <outcome curto>`. Não faça `git push` nesta etapa.
5. Registre a mensagem e o hash retornado por `git rev-parse HEAD` no resultado da execução e no chat. Não reabra o `plan.md` apenas para anexar o hash, pois isso criaria um residual fora do commit da task. O próximo estado começa no commit criado.

## 5. Resposta no chat e fechamento

Antes da resposta final, confirme que cada T* concluída tem commit próprio e que `git show --format= --name-only HEAD` contém somente seus paths. Se o commit falhar, resolva a causa e tente novamente; não declare a T* concluída com trabalho verde sem commit. Não faça push: ele pertence ao fechamento aprovado em `vibe-review`.

Responda de forma curta, com: T*/R*/avulsa executada; **total de T*s da fase e quantas estão concluídas** (conte os cabeçalhos `### T{n}:` do plan, não os itens elegíveis); IDs marcados; prova e resultado; paths no commit; mensagem e hash do commit; próximo passo ou impedimento concreto. Para execução avulsa sem plan, informe que não há contagem de T*. Recomende novo chat para a próxima T* ou review sem bloquear a continuidade aqui. Handoff no chat e no arquivo; não invente trabalho extra.
