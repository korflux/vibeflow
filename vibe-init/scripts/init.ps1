#Requires -Version 7.0
# Prepara AGENTS.md como fonte única das regras de um projeto VibeFlow.
param([string]$Root)

$ErrorActionPreference = 'Stop'
$Utf8 = [Text.UTF8Encoding]::new($false)
$Start = '<!-- VIBEFLOW:CADEIA start -->'
$End = '<!-- VIBEFLOW:CADEIA end -->'

# Localiza o projeto por argumento, Git ou diretório atual.
function Get-ProjectRoot {
    if ($Root) { return (Resolve-Path -LiteralPath $Root).Path }
    if (Get-Command git -ErrorAction SilentlyContinue) {
        $gitRoot = & git rev-parse --show-toplevel 2>$null
        if ($LASTEXITCODE -eq 0) { return (Resolve-Path -LiteralPath $gitRoot).Path }
    }
    return (Get-Location).Path
}

# Confere se a fonte é arquivo local, inclusive quando AGENTS ainda é symlink legado.
function Get-LocalSource([string]$Path, [string]$Project) {
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    if (-not $item) { return $null }
    $candidate = if ($item.LinkType) {
        $target = @($item.Target)[0]
        if ([IO.Path]::IsPathRooted($target)) { $target } else { [IO.Path]::GetFullPath((Join-Path (Split-Path -Parent $Path) $target)) }
    } else { $Path }
    $resolved = (Resolve-Path -LiteralPath $candidate).Path
    if (-not $resolved.StartsWith($Project + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw "FONTE_EXTERNA: $Path aponta para fora do projeto"
    }
    if (-not (Test-Path -LiteralPath $resolved -PathType Leaf)) { throw "TIPO_INESPERADO: $Path não é arquivo" }
    if ((Get-Item -LiteralPath $resolved).Length -gt 1MB) { throw "FONTE_GRANDE: $Path excede 1 MiB" }
    return $resolved
}

# Copia e verifica cada fonte antes de uma substituição; colisões recebem sufixo.
function Save-Old([string]$Source, [string]$Project, [string]$OldDir, [string]$Name, $Records) {
    New-Item -ItemType Directory -Path $OldDir -Force | Out-Null
    $destination = Join-Path $OldDir $Name
    if (Test-Path -LiteralPath $destination) {
        if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash -eq (Get-FileHash -LiteralPath $Source -Algorithm SHA256).Hash) { return }
        $destination = Join-Path $OldDir ($Name + '.' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffffffZ'))
    }
    Copy-Item -LiteralPath $Source -Destination $destination
    $sourceItem = Get-Item -LiteralPath $Source
    $copyItem = Get-Item -LiteralPath $destination
    $hash = (Get-FileHash -LiteralPath $Source -Algorithm SHA256).Hash
    if ($sourceItem.Length -ne $copyItem.Length -or $hash -ne (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash) {
        Remove-Item -LiteralPath $destination -Force
        throw "OLD_HASH_MISMATCH: backup de $Source não confere"
    }
    $Records.Add(@{ from = [IO.Path]::GetRelativePath($Project, $Source).Replace('\','/'); to = [IO.Path]::GetRelativePath($Project, $destination).Replace('\','/'); sha256 = $hash })
}

# Atualiza só a regra de escopo e o roteador sem reescrever as demais regras.
function Update-Header([string]$Content, [string]$Template) {
    $begin = $Template.IndexOf($Start)
    $finish = $Template.IndexOf($End) + $End.Length
    $block = $Template.Substring($begin, $finish - $begin)
    $scope = $Template.Split(@("`n`n"), 3, [StringSplitOptions]::None)[1].Trim()
    $hasStart = $Content.Contains($Start)
    $hasEnd = $Content.Contains($End)
    if ($hasStart -xor $hasEnd) { throw 'CADEIA_INCOMPLETA: delimitadores do roteador não formam um par' }
    if ($hasStart) {
        $Content = $Content.Substring(0, $Content.IndexOf($Start)) + $block + $Content.Substring($Content.IndexOf($End) + $End.Length)
    } else {
        if ($Content.StartsWith('# ') -and $Content.Contains("`n")) {
            $split = $Content.IndexOf("`n")
            $Content = $Content.Substring(0, $split) + "`n`n" + $block + "`n`n" + $Content.Substring($split + 1).TrimStart()
        } else { $Content = $block + "`n`n" + $Content.TrimStart() }
    }
    if (-not $Content.Contains($scope)) {
        if ($Content.StartsWith('# ') -and $Content.Contains("`n")) {
            $split = $Content.IndexOf("`n")
            $Content = $Content.Substring(0, $split) + "`n`n" + $scope + "`n`n" + $Content.Substring($split + 1).TrimStart()
        } else { $Content = $scope + "`n`n" + $Content }
    }
    return $Content.TrimEnd() + "`n"
}

# Executa o init e relata arquivos legados que ainda exigem consolidação sem apagá-los.
function Invoke-VibeInit {
    $project = Get-ProjectRoot
    $vf = Join-Path $project '.vibeflow'
    $phases = Join-Path $vf 'phases'
    $old = Join-Path $vf 'old'
    $agents = Join-Path $project 'AGENTS.md'
    $bridge = Join-Path $project '.agents/rules/vibeflow.md'
    $templatePath = Join-Path $PSScriptRoot '../templates/AGENTS.md'
    $template = [IO.File]::ReadAllText($templatePath)
    foreach ($directory in @($vf, $phases, $old, (Join-Path $project '.agents'), (Split-Path -Parent $bridge))) {
        $item = Get-Item -LiteralPath $directory -Force -ErrorAction SilentlyContinue
        if ($item -and ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw "TIPO_INESPERADO: $directory não pode ser link" }
        if (Test-Path -LiteralPath $directory -PathType Leaf) { throw "TIPO_INESPERADO: $directory não é diretório" }
    }
    foreach ($operational in @((Join-Path $vf '.gitignore'), (Join-Path $vf 'init-report.json'), (Join-Path $phases '.gitkeep'), $bridge)) {
        $item = Get-Item -LiteralPath $operational -Force -ErrorAction SilentlyContinue
        if ($item -and ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw "TIPO_INESPERADO: $operational não pode ser link" }
    }
    $legacy = @((Join-Path $vf 'REGRAS.md'), (Join-Path $project 'REGRAS.md'), (Join-Path $project 'CLAUDE.md'))
    $agentSource = Get-LocalSource $agents $project
    $legacySources = @($legacy | ForEach-Object { $source = Get-LocalSource $_ $project; if ($source) { @{ path = $_; source = $source } } })
    foreach ($directory in @($vf, $phases, (Split-Path -Parent $bridge))) {
        New-Item -ItemType Directory -Path $directory -Force | Out-Null
    }
    $gitkeep = Join-Path $phases '.gitkeep'
    if (-not (Test-Path -LiteralPath $gitkeep)) { [IO.File]::WriteAllText($gitkeep, '', $Utf8) }
    $gitignore = Join-Path $vf '.gitignore'
    $ignored = if (Test-Path -LiteralPath $gitignore) { [IO.File]::ReadAllText($gitignore) } else { '' }
    foreach ($entry in @('init-report.json', 'init-pending.json')) {
        if (($ignored -split "`r?`n") -notcontains $entry) { $ignored = $ignored.TrimEnd("`r", "`n") + "`n" + $entry + "`n" }
    }
    [IO.File]::WriteAllText($gitignore, $ignored, $Utf8)

    $records = [Collections.Generic.List[object]]::new()
    $actions = [Collections.Generic.List[string]]::new()
    if ($agentSource) {
        $original = [IO.File]::ReadAllText($agentSource)
        $agentItem = Get-Item -LiteralPath $agents -Force
        if ($agentItem.LinkType -or -not $original.Trim()) {
            Save-Old $agentSource $project $old 'AGENTS.md' $records
            if ($agentItem.LinkType) { Remove-Item -LiteralPath $agents -Force }
            [IO.File]::WriteAllText($agents, $(if ($original.Trim()) { $original } else { $template }), $Utf8)
            $actions.Add('materializar_AGENTS')
        }
    } else {
        $source = if ($legacySources.Count) { $legacySources[0].source } else { $null }
        [IO.File]::WriteAllText($agents, $(if ($source) { [IO.File]::ReadAllText($source) } else { $template }), $Utf8)
        $actions.Add('criar_AGENTS')
    }
    foreach ($entry in $legacySources) {
        if (-not (Get-Item -LiteralPath $entry.path -Force).LinkType) {
            $name = if ($entry.path -eq (Join-Path $vf 'REGRAS.md')) { 'REGRAS-vibeflow.md' } else { Split-Path -Leaf $entry.path }
            Save-Old $entry.source $project $old $name $records
        }
    }
    $current = [IO.File]::ReadAllText($agents)
    $updated = Update-Header $current $template
    if ($updated -cne $current) {
        if ($current.Trim() -and -not @($records | Where-Object { $_.from -eq 'AGENTS.md' }).Count) { Save-Old $agents $project $old 'AGENTS.md' $records }
        [IO.File]::WriteAllText($agents, $updated, $Utf8)
        $actions.Add('atualizar_AGENTS')
    }
    $bridgeContent = '@../../AGENTS.md' + "`n"
    if (Test-Path -LiteralPath $bridge) {
        if (-not (Test-Path -LiteralPath $bridge -PathType Leaf)) { throw "TIPO_INESPERADO: $bridge não é arquivo" }
        if ([IO.File]::ReadAllText($bridge) -cne $bridgeContent) { Save-Old $bridge $project $old 'antigravity-vibeflow.md' $records }
    }
    if (-not (Test-Path -LiteralPath $bridge) -or [IO.File]::ReadAllText($bridge) -cne $bridgeContent) {
        [IO.File]::WriteAllText($bridge, $bridgeContent, $Utf8)
        $actions.Add('atualizar_ponte_antigravity')
    }
    $merges = @($legacySources | Where-Object { (Get-FileHash -LiteralPath $_.source -Algorithm SHA256).Hash -ne (Get-FileHash -LiteralPath $agents -Algorithm SHA256).Hash } | ForEach-Object { [IO.Path]::GetRelativePath($project, $_.path).Replace('\','/') })
    $report = @{ root = $project; target = 'AGENTS.md'; actions = @($actions); olds = @($records); merges = $merges; legacy_present = @($legacySources | ForEach-Object { [IO.Path]::GetRelativePath($project, $_.path).Replace('\','/') }) }
    $reportPath = Join-Path $vf 'init-report.json'
    [IO.File]::WriteAllText($reportPath, ($report | ConvertTo-Json -Depth 8), $Utf8)
    Write-Output $reportPath
}

try { Invoke-VibeInit } catch { [Console]::Error.WriteLine($_.Exception.Message); exit 1 }
