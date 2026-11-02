# Etapa implement

Um passo só é concluído com prova verde e commit real. O plan define a ordem e guarda o estado nas caixas; a review guarda os achados; o Git guarda o histórico. Formatos de passo, checkpoint, commit e estado moram em `references/disco.md`.

## Entrada

- Gate: em `high` e `mvp`, spec aprovada e `plan.md` com `## Achados do analyze`. Low e medium não têm plan.
- Leia o `plan.md` (caixas, `Arquivos:`, `Prova:`, checkpoints), o `review.md` quando existir, `git status` e o `git log` com os commits do alvo.

| Situação | Como conduzir |
|---|---|
| Low sem phase de origem | Brief curto ao implementador, prova proporcional por `references/testes.md`; o líder confere o relatório e commita com staging explícito dos paths entregues, sem push, sem phase nem artefato |
| Ajuste de uma phase ou do MVP | `references/ajuste.md` |
| Medium | Rota medium |
| `high` ou `mvp` com os perfis carregados | Passos 1 a 4 |
| Sem subagentes ou perfil exigido ausente | Modo B (`references/retomada.md`) |

## Quem faz

| Trabalho | Responsável |
|---|---|
| Codar, escrever os testes e rodar a `Prova:` do passo | Implementador, conforme `references/implementador.md`; redator nos passos de prosa |
| Conferir o relatório, marcar a caixa e commitar | Líder |
| Checkpoint | Verificador de contexto limpo |
| Review | Revisor de contexto limpo (`references/review.md`) |
| Corrigir achados | Implementador no código e nos testes; redator na prosa |

O líder nunca edita código nem executa teste. Antes do primeiro passo, confira nas ferramentas do host os perfis exigidos; perfil ausente leva ao Modo B, com aviso de uma linha e a sugestão de rodar `/vibeflow init` e recarregar o host.

## Passos

### 1. Executar o passo

1. Pegue o primeiro número com caixa aberta. Passo sozinho vai a um implementador; grupo paralelo (`2a`, `2b`) vai num único despacho, em chamadas paralelas, um implementador por passo, cada um com ownership exclusivo dos `Arquivos:` do seu passo. Passo que precise de path fora do recorte volta ao líder antes de editar.
2. O implementador coda, escreve os testes e roda a `Prova:` do passo (`references/implementador.md`). Prova vermelha volta ao mesmo implementador, que tem o contexto, até ficar verde ou virar impedimento real.
3. O líder lê o relatório e confere que os arquivos alterados batem com o `Arquivos:` do passo (`references/delegation.md`, Conferência do líder). Divergência volta ao implementador.
4. Com o passo verde, ou com todos os passos do grupo verdes, o líder marca as caixas e faz um commit para o passo ou para o grupo, com staging explícito dos paths conferidos e `git diff --cached --check` limpo. Falha de commit mantém a caixa aberta.

### 2. Checkpoint

Com todos os passos anteriores a uma linha `Checkpoint:` marcados, o líder despacha um verificador de contexto limpo com brief que traz só o diff do grupo e os critérios listados; ele segue `references/verificador.md`. A posição e o número de checkpoints seguem `references/disco.md` (Checkpoint).

Falha volta ao implementador do passo que a causou; a correção entra no commit seguinte do grupo, no formato de passo. Verde, o líder marca a caixa do checkpoint, que entra no próximo commit da phase. Flake ou achado fora do recorte que o verificador registra em `.erros-encontrados/` também entra no commit seguinte da phase (`references/disco.md`, Glossário). Phase sem checkpoint segue direto para a review.

### 3. Revisar

Com todos os passos e checkpoints marcados, o revisor de contexto limpo executa `references/review.md` no alvo.

### 4. Corrigir achados

Roteie cada R* aberto pelo `papel:`: `implementador` para código e testes, `redator` para prosa; remédio em `review.md` volta ao revisor. Quem corrige roda os testes afetados da correção e devolve o relatório. O líder confere, marca `[x]` nos R* comprovados e commita `task(<alvo>:Rn,...)`. A re-review, o limite de rodadas e a confirmação final seguem `references/review.md`.

## Rota medium

1. O líder escreve no brief os critérios de aceite `A1`, `A2` em diante, na forma de `references/spec.md` (Critérios de aceite). O implementador entrega a mudança com a prova por `references/testes.md`, e o líder confere o relatório.
2. Prova verde, o líder faz staging explícito dos paths entregues, confere `git diff --cached --check` e commita `task(medium): <resultado>` com os critérios do brief no corpo (`references/disco.md`, Commits).
3. A review abre a phase: o líder fixa o alvo e o revisor cria o `review.md` com `# Rota: medium`, registra o commit `task(medium): ...` como base e julga o diff contra os critérios do corpo desse commit.
4. Achados seguem o passo 4, com commit `task(<alvo>:Rn,...)`.

## Saída

Caixas marcadas no `plan.md`, commits `task(...)` e o `review.md` do revisor. Não copie hashes, logs ou histórico de comandos para Markdown.

## Fechar

Responda com o resultado, a linha de progresso do `SKILL.md`, as provas, os commits e paths, as pendências e o próximo passo. Pergunta material vai ao humano com recomendação; trabalho independente segue enquanto ela está pendente. Na retomada, o disco indica o passo e código válido não é refeito.
