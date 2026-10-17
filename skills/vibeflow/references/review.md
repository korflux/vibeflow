# Etapa review

O líder nunca escreve `review.md`. A review não edita código, teste nem lockfile. Pergunta aberta no arquivo é defeito. Correções acontecem na etapa implement; o Git só é finalizado depois do Approve e da confirmação humana. Decisões vigentes em `AGENTS.md` só mudam após Approve sem bloqueios e confirmação humana explícita.

## Entrada

- Gate (`SKILL.md`, seção 3): todas as T* concluídas com commit; em medium, o commit `task(medium): ...` da entrega; no MVP, interview, spec, plan e analyze presentes.
- Sem alvo e sem diff: peça path, branch ou PR. Phase do diff diferente da phase aberta: use a phase do diff ou peça o path; não grude review nova no `n` de outro pedido.
- Medium: o líder fixa o alvo de uma phase nova (`references/disco.md`) e o `review.md` nasce com `# Rota: medium` (`references/implement.md`, seção 8). `review.md` existente recebe a próxima etapa no mesmo arquivo.
- O revisor lê o `plan.md` (caixas, `Arquivos:`, `Prova afetada:`, `Regressão completa`, linhas `Estado:` e `Resumo:`), `spec.md`, `analyze.md` quando houver, `interview.md`, `AGENTS.md`, o `git log` com os commits da phase (`references/disco.md`, Commits) e o diff da phase. O intervalo do diff vai do commit anterior ao primeiro commit `task(<alvo>:...)` até `HEAD`, ou da base que o líder informar; em medium, do commit anterior ao `task(medium): ...` registrado no Contexto do `review.md`, julgado contra o brief, sem T*. Commits de outro alvo dentro do intervalo não são julgados e vão para Notas.

Declare em até 7 linhas: rota, tipo, alvo, fila, spec, analyze e diff.

```text
rota: max · final · etapa 1 · alvo: .vibeflow/phases/phase-2-agenda-online/ · fila: concluída · spec: sim · analyze: sim · diff: a1b2c3d..HEAD
```

## Quem faz

| Quem | Faz |
|---|---|
| Revisor de contexto limpo | Julga, executa a `Regressão completa`, grava a etapa no `review.md` e devolve o relatório |
| Líder | Delega, leva ao humano as perguntas que definem o veredito, roteia os R* (`references/implement.md`) e pede a confirmação final |
| Finalizador | Executa a seção Finalizar depois da confirmação humana |

Sem subagentes, o líder grava o estado e instrui abrir chat novo com `/vibeflow review`; esse chat segue o Modo B do `SKILL.md`, seção 7: escreve a review como revisor e, depois de gravá-la, conduz como líder as perguntas, a confirmação e a finalização inline.

## Passos

### 1. Escolher o tipo

| Sinal | Ação |
|---|---|
| T* abertas | Não faça review; devolva à etapa implement com a lista do que falta |
| Todas as T* concluídas, ou entrega medium commitada | Review final da integração e dos riscos alterados |
| Intenção, sucesso ou fora frouxos | Devolva à interview ou à spec |
| "Já corrige" | Grave o veredito primeiro; a correção segue pela etapa implement |
| MVP sem cadeia max completa | Recuse e aponte a etapa ausente |

Barra de Approve: saúde do código e convenção do repo, sem bloquear gosto. Em medium, julgue rastreabilidade contra o brief e inspecione o resultado renderizado só quando ele fizer parte do aceite. Segurança e banco só abrem se o diff tocar essas superfícies.

### 2. Conferir a solicitação original

1. Recupere a solicitação original e as alterações autorizadas pelo humano no contexto e em `interview.md`. Ausência no plan não retira obrigação aplicável.
2. Preencha a matriz de Cobertura da solicitação: item e fonte, implementação, evidência e situação `atendido`, `parcial`, `ausente` ou `retirado explicitamente pelo humano`, citando a decisão humana na retirada. Relacione A*/C* quando existirem.
3. Obrigação parcial ou ausente abre R* Required ou Critical e bloqueia Approve. Origem insuficiente é declarada como limitação e devolvida ao líder, sem certificar completude.

### 3. Auditar o executado

