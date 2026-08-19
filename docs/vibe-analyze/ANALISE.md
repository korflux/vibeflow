# vibe-analyze — mapeamento e fluxo

Fontes:

- [spec-kit clarify](https://github.com/github/spec-kit/blob/main/templates/commands/clarify.md)
- [spec-kit analyze](https://github.com/github/spec-kit/blob/main/templates/commands/analyze.md)
- Contrato `.vibeflow/REGRAS.md` e as skills `vibe-interview`, `vibe-spec`, `vibe-plan`

Pedido: **uma** skill. Não duas portas. Análise cruzada de interview + spec + plan.

---

## O que cada fonte é

| | Spec-kit clarify | Spec-kit analyze | Cadeia vibe |
|---|---|---|---|
| Papel | Até 5 perguntas; grava a resposta **dentro** do `spec.md` | Relatório read-only de consistência spec/plan/`tasks.md` | Interview fecha intenção; spec o decidido; plan as T*; analyze o cruzamento |
| Quando | Antes do plan | Depois do `tasks.md`, antes do implement | Depois do `plan.md`, antes do implement (rota `max`; também se o humano pedir) |
| Disco | Patch no spec | Só chat (não grava arquivo) | `.vibeflow/phases/phase-N-slug/analyze.md` |
| Constituição | `memory/constitution.md` | Idem; violação = CRITICAL | `.vibeflow/REGRAS.md` |
| Terceiro artefato | — | `tasks.md` separado | Corpo das T* **já está** no `plan.md` |

Clarify e analyze no spec-kit são portas distintas: uma **escreve** a spec, a outra **proíbe** escrita. Juntar as duas sem regra vira a analyze patchando spec em silêncio, ou a clarify fingindo consistência cruzada. A síntese separa os papéis no tempo da run, não em duas skills.

---

## Síntese (uma skill, um arquivo)

```
.vibeflow/phases/phase-N-slug/analyze.md
```

A IA lê as três fontes (interview se existir) e o `REGRAS.md`. Cruza. Pergunta no chat só o que o disco não fecha (máx. 5). Grava o relatório. **Não** pisa interview/spec/plan. Remédio de um achado CRITICAL/HIGH é handoff de volta à skill dona do arquivo.

| Entra | De onde | Como |
|---|---|---|
| Read-only das fontes | Analyze | Script e skill não editam os três `.md` de origem |
| Tabela de achados + gravidade | Analyze | `F1…` no `analyze.md`, não no chat |
| Cobertura requisito × task | Analyze (`tasks.md`) | A*/C* da spec × `Spec:` das T* no plan |
| Constituição MUST | Analyze + constitution | Choque com `REGRAS.md` = CRITICAL |
| Teto 50 achados + overflow | Analyze | Métricas |
| Taxonomia de furo (escopo, dado, UX, NFR, borda…) | Clarify | `references/coverage.md`, mapa interno |
| Até 5 perguntas, uma por vez, com recomendação | Clarify | Chat. Resposta vai para **Clarificações** no analyze, não para o spec |
| Interview no cruzamento | Vibe (não existe no spec-kit) | Resultado/Fora da interview × Objetivo/A*/Fora da spec × T* |
| Mesma pasta, sem `n` novo | Vibe-plan | `ANALYZE_SEM_PLAN` / `ANALYZE_SEM_SPEC` |
| Pedido desta porta aprova plan rascunho | Vibe-spec/plan | Flip no `plan.md` |
| Grava já; chat = path + resumo | Vibe-spec/plan | Igual às irmãs |
| Handoff sem disparar a próxima | REGRAS | `vibe-implement` se limpo; senão `volta vibe-*` |

---

## O que foi cortado

| Corte | Motivo |
|---|---|
| Skill `vibe-clarify` à parte | Pedido: uma. Interview já fecha intenção; spec já fecha buraco pontual com Q+RECOMENDO |
| Patch automático no `spec.md` | Dono do arquivo é `vibe-spec`. Analyze que escreve spec fura a fonte única e apaga trilha |
| Relatório só no chat | REGRAS: disco completo. Spec-kit analyze some no scroll |
| `tasks.md` / T001 / `[P]` / `[US1]` | Plan já fatia no `plan.md` |
| `docs/fluxline/`, `specs/NNN-slug/` | Contrato `phase-N-slug` |
| Hooks, `extensions.yml`, checklist `requirements.md` | Outro produto |
| FR-00N / SC-00N | A*/C*/T* já existem |
| Abrir fase nova | Analyze não nasce sem plan |
| Disparar implement ou a skill de remédio | Handoff é linha |
| Open Questions no `.md` | Chat. Achado é fato + remédio, não pergunta aberta |
| Código nesta skill | Fora |

---

## Fluxo de uma run

```
[1] Script inventário → analyze-report.json
[2] IA lê relatório + spec.md + plan.md (+ interview.md) + REGRAS.md
[3] Sem plan → para, mande vibe-plan. Sem spec no destino → ANALYZE_SEM_SPEC
[4] Plan rascunho + humano pediu analyze → flip plan para aprovado, segue
[5] Mapa interno (coverage.md). Passes: duplicação, ambiguidade, furo,
    constituição, cobertura, inconsistência cruzada
[6] Se um furo só o humano fecha: até 5 Q+RECOMENDO, uma a uma.
    Resposta entra em Clarificações. Não edita spec/plan
[7] Wip = analyze.md completo (veredito limpo ou bloqueado)
[8] Apply promove
[9] Chat: path + métricas + 3–5 F* altos. Humano lê o arquivo
[10] Ajuste = patch no vivo. Aprovado = Status aprovado
[11] Fecha. Não commita. Não dispara a próxima
```

---

## Assumido

- Sem plan não há analyze. Rota `max` passa por spec e plan primeiro. Pedido explícito `/vibe-analyze` também.
- Interview ausente (rota `high`) não bloqueia: o cruzamento é spec × plan + REGRAS; a ausência é uma linha em Fontes.
- CRITICAL aberto ⇒ veredito `bloqueado` ⇒ handoff `volta` para a skill dona. Implement não começa.
- `PLAN_JA_ANALISADO` na vibe-plan continua valendo: plan não pisa pasta que já tem `analyze.md`. Re-run de analyze **pode** sobrescrever o próprio `analyze.md`.
- Implement ainda não existe; não há trava `ANALYZE_JA_IMPLEMENTADO` no v1.
