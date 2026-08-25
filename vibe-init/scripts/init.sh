#!/usr/bin/env bash
# vibe-init/scripts/init.sh — Executa o setup de infraestrutura no Unix.
set -euo pipefail

ROOT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) ROOT="$2"; shift 2 ;;
    *) echo "uso: init.sh [--root DIR]" >&2; exit 2 ;;
  esac
done

PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

if [[ -n "$PYTHON_BIN" ]]; then
  args=()
  [[ -n "$ROOT" ]] && args+=(--root "$ROOT")
  exec "$PYTHON_BIN" "$(dirname "$0")/init.py" "${args[@]}"
fi

if command -v pwsh >/dev/null 2>&1; then
  args=()
  [[ -n "$ROOT" ]] && args+=(-Root "$ROOT")
  exec pwsh -NoProfile -ExecutionPolicy Bypass -File "$(dirname "$0")/init.ps1" "${args[@]}"
fi
echo "init.sh precisa de Python 3 ou PowerShell 7+." >&2
exit 1
