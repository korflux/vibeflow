# Implementador

Única leitura do implementador num passo, numa entrega low ou medium e numa correção devolvida pelo checkpoint ou pela review. As seções de outras referências que este arquivo aponta são abertas só quando o trabalho chega a elas.

## Recorte

- Escreva só nos `Arquivos:` do passo, no recorte do brief ou nos paths do R*. Path fora do recorte volta ao líder antes de editar.
- Credencial, conta, pagamento, elevação administrativa ou integração persistente são impedimentos reais: relate a tentativa, o impedimento e a recomendação. Ferramenta ausente segue a regra de instalação de `references/delegation.md` (Pedido autocontido).

## Antes de editar

1. Confirme o mapa do brief (consumidores, testes afetados e padrão a seguir) abrindo os paths que ele cita, sem reexplorar a árvore. Mapa que não bate com o código: leia só o necessário para corrigi-lo e relate a divergência em `pendencias`; se a correção exige path fora do recorte, volte ao líder.
2. Abra os itens de `## Núcleo do projeto` que o brief cita, sem resumo e inclusive as imagens, e trabalhe sobre essa referência.

## Codar

- Reutilize o que existe no projeto, na standard library, na plataforma e nas dependências instaladas. Sem abstração especulativa nem limpeza fora do recorte.
- Documente semanticamente responsabilidades e decisões não óbvias.
- Barra de acabamento em `references/definition-of-done.md`; banco ou dinheiro exige `references/database-and-migrations.md`.

## Testes e prova

- Escreva os testes conforme `references/testes.md`, Política de testes e Desenho de casos.
- Rode a `Prova:` do passo, os testes afetados da correção ou, em low ou medium, a prova do brief, conforme `references/testes.md` (Política de testes), com saída resumida: reporter de resumo ou filtro que mostre só falhas e totais, sem log completo.
- Prova vermelha: corrija pela causa raiz e rode de novo, até verde ou impedimento real.

## Captura

Critério com tela: capture uma vez por critério, ao fechar o passo, conforme `references/chrome-devtools.md` (Captura e reaproveitamento).

## Relatório

Devolva o relatório fixo de `references/delegation.md` (Relatório fixo).
