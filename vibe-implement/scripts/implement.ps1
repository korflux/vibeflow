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
# Prefixo do aviso emitido para T* sem linha concluída. A derivação da etapa o reconhece, pois a T* some da fila.
$script:AvisoSemConcluida = 'sem linha concluída'
# Marcas do review.md lidas só para derivar a etapa; o conteúdo semântico do arquivo não é interpretado.
$script:ReviewStatusRe = [regex]::new('^# Status:\s*([^\s]+)\s*$', 'Multiline, IgnoreCase')
$script:OpenBlockerRe = [regex]::new('^\s*- \[ \] R\d+: \*\*(?:Critical|Required)\*\*')
$script:ApproveMarkRe = [regex]::new('^\s*- \[[xX]\] \*\*Approve(?: com defer)?\*\*')
$script:VereditoVigenteRe = [regex]::new('^##\s+Veredito vigente\s*$')
$script:EtapaHeadingRe = [regex]::new('^### Etapa\b')
$script:EtapaVerdictRe = [regex]::new('^\s*- Veredito desta etapa:\s*(.*?)\s*$')
$script:RequestChangesRe = [regex]::new('^Request changes\.?$')

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
            $avisos.Add("$($script:AvisoSemConcluida): $tid")
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

# Conta as correções já aplicadas. Cada etapa com veredito Request changes soma 1; a última não conta
# enquanto houver Critical ou Required em [ ], porque a correção que ela pediu ainda está pendente.
function Get-CorrectionRounds([string[]]$Lines, [bool]$BlockersOpen) {
    $verdicts = New-Object System.Collections.Generic.List[string]
    $inEtapas = $false
    foreach ($line in $Lines) {
        if ($script:EtapaHeadingRe.IsMatch($line)) {
            $verdicts.Add('')
            $inEtapas = $true
        } elseif ($line.StartsWith('## ')) {
            $inEtapas = $false
        } elseif ($inEtapas -and $verdicts[$verdicts.Count - 1] -eq '') {
            $m = $script:EtapaVerdictRe.Match($line)
            if ($m.Success) { $verdicts[$verdicts.Count - 1] = $m.Groups[1].Value }
        }
    }
    $rounds = 0
    foreach ($verdict in $verdicts) {
        if ($script:RequestChangesRe.IsMatch($verdict)) { $rounds++ }
    }
    if ($verdicts.Count -gt 0 -and $script:RequestChangesRe.IsMatch($verdicts[$verdicts.Count - 1]) -and $BlockersOpen) {
        $rounds--
    }
    return $rounds
}

# Indica se o Veredito vigente tem Approve ou Approve com defer marcado; a lista de alternativas do template não conta.
function Test-ApprovalMarked([string[]]$Lines) {
    $inSection = $false
    foreach ($line in $Lines) {
        if ($script:VereditoVigenteRe.IsMatch($line)) {
            $inSection = $true
        } elseif ($line.StartsWith('## ')) {
            $inSection = $false
        } elseif ($inSection -and $script:ApproveMarkRe.IsMatch($line)) {
            return $true
        }
    }
    return $false
}

# Lê as marcas do review.md do alvo. Arquivo ausente devolve $null; ilegível ou sem Status vira aviso e
# legivel=$false, para a etapa não ser inventada. UTF-8 estrito, como o motor Python, para a paridade do ilegível.
function Read-ReviewMarks([string]$Repo, $Alvo, $Warnings) {
    if ($null -eq $Alvo) { return $null }
    $path = Join-Path (Join-Path $Repo ([string]$Alvo.path)) 'review.md'
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { return $null }
    try {
        $text = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false, $true))
    } catch {
        $Warnings.Add('review.md ilegível: etapa não derivada')
        return [pscustomobject]@{ legivel = $false; status = $null; bloqueiosAbertos = $false; aprovacaoMarcada = $false; rodadas = 0 }
    }
    $lines = [string[]]($text -split '\r?\n')
    $statusMatch = $script:ReviewStatusRe.Match($text)
    if (-not $statusMatch.Success) {
        $Warnings.Add("review.md sem '# Status:': etapa não derivada")
    }
    $blockersOpen = $false
    foreach ($line in $lines) {
        if ($script:OpenBlockerRe.IsMatch($line)) { $blockersOpen = $true; break }
    }
    return [pscustomobject]@{
        legivel          = $statusMatch.Success
        status           = if ($statusMatch.Success) { $statusMatch.Groups[1].Value.ToLowerInvariant() } else { $null }
        bloqueiosAbertos = $blockersOpen
        aprovacaoMarcada = (Test-ApprovalMarked $lines)
        rodadas          = (Get-CorrectionRounds $lines $blockersOpen)
    }
}

# Deriva a etapa da phase só de plan e review, na precedência do contrato. Sem fila legível ou com review
# ilegível devolve $null: o coordenador não recebe um chute no lugar de um estado indeterminado.
function Get-Etapa($Fila, $Review) {
    if ($null -eq $Fila -or $Fila.parse -eq 'ausente') { return $null }
    foreach ($aviso in $Fila.avisos) {
        if ($aviso.StartsWith($script:AvisoSemConcluida)) { return $null }
    }
    if ($null -ne $Review) {
        if (-not $Review.legivel) { return $null }
        if ($Review.status -eq 'aprovado') { return 'concluida' }
        if ($Review.bloqueiosAbertos) { return 'corrigir' }
    }
    if (@($Fila.abertas).Count -eq 0) {
        if ($null -ne $Review -and $Review.aprovacaoMarcada) { return 'confirmar' }
        return 'revisar'
    }
    if (@($Fila.elegiveis).Count -gt 0) { return 'implementar' }
    return 'bloqueada'
}

# Serializa alvo, fila, etapa da phase, rodadas de correção e avisos necessários para a execução imediata.
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

    $fila = Get-FilaFromAlvo $repo $alvoItem
    $review = Read-ReviewMarks $repo $alvoItem $warnings
    $payload = @{
        alvo             = ConvertTo-PhaseMap $alvoItem
        fila             = $fila
        etapa            = Get-Etapa $fila $review
        rodadas_correcao = if ($null -ne $review) { [int]$review.rodadas } else { 0 }
        avisos           = $warnings.ToArray()
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
