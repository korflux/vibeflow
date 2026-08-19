#!/usr/bin/env python3
"""Contratos nativos e paridade essencial da skill vibe-interview canônica."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[3] / "vibe-interview"
SCRIPT = SKILL_DIR / "scripts" / "interview.py"
POWERSHELL_SCRIPT = SKILL_DIR / "scripts" / "interview.ps1"


# Executa o motor Python e devolve processo e relatório, quando produzido.
def invoke(repo: Path, *arguments: str, check: bool = True) -> tuple[subprocess.CompletedProcess[str], dict | None]:
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo), *arguments],
        capture_output=True,
        text=True,
        check=check,
    )
    report_path = repo / ".vibeflow" / "interview-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else None
    return process, report


# Cria só a pasta .vibeflow, como se o init tivesse rodado sem phases.
def seed_vibeflow(repo: Path) -> Path:
    vf = repo / ".vibeflow"
    vf.mkdir()
    (vf / ".gitignore").write_text("init-report.json\ninit-pending.json\n", encoding="utf-8")
    return vf


class PythonContracts(unittest.TestCase):
    """Verifica os invariantes com maior risco de path, número ou perda do wip."""

    def setUp(self) -> None:
        self.repo = Path.cwd() / f".vibe-interview-python-{uuid.uuid4().hex}"
        self.repo.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.repo, ignore_errors=True)

    def test_init_ausente(self) -> None:
        process, report = invoke(self.repo, check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("INIT_AUSENTE", process.stderr)
        self.assertIsNone(report)
        self.assertFalse((self.repo / ".vibeflow").exists())

    def test_creates_missing_phases(self) -> None:
        seed_vibeflow(self.repo)
        _, report = invoke(self.repo)
        self.assertEqual(1, report["next_n"])
        self.assertTrue((self.repo / ".vibeflow" / "phases" / ".gitkeep").is_file())
        self.assertEqual("criar_phases", report["actions"][0]["op"])

    def test_next_n_is_numeric(self) -> None:
        vf = seed_vibeflow(self.repo)
        phases = vf / "phases"
        phases.mkdir()
        (phases / "phase-1-a").mkdir()
        (phases / "phase-10-b").mkdir()
        (phases / "phase-1-a" / "interview.md").write_text("x", encoding="utf-8")
        (phases / "phase-10-b" / "interview.md").write_text("y", encoding="utf-8")
        _, report = invoke(self.repo)
        self.assertEqual(11, report["next_n"])

    def test_ignores_off_pattern(self) -> None:
        vf = seed_vibeflow(self.repo)
        phases = vf / "phases"
        phases.mkdir()
        (phases / "notes").mkdir()
        _, report = invoke(self.repo)
        self.assertEqual([], report["existing"])
        self.assertTrue(any("notes" in item for item in report["avisos"]))

    def test_apply_without_wip(self) -> None:
        seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--apply", "--slug", "dashboard", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("WIP_AUSENTE", process.stderr)

    def test_apply_promotes_sanitized_slug(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "interview-wip.md").write_text("# trilha\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply", "--slug", "Dashboard Standup!!")
        dest = vf / "phases" / "phase-1-dashboard-standup" / "interview.md"
        self.assertTrue(dest.is_file())
        self.assertEqual("# trilha\n", dest.read_text(encoding="utf-8"))
        self.assertFalse((vf / "interview-wip.md").exists())
        self.assertEqual("phase-1-dashboard-standup", report["created"]["dir"])
        self.assertEqual(2, report["next_n"])
        self.assertEqual("phase-1-dashboard-standup", report["aberta"]["dir"])

    def test_second_apply_increments(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "interview-wip.md").write_text("um\n", encoding="utf-8")
        invoke(self.repo, "--apply", "--slug", "primeiro")
        (vf / "interview-wip.md").write_text("dois\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply", "--slug", "segundo")
        self.assertTrue((vf / "phases" / "phase-2-segundo" / "interview.md").is_file())
        self.assertEqual(2, report["created"]["n"])

    def test_invalid_slug(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "interview-wip.md").write_text("x\n", encoding="utf-8")
        process, _ = invoke(self.repo, "--apply", "--slug", "!!!", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("SLUG_INVALIDO", process.stderr)

    def test_fase_existe(self) -> None:
        vf = seed_vibeflow(self.repo)
        phases = vf / "phases"
        phases.mkdir()
        # Destino com o próximo n, mas que o inventário não conta (é arquivo, não pasta).
        (phases / "phase-1-dashboard").write_text("colisao", encoding="utf-8")
        (vf / "interview-wip.md").write_text("x\n", encoding="utf-8")
        process, _ = invoke(self.repo, "--apply", "--slug", "dashboard", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("FASE_EXISTE", process.stderr)
        self.assertTrue((vf / "interview-wip.md").exists())

    def test_gitignore_preserves_init_entries(self) -> None:
        vf = seed_vibeflow(self.repo)
        invoke(self.repo)
        text = (vf / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("init-report.json", text)
        self.assertIn("interview-report.json", text)
        self.assertIn("interview-wip.md", text)

    def test_aberta_requires_interview_without_spec(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock"
        phase.mkdir(parents=True)
        (phase / "interview.md").write_text("ok\n", encoding="utf-8")
        _, report = invoke(self.repo)
        self.assertEqual("phase-1-lock", report["aberta"]["dir"])
        (phase / "spec.md").write_text("spec\n", encoding="utf-8")
        _, report = invoke(self.repo)
        self.assertIsNone(report["aberta"])

    def test_phases_file_is_unexpected(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "phases").write_text("nao", encoding="utf-8")
        process, _ = invoke(self.repo, check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("PHASES_INESPERADO", process.stderr)


@unittest.skipUnless(shutil.which("pwsh"), "pwsh indisponível")
class PowershellParity(unittest.TestCase):
    """Confere que o apply essencial do PowerShell grava o mesmo path."""

    def setUp(self) -> None:
        self.repo = Path.cwd() / f".vibe-interview-ps-{uuid.uuid4().hex}"
        self.repo.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.repo, ignore_errors=True)

    def test_apply_same_path(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "interview-wip.md").write_text("# trilha\n", encoding="utf-8")
        process = subprocess.run(
            [
                "pwsh",
                "-File",
                str(POWERSHELL_SCRIPT),
                "-Root",
                str(self.repo),
                "-Apply",
                "-Slug",
                "Dashboard Standup!!",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        dest = vf / "phases" / "phase-1-dashboard-standup" / "interview.md"
        self.assertTrue(dest.is_file())
        self.assertEqual("# trilha\n", dest.read_text(encoding="utf-8"))
        self.assertFalse((vf / "interview-wip.md").exists())


if __name__ == "__main__":
    unittest.main()
