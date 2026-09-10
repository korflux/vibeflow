# vibe-spec, arquitetura

`/vibe-spec` grava o comportamento decidido para que o plan não invente escopo. A IA conduz o gate semântico e escreve o documento vivo; o motor resolve o alvo e prepara o arquivo.

```text
.vibeflow/phases/phase-<n>-<slug>/spec.md
.vibeflow/mvp/spec.md
```

## 1. Papéis e ownership

| Peça | Responsabilidade |
|---|---|
| `SKILL.md` | Entender a intenção, fechar dúvidas e redigir comportamento, aceite e limites. |
| `scripts/spec.py`, `spec.ps1`, `spec.sh` | Inventário, resolução phase/MVP, validação de predecessores, preparação do vivo e relatório. |
| `templates/spec.md` | Estrutura do documento. O motor não preenche prosa. |
| `references/ui-visual-direction.md` | Catálogo consultado somente quando a spec toca UI. |
| `.vibeflow/spec-report.json` | Evidência operacional, fora do Git. |
| `spec.md` | Fonte viva, rascunho ou aprovada, commitável. |

## 2. Dependências e seleção

Sem `.vibeflow/`, `INIT_AUSENTE`. No modo phase, o alvo é a maior phase com `interview.md` sem `spec.md`, depois a maior phase com spec sem plan. Se não houver alvo, `--slug` cria uma phase nova. `--dir` força uma phase existente.

No modo MVP, `--mvp` exige `.vibeflow/mvp/interview.md`, recusa `--slug` e `--dir`, e nunca cria phase. `plan.md` existente bloqueia uma nova escrita semântica para esse alvo.

Flags públicas:

```text
python spec.py [--root PATH] [--apply] [--slug TEXTO] [--dir phase-N-slug] [--mvp]
pwsh spec.ps1 [-Root PATH] [-Apply] [-Slug TEXTO] [-Dir phase-N-slug] [-Mvp]
bash spec.sh [--root PATH] [--apply] [--slug TEXTO] [--dir phase-N-slug] [--mvp]
```

## 3. Relatório

O relatório mantém `vibeflow`, `phases`, `next_n`, `existing`, `interview_pendente`, `rascunho`, `alvo`, `mvp`, `modo_sugerido`, `created`, `modo`, `actions` e `avisos`. O campo `files` lista apenas artefatos vivos da cadeia.

`actions` registra criação de `phases/.gitkeep`, phase, MVP ou do arquivo vivo. O relatório não descreve conteúdo semântico nem uma etapa de transporte temporário.

## 4. Apply e escrita direta

1. Reexecuta o inventário e valida `spec.md` predecessor, slug e colisões.
2. Prepara `spec.md` vazio quando o destino ainda não possui o arquivo.
3. Preserva byte a byte o arquivo vivo existente.
4. Grava o relatório operacional.
5. A IA escreve ou atualiza diretamente o `spec.md`, mantendo `# Status: rascunho` durante a elaboração.
6. A aprovação é um patch no vivo; um novo apply não é necessário para mudar o status.

O script não escolhe comportamento, não pergunta, não preenche markdown e não altera `REGRAS.md`. Em falhas de seleção, o arquivo anterior permanece intacto.

## 5. Artefato e decisões

Seções: Objetivo, Inventário quando houver lista, Suposições e decisões, Escopo e comportamento, Fora, Direção visual quando aplicável, Checklist de entrega, Implementação delta, Como provar, Boundaries e Handoff.

Sem Open Questions, mural de user story ou CSS na spec. IDs de decisões críticas do MVP atravessam o plan; publicação de decisão vigente só ocorre após review aprovada e confirmação humana.

## 6. Erros e testes

Falhas previstas usam `CODIGO: descrição` no stderr. O contrato cobre `INIT_AUSENTE`, `PHASES_INESPERADO`, `MVP_INESPERADO`, `MVP_INTERVIEW_AUSENTE`, `SPEC_SEM_ALVO`, `PLAN_SEM_SPEC`, `SPEC_JA_PLANEJADA`, `FASE_AUSENTE`, `FASE_EXISTE`, `SLUG_INVALIDO` e `MODO_INVALIDO` conforme o modo.

Suítes: `docs/vibe-spec/tests/test-spec.py` e `docs/vibe-spec/tests/test-spec.sh`. Elas verificam criação, reexecução, MVP, `--dir`, colisões, paridade e preservação do vivo.

## 7. Limites

- A IA é dona da prosa; o script é dono de path, inventário e relatório.
- Um alvo possui um `spec.md`; pedido novo usa outra phase.
- O inventário e o relatório são mapas de seleção. A IA usa `rg --files` e `rg -n` para abrir somente as entradas e dependências relevantes.
- A continuidade pode permanecer no chat de `interview`; `plan` deve receber o caminho e o status do arquivo vivo.
- O arquivo vivo entra no Git; `spec-report.json` fica fora. Não há commit automático.
