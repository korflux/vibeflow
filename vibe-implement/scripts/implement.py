#!/usr/bin/env python3
"""Seleciona alvo e fila do plan sem criar artefato de execução."""

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
CHAIN_FILES = ("interview.md", "spec.md", "plan.md", "analyze.md", "review.md")
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
TASK_HEADING_RE = re.compile(r"^### T(\d+):")
DONE_LINE_RE = re.compile(r"^- \[([ xX])\] T(\d+) concluída\s*$")
DEPS_LINE_RE = re.compile(r"^- \*\*Deps:\*\*\s*(.*)$")
DEP_ID_RE = re.compile(r"T(\d+)")

# Prefixo do aviso emitido para T* sem linha concluída. A derivação da etapa o reconhece, pois a T* some da fila.
AVISO_SEM_CONCLUIDA = "sem linha concluída"

# Marcas do review.md lidas só para derivar a etapa; o conteúdo semântico do arquivo não é interpretado.
REVIEW_STATUS_RE = re.compile(r"^# Status:\s*([^\s]+)\s*$", re.MULTILINE | re.IGNORECASE)
OPEN_BLOCKER_RE = re.compile(r"^\s*- \[ \] R\d+: \*\*(?:Critical|Required)\*\*")
APPROVE_MARK_RE = re.compile(r"^\s*- \[[xX]\] \*\*Approve(?: com defer)?\*\*")
VEREDITO_VIGENTE_RE = re.compile(r"^##\s+Veredito vigente\s*$")
ETAPA_HEADING_RE = re.compile(r"^### Etapa\b")
ETAPA_VERDICT_RE = re.compile(r"^\s*- Veredito desta etapa:\s*(.*?)\s*$")
# O veredito conta quando começa com `Request changes`, com marcação `*` ou `_` opcional antes e texto depois,
# porque reviews reais o escrevem assim (`**Request changes**. motivo`). A lista de alternativas do template
# começa com outro valor e não conta. O lookahead recusa só letra ou dígito depois (`_` fecha a marcação).
REQUEST_CHANGES_RE = re.compile(r"^[*_]*Request changes(?![^\W_])")


# Interpreta somente os parâmetros equivalentes ao contrato público do implement.ps1.
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seleciona o alvo e a fila do plan sem criar artefato de execução")
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


