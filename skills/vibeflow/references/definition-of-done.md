# Definition of Done

Barra permanente. O critério de aceite responde "é a coisa certa?"; o DoD responde "está acabado?". Os dois valem.

Abra no fechamento do passo, não no boot. Na review, julgue se o diff passa Correctness, Quality e Integration no que couber; aplicar o remédio pertence à etapa implement.

## Correctness

- Critério de aceite do passo, ou do R*, atendido.
- Roda em runtime, não só no typecheck.
- Testes conforme `references/testes.md` (Política de testes), capazes de detectar a ausência do comportamento.
- `Prova:` do passo verde. Passo só manual não conta.
- Quando o critério depende de aparência, layout, responsividade ou comportamento renderizado de UI web, prova focada no browser (`references/chrome-devtools.md`).

## Quality

- Sem escopo extra (`NOTICED BUT NOT TOUCHING`).
- Simplificação, reutilização e remoção de redundância no código tocado; otimização de desempenho fundamentada quando necessária, preservando controles, comportamento e cobertura, sem abstração especulativa.
- Comentário semântico no que não é óbvio (papel, porquê).
- Lint e format do repo, se existirem.

## Integration

- Encaixa no que já existe. Sem módulo paralelo "por via das dúvidas".
- API interna obsoleta: apaga. API publicada a terceiros: não remove em silêncio.

Não renegocie esta lista a cada passo. Adapte uma vez ao repo se o `AGENTS.md` já tiver barra própria; senão use esta.
