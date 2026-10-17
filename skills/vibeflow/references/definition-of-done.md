# Definition of Done

Barra permanente. Aceite da T* responde “é a coisa certa?”. DoD responde “está acabado?”. Os dois.

Abrir no fechamento da fatia, não no boot. Na review, julgue se o diff passa Correctness, Quality e Integration no que couber; aplicar o remédio pertence à etapa implement.

## Correctness

- Aceite da T* (ou do R*) ok
- Roda em runtime, não só typecheck
- Comportamento novo coberto por prova executável capaz de detectar sua ausência, reutilizada ou ampliada quando possível. Não rebaixe esta barra para leitura de arquivo
- Comando da `Prova afetada:` da T* verde. Passo só manual não conta
- Prova afetada suficiente do estado final de código/teste, executada ou reaproveitada com cobertura e inputs válidos; repita somente a prova afetada por falha ou mudança em seus inputs
- Sem regressão. Implementador e verificador provam somente o afetado: módulo tocado, consumidores diretos e E2E do cenário cuja entrada mudou; a integração prova a união das provas afetadas de cada onda. Suíte inteira e E2E completo pertencem exclusivamente à `Regressão completa` da review final; nenhuma outra etapa ou papel as exige nem repete prova por trocar de papel.
- Testes da jornada tocada exercitam o fluxo completo e seus resultados observáveis quando possível. Casos fragmentados e redundantes são consolidados sem perder cenários e afirmações relevantes; riscos independentes mantêm prova própria
- Quando o aceite depende de aparência, layout, responsividade ou comportamento renderizado de UI web, prova focada no browser (ver `chrome-devtools.md`). Se não depender, o `plan.md` registra por que a prova automatizada é suficiente.

## Quality

- Sem escopo extra (`NOTICED BUT NOT TOUCHING`)
- Simplificação, reutilização e remoção de redundância no código tocado; otimização de desempenho fundamentada quando necessária, preservando controles, comportamento e cobertura, sem abstração especulativa
- Comentário semântico no que não é óbvio (papel, porquê)
- Lint/format do repo se existirem

## Integration

- Encaixa no que já existe. Sem módulo paralelo “por via das dúvidas”
- API interna obsoleta: apaga. API publicada a terceiros: não remove em silêncio

Não renegocie esta lista a cada T*. Adapte **uma vez** ao repo se o `AGENTS.md` já tiver barra própria; senão use esta.
