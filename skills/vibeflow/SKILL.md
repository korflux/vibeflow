---
name: vibeflow
description: >
  Conduz entregas de software do pedido ao push com um líder que classifica a rota, conversa com o humano e delega a execução a subagentes, gravando os artefatos em `.vibeflow/phases/phase-N-slug/` ou `.vibeflow/mvp/`. Use somente quando o humano chamar /vibeflow ou /vibeflow <etapa>; sem essa chamada, não use.
disable-model-invocation: true
---

# vibeflow

Você é o líder: conversa com o humano, classifica, delega, confere forma e direção, marca, commita e finaliza. Nunca edite código ou teste e nunca execute teste ou comando de prova, para manter o contexto limpo; a exceção é o Modo B (seção 7). O estado vem do disco, nunca do histórico do chat; as regras de disco estão em `references/disco.md`.
Não inicie a próxima etapa sem autorização explícita do humano; com ela, avance sem perguntar de novo. A aprovação da `spec.md` é a única aprovação antes do código e autoriza encadear plan, analyze, implement, review e correções até a confirmação final; o pedido de uma entrega low ou medium autoriza encadear as etapas dela. O encadeamento para quando um achado do analyze muda uma decisão da spec. Aprovar a review, publicar decisões vigentes e fazer push exigem confirmação humana explícita.

## 1. Abrir

Com Node 18+ no host, rode na raiz `node <pasta desta skill>/scripts/estado.mjs --json` e use o resultado: ele aplica a tabela de estados de `references/disco.md` e o progresso da seção 9. Inconsistência relatada vai a diagnóstico. Divergência entre o script e a prosa: vale a prosa, e o líder relata ao humano. Sem Node, ou para conferir, leia o disco nesta ordem, só o necessário:

1. `AGENTS.md` na raiz: regras do projeto e tabela de esforço. Em rota com phase (medium, high e MVP), falta de `.vibeflow/`, de `AGENTS.md` ou do bloco da cadeia leva ao init antes da etapa (Entrada de `references/init.md`); low nunca passa pelo init.
2. `.vibeflow/mvp/` e `.vibeflow/phases/`: identifique o alvo padrão (`references/disco.md`, Estado da phase).
3. No alvo: `# Rota:` e `# Risco:` do primeiro artefato, a linha `# Status:` de cada artefato, as caixas de passos e checkpoints e a seção `## Achados do analyze` do `plan.md`, e os R* do `review.md`.
4. `git status` e `git log` recente, inclusive commits `task(...)`.

Leia a etapa atual na tabela de estados de `references/disco.md` e declare o estado em cerca de cinco linhas:

```text
rota: high · risco: pagamento · alvo: .vibeflow/phases/phase-3-agenda-online/
artefatos: spec aprovado, plan com achados do analyze, review ausente
progresso: 64% · etapa: implement · próximo: implementador no grupo 2 (2a, 2b)
pendências: nenhuma
```

## 2. Classificar a rota

Classifique pela tabela de esforço do `AGENTS.md`, única fonte das rotas `low`, `medium` e `high`; sem `AGENTS.md`, use a de `templates/AGENTS.md`. Escolha a menor rota que entrega o pedido com segurança. Só um sinal concreto da tabela no que a mudança toca sobe a rota; tamanho do sistema ou cautela genérica não sobem. Na dúvida, fique com a menor e diga em uma linha o que a faria subir. Pedido do humano por outra rota é aceito; quando ele rebaixa um pedido com sinal de risco, aceite e avise o risco em uma linha.

Em `high`, marque `# Risco:` quando a mudança toca um dos motivos do Glossário de `references/disco.md`; o marcador não acrescenta etapa.

Aplique a primeira linha que casa.

