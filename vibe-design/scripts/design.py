#!/usr/bin/env python3
"""Inventaria .vibeflow/phases e prepara phase-N-slug/design.md."""

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
CHAIN_FILES = ("interview.md", "spec.md", "design.md", "plan.md", "analyze.md", "implement.md", "review.md")
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


# Interpreta somente os parâmetros equivalentes ao contrato público do design.ps1.
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inventaria e prepara design para .vibeflow/phases")
    parser.add_argument("--root")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--slug")
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


# Representa o alvo MVP sem inferir a rota a partir do conteúdo do projeto.
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


# Maior n com spec e sem design: a design deve reusar esta pasta.
def find_spec_pendente(existing: list[dict[str, Any]]) -> dict[str, Any] | None:
    for item in reversed(existing):
        if "spec.md" in item["files"] and "design.md" not in item["files"]:
            return item
    return None


# Maior n com design e sem plan: rascunho ainda atualizável.
def find_rascunho(existing: list[dict[str, Any]]) -> dict[str, Any] | None:
    for item in reversed(existing):
        if "design.md" in item["files"] and "plan.md" not in item["files"]:
            return item
    return None


# Escolhe o alvo sem misturar pedido novo com rascunho antigo.
def resolve_alvo(
    existing: list[dict[str, Any]],
    explicit_slug: bool = False,
) -> tuple[dict[str, Any] | None, str]:
    pending = find_spec_pendente(existing)
    if pending:
        return pending, "reuse"
    if explicit_slug:
        return None, "criar"
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


# Remove a pasta recém-criada quando o gate recusa, para não deixar fase vazia no disco.
def rollback_empty_dir(dest_dir: Path) -> None:
    if not is_reparse_point(dest_dir) and dest_dir.exists() and not any(dest_dir.iterdir()):
        dest_dir.rmdir()


# Serializa o inventário como JSON transitório para o consumidor imediato, sem criar estado no workspace.
def emit_report(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


# Inventaria o disco e prepara o arquivo vivo no apply.
def run(args: argparse.Namespace) -> None:
    if args.mvp and (args.slug is not None or args.dir is not None):
        raise RuntimeError("MODO_INVALIDO: o alvo MVP não aceita --slug nem --dir.")

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
    alvo, modo_sugerido = resolve_alvo(existing, args.slug is not None)
    mvp = get_mvp(vf)
    if args.mvp and (mvp is None or "spec.md" not in mvp["files"]):
        raise RuntimeError("DESIGN_SEM_SPEC: falta .vibeflow/mvp/spec.md. Rode /vibe-spec primeiro.")
    created: dict[str, Any] | None = None
    modo: str | None = None

    if args.apply:
        dest_dir: Path
        created_dir = False
        if args.mvp:
            dest_dir = vf / "mvp"
            modo = "atualizar" if (dest_dir / "design.md").is_file() else "reuse"
        elif args.dir:
            dest_dir = phases / Path(args.dir).name
            if is_reparse_point(dest_dir) or not dest_dir.is_dir():
                raise RuntimeError(f"FASE_AUSENTE: .vibeflow/phases/{dest_dir.name} não existe.")
            match = PHASE_RE.fullmatch(dest_dir.name)
            if not match:
                raise RuntimeError(f"FASE_AUSENTE: {dest_dir.name} não é uma pasta de fase.")
            modo = "atualizar" if (dest_dir / "design.md").is_file() else "reuse"
        elif alvo:
            dest_dir = repo / alvo["path"]
            modo = modo_sugerido
        else:
            if not (args.slug or "").strip():
                raise RuntimeError("DESIGN_SEM_ALVO: sem fase alvo; passe --slug para abrir uma pasta nova.")
            slug = sanitize_slug(args.slug or "")
            if len(slug) < 2:
                raise RuntimeError("SLUG_INVALIDO: a frase curta não gerou um slug utilizável.")
            dest_dir = phases / f"phase-{next_n}-{slug}"
            if is_reparse_point(dest_dir) or dest_dir.exists():
                raise RuntimeError(f"FASE_EXISTE: .vibeflow/phases/{dest_dir.name} já existe.")
            dest_dir.mkdir(parents=True)
            created_dir = True
            modo = "criar"

        if not (dest_dir / "spec.md").is_file():
            if created_dir:
                rollback_empty_dir(dest_dir)
            raise RuntimeError(
                f"DESIGN_SEM_SPEC: {dest_dir.name} não tem spec.md. Rode /vibe-spec primeiro."
            )

        if (dest_dir / "plan.md").is_file():
            if created_dir:
                rollback_empty_dir(dest_dir)
            raise RuntimeError(
                f"DESIGN_JA_PLANEJADO: {dest_dir.name} já tem plan.md. Não pise. Pedido novo = outra phase."
            )

        dest_file = dest_dir / "design.md"
        rel = ".vibeflow/mvp" if args.mvp else f".vibeflow/phases/{dest_dir.name}"
        try:
            file_created = prepare_live_file(dest_file)
        except Exception:
            if created_dir:
                rollback_empty_dir(dest_dir)
            raise
        if file_created:
            actions.append({"op": "criar_arquivo", "alvo": f"{rel}/design.md"})
        if args.mvp:
            mvp = get_mvp(vf)
            created = mvp
        else:
            existing, extra_warnings = list_phases(phases)
            warnings.extend(extra_warnings)
            next_n = (existing[-1]["n"] + 1) if existing else 1
            pending = find_spec_pendente(existing)
            draft = find_rascunho(existing)
            alvo, modo_sugerido = resolve_alvo(existing, args.slug is not None)
            created = next((item for item in existing if item["dir"] == dest_dir.name), None)

    if args.mvp and mvp is not None:
        modo_sugerido_mvp = "atualizar" if "design.md" in mvp["files"] else "reuse"
    elif args.mvp:
        modo_sugerido_mvp = "reuse"
    else:
        modo_sugerido_mvp = modo_sugerido
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
        "modo_sugerido": modo_sugerido_mvp,
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
