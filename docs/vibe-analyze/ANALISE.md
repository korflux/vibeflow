# vibe-analyze, mapeamento e fluxo

Fontes:

- [spec-kit clarify](https://github.com/github/spec-kit/blob/main/templates/commands/clarify.md)
- [spec-kit analyze](https://github.com/github/spec-kit/blob/main/templates/commands/analyze.md)
- Contrato `.vibeflow/REGRAS.md` e as skills `vibe-interview`, `vibe-spec`, `vibe-plan`

Pedido: **uma** skill. Não duas portas. Análise cruzada de interview + spec + plan.

---

## O que cada fonte é

| | Spec-kit clarify | Spec-kit analyze | Cadeia vibe |
|---|---|---|---|
| Papel | Até 5 perguntas; grava a resposta dentro do `spec.md` | Relatório read-only de consistência spec/plan/`tasks.md` | Interview fecha intenção; spec o decidido; plan as T*; analyze o cruzamento |
| Quando | Antes do plan | Depois do `tasks.md`, antes do implement | Depois do `plan.md`, antes do implement (rota `max`; também se o humano pedir) |
| Disco | Patch no spec | Só chat (não grava arquivo) | `.vibeflow/phases/phase-N-slug/analyze.md` |
| Constituição | `memory/constitution.md` | Idem; violação = CRITICAL | `.vibeflow/REGRAS.md` |
| Terceiro artefato | N/A | `tasks.md` separado | Corpo das T* já está no `plan.md` |

Clarify e analyze no spec-kit são portas distintas: uma escreve a spec, a outra proíbe escrita. Juntar as duas sem regra vira a analyze patchando spec em silêncio, ou a clarify fingindo consistência cruzada. A síntese separa os papéis no tempo da run, não em duas skills.

---

## Síntese (uma skill, um arquivo de certificação)

```
.vibeflow/phases/phase-N-slug/analyze.md
```

A IA lê as três fontes (interview se existir) e o `REGRAS.md`. Cruza. Audita a solidez dos testes (smoke test na T1, comandos executáveis de teste, presença de gitleaks/chrome-devtools) e a consistência das decisões de MVP. Corrige erros e inconsistências óbvias diretamente nos artefatos (`spec.md` ou `plan.md`). Pergunta no chat ambiguidades reais de negócio/arquitetura sem limite arbitrário, aplicando as respostas. Grava o relatório de certificação de consistência (`analyze.md`) com veredito limpo para handoff imediato para `vibe-implement`.

| Entra | De onde | Como |
|---|---|---|
| Correção ativa de erros óbvios | Vibe | Ajusta diretamente `spec.md` e `plan.md` em vez de travar o fluxo |
| Tabela de achados e resoluções | Analyze | `F1...` no `analyze.md`, registrando o problema e o patch aplicado |
| Cobertura requisito x task | Analyze (`tasks.md`) | A*/C* da spec x `Spec:` das T* no plan |
| Qualidade de Testes e Executabilidade | Governança | T1 com smoke test real; comandos de teste executáveis; gitleaks/chrome-devtools |
| Decisões Críticas e MVP | Governança | Cruzamento estrito de IDs (`AUTH-01`, etc.); divergências sanadas diretamente ou via pergunta |
| Constituição MUST | Analyze + constitution | Choque com `REGRAS.md` corrigido imediatamente nos artefatos |
| Taxonomia de furo (escopo, dado, UX, NFR, borda...) | Clarify | `references/coverage.md`, mapa interno |
| Clarificações pontuais | Clarify | Perguntas no chat para ambiguidades reais, aplicando as respostas nos documentos |
| Interview no cruzamento | Vibe | Resultado/Fora da interview x Objetivo/A*/Fora da spec x T* |
| Mesma pasta, sem `n` novo | Vibe-plan | `ANALYZE_SEM_PLAN` / `ANALYZE_SEM_SPEC` |
| Pedido desta porta aprova plan rascunho | Vibe-spec/plan | Flip no `plan.md` |
| Grava já; chat = path + resumo | Vibe-spec/plan | Igual às irmãs |
| Handoff sem disparar a próxima | REGRAS | `vibe-implement` com veredito limpo certificado |

---

## O que foi cortado

| Corte | Motivo |
|---|---|
| Skill `vibe-clarify` à parte | Pedido: uma. Interview já fecha intenção; spec já fecha buraco pontual com Q+RECOMENDO |
| Modelo passivo que só aponta erro e trava | Ineficiente; a skill agora corrige erros óbvios e esclarece ambiguidades na hora |
| Limite arbitrário de 5 perguntas | A IA faz as perguntas estritamente necessárias para sanar ambiguidades reais |
| Relatório só no chat | REGRAS: disco completo. Spec-kit analyze some no scroll |
| `tasks.md` / T001 / `[P]` / `[US1]` | Plan já fatia no `plan.md` |
| `docs/fluxline/`, `specs/NNN-slug/` | Contrato `phase-N-slug` |
| Hooks, `extensions.yml`, checklist `requirements.md` | Outro produto |
| FR-00N / SC-00N | A*/C*/T* já existem |
| Abrir fase nova | Analyze não nasce sem plan |
| Disparar implement | REGRAS: handoff é linha |
| Open Questions no `.md` | Chat. Ambiguidade é esclarecida e gravada como decisão/resolução |
| Código nesta skill | Fora |

---

## Fluxo de uma run

```
[1] IA entende o motor analyze, entradas e invariantes
[2] Script inventário → analyze-report.json
[3] IA lê relatório como evidência, spec.md, plan.md (+ interview.md) e REGRAS.md
[4] Sem plan → para, mande vibe-plan. Sem spec no destino → ANALYZE_SEM_SPEC
[5] Plan rascunho + humano pediu analyze → flip plan para aprovado, segue
[6] Varredura e auditoria (coverage.md): duplicação, ambiguidade, furo,
    constituição, cobertura, qualidade de testes e decisões críticas de MVP
[7] Erros óbvios corrigidos diretamente em spec.md e plan.md
[8] Ambiguidades reais resolvidas via perguntas ao usuário, aplicando nos artefatos
[9] Wip = analyze.md completo (certificação de consistência e veredito limpo)
[10] Apply promove com validação atômica
[11] Chat: path + métricas + correções aplicadas. Humano lê o arquivo
[12] Ajuste = patch no vivo. Aprovado = Status aprovado
[13] Fecha. Não commita. Não dispara a próxima (handoff vibe-implement)
```



---

## Assumido

### Extensão MVP

No alvo MVP, a interview deixa de ser opcional porque contém o baseline de descoberta. A análise compara os IDs críticos com a ação declarada na spec e com as tasks do plan. A cronologia não resolve conflito: mudança sem `substitui` é finding `CRITICAL`. A IA mantém as fontes e `REGRAS.md` intactos; publicação de decisão vigente pertence ao pós-review.

- Sem plan não há analyze. Rota `max` passa por spec e plan primeiro. Pedido explícito `/vibe-analyze` também.
- Interview ausente (rota `high`) não bloqueia: o cruzamento é spec × plan + REGRAS; a ausência é uma linha em Fontes.
- CRITICAL aberto ⇒ veredito `bloqueado` ⇒ handoff `volta` para a skill dona. Implement não começa.
- `PLAN_JA_ANALISADO` na vibe-plan continua valendo: plan não pisa pasta que já tem `analyze.md`. Re-run de analyze **pode** sobrescrever o próprio `analyze.md`.
- Implement ainda não existe; não há trava `ANALYZE_JA_IMPLEMENTADO` no v1.
