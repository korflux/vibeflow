# Definition of Done

Barra permanente de acabamento, aberta no fechamento do passo e somada ao critério de aceite. Na review, julgue se o diff passa Correctness, Quality e Integration no que couber; o remédio pertence à etapa implement.

## Correctness

- Critério do passo, ou do R*, atendido e rodando em runtime, não só no typecheck.
- Testes e `Prova:` verdes conforme `references/testes.md` (Política de testes e Desenho de casos); passo só manual não conta.
- Critério de aparência, layout, responsividade ou comportamento renderizado de UI web: prova no navegador, com a captura de `references/chrome-devtools.md` (Captura e reaproveitamento) citada no relatório.

## Quality

- Sem escopo extra (`NOTICED BUT NOT TOUCHING`) nem abstração especulativa.
- Simplificação, reutilização e remoção de redundância no código tocado; otimização fundamentada quando necessária, preservando controles, comportamento e cobertura.
- Comentário semântico no que não é óbvio (papel, porquê); lint e format do repo, se existirem.

## Integration

- Encaixa no que já existe, sem módulo paralelo "por via das dúvidas".
- API interna obsoleta: apague. API publicada a terceiros: não remova em silêncio.

Adapte esta lista uma vez ao repo se o `AGENTS.md` tiver barra própria; senão use esta, sem renegociar a cada passo.
