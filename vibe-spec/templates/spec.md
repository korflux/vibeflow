# Spec: <frase curta>
# Alvo: <phase-<n>-<slug> ou mvp>
# Status: rascunho

<!-- Escreva diretamente neste artefato vivo; o status permanece rascunho durante a elaboração. -->

## Objetivo

<quem opera, o que esta entrega resolve, o que sucesso parece — 2–4 frases>

## Inventário

<!-- omitir se a entrega for unitária sem lista -->

1. …

## Suposições e decisões

1. … — (produto / segurança / processo / escopo; já fechado)

## Decisões críticas

<!-- Omitir fora do MVP e quando a phase não cria nem substitui decisão crítica. -->

| ID | Ação | Decisão | Motivo e impacto | Fonte anterior |
|---|---|---|---|---|
| <DOMINIO-01> | <mantém, cria ou substitui> | <opção fechada> | <por que e o que determina> | <interview MVP ou decisão vigente; N/A se cria> |

## Escopo e comportamento

### 1. Fluxo F*:<nome>

<!-- Obrigatório quando a rota tem spec. Passo sem superfície é defeito. Superfície por passo é exatamente uma de tela, popup, drawer, inline, redirect ou toast. Use N/A explícito sem UI. -->

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

## Implementação

### Stack

<!-- omitir se zero decisão -->

| Área | Escolha |
|---|---|
| … | existente: … / delta: … |
| Dependências novas | Nenhuma / <nome + por quê topado> |

### Estrutura tocada

<!-- omitir se irrelevante; só paths da fatia -->

```text
path/arquivo    # papel na entrega
```

### Estilo e padrões

<!-- só o que esta entrega deve obedecer -->

- reutilizar: …

### Contratos e módulos

- limites: …
- API / schema / eventos fechados: …
- Catálogo de erros na borda: CODE_EXEMPLO (status HTTP/CLI, mensagem segura e causa)

## Como provar

### Seams

- …

### Estratégia

- Unitário / componente: …
- E2E / integração: …
- Manual: …

### Comandos

```bash
# só comandos que existem no repo ou foram acordados
```

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

- Chat: recomende novo chat para `vibe-design` com UI visível, senão `vibe-plan`; continuidade no mesmo chat só por escolha consciente. O `spec.md` vivo é a ponte.

- [ ] Aprovação humana (leu o arquivo e confirmou)
