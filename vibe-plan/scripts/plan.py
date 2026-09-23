#!/usr/bin/env python3
"""Inventaria .vibeflow/phases e prepara phase-N-slug/plan.md."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any


PHASE_RE = re.compile(r"^phase-(\d+)-([a-z0-9]+(?:-[a-z0-9]+)*)$")
CHAIN_FILES = ("interview.md", "spec.md", "plan.md", "analyze.md", "implement.md", "review.md")
REPARSE_POINT = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


# Detecta symlinks, junctions e outros reparse points sem seguir o alvo do caminho.
def is_reparse_point(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
    except FileNotFoundError:
        return False
    return bool(attributes & REPARSE_POINT)


# Interpreta somente os parâmetros equivalentes ao contrato público do plan.ps1.
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inventaria e prepara plan para .vibeflow/phases")
    parser.add_argument("--root")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--dir")
    parser.add_argument("--mvp", action="store_true")
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


# Classifica .vibeflow antes de qualquer escrita.
def vibeflow_state(path: Path) -> str:
    if is_reparse_point(path):
        return "inesperado"
    if not path.exists():
        return "ausente"
    if not path.is_dir():
        return "inesperado"
    return "ok"


# Classifica phases/ sem interpretar o conteúdo das fases.
def phases_state(path: Path) -> str:
    if is_reparse_point(path):
        return "inesperado"
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
        if is_reparse_point(child):
            warnings.append(f"ignorado (link/reparse point): {child.name}")
            continue
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
                "kind": "phase",
                "dir": child.name,
                "n": int(match.group(1)),
                "slug": match.group(2),
                "path": ".vibeflow/phases/" + child.name,
                "files": files,
            }
        )
    existing.sort(key=lambda item: item["n"])
    return existing, warnings


# Representa o alvo MVP sem inferir a rota a partir dos artefatos existentes.
def get_mvp(vf: Path) -> dict[str, Any] | None:
    mvp = vf / "mvp"
    if is_reparse_point(mvp):
        raise RuntimeError("MVP_INESPERADO: .vibeflow/mvp não pode ser symlink, junction ou reparse point.")
    if not mvp.exists():
        return None
    if not mvp.is_dir():
        raise RuntimeError("MVP_INESPERADO: .vibeflow/mvp existe, mas não é um diretório.")
    return {
        "kind": "mvp",
        "dir": "mvp",
        "path": ".vibeflow/mvp",
        "files": [name for name in CHAIN_FILES if (mvp / name).is_file()],
    }


# Maior n com spec e sem plan: o plan deve reusar esta pasta.
def find_spec_pendente(existing: list[dict[str, Any]]) -> dict[str, Any] | None:
    for item in reversed(existing):
        if "spec.md" in item["files"] and "plan.md" not in item["files"]:
            return item
    return None


# Maior n com plan e sem analyze: rascunho ainda atualizável.
def find_rascunho(existing: list[dict[str, Any]]) -> dict[str, Any] | None:
    for item in reversed(existing):
        if "plan.md" in item["files"] and "analyze.md" not in item["files"]:
            return item
    return None


# Destino preferido: spec pendente, senão rascunho. Sem alvo = não há o que gravar.
def resolve_alvo(
    existing: list[dict[str, Any]],
) -> tuple[dict[str, Any] | None, str]:
    pending = find_spec_pendente(existing)
    if pending:
        return pending, "reuse"
    draft = find_rascunho(existing)
    if draft:
        return draft, "atualizar"
    return None, "criar"


# Cria o arquivo vivo vazio sem substituir conteúdo já escrito pela IA.
def prepare_live_file(dest_file: Path) -> bool:
    if dest_file.is_symlink() or dest_file.exists():
        if dest_file.is_symlink() or not dest_file.is_file():
            raise RuntimeError(f"ARTEFATO_INESPERADO: {dest_file.name} não é um arquivo vivo.")
        return False
    try:
        with dest_file.open("xb"):
            pass
    except FileExistsError:
        if dest_file.is_file() and not dest_file.is_symlink():
            return False
        raise RuntimeError(f"ARTEFATO_INESPERADO: {dest_file.name} não é um arquivo vivo.")
    return True


# Serializa o inventário como JSON transitório para o consumidor imediato, sem criar estado no workspace.
def emit_report(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


# Inventaria o disco e prepara o arquivo vivo no apply.
def run(args: argparse.Namespace) -> None:
    if args.mvp and args.dir is not None:
        raise RuntimeError("MODO_INVALIDO: o alvo MVP não aceita --dir.")

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

    existing, warnings = list_phases(phases)
    next_n = (existing[-1]["n"] + 1) if existing else 1
    pending = find_spec_pendente(existing)
    draft = find_rascunho(existing)
    alvo, modo_sugerido = resolve_alvo(existing)
    mvp = get_mvp(vf)
    if args.mvp and (mvp is None or "spec.md" not in mvp["files"]):
        raise RuntimeError("PLAN_SEM_SPEC: falta .vibeflow/mvp/spec.md. Rode /vibe-spec primeiro.")
    created: dict[str, Any] | None = None
    modo: str | None = None

    if args.apply:
        if args.mvp:
            dest_dir = vf / "mvp"
            modo = "atualizar" if (dest_dir / "plan.md").is_file() else "reuse"
        elif args.dir:
            dest_dir = phases / Path(args.dir).name
            if is_reparse_point(dest_dir) or not dest_dir.is_dir() or not PHASE_RE.fullmatch(dest_dir.name):
                raise RuntimeError(f"FASE_AUSENTE: .vibeflow/phases/{dest_dir.name} não é uma pasta de fase.")
            modo = "atualizar" if (dest_dir / "plan.md").is_file() else "reuse"
        elif alvo:
            dest_dir = repo / alvo["path"]
            modo = modo_sugerido
        else:
            raise RuntimeError("PLAN_SEM_SPEC: sem spec.md numa fase. Rode /vibe-spec primeiro.")

        if not (dest_dir / "spec.md").is_file():
            raise RuntimeError(f"PLAN_SEM_SPEC: {dest_dir.name} não tem spec.md. Rode /vibe-spec primeiro.")
        if (dest_dir / "analyze.md").is_file():
            raise RuntimeError(
                f"PLAN_JA_ANALISADO: {dest_dir.name} já tem analyze.md. Não pise. Pedido novo = outra phase."
            )

        dest_file = dest_dir / "plan.md"
        rel = ".vibeflow/mvp" if args.mvp else f".vibeflow/phases/{dest_dir.name}"
        file_created = prepare_live_file(dest_file)
        if file_created:
            actions.append({"op": "criar_arquivo", "alvo": f"{rel}/plan.md"})
        if args.mvp:
            mvp = get_mvp(vf)
            created = mvp
        else:
            existing, extra_warnings = list_phases(phases)
            warnings.extend(extra_warnings)
            next_n = (existing[-1]["n"] + 1) if existing else 1
            pending = find_spec_pendente(existing)
            draft = find_rascunho(existing)
            alvo, modo_sugerido = resolve_alvo(existing)
            created = next((item for item in existing if item["dir"] == dest_dir.name), None)

    payload = {
        "root": str(repo),
        "rota": "mvp" if args.mvp else "phase",
        "vibeflow": vf_state,
        "phases": ph_state,
        "next_n": next_n,
        "existing": existing,
        "spec_pendente": pending,
        "rascunho": draft,
        "alvo": mvp if args.mvp else alvo,
        "mvp": mvp,
        "modo_sugerido": "atualizar" if args.mvp and "plan.md" in mvp["files"] else ("reuse" if args.mvp else modo_sugerido),
        "created": created,
        "modo": modo,
        "actions": actions,
        "avisos": warnings,
    }
    emit_report(payload)


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
