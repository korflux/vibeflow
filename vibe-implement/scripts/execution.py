"""Estado mecânico de coordenacao-v1; chamado pelo motor, sem executar evidências."""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

PROTOCOL = "coordenacao-v1"
MAX_BYTES = 1048576
HASH = r"[a-f0-9]{40}|[a-f0-9]{64}"


# Falhas do sidecar têm código estável e não permitem fallback para checkboxes.
def fail(message):
    raise ValueError("EXECUTION_INVALIDO: " + message)


# Recusa ambiguidade JSON antes de aplicar o schema estrito.
def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            fail("chave duplicada")
        result[key] = value
    return result


# Protege cada componente, inclusive links quebrados, antes de ler ou substituir.
def safe_path(repo, relative, reparse):
    if (not isinstance(relative, str) or not 0 < len(relative) <= 512
            or "\\" in relative or ":" in relative or relative.startswith(("/", "-"))
            or any(ord(char) < 32 for char in relative)
            or any(part.lower() in ("", ".", "..", ".git") or part.endswith((".", " "))
                   or re.fullmatch(r"(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", part)
                   for part in relative.split("/"))):
        fail("path inválido")
    path = repo
    for part in relative.split("/"):
        path = path / part
        if reparse(path):
            fail("link/reparse point")
    return path


# Mantém comandos Git constantes: strings de evidência nunca entram no processo.
def git(repo, *args):
    process = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, encoding="utf-8", check=False)
    if process.returncode:
        fail("Git não comprovou a operação")
    return process.stdout.strip()


# Valida formatos sem misturar corrupção com invalidação normal de arquivos alterados.
def proof_schema(proof, repo, reparse, target):
    if not isinstance(proof, dict) or set(proof) != {"head", "inputs", "comando", "resultado"}:
        fail("snapshot inválido")
    if not isinstance(proof["head"], str) or not re.fullmatch(HASH, proof["head"]):
        fail("HEAD inválido")
    if proof["resultado"] not in ("verde", "falha") or not isinstance(proof["comando"], str) or not 0 < len(proof["comando"].strip()) <= 2048:
        fail("resultado/comando inválido")
    if not isinstance(proof["inputs"], dict) or not 1 <= len(proof["inputs"]) <= 256:
        fail("inputs inválidos")
    for relative, hashed in proof["inputs"].items():
        safe_path(repo, relative, reparse)
        if relative.lower() in {target.lower() + "/" + name for name in ("plan.md", "spec.md", "review.md", "execution.json")}:
            fail("artefato operacional não é input")
        if not isinstance(hashed, str) or not re.fullmatch(HASH, hashed):
            fail("hash inválido")


# Um grafo inválido jamais libera tarefas, mesmo se checkboxes estiverem marcados.
def task_graph(text, split, deps_parser):
    tasks = {}
    sections = split(text)
    if not 1 <= len(sections) <= 500:
        fail("quantidade de tasks inválida")
    for tid, lines in sections:
        deps = [m.group(1) for line in lines if (m := re.fullmatch(r"- \*\*Deps:\*\*\s*(.*)", line.strip()))]
        if tid in tasks or not re.fullmatch(r"T[1-9]\d*", tid) or len(deps) != 1 or not re.fullmatch(r"nenhuma|T[1-9]\d*(?:[ ,]+T[1-9]\d*)*", deps[0]):
            fail("task/Deps inválida")
        tasks[tid] = deps_parser(deps[0])
    visited, active = set(), set()
    # Percorre dependências para recusar ciclos e referências inexistentes.
    def visit(tid):
        if tid not in tasks or tid in active:
            fail("dependência inexistente ou ciclo")
        if tid in visited:
            return
        active.add(tid)
        for dep in tasks[tid]:
            visit(dep)
        active.remove(tid)
        visited.add(tid)
    for tid in tasks:
        visit(tid)
    return tasks


# Registra executor distinto do escritor para certificação independente da integração.
def actor_valid(value):
    return isinstance(value, str) and re.fullmatch(r"[a-zA-Z0-9_.-]{1,64}", value) is not None


