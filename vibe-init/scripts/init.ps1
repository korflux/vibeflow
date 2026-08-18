# vibe-init/scripts/init.ps1
# Inventário → old verificado → matriz → scan factual → init-report.json.
# Symlink de ponteiro só com merge já fechado (ou -ApplyPointers após a IA unir).
param(
    [string]$Root,
    [switch]$ApplyPointers,
    [ValidateSet('AGENTS', 'CLAUDE')]
    [string]$RedirectPointer,
    [switch]$StopAfterOld
)

$ErrorActionPreference = 'Stop'

# --- paths e bytes -----------------------------------------------------------

function Get-RepoRoot {
    if ($Root) { return (Resolve-Path -LiteralPath $Root).Path }
    $git = & git rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -eq 0 -and $git) { return $git.Trim() }
    return (Get-Location).Path
}

function Get-SkillDir {
    return (Split-Path -Parent $PSScriptRoot)
}

function Get-Sha256File([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Test-SameBytes([string]$A, [string]$B) {
    if (-not (Test-Path -LiteralPath $A) -or -not (Test-Path -LiteralPath $B)) { return $false }
    $ia = Get-Item -LiteralPath $A -Force
    $ib = Get-Item -LiteralPath $B -Force
    if ($ia.Length -ne $ib.Length) { return $false }
    return (Get-Sha256File $A) -eq (Get-Sha256File $B)
}

function Get-FsItem([string]$Path) {
    return Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
}

function Test-IsSymlink($Item) {
    if (-not $Item) { return $false }
    return $Item.Attributes.ToString() -match 'ReparsePoint' -or $Item.LinkType -eq 'SymbolicLink'
}

function Get-LinkTargetString($Item) {
    $t = $Item.Target
    if ($null -eq $t) { return $null }
    if ($t -is [array]) { return [string]$t[0] }
    return [string]$t
}

function Resolve-MaybeRelative([string]$BaseDir, [string]$Target) {
    if ([string]::IsNullOrWhiteSpace($Target)) { return $null }
    if ([System.IO.Path]::IsPathRooted($Target)) {
        return [System.IO.Path]::GetFullPath($Target)
    }
    return [System.IO.Path]::GetFullPath((Join-Path $BaseDir $Target))
}

function Get-Text([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    return [System.IO.File]::ReadAllText($Path)
}

function Test-WhitespaceOnly([string]$Path) {
    $t = Get-Text $Path
    return [string]::IsNullOrWhiteSpace($t)
}

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
    return [string]::Equals($norm, '.vibeflow/REGRAS.md', [StringComparison]::OrdinalIgnoreCase)
}

# --- inventário (zero escrita) -----------------------------------------------

function Get-VibeflowState([string]$Vf) {
    if (-not (Test-Path -LiteralPath $Vf)) { return 'ausente' }
    $regras = Join-Path $Vf 'REGRAS.md'
    if (Test-Path -LiteralPath $regras) { return 'com_regras' }
    $kids = @(Get-ChildItem -LiteralPath $Vf -Force -ErrorAction SilentlyContinue)
    if ($kids.Count -eq 0) { return 'vazia' }
    return 'sem_regras'
}

function Get-RegrasFileState([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) { return 'ausente' }
    if (Test-WhitespaceOnly $Path) { return 'vazio' }
    $slots = @(Get-OpenSlots (Get-Text $Path))
    if ($slots.Count -gt 0) { return 'template' }
    return 'preenchido'
}

function Get-RegrasState([string]$Repo, [string]$VfRegras, [string]$RootRegras) {
    $hasVf = Test-Path -LiteralPath $VfRegras
    $hasRoot = Test-Path -LiteralPath $RootRegras
    if ($hasVf -and $hasRoot) { return 'raiz_e_vibeflow' }
    if ($hasRoot -and -not $hasVf) { return 'raiz_sozinho' }
    return (Get-RegrasFileState $VfRegras)
}

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
            if ([string]::Equals($resolved, $want, [StringComparison]::OrdinalIgnoreCase)) {
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

function New-OldDest([string]$OldDir, [string]$Name) {
    $dest = Join-Path $OldDir $Name
    if (-not (Test-Path -LiteralPath $dest)) { return $dest }
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    return (Join-Path $OldDir "$Name.$stamp")
}

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
    $tmp = "$LinkPath.__vibe_symlink__"
    if (Test-Path -LiteralPath $tmp) { Remove-Item -LiteralPath $tmp -Force }
    try {
        New-Item -ItemType SymbolicLink -Path $tmp -Target $TargetRel -ErrorAction Stop | Out-Null
    } catch {
        throw "SYMLINK_RECUSADO: o OS recusou criar o link '$LinkPath' -> '$TargetRel'. Ative o Developer Mode (Configurações → Sistema → Para desenvolvedores) ou rode como administrador. Sem cópia na raiz — o original permanece."
    }
    if (Test-Path -LiteralPath $LinkPath) {
        Remove-Item -LiteralPath $LinkPath -Force
    }
    Rename-Item -LiteralPath $tmp -NewName (Split-Path -Leaf $LinkPath)
}

# --- scan: só SLOT aberto + evidência ----------------------------------------

function Get-ProjectName([string]$Repo) {
    $pkg = Join-Path $Repo 'package.json'
    if (Test-Path -LiteralPath $pkg) {
        try {
            $n = (Get-Content -LiteralPath $pkg -Raw | ConvertFrom-Json).name
            if ($n) { return @{ value = [string]$n; from = 'package.json' } }
        } catch {}
    }
    $py = Join-Path $Repo 'pyproject.toml'
    if (Test-Path -LiteralPath $py) {
        $raw = Get-Text $py
        $m = [regex]::Match($raw, '(?ms)\[project\].*?^name\s*=\s*["'']([^"'']+)["'']')
        if ($m.Success) { return @{ value = $m.Groups[1].Value; from = 'pyproject.toml' } }
    }
    $go = Join-Path $Repo 'go.mod'
    if (Test-Path -LiteralPath $go) {
        $m = [regex]::Match((Get-Text $go), '(?m)^module\s+(\S+)')
        if ($m.Success) {
            $mod = $m.Groups[1].Value
            $leaf = ($mod -split '/')[-1]
            return @{ value = $leaf; from = 'go.mod' }
        }
    }
    return @{ value = (Split-Path -Leaf $Repo); from = 'pasta' }
}

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

function Get-ParagrafoEvidence([string]$Repo) {
    foreach ($name in @('README.md', 'README.MD', 'readme.md')) {
        $p = Join-Path $Repo $name
        if (Test-Path -LiteralPath $p) {
            $para = Get-UsefulParagraph (Get-Text $p)
            if ($para) { return @{ text = $para; from = $name } }
        }
    }
    $pkg = Join-Path $Repo 'package.json'
    if (Test-Path -LiteralPath $pkg) {
        try {
            $d = (Get-Content -LiteralPath $pkg -Raw | ConvertFrom-Json).description
            if ($d) { return @{ text = [string]$d; from = 'package.json' } }
        } catch {}
    }
    $py = Join-Path $Repo 'pyproject.toml'
    if (Test-Path -LiteralPath $py) {
        $raw = Get-Text $py
        $m = [regex]::Match($raw, '(?ms)\[project\].*?^description\s*=\s*["'']([^"'']+)["'']')
        if ($m.Success) { return @{ text = $m.Groups[1].Value; from = 'pyproject.toml' } }
    }
    return $null
}

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
    return @($out)
}

function Get-Stack([string]$Repo) {
    $names = @(
        'package.json', 'pyproject.toml', 'go.mod', 'Cargo.toml', 'composer.json',
        'Gemfile', 'pom.xml', 'build.gradle', 'requirements.txt', 'Pipfile'
    )
    return @($names | Where-Object { Test-Path -LiteralPath (Join-Path $Repo $_) })
}

function Test-Migrations([string]$Repo) {
    $hits = @(
        'prisma/migrations', 'alembic', 'alembic.ini', 'drizzle',
        'knexfile.js', 'knexfile.ts', 'supabase/migrations'
    )
    foreach ($h in $hits) {
        if (Test-Path -LiteralPath (Join-Path $Repo $h)) { return $true }
    }
    $django = Get-ChildItem -LiteralPath $Repo -Recurse -Directory -Filter 'migrations' -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch 'node_modules|\\.git|vendor' } |
        Select-Object -First 1
    return [bool]$django
}

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

