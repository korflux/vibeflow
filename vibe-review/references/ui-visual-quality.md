# Qualidade visual (review)

Abrir **só** se o diff muda o que o usuário vê no browser. Julgamento. Não implementa CSS.

## Prova

Mesma regra da implement: Chrome DevTools default (screenshot + **leitura**). Playwright/E2E se a T* ou o humano mandou. Print sem leitura = Required.

Ver `../../vibe-implement/references/chrome-devtools.md` se precisar do fluxo de captura.

## Rubrica (finding → R*)

| Falha | Severidade típica |
|---|---|
| Fluxo user-visible sem prova de browser | Required |
| Copy de empty/erro ausente ou genérica demais para o aceite | Required se a spec pediu; senão Nit |
| Hierarquia ilegível, elemento coberto, contraste óbvio quebrado | Required |
| Kit/DS do repo ignorado (botão/modal copiado na page) | Required |
| Template genérico / slop com DS no repo | Required |
| “Eu usaria outro tom” sem a spec pedir redesign | Não bloqueia |

Não inventar paleta nem type. Não Approve silencioso de UI sem evidência visual.
