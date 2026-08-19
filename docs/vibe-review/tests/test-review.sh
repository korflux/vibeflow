#!/usr/bin/env bash
# Contratos do launcher vibe-review/scripts/review.sh: motor, --apply, --slug e --dir.
set -u
set -o pipefail

HERE=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
# shellcheck source=../../tests/launcher-harness.sh
. "$HERE/../../tests/launcher-harness.sh"

LAUNCHER="$HERE/../../../vibe-review/scripts/review.sh"
set -e

# 1. Sem .vibeflow o motor responde INIT_AUSENTE.
s=$(new_sandbox)
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root"
assert "$( [ "$last_rc" -ne 0 ] && grep -q INIT_AUSENTE "$last_err" && echo 1 || echo 0 )" \
  "1-init-ausente" "rc=$last_rc err=$(cat "$last_err")"
rm -rf "$s"

# 2. --apply --slug criam review avulsa.
s=$(new_sandbox)
seed_vibeflow "$s"
printf '# avulsa\n' >"$s/.vibeflow/review-wip.md"
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --apply --slug diff-local
dest="$s/.vibeflow/phases/phase-1-diff-local/review.md"
assert "$( [ "$last_rc" -eq 0 ] && [ -f "$dest" ] && echo 1 || echo 0 )" \
  "2-apply-slug" "rc=$last_rc dest=$dest err=$(cat "$last_err")"
rm -rf "$s"

# 3. --dir reusa pasta existente mesmo sem plan.
s=$(new_sandbox)
seed_vibeflow "$s"
mkdir -p "$s/.vibeflow/phases/phase-1-so-spec"
printf 's\n' >"$s/.vibeflow/phases/phase-1-so-spec/spec.md"
printf '# dir\n' >"$s/.vibeflow/review-wip.md"
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --apply --dir phase-1-so-spec
dest="$s/.vibeflow/phases/phase-1-so-spec/review.md"
assert "$( [ "$last_rc" -eq 0 ] && [ -f "$dest" ] && echo 1 || echo 0 )" \
  "3-apply-dir" "rc=$last_rc dest=$dest err=$(cat "$last_err")"
rm -rf "$s"

# 4. Flag desconhecida para no launcher.
s=$(new_sandbox)
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --force
assert "$( [ "$last_rc" -eq 2 ] && grep -q 'uso: review.sh' "$last_err" && echo 1 || echo 0 )" \
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