function Set-Slot([string]$Content, [string]$Slot, [string]$Value, [string]$Evidencia) {
    $pattern = "(?m)^<!--\s*SLOT:$([regex]::Escape($Slot))\s*-->\s*\r?\n(?:<!--\s*evidência:[^\n]*-->\s*\r?\n)?"
    $repl = $Value.TrimEnd() + "`n"
    if ($null -ne $Evidencia) { $repl += "<!-- evidência: $Evidencia -->`n" }
    return [regex]::Replace($Content, $pattern, { $repl }, 1)
}

# --- fluxo -------------------------------------------------------------------

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
    $targetRel = '.vibeflow/REGRAS.md'

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

    function Add-Action([string]$Op, [string]$Alvo) {
        [void]$actions.Add([ordered]@{ op = $Op; alvo = $Alvo })
    }

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
        $gitkeep = Join-Path $phases '.gitkeep'
        if (-not (Test-Path -LiteralPath $gitkeep)) { [System.IO.File]::WriteAllText($gitkeep, '') }
        Add-Action 'criar_phases' '.vibeflow/phases'
    }
    $gi = Join-Path $vf '.gitignore'
    if (-not (Test-Path -LiteralPath $gi)) {
        [System.IO.File]::WriteAllText($gi, "init-report.json`n")
    }

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

    $mergePending = $false
    if (-not $ApplyPointers) {
        if ($needTemplate -or $regrasContentState -eq 'vazio' -or $inventory.regras -eq 'ausente') {
            if ($agentsLegado -and $claudeLegado -and -not $agentsEqClaude) {
                $mergePending = $true
                [void]$merges.Add([ordered]@{
                    id      = 'duas_fontes'
                    sources = @('.vibeflow/old/AGENTS.md', '.vibeflow/old/CLAUDE.md')
                    target  = '.vibeflow/REGRAS.md'
                })
            } elseif ($agentsLegado -or $claudeLegado) {
                $mergePending = $true
                $src = @()
                if ($agentsLegado) { $src += '.vibeflow/old/AGENTS.md' }
                if ($claudeLegado) { $src += '.vibeflow/old/CLAUDE.md' }
                [void]$merges.Add([ordered]@{
                    id      = 'legado_vs_regras'
                    sources = $src
                    target  = '.vibeflow/REGRAS.md'
                })
            }
        } elseif ($inventory.regras -eq 'template' -or $inventory.regras -eq 'preenchido') {
            $src = @()
            if ($agentsLegado) { $src += '.vibeflow/old/AGENTS.md' }
            if ($claudeLegado) { $src += '.vibeflow/old/CLAUDE.md' }
            if ($src.Count -gt 0) {
                $mergePending = $true
                $src += '.vibeflow/old/REGRAS.md'
                [void]$merges.Add([ordered]@{
                    id      = 'legado_vs_regras'
                    sources = $src
                    target  = '.vibeflow/REGRAS.md'
                })
            }
        } elseif ($inventory.regras -eq 'raiz_e_vibeflow' -and -not (Test-SameBytes $rootRegras $vfRegras)) {
            $mergePending = $true
            [void]$merges.Add([ordered]@{
                id      = 'regras_duplicado'
                sources = @('.vibeflow/old/REGRAS-raiz.md', '.vibeflow/old/REGRAS.md')
                target  = '.vibeflow/REGRAS.md'
            })
        }
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
    if ($agentsLegado -or $inventory.agents -in @('arquivo_igual', 'ponteiro_texto')) { [void](Save-Old $agentsPath 'AGENTS.md') }
    if ($claudeLegado -or $inventory.claude -in @('arquivo_igual', 'ponteiro_texto')) { [void](Save-Old $claudePath 'CLAUDE.md') }
    if ($inventory.regras -eq 'raiz_sozinho' -or $inventory.regras -eq 'raiz_e_vibeflow') {
        [void](Save-Old $rootRegras 'REGRAS-raiz.md')
    }
    if ($mergePending -and ($inventory.regras -in @('template', 'preenchido', 'raiz_e_vibeflow')) -and (Test-Path -LiteralPath $vfRegras) -and -not (Test-WhitespaceOnly $vfRegras)) {
        [void](Save-Old $vfRegras 'REGRAS.md')
    }

    if ($StopAfterOld) {
        Write-Report $repo $flow $inventory $olds $actions $merges $conflicts $avisos @{} @() $false @{} $false $false
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
    function Convert-Pointer([string]$Name, [string]$State) {
        $path = Join-Path $repo $Name
        $key = $Name.ToLower()
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
            Remove-Item -LiteralPath $path -Force
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

    # scan: só SLOT ainda aberto
    $filled = [ordered]@{}
    $nome = Get-ProjectName $repo
    $filled['nome'] = $nome
    $estrutura = @(Get-Estrutura $repo)
    $stack = @(Get-Stack $repo)
    $mig = Test-Migrations $repo
    $evidPara = Get-ParagrafoEvidence $repo
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

    if ($IsWindows -or $env:OS -match 'Windows') {
        $cs = & git -C $repo config --get core.symlinks 2>$null
        if ($cs -and $cs.Trim() -ne 'true') {
            [void]$avisos.Add('git core.symlinks não é true (aviso; não forçado)')
        }
    }

    Write-Report $repo $flow $inventory $olds $actions $merges $conflicts $avisos $filled $slotsAbertos $mig $scan $syAgents $syClaude
}

function Write-Report(
    $repo, $flow, $inventory, $olds, $actions, $merges, $conflicts, $avisos,
    $filled, $slotsAbertos, $mig, $scan, $syAgents, $syClaude
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
    }
    $jsonPath = Join-Path $vf 'init-report.json'
    $json = $report | ConvertTo-Json -Depth 10
    $utf8 = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($jsonPath, $json, $utf8)
    Write-Output $jsonPath
}

Invoke-VibeInit
