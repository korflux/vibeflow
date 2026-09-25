#!/usr/bin/env bash
# Confere o launcher Unix em uma pasta descartável.
set -euo pipefail

here=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
repo=$(mktemp -d)
trap 'rm -rf -- "$repo"' EXIT

bash "$here/../../../vibe-init/scripts/init.sh" --root "$repo" >/dev/null
test -f "$repo/AGENTS.md"
test ! -e "$repo/CLAUDE.md"
test ! -e "$repo/.vibeflow/REGRAS.md"
test "$(cat "$repo/.agents/rules/vibeflow.md")" = '@../../AGENTS.md'
