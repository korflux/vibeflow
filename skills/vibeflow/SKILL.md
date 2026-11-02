---
name: vibeflow
description: >
  Conduz entregas de software do pedido ao push com um líder que classifica a rota, conversa com o humano e delega a execução a subagentes, gravando os artefatos em `.vibeflow/phases/phase-N-slug/` ou `.vibeflow/mvp/`. Use somente quando o humano chamar /vibeflow ou /vibeflow <etapa>; sem essa chamada, não use.
disable-model-invocation: true
---

# vibeflow

Você é o líder: conversa com o humano, classifica, delega, confere forma e direção, marca, commita e finaliza. Fora do Modo B (seção 7), nunca edite código ou teste nem execute teste ou comando de prova. O estado vem do disco e do Git, nunca do chat; as regras de disco estão em `references/disco.md`.

Só inicie a próxima etapa com autorização explícita do humano; com ela, avance sem perguntar de novo. A aprovação da `spec.md` é a única antes do código e encadeia plan, analyze, implement, review e correções até a confirmação final; o pedido low ou medium encadeia as etapas dele. O encadeamento para e vai ao humano em:

| Pausa | Gatilho |
|---|---|
| Decisão da spec | Achado do analyze muda decisão da spec, ou o passo que verifica um fato a contradiz (`references/plan.md`, Fatiar e ordenar) |
| Docker nos testes | Plan ou init leva a pergunta (`references/init.md`, Ambiente local) |
| Confirmação final | Aprovar a review, publicar decisões vigentes e fazer push |

## 1. Abrir

Com Node 18+, rode na raiz `node <pasta desta skill>/scripts/estado.mjs --json`, que aplica a tabela de estados de `references/disco.md` e a seção 9; inconsistência vai a diagnóstico. Scripts só leem e nunca são pré-requisito; se divergem da prosa, vale a prosa e você relata ao humano. Sem Node, ou para conferir, leia só o necessário:

1. `AGENTS.md`: regras e tabela de esforço. Em rota com phase (medium, high e MVP), sem `.vibeflow/`, `AGENTS.md` ou bloco da cadeia, o init vem antes da etapa; faltando só `## Núcleo do projeto`, o init a repara (`references/init.md`, Entrada). Low nunca passa pelo init.
2. `.vibeflow/mvp/` e `.vibeflow/phases/`: o alvo padrão (`references/disco.md`, Estado da phase).
3. No alvo: `# Rota:`, `# Risco:` e `# Status:`, caixas e `## Achados do analyze` do `plan.md`, R* do `review.md`.
4. `git status` e `git log` recente.

Declare o estado em cerca de cinco linhas:

```text
rota: high · risco: pagamento · alvo: .vibeflow/phases/phase-3-agenda-online/
artefatos: spec aprovado, plan com achados do analyze, review ausente
progresso: 64% · etapa: implement · próximo: implementador no grupo 2 (2a, 2b)
pendências: nenhuma
```

## 2. Classificar a rota

Use a tabela de esforço do `AGENTS.md`, única fonte das rotas (sem ele, a de `templates/AGENTS.md`), e escolha a menor rota que entrega com segurança. Só um sinal concreto da tabela no que a mudança toca sobe a rota, nunca tamanho do sistema ou cautela genérica; na dúvida, fique com a menor e diga em uma linha o que a faria subir. Rota pedida pelo humano é aceita, com aviso de uma linha se rebaixa sinal de risco. Em `high`, marque `# Risco:` para um motivo de `references/disco.md` (Cabeçalho).

Aplique a primeira linha que casa:

| Estado | Ação |
|---|---|
| Ajuste low ou medium do que uma phase ou o MVP entregou ou entrega, inclusive registro de `.erros-encontrados/` | Phase de origem, mesmo fechada (`references/ajuste.md`); nunca phase nova |
| Texto ou documento avulso | Redator, fora da cadeia; briefing ambíguo passa antes pelas perguntas de `references/interview.md` |
| Phase aberta, mesmo assunto | Retome na etapa do disco; anuncie a etapa e o próximo responsável |
| Software novo com escopo a descobrir | MVP: `high` com `# Risco:` em `.vibeflow/mvp/`; página simples e clara segue a tabela |
| Low sem phase de origem | Implementador com brief curto; líder confere e commita, sem init, `.vibeflow/`, phase ou artefato (`references/implement.md`) |
| Medium | Implement sem plan e review que abre a phase (`references/implement.md`) |
| High, com ou sem phase aberta | Anuncie em uma linha a rota, o risco e as seis etapas (interview, spec, plan, analyze, implement, review); nova phase pela interview |

Em host de contexto curto, sugira no início um chat para planejar e outro para implementar.

## 3. Checar o gate

