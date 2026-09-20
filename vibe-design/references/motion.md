# Motion, física e baseline mobile (design)

Leia este catálogo quando a tela tiver motion, gesto ou prova em celular. A skill aponta para cá, não resume a tabela no SKILL.

## Gate de frequência

| Frequência | Decisão |
|---|---|
| 100+ vezes por dia, ação de teclado, command palette | Sem animação |
| Dezenas por dia, hover, navegação de lista | Sutil e rápida, ou nada |
| Ocasional, modal, drawer, toast | Animação padrão |
| Rara ou primeira vez, onboarding, celebração | Pode ter delight |

## Propósito nomeado

Cada motion declara um propósito: feedback, consistência espacial, indicação de estado, evitar teleporte, explicação ou delight no tier raro. Sem propósito nomeado, não especifica motion.

## Easing e duração

| Situação | Easing |
|---|---|
| Entrada ou saída | ease-out |
| Movimento em tela | ease-in-out |
| Hover ou cor | ease |
| Movimento constante | linear |

Evite ease-in em UI; prefira ease-out, com exceção justificada em saída curta. Curvas fortes:

- `--ease-out: cubic-bezier(0.23, 1, 0.32, 1)`
- `--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1)`
- `--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1)`

| Elemento | Duração |
|---|---|
| Press de botão | 100 a 160ms |
| Tooltip, popover pequeno | 125 a 200ms |
| Dropdown, select | 150 a 250ms |
| Modal, drawer | 200 a 300ms como padrão, até 500ms em deslocamento maior com motivo |

UI frequente fica abaixo de 300ms. Drawer ou modal com maior deslocamento pode chegar a 500ms com motivo registrado. Marketing pode passar com motivo.

## Física e interrupção

- Nunca `scale(0)`. Entrada usa `scale(0.95)` mais `opacity: 0`.
- `transform-origin` no trigger para popover, dropdown, menu e tooltip. Modal fica centrado.
- Prefira `transform` e `opacity`. Cor é permitida para hover e feedback. `clip-path` e `filter` só com necessidade e prova de desempenho. Largura, altura, margem e padding não animam.
- Transição para elemento disparável em sequência. Keyframe só para motion predeterminada. Spring só para gesto arrastável com momentum.
- Entrada e saída pelo mesmo caminho. Timing assimétrico: fase deliberada lenta, resposta do sistema rápida.
- Stagger de 30 a 80ms entre itens. Blur sutil para mascarar crossfade imperfeito.

## Acessibilidade

- Com `prefers-reduced-motion`, remova motion não essencial e mantenha feedback de estado imediato. Fade e cor curtos são opcionais, não obrigação. Ação frequente continua instantânea.
- Hover só em `@media (hover: hover) and (pointer: fine)`. Press usa `:active` para touch.

## Baseline mobile

| Sinal | Regra |
|---|---|
| Shell do app, drawer | `100dvh` |
| Hero, primeira dobra | `100svh` |
| Flash cinza no tap | `-webkit-tap-highlight-color: transparent` mais `:active` próprio |
| Tap com atraso | `touch-action: manipulation` em botão e link |
| Zoom no input iOS | input com 16px mínimo |
| Scroll puxa a página | Em app shell com gesto próprio use `overscroll-behavior: none` na raiz; em página de conteúdo preserve o scroll nativo. Em lista interna use `contain` |
| Notch e home indicator | `viewport-fit=cover` mais `env(safe-area-inset-*)` |
| Status bar | `theme-color` por esquema claro e escuro |
| Texto de controle selecionável | `user-select: none` só em controle, nunca no body |

## Prova

Em gesto ou mobile com risco, revisar com fresh eyes, em câmera lenta de 2 a 5x, frame a frame no inspector, e gesto em hardware real. Para ajuste simples de desktop sem gesto, basta prova direta. Emulação não reproduz hover preso, tap delay, `dvh`, zoom de input, overscroll ou safe area.
