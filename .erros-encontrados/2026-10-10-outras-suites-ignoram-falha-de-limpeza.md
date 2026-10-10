# Outras suítes ignoram falha de limpeza

- Data: 2026-10-10.
- Local: tearDown de spec, design, plan, analyze e interview; docs/tests/test-mvp-flow.py; blocos finally de docs/tests/test-reparse-safety.py.
- Problema: chamadas shutil.rmtree com ignore_errors=True ocultam falha de remoção, como o erro registrado na suíte review.
- Impacto: fixtures podem permanecer no workspace apesar de prova verde.
- Correção prevista: propagar erros de remoção e conferir ausência das fixtures, sem tratar situações hipotéticas.
- Relação: extensão da mesma causa raiz encontrada durante as correções de .erros-encontrados autorizadas por Marco.

## Correção autorizada em 2026-10-10

Resolvido na phase 15 após pedido humano de corrigir os registros vigentes. Falhas de remoção agora propagam; a suíte reparse tenta remover ambas as fixtures e preserva o encadeamento de falhas. Comentários órfãos e classe vazia foram removidos sem alterar asserts funcionais.

Provas: review 19, distribuição 9, spec 19, design 19, plan 16, analyze 16, interview 19, MVP 1 e reparse 12 testes verdes. Simulação de PermissionError comprovou propagação nos tearDown; em reparse comprovou segunda tentativa de limpeza e erros encadeados. Fixtures removidas e diff check verde.
