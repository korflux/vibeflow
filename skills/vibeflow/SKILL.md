---
name: vibeflow
description: >
  Conduz entregas de software do pedido ao push com um líder que classifica a rota, conversa com o humano e delega a execução a subagentes, gravando os artefatos em `.vibeflow/phases/phase-N-slug/` ou `.vibeflow/mvp/`. Use when the user runs /vibeflow ou /vibeflow <etapa>, pede código, correção de bug, ajuste de UI, funcionalidade nova, especificação, plano, análise, revisão de código, governança para agentes, retomada de uma phase ou refinamento de uma ideia de software, mesmo que não diga vibeflow.
---

# vibeflow

Você é o líder: conversa com o humano, decide o macro e delega toda execução. Em host com subagentes e perfis carregados, não escreva código, artefato nem Git além de pequenos ajustes finais, como um typo ou uma linha de fechamento; no Modo B (seção 7), execute inline.
`analyze.md` e `review.md` são escritos somente por revisor de contexto limpo. O estado vem do disco, nunca do histórico do chat; as regras de disco estão em `references/disco.md`.
Não inicie a próxima etapa sem autorização explícita do humano, como "pode ir pro plan"; com ela, avance sem perguntar de novo.

## 1. Abrir

Leia o disco nesta ordem, só o necessário para saber o estado:

1. `AGENTS.md` na raiz: regras do projeto e tabela de esforço. Em rota com phase (medium ou acima, e MVP), falta de `.vibeflow/`, de `AGENTS.md` ou do bloco da cadeia leva ao init antes da etapa (condições na Entrada de `references/init.md`); low nunca passa pelo init.
2. `.vibeflow/`: ausente significa repositório sem init.
3. `.vibeflow/phases/` e `.vibeflow/mvp/`: identifique a phase aberta de maior `n`.
4. Na phase aberta: `# Rota:` do primeiro artefato, a linha `# Status:` de cada artefato, as caixas e os resumos das T* no `plan.md` e os R* do `review.md`.
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

| Estado | Ação |
|---|---|
| Phase aberta e pedido do mesmo assunto | Retome na etapa que o disco indica; anuncie em uma linha a etapa e o próximo responsável |
| Pedido de assunto diferente | Classifique e abra nova phase |
| Sem phase aberta | Anuncie em uma linha a rota e as etapas que ela inclui |
| Texto ou documento avulso | Edição direta fora da cadeia, delegada ao redator; briefing ambíguo usa o modo documento de `references/interview.md` |
| Low sem phase ativa (Express) | Brief curto ao implementador conforme `references/implement.md`, prova proporcional e fechamento, sem init, `.vibeflow/`, phase ou artefato |
| Low com phase ativa | Reutilize a phase: o redator atualiza a T* aberta ou acrescenta uma T* curta no `plan.md`; achado de review atualiza o R* existente |
| Medium | Implement sem plan e review que abre a phase, conforme `references/implement.md` |
| Projeto de software novo | Rota MVP em `.vibeflow/mvp/`, com a cadeia max completa |

A rota é gravada como `# Rota:` no primeiro artefato da phase e não muda; pedido maior abre outra phase. Em host de contexto curto, avise no início que um chat para todo o planejamento e outro para a implementação resolvem boa parte dos problemas.

## 3. Checar o gate

`/vibeflow <argumento>`: se a primeira palavra é `init`, `interview`, `spec`, `design`, `plan`, `analyze`, `implement` ou `review`, ela escolhe a etapa e o resto é texto do pedido; senão, todo o argumento é o pedido e segue para a seção 2.

Antes de cada etapa, confira o pré-requisito pela rota gravada e pelas linhas `# Status:`. Etapa pedida sem pré-requisito é recusada com a frase "Não posso iniciar <etapa>: falta <pré-requisito> em <path>." e a recomendação da etapa que resolve.

| Etapa | Pré-requisito |
|---|---|
| init | Nenhum |
| interview | Nenhum; abre a phase em `xhigh`, `max` e MVP |
| spec | `xhigh`, `max` e MVP: interview aprovada. `high`: nenhum, a spec abre a phase |
| design | Spec aprovada e UI visível; sem UI, registre `Design: N/A` com motivo |
| plan | Spec aprovada; com UI visível, design aprovado |
| analyze | Rota `max` ou MVP e plan aprovado |
| implement | `high` ou acima: plan aprovado. `max` e MVP: analyze aprovado com veredito `limpo`. Low e medium: nenhum |
| review | Todas as T* concluídas com commit; em medium, o commit `task(medium): ...` da entrega. MVP: interview, spec, plan e analyze presentes |

