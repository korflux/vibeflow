# Launcher Bash não inicia neste host Windows

- Data: 2026-08-31
- Onde: `docs/vibe-plan/tests/test-plan.sh`, ao executar o launcher de contrato
- Problema: o Bash do Windows falha antes de executar o script com `E_ACCESSDENIED` ao criar o signal pipe, tanto pelo `bash` do sistema quanto pelo Bash do Git. A falha é do ambiente de execução, não do launcher ou da mudança desta phase.
- Evidência inicial: `bash docs/vibe-plan/tests/test-plan.sh` e `C:\Program Files\Git\bin\bash.exe docs/vibe-plan/tests/test-plan.sh` encerraram antes dos testes com `couldn't create signal pipe, Win32 error 5`.
- Correção: o launcher foi rerodado pelo Git Bash com execução fora da restrição do sandbox, mantendo o script sem alteração.
- Evidência atual: `C:\Program Files\Git\bin\bash.exe docs/vibe-plan/tests/test-plan.sh` retornou `pass=6 fail=0`.
- Estado: corrigido em 2026-08-31 para o ambiente de validação. O shim `bash` do sandbox continua sujeito à restrição de criação do signal pipe.
