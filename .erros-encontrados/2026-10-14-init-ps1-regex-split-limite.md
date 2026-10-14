# Limite de partes ignorado no Split do init.ps1

- Data: 2026-10-14.
- Local: vibe-init/scripts/init.ps1, linha 138 (`$paragraphs = @([regex]::Split($Template, '\r?\n\r?\n', 3))`).
- Problema: na sobrecarga estática `[regex]::Split(input, pattern, options)`, o terceiro argumento `3` é interpretado como `RegexOptions` e não como limite de partes. Na verificação, o template foi dividido em 13 partes em vez de 3.
- Impacto: hoje sem divergência observável, porque o índice `[1]` usado pelo motor coincide com o parágrafo que o `init.py` extrai. Uma mudança no template que dependa do limite de 3 partes (por exemplo, juntar o restante em `[2]`) faria os dois motores divergirem.
- Sugestão de correção: usar a sobrecarga de instância com limite, `[regex]::new('\r?\n\r?\n').Split($Template, 3)`, e conferir paridade com o `init.py` na suíte PowerShell.
- Relação: encontrado na verificação da T1 da phase 20. Fora do escopo, porque o motor do init não muda nesta phase.
