#!/usr/bin/env python3
"""Execução piloto do Modo A do vibe-implement e das portas delegadas, num repo descartável.

O que este script faz
    Cria fixtures Git descartáveis fora do repo, roda `claude -p` contra uma CÓPIA do plugin
    (nunca contra o repo real) e confere, no disco da fixture, os efeitos que a spec da phase 14
    exige: commits `task(Tn)`, review em subagente, no máximo 2 rodadas de correção, uma única
    pergunta ao humano, push no remoto local, retomada pela etapa do motor e Modo B.

Rodadas (`--rounds`)
    0  analyze delegado no chat do plan (A1 e A2): plan aprovado, sem analyze.md, achado plantado.
    1  piloto completo (A3 a A6 e A10): `/vibe-implement` até a pergunta final, depois confirmação
       na mesma sessão e push.
    2  retomada (A7): execução interrompida após a primeira T* e retomada em sessão nova.
    3  Modo B (A8): pedido explícito de uma T* por vez conclui só uma T*.

Limites conhecidos (não é teste de CI)
    * Não é determinístico e consome tokens da conta do humano: cada chamada tem teto
      `--budget-usd`. Não entra no CI.
    * O modo de permissão do `claude -p` não confina o agente à pasta temporária. O padrão é
      `acceptEdits` (edições só no diretório de trabalho e no `--add-dir`) com `--allowedTools`
      para Git, Python e o python da venv. `python` e `git` aceitam comandos arbitrários, então
      rode apenas numa máquina em que isso seja aceitável.
    * Testes de skill não verificam texto de SKILL.md: este script confere só efeitos no disco da
      fixture e o transcript como evidência. Falha por comportamento da skill volta para a T3 ou
      a T4 como correção, não para este script.

Uso
    python docs/vibe-implement/tests/piloto-modo-a.py --prepare-only      # valida fixtures, sem tokens
    python docs/vibe-implement/tests/piloto-modo-a.py --rounds 3          # só o Modo B
    python docs/vibe-implement/tests/piloto-modo-a.py --rounds 0,1,2,3
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
IS_WINDOWS = sys.platform == "win32"
POLL_SECONDS = 2
PHASE_DIR = ".vibeflow/phases/phase-1-textkit"
# Python da venv da fixture em sintaxe POSIX, a que o Bash do agente enxerga em qualquer sistema.
VENV_PYTHON = ".venv/Scripts/python" if IS_WINDOWS else ".venv/bin/python"
# Ferramentas que o piloto libera. Edições ficam por conta do `acceptEdits`, que as restringe ao cwd.
ALLOWED_TOOLS = (
    "Read", "Glob", "Grep", "Skill", "Task", "Agent", "TodoWrite",
    "Bash(git *)", "Bash(python *)", "Bash(python3 *)", f"Bash({VENV_PYTHON} *)", f"Bash(./{VENV_PYTHON} *)",
    "Bash(ls *)", "Bash(cat *)", "Bash(rg *)", "Bash(grep *)", "Bash(wc *)", "Bash(head *)", "Bash(tail *)",
)


# ============================ Resultado das conferências ============================


@dataclass
class Report:
    """Acumula as conferências de uma rodada, com o detalhe que explica cada falha."""

    name: str
    checks: list[tuple[bool, str, str]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    # Registra uma conferência; devolve o resultado para permitir encadear decisões.
    def check(self, ok: bool, label: str, detail: str = "") -> bool:
        self.checks.append((bool(ok), label, detail))
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" ({detail})" if detail and not ok else ""), flush=True)
        return bool(ok)

    # Guarda uma observação de evidência que não é conferência (custo, trechos do transcript).
    def note(self, text: str) -> None:
        self.notes.append(text)

    @property
    def passed(self) -> bool:
        return all(ok for ok, _, _ in self.checks)


# ============================ Fixture descartável ============================


@dataclass
class Fixture:
    """Pasta de uma rodada: o repo de trabalho, o remoto bare local e a cópia do plugin."""

    root: Path
    work: Path
    remote: Path
    plugin: Path
    baseline: str


# Remove uma árvore apagando o atributo read-only que o Git cria no Windows; outra falha propaga.
def remove_tree(path: Path) -> None:
    def retry_writable(operation, filename, error) -> None:
        os.chmod(filename, stat.S_IWRITE)
        operation(filename)

    shutil.rmtree(path, onerror=retry_writable)


# Executa Git em `cwd` sem shell; falha vira exceção com a saída, pois a fixture não pode ficar meio criada.
def git(cwd: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", check=False)
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} falhou: {result.stderr.strip()}")
    return result.stdout.strip()


# Copia só o que o plugin precisa (manifest e pacotes das skills), sem cache, para o agente nunca tocar o repo real.
def snapshot_plugin(dest: Path) -> None:
    dest.mkdir(parents=True)
    shutil.copytree(REPO / ".claude-plugin", dest / ".claude-plugin")
    for package in sorted(REPO.glob("vibe-*")):
        shutil.copytree(package, dest / package.name, ignore=shutil.ignore_patterns("__pycache__"))


# Conteúdo do projeto textkit: o defeito está em `normalize`, que só colapsa pares exatos de espaços.
def project_files() -> dict[str, str]:
    return {
        "AGENTS.md": (
            "# Regras do projeto textkit (fixture do piloto)\n\n"
            "## Ambiente\n\nhomolog. Sem banco nem tráfego de usuário.\n\n"
            "## Comandos\n\n"
            f"- Testes: `{VENV_PYTHON} -m pytest -q`.\n"
            "- Neste ambiente os motores das skills vibe rodam com `python <skill>/scripts/<nome>.py --root .`.\n\n"
            "## Git\n\n- Sem `Co-Authored-By` em commit.\n- Commit de task: `task(Tn): <outcome curto>`.\n"
        ),
        ".gitignore": ".venv/\n__pycache__/\n.pytest_cache/\n.vibeflow/*-report.json\n.vibeflow/*-pending.json\n",
        "requirements-dev.txt": "pytest\n",
        "textkit/__init__.py": '"""Utilitários de texto."""\n',
        "textkit/normalize.py": (
            '"""Normalização de texto compartilhada pelos utilitários."""\n\n'
            "import re\n\n\n"
            "def normalize(text: str) -> str:\n"
            '    """Devolve o texto em minúsculas, sem bordas e com espaços internos colapsados."""\n'
            '    return re.sub(r" {2}", " ", text.strip().lower())\n'
        ),
        "tests/test_normalize.py": (
            "from textkit.normalize import normalize\n\n\n"
            "def test_normalize_minusculas_e_sem_bordas():\n"
            '    assert normalize("  Olá Mundo  ") == "olá mundo"\n\n\n'
            "def test_normalize_colapsa_espaco_duplo():\n"
            '    assert normalize("a  b") == "a b"\n'
        ),
        "tests/test_stats.py": (
            "from textkit.stats import word_count\n\n\n"
            "def test_conta_palavras_separadas_por_qualquer_espaco():\n"
            '    assert word_count("um  dois\\tTres\\nquatro") == 4\n\n\n'
            "def test_vazio_ou_so_espacos_retorna_zero():\n"
            '    assert word_count("") == 0\n'
            '    assert word_count("   \\n\\t ") == 0\n'
        ),
        "tests/test_slug.py": (
            "from textkit.slug import slugify\n\n\n"
            "def test_slug_sem_acento_e_com_um_hifen():\n"
            '    assert slugify("Olá Mundo Bonito") == "ola-mundo-bonito"\n\n\n'
            "def test_slug_com_espacos_repetidos_gera_um_unico_hifen():\n"
            '    assert slugify("  Olá   Mundo    Bonito ") == "ola-mundo-bonito"\n'
        ),
        "tests/test_report.py": (
            "from textkit.report import summarize\n\n\n"
            "def test_summarize_combina_contagem_e_slug():\n"
            '    assert summarize("Olá   Mundo Bonito") == {"words": 3, "slug": "ola-mundo-bonito"}\n'
        ),
    }


SPEC = """# Spec: Utilitários de texto
# Alvo: phase-1-textkit
# Status: aprovado

