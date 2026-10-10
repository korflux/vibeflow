# Comentários órfãos em test-distribuicao.py

- **Data:** 2026-10-03
- **Onde:** `docs/tests/test-distribuicao.py`, bloco final da classe `DistribuicaoContracts` (comentários "C4: README...", "T5: cada skill investiga...", "C5: o contrato Git...", "C5: retomada...", "C4: apenas o estado persistido...", "C5: o workflow...")
- **Problema:** seis comentários de teste sem função logo abaixo. Sobraram quando os testes textuais foram removidos (commit "Migra regras legadas e remove testes textuais").
- **Impacto:** nenhum funcional. Os comentários sugerem cobertura que não existe e confundem quem procura o contrato de distribuição.
- **Sugestão:** remover os seis comentários órfãos na próxima vez que o arquivo for editado.
- **Relação com a tarefa:** a T2 e a T5 da phase 14 editam este arquivo, mas não dependem do bloco. Registrado sem alterar.

## Correção autorizada em 2026-10-10

Resolvido na phase 15 após pedido humano de corrigir os registros vigentes. Falhas de remoção agora propagam; a suíte reparse tenta remover ambas as fixtures e preserva o encadeamento de falhas. Comentários órfãos e classe vazia foram removidos sem alterar asserts funcionais.

Provas: review 19, distribuição 9, spec 19, design 19, plan 16, analyze 16, interview 19, MVP 1 e reparse 12 testes verdes. Simulação de PermissionError comprovou propagação nos tearDown; em reparse comprovou segunda tentativa de limpeza e erros encadeados. Fixtures removidas e diff check verde.
