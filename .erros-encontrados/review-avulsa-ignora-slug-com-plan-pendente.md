# Review avulsa ignora slug quando existe plan pendente

- Data: 2026-09-24
- Onde: `vibe-review/scripts/review.ps1` e `vibe-review/scripts/review.py`, seleção do alvo com `-Apply -Slug` / `--apply --slug`.
- Problema: quando o inventário encontra uma phase com `plan.md` pendente, a execução prioriza essa phase e ignora o slug explícito. Uma review avulsa pode acabar sendo preparada em uma phase sem relação com o diff.
- Evidência: `pwsh vibe-review/scripts/review.ps1 -Apply -Slug aprovacao-design-vibe-plan` criou `.vibeflow/phases/phase-9-commits-por-task-e-fechamento-da-fase/review.md` vazio, embora a intenção fosse abrir uma review avulsa. O arquivo criado foi removido após a confirmação do path e do tamanho zero.
- Encaminhamento: corrigir a precedência do slug explícito nos dois motores e cobrir o contrato com um teste isolado.
