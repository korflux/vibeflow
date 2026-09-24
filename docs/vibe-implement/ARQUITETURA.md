# vibe-implement, arquitetura

`/vibe-implement` executa uma fatia elegível, prova o resultado e registra status, paths, prova e bloqueios diretamente na task do `plan.md`. A IA inspeciona o fluxo, codifica, testa e simplifica; o motor seleciona alvo e fila sem criar um segundo registro.

```text
.vibeflow/phases/phase-<n>-<slug>/plan.md
.vibeflow/phases/phase-<n>-<slug>/spec.md
.vibeflow/phases/phase-<n>-<slug>/review.md
.vibeflow/mvp/plan.md
```

## 1. Papéis e ownership

| Peça | Responsabilidade |
|---|---|
| `SKILL.md` | Gate, escolha de T*/R*, delegação opcional por capacidade do host, ciclo de seis passos, prova final, commit da task, registro e handoff. |
| `scripts/implement.py`, `implement.ps1`, `implement.sh` | Inventário interno, alvo, fila, gate MVP e JSON operacional compacto no stdout. |
| `references/chrome-devtools.md` | Prova renderizada proporcional, consultada quando a task toca UI. |
| `stdout (JSON)` | Alvo, fila e avisos necessários; no MVP também traz o gate de analyze. O inventário completo não é serializado. |
| `plan.md` | Registro único por T*: status, dependências/bloqueios, verificação, prova, paths e decisões materiais. |

O script não codifica, não escreve a prosa da implementação, não marca aceite e não escolhe semântica.

## 2. Alvo e fila

Sem `.vibeflow/`, `INIT_AUSENTE`. Com plan, o alvo é a maior phase com `plan.md`; `--dir` força uma phase existente. Sem plan, o JSON deixa a fila nula e a skill encaminha `high+` para `vibe-plan`; uma execução avulsa `low/medium` pode usar `--slug`.

O parser lê somente `### T{n}:`, a linha `T{n} concluída` e `Deps`. `fila.elegiveis` contém tasks abertas cujas dependências estão concluídas; `fila.bloqueadas` expõe as dependências faltantes. R* Critical/Required abertos têm prioridade sem alterar o plan.

No MVP, `--mvp` fixa `.vibeflow/mvp/`, exige plan e analyze aprovado com veredito limpo, e não aceita slug ou dir.

## 3. JSON operacional no stdout

O JSON transitório contém somente `alvo`, `fila` e `avisos`. O alvo expõe `kind`, `dir`, `n`, `slug` e `path`; no MVP, `analyze_gate` acompanha esses campos. A fila traz parse, status das T*, elegíveis, dependências bloqueantes e avisos do plan. Nenhum item serializa todas as phases.

## 4. Apply e escrita direta

1. Reexecuta o inventário e a projeção da fila.
2. Valida o alvo e, no MVP, o gate de analyze.
3. Cria somente a pasta da phase quando `--slug` for permitido.
4. Emite o JSON operacional compacto para leitura imediata da IA.
5. Depois da prova verde, a IA atualiza status, prova e paths diretamente sob a T* no `plan.md`.

Apply não cria `implement.md`, não altera arquivos históricos e não escreve a prosa do plan. Spec e review recebem somente os patches semânticos que a skill autoriza, depois da prova verde.

## 5. Ciclo da fatia

Cada T*/R* segue: reconhecer o fluxo real, selecionar execução sequencial ou delegação nativa do host, integrar as mudanças, simplificar e executar a prova final. A prova roda após a última edição de código/teste e cobre o estado integrado. Falha exige diagnóstico e repetição da prova afetada; alteração posterior em um input de código/teste invalida somente as provas que o cobrem. Atualização de plan, spec, review ou metadados não invalida a prova. Smoke Test acompanha mudança real no ponto de entrada, não o número da task.

