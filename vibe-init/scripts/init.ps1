#Requires -Version 7.0
# vibe-init/scripts/init.ps1
# Inventário → old verificado → matriz → scan factual → init-report.json.
# Symlink de ponteiro só com merge já fechado (ou -ApplyPointers após a IA unir).
param(
    [string]$Root,
    [switch]$ApplyPointers,
    [string]$MergeToken,
    [ValidateSet('AGENTS', 'CLAUDE')]
    [string]$RedirectPointer,
    [switch]$StopAfterOld
)

$ErrorActionPreference = 'Stop'
$script:EvidenceWarnings = New-Object System.Collections.Generic.List[string]
# Estado vivo da run, para que uma falha depois da primeira escrita ainda produza relatório.
$script:Partial = $null

# --- paths e bytes -----------------------------------------------------------

# Resolve a raiz por parâmetro, Git ou cwd sem exigir que Git esteja instalado.
function Get-RepoRoot {
    if ($Root) { return (Resolve-Path -LiteralPath $Root).Path }
    # Usa o Git somente quando instalado; repositórios sem Git continuam suportados pelo cwd.
    if (Get-Command git -ErrorAction SilentlyContinue) {
        $git = & git rev-parse --show-toplevel 2>$null
        if ($LASTEXITCODE -eq 0 -and $git) { return $git.Trim() }
    }
    return (Get-Location).Path
}

# Localiza template e recursos a partir do diretório estável do próprio script.
function Get-SkillDir {
    return (Split-Path -Parent $PSScriptRoot)
}

