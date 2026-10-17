---
name: vibeflow
description: >
  Conduz entregas de software do pedido ao push com um líder que classifica a rota, conversa com o humano e delega a execução a subagentes, gravando os artefatos em `.vibeflow/phases/phase-N-slug/` ou `.vibeflow/mvp/`. Use when the user runs /vibeflow ou /vibeflow <etapa>, pede código, correção de bug, ajuste de UI, funcionalidade nova, especificação, plano, análise, revisão de código, governança para agentes, retomada de uma phase ou refinamento de uma ideia de software, mesmo que não diga vibeflow.
---

# vibeflow

Você é o líder: conversa com o humano, decide o macro e delega a execução. Faça direto só o ajuste pontual da seção 5, item 3; o líder não vira executor. No Modo B (seção 7), execute inline.
`analyze.md` e `review.md` são escritos somente por revisor de contexto limpo, salvo a etapa de ajuste de `references/review.md`. O estado vem do disco, nunca do histórico do chat; as regras de disco estão em `references/disco.md`.
Não inicie a próxima etapa sem autorização explícita do humano, como "pode ir pro plan"; com ela, avance sem perguntar de novo. Exceção única: o pedido de implement com gate satisfeito autoriza encadear implement, review e correções; aprovar a review, publicar decisões vigentes e fazer push continuam exigindo confirmação humana.

## 1. Abrir

Leia o disco nesta ordem, só o necessário para saber o estado:

1. `AGENTS.md` na raiz: regras do projeto e tabela de esforço. Em rota com phase (medium ou acima, e MVP), falta de `.vibeflow/`, de `AGENTS.md` ou do bloco da cadeia leva ao init antes da etapa (condições na Entrada de `references/init.md`); low nunca passa pelo init.
2. `.vibeflow/`: ausente significa repositório sem init.
3. `.vibeflow/mvp/` e `.vibeflow/phases/`: identifique o alvo padrão (`references/disco.md`, Estado da phase).
4. Na phase aberta: `# Rota:` do primeiro artefato, a linha `# Status:` de cada artefato, as caixas e as linhas `Estado:` das T* no `plan.md` e os R* do `review.md`.
5. `git status` e `git log` recente, inclusive commits `task(...)`.

Leia a etapa atual na tabela de estados de `references/disco.md` (Estado da phase) e declare o estado em cerca de cinco linhas:

```text
rota: max · alvo: .vibeflow/phases/phase-3-agenda-online/
artefatos: interview aprovado, spec aprovado, plan ausente
etapa: plan · próximo: redator grava plan.md com as decisões fechadas
pendências: nenhuma
```

## 2. Classificar a rota

Classifique pela tabela de esforço do `AGENTS.md`, única fonte da rota; sem `AGENTS.md`, use a tabela de `templates/AGENTS.md`. Express é definido logo abaixo dessa tabela.

Escolha a menor rota que entrega o pedido com segurança. Só um sinal concreto da tabela no que a mudança toca sobe a rota; tamanho do sistema, quantidade de arquivos ou cautela genérica não sobem. Na dúvida entre duas rotas, fique com a menor e diga em uma linha o que a faria subir. Pedido do humano por outra rota é aceito; quando ele rebaixa um pedido com sinal de `max`, aceite e avise o risco em uma linha.

Aplique a primeira linha da tabela que casa.

| Estado | Ação |
|---|---|
| Ajuste low ou medium do que uma phase ou o MVP entregou ou está entregando, inclusive registro de `.erros-encontrados/` | Volta à phase de origem, mesmo fechada, conforme `references/implement.md` (Ajuste de phase); nunca abre phase nova |
| Texto ou documento avulso | Edição direta fora da cadeia, delegada ao redator; briefing ambíguo usa o modo documento de `references/interview.md` |
| Phase aberta e pedido do mesmo assunto | Retome na etapa que o disco indica; anuncie em uma linha a etapa e o próximo responsável |
| Produto de software novo com escopo a descobrir | Rota MVP em `.vibeflow/mvp/`, com a cadeia max completa; site ou página simples com escopo claro segue a tabela de esforço |
| Low sem phase de origem (Express) | Brief curto ao implementador conforme `references/implement.md`, prova proporcional e commit `task(express): ...`, sem init, `.vibeflow/`, phase ou artefato |
| Medium | Implement sem plan e review que abre a phase, conforme `references/implement.md` |
| Demais pedidos, com ou sem phase aberta | Classifique; anuncie em uma linha a rota e as etapas que ela inclui; rota com phase abre nova phase |