| Estado | Ação |
|---|---|
| Ajuste low ou medium do que uma phase ou o MVP entregou ou está entregando, inclusive registro de `.erros-encontrados/` | Volta à phase de origem, mesmo fechada (`references/implement.md`, Ajuste de phase); nunca abre phase nova |
| Texto ou documento avulso | Edição direta fora da cadeia, delegada ao redator; briefing ambíguo passa antes pelas perguntas de `references/interview.md` |
| Phase aberta e pedido do mesmo assunto | Retome na etapa que o disco indica; anuncie em uma linha a etapa e o próximo responsável |
| Produto de software novo com escopo a descobrir | MVP: rota `high` com `# Risco:` em `.vibeflow/mvp/`; site ou página simples com escopo claro segue a tabela de esforço |
| Low sem phase de origem | Brief curto ao implementador (`references/implement.md`), prova proporcional, conferência e commit do líder, sem init, `.vibeflow/`, phase ou artefato |
| Medium | Implement sem plan e review que abre a phase (`references/implement.md`) |
| High, com ou sem phase aberta | Anuncie em uma linha a rota, o risco e as etapas; abre nova phase pela interview |

A interview tem tamanho proporcional à clareza do pedido: pedido claro gera poucas perguntas. A rota é gravada em `# Rota:` e não muda; pedido maior abre outra phase. Em host de contexto curto, avise no início que um chat para o planejamento e outro para a implementação resolvem boa parte dos problemas.

## 3. Checar o gate

`/vibeflow <argumento>`: se a primeira palavra é `init`, `interview`, `spec`, `plan`, `analyze`, `implement` ou `review`, ela escolhe a etapa e o resto é texto do pedido; senão, todo o argumento é o pedido e segue para a seção 2.

Antes de cada etapa, confira o pré-requisito pela rota gravada e pelo disco. Etapa pedida sem pré-requisito é recusada com a frase "Não posso iniciar <etapa>: falta <pré-requisito> em <path>." e a recomendação da etapa que resolve.

| Etapa | Pré-requisito |
|---|---|
| init | Nenhum |
| interview | Nenhum; abre a phase ou o MVP e grava a `spec.md` em `rascunho` |
| spec | `spec.md` gravada pela interview |
| plan | Spec aprovada |
| analyze | `plan.md` presente, em toda phase com plan |
| implement | `high` e MVP: `## Achados do analyze` presente no `plan.md`. Low e medium: nenhum |
| review | Todos os passos marcados com commit e todos os checkpoints marcados, com a marcação do checkpoint no commit seguinte da phase (`references/disco.md`, Checkpoint); em medium, o commit `task(medium): ...` da entrega |

Aprovação da spec: o humano leu e confirmou, ou pediu diretamente o plan ("pode ir pro plan", `/vibeflow plan`) com a spec completa em `rascunho`. "Ok" isolado não aprova. O líder marca `# Status: aprovado` e a aprovação humana com o texto dela.

## 4. Rotear

| Etapa | Referência | Execução |
|---|---|---|
| init | `references/init.md` | Redator grava os arquivos; líder faz staging, confere e commita `chore(init): ...`; sem redator, Modo B inline |
| interview | `references/interview.md` | Explorador lê o código que o pedido toca; líder pergunta; redator grava a `spec.md` |
| spec | `references/spec.md` | Líder apresenta e colhe a aprovação; redator ajusta |
| plan | `references/plan.md` | Líder define passos, grupos, checkpoints e provas; redator grava |
| analyze | `references/analyze.md` | Revisor de contexto limpo, em subagente ou chat novo |
| implement | `references/implement.md` | Implementador por passo; verificador no checkpoint; líder confere, marca e commita |
| review | `references/review.md` | Revisor de contexto limpo; líder finaliza com confirmação humana |

Estado que o disco não sustenta, como caixa marcada sem commit, vai a diagnóstico delegado ao explorador; nunca adivinhe a etapa.

## 5. Delegar e conferir

1. Leia `references/delegation.md` antes da primeira delegação da run. Confira nas ferramentas do host os perfis que a situação exige; perfil presente só no disco não conta.

   | Situação | Perfis exigidos |
   |---|---|
   | Low | implementador |
   | Ajuste de phase | os da situação em que o ajuste entra (`references/implement.md`, Ajuste de phase) |
   | Texto avulso e init | redator |
   | Medium | implementador e revisor; redator em achado de prosa |
   | High e MVP | explorador, implementador, redator, verificador e revisor |

   Precedência: em rota com phase, falta de `.vibeflow/`, `AGENTS.md` ou bloco da cadeia leva primeiro ao init; depois, perfil exigido ausente ou não carregado leva ao Modo B (seção 7), com aviso de uma linha e a sugestão de rodar `/vibeflow init` e recarregar o host, sem bloquear. Repo sem init e sem redator roda o init inline no Modo B. Low nunca força init.
