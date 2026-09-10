#!/usr/bin/env python3
"""Inventaria o interview e prepara um alvo phase ou MVP explícito."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import stat
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Any


PHASE_RE = re.compile(r"^phase-(\d+)-([a-z0-9]+(?:-[a-z0-9]+)*)$")
CHAIN_FILES = ("interview.md", "spec.md", "plan.md", "analyze.md", "implement.md", "review.md")
MAX_SLUG = 48
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


# Interpreta somente os parâmetros equivalentes ao contrato público do interview.ps1.
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inventaria e prepara interview para um alvo phase ou MVP")
    parser.add_argument("--root")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--slug")
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


# Lê texto operacional que precisa ser preservado integralmente.
def read_text(path: Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8-sig")


# Recusa caminhos operacionais linkados ou de tipo incompatível antes de qualquer escrita.
def assert_safe_operational_path(path: Path, code: str) -> None:
    if is_reparse_point(path) or (path.exists() and not path.is_file()):
        raise RuntimeError(f"{code}: {path.name} não é um arquivo operacional regular.")


# Acrescenta exclusões operacionais preservando regras existentes e evitando duplicação.
def add_gitignore_entry(path: Path, entry: str) -> None:
    assert_safe_operational_path(path, "GITIGNORE_INESPERADO")
    body = read_text(path) or ""
    if entry in {line.strip() for line in body.splitlines()}:
        return
    prefix = "\n" if body and not body.endswith("\n") else ""
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(f"{prefix}{entry}\n")


# Garante que o relatório operacional não entre no Git sem apagar as entradas existentes.
def ensure_gitignore(vf: Path) -> None:
    gitignore = vf / ".gitignore"
    add_gitignore_entry(gitignore, "interview-report.json")


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


# Transforma a frase curta da fase em slug ASCII [a-z0-9-], 2–48 chars.
def sanitize_slug(raw: str) -> str:
    decomposed = unicodedata.normalize("NFKD", raw or "")
    ascii_only = decomposed.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_only.lower()
    compact = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    compact = re.sub(r"-{2,}", "-", compact)
    return compact[:MAX_SLUG].strip("-")


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


# Representa o alvo MVP sem inferir intenção; a flag pública continua sendo decisão da IA.
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


# Fase de maior n com interview e sem spec: entrevista ainda não entregue à spec.
def find_aberta(existing: list[dict[str, Any]]) -> dict[str, Any] | None:
    for item in reversed(existing):
        if "interview.md" in item["files"] and "spec.md" not in item["files"]:
            return item
    return None


# Monta o JSON que a skill lê; stdout só o path do relatório.
def write_report(vf: Path, payload: dict[str, Any]) -> Path:
    report_path = vf / "interview-report.json"
    assert_safe_operational_path(report_path, "RELATORIO_INESPERADO")
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print(report_path)
    return report_path


# Inventaria o disco, cria phases/ se faltar e prepara o arquivo vivo no apply.
def run(args: argparse.Namespace) -> Path:
    if args.mvp and args.slug is not None:
        raise RuntimeError("MODO_INVALIDO: o alvo MVP não aceita --slug.")

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
    mvp = get_mvp(vf)
    created: dict[str, Any] | None = None

    if args.apply:
        if args.mvp:
            dest_dir = vf / "mvp"
            if is_reparse_point(dest_dir):
                raise RuntimeError("MVP_INESPERADO: .vibeflow/mvp não pode ser symlink, junction ou reparse point.")
            dest_file = dest_dir / "interview.md"
            created_dir = not dest_dir.exists()
            if created_dir:
                dest_dir.mkdir()
            try:
                file_created = prepare_live_file(dest_file)
            except Exception:
                if created_dir and not is_reparse_point(dest_dir) and dest_dir.exists() and not any(dest_dir.iterdir()):
                    dest_dir.rmdir()
                raise
            if file_created:
                actions.append({"op": "criar_arquivo", "alvo": ".vibeflow/mvp/interview.md"})
            mvp = get_mvp(vf)
            created = mvp
        else:
            slug = sanitize_slug(args.slug or "")
            if len(slug) < 2:
                raise RuntimeError("SLUG_INVALIDO: a frase curta não gerou um slug utilizável.")
            dest_dir = phases / f"phase-{next_n}-{slug}"
            dest_file = dest_dir / "interview.md"
            rel = f".vibeflow/phases/{dest_dir.name}"
            if is_reparse_point(dest_dir) or dest_dir.exists():
                raise RuntimeError(f"FASE_EXISTE: {rel} já existe.")
            dest_dir.mkdir(parents=True)
            try:
                file_created = prepare_live_file(dest_file)
            except Exception:
                if not is_reparse_point(dest_dir) and dest_dir.exists() and not any(dest_dir.iterdir()):
                    dest_dir.rmdir()
                raise
            if file_created:
                actions.append({"op": "criar_arquivo", "alvo": f"{rel}/interview.md"})
            created = {
                "kind": "phase",
                "dir": dest_dir.name,
                "n": next_n,
                "slug": slug,
                "path": rel,
                "files": ["interview.md"],
            }
            existing, extra_warnings = list_phases(phases)
            warnings.extend(extra_warnings)
            next_n = (existing[-1]["n"] + 1) if existing else 1

    aberta = find_aberta(existing)

    payload = {
        "root": str(repo),
        "rota": "mvp" if args.mvp else "phase",
        "modo": "mvp" if args.mvp else "phase",
        "vibeflow": vf_state,
        "phases": ph_state,
        "next_n": next_n,
        "existing": existing,
        "aberta": aberta,
        "mvp": mvp,
        "alvo": mvp if args.mvp else aberta,
        "created": created,
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
