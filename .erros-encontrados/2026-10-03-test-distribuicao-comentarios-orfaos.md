# Comentários órfãos em test-distribuicao.py

- **Data:** 2026-10-03
- **Onde:** `docs/tests/test-distribuicao.py`, bloco final da classe `DistribuicaoContracts` (comentários "C4: README...", "T5: cada skill investiga...", "C5: o contrato Git...", "C5: retomada...", "C4: apenas o estado persistido...", "C5: o workflow...")
- **Problema:** seis comentários de teste sem função logo abaixo. Sobraram quando os testes textuais foram removidos (commit "Migra regras legadas e remove testes textuais").
- **Impacto:** nenhum funcional. Os comentários sugerem cobertura que não existe e confundem quem procura o contrato de distribuição.
- **Sugestão:** remover os seis comentários órfãos na próxima vez que o arquivo for editado.
- **Relação com a tarefa:** a T2 e a T5 da phase 14 editam este arquivo, mas não dependem do bloco. Registrado sem alterar.
