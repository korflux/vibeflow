# Review: coordenação estratégica
# Alvo: phase-17-coordenacao-estrategica
# Status: request-changes

## Contexto

- Review independente delegada, sem participação na implementação e com escrita exclusiva deste arquivo.
- Cadeia: spec.md e plan.md aprovados, rota high, sem UI; analyze não exigido. Esta fase executa etapas-v1 para construir coordenacao-v1, sem migrar o próprio registro.
- Diff: `c535c3c1dac36f6c541af352cd948f7022ee3349..78c781567f01c2a82f51727766b5f14132717d1f`.
- Entrega: coordenador estratégico, colaboração dirigida, verificador independente e finalizador operacional; execução estruturada fora dos plans novos.

## Tipo de review

- Tipo: final, integração de T1 e T2.
- Fila: concluída na fonte etapas-v1; motor confirmou ambas as provas locais, integração atual e commit real `78c781567f01c2a82f51727766b5f14132717d1f`, sem avisos, antes da criação desta review.
- Provas reaproveitadas: 153 casos registrados no plan pelo verificador independente, incluindo Python/PowerShell, launcher, consumidores, distribuição, reparse e encoding; Gitleaks histórico e working tree verdes. O motor confirmou os inputs atuais do snapshot. Não foi repetida a matriz válida.
- Provas executadas: `pwsh -NoProfile -File vibe-implement/scripts/implement.ps1 -Dir phase-17-coordenacao-estrategica`, leitura verde, etapa revisar; `git diff --check c535c3c1dac36f6c541af352cd948f7022ee3349 78c781567f01c2a82f51727766b5f14132717d1f`, sem erros. Apply da review criou somente este arquivo no alvo explícito.
- Inspeção adicional: fluxo real dos motores execution Python/PowerShell, seleção do protocolo, snapshots, paths, operações, commit, testes de jornada, referências e consumidores. R1 foi demonstrado pela análise do fluxo; não se alega execução de uma fixture pós-correção nesta review.

## Cobertura da solicitação

- Origem suficiente: pedido humano transmitido no handoff, para deixar o coordenador mais leve, delegar conferência/operação e reduzir o bloco operacional do plan; aprovação explícita da proposta com acréscimo de colaboração inteligente entre subagentes. Spec registra essa origem em F1–F4. Nenhuma obrigação foi retirada.

| Item da solicitação e fonte | Implementação | Evidência | Situação |
|---|---|---|---|
| Coordenador estrategista, sem reconferência rotineira; proposta aprovada, A1 | vibe-implement/SKILL.md §2–3 e references/delegation.md transferem investigação, conferência e provas aos responsáveis | Ensaio comportamental independente: T1 base, T2 consumidora e integração falha têm responsáveis e handoffs definidos | atendido |
| Subagentes que trabalham em conjunto; complemento humano, A2 | referências de delegação, skill e template do plan delimitam interlocução direta, preparação conjunta e ownership | Ensaio cobre investigação de contrato compartilhado, reutilização de implementador e independência do verificador/revisor | atendido |
| Plan enxuto e retomada; proposta aprovada, A3 | template novo não contém snapshots; execution.json é mantido mecanicamente e detalhes são opt-in | Testes de ausência/init, retomada, corrupção, invalidação e leitura sem escrita; código inspecionado | atendido |
| Paridade e preservação de histórico, A4/C1 | motores Python/PowerShell selecionam protocolo explícito; etapas-v1 e B mantêm leitores anteriores | Suítes válidas e leitura da própria phase17 etapas-v1; fixtures testam CLI/disco, não presença de prosa | atendido |
| Validação independente, finalizador e fechamento completo após correções; proposta aprovada, A5/C2 | Papéis e confirmação estão definidos, mas o gate de commit do novo protocolo perde a conclusão após correção R* que modifica input | R1: commit original é comparado com blobs da prova renovada, enquanto commit R* não satisfaz o prefixo exigido | parcial |

## Checklist de correções

### Required

- [x] R1: **Required** - `vibe-implement/scripts/execution.py:151` e `:192`; `vibe-implement/scripts/execution.ps1:129` e `:159` - A revalidação após correção de review torna o commit integrado original inválido e impede voltar à review final. `commit_matches`/`Test-CoordinateCommit` compara os blobs do commit T* preservado com os inputs da integração atualizada. Se um input foi corrigido, os hashes necessariamente divergem. O commit `task(R1): ...` da correção também é recusado, pois a função exige o prefixo `task(T1,T2,...): `. Após fechar os R*, a projeção volta a `commitar_integracao`; a operação commit não encontra candidato válido, embora a correção esteja provada e commitada. Isso contradiz `references/execution.md:23`, que exige preservar commit/origem e manter a correção R* no Git/review. Remédio: vibe-implement deve separar a comprovação histórica do commit integrado da comprovação do estado corrigido, preservando origem, verificação dos blobs efetivamente commitados e detecção de alterações ainda não commitadas, sem exigir outro commit T* nem aceitar conclusão só pelo título. Prova exigida: jornada CLI/disco em ambos os motores com integração e commit T*, review Request changes, mudança real em input, renovação local/integrada independente, commit R*, fechamento do achado, retorno a revisar e depois confirmar; incluir controle negativo de correção verde ainda não commitada. Source: A3, A5, C2, F4 e contrato execution.md; gap: partial.

## Segurança

- A superfície alterada é CLI e arquivo operacional local: paths relativos validados por componente, links/reparse recusados, schema/campos/tipos limitados, gravação por temporário e substituição atômica. Comandos de evidência não são executados; Git recebe argumentos estruturados.
- Não foram identificados Critical na inspeção. Segredos foram cobertos pela prova Gitleaks válida do verificador. UI, banco e serviço web não fazem parte do diff.

## Notas

- O ensaio comportamental anterior certificou as instruções e os cenários solicitados, não o ciclo mecânico pós-correção agora identificado.
- Os testes existentes exercitam invalidação e preservação da origem, mas não completam a jornada integração → correção R* commitada → nova review.
- A frase final do plan sobre commit pendente é anterior à finalização; o motor e Git comprovaram o commit real. Não é bloqueio técnico.
- Não há novos IDs de decisões vigentes propostos na spec; nenhuma publicação em AGENTS.md foi feita ou autorizada por esta review.

## Veredito vigente

- [ ] **Approve**: pendente da correção de R1 e nova review.
- [x] **Request changes**: R1 Required aberto; cobertura de A5/C2 parcial.

## Handoff

vibe-implement: corrigir R1, renovar somente provas afetadas, registrar a correção conforme etapas-v1 desta phase e solicitar nova review independente.

- [ ] Aprovação humana (leu o arquivo e confirmou)
- Confirmação final, publicação de decisões e push continuam fechados. O revisor não opera índice, commits ou push e não altera spec/plan/AGENTS.

## Etapas

### Etapa 1 - first-pass - integração T1/T2 e contrato do novo protocolo

- Tipo: final.
- T* abertas: nenhuma; conclusão integrada comprovada antes desta review.
- Leu: origem humana do handoff, spec/plan, skills implement/review, referências de delegação/execução/histórico, motores e testes afetados, template do plan, contratos e diffs de consumidores/distribuição.
- Provas: reaproveitadas as provas integradas válidas; leitura do motor e diff-check executados conforme Tipo de review.
- Cobertura: origem suficiente; matriz acima registra A5/C2 parcial pelo ciclo pós-correção.
- Abriu: R1 Required.
- Fechou: nenhum.
- Critical encontrados: nenhum.
- Decisões vigentes propostas: nenhuma.
- Veredito desta etapa: Request changes.
