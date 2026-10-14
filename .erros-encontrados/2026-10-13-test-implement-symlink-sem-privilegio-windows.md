# test-implement.py falha ao criar symlink no Windows sem privilégio

- Data: 2026-10-13.
- Onde: `docs/vibe-implement/tests/test-implement.py`, `StageProtocolContracts.test_integration_snapshot_types_and_old_commit` (`linked.symlink_to(copy)`).
- Problema: o teste cria um symlink real no trecho final e falha com `OSError: [WinError 1314]` quando o usuário do host não tem o privilégio de symlink. O teste irmão em `test-execution.py` trata o mesmo caso com `skipTest('host sem permissão de symlink')`; este não trata. Os demais testes da suíte passam (restam 2 skips de symlink em `test-execution.py`).
- Impacto: a prova afetada `py -3 docs/vibe-implement/tests/test-implement.py -v` termina com 1 erro neste host mesmo sem relação com a mudança testada. No CI Linux o teste passa.
- Correção futura: fazer o teste pular o trecho do symlink com `skipTest` quando `OSError` indicar falta de privilégio (como em `test-execution.py`), ou habilitar symlinks no Windows (Modo de Desenvolvedor), mesma causa de `2026-09-23-symlinks-skills-windows.md`.
- Relação com a tarefa atual: nenhuma. Encontrado ao rodar a suíte na T1 da phase 19; a T1 não toca esse teste.

## Também afeta

Mesma causa (usuário do host sem privilégio de symlink no Windows), confirmada em 2026-10-13 na T6 da phase 19 ao rodar as suítes do vibe-init:

- `docs/vibe-init/tests/test-init.py`: `py -3 docs/vibe-init/tests/test-init.py` termina com 22 erros `OSError: [WinError 1314]` (12 testes executados), todos nos testes de alias/symlink, como `test_profiles_preflight_rejects_unsafe_destinations` (cenários `linked_root`, `linked_parent`, `linked_leaf`, `broken_link`, nas duas variantes de interpretador).
- `docs/vibe-init/tests/test-init.ps1`: o cenário `ponte-legada` falha com "É necessário privilégio de administrador para essa operação."; os demais cenários passam.
- `docs/vibe-init/tests/test-init.sh`: aborta com `Not a directory` porque `skills/vibe-init` é texto (`core.symlinks=false`), mesma causa de `2026-09-23-symlinks-skills-windows.md`. Apontando uma cópia do script para `vibe-init/scripts/init.sh` físico, o teste passa (doze perfis).
- Impacto e correção: iguais aos descritos acima (sem relação com a T6; o CI Linux cobre; reparo exige Modo de Desenvolvedor ou privilégio e novo checkout).
