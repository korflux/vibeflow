# Qualidade Visual e Interface

Abra esta referência quando o diff alterar elementos visuais, layouts, componentes de UI ou fluxos web vistos no navegador. Julgue o estado renderizado com evidência factual. Toda anomalia real vira `R*` `Required`; preferência estética sem exigência da spec não bloqueia.

## Ferramenta e evidência

Use a seleção definida em `vibe-implement/references/chrome-devtools.md`: navegador integrado (`@Browser` ou equivalente) primeiro quando disponível, MCP Server `chrome-devtools` para snapshot, screenshot, DOM, estilos, console, rede e assets, e Playwright somente se já existir no repositório ou for solicitado para fluxos repetíveis e assertions. Sem capacidade visual, registre `R*` `Required`; não aprove silenciosamente e não instale ferramenta automaticamente.

Em toda prova, registre rota, viewport, estado, ações e evidência observada. Screenshot isolado não substitui a inspeção da interação relevante.

## Checklist única de auditoria renderizada

| Área | Conferir |
|---|---|
| Viewport e geometria | overflow horizontal ou vertical inesperado, conteúdo fora da viewport, clipping, sobreposição ou cobertura e z-index de modal ou sticky |
| Texto e proporção | truncamento, quebra de texto e proporção de largura dos containers |
| Controles e composição | controles maiores que o necessário e input com ícone na mesma linha quando houver espaço |
| Responsividade | comportamento em viewport estreita |
| Estados | loading, empty, error e success |
| Acessibilidade | nome acessível, foco visível, teclado e contraste |
| Runtime | erros de console, rede e carregamento de assets |

## Controles compactos e semânticos

- Use `icon-only` somente para ações universalmente reconhecíveis, como o ícone de lixeira para apagar.
- Todo controle `icon-only` mantém nome acessível programático, área de interação adequada, foco visível e tooltip quando aplicável.
- Mantenha texto em ações ambíguas, compostas ou que dependam de contexto para evitar erro de uso. Não transforme uma ação ambígua em `icon-only` só para reduzir largura.
- O ícone não pode esconder confirmação, feedback, estado de carregamento, erro ou permissão da ação.

## Barra de aprovação

Interface sem rota, viewport, estado e evidência observada não está provada. Interface com elemento coberto, overflow não intencional, clipping, texto ilegível, foco ausente ou erro de console/rede/assets recebe `R*` `Required`, com remédio apontando para `vibe-implement`.
