---
name: vibe-analyze
description: >
  Cruza interview, spec e plan do mesmo alvo e grava em `.vibeflow/phases/phase-N-slug/analyze.md` ou `.vibeflow/mvp/analyze.md`. Use when the user runs /vibe-analyze, pede análise cruzada, consistência, cobertura, gaps, contradição entre artefatos, clarify depois do plan, ou a rota é max com plan em disco, mesmo que não diga vibe-analyze.
---

# vibe-analyze

Não invente `n`, slug ou path. Sem plan no alvo, não há analyze. Sem `.vibeflow/`, pare e mande `/vibe-init`.
Erros óbvios e lacunas determinísticas identificados no cruzamento devem ser corrigidos diretamente nos artefatos (`spec.md` ou `plan.md`). Ambiguidades reais de negócio ou arquitetura devem ser esclarecidas com o usuário via chat.
Não atualize decisões vigentes nem `REGRAS.md`. No MVP, conflito crítico sem `substitui` explícito bloqueia a implementação.

## 0. Entender e usar o script

1. Resolva o diretório desta skill e leia o motor que vai executar: `scripts/analyze.ps1` no Windows ou `scripts/analyze.py` no fluxo Unix. Entenda alvo, predecessores, recusas e promoção atômica temporária antes de chamá-lo. Se encontrar defeito, corrija o motor e prove o contrato antes de continuar.
2. No cwd do repo:
   - Windows: `pwsh "<skill>/scripts/analyze.ps1"`.
   - Unix: `bash "<skill>/scripts/analyze.sh"`.
   - Alvo MVP: acrescente `-Mvp` ou `--mvp`.
3. Leia `.vibeflow/analyze-report.json` como evidência operacional. Abra `spec.md` e `plan.md` (obrigatórios), `interview.md` se houver, `analyze.md` se rascunho. Leia `.vibeflow/REGRAS.md` e os arquivos de código necessários de forma direcionada.

Erros determinísticos previstos: `INIT_AUSENTE` exige `/vibe-init`. `ANALYZE_SEM_PLAN` exige plan. `ANALYZE_SEM_SPEC`, `ANALYZE_SEM_INTERVIEW`, `MVP_INESPERADO`, `MODO_INVALIDO` e `FASE_AUSENTE` exigem diagnosticar a causa e não devem ser contornados.

## 1. Abrir

Declare em cerca de cinco linhas: rota, modo, alvo, plan, interview e wip.

```text
modo: reuse · alvo: phase-1-lock-bloco · plan: sim · interview: sim · wip: ausente
```

- `modo_sugerido=criar`: não há pasta com plan. Não invente fase; mande `/vibe-plan`.
- No MVP, interview, spec e plan são obrigatórios no alvo especial e o plan precisa estar aprovado.

## 2. Gate

| Sinal | Ação |
|---|---|
| Typo ou uma linha óbvia | Não usar analyze |
| Sem `plan.md` no alvo | Parar. Encaminhar para `/vibe-plan` |
| Destino sem `spec.md` | Parar. Não contornar `ANALYZE_SEM_SPEC` |
| Plan `# Status: rascunho` e o humano pediu analyze | Alterar o plan para `aprovado` diretamente no arquivo (1 linha no chat) e seguir |
| Plan rascunho sem pedido de analyze | Parar. Pedir leitura do plan |
| Intenção, sucesso ou limites frouxos de verdade | Devolver para `vibe-interview` ou `vibe-spec`. Não "completar" no chute |
| Dúvida de arquitetura ou regra aberta | Perguntar diretamente ao usuário via chat (Q + RECOMENDO) |

```text
Q: <decisão ou clarificação necessária>
RECOMENDO: <opção>, <1 linha explicando motivo e impacto>
(ok / outra?)
```

## 3. Varredura, Correção e Auditoria de Qualidade

Leia `references/coverage.md` como mapa interno. Não copie a taxonomia no chat.

Audite, cruze e resolva:

1. **Interview → spec:** Resultado da interview (o quê, sucesso, fora) contra Objetivo, A*/C* e Fora da spec.
2. **Spec → plan:** Cada A*/C* possui T* correspondente no campo `Spec:`; cada T* referencia A*/C* ou é infraestrutura justificada.
3. **Plan → spec:** Nenhuma T* inventa comportamento, caminhos ou módulos fora do escopo aprovado.
4. **Qualidade dos Testes e Executabilidade:**
   - A T1 do plan estabelece um *Smoke Test / Walking Skeleton* real validando a subida/ponto de entrada do sistema? Se faltar, corrija diretamente no `plan.md` inserindo o teste na T1.
   - As tasks possuem comandos reais de teste no repositório? Se houver verificação puramente manual sem comando, converta para comando executável real no `plan.md`.
   - Ferramentas essenciais (`gitleaks`, MCP `chrome-devtools`) foram validadas ou possuem task de setup? Se faltar, adicione a task de setup necessária no `plan.md`.
