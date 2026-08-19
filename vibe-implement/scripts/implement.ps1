# vibe-implement/scripts/implement.ps1
# Inventário de .vibeflow/phases → implement-report.json. Sem apply e sem wip.
param(
    [string]$Root,
    [string]$Dir
)

$ErrorActionPreference = 'Stop'
$script:ChainFiles = @('interview.md', 'spec.md', 'plan.md', 'analyze.md', 'review.md')

# Resolve a raiz por parâmetro, Git ou cwd sem exigir que Git esteja instalado.
function Get-RepoRoot {
    if ($Root) { return (Resolve-Path -LiteralPath $Root).Path }
    if (Get-Command git -ErrorAction SilentlyContinue) {
        $git = & git rev-parse --show-toplevel 2>$null
        if ($LASTEXITCODE -eq 0 -and $git) { return $git.Trim() }
    }
    return (Get-Location).Path
}

# Acrescenta exclusões operacionais preservando regras existentes e evitando duplicação.
function Add-GitignoreEntry([string]$Path, [string]$Entry) {
    $body = ''
    if (Test-Path -LiteralPath $Path) { $body = [System.IO.File]::ReadAllText($Path) }
    $lines = @()
    if ($body) { $lines = $body -split '\r?\n' }
    foreach ($line in $lines) {
        if ($line.Trim() -eq $Entry) { return }
    }
    $prefix = ''
    if ($body -and -not $body.EndsWith("`n")) { $prefix = "`n" }
    [System.IO.File]::AppendAllText($Path, "$prefix$Entry`n")
}

# Garante que o relatório não entre no Git sem apagar as entradas das outras skills.
function Assert-ImplementGitignore([string]$Vf) {
    Add-GitignoreEntry (Join-Path $Vf '.gitignore') 'implement-report.json'
}

# Lista pastas que batem o padrão phase-N-slug e ignora o restante.
function Get-PhaseList([string]$Phases) {
    $existing = New-Object System.Collections.Generic.List[object]
    $warnings = New-Object System.Collections.Generic.List[string]
    if (-not (Test-Path -LiteralPath $Phases)) {
        return @{ existing = @(); warnings = @() }
    }
    Get-ChildItem -LiteralPath $Phases -Force | ForEach-Object {
        if (-not $_.PSIsContainer) {
            if ($_.Name -ne '.gitkeep') { $warnings.Add("ignorado (não é pasta de fase): $($_.Name)") }
            return
        }
        $m = [regex]::Match($_.Name, '^phase-(\d+)-([a-z0-9]+(?:-[a-z0-9]+)*)$')
        if (-not $m.Success) {
            $warnings.Add("ignorado (nome fora do padrão): $($_.Name)")
            return
        }
        $files = New-Object System.Collections.Generic.List[string]
        foreach ($name in $script:ChainFiles) {
            if (Test-Path -LiteralPath (Join-Path $_.FullName $name)) { [void]$files.Add($name) }
        }
        $existing.Add([pscustomobject]@{
            dir   = $_.Name
            n     = [int]$m.Groups[1].Value
            slug  = $m.Groups[2].Value
            path  = ".vibeflow/phases/$($_.Name)"
            files = @($files)
        })
    }
    $sorted = @($existing | Sort-Object n)
    return @{ existing = $sorted; warnings = @($warnings) }
}

# Maior n que já tem plan.md: é a fila desta skill sem -Dir.
function Get-AlvoComPlan($Existing) {
    foreach ($item in ($Existing | Sort-Object n -Descending)) {
        if ($item.files -contains 'plan.md') { return $item }
    }
    return $null
}

# Converte o objeto da fase para PSCustomObject (hashtable enumeraria no JSON).
function ConvertTo-PhaseMap($Item) {
    if ($null -eq $Item) { return $null }
    return [pscustomobject]@{
        dir   = [string]$Item.dir
        n     = [int]$Item.n
        slug  = [string]$Item.slug
        path  = [string]$Item.path
        files = @($Item.files)
    }
}

