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
| design.md | presente | N/A sem UI visível |
| plan.md | presente |
| AGENTS.md | lido |

## Cobertura e Rastreabilidade

| Chave | Origem | T* | Notas |
|---|---|---|---|
| A1 | spec.md | T1 | ... |
| C1 | spec.md | T2 | ... |

<!-- interview Resultado.Sucesso vira linha se interview.md existir -->

## Achados e Resoluções

| ID | Categoria | Gravidade | Onde | Problema | Resolução Aplicada |
|---|---|---|---|---|---|
| F1 | <categoria> | <gravidade> | <arquivo> | <problema> | <resolução aplicada> |

### F1: <resumo curto>

- **Gravidade:** CRITICAL | HIGH | MEDIUM | LOW
- **Categoria:** duplicacao | ambiguidade | furo | constituicao | cobertura | inconsistencia | qualidade_teste | decisao | contrato_implement
- **Onde:** `spec.md`, `design.md` ou `plan.md`
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

<!-- Omitir se zero choque com AGENTS.md -->

- Regra: <qual regra> -> Resolução: <ajuste aplicado para conformidade>

## Métricas

- A*/C* na spec:
- T* no plan:
- Cobertura (A*/C* com >= 1 T*):
- Qualidade de Testes: <`Prova afetada:` restrita ao recorte por T*; `Regressão completa` única; smoke na T* que entrega o ponto de entrada; ferramentas necessárias ou limitações registradas>
- Contrato da implement: <protocolo; `Arquivos:` válidos e comparáveis; sobreposição sem `Deps`; prontidão com local e destino; ou N/A em plan histórico>
- Achados corrigidos / resolvidos:
- Achados bloqueantes pendentes: 0

## Veredito

limpo | bloqueado

<!-- limpo quando todas as inconsistências foram corrigidas e o plano está pronto para execução -->

## Handoff

vibe-implement
<!-- Na rota max (MVP ou phase), acrescentar: rota: max -->

- Chat: com subagentes, o `vibe-analyze` roda a partir do chat do plan; sem eles, recomende chat novo para iniciar a análise. Recomende com ênfase um chat novo com `/vibe-implement`, que rodará em Modo A num host com subagentes e em Modo B sem eles. Se o humano preferir continuar no mesmo chat, isso não bloqueia. O `analyze.md` e os artefatos vivos são a ponte.

- [ ] Aprovação humana (leu o arquivo e confirmou)
