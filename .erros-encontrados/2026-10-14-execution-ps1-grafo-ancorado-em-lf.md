# execution.ps1 ancora o grafo do plan em LF e diverge do motor Python

- Data: 2026-10-14.
- Onde: `vibe-implement/scripts/execution.ps1`, `Get-CoordinateGraph` (regex de seções e de `Deps`); `vibe-implement/scripts/implement.ps1`, regex de seções do `etapas-v1` (`(?ms)^### T...`).
- Problema: `Get-CoordinateGraph` ancora seções e `Deps` com `^` multilinha, que só reconhece `\n` como fim de linha. Num plan com `\r` isolado como fim de linha, o PowerShell recusa o grafo (`EXECUTION_INVALIDO`) e o Python aceita, porque o `read_text` do Python converte `\r` em `\n`. A regex de seções do `etapas-v1` em `implement.ps1` tem a mesma raiz. Além disso, a regex de `Deps` do `execution.ps1` não apara espaço inicial como o Python (`line.strip()`), então uma linha `Deps` indentada diverge entre os motores.
- Impacto: quebra de paridade entre motores em plans com fins de linha exóticos (`\r` isolado) ou com linha `Deps` indentada. Não afeta o cálculo da onda, e plans reais usam `\n` ou `\r\n`.
- Sugestão de correção: normalizar `\r\n|\r` para `\n` na entrada do `execution.ps1` (e da regex de seções do `etapas-v1` em `implement.ps1`) e aparar a linha de `Deps` antes do match, como o Python faz.
- Relação com a tarefa atual: encontrado na T1 da phase 19; pré-existente e fora do escopo da T1.

## Resolução

Resolvido em 2026-10-14 na T1 da phase 19: o PowerShell normaliza `\r\n` e `\r` para `\n` na leitura (`ConvertTo-LfText`) em `implement.ps1` e `execution.ps1`, e a linha Deps passou a ser aparada como no Python; testes de paridade com plan em `\r`, `\r\n`, misto e Deps indentada.
