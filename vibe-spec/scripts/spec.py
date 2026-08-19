#!/usr/bin/env python3
"""Inventaria .vibeflow/phases e promove o wip para phase-N-slug/spec.md."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Any


PHASE_RE = re.compile(r"^phase-(\d+)-([a-z0-9]+(?:-[a-z0-9]+)*)$")
CHAIN_FILES = ("interview.md", "spec.md", "plan.md", "analyze.md")
MAX_SLUG = 48


# Interpreta somente os parâmetros equivalentes ao contrato público do spec.ps1.
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inventaria e promove spec para .vibeflow/phases")
    parser.add_argument("--root")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--slug")
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
    add_gitignore_entry(gitignore, "spec-report.json")
    add_gitignore_entry(gitignore, "spec-wip.md")


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


# Maior n com interview e sem spec: a spec deve reusar esta pasta.
def find_interview_pendente(existing: list[dict[str, Any]]) -> dict[str, Any] | None:
    for item in reversed(existing):
        if "interview.md" in item["files"] and "spec.md" not in item["files"]:
            return item
    return None


# Maior n com spec e sem plan: rascunho ainda atualizável.
def find_rascunho(existing: list[dict[str, Any]]) -> dict[str, Any] | None:
    for item in reversed(existing):
        if "spec.md" in item["files"] and "plan.md" not in item["files"]:
            return item
    return None


# Destino preferido: interview pendente, senão rascunho, senão criar.
def resolve_alvo(
    existing: list[dict[str, Any]],
) -> tuple[dict[str, Any] | None, str]:
    pending = find_interview_pendente(existing)
    if pending:
        return pending, "reuse"
    draft = find_rascunho(existing)
    if draft:
        return draft, "atualizar"
    return None, "criar"


# Cópia binária conferida. Não apaga pasta que já tinha outros artefatos.
def promote_wip(wip: Path, dest_file: Path, dest_dir: Path, created_dir: bool) -> None:
    dest_file.write_bytes(wip.read_bytes())
    if dest_file.stat().st_size != wip.stat().st_size or sha256(dest_file) != sha256(wip):
        dest_file.unlink(missing_ok=True)
        if created_dir and dest_dir.exists() and not any(dest_dir.iterdir()):
            dest_dir.rmdir()
        raise RuntimeError("COPY_HASH_MISMATCH: a cópia do wip não bateu com o original.")


# Monta o JSON que a skill lê; stdout só o path do relatório.
def write_report(vf: Path, payload: dict[str, Any]) -> Path:
    report_path = vf / "spec-report.json"
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print(report_path)
    return report_path


# Inventaria o disco e opcionalmente promove o wip para spec.md.
def run(args: argparse.Namespace) -> Path:
    repo = repo_root(args.root)
    vf = repo / ".vibeflow"
    phases = vf / "phases"
    wip = vf / "spec-wip.md"
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
    pending = find_interview_pendente(existing)
    draft = find_rascunho(existing)
    alvo, modo_sugerido = resolve_alvo(existing)
    created: dict[str, Any] | None = None
    modo: str | None = None

    if args.apply:
        if not wip.is_file() or wip.stat().st_size == 0:
            raise RuntimeError("WIP_AUSENTE: falta .vibeflow/spec-wip.md preenchido.")

        dest_dir: Path
        created_dir = False
        if args.dir:
            dest_dir = phases / Path(args.dir).name
            if not dest_dir.is_dir():
                raise RuntimeError(f"FASE_AUSENTE: .vibeflow/phases/{dest_dir.name} não existe.")
            match = PHASE_RE.fullmatch(dest_dir.name)
            if not match:
                raise RuntimeError(f"FASE_AUSENTE: {dest_dir.name} não é uma pasta de fase.")
            modo = "atualizar" if (dest_dir / "spec.md").is_file() else "reuse"
        elif alvo:
            dest_dir = repo / alvo["path"]
            modo = modo_sugerido
        else:
            if not (args.slug or "").strip():
                raise RuntimeError("SPEC_SEM_ALVO: sem fase alvo; passe --slug para abrir uma pasta nova.")
            slug = sanitize_slug(args.slug or "")
            if len(slug) < 2:
                raise RuntimeError("SLUG_INVALIDO: a frase curta não gerou um slug utilizável.")
            dest_dir = phases / f"phase-{next_n}-{slug}"
            if dest_dir.exists():
                raise RuntimeError(f"FASE_EXISTE: .vibeflow/phases/{dest_dir.name} já existe.")
            dest_dir.mkdir(parents=True)
            created_dir = True
            modo = "criar"

        if (dest_dir / "plan.md").is_file():
            if created_dir and not any(dest_dir.iterdir()):
                dest_dir.rmdir()
            raise RuntimeError(
                f"SPEC_JA_PLANEJADA: {dest_dir.name} já tem plan.md. Não pise. Pedido novo = outra fase."
            )

        dest_file = dest_dir / "spec.md"
        rel = f".vibeflow/phases/{dest_dir.name}"
        try:
            promote_wip(wip, dest_file, dest_dir, created_dir)
        except Exception:
            if created_dir:
                dest_file.unlink(missing_ok=True)
                if dest_dir.exists() and not any(dest_dir.iterdir()):
                    dest_dir.rmdir()
            raise
        wip.unlink()
        actions.append({"op": "promover_wip", "alvo": f"{rel}/spec.md"})
        existing, extra_warnings = list_phases(phases)
        warnings.extend(extra_warnings)
        next_n = (existing[-1]["n"] + 1) if existing else 1
        pending = find_interview_pendente(existing)
        draft = find_rascunho(existing)
        alvo, modo_sugerido = resolve_alvo(existing)
        created = next((item for item in existing if item["dir"] == dest_dir.name), None)

    payload = {
        "root": str(repo),
        "vibeflow": vf_state,
        "phases": ph_state,
        "next_n": next_n,
        "existing": existing,
        "interview_pendente": pending,
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
