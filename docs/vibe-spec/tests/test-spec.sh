#!/usr/bin/env bash
# Contratos do launcher vibe-spec/scripts/spec.sh: motor, --apply, --slug e --dir.
set -u
set -o pipefail

HERE=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
# shellcheck source=../../tests/launcher-harness.sh
. "$HERE/../../tests/launcher-harness.sh"

LAUNCHER="$HERE/../../../vibe-spec/scripts/spec.sh"
set -e

# 1. Sem .vibeflow o motor responde INIT_AUSENTE.
s=$(new_sandbox)
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root"
assert "$( [ "$last_rc" -ne 0 ] && grep -q INIT_AUSENTE "$last_err" && echo 1 || echo 0 )" \
  "1-init-ausente" "rc=$last_rc err=$(cat "$last_err")"
rm -rf "$s"

# 2. --apply --slug criam a fase e promovem o wip.
s=$(new_sandbox)
seed_vibeflow "$s"
printf '# spec\n' >"$s/.vibeflow/spec-wip.md"
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --apply --slug "Dashboard!!"
dest="$s/.vibeflow/phases/phase-1-dashboard/spec.md"
assert "$( [ "$last_rc" -eq 0 ] && [ -f "$dest" ] && echo 1 || echo 0 )" \
  "2-apply-slug" "rc=$last_rc dest=$dest err=$(cat "$last_err")"
rm -rf "$s"

# 3. --dir reusa a pasta da interview e não abre phase-2.
s=$(new_sandbox)
seed_vibeflow "$s"
mkdir -p "$s/.vibeflow/phases/phase-1-lock"
printf 'i\n' >"$s/.vibeflow/phases/phase-1-lock/interview.md"
printf '# spec\n' >"$s/.vibeflow/spec-wip.md"
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --apply --dir phase-1-lock
dest="$s/.vibeflow/phases/phase-1-lock/spec.md"
assert "$( [ "$last_rc" -eq 0 ] && [ -f "$dest" ] && [ ! -d "$s/.vibeflow/phases/phase-2-lock" ] && echo 1 || echo 0 )" \
  "3-apply-dir" "rc=$last_rc dest=$dest err=$(cat "$last_err")"
rm -rf "$s"

# 4. Flag desconhecida para no launcher.
s=$(new_sandbox)
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --force
assert "$( [ "$last_rc" -eq 2 ] && grep -q 'uso: spec.sh' "$last_err" && echo 1 || echo 0 )" \
  "4-flag-desconhecida" "rc=$last_rc err=$(cat "$last_err")"
rm -rf "$s"

# 5. Sem motor: recusa explícita.
s=$(new_sandbox)
root=$(native_root "$s")
run_without_motors bash "$LAUNCHER" --root "$root"
assert "$( [ "$last_rc" -eq 1 ] && grep -q 'precisa de Python 3 ou PowerShell' "$last_err" && echo 1 || echo 0 )" \
  "5-sem-motor" "rc=$last_rc err=$(cat "$last_err")"
rm -rf "$s"

finish
