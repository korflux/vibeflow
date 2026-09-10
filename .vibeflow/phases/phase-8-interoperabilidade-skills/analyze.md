# Analyze: interoperabilidade, escrita direta e isolamento de etapas
# Alvo: phase-8-interoperabilidade-skills
# Status: rascunho
# Plan: plan.md (mesma pasta)

## Fontes

| Arquivo | Estado |
|---|---|
| interview.md | ausente |
| spec.md | presente |
| plan.md | presente, aprovado pelo gate desta análise explícita |
| REGRAS.md | lido |

## Cobertura e Rastreabilidade

| Chave | Origem | T* | Notas |
|---|---|---|---|
| A1 | spec.md | T1, T7, T8 | Ponte Antigravity, documentação canônica e regressão final |
| A2 | spec.md | T2, T7, T8 | Manifest, instalação, paths por host e prova de distribuição |
| A3 | spec.md | T3, T4, T7, T8 | Escrita direta, preservação do vivo e remoção do contrato WIP |
| A4 | spec.md | T5, T7, T8 | Investigação por perguntas, evidências e fluxo real |
| A5 | spec.md | T5, T7, T8 | Handoff, novo chat recomendado e isolamento por T* |
| A6 | spec.md | T6, T7, T8 | Controles compactos com semântica e acessibilidade |
| A7 | spec.md | T6, T7, T8 | Seleção de ferramenta e prova visual renderizada |
| C1 | spec.md | T1, T8 | Fixture de init, reparo, conflito e fonte única |
| C2 | spec.md | T2, T8 | Manifest, sete pacotes, ponteiros e README |
| C3 | spec.md | T3, T4, T8 | Suítes, launchers, PowerShell e apply sem WIP |
| C4 | spec.md | T5, T7, T8 | Busca dirigida, remoção de contratos antigos e busca final ampliada |
| C5 | spec.md | T5, T7 | Contrato de investigação, escrita direta e isolamento documentado |
| C6 | spec.md | T6, T7, T8 | Checklist visual única nas referências existentes |
| C7 | spec.md | T6, T7, T8 | Ferramenta visual disponível, fallback explícito e limitação registrada |

## Achados e Resoluções

| ID | Categoria | Gravidade | Onde | Problema | Resolução Aplicada |
|---|---|---|---|---|---|
| F1 | decisao | CRITICAL | plan.md | `HOST-01`, `UI-01` e `QA-01` estavam na spec, mas nenhuma T* os vinculava no campo `Decisões:`. | IDs vinculados a T1/T2 (`HOST-01`) e T6 (`UI-01`, `QA-01`). |
| F2 | constituicao | CRITICAL | plan.md | T7 podia publicar `UI-01` na tabela de decisões vigentes antes de implementação, review aprovada e confirmação humana. | T7 agora atualiza o contrato geral e mantém o patch de `UI-01` explicitamente adiado; a orientação desta phase fica nas skills e referências. |
| F3 | inconsistencia | MEDIUM | plan.md | T8 afirmava que havia seis WIPs atuais, mas o inventário operacional encontrou somente `implement-wip.md`. | Aceite e descrição de T8 foram generalizados para os WIPs presentes no momento da execução. |
| F4 | qualidade_teste | HIGH | plan.md | A busca final de C4 não estava prevista como verificação própria em T8 e a busca de T7 não cobria `docs/tests`, onde o fluxo MVP ainda referencia WIP. | T8 recebeu um comando `rg` final cobrindo `.vibeflow`, documentação, testes operacionais, CI e os sete pacotes. |

### F1: decisões críticas sem rastreabilidade nas tasks

- **Gravidade:** CRITICAL
- **Categoria:** decisao
- **Onde:** `plan.md`
- **Evidência:** a spec declara `HOST-01`, `UI-01` e `QA-01`; o plan tinha `Spec:` em T1–T8, mas nenhum campo `Decisões:`.
- **Resolução:** `HOST-01` foi associado a T1 e T2; `UI-01` e `QA-01` foram associados a T6, que implementa essas escolhas.

### F2: publicação prematura de decisão vigente

- **Gravidade:** CRITICAL
- **Categoria:** constituicao
- **Onde:** `plan.md`
- **Evidência:** `REGRAS.md` determina que a tabela de decisões vigentes só muda após implementação, review aprovada e confirmação humana; T7 ocorreria antes dessas etapas.
- **Resolução:** T7 passou a proibir a publicação de `UI-01` na tabela vigente nesta etapa e a manter a decisão operacional nas skills e referências até o gate correto.

### F3: contagem de WIPs divergente do disco

- **Gravidade:** MEDIUM
- **Categoria:** inconsistencia
- **Onde:** `plan.md`
- **Evidência:** o inventário encontrou `implement-wip.md`; não encontrou os outros cinco nomes listados como WIPs atuais.
- **Resolução:** T8 agora remove todos os WIPs operacionais presentes, sem depender de uma contagem fixa e sem tocar reports ou phases históricas.

### F4: busca de contrato incompleta no fechamento

- **Gravidade:** HIGH
- **Categoria:** qualidade_teste
- **Onde:** `plan.md`
- **Evidência:** C4 exige busca canônica; a verificação de T7 omitia `docs/tests`, enquanto `docs/tests/test-mvp-flow.py` ainda usava `write_wip`.
- **Resolução:** T8 agora executa uma busca final explícita sobre `docs/tests`, CI, `.vibeflow`, documentação e pacotes ativos, depois das atualizações previstas para os testes.

## Decisões críticas

| ID | Interview | Spec | Plan | Estado |
|---|---|---|---|---|
| HOST-01 | ausente | adaptador mínimo por host, fonte única em `.vibeflow/REGRAS.md`, inspeção da carga efetiva | T1 e T2 | consistente |
| UI-01 | ausente | icon-only apenas para ação universalmente reconhecível, com semântica e acessibilidade | T6 | consistente |
| QA-01 | ausente | navegador integrado primeiro; Chrome DevTools MCP para inspeção; Playwright só se existente ou solicitado | T6 | consistente |

## Constituição

- Regra: a tabela de decisões vigentes em `REGRAS.md` só muda após implementação, review aprovada e confirmação humana. Resolução: T7 foi ajustada para não publicar `UI-01` antes desse momento.

## Métricas

- A*/C* na spec: 14, A1–A7 e C1–C7.
- T* no plan: 8, T1–T8.
- Cobertura (A*/C* com >= 1 T*): 14/14.
- Qualidade de Testes: T1 contém smoke test real (`python vibe-init/scripts/init.py --help`); cada T* possui comando executável; `gitleaks 8.30.1` e MCP Chrome DevTools estão disponíveis; o teste visual é criado em T6 antes de ser executado nos checkpoints finais.
- Achados corrigidos / resolvidos: F1, F2, F3 e F4.
- Achados bloqueantes pendentes: 0.

## Veredito

limpo

## Handoff

vibe-implement

Recomendação de chat: abrir novo chat para `vibe-implement` e usar um chat focado por T*.

- [ ] Aprovação humana (leu o arquivo e confirmou)
