#!/usr/bin/env bash
# Contratos do launcher vibe-init/scripts/init.sh: motor, --root e flags próprias.
set -u
set -o pipefail

HERE=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
# shellcheck source=../../tests/launcher-harness.sh
. "$HERE/../../tests/launcher-harness.sh"

LAUNCHER="$HERE/../../../vibe-init/scripts/init.sh"
set -e

# 1. --root chega no motor: repo vazio produz relatório e flow=novo.
s=$(new_sandbox)
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root"
flow=""
if [ -f "$s/.vibeflow/init-report.json" ]; then
  flow=$(json_field "$s/.vibeflow/init-report.json" flow)
fi
assert "$( [ "$last_rc" -eq 0 ] && [ "$flow" = novo ] && echo 1 || echo 0 )" \
  "1-root-inventario" "rc=$last_rc flow=$flow err=$(cat "$last_err")"
rm -rf "$s"

# 2. --stop-after-old é repassado: backup existe e o legado ainda não virou symlink.
s=$(new_sandbox)
printf 'regra critica\n' >"$s/AGENTS.md"
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --stop-after-old
still_file=0
[ -f "$s/AGENTS.md" ] && [ ! -L "$s/AGENTS.md" ] && still_file=1
has_old=0
[ -f "$s/.vibeflow/old/AGENTS.md" ] && has_old=1
assert "$( [ "$last_rc" -eq 0 ] && [ "$still_file" -eq 1 ] && [ "$has_old" -eq 1 ] && echo 1 || echo 0 )" \
  "2-stop-after-old" "rc=$last_rc file=$still_file old=$has_old err=$(cat "$last_err")"
rm -rf "$s"

# 3. Flag que o launcher não conhece para com uso, sem chamar o motor.
s=$(new_sandbox)
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --force
assert "$( [ "$last_rc" -eq 2 ] && grep -q 'uso: init.sh' "$last_err" && echo 1 || echo 0 )" \
  "3-flag-desconhecida" "rc=$last_rc err=$(cat "$last_err")"
rm -rf "$s"

# 4. Sem Python 3 e sem pwsh: recusa explícita, sem motor degradado.
s=$(new_sandbox)
root=$(native_root "$s")
run_without_motors bash "$LAUNCHER" --root "$root"
assert "$( [ "$last_rc" -eq 1 ] && grep -q 'precisa de Python 3 ou PowerShell' "$last_err" && echo 1 || echo 0 )" \
  "4-sem-motor" "rc=$last_rc err=$(cat "$last_err")"
rm -rf "$s"

# 5. Só pwsh no PATH: fallback integral ainda grava o relatório.
s=$(new_sandbox)
root=$(native_root "$s")
run_pwsh_only bash "$LAUNCHER" --root "$root"
if [ "$last_rc" -eq 127 ] && grep -q 'pwsh 7+ ausente' "$last_err"; then
  ok "5-so-pwsh (skip: pwsh 7+ ausente)"
else
  flow=""
  [ -f "$s/.vibeflow/init-report.json" ] && flow=$(json_field "$s/.vibeflow/init-report.json" flow)
  assert "$( [ "$last_rc" -eq 0 ] && [ "$flow" = novo ] && echo 1 || echo 0 )" \
    "5-so-pwsh" "rc=$last_rc flow=$flow err=$(cat "$last_err")"
fi
rm -rf "$s"

finish
