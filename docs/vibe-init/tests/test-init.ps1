# docs/vibe-init/tests/test-init.ps1
# Contratos de docs/vibe-init/ARQUITETURA.md §13 — sem framework.
$ErrorActionPreference = 'Stop'
$skillDir = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..\..\vibe-init')).Path
$init = Join-Path $skillDir 'scripts\init.ps1'
$fail = 0
$pass = 0

# Registra um contrato aprovado sem interromper a suíte.
function Ok([string]$Name) { $script:pass++; Write-Host "PASS $Name" }
# Registra uma falha com evidência e permite que os demais contratos sejam executados.
function Bad([string]$Name, [string]$Why) { $script:fail++; Write-Host "FAIL $Name — $Why" }
# Converte uma condição observável no resultado padronizado da suíte.
function Assert([bool]$Cond, [string]$Name, [string]$Why) {
    if ($Cond) { Ok $Name } else { Bad $Name $Why }
}

# Cria uma raiz descartável por cenário sem compartilhar estado entre testes.
function New-Sandbox {
    $d = Join-Path $env:TEMP ("vibe-init-" + [guid]::NewGuid().ToString('n'))
    New-Item -ItemType Directory -Path $d | Out-Null
    return $d
}

# Executa a entrada PowerShell no repositório isolado informado.
function Invoke-Init([string]$Repo) {
    & $init -Root $Repo | Out-Null
}

# Desserializa o contrato produzido para as asserções do cenário.
function Read-Report([string]$Repo) {
    Get-Content -LiteralPath (Join-Path $Repo '.vibeflow\init-report.json') -Raw | ConvertFrom-Json
}

# Simula o merge semântico da IA e usa o token emitido para finalizar os ponteiros.
function Complete-Merge([string]$Repo, $Report, [string]$Text) {
    $target = Join-Path $Repo '.vibeflow\REGRAS.md'
    $body = Get-Content -LiteralPath $target -Raw
    [System.IO.File]::WriteAllText($target, "$body`n$Text`n")
    & $init -Root $Repo -ApplyPointers -MergeToken $Report.apply_token | Out-Null
}

# Confirma que o item final é um symlink real, não uma cópia ou ponteiro textual.
function Test-IsLink([string]$Path) {
    $i = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    return [bool]($i -and ($i.LinkType -eq 'SymbolicLink' -or $i.Attributes.ToString() -match 'ReparsePoint'))
}