## Objetivo

Biblioteca `textkit` com contagem de palavras, slug e resumo de texto.

## Suposições e decisões

1. Sem decisão crítica transversal nesta entrega. (processo)

## Escopo e comportamento

### 1. Fluxo F1: utilitários de texto

- Jornada: chamar `word_count`, `slugify` e `summarize` sobre um texto.
- Superfície por passo: N/A, biblioteca sem UI.
- Aceite: A1, A2, A3.

### Fora

- Interface de linha de comando e persistência.

## Checklist de entrega

### Aceite

- [ ] A1: `word_count(text)` conta palavras separadas por qualquer espaço em branco; texto vazio ou só espaços retorna 0.
- [ ] A2: `slugify(text)` devolve minúsculas, sem acento, com palavras separadas por um único hífen, mesmo com espaços repetidos.
- [ ] A3: `summarize(text)` devolve `{"words": n, "slug": s}` usando A1 e A2.

### Critérios de sucesso

- [ ] C1: a suíte completa `pytest -q` passa.

## Handoff

vibe-plan
rota: max

- Design: N/A, a entrega não tem UI visível.

- [x] Aprovação humana (leu o arquivo e confirmou)
"""


# Monta o plan aprovado. `plant_finding` remove A3 do campo Spec da T3: achado determinístico que o analyze deve corrigir.
def plan_text(plant_finding: bool) -> str:
    py = VENV_PYTHON
    t3_spec = "C1" if plant_finding else "A3, C1"
    return f"""# Plan: Utilitários de texto
# Alvo: phase-1-textkit
# Status: aprovado
# Spec: spec.md (mesma pasta)

## Overview

Entrega `word_count`, `slugify` e `summarize` em `textkit`, conforme `spec.md`.
- **Design:** N/A, sem UI visível.

## Prontidão das provas

- **Requisitos verificados:** Python 3 local; `pytest` no venv `.venv` do projeto.
- **Ausências e ação na fila:** `pytest` ausente no venv; instalar com `{py} -m pip install -r requirements-dev.txt` na T1, a primeira T* que depende dele.

## Tasks

### T1: Contar palavras em textkit.stats

- [ ] T1 concluída
- **Spec:** A1
- **O quê:** `textkit/stats.py` com `word_count(text)`.
- **Aceite:**
  - [ ] Conta palavras separadas por qualquer espaço em branco; vazio ou só espaços retorna 0.
