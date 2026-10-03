# Motores emitem o stdout em codificações legadas diferentes no Windows

- **Data:** 2026-10-03
- **Onde:** `vibe-implement/scripts/implement.py` (`print` do JSON) e `vibe-implement/scripts/implement.ps1` (`[Console]::Out.WriteLine`); o mesmo padrão existe nos motores das outras skills `vibe-*`.
- **Problema:** com o stdout em pipe no Windows, o motor Python escreve em cp1252 (`í` vira o byte `0xED`) e o PowerShell em cp850 (`í` vira `0xA1`). Nenhum dos dois emite UTF-8, embora o JSON seja gravado com `ensure_ascii=False` e `ConvertTo-Json` sem escape de acentos.
- **Impacto:** o texto acentuado de `avisos` (por exemplo `sem linha concluída`, `review.md ilegível`) chega ao consumidor com bytes diferentes conforme o motor e não é decodificável como UTF-8 em nenhum dos dois. Os campos de identificadores (`alvo`, `fila`, `etapa`) são ASCII e não são afetados.
- **Sugestão:** fixar UTF-8 na saída dos dois motores (`sys.stdout.reconfigure(encoding="utf-8")` no Python; `[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)` no PowerShell) e cobrir com um teste de bytes por skill; ou emitir JSON com `ensure_ascii=True`, que elimina a dependência de codificação.
- **Relação com a tarefa atual:** T1 da phase 14 acrescentou avisos acentuados ao JSON do implement. O teste de paridade da T1 compara a contagem de avisos, não o texto, para não depender dessa codificação.
