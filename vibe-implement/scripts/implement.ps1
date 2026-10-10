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
# Mantém stdout e stderr Unicode em UTF-8 também quando capturados por pipe.
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
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
# O veredito conta quando começa com `Request changes`, com marcação `*` ou `_` opcional antes e texto depois,
# porque reviews reais o escrevem assim (`**Request changes**. motivo`). A lista de alternativas do template
# começa com outro valor e não conta. O lookahead recusa só letra ou dígito depois (`_` fecha a marcação).
$script:RequestChangesRe = [regex]::new('^[*_]*Request changes(?![^\W_])')

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
# Confere os mesmos snapshots do motor portátil, sem executar comandos recebidos no plan.
function Test-Snapshot([string]$Repo, $Value) {
    if ($Value -isnot [Collections.IDictionary] -or $Value.Count -ne 4 -or @($Value.Keys | Where-Object { $_ -cnotin @('head','inputs','comando','resultado') }).Count) { return $false }
    if ($Value.resultado -cnotin @('verde','falha') -or $Value.comando -isnot [string] -or -not $Value.comando.Trim() -or $Value.head -isnot [string] -or $Value.head -cnotmatch '^(?:[a-f0-9]{40}|[a-f0-9]{64})$') { return $false }
    if ($Value.inputs -isnot [Collections.IDictionary] -or $Value.inputs.Count -eq 0 -or -not (Get-Command git -ErrorAction SilentlyContinue)) { return $false }
    & git -C $Repo merge-base --is-ancestor $Value.head HEAD 2>$null
    if ($LASTEXITCODE -ne 0) { return $false }
    foreach ($relative in $Value.inputs.Keys) {
        $expected = $Value.inputs[$relative]
        if ($relative -isnot [string] -or -not $relative -or $relative.Contains('\') -or $relative.StartsWith('-') -or [IO.Path]::IsPathRooted($relative) -or $relative.Contains(':') -or @($relative.Split('/') | Where-Object { $_ -in @('', '.', '..') }).Count -or $expected -isnot [string] -or $expected -cnotmatch '^(?:[a-f0-9]{40}|[a-f0-9]{64})$') { return $false }
        $candidate = Join-Path $Repo $relative
        $item = Get-FsItem $candidate
        if ($item -isnot [IO.FileInfo]) { return $false }
        while ($candidate -ne $Repo) {
            if (Test-IsReparsePoint (Get-FsItem $candidate)) { return $false }
            $candidate = [IO.Path]::GetDirectoryName($candidate)
            if (-not $candidate) { return $false }
        }
        $actual = & git -C $Repo hash-object -- $relative 2>$null
        if ($LASTEXITCODE -ne 0 -or $actual -cne $expected) { return $false }
    }
    return $true
}

# Extrai exatamente um registro JSON; duplicação ou ausência é estado indeterminado.
function Get-ExecutionField([string[]]$Lines, [string]$Name) {
    $prefix = "- **${Name}:** "
    $found = @($Lines | ForEach-Object { $line = $_.Trim(); if ($line.StartsWith($prefix)) { $line.Substring($prefix.Length) } })
    if ($found.Count -ne 1) { throw "campo $Name ausente ou duplicado" }
    try { return ConvertFrom-Json -InputObject $found[0] -AsHashtable } catch { throw "campo $Name JSON inválido" }
}

# Encontra o commit efetivo posterior à prova; declaração no plan não equivale a sucesso de Git.
function Get-IntegrationCommit([string]$Repo, [string[]]$Tasks, $Proof, $Origin = $null) {
    if ($Proof -isnot [Collections.IDictionary] -or -not (Get-Command git -ErrorAction SilentlyContinue)) { return $null }
    if ($null -eq $Origin) { $Origin = $Proof.head }
    if ($Origin -isnot [string] -or $Origin -cnotmatch '^(?:[a-f0-9]{40}|[a-f0-9]{64})$') { return $null }
    & git -C $Repo merge-base --is-ancestor $Origin $Proof.head 2>$null
    if ($LASTEXITCODE -ne 0) { return $null }
    $history = @(& git -C $Repo log '--format=%H %s' 2>$null)
    if ($LASTEXITCODE -ne 0) { return $null }
    $prefix = 'task(' + ($Tasks -join ',') + '): '
    foreach ($line in $history) {
        $split = $line.IndexOf(' ')
        if ($split -lt 0) { continue }
        $sha = $line.Substring(0, $split)
        if (-not $line.Substring($split + 1).StartsWith($prefix) -or $sha -eq $Origin) { continue }
        & git -C $Repo merge-base --is-ancestor $Origin $sha 2>$null
        if ($LASTEXITCODE -eq 0) { return $sha }
    }
    return $null
}

# Recusa ciclos e dependências inexistentes independentemente do estado implementado.
function Test-ExecutionDependency([string]$Id, $Tasks, $Active, $Visited) {
    if ($Active.Contains($Id)) { throw 'ciclo de dependências' }
    if ($Visited.Contains($Id)) { return }
    [void]$Active.Add($Id)
    foreach ($dep in $Tasks[$Id].deps) {
        if (-not $Tasks.Contains($dep)) { throw "dependência inexistente: $dep" }
        Test-ExecutionDependency $dep $Tasks $Active $Visited
    }
    [void]$Active.Remove($Id)
    [void]$Visited.Add($Id)
}

# Projeta somente o protocolo explícito e preserva leitura histórica e Modo B.
function Get-ExecutionFromPlan([string]$Repo, $Alvo, $Fila) {
    if ($null -eq $Alvo -or $null -eq $Fila) { return $null }
    $text = [IO.File]::ReadAllText((Join-Path $Repo ($Alvo.path + '/plan.md')))
    $protocols = @([regex]::Matches($text, '(?m)^# Protocolo:\s*(.*?)\s*$') | ForEach-Object { $_.Groups[1].Value })
    if ($protocols.Count -eq 0) { return $null }
    $modes = @([regex]::Matches($text, '(?m)^# Modo:\s*(.*?)\s*$') | ForEach-Object { $_.Groups[1].Value })
    $errors = [Collections.Generic.List[string]]::new()
    $result = @{ protocolo = $protocols[0]; modo = if ($modes.Count) { $modes[0] } else { $null }; tasks = @(); integracao = $null; avisos = $errors }
    if ($protocols.Count -ne 1 -or $protocols[0] -cne 'etapas-v1' -or $modes.Count -ne 1 -or $modes[0] -cnotin @('A','B')) { $errors.Add('protocolo ou modo de execução inválido'); return $result }
    if ($modes[0] -eq 'B') { return $result }
    try {
        if ($Fila.parse -ne 'ok') { throw 'fila incompleta ou inválida' }
        $tasks = [ordered]@{}
        $sections = [regex]::Matches($text, '(?ms)^### (T\d+):[^\r\n]*\r?\n(.*?)(?=^### T\d+:|\z)')
        if ($sections.Count -eq 0) { throw 'fila incompleta ou inválida' }
        foreach ($section in $sections) {
            $tid = $section.Groups[1].Value
            if ($tasks.Contains($tid)) { throw 'T* duplicada' }
            $lines = $section.Groups[2].Value -split '\r?\n'
            $deps = @($lines | ForEach-Object { if ($_.Trim() -cmatch '^- \*\*Deps:\*\*\s*(.*)$') { $Matches[1] } })
            $done = @($lines | ForEach-Object { if ($_.Trim() -cmatch "^- \[([ xX])\] $tid concluída\s*$") { $Matches[1] } })
            if ($deps.Count -ne 1 -or $done.Count -ne 1 -or $deps[0] -cnotmatch '^(?:nenhuma|T[1-9]\d*(?:[ ,]+T[1-9]\d*)*)$') { throw "conclusão ou Deps inválida: $tid" }
            $state = Get-ExecutionField $lines 'Execução'
            if ($state -isnot [Collections.IDictionary] -or $state.Count -ne 2 -or @($state.Keys | Where-Object { $_ -cnotin @('estado','local') }).Count -or $state.estado -cnotin @('pendente','implementada')) { throw "registro de execução inválido: $tid" }
            if ($state.estado -eq 'implementada' -and $state.local -isnot [Collections.IDictionary]) { throw "snapshot local ausente: $tid" }
            if ($state.estado -eq 'pendente' -and $null -ne $state.local) { throw "snapshot local inesperado: $tid" }
            $tasks[$tid] = @{ id = $tid; estado = $state.estado; local_valida = (Test-Snapshot $Repo $state.local) -and $state.local.resultado -eq 'verde'; deps = @((ConvertFrom-DepsValue $deps[0])); done = $done[0] -ne ' ' }
        }
        $active = [Collections.Generic.HashSet[string]]::new()
        $visited = [Collections.Generic.HashSet[string]]::new()
        foreach ($tid in $tasks.Keys) { Test-ExecutionDependency $tid $tasks $active $visited }
        $prefix = ($text -split '(?m)^## Tasks', 2)[0] -split '\r?\n'
        $integration = Get-ExecutionField $prefix 'Integração'
        if ($integration -isnot [Collections.IDictionary] -or $integration.Count -notin @(3,4) -or @('testes','prova','commit' | Where-Object { -not $integration.Contains($_) }).Count -or @($integration.Keys | Where-Object { $_ -cnotin @('testes','prova','commit','origem') }).Count -or $integration.testes -cnotin @('pendentes','prontos') -or $integration.commit -cnotin @('pendente','registrado')) { throw 'registro de integração inválido' }
        if ($null -ne $integration.origem -and ($integration.origem -isnot [string] -or $integration.origem -cnotmatch '^(?:[a-f0-9]{40}|[a-f0-9]{64})$')) { throw 'origem da integração inválida' }
        $valid = Test-Snapshot $Repo $integration.prova
        $ordered = @($tasks.Keys | Sort-Object { [int]$_.Substring(1) })
        $result.tasks = @($ordered | ForEach-Object { $tasks[$_] })
        $integration.prova_valida = $valid
        $integration.commit_encontrado = if ($valid -and $integration.commit -eq 'registrado') { Get-IntegrationCommit $Repo $ordered $integration.prova $integration.origem } else { $null }
        $result.integracao = $integration
        $ready = @($ordered | Where-Object { $tasks[$_].done -or ($tasks[$_].estado -eq 'implementada' -and $tasks[$_].local_valida) })
        $pending = @($ordered | Where-Object { $_ -notin $ready })
        $Fila.elegiveis = @($pending | Where-Object { @($tasks[$_].deps | Where-Object { $_ -notin $ready }).Count -eq 0 })
        $Fila.bloqueadas = @($pending | Where-Object { $_ -notin $Fila.elegiveis } | ForEach-Object { @{ id = $_; deps = @($tasks[$_].deps | Where-Object { $_ -notin $ready }) } })
    } catch { $errors.Add($_.Exception.Message); $Fila.elegiveis = @() }
    return $result
}

# Mantém implementação, complemento de testes, validação e commit como etapas independentes.
function Get-ExecutionEtapa($Fila, $Review, $Execution) {
    if ($Execution.avisos.Count) { return $null }
    if ($Execution.modo -eq 'B') { return Get-Etapa $Fila $Review }
    if ($null -ne $Review -and -not $Review.legivel) { return $null }
    if ($null -ne $Review -and $Review.bloqueiosAbertos) { return 'corrigir' }
    if (@($Execution.tasks | Where-Object { -not $_.done -and ($_.estado -ne 'implementada' -or -not $_.local_valida) }).Count) {
        if (@($Fila.elegiveis).Count) { return 'implementar' }
        return 'bloqueada'
    }
    $integration = $Execution.integracao
    if ($integration.testes -ne 'prontos') { return 'testar' }
    if (-not $integration.prova_valida) { return 'validar' }
    if ($integration.prova.resultado -ne 'verde') { return 'corrigir_validacao' }
    if (-not $integration.commit_encontrado -or @($Fila.abertas).Count) { return 'commitar_integracao' }
    return Get-Etapa $Fila $Review
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
    $execution = Get-ExecutionFromPlan $repo $alvoItem $fila
    $payload = @{
        alvo             = ConvertTo-PhaseMap $alvoItem
        fila             = $fila
        etapa            = if ($null -ne $execution) { Get-ExecutionEtapa $fila $review $execution } else { Get-Etapa $fila $review }
        rodadas_correcao = if ($null -ne $review) { [int]$review.rodadas } else { 0 }
        avisos           = $warnings.ToArray()
    }
    if ($null -ne $execution) { $payload.execucao = $execution }
    if ($Mvp) { $payload.analyze_gate = $analyzeGate }
    Write-ImplementOutput $payload
}

try {
    Invoke-Implement
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}