# Lê texto operacional que precisa ser preservado integralmente.
def read_text(path: Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8-sig")


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


# Monta o objeto de fase a partir de uma pasta que já bateu o padrão.
def phase_item(child: Path) -> dict[str, Any]:
    match = PHASE_RE.fullmatch(child.name)
    assert match is not None
    files = [name for name in CHAIN_FILES if (child / name).is_file()]
    return {
        "kind": "phase",
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
        if is_reparse_point(child):
            warnings.append(f"ignorado (link/reparse point): {child.name}")
            continue
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


# Extrai apenas status e veredito do analyze MVP para impedir código antes da aprovação limpa.
def analyze_gate(path: Path) -> dict[str, Any]:
    body = read_text(path)
    if body is None:
        return {"status": "ausente", "veredito": "ausente", "pronto": False}
    status_match = re.search(r"^# Status:\s*([^\s]+)\s*$", body, re.MULTILINE | re.IGNORECASE)
    verdict_match = re.search(
        r"^## Veredito\s*$\s*^\s*(limpo|bloqueado)\s*$",
        body,
        re.MULTILINE | re.IGNORECASE,
    )
    status = status_match.group(1).lower() if status_match else "ausente"
    verdict = verdict_match.group(1).lower() if verdict_match else "ausente"
    return {"status": status, "veredito": verdict, "pronto": status == "aprovado" and verdict == "limpo"}


# Maior n com plan.md: é a fila desta skill sem --dir.
def find_alvo_com_plan(existing: list[dict[str, Any]]) -> dict[str, Any] | None:
    for item in reversed(existing):
        if "plan.md" in item["files"]:
            return item
    return None


# Seleciona a fase com plan mais recente, sem depender de implement.md histórico.
def resolve_alvo(existing: list[dict[str, Any]]) -> dict[str, Any] | None:
    return find_alvo_com_plan(existing)


# Quebra o plan em seções T* só pelos headings ### T{n}:; o resto da prosa não inicia tarefa.
def split_task_sections(text: str) -> list[tuple[str, list[str]]]:
    sections: list[tuple[str, list[str]]] = []
    current_id: str | None = None
    current_lines: list[str] = []
    for line in text.splitlines():
        heading = TASK_HEADING_RE.match(line)
        if heading:
            if current_id is not None:
                sections.append((current_id, current_lines))
            current_id = f"T{heading.group(1)}"
            current_lines = []
            continue
        if current_id is not None:
            current_lines.append(line)
    if current_id is not None:
        sections.append((current_id, current_lines))
    return sections


# Extrai ids T* da linha Deps. "nenhuma", vazio ou ausência viram lista vazia.
def parse_deps_value(raw: str | None) -> list[str]:
    text = (raw or "").strip()
    if text == "" or text.lower() == "nenhuma":
        return []
    found: list[str] = []
    seen: set[str] = set()
    for match in DEP_ID_RE.finditer(text):
        token = f"T{match.group(1)}"
        if token not in seen:
            seen.add(token)
            found.append(token)
    return found


# n numérico de T12 → 12, para ordenar a fila sem ordem lexicográfica.
def task_n(tid: str) -> int:
    return int(tid[1:])


# Lê só concluída + Deps. Não interpreta Status, aceite ou texto livre.
def parse_plan_fila(text: str) -> dict[str, Any]:
    empty: dict[str, Any] = {
        "parse": "ausente",
        "concluidas": [],
        "abertas": [],
        "elegiveis": [],
        "bloqueadas": [],
        "avisos": [],
    }
    sections = split_task_sections(text)
    if not sections:
        return empty

    avisos: list[str] = []
    parsed: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for tid, lines in sections:
        if tid in seen_ids:
            avisos.append(f"T* duplicada ignorada: {tid}")
            continue
        seen_ids.add(tid)
        done: bool | None = None
        deps_raw: str | None = None
        for line in lines:
            stripped = line.strip()
            if done is None:
                done_match = DONE_LINE_RE.match(stripped)
                if done_match and f"T{done_match.group(2)}" == tid:
                    done = done_match.group(1) != " "
            if deps_raw is None:
                deps_match = DEPS_LINE_RE.match(stripped)
                if deps_match:
                    deps_raw = deps_match.group(1)
        if done is None:
            avisos.append(f"{AVISO_SEM_CONCLUIDA}: {tid}")
            continue
        parsed.append({"id": tid, "done": done, "deps": parse_deps_value(deps_raw)})

    known_ids = {item["id"] for item in parsed}
    concluidas = sorted((item["id"] for item in parsed if item["done"]), key=task_n)
    abertas = sorted((item["id"] for item in parsed if not item["done"]), key=task_n)
    done_set = set(concluidas)
    elegiveis: list[str] = []
    bloqueadas: list[dict[str, Any]] = []
    for item in sorted((row for row in parsed if not row["done"]), key=lambda row: task_n(row["id"])):
        phantom = [dep for dep in item["deps"] if dep not in known_ids]
        unmet = [dep for dep in item["deps"] if dep not in done_set]
        if phantom:
            avisos.append(f"dep inexistente em {item['id']}: {', '.join(phantom)}")
            bloqueadas.append({"id": item["id"], "deps": item["deps"]})
            continue
        if unmet:
            bloqueadas.append({"id": item["id"], "deps": unmet})
        else:
            elegiveis.append(item["id"])

    return {
        "parse": "parcial" if avisos else "ok",
        "concluidas": concluidas,
        "abertas": abertas,
        "elegiveis": elegiveis,
        "bloqueadas": bloqueadas,
        "avisos": avisos,
    }


# Projeta a fila do plan do alvo. Sem plan.md, a skill avulsa não recebe fila.
def fila_from_alvo(repo: Path, alvo: dict[str, Any] | None) -> dict[str, Any] | None:
    if not alvo:
        return None
    body = read_text(repo / alvo["path"] / "plan.md")
    if body is None:
        return None
    return parse_plan_fila(body)


# Confere snapshots sem executar a prosa do comando; Git e arquivos locais são a evidência mecânica.
def snapshot_valid(repo: Path, value: Any) -> bool:
    if not isinstance(value, dict) or set(value) != {"head", "inputs", "comando", "resultado"}:
        return False
    if value["resultado"] not in ("verde", "falha") or not isinstance(value["comando"], str) or not value["comando"].strip():
        return False
    if not isinstance(value["head"], str) or not re.fullmatch(r"[a-f0-9]{40}|[a-f0-9]{64}", value["head"]):
        return False
    if not isinstance(value["inputs"], dict) or not value["inputs"] or not shutil.which("git"):
        return False
    ancestry = subprocess.run(["git", "merge-base", "--is-ancestor", value["head"], "HEAD"], cwd=repo, capture_output=True, check=False)
    if ancestry.returncode:
        return False
    for relative, expected in value["inputs"].items():
        if not isinstance(relative, str) or "\\" in relative or ":" in relative or not relative or any(part in ("", ".", "..") for part in relative.split("/")):
            return False
        path = Path(relative)
        if path.is_absolute() or path.drive or relative.startswith("-") or not isinstance(expected, str) or not re.fullmatch(r"[a-f0-9]{40}|[a-f0-9]{64}", expected):
            return False
        destination = repo / path
        for candidate in (destination, *destination.parents):
            if candidate == repo:
                break
            if is_reparse_point(candidate):
                return False
        if not destination.is_file():
            return False
        actual = subprocess.run(["git", "hash-object", "--", relative], cwd=repo, capture_output=True, text=True, check=False)
        if actual.returncode or actual.stdout.strip() != expected:
            return False
    return True


# Extrai um único campo JSON operacional, sem interpretar prosa ou aceitar registros duplicados.
def execution_field(lines: list[str], name: str) -> Any:
    prefix = f"- **{name}:** "
    found = [line.strip()[len(prefix):] for line in lines if line.strip().startswith(prefix)]
    if len(found) != 1:
        raise ValueError(f"campo {name} ausente ou duplicado")
    try:
        return json.loads(found[0])
    except json.JSONDecodeError:
        raise ValueError(f"campo {name} JSON inválido") from None


# Localiza o commit integrado real; uma declaração no plan não prova que o Git concluiu a operação.
def integration_commit(repo: Path, tasks: list[str], proof: Any, origin: Any = None) -> str | None:
    if not isinstance(proof, dict) or not shutil.which("git"):
        return None
    origin = origin if origin is not None else proof["head"]
    if not isinstance(origin, str) or not re.fullmatch(r"[a-f0-9]{40}|[a-f0-9]{64}", origin):
        return None
    ancestry = subprocess.run(["git", "merge-base", "--is-ancestor", origin, proof["head"]], cwd=repo, capture_output=True, check=False)
    if ancestry.returncode:
        return None
    result = subprocess.run(["git", "log", "--format=%H %s"], cwd=repo, capture_output=True, text=True, check=False)
    prefix = "task(" + ",".join(tasks) + "): "
    for line in result.stdout.splitlines() if result.returncode == 0 else []:
        sha, _, subject = line.partition(" ")
        if not subject.startswith(prefix) or sha == origin:
            continue
        ancestry = subprocess.run(["git", "merge-base", "--is-ancestor", origin, sha], cwd=repo, capture_output=True, check=False)
        if ancestry.returncode == 0:
            return sha
    return None


# Projeta somente o protocolo explicitamente selecionado; legado e Modo B mantêm a fila anterior.
def execution_from_plan(repo: Path, alvo: dict[str, Any] | None, fila: dict[str, Any] | None) -> dict[str, Any] | None:
    if alvo is None or fila is None:
        return None
    text = read_text(repo / alvo["path"] / "plan.md") or ""
    protocols = re.findall(r"^# Protocolo:\s*(.*?)\s*$", text, re.MULTILINE)
    if not protocols:
        return None
    modes = re.findall(r"^# Modo:\s*(.*?)\s*$", text, re.MULTILINE)
    result: dict[str, Any] = {"protocolo": protocols[0], "modo": modes[0] if modes else None, "tasks": [], "integracao": None, "avisos": []}
    errors = result["avisos"]
    if protocols != ["etapas-v1"] or len(modes) != 1 or modes[0] not in ("A", "B"):
        errors.append("protocolo ou modo de execução inválido")
        return result
    if modes[0] == "B":
        return result
    try:
        sections = split_task_sections(text)
        if not sections or fila["parse"] != "ok":
            raise ValueError("fila incompleta ou inválida")
        known = {tid for tid, _ in sections}
        if len(known) != len(sections):
            raise ValueError("T* duplicada")
        tasks = {}
        for tid, lines in sections:
            deps = [match.group(1) for line in lines if (match := DEPS_LINE_RE.match(line.strip()))]
            done = [match for line in lines if (match := DONE_LINE_RE.match(line.strip())) and f"T{match.group(2)}" == tid]
            if len(deps) != 1 or len(done) != 1 or not re.fullmatch(r"nenhuma|T[1-9]\d*(?:[ ,]+T[1-9]\d*)*", deps[0]):
                raise ValueError(f"conclusão ou Deps inválida: {tid}")
            state = execution_field(lines, "Execução")
            if not isinstance(state, dict) or set(state) != {"estado", "local"} or state["estado"] not in ("pendente", "implementada"):
                raise ValueError(f"registro de execução inválido: {tid}")
            if state["estado"] == "implementada" and not isinstance(state["local"], dict):
                raise ValueError(f"snapshot local ausente: {tid}")
            if state["estado"] == "pendente" and state["local"] is not None:
                raise ValueError(f"snapshot local inesperado: {tid}")
            tasks[tid] = {"id": tid, "estado": state["estado"], "local_valida": snapshot_valid(repo, state["local"]) and state["local"]["resultado"] == "verde", "deps": parse_deps_value(deps[0]), "done": done[0].group(1) != " "}
        # A DFS detecta ciclos mesmo quando uma parte da fila já recebeu prova local.
        visited: set[str] = set()
        active: set[str] = set()
        # Percorre a cadeia desta task e recusa retorno a um nó ativo antes de liberar qualquer dependente.
        def visit(tid: str) -> None:
            if tid in active:
                raise ValueError("ciclo de dependências")
            if tid in visited:
                return
            active.add(tid)
            for dep in tasks[tid]["deps"]:
                if dep not in tasks:
                    raise ValueError(f"dependência inexistente: {dep}")
                visit(dep)
            active.remove(tid)
            visited.add(tid)
        for tid in tasks:
            visit(tid)
        prefix = text.split("## Tasks", 1)[0].splitlines()
        integration = execution_field(prefix, "Integração")
        if not isinstance(integration, dict) or not {"testes", "prova", "commit"} <= set(integration) <= {"testes", "prova", "commit", "origem"} or integration["testes"] not in ("pendentes", "prontos") or integration["commit"] not in ("pendente", "registrado"):
            raise ValueError("registro de integração inválido")
        origin = integration.get("origem")
        if origin is not None and (not isinstance(origin, str) or not re.fullmatch(r"[a-f0-9]{40}|[a-f0-9]{64}", origin)):
            raise ValueError("origem da integração inválida")
        valid = snapshot_valid(repo, integration["prova"])
        ordered = sorted(tasks, key=task_n)
        result["tasks"] = [tasks[tid] for tid in ordered]
        result["integracao"] = {**integration, "prova_valida": valid, "commit_encontrado": integration_commit(repo, ordered, integration["prova"], origin) if valid and integration["commit"] == "registrado" else None}
        ready = {tid for tid, item in tasks.items() if item["done"] or item["estado"] == "implementada" and item["local_valida"]}
        pending = [tid for tid in ordered if tid not in ready]
        fila["elegiveis"] = [tid for tid in pending if all(dep in ready for dep in tasks[tid]["deps"])]
        fila["bloqueadas"] = [{"id": tid, "deps": [dep for dep in tasks[tid]["deps"] if dep not in ready]} for tid in pending if tid not in fila["elegiveis"]]
    except (ValueError, TypeError, KeyError) as error:
        errors.append(str(error))
        fila["elegiveis"] = []
    return result


# Seleciona a próxima etapa nova sem confundir checagem local, prova final e commit efetivo.
def execution_etapa(fila: dict[str, Any], review: dict[str, Any] | None, execution: dict[str, Any]) -> str | None:
    if execution["avisos"]:
        return None
    if execution["modo"] == "B":
        return derive_etapa(fila, review)
    if review is not None and not review["legivel"]:
        return None
    if review is not None and review["bloqueios_abertos"]:
        return "corrigir"
    if any(not item["done"] and (item["estado"] != "implementada" or not item["local_valida"]) for item in execution["tasks"]):
        return "implementar" if fila["elegiveis"] else "bloqueada"
    integration = execution["integracao"]
    if integration["testes"] != "prontos":
        return "testar"
    if not integration["prova_valida"]:
        return "validar"
    if integration["prova"]["resultado"] != "verde":
        return "corrigir_validacao"
    if not integration["commit_encontrado"] or fila["abertas"]:
        return "commitar_integracao"
    return derive_etapa(fila, review)


# Conta as correções já aplicadas. Cada etapa com veredito Request changes soma 1; a última não conta
# enquanto houver Critical ou Required em [ ], porque a correção que ela pediu ainda está pendente.
def count_correction_rounds(lines: list[str], blockers_open: bool) -> int:
    verdicts: list[str | None] = []
    in_etapas = False
    for line in lines:
        if ETAPA_HEADING_RE.match(line):
            verdicts.append(None)
            in_etapas = True
        elif line.startswith("## "):
            in_etapas = False
        elif in_etapas and verdicts[-1] is None:
            verdict = ETAPA_VERDICT_RE.match(line)
            if verdict:
                verdicts[-1] = verdict.group(1)
    rounds = sum(1 for verdict in verdicts if verdict is not None and REQUEST_CHANGES_RE.match(verdict))
    if verdicts and verdicts[-1] is not None and REQUEST_CHANGES_RE.match(verdicts[-1]) and blockers_open:
        rounds -= 1
    return rounds


# Indica se o Veredito vigente tem Approve ou Approve com defer marcado; a lista de alternativas do template não conta.
def approval_marked(lines: list[str]) -> bool:
    in_section = False
    for line in lines:
        if VEREDITO_VIGENTE_RE.match(line):
            in_section = True
        elif line.startswith("## "):
            in_section = False
        elif in_section and APPROVE_MARK_RE.match(line):
            return True
    return False


# Lê as marcas do review.md do alvo. Arquivo ausente devolve None; ilegível ou sem Status vira aviso e
# legivel=False, para a etapa não ser inventada.
def read_review(repo: Path, alvo: dict[str, Any] | None, warnings: list[str]) -> dict[str, Any] | None:
    if not alvo:
        return None
    path = repo / alvo["path"] / "review.md"
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        warnings.append("review.md ilegível: etapa não derivada")
        return {"legivel": False, "status": None, "bloqueios_abertos": False, "aprovacao_marcada": False, "rodadas": 0}
    lines = text.splitlines()
    status_match = REVIEW_STATUS_RE.search(text)
    if status_match is None:
        warnings.append("review.md sem '# Status:': etapa não derivada")
    blockers_open = any(OPEN_BLOCKER_RE.match(line) for line in lines)
    return {
        "legivel": status_match is not None,
        "status": status_match.group(1).lower() if status_match else None,
        "bloqueios_abertos": blockers_open,
        "aprovacao_marcada": approval_marked(lines),
        "rodadas": count_correction_rounds(lines, blockers_open),
    }


# Deriva a etapa da phase só de plan e review, na precedência do contrato. Sem fila legível ou com review
# ilegível devolve None: o coordenador não recebe um chute no lugar de um estado indeterminado.
def derive_etapa(fila: dict[str, Any] | None, review: dict[str, Any] | None) -> str | None:
    if fila is None or fila["parse"] == "ausente":
        return None
    if any(aviso.startswith(AVISO_SEM_CONCLUIDA) for aviso in fila["avisos"]):
        return None
    if review is not None:
        if not review["legivel"]:
            return None
        if review["status"] == "aprovado":
            return "concluida"
        if review["bloqueios_abertos"]:
            return "corrigir"
    if not fila["abertas"]:
        return "confirmar" if review is not None and review["aprovacao_marcada"] else "revisar"
    return "implementar" if fila["elegiveis"] else "bloqueada"


# Resolve --dir explícito ou seleciona a fase mais recente que possui plan.md.
def resolve_alvo_com_dir(
    existing: list[dict[str, Any]],
    dir_arg: str | None,
    phases: Path,
) -> dict[str, Any] | None:
    if dir_arg:
        dest = phases / Path(dir_arg).name
        if is_reparse_point(dest) or not dest.is_dir() or not PHASE_RE.fullmatch(dest.name):
            raise RuntimeError(
                f"FASE_AUSENTE: .vibeflow/phases/{dest.name} não é uma pasta de fase."
            )
        found = next((item for item in existing if item["dir"] == dest.name), None)
        item = found if found is not None else phase_item(dest)
        return item
    return resolve_alvo(existing)


# Expõe só identificadores do alvo, sem serializar o inventário de fases.
def public_target(item: dict[str, Any] | None) -> dict[str, Any] | None:
    if item is None:
        return None
    return {key: item[key] for key in ("kind", "dir", "n", "slug", "path") if key in item}


# Serializa alvo, fila, etapa da phase, rodadas de correção e avisos necessários para a execução imediata.
def emit_report(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


# Seleciona alvo e fila; Apply só cria uma phase quando há slug explícito.
def run(args: argparse.Namespace) -> None:
    if args.mvp and (args.slug is not None or args.dir is not None):
        raise RuntimeError("MODO_INVALIDO: o alvo MVP não aceita --slug nem --dir.")

    repo = repo_root(args.root)
    vf = repo / ".vibeflow"
    phases = vf / "phases"
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
        ph_state = "ok"

    existing, warnings = list_phases(phases)
    next_n = (existing[-1]["n"] + 1) if existing else 1
    alvo = resolve_alvo_com_dir(existing, args.dir, phases)
    mvp = get_mvp(vf)
    if args.mvp and (mvp is None or "plan.md" not in mvp["files"]):
        raise RuntimeError("IMPLEMENT_SEM_PLAN: falta .vibeflow/mvp/plan.md.")
    if args.mvp:
        alvo = mvp
    gate = analyze_gate(vf / "mvp" / "analyze.md") if args.mvp else None

    if args.apply:
        if args.mvp:
            if gate["status"] == "ausente" and gate["veredito"] == "ausente":
                raise RuntimeError("IMPLEMENT_ANALYZE_AUSENTE: falta .vibeflow/mvp/analyze.md.")
            if gate["status"] != "aprovado":
                raise RuntimeError("IMPLEMENT_ANALYZE_RASCUNHO: analyze MVP não está aprovado.")
            if gate["veredito"] != "limpo":
                raise RuntimeError("IMPLEMENT_ANALYZE_BLOQUEADO: analyze MVP não está limpo.")
        if not args.mvp and not args.dir and alvo is None:
            if not (args.slug or "").strip():
                raise RuntimeError(
                    "IMPLEMENT_SEM_ALVO: sem fase alvo; passe --slug para abrir uma pasta nova."
                )
            slug = sanitize_slug(args.slug or "")
            if len(slug) < 2:
                raise RuntimeError("SLUG_INVALIDO: a frase curta não gerou um slug utilizável.")
            dest_dir = phases / f"phase-{next_n}-{slug}"
            if is_reparse_point(dest_dir) or dest_dir.exists():
                raise RuntimeError(f"FASE_EXISTE: .vibeflow/phases/{dest_dir.name} já existe.")
            dest_dir.mkdir(parents=True)
            alvo = phase_item(dest_dir)

    fila = fila_from_alvo(repo, alvo)
    review = read_review(repo, alvo, warnings)
    execution = execution_from_plan(repo, alvo, fila)
    payload = {
        "alvo": public_target(alvo),
        "fila": fila,
        "etapa": execution_etapa(fila, review, execution) if execution is not None else derive_etapa(fila, review),
        "rodadas_correcao": review["rodadas"] if review else 0,
        "avisos": warnings,
    }
    if execution is not None:
        payload["execucao"] = execution
    if args.mvp:
        payload["analyze_gate"] = gate
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
