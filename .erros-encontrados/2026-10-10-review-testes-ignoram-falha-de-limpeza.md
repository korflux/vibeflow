# Suíte review ignora falhas de limpeza

- Data: 2026-10-10.
- Local: `docs/vibe-review/tests/test-review.py`, métodos `tearDown` das suítes Python e PowerShell (linhas 58 e 237 no estado observado).
- Problema: `shutil.rmtree(self.repo, ignore_errors=True)` oculta falhas de remoção das fixtures isoladas, contrariando o contrato de limpeza obrigatória do projeto.
- Impacto: a suíte pode passar deixando diretórios temporários no workspace; falhas de acesso ou arquivos bloqueados ficam sem diagnóstico e podem contaminar execuções posteriores.
- Sugestão: remover `ignore_errors=True` e, quando necessário no Windows, tratar somente o atributo read-only de maneira específica; propagar qualquer falha residual e confirmar remoção.
- Relação com phase 15: encontrado ao preparar T3 e sua validação compartilhada. É uma deficiência preexistente do harness de review, sem alteração do motor nesta task. Registrado sem ampliar o patch; a execução desta phase confere adicionalmente a ausência das fixtures no disco.
## Correção autorizada em 2026-10-10

Resolvido na phase 15 após pedido humano de corrigir os registros vigentes. Falhas de remoção agora propagam; a suíte reparse tenta remover ambas as fixtures e preserva o encadeamento de falhas. Comentários órfãos e classe vazia foram removidos sem alterar asserts funcionais.

Provas: review 19, distribuição 9, spec 19, design 19, plan 16, analyze 16, interview 19, MVP 1 e reparse 12 testes verdes. Simulação de PermissionError comprovou propagação nos tearDown; em reparse comprovou segunda tentativa de limpeza e erros encadeados. Fixtures removidas e diff check verde.
