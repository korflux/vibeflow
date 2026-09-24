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
if [ "$last_rc" -eq 0 ]; then alvo=$(json_field_output alvo.dir); fi
assert "$( [ "$last_rc" -eq 0 ] && [ "$alvo" = phase-1-so-spec ] && [ ! -e "$s/.vibeflow/implement-report.json" ] && echo 1 || echo 0 )" \
  "2-dir-sem-plan" "rc=$last_rc alvo=$alvo err=$(cat "$last_err")"
rm -rf "$s"

# 3. --apply reaproveita o plan sem criar implement.md.
s=$(new_sandbox)
seed_vibeflow "$s"
mkdir -p "$s/.vibeflow/phases/phase-1-a"
printf 'p\n' >"$s/.vibeflow/phases/phase-1-a/plan.md"
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --apply
dest="$s/.vibeflow/phases/phase-1-a/implement.md"
assert "$( [ "$last_rc" -eq 0 ] && [ ! -e "$dest" ] && echo 1 || echo 0 )" \
  "3-apply-sem-implement" "rc=$last_rc dest=$dest err=$(cat "$last_err")"
rm -rf "$s"

# 4. Reexecução preserva byte a byte o implement histórico.
s=$(new_sandbox)
seed_vibeflow "$s"
mkdir -p "$s/.vibeflow/phases/phase-1-a"
printf 'p\n' >"$s/.vibeflow/phases/phase-1-a/plan.md"
printf '# historico\n' >"$s/.vibeflow/phases/phase-1-a/implement.md"
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --apply
dest="$s/.vibeflow/phases/phase-1-a/implement.md"
assert "$( [ "$last_rc" -eq 0 ] && [ "$(cat "$dest")" = '# historico' ] && echo 1 || echo 0 )" \
  "4-preserva-vivo" "rc=$last_rc dest=$dest err=$(cat "$last_err")"
rm -rf "$s"

# 5. --apply --slug cria apenas a pasta de destino.
s=$(new_sandbox)
seed_vibeflow "$s"
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --apply --slug hotfix-cor
dest="$s/.vibeflow/phases/phase-1-hotfix-cor"
assert "$( [ "$last_rc" -eq 0 ] && [ -d "$dest" ] && [ ! -e "$dest/implement.md" ] && echo 1 || echo 0 )" \
  "5-apply-slug" "rc=$last_rc dest=$dest err=$(cat "$last_err")"
rm -rf "$s"

# 6. --mvp respeita analyze aprovado sem criar implement.md.
s=$(new_sandbox)
seed_vibeflow "$s"
mkdir -p "$s/.vibeflow/mvp"
printf '### T1: fixture\n\n- [ ] T1 concluída\n- **Deps:** nenhuma\n' >"$s/.vibeflow/mvp/plan.md"
printf '# Analyze\n# Status: aprovado\n\n## Veredito\n\nlimpo\n' >"$s/.vibeflow/mvp/analyze.md"
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --apply --mvp
dest="$s/.vibeflow/mvp/implement.md"
assert "$( [ "$last_rc" -eq 0 ] && [ ! -e "$dest" ] && echo 1 || echo 0 )" \
  "6-apply-mvp-sem-implement" "rc=$last_rc dest=$dest err=$(cat "$last_err")"
rm -rf "$s"

# 7. Sem motor: recusa explícita.
s=$(new_sandbox)
root=$(native_root "$s")
run_without_motors bash "$LAUNCHER" --root "$root"
assert "$( [ "$last_rc" -eq 1 ] && grep -q 'precisa de Python 3 ou PowerShell' "$last_err" && echo 1 || echo 0 )" \
  "7-sem-motor" "rc=$last_rc err=$(cat "$last_err")"
rm -rf "$s"

# 8. Flag desconhecida para no launcher.
s=$(new_sandbox)
root=$(native_root "$s")
run_sh bash "$LAUNCHER" --root "$root" --force
assert "$( [ "$last_rc" -eq 2 ] && grep -q 'uso: implement.sh' "$last_err" && echo 1 || echo 0 )" \
  "8-flag-desconhecida" "rc=$last_rc err=$(cat "$last_err")"
rm -rf "$s"

finish
