# Spec: <frase curta>
# Alvo: <phase-<n>-<slug> ou mvp>
# Status: rascunho

<!-- Escreva diretamente neste artefato vivo; o status permanece rascunho durante a elaboração. -->

## Objetivo

<quem opera, o que esta entrega resolve, o que sucesso parece — 2–4 frases>

## Cobertura da origem

<!-- Com interview: uma linha por jornada, página ou módulo aplicável; agrupe itens com o mesmo destino. Sem interview: liste somente partes da entrega que poderiam ficar esquecidas. Não copie a entrevista. -->

| Origem | Destino na spec | Motivo se fora/N/A |
|---|---|---|
| <jornada, página ou módulo> | <F* / decisão / Fora / N/A> | <motivo ou N/A> |

## Suposições e decisões

1. … — (produto / segurança / processo / escopo; já fechado)

## Decisões críticas

<!-- Omitir fora do MVP e quando a phase não cria nem substitui decisão crítica. -->

| ID | Ação | Decisão | Motivo e impacto | Fonte anterior |
|---|---|---|---|---|
| <DOMINIO-01> | <mantém, cria ou substitui> | <opção fechada> | <por que e o que determina> | <interview MVP ou decisão vigente; N/A se cria> |

## Escopo e comportamento

### 1. Fluxo F*:<nome>

<!-- Obrigatório quando houver fluxo ou UX. Passo sem superfície é defeito. Escolha tela, popup, drawer, inline, redirect ou toast. Em página informativa simples, use F* curto e N/A fundamentado para regras inexistentes. Sem UI, use N/A explícito. -->

- Jornada: <jornada da interview ou N/A com motivo>
- Rota: <rota da cadeia ou N/A>
- Gatilho: <o que inicia>
- Pré-condição: <estado exigido antes do passo 1>
- Superfície por passo: <tela, popup, drawer, inline, redirect ou toast por passo>
- Passos:
  1. <ação> -> <resposta> [superfície: <uma das seis>]
- Validações: <regra por passo>
- Erros: <CÓDIGO> (<mensagem segura e causa>)
- Estados: <vazio, loading, erro, sucesso, sem permissão>
- Aceite: <A* observável>
- Reutilizar: <seção atual, helper ou contrato existente>

<!-- Repita o bloco F* por fluxo. Área genérica sem F* só quando a entrega não tem fluxo nem UX. -->

### Fora

- <recusa real e tentadora> — <motivo em 1 linha>

## Direção visual

<!-- omitir se a entrega não for user-visible. Spec fecha comportamento e superfície, nunca hex ou token, token pertence à design. -->

- Modo: reuso DS em `…` | greenfield | redesign de …
- Tom: …
- Evitar: …
- Copy de UI: … (N/A se não importar)
- Prova: E2E + screenshot de …

## Checklist de entrega

### Aceite

- [ ] A1: <outcome observável>

### Critérios de sucesso

- [ ] C1: <pronto testável, não adjetivo>

## Contratos e restrições necessárias

<!-- Omitir quando não houver contrato técnico que altere comportamento, segurança ou integração. Não listar arquivos, tarefas, comandos ou escolhas internas reversíveis; isso pertence ao plan. -->

- Dados e invariantes: <o que precisa permanecer verdadeiro ou N/A>
- Integrações e interfaces: <entradas, saídas e falhas necessárias ou N/A>
- Segurança e operação: <para entradas externas, campos e valores aceitos por allowlist e tamanho máximo; para acesso cross-origin, allowlist de origens CORS; outros controles aplicáveis ou N/A fundamentado>
- Tecnologia imposta: <restrição existente e motivo ou N/A>

<!-- Para entradas externas, declarar allowlist de campos/valores e tamanho máximo por entrada. Com API, handle, segredo, dado pessoal ou rota autenticada, fechar os demais controles aplicáveis. Se houver acesso browser cross-origin, declarar a allowlist de origens CORS e nunca combinar * com credenciais; sem necessidade, justificar N/A. Fato novo em mock que é contrato exige nome, forma, janela e escopo ou delegação ao design com Ask first. -->

## Como provar

<!-- Uma evidência observável por A*. O plan escolhe ferramentas, comandos e ordem de execução. -->

| Aceite | Evidência esperada |
|---|---|
| A1 | <o que observar e onde> |

## Boundaries

### Always

- …

### Ask first

- …

### Never

- …

## Handoff

<!-- Com UI visível: vibe-design. Sem UI visível: vibe-plan. Não pular design em silêncio. Plan existente bloqueia nova escrita, pedido novo exige outra phase. -->

vibe-design com UI visível, senão vibe-plan
<!-- No MVP, acrescentar: rota: max -->

- Chat: `interview`, `spec` e, com UI, `design` podem continuar no mesmo chat. Recomende novo chat para `vibe-plan`; se o humano preferir, continuar no mesmo chat não bloqueia. O `spec.md` vivo é a ponte.

- [ ] Aprovação humana (leu o arquivo e confirmou)
