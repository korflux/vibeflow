# vibe-implement, arquitetura

`/vibe-implement` executa uma fatia elegível, prova o resultado e registra a trilha em `implement.md`. A IA inspeciona o fluxo, codifica, testa, simplifica e atualiza os artefatos vivos; o motor projeta a fila e prepara o destino.

```text
.vibeflow/phases/phase-<n>-<slug>/plan.md
.vibeflow/phases/phase-<n>-<slug>/implement.md
.vibeflow/phases/phase-<n>-<slug>/spec.md
.vibeflow/phases/phase-<n>-<slug>/review.md
.vibeflow/mvp/implement.md
```

## 1. Papéis e ownership

| Peça | Responsabilidade |
|---|---|
| `SKILL.md` | Gate, escolha de T*/R*, ciclo de seis passos, prova visual, commit da task, registro e handoff. |
| `scripts/implement.py`, `implement.ps1`, `implement.sh` | Inventário, alvo, fila, gate MVP, preparação do vivo e relatório. |
| `templates/implement.md` | Forma da trilha por fatia. |
| `references/chrome-devtools.md` | Checklist de prova renderizada, consultada quando a task toca UI. |
| `.vibeflow/implement-report.json` | Evidência operacional, fora do Git. |
| `implement.md` | Histórico acumulativo da execução, incluindo a mensagem do commit e o handoff; o hash fica no resultado da execução e no chat para evitar um residual pós-commit. |

O script não codifica, não escreve a prosa da implementação, não marca aceite e não escolhe semântica.

## 2. Alvo e fila

Sem `.vibeflow/`, `INIT_AUSENTE`. Com plan, o alvo é a maior phase com `plan.md`; `--dir` força uma phase existente. Sem plan, o relatório deixa a fila nula e a skill encaminha `high+` para `vibe-plan`; uma execução avulsa `low/medium` pode usar `--slug`.

O parser lê somente `### T{n}:`, a linha `T{n} concluída` e `Deps`. `fila.elegiveis` contém tasks abertas cujas dependências estão concluídas; `fila.bloqueadas` expõe as dependências faltantes. R* Critical/Required abertos têm prioridade sem alterar o plan.

No MVP, `--mvp` fixa `.vibeflow/mvp/`, exige plan e analyze aprovado com veredito limpo, e não aceita slug ou dir.

## 3. Relatório

O relatório contém `vibeflow`, `phases`, `next_n`, `existing`, `plan_pendente`, `rascunho`, `alvo`, `mvp`, `modo_sugerido`, `created`, `modo`, `actions`, `avisos` e `fila`. `files` lista os seis artefatos vivos.

`actions` registra criação de phase ou de `implement.md`. Não há estado de arquivo temporário, promoção, cópia ou hash de conteúdo semântico.

## 4. Apply e escrita direta

1. Reexecuta o inventário e a projeção da fila.
2. Valida alvo, modo e, no MVP, o gate de analyze.
3. Cria a phase avulsa quando `--slug` for permitido.
4. Prepara `implement.md` vazio somente quando ausente.
5. Preserva bytes do vivo existente.
6. A IA executa a task e grava diretamente a nova seção em `implement.md`.

O apply não substitui histórico acumulativo. Plan, spec e review recebem apenas os patches semânticos que a skill autoriza, depois da prova verde.

## 5. Ciclo da fatia

Cada T*/R* segue: reconhecer o fluxo real, codar a solução mínima, testar com comando real, simplificar, re-testar e registrar. Falha de teste exige diagnóstico da causa raiz e nova execução.

Em UI, a seleção é navegador integrado quando disponível, MCP Server `chrome-devtools` para snapshot, screenshot, DOM, estilos, console, rede e assets, e Playwright somente se já existir no repositório ou for solicitado. Com UI, o `design.md` aprovado do alvo é entrada do reconhecer, com tokens, motion e prova por tela. No Express, a implement segue só o recorte existente e alterado do design quando houver, sem exigir design ausente, sem apply de design, sem plan novo e sem reabrir tasks antigas. A prova registra rota, viewport, estado, ações e evidência; sem capacidade visual, a limitação impede marcar a validação visual.

## 6. Artefato, modos e handoff

`implement.md` mantém uma seção por T*/R* com feito, marcado, prova, feedback, commit e pontos para review. Modo A executa exatamente uma task elegível, cria seu commit e para; modo B só existe quando o humano pede execução contínua e cria um commit por task. A mensagem e o hash do commit são registrados no resultado da execução e no chat, sem reabrir o artefato vivo depois do commit.

Quando a fila da run termina, o handoff é `vibe-review`. Recomenda-se um novo chat focado por T* e outro para review. O plan e o implement vivos são a ponte; continuar no mesmo chat é escolha consciente.

## 7. Erros e testes

Falhas previstas usam `CODIGO: descrição`, incluindo `IMPLEMENT_SEM_ALVO`, `IMPLEMENT_SEM_PLAN`, `IMPLEMENT_ANALYZE_AUSENTE`, `IMPLEMENT_ANALYZE_RASCUNHO`, `IMPLEMENT_ANALYZE_BLOQUEADO`, `FASE_AUSENTE`, `MODO_INVALIDO` e `PHASES_INESPERADO`.

Suítes: `docs/vibe-implement/tests/test-implement.py` e `docs/vibe-implement/tests/test-implement.sh`. Elas cobrem seleção, fila, phase/MVP, reexecução, preservação e paridade.

## 8. Limites

- Sem teste verde executável, não marca `[x]`.
- Não cria `todo.md`, `tasks.md` ou uma segunda trilha.
- Não interpreta a prosa do plan para montar a fila.
- Não publica decisões vigentes em `REGRAS.md`.
- Código e artefatos vivos da task entram no commit path-scoped; relatório fica fora. Cada task verde gera commit sem push; o push só ocorre no fechamento aprovado da phase pela review.