# Sidecar atual tem uma fonte por fato; histórico continua no Git.
def load(path, graph, repo, reparse, target):
    empty = {"schema": 1, "protocolo": PROTOCOL, "tasks": {}, "integracao": None, "commit": None}
    if not path.exists():
        return empty
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        fail("arquivo/tamanho inválido")
    try:
        state = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_object)
    except (UnicodeError, json.JSONDecodeError, RecursionError):
        fail("JSON/encoding inválido")
    if not isinstance(state, dict) or set(state) not in (set(empty), set(empty) | {"correcao"}) or type(state["schema"]) is not int or state["schema"] != 1 or state["protocolo"] != PROTOCOL or not isinstance(state["tasks"], dict):
        fail("schema inválido")
    for tid, row in state["tasks"].items():
        if tid not in graph or not isinstance(row, dict) or set(row) != {"actor", "proof"} or not actor_valid(row["actor"]):
            fail("task registrada inválida")
        proof_schema(row["proof"], repo, reparse, target)
    integration = state["integracao"]
    if integration is not None:
        if not isinstance(integration, dict) or set(integration) != {"actor", "proof", "origem"} or not actor_valid(integration["actor"]) or not isinstance(integration["origem"], str) or not re.fullmatch(HASH, integration["origem"]):
            fail("integração inválida")
        proof_schema(integration["proof"], repo, reparse, target)
        if set(state["tasks"]) != set(graph) or integration["actor"] in {row["actor"] for row in state["tasks"].values()}:
            fail("integração sem independência")
    if state["commit"] is not None and (integration is None or not isinstance(state["commit"], str) or not re.fullmatch(HASH, state["commit"])):
        fail("commit inválido")
    if "correcao" in state:
        correction = state["correcao"]
        if (state["commit"] is None or not isinstance(correction, dict) or set(correction) != {"base", "commit"}
                or correction["commit"] is not None and (not isinstance(correction["commit"], str) or not re.fullmatch(HASH, correction["commit"]))):
            fail("correção inválida")
        proof_schema(correction["base"], repo, reparse, target)
        if correction["base"]["resultado"] != "verde":
            fail("base da correção não é verde")
    return state


# Captura HEAD/hashes dos arquivos reais após checagem executada pelo responsável.
def capture(repo, args, reparse, target):
    inputs = args.input or []
    if not 1 <= len(inputs) <= 256 or len(set(inputs)) != len(inputs):
        fail("inputs ausentes/duplicados")
    proof = {"head": git(repo, "rev-parse", "HEAD"), "inputs": {}, "comando": args.command, "resultado": args.result}
    for relative in inputs:
        path = safe_path(repo, relative, reparse)
        if not path.is_file():
            fail("input não é arquivo")
        proof["inputs"][relative] = git(repo, "hash-object", "--", relative)
    proof_schema(proof, repo, reparse, target)
    return proof


# Não confunde declaração com commit: exige descendência, título e blobs provados.
def commit_matches(repo, sha, tasks, integration):
    try:
        subject = git(repo, "show", "-s", "--format=%s", sha)
        if not subject.startswith("task(" + ",".join(tasks) + "): ") or sha == integration["origem"]:
            return False
        git(repo, "merge-base", "--is-ancestor", integration["origem"], sha)
        git(repo, "merge-base", "--is-ancestor", sha, "HEAD")
        return all(git(repo, "rev-parse", sha + ":" + relative) == hashed for relative, hashed in integration["proof"]["inputs"].items())
    except ValueError:
        return False


# Separa a integração histórica T* dos blobs atuais de uma correção R* real.
def correction_matches(repo, sha, tasks, state, correction_ids):
    correction = state["correcao"]
    baseline = {"origem": state["integracao"]["origem"], "proof": correction["base"]}
    if not commit_matches(repo, state["commit"], tasks, baseline):
        return False
    try:
        subject = git(repo, "show", "-s", "--format=%s", sha)
        match = re.fullmatch(r"task\((R[1-9]\d*(?:,R[1-9]\d*)*)\): .+", subject)
        ids = match.group(1).split(",") if match else []
        if not ids or ids != sorted(set(ids), key=lambda rid: int(rid[1:])) or not set(ids) <= correction_ids or sha == state["commit"]:
            return False
        git(repo, "merge-base", "--is-ancestor", state["commit"], sha)
        git(repo, "merge-base", "--is-ancestor", sha, "HEAD")
        return all(git(repo, "rev-parse", sha + ":" + relative) == hashed for relative, hashed in state["integracao"]["proof"]["inputs"].items())
    except ValueError:
        return False


