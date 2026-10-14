# Sandbox da suíte implement criado na raiz do repo

- Data: 2026-10-14.
- Local: docs/vibe-implement/tests/test-implement.py, linha 1270 (`setUp` com `self.repo = Path.cwd() / f".vibe-etapas-{uuid.uuid4().hex}"`).
- Mesmo padrão: a classe `PowershellParity` usa `Path.cwd() / f".vibe-implement-ps-{uuid.uuid4().hex}"` em docs/vibe-implement/tests/test-implement.py, linha 988 (`setUp`).
- Problema: o sandbox `.vibe-etapas-<uuid>` é criado em `Path.cwd()`, que na execução padrão é a raiz do repo real. Isso contraria a regra 9 do `AGENTS.md`, que exige pasta isolada e proíbe escrever no repo real.
- Impacto: o teardown remove a pasta, mas execuções paralelas mostram o diretório temporário no `git status` de outros agentes, e uma falha ou interrupção antes do teardown deixa resíduo visível na raiz, com risco de staging acidental.
- Sugestão de correção: criar o sandbox com `tempfile.mkdtemp()` (ou `TemporaryDirectory`), preservando o repositório Git próprio que o caso precisa e a propagação de falha de limpeza.
- Relação: observado durante a phase 20; defeito pré-existente, fora do escopo desta phase.
