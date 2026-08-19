# Direção visual (spec)

Fechar o que plan/implement **não** inventam. Não é CSS. Sem UI user-visible: omitir a seção e esta ref.

| Decisão | Linha na spec | Se vago |
|---|---|---|
| Modo | Reuso do DS **ou** greenfield/redesign | DS no repo → RECOMENDO reuso |
| Tom | 1 palavra + 1 frase (sóbrio, denso, ousado, minimal) | Q+RECOMENDO |
| Anti-slop | O que evitar (template genérico, hierarquia frouxa) | Default se UI nova |
| Copy | empty/erro, vocabulário do usuário | Só se a fatia expõe |
| Prova | E2E + screenshot do alvo | Sempre se UI web |

Não fechar na spec: paleta hex, type pairing, “signature” artística.

A*/C* de UI são observáveis. Não usar “bonito” / “moderno” como C*.

DS existente → Always: kit/tokens. Never: primitivo novo na page.
Greenfield → Always: anti-slop. Ask first: mudar tom depois de aprovado.
