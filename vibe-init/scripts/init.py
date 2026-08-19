#!/usr/bin/env python3
"""Inicializa ou repara a fonte única de regras sem depender de PowerShell."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any


TARGET_REL = ".vibeflow/REGRAS.md"
IGNORED_DIRS = {"node_modules", ".git", "dist", "build", ".next", "vendor", "__pycache__"}
EVIDENCE_WARNINGS: list[str] = []


# Interpreta somente os parâmetros equivalentes ao contrato público do init.ps1.
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inicializa ou repara .vibeflow")
    parser.add_argument("--root")
    parser.add_argument("--apply-pointers", action="store_true")
    parser.add_argument("--merge-token")
    parser.add_argument("--redirect-pointer", choices=("AGENTS", "CLAUDE"))
    parser.add_argument("--stop-after-old", action="store_true")
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


# Calcula o hash usado para validar backups e fontes de merge byte a byte.
def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


# Compara arquivos sem carregar conteúdo potencialmente grande em memória.
def same_bytes(first: Path, second: Path) -> bool:
    return first.is_file() and second.is_file() and first.stat().st_size == second.stat().st_size and sha256(first) == sha256(second)


# Compara caminhos com sensibilidade a caixa coerente com o sistema operacional.
def same_path(first: Path | str, second: Path | str) -> bool:
    left, right = os.path.abspath(str(first)), os.path.abspath(str(second))
    return os.path.normcase(left) == os.path.normcase(right)


# Lê texto operacional que precisa ser preservado integralmente.
def read_text(path: Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8-sig")


# Limita arquivos usados apenas como evidência para evitar consumo irrestrito de memória.
def read_evidence(path: Path, max_bytes: int = 1024 * 1024) -> str | None:
    if not path.is_file():
        return None
    if path.stat().st_size > max_bytes:
        EVIDENCE_WARNINGS.append(f"evidência ignorada por tamanho: {path}")
        return None
    return path.read_text(encoding="utf-8-sig")


# Extrai os SLOTs que ainda exigem evidência ou resposta humana.
def open_slots(text: str | None) -> list[str]:
    return re.findall(r"<!--\s*SLOT:(\w+)\s*-->", text or "")


# Reconhece o arquivo textual produzido quando um checkout degrada um symlink.
def is_pointer_text(path: Path) -> bool:
    text = read_text(path)
    if text is None:
        return False
    normalized = text.strip().lstrip("\ufeff").replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    if os.name == "nt":
        return normalized.casefold() == TARGET_REL.casefold()
    return normalized == TARGET_REL


# Classifica a pasta principal antes de qualquer alteração.
def vibeflow_state(path: Path) -> str:
    if not path.exists():
        return "ausente"
    if not path.is_dir():
        return "inesperado"
    if (path / "REGRAS.md").exists():
        return "com_regras"
    return "vazia" if not any(path.iterdir()) else "sem_regras"


# Classifica um arquivo de regras sem interpretar semanticamente seu conteúdo.
def regras_file_state(path: Path) -> str:
    if not path.exists():
        return "ausente"
    if not path.is_file():
        return "inesperado"
    text = read_text(path) or ""
    if not text.strip():
        return "vazio"
    return "template" if open_slots(text) else "preenchido"


# Resume a relação entre a fonte viva e uma possível cópia na raiz.
def regras_state(live: Path, root_copy: Path) -> str:
    if live.exists() and root_copy.exists():
        return "raiz_e_vibeflow"
    if root_copy.exists() and not live.exists():
        return "raiz_sozinho"
    return regras_file_state(live)


# Classifica um ponteiro considerando links quebrados, cópias e conteúdo legado.
def pointer_state(repo: Path, name: str, live: Path) -> str:
    path = repo / name
    if not path.exists() and not path.is_symlink():
        return "ausente"
    if path.is_dir() and not path.is_symlink():
        return "inesperado"
    if path.is_symlink():
        target = Path(os.readlink(path))
        resolved = (repo / target).resolve(strict=False) if not target.is_absolute() else target.resolve(strict=False)
        if not resolved.exists():
            return "symlink_quebrado"
        return "symlink_ok" if live.exists() and same_path(resolved, live.resolve()) else "symlink_outro"
    text = read_text(path) or ""
    if not text.strip():
        return "vazio"
    if is_pointer_text(path):
        return "ponteiro_texto"
    return "arquivo_igual" if live.is_file() and same_bytes(path, live) else "arquivo_legado"


# Recusa tipos estruturais que impediriam um reparo previsível antes da primeira escrita.
def assert_infrastructure_types(vf: Path, live: Path, root_copy: Path, phases: Path) -> None:
    if vf.exists() and not vf.is_dir():
        raise RuntimeError("TIPO_INESPERADO: .vibeflow existe, mas não é um diretório.")
    for path in (live, root_copy):
        if path.exists() and not path.is_file():
            raise RuntimeError(f"TIPO_INESPERADO: '{path}' existe, mas não é um arquivo.")
    if phases.exists() and not phases.is_dir():
        raise RuntimeError("TIPO_INESPERADO: .vibeflow/phases existe, mas não é um diretório.")


# Escolhe um nome de backup único sem depender da precisão do relógio.
def unique_old_path(old_dir: Path, name: str) -> Path:
    direct = old_dir / name
    if not direct.exists():
        return direct
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    candidate = old_dir / f"{name}.{stamp}"
    suffix = 1
    while candidate.exists():
        candidate = old_dir / f"{name}.{stamp}.{suffix}"
        suffix += 1
    return candidate


# Copia e valida um backup antes que qualquer fonte original possa ser substituída.
def copy_verified(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    if os.environ.get("VIBE_INIT_TEST_CORRUPT_OLD") == "1":
        destination.write_text("CORRUPT", encoding="utf-8")
    if not same_bytes(source, destination):
        destination.unlink(missing_ok=True)
        raise RuntimeError(f"OLD_HASH_MISMATCH: cópia de '{source}' não bateu com '{destination}'. Peça não substituída.")


# Cria e valida o link temporário antes de substituir o item que ocupa o caminho final.
def replace_symlink(link: Path, target: str) -> None:
    temporary = link.with_name(f"{link.name}.__vibe_symlink__{uuid.uuid4().hex}")
    try:
        temporary.symlink_to(target)
    except OSError as error:
        raise RuntimeError(
            f"SYMLINK_RECUSADO: o OS recusou criar o link '{link}' -> '{target}'. "
            "Ative o suporte a symlink ou execute com privilégios adequados; o original permanece."
        ) from error
    try:
        if link.exists() or link.is_symlink():
            link.unlink()
        temporary.rename(link)
    finally:
        temporary.unlink(missing_ok=True)


# Acrescenta exclusões operacionais preservando regras existentes e evitando duplicação.
def add_gitignore_entry(path: Path, entry: str) -> None:
    body = read_text(path) or ""
    if entry in {line.strip() for line in body.splitlines()}:
        return
    prefix = "\n" if body and not body.endswith("\n") else ""
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(f"{prefix}{entry}\n")


# Extrai um nome factual de manifests conhecidos ou do diretório do projeto.
def project_name(repo: Path) -> dict[str, str]:
    package = read_evidence(repo / "package.json")
    if package:
        try:
            value = json.loads(package).get("name")
            if value:
                return {"value": str(value), "from": "package.json"}
        except (json.JSONDecodeError, AttributeError):
            pass
    pyproject = read_evidence(repo / "pyproject.toml")
    if pyproject:
        match = re.search(r'(?ms)^\[project\].*?^name\s*=\s*["\']([^"\']+)["\']', pyproject)
        if match:
            return {"value": match.group(1), "from": "pyproject.toml"}
    gomod = read_evidence(repo / "go.mod")
    if gomod:
        match = re.search(r"(?m)^module\s+(\S+)", gomod)
        if match:
            return {"value": match.group(1).split("/")[-1], "from": "go.mod"}
    return {"value": repo.name, "from": "pasta"}


# Seleciona o primeiro parágrafo útil, ignorando títulos, badges e imagens iniciais.
def useful_paragraph(text: str | None) -> str | None:
    if not text or not text.strip():
        return None
    lines: list[str] = []
    started = False
    for raw in text.splitlines():
        line = raw.strip()
        if not started:
            if not line or re.match(r"^#+|^\[!\[|^!\[|^<!--|^<img", line):
                continue
            started = True
        if not line:
            break
        lines.append(line)
    return " ".join(lines).strip() or None


# Localiza uma descrição factual sem abrir arquivos maiores que o limite de evidência.
def paragraph_evidence(repo: Path) -> dict[str, str] | None:
    for name in ("README.md", "README.MD", "readme.md"):
        paragraph = useful_paragraph(read_evidence(repo / name))
        if paragraph:
            return {"text": paragraph, "from": name}
    package = read_evidence(repo / "package.json")
    if package:
        try:
            value = json.loads(package).get("description")
            if value:
                return {"text": str(value), "from": "package.json"}
        except (json.JSONDecodeError, AttributeError):
            pass
    pyproject = read_evidence(repo / "pyproject.toml")
    if pyproject:
        match = re.search(r'(?ms)^\[project\].*?^description\s*=\s*["\']([^"\']+)["\']', pyproject)
        if match:
            return {"text": match.group(1), "from": "pyproject.toml"}
    return None


# Lista dois níveis úteis da árvore sem entrar em diretórios de dependências ou build.
def structure(repo: Path) -> list[str]:
    result: list[str] = []
    for entry in sorted(repo.iterdir(), key=lambda item: item.name.casefold()):
        if entry.name in IGNORED_DIRS:
            continue
        result.append(entry.name)
        if entry.is_dir() and not entry.is_symlink():
            try:
                children = sorted(entry.iterdir(), key=lambda item: item.name.casefold())
            except OSError:
                children = []
            result.extend(f"{entry.name}/{child.name}" for child in children if child.name not in IGNORED_DIRS)
    return result


# Identifica a stack apenas pela presença de manifests conhecidos.
def stack(repo: Path) -> list[str]:
    names = ("package.json", "pyproject.toml", "go.mod", "Cargo.toml", "composer.json", "Gemfile", "pom.xml", "build.gradle", "requirements.txt", "Pipfile")
    return [name for name in names if (repo / name).is_file()]


# Detecta migrations com travessia podada, sem visitar dependências, builds ou symlinks.
def has_migrations(repo: Path) -> bool:
    known = ("prisma/migrations", "alembic", "alembic.ini", "drizzle", "knexfile.js", "knexfile.ts", "supabase/migrations")
    if any((repo / path).exists() for path in known):
        return True
    queue: deque[Path] = deque([repo])
    while queue:
        current = queue.popleft()
        try:
            children = current.iterdir()
        except OSError:
            continue
        for child in children:
            if child.name in IGNORED_DIRS or child.is_symlink() or not child.is_dir():
                continue
            if child.name == "migrations":
                return True
            queue.append(child)
    return False


# Extrai do template o único bloco que a skill controla integralmente.
def cadeia_block(template: str) -> str:
    match = re.search(r"(?s)<!-- VIBEFLOW:CADEIA start -->.*?<!-- VIBEFLOW:CADEIA end -->", template)
    if not match:
        raise RuntimeError("Template sem bloco VIBEFLOW:CADEIA")
    return match.group(0)


# Atualiza ou insere o roteador preservando todo o conteúdo pertencente ao usuário.
def set_cadeia(content: str, block: str) -> str:
    pattern = r"(?s)<!-- VIBEFLOW:CADEIA start -->.*?<!-- VIBEFLOW:CADEIA end -->"
    if re.search(pattern, content):
        return re.sub(pattern, lambda _: block, content, count=1)
    title = re.match(r"(?s)^(# [^\r\n]+\r?\n)(\r?\n)?", content)
    if title:
        return f"{title.group(1)}\n{block}\n\n{content[title.end():]}"
    return f"{block}\n\n{content}"


# Preenche somente um SLOT explicitamente respaldado por evidência.
def set_slot(content: str, slot: str, value: str, evidence: str | None = None) -> str:
    pattern = rf"(?m)^<!--\s*SLOT:{re.escape(slot)}\s*-->\s*\r?\n(?:<!--\s*evidência:[^\n]*-->\s*\r?\n)?"
    replacement = value.rstrip() + "\n"
    if evidence is not None:
        replacement += f"<!-- evidência: {evidence} -->\n"
    return re.sub(pattern, lambda _: replacement, content, count=1)


# Persiste o estado que vincula um merge às fontes e ao consolidado inventariados.
def write_pending(path: Path, repo: Path, target: Path, merges: list[dict[str, Any]]) -> dict[str, Any]:
    source_paths = list(dict.fromkeys(source for merge in merges for source in merge["sources"]))
    sources = []
    for source in source_paths:
        absolute = repo / source
        if not absolute.is_file():
            raise RuntimeError(f"MERGE_SOURCE_AUSENTE: fonte de merge não encontrada: {source}")
        sources.append({"path": source, "sha256": sha256(absolute)})
    pending = {
        "version": 1,
        "token": uuid.uuid4().hex,
        "target": target.relative_to(repo).as_posix(),
        "target_sha256_inicial": sha256(target),
        "sources": sources,
        "remove_regras_raiz": any(merge["id"] == "regras_duplicado" for merge in merges),
    }
    path.write_text(json.dumps(pending, ensure_ascii=False, indent=2), encoding="utf-8")
    return pending


# Autoriza a finalização somente quando token, fontes e consolidado permanecem coerentes.
def confirm_pending(path: Path, repo: Path, token: str | None) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError("APPLY_SEM_MERGE: não existe merge pendente para finalizar.")
    pending = json.loads(path.read_text(encoding="utf-8"))
    if not token or token != pending["token"]:
        raise RuntimeError("MERGE_TOKEN_INVALIDO: use o apply_token do init-report.json atual.")
    for source in pending["sources"]:
        absolute = repo / source["path"]
        if not absolute.is_file() or sha256(absolute) != source["sha256"]:
            raise RuntimeError(f"MERGE_SOURCE_ALTERADA: a fonte '{source['path']}' mudou desde o inventário.")
    target = repo / pending["target"]
    if not target.is_file():
        raise RuntimeError(f"MERGE_TARGET_AUSENTE: consolidado não encontrado: {pending['target']}")
    if sha256(target) == pending["target_sha256_inicial"]:
        raise RuntimeError("MERGE_NAO_APLICADO: o consolidado não mudou desde o inventário; os ponteiros foram preservados.")
    return pending


# Executa a matriz determinística e produz o relatório consumido pela IA.
def run(args: argparse.Namespace) -> Path:
    EVIDENCE_WARNINGS.clear()
    repo = repo_root(args.root)
    skill = Path(__file__).resolve().parent.parent
    template_path = skill / "templates" / "REGRAS.md"
    vf, root_copy = repo / ".vibeflow", repo / "REGRAS.md"
    live, old_dir, phases = vf / "REGRAS.md", vf / "old", vf / "phases"
    pending_path = vf / "init-pending.json"
    assert_infrastructure_types(vf, live, root_copy, phases)
    confirmed = confirm_pending(pending_path, repo, args.merge_token) if args.apply_pointers else None
    if not args.apply_pointers and pending_path.exists():
        raise RuntimeError("MERGE_PENDENTE: finalize o consolidado e use o apply_token do relatório atual.")

    inventory = {
        "vibeflow": vibeflow_state(vf),
        "phases": "ok" if phases.is_dir() else "ausente",
        "regras": regras_state(live, root_copy),
        "agents": pointer_state(repo, "AGENTS.md", live),
        "claude": pointer_state(repo, "CLAUDE.md", live),
    }
    flow = "reparar" if inventory["vibeflow"] != "ausente" or root_copy.exists() or inventory["agents"] != "ausente" or inventory["claude"] != "ausente" else "novo"
    olds: list[dict[str, Any]] = []
    actions: list[dict[str, str]] = []
    merges: list[dict[str, Any]] = []
    conflicts: list[dict[str, str]] = []
    warnings: list[str] = []

    # Registra ações em um único formato para manter paridade com o relatório PowerShell.
    def action(operation: str, target: str) -> None:
        actions.append({"op": operation, "alvo": target})

    # Salva uma fonte e devolve o path real, inclusive quando recebeu sufixo de colisão.
    def save_old(source: Path, name: str) -> str:
        destination = unique_old_path(old_dir, name)
        copy_verified(source, destination)
        relative = destination.relative_to(repo).as_posix()
        olds.append({"from": source.relative_to(repo).as_posix(), "to": relative, "bytes": destination.stat().st_size, "sha256": sha256(destination)})
        action("old", relative)
        return relative

    if inventory["vibeflow"] == "ausente":
        vf.mkdir()
        action("criar_dir", ".vibeflow")
    if not phases.exists():
        phases.mkdir(parents=True)
        (phases / ".gitkeep").write_text("", encoding="utf-8")
        action("criar_phases", ".vibeflow/phases")
    add_gitignore_entry(vf / ".gitignore", "init-report.json")
    add_gitignore_entry(vf / ".gitignore", "init-pending.json")

    agents_path, claude_path = repo / "AGENTS.md", repo / "CLAUDE.md"
    agents_legacy, claude_legacy = inventory["agents"] == "arquivo_legado", inventory["claude"] == "arquivo_legado"
    equal_legacy = agents_legacy and claude_legacy and same_bytes(agents_path, claude_path)
    content_state = regras_file_state(live if live.exists() else root_copy)
    need_template = inventory["regras"] not in ("raiz_sozinho", "raiz_e_vibeflow") and content_state in ("ausente", "vazio")
    merge_pending = False
    if not args.apply_pointers:
        if need_template or content_state == "vazio" or inventory["regras"] == "ausente":
            if agents_legacy and claude_legacy and not equal_legacy:
                merge_pending = True
                merges.append({"id": "duas_fontes", "sources": [".vibeflow/old/AGENTS.md", ".vibeflow/old/CLAUDE.md"], "target": TARGET_REL})
            elif agents_legacy or claude_legacy:
                merge_pending = True
                sources = ([".vibeflow/old/AGENTS.md"] if agents_legacy else []) + ([".vibeflow/old/CLAUDE.md"] if claude_legacy else [])
                merges.append({"id": "legado_vs_regras", "sources": sources, "target": TARGET_REL})
        elif inventory["regras"] in ("template", "preenchido"):
            sources = ([".vibeflow/old/AGENTS.md"] if agents_legacy else []) + ([".vibeflow/old/CLAUDE.md"] if claude_legacy else [])
            if sources:
                merge_pending = True
                merges.append({"id": "legado_vs_regras", "sources": sources + [".vibeflow/old/REGRAS.md"], "target": TARGET_REL})
        elif inventory["regras"] == "raiz_e_vibeflow" and not same_bytes(root_copy, live):
            merge_pending = True
            merges.append({"id": "regras_duplicado", "sources": [".vibeflow/old/REGRAS-raiz.md", ".vibeflow/old/REGRAS.md"], "target": TARGET_REL})
    if merges:
        action("merge_pendente", TARGET_REL)

    for name, state in (("AGENTS.md", inventory["agents"]), ("CLAUDE.md", inventory["claude"])):
        if state == "ponteiro_texto":
            warnings.append(f"{name} é ponteiro_texto (checkout sem symlink). Não entra em merge.")
        elif state == "symlink_outro":
            conflicts.append({"id": "ponteiro_alheio", "peca": name, "detalhe": f"link para outro arquivo (não é {TARGET_REL})"})
        elif state == "inesperado":
            conflicts.append({"id": "tipo_inesperado", "peca": name, "detalhe": "não é arquivo nem symlink"})

    old_map: dict[str, str] = {}
    if not args.apply_pointers:
        if agents_legacy or inventory["agents"] in ("arquivo_igual", "ponteiro_texto"):
            old_map[".vibeflow/old/AGENTS.md"] = save_old(agents_path, "AGENTS.md")
        if claude_legacy or inventory["claude"] in ("arquivo_igual", "ponteiro_texto"):
            old_map[".vibeflow/old/CLAUDE.md"] = save_old(claude_path, "CLAUDE.md")
        if inventory["regras"] in ("raiz_sozinho", "raiz_e_vibeflow"):
            old_map[".vibeflow/old/REGRAS-raiz.md"] = save_old(root_copy, "REGRAS-raiz.md")
        if merge_pending and inventory["regras"] in ("template", "preenchido", "raiz_e_vibeflow") and live.is_file() and (read_text(live) or "").strip():
            old_map[".vibeflow/old/REGRAS.md"] = save_old(live, "REGRAS.md")
        for merge in merges:
            merge["sources"] = [old_map.get(source, source) for source in merge["sources"]]

    if args.stop_after_old:
        return write_report(repo, flow, inventory, olds, actions, merges, conflicts, warnings, {}, [], False, {}, False, False, None)

    if inventory["regras"] == "raiz_sozinho":
        root_copy.replace(live)
        action("mover", "REGRAS.md -> .vibeflow/REGRAS.md")
    elif inventory["regras"] == "raiz_e_vibeflow" and same_bytes(root_copy, live):
        root_copy.unlink()
        action("apagar_raiz", "REGRAS.md")
    elif need_template:
        shutil.copyfile(template_path, live)
        action("escrever_template", TARGET_REL)

    # Converte cada ponteiro independentemente, preservando fontes ainda necessárias ao merge.
    def convert_pointer(name: str, state: str) -> None:
        path = repo / name
        key = name.removesuffix(".md")
        if state in ("inesperado", "symlink_ok") or state == "symlink_outro" and args.redirect_pointer != key:
            return
        if state == "arquivo_legado" and merge_pending and not args.apply_pointers:
            return
        if state == "symlink_outro" and args.redirect_pointer == key:
            previous = os.readlink(path)
            destination = unique_old_path(old_dir, name.replace(".md", ".target.txt"))
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(previous, encoding="utf-8")
            olds.append({"from": name, "to": destination.relative_to(repo).as_posix(), "bytes": len(previous.encode()), "sha256": "target-path"})
        if state in ("ausente", "vazio", "arquivo_igual", "arquivo_legado", "ponteiro_texto"):
            replace_symlink(path, TARGET_REL)
            action("symlink_criar", name)
        elif state == "symlink_quebrado" or state == "symlink_outro" and args.redirect_pointer:
            replace_symlink(path, TARGET_REL)
            action("symlink_recriar", name)

    if live.exists():
        convert_pointer("AGENTS.md", inventory["agents"])
        convert_pointer("CLAUDE.md", inventory["claude"])
    if args.apply_pointers and confirmed and confirmed["remove_regras_raiz"] and root_copy.is_file():
        root_copy.unlink()
        action("apagar_raiz", "REGRAS.md")

    filled: dict[str, Any] = {"nome": project_name(repo)}
    tree, manifests, migrations, evidence = structure(repo), stack(repo), has_migrations(repo), paragraph_evidence(repo)
    warnings.extend(item for item in dict.fromkeys(EVIDENCE_WARNINGS) if item not in warnings)
    scan = {"estrutura": tree, "stack": manifests, "evidencia_paragrafo": evidence}
    if live.is_file():
        body = read_text(live) or ""
        slots = open_slots(body)
        if "estrutura" in slots:
            body = set_slot(body, "estrutura", "\n".join(f"- {item}" for item in tree) if tree else "- (raiz vazia)")
        if "paragrafo" in slots and evidence:
            body = set_slot(body, "paragrafo", evidence["text"], evidence["from"])
            filled["paragrafo"] = {"value": evidence["text"], "from": evidence["from"]}
        refreshed = set_cadeia(body, cadeia_block(read_text(template_path) or ""))
        if refreshed != body:
            action("cadeia_upsert", TARGET_REL)
        live.write_text(refreshed, encoding="utf-8", newline="\n")

    slots = open_slots(read_text(live))
    symlink_agents = pointer_state(repo, "AGENTS.md", live) == "symlink_ok"
    symlink_claude = pointer_state(repo, "CLAUDE.md", live) == "symlink_ok"
    apply_token = None
    if not args.apply_pointers and merges:
        apply_token = write_pending(pending_path, repo, live, merges)["token"]
    if args.apply_pointers:
        pending_path.unlink(missing_ok=True)
    return write_report(repo, flow, inventory, olds, actions, merges, conflicts, warnings, filled, slots, migrations, scan, symlink_agents, symlink_claude, apply_token)


# Grava o JSON final usando o mesmo schema emitido pela implementação PowerShell.
def write_report(
    repo: Path,
    flow: str,
    inventory: dict[str, str],
    olds: list[dict[str, Any]],
    actions: list[dict[str, str]],
    merges: list[dict[str, Any]],
    conflicts: list[dict[str, str]],
    warnings: list[str],
    filled: dict[str, Any],
    slots: list[str],
    migrations: bool,
    scan: dict[str, Any],
    symlink_agents: bool,
    symlink_claude: bool,
    apply_token: str | None,
) -> Path:
    report_path = repo / ".vibeflow" / "init-report.json"
    report = {
        "flow": flow,
        "root": str(repo),
        "inventory": inventory,
        "olds": olds,
        "actions": actions,
        "merges": merges,
        "conflicts": conflicts,
        "filled": filled,
        "slots_abertos": slots,
        "migrations_detectadas": migrations,
        "symlink_ok": {"agents": symlink_agents, "claude": symlink_claude},
        "scan": scan,
        "avisos": warnings,
        "apply_token": apply_token,
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print(report_path)
    return report_path


# Converte falhas previstas em mensagens curtas, sem stack trace operacional para o usuário.
def main() -> int:
    try:
        run(parse_args())
        return 0
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
