#!/usr/bin/env bash
# Contratos do launcher vibe-interview/scripts/interview.sh: motor e alvos phase/MVP.
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
if [ "$last_rc" -eq 0 ]; then next=$(json_field_output next_n); fi
assert "$( [ "$last_rc" -eq 0 ] && [ "$next" = 1 ] && [ ! -e "$s/.vibeflow/interview-report.json" ] && echo 1 || echo 0 )" \
  "2-root-inventario" "rc=$last_rc next=$next err=$(cat "$last_err")"
rm -rf "$s"

# 3. --apply --slug chega no motor e prepara o arquivo vivo.
s=$(new_sandbox)
seed_vibeflow "$s"
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --apply --slug "Dashboard Standup!!"
dest="$s/.vibeflow/phases/phase-1-dashboard-standup/interview.md"
assert "$( [ "$last_rc" -eq 0 ] && [ -f "$dest" ] && [ ! -s "$dest" ] && echo 1 || echo 0 )" \
  "3-apply-slug" "rc=$last_rc dest=$dest err=$(cat "$last_err")"
rm -rf "$s"

# 4. Flag desconhecida para no launcher (exit 2), sem inventar motor.
s=$(new_sandbox)
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --force
assert "$( [ "$last_rc" -eq 2 ] && grep -q 'uso: interview.sh' "$last_err" && echo 1 || echo 0 )" \
  "4-flag-desconhecida" "rc=$last_rc err=$(cat "$last_err")"
rm -rf "$s"

# 5. --mvp chega no motor e não cria phase-N.
s=$(new_sandbox)
seed_vibeflow "$s"
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --apply --mvp
dest="$s/.vibeflow/mvp/interview.md"
phase_count=$(find "$s/.vibeflow/phases" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
assert "$( [ "$last_rc" -eq 0 ] && [ -f "$dest" ] && [ ! -s "$dest" ] && [ "$phase_count" = 0 ] && echo 1 || echo 0 )" \
  "5-apply-mvp" "rc=$last_rc phases=$phase_count dest=$dest err=$(cat "$last_err")"
rm -rf "$s"

# 6. Sem motor: recusa explícita.
s=$(new_sandbox)
root=$(native_root "$s")
run_without_motors bash "$LAUNCHER" --root "$root"
assert "$( [ "$last_rc" -eq 1 ] && grep -q 'precisa de Python 3 ou PowerShell' "$last_err" && echo 1 || echo 0 )" \
  "6-sem-motor" "rc=$last_rc err=$(cat "$last_err")"
rm -rf "$s"

finish
