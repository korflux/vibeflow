# Direção visual (spec)

Fechar o que plan/implement **não** inventam. Não é CSS. Sem UI user-visible: omitir a seção e esta ref.

| Decisão | Linha na spec | Se vago |
|---|---|---|
| Modo | Reuso do DS **ou** greenfield/redesign | DS no repo → RECOMENDO reuso |
| Tom | 1 palavra + 1 frase (sóbrio, denso, ousado, minimal) | Q+RECOMENDO |
| Anti-slop | O que evitar (template genérico, hierarquia frouxa) | Default se UI nova |
| Copy | empty/erro, vocabulário do usuário | Só se a fatia expõe |
| Evidência renderizada | Telas e estados que precisam aparecer renderizados para o aceite, ligados aos `A*` em Como provar | Sempre se UI web; ferramenta e comando ficam para o plan |

Não fechar na spec: paleta hex, type pairing, “signature” artística. Token visual pertence à design.

Handoff condicional: com UI visível a spec entrega para a etapa design, sem UI visível entrega para a etapa plan. Design e plan não inventam comportamento.

A*/C* de UI são observáveis. Não usar “bonito” / “moderno” como C*.

DS existente → Always: kit/tokens. Never: primitivo novo na page.
Greenfield → Always: anti-slop. Ask first: mudar tom depois de aprovado.
