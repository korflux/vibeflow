#!/usr/bin/env python3
"""Contratos nativos e paridade essencial da skill vibe-implement canônica."""

from __future__ import annotations

from functools import cache

import json
import os
import shutil
import stat
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[3] / "vibe-implement"
SCRIPT = SKILL_DIR / "scripts" / "implement.py"
POWERSHELL_SCRIPT = SKILL_DIR / "scripts" / "implement.ps1"


# Limpa a fixture e torna graváveis objetos Git que o Windows cria como read-only.
def remove_fixture_tree(path: Path) -> None:
    # A falha volta ao teste se o problema não for apenas o atributo read-only.
    def retry_writable(operation, filename, error) -> None:
        os.chmod(filename, stat.S_IWRITE)
        operation(filename)

    shutil.rmtree(path, onerror=retry_writable)


# Executa o motor Python e decodifica o inventário transitório enviado no stdout.
def invoke(repo: Path, *arguments: str, check: bool = True) -> tuple[subprocess.CompletedProcess[str], dict | None]:
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo), *arguments],
        capture_output=True,
        text=True, encoding="utf-8",
        check=check,
    )
    report = json.loads(process.stdout) if process.returncode == 0 and process.stdout.strip() else None
    return process, report


# Cria só a pasta .vibeflow, como se o init tivesse rodado sem phases.
def seed_vibeflow(repo: Path) -> Path:
    vf = repo / ".vibeflow"
    vf.mkdir()
    (vf / ".gitignore").write_text("init-report.json\ninit-pending.json\n", encoding="utf-8")
    return vf


# Grava uma fase mínima com os arquivos pedidos.
def seed_phase(vf: Path, name: str, *files: str) -> Path:
    phase = vf / "phases" / name
    phase.mkdir(parents=True)
    for filename in files:
        (phase / filename).write_text(f"{filename}\n", encoding="utf-8")
    return phase


# Plan mínimo com as duas linhas congeladas por T* (concluída + Deps).
def plan_tasks(*tasks: tuple[str, str, str]) -> str:
    chunks = ["# Plan: fixture\n"]
    for tid, mark, deps in tasks:
        chunks.append(
            f"### {tid}: fixture {tid}\n\n"
            f"- [{mark}] {tid} concluída\n"
            f"- **Deps:** {deps}\n"
        )
    return "\n".join(chunks)


# Troca o corpo do plan.md da fase já criada.
def write_plan(phase: Path, body: str) -> None:
    (phase / "plan.md").write_text(body, encoding="utf-8")


# Grava o alvo MVP mínimo e permite variar o gate do analyze nos contratos.
def seed_mvp(vf: Path, plan: str, status: str | None = "aprovado", verdict: str = "limpo") -> Path:
    mvp = vf / "mvp"
    mvp.mkdir()
    (mvp / "plan.md").write_text(plan, encoding="utf-8")
    if status is not None:
        (mvp / "analyze.md").write_text(
            f"# Analyze: fixture\n# Status: {status}\n\n## Veredito\n\n{verdict}\n",
            encoding="utf-8",
        )
    return mvp


# Campos do JSON operacional; analyze_gate acompanha esses somente no alvo MVP.
REPORT_KEYS = {"alvo", "fila", "etapa", "rodadas_correcao", "avisos"}


# Fotografa os bytes de todos os arquivos sob a raiz, para provar que o motor não escreve ao derivar a etapa.
def tree_snapshot(root: Path) -> dict[str, bytes]:
    return {str(path.relative_to(root)): path.read_bytes() for path in sorted(root.rglob("*")) if path.is_file()}


# Monta um review.md mínimo no formato do template: Status, checklist, Notas, Veredito vigente e Etapas.
# `status=None` omite a linha; `vigente` marca uma das alternativas; cada item de `etapas` vira um bloco de etapa.
def review_text(
    status: str | None = "rascunho",
    blockers: tuple[str, ...] = (),
    notas: str = "",
    vigente: str | None = None,
    etapas: tuple[str, ...] = (),
) -> str:
    lines = ["# Review: fixture", "# Alvo: phase-1-a"]
    if status is not None:
        lines.append(f"# Status: {status}")
    lines += ["", "## Checklist de correções", "", *blockers, "", "## Notas", "", notas, "", "## Veredito vigente", ""]
    for option in ("Approve", "Request changes", "Approve com defer"):
        lines.append(f"- [{'x' if option == vigente else ' '}] **{option}**: texto do template")
    lines += ["", "## Etapas", ""]
    for number, verdict in enumerate(etapas, start=1):
        lines += [f"### Etapa {number} - fixture", "", f"- Veredito desta etapa: {verdict}", ""]
    return "\n".join(lines) + "\n"


FILA_ABERTA = plan_tasks(("T1", " ", "nenhuma"), ("T2", " ", "T1"))
FILA_CONCLUIDA = plan_tasks(("T1", "x", "nenhuma"), ("T2", "x", "T1"))
CRITICAL_ABERTO = "- [ ] R1: **Critical** - `a.py` - problema - remédio: corrigir - prova: teste"
CRITICAL_FECHADO = CRITICAL_ABERTO.replace("[ ]", "[x]")
REQUIRED_FECHADO = "- [x] R2: **Required** - `b.py` - problema - remédio: corrigir - prova: teste"
NIT_ABERTO = "- [ ] R3: **Nit** - `c.py` - detalhe - defer: cosmético; retomar na revisão visual"
ALTERNATIVAS_DO_TEMPLATE = "Marco aprovado | Request changes | Approve final | Approve com defer"

# Estados da phase que o motor precisa distinguir. `avisos` é a contagem esperada no campo avisos do JSON.
ETAPA_CASES: list[dict] = [
    {"nome": "t-elegivel", "plan": FILA_ABERTA, "review": None, "etapa": "implementar", "rodadas": 0, "avisos": 0},
    {"nome": "t-bloqueada", "plan": plan_tasks(("T1", " ", "T9")), "review": None, "etapa": "bloqueada", "rodadas": 0, "avisos": 0},
    {"nome": "fila-concluida-sem-review", "plan": FILA_CONCLUIDA, "review": None, "etapa": "revisar", "rodadas": 0, "avisos": 0},
    {
        "nome": "review-com-bloqueio-aberto",
        "plan": FILA_CONCLUIDA,
        "review": review_text(blockers=(CRITICAL_ABERTO,), etapas=("Request changes",)),
        "etapa": "corrigir", "rodadas": 0, "avisos": 0,
    },
    {
        "nome": "bloqueios-fechados-aguardando-nova-review",
        "plan": FILA_CONCLUIDA,
        "review": review_text(blockers=(CRITICAL_FECHADO, REQUIRED_FECHADO), etapas=("Request changes",)),
        "etapa": "revisar", "rodadas": 1, "avisos": 0,
    },
    {
        "nome": "approve-aguardando-confirmacao",
        "plan": FILA_CONCLUIDA,
        "review": review_text(
            blockers=(CRITICAL_FECHADO,), vigente="Approve", etapas=("Request changes", "Approve final"),
        ),
        "etapa": "confirmar", "rodadas": 1, "avisos": 0,
    },
    {
        "nome": "approve-com-defer-nao-adia-nit",
        "plan": FILA_CONCLUIDA,
        "review": review_text(blockers=(NIT_ABERTO,), vigente="Approve com defer", etapas=("Approve com defer",)).replace(
            "**Approve com defer**: texto do template",
            "**Approve com defer**: R3; fonte: `c.py`; motivo: cosmético; retomar na revisão visual",
        ),
        "etapa": "corrigir", "rodadas": 0, "avisos": 0,
    },
    {
        # Mesmo marcado como defer, bloqueio Critical permanece na fila de correção.
        "nome": "approve-com-defer-nao-adia-critical",
        "plan": FILA_CONCLUIDA,
        "review": review_text(blockers=(CRITICAL_ABERTO,), vigente="Approve com defer", etapas=("Approve com defer",)),
        "etapa": "corrigir", "rodadas": 0, "avisos": 0,
    },
    {
        # Obrigação parcial registrada como Required não pode ser adiada pelo veredito.
        "nome": "approve-com-defer-nao-adia-required",
        "plan": FILA_CONCLUIDA,
        "review": review_text(blockers=("- [ ] R4: **Required** - `d.py` - obrigação parcial - defer: próxima fase",),
                              vigente="Approve com defer", etapas=("Approve com defer",)),
        "etapa": "corrigir", "rodadas": 0, "avisos": 0,
    },
    {
        "nome": "phase-finalizada",
        "plan": FILA_CONCLUIDA,
        "review": review_text(status="aprovado", vigente="Approve", etapas=("Request changes", "Approve final")),
        "etapa": "concluida", "rodadas": 1, "avisos": 0,
    },
    {
        "nome": "duas-rodadas-usadas-com-bloqueio-aberto",
        "plan": FILA_CONCLUIDA,
        "review": review_text(
            blockers=(CRITICAL_ABERTO,), etapas=("Request changes", "Request changes", "Request changes"),
        ),
        "etapa": "corrigir", "rodadas": 2, "avisos": 0,
    },
    {
        "nome": "alternativas-do-template-nao-contam",
        "plan": FILA_CONCLUIDA,
        "review": review_text(etapas=(ALTERNATIVAS_DO_TEMPLATE,)),
        "etapa": "revisar", "rodadas": 0, "avisos": 0,
    },
    {
        "nome": "request-changes-com-ponto-final",
        "plan": FILA_CONCLUIDA,
        "review": review_text(blockers=(CRITICAL_FECHADO,), etapas=("Request changes.",)),
        "etapa": "revisar", "rodadas": 1, "avisos": 0,
    },
    {
        # Formato real da phase 10: negrito e texto depois do veredito.
        "nome": "request-changes-com-negrito-e-texto",
        "plan": FILA_CONCLUIDA,
        "review": review_text(blockers=(CRITICAL_FECHADO,), etapas=("**Request changes**. As inconsistências persistem",)),
        "etapa": "revisar", "rodadas": 1, "avisos": 0,
    },
    {
        # A última etapa com bloqueio aberto não soma, mesmo com formatos diferentes nas etapas anteriores.
        "nome": "request-changes-em-formatos-variados-com-bloqueio-aberto",
        "plan": FILA_CONCLUIDA,
        "review": review_text(
            blockers=(CRITICAL_ABERTO,),
            etapas=("**Request changes**. texto", "_Request changes_", "Request changes, R1 aberto"),
        ),
        "etapa": "corrigir", "rodadas": 2, "avisos": 0,
    },
    {
        # Citar Request changes no meio de outro veredito não é um Request changes.
        "nome": "mencao-a-request-changes-no-meio-nao-conta",
        "plan": FILA_CONCLUIDA,
        "review": review_text(etapas=("Approve final (sem Request changes)",)),
        "etapa": "revisar", "rodadas": 0, "avisos": 0,
    },
    {
        "nome": "nit-aberto-bloqueia",
        "plan": FILA_CONCLUIDA,
        "review": review_text(blockers=(NIT_ABERTO,), etapas=("Marco aprovado",)),
        "etapa": "corrigir", "rodadas": 0, "avisos": 0,
    },
    {
        "nome": "approve-fora-do-veredito-vigente-nao-conta",
        "plan": FILA_CONCLUIDA,
        "review": review_text(notas="- [x] **Approve**: citado nas notas"),
        "etapa": "revisar", "rodadas": 0, "avisos": 0,
    },
    {
        "nome": "review-sem-status",
        "plan": FILA_CONCLUIDA,
        "review": review_text(status=None, vigente="Approve"),
        "etapa": None, "rodadas": 0, "avisos": 1,
    },
    {
        "nome": "review-ilegivel",
        "plan": FILA_CONCLUIDA,
        "review": b"\x80\x81\x82 nao e utf-8\n",
        "etapa": None, "rodadas": 0, "avisos": 1,
    },
    {"nome": "sem-plan", "plan": None, "review": None, "etapa": None, "rodadas": 0, "avisos": 0},
    {"nome": "fila-ilegivel", "plan": "# Plan sem tasks\n", "review": None, "etapa": None, "rodadas": 0, "avisos": 0},
    {
        "nome": "t-sem-linha-concluida",
        "plan": "### T1: sem checkbox\n\n- **Deps:** nenhuma\n\n### T2: ok\n\n- [x] T2 concluída\n- **Deps:** nenhuma\n",
        "review": None,
        "etapa": None, "rodadas": 0, "avisos": 0,
    },
]


