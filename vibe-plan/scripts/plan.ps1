#Requires -Version 7.0
# vibe-plan/scripts/plan.ps1
# Inventário de .vibeflow/phases → prepara phase-N-slug/plan.md.
param(
    [string]$Root,
    [switch]$Apply,
    [string]$Dir,
    [switch]$Mvp
)

$ErrorActionPreference = 'Stop'
$script:DirWasBound = $PSBoundParameters.ContainsKey('Dir')
$script:ChainFiles = @('interview.md', 'spec.md', 'plan.md', 'analyze.md', 'implement.md', 'review.md')

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
function Assert-PlanGitignore([string]$Vf) {
    $gi = Join-Path $Vf '.gitignore'
    Add-GitignoreEntry $gi 'plan-report.json'
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

# Representa o alvo MVP sem inferir a rota a partir dos artefatos existentes.
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
    return [pscustomobject]@{ kind = 'mvp'; dir = 'mvp'; path = '.vibeflow/mvp'; files = @($files) }
}

# Maior n com spec e sem plan: o plan deve reusar esta pasta.
function Get-SpecPendente($Existing) {
    foreach ($item in ($Existing | Sort-Object n -Descending)) {
        if ($item.files -contains 'spec.md' -and $item.files -notcontains 'plan.md') {
            return $item
        }
    }
    return $null
}

# Maior n com plan e sem analyze: rascunho ainda atualizável.
function Get-Rascunho($Existing) {
    foreach ($item in ($Existing | Sort-Object n -Descending)) {
        if ($item.files -contains 'plan.md' -and $item.files -notcontains 'analyze.md') {
            return $item
        }
    }
    return $null
}

