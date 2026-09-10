# Harness do launcher não isola fallback PowerShell no Git Bash Windows

- Data: 2026-09-07
- Onde: `docs/tests/launcher-harness.sh`, função `run_pwsh_only`
- Problema: o harness cria um symlink temporário para `pwsh.exe` em um PATH isolado. Neste host, o executável resolve para um caminho inválido de `pwsh.dll` e falha antes de chamar o launcher. A suíte `docs/vibe-init/tests/test-init.sh` registra falha no cenário `5-so-pwsh`.
- Evidência: a suíte executada pelo Git Bash com Python real retornou `pass=4 fail=1`; a execução direta de `vibe-init/scripts/init.sh` com `C:\Program Files\PowerShell\7` no PATH criou a ponte e retornou `PASS direct-pwsh-fallback`.
- Correção: `run_pwsh_only` agora cria um wrapper temporário que chama o executável real, preservando a resolução de `pwsh.dll`; `vibe-init/scripts/init.sh` também valida aliases executáveis de Python e PowerShell antes da seleção.
- Evidência pós-correção: os sete launchers Git Bash passaram, incluindo `init` 5/5 e o fallback isolado de PowerShell.
- Estado: corrigido na T8 de integração e regressão do contrato.
