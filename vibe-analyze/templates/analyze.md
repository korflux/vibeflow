# Analyze: <frase curta>
# Alvo: <phase-<n>-<slug> ou mvp>
# Status: rascunho
# Plan: plan.md (mesma pasta)

<!-- Escreva diretamente neste artefato vivo; o status permanece rascunho durante a elaboração. -->

## Fontes

| Arquivo | Estado |
|---|---|
| interview.md | presente | ausente |
| spec.md | presente |
| plan.md | presente |
| REGRAS.md | lido |

## Cobertura e Rastreabilidade

| Chave | Origem | T* | Notas |
|---|---|---|---|
| A1 | spec.md | T1 | ... |
| C1 | spec.md | T2 | ... |

<!-- interview Resultado.Sucesso vira linha se interview.md existir -->

## Achados e Resoluções

| ID | Categoria | Gravidade | Onde | Problema | Resolução Aplicada |
|---|---|---|---|---|---|
| F1 | cobertura | HIGH | plan.md | A3 sem T* correspondente | Patch aplicado em plan.md adicionando T3 |

### F1: <resumo curto>

- **Gravidade:** CRITICAL | HIGH | MEDIUM | LOW
- **Categoria:** duplicacao | ambiguidade | furo | constituicao | cobertura | inconsistencia | qualidade_teste | decisao
- **Onde:** `spec.md` ou `plan.md`
- **Evidência:** <trecho ou ID afetado>
- **Resolução:** <ação corretiva aplicada diretamente no arquivo ou decisão do usuário>

## Decisões críticas

<!-- Omitir fora do MVP e quando a phase não cria nem substitui decisões. -->

| ID | Interview | Spec | Plan | Estado |
|---|---|---|---|---|
| <DOMINIO-01> | <opção> | <mantém, cria ou substitui: opção> | <T* responsável> | consistente |

## Clarificações com o Usuário

<!-- Omitir se não foram necessárias perguntas adicionais -->

- Q: ... -> A: ... (aplicado em <arquivo>)

## Constituição

<!-- Omitir se zero choque com REGRAS.md -->

- Regra: <qual regra> -> Resolução: <ajuste aplicado para conformidade>

## Métricas

- A*/C* na spec:
- T* no plan:
- Cobertura (A*/C* com >= 1 T*):
- Qualidade de Testes: T1 smoke test ok, comandos executáveis ok, ferramentas essenciais ok
- Achados corrigidos / resolvidos:
- Achados bloqueantes pendentes: 0

## Veredito

limpo | bloqueado

<!-- limpo quando todas as inconsistências foram corrigidas e o plano está pronto para execução -->

## Handoff

vibe-implement
<!-- No MVP, acrescentar: rota: max -->

- Chat: recomende novo chat para `vibe-implement`; continuidade no mesmo chat só por escolha consciente. O `analyze.md` e os artefatos vivos são a ponte.

- [ ] Aprovação humana (leu o arquivo e confirmou)
