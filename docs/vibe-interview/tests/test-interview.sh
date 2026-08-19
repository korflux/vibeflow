#!/usr/bin/env bash
# Contratos do launcher vibe-interview/scripts/interview.sh: motor e --apply/--slug.
set -u
set -o pipefail

HERE=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
# shellcheck source=../../tests/launcher-harness.sh
. "$HERE/../../tests/launcher-harness.sh"

LAUNCHER="$HERE/../../../vibe-interview/scripts/interview.sh"
set -e

# 1. Sem .vibeflow o motor responde INIT_AUSENTE: o launcher não engole o erro.
s=$(new_sandbox)
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root"
assert "$( [ "$last_rc" -ne 0 ] && grep -q INIT_AUSENTE "$last_err" && echo 1 || echo 0 )" \
  "1-init-ausente" "rc=$last_rc err=$(cat "$last_err")"
rm -rf "$s"

# 2. --root inventaria: next_n=1 depois do seed.
s=$(new_sandbox)
seed_vibeflow "$s"
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root"
next=""
[ -f "$s/.vibeflow/interview-report.json" ] && next=$(json_field "$s/.vibeflow/interview-report.json" next_n)
assert "$( [ "$last_rc" -eq 0 ] && [ "$next" = 1 ] && echo 1 || echo 0 )" \
  "2-root-inventario" "rc=$last_rc next=$next err=$(cat "$last_err")"
rm -rf "$s"

# 3. --apply --slug chegam no motor e promovem o wip.
s=$(new_sandbox)
seed_vibeflow "$s"
printf '# trilha\n' >"$s/.vibeflow/interview-wip.md"
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --apply --slug "Dashboard Standup!!"
dest="$s/.vibeflow/phases/phase-1-dashboard-standup/interview.md"
assert "$( [ "$last_rc" -eq 0 ] && [ -f "$dest" ] && [ ! -f "$s/.vibeflow/interview-wip.md" ] && echo 1 || echo 0 )" \
  "3-apply-slug" "rc=$last_rc dest=$dest err=$(cat "$last_err")"
rm -rf "$s"

# 4. Flag desconhecida para no launcher (exit 2), sem inventar motor.
s=$(new_sandbox)
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --force
assert "$( [ "$last_rc" -eq 2 ] && grep -q 'uso: interview.sh' "$last_err" && echo 1 || echo 0 )" \
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
