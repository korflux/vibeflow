# Aparo de linha diverge entre motores: Python `strip()` remove `\x1c`-`\x1f` e .NET `Trim()` não

- Data: 2026-10-14.
- Onde: `vibe-implement/scripts/execution.ps1:73` (linha `Deps` do grafo `coordenacao-v1`), `vibe-implement/scripts/implement.ps1:258` e `vibe-implement/scripts/implement.py:298` (aparo das linhas `Deps` e de concluída na fila). Os dois últimos são anteriores à phase 19.
- Problema: o Python apara a linha com `str.strip()`, que trata os separadores de controle `\x1c`, `\x1d`, `\x1e` e `\x1f` como espaço em branco. O .NET `String.Trim()` não os considera espaço em branco. Uma linha `Deps` ou de concluída com um desses controles na ponta é reconhecida pelo motor Python e recusada ou lida de outra forma pelo motor PowerShell.
- Impacto: um plan com esses controles na ponta da linha pode produzir fila, `Deps` ou estado de concluída diferentes entre os motores. Não afeta o cálculo da onda, porque `Arquivos:` usa um conjunto ASCII fixo de aparo. Plans reais dificilmente contêm esses caracteres.
- Sugestão de correção: usar um único conjunto explícito de aparo nos dois motores para as linhas `Deps` e de concluída, como já é feito com o `WAVE_WHITESPACE` da onda, e cobrir com um teste de paridade com `\x1c`-`\x1f` na ponta da linha.
- Relação com a tarefa atual: apontado pelo verificador e pela review da phase 19; fora do escopo das T* e dos R* desta phase.
