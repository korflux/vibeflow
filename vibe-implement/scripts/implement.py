#!/usr/bin/env python3
"""Inventaria .vibeflow/phases e aponta a fase a implementar. Não promove wip."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


PHASE_RE = re.compile(r"^phase-(\d+)-([a-z0-9]+(?:-[a-z0-9]+)*)$")
CHAIN_FILES = ("interview.md", "spec.md", "plan.md", "analyze.md", "review.md")


# Interpreta somente as flags públicas do implement.ps1. Qualquer outra é erro.
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inventaria a fase para vibe-implement")
    parser.add_argument("--root")
    parser.add_argument("--dir")
    args, unknown = parser.parse_known_args()
    if unknown:
        joined = " ".join(unknown)
        raise RuntimeError(f"FLAG_DESCONHECIDA: {joined} não existe nesta skill.")
    return args


# Resolve a raiz por parâmetro, Git ou cwd, sem tornar o Git uma dependência obrigatória.
def repo_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).resolve(strict=True)
    if shutil.which("git"):
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip()).resolve()
    return Path.cwd().resolve()


# Lê texto operacional que precisa ser preservado integralmente.
def read_text(path: Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8-sig")


# Acrescenta exclusões operacionais preservando regras existentes e evitando duplicação.
def add_gitignore_entry(path: Path, entry: str) -> None:
    body = read_text(path) or ""
    if entry in {line.strip() for line in body.splitlines()}:
        return
    prefix = "\n" if body and not body.endswith("\n") else ""
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(f"{prefix}{entry}\n")


# Garante que o relatório não entre no Git sem apagar as entradas das outras skills.
def ensure_gitignore(vf: Path) -> None:
    add_gitignore_entry(vf / ".gitignore", "implement-report.json")


# Classifica .vibeflow antes de qualquer escrita.
def vibeflow_state(path: Path) -> str:
    if not path.exists():
        return "ausente"
    if not path.is_dir():
        return "inesperado"
    return "ok"


# Classifica phases/ sem interpretar o conteúdo das fases.
def phases_state(path: Path) -> str:
    if not path.exists():
        return "ausente"
    if not path.is_dir():
        return "inesperado"
    return "ok"


# Monta o objeto de fase a partir de uma pasta que já bateu o padrão.
def phase_item(child: Path) -> dict[str, Any]:
    match = PHASE_RE.fullmatch(child.name)
    assert match is not None
    files = [name for name in CHAIN_FILES if (child / name).is_file()]
    return {
        "dir": child.name,
        "n": int(match.group(1)),
        "slug": match.group(2),
        "path": ".vibeflow/phases/" + child.name,
        "files": files,
    }


# Lista pastas que batem o padrão phase-N-slug e ignora o restante.
def list_phases(phases: Path) -> tuple[list[dict[str, Any]], list[str]]:
    existing: list[dict[str, Any]] = []
    warnings: list[str] = []
    if not phases.is_dir():
        return existing, warnings
    for child in phases.iterdir():
        if not child.is_dir():
            if child.name != ".gitkeep":
                warnings.append(f"ignorado (não é pasta de fase): {child.name}")
            continue
        if not PHASE_RE.fullmatch(child.name):
            warnings.append(f"ignorado (nome fora do padrão): {child.name}")
            continue
        existing.append(phase_item(child))
    existing.sort(key=lambda item: item["n"])
    return existing, warnings


# Maior n que já tem plan.md: é a fila desta skill sem --dir.
def find_alvo_com_plan(existing: list[dict[str, Any]]) -> dict[str, Any] | None:
    for item in reversed(existing):
        if "plan.md" in item["files"]:
            return item
    return None


# Destino: --dir se veio; senão maior n com plan. Sem alvo = não há fila no disco.
def resolve_alvo(
    existing: list[dict[str, Any]],
    dir_arg: str | None,
    phases: Path,
) -> tuple[dict[str, Any] | None, str]:
    if dir_arg:
        dest = phases / Path(dir_arg).name
        if not dest.is_dir() or not PHASE_RE.fullmatch(dest.name):
            raise RuntimeError(
                f"FASE_AUSENTE: .vibeflow/phases/{dest.name} não é uma pasta de fase."
            )
        found = next((item for item in existing if item["dir"] == dest.name), None)
        return (found if found is not None else phase_item(dest)), "reuse"
    found = find_alvo_com_plan(existing)
    if found:
        return found, "reuse"
    return None, "criar"


# Monta o JSON que a skill lê; stdout só o path do relatório.
def write_report(vf: Path, payload: dict[str, Any]) -> Path:
    report_path = vf / "implement-report.json"
    report_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    print(report_path)
    return report_path


# Inventaria o disco. Não escreve plan/spec e não promove wip.
def run(args: argparse.Namespace) -> Path:
    repo = repo_root(args.root)
    vf = repo / ".vibeflow"
    phases = vf / "phases"
    actions: list[dict[str, str]] = []

    vf_state = vibeflow_state(vf)
    if vf_state == "ausente":
        raise RuntimeError("INIT_AUSENTE: não existe .vibeflow/. Rode /vibe-init antes.")
    if vf_state == "inesperado":
        raise RuntimeError("INIT_AUSENTE: .vibeflow existe, mas não é um diretório.")

    ph_state = phases_state(phases)
    if ph_state == "inesperado":
        raise RuntimeError("PHASES_INESPERADO: .vibeflow/phases existe, mas não é um diretório.")
    if ph_state == "ausente":
        phases.mkdir(parents=True)
        (phases / ".gitkeep").write_text("", encoding="utf-8")
        actions.append({"op": "criar_phases", "alvo": ".vibeflow/phases"})
        ph_state = "ok"

    ensure_gitignore(vf)
    existing, warnings = list_phases(phases)
    next_n = (existing[-1]["n"] + 1) if existing else 1
    alvo, modo_sugerido = resolve_alvo(existing, args.dir, phases)

    payload = {
        "root": str(repo),
        "vibeflow": vf_state,
        "phases": ph_state,
        "next_n": next_n,
        "existing": existing,
        "plan_pendente": None,
        "rascunho": None,
        "alvo": alvo,
        "modo_sugerido": modo_sugerido,
        "wip": "ausente",
        "created": None,
        "modo": None,
        "actions": actions,
        "avisos": warnings,
    }
    return write_report(vf, payload)


# Converte falhas previstas em mensagens curtas, sem stack trace operacional.
def main() -> int:
    try:
        run(parse_args())
        return 0
    except (OSError, RuntimeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