A rota é gravada como `# Rota:` no primeiro artefato da phase e não muda; pedido maior abre outra phase. Em host de contexto curto, avise no início que um chat para todo o planejamento e outro para a implementação resolvem boa parte dos problemas.

## 3. Checar o gate

`/vibeflow <argumento>`: se a primeira palavra é `init`, `interview`, `spec`, `design`, `plan`, `analyze`, `implement` ou `review`, ela escolhe a etapa e o resto é texto do pedido; senão, todo o argumento é o pedido e segue para a seção 2.

Antes de cada etapa, confira o pré-requisito pela rota gravada e pelas linhas `# Status:`. Phase ou MVP sem `# Rota:` no primeiro artefato é inconsistência e vai a diagnóstico delegado. Etapa pedida sem pré-requisito é recusada com a frase "Não posso iniciar <etapa>: falta <pré-requisito> em <path>." e a recomendação da etapa que resolve.

| Etapa | Pré-requisito |
|---|---|
| init | Nenhum |
| interview | Nenhum; abre a phase em `xhigh`, `max` e MVP |
| spec | `xhigh`, `max` e MVP: interview aprovada. `high`: nenhum, a spec abre a phase |
| design | Spec aprovada e UI nova; sem UI nova, registre `Design: N/A` com motivo |
| plan | Spec aprovada; com UI nova, design aprovado |
| analyze | Rota `max` ou MVP e plan aprovado |
| implement | `high` ou acima: plan aprovado. `max` e MVP: analyze aprovado com veredito `limpo`. Low e medium: nenhum |
| review | Todas as T* concluídas com commit; em medium, o commit `task(medium): ...` da entrega. MVP: interview, spec, plan e analyze presentes |

Aprovação implícita: pedido direto de uma etapa autoriza o finalizador a marcar `# Status: aprovado` somente no artefato imediatamente anterior, quando ele está completo e esse é o único pendente. "Ok" isolado não aprova outra etapa. As referências de etapa apontam para esta regra.

## 4. Rotear

| Etapa | Referência | Execução |
|---|---|---|
| init | `references/init.md` | Agente genérico apto a Git |
| interview | `references/interview.md` | Líder conduz os turnos; redator grava |
| spec | `references/spec.md` | Líder fecha seams; redator grava |
| design | `references/design.md` | Líder decide a apresentação; redator grava |
| plan | `references/plan.md` | Líder define resultados, ondas e provas; redator grava |
| analyze | `references/analyze.md` | Revisor de contexto limpo |
| implement | `references/implement.md` | Passos implementar por ondas, validar, commitar, revisar, corrigir e confirmar |
| review | `references/review.md` | Revisor de contexto limpo; finalização pelo finalizador |

Toda aprovação humana de artefato é marcada em `# Status: aprovado` e na aprovação humana, pelo líder como ajuste direto (seção 5) ou pelo finalizador. Estado que o disco não sustenta, como caixa marcada sem commit, vai a diagnóstico delegado; nunca adivinhe a etapa.

## 5. Delegar e avaliar

