# vibeflow

Cadeia de skills para inicializar e conduzir o trabalho de agentes num repo.

- `vibe-init` — fonte única de regras (`.vibeflow/REGRAS.md`) + `AGENTS.md` / `CLAUDE.md` como symlink. Arquitetura em [`docs/vibe-init/ARQUITETURA.md`](docs/vibe-init/ARQUITETURA.md).
- `vibe-interview` — fecha intenção ambígua e grava `.vibeflow/phases/phase-N-slug/interview.md`. Arquitetura em [`docs/vibe-interview/ARQUITETURA.md`](docs/vibe-interview/ARQUITETURA.md).
- `vibe-spec` — grava o decidido em `.vibeflow/phases/phase-N-slug/spec.md` (reusa a pasta da interview). Arquitetura em [`docs/vibe-spec/ARQUITETURA.md`](docs/vibe-spec/ARQUITETURA.md).
- `vibe-plan` — fatia a spec em tasks e grava `.vibeflow/phases/phase-N-slug/plan.md`. Arquitetura em [`docs/vibe-plan/ARQUITETURA.md`](docs/vibe-plan/ARQUITETURA.md).
- `vibe-analyze` — cruza interview, spec e plan e grava `.vibeflow/phases/phase-N-slug/analyze.md`. Arquitetura em [`docs/vibe-analyze/ARQUITETURA.md`](docs/vibe-analyze/ARQUITETURA.md).
- `vibe-implement` — executa a fatia com prova e marca `[x]` no `plan.md` da fase. Arquitetura em [`docs/vibe-implement/ARQUITETURA.md`](docs/vibe-implement/ARQUITETURA.md).
- `vibe-review` — julga o patch e grava `.vibeflow/phases/phase-N-slug/review.md`. Arquitetura em [`docs/vibe-review/ARQUITETURA.md`](docs/vibe-review/ARQUITETURA.md).