1. **Diff na união:** todo path alterado fora de `.vibeflow/` pelos commits da phase está na união dos `Arquivos:` das T* (regras de `references/plan.md`), ou no recorte do brief em medium, ou é path que o remédio de um R* desta review manda alterar; path fora abre R* Required com o remédio de declará-lo ou desfazê-lo. Arquivo novo em `.erros-encontrados/` vai para Notas.
2. **Consumidor compartilhado:** para cada par de T* sem `Deps` entre si, confira que todo consumidor de contrato, componente ou texto que elas compartilham continua coerente com as mudanças de ambas; incoerência abre R* com o path do consumidor.
3. **Commits:** cada T* com caixa marcada aparece num commit `task(<alvo>:...)` com seu ID e paths coerentes com seus `Arquivos:`. T* marcada sem código correspondente vira R* Critical `gap: missing`.
4. **Cobertura por prova:** a evidência de cada A*/C* cita a `Prova afetada:` da T* que o declara ou a regressão completa; sem nenhuma das duas, a situação é `parcial`.

### 4. Executar as provas

- Execute a `Regressão completa` do plan uma vez, no estado integrado final, e registre comando, resultado e `HEAD` em "Provas executadas". E2E excluído pelo plan com motivo não roda; registre a exclusão.
- Árvore suja em path de código ou teste: não execute; devolva `estado: bloqueado` pedindo o isolamento.
- Paths de código e teste são todos os do repo fora de `.vibeflow/` e de `.erros-encontrados/`, inclusive docs, skills e config; registro novo em `.erros-encontrados/` não conta como árvore suja. `AGENTS.md` fica fora quando todo o seu diff cai em `## Decisões vigentes`.
- Repita a regressão antes do Approve somente se algum path de código ou teste mudou desde a última execução verde, comparando o `HEAD` registrado com a árvore atual.
- Provas afetadas das T* com inputs inalterados são reaproveitadas; mudança em plan, spec ou review não invalida prova de código.
- Plan sem `Regressão completa`: use a verificação agregada do repo (CI ou comandos do `AGENTS.md`) e registre a origem; sem nenhuma das duas, devolva a necessidade ao líder, sem aprovar.
- Re-review: confira primeiro que o commit `task(<alvo>:Rn,...)` existe e que seus IDs são exatamente os R* marcados `[x]` desde a etapa anterior; divergência bloqueia Approve e volta ao líder. Reaproveite a prova da correção certificada pelo verificador quando seus inputs não mudaram.
- Falha abre R* Required com o comando e o remédio. Approve exige regressão completa verde sobre o código final.

### 5. Julgar o código

1. **Rastreabilidade:** cruze a matriz da solicitação com a Cobertura da origem da spec, os A*/C* e o plan. Item aplicável da interview sem destino na spec é lacuna de escopo.
2. **Testes:** cace falsos positivos (sem asserção real, `assert True`, teste que só exercita mock). Testes consolidados mantêm cobertos os cenários removidos. Verifique bordas e erros das superfícies alteradas.
3. **Segurança:** nas superfícies tocadas, siga `references/review/security-and-hardening.md`: injeção (SQL, XSS, shell, SSRF), limite de tamanho, IDOR e segredo exposto. Brecha explorável vira R* Critical; falta de limite ou validação de borda, R* Required.
4. **Visual:** inspecione quando o plan marca `Visual: necessária` ou o diff revela saída renderizada relevante não prevista, conforme `references/review/ui-visual-quality.md`; reaproveite evidência válida. Com `design.md`, mudança em componente ou token de `Superfícies compartilhadas` reconfere todas as telas listadas ali. `icon-only` só para ação universal, com nome acessível, área adequada, foco visível e tooltip quando aplicável. Ferramenta ausente segue a regra de instalação de `references/delegation.md`; sem capacidade, R* Required.
5. **Qualidade:** simplificação, reutilização e ausência de duplicação no recorte, comentários semânticos nas funções criadas ou alteradas e a barra de `references/definition-of-done.md`. Decisão crítica desrespeitada ou conflito aberto bloqueia Approve.
6. **Banco e precisão:** se o diff tocar persistência ou valores monetários, siga `references/database-and-migrations.md`: `FLOAT` em dinheiro, query não parametrizada e migration destrutiva sem rollback e autorização são Critical; FK sem índice, N+1, `SELECT *` desnecessário e paginação por `OFFSET` massivo são Required.

