# Definition of Done

Barra permanente. Aceite da T* responde “é a coisa certa?”. DoD responde “está acabado?”. Os dois.

Abrir no fechamento da fatia, não no boot.

## Correctness

- Aceite da T* (ou do R*) ok
- Roda em runtime, não só typecheck
- Comportamento novo coberto por teste que falha sem a mudança
- Sem regressão na suite relevante
- UI web user-visible: prova no browser (ver `chrome-devtools.md`)

## Quality

- Sem escopo extra (`NOTICED BUT NOT TOUCHING`)
- Comentário semântico no que não é óbvio (papel, porquê)
- Lint/format do repo se existirem

## Integration

- Encaixa no que já existe. Sem módulo paralelo “por via das dúvidas”
- API interna obsoleta: apaga. API publicada a terceiros: não remove em silêncio

Não renegocie esta lista a cada T*. Adapte **uma vez** ao repo se o `REGRAS.md` já tiver barra própria; senão use esta.
