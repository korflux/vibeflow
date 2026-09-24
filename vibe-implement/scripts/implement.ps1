#Requires -Version 7.0
# vibe-implement/scripts/implement.ps1
# Seleciona alvo e fila do plan sem criar artefato de execução.
param(
    [string]$Root,
    [switch]$Apply,
    [string]$Slug,
    [string]$Dir,
    [switch]$Mvp
)

$ErrorActionPreference = 'Stop'
$script:SlugWasBound = $PSBoundParameters.ContainsKey('Slug')
$script:DirWasBound = $PSBoundParameters.ContainsKey('Dir')
$script:ChainFiles = @('interview.md', 'spec.md', 'plan.md', 'analyze.md', 'review.md')
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

# Resolve a raiz por parâmetro, Git ou cwd sem exigir que Git esteja instalado.
function Get-RepoRoot {
    if ($Root) { return (Resolve-Path -LiteralPath $Root).Path }
    if (Get-Command git -ErrorAction SilentlyContinue) {
        $git = & git rev-parse --show-toplevel 2>$null
        if ($LASTEXITCODE -eq 0 -and $git) { return $git.Trim() }
    }
    return (Get-Location).Path
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

# Representa o alvo MVP sem inferir a rota a partir dos artefatos existentes.
function Get-MvpMap([string]$Vf) {
    $mvpPath = Join-Path $Vf 'mvp'
    $item = Get-FsItem $mvpPath
    if (-not $item) { return $null }
    if (Test-IsReparsePoint $item) { throw 'MVP_INESPERADO: .vibeflow/mvp não pode ser symlink, junction ou reparse point.' }
    if (-not $item.PSIsContainer) { throw 'MVP_INESPERADO: .vibeflow/mvp existe, mas não é um diretório.' }
    $files = New-Object System.Collections.Generic.List[string]
    foreach ($name in $script:ChainFiles) {
        if (Test-Path -LiteralPath (Join-Path $mvpPath $name) -PathType Leaf) { [void]$files.Add($name) }
    }
    return [pscustomobject]@{ kind = 'mvp'; dir = 'mvp'; path = '.vibeflow/mvp'; files = @($files) }
}

# Extrai somente status e veredito do analyze MVP para bloquear implementação prematura.
function Get-AnalyzeGate([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return [pscustomobject]@{ status = 'ausente'; veredito = 'ausente'; pronto = $false }
    }
    $text = [System.IO.File]::ReadAllText($Path)
    $statusMatch = [regex]::Match($text, '(?im)^# Status:\s*([^\s]+)\s*$')
    $verdictMatch = [regex]::Match($text, '(?im)^## Veredito\s*\r?\n+\s*(limpo|bloqueado)\s*$')
    $status = if ($statusMatch.Success) { $statusMatch.Groups[1].Value.ToLowerInvariant() } else { 'ausente' }
    $veredito = if ($verdictMatch.Success) { $verdictMatch.Groups[1].Value.ToLowerInvariant() } else { 'ausente' }
    return [pscustomobject]@{ status = $status; veredito = $veredito; pronto = ($status -eq 'aprovado' -and $veredito -eq 'limpo') }
}

# Maior n com plan.md: é a fila desta skill sem -Dir.
function Get-AlvoComPlan($Existing) {
    foreach ($item in ($Existing | Sort-Object n -Descending)) {
        if ($item.files -contains 'plan.md') { return $item }
    }
    return $null
}

# Projeta apenas os identificadores do alvo, sem serializar o inventário de fases.
function ConvertTo-PhaseMap($Item) {
    if ($null -eq $Item) { return $null }
    $map = [ordered]@{ kind = [string]$Item.kind; dir = [string]$Item.dir }
    if ($Item.PSObject.Properties['n']) { $map.n = [int]$Item.n }
    if ($Item.PSObject.Properties['slug']) { $map.slug = [string]$Item.slug }
    $map.path = [string]$Item.path
    return [pscustomobject]$map
}

# Resolve -Dir explícito ou seleciona a fase mais recente que possui plan.md.
function Get-ImplementAlvoComDir($Existing, [string]$Phases) {
    if (-not [string]::IsNullOrWhiteSpace($Dir)) {
        $destName = [System.IO.Path]::GetFileName($Dir)
        $destDir = Join-Path $Phases $destName
        $destItem = Get-FsItem $destDir
        if (-not $destItem -or (Test-IsReparsePoint $destItem) -or -not $destItem.PSIsContainer) {
            throw "FASE_AUSENTE: .vibeflow/phases/$destName não é uma pasta de fase."
        }
        if (-not [regex]::IsMatch($destName, '^phase-(\d+)-([a-z0-9]+(?:-[a-z0-9]+)*)$')) {
            throw "FASE_AUSENTE: $destName não é uma pasta de fase."
        }
        foreach ($item in $Existing) {
            if ($item.dir -eq $destName) {
                return $item
            }
        }
        throw "FASE_AUSENTE: .vibeflow/phases/$destName não é uma pasta de fase."
    }
    return Get-AlvoComPlan $Existing
}

# Extrai ids T* da linha Deps. "nenhuma", vazio ou ausência viram lista vazia. Sempre List, para não iterar caractere.
function ConvertFrom-DepsValue([string]$Raw) {
    $found = New-Object System.Collections.Generic.List[string]
    $text = if ($null -eq $Raw) { '' } else { $Raw.Trim() }
    if ($text -eq '' -or $text.ToLowerInvariant() -eq 'nenhuma') { return $found }
    $seen = New-Object 'System.Collections.Generic.HashSet[string]'
    foreach ($m in [regex]::Matches($text, 'T(\d+)')) {
        $token = "T$($m.Groups[1].Value)"
        if ($seen.Add($token)) { [void]$found.Add($token) }
    }
    return $found
}

# Lê só concluída + Deps. Não interpreta Status, aceite ou texto livre.
function ConvertFrom-PlanFila([string]$Text) {
    $avisos = New-Object System.Collections.Generic.List[string]
    $headingRe = [regex]'^### T(\d+):'
    $doneRe = [regex]'^- \[([ xX])\] T(\d+) concluída\s*$'
    $depsRe = [regex]'^- \*\*Deps:\*\*\s*(.*)$'
    $sections = New-Object System.Collections.Generic.List[object]
    $currentId = $null
    $currentLines = New-Object System.Collections.Generic.List[string]
    foreach ($line in ($Text -split '\r?\n')) {
        $head = $headingRe.Match($line)
        if ($head.Success) {
            if ($null -ne $currentId) {
                $sections.Add([pscustomobject]@{ id = $currentId; lines = @($currentLines) })
            }
            $currentId = "T$($head.Groups[1].Value)"
            $currentLines = New-Object System.Collections.Generic.List[string]
            continue
        }
        if ($null -ne $currentId) { [void]$currentLines.Add($line) }
    }
    if ($null -ne $currentId) {
        $sections.Add([pscustomobject]@{ id = $currentId; lines = @($currentLines) })
    }
    if ($sections.Count -eq 0) {
        return [pscustomobject]@{
            parse      = 'ausente'
            concluidas = [string[]]@()
            abertas    = [string[]]@()
            elegiveis  = [string[]]@()
            bloqueadas = @()
            avisos     = [string[]]@()
        }
    }

    $parsed = New-Object System.Collections.Generic.List[object]
    $seenIds = New-Object 'System.Collections.Generic.HashSet[string]'
    foreach ($sec in $sections) {
        $tid = [string]$sec.id
        if (-not $seenIds.Add($tid)) {
            $avisos.Add("T* duplicada ignorada: $tid")
            continue
        }
        $done = $null
        $depsRaw = $null
        foreach ($rawLine in @($sec.lines)) {
            $stripped = $rawLine.Trim()
            if ($null -eq $done) {
                $dm = $doneRe.Match($stripped)
                if ($dm.Success -and ("T$($dm.Groups[2].Value)" -eq $tid)) {
                    $done = $dm.Groups[1].Value -ne ' '
                }
            }
            if ($null -eq $depsRaw) {
                $depM = $depsRe.Match($stripped)
                if ($depM.Success) { $depsRaw = $depM.Groups[1].Value }
            }
        }
        if ($null -eq $done) {
            $avisos.Add("sem linha concluída: $tid")
            continue
        }
        $depIds = New-Object System.Collections.Generic.List[string]
        foreach ($dep in (ConvertFrom-DepsValue $depsRaw)) { [void]$depIds.Add([string]$dep) }
        $parsed.Add([pscustomobject]@{
            id   = $tid
            n    = [int]($tid.Substring(1))
            done = [bool]$done
            deps = $depIds
        })
    }

    $known = New-Object 'System.Collections.Generic.HashSet[string]'
    foreach ($item in $parsed) { [void]$known.Add([string]$item.id) }
    $concluidas = @($parsed | Where-Object { $_.done } | Sort-Object n | ForEach-Object { [string]$_.id })
    $abertas = @($parsed | Where-Object { -not $_.done } | Sort-Object n | ForEach-Object { [string]$_.id })
    $doneSet = New-Object 'System.Collections.Generic.HashSet[string]'
    foreach ($cid in $concluidas) { [void]$doneSet.Add([string]$cid) }
    $elegiveis = New-Object System.Collections.Generic.List[string]
    $bloqueadas = New-Object System.Collections.Generic.List[object]
    foreach ($item in ($parsed | Where-Object { -not $_.done } | Sort-Object n)) {
        $phantom = New-Object System.Collections.Generic.List[string]
        $unmet = New-Object System.Collections.Generic.List[string]
        foreach ($dep in $item.deps) {
            $depId = [string]$dep
            if (-not $known.Contains($depId)) { [void]$phantom.Add($depId) }
            if (-not $doneSet.Contains($depId)) { [void]$unmet.Add($depId) }
        }
        if ($phantom.Count -gt 0) {
            $avisos.Add("dep inexistente em $($item.id): $($phantom -join ', ')")
            $bloqueadas.Add([pscustomobject]@{ id = [string]$item.id; deps = $item.deps.ToArray() })
            continue
        }
        if ($unmet.Count -gt 0) {
            $bloqueadas.Add([pscustomobject]@{ id = [string]$item.id; deps = $unmet.ToArray() })
        } else {
            [void]$elegiveis.Add([string]$item.id)
        }
    }
    $parse = if ($avisos.Count -gt 0) { 'parcial' } else { 'ok' }
    return [pscustomobject]@{
        parse      = $parse
        concluidas = $concluidas
        abertas    = $abertas
        elegiveis  = $elegiveis.ToArray()
        bloqueadas = $bloqueadas.ToArray()
        avisos     = $avisos.ToArray()
    }
}

# Projeta a fila do plan do alvo. Sem plan.md, a skill avulsa não recebe fila.
function Get-FilaFromAlvo([string]$Repo, $Alvo) {
    if ($null -eq $Alvo) { return $null }
    $path = Join-Path (Join-Path $Repo ([string]$Alvo.path)) 'plan.md'
    if (-not (Test-Path -LiteralPath $path)) { return $null }
    $text = [System.IO.File]::ReadAllText($path)
    return ConvertFrom-PlanFila $text
}

# Serializa alvo, fila e avisos necessários para a execução imediata.
function Write-ImplementOutput([hashtable]$Payload) {
    $json = [string](ConvertTo-Json -InputObject $Payload -Depth 8)
    [Console]::Out.WriteLine($json)
}

# Seleciona alvo e fila; Apply só cria uma phase quando há slug explícito.
function Invoke-Implement {
    if ($Mvp -and ($script:SlugWasBound -or $script:DirWasBound)) {
        throw 'MODO_INVALIDO: o alvo MVP não aceita -Slug nem -Dir.'
    }

    $repo = Get-RepoRoot
    $vf = Join-Path $repo '.vibeflow'
    $phases = Join-Path $vf 'phases'
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
        $phState = 'ok'
    }

    $listed = Get-PhaseList $phases
    $existing = @($listed.existing)
    $warnings = New-Object System.Collections.Generic.List[string]
    foreach ($w in $listed.warnings) { $warnings.Add($w) }
    $nextN = 1
    if ($existing.Count -gt 0) { $nextN = [int]$existing[-1].n + 1 }
    $alvoItem = Get-ImplementAlvoComDir $existing $phases
    $mvpMap = Get-MvpMap $vf
    if ($Mvp -and ($null -eq $mvpMap -or $mvpMap.files -notcontains 'plan.md')) {
        throw 'IMPLEMENT_SEM_PLAN: falta .vibeflow/mvp/plan.md.'
    }
    if ($Mvp) {
        $alvoItem = $mvpMap
    }
    $analyzeGate = if ($Mvp) { Get-AnalyzeGate (Join-Path (Join-Path $vf 'mvp') 'analyze.md') } else { $null }

    if ($Apply) {
        if ($Mvp) {
            if ($analyzeGate.status -eq 'ausente' -and $analyzeGate.veredito -eq 'ausente') {
                throw 'IMPLEMENT_ANALYZE_AUSENTE: falta .vibeflow/mvp/analyze.md.'
            }
            if ($analyzeGate.status -ne 'aprovado') {
                throw 'IMPLEMENT_ANALYZE_RASCUNHO: analyze MVP não está aprovado.'
            }
            if ($analyzeGate.veredito -ne 'limpo') {
                throw 'IMPLEMENT_ANALYZE_BLOQUEADO: analyze MVP não está limpo.'
            }
        }
        if (-not $Mvp -and [string]::IsNullOrWhiteSpace($Dir) -and $null -eq $alvoItem) {
            if ([string]::IsNullOrWhiteSpace($Slug)) {
                throw 'IMPLEMENT_SEM_ALVO: sem fase alvo; passe -Slug para abrir uma pasta nova.'
            }
            $clean = ConvertTo-Slug $Slug
            if ($clean.Length -lt 2) {
                throw 'SLUG_INVALIDO: a frase curta não gerou um slug utilizável.'
            }
            $destDir = Join-Path $phases "phase-$nextN-$clean"
            if ((Test-IsReparsePoint (Get-FsItem $destDir)) -or (Test-Path -LiteralPath $destDir)) {
                throw "FASE_EXISTE: .vibeflow/phases/phase-$nextN-$clean já existe."
            }
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            $name = [System.IO.Path]::GetFileName($destDir)
            $alvoItem = [pscustomobject]@{
                kind  = 'phase'
                dir   = $name
                n     = [int]$nextN
                slug  = $clean
                path  = ".vibeflow/phases/$name"
                files = @()
            }
        }
    }

    $payload = @{
        alvo   = ConvertTo-PhaseMap $alvoItem
        fila   = Get-FilaFromAlvo $repo $alvoItem
        avisos         = $warnings.ToArray()
    }
    if ($Mvp) { $payload.analyze_gate = $analyzeGate }
    Write-ImplementOutput $payload
}

try {
    Invoke-Implement
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}