Finding: evidência (path), severidade, remédio nomeado e prova; sem evidência concreta não entra. Achado novo recebe o próximo `R*` livre, sem renumerar fechados. R* cujo remédio altera paths de `Arquivos:` traz `papel: redator` quando é só prosa desses paths e `papel: corretor` nos demais casos; remédio de prosa em `plan.md`, `spec.md` ou `AGENTS.md` (inclusive acrescentar T*) também leva `papel: redator`; remédio em `review.md` é do revisor, sem `papel`. O finalizador só marca. Todo R* aberto bloqueia Approve, inclusive Nit; informação sem remédio vai para Notas. Preferência pessoal sem fundamento não é achado. Não ofereça Approve com defer.

### 6. Gravar

O revisor cria o `review.md` a partir de `templates/review.md`, ou acrescenta `### Etapa N` ao vivo sem apagar etapas anteriores, e marca a proposta (`Approve` ou `Request changes`) no veredito vigente. Uma casa por fato; omita seção que a etapa não precisa (Execução e Cobertura sempre que houver plan e spec; Visual e Segurança só quando abertas). Status: `rascunho` enquanto o Approve aguarda confirmação; `request-changes` com R* bloqueante aberto; `aprovado` só na finalização.

## Saída

O relatório fixo de `references/delegation.md` acrescenta `veredito` (`Approve final` ou `Request changes`), `abertos`, `fechados`, `critical_encontrados` e `decisoes_vigencia`, além da cobertura da solicitação e de qualquer limitação de origem. O revisor não pergunta ao humano: veredito que depende dele volta como `estado: pergunta`. É proibido ao revisor finalizar, commitar, fazer push, editar `AGENTS.md`, marcar aprovação humana ou `[x]` de R* e corrigir código.

## Fechar e próxima etapa

Request changes devolve à etapa implement, passo corrigir. Approve final sem R* aberto ainda é proposta até o humano ler e confirmar.

### Finalizar

Depois da confirmação humana explícita, com todas as T* concluídas (no medium, o commit `task(medium): ...`) e nenhum R* aberto. O finalizador:

1. Marca `# Status: aprovado` e a aprovação humana no `review.md`; o veredito Approve, já marcado pelo revisor, não é alterado.
2. Com **Decisões para vigência** preenchida, aplica patch mínimo em `AGENTS.md`: uma única seção `## Decisões vigentes` com a tabela `ID | Decisão vigente | Fonte`, atualizada por ID, preservando linhas não citadas e usando como fonte o review aprovado. Justificativa e histórico ficam nos artefatos. Relê e confirma que só os IDs aprovados mudaram. Sem decisões, não toca regras.
3. Confirma que a regressão completa verde registrada continua válida, executa `git diff --check` e gitleaks quando o repo prevê.
4. Compara `git status` com o estado registrado na última etapa; path fora da phase, das decisões aprovadas ou das correções registradas interrompe e pede isolamento. Em medium, o código da entrega já está no commit `task(medium): ...` e nos commits de correção, e o diff fora da phase que eles contêm é aceito.
5. Faz staging explícito só dos paths residuais autorizados (`git add -- <path da phase> AGENTS.md`), confere `git diff --cached --check` e cria `chore(<alvo>): finalize review` (`references/disco.md`, Commits); sem residual, não cria commit vazio.
6. Confere o intervalo do push como no passo 2 da retomada abaixo e executa `git push` para o upstream do branch atual, sem `--force`. Humano que recusa ou adia o push: grave a linha de push adiado (`references/disco.md`, Estado da phase) e commite-a como `chore(<alvo>): push adiado` (`references/disco.md`, Commits), sem push. Falha de commit é relatada com a causa segura e corrigida antes do push. Sem upstream ou com falha de push, a phase fica fechada com push pendente, retomada pela linha de push pendente da tabela de estados de `references/disco.md`, e a causa segura é relatada.
7. Relata hash final, resultado do push e paths enviados.

Retomada de push pendente (linha de push da tabela de estados de `references/disco.md`), com a confirmação humana:

1. Se o residual da finalização (`# Status: aprovado` e aprovação humana no `review.md`) ainda não foi commitado, commita-o como no passo 5.
2. Confere `git log @{u}..HEAD` ou, sem upstream, os commits desde a base da phase. Commits de alvo fechado e `task(express): ...` podem seguir; commit de phase ou MVP aberto, ou `task(medium): ...` sem phase fechada que o registre, nunca entra nesse push: havendo um, para e relata.
3. Executa `git push` sem `--force`; sem upstream, `git push -u origin <branch>`.
