# Etapa implement

Um passo só é concluído com prova verde e commit real. Formatos de passo, checkpoint, commit e estado, e a regra de staging, moram em `references/disco.md`.

## Entrada

- Gate: em `high` e `mvp`, spec aprovada e `plan.md` com `## Achados do analyze`. Low e medium não têm plan.
- Leia o `plan.md` (caixas, `Arquivos:`, `Prova:`, checkpoints), o `review.md` quando existir, `git status` e o `git log` com os commits do alvo.

| Situação | Como conduzir |
|---|---|
| Low sem phase de origem | Brief curto ao implementador, prova proporcional por `references/testes.md`; o líder confere o relatório e commita (`references/disco.md`, Commits), sem phase nem artefato |
| Medium | Rota medium |
| `high` ou `mvp` com os perfis carregados | Passos 1 a 4 |

Ajuste de phase segue `references/ajuste.md`, e o Modo B, `references/retomada.md`.

Quem faz: o implementador coda, prova e commita cada passo (o redator, na prosa, com o commit pelo líder), o verificador confere o checkpoint, o revisor faz a review, e o líder delega, confere, marca checkpoint e R* e faz os demais commits.

## Passos

### 1. Executar o trecho

1. O trecho são os passos abertos do primeiro com caixa aberta até o próximo checkpoint ou o fim (`references/disco.md`, Glossário). Um implementador recebe o trecho inteiro num despacho, com o brief de cada passo (`references/delegation.md`, Pedido autocontido), e faz os passos em ordem, na mesma thread: o contexto do código lido num passo serve aos seguintes.
2. Grupo paralelo (`2a`, `2b`) dentro do trecho: o implementador do trecho o faz em sequência, por padrão. Só quando os passos irmãos são grandes e independentes o líder os despacha em chamadas paralelas, um implementador por passo, cada um com ownership exclusivo dos `Arquivos:` do seu passo, e o trecho continua depois de todos verdes.
3. Em cada passo, o implementador coda, escreve os testes, roda a `Prova:` e commita o passo com a caixa marcada (`references/implementador.md`, Commit do passo). Prova vermelha é corrigida por ele mesmo, até verde ou impedimento real. Impedimento, pergunta ou path fora do recorte param o trecho: os passos já commitados ficam, e o relatório diz onde parou.
4. Passo de prosa no trecho vai ao redator, que não commita: o líder commita o passo dele e devolve o trecho ao implementador.
5. Ao fim do trecho, o líder lê o relatório e confere cada commit do trecho contra os `Arquivos:` do passo do ID (`references/delegation.md`, Conferência do líder). Divergência volta ao implementador, que a corrige num commit do mesmo passo.

### 2. Checkpoint

Com todos os passos anteriores a uma linha `Checkpoint:` marcados, o líder despacha um verificador de contexto limpo com brief que traz só o diff do grupo e os critérios listados; ele segue `references/verificador.md`. Falha volta ao dono do passo que a causou (implementador, ou redator no passo de prosa), e a correção entra num commit novo do mesmo passo, no formato de passo, feito pelo implementador ou, na prosa, pelo líder; o checkpoint roda de novo sobre a correção. Verde em todos os critérios listados, com evidência, o líder marca a caixa conforme `references/disco.md` (Plan > Checkpoint); flake e achado fora do recorte seguem o Glossário dele. Phase sem checkpoint segue direto para a review.

O líder não move critério entre checkpoints nem marca checkpoint com evidência pendente. Critério mal atribuído no plan, listado num checkpoint anterior ao passo que o entrega, é corrigido no `plan.md` pelo redator, a pedido do líder, antes de o checkpoint rodar de novo.

### 3. Revisar

Com todos os passos e checkpoints marcados, o revisor de contexto limpo executa `references/review.md` no alvo.

### 4. Corrigir achados

Roteie cada R* aberto pelo `papel:`: `implementador` para código e testes, `redator` para prosa; remédio em `review.md` volta ao revisor. Quem corrige roda os testes afetados da correção e devolve o relatório. O líder confere, marca `[x]` nos R* comprovados e commita a correção (`references/disco.md`, Commits). A re-review, o limite de rodadas e a confirmação final seguem `references/review.md`.

## Rota medium

1. O líder escreve no brief os critérios de aceite `A1`, `A2` em diante, na forma de `references/spec.md` (Critérios de aceite). O implementador entrega a mudança com a prova por `references/testes.md`, e o líder confere o relatório.
2. Prova verde, o líder commita `task(medium): <resultado>` com os critérios do brief no corpo (`references/disco.md`, Commits).
3. A review abre a phase e julga o diff contra os critérios do corpo do commit (`references/review.md`, Entrada).
4. Achados seguem o passo 4.

## Saída

Caixas marcadas no `plan.md`, commits `task(...)` e o `review.md` do revisor, sem hashes, logs ou histórico de comandos em Markdown.

## Fechar

Responda com o resultado, a linha de progresso do `SKILL.md`, as provas, os commits e paths, as pendências e o próximo passo. Pergunta material vai ao humano com recomendação; trabalho independente segue enquanto ela está pendente. Na retomada, o disco indica o passo e código válido não é refeito.
