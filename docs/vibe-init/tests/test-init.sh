#!/usr/bin/env bash
# Confere o launcher Unix em uma pasta descartável.
set -euo pipefail

here=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
repo=$(mktemp -d)
trap 'rm -rf -- "$repo"' EXIT

# O alias de descoberta representa a instalação por symlink do pacote distribuído.
launcher="$here/../../../skills/vibe-init/scripts/init.sh"
bash "$launcher" --root "$repo" >/dev/null
test -f "$repo/AGENTS.md"
test ! -e "$repo/CLAUDE.md"
test ! -e "$repo/.vibeflow/REGRAS.md"
test "$(cat "$repo/.agents/rules/vibeflow.md")" = '@../../AGENTS.md'

# Confere os dez perfis contra o pacote físico e preserva seus bytes na repetição.
mkdir "$repo/snapshots"
for host in codex claude; do
  extension=toml
  [[ "$host" == claude ]] && extension=md
  for role in explorador implementador verificador corretor revisor; do
    profile="$repo/.$host/agents/$role.$extension"
    cmp "$here/../../../vibe-init/templates/agents/$host/$role.$extension" "$profile"
    cp "$profile" "$repo/snapshots/$host-$role"
  done
done
cp "$repo/AGENTS.md" "$repo/snapshots/AGENTS.md"
bash "$launcher" --root "$repo" >/dev/null
cmp "$repo/AGENTS.md" "$repo/snapshots/AGENTS.md"
for host in codex claude; do
  extension=toml
  [[ "$host" == claude ]] && extension=md
  for role in explorador implementador verificador corretor revisor; do
    cmp "$repo/.$host/agents/$role.$extension" "$repo/snapshots/$host-$role"
  done
done
echo 'PASS launcher-alias: dez perfis e repetição sem alteração'
