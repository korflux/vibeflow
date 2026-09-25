#!/usr/bin/env python3
"""Prepara AGENTS.md como fonte única das regras de um projeto VibeFlow."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


START = "<!-- VIBEFLOW:CADEIA start -->"
END = "<!-- VIBEFLOW:CADEIA end -->"
BRIDGE = "@../../AGENTS.md\n"


# Recusa symlinks e junctions nos diretórios e artefatos operacionais do init.
def is_reparse(path: Path) -> bool:
    if not path.exists() and not path.is_symlink():
        return False
    return path.is_symlink() or bool(getattr(path.lstat(), "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


# Aceita uma raiz explícita e só usa Git para localizar o projeto quando ela falta.
def repo_root(value: str | None) -> Path:
    if value:
        root = Path(value).resolve()
    else:
        probe = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False) if shutil.which("git") else None
        root = Path(probe.stdout.strip()).resolve() if probe and probe.returncode == 0 else Path.cwd().resolve()
    if not root.is_dir():
        raise RuntimeError(f"RAIZ_AUSENTE: {root}")
    return root


# Calcula o hash usado para conferir backups antes de qualquer substituição.
def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


# Recusa links externos e tipos inesperados nas fontes de regras.
def readable_source(path: Path, root: Path) -> Path | None:
    if not path.exists() and not path.is_symlink():
        return None
    target = (path.parent / os.readlink(path)).resolve(strict=True) if path.is_symlink() else path.resolve(strict=True)
    try:
        local = os.path.commonpath((str(root), str(target))) == str(root)
    except ValueError:
        local = False
    if not local:
        raise RuntimeError(f"FONTE_EXTERNA: {path} aponta para fora do projeto")
    if not target.is_file():
        raise RuntimeError(f"TIPO_INESPERADO: {path} não é arquivo")
    if target.stat().st_size > 1024 * 1024:
        raise RuntimeError(f"FONTE_GRANDE: {path} excede 1 MiB")
    return target


# Salva uma cópia verificada e preserva colisões com sufixo de tempo.
def backup(source: Path, root: Path, old: Path, name: str, records: list[dict[str, str]]) -> Path:
    old.mkdir(parents=True, exist_ok=True)
    destination = old / name
    if destination.exists():
        if sha256(destination) == sha256(source):
            return destination
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        destination = old / f"{name}.{stamp}"
    shutil.copyfile(source, destination)
    if destination.stat().st_size != source.stat().st_size or sha256(destination) != sha256(source):
        destination.unlink(missing_ok=True)
        raise RuntimeError(f"OLD_HASH_MISMATCH: backup de {source} não confere")
    records.append({"from": source.relative_to(root).as_posix(), "to": destination.relative_to(root).as_posix(), "sha256": sha256(destination)})
    return destination


# Atualiza só o roteador e a regra de escopo no topo, preservando as outras regras do usuário.
def update_header(content: str, template: str) -> str:
    block = template[template.index(START):template.index(END) + len(END)]
    scope = template.split(START, 1)[0].split("\n\n", 1)[1].strip()
    if (START in content) != (END in content):
        raise RuntimeError("CADEIA_INCOMPLETA: delimitadores do roteador não formam um par")
    if START in content:
        content = content[:content.index(START)] + block + content[content.index(END) + len(END):]
    else:
        if content.startswith("# ") and "\n" in content:
            title, body = content.split("\n", 1)
            content = f"{title}\n\n{block}\n\n{body.lstrip()}"
        else:
            content = f"{block}\n\n{content.lstrip()}"
    if scope not in content:
        if content.startswith("# ") and "\n" in content:
            title, body = content.split("\n", 1)
            content = f"{title}\n\n{scope}\n\n{body.lstrip()}"
        else:
            content = f"{scope}\n\n{content}"
    return content.rstrip() + "\n"


# Prepara diretórios e relatório operacional sem criar outra fonte de regras.
def run(root: Path) -> Path:
    vf = root / ".vibeflow"
    phases = vf / "phases"
    old = vf / "old"
    agents = root / "AGENTS.md"
    bridge = root / ".agents" / "rules" / "vibeflow.md"
    template = (Path(__file__).resolve().parent.parent / "templates" / "AGENTS.md").read_text(encoding="utf-8")
    for directory in (vf, phases, old, bridge.parent.parent, bridge.parent):
        if is_reparse(directory) or directory.exists() and not directory.is_dir():
            raise RuntimeError(f"TIPO_INESPERADO: {directory} não é diretório")
    for operational in (vf / ".gitignore", vf / "init-report.json", phases / ".gitkeep", bridge):
        if is_reparse(operational):
            raise RuntimeError(f"TIPO_INESPERADO: {operational} não pode ser link")
    legacy = [root / ".vibeflow" / "REGRAS.md", root / "REGRAS.md", root / "CLAUDE.md"]
    agent_source = readable_source(agents, root)
    legacy_sources = [(path, readable_source(path, root)) for path in legacy]
    legacy_sources = [(path, source) for path, source in legacy_sources if source]
    for directory in (vf, phases, bridge.parent):
        directory.mkdir(parents=True, exist_ok=True)
    (phases / ".gitkeep").touch(exist_ok=True)
    gitignore = vf / ".gitignore"
    ignored = gitignore.read_text(encoding="utf-8") if gitignore.is_file() else ""
    for entry in ("init-report.json", "init-pending.json"):
        if entry not in ignored.splitlines():
            ignored += ("" if not ignored or ignored.endswith("\n") else "\n") + entry + "\n"
    gitignore.write_text(ignored, encoding="utf-8")

    records: list[dict[str, str]] = []
    actions: list[str] = []
    if agent_source:
        original = agent_source.read_text(encoding="utf-8")
        if agents.is_symlink() or not original.strip():
            backup(agent_source, root, old, "AGENTS.md", records)
            if agents.is_symlink():
                agents.unlink()
            agents.write_text(original if original.strip() else template, encoding="utf-8")
            actions.append("materializar_AGENTS")
    else:
        source = legacy_sources[0][1] if legacy_sources else None
        agents.write_text(source.read_text(encoding="utf-8") if source else template, encoding="utf-8")
        actions.append("criar_AGENTS")

    for path, source in legacy_sources:
        if path.is_symlink():
            continue
        backup(source, root, old, path.name if path.parent == root else "REGRAS-vibeflow.md", records)
    current = agents.read_text(encoding="utf-8")
    updated = update_header(current, template)
    if updated != current:
        if not any(item["from"] == "AGENTS.md" for item in records) and current.strip():
            backup(agents, root, old, "AGENTS.md", records)
        agents.write_text(updated, encoding="utf-8", newline="\n")
        actions.append("atualizar_AGENTS")

    if bridge.exists() and not bridge.is_file():
        raise RuntimeError(f"TIPO_INESPERADO: {bridge} não é arquivo")
    if bridge.is_file() and bridge.read_text(encoding="utf-8") != BRIDGE:
        backup(bridge, root, old, "antigravity-vibeflow.md", records)
    if not bridge.exists() or bridge.read_text(encoding="utf-8") != BRIDGE:
        bridge.write_text(BRIDGE, encoding="utf-8")
        actions.append("atualizar_ponte_antigravity")

    merges = [path.relative_to(root).as_posix() for path, source in legacy_sources if source.read_bytes() != agents.read_bytes()]
    report = {"root": str(root), "target": "AGENTS.md", "actions": actions, "olds": records, "merges": merges, "legacy_present": [path.relative_to(root).as_posix() for path, _ in legacy_sources]}
    output = vf / "init-report.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output)
    return output


# Converte erros previsíveis em mensagem curta para o usuário.
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root")
    args = parser.parse_args()
    try:
        run(repo_root(args.root))
        return 0
    except (OSError, RuntimeError, ValueError, UnicodeError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
