# Phase 9: T1 sem commit isolado e seleção de review por alvo explícito

- Data: 2026-09-23.
- Onde: `.vibeflow/phases/phase-9-commits-por-task-e-fechamento-da-fase/plan.md`, `implement.md` e seleção de alvo de `vibe-review`.
- Evidência: `plan.md` está aprovado como plano, mas T1 não está concluída. A implementação consta no commit amplo `fe68e31` (79 arquivos), sem commit path-scoped `task(T1)`; `implement.md` registrava essa pendência. Portanto a phase 9 não pode ser encerrada sem exceção explícita ao contrato de commit por task.
- Seleção: o inventário aponta a maior phase com plan sem review. A phase 9 é o alvo pendente correto enquanto não houver `review.md`. Havia também um defeito real nos dois motores: `--dir`/`-Dir` alterava o destino do apply, mas o inventário continuava reportando a phase automática, podendo mostrar um alvo diferente do diff revisado.
- Correção aplicada: `review.py` e `review.ps1` agora resolvem e reportam a phase explícita antes e depois do apply; a suíte cobre o override quando há outra plan pendente mais recente. `vibe-review/SKILL.md` orienta a IA a comparar o diff com o alvo automático e usar `--dir` quando forem diferentes. `implement.md` voltou para `em-curso`; `plan.md` registra a evidência do commit amplo e mantém T1 aberta.
- Provas: `python docs/vibe-review/tests/test-review.py` e `git diff --check`.
- Estado restante: T1 segue aberta porque o commit isolado não pode ser recriado sem reescrever histórico já publicado. Não marcar conclusão por aproximação.