- **Verificação:**
  - [ ] `{py} -m pytest -q tests/test_stats.py`
- **Deps:** nenhuma
- **Arquivos:** `textkit/stats.py`

### T2: Gerar slug em textkit.slug

- [ ] T2 concluída
- **Spec:** A2
- **O quê:** `textkit/slug.py` com `slugify(text)`, reutilizando a normalização compartilhada.
- **Aceite:**
  - [ ] Minúsculas, sem acento e um único hífen entre palavras, mesmo com espaços repetidos.
- **Verificação:**
  - [ ] `{py} -m pytest -q tests/test_slug.py`
- **Deps:** nenhuma
- **Arquivos:** `textkit/slug.py`

### T3: Resumir texto em textkit.report

- [ ] T3 concluída
- **Spec:** {t3_spec}
- **O quê:** `textkit/report.py` com `summarize(text)` usando `word_count` e `slugify`.
- **Aceite:**
  - [ ] Devolve `{{"words": n, "slug": s}}`; a suíte completa passa.
- **Verificação:**
  - [ ] `{py} -m pytest -q`
- **Deps:** T1, T2
- **Arquivos:** `textkit/report.py`

## Handoff

vibe-analyze
rota: max

- Chat: recomende novo chat para a próxima porta; continuar aqui é válido se o humano preferir.
"""


ANALYZE = """# Analyze: Utilitários de texto
# Alvo: phase-1-textkit
# Status: aprovado
# Plan: plan.md (mesma pasta)

## Fontes

| Arquivo | Estado |
|---|---|
| interview.md | ausente |
| spec.md | presente |
| plan.md | presente |
| AGENTS.md | lido |

## Cobertura e Rastreabilidade

| Chave | Origem | T* | Notas |
|---|---|---|---|
| A1 | spec.md | T1 | word_count |
| A2 | spec.md | T2 | slugify |
| A3 | spec.md | T3 | summarize |
| C1 | spec.md | T3 | suíte completa |

## Achados e Resoluções

Nenhum achado.

## Métricas

- A*/C* na spec: 4
- T* no plan: 3
- Cobertura (A*/C* com >= 1 T*): 4 / 4
- Qualidade de Testes: todas as T* têm comando executável; pytest ausente no venv e instalação planejada na T1
- Achados corrigidos / resolvidos: 0
- Achados bloqueantes pendentes: 0

## Veredito

limpo

## Handoff

vibe-implement
rota: max