# Percorre classificações históricas no mesmo contrato de identidade R*, com aprovação contraditória.
for severity in ("Critical", "Required", "Nit", "Optional", "FYI"):
    correction = f"- [ ] R7: **{severity}** - `core.py` - corrigir"
    ETAPA_CASES.extend([
        {"nome": f"aprovado-com-{severity.lower()}-aberto", "plan": FILA_CONCLUIDA,
         "review": review_text(status="aprovado", blockers=(correction,), vigente="Approve", etapas=("Request changes",)),
         "etapa": "corrigir", "rodadas": 0, "avisos": 0},
        {"nome": f"defer-com-{severity.lower()}-fechado", "plan": FILA_CONCLUIDA,
         "review": review_text(blockers=(correction.replace("[ ]", "[X]"),), vigente="Approve com defer", etapas=("Request changes",)),
         "etapa": "confirmar", "rodadas": 1, "avisos": 0},
    ])

# Retomada bloqueada independe do protocolo e não exige migrar ou inicializar o registro.
for protocol, mode in (("coordenacao-v1", "A"), ("coordenacao-v1", "B"), ("etapas-v1", "A"), ("etapas-v1", "B")):
    operational_plan = f"# Protocolo: {protocol}\n# Modo: {mode}\n" + FILA_ABERTA
    if protocol == "etapas-v1" and mode == "A":
        operational_plan = operational_plan.replace("### T1:", '- **Integração:** {"testes":"pendentes","prova":null,"commit":"pendente"}\n## Tasks\n### T1:')
        operational_plan = operational_plan.replace('- **Deps:** nenhuma', '- **Deps:** nenhuma\n- **Execução:** {"estado":"pendente","local":null}').replace('- **Deps:** T1', '- **Deps:** T1\n- **Execução:** {"estado":"pendente","local":null}')
    ETAPA_CASES.append({"nome": f"{protocol}-{mode}-correcao-aberta", "plan": operational_plan,
                        "review": review_text(status="aprovado", blockers=(NIT_ABERTO,), vigente="Approve com defer"),
                        "etapa": "corrigir", "rodadas": 0, "avisos": 0})


# Plan aprovado de coordenacao-v1 com `Arquivos:` cru por T*, na forma `(id, deps, arquivos)`. `arquivos=None` omite a
# linha, para exercitar a T* sem arquivos declarados. Protocolo e modo variam para provar que só o Modo A emite onda.
def wave_plan(*tasks: tuple[str, str, str | None], protocol: str = "coordenacao-v1", mode: str | None = "A") -> str:
    header = ["# Plan: onda", "# Status: aprovado"]
    if protocol:
        header.append(f"# Protocolo: {protocol}")
    if mode:
        header.append(f"# Modo: {mode}")
    chunks = ["\n".join(header) + "\n\n## Tasks\n"]
    for tid, deps, arquivos in tasks:
        lines = [f"### {tid}: fixture {tid}", "", f"- [ ] {tid} concluída", f"- **Deps:** {deps}"]
        if arquivos is not None:
            lines.append(f"- **Arquivos:** {arquivos}")
        chunks.append("\n".join(lines) + "\n")
    return "\n".join(chunks)


# Plan etapas-v1 Modo A válido (Execução e Integração pendentes) com `Arquivos:` disjuntos: se o motor aplicasse a
# regra da onda fora do coordenacao-v1, `fila.onda` apareceria com T1 e T2.
def etapas_modo_a_plan() -> str:
    body = "# Plan: etapas\n# Status: aprovado\n# Protocolo: etapas-v1\n# Modo: A\n"
    body += '- **Integração:** {"testes":"pendentes","prova":null,"commit":"pendente"}\n\n## Tasks\n'
    for tid in ("T1", "T2"):
        body += (f"### {tid}: capacidade\n- [ ] {tid} concluída\n- **Deps:** nenhuma\n"
                 f'- **Execução:** {{"estado":"pendente","local":null}}\n- **Arquivos:** `{tid.lower()}.py`\n')
    return body


T_DISJUNTAS = (("T1", "nenhuma", "`src/a.py`"), ("T2", "nenhuma", "`lib/b.py`"))

# Planos que NÃO são coordenacao-v1 Modo A e portanto mantêm a fila sem `onda` e `sem_arquivos`, mesmo com `Arquivos:` disjuntos.
SEM_ONDA_PLANS: dict[str, str] = {
    "coordenacao-v1-modo-b": wave_plan(*T_DISJUNTAS, mode="B"),
    "etapas-v1-modo-a": etapas_modo_a_plan(),
    "etapas-v1-modo-b": wave_plan(*T_DISJUNTAS, protocol="etapas-v1", mode="B"),
    "sem-marcador": wave_plan(*T_DISJUNTAS, protocol="", mode=None),
}

