#!/usr/bin/env bash
# Contratos do launcher vibe-implement/scripts/implement.sh: motor, --dir, --apply e --slug.
set -u
set -o pipefail

HERE=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
# shellcheck source=../../tests/launcher-harness.sh
. "$HERE/../../tests/launcher-harness.sh"

LAUNCHER="$HERE/../../../vibe-implement/scripts/implement.sh"
set -e

# 1. Sem .vibeflow o motor responde INIT_AUSENTE.
s=$(new_sandbox)
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root"
assert "$( [ "$last_rc" -ne 0 ] && grep -q INIT_AUSENTE "$last_err" && echo 1 || echo 0 )" \
  "1-init-ausente" "rc=$last_rc err=$(cat "$last_err")"
rm -rf "$s"

# 2. --root inventaria e --dir escolhe a pasta sem plan (rota low).
s=$(new_sandbox)
seed_vibeflow "$s"
mkdir -p "$s/.vibeflow/phases/phase-1-so-spec"
printf 's\n' >"$s/.vibeflow/phases/phase-1-so-spec/spec.md"
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --dir phase-1-so-spec
alvo=""
if [ -f "$s/.vibeflow/implement-report.json" ]; then
  alvo=$(host_python -c "import json,sys; print(json.load(open(sys.argv[1], encoding='utf-8-sig'))['alvo']['dir'])" "$s/.vibeflow/implement-report.json")
fi
assert "$( [ "$last_rc" -eq 0 ] && [ "$alvo" = phase-1-so-spec ] && echo 1 || echo 0 )" \
  "2-dir-sem-plan" "rc=$last_rc alvo=$alvo err=$(cat "$last_err")"
rm -rf "$s"

# 3. --apply sem wip devolve WIP_AUSENTE: a flag chegou no motor.
s=$(new_sandbox)
seed_vibeflow "$s"
mkdir -p "$s/.vibeflow/phases/phase-1-a"
printf 'p\n' >"$s/.vibeflow/phases/phase-1-a/plan.md"
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --apply
assert "$( [ "$last_rc" -ne 0 ] && grep -q WIP_AUSENTE "$last_err" && echo 1 || echo 0 )" \
  "3-apply-sem-wip" "rc=$last_rc err=$(cat "$last_err")"
rm -rf "$s"

# 4. --apply --slug criam implement avulsa.
s=$(new_sandbox)
seed_vibeflow "$s"
printf '# avulsa\n' >"$s/.vibeflow/implement-wip.md"
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --apply --slug hotfix-cor
dest="$s/.vibeflow/phases/phase-1-hotfix-cor/implement.md"
assert "$( [ "$last_rc" -eq 0 ] && [ -f "$dest" ] && echo 1 || echo 0 )" \
  "4-apply-slug" "rc=$last_rc dest=$dest err=$(cat "$last_err")"
rm -rf "$s"

# 5. --mvp respeita analyze aprovado e promove no alvo especial.
s=$(new_sandbox)
seed_vibeflow "$s"
mkdir -p "$s/.vibeflow/mvp"
printf '### T1: fixture\n\n- [ ] T1 concluída\n- **Deps:** nenhuma\n' >"$s/.vibeflow/mvp/plan.md"
printf '# Analyze\n# Status: aprovado\n\n## Veredito\n\nlimpo\n' >"$s/.vibeflow/mvp/analyze.md"
printf '# MVP\n' >"$s/.vibeflow/implement-wip.md"
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --apply --mvp
dest="$s/.vibeflow/mvp/implement.md"
assert "$( [ "$last_rc" -eq 0 ] && [ -f "$dest" ] && echo 1 || echo 0 )" \
  "5-apply-mvp" "rc=$last_rc dest=$dest err=$(cat "$last_err")"
rm -rf "$s"

# 6. Sem motor: recusa explícita.
s=$(new_sandbox)
root=$(native_root "$s")
run_without_motors bash "$LAUNCHER" --root "$root"
assert "$( [ "$last_rc" -eq 1 ] && grep -q 'precisa de Python 3 ou PowerShell' "$last_err" && echo 1 || echo 0 )" \
  "6-sem-motor" "rc=$last_rc err=$(cat "$last_err")"
rm -rf "$s"

# 7. Flag desconhecida para no launcher.
s=$(new_sandbox)
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --force
assert "$( [ "$last_rc" -eq 2 ] && grep -q 'uso: implement.sh' "$last_err" && echo 1 || echo 0 )" \
  "7-flag-desconhecida" "rc=$last_rc err=$(cat "$last_err")"
rm -rf "$s"

finish
