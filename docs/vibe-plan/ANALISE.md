# vibe-plan — mapeamento e fluxo

Fontes:

- [fluxline-plan](https://github.com/korflux/fluxline/blob/main/skills/fluxline-plan/SKILL.md)
- [spec-kit plan](https://github.com/github/spec-kit/blob/main/templates/commands/plan.md) + [plan-template.md](https://github.com/github/spec-kit/blob/main/templates/plan-template.md)
- [spec-kit tasks](https://github.com/github/spec-kit/blob/main/templates/commands/tasks.md) + [tasks-template.md](https://github.com/github/spec-kit/blob/main/templates/tasks-template.md)
- [spec-kit checklist](https://github.com/github/spec-kit/blob/main/templates/commands/checklist.md)

Pedido: **uma** skill `plan`. Não três portas. Não `todo.md` extra.

---

## O que cada fonte é

| | Fluxline plan | Spec-kit plan | Spec-kit tasks | Spec-kit checklist |
|---|---|---|---|---|
| Papel | Fatiar a spec em T* executáveis | Desenho técnico (research, modelo, contratos) | Lista T001 por user story | “Unit test” da prosa da spec |
| Disco | `plan-fase` **e** `todo-fase` | `plan.md` + `research.md` + `data-model.md` + `contracts/` + `quickstart.md` | `tasks.md` | `checklists/<domínio>.md` |
| N | Reusa o da spec | Pasta `specs/NNN-slug` já existente | Idem | Idem |
| How | Ordem, grafo, aceite, verificação | Tech context, constitution, 3 layouts de repo | Setup → Foundational → US1… → Polish | Qualidade da *escrita*, não da entrega |
| Task | T1 corpo completo no todo | Não fatia | `- [ ] T001 [P] [US1] … path` | CHK001 perguntas à spec |

Spec-kit parte plan (técnica) e tasks (fila). Fluxline parte plan (índice) e todo (corpo). Checklist do spec-kit testa se a spec está bem escrita: isso já é gate da `vibe-spec` (A*/C*, Q+RECOMENDO, sem Open Questions).

---

## Síntese (uma skill, um arquivo)

```
.vibeflow/phases/phase-N-slug/plan.md
```

Um arquivo. Overview + ordem + riscos + **corpo das T\*** + conferência. A build futura marca `[x]` neste arquivo. Spec continua a fonte do “o quê”; plan só fatia.

| Entra | De onde | Como |
|---|---|---|
| Gate: sem spec não planeja | Fluxline | `PLAN_SEM_SPEC` |
| Pedido de plan aprova spec rascunho | Fluxline | Patch no `spec.md` |
| Fatia vertical, não horizontal | Fluxline + tasks (história independente) | Uma T* = caminho usável |
| Size ≤ high; quebrar xhigh/max | Fluxline | Tabela na skill |
| T* com aceite, verificação, deps, Spec: A*/C* | Fluxline | Corpo no `plan.md` |
| Checkpoints a cada 2–3 | Fluxline + tasks Checkpoint | Índice no plan |
| Alto risco cedo | Fluxline | Ordem |
| UI greenfield: T* de kit **antes** das telas | Fluxline | Regra na skill |
| Paralelo vs sequencial | Fluxline + marker `[P]` do tasks | Seção, sem `[P] [US1]` no ID |
| Grava já; chat = path + resumo | Fluxline / spec | Igual à spec |
| Conferência curta da spec | Checklist (idéia) | Seção no plan, não `checklists/` |
| Comandos reais do repo | Fluxline | Verificação da T*; só manual recusa |
| Linhas `concluída` + `Deps` estáveis | Pedido (fila elegível) | Template congelado; parser mora na implement |
| Ler REGRAS.md | Constitution do spec-kit | Sem tabela Constitution Check |

---

## O que foi cortado

| Corte | Motivo |
|---|---|
| Segundo arquivo `todo.md` / `tasks.md` | REGRAS: um arquivo por skill. Índice + corpo no mesmo `plan.md` |
| `docs/fluxline/plan/…`, `specs/`, branch | Contrato `phase-N-slug` |
| `research.md`, `data-model.md`, `contracts/`, `quickstart.md` | Incham a pasta. Delta técnico já está na spec. Se faltar decisão de ordem, Q+RECOMENDO |
| Constitution Check + Option 1/2/3 | `REGRAS.md` + paths reais. Árvore genérica é ruído |
| Fases Setup / Foundational / Polish obrigatórias | Só existem se **bloquearem** fatia. Senão, fatia vertical |
| Formato `T001 [P] [US1]` | Barulho. `T1` + Deps + seção Paralelização |
| Mural de user stories como eixo | Spec não tem US. Eixo = fatia de valor / A* |
| Testes “opcionais” do tasks | Toda T* tem verificação **comando**. Sem T010 de contrato se a spec não pediu |
| Verificação só “passo manual” / leitura | A implement não marca sem RED-GREEN; o plan não oferece essa fuga |
| `checklists/ux.md` CHK001… | Qualidade da spec é job da spec. Plan só confere cobertura A*/C* |
| Pointer DoD da build | `vibe-implement` ainda não existe. Aceite da T* + C* da spec |
| Hooks, extensions.yml | Outro produto |
| Abrir fase nova com slug | Plan **não** nasce sem spec |
| Disparar implement | Handoff é linha |
| Open Questions no `.md` | Chat |
| Código nesta skill | Fora |

---

## Fluxo de uma run

```
[1] Script inventário → plan-report.json
[2] IA lê relatório + spec.md da alvo (+ interview.md se houver) + REGRAS.md
[3] Sem spec → para, mande vibe-spec
[4] Spec rascunho + humano pediu plan → flip spec para aprovado, segue
[5] Buraco de intenção → interview/spec. Buraco de ordem → Q+RECOMENDO
[6] Conferência: A*/C* testáveis, Fora real, UI com direção se couber
[7] Fatia vertical, size, deps, checkpoints, T* de kit se UI greenfield
[8] Wip = plan.md completo. Apply promove
[9] Chat: path + 4 linhas. Humano lê o arquivo
[10] Ajuste = patch. Aprovado ou “pode ir pro implement” = Status aprovado
[11] Fecha. Não commita. Não dispara implement
```

---

## Assumido

- Sem spec não há plan. Rota `high` passa por spec primeiro.
- `analyze.md` na pasta trava overwrite (`PLAN_JA_ANALISADO`). Pedido novo = outra fase.
- Conferência não substitui review. É só “a spec aguenta o fatiamento?”
- Handoff padrão: `vibe-implement`. Cadeia `max` (analyze no meio) fica para quando essa skill existir; o plan não escolhe sozinho.
