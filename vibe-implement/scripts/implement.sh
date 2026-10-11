#!/usr/bin/env bash
# Launcher integral: valida flags públicas e preserva argv para ambos os motores.
set -euo pipefail

# Recusa sintaxe inválida com a mesma mensagem em qualquer runtime disponível.
usage_error() {
  echo "uso: implement.sh [--root DIR] [--apply] [--slug SLUG] [--dir PASTA] [--mvp] [--operation OP] [--task ID] [--input PATH] [--command TEXTO] [--result RESULTADO] [--actor PAPEL] [--details]" >&2
  exit 2
}

# Valida a interface antes de escolher o motor; valores continuam sendo dados.
arguments=("$@")
for ((index=0; index<${#arguments[@]}; index++)); do
  case "${arguments[index]}" in
    --apply|--mvp|--details) ;;
    --root|--slug|--dir|--operation|--task|--input|--command|--result|--actor)
      if ((index + 1 < ${#arguments[@]})); then
        index=$((index + 1))
        continue
      fi
      usage_error ;;
    *) usage_error ;;
  esac
done

for runtime in python3 python; do
  if command -v "$runtime" >/dev/null 2>&1 && "$runtime" -c 'import sys; raise SystemExit(sys.version_info.major != 3)' >/dev/null 2>&1; then
    exec "$runtime" "$(dirname "$0")/implement.py" "$@"
  fi
done

# Conversão nativa de flags e arrays: nenhuma string de evidência vira código.
if command -v pwsh >/dev/null 2>&1 && pwsh -NoProfile -Command 'exit [int]($PSVersionTable.PSVersion.Major -lt 7)' >/dev/null 2>&1; then
  export VIBE_IMPLEMENT_SCRIPT="$(dirname "$0")/implement.ps1"
  export VIBE_IMPLEMENT_COUNT="$#"
  index=0
  for argument in "$@"; do
    export "VIBE_IMPLEMENT_ARG_${index}=$argument"
    index=$((index + 1))
  done
  exec pwsh -NoProfile -Command '
    $scriptPath = $env:VIBE_IMPLEMENT_SCRIPT
    $arguments = @(for ($index=0; $index -lt [int]$env:VIBE_IMPLEMENT_COUNT; $index++) { [Environment]::GetEnvironmentVariable("VIBE_IMPLEMENT_ARG_$index") })
    $values = @{}
    $map = @{ "--root"="Root"; "--slug"="Slug"; "--dir"="Dir"; "--operation"="Operation"; "--task"="Task"; "--command"="Command"; "--result"="Result"; "--actor"="Actor" }
    for ($i=0; $i -lt $arguments.Count; $i++) {
      $flag = $arguments[$i]
      if ($flag -cin @("--apply", "--mvp", "--details")) { $values[$flag.Substring(2)] = $true }
      elseif ($flag -ceq "--input" -and $i+1 -lt $arguments.Count) { $values.InputPath = @($values.InputPath | Where-Object { $null -ne $_ }) + $arguments[++$i] }
      elseif ($map.ContainsKey($flag) -and $i+1 -lt $arguments.Count) { $values[$map[$flag]] = $arguments[++$i] }
      else { [Console]::Error.WriteLine("ARGUMENTO_INVALIDO: flag desconhecida ou sem valor"); exit 2 }
    }
    & $scriptPath @values
    exit $LASTEXITCODE
  '
fi

echo "implement.sh precisa de Python 3 ou PowerShell 7+." >&2
exit 1
