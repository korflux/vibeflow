#!/usr/bin/env python3
"""Contratos nativos e paridade essencial da skill vibe-implement canônica."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[3] / "vibe-implement"
SCRIPT = SKILL_DIR / "scripts" / "implement.py"
POWERSHELL_SCRIPT = SKILL_DIR / "scripts" / "implement.ps1"


# Executa o motor Python e devolve processo e relatório, quando produzido.
def invoke(repo: Path, *arguments: str, check: bool = True) -> tuple[subprocess.CompletedProcess[str], dict | None]:
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo), *arguments],
        capture_output=True,
        text=True,
        check=check,
    )
    report_path = repo / ".vibeflow" / "implement-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else None
    return process, report


# Cria só a pasta .vibeflow, como se o init tivesse rodado sem phases.
def seed_vibeflow(repo: Path) -> Path:
    vf = repo / ".vibeflow"
    vf.mkdir()
    (vf / ".gitignore").write_text("init-report.json\nplan-report.json\n", encoding="utf-8")
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


class PythonContracts(unittest.TestCase):
    """Verifica inventário, alvo com plan, apply do wip e gitignore."""

    def setUp(self) -> None:
        self.repo = Path.cwd() / f".vibe-implement-python-{uuid.uuid4().hex}"
        self.repo.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.repo, ignore_errors=True)

    def test_init_ausente(self) -> None:
        process, report = invoke(self.repo, check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("INIT_AUSENTE", process.stderr)
        self.assertIsNone(report)

    def test_creates_missing_phases(self) -> None:
        seed_vibeflow(self.repo)
        _, report = invoke(self.repo)
        self.assertEqual("criar", report["modo_sugerido"])
        self.assertIsNone(report["alvo"])
        self.assertTrue((self.repo / ".vibeflow" / "phases" / ".gitkeep").is_file())
        self.assertIsNone(report["created"])
        self.assertIsNone(report["modo"])
        self.assertEqual("ausente", report["wip"])

    def test_reuse_plan_folder_does_not_create_phase_two(self) -> None:
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-a", "spec.md", "plan.md")
        _, report = invoke(self.repo)
        self.assertEqual("phase-1-a", report["alvo"]["dir"])
        self.assertEqual("reuse", report["modo_sugerido"])
        self.assertFalse((vf / "phases" / "phase-2-a").exists())
        self.assertIsNone(report["created"])

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
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-so-spec", "spec.md")
        _, report = invoke(self.repo, "--dir", "phase-1-so-spec")
        self.assertEqual("phase-1-so-spec", report["alvo"]["dir"])
        self.assertEqual("reuse", report["modo_sugerido"])
        self.assertNotIn("plan.md", report["alvo"]["files"])

    def test_dir_missing_or_invalid(self) -> None:
        seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--dir", "phase-9-sumiu", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("FASE_AUSENTE", process.stderr)
        process, _ = invoke(self.repo, "--dir", "nao-e-fase", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("FASE_AUSENTE", process.stderr)

    def test_review_and_implement_listed_in_files(self) -> None:
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-com-review", "plan.md", "review.md", "implement.md")
        _, report = invoke(self.repo)
        self.assertIn("review.md", report["alvo"]["files"])
        self.assertIn("plan.md", report["alvo"]["files"])
        self.assertIn("implement.md", report["alvo"]["files"])
        self.assertEqual("atualizar", report["modo_sugerido"])

    def test_gitignore_preserves_siblings(self) -> None:
        vf = seed_vibeflow(self.repo)
        invoke(self.repo)
        text = (vf / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("plan-report.json", text)
        self.assertIn("implement-report.json", text)
        self.assertIn("implement-wip.md", text)

    def test_apply_without_wip(self) -> None:
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-a", "plan.md")
        process, _ = invoke(self.repo, "--apply", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("WIP_AUSENTE", process.stderr)
        self.assertFalse((vf / "phases" / "phase-1-a" / "implement.md").exists())

    def test_apply_reuses_plan_folder(self) -> None:
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-a", "spec.md", "plan.md")
        (vf / "implement-wip.md").write_text("# trilha\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply")
        dest = vf / "phases" / "phase-1-a" / "implement.md"
        self.assertTrue(dest.is_file())
        self.assertEqual("# trilha\n", dest.read_text(encoding="utf-8"))
        self.assertFalse((vf / "implement-wip.md").exists())
        self.assertFalse((vf / "phases" / "phase-2-a").exists())
        self.assertEqual("reuse", report["modo"])
        self.assertIn("implement.md", report["alvo"]["files"])

    def test_apply_updates_existing_implement(self) -> None:
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-a", "plan.md", "implement.md")
        (vf / "implement-wip.md").write_text("# fatia 2\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply")
        self.assertEqual("# fatia 2\n", (vf / "phases" / "phase-1-a" / "implement.md").read_text(encoding="utf-8"))
        self.assertEqual("atualizar", report["modo"])

    def test_apply_without_alvo_or_slug(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "implement-wip.md").write_text("x\n", encoding="utf-8")
        process, _ = invoke(self.repo, "--apply", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("IMPLEMENT_SEM_ALVO", process.stderr)
        self.assertTrue((vf / "implement-wip.md").is_file())

    def test_slug_creates_avulsa(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "implement-wip.md").write_text("# avulsa\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply", "--slug", "hotfix-cor")
        dest = vf / "phases" / "phase-1-hotfix-cor" / "implement.md"
        self.assertTrue(dest.is_file())
        self.assertEqual("# avulsa\n", dest.read_text(encoding="utf-8"))
        self.assertEqual("criar", report["modo"])
        self.assertEqual(2, report["next_n"])

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


class SkillContracts(unittest.TestCase):
    """Trava no disco as frases que a skill precisa para ler fila e recusar sem RED-GREEN."""

    def test_skill_reads_fila_from_report(self) -> None:
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("fila.elegiveis", text)
        self.assertIn("não monta a fila varrendo", text)
        self.assertIn("2+ elegíveis", text)

    def test_skill_refuses_without_red_green(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        dod = (SKILL_DIR / "references" / "definition-of-done.md").read_text(encoding="utf-8")
        self.assertIn("Sem RED-GREEN", skill)
        self.assertIn("Não rebaixe", dod)


# Verifica se existe uma versão real de PowerShell 7, única suportada pelo motor gêmeo.
def powershell7() -> str | None:
    executable = shutil.which("pwsh")
    if not executable:
        return None
    probe = subprocess.run([executable, "-NoProfile", "-Command", "$PSVersionTable.PSVersion.Major"], capture_output=True, text=True, check=False)
    return executable if probe.stdout.strip().isdigit() and int(probe.stdout.strip()) >= 7 else None


@unittest.skipUnless(powershell7(), "PowerShell 7 indisponível")
class PowershellParity(unittest.TestCase):
    """Confere que o apply reuse do PowerShell grava o mesmo path."""

    def setUp(self) -> None:
        self.repo = Path.cwd() / f".vibe-implement-ps-{uuid.uuid4().hex}"
        self.repo.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.repo, ignore_errors=True)

    def test_apply_reuse_same_path(self) -> None:
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-lock-bloco", "spec.md", "plan.md")
        (vf / "implement-wip.md").write_text("# trilha\n", encoding="utf-8")
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        dest = vf / "phases" / "phase-1-lock-bloco" / "implement.md"
        self.assertTrue(dest.is_file())
        self.assertEqual("# trilha\n", dest.read_text(encoding="utf-8"))
        self.assertTrue((vf / "phases" / "phase-1-lock-bloco" / "plan.md").is_file())
        self.assertFalse((vf / "implement-wip.md").exists())

    def test_fila_parity_dep_blocks(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = seed_phase(vf, "phase-1-a", "plan.md")
        write_plan(phase, plan_tasks(("T1", " ", "nenhuma"), ("T2", " ", "T1")))
        _, py_report = invoke(self.repo)
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        ps_report = json.loads((vf / "implement-report.json").read_text(encoding="utf-8"))
        self.assertEqual(py_report["fila"]["elegiveis"], ps_report["fila"]["elegiveis"])
        self.assertEqual(py_report["fila"]["bloqueadas"], ps_report["fila"]["bloqueadas"])
        self.assertEqual(["T1"], ps_report["fila"]["elegiveis"])
        self.assertEqual([{"id": "T2", "deps": ["T1"]}], ps_report["fila"]["bloqueadas"])


if __name__ == "__main__":
    unittest.main()
