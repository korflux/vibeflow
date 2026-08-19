#!/usr/bin/env bash
# vibe-init/scripts/init.sh — seleciona uma implementação completa com o mesmo contrato no Unix.
set -euo pipefail

ROOT=""
APPLY_POINTERS=0
REDIRECT_POINTER=""
STOP_AFTER_OLD=0
MERGE_TOKEN=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) ROOT="$2"; shift 2 ;;
    --apply-pointers) APPLY_POINTERS=1; shift ;;
    --merge-token) MERGE_TOKEN="$2"; shift 2 ;;
    --redirect-pointer) REDIRECT_POINTER="$2"; shift 2 ;;
    --stop-after-old) STOP_AFTER_OLD=1; shift ;;
    *) echo "uso: init.sh [--root DIR] [--apply-pointers --merge-token TOKEN] [--redirect-pointer AGENTS|CLAUDE] [--stop-after-old]" >&2; exit 2 ;;
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
  [[ "$APPLY_POINTERS" -eq 1 ]] && args+=(--apply-pointers)
  [[ -n "$MERGE_TOKEN" ]] && args+=(--merge-token "$MERGE_TOKEN")
  [[ -n "$REDIRECT_POINTER" ]] && args+=(--redirect-pointer "$REDIRECT_POINTER")
  [[ "$STOP_AFTER_OLD" -eq 1 ]] && args+=(--stop-after-old)
  exec "$PYTHON_BIN" "$(dirname "$0")/init.py" "${args[@]}"
fi

if command -v pwsh >/dev/null 2>&1 && pwsh -NoProfile -Command 'exit [int]($PSVersionTable.PSVersion.Major -lt 7)' >/dev/null 2>&1; then
  args=()
  [[ -n "$ROOT" ]] && args+=(-Root "$ROOT")
  [[ "$APPLY_POINTERS" -eq 1 ]] && args+=(-ApplyPointers)
  [[ -n "$MERGE_TOKEN" ]] && args+=(-MergeToken "$MERGE_TOKEN")
  [[ -n "$REDIRECT_POINTER" ]] && args+=(-RedirectPointer "$REDIRECT_POINTER")
  [[ "$STOP_AFTER_OLD" -eq 1 ]] && args+=(-StopAfterOld)
  exec pwsh -NoProfile -ExecutionPolicy Bypass -File "$(dirname "$0")/init.ps1" "${args[@]}"
fi

echo "init.sh precisa de Python 3 ou PowerShell 7+." >&2
exit 1
