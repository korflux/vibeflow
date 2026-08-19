#!/usr/bin/env bash
# vibe-interview/scripts/interview.sh — seleciona uma implementação completa com o mesmo contrato no Unix.
set -euo pipefail

ROOT=""
APPLY=0
SLUG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) ROOT="$2"; shift 2 ;;
    --apply) APPLY=1; shift ;;
    --slug) SLUG="$2"; shift 2 ;;
    *) echo "uso: interview.sh [--root DIR] [--apply --slug SLUG]" >&2; exit 2 ;;
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
  [[ "$APPLY" -eq 1 ]] && args+=(--apply)
  [[ -n "$SLUG" ]] && args+=(--slug "$SLUG")
  exec "$PYTHON_BIN" "$(dirname "$0")/interview.py" "${args[@]}"
fi

if command -v pwsh >/dev/null 2>&1 && pwsh -NoProfile -Command 'exit [int]($PSVersionTable.PSVersion.Major -lt 7)' >/dev/null 2>&1; then
  args=()
  [[ -n "$ROOT" ]] && args+=(-Root "$ROOT")
  [[ "$APPLY" -eq 1 ]] && args+=(-Apply)
  [[ -n "$SLUG" ]] && args+=(-Slug "$SLUG")
  exec pwsh -NoProfile -ExecutionPolicy Bypass -File "$(dirname "$0")/interview.ps1" "${args[@]}"
fi

echo "interview.sh precisa de Python 3 ou PowerShell 7+." >&2
exit 1
