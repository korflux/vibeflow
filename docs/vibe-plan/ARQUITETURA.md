# vibe-plan, arquitetura

`/vibe-plan` fatia uma spec aprovada em tasks verificáveis e grava um único `plan.md`. A IA define a ordem técnica e a prova; os motores inventariam o alvo e preparam o arquivo vivo.

```text
.vibeflow/phases/phase-<n>-<slug>/plan.md
.vibeflow/mvp/plan.md
```

## 1. Papéis e ownership

| Peça | Responsabilidade |
|---|---|
| `SKILL.md` | Validar a spec, preparo das provas, resultados, dependências e paralelismo seguro. |
| `scripts/plan.py`, `plan.ps1`, `plan.sh` | Inventário, seleção do alvo, gates mecânicos, preparação do vivo e JSON operacional no stdout. |
| `templates/plan.md` | Forma compacta de Overview, preparo opcional, Tasks e handoff. |
| `stdout (JSON)` | Evidência operacional transitória, consumida na mesma execução. |
| `plan.md` | Fila executável e fonte da próxima T*. |

## 2. Dependências e seleção

Sem `.vibeflow/`, `INIT_AUSENTE`. O modo phase exige `spec.md` e reusa a maior phase com spec sem plan. `--dir` força uma phase existente. O plan não cria uma phase nova e não pisa um alvo com `analyze.md`.

No modo MVP, `--mvp` fixa `.vibeflow/mvp/`, exige `spec.md`, recusa `--dir` e encaminha para `vibe-analyze`. A flag representa uma decisão semântica da IA.

Flags públicas:

```text
python plan.py [--root PATH] [--apply] [--dir phase-N-slug] [--mvp]
pwsh plan.ps1 [-Root PATH] [-Apply] [-Dir phase-N-slug] [-Mvp]
bash plan.sh [--root PATH] [--apply] [--dir phase-N-slug] [--mvp]
```

## 3. Pré-requisitos de prova

A IA verifica `gitleaks` quando o repositório prevê essa prova. Se a spec toca UI, escolhe navegador integrado quando disponível, depois MCP Server `chrome-devtools`, e Playwright somente se já existir no repositório ou tiver sido solicitado. Ausência de capacidade visual é limitação explícita, não passe silencioso.

Tasks devem conter um resultado coeso, aceite observável, comando executável de verificação, `Deps` e `Spec: A*/C*`. `Arquivos` e `Risco` são opcionais quando orientam execução, isolamento ou review. Se a task criar ou alterar um ponto de entrada executável, a prova de smoke entra nessa mesma task.

## 4. JSON operacional no stdout

O JSON transitório mantém `vibeflow`, `phases`, `next_n`, `existing`, `spec_pendente`, `rascunho`, `alvo`, `mvp`, `modo_sugerido`, `created`, `modo`, `actions` e `avisos`. Não existe estado de arquivo temporário no contrato.

`actions` registra criação de `phases/.gitkeep` ou do arquivo vivo. `files` lista os seis artefatos da cadeia.

## 5. Apply e escrita direta

1. Reexecuta o inventário.
2. Valida predecessor, `--dir`, status mecânico e ausência de `analyze.md`.
3. Prepara `plan.md` vazio quando ausente.
4. Preserva bytes do vivo existente.
5. Emite o JSON operacional no stdout para leitura imediata da IA.
6. A IA escreve ou atualiza diretamente `plan.md`, mantendo `# Status: rascunho` até aprovação.

O script não escreve prosa, não escolhe a semântica da fila e não dispara implement. Ajuste ou aprovação posterior é patch no arquivo vivo.

## 6. Contrato do artefato

Seções: Overview, preparo local opcional, Tasks e Handoff. `Paralelização` e checkpoint de review aparecem somente quando mudam a execução. `Deps` é a única declaração da fila. Cada task usa `T1`, `T2` em sequência, tem um resultado coeso, comando próprio de verificação e é a unidade que a implement pode commitar. Não usar `todo.md`, `tasks.md`, `T001`, `[P]`, `[US1]`, `checklists/` ou verificação apenas manual.

## 7. Erros, testes e handoff

Falhas previstas usam `CODIGO: descrição`, incluindo `INIT_AUSENTE`, `PLAN_SEM_SPEC`, `PLAN_JA_ANALISADO`, `FASE_AUSENTE`, `MVP_INESPERADO` e `MODO_INVALIDO`.

Suítes: `docs/vibe-plan/tests/test-plan.py` e `docs/vibe-plan/tests/test-plan.sh`.

O handoff normal é `vibe-implement`; no MVP é `vibe-analyze`. Recomende novo chat para iniciar plan após spec/design e para a porta seguinte, sem bloquear a continuidade se o humano preferir. Para grupos paralelizáveis, o `plan.md` nomeia as T*s e registra o motivo; o `plan.md` vivo carrega a fila verificável.

## 8. Limites

- Plan não contém código nem abre fase por conta própria.
- O inventário não autoriza ler a árvore inteira. A IA localiza evidências com `rg --files` e `rg -n`.
- O JSON operacional é transitório no stdout; `plan.md` entra no Git.
- Plan não commita; o commit começa somente quando a implement fecha uma task verde. Não há disparo automático da próxima skill.
