# vibe-plan, mapeamento e fluxo

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
| Papel | Fatiar a spec em T* executáveis | Desenho técnico (research, modelo, contratos) | Lista T001 por user story | Teste de qualidade da prosa da spec |
| Disco | `plan-fase` **e** `todo-fase` | `plan.md` + `research.md` + `data-model.md` + `contracts/` + `quickstart.md` | `tasks.md` | `checklists/<domínio>.md` |
| N | Reusa o da spec | Pasta `specs/NNN-slug` já existente | Idem | Idem |
| How | Ordem, grafo, aceite, verificação | Tech context, constitution, 3 layouts de repo | Setup → Foundational → US1... → Polish | Qualidade da escrita, não da entrega |
| Task | T1 corpo completo no todo | Não fatia | `- [ ] T001 [P] [US1] … path` | CHK001 perguntas à spec |

Spec-kit parte plan (técnica) e tasks (fila). Fluxline parte plan (índice) e todo (corpo). Checklist do spec-kit testa se a spec está bem escrita: isso já é gate da `vibe-spec` (A*/C*, Q+RECOMENDO, sem Open Questions).

---

## Síntese (uma skill, um arquivo)

```
.vibeflow/phases/phase-N-slug/plan.md
```

Um arquivo. Overview + ordem + riscos + **corpo das T\*** + conferência. A build futura marca `[x]` neste arquivo. Spec continua a fonte do "o quê"; plan só fatia.

| Entra | De onde | Como |
|---|---|---|
| Gate: sem spec não planeja | Fluxline | `PLAN_SEM_SPEC` |
| Pedido de plan aprova spec rascunho | Fluxline | Patch no `spec.md` |
| Fatia vertical, não horizontal | Fluxline + tasks (história independente) | Uma T* = caminho usável |
| Size por score de cinco dimensões; quebrar score 9–10 | Decisão desta phase | Matriz canônica na skill |
| Risk separado do Size | Decisão desta phase | Campo próprio no template |
| Tempo fora do cálculo | Decisão desta phase | Size é classificação ordinal, não estimativa |
| T* com aceite, verificação, deps, Spec: A*/C* | Fluxline | Corpo no `plan.md` |
| Walking Skeleton / Smoke Test na T1 | Engenharia / Robustez | T1 valida ponto de entrada real |
| Validação de ferramentas de teste (gitleaks, chrome-devtools) | Governança | Checar ambiente; alocar task se faltar |
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
| Testes "opcionais" do tasks | Toda T* tem verificação **comando**. Sem T010 de contrato se a spec não pediu |
| Verificação só "passo manual" / leitura | A implement não marca sem RED-GREEN; o plan não oferece essa fuga |
| `checklists/ux.md` CHK001… | Qualidade da spec é job da spec. Plan só confere cobertura A*/C* |
| Pointer DoD da build | `vibe-implement` ainda não existe. Aceite da T* + C* da spec |
| Hooks, extensions.yml | Outro produto |
| Abrir fase nova com slug | Plan **não** nasce sem spec |
| Disparar implement | REGRAS: handoff é linha |
| Open Questions no `.md` | Chat |
| Código nesta skill | Fora |

---

## Fluxo de uma run

```
[1] IA compreende o motor plan, parâmetros e invariantes determinísticos
[2] Script executa inventário mecânico → plan-report.json
[3] IA analisa o relatório como evidência, lê spec.md da alvo, interview.md (se houver) e REGRAS.md
[4] IA valida ferramentas de suporte no ambiente (gitleaks, chrome-devtools) e define tasks de setup se ausentes
[5] Sem spec → para, mande vibe-spec. Spec rascunho + humano pediu plan → flip spec para aprovado
[6] IA realiza conferência de robustez, pontua cada T* nas cinco dimensões e faz o fatiamento vertical com smoke test na T1
[7] IA escreve plan-wip.md no molde do template (Status: rascunho)
[8] Script apply promove com validação atômica → phase-N-slug/plan.md ou mvp/plan.md
[9] Chat: path + 4 linhas com resumo e validação de ferramentas
[10] Ajuste = patch no vivo. Aprovado ou "pode ir pro implement" = Status: aprovado
[11] IA fecha a run sem commit automático e sem auto-invoke da próxima skill
```

---

## Assumido

### Extensão MVP

No MVP, o mesmo fatiamento vertical opera em `.vibeflow/mvp/`. A spec aprovada é obrigatória, os IDs críticos atravessam as tasks que os implementam e o handoff muda para `vibe-analyze`, mantendo a rota max. A flag é explícita porque selecionar produto versus feature continua sendo responsabilidade da IA.

- Sem spec não há plan. Rota `high` passa por spec primeiro.
- `analyze.md` na pasta trava overwrite (`PLAN_JA_ANALISADO`). Pedido novo = outra fase.
- Conferência não substitui review. É só “a spec aguenta o fatiamento?”
- Handoff padrão da phase sem analyze obrigatório: `vibe-implement`. No alvo MVP: `vibe-analyze`.
