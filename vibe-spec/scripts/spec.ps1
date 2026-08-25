#Requires -Version 7.0
# vibe-spec/scripts/spec.ps1
# Inventário de .vibeflow/phases → promove spec-wip.md para phase-N-slug/spec.md.
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
$script:ChainFiles = @('interview.md', 'spec.md', 'plan.md', 'analyze.md', 'implement.md', 'review.md')
$script:MaxSlug = 48

# Resolve a raiz por parâmetro, Git ou cwd sem exigir que Git esteja instalado.
function Get-RepoRoot {
    if ($Root) { return (Resolve-Path -LiteralPath $Root).Path }
    if (Get-Command git -ErrorAction SilentlyContinue) {
        $git = & git rev-parse --show-toplevel 2>$null
        if ($LASTEXITCODE -eq 0 -and $git) { return $git.Trim() }
    }
    return (Get-Location).Path
}

# Calcula o hash usado para validar a cópia do wip byte a byte.
function Get-Sha256File([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

# Lê texto operacional que precisa ser preservado integralmente.
function Read-Utf8File([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    return [System.IO.File]::ReadAllText($Path)
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

# Garante que relatório e wip não entrem no Git sem apagar as entradas das outras skills.
function Assert-SpecGitignore([string]$Vf) {
    $gi = Join-Path $Vf '.gitignore'
    Add-GitignoreEntry $gi 'spec-report.json'
    Add-GitignoreEntry $gi 'spec-wip.md'
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

# Representa o alvo MVP sem inferir a rota a partir do conteúdo do projeto.
function Get-MvpMap([string]$Vf) {
    $mvpPath = Join-Path $Vf 'mvp'
    if (-not (Test-Path -LiteralPath $mvpPath)) { return $null }
    $item = Get-Item -LiteralPath $mvpPath -Force
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

# Maior n com interview e sem spec: a spec deve reusar esta pasta.
function Get-InterviewPendente($Existing) {
    foreach ($item in ($Existing | Sort-Object n -Descending)) {
        if ($item.files -contains 'interview.md' -and $item.files -notcontains 'spec.md') {
            return $item
        }
    }
    return $null
}

# Maior n com spec e sem plan: rascunho ainda atualizável.
function Get-Rascunho($Existing) {
    foreach ($item in ($Existing | Sort-Object n -Descending)) {
        if ($item.files -contains 'spec.md' -and $item.files -notcontains 'plan.md') {
            return $item
        }
    }
    return $null
}

# Destino preferido: interview pendente, senão rascunho, senão criar.
function Get-Alvo($Existing) {
    $pending = Get-InterviewPendente $Existing
    if ($null -ne $pending) { return @{ item = $pending; modo = 'reuse' } }
    $draft = Get-Rascunho $Existing
    if ($null -ne $draft) { return @{ item = $draft; modo = 'atualizar' } }
    return @{ item = $null; modo = 'criar' }
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
function Write-SpecReport([string]$Vf, [hashtable]$Payload) {
    $reportPath = Join-Path $Vf 'spec-report.json'
    $json = [string](ConvertTo-Json -InputObject $Payload -Depth 8)
    $utf8 = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($reportPath, $json, $utf8)
    Write-Output $reportPath
}

# Inventaria o disco e opcionalmente promove o wip para spec.md.
function Invoke-Spec {
    if ($Mvp -and ($script:SlugWasBound -or $script:DirWasBound)) {
        throw 'MODO_INVALIDO: o alvo MVP não aceita -Slug nem -Dir.'
    }

    $repo = Get-RepoRoot
    $vf = Join-Path $repo '.vibeflow'
    $phases = Join-Path $vf 'phases'
    $wip = Join-Path $vf 'spec-wip.md'
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

    Assert-SpecGitignore $vf
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
    if ($Mvp -and ($null -eq $mvpMap -or $mvpMap.files -notcontains 'interview.md')) {
        throw 'MVP_INTERVIEW_AUSENTE: falta .vibeflow/mvp/interview.md.'
    }
    $created = $null
    $modo = $null

    if ($Apply) {
        if (-not (Test-Path -LiteralPath $wip) -or (Get-Item -LiteralPath $wip).Length -eq 0) {
            throw 'WIP_AUSENTE: falta .vibeflow/spec-wip.md preenchido.'
        }

        $createdDir = $false
        if ($Mvp) {
            $destDir = Join-Path $vf 'mvp'
            $modo = if (Test-Path -LiteralPath (Join-Path $destDir 'spec.md') -PathType Leaf) { 'atualizar' } else { 'reuse' }
        } elseif (-not [string]::IsNullOrWhiteSpace($Dir)) {
            $destDir = Join-Path $phases ([System.IO.Path]::GetFileName($Dir))
            if (-not (Test-Path -LiteralPath $destDir) -or -not (Get-Item -LiteralPath $destDir).PSIsContainer) {
                throw "FASE_AUSENTE: .vibeflow/phases/$([System.IO.Path]::GetFileName($Dir)) não existe."
            }
            $name = [System.IO.Path]::GetFileName($destDir)
            if (-not [regex]::IsMatch($name, '^phase-(\d+)-([a-z0-9]+(?:-[a-z0-9]+)*)$')) {
                throw "FASE_AUSENTE: $name não é uma pasta de fase."
            }
            $modo = if (Test-Path -LiteralPath (Join-Path $destDir 'spec.md')) { 'atualizar' } else { 'reuse' }
        } elseif ($null -ne $alvoItem) {
            $destDir = Join-Path $repo $alvoItem.path
            $modo = $modoSugerido
        } else {
            if ([string]::IsNullOrWhiteSpace($Slug)) {
                throw 'SPEC_SEM_ALVO: sem fase alvo; passe -Slug para abrir uma pasta nova.'
            }
            $clean = ConvertTo-Slug $Slug
            if ($clean.Length -lt 2) {
                throw 'SLUG_INVALIDO: a frase curta não gerou um slug utilizável.'
            }
            $destDir = Join-Path $phases "phase-$nextN-$clean"
            if (Test-Path -LiteralPath $destDir) {
                throw "FASE_EXISTE: .vibeflow/phases/phase-$nextN-$clean já existe."
            }
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            $createdDir = $true
            $modo = 'criar'
        }

        $destFile = Join-Path $destDir 'spec.md'
        $destName = [System.IO.Path]::GetFileName($destDir)
        $rel = if ($Mvp) { '.vibeflow/mvp' } else { ".vibeflow/phases/$destName" }
        if (Test-Path -LiteralPath (Join-Path $destDir 'plan.md')) {
            if ($createdDir -and -not (Get-ChildItem -LiteralPath $destDir -Force)) {
                Remove-Item -LiteralPath $destDir -Force
            }
            throw "SPEC_JA_PLANEJADA: $destName já tem plan.md. Não pise. Pedido novo = outra phase."
        }

        $tempFile = Join-Path $destDir ('.spec-' + [System.IO.Path]::GetRandomFileName())
        try {
            Copy-Item -LiteralPath $wip -Destination $tempFile
            $srcHash = Get-Sha256File $wip
            $dstHash = Get-Sha256File $tempFile
            $srcLen = (Get-Item -LiteralPath $wip).Length
            $dstLen = (Get-Item -LiteralPath $tempFile).Length
            if ($srcHash -ne $dstHash -or $srcLen -ne $dstLen) {
                throw 'COPY_HASH_MISMATCH: a cópia do wip não bateu com o original.'
            }
            [System.IO.File]::Move($tempFile, $destFile, $true)
        } catch {
            if (Test-Path -LiteralPath $tempFile) { Remove-Item -LiteralPath $tempFile -Force }
            if ($createdDir) {
                if ((Test-Path -LiteralPath $destDir) -and -not (Get-ChildItem -LiteralPath $destDir -Force)) {
                    Remove-Item -LiteralPath $destDir -Force
                }
            }
            throw
        }
        Remove-Item -LiteralPath $wip -Force
        $actions.Add([pscustomobject]@{ op = 'promover_wip'; alvo = "$rel/spec.md" })
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
    $wipState = 'ausente'
    if (Test-Path -LiteralPath $wip) { $wipState = 'presente' }

    $payload = @{
        root                = "$repo"
        rota                = $(if ($Mvp) { 'mvp' } else { 'phase' })
        vibeflow            = 'ok'
        phases              = "$phState"
        next_n              = [int]$nextN
        existing            = $mapped.ToArray()
        interview_pendente  = ConvertTo-PhaseMap (Get-InterviewPendente $existing)
        rascunho            = ConvertTo-PhaseMap (Get-Rascunho $existing)
        alvo                = $(if ($Mvp) { $mvpMap } else { ConvertTo-PhaseMap $alvoItem })
        mvp                 = $mvpMap
        modo_sugerido       = $(if ($Mvp -and $mvpMap.files -contains 'spec.md') { 'atualizar' } elseif ($Mvp) { 'reuse' } else { "$modoSugerido" })
        wip                 = "$wipState"
        created             = $(if ($Mvp) { $created } else { ConvertTo-PhaseMap $created })
        modo                = $modo
        actions             = $actions.ToArray()
        avisos              = $warnings.ToArray()
    }
    Write-SpecReport $vf $payload
}

try {
    Invoke-Spec
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}