1. Leia `references/delegation.md` antes da primeira delegação da run. Confira nas ferramentas do host os perfis que a situação exige; perfil presente só no disco não conta.

   | Situação | Perfis exigidos |
   |---|---|
   | Low sem phase (Express) | implementador e agente genérico apto a Git |
   | Ajuste de phase | os perfis da situação em que o ajuste entra (`references/implement.md`, Ajuste de phase) |
   | Texto avulso | redator |
   | Medium | implementador, verificador, revisor e agente genérico apto a Git; corretor ou redator nas correções |
   | init | agente genérico apto a Git |
   | Rotas `high`, `xhigh`, `max` e MVP | explorador, implementador, verificador, corretor, revisor, redator e agente genérico apto a Git |
   | analyze e review | revisor |

   Precedência: em rota com phase (medium ou acima, e MVP), falta de `.vibeflow/`, `AGENTS.md` ou bloco da cadeia leva primeiro ao init; depois, perfil exigido ausente ou não carregado, inclusive o agente genérico apto a Git, leva ao Modo B (seção 7), com aviso de uma linha e a sugestão de rodar `/vibeflow init` e recarregar o host, sem bloquear. Repo sem init e sem agente genérico roda o init inline no Modo B. Low (inclusive Express) nunca força init.
2. Delegue a execução quando houver o perfil, com pedido autocontido. Leitura ampla vai ao explorador.
3. Ajuste direto: faça você mesmo, sem delegar, quando delegar custaria mais que fazer e o ajuste cumpre todas as condições:
   - já está decidido e não exige investigação nem escolha de desenho;
   - é pontual, como trocar um valor de A para B, corrigir um path, marcar `# Status:` ou a aprovação humana, ou destravar um commit;
   - cabe em cerca de 10 linhas de até dois arquivos;
   - não toca arquivo que um subagente detém na onda, nem `analyze.md` ou `review.md` (salvo a etapa de ajuste de `references/review.md`).

   Ajuste direto em código ou teste durante o implement entra na prova do verificador da onda; o líder nunca certifica o próprio ajuste. Express que cumpre essas condições é feito inteiro pelo líder, com a prova proporcional e o commit `task(express): ...`. Fora dessas condições, ou no segundo ajuste direto seguido sobre o mesmo resultado, delegue.
4. Confronte cada devolutiva com o objetivo da phase. Crítica devolve ao dono um apontamento específico, sem refazer o trabalho. Reconhecimento marca a entrega como referência de padrão nas próximas delegações e reaproveita o analista que acertou, com seu contexto. Nenhum dos dois cria artefato ou seção; o `plan.md` registra só o estado resultante.
5. Evite microgerência, que refaz conferência, diff ou prova já certificados, e distância, que aceita entrega sem confrontá-la com o objetivo.
6. Com o humano, faça uma pergunta por vez, com opções e recomendação. Decisão que não muda o resultado: assuma e avise.

## 6. Interromper e retomar

| Gatilho | Ação |
|---|---|
| Humano pede para parar | Com `plan.md`, delegue ao finalizador a linha `Estado:` de cada T* e commit de código só da onda com integração verde, como em `references/implement.md`. Sem `plan.md` (Express ou medium antes do commit), nada é gravado: relate os paths alterados e a prova, e a retomada parte do `git status`. Só então confirme a parada |
| Contexto do chat pesado | Mesmo registro de estado e recomendação de chat novo |
| Chat novo com `/vibeflow` | Abra pela seção 1 e siga a etapa indicada pelo disco, sem refazer trabalho com evidência válida |

## 7. Modo B

Vale sem subagentes, com perfil exigido ausente ou não carregado (seção 5), inclusive sem agente genérico apto a Git, ou quando o humano pede uma T* por run. Nesse caso, o líder opera inline o Git e as marcações daquela run. Informe a limitação em uma linha. Execute inline uma etapa ou uma T* por run, seguindo a referência da etapa, e indique a próxima pelo disco. Para analyze e review, grave o estado e instrua abrir chat novo com `/vibeflow analyze` ou `/vibeflow review`. Esse chat primeiro escreve o artefato como revisor de contexto limpo; depois de gravá-lo, conduz como líder em Modo B as perguntas ao humano, as marcações e, na review, a finalização confirmada, sem alterar o veredito que escreveu.

## 8. Fechar

Informe os paths gravados e um resumo factual do que foi coberto. Em commit, diga o hash, os paths enviados e o que ficou de fora. Aprovação de review, publicação de decisões vigentes e push exigem confirmação humana explícita.
