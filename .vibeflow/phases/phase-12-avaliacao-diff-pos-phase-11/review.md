# Review: mudanças após a phase 11
# Alvo: phase-12-avaliacao-diff-pos-phase-11
# Status: rascunho

## Contexto

- Alvo: diff `a9df01c..a19ae2a`, três commits, 37 arquivos.
- Cadeia: revisão avulsa do diff, sem `interview.md`, `spec.md` ou `plan.md` próprios.
- O que muda: descoberta de MVP, cobertura da origem na spec, prova proporcional, suporte de instalação a OpenCode/Pi e ajustes de portabilidade nos testes.

## Tipo de review

- Tipo: final, revisão informativa do diff; não encerra outra phase.
- Marco e justificativa: todos os arquivos do diff foram inspecionados; o escopo é documental e de testes, sem alteração dos motores de execução das skills.
- T* abertas fora do escopo: T1 da phase 9 permanece desmarcada; não pertence a este diff.
- Provas reaproveitadas: nenhuma prova da phase 11 cobre estas alterações posteriores.
- Provas executadas: `git diff --check a9df01c..a19ae2a` → OK.
- Provas não executadas: suítes de contrato e CI; esta avaliação foi estática.

## Checklist de correções

### Critical

Nenhum.

### Required

Nenhum.

### Optional / Nit

- [x] R1: **Nit** - `vibe-spec/SKILL.md:83` - Resolvido em 2026-09-23: a skill, o template de spec e a arquitetura agora explicitam allowlist e tamanho máximo para entradas externas, além de allowlist de origens CORS quando houver acesso entre origens. Prova: `git diff --check` no patch e conferência dos três contratos.
- [x] R2: **Nit** - `docs/vibe-interview/tests/test-interview.py:216` - Resolvido em 2026-09-23: a suíte extrai os caminhos `modules/*.md` do roteador e falha se algum arquivo não existir. Prova: `python docs/vibe-interview/tests/test-interview.py` → 25 testes OK; os sete destinos atuais existem.

## Notas

- Avaliação: melhor no geral. A entrevista começa pelo produto e suas jornadas, a spec rastreia a origem, e as decisões internas e comandos ficam no plan. A prova pode ser reutilizada por capacidade, com ressalvas explícitas para borda, erro, permissão, integração e edição posterior.
- Trade-off: os módulos seguem condicionais para reduzir perguntas desnecessárias. Gatilhos explícitos agora abrem privacidade para dados pessoais/sensíveis, monitoramento ou compartilhamento, e requisitos legais para setor regulado ou jornadas com obrigação concreta. Os demais domínios ainda dependem do contexto da jornada.
- Segurança: a lacuna registrada em R1 foi corrigida na skill, no template da spec e na arquitetura, mantendo allowlist e tamanho máximo junto da regra de CORS por origem.
- Testes: as asserções do template seguem cobrindo sua estrutura; um contrato adicional valida os caminhos dos módulos citados e os gatilhos de privacidade/jurídico. Nenhum caminho quebrado foi encontrado.
- Portabilidade: o uso de `Path.GetTempPath()` e o PATH restrito do fallback PowerShell são correções coerentes; não executei essas suítes nesta revisão.
- Distribuição: README agora documenta OpenCode e Pi via `~/.agents/skills/`; isso corresponde aos locais de descoberta documentados oficialmente pelo [OpenCode](https://opencode.ai/docs/skills) e pelo [Pi](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md).
- Conclusão: não encontrei regressão bloqueante no diff. Recomendo manter as mudanças e observar se os módulos condicionais deixam algum requisito de privacidade/operação escapar em entrevistas reais.

## Veredito vigente

- [ ] **Approve**: recomendação favorável para o diff; aguarda confirmação humana.
- [ ] **Request changes**: nenhum bloqueio identificado.

## Handoff

Sem handoff de implementação; esta revisão não aprova nem publica a phase.

## Etapas

### Etapa 1 - diff completo - commits `6eb9fea`, `96ac6e1` e `a19ae2a`

- Tipo: final, avulsa.
- Marco e justificativa: comparação do estado anterior e posterior aos três commits.
- T* abertas fora do escopo: phase 9, T1.
- Provas reaproveitadas: nenhuma.
- Provas executadas: `git diff --check a9df01c..a19ae2a` → OK; não executei suítes.
- Leu: `plan.md` e `spec.md` não disponíveis para este diff.
- Abriu: nenhum R* bloqueante.
- Fechou: nenhum.
- Veredito desta etapa: recomendação favorável, sem fechamento de phase.
