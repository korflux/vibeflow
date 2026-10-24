# Direção visual (interview)

Fechar com o humano o que plan e implement **não** inventam. Não é CSS. Sem UI user-visible: não usar esta ref.

| Decisão | Onde na spec | Se vago |
|---|---|---|
| Modo | Decisões: reuso do DS **ou** greenfield/redesign | DS no repo → recomendar reuso |
| Tom | Decisões: 1 palavra + 1 frase (sóbrio, denso, ousado, minimal) | Pergunta com recomendação |
| Anti-slop | Decisões: o que evitar (template genérico, hierarquia frouxa) | Default se UI nova |
| Copy | Decisões: empty/erro, vocabulário do usuário | Só se a fatia expõe |
| Evidência renderizada | Critérios de aceite: telas e estados que precisam aparecer renderizados | Sempre se UI web; ferramenta e comando ficam para o plan |

Não fechar na spec: paleta hex, type pairing, “signature” artística. Token visual fica para a implementação, sobre o DS existente.

Plan e implement não inventam comportamento nem tom.

A* de UI são observáveis. Não usar “bonito” / “moderno” como critério.

DS existente → reusar kit/tokens; nunca primitivo novo na page.
Greenfield → anti-slop; mudar o tom depois da aprovação exige nova aprovação da spec.
