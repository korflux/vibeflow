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

## Superfícies compartilhadas

<!-- Uma linha por componente ou token comum novo ou alterado. Sem item comum, registre N/A com motivo. Ordem para o plan e reconferência na review em references/kit-e-tokens.md. -->

| Componente ou token | Novo ou alterado | Telas afetadas |
|---|---|---|
| <nome> | <novo, alterado ou reusado sem mudança> | <telas que consomem o item, dentro ou fora do inventário> |

## Tela: <nome>

<!-- Repita este bloco por tela do inventário. -->

- Hierarquia de cima para baixo: <zonas em ordem>
- Layout e grid: <colunas, alinhamento e ordem de leitura>
- Componente por zona: <zona mais componente permitido>
- Tokens: <cor, tipo, espaço e raio aplicados>
- Iconografia: <ícone por ação, texto obrigatório em ação ambígua>
- Motion: <frequência, propósito, easing, duração ou N/A com motivo, ver references/motion.md>
- Responsivo: <regra responsiva da tela ou N/A com motivo; overflow, truncamento e quebra de texto>
- Estados: <vazio, loading, erro, sucesso e sem permissão>

## Tokens e iconografia

- Tokens por tela: <onde cada token vale>
- Regra de ícone: <icon-only só em ação universalmente reconhecível, com nome acessível, área de interação, foco visível e tooltip; ação ambígua mantém texto>

## Responsivo e estados

- Viewport estreita: <o que muda, somente quando houver regra responsiva>
- Overflow e truncamento: <regra por zona>
- Estados globais: <loading, empty, error, success e sem permissão>

## Motion e baseline mobile

<!-- Opcional. Omitir somente sem motion nem alvo mobile. Campos não aplicáveis recebem N/A. Forma em references/motion.md. -->

- Motion por tela: <frequência, propósito, easing, duração ou N/A>
- Física: <scale, origin, preferência por transform e opacity, cor permitida, clip-path e filter só com necessidade, interrupção, stagger>
- Acessibilidade: <reduced motion suave, hover com media query, active para touch>
- Baseline mobile: <dvh ou svh, tap-highlight, touch-action, input 16px, overscroll quando app shell, safe-area, theme-color>

## Prova visual esperada

<!-- Uma linha por tela do inventário. Papel desta seção e consumo pelo plan em references/kit-e-tokens.md. Screenshot isolado não substitui a interação relevante. -->

| Tela | Rota | Viewport de julgamento | Viewport estreita | Estado e ações | Evidência observável |
|---|---|---|---|---|---|
| <nome> | <rota> | <largura em que o aceite é julgado> | <largura, somente com regra responsiva; senão N/A> | <estado exercitado e ações> | <o que deve aparecer renderizado> |

- Console, rede e assets sem erro: <como conferir>

## Decisões

| Decisão | Origem | Motivo e impacto |
|---|---|---|
| <reusado ou adaptado> | <DS, DESIGN.md, Figma ou kit novo> | <por que e o que determina> |

## Handoff

vibe-plan

- Chat: `interview`, `spec` e `design` podem continuar no mesmo chat. Recomende novo chat para `vibe-plan`; se o humano preferir, continuar aqui não bloqueia. O `design.md` vivo é a ponte e entra no git.

- [ ] Aprovação humana (leu o arquivo e confirmou)
