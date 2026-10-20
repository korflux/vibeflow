# Review: <frase curta>
# Alvo: <phase-<n>-<slug> ou mvp>
# Status: rascunho
# Rota: <medium | high | xhigh | max | mvp>
<!-- Linha só quando este é o primeiro artefato da phase: rota medium. Nos demais casos, apague a linha. -->

<!-- Escreva diretamente neste artefato vivo; o status permanece rascunho até o veredito e a confirmação humana. -->

## Contexto

- Alvo: <fase | branch | PR | local>
- Cadeia: interview? / spec.md / plan.md / analyze.md
- O que muda: <1-3 frases>
- Base medium: <commit `task(medium): ...` da entrega; omitir fora do medium>

## Cobertura da solicitação

<!-- Obrigatória. Comece pela solicitação original e alterações humanas; ausência no plan não retira obrigação. Declare aqui limites de origem/contexto, sem certificar completude quando faltarem. -->

- Origem e limites: <fontes disponíveis e limites de cobertura | origem completa>

| Item da solicitação e fonte (A*/C* quando houver) | Implementação | Evidência | Situação |
|---|---|---|---|
| <obrigação e fonte verificável> | <path e comportamento, ou ausente> | <comando/resultado ou decisão humana com fonte> | <atendido / parcial / ausente / retirado explicitamente pelo humano> |

## Checklist de correções

<!-- Todo R* aberto bloqueia, inclusive nit. O finalizador marca [x] somente após prova certificada. -->
<!-- R* cujo remédio altera Arquivos: da phase termina com papel: redator (só prosa desses paths) ou papel: corretor; remédio de prosa em plan, spec ou AGENTS.md também leva papel: redator; o finalizador só marca. -->
<!-- Sem bloqueio: uma linha "nenhum bloqueio" e omitir as listas vazias. -->
<!-- Achado novo em etapa posterior: próximo número livre. Não renumerar fechados. -->

### Critical

- [ ] R1: **Critical** - `path` - <o que está errado> - remédio: <movimento> - prova: <comando> - source: <solicitação|decisão humana|A*|C*|diff|plan.md> - gap: <missing|partial|contradicts|nenhum> - papel: <corretor|redator>

### Required

- [ ] R2: **Required** - `path` - <...> - remédio: ... - prova: ... - papel: <corretor|redator>

### Nit

<!-- omitir se vazio -->

- [ ] R3: **Nit** - `path` - <problema fundamentado> - remédio: <movimento> - prova: <checagem> - papel: <corretor|redator>

## Visual

<!-- omitir se não há prova renderizada necessária; reaproveitar a evidência válida (`references/chrome-devtools.md`, Captura e reaproveitamento) -->

- Browser: <DevTools | E2E do repo>
- Screenshot: <path> - leitura: <ok | falhas>

## Segurança

<!-- omitir se o diff não toca input, auth, segredo, upload, pagamento, LLM ou dado pessoal -->
<!-- ref: references/review/security-and-hardening.md. Sem catálogo fixo. -->

- <achado ou "nada no que o diff tocou">

## DoD

<!-- omitir se tudo N/A -->

- [ ] <item aplicável>

## Notas

<!-- omitir se vazio; teto 5 linhas. Informações sem correção ficam aqui, sem R*. -->

## Veredito vigente

<!-- Todo R* aberto, obrigação parcial/ausente ou origem insuficiente bloqueia Approve. Preserve o histórico. -->

- [ ] **Approve**: origem suficiente, obrigações atendidas ou retiradas explicitamente pelo humano e nenhum R* de correção em `[ ]`
- [ ] **Request changes**: há R* de correção em `[ ]`

## Decisões para vigência

<!-- Omitir quando a entrega não cria nem substitui decisão crítica. Esta tabela é proposta e continua sujeita à aprovação humana. -->

| ID | Ação | Decisão aprovada | Fonte da decisão | Evidência de implementação |
|---|---|---|---|---|
| <DOMINIO-01> | <cria ou substitui> | <decisão compacta> | <spec.md ID> | <plan.md T* e prova> |

## Handoff

implement | finalização Git da phase

<!-- ou: volta spec | cadeia fechada -->

<!-- Aprovação humana só depois do Approve e da fila concluída. -->
- [ ] Aprovação humana (leu o arquivo e confirmou)

- Chat: no Modo A, esta review roda em revisor de contexto limpo, a pedido do líder; sem subagentes, roda num chat novo com `/vibeflow review`. As correções seguem pela etapa implement, com corretor ou redator conforme o `papel` de cada R*; sem subagentes, num chat novo com `/vibeflow implement`. Após Approve e confirmação humana, o handoff é a finalização Git da phase. O `review.md` vivo e o diff são a ponte.

## Finalização Git da phase

<!-- Só a fila concluída e a aprovação humana abrem este gate. -->

- Pré-condições: Approve final confirmado, todas as `T*` concluídas (no medium, o commit `task(medium): ...`), todos os R* de correção fechados, prova necessária da integração verde, `git diff --check` e gitleaks quando previsto.
- Commit final: `chore(<alvo>): finalize review`, somente com paths residuais autorizados; sem mudanças residuais, manter o último commit integrado ou da task.
- Push: `git push` para o upstream atual, sem `--force`. Registrar hash/HEAD, paths e resultado; falha mantém o handoff bloqueado.
<!-- Somente quando o humano recusar ou adiar o push, o finalizador acrescenta: - Push adiado pelo humano: <AAAA-MM-DD> -->

## Etapas

### Etapa 1 - first-pass - <o que olhou: T* / diff / provas>

- Provas reaproveitadas: <IDs e resultado | nenhuma>
- Provas executadas: <comando, motivo e resultado; na regressão completa, também HEAD | nenhuma>
- Execução: <diff na união dos Arquivos:, consumidores compartilhados, commits task(<alvo>:...) por T* e, na re-review, commit task(<alvo>:Rn,...) e IDs>
- Leu: <solicitação original, alterações humanas e artefatos consultados>
- Cobertura: <mudanças na matriz | conferida sem mudança>
- Abriu: R1, R2 (ou nenhum)
- Fechou: nenhum
- Veredito desta etapa: Request changes | Approve final

<!-- etapa seguinte: copie ### Etapa N abaixo. Não apague as anteriores. -->
<!-- Ajuste de phase fechada: o líder acrescenta ### Ajuste N - <pedido> com Pedido (texto do humano ou path do registro) e Abriu: Rn; os R* vão na Checklist de correções (references/implement.md, Ajuste de phase). -->
