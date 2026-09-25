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
    if ($report.merges -notcontains 'CLAUDE.md' -or -not (Test-Path (Join-Path $repo '.vibeflow/old/CLAUDE.md'))) { throw 'legado não preservado' }
}

if ($failed) { exit 1 }
