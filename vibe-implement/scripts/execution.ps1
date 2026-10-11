# Estado mecânico de coordenacao-v1; dot-sourced pelo motor, sem executar evidências.
$script:CoordinateProtocol = 'coordenacao-v1'
$script:CoordinateHash = '^(?:[a-f0-9]{40}|[a-f0-9]{64})$'

# Código estável distingue corrupção da invalidação normal de uma prova.
function Stop-Coordinate([string]$Message) { throw "EXECUTION_INVALIDO: $Message" }

# Cada componente é validado antes de ler ou substituir, inclusive links quebrados.
function Get-CoordinatePath([string]$Repo, $Relative) {
    if ($Relative -isnot [string] -or $Relative.Length -eq 0 -or $Relative.Length -gt 512 -or $Relative.Contains('\') -or $Relative.Contains(':') -or $Relative.StartsWith('/') -or $Relative.StartsWith('-') -or @($Relative.Split('/') | Where-Object { $_ -in @('', '.', '..', '.git') }).Count) { Stop-Coordinate 'path inválido' }
    if ($Relative -match '[\x00-\x1f]' -or @($Relative.Split('/') | Where-Object { $_.EndsWith('.') -or $_.EndsWith(' ') -or $_ -match '^(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?$' }).Count) { Stop-Coordinate 'path inválido' }
    $path = $Repo
    foreach ($part in $Relative.Split('/')) {
        $path = Join-Path $path $part
        if (Test-IsReparsePoint (Get-FsItem $path)) { Stop-Coordinate 'link/reparse point' }
    }
    return $path
}

# Argumentos Git são constantes; a string do comando de prova nunca é executada.
function Invoke-CoordinateGit([string]$Repo, [string[]]$Arguments) {
    $output = @(& git -C $Repo @Arguments 2>$null)
    if ($LASTEXITCODE -ne 0) { Stop-Coordinate 'Git não comprovou a operação' }
    return ($output -join "`n").Trim()
}

# Comparação ordinal de chaves mantém o schema equivalente ao motor Python.
function Test-CoordinateKeys($Value, [string[]]$Keys) {
    return $Value -is [Collections.IDictionary] -and $Value.Count -eq $Keys.Count -and @($Value.Keys | Where-Object { $_ -cnotin $Keys }).Count -eq 0
}

# Identidade operacional do executor, sem dados pessoais ou credenciais.
function Test-CoordinateActor($Value) { return $Value -is [string] -and $Value -cmatch '^[a-zA-Z0-9_.-]{1,64}$' }

# Valida formato antes da checagem de hash/ancestralidade; prova alterada não é JSON corrupto.
function Assert-CoordinateProof($Proof, [string]$Repo, [string]$Target) {
    if (-not (Test-CoordinateKeys $Proof @('head','inputs','comando','resultado'))) { Stop-Coordinate 'snapshot inválido' }
    if ($Proof.head -isnot [string] -or $Proof.head -cnotmatch $script:CoordinateHash) { Stop-Coordinate 'HEAD inválido' }
    if ($Proof.resultado -cnotin @('verde','falha') -or $Proof.comando -isnot [string] -or -not $Proof.comando.Trim() -or $Proof.comando.Trim().Length -gt 2048) { Stop-Coordinate 'resultado/comando inválido' }
    if ($Proof.inputs -isnot [Collections.IDictionary] -or $Proof.inputs.Count -lt 1 -or $Proof.inputs.Count -gt 256) { Stop-Coordinate 'inputs inválidos' }
    foreach ($relative in $Proof.inputs.Keys) {
        $null = Get-CoordinatePath $Repo $relative
        if ($relative -in @("$Target/plan.md", "$Target/spec.md", "$Target/review.md", "$Target/execution.json")) { Stop-Coordinate 'artefato operacional não é input' }
        if ($Proof.inputs[$relative] -isnot [string] -or $Proof.inputs[$relative] -cnotmatch $script:CoordinateHash) { Stop-Coordinate 'hash inválido' }
    }
}

# Parse JSON nativo verifica duplicatas em qualquer objeto antes da conversão para hashtable.
function Assert-CoordinateJson($Element) {
    if ($Element.ValueKind -eq [Text.Json.JsonValueKind]::Object) {
        $seen = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
        foreach ($property in $Element.EnumerateObject()) {
            if (-not $seen.Add($property.Name)) { Stop-Coordinate 'chave duplicada' }
            Assert-CoordinateJson $property.Value
        }
    } elseif ($Element.ValueKind -eq [Text.Json.JsonValueKind]::Array) {
        foreach ($item in $Element.EnumerateArray()) { Assert-CoordinateJson $item }
    }
}

# O grafo define trabalho; checkboxes do plan são somente resumo neste protocolo.
function Get-CoordinateGraph([string]$Text) {
    $graph = @{}
    $sections = @([regex]::Matches($Text, '(?ms)^### (T\d+):[^\r\n]*\r?\n(.*?)(?=^### T\d+:|\z)'))
    if ($sections.Count -lt 1 -or $sections.Count -gt 500) { Stop-Coordinate 'quantidade de tasks inválida' }
    foreach ($section in $sections) {
        $tid = $section.Groups[1].Value
        $deps = @([regex]::Matches($section.Groups[2].Value, '(?m)^- \*\*Deps:\*\*\s*([^\r\n]*)'))
        if ($graph.ContainsKey($tid) -or $tid -cnotmatch '^T[1-9]\d*$' -or $deps.Count -ne 1 -or $deps[0].Groups[1].Value -cnotmatch '^(?:nenhuma|T[1-9]\d*(?:[ ,]+T[1-9]\d*)*)$') { Stop-Coordinate 'task/Deps inválida' }
        $graph[$tid] = @([regex]::Matches($deps[0].Groups[1].Value, 'T\d+') | ForEach-Object { $_.Value } | Select-Object -Unique)
    }
    $visited = [Collections.Generic.HashSet[string]]::new()
    $active = [Collections.Generic.HashSet[string]]::new()
    # DFS recusa ciclos ou referência inexistente antes de liberar qualquer tarefa.
    function Visit-CoordinateTask([string]$Id) {
        if (-not $graph.ContainsKey($Id) -or $active.Contains($Id)) { Stop-Coordinate 'dependência inexistente ou ciclo' }
        if ($visited.Contains($Id)) { return }
        $null = $active.Add($Id)
        foreach ($dep in $graph[$Id]) { Visit-CoordinateTask $dep }
        $null = $active.Remove($Id)
        $null = $visited.Add($Id)
    }
    foreach ($tid in $graph.Keys) { Visit-CoordinateTask $tid }
    return $graph
}

# Leitura estrita do único estado operacional; ausência não escreve arquivo.
function Read-CoordinateState([string]$Path, $Graph, [string]$Repo, [string]$Target) {
    $empty = @{ schema = 1; protocolo = $script:CoordinateProtocol; tasks = @{}; integracao = $null; commit = $null }
    if (-not (Test-Path -LiteralPath $Path)) { return $empty }
    $item = Get-FsItem $Path
    if ($item -isnot [IO.FileInfo] -or $item.Length -gt 1048576) { Stop-Coordinate 'arquivo/tamanho inválido' }
    try {
        $text = [IO.File]::ReadAllText($Path, [Text.UTF8Encoding]::new($false, $true))
        $document = [Text.Json.JsonDocument]::Parse($text)
        try { Assert-CoordinateJson $document.RootElement } finally { $document.Dispose() }
        $state = ConvertFrom-Json -InputObject $text -AsHashtable -Depth 20
    } catch { Stop-Coordinate 'JSON/encoding inválido' }
    if ((-not (Test-CoordinateKeys $state @('schema','protocolo','tasks','integracao','commit')) -and -not (Test-CoordinateKeys $state @('schema','protocolo','tasks','integracao','commit','correcao'))) -or $state.schema -is [bool] -or $state.schema -is [double] -or $state.schema -is [string] -or $state.schema -ne 1 -or $state.protocolo -cne $script:CoordinateProtocol -or $state.tasks -isnot [Collections.IDictionary]) { Stop-Coordinate 'schema inválido' }
    foreach ($tid in $state.tasks.Keys) {
        $row = $state.tasks[$tid]
        if ($tid -cnotin $Graph.Keys -or -not (Test-CoordinateKeys $row @('actor','proof')) -or -not (Test-CoordinateActor $row.actor)) { Stop-Coordinate 'task registrada inválida' }
        Assert-CoordinateProof $row.proof $Repo $Target
    }
    $integration = $state.integracao
    if ($null -ne $integration) {
        if (-not (Test-CoordinateKeys $integration @('actor','proof','origem')) -or -not (Test-CoordinateActor $integration.actor) -or $integration.origem -isnot [string] -or $integration.origem -cnotmatch $script:CoordinateHash) { Stop-Coordinate 'integração inválida' }
        Assert-CoordinateProof $integration.proof $Repo $Target
        if ($state.tasks.Count -ne $Graph.Count -or $integration.actor -cin @($state.tasks.Values | ForEach-Object { $_.actor })) { Stop-Coordinate 'integração sem independência' }
    }
    if ($null -ne $state.commit -and ($null -eq $integration -or $state.commit -isnot [string] -or $state.commit -cnotmatch $script:CoordinateHash)) { Stop-Coordinate 'commit inválido' }
    if ($state.ContainsKey('correcao')) {
        $correction = $state.correcao
        if ($null -eq $state.commit -or -not (Test-CoordinateKeys $correction @('base','commit')) -or ($null -ne $correction.commit -and ($correction.commit -isnot [string] -or $correction.commit -cnotmatch $script:CoordinateHash))) { Stop-Coordinate 'correção inválida' }
        Assert-CoordinateProof $correction.base $Repo $Target
        if ($correction.base.resultado -cne 'verde') { Stop-Coordinate 'base da correção não é verde' }
    }
    return $state
}

# Captura HEAD e hashes diretamente do disco após prova feita pelo responsável.
function New-CoordinateProof([string]$Repo, [string]$Target) {
    if ($InputPath.Count -lt 1 -or $InputPath.Count -gt 256 -or @($InputPath | Select-Object -Unique).Count -ne $InputPath.Count) { Stop-Coordinate 'inputs ausentes/duplicados' }
    $proof = @{ head = Invoke-CoordinateGit $Repo @('rev-parse','HEAD'); inputs = @{}; comando = $Command; resultado = $Result }
    foreach ($relative in $InputPath) {
        $path = Get-CoordinatePath $Repo $relative
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { Stop-Coordinate 'input não é arquivo' }
        $proof.inputs[$relative] = Invoke-CoordinateGit $Repo @('hash-object','--',$relative)
    }
    Assert-CoordinateProof $proof $Repo $Target
    return $proof
}

# Commit deve existir e conter todos os blobs da prova, com título e origem reais.
function Test-CoordinateCommit([string]$Repo, [string]$Sha, [string[]]$Tasks, $Integration) {
    try {
        $subject = Invoke-CoordinateGit $Repo @('show','-s','--format=%s',$Sha)
        if (-not $subject.StartsWith('task(' + ($Tasks -join ',') + '): ') -or $Sha -ceq $Integration.origem) { return $false }
        $null = Invoke-CoordinateGit $Repo @('merge-base','--is-ancestor',$Integration.origem,$Sha)
        $null = Invoke-CoordinateGit $Repo @('merge-base','--is-ancestor',$Sha,'HEAD')
        foreach ($relative in $Integration.proof.inputs.Keys) {
            if ((Invoke-CoordinateGit $Repo @('rev-parse',"${Sha}:$relative")) -cne $Integration.proof.inputs[$relative]) { return $false }
        }
        return $true
    } catch { return $false }
}

# A base T* conserva sua prova; o commit R* precisa conter os blobs atuais.
function Test-CoordinateCorrection([string]$Repo, [string]$Sha, [string[]]$Tasks, $State, [string[]]$CorrectionIds) {
    $baseline = @{ origem = $State.integracao.origem; proof = $State.correcao.base }
    if (-not (Test-CoordinateCommit $Repo $State.commit $Tasks $baseline)) { return $false }
    try {
        $subject = Invoke-CoordinateGit $Repo @('show','-s','--format=%s',$Sha)
        $match = [regex]::Match($subject, '^task\((R[1-9]\d*(?:,R[1-9]\d*)*)\): .+$')
        if (-not $match.Success -or $Sha -ceq $State.commit) { return $false }
        $ids = @($match.Groups[1].Value.Split(','))
        $orderedIds = @($ids | Sort-Object { [int]$_.Substring(1) } -Unique)
        if (($ids -join ',') -cne ($orderedIds -join ',') -or @($ids | Where-Object { $_ -cnotin $CorrectionIds }).Count) { return $false }
        $null = Invoke-CoordinateGit $Repo @('merge-base','--is-ancestor',$State.commit,$Sha)
        $null = Invoke-CoordinateGit $Repo @('merge-base','--is-ancestor',$Sha,'HEAD')
        foreach ($relative in $State.integracao.proof.inputs.Keys) {
            if ((Invoke-CoordinateGit $Repo @('rev-parse',"${Sha}:$relative")) -cne $State.integracao.proof.inputs[$relative]) { return $false }
        }
        return $true
    } catch { return $false }
}

# Troca atômica: arquivo temporário exclusivo no mesmo diretório e limpeza em falha.
function Save-CoordinateState([string]$Path, $State) {
    $data = [Text.UTF8Encoding]::new($false).GetBytes((ConvertTo-Json -InputObject $State -Depth 20) + "`n")
    if ($data.Length -gt 1048576) { Stop-Coordinate 'limite do registro' }
    $temporary = Join-Path ([IO.Path]::GetDirectoryName($Path)) ('.execution-' + [guid]::NewGuid().ToString('N') + '.tmp')
    try {
        $stream = [IO.File]::Open($temporary, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
        try { $stream.Write($data); $stream.Flush($true) } finally { $stream.Dispose() }
        [IO.File]::Move($temporary, $Path, $true)
    } finally { if ([IO.File]::Exists($temporary)) { [IO.File]::Delete($temporary) } }
}

# Deriva validade sem apagar evidências antigas nem executar strings registradas.
function Get-CoordinateValidity([string]$Repo, $Graph, $State, [string[]]$Ordered, [string[]]$CorrectionIds) {
    $ready = @($State.tasks.Keys | Where-Object { (Test-Snapshot $Repo $State.tasks[$_].proof) -and $State.tasks[$_].proof.resultado -ceq 'verde' })
    $valid = $null -ne $State.integracao -and $ready.Count -eq $Graph.Count -and (Test-Snapshot $Repo $State.integracao.proof)
    if ($valid) { foreach ($row in $State.tasks.Values) { foreach ($relative in $row.proof.inputs.Keys) { if ($relative -cnotin $State.integracao.proof.inputs.Keys) { $valid = $false } } } }
    $commitValid = if ($State.ContainsKey('correcao')) { $null -ne $State.correcao.commit -and (Test-CoordinateCorrection $Repo $State.correcao.commit $Ordered $State $CorrectionIds) } else { $null -ne $State.commit -and (Test-CoordinateCommit $Repo $State.commit $Ordered $State.integracao) }
    $committed = $valid -and $State.integracao.proof.resultado -ceq 'verde' -and $commitValid
    return @{ ready = $ready; valid = $valid; committed = $committed }
}

# Opera somente recorte autorizado; stdout compacta o estado para roteamento estratégico.
function Invoke-Coordinate([string]$Repo, [string]$Target, [string]$Text, $Fila, $Review) {
    $graph = Get-CoordinateGraph $Text
    $path = Get-CoordinatePath $Repo "$Target/execution.json"
    $state = Read-CoordinateState $path $graph $Repo $Target
    $ordered = @($graph.Keys | Sort-Object { [int]$_.Substring(1) })
    $reviewPath = Get-CoordinatePath $Repo "$Target/review.md"
    # Reconhece os mesmos R* abertos/fechados da fila, inclusive classificações históricas.
    $correctionIds = @(if ($null -ne $Review -and $Review.legivel -and [IO.File]::Exists($reviewPath)) { [regex]::Matches([IO.File]::ReadAllText($reviewPath), '(?m)^\s*- \[[ xX]\] (R[1-9]\d*):') | ForEach-Object { $_.Groups[1].Value } })
    $validity = Get-CoordinateValidity $Repo $graph $state $ordered $correctionIds
    if ($Operation) {
        if ($Details -or $Text -cnotmatch '(?m)^# Status:\s*aprovado\s*$') { Stop-Coordinate 'mutação exige plan aprovado e sem details' }
        if (-not (Test-CoordinateActor $Actor)) { Stop-Coordinate 'executor inválido' }
        if ($Operation -cin @('init','commit') -and ($Task -or $InputPath.Count -or $Command -or $Result)) { Stop-Coordinate 'campos fora da operação' }
        switch -CaseSensitive ($Operation) {
            'init' { }
            'local' {
                if ($Task -cnotin $graph.Keys -or @($graph[$Task] | Where-Object { $_ -cnotin $validity.ready }).Count) { Stop-Coordinate 'task não elegível' }
                $state.tasks[$Task] = @{ actor = $Actor; proof = New-CoordinateProof $Repo $Target }
                if ($state.integracao -and $state.integracao.actor -ceq $Actor) { Stop-Coordinate 'escritor não pode ser verificador' }
            }
            'integracao' {
                if ($Task -or $validity.ready.Count -ne $graph.Count -or $Actor -cin @($state.tasks.Values | ForEach-Object { $_.actor })) { Stop-Coordinate 'integração exige locais verdes e executor independente' }
                $proof = New-CoordinateProof $Repo $Target
                foreach ($row in $state.tasks.Values) { foreach ($relative in $row.proof.inputs.Keys) { if ($relative -cnotin $proof.inputs.Keys) { Stop-Coordinate 'integração não cobre inputs locais' } } }
                $origin = if ($state.integracao) { $state.integracao.origem } else { $proof.head }
                $inputsChanged = $state.integracao -and ($proof.inputs.Count -ne $state.integracao.proof.inputs.Count -or @($proof.inputs.Keys | Where-Object { $_ -cnotin $state.integracao.proof.inputs.Keys -or $proof.inputs[$_] -cne $state.integracao.proof.inputs[$_] }).Count)
                if (-not $state.ContainsKey('correcao') -and $state.commit -and $inputsChanged -and (Test-CoordinateCommit $Repo $state.commit $ordered $state.integracao)) {
                    $state.correcao = @{ base = $state.integracao.proof; commit = $null }
                }
                $state.integracao = @{ actor = $Actor; proof = $proof; origem = $origin }
            }
            'commit' {
                if (-not $validity.valid -or $state.integracao.proof.resultado -cne 'verde') { Stop-Coordinate 'commit exige integração verde atual' }
                $found = $null
                foreach ($sha in ((Invoke-CoordinateGit $Repo @('log','--format=%H')) -split "`n")) {
                    $matches = if ($state.ContainsKey('correcao')) { Test-CoordinateCorrection $Repo $sha $ordered $state $correctionIds } else { Test-CoordinateCommit $Repo $sha $ordered $state.integracao }
                    if ($matches) { $found = $sha; break }
                }
                if (-not $found) { Stop-Coordinate 'commit integrado não encontrado' }
                if ($state.ContainsKey('correcao')) { $state.correcao.commit = $found } else { $state.commit = $found }
            }
            default { Stop-Coordinate 'operação inválida' }
        }
        if ($Operation -cne 'init' -or -not [IO.File]::Exists($path)) { Save-CoordinateState $path $state }
        $validity = Get-CoordinateValidity $Repo $graph $state $ordered $correctionIds
    }
    $pending = @($ordered | Where-Object { $_ -cnotin $validity.ready })
    $eligible = @($pending | Where-Object { @($graph[$_] | Where-Object { $_ -cnotin $validity.ready }).Count -eq 0 })
    $Fila.parse = 'ok'; $Fila.avisos = @(); $Fila.elegiveis = $eligible
    $Fila.concluidas = @(if ($validity.committed) { $ordered })
    $Fila.abertas = @(if (-not $validity.committed) { $ordered })
    $Fila.bloqueadas = @($pending | Where-Object { $_ -cnotin $eligible } | ForEach-Object { @{ id = $_; deps = @($graph[$_] | Where-Object { $_ -cnotin $validity.ready }) } })
    $stage = if ($pending.Count) { if ($eligible.Count) { 'implementar' } else { 'bloqueada' } } elseif (-not $validity.valid) { 'validar' } elseif ($state.integracao.proof.resultado -cne 'verde') { 'corrigir_validacao' } elseif (-not $validity.committed) { 'commitar_integracao' } else { Get-Etapa $Fila $Review }
    if ($null -ne $Review -and -not $Review.legivel) { $stage = $null } elseif ($null -ne $Review -and $Review.bloqueiosAbertos) { $stage = 'corrigir' }
    $currentCommit = if ($state.ContainsKey('correcao')) { $state.correcao.commit } else { $state.commit }
    $summary = @{ protocolo = $script:CoordinateProtocol; modo = 'A'; registro = "$Target/execution.json"; tasks = @($ordered | ForEach-Object { @{ id = $_; local_valida = $_ -cin $validity.ready } }); integracao = @{ prova_valida = $validity.valid; commit_encontrado = if ($validity.committed) { $currentCommit } else { $null } }; avisos = @() }
    if ($Details) { $summary.detalhes = $state }
    return @{ execucao = $summary; etapa = $stage }
}
