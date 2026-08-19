# Analyze: <frase curta>
# Pasta: phase-<n>-<slug>
# Status: rascunho
# Plan: plan.md (mesma pasta)

## Fontes

| Arquivo | Estado |
|---|---|
| interview.md | presente \| ausente |
| spec.md | presente |
| plan.md | presente |
| REGRAS.md | lido |

## Cobertura

| Chave | Origem | T* | Notas |
|---|---|---|---|
| A1 | spec.md | T1 | … |
| C1 | spec.md | T2 | … |

<!-- interview Resultado.Sucesso vira linha se interview.md existir -->

## Achados

| ID | Categoria | Gravidade | Onde | Resumo | Remédio |
|---|---|---|---|---|---|
| F1 | cobertura | HIGH | spec.md A3 / plan.md | A3 sem T* | volta vibe-plan |

### F1: <resumo curto>

- **Gravidade:** CRITICAL \| HIGH \| MEDIUM \| LOW
- **Categoria:** duplicacao \| ambiguidade \| furo \| constituicao \| cobertura \| inconsistencia
- **Onde:** `spec.md` A3; `plan.md` T1
- **Evidência:** <trecho ou id; sem isso o F* não existe>
- **Remédio:** volta vibe-spec \| volta vibe-plan \| volta vibe-interview \| nenhum

## Clarificações

<!-- omitir se esta run não fez Q -->

- Q: … → A: …

## Constituição

<!-- omitir se zero choque com REGRAS.md -->

- F*: <qual regra> — <o que o artefato diz>

## Métricas

- A*/C* na spec:
- T* no plan:
- Cobertura (A*/C* com ≥1 T*):
- Achados: CRITICAL / HIGH / MEDIUM / LOW
- Overflow além de 50: <n ou 0>

## Veredito

limpo \| bloqueado

<!-- bloqueado se algum CRITICAL aberto -->

## Handoff

vibe-implement

<!-- se bloqueado: volta vibe-spec | volta vibe-plan | volta vibe-interview -->

- [ ] Aprovação humana (leu o arquivo e confirmou)
