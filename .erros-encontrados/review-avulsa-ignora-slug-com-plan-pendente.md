# Review avulsa ignora slug quando existe plan pendente

- Data: 2026-09-24
- Onde: `vibe-review/scripts/review.ps1` e `vibe-review/scripts/review.py`, seleção do alvo com `-Apply -Slug` / `--apply --slug`.
- Problema: quando o inventário encontra uma phase com `plan.md` pendente, a execução prioriza essa phase e ignora o slug explícito. Uma review avulsa pode acabar sendo preparada em uma phase sem relação com o diff.
- Evidência: `pwsh vibe-review/scripts/review.ps1 -Apply -Slug aprovacao-design-vibe-plan` criou `.vibeflow/phases/phase-9-commits-por-task-e-fechamento-da-fase/review.md` vazio, embora a intenção fosse abrir uma review avulsa. O arquivo criado foi removido após a confirmação do path e do tamanho zero.
- Encaminhamento: corrigir a precedência do slug explícito nos dois motores e cobrir o contrato com um teste isolado.

## Correção atual

R5/R6 resolvidos em 2026-10-10: slug explícito prevalece sobre plan pendente/rascunho, preview não cria e apply preserva o novo alvo; slug vazio/inválido, slug+dir e MVP misto recusados antes de mutação. Defer limitado a Nit/Optional/FYI com ID, fonte, motivo e retomada; Critical/Required, obrigação ausente/parcial e origem insuficiente bloqueiam. Provas: review 23 testes OK, estados implement Python/PowerShell 2 testes com 23 fixtures cada, reparse específico review 12 OK. Captura UTF-8 estrita com aviso real; fases anteriores bytes intactos. Fixtures ausentes, diff check verde; Gitleaks exit 0 sem vazamentos (1,78 MB).
