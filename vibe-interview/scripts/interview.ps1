#Requires -Version 7.0
# vibe-interview/scripts/interview.ps1
# Inventaria o interview e prepara um alvo phase ou MVP explícito.
param(
    [string]$Root,
    [switch]$Apply,
    [string]$Slug,
    [switch]$Mvp
)

$ErrorActionPreference = 'Stop'
$script:SlugWasBound = $PSBoundParameters.ContainsKey('Slug')
$script:ChainFiles = @('interview.md', 'spec.md', 'plan.md', 'analyze.md', 'implement.md', 'review.md')
$script:MaxSlug = 48

# Obtém o item do sistema de arquivos sem resolver links quebrados em ausência.
function Get-FsItem([string]$Path) {
    return Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
}

# Detecta symlink, junction ou outro reparse point antes de qualquer leitura ou escrita.
function Test-IsReparsePoint($Item) {
    if (-not $Item) { return $false }
    return $Item.Attributes.ToString() -match 'ReparsePoint' -or $Item.LinkType -eq 'SymbolicLink'
}

# Recusa caminhos operacionais linkados ou de tipo incompatível antes de qualquer escrita.
function Assert-SafeOperationalFile([string]$Path, [string]$Code) {
    $item = Get-FsItem $Path
    if ($item -and ((Test-IsReparsePoint $item) -or $item.PSIsContainer)) {
        throw "${Code}: $([System.IO.Path]::GetFileName($Path)) não é um arquivo operacional regular."
    }
}

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
    Assert-SafeOperationalFile $Path 'GITIGNORE_INESPERADO'
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

# Garante que o relatório operacional não entre no Git sem apagar as entradas existentes.
function Assert-InterviewGitignore([string]$Vf) {
    $gi = Join-Path $Vf '.gitignore'
    Add-GitignoreEntry $gi 'interview-report.json'
}

# Transforma a frase curta da fase em slug ASCII [a-z0-9-], 2–48 chars.
function ConvertTo-Slug([string]$Raw) {
    if ([string]::IsNullOrWhiteSpace($Raw)) { return '' }
    $formD = $Raw.Normalize([Text.NormalizationForm]::FormD)
    $chars = foreach ($ch in $formD.ToCharArray()) {
        $cat = [Globalization.CharUnicodeInfo]::GetUnicodeCategory($ch)
        if ($cat -ne [Globalization.UnicodeCategory]::NonSpacingMark) { $ch }
    }
    $ascii = -join $chars
    $ascii = $ascii.Normalize([Text.NormalizationForm]::FormC).ToLowerInvariant()
    $compact = [regex]::Replace($ascii, '[^a-z0-9]+', '-')
    $compact = $compact.Trim('-')
    $compact = [regex]::Replace($compact, '-{2,}', '-')
    if ($compact.Length -gt $script:MaxSlug) {
        $compact = $compact.Substring(0, $script:MaxSlug).Trim('-')
    }
    return $compact
}

