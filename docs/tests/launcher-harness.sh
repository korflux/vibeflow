# Harness compartilhado das suítes test-<nome>.sh.
# Só o contrato do launcher: escolhe motor, repassa flag, recusa o que não existe.
# Cada teste chama ok/bad; a suíte não aborta no primeiro fail.

pass=0
fail=0

# Registra um contrato aprovado sem interromper a suíte.
ok() { pass=$((pass + 1)); printf 'PASS %s\n' "$1"; }

# Registra uma falha com evidência e deixa os demais contratos rodarem.
bad() { fail=$((fail + 1)); printf 'FAIL %s — %s\n' "$1" "$2"; }

# Converte condição observável no resultado padronizado da suíte.
assert() {
  if [ "$1" = 1 ]; then ok "$2"; else bad "$2" "$3"; fi
}

# Pasta descartável por cenário. Windows (Git Bash) vira path nativo via cygpath.
new_sandbox() {
  mktemp -d "${TMPDIR:-/tmp}/vibe-sh.XXXXXX"
}

# --root que o motor Windows entende quando o teste roda no Git Bash.
native_root() {
  if command -v cygpath >/dev/null 2>&1; then
    cygpath -w "$1"
  else
    printf '%s\n' "$1"
  fi
}

# Python 3 do host, só para ler JSON do relatório. Não é o motor sob teste.
host_python() {
  if command -v python3 >/dev/null 2>&1; then
    python3 "$@"
  else
    python "$@"
  fi
}

# Lê um campo de primeiro nível do relatório JSON.
json_field() {
  host_python -c "import json,sys; print(json.load(open(sys.argv[1], encoding='utf-8-sig'))[sys.argv[2]])" "$1" "$2"
}

# Roda o launcher e grava rc/stdout/stderr em variáveis da suíte.
run_sh() {
  last_out=$(mktemp)
  last_err=$(mktemp)
  set +e
  "$@" >"$last_out" 2>"$last_err"
  last_rc=$?
  set -e
}

# Git Bash precisa da pasta do bash.exe no PATH (DLL). Linux não: /usr/bin tem python3.
_is_msys() {
  case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*) return 0 ;;
    *) return 1 ;;
  esac
}

# Roda o launcher com PATH controlado. O primeiro argumento "bash" vira path absoluto.
_run_restricted() {
  path=$1
  shift
  bash_abs=$(command -v bash)
  if [ "${1:-}" = bash ]; then
    shift
    run_sh env PATH="$path" "$bash_abs" "$@"
  else
    run_sh env PATH="$path" "$@"
  fi
}

# PATH sem python3, python nem pwsh: o launcher tem de recusar em vez de degradar.
run_without_motors() {
  empty=$(mktemp -d)
  if _is_msys; then
    _run_restricted "$(dirname "$(command -v bash)")" "$@"
  else
    _run_restricted "$empty" "$@"
  fi
  rm -rf "$empty"
}

# PATH só com pwsh: fallback integral, não versão reduzida.
# Pula (não falha) se pwsh 7+ não existir. 5.1 não é motor gêmeo.
run_pwsh_only() {
  pwsh_bin=$(command -v pwsh 2>/dev/null || true)
  major=""
  _pwsh_major() { "$1" -NoProfile -Command '$PSVersionTable.PSVersion.Major' 2>/dev/null | tr -d '\r'; }
  if [ -n "$pwsh_bin" ]; then
    major=$(_pwsh_major "$pwsh_bin")
  fi
  if [ -z "$pwsh_bin" ] || ! [ "${major:-0}" -ge 7 ] 2>/dev/null; then
    for candidate in \
      "/c/Program Files/PowerShell/7/pwsh.exe" \
      "/mnt/c/Program Files/PowerShell/7/pwsh.exe" \
      /c/Program\ Files/WindowsApps/Microsoft.PowerShell_*/pwsh.exe \
      "/usr/bin/pwsh"
    do
      if [ -x "$candidate" ]; then
        cand_major=$(_pwsh_major "$candidate")
        if [ "${cand_major:-0}" -ge 7 ] 2>/dev/null; then
          pwsh_bin=$candidate
          major=$cand_major
          break
        fi
      fi
    done
  fi
  if [ -z "$pwsh_bin" ] || ! [ "${major:-0}" -ge 7 ] 2>/dev/null; then
    last_rc=127
    last_out=$(mktemp)
    last_err=$(mktemp)
    printf 'pwsh 7+ ausente\n' >"$last_err"
    return 0
  fi
  bindir=$(mktemp -d)
  ln -s "$pwsh_bin" "$bindir/pwsh"
  if [ -f "${pwsh_bin}.exe" ] || [[ "$pwsh_bin" == *.exe ]]; then
    ln -sf "$pwsh_bin" "$bindir/pwsh.exe" 2>/dev/null || true
  fi
  path="$bindir"
  if _is_msys; then
    path="$bindir:$(dirname "$(command -v bash)")"
  fi
  _run_restricted "$path" "$@"
  rm -rf "$bindir"
}

# .vibeflow mínimo, como se o init tivesse rodado sem phases.
seed_vibeflow() {
  mkdir -p "$1/.vibeflow"
  printf 'init-report.json\n' >"$1/.vibeflow/.gitignore"
}

# Encerra com o código da suíte e o placar.
finish() {
  printf '\npass=%s fail=%s\n' "$pass" "$fail"
  if [ "$fail" -gt 0 ]; then exit 1; fi
  exit 0
}
