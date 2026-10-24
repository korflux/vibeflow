# Etapa implement

Um passo só é concluído com prova verde e commit real. O plan define a ordem e guarda o estado nas caixas; a review guarda os achados; o Git guarda o histórico. Formatos de passo, checkpoint, commit e estado moram em `references/disco.md`.

## Entrada

- Gate: em `high` e `mvp`, spec aprovada e `plan.md` com `## Achados do analyze`. Low e medium não têm plan.
- Leia o `plan.md` (caixas, `Arquivos:`, `Prova:`, checkpoints), o `review.md` quando existir, `git status` e o `git log` com os commits do alvo.

| Situação | Como conduzir |
|---|---|
| Low sem phase de origem | Brief curto ao implementador, prova proporcional por `references/testes.md`; o líder confere o relatório e commita com staging explícito dos paths entregues, sem push, sem phase nem artefato |
| Ajuste de uma phase ou do MVP | Ajuste de phase, abaixo |
| Medium | Rota medium |
| `high` ou `mvp` com os perfis carregados | Passos 1 a 4 |
| Sem subagentes ou perfil exigido ausente | Modo B |

## Quem faz

| Trabalho | Responsável |
|---|---|
| Codar, escrever os testes e rodar a `Prova:` do passo | Implementador; redator nos passos de prosa |
| Conferir o relatório, marcar a caixa e commitar | Líder |
| Checkpoint | Verificador de contexto limpo |
| Review | Revisor de contexto limpo (`references/review.md`) |
| Corrigir achados | Implementador no código e nos testes; redator na prosa |

O líder nunca edita código nem executa teste. Antes do primeiro passo, confira nas ferramentas do host os perfis exigidos; perfil ausente leva ao Modo B, com aviso de uma linha e a sugestão de rodar `/vibeflow init` e recarregar o host.

## Passos

### 1. Executar o passo

1. Pegue o primeiro número com caixa aberta. Passo sozinho vai a um implementador; grupo paralelo (`2a`, `2b`) vai num único despacho, em chamadas paralelas, um implementador por passo, cada um com ownership exclusivo dos `Arquivos:` do seu passo. Passo que precise de path fora do recorte volta ao líder antes de editar.
2. O implementador coda, escreve os testes e roda a `Prova:` do passo (Trabalho de quem implementa). Prova vermelha volta ao mesmo implementador, que tem o contexto, até ficar verde ou virar impedimento real.
3. O líder lê o relatório e confere que os arquivos alterados batem com o `Arquivos:` do passo (`references/delegation.md`, Conferência do líder). Divergência volta ao implementador.
4. Com o passo verde, ou com todos os passos do grupo verdes, o líder marca as caixas e faz um commit para o passo ou para o grupo, com staging explícito dos paths conferidos e `git diff --cached --check` limpo. Falha de commit mantém a caixa aberta.

### 2. Checkpoint

Com todos os passos anteriores a uma linha `Checkpoint:` marcados, um verificador de contexto limpo:

- roda os testes dos passos do grupo e o E2E só dos critérios listados que têm tela;
- confere o diff do grupo contra os critérios listados na spec.

Falha volta ao implementador do passo que a causou; a correção entra no commit seguinte do grupo, no formato de passo. Verde, o líder marca a caixa do checkpoint, que entra no próximo commit da phase. Flake ou achado fora do recorte que o verificador registra em `.erros-encontrados/` também entra no commit seguinte da phase (`references/disco.md`, Glossário). Phase sem checkpoint segue direto para a review.

### 3. Revisar

Com todos os passos e checkpoints marcados, o revisor de contexto limpo executa `references/review.md` no alvo.

### 4. Corrigir achados

Roteie cada R* aberto pelo `papel:`: `implementador` para código e testes, `redator` para prosa; remédio em `review.md` volta ao revisor. Quem corrige roda os testes afetados da correção e devolve o relatório. O líder confere, marca `[x]` nos R* comprovados e commita `task(<alvo>:Rn,...)`. A re-review, o limite de rodadas e a confirmação final seguem `references/review.md`.

## Modo B

Informe a limitação em uma linha. Cada run executa um passo, o primeiro aberto ou o que o humano nomeou: o chat assume o papel do implementador, roda a `Prova:`, marca a caixa e commita, sem push. Grupo paralelo roda em sequência. O checkpoint roda num chat novo com `/vibeflow implement`, que pela tabela de estados cai no checkpoint e o executa como verificador. A review roda num chat novo com `/vibeflow review`. Correção de R* segue o passo 4 inline, numa rodada por run; medium segue a Rota medium inline.

