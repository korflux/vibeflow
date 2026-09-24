# Definition of Done

Barra permanente. Aceite da T* responde “é a coisa certa?”. DoD responde “está acabado?”. Os dois.

Abrir no fechamento da fatia, não no boot.

## Correctness

- Aceite da T* (ou do R*) ok
- Roda em runtime, não só typecheck
- Comportamento novo coberto por prova executável capaz de detectar sua ausência, reutilizada ou ampliada quando possível. Não rebaixe esta barra para leitura de arquivo
- Comando da Verificação da T* verde. Passo só manual não conta
- Prova final executada após as edições de código/teste; repita somente a prova afetada por falha ou mudança em seus inputs
- Sem regressão na prova executável relevante; amplie a cobertura quando o risco ou a integração exigir
- Testes redundantes da capacidade tocada podem ser consolidados apenas com preservação dos cenários e afirmações relevantes
- Quando o aceite depende de aparência, layout, responsividade ou comportamento renderizado de UI web, prova focada no browser (ver `chrome-devtools.md`). Se não depender, o `plan.md` registra por que a prova automatizada é suficiente.

## Quality

- Sem escopo extra (`NOTICED BUT NOT TOUCHING`)
- Comentário semântico no que não é óbvio (papel, porquê)
- Lint/format do repo se existirem

## Integration

- Encaixa no que já existe. Sem módulo paralelo “por via das dúvidas”
- API interna obsoleta: apaga. API publicada a terceiros: não remove em silêncio

Não renegocie esta lista a cada T*. Adapte **uma vez** ao repo se o `REGRAS.md` já tiver barra própria; senão use esta.
