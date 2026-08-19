#Requires -Version 7.0
# vibe-review/scripts/review.ps1
# Inventário de .vibeflow/phases → promove review-wip.md para phase-N-slug/review.md.
param(
    [string]$Root,
    [switch]$Apply,
    [string]$Dir,
    [string]$Slug
)

$ErrorActionPreference = 'Stop'
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
function Assert-ReviewGitignore([string]$Vf) {
    $gi = Join-Path $Vf '.gitignore'
    Add-GitignoreEntry $gi 'review-report.json'
    Add-GitignoreEntry $gi 'review-wip.md'
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

# Maior n com plan e sem review: a review da cadeia reusa esta pasta.
function Get-PlanPendente($Existing) {
    foreach ($item in ($Existing | Sort-Object n -Descending)) {
        if ($item.files -contains 'plan.md' -and $item.files -notcontains 'review.md') {
            return $item
        }
    }
    return $null
}

# Maior n que já tem review.md: rascunho ou re-run ainda atualizável.
function Get-Rascunho($Existing) {
    foreach ($item in ($Existing | Sort-Object n -Descending)) {
        if ($item.files -contains 'review.md') { return $item }
    }
    return $null
}

# Destino preferido: plan sem review, senão rascunho. Sem alvo = avulsa ou REVIEW_SEM_ALVO.
function Get-Alvo($Existing) {
    $pending = Get-PlanPendente $Existing
    if ($null -ne $pending) { return @{ item = $pending; modo = 'reuse' } }
    $draft = Get-Rascunho $Existing
    if ($null -ne $draft) { return @{ item = $draft; modo = 'atualizar' } }
    return @{ item = $null; modo = 'criar' }
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

# Monta o JSON que a skill lê; stdout só o path do relatório.
function Write-ReviewReport([string]$Vf, [hashtable]$Payload) {
    $reportPath = Join-Path $Vf 'review-report.json'
    $json = [string](ConvertTo-Json -InputObject $Payload -Depth 8)
    $utf8 = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($reportPath, $json, $utf8)
    Write-Output $reportPath
}

# Inventaria o disco e opcionalmente promove o wip para review.md.
function Invoke-Review {
    $repo = Get-RepoRoot
    $vf = Join-Path $repo '.vibeflow'
    $phases = Join-Path $vf 'phases'
    $wip = Join-Path $vf 'review-wip.md'
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

    Assert-ReviewGitignore $vf
    $listed = Get-PhaseList $phases
    $existing = @($listed.existing)
    $warnings = New-Object System.Collections.Generic.List[string]
    foreach ($w in $listed.warnings) { $warnings.Add($w) }
    $nextN = 1
    if ($existing.Count -gt 0) { $nextN = [int]$existing[-1].n + 1 }
    $resolved = Get-Alvo $existing
    $alvoItem = $resolved.item
    $modoSugerido = $resolved.modo
    $created = $null
    $modo = $null

    if ($Apply) {
        if (-not (Test-Path -LiteralPath $wip) -or (Get-Item -LiteralPath $wip).Length -eq 0) {
            throw 'WIP_AUSENTE: falta .vibeflow/review-wip.md preenchido.'
        }

        $createdDir = $false
        if (-not [string]::IsNullOrWhiteSpace($Dir)) {
            $destDir = Join-Path $phases ([System.IO.Path]::GetFileName($Dir))
            $destName = [System.IO.Path]::GetFileName($destDir)
            if (-not (Test-Path -LiteralPath $destDir) -or -not (Get-Item -LiteralPath $destDir).PSIsContainer) {
                throw "FASE_AUSENTE: .vibeflow/phases/$destName não é uma pasta de fase."
            }
            if (-not [regex]::IsMatch($destName, '^phase-(\d+)-([a-z0-9]+(?:-[a-z0-9]+)*)$')) {
                throw "FASE_AUSENTE: $destName não é uma pasta de fase."
            }
            $modo = if (Test-Path -LiteralPath (Join-Path $destDir 'review.md')) { 'atualizar' } else { 'reuse' }
        } elseif ($null -ne $alvoItem) {
            $destDir = Join-Path $repo $alvoItem.path
            $modo = $modoSugerido
        } else {
            if ([string]::IsNullOrWhiteSpace($Slug)) {
                throw 'REVIEW_SEM_ALVO: sem fase alvo; passe -Slug para review avulsa.'
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
            $actions.Add([pscustomobject]@{ op = 'criar_fase'; alvo = ".vibeflow/phases/phase-$nextN-$clean" })
        }

        $destName = [System.IO.Path]::GetFileName($destDir)
        $destFile = Join-Path $destDir 'review.md'
        $rel = ".vibeflow/phases/$destName"
        $existed = Test-Path -LiteralPath $destFile
        try {
            Copy-Item -LiteralPath $wip -Destination $destFile -Force
            $srcHash = Get-Sha256File $wip
            $dstHash = Get-Sha256File $destFile
            $srcLen = (Get-Item -LiteralPath $wip).Length
            $dstLen = (Get-Item -LiteralPath $destFile).Length
            if ($srcHash -ne $dstHash -or $srcLen -ne $dstLen) {
                if (-not $existed) { Remove-Item -LiteralPath $destFile -Force }
                if ($createdDir -and (Test-Path -LiteralPath $destDir) -and -not (Get-ChildItem -LiteralPath $destDir -Force)) {
                    Remove-Item -LiteralPath $destDir -Force
                }
                throw 'COPY_HASH_MISMATCH: a cópia do wip não bateu com o original.'
            }
        } catch {
            if ($createdDir) {
                if (Test-Path -LiteralPath $destFile) { Remove-Item -LiteralPath $destFile -Force }
                if ((Test-Path -LiteralPath $destDir) -and -not (Get-ChildItem -LiteralPath $destDir -Force)) {
                    Remove-Item -LiteralPath $destDir -Force
                }
            }
            throw
        }
        Remove-Item -LiteralPath $wip -Force
        $actions.Add([pscustomobject]@{ op = 'promover_wip'; alvo = "$rel/review.md" })
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

    $mapped = New-Object System.Collections.Generic.List[object]
    foreach ($item in @($existing)) {
        if ($null -ne $item) { [void]$mapped.Add((ConvertTo-PhaseMap $item)) }
    }
    $wipState = 'ausente'
    if (Test-Path -LiteralPath $wip) { $wipState = 'presente' }

    $payload = @{
        root               = "$repo"
        vibeflow           = 'ok'
        phases             = "$phState"
        next_n             = [int]$nextN
        existing           = $mapped.ToArray()
        plan_pendente      = ConvertTo-PhaseMap (Get-PlanPendente $existing)
        rascunho           = ConvertTo-PhaseMap (Get-Rascunho $existing)
        alvo               = ConvertTo-PhaseMap $alvoItem
        modo_sugerido      = "$modoSugerido"
        wip                = "$wipState"
        created            = ConvertTo-PhaseMap $created
        modo               = $modo
        actions            = $actions.ToArray()
        avisos             = $warnings.ToArray()
    }
    Write-ReviewReport $vf $payload
}

try {
    Invoke-Review
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}
