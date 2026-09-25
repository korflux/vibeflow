#Requires -Version 7.0
# Prova os contratos essenciais do motor PowerShell em pastas isoladas.
$ErrorActionPreference = 'Stop'
$engine = Join-Path $PSScriptRoot '../../../vibe-init/scripts/init.ps1'
$failed = 0

# Executa um cenário e remove somente a pasta temporária criada por ele.
function Check-Scenario([string]$Name, [scriptblock]$Body) {
    $repo = Join-Path (Get-Location).Path ('.vibe-init-ps-' + [guid]::NewGuid().ToString('n'))
    New-Item -ItemType Directory -Path $repo | Out-Null
    try { & $Body $repo; Write-Output "PASS $Name" }
    catch { $script:failed++; Write-Output "FAIL $Name : $_" }
    finally { Remove-Item -LiteralPath $repo -Recurse -Force }
}

Check-Scenario 'novo' {
    param($repo)
    & $engine -Root $repo | Out-Null
    if (-not (Test-Path (Join-Path $repo 'AGENTS.md')) -or (Test-Path (Join-Path $repo 'CLAUDE.md')) -or (Test-Path (Join-Path $repo '.vibeflow/REGRAS.md'))) { throw 'fonte incorreta' }
    if ((Get-Content -LiteralPath (Join-Path $repo '.agents/rules/vibeflow.md') -Raw) -ne "@../../AGENTS.md`n") { throw 'ponte incorreta' }
}

Check-Scenario 'legado' {
    param($repo)
    Set-Content -LiteralPath (Join-Path $repo 'CLAUDE.md') -Value 'regra legada' -Encoding utf8
    & $engine -Root $repo | Out-Null
    $report = Get-Content -LiteralPath (Join-Path $repo '.vibeflow/init-report.json') -Raw | ConvertFrom-Json
    if ($report.migrated -notcontains 'CLAUDE.md' -or (Test-Path (Join-Path $repo 'CLAUDE.md')) -or -not (Test-Path (Join-Path $repo '.vibeflow/old/CLAUDE.md'))) { throw 'legado não migrado' }
}

# Executa uma cópia do motor contra template CRLF e confirma que a segunda execução não reescreve o resultado.
Check-Scenario 'template-crlf-idempotente' {
    param($repo)
    $skillCopy = Join-Path $repo '.skill'
    $scriptsCopy = Join-Path $skillCopy 'scripts'
    $templatesCopy = Join-Path $skillCopy 'templates'
    New-Item -ItemType Directory -Path $scriptsCopy, $templatesCopy -Force | Out-Null
    $engineCopy = Join-Path $scriptsCopy 'init.ps1'
    Copy-Item -LiteralPath $engine -Destination $engineCopy
    $templateSource = Join-Path $PSScriptRoot '../../../vibe-init/templates/AGENTS.md'
    $templateCopy = Join-Path $templatesCopy 'AGENTS.md'
    $templateText = [IO.File]::ReadAllText($templateSource)
    $templateText = [regex]::Replace($templateText, '\r?\n', "`r`n")
    [IO.File]::WriteAllText($templateCopy, $templateText, [Text.UTF8Encoding]::new($false))

    $target = Join-Path $repo 'project'
    New-Item -ItemType Directory -Path $target | Out-Null
    $first = & pwsh -NoProfile -File $engineCopy -Root $target 2>&1
    if ($LASTEXITCODE -ne 0) { throw "CRLF falhou na primeira execução: $first" }
    $reportPath = Join-Path $target '.vibeflow/init-report.json'
    $report = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
    if ($report.target -ne 'AGENTS.md') { throw 'relatório do cenário CRLF aponta para alvo incorreto' }
    $before = [Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $target 'AGENTS.md')))

    $second = & pwsh -NoProfile -File $engineCopy -Root $target 2>&1
    if ($LASTEXITCODE -ne 0) { throw "CRLF falhou na segunda execução: $second" }
    $after = [Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $target 'AGENTS.md')))
    $report = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
    if ($before -cne $after -or @($report.actions).Count -ne 0) { throw 'execução CRLF não é idempotente' }
}

Check-Scenario 'ponte-legada' {
    param($repo)
    $vf = Join-Path $repo '.vibeflow'
    New-Item -ItemType Directory -Path $vf | Out-Null
    [IO.File]::WriteAllText((Join-Path $vf 'REGRAS.md'), "# Regra antiga`n")
    New-Item -ItemType SymbolicLink -Path (Join-Path $repo 'AGENTS.md') -Target '.vibeflow/REGRAS.md' | Out-Null
    New-Item -ItemType SymbolicLink -Path (Join-Path $repo 'CLAUDE.md') -Target '.vibeflow/REGRAS.md' | Out-Null
    & $engine -Root $repo | Out-Null
    $report = Get-Content -LiteralPath (Join-Path $vf 'init-report.json') -Raw | ConvertFrom-Json
    if ((Test-Path (Join-Path $vf 'REGRAS.md')) -or (Test-Path (Join-Path $repo 'CLAUDE.md')) -or $report.migrated -notcontains '.vibeflow/REGRAS.md') { throw 'ponte antiga não migrada' }
    if ((Get-Item -LiteralPath (Join-Path $repo 'AGENTS.md')).LinkType) { throw 'AGENTS continua symlink' }
}

if ($failed) { exit 1 }
