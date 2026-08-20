# Implement: distribuição das skills para Codex, Claude, Grok e Antigravity
# Pasta: phase-4-distribuicao-skills
# Status: em-curso

## Fatia T1

- Feito: `docs/tests/test-distribuicao.py` (C1–C5). RED: 7 testes, 4 FAIL + 3 ERROR, sem `skills/` nem manifests.
- Marcado: T1 no `plan.md`
- Prova: `python docs/tests/test-distribuicao.py -v` → FAIL (antes de T2/T3); depois da cadeia, 7 ok

## Fatia T2

- Feito: `skills/vibe-*` (symlink dir `../vibe-*`), `.claude-plugin/marketplace.json` + `plugin.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `.grok-plugin/marketplace.json`, `plugin.json` (Antigravity). Sem `commands/`.
- Marcado: T2, C1, C2, C3
- Prova: `python docs/tests/test-distribuicao.py -v` → 7 ok depois de T3; `npx --yes skills add . --list` → Found 7 skills, sem duplicata

### Feedback −

- `Path.symlink_to(..., target_is_directory=True)` no Windows criou link que `exists()` via como quebrado. `mklink /D` criou symlink de diretório válido. Checkout Linux/CI usa git mode 120000.

## Fatia T3

- Feito: Quick Start no `README.md`; Estrutura e install em `.vibeflow/REGRAS.md`; `docs/ESCOPO.md` §3.4; uma linha de install nas sete `ARQUITETURA.md`; CI roda `docs/tests/test-distribuicao.py`.
- Marcado: T3, A1, A2, C4, C5, checkpoints T1–T2 e T3
- Prova: `python docs/tests/test-distribuicao.py -v` → Ran 7 tests, OK

### Para a review

- Conferir que `git add skills/` grava mode 120000, não cópia do pacote.
- Install nativo (`/plugin`, `codex plugin`, `grok plugin`, `agy plugin`) ficou fora da CI; só o contrato de disco e o `--list` do CLI.

## Handoff

vibe-review