- [x] Aprovação humana (leu o arquivo e confirmou)
"""


# Cria a fixture completa: projeto com defeito, phase max, venv sem pytest, repo Git e remoto bare local.
def build_fixture(parent: Path, name: str, *, with_analyze: bool, plant_finding: bool) -> Fixture:
    root = parent / name
    work = root / "work"
    remote = root / "remote.git"
    plugin = root / "plugin"
    work.mkdir(parents=True)

    files = project_files()
    files[f"{PHASE_DIR}/spec.md"] = SPEC
    files[f"{PHASE_DIR}/plan.md"] = plan_text(plant_finding)
    if with_analyze:
        files[f"{PHASE_DIR}/analyze.md"] = ANALYZE
    for relative, content in files.items():
        target = work / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")

    # A venv nasce sem pytest, de propósito: o requisito de prova ausente que o piloto precisa instalar.
    subprocess.run([sys.executable, "-m", "venv", str(work / ".venv")], check=True, capture_output=True)

    git(work, "init", "-q", "-b", "main")
    for key, value in (("user.name", "Piloto VibeFlow"), ("user.email", "piloto@example.invalid"), ("core.autocrlf", "false")):
        git(work, "config", key, value)
    git(work, "add", "--", ".")
    git(work, "commit", "-q", "-m", "fixture: baseline")
    git(root, "init", "-q", "--bare", "-b", "main", str(remote))
    git(work, "remote", "add", "origin", str(remote))
    git(work, "push", "-q", "-u", "origin", "main")
    snapshot_plugin(plugin)
    return Fixture(root, work, remote, plugin, git(work, "rev-parse", "HEAD"))


# ============================ Leitura do estado da fixture ============================


# Roda o motor do implement da cópia do plugin contra a fixture e devolve o JSON (etapa, fila, rodadas).
def engine_state(fx: Fixture) -> dict:
    script = fx.plugin / "vibe-implement" / "scripts" / "implement.py"
    result = subprocess.run(
        [sys.executable, str(script), "--root", str(fx.work)],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"motor do implement falhou: {result.stderr.strip()}")
    return json.loads(result.stdout)


# Lista os commits novos da fixture como (hash, assunto), do mais antigo ao mais recente.
def new_commits(fx: Fixture) -> list[tuple[str, str]]:
    out = git(fx.work, "log", "--reverse", "--format=%H%x09%s", f"{fx.baseline}..HEAD", check=False)
    return [tuple(line.split("\t", 1)) for line in out.splitlines() if line]  # type: ignore[misc]


# Assuntos dos commits `task(Tn)` ou `task(Rn)` criados depois do baseline.
def task_subjects(fx: Fixture, prefix: str = "task(") -> list[str]:
    return [subject for _, subject in new_commits(fx) if subject.startswith(prefix)]


# Verdadeiro quando já existe um commit `task(<task>)` na fixture; usado para interromper a rodada 2.
def has_task_commit(fx: Fixture, task: str) -> bool:
    return any(subject.startswith(f"task({task})") for subject in task_subjects(fx))


# Lê o plan.md vivo da fixture.
def plan_of(fx: Fixture) -> str:
    return (fx.work / PHASE_DIR / "plan.md").read_text(encoding="utf-8")


# Corpo da seção de uma T* no plan.md (do cabeçalho `### Tn:` ao próximo).
def task_section(plan: str, task: str) -> str:
    match = re.search(rf"^### {task}:.*?(?=^### T\d+:|^## |\Z)", plan, re.MULTILINE | re.DOTALL)
    return match.group(0) if match else ""


# Verdadeiro quando `normalize` colapsa três espaços: o defeito da fixture está corrigido na origem.
def normalize_is_fixed(fx: Fixture) -> bool:
    probe = "from textkit.normalize import normalize; raise SystemExit(0 if normalize('a   b') == 'a b' else 1)"
    return subprocess.run([sys.executable, "-c", probe], cwd=fx.work, capture_output=True, check=False).returncode == 0


# Roda o python da venv da fixture; devolve (código, saída). Usado para provar efeitos, não para implementar.
def venv_run(fx: Fixture, *args: str) -> tuple[int, str]:
    python = fx.work / (".venv/Scripts/python.exe" if IS_WINDOWS else ".venv/bin/python")
    result = subprocess.run([str(python), *args], cwd=fx.work, capture_output=True, text=True, encoding="utf-8", check=False)
    return result.returncode, (result.stdout + result.stderr).strip()


# ============================ Execução do claude -p ============================


@dataclass
class Config:
    """Parâmetros comuns às chamadas do `claude -p`."""

    model: str
    budget_usd: float
    timeout_s: int
    permission_mode: str
    evidence: Path


@dataclass
class Call:
    """Resultado de uma chamada: transcript parseado e como ela terminou."""

    label: str
    session_id: str | None = None
    result: dict | None = None
    tool_uses: list[tuple[str, dict]] = field(default_factory=list)
    tool_results: list[str] = field(default_factory=list)
    interrupted_by: str | None = None
    returncode: int | None = None

    @property
    def text(self) -> str:
        return (self.result or {}).get("result") or ""

    @property
    def ok(self) -> bool:
        return bool(self.result) and not self.result.get("is_error") and self.result.get("subtype") == "success"

    # Prompts dos subagentes (ferramenta Task ou Agent) que o coordenador abriu nesta chamada.
    def subagent_prompts(self) -> list[str]:
        return [str(args.get("prompt") or args.get("description") or "") for name, args in self.tool_uses if name in ("Task", "Agent")]


# Encerra o processo e seus filhos; no Windows o `taskkill /T` evita deixar git ou python órfãos.
def kill_tree(proc: subprocess.Popen) -> None:
    if IS_WINDOWS:
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True, check=False)
    else:
        proc.kill()


# Extrai de um stream-json o id de sessão, o evento final e as ferramentas usadas (evidência do transcript).
def parse_stream(path: Path, call: Call) -> None:
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        call.session_id = event.get("session_id") or call.session_id
        kind = event.get("type")
        if kind == "result":
            call.result = event
        content = (event.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if kind == "assistant" and block.get("type") == "tool_use":
                call.tool_uses.append((block.get("name", ""), block.get("input") or {}))
            elif kind == "user" and block.get("type") == "tool_result":
                body = block.get("content")
                call.tool_results.append(body if isinstance(body, str) else json.dumps(body, ensure_ascii=False))


# Chama `claude -p` na fixture. O prompt entra por stdin (o `--allowedTools` é variádico e engoliria um argumento).
# `kill_when` permite interromper a chamada, como na rodada 2; `resume` continua a sessão de uma chamada anterior.
def run_claude(cfg: Config, fx: Fixture, prompt: str, label: str, *, resume: str | None = None,
               persist: bool = False, kill_when=None) -> Call:
    out = cfg.evidence / f"{label}.jsonl"
    cmd = [
        shutil.which("claude") or "claude", "-p",
        "--plugin-dir", str(fx.plugin), "--add-dir", str(fx.plugin),
        "--setting-sources", "project,local",
        "--permission-mode", cfg.permission_mode,
        "--allowedTools", ",".join(ALLOWED_TOOLS),
        "--output-format", "stream-json", "--verbose",
        "--max-budget-usd", str(cfg.budget_usd),
        "--model", cfg.model,
    ]
    if resume:
        cmd += ["--resume", resume]
    if not persist and not resume:
        cmd.append("--no-session-persistence")

    call = Call(label=label)
    with out.open("wb") as stdout, (cfg.evidence / f"{label}.stderr.txt").open("wb") as stderr:
        proc = subprocess.Popen(cmd, cwd=fx.work, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr)
        assert proc.stdin is not None
        proc.stdin.write(prompt.encode("utf-8"))
        proc.stdin.close()
        started = time.monotonic()
        while proc.poll() is None:
            time.sleep(POLL_SECONDS)
            if time.monotonic() - started > cfg.timeout_s:
                call.interrupted_by = "timeout"
                kill_tree(proc)
                break
            if kill_when is not None and kill_when():
                call.interrupted_by = "interrupção planejada"
                kill_tree(proc)
                break
        proc.wait()
    call.returncode = proc.returncode
    parse_stream(out, call)
    cost = (call.result or {}).get("total_cost_usd")
    print(f"  chamada {label}: fim={call.interrupted_by or 'normal'} custo={cost} turnos={(call.result or {}).get('num_turns')}", flush=True)
    return call


# Conferência comum: a chamada terminou sem erro nem teto de custo, e nenhuma permissão foi negada.
def check_call(report: Report, call: Call, *, allow_interrupt: bool = False) -> None:
    result = call.result or {}
    if not allow_interrupt:
        report.check(call.ok, f"{call.label}: terminou sem erro", f"subtype={result.get('subtype')} interrompida={call.interrupted_by}")
    denials = result.get("permission_denials") or []
    if denials:
        print(f"  permissões negadas em {call.label}: {len(denials)}", flush=True)
        report.note(f"{call.label}: permissões negadas ({len(denials)}):\n" + json.dumps(denials, ensure_ascii=False)[:1500])
    report.note(f"{call.label}: custo={result.get('total_cost_usd')} turnos={result.get('num_turns')} subagentes={len(call.subagent_prompts())}")


# ============================ Rodadas ============================


# Confere as cadeias comuns às rodadas de implementação: fixture válida e defeito real presente.
def check_fixture_start(report: Report, fx: Fixture) -> None:
    state = engine_state(fx)
    report.check(state["etapa"] == "implementar" and state["fila"]["elegiveis"] == ["T1", "T2"],
                 "fixture: motor informa etapa implementar com T1 e T2 elegíveis", json.dumps(state)[:300])
    report.check(not normalize_is_fixed(fx), "fixture: defeito de normalize presente (três espaços não colapsam)")
    pytest_code, _ = venv_run(fx, "-c", "import pytest")
    report.check(pytest_code != 0, "fixture: pytest ausente na venv do projeto")


# Rodada 0 (A1 e A2): o chat do plan delega o analyze, e o achado plantado é corrigido no plan.md.
def round0(cfg: Config, parent: Path) -> Report:
    report = Report("rodada 0: analyze delegado (A1, A2)")
    fx = build_fixture(parent, "r0", with_analyze=False, plant_finding=True)
    report.check("A3" not in task_section(plan_of(fx), "T3"), "fixture: achado plantado (T3 sem A3 em Spec)")
    prompt = "/vibeflow:vibe-plan O plan.md desta phase já está aprovado. Pode ir pro analyze."
    call = run_claude(cfg, fx, prompt, "r0-plan-analyze")
    check_call(report, call)
    analyze = fx.work / PHASE_DIR / "analyze.md"
    report.check(analyze.is_file(), "analyze.md gravado na phase")
    plan = plan_of(fx)
    covered = any("A3" in re.findall(r"A\d+", line) for line in plan.splitlines() if "**Spec:**" in line)
    report.check(covered, "achado plantado corrigido: alguma T* passou a citar A3 em Spec")
    prompts = call.subagent_prompts()
    report.check(any("analy" in p.lower() for p in prompts), "analyze delegado a subagente", f"{len(prompts)} subagente(s)")
    report.check(not task_subjects(fx), "nenhum commit de task criado pelo chat do plan")
    report.note("fechamento do plan (evidência de A2, para leitura humana):\n" + call.text[:2500])
    return report


# Rodada 1 (A3 a A6 e A10): piloto completo até a pergunta final, depois confirmação e push.
def round1(cfg: Config, parent: Path) -> Report:
    report = Report("rodada 1: piloto completo (A3 a A6, A10)")
    fx = build_fixture(parent, "r1", with_analyze=True, plant_finding=False)
    check_fixture_start(report, fx)
    original_tests = {p.name: p.read_text(encoding="utf-8") for p in (fx.work / "tests").glob("test_*.py")}

    first = run_claude(cfg, fx, "/vibeflow:vibe-implement", "r1-implement", persist=True)
    check_call(report, first)
    state = engine_state(fx)
    report.check(state["etapa"] == "confirmar", "uma única parada antes da confirmação: etapa final do motor é confirmar",
                 f"etapa={state['etapa']} rodadas={state['rodadas_correcao']}")
    report.check(state["rodadas_correcao"] <= 2, "no máximo 2 rodadas de correção", f"rodadas={state['rodadas_correcao']}")
    subjects = task_subjects(fx)
    for task in ("T1", "T2", "T3"):
        report.check(sum(s.startswith(f"task({task})") for s in subjects) == 1, f"exatamente um commit task({task})", "; ".join(subjects))
    order = [match.group(1) for s in subjects if (match := re.match(r"task\((T\d)\)", s))]
    report.check({"T1", "T2", "T3"} <= set(order) and order.index("T3") > max(order.index("T1"), order.index("T2")),
                 "T3 só depois de T1 e T2", str(order))
    report.check(len(first.subagent_prompts()) >= 4, "implementação e review em subagentes (pelo menos 3 T* e 1 review)", f"{len(first.subagent_prompts())} subagente(s)")
    report.check(any("review" in p.lower() or "revis" in p.lower() for p in first.subagent_prompts()), "alguma delegação é a review")
    report.check((fx.work / PHASE_DIR / "review.md").is_file(), "review.md gravado")
    remote_before = git(fx.remote, "rev-parse", "main")
    report.check(remote_before == fx.baseline, "nenhum push antes da confirmação (remoto no baseline)")

    # A6: causa raiz corrigida no código compartilhado, sem enfraquecer nenhum teste original.
    report.check(normalize_is_fixed(fx), "A6: defeito corrigido na origem (normalize colapsa três espaços)")
    weakened = [name for name, text in original_tests.items()
                if not set(line for line in text.splitlines() if line.strip()) <= set((fx.work / "tests" / name).read_text(encoding="utf-8").splitlines())]
    report.check(not weakened, "A6: nenhuma asserção original removida ou alterada nos testes", ", ".join(weakened))
    # A10: o requisito ausente foi instalado e a instalação ficou registrada no plan.
    pytest_code, _ = venv_run(fx, "-m", "pytest", "--version")
    report.check(pytest_code == 0, "A10: pytest instalado na venv")
    report.check(re.search(r"instal|pip", task_section(plan_of(fx), "T1"), re.IGNORECASE) is not None, "A10: instalação registrada sob a T1 no plan")
    suite_code, suite_out = venv_run(fx, "-m", "pytest", "-q")
    report.check(suite_code == 0, "suíte completa verde no estado final", suite_out[-300:])
    report.note("pergunta final do piloto:\n" + first.text[:2500])

    # A5: confirmação na mesma sessão, com push no remoto local e review aprovada.
    second = run_claude(cfg, fx, "Confirmo: pode aprovar a review, publicar as decisões vigentes e fazer o push.",
                        "r1-confirm", resume=first.session_id)
    check_call(report, second)
    final = engine_state(fx)
    report.check(final["etapa"] == "concluida", "após a confirmação a etapa do motor é concluida", f"etapa={final['etapa']}")
    report.check(git(fx.remote, "rev-parse", "main") == git(fx.work, "rev-parse", "HEAD"), "push registrado no remoto local (HEAD igual)")
    report.check(len(git(fx.work, "log", "--format=%s", "--grep=^task(").splitlines()) >= 3, "commits task(Tn) preservados no histórico")
    with_trailer = [h for h, _ in new_commits(fx) if "Co-Authored-By" in git(fx.work, "show", "-s", "--format=%B", h)]
    report.note(f"commits com Co-Authored-By (informativo): {len(with_trailer)}")
    report.note("mensagem final após a confirmação:\n" + second.text[:1500])
    report.note("commits da rodada:\n" + "\n".join(f"{h[:9]} {s}" for h, s in new_commits(fx)))
    report.note(f"perguntas ao humano antes do push: 1 (a chamada r1-implement terminou em etapa {state['etapa']})")
    return report


# Rodada 2 (A7): interrompe depois da primeira T* e retoma em sessão nova, sem refazer a T* concluída.
def round2(cfg: Config, parent: Path) -> Report:
    report = Report("rodada 2: retomada em sessão nova (A7)")
    fx = build_fixture(parent, "r2", with_analyze=True, plant_finding=False)
    check_fixture_start(report, fx)
    first = run_claude(cfg, fx, "/vibeflow:vibe-implement", "r2-implement-interrompida",
                       kill_when=lambda: has_task_commit(fx, "T1") or has_task_commit(fx, "T2"))
    report.check(first.interrupted_by == "interrupção planejada", "primeira sessão interrompida após a primeira T*", f"fim={first.interrupted_by}")
    done_first = [s.split(":")[0] for s in task_subjects(fx)]
    report.check(len(done_first) >= 1, "há ao menos uma T* commitada antes da interrupção", str(done_first))
    first_ids = set(done_first)

    resumed = run_claude(cfg, fx, "/vibeflow:vibe-implement", "r2-implement-retomada",
                         kill_when=lambda: len(task_subjects(fx)) > len(first_ids))
    check_call(report, resumed, allow_interrupt=True)
    report.check(resumed.session_id != first.session_id, "retomada em sessão nova", f"{first.session_id} -> {resumed.session_id}")
    after = [s.split(":")[0] for s in task_subjects(fx)]
    report.check(all(after.count(task) == 1 for task in set(after)), "nenhum commit duplicado para T* já concluída", str(after))
    report.check(len(set(after) - first_ids) >= 1, "a retomada avançou para uma T* nova", str(after))
    used_engine = any(name in ("Bash", "PowerShell") and re.search(r"implement\.(py|ps1)", json.dumps(args)) for name, args in resumed.tool_uses)
    report.check(used_engine, "a sessão nova consultou o motor do implement")
    report.note("commits da rodada:\n" + "\n".join(f"{h[:9]} {s}" for h, s in new_commits(fx)))
    return report


# Rodada 3 (A8): pedido explícito de uma T* por vez conclui só uma T*, sem piloto nem review.
def round3(cfg: Config, parent: Path) -> Report:
    report = Report("rodada 3: Modo B, uma T* por vez (A8)")
    fx = build_fixture(parent, "r3", with_analyze=True, plant_finding=False)
    check_fixture_start(report, fx)
    call = run_claude(cfg, fx, "/vibeflow:vibe-implement Execute só a T1. Quero acompanhar uma T* por vez.", "r3-modo-b")
    check_call(report, call)
    subjects = task_subjects(fx)
    report.check(len(subjects) == 1 and subjects[0].startswith("task(T1)"), "exatamente um commit, task(T1)", "; ".join(subjects))
    state = engine_state(fx)
    report.check(state["fila"]["concluidas"] == ["T1"], "fila: só a T1 concluída", json.dumps(state["fila"]["concluidas"]))
    report.check(not (fx.work / PHASE_DIR / "review.md").exists(), "nenhuma review aberta no Modo B")
    report.check(git(fx.remote, "rev-parse", "main") == fx.baseline, "nenhum push no Modo B")
    report.note("resposta final do Modo B:\n" + call.text[:1800])
    return report


ROUNDS = {"0": round0, "1": round1, "2": round2, "3": round3}


# ============================ Linha de comando ============================


# Prepara uma jornada stdlib do protocolo novo para avaliação por agentes do host, sem conta externa.
def build_stage_fixture(parent: Path) -> Fixture:
    root = parent / "etapas"
    work = root / "work"
    work.mkdir(parents=True)
    plugin = root / "plugin"
    remote = root / "remote.git"
    files = {
        "AGENTS.md": "# Fixture etapas\nResponda em PT-BR. Use unittest da standard library. Sem rede, instalação, configuração global ou push. Somente o coordenador modifica os artefatos e Git desta fixture.\n",
        ".gitignore": "__pycache__/\n",
        "textkit/__init__.py": "# Utilitários de texto da fixture.\n",
        "textkit/shared.py": "# Normalização compartilhada pelo código existente e pelos novos consumidores.\ndef normalize(text):\n    return text.strip().replace('  ', ' ')\n",
        "tests/test_existing.py": "import unittest\nfrom textkit.shared import normalize\nclass Existing(unittest.TestCase):\n    def test_existing_normalization(self):\n        self.assertEqual('a b', normalize(' a  b '))\n",
        f"{PHASE_DIR}/spec.md": "# Spec: utilitários de texto\n# Status: aprovado\nA1: word_count(text) conta palavras após normalização compartilhada, com qualquer espaço em branco, incluindo tabs, repetição, vazio e Unicode.\nA2: summarize(text) devolve {'normalized': texto normalizado com um espaço entre palavras, 'count': contagem} reutilizando word_count e normalize. Nenhum resultado contém espaços repetidos ou tabs.\nFora: UI, rede e dependências externas.\n",
    }
    integration = {"testes": "pendentes", "prova": None, "commit": "pendente"}
    plan = "# Plan: utilitários de texto\n# Status: aprovado\n# Protocolo: etapas-v1\n# Modo: A\n"
    plan += "- **Integração:** " + json.dumps(integration) + "\n\n## Tasks\n"
    for tid, deps, description, paths in (("T1", "nenhuma", "Implementar word_count em textkit.stats usando normalização compartilhada", "textkit/stats.py"), ("T2", "T1", "Implementar summarize em textkit.report reutilizando word_count e normalize", "textkit/report.py")):
        plan += f"### {tid}: {description}\n- [ ] {tid} concluída\n- **Spec:** {'A1' if tid == 'T1' else 'A2'}\n- **Deps:** {deps}\n- **Arquivos:** `{paths}`\n- **Verificação:** `python -m unittest discover -s tests -v`\n- **Execução:** " + json.dumps({"estado": "pendente", "local": None}) + "\n"
    files[f"{PHASE_DIR}/plan.md"] = plan
    for relative, content in files.items():
        path = work / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    git(work, "init", "-q", "-b", "main")
    for key, value in (("user.name", "Fixture VibeFlow"), ("user.email", "fixture@example.invalid"), ("core.autocrlf", "false")):
        git(work, "config", key, value)
    git(work, "add", "--", "AGENTS.md", ".gitignore", "textkit", "tests", ".vibeflow")
    git(work, "commit", "-q", "-m", "fixture: baseline etapas")
    git(root, "init", "-q", "--bare", "-b", "main", str(remote))
    git(work, "remote", "add", "origin", str(remote))
    snapshot_plugin(plugin)
    return Fixture(root, work, remote, plugin, git(work, "rev-parse", "HEAD"))


# Verifica estrutura e etapa inicial sem substituir a avaliação comportamental por modelo independente.
def check_stage_fixture(fx: Fixture) -> bool:
    state = engine_state(fx)
    run = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=fx.work, capture_output=True, text=True)
    return state["etapa"] == "implementar" and state["fila"]["elegiveis"] == ["T1"] and state["execucao"]["modo"] == "A" and run.returncode == 0


# Valida só as fixtures, sem chamar o claude: confirma que o defeito, a ausência do pytest e o remoto estão corretos.
def prepare_only(parent: Path) -> bool:
    ok = True
    for name, with_analyze, plant in (("r0", False, True), ("r1", True, False)):
        report = Report(f"fixture {name}")
        fx = build_fixture(parent, name, with_analyze=with_analyze, plant_finding=plant)
        if plant:
            report.check("A3" not in task_section(plan_of(fx), "T3"), "achado plantado presente")
            report.check(not (fx.work / PHASE_DIR / "analyze.md").exists(), "sem analyze.md")
        else:
            check_fixture_start(report, fx)
            report.check(git(fx.remote, "rev-parse", "main") == fx.baseline, "remoto bare no baseline")
        ok = ok and report.passed
    stages = build_stage_fixture(parent)
    stage_valid = check_stage_fixture(stages)
    print("  [PASS] fixture etapas-v1 stdlib" if stage_valid else "  [FAIL] fixture etapas-v1 stdlib")
    return ok and stage_valid


# Escreve o resumo da execução (conferências e notas de evidência) ao lado dos transcripts.
def write_summary(cfg: Config, reports: list[Report]) -> Path:
    lines = [f"# Piloto do Modo A ({datetime.now():%Y-%m-%d %H:%M})", "", f"Modelo: `{cfg.model}`. Permissão: `{cfg.permission_mode}`.", ""]
    for report in reports:
        lines += [f"## {report.name}: {'PASS' if report.passed else 'FAIL'}", ""]
        lines += [f"- {'PASS' if ok else 'FAIL'}: {label}" + (f" ({detail})" if detail and not ok else "") for ok, label, detail in report.checks]
        for note in report.notes:
            lines += ["", "```text", note, "```"]
        lines.append("")
    path = cfg.evidence / "summary.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# Ponto de entrada: valida argumentos, cria a pasta temporária, roda as rodadas e remove tudo no fim.
def main() -> int:
    parser = argparse.ArgumentParser(description="Piloto do Modo A do vibe-implement em repo descartável")
    parser.add_argument("--rounds", default="0,1,2,3", help="rodadas separadas por vírgula (padrão: todas)")
    parser.add_argument("--model", default="sonnet", help="modelo do claude -p (padrão: sonnet)")
    parser.add_argument("--budget-usd", type=float, default=12.0, help="teto de custo por chamada do claude -p")
    parser.add_argument("--timeout-min", type=int, default=45, help="tempo máximo por chamada, em minutos")
    parser.add_argument("--permission-mode", default="acceptEdits", choices=("acceptEdits", "dontAsk", "bypassPermissions"))
    parser.add_argument("--confirmado-pelo-humano", action="store_true", help="exigido para bypassPermissions")
    parser.add_argument("--evidence-dir", help="pasta dos transcripts e do resumo (padrão: temporária, mantida)")
    parser.add_argument("--keep", action="store_true", help="não remove as fixtures ao final (depuração)")
    parser.add_argument("--prepare-only", action="store_true", help="só valida as fixtures, sem chamar o claude")
    parser.add_argument("--prepare-stages", help="prepara fixture etapas-v1 no diretório explícito, sem chamar modelos; coordenador deve removê-la após avaliação")
    args = parser.parse_args()
    sys.stdout.reconfigure(errors="replace")
    if args.prepare_stages:
        destination = Path(args.prepare_stages).absolute()
        if destination.exists():
            parser.error("--prepare-stages exige diretório ausente para não substituir trabalho existente")
        destination.mkdir(parents=True)
        try:
            fx = build_stage_fixture(destination)
            if not check_stage_fixture(fx):
                raise RuntimeError("fixture etapas-v1 inválida")
            print(json.dumps({"fixture": str(fx.root), "work": str(fx.work), "plugin": str(fx.plugin), "remote": str(fx.remote), "baseline": fx.baseline}, ensure_ascii=False))
            return 0
        except Exception:
            remove_tree(destination)
            raise

    if args.permission_mode == "bypassPermissions" and not args.confirmado_pelo_humano:
        parser.error("bypassPermissions exige --confirmado-pelo-humano: o modo não confina o agente à pasta temporária")
    wanted = [item.strip() for item in args.rounds.split(",") if item.strip()]
    unknown = [item for item in wanted if item not in ROUNDS]
    if unknown:
        parser.error(f"rodadas desconhecidas: {', '.join(unknown)}")
    if not args.prepare_only and shutil.which("claude") is None:
        print("PILOTO_SEM_CLAUDE: o executável `claude` não está no PATH.", file=sys.stderr)
        return 1

    parent = Path(tempfile.mkdtemp(prefix="vibe-piloto-"))
    # O modo `--prepare-only` não chama o claude e, portanto, não produz evidência.
    if args.prepare_only:
        evidence = parent
    else:
        evidence = Path(args.evidence_dir) if args.evidence_dir else Path(tempfile.mkdtemp(prefix="vibe-piloto-evidencia-"))
        evidence.mkdir(parents=True, exist_ok=True)
    cfg = Config(args.model, args.budget_usd, args.timeout_min * 60, args.permission_mode, evidence)
    reports: list[Report] = []
    try:
        if args.prepare_only:
            print("Validando fixtures (sem tokens)")
            return 0 if prepare_only(parent) else 1
        for key in wanted:
            print(f"Rodada {key}", flush=True)
            reports.append(ROUNDS[key](cfg, parent))
        summary = write_summary(cfg, reports)
        print(f"\nResumo e transcripts: {summary.parent}")
        return 0 if all(report.passed for report in reports) else 1
    finally:
        # A falha de limpeza não é ignorada: a pasta temporária guarda um repo Git e uma venv.
        if args.keep:
            print(f"Fixtures mantidas em {parent}")
        else:
            remove_tree(parent)


if __name__ == "__main__":
    raise SystemExit(main())