# Calcula o hash usado para validar backups e fontes de merge.
function Get-Sha256File([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

# Compara tamanho e SHA-256 sem normalizar conteúdo do usuário.
function Test-SameBytes([string]$A, [string]$B) {
    if (-not (Test-Path -LiteralPath $A) -or -not (Test-Path -LiteralPath $B)) { return $false }
    $ia = Get-Item -LiteralPath $A -Force
    $ib = Get-Item -LiteralPath $B -Force
    if ($ia.Length -ne $ib.Length) { return $false }
    return (Get-Sha256File $A) -eq (Get-Sha256File $B)
}

# Obtém inclusive symlinks quebrados e itens ocultos sem transformar ausência em exceção.
function Get-FsItem([string]$Path) {
    return Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
}

# Reconhece symlinks pelas propriedades disponíveis nas versões suportadas do PowerShell.
function Test-IsSymlink($Item) {
    if (-not $Item) { return $false }
    return $Item.Attributes.ToString() -match 'ReparsePoint' -or $Item.LinkType -eq 'SymbolicLink'
}

# Compara caminhos conforme a semântica do sistema, sensível a caixa em Unix.
function Test-SamePath([string]$A, [string]$B) {
    $comparison = if ($IsWindows -or $env:OS -match 'Windows') {
        [StringComparison]::OrdinalIgnoreCase
    } else {
        [StringComparison]::Ordinal
    }
    return [string]::Equals($A, $B, $comparison)
}

# Normaliza o alvo exposto pelo PowerShell para uma única string comparável.
function Get-LinkTargetString($Item) {
    $t = $Item.Target
    if ($null -eq $t) { return $null }
    if ($t -is [array]) { return [string]$t[0] }
    return [string]$t
}

# Resolve alvos absolutos ou relativos sem exigir que o destino exista.
function Resolve-MaybeRelative([string]$BaseDir, [string]$Target) {
    if ([string]::IsNullOrWhiteSpace($Target)) { return $null }
    if ([System.IO.Path]::IsPathRooted($Target)) {
        return [System.IO.Path]::GetFullPath($Target)
    }
    return [System.IO.Path]::GetFullPath((Join-Path $BaseDir $Target))
}

# Lê conteúdo operacional integral que deve ser preservado byte a byte no backup.
function Get-Text([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    return [System.IO.File]::ReadAllText($Path)
}

# Lê somente evidências pequenas; arquivos do projeto não podem consumir memória sem limite no scan.
function Get-EvidenceText([string]$Path, [int64]$MaxBytes = 1048576) {
    $item = Get-FsItem $Path
    if (-not $item -or $item.PSIsContainer) { return $null }
    if ($item.Length -gt $MaxBytes) {
        [void]$script:EvidenceWarnings.Add("evidência ignorada por tamanho: $Path")
        return $null
    }
    return [System.IO.File]::ReadAllText($Path)
}

# Distingue arquivos vazios de fontes legadas com conteúdo aproveitável.
function Test-WhitespaceOnly([string]$Path) {
    $t = Get-Text $Path
    return [string]::IsNullOrWhiteSpace($t)
}

# Extrai os SLOTs que ainda exigem evidência ou resposta humana.
function Get-OpenSlots([string]$Text) {
    if ($null -eq $Text) { return @() }
    return [regex]::Matches($Text, '<!--\s*SLOT:(\w+)\s*-->') | ForEach-Object { $_.Groups[1].Value }
}

# Checkout Windows (core.symlinks=false): o "symlink" vira arquivo cujo texto é o alvo.
function Test-IsPointerText([string]$Path) {
    $t = Get-Text $Path
    if ($null -eq $t) { return $false }
    $t = $t.Trim().Trim([char]0xFEFF)
    $norm = ($t -replace '\\', '/' -replace '^\./', '').Trim()
    return Test-SamePath $norm '.vibeflow/REGRAS.md'
}

# --- inventário (zero escrita) -----------------------------------------------

# Classifica a pasta principal antes de qualquer alteração no disco.
function Get-VibeflowState([string]$Vf) {
    $item = Get-FsItem $Vf
    if (-not $item) { return 'ausente' }
    if (-not $item.PSIsContainer) { return 'inesperado' }
    $regras = Join-Path $Vf 'REGRAS.md'
    if (Test-Path -LiteralPath $regras) { return 'com_regras' }
    $kids = @(Get-ChildItem -LiteralPath $Vf -Force -ErrorAction SilentlyContinue)
    if ($kids.Count -eq 0) { return 'vazia' }
    return 'sem_regras'
}

# Classifica um arquivo de regras sem interpretar semanticamente sua prosa.
function Get-RegrasFileState([string]$Path) {
    $item = Get-FsItem $Path
    if (-not $item) { return 'ausente' }
    if ($item.PSIsContainer) { return 'inesperado' }
    if (Test-WhitespaceOnly $Path) { return 'vazio' }
    $slots = @(Get-OpenSlots (Get-Text $Path))
    if ($slots.Count -gt 0) { return 'template' }
    return 'preenchido'
}

# Resume a relação entre a fonte viva e uma possível cópia na raiz.
function Get-RegrasState([string]$Repo, [string]$VfRegras, [string]$RootRegras) {
    $hasVf = Test-Path -LiteralPath $VfRegras
    $hasRoot = Test-Path -LiteralPath $RootRegras
    if ($hasVf -and $hasRoot) { return 'raiz_e_vibeflow' }
    if ($hasRoot -and -not $hasVf) { return 'raiz_sozinho' }
    return (Get-RegrasFileState $VfRegras)
}

# Classifica um ponteiro considerando links quebrados, cópias e conteúdo legado.
function Get-PointerState([string]$Repo, [string]$Name, [string]$VfRegras) {
    $path = Join-Path $Repo $Name
    $item = Get-FsItem $path
    if (-not $item) { return 'ausente' }
    if ($item.PSIsContainer) { return 'inesperado' }
    if (Test-IsSymlink $item) {
        $target = Get-LinkTargetString $item
        $resolved = Resolve-MaybeRelative $Repo $target
        if (-not $resolved -or -not (Test-Path -LiteralPath $resolved)) { return 'symlink_quebrado' }
        if (Test-Path -LiteralPath $VfRegras) {
            $want = (Get-Item -LiteralPath $VfRegras).FullName
            if (Test-SamePath $resolved $want) {
                return 'symlink_ok'
            }
        }
        return 'symlink_outro'
    }
    if (Test-WhitespaceOnly $path) { return 'vazio' }
    if (Test-IsPointerText $path) { return 'ponteiro_texto' }
    if ((Test-Path -LiteralPath $VfRegras) -and (Test-SameBytes $path $VfRegras)) {
        return 'arquivo_igual'
    }
    return 'arquivo_legado'
}

# --- old (nunca sobrescreve; sem verify não segue) ---------------------------

# Escolhe um destino de backup único sem depender apenas da precisão do relógio.
function New-OldDest([string]$OldDir, [string]$Name) {
    $dest = Join-Path $OldDir $Name
    if (-not (Test-Path -LiteralPath $dest)) { return $dest }
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $candidate = Join-Path $OldDir "$Name.$stamp"
    $suffix = 1
    while (Test-Path -LiteralPath $candidate) {
        $candidate = Join-Path $OldDir "$Name.$stamp.$suffix"
        $suffix++
    }
    return $candidate
}

# Copia e valida o old antes que o original possa ser substituído.
function Copy-Verified([string]$From, [string]$To) {
    $dir = Split-Path -Parent $To
    if (-not (Test-Path -LiteralPath $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    Copy-Item -LiteralPath $From -Destination $To -Force
    if ($env:VIBE_INIT_TEST_CORRUPT_OLD -eq '1') {
        [System.IO.File]::WriteAllText($To, 'CORRUPT')
    }
    if (-not (Test-SameBytes $From $To)) {
        Remove-Item -LiteralPath $To -Force -ErrorAction SilentlyContinue
        return $false
    }
    return $true
}

# --- symlink: cria o link primeiro; só então tira o original -----------------

function New-RelSymlink([string]$LinkPath, [string]$TargetRel) {
    $tmp = "$LinkPath.__vibe_symlink__$([guid]::NewGuid().ToString('n'))"
    try {
        New-Item -ItemType SymbolicLink -Path $tmp -Target $TargetRel -ErrorAction Stop | Out-Null
    } catch {
        throw "SYMLINK_RECUSADO: o OS recusou criar o link '$LinkPath' -> '$TargetRel'. Ative o Developer Mode (Configurações → Sistema → Para desenvolvedores) ou rode como administrador. Sem cópia na raiz — o original permanece."
    }
    try {
        if (Get-FsItem $LinkPath) {
            Remove-Item -LiteralPath $LinkPath -Force
        }
        Rename-Item -LiteralPath $tmp -NewName (Split-Path -Leaf $LinkPath)
    } finally {
        # Remove somente o temporário desta execução se a troca não foi concluída.
        if (Get-FsItem $tmp) { Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue }
    }
}

# Garante uma regra operacional sem sobrescrever as exclusões já mantidas pelo projeto.
function Add-GitIgnoreEntry([string]$Path, [string]$Entry) {
    $body = if (Test-Path -LiteralPath $Path) { Get-Text $Path } else { '' }
    $present = @($body -split '\r?\n') | Where-Object { $_.Trim() -eq $Entry }
    if ($present.Count -gt 0) { return $false }
    $prefix = if ($body -and -not $body.EndsWith("`n")) { "`n" } else { '' }
    [System.IO.File]::AppendAllText($Path, "$prefix$Entry`n", (New-Object System.Text.UTF8Encoding $false))
    return $true
}

# --- scan: só SLOT aberto + evidência ----------------------------------------

# Extrai um nome factual de manifests conhecidos ou do diretório do projeto.
function Get-ProjectName([string]$Repo) {
    $pkg = Join-Path $Repo 'package.json'
    if (Test-Path -LiteralPath $pkg) {
        try {
            $raw = Get-EvidenceText $pkg
            if (-not $raw) { throw 'manifest excede o limite de leitura' }
            $n = ($raw | ConvertFrom-Json).name
            if ($n) { return @{ value = [string]$n; from = 'package.json' } }
        } catch {}
    }
    $py = Join-Path $Repo 'pyproject.toml'
    if (Test-Path -LiteralPath $py) {
        $raw = Get-EvidenceText $py
        if ($raw) {
            $m = [regex]::Match($raw, '(?ms)\[project\].*?^name\s*=\s*["'']([^"'']+)["'']')
            if ($m.Success) { return @{ value = $m.Groups[1].Value; from = 'pyproject.toml' } }
        }
    }
    $go = Join-Path $Repo 'go.mod'
    if (Test-Path -LiteralPath $go) {
        $raw = Get-EvidenceText $go
        $m = if ($raw) { [regex]::Match($raw, '(?m)^module\s+(\S+)') } else { $null }
        if ($m -and $m.Success) {
            $mod = $m.Groups[1].Value
            $leaf = ($mod -split '/')[-1]
            return @{ value = $leaf; from = 'go.mod' }
        }
    }
    return @{ value = (Split-Path -Leaf $Repo); from = 'pasta' }
}

# Seleciona o primeiro parágrafo útil, ignorando títulos, badges e imagens iniciais.
function Get-UsefulParagraph([string]$Text) {
    if ([string]::IsNullOrWhiteSpace($Text)) { return $null }
    $buf = New-Object System.Collections.Generic.List[string]
    $started = $false
    foreach ($line in ($Text -split '\r?\n')) {
        $t = $line.Trim()
        if (-not $started) {
            if ($t -eq '') { continue }
            if ($t -match '^#+' -or $t -match '^\[!\[' -or $t -match '^!\[' -or $t -match '^<!--' -or $t -match '^<img') { continue }
            $started = $true
        }
        if ($t -eq '') { break }
        [void]$buf.Add($t)
    }
    $p = ($buf -join ' ').Trim()
    if ($p) { return $p }
    return $null
}

# Localiza uma descrição factual sem ultrapassar o limite de leitura de evidências.
function Get-ParagrafoEvidence([string]$Repo) {
    foreach ($name in @('README.md', 'README.MD', 'readme.md')) {
        $p = Join-Path $Repo $name
        if (Test-Path -LiteralPath $p) {
            $para = Get-UsefulParagraph (Get-EvidenceText $p)
            if ($para) { return @{ text = $para; from = $name } }
        }
    }
    $pkg = Join-Path $Repo 'package.json'
    if (Test-Path -LiteralPath $pkg) {
        try {
            $raw = Get-EvidenceText $pkg
            if (-not $raw) { throw 'manifest excede o limite de leitura' }
            $d = ($raw | ConvertFrom-Json).description
            if ($d) { return @{ text = [string]$d; from = 'package.json' } }
        } catch {}
    }
    $py = Join-Path $Repo 'pyproject.toml'
    if (Test-Path -LiteralPath $py) {
        $raw = Get-EvidenceText $py
        if ($raw) {
            $m = [regex]::Match($raw, '(?ms)\[project\].*?^description\s*=\s*["'']([^"'']+)["'']')
            if ($m.Success) { return @{ text = $m.Groups[1].Value; from = 'pyproject.toml' } }
        }
    }
    return $null
}

# Lista dois níveis úteis sem entrar em diretórios de dependências ou build.
function Get-Estrutura([string]$Repo) {
    $ignore = @('node_modules', '.git', 'dist', 'build', '.next', 'vendor', '__pycache__')
    $out = New-Object System.Collections.Generic.List[string]
    $level1 = @(Get-ChildItem -LiteralPath $Repo -Force | Where-Object { $ignore -notcontains $_.Name })
    foreach ($e in $level1) {
        [void]$out.Add($e.Name)
        if ($e.PSIsContainer) {
            $kids = @(Get-ChildItem -LiteralPath $e.FullName -Force -ErrorAction SilentlyContinue |
                Where-Object { $ignore -notcontains $_.Name })
            foreach ($k in $kids) { [void]$out.Add("$($e.Name)/$($k.Name)") }
        }
    }
    if ($out.Count -gt 120) {
        $extra = $out.Count - 120
        return @(@($out[0..119]) + @("… (+$extra itens omitidos)"))
    }
    return @($out)
}

# Identifica a stack apenas pela presença de manifests conhecidos.
function Get-Stack([string]$Repo) {
    $names = @(
        'package.json', 'pyproject.toml', 'go.mod', 'Cargo.toml', 'composer.json',
        'Gemfile', 'pom.xml', 'build.gradle', 'requirements.txt', 'Pipfile'
    )
    return @($names | Where-Object { Test-Path -LiteralPath (Join-Path $Repo $_) })
}

# Detecta migrations conhecidas e nomes convencionais com travessia podada.
function Test-Migrations([string]$Repo) {
    $hits = @(
        'prisma/migrations', 'alembic', 'alembic.ini', 'drizzle',
        'knexfile.js', 'knexfile.ts', 'supabase/migrations'
    )
    foreach ($h in $hits) {
        if (Test-Path -LiteralPath (Join-Path $Repo $h)) { return $true }
    }
    # Percorre diretórios com poda real; filtrar depois de -Recurse ainda entraria em árvores enormes.
    $ignore = @('node_modules', '.git', 'vendor', 'dist', 'build', '.next', '__pycache__')
    $queue = New-Object 'System.Collections.Generic.Queue[object]'
    $queue.Enqueue(@{ path = $Repo; depth = 0 })
    while ($queue.Count -gt 0) {
        $current = $queue.Dequeue()
        foreach ($dir in @(Get-ChildItem -LiteralPath $current.path -Directory -Force -ErrorAction SilentlyContinue)) {
            if ($ignore -contains $dir.Name -or (Test-IsSymlink $dir)) { continue }
            if ($dir.Name -eq 'migrations') { return $true }
            if ($current.depth + 1 -lt 4) { $queue.Enqueue(@{ path = $dir.FullName; depth = $current.depth + 1 }) }
        }
    }
    return $false
}

# Extrai do template o único bloco controlado integralmente pela skill.
function Get-CadeiaBlock([string]$TemplatePath) {
    $t = Get-Text $TemplatePath
    $m = [regex]::Match($t, '(?s)<!-- VIBEFLOW:CADEIA start -->.*?<!-- VIBEFLOW:CADEIA end -->')
    if (-not $m.Success) { throw "Template sem bloco VIBEFLOW:CADEIA: $TemplatePath" }
    return $m.Value
}

# Recoloca só o roteador delimitado — não mexe no resto do REGRAS do usuário.
function Set-CadeiaBlock([string]$Content, [string]$Block) {
    $pattern = '(?s)<!-- VIBEFLOW:CADEIA start -->.*?<!-- VIBEFLOW:CADEIA end -->'
    if ([regex]::IsMatch($Content, $pattern)) {
        return [regex]::Replace($Content, $pattern, { $Block }, 1)
    }
    $m = [regex]::Match($Content, '(?s)^(# [^\r\n]+\r?\n)(\r?\n)?')
    if ($m.Success) {
        return $m.Groups[1].Value + "`n" + $Block + "`n`n" + $Content.Substring($m.Length)
    }
    return $Block + "`n`n" + $Content
}

# Preenche somente um SLOT explicitamente respaldado por evidência.
function Set-Slot([string]$Content, [string]$Slot, [string]$Value, [string]$Evidencia) {
    $pattern = "(?m)^<!--\s*SLOT:$([regex]::Escape($Slot))\s*-->\s*\r?\n(?:<!--\s*evidência:[^\n]*-->\s*\r?\n)?"
    $repl = $Value.TrimEnd() + "`n"
    if ($null -ne $Evidencia) { $repl += "<!-- evidência: $Evidencia -->`n" }
    return [regex]::Replace($Content, $pattern, { $repl }, 1)
}

# Converte um caminho absoluto do repositório para o formato portátil usado no relatório.
function Get-RepoRelativePath([string]$Repo, [string]$Path) {
    return $Path.Substring($Repo.Length).TrimStart('\', '/').Replace('\', '/')
}

# Persiste a autorização verificável necessária para finalizar um merge em outra execução.
function Write-PendingMerge([string]$Path, [string]$Repo, [string]$TargetPath, $Merges) {
    $sources = New-Object System.Collections.Generic.List[object]
    foreach ($source in @($Merges | ForEach-Object { $_.sources } | Select-Object -Unique)) {
        $absolute = Join-Path $Repo $source
        if (-not (Test-Path -LiteralPath $absolute -PathType Leaf)) {
            throw "MERGE_SOURCE_AUSENTE: fonte de merge não encontrada: $source"
        }
        [void]$sources.Add([ordered]@{ path = $source; sha256 = Get-Sha256File $absolute })
    }
    $pending = [ordered]@{
        version               = 1
        token                 = [guid]::NewGuid().ToString('n')
        target                = Get-RepoRelativePath $Repo $TargetPath
        target_sha256_inicial = Get-Sha256File $TargetPath
        sources               = $sources
        remove_regras_raiz    = [bool](@($Merges | Where-Object { $_.id -eq 'regras_duplicado' }).Count -gt 0)
    }
    $json = $pending | ConvertTo-Json -Depth 10
    [System.IO.File]::WriteAllText($Path, $json, (New-Object System.Text.UTF8Encoding $false))
    return $pending
}

# Valida token, imutabilidade das fontes e alteração do consolidado antes de trocar ponteiros.
function Confirm-PendingMerge([string]$Path, [string]$Repo, [string]$Token) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw 'APPLY_SEM_MERGE: não existe merge pendente para finalizar.'
    }
    $pending = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    if (-not $Token -or -not [string]::Equals([string]$pending.token, $Token, [StringComparison]::Ordinal)) {
        throw 'MERGE_TOKEN_INVALIDO: use o apply_token do init-report.json atual.'
    }
    foreach ($source in @($pending.sources)) {
        $absolute = Join-Path $Repo $source.path
        if (-not (Test-Path -LiteralPath $absolute -PathType Leaf) -or
            (Get-Sha256File $absolute) -ne $source.sha256) {
            throw "MERGE_SOURCE_ALTERADA: a fonte '$($source.path)' mudou desde o inventário. Execute o init novamente após resolver o estado pendente."
        }
    }
    $target = Join-Path $Repo $pending.target
    if (-not (Test-Path -LiteralPath $target -PathType Leaf)) {
        throw "MERGE_TARGET_AUSENTE: consolidado não encontrado: $($pending.target)"
    }
    if ((Get-Sha256File $target) -eq $pending.target_sha256_inicial) {
        throw 'MERGE_NAO_APLICADO: o consolidado não mudou desde o inventário; os ponteiros foram preservados.'
    }
    return $pending
}

# Interrompe antes da primeira escrita quando caminhos estruturais possuem tipos incompatíveis.
function Assert-InfrastructureTypes([string]$Vf, [string]$VfRegras, [string]$RootRegras, [string]$Phases) {
    $vfItem = Get-FsItem $Vf
    if ($vfItem -and -not $vfItem.PSIsContainer) {
        throw 'TIPO_INESPERADO: .vibeflow existe, mas não é um diretório.'
    }
    foreach ($path in @($VfRegras, $RootRegras)) {
        $item = Get-FsItem $path
        if ($item -and $item.PSIsContainer) {
            throw "TIPO_INESPERADO: '$path' existe, mas não é um arquivo."
        }
    }
    $phasesItem = Get-FsItem $Phases
    if ($phasesItem -and -not $phasesItem.PSIsContainer) {
        throw 'TIPO_INESPERADO: .vibeflow/phases existe, mas não é um diretório.'
    }
}

# --- fluxo -------------------------------------------------------------------

# Executa a matriz determinística e coordena inventário, backup, scan e ponteiros.
function Invoke-VibeInit {
    $repo = Get-RepoRoot
    $skill = Get-SkillDir
    $template = Join-Path $skill 'templates\REGRAS.md'
    if (-not (Test-Path -LiteralPath $template)) {
        throw "Template não encontrado: $template"
    }

    $vf = Join-Path $repo '.vibeflow'
    $vfRegras = Join-Path $vf 'REGRAS.md'
    $rootRegras = Join-Path $repo 'REGRAS.md'
    $oldDir = Join-Path $vf 'old'
    $phases = Join-Path $vf 'phases'
    $pendingPath = Join-Path $vf 'init-pending.json'
    $targetRel = '.vibeflow/REGRAS.md'

    Assert-InfrastructureTypes $vf $vfRegras $rootRegras $phases

    $confirmedPending = $null
    if ($ApplyPointers) {
        $confirmedPending = Confirm-PendingMerge $pendingPath $repo $MergeToken
    } elseif (Test-Path -LiteralPath $pendingPath) {
        throw 'MERGE_PENDENTE: finalize o consolidado e execute -ApplyPointers com o apply_token do relatório atual.'
    }

    $inventory = [ordered]@{
        vibeflow = Get-VibeflowState $vf
        phases   = $(if (Test-Path -LiteralPath $phases) { 'ok' } else { 'ausente' })
        regras   = Get-RegrasState $repo $vfRegras $rootRegras
        agents   = Get-PointerState $repo 'AGENTS.md' $vfRegras
        claude   = Get-PointerState $repo 'CLAUDE.md' $vfRegras
    }

    $hasAny = ($inventory.vibeflow -ne 'ausente') -or
        (Test-Path -LiteralPath $rootRegras) -or
        ($inventory.agents -ne 'ausente') -or
        ($inventory.claude -ne 'ausente')
    $flow = if ($hasAny) { 'reparar' } else { 'novo' }

    $olds = New-Object System.Collections.Generic.List[object]
    $actions = New-Object System.Collections.Generic.List[object]
    $merges = New-Object System.Collections.Generic.List[object]
    $conflicts = New-Object System.Collections.Generic.List[object]
    $avisos = New-Object System.Collections.Generic.List[string]
    $script:Partial = [ordered]@{
        repo = $repo; flow = $flow; inventory = $inventory; olds = $olds
        actions = $actions; merges = $merges; conflicts = $conflicts; avisos = $avisos
    }

    # Registra ações em um formato único para o relatório consumido pela IA.
    function Add-Action([string]$Op, [string]$Alvo) {
        [void]$actions.Add([ordered]@{ op = $Op; alvo = $Alvo })
    }

    # Salva uma fonte e devolve o destino real, inclusive quando recebeu sufixo de colisão.
    function Save-Old([string]$FromPath, [string]$OldName) {
        if (-not (Test-Path -LiteralPath $FromPath)) { return $null }
        if (-not (Test-Path -LiteralPath $oldDir)) {
            New-Item -ItemType Directory -Path $oldDir -Force | Out-Null
        }
        $dest = New-OldDest $oldDir $OldName
        if (-not (Copy-Verified $FromPath $dest)) {
            throw "OLD_HASH_MISMATCH: cópia de '$FromPath' não bateu com '$dest'. Peça não substituída."
        }
        $item = Get-Item -LiteralPath $dest -Force
        $rec = [ordered]@{
            from   = ($FromPath.Substring($repo.Length).TrimStart('\', '/').Replace('\', '/'))
            to     = ($dest.Substring($repo.Length).TrimStart('\', '/').Replace('\', '/'))
            bytes  = [int64]$item.Length
            sha256 = Get-Sha256File $dest
        }
        [void]$olds.Add($rec)
        Add-Action 'old' $rec.to
        return $dest
    }

    # a. pasta + phases
    if ($inventory.vibeflow -eq 'ausente') {
        New-Item -ItemType Directory -Path $vf -Force | Out-Null
        Add-Action 'criar_dir' '.vibeflow'
    }
    if (-not (Test-Path -LiteralPath $phases)) {
        New-Item -ItemType Directory -Path $phases -Force | Out-Null
        Add-Action 'criar_phases' '.vibeflow/phases'
    }
    $gitkeep = Join-Path $phases '.gitkeep'
    if (-not (Test-Path -LiteralPath $gitkeep)) {
        [System.IO.File]::WriteAllText($gitkeep, '')
        Add-Action 'criar_phases' '.vibeflow/phases/.gitkeep'
    }
    $gi = Join-Path $vf '.gitignore'
    [void](Add-GitIgnoreEntry $gi 'init-report.json')
    [void](Add-GitIgnoreEntry $gi 'init-pending.json')

    $agentsPath = Join-Path $repo 'AGENTS.md'
    $claudePath = Join-Path $repo 'CLAUDE.md'
    $agentsLegado = $inventory.agents -eq 'arquivo_legado'
    $claudeLegado = $inventory.claude -eq 'arquivo_legado'
    $agentsEqClaude = $false
    if ($agentsLegado -and $claudeLegado) {
        $agentsEqClaude = Test-SameBytes $agentsPath $claudePath
    }

    $regrasContentState = if (Test-Path -LiteralPath $vfRegras) {
        Get-RegrasFileState $vfRegras
    } elseif (Test-Path -LiteralPath $rootRegras) {
        Get-RegrasFileState $rootRegras
    } else { 'ausente' }

    $needTemplate = ($inventory.regras -eq 'ausente' -or $regrasContentState -eq 'ausente' -or $regrasContentState -eq 'vazio') -and
        $inventory.regras -ne 'raiz_sozinho' -and $inventory.regras -ne 'raiz_e_vibeflow'

    # Toda fonte de texto que perde o papel de arquivo editável vira merge, inclusive quando o
    # REGRAS vem da raiz: sem isso o legado só sobrevive em old/ e some do consolidado.
    # AGENTS idêntico a CLAUDE entra uma vez só; a IA não precisa ler o mesmo texto duas vezes.
    $legacySources = @()
    if ($agentsLegado) { $legacySources += '.vibeflow/old/AGENTS.md' }
    if ($claudeLegado -and -not $agentsEqClaude) { $legacySources += '.vibeflow/old/CLAUDE.md' }
    $liveHasText = (Test-Path -LiteralPath $vfRegras -PathType Leaf) -and -not (Test-WhitespaceOnly $vfRegras)
    $duplicated = $inventory.regras -eq 'raiz_e_vibeflow' -and -not (Test-SameBytes $rootRegras $vfRegras)

    $mergePending = $false
    if (-not $ApplyPointers) {
        if ($duplicated) {
            [void]$merges.Add([ordered]@{
                id      = 'regras_duplicado'
                sources = @('.vibeflow/old/REGRAS-raiz.md', '.vibeflow/old/REGRAS.md')
                target  = '.vibeflow/REGRAS.md'
            })
        }
        if ($legacySources.Count -gt 0) {
            # Texto que o consolidado já terá nesta run: o vivo, ou o REGRAS da raiz que vira o vivo.
            $existing = @()
            if ($duplicated) {
                $existing = @()
            } elseif ($inventory.regras -eq 'raiz_sozinho') {
                $existing = @('.vibeflow/old/REGRAS-raiz.md')
            } elseif ($liveHasText -and $inventory.regras -in @('template', 'preenchido', 'raiz_e_vibeflow')) {
                $existing = @('.vibeflow/old/REGRAS.md')
            }
            $mergeId = if ($existing.Count -eq 0 -and $legacySources.Count -gt 1) { 'duas_fontes' } else { 'legado_vs_regras' }
            [void]$merges.Add([ordered]@{
                id      = $mergeId
                sources = @($legacySources + $existing)
                target  = '.vibeflow/REGRAS.md'
            })
        }
        $mergePending = $merges.Count -gt 0
    }

    if ($merges.Count -gt 0) { Add-Action 'merge_pendente' '.vibeflow/REGRAS.md' }

    foreach ($pair in @(@('AGENTS.md', $inventory.agents), @('CLAUDE.md', $inventory.claude))) {
        if ($pair[1] -eq 'ponteiro_texto') {
            [void]$avisos.Add("$($pair[0]) é ponteiro_texto (checkout sem symlink). Não é regra — não entra em merge.")
        }
    }

    foreach ($name in @('AGENTS.md', 'CLAUDE.md')) {
        $st = if ($name -eq 'AGENTS.md') { $inventory.agents } else { $inventory.claude }
        if ($st -eq 'symlink_outro') {
            [void]$conflicts.Add([ordered]@{
                id      = 'ponteiro_alheio'
                peca    = $name
                detalhe = "link para outro arquivo (não é $targetRel)"
            })
        }
        if ($st -eq 'inesperado') {
            [void]$conflicts.Add([ordered]@{
                id      = 'tipo_inesperado'
                peca    = $name
                detalhe = 'não é arquivo nem symlink'
            })
        }
    }

    # b. old de toda peça que esta run vai mexer (original permanece até o symlink)
    $neededSources = @($merges | ForEach-Object { $_.sources } | Select-Object -Unique)
    $oldSourceMap = @{}
    if (-not $ApplyPointers) {
        if ($agentsLegado -or $inventory.agents -in @('arquivo_igual', 'ponteiro_texto')) {
            $oldSourceMap['.vibeflow/old/AGENTS.md'] = Get-RepoRelativePath $repo (Save-Old $agentsPath 'AGENTS.md')
        }
        if ($claudeLegado -or $inventory.claude -in @('arquivo_igual', 'ponteiro_texto')) {
            $oldSourceMap['.vibeflow/old/CLAUDE.md'] = Get-RepoRelativePath $repo (Save-Old $claudePath 'CLAUDE.md')
        }
        if ($inventory.regras -eq 'raiz_sozinho' -or $inventory.regras -eq 'raiz_e_vibeflow') {
            $oldSourceMap['.vibeflow/old/REGRAS-raiz.md'] = Get-RepoRelativePath $repo (Save-Old $rootRegras 'REGRAS-raiz.md')
        }
        if ($neededSources -contains '.vibeflow/old/REGRAS.md' -and $liveHasText) {
            $oldSourceMap['.vibeflow/old/REGRAS.md'] = Get-RepoRelativePath $repo (Save-Old $vfRegras 'REGRAS.md')
        }
        foreach ($merge in $merges) {
            $merge.sources = @($merge.sources | ForEach-Object { if ($oldSourceMap.ContainsKey($_)) { $oldSourceMap[$_] } else { $_ } })
        }
    }

    if ($StopAfterOld) {
        Write-Report $repo $flow $inventory $olds $actions $merges $conflicts $avisos @{} @() $false @{} $false $false $null
        return
    }

    # c. resolver REGRAS.md
    if ($inventory.regras -eq 'raiz_sozinho') {
        if (-not (Test-Path -LiteralPath $vf)) { New-Item -ItemType Directory -Path $vf -Force | Out-Null }
        Move-Item -LiteralPath $rootRegras -Destination $vfRegras -Force
        Add-Action 'mover' 'REGRAS.md -> .vibeflow/REGRAS.md'
    } elseif ($inventory.regras -eq 'raiz_e_vibeflow') {
        if (Test-SameBytes $rootRegras $vfRegras) {
            Remove-Item -LiteralPath $rootRegras -Force
            Add-Action 'apagar_raiz' 'REGRAS.md'
        } else {
            # merge pendente: raiz permanece até a IA unir; old já gravado
        }
    } elseif ($needTemplate) {
        Copy-Item -LiteralPath $template -Destination $vfRegras -Force
        Add-Action 'escrever_template' '.vibeflow/REGRAS.md'
    }

    # d. ponteiros — não viram symlink se o merge ainda usa o arquivo como fonte
    # Converte uma peça independentemente, preservando fontes ainda necessárias ao merge.
    function Convert-Pointer([string]$Name, [string]$State) {
        $path = Join-Path $repo $Name
        if ($State -eq 'inesperado') { return }
        if ($State -eq 'symlink_ok') { return }
        if ($State -eq 'symlink_outro' -and $RedirectPointer -ne ($Name -replace '\.md$', '')) { return }
        if ($State -eq 'arquivo_legado' -and $mergePending -and -not $ApplyPointers) { return }

        if ($State -eq 'symlink_outro' -and $RedirectPointer -eq ($Name -replace '\.md$', '')) {
            $item = Get-FsItem $path
            $prev = Get-LinkTargetString $item
            if (-not (Test-Path -LiteralPath $oldDir)) {
                New-Item -ItemType Directory -Path $oldDir -Force | Out-Null
            }
            $tgtFile = New-OldDest $oldDir ($Name -replace '\.md$', '.target.txt')
            [System.IO.File]::WriteAllText($tgtFile, [string]$prev)
            [void]$olds.Add([ordered]@{
                from   = $Name
                to     = ($tgtFile.Substring($repo.Length).TrimStart('\', '/').Replace('\', '/'))
                bytes  = ([System.Text.Encoding]::UTF8.GetByteCount([string]$prev))
                sha256 = 'target-path'
            })
        }

        if ($State -eq 'ausente') {
            New-RelSymlink $path $targetRel
            Add-Action 'symlink_criar' $Name
            return
        }
        if ($State -eq 'symlink_quebrado' -or ($State -eq 'symlink_outro' -and $RedirectPointer)) {
            New-RelSymlink $path $targetRel
            Add-Action 'symlink_recriar' $Name
            return
        }
        if ($State -in @('vazio', 'arquivo_igual', 'arquivo_legado', 'ponteiro_texto')) {
            New-RelSymlink $path $targetRel
            Add-Action 'symlink_criar' $Name
        }
    }

    if (Test-Path -LiteralPath $vfRegras) {
        Convert-Pointer 'AGENTS.md' $inventory.agents
        Convert-Pointer 'CLAUDE.md' $inventory.claude
    }

    # e. leftover raiz (caso iguais já apagou; diferentes esperam merge)
    if ((Test-Path -LiteralPath $rootRegras) -and (Test-Path -LiteralPath $vfRegras) -and (Test-SameBytes $rootRegras $vfRegras) -and $inventory.regras -ne 'raiz_e_vibeflow') {
        Remove-Item -LiteralPath $rootRegras -Force
        Add-Action 'apagar_raiz' 'REGRAS.md'
    }

    if ($ApplyPointers -and $confirmedPending.remove_regras_raiz -and (Test-Path -LiteralPath $rootRegras -PathType Leaf)) {
        Remove-Item -LiteralPath $rootRegras -Force
        Add-Action 'apagar_raiz' 'REGRAS.md'
    }

    # scan: só SLOT ainda aberto
    $filled = [ordered]@{}
    $nome = Get-ProjectName $repo
    $filled['nome'] = $nome
    $estrutura = @(Get-Estrutura $repo)
    $stack = @(Get-Stack $repo)
    $mig = Test-Migrations $repo
    $evidPara = Get-ParagrafoEvidence $repo
    foreach ($warning in @($script:EvidenceWarnings | Select-Object -Unique)) {
        [void]$avisos.Add($warning)
    }
    $scan = [ordered]@{
        estrutura           = $estrutura
        stack               = $stack
        evidencia_paragrafo = $evidPara
    }

    if (Test-Path -LiteralPath $vfRegras) {
        $body = Get-Text $vfRegras
        $open = @(Get-OpenSlots $body)
        $changed = $false
        if ($open -contains 'estrutura') {
            $list = if ($estrutura.Count) { ($estrutura | ForEach-Object { "- $_" }) -join "`n" } else { '- (raiz vazia)' }
            $body = Set-Slot $body 'estrutura' $list $null
            $changed = $true
        }
        if ($open -contains 'paragrafo' -and $evidPara) {
            $body = Set-Slot $body 'paragrafo' $evidPara.text $evidPara.from
            $changed = $true
            $filled['paragrafo'] = @{ value = $evidPara.text; from = $evidPara.from }
        }
        $cadeia = Get-CadeiaBlock $template
        $withCadeia = Set-CadeiaBlock $body $cadeia
        if ($withCadeia -ne $body) {
            $body = $withCadeia
            $changed = $true
            Add-Action 'cadeia_upsert' '.vibeflow/REGRAS.md'
        }
        if ($changed) {
            $utf8 = New-Object System.Text.UTF8Encoding $false
            [System.IO.File]::WriteAllText($vfRegras, $body, $utf8)
        }
    }

    $slotsAbertos = @()
    if (Test-Path -LiteralPath $vfRegras) {
        $slotsAbertos = @(Get-OpenSlots (Get-Text $vfRegras))
    }

    $syAgents = (Get-PointerState $repo 'AGENTS.md' $vfRegras) -eq 'symlink_ok'
    $syClaude = (Get-PointerState $repo 'CLAUDE.md' $vfRegras) -eq 'symlink_ok'

    if (($IsWindows -or $env:OS -match 'Windows') -and (Get-Command git -ErrorAction SilentlyContinue)) {
        $cs = & git -C $repo config --get core.symlinks 2>$null
        if ($cs -and $cs.Trim() -ne 'true') {
            [void]$avisos.Add('git core.symlinks não é true (aviso; não forçado)')
        }
    }

    $applyToken = $null
    if (-not $ApplyPointers -and $merges.Count -gt 0) {
        $pending = Write-PendingMerge $pendingPath $repo $vfRegras $merges
        $applyToken = $pending.token
    }
    if ($ApplyPointers -and (Test-Path -LiteralPath $pendingPath)) {
        Remove-Item -LiteralPath $pendingPath -Force
    }

    Write-Report $repo $flow $inventory $olds $actions $merges $conflicts $avisos $filled $slotsAbertos $mig $scan $syAgents $syClaude $applyToken
}

# Serializa o contrato entre o script determinístico e a IA que conclui o conteúdo semântico.
function Write-Report(
    $repo, $flow, $inventory, $olds, $actions, $merges, $conflicts, $avisos,
    $filled, $slotsAbertos, $mig, $scan, $syAgents, $syClaude, $applyToken
) {
    $vf = Join-Path $repo '.vibeflow'
    if (-not (Test-Path -LiteralPath $vf)) { New-Item -ItemType Directory -Path $vf -Force | Out-Null }
    $report = [ordered]@{
        flow                  = $flow
        root                  = $repo
        inventory             = $inventory
        olds                  = $olds
        actions               = $actions
        merges                = $merges
        conflicts             = $conflicts
        filled                = $filled
        slots_abertos         = @($slotsAbertos)
        migrations_detectadas = [bool]$mig
        symlink_ok            = [ordered]@{ agents = [bool]$syAgents; claude = [bool]$syClaude }
        scan                  = $scan
        avisos                = @($avisos)
        apply_token           = $applyToken
    }
    $jsonPath = Join-Path $vf 'init-report.json'
    $json = $report | ConvertTo-Json -Depth 10
    $utf8 = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($jsonPath, $json, $utf8)
    Write-Output $jsonPath
}

# Grava o que a run já fez quando ela falha no meio: sem isso a IA fica sem contrato de disco
# justamente no cenário em que o repositório ficou parcialmente convertido.
function Write-PartialReport([string]$Message) {
    if (-not $script:Partial) { return }
    $state = $script:Partial
    if ($state.actions.Count -eq 0) { return }
    if (-not (Test-Path -LiteralPath (Join-Path $state.repo '.vibeflow'))) { return }
    [void]$state.avisos.Add("run interrompida: $Message")
    Write-Report $state.repo $state.flow $state.inventory $state.olds $state.actions `
        $state.merges $state.conflicts $state.avisos @{} @() $false @{} $false $false $null
}

try {
    Invoke-VibeInit
} catch {
    Write-PartialReport $_.Exception.Message
    throw
}
