# Ajuste de phase

Leia quando o pedido é um ajuste (`SKILL.md`, seção 2). Ajuste é o pedido low ou medium que corrige, completa ou alinha o que uma phase ou o MVP entregou ou está entregando, sem mudar decisão, banco, autenticação ou autorização da spec. Inclui corrigir um registro de `.erros-encontrados/` nesse escopo. Ajuste volta à phase de origem, aberta ou fechada, e nunca abre phase nova; pedido `high`, ou que muda o que a spec decidiu, abre phase nova com substituição explícita. O líder identifica a origem pelo assunto e pelos paths e a anuncia em uma linha; na dúvida entre duas phases, pergunte.

| Situação da phase de origem | Como o ajuste entra |
|---|---|
| Antes do implement | Insumo da spec ou do plan, gravado pelo redator; nenhum código antes do plan |
| Plan com passos e sem `review.md` | O redator acrescenta ao fim do checklist um passo com o próximo número, `Arquivos:` e `Prova:`, sem nova rodada do analyze; o passo segue os passos 1 e 2 de `references/implement.md` |
| `review.md` aberto | O revisor registra o ajuste como R* na etapa vigente, com `papel:`; segue o passo 4 de `references/implement.md` |
| Fechada | O líder acrescenta ao `review.md` uma etapa `### Ajuste N - <pedido>`, com o pedido e `Abriu: Rn`, e um R* Required por item. Low: o `# Status: aprovado` é mantido e não há re-review; o líder marca o `[x]` no commit `task(<alvo>:Rn,...)`, que inclui o `review.md`, os paths do R* e o registro apagado. Medium: o líder muda o `# Status:` para `request-changes`, a exceção de `references/disco.md` (Cabeçalho), e desmarca o Approve e a aprovação humana; o ajuste segue o passo 4 de `references/implement.md`, a re-review de ajuste e a confirmação de `references/review.md` |

R* de ajuste (`path` é um ou mais paths entre crases, separados por `, `, logo depois da severidade):

```text
- [ ] Rn: **Required** - `path` - <pedido do humano> - remédio: <o pedido> - prova: <testes afetados> - source: <pedido humano | path do registro de .erros-encontrados/> - papel: <implementador | redator>
```

Entrega medium ainda sem `review.md`: antes do commit `task(medium): ...`, o ajuste entra no recorte da entrega e, quando muda o aceite, nos critérios do brief; depois dele, o revisor o registra como R* na review que abre a phase. Sem phase de origem, o ajuste segue a linha low da Entrada de `references/implement.md`.

Registro de `.erros-encontrados/` corrigido é apagado no mesmo commit da correção; o Git guarda o histórico.
