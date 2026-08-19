#!/usr/bin/env bash
# Contratos do launcher vibe-analyze/scripts/analyze.sh: motor, --apply e --dir.
set -u
set -o pipefail

HERE=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
# shellcheck source=../../tests/launcher-harness.sh
. "$HERE/../../tests/launcher-harness.sh"

LAUNCHER="$HERE/../../../vibe-analyze/scripts/analyze.sh"
set -e

# 1. Sem .vibeflow o motor responde INIT_AUSENTE.
s=$(new_sandbox)
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root"
assert "$( [ "$last_rc" -ne 0 ] && grep -q INIT_AUSENTE "$last_err" && echo 1 || echo 0 )" \
  "1-init-ausente" "rc=$last_rc err=$(cat "$last_err")"
rm -rf "$s"

# 2. --apply reusa a pasta do plan e promove o wip.
s=$(new_sandbox)
seed_vibeflow "$s"
mkdir -p "$s/.vibeflow/phases/phase-1-lock"
printf 's\n' >"$s/.vibeflow/phases/phase-1-lock/spec.md"
printf 'p\n' >"$s/.vibeflow/phases/phase-1-lock/plan.md"
printf '# analyze\n' >"$s/.vibeflow/analyze-wip.md"
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --apply
dest="$s/.vibeflow/phases/phase-1-lock/analyze.md"
assert "$( [ "$last_rc" -eq 0 ] && [ -f "$dest" ] && [ ! -f "$s/.vibeflow/analyze-wip.md" ] && echo 1 || echo 0 )" \
  "2-apply-reuse" "rc=$last_rc dest=$dest err=$(cat "$last_err")"
rm -rf "$s"

# 3. --dir sem plan devolve ANALYZE_SEM_PLAN: a flag chegou.
s=$(new_sandbox)
seed_vibeflow "$s"
mkdir -p "$s/.vibeflow/phases/phase-1-so-spec"
printf 's\n' >"$s/.vibeflow/phases/phase-1-so-spec/spec.md"
printf 'x\n' >"$s/.vibeflow/analyze-wip.md"
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --apply --dir phase-1-so-spec
assert "$( [ "$last_rc" -ne 0 ] && grep -q ANALYZE_SEM_PLAN "$last_err" && [ ! -f "$s/.vibeflow/phases/phase-1-so-spec/analyze.md" ] && echo 1 || echo 0 )" \
  "3-dir-sem-plan" "rc=$last_rc err=$(cat "$last_err")"
rm -rf "$s"

# 4. Flag desconhecida para no launcher.
s=$(new_sandbox)
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --force
assert "$( [ "$last_rc" -eq 2 ] && grep -q 'uso: analyze.sh' "$last_err" && echo 1 || echo 0 )" \
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
