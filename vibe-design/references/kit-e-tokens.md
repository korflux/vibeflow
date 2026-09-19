# Kit, tokens e prova (design)

Leia este catálogo quando faltar forma de kit, token, ícone, responsivo, estado ou prova. A skill aponta para cá, não resume a tabela no SKILL.

## Kit mínimo greenfield

| Peça | Conteúdo |
|---|---|
| Cores | Papéis de fundo, texto, borda e ação |
| Tipografia | Papéis de título, corpo e apoio |
| Espaçamento e raio | Escala e regra de uso por zona |
| Base | Botão, input, modal, toast, tabela e empty state |

Com DS existente, omita o kit e reuse os tokens do DS.

## Tokens por tela

Cada tela declara cor, tipo, espaço e raio aplicados por zona. Token novo só em greenfield ou com motivo registrado em Decisões. A spec não fecha token.

## Iconografia

Use icon-only somente em ação universalmente reconhecível, como lixeira para apagar. Todo icon-only mantém nome acessível, área de interação adequada, foco visível e tooltip quando aplicável. Ação ambígua mantém texto. O ícone não esconde confirmação, estado ou erro da ação.

## Responsivo e estados

Em viewport estreita, declare o que muda por zona, com regra de overflow, truncamento e quebra de texto. Cubra vazio, loading, erro, sucesso e sem permissão por tela. Overflow não intencional, clipping e texto ilegível são defeito.

## Prova visual esperada

Registre por tela rota, viewport normal e estreita, estado, ações e evidência observada. Inclua console, rede e assets sem erro. A review confere no navegador com a seleção da implement, sem instalar ferramenta automaticamente.