5. **Decisões Críticas (MVP):** Cruze cada ID entre interview, spec e plan. Se houver divergência sem declaração de `substitui` ou ID órfão, ajuste a consistência nos artefatos ou pergunte ao usuário se for mudança intencional.
6. **Conformidade com REGRAS.md:** Violação de regras mandatórias (segurança, auth, dados, segredos, CSP) = aplicar patch corretivo imediato nos artefatos.
7. **Passes de Consistência:** Duplicação, ambiguidade de adjetivos, furos de aceite e inconsistências de termos = aplicar correção direta.

Para cada ajuste aplicado diretamente em `spec.md` ou `plan.md`, registre a entrada na seção **Achados e Resoluções** do `analyze.md`.
Gravidade: `CRITICAL` · `HIGH` · `MEDIUM` · `LOW`. IDs: `F1`, `F2`... na ordem da tabela.

## 4. Clarificações

Quando houver ambiguidade que não seja um erro óbvio e dependa de decisão humana:
- Pergunte diretamente no chat (Q + RECOMENDO), uma por vez.
- Aplique a resposta do usuário no arquivo correspondente (`spec.md` ou `plan.md`).
- Registre o resumo da pergunta e resposta na seção **Clarificações com o Usuário** do `analyze.md`.
- Não há limite arbitrário de perguntas; pergunte o que for estritamente necessário para eliminar ambiguidades.

## 5. Escrever e Salvar

Wip: `.vibeflow/analyze-wip.md`. Molde: `templates/analyze.md`. Status inicial: `rascunho`.
Não pergunte se pode salvar e não cole o corpo do documento no chat.

1. Preencha o wip certificando a cobertura, os achados corrigidos e a consistência final.
   Veredito: `limpo` quando todas as correções forem aplicadas e o plano estiver validado para execução; `bloqueado` apenas se restar conflito crítico não resolvido.
2. Execute o apply:
   - Modo phase:
     `pwsh "<skill>/scripts/analyze.ps1" -Apply`
     `bash "<skill>/scripts/analyze.sh" --apply`
   - Modo MVP:
     `pwsh "<skill>/scripts/analyze.ps1" -Apply -Mvp`
     `bash "<skill>/scripts/analyze.sh" --apply --mvp`
3. Responda no chat apenas:

```text
Analyze gravado: <created.path>/analyze.md

- Veredito: limpo | bloqueado
- Cobertura: <A*/C* com T* / total>
- Qualidade de testes: <smoke test na T1 e comandos de teste validados>
- Correções aplicadas: <F1... no spec.md / plan.md ou nenhuma necessária>
- Handoff: vibe-implement

Arquivo disponível em <created.path>/analyze.md. Responda "aprovado" para confirmar, "pode ir pro implement" (ou "pode ir para a próxima fase") para avançar imediatamente, ou indique os ajustes desejados.
```

## 6. Ajuste ou Aprovação

| Resposta | Ação |
|---|---|
| Aprovado (sem pedir implementação) | `# Status: aprovado` no vivo **apenas se** veredito `limpo`; parar e aguardar próximo comando |
| "Pode ir pro implement" / "pode ir para a próxima fase" / pede código | `# Status: aprovado` no vivo **apenas se** veredito `limpo`; iniciar imediatamente `vibe-implement` |
| Pedido de alteração | Patch direto no arquivo vivo; até 5 bullets no chat; solicitar nova conferência |
| "Parece bom" sem pedir implementação | Perguntar: "Aprovado no arquivo ou deseja algum ajuste?" |
| Veredito `bloqueado` e usuário pede implementação | Recusar. Exibir os achados bloqueantes pendentes |
| Spec, plan ou intenção quebrou | Devolver para a skill responsável. Não forçar implementação |

Rascunho sem "aprovado" e sem pedido da próxima porta não autoriza iniciar o código.

## 7. Fechar

Não commite no git. Não dispare a próxima skill a menos que o usuário tenha pedido explicitamente para avançar (§6).
Informe que os arquivos `analyze.md`, `plan.md` e `spec.md` atualizados entram no git e que `analyze-report.json` e `analyze-wip.md` ficam de fora.
Handoff registrado no arquivo: `vibe-implement`. Zero implementação nesta execução.