# Casos da onda paralela em coordenacao-v1 Modo A. `onda` e `sem_arquivos` são o resultado esperado do motor.
WAVE_CASES: list[dict] = [
    {"nome": "disjuntas-na-mesma-onda",
     "plan": wave_plan(("T1", "nenhuma", "`src/a.py`"), ("T2", "nenhuma", "`src/b.py`"), ("T3", "nenhuma", "`docs/x.md`")),
     "onda": ["T1", "T2", "T3"], "sem_arquivos": []},
    {"nome": "path-igual-fica-fora",
     "plan": wave_plan(("T1", "nenhuma", "`src/a.py`"), ("T2", "nenhuma", "`src/a.py`"), ("T3", "nenhuma", "`lib/c.py`")),
     "onda": ["T1", "T3"], "sem_arquivos": []},
    {"nome": "igualdade-ignora-caixa-barra-invertida-e-ponto-barra",
     "plan": wave_plan(("T1", "nenhuma", "`src/a.py`"), ("T2", "nenhuma", "`.\\SRC\\A.py`")),
     "onda": ["T1"], "sem_arquivos": []},
    {"nome": "prefixo-de-diretorio",
     "plan": wave_plan(("T1", "nenhuma", "`src/core/a.py`"), ("T2", "nenhuma", "`src/core`"),
                       ("T3", "nenhuma", "`src/core-extra/x.py`"), ("T4", "nenhuma", "`src/core/`")),
     "onda": ["T1", "T3"], "sem_arquivos": []},
    {"nome": "curinga-vale-como-diretorio-prefixo",
     "plan": wave_plan(("T1", "nenhuma", "`docs/x/*.md`"), ("T2", "nenhuma", "`docs/x/sub/t.py`"), ("T3", "nenhuma", "`docs/y/a.md`")),
     "onda": ["T1", "T3"], "sem_arquivos": []},
    {"nome": "curinga-no-nome-corta-no-diretorio",
     "plan": wave_plan(("T1", "nenhuma", "`src/foo*.py`"), ("T2", "nenhuma", "`src/bar.py`"), ("T3", "nenhuma", "`lib/a.py`")),
     "onda": ["T1", "T3"], "sem_arquivos": []},
    {"nome": "curinga-interrogacao-e-colchete",
     "plan": wave_plan(("T1", "nenhuma", "`src/a?.py`"), ("T2", "nenhuma", "`src/[bc].py`"), ("T3", "nenhuma", "`lib/x.py`")),
     "onda": ["T1", "T3"], "sem_arquivos": []},
    {"nome": "curinga-na-raiz-sobrepoe-tudo",
     "plan": wave_plan(("T1", "nenhuma", "`*.md`"), ("T2", "nenhuma", "`b.py`"), ("T3", "nenhuma", "`docs/c.md`")),
     "onda": ["T1"], "sem_arquivos": []},
    {"nome": "sem-arquivos-primeira-forma-onda-sozinha",
     "plan": wave_plan(("T1", "nenhuma", None), ("T2", "nenhuma", "`a.py`"), ("T3", "nenhuma", "`b.py`")),
     "onda": ["T1"], "sem_arquivos": ["T1"]},
    {"nome": "sem-arquivos-no-meio-nao-divide-onda",
     "plan": wave_plan(("T1", "nenhuma", "`a.py`"), ("T2", "nenhuma", None), ("T3", "nenhuma", "`b.py`")),
     "onda": ["T1", "T3"], "sem_arquivos": ["T2"]},
    {"nome": "lista-vazia-equivale-a-ausente",
     "plan": wave_plan(("T1", "nenhuma", ""), ("T2", "nenhuma", "``"), ("T3", "nenhuma", "`a.py`")),
     "onda": ["T1"], "sem_arquivos": ["T1", "T2"]},
    {"nome": "sem-crases-separa-por-virgula",
     "plan": wave_plan(("T1", "nenhuma", "src/a.py, src/b.py"), ("T2", "nenhuma", "src/b.py"), ("T3", "nenhuma", "lib/z.py")),
     "onda": ["T1", "T3"], "sem_arquivos": []},
    {"nome": "crases-ignoram-prosa-ao-redor",
     "plan": wave_plan(("T1", "nenhuma", "`src/a.py` e `src/b.py` (mais testes)"), ("T2", "nenhuma", "`src/b.py`"), ("T3", "nenhuma", "`lib/z.py`")),
     "onda": ["T1", "T3"], "sem_arquivos": []},
    {"nome": "dependencia-nao-elegivel-fica-fora",
     "plan": wave_plan(("T1", "nenhuma", "`a.py`"), ("T2", "T1", "`b.py`"), ("T3", "nenhuma", "`c.py`")),
     "onda": ["T1", "T3"], "sem_arquivos": []},
    {"nome": "ordem-numerica-guloso",
     "plan": wave_plan(("T10", "nenhuma", "`a.py`"), ("T2", "nenhuma", "`a.py`"), ("T3", "nenhuma", "`b.py`")),
     "onda": ["T2", "T3"], "sem_arquivos": []},
    # Normalização léxica: toda forma de escrever o mesmo arquivo ou a raiz tem de serializar as T* envolvidas.
    {"nome": "ponto-vale-como-raiz",
     "plan": wave_plan(("T1", "nenhuma", "`.`"), ("T2", "nenhuma", "`b.py`")),
     "onda": ["T1"], "sem_arquivos": []},
    {"nome": "ponto-barra-vale-como-raiz",
     "plan": wave_plan(("T1", "nenhuma", "`./`"), ("T2", "nenhuma", "`b.py`")),
     "onda": ["T1"], "sem_arquivos": []},
    {"nome": "raiz-depois-de-outra-fica-fora",
     "plan": wave_plan(("T1", "nenhuma", "`a.py`"), ("T2", "nenhuma", "`./.`"), ("T3", "nenhuma", "`lib/c.py`")),
     "onda": ["T1", "T3"], "sem_arquivos": []},
    {"nome": "barra-dupla-colapsa",
     "plan": wave_plan(("T1", "nenhuma", "`src/a.py`"), ("T2", "nenhuma", "`src//a.py`"), ("T3", "nenhuma", "`lib//c.py`")),
     "onda": ["T1", "T3"], "sem_arquivos": []},
    {"nome": "segmento-ponto-interno-some",
     "plan": wave_plan(("T1", "nenhuma", "`src/a.py`"), ("T2", "nenhuma", "`src/./a.py`"), ("T3", "nenhuma", "`lib/./c.py`")),
     "onda": ["T1", "T3"], "sem_arquivos": []},
    {"nome": "ponto-ponto-interno-e-resolvido",
     "plan": wave_plan(("T1", "nenhuma", "`src/a.py`"), ("T2", "nenhuma", "`a/../src/a.py`"),
                       ("T3", "nenhuma", "`lib/x/../c.py`"), ("T4", "nenhuma", "`lib/c.py`")),
     "onda": ["T1", "T3"], "sem_arquivos": []},
    {"nome": "ponto-ponto-que-escapa-da-raiz-sobrepoe-tudo",
     "plan": wave_plan(("T1", "nenhuma", "`../fora.py`"), ("T2", "nenhuma", "`b.py`")),
     "onda": ["T1"], "sem_arquivos": []},
    {"nome": "ponto-ponto-que-escapa-depois-de-outra-fica-fora",
     "plan": wave_plan(("T1", "nenhuma", "`src/a.py`"), ("T2", "nenhuma", "`a/../../y.py`"), ("T3", "nenhuma", "`lib/c.py`")),
     "onda": ["T1", "T3"], "sem_arquivos": []},
    {"nome": "curinga-depois-de-ponto-ponto",
     "plan": wave_plan(("T1", "nenhuma", "`x/../src/*.py`"), ("T2", "nenhuma", "`src/b.py`"), ("T3", "nenhuma", "`lib/c.py`")),
     "onda": ["T1", "T3"], "sem_arquivos": []},
    {"nome": "caixa-ascii-no-arquivo-e-no-diretorio",
     "plan": wave_plan(("T1", "nenhuma", "`Src/A.PY`"), ("T2", "nenhuma", "`src/a.py`"),
                       ("T3", "nenhuma", "`DOCS`"), ("T4", "nenhuma", "`docs/x.md`")),
     "onda": ["T1", "T3"], "sem_arquivos": []},
    # Path com qualquer caractere não ASCII não é comparável (ß/SS, É/é, NFC/NFD podem ser o mesmo arquivo): a T* roda
    # sozinha e vai para `sem_arquivos`, em vez de dividir onda com outra T* que poderia escrever o mesmo arquivo.
    {"nome": "nao-ascii-primeira-forma-onda-sozinha",
     "plan": wave_plan(("T1", "nenhuma", "`docs/Stra\u00dfe.md`"), ("T2", "nenhuma", "`docs/STRASSE.md`")),
     "onda": ["T1"], "sem_arquivos": ["T1"]},
    {"nome": "nao-ascii-no-meio-fica-de-fora-e-vai-para-sem-arquivos",
     "plan": wave_plan(("T1", "nenhuma", "`a.py`"), ("T2", "nenhuma", "`docs/caf\u00e9.md`"),
                       ("T3", "nenhuma", "`docs/cafe\u0301.md`"), ("T4", "nenhuma", "`docs/\u00c9.md`"),
                       ("T5", "nenhuma", "`docs/\u00e9.md`"), ("T6", "nenhuma", "`b.py`")),
     "onda": ["T1", "T6"], "sem_arquivos": ["T2", "T3", "T4", "T5"]},
    {"nome": "um-path-nao-ascii-contamina-a-T-inteira",
     "plan": wave_plan(("T1", "nenhuma", "`a.py`"), ("T2", "nenhuma", "`lib/x.py`, `lib/\u00e9.md`"), ("T3", "nenhuma", "`c.py`")),
     "onda": ["T1", "T3"], "sem_arquivos": ["T2"]},
    {"nome": "nao-ascii-sem-crases-e-espaco-nao-ascii-na-ponta",
     "plan": wave_plan(("T1", "nenhuma", "a.py"), ("T2", "nenhuma", "a.py\u00a0, d.py"), ("T3", "nenhuma", "docs/\u00e9.md, b.py"),
                       ("T4", "nenhuma", "c.py")),
     "onda": ["T1", "T4"], "sem_arquivos": ["T2", "T3"]},
    # Path absoluto ou com unidade (`/x`, `C:/x`, `C:\x`, `\\srv\x`, `d:x`) também não é comparável com `Arquivos:` relativos.
    {"nome": "absoluto-ou-com-unidade-fica-de-fora-e-vai-para-sem-arquivos",
     "plan": wave_plan(("T1", "nenhuma", "`a.py`"), ("T2", "nenhuma", "`C:/x/a.py`"), ("T3", "nenhuma", "`c:\\x\\a.py`"),
                       ("T4", "nenhuma", "`\\\\srv\\share\\a.py`"), ("T5", "nenhuma", "`D:rel.py`"),
                       ("T6", "nenhuma", "`/etc/a.py`"), ("T7", "nenhuma", "`b.py`")),
     "onda": ["T1", "T7"], "sem_arquivos": ["T2", "T3", "T4", "T5", "T6"]},
    {"nome": "absoluto-primeiro-forma-onda-sozinho",
     "plan": wave_plan(("T1", "nenhuma", "`/x/a.py`"), ("T2", "nenhuma", "`b.py`")),
     "onda": ["T1"], "sem_arquivos": ["T1"]},
    {"nome": "um-path-absoluto-contamina-a-T-inteira",
     "plan": wave_plan(("T1", "nenhuma", "`a.py`"), ("T2", "nenhuma", "`lib/x.py`, `C:\\y.py`"), ("T3", "nenhuma", "`c.py`")),
     "onda": ["T1", "T3"], "sem_arquivos": ["T2"]},
    # Grafias que o Windows resolve para outro arquivo: `:` em qualquer posição (stream alternativo, unidade), segmento
    # terminado em `.` ou espaço e caracteres que não existem em nome de arquivo. A T* roda sozinha e vai para `sem_arquivos`.
    {"nome": "dois-pontos-em-qualquer-posicao-serializa",
     "plan": wave_plan(("T1", "nenhuma", "`a.py`"), ("T2", "nenhuma", "`a.py:stream`"), ("T3", "nenhuma", "`src/b:c.py`"),
                       ("T4", "nenhuma", "`b.py`")),
     "onda": ["T1", "T4"], "sem_arquivos": ["T2", "T3"]},
    {"nome": "segmento-terminado-em-ponto-ou-espaco-serializa",
     "plan": wave_plan(("T1", "nenhuma", "`a.py`"), ("T2", "nenhuma", "`src./a.py`"), ("T3", "nenhuma", "`src /a.py`"),
                       ("T4", "nenhuma", "`lib/c.py.`"), ("T5", "nenhuma", "`.../x.py`"), ("T6", "nenhuma", "`b.py`")),
     "onda": ["T1", "T6"], "sem_arquivos": ["T2", "T3", "T4", "T5"]},
    {"nome": "caracteres-invalidos-no-windows-serializam",
     "plan": wave_plan(("T1", "nenhuma", "`a.py`"), ("T2", "nenhuma", "`src/<a>.py`"), ("T3", "nenhuma", "`src/a\"b.py`"),
                       ("T4", "nenhuma", "`src/a|b.py`"), ("T5", "nenhuma", "`src/a>.py`"), ("T6", "nenhuma", "`b.py`")),
     "onda": ["T1", "T6"], "sem_arquivos": ["T2", "T3", "T4", "T5"]},
    # Quebra de linha só em \r\n, \r e \n nos dois motores. Separador Unicode e controles (U+2028, U+2029, \x0b, \x85,
    # \x1c) ficam dentro da linha: o segundo path continua declarado pela T* e a serializa com quem escreve o mesmo arquivo.
    {"nome": "separador-unicode-entre-paths-nao-quebra-a-linha",
     "plan": wave_plan(("T1", "nenhuma", "`src/a.py` `src/b.py`"), ("T2", "nenhuma", "`src/b.py`"),
                       ("T3", "nenhuma", "`lib/c.py`")),
     "onda": ["T1", "T3"], "sem_arquivos": []},
    {"nome": "separador-unicode-sem-crases-torna-o-path-nao-ascii",
     "plan": wave_plan(("T1", "nenhuma", "`lib/c.py`"), ("T2", "nenhuma", "src/a.py src/b.py"),
                       ("T3", "nenhuma", "`src/b.py`")),
     "onda": ["T1", "T3"], "sem_arquivos": ["T2"]},
    {"nome": "outros-separadores-e-controles-nao-quebram-a-linha",
     "plan": wave_plan(("T1", "nenhuma", "`a.py` `b.py`"), ("T2", "nenhuma", "`b.py`"),
                       ("T3", "nenhuma", "`c.py`\x0b`d.py`"), ("T4", "nenhuma", "`d.py`"),
                       ("T5", "nenhuma", "`e.py`\u0085`f.py`"), ("T6", "nenhuma", "`f.py`"),
                       ("T7", "nenhuma", "`g.py`\x1c`h.py`"), ("T8", "nenhuma", "`h.py`")),
     "onda": ["T1", "T3", "T5", "T7"], "sem_arquivos": []},
    # `\r` isolado é quebra de linha: o texto depois dele deixa de ser a linha `Arquivos:` (regra documentada, igual nos dois motores).
    {"nome": "cr-isolado-quebra-a-linha",
     "plan": wave_plan(("T1", "nenhuma", "`src/a.py`\r`src/b.py`"), ("T2", "nenhuma", "`src/b.py`")),
     "onda": ["T1", "T2"], "sem_arquivos": []},
    {"nome": "ponto-e-ponto-ponto-continuam-comparaveis",
     "plan": wave_plan(("T1", "nenhuma", "`a.py`"), ("T2", "nenhuma", "`./src/../a.py`"), ("T3", "nenhuma", "`lib/./c.py`")),
     "onda": ["T1", "T3"], "sem_arquivos": []},
]