Delegação só atende T*s elegíveis e independentes. Cada entrega recebe resultado, aceite, dependências, paths exclusivos e comando de verificação. Use worktree/branch isolada ou ownership sem sobreposição; sem isolamento seguro, mantenha a execução sequencial. O coordenador é o único escritor de `plan.md`, `spec.md`, `review.md` e do índice Git. A prova reportada por um agente não substitui a verificação do estado integrado.

Em UI, a seleção é navegador integrado quando disponível, MCP Server `chrome-devtools` para snapshot, screenshot, DOM, estilos, console, rede e assets, e Playwright somente se já existir no repositório ou for solicitado. Com UI, o `design.md` aprovado do alvo é entrada do reconhecer, com tokens, motion e prova por tela. A checagem começa pela tela, estado e viewport afetados; amplia quando layout, responsividade, interação, componente compartilhado ou risco exigirem. No Express, a implement segue só o recorte existente e alterado do design quando houver, sem exigir design ausente, sem apply de design, sem plan novo e sem reabrir tasks antigas. A prova registra rota, viewport, estado, ações e evidência; sem capacidade visual, a limitação impede marcar a validação visual.

Checkpoint de retomada é um bloco opcional sob uma T* que continua incompleta ou entra em handoff. Registra estado, próximo passo, paths que alimentam a prova, `HEAD`, hashes `git hash-object` desses paths e a última prova. Na retomada, a IA confere `git status --short`, `HEAD` e cada hash antes de reaproveitar a prova; hash divergente ou snapshot incompleto invalida somente a prova afetada. O checkpoint sai do plan quando a task fecha; status, prova e paths finais permanecem na T*.

## 6. Artefato, modos e handoff

`plan.md` mantém o status, a verificação, o resultado da prova, os paths e os bloqueios de cada T*. Achados R* e vereditos continuam no `review.md`. Modo A executa exatamente uma task elegível, cria seu commit e para. Modo B exige autorização explícita; pode delegar T*s independentes, recalcula a fila após cada conclusão e cria um commit por task. O coordenador serializa as marcações e operações no índice Git. A mensagem e o hash do commit ficam no resultado da execução e no chat, sem reabrir o plan após o commit.

Quando a fila da run termina, o handoff é `vibe-review`. Recomende um chat por T* em execução sequencial e novo chat para review. Um grupo paralelo aprovado pode ser conduzido por um chat coordenador, mantendo isolamento e commit próprio por task. Se o humano preferir o mesmo chat, continue sem bloquear; o plan e o diff são a ponte.

## 7. Erros e testes

Falhas previstas usam `CODIGO: descrição`, incluindo `IMPLEMENT_SEM_ALVO`, `IMPLEMENT_SEM_PLAN`, `IMPLEMENT_ANALYZE_AUSENTE`, `IMPLEMENT_ANALYZE_RASCUNHO`, `IMPLEMENT_ANALYZE_BLOQUEADO`, `FASE_AUSENTE`, `MODO_INVALIDO` e `PHASES_INESPERADO`.

Suítes: `docs/vibe-implement/tests/test-implement.py` e `docs/vibe-implement/tests/test-implement.sh`. Elas cobrem seleção, fila, phase/MVP, preservação, paridade, ordem de conclusão independente e contratos de delegação, ownership, prova final e retomada.

## 8. Limites

- Sem teste verde executável, não marca `[x]`.
- Não cria `todo.md`, `tasks.md` ou uma segunda trilha.
- Não interpreta a prosa do plan para montar a fila.
- Não cria `implement.md` nem depende dele para selecionar uma execução; arquivos históricos permanecem intactos.
- Agentes delegados não escrevem artefatos vivos, não operam o índice Git e não criam commits.
- Não publica decisões vigentes em `REGRAS.md`.
- Código e artefatos vivos da task entram no commit path-scoped; o JSON do inventário é transitório no stdout. Cada task verde gera commit sem push; o push só ocorre no fechamento aprovado da phase pela review.
