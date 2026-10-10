# Review: <frase curta>
# Alvo: <phase-<n>-<slug> ou mvp>
# Status: rascunho

<!-- Escreva diretamente neste artefato vivo; o status permanece rascunho até o veredito e a confirmação humana. -->

## Contexto

- Alvo: <fase | branch | PR | local>
- Cadeia: interview? / spec.md / plan.md / analyze.md
- O que muda: <1-3 frases>

## Tipo de review

- Tipo: <checkpoint | final>
- Marco e justificativa: <referência exata ao plan.md | integração final>
- T* abertas fora do marco: <IDs ou nenhuma>
- Provas reaproveitadas: <T* e resultado | nenhuma>
- Provas executadas: <comando, motivo e resultado | nenhuma>

## Cobertura da solicitação

<!-- Obrigatória. Comece pela solicitação original e alterações humanas; ausência no plan não retira obrigação. No checkpoint indique o limite do marco. Declare aqui limites de origem/contexto, sem certificar completude quando faltarem. -->

- Origem e limites: <fontes disponíveis e limites de cobertura | origem completa>

| Item da solicitação e fonte (A*/C* quando houver) | Implementação | Evidência | Situação |
|---|---|---|---|
| <obrigação e fonte verificável> | <path e comportamento, ou ausente> | <comando/resultado ou decisão humana com fonte> | <atendido / parcial / ausente / retirado explicitamente pelo humano> |

## Checklist de correções

<!-- Só Critical e Required bloqueiam. Implement marca [x] no vivo. -->
<!-- Sem bloqueio: uma linha "nenhum bloqueio" e omitir as listas vazias. -->
<!-- Achado novo em etapa posterior: próximo número livre. Não renumerar fechados. -->

### Critical

- [ ] R1: **Critical** - `path` - <o que está errado> - remédio: <movimento> - prova: <comando> - source: <solicitação|decisão humana|A*|C*|diff|plan.md> - gap: <missing|partial|contradicts|nenhum>

### Required

- [ ] R2: **Required** - `path` - <...> - remédio: ... - prova: ...

### Optional / Nit

<!-- omitir se vazio -->

- [ ] R3: **Nit** - ...

## Visual

<!-- omitir se não há prova renderizada necessária; reaproveitar a evidência válida registrada no plan -->

- Browser: <DevTools | E2E do repo>
- Screenshot: <path> - leitura: <ok | falhas>

## Segurança

<!-- omitir se o diff não toca input, auth, segredo, upload, pagamento, LLM ou dado pessoal -->
<!-- ref: references/security-and-hardening.md. Sem catálogo fixo. -->

- <achado ou "nada no que o diff tocou">

## DoD

<!-- omitir se tudo N/A -->

- [ ] <item aplicável>

## Notas

<!-- omitir se vazio; teto 5 linhas -->

## Veredito vigente

<!-- Defer somente para Nit/Optional/FYI. Critical/Required aberto, obrigação parcial/ausente ou origem insuficiente bloqueiam qualquer Approve. -->
<!-- Preencher somente na review final. Checkpoint registra o resultado do marco em Etapas e nunca aprova nem conclui a phase. -->

- [ ] **Approve**: origem suficiente, obrigações atendidas ou retiradas explicitamente pelo humano e nenhum Critical/Required em `[ ]`
- [ ] **Request changes**: há Critical/Required em `[ ]`
- [ ] **Approve com defer**: <R* Nit/Optional/FYI; fonte/path; motivo; encaminhamento e condição ou momento de retomada>

## Decisões para vigência

<!-- Omitir em checkpoint e quando a entrega não cria nem substitui decisão crítica. Esta tabela só é proposta na review final e continua sujeita à aprovação humana. -->

| ID | Ação | Decisão aprovada | Fonte da decisão | Evidência de implementação |
|---|---|---|---|---|
| <DOMINIO-01> | <cria ou substitui> | <decisão compacta> | <spec.md ID> | <plan.md T* e prova> |

## Handoff

vibe-implement | finalização Git da phase

<!-- ou: volta vibe-spec | cadeia fechada -->

<!-- Aprovação humana só se aplica à review final, depois do Approve e da fila concluída. -->
- [ ] Aprovação humana (leu o arquivo e confirmou)

- Chat: recomende iniciar esta review em chat novo, separado da implementação; no Modo A do `vibe-implement`, ela roda em subagente de contexto limpo, a pedido do coordenador. Para correções `vibe-implement`, recomende outro chat ou, no Modo A, um subagente corretor; se o humano preferir continuar aqui, siga sem bloquear. Após Approve e confirmação humana, o handoff é a finalização Git da phase. O `review.md` vivo e o diff são a ponte.

## Finalização Git da phase

<!-- Omitir em checkpoint. Só a review final, com fila concluída e aprovação humana, abre este gate. -->

- Pré-condições: Approve final confirmado, todas as `T*` concluídas, Critical/Required fechados, prova necessária da integração verde, `git diff --check` e gitleaks quando previsto.
- Commit final: `chore(phase-N): finalize review`, somente com paths residuais autorizados e sem `Co-Authored-By`; sem mudanças residuais, manter o último commit integrado ou da task.
- Push: `git push` para o upstream atual, sem `--force`. Registrar hash/HEAD, paths e resultado; falha mantém o handoff bloqueado.

## Etapas

### Etapa 1 - first-pass - <o que olhou: T* / diff / provas>

- Tipo: <checkpoint | final>
- Marco e justificativa: <referência ao plan.md | integração final>
- T* abertas fora do marco: <IDs ou nenhuma>
- Provas reaproveitadas: <IDs e resultado | nenhuma>
- Provas executadas: <comando, motivo e resultado | nenhuma>
- Leu: <solicitação original, alterações humanas e artefatos consultados>
- Cobertura: <mudanças na matriz e limite do marco | conferida sem mudança>
- Abriu: R1, R2 (ou nenhum)
- Fechou: nenhum
- Veredito desta etapa: Marco aprovado | Request changes | Approve final | Approve com defer
- Defer: <R* Nit/Optional/FYI; fonte/path; motivo; encaminhamento e retomada | omitir sem defer>

<!-- etapa seguinte: copie ### Etapa N abaixo. Não apague as anteriores. -->
