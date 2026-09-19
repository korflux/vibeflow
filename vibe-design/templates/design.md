# Design: <frase curta>
# Alvo: <phase-<n>-<slug> ou mvp>
# Status: rascunho

<!-- Escreva diretamente neste artefato vivo; o status permanece rascunho durante a elaboração. -->

## Entrada

- Spec: <path da spec aprovada na mesma pasta>
- Interview: <path ou N/A com motivo>
- Modo: <com referência | greenfield>
- Referências de leitura: <DS em path, DESIGN.md em path, Figma como leitura, ou N/A com motivo>
- Uso: <criar | corrigir | analisar>

## Inventário de telas

<!-- Uma linha por tela da spec. Sem tela user-visible, registre N/A explícito e encerre aqui. -->

| Tela | Jornada F | Rota | Componentes candidatos | Origem |
|---|---|---|---|---|
| <nome> | <F da spec> | <rota ou N/A> | <blocos principais> | <reuso, adaptação ou kit novo com motivo> |

## Kit mínimo

<!-- Omitir quando houver DS aproveitável. Greenfield cria antes das telas. -->

- Cores: <papel e token, sem hex final quando a decisão for posterior>
- Tipografia: <papéis e escala>
- Espaçamento e raio: <escala e regra de uso>
- Componentes base: <botão, input, modal, toast, tabela e empty state>

## Tela: <nome>

<!-- Repita este bloco por tela do inventário. -->

- Hierarquia de cima para baixo: <zonas em ordem>
- Layout e grid: <colunas, alinhamento e ordem de leitura>
- Componente por zona: <zona mais componente permitido>
- Tokens: <cor, tipo, espaço e raio aplicados>
- Iconografia: <ícone por ação, texto obrigatório em ação ambígua>
- Responsivo: <viewport estreita, overflow, truncamento e quebra de texto>
- Estados: <vazio, loading, erro, sucesso e sem permissão>
- Prova visual esperada: <rota, viewport, estado, ações e evidência para a review>

## Tokens e iconografia

- Tokens por tela: <onde cada token vale>
- Regra de ícone: <icon-only só em ação universalmente reconhecível, com nome acessível, área de interação, foco visível e tooltip; ação ambígua mantém texto>

## Responsivo e estados

- Viewport estreita: <o que muda>
- Overflow e truncamento: <regra por zona>
- Estados globais: <loading, empty, error, success e sem permissão>

## Prova visual esperada

<!-- A review confere no navegador. Screenshot isolado não substitui a interação relevante. -->

- Rota, viewport, estado, ações e evidência por tela: <lista curta>
- Console, rede e assets sem erro: <como conferir>

## Decisões

| Decisão | Origem | Motivo e impacto |
|---|---|---|
| <reusado ou adaptado> | <DS, DESIGN.md, Figma ou kit novo> | <por que e o que determina> |

## Handoff

vibe-plan

- Chat: recomende novo chat para `vibe-plan`; continuidade no mesmo chat só por escolha consciente. O `design.md` vivo é a ponte. O artefato vivo entra no git; `design-report.json` fica de fora.

- [ ] Aprovação humana (leu o arquivo e confirmou)
