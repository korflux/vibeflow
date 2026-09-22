# vibe-plan, análise

## Problema

Os modelos históricos descreviam plan técnico, tasks e checklists como arquivos separados. No Vibeflow, a fila, o corpo das tasks, a prova e o handoff precisam permanecer em um único `plan.md`, e o arquivo precisa continuar sendo a fonte depois que a IA fecha a etapa.

## Decisão de desenho

```text
spec.md aprovado
  → inventário do mesmo alvo
  → preparo curto das ferramentas exigidas pelas provas
  → fatiamento por resultados e dependências reais
  → apply prepara plan.md
  → IA escreve tasks diretamente, cada uma com sua prova
  → humano aprova o arquivo
  → handoff vibe-implement ou vibe-analyze
```

`--apply` não transporta a prosa do plan. Ele garante o path e evita sobrescrever um arquivo vivo. Isso deixa o parser mecânico restrito a `### T*`, à linha de conclusão e a `Deps`, enquanto a IA continua dona do significado de aceite, ordem e prova.

## Investigação e ferramentas

A investigação começa pela pergunta de fatiamento e pela dependência que precisa ser provada. A IA usa `rg --files` para localizar spec, regras, entradas e testes, e `rg -n` para localizar A*/C*, decisões, símbolos e comandos. Só abre as entradas e dependências do fluxo. A disponibilidade de `gitleaks` e de capacidade visual é registrada antes de fechar as verificações.

Para UI, a ordem é navegador integrado, MCP Server `chrome-devtools`, Playwright existente ou explicitamente solicitado. Uma tarefa sem UI não recebe um gate de browser.

## Resultados, dependências e fila

Cada T* reúne um resultado coeso verificável. Uma nova T* só aparece para um resultado separado, uma dependência real de execução, isolamento de risco ou impossibilidade de verificar a fatia como unidade. Número de arquivos, sessões, critérios de aceite, uma pontuação ou a conjunção no título não acionam quebras automáticas. Arquivos e risco são registrados quando ajudam a executar, isolar ou revisar.

O preparo local lista as ferramentas necessárias para as provas e resolve ausências simples quando disponível e autorizado. Uma ferramenta ausente só vira T* quando o setup persistente faz parte da entrega do projeto; bloqueios externos ficam registrados. `Deps` contém apenas dependências de execução e define a fila. Paralelização e checkpoints são omitidos quando não alteram execução ou review. Se uma T* criar ou alterar um ponto de entrada executável, o smoke test fica na prova dessa mesma T*.

## Chat e continuidade

Plan é uma porta de maior risco cognitivo e recomenda novo chat no handoff. O humano pode continuar conscientemente no mesmo chat. O `plan.md` vivo, o status e a linha de handoff são a ponte; o histórico da conversa não é prova.

## Cortes

| Corte | Motivo |
|---|---|
| `todo.md` ou `tasks.md` | Uma casa por fato: índice e corpo ficam no plan. |
| Escrita do plan pelo script | Mantém o motor mecânico e a prosa sob responsabilidade da IA. |
| Verificação somente manual | A implement precisa de comando executável. |
| Instalação automática de navegador | Não adiciona dependência apenas para preencher um gate. |
| Task para preparar ferramenta local simples | O preparo é checklist; só setup persistente do projeto vira T*. |
| Quebra por score, sessão, tamanho da lista ou título | A unidade vem do resultado e das dependências reais. |
| Disparo automático de implement | Handoff é explícito e fica no arquivo. |

## Impacto

O implement consegue projetar a fila de T* a partir do vivo, sem depender de uma pasta auxiliar. O contrato de distribuição, os templates e os motores ficam alinhados: um arquivo por etapa, uma entrada viva e uma prova executável.