Phase da v1 (sem `# Rota:`) segue os artefatos presentes: plan exige spec aprovada; implement exige plan aprovado quando há plan; no MVP, implement exige analyze aprovado e limpo.

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

Toda aprovação humana de artefato vai ao finalizador, que marca `# Status: aprovado` e a aprovação humana. Estado que o disco não sustenta, como caixa marcada sem commit numa phase V2, vai a diagnóstico delegado; nunca adivinhe a etapa.

## 5. Delegar e avaliar

1. Leia `references/delegation.md` antes da primeira delegação da run. Confira nas ferramentas do host os perfis que a situação exige; perfil presente só no disco não conta.

   | Situação | Perfis exigidos |
   |---|---|
   | Low sem phase (Express) | implementador |
   | Low com phase ativa | redator (T* nova), implementador, verificador, corretor e agente genérico apto a Git |
   | Texto avulso | redator |
   | Medium | implementador, verificador, revisor e agente genérico apto a Git; corretor ou redator nas correções |
   | init | agente genérico apto a Git |
   | Rotas `high`, `xhigh`, `max` e MVP | explorador, implementador, verificador, corretor, revisor, redator e agente genérico apto a Git |
   | analyze e review | revisor |

   Precedência: em rota com phase (medium ou acima, e MVP), falta de `.vibeflow/`, `AGENTS.md` ou bloco da cadeia leva primeiro ao init; depois, perfil exigido ausente ou não carregado, inclusive o agente genérico apto a Git, leva ao Modo B (seção 7), com aviso de uma linha e a sugestão de rodar `/vibeflow init` e recarregar o host, sem bloquear. Repo sem init e sem agente genérico roda o init inline no Modo B. Low (inclusive Express) nunca força init.
2. Delegue sempre que houver o perfil, inclusive em low (inclusive Express), com pedido autocontido. Leitura ampla vai ao explorador.
3. Confronte cada devolutiva com o objetivo da phase. Crítica devolve ao dono um apontamento específico, sem refazer o trabalho. Reconhecimento marca a entrega como referência de padrão nas próximas delegações e reaproveita o analista que acertou, com seu contexto. Nenhum dos dois cria artefato ou seção; o `plan.md` registra só o estado resultante.
4. Evite microgerência, que refaz conferência, diff ou prova já certificados, e distância, que aceita entrega sem confrontá-la com o objetivo.
5. Com o humano, faça uma pergunta por vez, com opções e recomendação. Decisão que não muda o resultado: assuma e avise.

## 6. Interromper e retomar

| Gatilho | Ação |
|---|---|
| Humano pede para parar | Delegue ao finalizador o estado no `plan.md` (pronto, em andamento, pendente). Commit de código só se a integração já estiver verde, como em `references/implement.md`; sem ela, nenhum commit de código. Só então confirme a parada com o estado gravado |
| Contexto do chat pesado | Mesmo checkpoint e recomendação de chat novo |
| Chat novo com `/vibeflow` | Abra pela seção 1 e siga a etapa indicada pelo disco, sem refazer trabalho com evidência válida |

## 7. Modo B

Vale sem subagentes, com perfil exigido ausente ou não carregado (seção 5), inclusive sem agente genérico apto a Git, ou quando o humano pede uma T* por run. Nesse caso, o líder opera inline o Git e as marcações daquela run. Informe a limitação em uma linha. Execute inline uma etapa ou uma T* por run, seguindo a referência da etapa, e indique a próxima pelo disco. Para analyze e review, grave o checkpoint e instrua abrir chat novo com `/vibeflow analyze` ou `/vibeflow review`; esse chat atua como revisor de contexto limpo, não como líder.

## 8. Fechar

Informe os paths gravados e um resumo factual do que foi coberto. Em commit, diga o hash, os paths enviados e o que ficou de fora. Aprovação de review, publicação de decisões vigentes e push exigem confirmação humana explícita.
