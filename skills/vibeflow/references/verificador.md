# Verificador

Única leitura do verificador, que atua só no checkpoint do plan. As seções de outras referências que este arquivo aponta são abertas só quando o trabalho chega a elas.

## Checkpoint

Trabalhe com contexto limpo, sobre o diff do grupo e os critérios do checkpoint que o brief entrega.

1. Não rerode a prova dos passos: ela já voltou verde.
2. Rode o E2E só dos critérios listados que têm tela, conforme `references/testes.md` (Política de testes e Desenho do E2E).
3. Confira o diff do grupo contra os critérios listados na spec.
4. Relate cada critério com comando ou trecho do diff, resultado e evidência. Falha é relatada, não corrigida; o líder a devolve ao implementador do passo que a causou.

Flake (teste que falha e passa na reexecução) e achado fora do recorte não bloqueiam: grave cada um em `.erros-encontrados/`, um arquivo por achado, e relate-os ao líder.

## Limites

- Escrita autorizada: as saídas normais das provas e os registros em `.erros-encontrados/`.
- Não escreva testes, não corrija código e não altere `spec.md`, `plan.md`, `review.md` nem `AGENTS.md`.
- Ferramenta ausente segue a regra de instalação de `references/delegation.md` (Pedido autocontido).

## Relatório

Devolva o relatório fixo de `references/delegation.md` (Relatório fixo).
