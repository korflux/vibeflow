# Kit, tokens e prova (design)

Leia este catálogo quando faltar forma de kit, superfície compartilhada, token, ícone, responsivo, estado ou prova. A referência da etapa design aponta para cá e não resume a tabela.

## Kit mínimo greenfield

| Peça | Conteúdo |
|---|---|
| Cores | Papéis de fundo, texto, borda e ação |
| Tipografia | Papéis de título, corpo e apoio |
| Espaçamento e raio | Escala e regra de uso por zona |
| Base | Botão, input, modal, toast, tabela e empty state |

Com DS existente, omita o kit e reuse os tokens do DS.

## Superfícies compartilhadas

Liste cada componente ou token comum que a entrega cria ou altera e todas as telas que o consomem, inclusive telas fora do inventário desta phase. Kit, tokens e componentes comuns precedem as telas que os consomem: o plan os entrega na primeira T* de tela consumidora, e as demais T* dessas telas dependem dela. A review reconfere cada tela afetada.

## Tokens por tela

Cada tela declara cor, tipo, espaço e raio aplicados por zona. Token novo só em greenfield ou com motivo registrado em Decisões. A spec não fecha token.

## Iconografia

Use icon-only somente em ação universalmente reconhecível, como lixeira para apagar. Todo icon-only mantém nome acessível, área de interação adequada, foco visível e tooltip quando aplicável. Ação ambígua mantém texto. O ícone não esconde confirmação, estado ou erro da ação.

## Responsivo e estados

Quando a tela tiver regra responsiva, declare o que muda por zona em viewport estreita, com regra de overflow, truncamento e quebra de texto. Sem regra responsiva, registre N/A com motivo. Cubra vazio, loading, erro, sucesso e sem permissão por tela. Overflow não intencional, clipping e texto ilegível são defeito.

## Prova visual esperada

A seção `Prova visual esperada` do `design.md` é a casa única da prova visual. Registre uma linha por tela com rota, viewport de julgamento do aceite, estado, ações e evidência observável. Inclua viewport estreita somente quando a tela tiver regra responsiva. Inclua console, rede e assets sem erro. O plan usa cada linha como insumo do `Visual:` e da `Prova afetada:` da T* que toca a tela e escolhe a ferramenta; a implement executa essa prova, e a review reconfere as telas tocadas e as Superfícies compartilhadas.