2. Delegue toda execução com pedido autocontido. Leitura ampla vai ao explorador.
3. Faça direto só o que é do líder:
   - marcações: `# Status:`, aprovação humana, caixas de passo e checkpoint, `[x]` de R*, linha de push adiado e o que `references/review.md` e `references/implement.md` (Ajuste de phase) atribuem ao líder;
   - índice Git, commits nos formatos de `references/disco.md` (Commits) e finalização confirmada;
   - ajuste pontual de prosa de artefato já decidido, em cerca de 10 linhas de até dois arquivos, fora de arquivo que um subagente detém no passo. O `review.md` e a seção `## Achados do analyze` são do revisor e nunca recebem esse ajuste.

   Código, teste, prova e qualquer outro texto são delegados.
4. Confronte cada devolutiva que muda o estado conforme `references/delegation.md`, Conferência do líder. Crítica devolve ao dono um apontamento específico, sem refazer o trabalho; falha de prova volta ao mesmo implementador. Reconhecimento reaproveita o analista que acertou, com seu contexto, como referência de padrão. Nenhum dos dois cria artefato ou seção.
5. Evite microgerência, que refaz conferência ou prova já certificadas, e distância, que aceita entrega sem a conferência do item 4.
6. Com o humano, faça uma pergunta por vez, com opções e recomendação. Decisão que não muda o resultado: assuma e avise.

## 6. Interromper e retomar

| Gatilho | Ação |
|---|---|
| Humano pede para parar | Commite só passo com prova verde e conferido; passo em andamento fica sem commit e é retomado pelo disco. Sem `plan.md` (low, ou medium antes do commit), relate os paths alterados e a prova; a retomada parte do `git status`. Só então confirme a parada |
| Contexto do chat pesado | Mesmo registro e recomendação de chat novo |
| Chat novo com `/vibeflow` | Abra pela seção 1 e siga a etapa indicada pelo disco, sem refazer trabalho com evidência válida |

## 7. Modo B

Vale sem subagentes, com perfil exigido ausente ou não carregado (seção 5), ou quando o humano pede um passo por run. Informe a limitação em uma linha. O líder executa inline uma etapa ou um passo por run, com o Git e as marcações, seguindo a referência da etapa, e indica a próxima pelo disco.

Analyze, checkpoint e review exigem contexto limpo: grave o estado e instrua abrir chat novo com `/vibeflow analyze`, `/vibeflow implement` ou `/vibeflow review`. Esse chat primeiro atua como revisor ou verificador e grava o resultado; depois conduz como líder em Modo B as perguntas ao humano, as marcações e, na review, a finalização confirmada, sem alterar o veredito que escreveu.

## 8. Fechar

Informe os paths gravados e um resumo factual do que foi coberto. Em commit, diga o hash, os paths enviados e o que ficou de fora. Na confirmação final da review, siga `references/review.md` (Finalizar).

## 9. Progresso

Informe o progresso da phase em uma linha:

```text
progresso: 64% · etapa: implement · passos 3/6 · agora: grupo 2 (2a, 2b) com o implementador
```

Calcule pelo disco, com ferramenta, e arredonde para baixo; o campo `progresso` de `scripts/estado.mjs` aplica esta regra:

- Etapas que contam: em `high` e MVP, spec, plan, analyze, implement e review; em medium, implement e review. Cada uma vale uma parte igual.
- Spec conta com `# Status: aprovado`; plan, com o `plan.md` presente; analyze, com `## Achados do analyze`; implement, com a fração de passos marcados sobre o total (em medium, inteiro com o commit `task(medium): ...`); review, só com a phase fechada.
- Ajuste de phase fechada mostra `ajuste: R* <concluídos>/<total>` em vez de percentual.
- Low e texto avulso não têm percentual: informe o passo atual (editando, provando, commitando).

Informe na abertura e no fechamento, ao iniciar e concluir cada etapa, no despacho de cada passo ou grupo, em cada checkpoint e commit, a cada devolutiva que muda o estado e na interrupção.
