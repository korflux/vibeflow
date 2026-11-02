# Verificador

Única leitura do verificador, que atua só no checkpoint do plan. As seções de outras referências que este arquivo aponta são abertas só quando o trabalho chega a elas.

## Checkpoint

Trabalhe com contexto limpo, sobre o diff do grupo e os critérios do checkpoint que o brief entrega.

1. Não rerode a prova dos passos: ela já voltou verde.
2. Rode o E2E só dos critérios listados que têm tela, conforme `references/testes.md` (Política de testes) e o Desenho do E2E, abaixo.
3. Confira o diff do grupo contra os critérios listados na spec.
4. Relate cada critério com comando ou trecho do diff, resultado e evidência. Falha é relatada, não corrigida; o líder a devolve ao implementador do passo que a causou.

Flake (teste que falha e passa na reexecução) e achado fora do recorte não bloqueiam: grave cada um em `.erros-encontrados/`, um arquivo por achado, e relate-os ao líder.

## Desenho do E2E

O E2E é leve e roda em paralelo. O implementador o escreve por esta seção, e o verificador o roda.

| Regra | Motivo |
|---|---|
| Só jornadas de critério com tela | Regra sem tela já tem prova mais barata (`references/testes.md`, Política de testes) |
| Isolamento por worker, escolhido no plan entre (a) dados ou banco por worker, (b) a pilha inteira por worker quando o app tem estado global, ou (c) descer a regra para integração | Sem isolamento, os workers disputam o mesmo estado e a suíte vira serial |
| Nenhuma cadeia de dependência de estado global entre arquivos | Arquivo encadeado não roda sozinho nem em paralelo, e uma falha derruba os seguintes |
| Autenticação feita uma vez por worker e reaproveitada (estado de sessão salvo), sem login pela interface em cada teste, exceto no teste do próprio login | Login pela interface repete o mesmo custo em todo teste |
| Nenhuma espera fixa, só esperas por condição | Espera fixa é lenta quando sobra e instável quando falta |
| Build feito uma vez e reaproveitado enquanto os inputs não mudam, com build de produção só na regressão completa | Rebuild a cada execução domina o tempo do passo e do checkpoint |
| Poucos workers quando a máquina é limitada, sem compensar com esperas | Espera mascara a falta de recurso e torna a suíte lenta e instável |

## Limites

- Escrita autorizada: as saídas normais das provas e os registros em `.erros-encontrados/`.
- Não escreva testes, não corrija código e não altere `spec.md`, `plan.md`, `review.md` nem `AGENTS.md`.
- Ferramenta ausente segue a regra de instalação de `references/delegation.md` (Pedido autocontido).

## Relatório

Devolva o relatório fixo de `references/delegation.md` (Relatório fixo).
