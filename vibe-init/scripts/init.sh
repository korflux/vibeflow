#!/usr/bin/env bash
# vibe-init/scripts/init.sh — mesma entrada de init.ps1 no Unix.
# ponytail: delega ao pwsh (fonte da matriz); port nativo só se Unix sem pwsh virar requisito.
set -euo pipefail

ROOT=""
APPLY_POINTERS=0
REDIRECT_POINTER=""
STOP_AFTER_OLD=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) ROOT="$2"; shift 2 ;;
    --apply-pointers) APPLY_POINTERS=1; shift ;;
    --redirect-pointer) REDIRECT_POINTER="$2"; shift 2 ;;
    --stop-after-old) STOP_AFTER_OLD=1; shift ;;
    *) echo "uso: init.sh [--root DIR] [--apply-pointers] [--redirect-pointer AGENTS|CLAUDE] [--stop-after-old]" >&2; exit 2 ;;
  esac
done

if ! command -v pwsh >/dev/null 2>&1; then
  echo "init.sh precisa de pwsh (matriz vive em init.ps1). Instale PowerShell 7+." >&2
  exit 1
fi

args=()
[[ -n "$ROOT" ]] && args+=(-Root "$ROOT")
[[ "$APPLY_POINTERS" -eq 1 ]] && args+=(-ApplyPointers)
[[ -n "$REDIRECT_POINTER" ]] && args+=(-RedirectPointer "$REDIRECT_POINTER")
[[ "$STOP_AFTER_OLD" -eq 1 ]] && args+=(-StopAfterOld)
exec pwsh -File "$(dirname "$0")/init.ps1" "${args[@]}"