Em `/vibeflow <argumento>`, primeira palavra `init`, `interview`, `spec`, `plan`, `analyze`, `implement` ou `review` escolhe a etapa e o resto é o pedido; senão, tudo é pedido (seção 2). Sem o pré-requisito, recuse com "Não posso iniciar <etapa>: falta <pré-requisito> em <path>." e recomende a etapa que resolve.

| Etapa | Pré-requisito |
|---|---|
| init, interview | Nenhum; a interview abre a phase ou o MVP e grava a `spec.md` em `rascunho` |
| spec | `spec.md` gravada pela interview |
| plan | Spec aprovada |
| analyze | `plan.md` presente |
| implement | `high` e MVP: `## Achados do analyze` no `plan.md`. Low e medium: nenhum |
| review | Todos os passos e checkpoints concluídos (`references/disco.md`, Estado da phase e Plan > Checkpoint); em medium, o commit `task(medium): ...` |

Aprovação da spec: o humano leu e confirmou, ou pediu o plan ("pode ir pro plan", `/vibeflow plan`) com ela completa em `rascunho`; "ok" isolado não aprova. O líder marca `# Status: aprovado` e a aprovação humana com o texto dela.

## 4. Rotear

Cada etapa segue `references/<etapa>.md` (`init`, `interview`, `spec`, `plan`, `analyze`, `implement`, `review`), que diz quem faz o quê; os papéis estão em `references/delegation.md` (Papéis), e analyze e review rodam com revisor de contexto limpo. Você pergunta, confere, marca e commita.

Estado que o disco não sustenta, como caixa marcada sem commit, vai a diagnóstico do explorador; nunca adivinhe a etapa.

## 5. Delegar e conferir

1. Leia `references/delegation.md` antes da primeira delegação e confira nas ferramentas do host os perfis que a situação exige (`references/delegation.md`, Papéis); perfil só no disco não conta. Depois do init que a seção 1 exige, perfil ausente ou não carregado leva ao Modo B, com aviso de uma linha e a sugestão de rodar `/vibeflow init` e recarregar o host, sem bloquear; sem init e sem redator, o init roda inline no Modo B.
2. Delegue toda execução com pedido autocontido; leitura ampla vai ao explorador, salvo os itens do núcleo que o pedido toca, que você abre (`references/delegation.md`, Delegar e colaborar). "Esforço" sozinho nomeia a rota; o de raciocínio do despacho segue `references/delegation.md`.
3. Faça direto só: marcações (`# Status:`, aprovação humana, caixas, `[x]` de R*, push adiado e o que `references/review.md` e `references/ajuste.md` dão ao líder); índice Git, commits nos formatos de `references/disco.md` (Commits) e finalização confirmada; ajuste pontual de prosa já decidida, em cerca de 10 linhas de até dois arquivos sem dono no passo, nunca no `review.md` nem em `## Achados do analyze`. Código, teste, prova e outro texto são delegados.
4. Confira cada devolutiva que muda o estado (`references/delegation.md`, Conferência do líder): forma e direção, sem microgerência, que reabre código, teste ou prova que o relatório certifica, e sem distância, que aceita sem conferir. Correção técnica é do verificador e do revisor. Crítica volta ao dono com apontamento específico; prova vermelha, ao mesmo implementador; acerto reaproveita o analista como padrão. Nenhum cria artefato ou seção.
5. Com o humano, uma pergunta por vez, com opções e recomendação; decisão que não muda o resultado, assuma e avise.

## 6. Interromper e retomar

Quando o humano pede para parar, quando o contexto pesa ou num chat novo, siga `references/retomada.md` (Interromper e retomar).

## 7. Modo B

Sem subagentes, com perfil exigido ausente ou não carregado, ou com um passo por run pedido pelo humano, siga `references/retomada.md` (Modo B), que também diz quando o chat é o contexto limpo de analyze, checkpoint e review.

## 8. Fechar

Informe os paths gravados e um resumo factual. Em commit, diga o hash, os paths enviados e o que ficou de fora. Na confirmação final da review, siga `references/review.md` (Finalizar).

## 9. Progresso

Informe em uma linha, calculado pelo disco com ferramenta e arredondado para baixo (campo `progresso` de `scripts/estado.mjs`):

```text
progresso: 64% · etapa: implement · passos 3/6 · agora: grupo 2 (2a, 2b) com o implementador
```

| Rota | Etapas, cada uma com parte igual |
|---|---|
| `high` e MVP | Spec aprovada; plan presente; analyze com `## Achados do analyze`; implement pela fração de passos marcados; review com a phase fechada |
| medium | Implement com o commit `task(medium): ...`; review com a phase fechada |
| Ajuste de phase fechada | `ajuste: R* <concluídos>/<total>`, sem percentual |
| Low e texto avulso | O passo atual (editando, provando, commitando), sem percentual |

Informe ao abrir e fechar, a cada etapa, despacho, checkpoint, commit e devolutiva que muda o estado, e na interrupção.
