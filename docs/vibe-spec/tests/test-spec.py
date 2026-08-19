#!/usr/bin/env python3
"""Contratos nativos e paridade essencial da skill vibe-spec canônica."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[3] / "vibe-spec"
SCRIPT = SKILL_DIR / "scripts" / "spec.py"
POWERSHELL_SCRIPT = SKILL_DIR / "scripts" / "spec.ps1"


# Executa o motor Python e devolve processo e relatório, quando produzido.
def invoke(repo: Path, *arguments: str, check: bool = True) -> tuple[subprocess.CompletedProcess[str], dict | None]:
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo), *arguments],
        capture_output=True,
        text=True,
        check=check,
    )
    report_path = repo / ".vibeflow" / "spec-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else None
    return process, report


# Cria só a pasta .vibeflow, como se o init tivesse rodado sem phases.
def seed_vibeflow(repo: Path) -> Path:
    vf = repo / ".vibeflow"
    vf.mkdir()
    (vf / ".gitignore").write_text("init-report.json\ninterview-report.json\n", encoding="utf-8")
    return vf


class PythonContracts(unittest.TestCase):
    """Verifica reuse de pasta, recusa com plan e criação sem interview."""

    def setUp(self) -> None:
        self.repo = Path.cwd() / f".vibe-spec-python-{uuid.uuid4().hex}"
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
        self.assertEqual(1, report["next_n"])
        self.assertEqual("criar", report["modo_sugerido"])
        self.assertTrue((self.repo / ".vibeflow" / "phases" / ".gitkeep").is_file())

    def test_reuse_interview_folder(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock-bloco"
        phase.mkdir(parents=True)
        (phase / "interview.md").write_text("trilha\n", encoding="utf-8")
        (vf / "spec-wip.md").write_text("# spec\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply")
        dest = phase / "spec.md"
        self.assertTrue(dest.is_file())
        self.assertEqual("# spec\n", dest.read_text(encoding="utf-8"))
        self.assertTrue((phase / "interview.md").is_file())
        self.assertFalse((vf / "phases" / "phase-2-lock-bloco").exists())
        self.assertEqual("reuse", report["modo"])
        self.assertEqual("phase-1-lock-bloco", report["created"]["dir"])
        self.assertFalse((vf / "spec-wip.md").exists())

    def test_apply_without_alvo_or_slug(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "spec-wip.md").write_text("x\n", encoding="utf-8")
        process, _ = invoke(self.repo, "--apply", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("SPEC_SEM_ALVO", process.stderr)

    def test_create_with_slug(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "spec-wip.md").write_text("# spec\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply", "--slug", "Dashboard!!")
        dest = vf / "phases" / "phase-1-dashboard" / "spec.md"
        self.assertTrue(dest.is_file())
        self.assertEqual("criar", report["modo"])
        self.assertEqual(2, report["next_n"])

    def test_spec_ja_planejada(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock"
        phase.mkdir(parents=True)
        (phase / "interview.md").write_text("i\n", encoding="utf-8")
        (phase / "spec.md").write_text("old\n", encoding="utf-8")
        (phase / "plan.md").write_text("plan\n", encoding="utf-8")
        (vf / "spec-wip.md").write_text("novo\n", encoding="utf-8")
        process, _ = invoke(self.repo, "--apply", "--dir", "phase-1-lock", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("SPEC_JA_PLANEJADA", process.stderr)
        self.assertEqual("old\n", (phase / "spec.md").read_text(encoding="utf-8"))
        self.assertTrue((vf / "spec-wip.md").exists())

    def test_overwrite_rascunho(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock"
        phase.mkdir(parents=True)
        (phase / "spec.md").write_text("old\n", encoding="utf-8")
        (vf / "spec-wip.md").write_text("novo\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply")
        self.assertEqual("novo\n", (phase / "spec.md").read_text(encoding="utf-8"))
        self.assertEqual("atualizar", report["modo"])

    def test_gitignore_preserves_siblings(self) -> None:
        vf = seed_vibeflow(self.repo)
        invoke(self.repo)
        text = (vf / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("init-report.json", text)
        self.assertIn("interview-report.json", text)
        self.assertIn("spec-report.json", text)
        self.assertIn("spec-wip.md", text)

    def test_phases_file_is_unexpected(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "phases").write_text("nao", encoding="utf-8")
        process, _ = invoke(self.repo, check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("PHASES_INESPERADO", process.stderr)

    def test_invalid_slug_on_create(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "spec-wip.md").write_text("x\n", encoding="utf-8")
        process, _ = invoke(self.repo, "--apply", "--slug", "!!!", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("SLUG_INVALIDO", process.stderr)


@unittest.skipUnless(shutil.which("pwsh"), "pwsh indisponível")
class PowershellParity(unittest.TestCase):
    """Confere que o apply reuse do PowerShell grava o mesmo path."""

    def setUp(self) -> None:
        self.repo = Path.cwd() / f".vibe-spec-ps-{uuid.uuid4().hex}"
        self.repo.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.repo, ignore_errors=True)

    def test_apply_reuse_same_path(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock-bloco"
        phase.mkdir(parents=True)
        (phase / "interview.md").write_text("trilha\n", encoding="utf-8")
        (vf / "spec-wip.md").write_text("# spec\n", encoding="utf-8")
        process = subprocess.run(
            ["pwsh", "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        dest = phase / "spec.md"
        self.assertTrue(dest.is_file())
        self.assertEqual("# spec\n", dest.read_text(encoding="utf-8"))
        self.assertTrue((phase / "interview.md").is_file())
        self.assertFalse((vf / "spec-wip.md").exists())


if __name__ == "__main__":
    unittest.main()