# Plan coordenacao-v1 Modo A com a linha Deps indentada (dois espaços em T1 e T4, tab em T2): o Python aparta a linha
# com `strip()`, então o motor PowerShell precisa aceitar a mesma indentação. T2 depende de T1; T3 repete `a.py` de T1.
def indented_deps_plan() -> str:
    indents = {"T1": "  ", "T2": "\t", "T3": "", "T4": "  "}
    plan = wave_plan(("T1", "nenhuma", "`a.py`"), ("T2", "T1", "`b.py`"), ("T3", "nenhuma", "`a.py`"), ("T4", "nenhuma", "`c.py`"))
    current, lines = "", []
    for line in plan.split("\n"):
        if line.startswith("### T"):
            current = line[4:].split(":", 1)[0]
        lines.append(indents[current] + line if line.startswith("- **Deps:**") else line)
    return "\n".join(lines)


# Variantes do mesmo plan com outros terminadores de linha: `\r` isolado (Mac antigo), `\r\n` e mistura dos três.
# O fim de linha é normalizado na leitura, então a fila, a onda e a etapa não podem depender dele.
def line_ending_variants(plan: str) -> dict[str, str]:
    lines = plan.split("\n")
    mixed = "".join(line + ("\r", "\r\n", "\n")[index % 3] for index, line in enumerate(lines[:-1])) + lines[-1]
    return {"lf": plan, "cr-isolado": "\r".join(lines), "crlf": "\r\n".join(lines), "misto": mixed}


# Grava o plan byte a byte, sem a tradução de `\n` do modo texto, para os terminadores da fixture chegarem ao motor intactos.
def seed_plan_bytes(repo: Path, plan: str) -> None:
    phase = seed_phase(seed_vibeflow(repo), "phase-1-a", "plan.md")
    (phase / "plan.md").write_bytes(plan.encode("utf-8"))


# Cria a fixture de um caso de etapa na phase-1-a: spec sempre, plan e review só quando o caso os define.
def seed_etapa_case(repo: Path, case: dict) -> None:
    vf = seed_vibeflow(repo)
    phase = seed_phase(vf, "phase-1-a", "spec.md")
    if case["plan"] is not None:
        write_plan(phase, case["plan"])
    if isinstance(case["review"], bytes):
        (phase / "review.md").write_bytes(case["review"])
    elif case["review"] is not None:
        (phase / "review.md").write_text(case["review"], encoding="utf-8")


