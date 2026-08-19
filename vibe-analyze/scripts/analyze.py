#!/usr/bin/env python3
"""Inventaria .vibeflow/phases e promove o wip para phase-N-slug/analyze.md."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


PHASE_RE = re.compile(r"^phase-(\d+)-([a-z0-9]+(?:-[a-z0-9]+)*)$")
CHAIN_FILES = ("interview.md", "spec.md", "plan.md", "analyze.md", "review.md")


# Interpreta somente os parâmetros equivalentes ao contrato público do analyze.ps1.
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inventaria e promove analyze para .vibeflow/phases")
    parser.add_argument("--root")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--dir")
    return parser.parse_args()


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


# Calcula o hash usado para validar a cópia do wip byte a byte.
def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


# Garante que relatório e wip não entrem no Git sem apagar as entradas das outras skills.
def ensure_gitignore(vf: Path) -> None:
    gitignore = vf / ".gitignore"
    add_gitignore_entry(gitignore, "analyze-report.json")
    add_gitignore_entry(gitignore, "analyze-wip.md")


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
        match = PHASE_RE.fullmatch(child.name)
        if not match:
            warnings.append(f"ignorado (nome fora do padrão): {child.name}")
            continue
        files = [name for name in CHAIN_FILES if (child / name).is_file()]
        existing.append(
            {
                "dir": child.name,
                "n": int(match.group(1)),
                "slug": match.group(2),
                "path": ".vibeflow/phases/" + child.name,
                "files": files,
            }
        )
    existing.sort(key=lambda item: item["n"])
    return existing, warnings


# Maior n com spec+plan e sem analyze: o analyze deve reusar esta pasta.
def find_plan_pendente(existing: list[dict[str, Any]]) -> dict[str, Any] | None:
    for item in reversed(existing):
        files = item["files"]
        if "spec.md" in files and "plan.md" in files and "analyze.md" not in files:
            return item
    return None


# Maior n que já tem analyze.md: rascunho ainda atualizável.
def find_rascunho(existing: list[dict[str, Any]]) -> dict[str, Any] | None:
    for item in reversed(existing):
        if "analyze.md" in item["files"]:
            return item
    return None


# Destino preferido: plan pendente, senão rascunho. Sem alvo = não há o que gravar.
def resolve_alvo(
    existing: list[dict[str, Any]],
) -> tuple[dict[str, Any] | None, str]:
    pending = find_plan_pendente(existing)
    if pending:
        return pending, "reuse"
    draft = find_rascunho(existing)
    if draft:
        return draft, "atualizar"
    return None, "criar"


# Cópia binária conferida. Não apaga pasta que já tinha spec ou plan.
def promote_wip(wip: Path, dest_file: Path) -> None:
    existed = dest_file.exists()
    dest_file.write_bytes(wip.read_bytes())
    if dest_file.stat().st_size != wip.stat().st_size or sha256(dest_file) != sha256(wip):
        if not existed:
            dest_file.unlink(missing_ok=True)
        raise RuntimeError("COPY_HASH_MISMATCH: a cópia do wip não bateu com o original.")


# Monta o JSON que a skill lê; stdout só o path do relatório.
def write_report(vf: Path, payload: dict[str, Any]) -> Path:
    report_path = vf / "analyze-report.json"
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print(report_path)
    return report_path


# Inventaria o disco e opcionalmente promove o wip para analyze.md.
def run(args: argparse.Namespace) -> Path:
    repo = repo_root(args.root)
    vf = repo / ".vibeflow"
    phases = vf / "phases"
    wip = vf / "analyze-wip.md"
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
    pending = find_plan_pendente(existing)
    draft = find_rascunho(existing)
    alvo, modo_sugerido = resolve_alvo(existing)
    created: dict[str, Any] | None = None
    modo: str | None = None

    if args.apply:
        if not wip.is_file() or wip.stat().st_size == 0:
            raise RuntimeError("WIP_AUSENTE: falta .vibeflow/analyze-wip.md preenchido.")

        if args.dir:
            dest_dir = phases / Path(args.dir).name
            if not dest_dir.is_dir() or not PHASE_RE.fullmatch(dest_dir.name):
                raise RuntimeError(f"FASE_AUSENTE: .vibeflow/phases/{dest_dir.name} não é uma pasta de fase.")
            modo = "atualizar" if (dest_dir / "analyze.md").is_file() else "reuse"
        elif alvo:
            dest_dir = repo / alvo["path"]
            modo = modo_sugerido
        else:
            raise RuntimeError("ANALYZE_SEM_PLAN: sem plan.md numa fase. Rode /vibe-plan primeiro.")

        if not (dest_dir / "plan.md").is_file():
            raise RuntimeError(f"ANALYZE_SEM_PLAN: {dest_dir.name} não tem plan.md. Rode /vibe-plan primeiro.")
        if not (dest_dir / "spec.md").is_file():
            raise RuntimeError(f"ANALYZE_SEM_SPEC: {dest_dir.name} não tem spec.md. Rode /vibe-spec primeiro.")

        dest_file = dest_dir / "analyze.md"
        rel = f".vibeflow/phases/{dest_dir.name}"
        promote_wip(wip, dest_file)
        wip.unlink()
        actions.append({"op": "promover_wip", "alvo": f"{rel}/analyze.md"})
        existing, extra_warnings = list_phases(phases)
        warnings.extend(extra_warnings)
        next_n = (existing[-1]["n"] + 1) if existing else 1
        pending = find_plan_pendente(existing)
        draft = find_rascunho(existing)
        alvo, modo_sugerido = resolve_alvo(existing)
        created = next((item for item in existing if item["dir"] == dest_dir.name), None)

    payload = {
        "root": str(repo),
        "vibeflow": vf_state,
        "phases": ph_state,
        "next_n": next_n,
        "existing": existing,
        "plan_pendente": pending,
        "rascunho": draft,
        "alvo": alvo,
        "modo_sugerido": modo_sugerido,
        "wip": "presente" if wip.is_file() else "ausente",
        "created": created,
        "modo": modo,
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
