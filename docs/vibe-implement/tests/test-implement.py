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


class PythonContracts(unittest.TestCase):
    """Verifica inventário, alvo com plan, flags recusadas e gitignore."""

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

    def test_review_listed_in_files(self) -> None:
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-com-review", "plan.md", "review.md")
        _, report = invoke(self.repo)
        self.assertIn("review.md", report["alvo"]["files"])
        self.assertIn("plan.md", report["alvo"]["files"])

    def test_gitignore_preserves_siblings(self) -> None:
        vf = seed_vibeflow(self.repo)
        invoke(self.repo)
        text = (vf / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("plan-report.json", text)
        self.assertIn("implement-report.json", text)
        self.assertNotIn("implement-wip.md", text)

    def test_apply_and_slug_rejected(self) -> None:
        vf = seed_vibeflow(self.repo)
        process, report = invoke(self.repo, "--apply", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("FLAG_DESCONHECIDA", process.stderr)
        self.assertIsNone(report)
        self.assertFalse((vf / "implement-wip.md").exists())
        process, _ = invoke(self.repo, "--slug", "x", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("FLAG_DESCONHECIDA", process.stderr)

    def test_phases_file_is_unexpected(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "phases").write_text("nao", encoding="utf-8")
        process, _ = invoke(self.repo, check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("PHASES_INESPERADO", process.stderr)


@unittest.skipUnless(shutil.which("pwsh"), "pwsh indisponível")
class PowershellParity(unittest.TestCase):
    """Confere que o inventário PowerShell aponta o mesmo alvo.path."""

    def setUp(self) -> None:
        self.repo = Path.cwd() / f".vibe-implement-ps-{uuid.uuid4().hex}"
        self.repo.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.repo, ignore_errors=True)

    def test_inventory_reuse_same_path(self) -> None:
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-lock-bloco", "spec.md", "plan.md")
        process = subprocess.run(
            ["pwsh", "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        report = json.loads((vf / "implement-report.json").read_text(encoding="utf-8"))
        self.assertEqual(".vibeflow/phases/phase-1-lock-bloco", report["alvo"]["path"])
        self.assertEqual("reuse", report["modo_sugerido"])
        self.assertFalse((vf / "phases" / "phase-2-lock-bloco").exists())


if __name__ == "__main__":
    unittest.main()