# Lista pastas que batem o padrão phase-N-slug e ignora o restante.
function Get-PhaseList([string]$Phases) {
    $existing = New-Object System.Collections.Generic.List[object]
    $warnings = New-Object System.Collections.Generic.List[string]
    if (-not (Test-Path -LiteralPath $Phases)) {
        return @{ existing = @(); warnings = @() }
    }
    Get-ChildItem -LiteralPath $Phases -Force | ForEach-Object {
        if (Test-IsReparsePoint $_) {
            $warnings.Add("ignorado (link/reparse point): $($_.Name)")
            return
        }
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
            kind  = 'phase'
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

# Representa o alvo MVP sem inferir intenção; a flag continua sendo decisão da IA.
function Get-MvpMap([string]$Vf) {
    $mvpPath = Join-Path $Vf 'mvp'
    $item = Get-FsItem $mvpPath
    if (-not $item) { return $null }
    if (Test-IsReparsePoint $item) { throw 'MVP_INESPERADO: .vibeflow/mvp não pode ser symlink, junction ou reparse point.' }
    if (-not $item.PSIsContainer) {
        throw 'MVP_INESPERADO: .vibeflow/mvp existe, mas não é um diretório.'
    }
    $files = New-Object System.Collections.Generic.List[string]
    foreach ($name in $script:ChainFiles) {
        if (Test-Path -LiteralPath (Join-Path $mvpPath $name) -PathType Leaf) { [void]$files.Add($name) }
    }
    return [pscustomobject]@{
        kind  = 'mvp'
        dir   = 'mvp'
        path  = '.vibeflow/mvp'
        files = @($files)
    }
}

# Cria o arquivo vivo vazio sem substituir conteúdo já escrito pela IA.
function New-LiveFile([string]$Path) {
    $item = Get-FsItem $Path
    if ($item) {
        if ((Test-IsReparsePoint $item) -or -not (Test-Path -LiteralPath $Path -PathType Leaf)) {
            throw "ARTEFATO_INESPERADO: $([System.IO.Path]::GetFileName($Path)) não é um arquivo vivo."
        }
        return $false
    }
    try {
        $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
        $stream.Dispose()
        return $true
    } catch [System.IO.IOException] {
        $item = Get-FsItem $Path
        if ($item -and -not (Test-IsReparsePoint $item) -and (Test-Path -LiteralPath $Path -PathType Leaf)) { return $false }
        throw "ARTEFATO_INESPERADO: $([System.IO.Path]::GetFileName($Path)) não é um arquivo vivo."
    }
}

# Fase de maior n com interview e sem spec: entrevista ainda não entregue à spec.
function Get-Aberta($Existing) {
    foreach ($item in ($Existing | Sort-Object n -Descending)) {
        if ($item.files -contains 'interview.md' -and $item.files -notcontains 'spec.md') {
            return $item
        }
    }
    return $null
}

# Converte o objeto da fase para PSCustomObject (hashtable enumeraria no Add do relatório).
function ConvertTo-PhaseMap($Item) {
    if ($null -eq $Item) { return $null }
    return [pscustomobject]@{
        kind  = 'phase'
        dir   = [string]$Item.dir
        n     = [int]$Item.n
        slug  = [string]$Item.slug
        path  = [string]$Item.path
        files = @($Item.files)
    }
}

# Monta o JSON que a skill lê; stdout só o path do relatório.
function Write-InterviewReport([string]$Vf, [hashtable]$Payload) {
    $reportPath = Join-Path $Vf 'interview-report.json'
    $json = [string](ConvertTo-Json -InputObject $Payload -Depth 8)
    $utf8 = New-Object System.Text.UTF8Encoding $false
    Assert-SafeOperationalFile $reportPath 'RELATORIO_INESPERADO'
    [System.IO.File]::WriteAllText($reportPath, $json, $utf8)
    Write-Output $reportPath
}

# Inventaria o disco, cria phases/ se faltar e prepara o arquivo vivo no apply.
function Invoke-Interview {
    if ($Mvp -and $script:SlugWasBound) {
        throw 'MODO_INVALIDO: o alvo MVP não aceita -Slug.'
    }

    $repo = Get-RepoRoot
    $vf = Join-Path $repo '.vibeflow'
    $phases = Join-Path $vf 'phases'
    $actions = New-Object System.Collections.Generic.List[object]

    if (-not (Test-Path -LiteralPath $vf)) {
        throw 'INIT_AUSENTE: não existe .vibeflow/. Rode /vibe-init antes.'
    }
    $vfItem = Get-FsItem $vf
    if (Test-IsReparsePoint $vfItem) { throw 'INIT_AUSENTE: .vibeflow não pode ser symlink, junction ou reparse point.' }
    if (-not $vfItem.PSIsContainer) {
        throw 'INIT_AUSENTE: .vibeflow existe, mas não é um diretório.'
    }

    $phState = 'ausente'
    $phItem = Get-FsItem $phases
    if ($phItem) {
        if (Test-IsReparsePoint $phItem) { throw 'PHASES_INESPERADO: .vibeflow/phases não pode ser symlink, junction ou reparse point.' }
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

    Assert-InterviewGitignore $vf
    $listed = Get-PhaseList $phases
    $existing = @($listed.existing)
    $warnings = New-Object System.Collections.Generic.List[string]
    foreach ($w in $listed.warnings) { $warnings.Add($w) }
    $nextN = 1
    if ($existing.Count -gt 0) { $nextN = [int]$existing[-1].n + 1 }
    $mvpMap = Get-MvpMap $vf
    $created = $null

    if ($Apply) {
        if ($Mvp) {
            $destDir = Join-Path $vf 'mvp'
            if (Test-IsReparsePoint (Get-FsItem $destDir)) {
                throw 'MVP_INESPERADO: .vibeflow/mvp não pode ser symlink, junction ou reparse point.'
            }
            $destFile = Join-Path $destDir 'interview.md'
            $createdDir = -not (Test-Path -LiteralPath $destDir)
            if ($createdDir) { New-Item -ItemType Directory -Path $destDir | Out-Null }
            try {
                $fileCreated = New-LiveFile $destFile
            } catch {
                if ($createdDir -and -not (Test-IsReparsePoint (Get-FsItem $destDir)) -and (Test-Path -LiteralPath $destDir) -and -not (Get-ChildItem -LiteralPath $destDir -Force)) {
                    Remove-Item -LiteralPath $destDir -Force
                }
                throw
            }
            if ($fileCreated) { $actions.Add([pscustomobject]@{ op = 'criar_arquivo'; alvo = '.vibeflow/mvp/interview.md' }) }
            $mvpMap = Get-MvpMap $vf
            $created = $mvpMap
        } else {
            $clean = ConvertTo-Slug $Slug
            if ($clean.Length -lt 2) {
                throw 'SLUG_INVALIDO: a frase curta não gerou um slug utilizável.'
            }
            $destDir = Join-Path $phases "phase-$nextN-$clean"
            $destFile = Join-Path $destDir 'interview.md'
            $rel = ".vibeflow/phases/phase-$nextN-$clean"
            if ((Test-IsReparsePoint (Get-FsItem $destDir)) -or (Test-Path -LiteralPath $destDir)) {
                throw "FASE_EXISTE: $rel já existe."
            }
            New-Item -ItemType Directory -Path $destDir | Out-Null
            try {
                $fileCreated = New-LiveFile $destFile
            } catch {
                if (-not (Test-IsReparsePoint (Get-FsItem $destDir)) -and (Test-Path -LiteralPath $destDir) -and -not (Get-ChildItem -LiteralPath $destDir -Force)) {
                    Remove-Item -LiteralPath $destDir -Force
                }
                throw
            }
            if ($fileCreated) { $actions.Add([pscustomobject]@{ op = 'criar_arquivo'; alvo = "$rel/interview.md" }) }
            $created = [pscustomobject]@{
                kind  = 'phase'
                dir   = "phase-$nextN-$clean"
                n     = $nextN
                slug  = $clean
                path  = $rel
                files = @('interview.md')
            }
            $listed = Get-PhaseList $phases
            $existing = @($listed.existing)
            foreach ($w in $listed.warnings) { $warnings.Add($w) }
            $nextN = 1
            if ($existing.Count -gt 0) { $nextN = [int]$existing[-1].n + 1 }
        }
    }

    $mapped = New-Object System.Collections.Generic.List[object]
    foreach ($item in @($existing)) {
        if ($null -ne $item) { [void]$mapped.Add((ConvertTo-PhaseMap $item)) }
    }
    $aberta = ConvertTo-PhaseMap (Get-Aberta $existing)
    $payload = @{
        root     = "$repo"
        rota     = $(if ($Mvp) { 'mvp' } else { 'phase' })
        modo     = $(if ($Mvp) { 'mvp' } else { 'phase' })
        vibeflow = 'ok'
        phases   = "$phState"
        next_n   = [int]$nextN
        existing = $mapped.ToArray()
        aberta   = $aberta
        mvp      = $mvpMap
        alvo     = $(if ($Mvp) { $mvpMap } else { $aberta })
        created  = $created
        actions  = $actions.ToArray()
        avisos   = $warnings.ToArray()
    }
    Write-InterviewReport $vf $payload
}

try {
    Invoke-Interview
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}