# Calcula hash para detectar qualquer reescrita não autorizada do conteúdo vivo.
function Get-Sha([string]$Path) {
    (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

# Lê o bloco canônico usado para montar fixtures preenchidas.
function Get-CadeiaSnippet {
    $t = Get-Content (Join-Path $skillDir 'templates\REGRAS.md') -Raw
    return [regex]::Match($t, '(?s)<!-- VIBEFLOW:CADEIA start -->.*?<!-- VIBEFLOW:CADEIA end -->').Value
}

# Produz uma fixture saudável sem SLOT para testar idempotência.
function New-RegrasPreenchido([string]$Projeto) {
    return "# Regras do projeto`n`n$(Get-CadeiaSnippet)`n`n## Projeto`n$Projeto`n`n## Ambiente`nhomolog`n`n## Versão (semver)`n- x`n`n## Git`n- y`n`n## Estrutura`n- src`n`n## Regras deste repo`nnada`n"
}

# 1. Repo vazio → NOVO
$s = New-Sandbox
try {
    Invoke-Init $s
    $r = Read-Report $s
    $ok = ($r.flow -eq 'novo') -and
        (Test-Path (Join-Path $s '.vibeflow\REGRAS.md')) -and
        (Test-Path (Join-Path $s '.vibeflow\phases\.gitkeep')) -and
        (Test-IsLink (Join-Path $s 'AGENTS.md')) -and
        (Test-IsLink (Join-Path $s 'CLAUDE.md')) -and
        -not (Test-Path (Join-Path $s '.vibeflow\old')) -and
        ((Get-Content (Join-Path $s '.vibeflow\REGRAS.md') -Raw) -match 'VIBEFLOW:CADEIA start')
    Assert $ok '1-novo-vazio' "flow=$($r.flow) old=$(Test-Path (Join-Path $s '.vibeflow\old'))"
} catch { Bad '1-novo-vazio' "$_" }

# 2. Sem README/description → paragrafo fica SLOT
$s = New-Sandbox
try {
    Invoke-Init $s
    $body = Get-Content (Join-Path $s '.vibeflow\REGRAS.md') -Raw
    Assert ($body -match 'SLOT:paragrafo') '2-paragrafo-slot' 'SLOT:paragrafo ausente'
} catch { Bad '2-paragrafo-slot' "$_" }

# 3. Só .vibeflow/ vazia → REPARAR
$s = New-Sandbox
try {
    New-Item -ItemType Directory -Path (Join-Path $s '.vibeflow') | Out-Null
    Invoke-Init $s
    $r = Read-Report $s
    $ok = ($r.flow -eq 'reparar') -and
        (Test-Path (Join-Path $s '.vibeflow\REGRAS.md')) -and
        (Test-Path (Join-Path $s '.vibeflow\phases')) -and
        (Test-IsLink (Join-Path $s 'AGENTS.md'))
    Assert $ok '3-reparar-pasta-vazia' "flow=$($r.flow)"
} catch { Bad '3-reparar-pasta-vazia' "$_" }

# 3b. .vibeflow sem phases
$s = New-Sandbox
try {
    $vf = Join-Path $s '.vibeflow'
    New-Item -ItemType Directory -Path $vf | Out-Null
    Copy-Item (Join-Path $skillDir 'templates\REGRAS.md') (Join-Path $vf 'REGRAS.md')
    Invoke-Init $s
    $r = Read-Report $s
    $ok = (Test-Path (Join-Path $vf 'phases')) -and ($r.flow -eq 'reparar')
    Assert $ok '3b-cria-phases' 'phases não criada'
} catch { Bad '3b-cria-phases' "$_" }

# 4. REGRAS existe, falta CLAUDE → só cria CLAUDE; não reescreve REGRAS; sem old
$s = New-Sandbox
try {
    $vf = Join-Path $s '.vibeflow'
    New-Item -ItemType Directory -Path $vf | Out-Null
    $regras = Join-Path $vf 'REGRAS.md'
    $texto = New-RegrasPreenchido 'App de teste.'
    [System.IO.File]::WriteAllText($regras, $texto)
    $hashAntes = Get-Sha $regras
    New-Item -ItemType SymbolicLink -Path (Join-Path $s 'AGENTS.md') -Target '.vibeflow\REGRAS.md' | Out-Null
    Invoke-Init $s
    $hashDepois = Get-Sha $regras
    $ok = ($hashAntes -eq $hashDepois) -and (Test-IsLink (Join-Path $s 'CLAUDE.md')) -and -not (Test-Path (Join-Path $vf 'old'))
    Assert $ok '4-so-claude' "hash igual=$($hashAntes -eq $hashDepois) old=$(Test-Path (Join-Path $vf 'old'))"
} catch { Bad '4-so-claude' "$_" }

# 5. Só AGENTS.md legado → old igual + merge + original permanece até ApplyPointers
$s = New-Sandbox
try {
    $orig = "regra legado agents`n"
    [System.IO.File]::WriteAllText((Join-Path $s 'AGENTS.md'), $orig)
    Invoke-Init $s
    $r = Read-Report $s
    $old = Join-Path $s '.vibeflow\old\AGENTS.md'
    $aindaArquivo = -not (Test-IsLink (Join-Path $s 'AGENTS.md'))
    $oldIgual = (Get-Content $old -Raw) -eq $orig
    $temMerge = @($r.merges).Count -gt 0
    Complete-Merge $s $r 'regra legado agents'
    $virou = Test-IsLink (Join-Path $s 'AGENTS.md')
    Assert ($aindaArquivo -and $oldIgual -and $temMerge -and $virou) '5-legado-agents' "arquivo=$aindaArquivo oldIgual=$oldIgual merge=$temMerge link=$virou"
} catch { Bad '5-legado-agents' "$_" }

# 6. AGENTS ≠ CLAUDE, sem REGRAS → old dos dois + duas_fontes; originais ficam
$s = New-Sandbox
try {
    [System.IO.File]::WriteAllText((Join-Path $s 'AGENTS.md'), "A diz X`n")
    [System.IO.File]::WriteAllText((Join-Path $s 'CLAUDE.md'), "C diz Y`n")
    Invoke-Init $s
    $r = Read-Report $s
    $ok = (Test-Path (Join-Path $s '.vibeflow\old\AGENTS.md')) -and
        (Test-Path (Join-Path $s '.vibeflow\old\CLAUDE.md')) -and
        ($r.merges[0].id -eq 'duas_fontes') -and
        -not (Test-IsLink (Join-Path $s 'AGENTS.md')) -and
        -not (Test-IsLink (Join-Path $s 'CLAUDE.md'))
    Assert $ok '6-duas-fontes' "merge=$($r.merges[0].id)"
} catch { Bad '6-duas-fontes' "$_" }

# 7. Segunda migração: old já existe → fonte versionada correta; first old intacto
$s = New-Sandbox
try {
    [System.IO.File]::WriteAllText((Join-Path $s 'AGENTS.md'), "v1`n")
    Invoke-Init $s
    $r1 = Read-Report $s
    $first = Get-Content (Join-Path $s '.vibeflow\old\AGENTS.md') -Raw
    Complete-Merge $s $r1 'v1'
    Remove-Item -LiteralPath (Join-Path $s 'AGENTS.md') -Force
    [System.IO.File]::WriteAllText((Join-Path $s 'AGENTS.md'), "v2`n")
    Invoke-Init $s
    $r2 = Read-Report $s
    $firstDepois = Get-Content (Join-Path $s '.vibeflow\old\AGENTS.md') -Raw
    $stamped = @(Get-ChildItem (Join-Path $s '.vibeflow\old') -Filter 'AGENTS.md.*')
    $mergeSource = [string]$r2.merges[0].sources[0]
    $sourceBody = Get-Content -LiteralPath (Join-Path $s $mergeSource) -Raw
    Assert (($first -eq $firstDepois) -and ($first -eq "v1`n") -and ($stamped.Count -ge 1) -and ($sourceBody -eq "v2`n")) '7-old-timestamp' "stamped=$($stamped.Count) source=$mergeSource"
} catch { Bad '7-old-timestamp' "$_" }

# 8. AGENTS arquivo = REGRAS → old + vira symlink
$s = New-Sandbox
try {
    $vf = Join-Path $s '.vibeflow'
    New-Item -ItemType Directory -Path $vf | Out-Null
    $txt = "# Regras do projeto`n`n## Projeto`nApp.`n`n## Ambiente`nhomolog`n`n## Versão (semver)`n- x`n`n## Git`n- y`n`n## Estrutura`n- src`n`n## Regras deste repo`nnada`n"
    [System.IO.File]::WriteAllText((Join-Path $vf 'REGRAS.md'), $txt)
    [System.IO.File]::WriteAllText((Join-Path $s 'AGENTS.md'), $txt)
    Invoke-Init $s
    $ok = (Test-Path (Join-Path $vf 'old\AGENTS.md')) -and (Test-IsLink (Join-Path $s 'AGENTS.md'))
    Assert $ok '8-arquivo-igual' 'não virou link ou sem old'
} catch { Bad '8-arquivo-igual' "$_" }

# 9. Hash do old ≠ original → não substitui o original
$s = New-Sandbox
try {
    $origPath = Join-Path $s 'AGENTS.md'
    [System.IO.File]::WriteAllText($origPath, "nao-apague`n")
    $env:VIBE_INIT_TEST_CORRUPT_OLD = '1'
    $threw = $false
    try { Invoke-Init $s } catch { $threw = $true }
    Remove-Item Env:VIBE_INIT_TEST_CORRUPT_OLD
    $ainda = Get-Content $origPath -Raw
    $ok = $threw -and ($ainda -eq "nao-apague`n") -and -not (Test-IsLink $origPath)
    Assert $ok '9-hash-mismatch' "threw=$threw ainda=$ainda link=$(Test-IsLink $origPath)"
} catch {
    Remove-Item Env:VIBE_INIT_TEST_CORRUPT_OLD -ErrorAction SilentlyContinue
    Bad '9-hash-mismatch' "$_"
}

# 10. Tudo symlink_ok sem SLOT → actions vazio, sem old novo
$s = New-Sandbox
try {
    $vf = Join-Path $s '.vibeflow'
    New-Item -ItemType Directory -Path (Join-Path $vf 'phases') -Force | Out-Null
    [System.IO.File]::WriteAllText((Join-Path $vf 'phases\.gitkeep'), '')
    $txt = New-RegrasPreenchido 'App.'
    [System.IO.File]::WriteAllText((Join-Path $vf 'REGRAS.md'), $txt)
    New-Item -ItemType SymbolicLink -Path (Join-Path $s 'AGENTS.md') -Target '.vibeflow\REGRAS.md' | Out-Null
    New-Item -ItemType SymbolicLink -Path (Join-Path $s 'CLAUDE.md') -Target '.vibeflow\REGRAS.md' | Out-Null
    Invoke-Init $s
    $r = Read-Report $s
    $ops = @($r.actions | ForEach-Object { $_.op })
    $temOld = $ops -contains 'old'
    # phases já existia; criar_phases não deve; symlink não deve
    $material = @($ops | Where-Object { $_ -in @('old', 'escrever_template', 'symlink_criar', 'symlink_recriar', 'mover', 'apagar_raiz', 'merge_pendente') })
    Assert ($material.Count -eq 0 -and -not $temOld) '10-ja-ok' "ops=$($ops -join ',')"
} catch { Bad '10-ja-ok' "$_" }

# 11. REGRAS.md só na raiz → old REGRAS-raiz.md + move
$s = New-Sandbox
try {
    [System.IO.File]::WriteAllText((Join-Path $s 'REGRAS.md'), "# Regras do projeto`n`n## Projeto`nRaiz.`n`n## Ambiente`nhomolog`n`n## Versão (semver)`n- x`n`n## Git`n- y`n`n## Estrutura`n- src`n`n## Regras deste repo`nnada`n")
    Invoke-Init $s
    $ok = (Test-Path (Join-Path $s '.vibeflow\old\REGRAS-raiz.md')) -and
        (Test-Path (Join-Path $s '.vibeflow\REGRAS.md')) -and
        -not (Test-Path (Join-Path $s 'REGRAS.md'))
    Assert $ok '11-regras-raiz' 'move/old falhou'
} catch { Bad '11-regras-raiz' "$_" }

# 12. Crash depois do old e antes do symlink → originais no lugar
$s = New-Sandbox
try {
    [System.IO.File]::WriteAllText((Join-Path $s 'AGENTS.md'), "preserve`n")
    & $init -Root $s -StopAfterOld | Out-Null
    $ok = (Test-Path (Join-Path $s '.vibeflow\old\AGENTS.md')) -and
        -not (Test-IsLink (Join-Path $s 'AGENTS.md')) -and
        ((Get-Content (Join-Path $s 'AGENTS.md') -Raw) -eq "preserve`n")
    Assert $ok '12-crash-apos-old' 'original sumiu ou sem old'
} catch { Bad '12-crash-apos-old' "$_" }

# 13. Checkout Windows: arquivo = path do link + REGRAS vivo → sem merge, vira symlink
$s = New-Sandbox
try {
    $vf = Join-Path $s '.vibeflow'
    New-Item -ItemType Directory -Path $vf | Out-Null
    $txt = New-RegrasPreenchido 'App.'
    $regras = Join-Path $vf 'REGRAS.md'
    [System.IO.File]::WriteAllText($regras, $txt)
    $hashAntes = Get-Sha $regras
    [System.IO.File]::WriteAllText((Join-Path $s 'AGENTS.md'), ".vibeflow/REGRAS.md`n")
    [System.IO.File]::WriteAllText((Join-Path $s 'CLAUDE.md'), ".vibeflow\REGRAS.md")
    Invoke-Init $s
    $r = Read-Report $s
    $ok = ($r.inventory.agents -eq 'ponteiro_texto') -and
        ($r.inventory.claude -eq 'ponteiro_texto') -and
        (@($r.merges).Count -eq 0) -and
        ((Get-Sha $regras) -eq $hashAntes) -and
        (Test-IsLink (Join-Path $s 'AGENTS.md')) -and
        (Test-IsLink (Join-Path $s 'CLAUDE.md'))
    Assert $ok '13-ponteiro-texto' "agents=$($r.inventory.agents) merges=$(@($r.merges).Count)"
} catch { Bad '13-ponteiro-texto' "$_" }

# 14. Só AGENTS.md com o path (sem REGRAS) → não mergeia a string no vivo
$s = New-Sandbox
try {
    [System.IO.File]::WriteAllText((Join-Path $s 'AGENTS.md'), ".vibeflow/REGRAS.md")
    Invoke-Init $s
    $r = Read-Report $s
    $body = Get-Content (Join-Path $s '.vibeflow\REGRAS.md') -Raw
    $ok = ($r.inventory.agents -eq 'ponteiro_texto') -and
        (@($r.merges).Count -eq 0) -and
        ($body -notmatch '(?m)^\.vibeflow/REGRAS') -and
        (Test-IsLink (Join-Path $s 'AGENTS.md'))
    Assert $ok '14-ponteiro-sem-regras' "agents=$($r.inventory.agents) merge=$(@($r.merges).Count)"
} catch { Bad '14-ponteiro-sem-regras' "$_" }

# 15. REGRAS sem bloco cadeia → upsert; texto do usuário permanece
$s = New-Sandbox
try {
    $vf = Join-Path $s '.vibeflow'
    New-Item -ItemType Directory -Path $vf | Out-Null
    [System.IO.File]::WriteAllText((Join-Path $vf 'REGRAS.md'), "# Regras do projeto`n`n## Projeto`nApp do time.`n`n## Ambiente`nhomolog`n`n## Versão (semver)`n- x`n`n## Git`n- y`n`n## Estrutura`n- src`n`n## Regras deste repo`nnada`n")
    Invoke-Init $s
    $body = Get-Content (Join-Path $vf 'REGRAS.md') -Raw
    $r = Read-Report $s
    $ops = @($r.actions | ForEach-Object { $_.op })
    $ok = ($body -match 'VIBEFLOW:CADEIA start') -and
        ($body -match 'App do time\.') -and
        ($ops -contains 'cadeia_upsert')
    Assert $ok '15-cadeia-upsert' "ops=$($ops -join ',')"
} catch { Bad '15-cadeia-upsert' "$_" }

# 16. Bloco cadeia velho → texto vira o do template; resto intacto
$s = New-Sandbox
try {
    $vf = Join-Path $s '.vibeflow'
    New-Item -ItemType Directory -Path $vf | Out-Null
    $velho = "# Regras do projeto`n`n<!-- VIBEFLOW:CADEIA start -->`n## Cadeia vibe`nvelho`n<!-- VIBEFLOW:CADEIA end -->`n`n## Projeto`nApp do time.`n`n## Ambiente`nhomolog`n`n## Versão (semver)`n- x`n`n## Git`n- y`n`n## Estrutura`n- src`n`n## Regras deste repo`nnada`n"
    [System.IO.File]::WriteAllText((Join-Path $vf 'REGRAS.md'), $velho)
    Invoke-Init $s
    $body = Get-Content (Join-Path $vf 'REGRAS.md') -Raw
    $ok = ($body -match 'VIBEFLOW:CADEIA start') -and
        ($body -notmatch '(?m)^velho$') -and
        ($body -match '\| xhigh \|') -and
        ($body -match 'App do time\.')
    Assert $ok '16-cadeia-refresh' 'bloco não atualizou ou comeu o usuário'
} catch { Bad '16-cadeia-refresh' "$_" }

# 17. ApplyPointers sem alteração do consolidado deve preservar o legado.
$s = New-Sandbox
try {
    [System.IO.File]::WriteAllText((Join-Path $s 'AGENTS.md'), "regra ainda nao unida`n")
    Invoke-Init $s
    $r = Read-Report $s
    $threw = $false
    try { & $init -Root $s -ApplyPointers -MergeToken $r.apply_token | Out-Null } catch { $threw = $_ -match 'MERGE_NAO_APLICADO' }
    $ok = $threw -and -not (Test-IsLink (Join-Path $s 'AGENTS.md')) -and (Test-Path (Join-Path $s '.vibeflow\init-pending.json'))
    Assert $ok '17-apply-sem-merge' "threw=$threw link=$(Test-IsLink (Join-Path $s 'AGENTS.md'))"
} catch { Bad '17-apply-sem-merge' "$_" }

# 18. Merge de REGRAS duplicado deve remover a cópia da raiz somente após confirmação.
$s = New-Sandbox
try {
    New-Item -ItemType Directory -Path (Join-Path $s '.vibeflow') | Out-Null
    [System.IO.File]::WriteAllText((Join-Path $s '.vibeflow\REGRAS.md'), "regra viva`n")
    [System.IO.File]::WriteAllText((Join-Path $s 'REGRAS.md'), "regra raiz`n")
    Invoke-Init $s
    $r = Read-Report $s
    Complete-Merge $s $r "regra raiz"
    $ok = -not (Test-Path -LiteralPath (Join-Path $s 'REGRAS.md')) -and
        -not (Test-Path -LiteralPath (Join-Path $s '.vibeflow\init-pending.json'))
    Assert $ok '18-regras-duplicado-finaliza' 'REGRAS.md da raiz ou estado pendente permaneceu'
} catch { Bad '18-regras-duplicado-finaliza' "$_" }

# 19. .gitignore preexistente deve ser preservado e receber os dois artefatos operacionais.
$s = New-Sandbox
try {
    New-Item -ItemType Directory -Path (Join-Path $s '.vibeflow') | Out-Null
    [System.IO.File]::WriteAllText((Join-Path $s '.vibeflow\.gitignore'), "custom.log`n")
    Invoke-Init $s
    $body = Get-Content -LiteralPath (Join-Path $s '.vibeflow\.gitignore') -Raw
    $ok = ($body -match '(?m)^custom\.log$') -and ($body -match '(?m)^init-report\.json$') -and ($body -match '(?m)^init-pending\.json$')
    Assert $ok '19-gitignore-preserva' $body
} catch { Bad '19-gitignore-preserva' "$_" }

# 20. Tipos estruturais inesperados devem falhar antes de criar qualquer arquivo auxiliar.
$s = New-Sandbox
try {
    [System.IO.File]::WriteAllText((Join-Path $s '.vibeflow'), 'arquivo, nao pasta')
    $threw = $false
    try { Invoke-Init $s } catch { $threw = $_ -match 'TIPO_INESPERADO' }
    Assert ($threw -and -not (Test-Path (Join-Path $s 'AGENTS.md'))) '20-tipo-infra' "threw=$threw"
} catch { Bad '20-tipo-infra' "$_" }

# 21. Scan de migrations não deve entrar em árvores explicitamente ignoradas.
$s = New-Sandbox
try {
    New-Item -ItemType Directory -Path (Join-Path $s 'node_modules\pkg\migrations') -Force | Out-Null
    Invoke-Init $s
    $r = Read-Report $s
    Assert (-not $r.migrations_detectadas) '21-migrations-poda' 'detectou migration dentro de node_modules'
} catch { Bad '21-migrations-poda' "$_" }

Write-Host ""
Write-Host "pass=$pass fail=$fail"
if ($fail -gt 0) { exit 1 }
