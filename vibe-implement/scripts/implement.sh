#!/usr/bin/env bash
# vibe-implement/scripts/implement.sh — seleciona uma implementação completa com o mesmo contrato no Unix.
set -euo pipefail

ROOT=""
DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) ROOT="$2"; shift 2 ;;
    --dir) DIR="$2"; shift 2 ;;
    --apply|--slug|-Apply|-Slug)
      echo "FLAG_DESCONHECIDA: $1 não existe nesta skill." >&2
      exit 1
      ;;
    *)
      echo "FLAG_DESCONHECIDA: $1 não existe nesta skill." >&2
      exit 1
      ;;
  esac
done

# Prefere Python 3 por ser portátil; pwsh permanece como fallback integral, não degradado.
PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1 && python3 -c 'import sys; raise SystemExit(sys.version_info.major != 3)' >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1 && python -c 'import sys; raise SystemExit(sys.version_info.major != 3)' >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

if [[ -n "$PYTHON_BIN" ]]; then
  args=()
  [[ -n "$ROOT" ]] && args+=(--root "$ROOT")
  [[ -n "$DIR" ]] && args+=(--dir "$DIR")
  exec "$PYTHON_BIN" "$(dirname "$0")/implement.py" "${args[@]}"
fi

if command -v pwsh >/dev/null 2>&1; then
  args=()
  [[ -n "$ROOT" ]] && args+=(-Root "$ROOT")
  [[ -n "$DIR" ]] && args+=(-Dir "$DIR")
  exec pwsh -File "$(dirname "$0")/implement.ps1" "${args[@]}"
fi

echo "implement.sh precisa de Python 3 ou PowerShell 7+." >&2
exit 1