# Troca atômica no mesmo diretório; falha nunca trunca a evidência existente.
def save(path, state):
    data = json.dumps(state, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
    if len(data) > MAX_BYTES:
        fail("limite do registro")
    descriptor, temporary = tempfile.mkstemp(prefix=".execution-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


# Projeta fila/etapa exclusivamente dos snapshots atuais e do Git real.
def coordinate(repo, target, text, args, fila, review, split, deps_parser, reparse, snapshot_valid, derive):
    graph = task_graph(text, split, deps_parser)
    path = safe_path(repo, target + "/execution.json", reparse)
    state = load(path, graph, repo, reparse, target)
    ordered = sorted(graph, key=lambda tid: int(tid[1:]))
    review_path = safe_path(repo, target + "/review.md", reparse)
    # Reconhece os mesmos R* abertos/fechados da fila, inclusive classificações históricas.
    correction_ids = set(re.findall(r"(?m)^\s*- \[[ xX]\] (R[1-9]\d*):", review_path.read_text(encoding="utf-8-sig"))) if review is not None and review["legivel"] and review_path.is_file() else set()
    # Invalidação é projetada, sem apagar a evidência ou modificar arquivo na leitura.
    def projection():
        ready = {tid for tid, row in state["tasks"].items() if snapshot_valid(repo, row["proof"]) and row["proof"]["resultado"] == "verde"}
        integration = state["integracao"]
        covered = integration is not None and set().union(*(row["proof"]["inputs"] for row in state["tasks"].values())) <= set(integration["proof"]["inputs"])
        valid = covered and ready == set(graph) and snapshot_valid(repo, integration["proof"])
        commit_valid = (bool(state["correcao"]["commit"] and correction_matches(repo, state["correcao"]["commit"], ordered, state, correction_ids))
                        if "correcao" in state else bool(state["commit"] and commit_matches(repo, state["commit"], ordered, integration))) if integration else False
        committed = bool(valid and integration["proof"]["resultado"] == "verde" and commit_valid)
        return ready, valid, committed
    ready, valid, committed = projection()
    operation = args.operation
    if operation:
        if args.details or not re.search(r"^# Status:\s*aprovado\s*$", text, re.MULTILINE):
            fail("mutação exige plan aprovado e sem details")
        if not actor_valid(args.actor):
            fail("executor inválido")
        proof_args = bool(args.input or args.command or args.result)
        if operation in ("init", "commit") and (args.task or proof_args):
            fail("campos fora da operação")
        if operation == "init":
            pass
        elif operation == "local":
            if args.task not in graph or any(dep not in ready for dep in graph[args.task]):
                fail("task não elegível")
            state["tasks"][args.task] = {"actor": args.actor, "proof": capture(repo, args, reparse, target)}
            # Mudança de escritor torna a certificação anterior inválida, sem perder origem.
            if state["integracao"] and state["integracao"]["actor"] == args.actor:
                fail("escritor não pode ser verificador")
        elif operation == "integracao":
            if args.task or ready != set(graph) or args.actor in {row["actor"] for row in state["tasks"].values()}:
                fail("integração exige locais verdes e executor independente")
            proof = capture(repo, args, reparse, target)
            if not set().union(*(row["proof"]["inputs"] for row in state["tasks"].values())) <= set(proof["inputs"]):
                fail("integração não cobre inputs locais")
            origin = state["integracao"]["origem"] if state["integracao"] else proof["head"]
            if ("correcao" not in state and state["commit"] and proof["inputs"] != state["integracao"]["proof"]["inputs"]
                    and commit_matches(repo, state["commit"], ordered, state["integracao"])):
                state["correcao"] = {"base": state["integracao"]["proof"], "commit": None}
            state["integracao"] = {"actor": args.actor, "proof": proof, "origem": origin}
        elif operation == "commit":
            if not valid or state["integracao"]["proof"]["resultado"] != "verde":
                fail("commit exige integração verde atual")
            sha = next((sha for sha in git(repo, "log", "--format=%H").splitlines()
                        if (correction_matches(repo, sha, ordered, state, correction_ids) if "correcao" in state
                            else commit_matches(repo, sha, ordered, state["integracao"]))), None)
            if sha is None:
                fail("commit integrado não encontrado")
            if "correcao" in state:
                state["correcao"]["commit"] = sha
            else:
                state["commit"] = sha
        if operation != "init" or not path.exists():
            save(path, state)
        ready, valid, committed = projection()
    pending = [tid for tid in ordered if tid not in ready]
    fila.update(parse="ok", concluidas=ordered if committed else [], abertas=[] if committed else ordered,
                elegiveis=[tid for tid in pending if all(dep in ready for dep in graph[tid])],
                bloqueadas=[{"id": tid, "deps": [dep for dep in graph[tid] if dep not in ready]} for tid in pending if any(dep not in ready for dep in graph[tid])], avisos=[])
    if pending:
        stage = "implementar" if fila["elegiveis"] else "bloqueada"
    elif not valid:
        stage = "validar"
    elif state["integracao"]["proof"]["resultado"] != "verde":
        stage = "corrigir_validacao"
    elif not committed:
        stage = "commitar_integracao"
    else:
        stage = derive(fila, review)
    if review is not None and not review["legivel"]:
        stage = None
    elif review is not None and review["bloqueios_abertos"]:
        stage = "corrigir"
    current_commit = state["correcao"]["commit"] if "correcao" in state else state["commit"]
    summary = {"protocolo": PROTOCOL, "modo": "A", "registro": target + "/execution.json", "tasks": [{"id": tid, "local_valida": tid in ready} for tid in ordered], "integracao": {"prova_valida": valid, "commit_encontrado": current_commit if committed else None}, "avisos": []}
    if args.details:
        summary["detalhes"] = state
    return summary, stage