# Destino preferido: spec pendente, senão rascunho. Sem alvo = não há o que gravar.
function Get-Alvo($Existing) {
    $pending = Get-SpecPendente $Existing
    if ($null -ne $pending) { return @{ item = $pending; modo = 'reuse' } }
    $draft = Get-Rascunho $Existing
    if ($null -ne $draft) { return @{ item = $draft; modo = 'atualizar' } }
    return @{ item = $null; modo = 'criar' }
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

# Converte o objeto da fase para PSCustomObject (hashtable enumeraria no JSON).
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
function Write-PlanReport([string]$Vf, [hashtable]$Payload) {
    $reportPath = Join-Path $Vf 'plan-report.json'
    $json = [string](ConvertTo-Json -InputObject $Payload -Depth 8)
    $utf8 = New-Object System.Text.UTF8Encoding $false
    Assert-SafeOperationalFile $reportPath 'RELATORIO_INESPERADO'
    [System.IO.File]::WriteAllText($reportPath, $json, $utf8)
    Write-Output $reportPath
}

# Inventaria o disco e prepara o arquivo vivo no apply.
function Invoke-Plan {
    if ($Mvp -and $script:DirWasBound) {
        throw 'MODO_INVALIDO: o alvo MVP não aceita -Dir.'
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

    Assert-PlanGitignore $vf
    $listed = Get-PhaseList $phases
    $existing = @($listed.existing)
    $warnings = New-Object System.Collections.Generic.List[string]
    foreach ($w in $listed.warnings) { $warnings.Add($w) }
    $nextN = 1
    if ($existing.Count -gt 0) { $nextN = [int]$existing[-1].n + 1 }
    $resolved = Get-Alvo $existing
    $alvoItem = $resolved.item
    $modoSugerido = $resolved.modo
    $mvpMap = Get-MvpMap $vf
    if ($Mvp -and ($null -eq $mvpMap -or $mvpMap.files -notcontains 'spec.md')) {
        throw 'PLAN_SEM_SPEC: falta .vibeflow/mvp/spec.md. Rode /vibe-spec primeiro.'
    }
    $created = $null
    $modo = $null

    if ($Apply) {
        if ($Mvp) {
            $destDir = Join-Path $vf 'mvp'
            $modo = if (Test-Path -LiteralPath (Join-Path $destDir 'plan.md') -PathType Leaf) { 'atualizar' } else { 'reuse' }
        } elseif (-not [string]::IsNullOrWhiteSpace($Dir)) {
            $destDir = Join-Path $phases ([System.IO.Path]::GetFileName($Dir))
            $destName = [System.IO.Path]::GetFileName($destDir)
            $destItem = Get-FsItem $destDir
            if (-not $destItem -or (Test-IsReparsePoint $destItem) -or -not $destItem.PSIsContainer) {
                throw "FASE_AUSENTE: .vibeflow/phases/$destName não é uma pasta de fase."
            }
            if (-not [regex]::IsMatch($destName, '^phase-(\d+)-([a-z0-9]+(?:-[a-z0-9]+)*)$')) {
                throw "FASE_AUSENTE: $destName não é uma pasta de fase."
            }
            $modo = if (Test-Path -LiteralPath (Join-Path $destDir 'plan.md')) { 'atualizar' } else { 'reuse' }
        } elseif ($null -ne $alvoItem) {
            $destDir = Join-Path $repo $alvoItem.path
            $modo = $modoSugerido
        } else {
            throw 'PLAN_SEM_SPEC: sem spec.md numa fase. Rode /vibe-spec primeiro.'
        }

        $destName = [System.IO.Path]::GetFileName($destDir)
        if (-not (Test-Path -LiteralPath (Join-Path $destDir 'spec.md'))) {
            throw "PLAN_SEM_SPEC: $destName não tem spec.md. Rode /vibe-spec primeiro."
        }
        if (Test-Path -LiteralPath (Join-Path $destDir 'analyze.md')) {
            throw "PLAN_JA_ANALISADO: $destName já tem analyze.md. Não pise. Pedido novo = outra phase."
        }

        $destFile = Join-Path $destDir 'plan.md'
        $rel = if ($Mvp) { '.vibeflow/mvp' } else { ".vibeflow/phases/$destName" }
        $fileCreated = New-LiveFile $destFile
        if ($fileCreated) { $actions.Add([pscustomobject]@{ op = 'criar_arquivo'; alvo = "$rel/plan.md" }) }
        if ($Mvp) {
            $mvpMap = Get-MvpMap $vf
            $created = $mvpMap
        } else {
            $listed = Get-PhaseList $phases
            $existing = @($listed.existing)
            foreach ($w in $listed.warnings) { $warnings.Add($w) }
            $nextN = 1
            if ($existing.Count -gt 0) { $nextN = [int]$existing[-1].n + 1 }
            $resolved = Get-Alvo $existing
            $alvoItem = $resolved.item
            $modoSugerido = $resolved.modo
            foreach ($item in $existing) {
                if ($item.dir -eq $destName) { $created = $item; break }
            }
        }
    }

    $mapped = New-Object System.Collections.Generic.List[object]
    foreach ($item in @($existing)) {
        if ($null -ne $item) { [void]$mapped.Add((ConvertTo-PhaseMap $item)) }
    }
    $payload = @{
        root               = "$repo"
        rota               = $(if ($Mvp) { 'mvp' } else { 'phase' })
        vibeflow           = 'ok'
        phases             = "$phState"
        next_n             = [int]$nextN
        existing           = $mapped.ToArray()
        spec_pendente      = ConvertTo-PhaseMap (Get-SpecPendente $existing)
        rascunho           = ConvertTo-PhaseMap (Get-Rascunho $existing)
        alvo               = $(if ($Mvp) { $mvpMap } else { ConvertTo-PhaseMap $alvoItem })
        mvp                = $mvpMap
        modo_sugerido      = $(if ($Mvp -and $mvpMap.files -contains 'plan.md') { 'atualizar' } elseif ($Mvp) { 'reuse' } else { "$modoSugerido" })
        created            = $(if ($Mvp) { $created } else { ConvertTo-PhaseMap $created })
        modo               = $modo
        actions            = $actions.ToArray()
        avisos             = $warnings.ToArray()
    }
    Write-PlanReport $vf $payload
}

try {
    Invoke-Plan
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}