class PythonContracts(unittest.TestCase):
    """Verifica inventário, alvo com plan, apply direto e gitignore."""

    def setUp(self) -> None:
        self.repo = Path.cwd() / f".vibe-implement-python-{uuid.uuid4().hex}"
        self.repo.mkdir()

    def tearDown(self) -> None:
        remove_fixture_tree(self.repo)

    # Executa Git no repositório temporário sem shell, preservando erros como evidência do teste.
    def _git(self, repo: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
        # O repositório Git da fixture fica fora do worktree para permitir limpeza estrita no sandbox.
        git_dir = repo.parent / f"{repo.name}-git"
        git_env = os.environ | {"GIT_DIR": str(git_dir), "GIT_WORK_TREE": str(repo)}
        return subprocess.run(
            ["git", *arguments],
            cwd=repo,
            env=git_env,
            capture_output=True,
            text=True, encoding="utf-8",
            check=True,
        )

    def test_init_ausente(self) -> None:
        process, report = invoke(self.repo, check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("INIT_AUSENTE", process.stderr)
        self.assertIsNone(report)

    def test_creates_missing_phases(self) -> None:
        """Mantém o stdout focado no alvo e cria apenas a estrutura phases ausente."""
        seed_vibeflow(self.repo)
        _, report = invoke(self.repo)
        self.assertEqual(REPORT_KEYS, set(report))
        self.assertIsNone(report["alvo"])
        self.assertIsNone(report["fila"])
        self.assertIsNone(report["etapa"])
        self.assertEqual(0, report["rodadas_correcao"])
        self.assertTrue((self.repo / ".vibeflow" / "phases" / ".gitkeep").is_file())
        self.assertNotIn("wip", report)

    def test_reuse_plan_folder_does_not_create_phase_two(self) -> None:
        """Seleciona o plan existente sem expor ou criar um segundo artefato."""
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-a", "spec.md", "plan.md")
        _, report = invoke(self.repo)
        self.assertEqual("phase-1-a", report["alvo"]["dir"])
        self.assertFalse((vf / "phases" / "phase-2-a").exists())

    def test_alvo_is_highest_n_with_plan(self) -> None:
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-old", "plan.md")
        seed_phase(vf, "phase-3-new", "plan.md")
        _, report = invoke(self.repo)
        self.assertEqual("phase-3-new", report["alvo"]["dir"])
        self.assertEqual(3, report["alvo"]["n"])

    def test_ignores_phase_without_plan_when_choosing_alvo(self) -> None:
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-2-so-spec", "spec.md")
        seed_phase(vf, "phase-1-com-plan", "plan.md")
        _, report = invoke(self.repo)
        self.assertEqual("phase-1-com-plan", report["alvo"]["dir"])

    def test_dir_without_plan_is_alvo(self) -> None:
        """Aceita override explícito mesmo quando a phase ainda não tem plan."""
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-so-spec", "spec.md")
        _, report = invoke(self.repo, "--dir", "phase-1-so-spec")
        self.assertEqual("phase-1-so-spec", report["alvo"]["dir"])
        self.assertIsNone(report["fila"])

    def test_dir_missing_or_invalid(self) -> None:
        seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--dir", "phase-9-sumiu", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("FASE_AUSENTE", process.stderr)
        process, _ = invoke(self.repo, "--dir", "nao-e-fase", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("FASE_AUSENTE", process.stderr)

    def test_historical_implement_does_not_select_a_target(self) -> None:
        """Arquivo histórico isolado não substitui o plan como fonte do alvo."""
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-9-historico", "implement.md")
        _, report = invoke(self.repo)
        self.assertIsNone(report["alvo"])
        self.assertIsNone(report["fila"])

    def test_stdout_omits_full_phase_inventory(self) -> None:
        """Emite apenas alvo, fila e avisos, mesmo com muitas phases no repositório."""
        vf = seed_vibeflow(self.repo)
        for number in range(1, 21):
            seed_phase(vf, f"phase-{number}-historico", "plan.md")
        process, report = invoke(self.repo)
        self.assertEqual(REPORT_KEYS, set(report))
        self.assertEqual("phase-20-historico", report["alvo"]["dir"])
        self.assertNotIn("phase-1-historico", process.stdout)

    # Confirma que o JSON transitório não cria relatório nem altera o gitignore de init.
    def test_stdout_report_does_not_mutate_workspace(self) -> None:
        vf = seed_vibeflow(self.repo)
        original = (vf / ".gitignore").read_bytes()
        _, report = invoke(self.repo)
        self.assertIsNotNone(report)
        self.assertEqual(original, (vf / ".gitignore").read_bytes())
        self.assertEqual([], list(vf.glob("*-report.json")))

    def test_apply_does_not_create_implement_file(self) -> None:
        """Apply reaproveita o plan sem criar implement.md para novas execuções."""
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-a", "plan.md")
        _, report = invoke(self.repo, "--apply")
        dest = vf / "phases" / "phase-1-a" / "implement.md"
        self.assertFalse(dest.exists())
        self.assertEqual("phase-1-a", report["alvo"]["dir"])
        self.assertNotIn("wip", report)

    def test_apply_reuses_plan_folder(self) -> None:
        """Apply mantém o alvo na phase existente e deixa o plan como único registro."""
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-a", "spec.md", "plan.md")
        _, report = invoke(self.repo, "--apply")
        dest = vf / "phases" / "phase-1-a" / "implement.md"
        self.assertFalse(dest.exists())
        self.assertFalse((vf / "phases" / "phase-2-a").exists())
        self.assertEqual("phase-1-a", report["alvo"]["dir"])
        self.assertNotIn("wip", report)

    def test_apply_preserves_existing_historical_implement(self) -> None:
        """Apply conserva byte a byte um implement.md legado sem depender dele."""
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-a", "plan.md", "implement.md")
        original = b"# fatia 1\n\x00historico\n"
        (vf / "phases" / "phase-1-a" / "implement.md").write_bytes(original)
        _, report = invoke(self.repo, "--apply")
        self.assertEqual(original, (vf / "phases" / "phase-1-a" / "implement.md").read_bytes())
        self.assertEqual("phase-1-a", report["alvo"]["dir"])
        self.assertNotIn("wip", report)

    def test_apply_without_alvo_or_slug(self) -> None:
        vf = seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--apply", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("IMPLEMENT_SEM_ALVO", process.stderr)

    def test_slug_creates_avulsa(self) -> None:
        """Slug explícito cria somente a pasta alvo, sem arquivo de execução."""
        vf = seed_vibeflow(self.repo)
        _, report = invoke(self.repo, "--apply", "--slug", "hotfix-cor")
        dest = vf / "phases" / "phase-1-hotfix-cor"
        self.assertTrue(dest.is_dir())
        self.assertFalse((dest / "implement.md").exists())
        self.assertEqual("phase-1-hotfix-cor", report["alvo"]["dir"])
        self.assertNotIn("wip", report)

    def test_phases_file_is_unexpected(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "phases").write_text("nao", encoding="utf-8")
        process, _ = invoke(self.repo, check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("PHASES_INESPERADO", process.stderr)

    def test_fila_null_without_plan(self) -> None:
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-so-spec", "spec.md")
        _, report = invoke(self.repo, "--dir", "phase-1-so-spec")
        self.assertIsNone(report["fila"])

    def test_fila_null_when_alvo_ausente(self) -> None:
        seed_vibeflow(self.repo)
        _, report = invoke(self.repo)
        self.assertIsNone(report["alvo"])
        self.assertIsNone(report["fila"])

    def test_fila_one_eligible(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = seed_phase(vf, "phase-1-a", "plan.md")
        write_plan(phase, plan_tasks(("T1", "x", "nenhuma"), ("T2", " ", "T1")))
        _, report = invoke(self.repo)
        fila = report["fila"]
        self.assertEqual("ok", fila["parse"])
        self.assertEqual(["T1"], fila["concluidas"])
        self.assertEqual(["T2"], fila["abertas"])
        self.assertEqual(["T2"], fila["elegiveis"])
        self.assertEqual([], fila["bloqueadas"])
        self.assertEqual([], fila["avisos"])

    def test_fila_two_eligible(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = seed_phase(vf, "phase-1-a", "plan.md")
        write_plan(phase, plan_tasks(("T1", " ", "nenhuma"), ("T4", " ", "nenhuma")))
        _, report = invoke(self.repo)
        fila = report["fila"]
        self.assertEqual("ok", fila["parse"])
        self.assertEqual(["T1", "T4"], fila["abertas"])
        self.assertEqual(["T1", "T4"], fila["elegiveis"])
        self.assertEqual([], fila["concluidas"])
        self.assertEqual([], fila["bloqueadas"])

    # Garante que texto de organização fora de T* não altera a fila mecânica.
    def test_fila_ignores_texto_fora_do_contrato(self) -> None:
        """Prova que preparo, paralelização e checkpoints não deslocam a fila compacta."""
        vf = seed_vibeflow(self.repo)
        phase = seed_phase(vf, "phase-1-a", "plan.md")
        write_plan(
            phase,
            "# Plan\n\n## Prontidão das provas\n\n- Requisitos verificados: Python disponível no CI\n"
            "- Ausências e ação na fila: nenhuma\n\n"
            "## Tasks\n\n### T1: entrega inicial\n\n- [ ] T1 concluída\n"
            "- **Spec:** A1\n- **O quê:** resultado inicial\n- **Aceite:** observável\n"
            "- **Verificação:** `python -m unittest`\n- **Deps:** nenhuma\n\n"
            "- **Checkpoint de retomada:** estado salvo\n  - Próximo passo: revisar\n"
            "  - Paths da prova: `src/a.py`=abc\n  - Git: `HEAD=def`\n"
            "  - Prova: válida no snapshot\n\n"
            "## Paralelização (opcional)\n\n- texto sem efeito na fila\n\n"
            "## Checkpoint de review (opcional)\n\n- revisar contrato compartilhado\n\n"
            "### T2: entrega dependente\n\n- [ ] T2 concluída\n- **Deps:** T1\n",
        )
        _, report = invoke(self.repo)
        fila = report["fila"]
        self.assertEqual(["T1"], fila["elegiveis"])
        self.assertEqual([{"id": "T2", "deps": ["T1"]}], fila["bloqueadas"])

    def test_fila_dep_blocks(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = seed_phase(vf, "phase-1-a", "plan.md")
        write_plan(phase, plan_tasks(("T1", " ", "nenhuma"), ("T2", " ", "T1")))
        _, report = invoke(self.repo)
        fila = report["fila"]
        self.assertEqual("ok", fila["parse"])
        self.assertEqual(["T1"], fila["elegiveis"])
        self.assertEqual([{"id": "T2", "deps": ["T1"]}], fila["bloqueadas"])
        self.assertEqual(["T1", "T2"], fila["abertas"])

    def test_fila_missing_concluida_is_parcial(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = seed_phase(vf, "phase-1-a", "plan.md")
        write_plan(
            phase,
            "### T1: sem checkbox\n\n- **Deps:** nenhuma\n\n### T2: ok\n\n- [ ] T2 concluída\n- **Deps:** nenhuma\n",
        )
        _, report = invoke(self.repo)
        fila = report["fila"]
        self.assertEqual("parcial", fila["parse"])
        self.assertEqual(["T2"], fila["elegiveis"])
        self.assertNotIn("T1", fila["abertas"])
        self.assertNotIn("T1", fila["elegiveis"])
        self.assertTrue(any("T1" in aviso for aviso in fila["avisos"]))

    def test_fila_ausente_without_task_headings(self) -> None:
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-a", "plan.md")
        _, report = invoke(self.repo)
        fila = report["fila"]
        self.assertEqual("ausente", fila["parse"])
        self.assertEqual([], fila["elegiveis"])
        self.assertEqual([], fila["avisos"])

    def test_mvp_fila_uses_only_special_plan(self) -> None:
        """Seleciona somente a fila do baseline MVP, isolada das phases numeradas."""
        vf = seed_vibeflow(self.repo)
        phase = seed_phase(vf, "phase-9-outra", "plan.md")
        write_plan(phase, plan_tasks(("T1", " ", "nenhuma")))
        seed_mvp(vf, plan_tasks(("T7", " ", "nenhuma")))
        _, report = invoke(self.repo, "--mvp")
        self.assertEqual("mvp", report["alvo"]["kind"])
        self.assertEqual(["T7"], report["fila"]["elegiveis"])
        self.assertTrue(report["analyze_gate"]["pronto"])

    def test_mvp_apply_refuses_missing_draft_and_blocked_analyze(self) -> None:
        for status, verdict, expected in (
            (None, "limpo", "IMPLEMENT_ANALYZE_AUSENTE"),
            ("rascunho", "limpo", "IMPLEMENT_ANALYZE_RASCUNHO"),
            ("aprovado", "bloqueado", "IMPLEMENT_ANALYZE_BLOQUEADO"),
        ):
            with self.subTest(expected=expected):
                repo = self.repo / expected
                repo.mkdir()
                vf = seed_vibeflow(repo)
                seed_mvp(vf, plan_tasks(("T1", " ", "nenhuma")), status, verdict)
                process, _ = invoke(repo, "--apply", "--mvp", check=False)
                self.assertNotEqual(0, process.returncode)
                self.assertIn(expected, process.stderr)
                self.assertFalse((vf / "mvp" / "implement.md").exists())

    def test_mvp_apply_preserves_existing_historical_implement(self) -> None:
        """Apply no MVP preserva o arquivo legado e não exige um novo implement.md."""
        vf = seed_vibeflow(self.repo)
        mvp = seed_mvp(vf, plan_tasks(("T1", " ", "nenhuma")))
        original = b"# Fatia T1\n\x00\n## Fatia T2\n"
        (mvp / "implement.md").write_bytes(original)
        _, report = invoke(self.repo, "--apply", "--mvp")
        self.assertEqual(original, (mvp / "implement.md").read_bytes())
        self.assertEqual("mvp", report["alvo"]["kind"])
        self.assertTrue(report["analyze_gate"]["pronto"])
        self.assertNotIn("wip", report)
        self.assertEqual([], [item.name for item in (vf / "phases").iterdir() if item.is_dir()])

    def test_mvp_etapa_usa_o_review_do_baseline(self) -> None:
        """No MVP a etapa vem do review do baseline e o gate de analyze continua no JSON."""
        vf = seed_vibeflow(self.repo)
        mvp = seed_mvp(vf, FILA_CONCLUIDA)
        (mvp / "review.md").write_text(review_text(status="aprovado", vigente="Approve"), encoding="utf-8")
        _, report = invoke(self.repo, "--mvp")
        self.assertEqual(REPORT_KEYS | {"analyze_gate"}, set(report))
        self.assertEqual("concluida", report["etapa"])
        # Aprovação do baseline não prevalece sobre uma correção histórica ainda aberta.
        review = mvp / "review.md"
        review.write_text(review_text(status="aprovado", blockers=(NIT_ABERTO,), vigente="Approve com defer"), encoding="utf-8")
        before = tree_snapshot(self.repo)
        _, report = invoke(self.repo, "--mvp")
        self.assertEqual("corrigir", report["etapa"])
        self.assertEqual(before, tree_snapshot(self.repo))

    def test_etapa_e_rodadas_por_fixture(self) -> None:
        """Cada estado da phase vira a etapa esperada, e o motor não escreve nada para derivá-la."""
        for case in ETAPA_CASES:
            with self.subTest(case["nome"]):
                repo = self.repo / case["nome"]
                repo.mkdir()
                seed_etapa_case(repo, case)
                before = tree_snapshot(repo)
                _, report = invoke(repo, "--dir", "phase-1-a")
                self.assertEqual(case["etapa"], report["etapa"])
                self.assertEqual(case["rodadas"], report["rodadas_correcao"])
                self.assertEqual(case["avisos"], len(report["avisos"]), report["avisos"])
                self.assertEqual(before, tree_snapshot(repo))

    def test_mvp_rejects_phase_selectors(self) -> None:
        seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--mvp", "--slug", "produto", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("MODO_INVALIDO", process.stderr)

    def test_independent_task_completions_preserve_queue_and_task_commit_attribution(self) -> None:
        """Compara fila, conteúdo final e commits Git reais após retornos serial ou fora de ordem."""
        results = {}
        for execution, completion_order in (
            ("sequential", ("T1", "T2")),
            ("delegated", ("T2", "T1")),
        ):
            repo = self.repo / execution
            repo.mkdir()
            vf = seed_vibeflow(repo)
            phase = seed_phase(vf, "phase-1-fixture", "plan.md")
            plan = plan_tasks(("T1", " ", "nenhuma"), ("T2", " ", "nenhuma"), ("T3", " ", "T1, T2"))
            write_plan(phase, plan)

            # Cada cenário usa Git real; o commit inicial separa o baseline das entregas das tasks.
            self._git(repo, "init", "--quiet")
            self._git(repo, "config", "user.name", "VibeFlow Test")
            self._git(repo, "config", "user.email", "vibeflow-test@example.invalid")
            self._git(repo, "add", "--", ".vibeflow")
            self._git(repo, "commit", "--quiet", "-m", "fixture: baseline")

            _, report = invoke(repo)
            self.assertEqual(["T1", "T2"], report["fila"]["elegiveis"])
            self.assertEqual([{"id": "T3", "deps": ["T1", "T2"]}], report["fila"]["bloqueadas"])

            # Integra cada retorno em path exclusivo e registra a alteração real no Git.
            for index, task in enumerate(completion_order):
                source_path = f"src/{task.lower()}.txt"
                source_file = repo / source_path
                source_file.parent.mkdir(parents=True, exist_ok=True)
                source_file.write_text(f"resultado de {task}\n", encoding="utf-8")
                plan = plan.replace(f"- [ ] {task} concluída", f"- [x] {task} concluída", 1)
                write_plan(phase, plan)
                plan_path = ".vibeflow/phases/phase-1-fixture/plan.md"
                self._git(repo, "add", "--", plan_path, source_path)
                self._git(repo, "commit", "--quiet", "-m", f"task({task}): resultado {task}")
                _, report = invoke(repo)
                if index == 0:
                    remaining = completion_order[1]
                    self.assertEqual([remaining], report["fila"]["elegiveis"])
                    self.assertEqual([{"id": "T3", "deps": [remaining]}], report["fila"]["bloqueadas"])
                else:
                    self.assertEqual(["T3"], report["fila"]["elegiveis"])
                    self.assertEqual([], report["fila"]["bloqueadas"])

            # A dependente só é liberada depois dos dois commits independentes.
            source_path = "src/t3.txt"
            source_file = repo / source_path
            source_file.parent.mkdir(parents=True, exist_ok=True)
            source_file.write_text("resultado de T3\n", encoding="utf-8")
            plan = plan.replace("- [ ] T3 concluída", "- [x] T3 concluída", 1)
            write_plan(phase, plan)
            plan_path = ".vibeflow/phases/phase-1-fixture/plan.md"
            self._git(repo, "add", "--", plan_path, source_path)
            self._git(repo, "commit", "--quiet", "-m", "task(T3): resultado T3")
            _, report = invoke(repo)

            # Lê mensagens e paths dos commits produzidos pelo Git, não de metadados montados no teste.
            task_commits = {}
            for line in self._git(repo, "log", "--format=%s%x09%H").stdout.splitlines():
                message, commit_hash = line.split("\t", 1)
                if not message.startswith("task("):
                    continue
                task = message[len("task("):].split(")", 1)[0]
                changed_paths = sorted(
                    path
                    for path in self._git(repo, "show", "--format=", "--name-only", commit_hash).stdout.splitlines()
                    if path
                )
                task_commits[task] = {"message": message, "paths": changed_paths}

            self.assertEqual([], report["fila"]["abertas"])
            self.assertEqual([], report["fila"]["elegiveis"])
            self.assertEqual([], self._git(repo, "status", "--porcelain").stdout.splitlines())
            expected_plan_path = ".vibeflow/phases/phase-1-fixture/plan.md"
            for task in ("T1", "T2", "T3"):
                self.assertEqual(
                    [expected_plan_path, f"src/{task.lower()}.txt"],
                    task_commits[task]["paths"],
                )
                self.assertEqual(f"task({task}): resultado {task}", task_commits[task]["message"])

            final_state = {
                path: (repo / path).read_bytes()
                for path in (expected_plan_path, "src/t1.txt", "src/t2.txt", "src/t3.txt")
            }
            results[execution] = {
                "fila": {
                    key: report["fila"][key]
                    for key in ("concluidas", "abertas", "elegiveis", "bloqueadas")
                },
                "commits": task_commits,
                "final_state": final_state,
            }

        self.assertEqual(results["sequential"], results["delegated"])
        commits = results["sequential"]["commits"]
        self.assertEqual({"T1", "T2", "T3"}, set(commits))





# Verifica se existe uma versão real de PowerShell 7, única suportada pelo motor gêmeo.
@cache
def powershell7() -> str | None:
    """Descobre uma vez por processo; simulações de ambiente devem limpar o cache."""
    executable = shutil.which("pwsh")
    if not executable:
        return None
    probe = subprocess.run([executable, "-NoProfile", "-Command", "$PSVersionTable.PSVersion.Major"], capture_output=True, text=True, encoding="utf-8", check=False)
    return executable if probe.stdout.strip().isdigit() and int(probe.stdout.strip()) >= 7 else None


# Executa o motor PowerShell no repositório da fixture e decodifica o JSON; falha do motor vira erro do teste com o stderr.
def invoke_powershell(repo: Path, *arguments: str) -> dict:
    process = subprocess.run(
        [powershell7(), "-NoProfile", "-File", str(POWERSHELL_SCRIPT), "-Root", str(repo), *arguments],
        capture_output=True,
        text=True, encoding="utf-8",
        check=False,
    )
    if process.returncode != 0:
        raise AssertionError(f"implement.ps1 falhou ({process.returncode}): {process.stderr}")
    return json.loads(process.stdout)


# Grava uma phase-1-a só com o plan da fixture, sem Git: basta para a leitura da fila e da onda.
def seed_plan_fixture(repo: Path, plan: str) -> None:
    write_plan(seed_phase(seed_vibeflow(repo), "phase-1-a", "plan.md"), plan)


@unittest.skipUnless(powershell7(), "PowerShell 7 indisponível")
class PowershellParity(unittest.TestCase):
    """Confere paridade do alvo, da fila e da preservação entre os motores."""

    def setUp(self) -> None:
        self.repo = Path.cwd() / f".vibe-implement-ps-{uuid.uuid4().hex}"
        self.repo.mkdir()

    def tearDown(self) -> None:
        remove_fixture_tree(self.repo)

    # Confirma que o PowerShell entrega o alvo sem criar implement.md ou relatório.
    def test_apply_reuse_same_path(self) -> None:
        """Apply mantém o destino existente e não prepara um registro duplicado."""
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-lock-bloco", "spec.md", "plan.md")
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply"],
            capture_output=True,
            text=True, encoding="utf-8",
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        dest = vf / "phases" / "phase-1-lock-bloco" / "implement.md"
        self.assertFalse(dest.exists())
        self.assertTrue((vf / "phases" / "phase-1-lock-bloco" / "plan.md").is_file())
        report = json.loads(process.stdout)
        self.assertFalse((vf / "implement-report.json").exists())
        self.assertEqual(REPORT_KEYS, set(report))
        self.assertNotIn("wip", report)

    # Confirma que o motor PowerShell preserva o conteúdo do implement já existente.
    def test_apply_preserves_existing_file(self) -> None:
        """Apply não altera bytes de um implement.md histórico já presente."""
        vf = seed_vibeflow(self.repo)
        phase = seed_phase(vf, "phase-1-lock-bloco", "spec.md", "plan.md", "implement.md")
        original = b"# implement\n\x00historico\n"
        (phase / "implement.md").write_bytes(original)
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply"],
            capture_output=True,
            text=True, encoding="utf-8",
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual(original, (phase / "implement.md").read_bytes())
        report = json.loads(process.stdout)
        self.assertFalse((vf / "implement-report.json").exists())
        self.assertEqual("phase-1-lock-bloco", report["alvo"]["dir"])
        self.assertNotIn("wip", report)

    # Compara fila Python e PowerShell pela saída transitória em JSON.
    def test_fila_parity_dep_blocks(self) -> None:
        """Mantém fila equivalente e stdout compacto nos dois motores."""
        vf = seed_vibeflow(self.repo)
        phase = seed_phase(vf, "phase-1-a", "plan.md")
        write_plan(phase, plan_tasks(("T1", " ", "nenhuma"), ("T2", " ", "T1")))
        for number in range(2, 21):
            seed_phase(vf, f"phase-{number}-historico", "spec.md")
        _, py_report = invoke(self.repo)
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo)],
            capture_output=True,
            text=True, encoding="utf-8",
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        ps_report = json.loads(process.stdout)
        self.assertFalse((vf / "implement-report.json").exists())
        self.assertEqual(REPORT_KEYS, set(py_report))
        self.assertEqual(REPORT_KEYS, set(ps_report))
        self.assertNotIn("phase-20-historico", process.stdout)
        self.assertEqual(py_report["alvo"], ps_report["alvo"])
        self.assertEqual(py_report["fila"]["elegiveis"], ps_report["fila"]["elegiveis"])
        self.assertEqual(py_report["fila"]["bloqueadas"], ps_report["fila"]["bloqueadas"])
        self.assertEqual(["T1"], ps_report["fila"]["elegiveis"])
        self.assertEqual([{"id": "T2", "deps": ["T1"]}], ps_report["fila"]["bloqueadas"])

    # Confirma que o gate MVP e a fila chegam no stdout sem relatório persistido.
    def test_mvp_apply_same_path_and_gate(self) -> None:
        """Apply no MVP mantém o gate e a fila sem criar implement.md."""
        vf = seed_vibeflow(self.repo)
        mvp = seed_mvp(vf, plan_tasks(("T1", " ", "nenhuma")))
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply", "-Mvp"],
            capture_output=True,
            text=True, encoding="utf-8",
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertFalse((mvp / "implement.md").exists())
        report = json.loads(process.stdout)
        self.assertFalse((vf / "implement-report.json").exists())
        self.assertEqual("mvp", report["alvo"]["kind"])
        self.assertEqual(REPORT_KEYS | {"analyze_gate"}, set(report))
        self.assertTrue(report["analyze_gate"]["pronto"])
        self.assertEqual(["T1"], report["fila"]["elegiveis"])
        self.assertNotIn("wip", report)

    # Compara etapa, rodadas e avisos dos dois motores, com as mesmas fixtures do motor Python, sem escrita no disco.
    def test_etapa_parity_por_fixture(self) -> None:
        """Python e PowerShell informam o mesmo estado para cada fixture de etapa."""
        for case in ETAPA_CASES:
            with self.subTest(case["nome"]):
                repo = self.repo / case["nome"]
                repo.mkdir()
                seed_etapa_case(repo, case)
                before = tree_snapshot(repo)
                _, py_report = invoke(repo, "--dir", "phase-1-a")
                process = subprocess.run(
                    [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(repo), "-Dir", "phase-1-a"],
                    capture_output=True,
                    text=True, encoding="utf-8",
                    check=False,
                )
                self.assertEqual(0, process.returncode, process.stderr)
                ps_report = json.loads(process.stdout)
                self.assertEqual(case["etapa"], ps_report["etapa"])
                self.assertEqual(case["rodadas"], ps_report["rodadas_correcao"])
                # Compara também o texto Unicode dos avisos no contrato comum dos motores.
                self.assertEqual(case["avisos"], len(ps_report["avisos"]))
                self.assertEqual(py_report["avisos"], ps_report["avisos"])
                self.assertEqual(before, tree_snapshot(repo))

    # A onda e as T* sem arquivos saem idênticas nos dois motores, inclusive array de um elemento e normalização de paths.
    def test_onda_parity_por_fixture(self) -> None:
        """Python e PowerShell emitem a mesma fila, com o mesmo resultado esperado para cada caso."""
        for case in WAVE_CASES:
            with self.subTest(case["nome"]):
                repo = self.repo / case["nome"]
                repo.mkdir()
                seed_plan_fixture(repo, case["plan"])
                before = tree_snapshot(repo)
                _, py_report = invoke(repo, "--dir", "phase-1-a")
                ps_report = invoke_powershell(repo, "-Dir", "phase-1-a")
                self.assertEqual(case["onda"], ps_report["fila"]["onda"])
                self.assertEqual(case["sem_arquivos"], ps_report["fila"]["sem_arquivos"])
                self.assertEqual(py_report, ps_report)
                self.assertEqual(before, tree_snapshot(repo))

    # Fora do coordenacao-v1 Modo A o PowerShell também mantém a fila anterior, sem `onda` nem `sem_arquivos`.
    def test_sem_onda_parity_fora_do_modo_a_coordenado(self) -> None:
        """Modo B, etapas-v1 e plan sem marcador têm o mesmo relatório nos dois motores, sem campos de onda."""
        for nome, plan in SEM_ONDA_PLANS.items():
            with self.subTest(nome):
                repo = self.repo / nome
                repo.mkdir()
                seed_plan_fixture(repo, plan)
                _, py_report = invoke(repo, "--dir", "phase-1-a")
                ps_report = invoke_powershell(repo, "-Dir", "phase-1-a")
                self.assertEqual({"parse", "concluidas", "abertas", "elegiveis", "bloqueadas", "avisos"}, set(ps_report["fila"]))
                self.assertEqual(py_report, ps_report)

    # Plan inteiro com `\r` isolado, `\r\n` ou mistura como terminador e Deps indentada: os motores dão o mesmo relatório.
    def test_fim_de_linha_e_deps_indentada_parity(self) -> None:
        """Fila, onda e etapa idênticas nos dois motores, para qualquer terminador de linha do plan."""
        for nome, plan in line_ending_variants(indented_deps_plan()).items():
            with self.subTest(nome):
                repo = self.repo / nome
                repo.mkdir()
                seed_plan_bytes(repo, plan)
                _, py_report = invoke(repo, "--dir", "phase-1-a")
                ps_report = invoke_powershell(repo, "-Dir", "phase-1-a")
                self.assertEqual(["T1", "T4"], ps_report["fila"]["onda"])
                self.assertEqual("implementar", ps_report["etapa"])
                self.assertEqual(py_report, ps_report)


# Exercita a onda paralela do coordenacao-v1 Modo A pelo motor real: relatório e efeitos de provas locais no disco.
class WaveContracts(unittest.TestCase):
    # Isola fixtures por teste; o tearDown remove a árvore inteira, inclusive objetos Git read-only do Windows.
    def setUp(self) -> None:
        self.repo = Path.cwd() / f".vibe-onda-{uuid.uuid4().hex}"
        self.repo.mkdir()

    def tearDown(self) -> None:
        remove_fixture_tree(self.repo)

    # Opera apenas o Git da fixture descartável, sem shell nem o índice do repositório real.
    def git(self, *arguments: str) -> str:
        result = subprocess.run(["git", *arguments], cwd=self.repo, capture_output=True, text=True, encoding="utf-8", check=False)
        self.assertEqual(0, result.returncode, result.stderr)
        return result.stdout.strip()

    # Cada caso da tabela vira a onda e as T* sem arquivos esperadas; a onda é subconjunto ordenado das elegíveis.
    def test_onda_por_fixture(self) -> None:
        """Disjuntas dividem a onda; path igual, prefixo de diretório e curinga serializam; T* sem arquivos fica sozinha."""
        for case in WAVE_CASES:
            with self.subTest(case["nome"]):
                repo = self.repo / case["nome"]
                repo.mkdir()
                seed_plan_fixture(repo, case["plan"])
                before = tree_snapshot(repo)
                _, report = invoke(repo, "--dir", "phase-1-a")
                fila = report["fila"]
                self.assertEqual(case["onda"], fila["onda"])
                self.assertEqual(case["sem_arquivos"], fila["sem_arquivos"])
                self.assertEqual([tid for tid in fila["elegiveis"] if tid in fila["onda"]], fila["onda"])
                self.assertEqual("implementar", report["etapa"])
                self.assertEqual(before, tree_snapshot(repo))

    # Modo B, etapas-v1 e plans sem marcador mantêm o relatório anterior: nenhuma chave nova na fila.
    def test_sem_onda_fora_do_modo_a_coordenado(self) -> None:
        """Os planos têm `Arquivos:` disjuntos e duas T* elegíveis, mas a fila só traz os campos históricos."""
        for nome, plan in SEM_ONDA_PLANS.items():
            with self.subTest(nome):
                repo = self.repo / nome
                repo.mkdir()
                seed_plan_fixture(repo, plan)
                _, report = invoke(repo, "--dir", "phase-1-a")
                self.assertEqual({"parse", "concluidas", "abertas", "elegiveis", "bloqueadas", "avisos"}, set(report["fila"]))
                self.assertEqual(["T1", "T2"], report["fila"]["elegiveis"])

    # O terminador de linha e a indentação da Deps não mudam a fila: todas as variantes dão o relatório do plan com `\n`.
    def test_fim_de_linha_e_deps_indentada(self) -> None:
        """Deps indentada vale; T2 segue bloqueada por T1 e T3 fica fora da onda por repetir o arquivo de T1."""
        reports = {}
        for nome, plan in line_ending_variants(indented_deps_plan()).items():
            with self.subTest(nome):
                repo = self.repo / nome
                repo.mkdir()
                seed_plan_bytes(repo, plan)
                _, reports[nome] = invoke(repo, "--dir", "phase-1-a")
                fila = reports[nome]["fila"]
                self.assertEqual(["T1", "T3", "T4"], fila["elegiveis"])
                self.assertEqual([{"id": "T2", "deps": ["T1"]}], fila["bloqueadas"])
                self.assertEqual(["T1", "T4"], fila["onda"])
                self.assertEqual("implementar", reports[nome]["etapa"])
                self.assertEqual(reports["lf"], reports[nome])

    # Percorre a fase onda a onda com provas locais reais: cada rodada libera dependências e reabre T* antes sobrepostas.
    def test_jornada_de_ondas_por_prova_local(self) -> None:
        """Sobreposição por path igual, prefixo e curinga adia a T*; a onda esvazia quando todas têm prova local."""
        phase = seed_phase(seed_vibeflow(self.repo), "phase-1-a", "plan.md")
        write_plan(phase, wave_plan(
            ("T1", "nenhuma", "`src/core.py`, `tests/test_core.py`"),
            ("T2", "nenhuma", "`docs/guia.md`"),
            ("T3", "nenhuma", "`./SRC/Core.py`"),
            ("T4", "nenhuma", "`src/*`"),
            ("T5", "nenhuma", "`docs`"),
            ("T6", "nenhuma", None),
            ("T7", "T1", "`lib/x.py`"),
        ))
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("add", "--", ".vibeflow")
        self.git("commit", "-q", "-m", "fixture: baseline")
        invoke(self.repo, "--operation", "init", "--actor", "finalizer")

        # Compara o relatório dos dois motores sobre o mesmo disco e prova que a leitura não escreve nada.
        def check(elegiveis: list[str], onda: list[str], sem_arquivos: list[str], etapa: str) -> None:
            before = tree_snapshot(self.repo)
            _, report = invoke(self.repo)
            self.assertEqual(elegiveis, report["fila"]["elegiveis"])
            self.assertEqual(onda, report["fila"]["onda"])
            self.assertEqual(sem_arquivos, report["fila"]["sem_arquivos"])
            self.assertEqual(etapa, report["etapa"])
            if powershell7():
                self.assertEqual(report, invoke_powershell(self.repo))
            self.assertEqual(before, tree_snapshot(self.repo))

        # Registra a prova local de cada T* da onda pelo motor, sobre um arquivo real da fixture.
        def register(*tasks: str) -> None:
            for tid in tasks:
                proof = self.repo / "proof" / f"{tid.lower()}.txt"
                proof.parent.mkdir(exist_ok=True)
                proof.write_text(f"prova de {tid}\n", encoding="utf-8")
                invoke(self.repo, "--operation", "local", "--task", tid, "--input", f"proof/{tid.lower()}.txt",
                       "--command", "check", "--result", "verde", "--actor", "writer")

        # T3 repete o path de T1 (caixa, `./`), T4 cobre `src` por curinga e T5 cobre `docs` por prefixo; T7 depende de T1.
        check(["T1", "T2", "T3", "T4", "T5", "T6"], ["T1", "T2"], ["T6"], "implementar")
        register("T1", "T2")
        check(["T3", "T4", "T5", "T6", "T7"], ["T3", "T5", "T7"], ["T6"], "implementar")
        register("T3", "T5", "T7")
        check(["T4", "T6"], ["T4"], ["T6"], "implementar")
        register("T4")
        check(["T6"], ["T6"], ["T6"], "implementar")
        register("T6")
        check([], [], [], "validar")


# Exercita o protocolo novo por efeitos no disco e Git real, mantendo fixtures históricas acima intactas.
class StageProtocolContracts(unittest.TestCase):
    # Isola código, testes e histórico Git do protocolo novo para os dois motores.
    def setUp(self) -> None:
        self.repo = Path.cwd() / f".vibe-etapas-{uuid.uuid4().hex}"
        self.repo.mkdir()
        self.phase = seed_phase(seed_vibeflow(self.repo), "phase-1-a", "plan.md")
        (self.repo / "core.py").write_text("def twice(value):\n    return value * 2\n", encoding="utf-8")
        (self.repo / "consumer.py").write_text("from core import twice\ndef total(value):\n    return twice(value) + 1\n", encoding="utf-8")
        tests = self.repo / "tests"
        tests.mkdir()
        (tests / "test_existing.py").write_text("import unittest\nfrom core import twice\nclass Existing(unittest.TestCase):\n    def test_basic(self):\n        self.assertEqual(4, twice(2))\n", encoding="utf-8")
        (self.repo / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("add", "--", "core.py", "consumer.py", "tests", ".gitignore", ".vibeflow")
        self.git("commit", "-q", "-m", "fixture: baseline")
        self.states = {tid: {"estado": "pendente", "local": None} for tid in ("T1", "T2")}
        self.integration = {"testes": "pendentes", "prova": None, "commit": "pendente"}

    # Exige remoção efetiva inclusive dos objetos Git read-only do Windows.
    def tearDown(self) -> None:
        remove_fixture_tree(self.repo)

    # Opera apenas o Git da fixture descartável, sem shell ou índice do repositório real.
    def git(self, *arguments: str) -> str:
        result = subprocess.run(["git", *arguments], cwd=self.repo, capture_output=True, text=True, encoding="utf-8", check=False)
        self.assertEqual(0, result.returncode, result.stderr)
        return result.stdout.strip()

    # Fotografa os inputs realmente checados e o HEAD de origem, sem inventar sucesso de teste.
    def proof(self, inputs: tuple[str, ...], command: str, result: str = "verde") -> dict:
        return {"head": self.git("rev-parse", "HEAD"), "inputs": {path: self.git("hash-object", "--", path) for path in inputs}, "comando": command, "resultado": result}

    # Grava somente o plan operacional da fixture, preservando a forma da fila histórica.
    def save(self, mode: str = "A", *, done: bool = False) -> None:
        body = "# Plan: etapas\n# Protocolo: etapas-v1\n# Modo: " + mode + "\n"
        body += "- **Integração:** " + json.dumps(self.integration) + "\n\n## Tasks\n"
        for tid, deps in (("T1", "nenhuma"), ("T2", "T1")):
            body += f"### {tid}: capacidade\n- [{'x' if done else ' '}] {tid} concluída\n- **Deps:** {deps}\n- **Execução:** " + json.dumps(self.states[tid]) + "\n"
        write_plan(self.phase, body)

    # Compara projeções nativas e prova ausência de mutações do motor.
    def state(self, stage: str | None, eligible: list[str] | None = None) -> dict:
        before = tree_snapshot(self.repo)
        _, py = invoke(self.repo)
        self.assertEqual(stage, py["etapa"], py)
        if eligible is not None: self.assertEqual(eligible, py["fila"]["elegiveis"])
        if powershell7():
            process = subprocess.run([powershell7(), "-NoProfile", "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo)], capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(0, process.returncode, process.stderr)
            ps = json.loads(process.stdout)
            self.assertEqual(py, ps)
        self.assertEqual(before, tree_snapshot(self.repo))
        return py

    # Percorre dependência implementada, complemento, falha real, correção, retomada e commit integrado.
    def test_full_stage_journey_and_commit_retry(self) -> None:
        self.save()
        self.state("implementar", ["T1"])
        for tid, path in (("T1", "core.py"), ("T2", "consumer.py")):
            check = subprocess.run([sys.executable, "-m", "py_compile", path], cwd=self.repo, capture_output=True, text=True)
            self.assertEqual(0, check.returncode, check.stderr)
            self.states[tid] = {"estado": "implementada", "local": self.proof((path,), "python -m py_compile " + path)}
            self.save()
            self.state("implementar" if tid == "T1" else "testar", ["T2"] if tid == "T1" else [])
        existing = (self.repo / "tests/test_existing.py").read_bytes()
        missing = self.repo / "tests/test_boundary.py"
        missing.write_text("import unittest\nfrom consumer import total\nclass Boundary(unittest.TestCase):\n    def test_negative_rejected(self):\n        with self.assertRaises(ValueError):\n            total(-1)\n", encoding="utf-8")
        self.assertEqual(existing, (self.repo / "tests/test_existing.py").read_bytes())
        self.integration["testes"] = "prontos"
        self.save()
        self.state("validar")
        inputs = ("core.py", "consumer.py", "tests/test_existing.py", "tests/test_boundary.py")
        command = "python -m unittest discover -s tests"
        failed = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=self.repo, capture_output=True, text=True)
        self.assertNotEqual(0, failed.returncode)
        self.integration["prova"] = self.proof(inputs, command, "falha")
        self.save()
        report = self.state("corrigir_validacao")
        self.assertEqual(0, report["rodadas_correcao"])
        (self.repo / "consumer.py").write_text("from core import twice\ndef total(value):\n    if value < 0:\n        raise ValueError('valor inválido')\n    return twice(value) + 1\n", encoding="utf-8")
        check = subprocess.run([sys.executable, "-m", "py_compile", "consumer.py"], cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(0, check.returncode)
        self.states["T2"]["local"] = self.proof(("consumer.py",), "python -m py_compile consumer.py")
        self.save()
        self.state("validar")
        passed = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(0, passed.returncode, passed.stderr)
        self.integration["prova"] = self.proof(inputs, command)
        self.save()
        self.state("commitar_integracao")
        # Interrupção/falha de commit não é disfarçada pelo registro de conclusão.
        self.integration["commit"] = "registrado"
        self.integration["origem"] = self.integration["prova"]["head"]
        self.save(done=True)
        self.state("commitar_integracao")
        self.git("add", "--", "core.py", "consumer.py", "tests/test_existing.py", "tests/test_boundary.py", ".vibeflow/phases/phase-1-a/plan.md")
        self.git("commit", "-q", "-m", "task(T1,T2): validar capacidades integradas")
        report = self.state("revisar")
        self.assertEqual(self.git("rev-parse", "HEAD"), report["execucao"]["integracao"]["commit_encontrado"])
        self.assertEqual(["T1", "T2"], report["fila"]["concluidas"])
        self.assertEqual(1, len(self.git("log", "--format=%s", "--grep=^task(").splitlines()))
        # Correção posterior renova prova/HEAD sem perder a origem da integração nem duplicar seu commit.
        (self.repo / "consumer.py").write_text("# correção de review\n" + (self.repo / "consumer.py").read_text(encoding="utf-8"), encoding="utf-8")
        passed = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(0, passed.returncode, passed.stderr)
        self.integration["prova"] = self.proof(inputs, command)
        self.states["T2"]["local"] = self.proof(("consumer.py",), "python -m py_compile consumer.py")
        self.save(done=True)
        self.git("add", "--", "consumer.py", ".vibeflow/phases/phase-1-a/plan.md")
        self.git("commit", "-q", "-m", "task(R1): correção posterior à integração")
        self.state("revisar")
        self.assertEqual(1, len(self.git("log", "--format=%s", "--grep=^task(T1,T2)").splitlines()))

    # Alterar um input invalida somente seu snapshot; campos/fila inválidos nunca liberam dependentes.
    def test_snapshot_invalidation_and_invalid_records(self) -> None:
        self.states["T1"] = {"estado": "implementada", "local": self.proof(("core.py",), "python -m py_compile core.py")}
        self.save()
        self.state("implementar", ["T2"])
        (self.repo / "core.py").write_text("# mudou\ndef twice(value):\n    return value * 2\n", encoding="utf-8")
        self.state("implementar", ["T1"])
        self.states["T1"]["local"] = self.proof(("core.py",), "python -m py_compile core.py")
        self.save()
        valid = (self.phase / "plan.md").read_text(encoding="utf-8")
        variants = {
            "ciclo": valid.replace("**Deps:** nenhuma", "**Deps:** T2"),
            "inexistente": valid.replace("**Deps:** T1", "**Deps:** T9"),
            "deps-invalida": valid.replace("**Deps:** T1", "**Deps:** talvez"),
            "modo-ausente": valid.replace("# Modo: A\n", ""),
            "protocolo": valid.replace("etapas-v1", "etapas-v99"),
            "duplicada": valid + valid[valid.index("### T2:"):],
            "conclusao-duplicada": valid.replace("- [ ] T1 concluída", "- [ ] T1 concluída\n- [x] T1 concluída"),
            "registro-ausente": valid.replace('- **Execução:** {"estado": "pendente", "local": null}', ""),
            "json-invalido": valid.replace('"estado": "pendente"', '"estado": quebrado'),
            "estado-lista": valid.replace('"estado": "pendente"', '"estado": []'),
            "estado-objeto": valid.replace('"estado": "pendente"', '"estado": {}'),
            "integracao-lista": valid.replace(json.dumps(self.integration), "[]"),
            "registro-maiusculo": valid.replace('"estado": "pendente"', '"ESTADO": "pendente"'),
        }
        for name, body in variants.items():
            with self.subTest(name=name):
                write_plan(self.phase, body)
                self.state(None)
        write_plan(self.phase, valid)
        self.state("implementar", ["T2"])
        for relative in ("../README.md", "/etc/passwd", "C:/Windows/x", "core.py:stream"):
            with self.subTest(relative=relative):
                self.states["T1"]["local"]["inputs"] = {relative: "a" * 40}
                self.save()
                self.state("implementar", ["T1"])

    # Sem marcador a run continua histórica; no B explícito, checagem local não libera Deps.
    def test_legacy_and_mode_b_keep_task_cycle(self) -> None:
        self.states["T1"] = {"estado": "implementada", "local": self.proof(("core.py",), "python -m py_compile core.py")}
        self.save(mode="B")
        self.state("implementar", ["T1"])
        write_plan(self.phase, plan_tasks(("T1", " ", "nenhuma"), ("T2", " ", "T1")))
        report = self.state("implementar", ["T1"])
        self.assertNotIn("execucao", report)
        write_plan(self.phase, plan_tasks(("T1", "x", "nenhuma"), ("T2", " ", "T1")))
        self.state("implementar", ["T2"])

    # Prova final muda somente quando seus inputs mudam e não aceita tipos, links ou commit antigo.
    def test_integration_snapshot_types_and_old_commit(self) -> None:
        self.git("commit", "-q", "--allow-empty", "-m", "task(T1,T2): commit antigo")
        for tid, path in (("T1", "core.py"), ("T2", "consumer.py")):
            self.states[tid] = {"estado": "implementada", "local": self.proof((path,), "python -m py_compile " + path)}
        self.integration = {"testes": "prontos", "prova": self.proof(("core.py", "consumer.py", "tests/test_existing.py"), "python -m unittest discover -s tests"), "commit": "registrado"}
        self.save(done=True)
        self.state("commitar_integracao")
        self.git("commit", "-q", "--allow-empty", "-m", "fixture: mudança sem input afetado")
        self.state("commitar_integracao")
        valid = json.loads(json.dumps(self.integration["prova"]))
        for key, wrong in (("resultado", []), ("resultado", {}), ("inputs", []), ("inputs", {}), ("head", 42), ("comando", [])):
            with self.subTest(key=key, wrong=wrong):
                self.integration["prova"] = {**valid, key: wrong}
                self.save(done=True)
                self.state("validar")
        self.integration["prova"] = valid
        wrong_case = dict(valid)
        wrong_case["HEAD"] = wrong_case.pop("head")
        self.integration["prova"] = wrong_case
        self.save(done=True)
        self.state("validar")
        self.integration["prova"] = valid
        self.save(done=True)
        self.state("commitar_integracao")
        for origin in ([], {}, "--all", 42):
            with self.subTest(origin=origin):
                self.integration["origem"] = origin
                self.save(done=True)
                self.state(None)
        self.integration.pop("origem")
        self.save(done=True)
        (self.repo / "tests/test_existing.py").write_text("# prova mudou\n", encoding="utf-8")
        report = self.state("validar")
        self.assertTrue(all(task["local_valida"] for task in report["execucao"]["tasks"]))
        # Link substituído com os mesmos bytes não conserva uma prova de arquivo regular.
        linked = self.repo / "core.py"
        data = linked.read_bytes()
        copy = self.repo / "core-copy.py"
        copy.write_bytes(data)
        linked.unlink()
        linked.symlink_to(copy)
        report = self.state("validar")
        self.assertFalse(report["execucao"]["tasks"][0]["local_valida"])


# Inclui o contrato novo na entrada histórica usada pelo CI, sem suíte paralela esquecida.
def load_tests(loader, tests, pattern):
    import importlib.util
    source = Path(__file__).with_name("test-execution.py")
    spec = importlib.util.spec_from_file_location("execution_contracts", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    tests.addTests(loader.loadTestsFromModule(module))
    return tests


if __name__ == "__main__":
    unittest.main()
