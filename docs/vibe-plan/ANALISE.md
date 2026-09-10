# vibe-plan, análise

## Problema

Os modelos históricos descreviam plan técnico, tasks e checklists como arquivos separados. No Vibeflow, a fila, o corpo das tasks, a prova e o handoff precisam permanecer em um único `plan.md`, e o arquivo precisa continuar sendo a fonte depois que a IA fecha a etapa.

## Decisão de desenho

```text
spec.md aprovado
  → inventário do mesmo alvo
  → validação de ferramentas e seams
  → fatiamento vertical com Size/Risk
  → apply prepara plan.md
  → IA escreve tasks diretamente, cada uma com sua prova
  → humano aprova o arquivo
  → handoff vibe-implement ou vibe-analyze
```

`--apply` não transporta a prosa do plan. Ele garante o path e evita sobrescrever um arquivo vivo. Isso deixa o parser mecânico restrito a `### T*`, à linha de conclusão e a `Deps`, enquanto a IA continua dona do significado de aceite, ordem e prova.

## Investigação e ferramentas

A investigação começa pela pergunta de fatiamento e pela dependência que precisa ser provada. A IA usa `rg --files` para localizar spec, regras, entradas e testes, e `rg -n` para localizar A*/C*, decisões, símbolos e comandos. Só abre as entradas e dependências do fluxo. A disponibilidade de `gitleaks` e de capacidade visual é registrada antes de fechar as verificações.

Para UI, a ordem é navegador integrado, MCP Server `chrome-devtools`, Playwright existente ou explicitamente solicitado. Uma tarefa sem UI não recebe um gate de browser.

## Size, Risk e fila

Size mede complexidade estrutural, não tempo ou número de arquivos. Cinco dimensões pontuadas de 0 a 2 classificam `0–3 low`, `4–6 medium`, `7–8 high`; `9–10` exige quebra. Risk permanece separado para registrar impacto e blast radius.

Deps são apenas dependências reais de execução. Cada `T*` tem sua verificação e vira a unidade de execução e commit após a prova verde. T1 deve conter smoke test ou walking skeleton no ponto de entrada real.

## Chat e continuidade

Plan é uma porta de maior risco cognitivo e recomenda novo chat no handoff. O humano pode continuar conscientemente no mesmo chat. O `plan.md` vivo, o status e a linha de handoff são a ponte; o histórico da conversa não é prova.

## Cortes

| Corte | Motivo |
|---|---|
| `todo.md` ou `tasks.md` | Uma casa por fato: índice e corpo ficam no plan. |
| Escrita do plan pelo script | Mantém o motor mecânico e a prosa sob responsabilidade da IA. |
| Verificação somente manual | A implement precisa de comando executável. |
| Instalação automática de navegador | Não adiciona dependência apenas para preencher um gate. |
| Disparo automático de implement | Handoff é explícito e fica no arquivo. |

## Impacto

O implement consegue projetar a fila de T* a partir do vivo, sem depender de uma pasta auxiliar. O contrato de distribuição, os templates e os motores ficam alinhados: um arquivo por etapa, uma entrada viva e uma prova executável.
