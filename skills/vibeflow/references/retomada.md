# Interromper, retomar e Modo B

Leia quando o humano pede para parar, quando o contexto do chat pesa, num chat novo com `/vibeflow` ou quando o Modo B vale (`SKILL.md`, seções 6 e 7).

## Interromper e retomar

| Gatilho | Ação |
|---|---|
| Humano pede para parar | Commite só passo com prova verde e conferido; passo em andamento fica sem commit e é retomado pelo disco. Sem `plan.md` (low, ou medium antes do commit), relate os paths alterados e a prova; a retomada parte do `git status`. Só então confirme a parada |
| Contexto do chat pesado | Mesmo registro e recomendação de chat novo |
| Chat novo com `/vibeflow` | Abra pela seção 1 do `SKILL.md` e siga a etapa indicada pelo disco, sem refazer trabalho com evidência válida |

## Modo B

Vale sem subagentes, com perfil exigido ausente ou não carregado (`SKILL.md`, seção 5), ou quando o humano pede um passo por run. Informe a limitação em uma linha. O líder executa inline uma etapa ou um passo por run, com o Git e as marcações, seguindo a referência da etapa, e indica a próxima pelo disco.

No implement, cada run executa um passo, o primeiro aberto ou o que o humano nomeou: o chat assume o papel do implementador conforme `references/implementador.md`, roda a `Prova:`, marca a caixa e commita (`references/disco.md`, Commits). O passo inline não tem conferência própria: vale a `Prova:` do passo, e o checkpoint e a review em contexto limpo certificam. Grupo paralelo roda em sequência. Correção de R* segue o passo 4 de `references/implement.md` inline, uma rodada por run; medium segue a Rota medium de `references/implement.md` inline.

### Contexto limpo

Analyze, checkpoint e review exigem contexto limpo.

| Chat atual | Ação |
|---|---|
| Já conduziu qualquer etapa da phase, inclusive analyze ou review | Não é contexto limpo: grave o estado e instrua abrir chat novo com `/vibeflow analyze`, `/vibeflow implement` ou `/vibeflow review`; o checkpoint chega por `/vibeflow implement`, que pela tabela de estados cai nele |
| Aberto com `/vibeflow analyze`, `/vibeflow implement` (checkpoint) ou `/vibeflow review`, sem trabalho anterior da phase | É o contexto limpo: atue primeiro como revisor no analyze e na review, conforme `references/revisor.md`, ou como verificador no checkpoint, conforme `references/verificador.md`, e grave o resultado; depois conduza como líder em Modo B as perguntas ao humano, as marcações e, na review, a finalização confirmada, sem alterar o veredito que escreveu |