# Destino: -Dir se veio; senão maior n com plan. Sem alvo = não há fila no disco.
function Get-ImplementAlvo($Existing, [string]$Phases) {
    if (-not [string]::IsNullOrWhiteSpace($Dir)) {
        $destName = [System.IO.Path]::GetFileName($Dir)
        $destDir = Join-Path $Phases $destName
        if (-not (Test-Path -LiteralPath $destDir) -or -not (Get-Item -LiteralPath $destDir).PSIsContainer) {
            throw "FASE_AUSENTE: .vibeflow/phases/$destName não é uma pasta de fase."
        }
        if (-not [regex]::IsMatch($destName, '^phase-(\d+)-([a-z0-9]+(?:-[a-z0-9]+)*)$')) {
            throw "FASE_AUSENTE: $destName não é uma pasta de fase."
        }
        foreach ($item in $Existing) {
            if ($item.dir -eq $destName) { return @{ item = $item; modo = 'reuse' } }
        }
        $listed = Get-PhaseList $Phases
        foreach ($item in $listed.existing) {
            if ($item.dir -eq $destName) { return @{ item = $item; modo = 'reuse' } }
        }
        throw "FASE_AUSENTE: .vibeflow/phases/$destName não é uma pasta de fase."
    }
    $found = Get-AlvoComPlan $Existing
    if ($null -ne $found) { return @{ item = $found; modo = 'reuse' } }
    return @{ item = $null; modo = 'criar' }
}

# Monta o JSON que a skill lê; stdout só o path do relatório.
function Write-ImplementReport([string]$Vf, [hashtable]$Payload) {
    $reportPath = Join-Path $Vf 'implement-report.json'
    $json = [string](ConvertTo-Json -InputObject $Payload -Depth 8)
    $utf8 = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($reportPath, $json, $utf8)
    Write-Output $reportPath
}

# Inventaria o disco. Não escreve plan/spec e não promove wip.
function Invoke-Implement {
    $repo = Get-RepoRoot
    $vf = Join-Path $repo '.vibeflow'
    $phases = Join-Path $vf 'phases'
    $actions = New-Object System.Collections.Generic.List[object]

    if (-not (Test-Path -LiteralPath $vf)) {
        throw 'INIT_AUSENTE: não existe .vibeflow/. Rode /vibe-init antes.'
    }
    $vfItem = Get-Item -LiteralPath $vf -Force
    if (-not $vfItem.PSIsContainer) {
        throw 'INIT_AUSENTE: .vibeflow existe, mas não é um diretório.'
    }

    $phState = 'ausente'
    if (Test-Path -LiteralPath $phases) {
        $phItem = Get-Item -LiteralPath $phases -Force
        if (-not $phItem.PSIsContainer) {
            throw 'PHASES_INESPERADO: .vibeflow/phases existe, mas não é um diretório.'
        }
        $phState = 'ok'
    } else {
        New-Item -ItemType Directory -Path $phases -Force | Out-Null
        [System.IO.File]::WriteAllText((Join-Path $phases '.gitkeep'), '')
        $actions.Add([pscustomobject]@{ op = 'criar_phases'; alvo = '.vibeflow/phases' })
        $phState = 'ok'
    }

    Assert-ImplementGitignore $vf
    $listed = Get-PhaseList $phases
    $existing = @($listed.existing)
    $warnings = New-Object System.Collections.Generic.List[string]
    foreach ($w in $listed.warnings) { $warnings.Add($w) }
    $nextN = 1
    if ($existing.Count -gt 0) { $nextN = [int]$existing[-1].n + 1 }
    $resolved = Get-ImplementAlvo $existing $phases
    $alvoItem = $resolved.item
    $modoSugerido = $resolved.modo

    $mapped = New-Object System.Collections.Generic.List[object]
    foreach ($item in @($existing)) {
        if ($null -ne $item) { [void]$mapped.Add((ConvertTo-PhaseMap $item)) }
    }

    $payload = @{
        root               = "$repo"
        vibeflow           = 'ok'
        phases             = "$phState"
        next_n             = [int]$nextN
        existing           = $mapped.ToArray()
        plan_pendente      = $null
        rascunho           = $null
        alvo               = ConvertTo-PhaseMap $alvoItem
        modo_sugerido      = "$modoSugerido"
        wip                = 'ausente'
        created            = $null
        modo               = $null
        actions            = $actions.ToArray()
        avisos             = $warnings.ToArray()
    }
    Write-ImplementReport $vf $payload
}

try {
    Invoke-Implement
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}