## Rota medium

1. O implementador entrega a mudança do brief com a prova por `references/testes.md`, e o líder confere o relatório.
2. Prova verde, o líder faz staging explícito dos paths entregues, confere `git diff --cached --check` e commita `task(medium): <resultado>`.
3. A review abre a phase: o líder fixa o alvo e o revisor cria o `review.md` com `# Rota: medium`, registra o commit `task(medium): ...` como base e julga o diff contra o brief.
4. Achados seguem o passo 4, com commit `task(<alvo>:Rn,...)`.

## Ajuste de phase

Ajuste é o pedido low ou medium que corrige, completa ou alinha o que uma phase ou o MVP entregou ou está entregando, sem mudar decisão, banco, autenticação ou autorização da spec. Inclui corrigir um registro de `.erros-encontrados/` nesse escopo. Ajuste volta à phase de origem, aberta ou fechada, e nunca abre phase nova; pedido `high`, ou que muda o que a spec decidiu, abre phase nova com substituição explícita. O líder identifica a origem pelo assunto e pelos paths e a anuncia em uma linha; na dúvida entre duas phases, pergunte.

| Situação da phase de origem | Como o ajuste entra |
|---|---|
| Antes do implement | Insumo da spec ou do plan, gravado pelo redator; nenhum código antes do plan |
| Plan com passos e sem `review.md` | O redator acrescenta ao fim do checklist um passo com o próximo número, `Arquivos:` e `Prova:`, sem nova rodada do analyze; o passo segue os passos 1 e 2 |
| `review.md` aberto | O revisor registra o ajuste como R* na etapa vigente, com `papel:`; segue o passo 4 |
| Fechada | O líder acrescenta ao `review.md` uma etapa `### Ajuste N - <pedido>`, com o pedido e `Abriu: Rn`, e um R* Required por item. Low: o `# Status: aprovado` é mantido e não há re-review; o líder marca o `[x]` no commit `task(<alvo>:Rn,...)`, que inclui o `review.md`, os paths do R* e o registro apagado. Medium: o líder muda o status para `request-changes` e desmarca o Approve e a aprovação humana; o ajuste segue o passo 4, a re-review de ajuste e a confirmação de `references/review.md` |

R* de ajuste:

```text
- [ ] Rn: **Required** - `path` - <pedido do humano> - remédio: <o pedido> - prova: <testes afetados> - source: <pedido humano | path do registro de .erros-encontrados/> - papel: <implementador | redator>
```

Entrega medium ainda sem `review.md`: antes do commit `task(medium): ...`, o ajuste entra no recorte da entrega; depois dele, o revisor o registra como R* na review que abre a phase. Sem phase de origem, o ajuste segue a linha low da Entrada.

Registro de `.erros-encontrados/` corrigido é apagado no mesmo commit da correção; o Git guarda o histórico.

## Trabalho de quem implementa

1. **Reconhecer:** trace entrada, chamadas, consumidores e padrões compartilhados antes de editar, sem varredura cega. Edite só os `Arquivos:` do passo ou o recorte do brief.
2. **Codar:** reutilize o que existe no projeto, na standard library, na plataforma e nas dependências instaladas. Sem abstração especulativa nem limpeza fora do recorte. Documente semanticamente responsabilidades e decisões. Barra de acabamento em `references/definition-of-done.md`; banco ou dinheiro exige `references/database-and-migrations.md`.
3. **Testar e provar:** siga `references/testes.md` e rode a `Prova:` do passo.
4. **Visual:** quando um critério depende da interface renderizada, capture e cite a evidência conforme `references/chrome-devtools.md`.
5. **Entregar:** relatório fixo de `references/delegation.md`, com paths, comando e resultado da prova e pendências.

Credencial, conta, pagamento, elevação administrativa ou integração persistente são impedimentos reais: relate a tentativa, o impedimento e a recomendação.

### Política de testes

A política, o ambiente local, a pirâmide, o desenho do E2E e o orçamento de duração moram em `references/testes.md`.

## Saída

Caixas marcadas no `plan.md`, commits `task(...)` e o `review.md` do revisor. Não copie hashes, logs ou histórico de comandos para Markdown.

## Fechar

Responda com o resultado, a linha de progresso do `SKILL.md`, as provas, os commits e paths, as pendências e o próximo passo. Pergunta material vai ao humano com recomendação; trabalho independente segue enquanto ela está pendente. Na retomada, o disco indica o passo e código válido não é refeito.
