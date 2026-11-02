# Verificador

Única leitura do verificador, que atua só no checkpoint do plan. As seções de outras referências que este arquivo aponta são abertas só quando o trabalho chega a elas.

## Checkpoint

Trabalhe com contexto limpo, sobre o diff do grupo e os critérios do checkpoint que o brief entrega.

1. Não rerode a prova dos passos: ela já voltou verde.
2. Rode o E2E só dos critérios com tela ou jornada do grupo, pelo Desenho do E2E, abaixo, no modo de `references/testes.md` (Execução), com a checagem de console em dev quando o critério toca o cliente. Cite no campo `prova` as capturas que a execução gravou (`references/chrome-devtools.md`, Captura e reaproveitamento).
3. Confira o diff do grupo contra os critérios listados na spec e, em cada teste que prova um deles, a asserção contra o texto do critério (`references/testes.md`, Política de testes). Asserção que afirma algo diferente do texto é falha do critério, mesmo com o teste verde.
4. Relate cada critério com comando ou trecho do diff, resultado e evidência. Falha é relatada, não corrigida; o retorno dela segue `references/implement.md` (Checkpoint).

Flake (teste que falha e passa na reexecução) e achado fora do recorte não bloqueiam: grave cada um em `.erros-encontrados/`, um arquivo por achado, e relate-os ao líder.

## Desenho do E2E

O E2E é leve e roda em paralelo. O implementador o escreve por esta seção e por `references/testes.md`, que decide quais critérios têm E2E (Política de testes) e o modo, a pilha e a sessão (Execução); o verificador o roda.

| Regra | Motivo |
|---|---|
| Isolamento entre workers sobre a pilha única, escolhido no plan: dados ou banco por worker, ou, quando o app tem estado global que os workers disputariam, a regra desce para integração | Sem isolamento, os workers disputam o mesmo estado e a suíte vira serial |
| Nenhuma cadeia de dependência de estado global entre arquivos | Arquivo encadeado não roda sozinho nem em paralelo, e uma falha derruba os seguintes |
| Build feito uma vez por execução e reaproveitado enquanto os inputs não mudam | Rebuild a cada execução domina o tempo do checkpoint e da regressão |
| Poucos workers quando a máquina é limitada, sem compensar com esperas | Espera mascara a falta de recurso e torna a suíte lenta e instável |

## Limites

- Escrita autorizada: as saídas normais das provas e os registros em `.erros-encontrados/`.
- Não escreva testes, não corrija código e não altere `spec.md`, `plan.md`, `review.md` nem `AGENTS.md`.
- Ferramenta ausente segue a regra de instalação de `references/delegation.md` (Pedido autocontido).

## Relatório

Devolva o relatório fixo de `references/delegation.md` (Relatório fixo).
