#!/usr/bin/env python3
"""Contratos nativos e paridade essencial da skill vibe-review canônica."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[3] / "vibe-review"
SCRIPT = SKILL_DIR / "scripts" / "review.py"
POWERSHELL_SCRIPT = SKILL_DIR / "scripts" / "review.ps1"


# Executa o motor Python e devolve processo e relatório, quando produzido.
def invoke(repo: Path, *arguments: str, check: bool = True) -> tuple[subprocess.CompletedProcess[str], dict | None]:
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo), *arguments],
        capture_output=True,
        text=True,
        check=check,
    )
    report_path = repo / ".vibeflow" / "review-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else None
    return process, report


# Cria só a pasta .vibeflow, como se o init tivesse rodado sem phases.
def seed_vibeflow(repo: Path) -> Path:
    vf = repo / ".vibeflow"
    vf.mkdir()
    (vf / ".gitignore").write_text("init-report.json\nplan-report.json\n", encoding="utf-8")
    return vf


class PythonContracts(unittest.TestCase):
    """Verifica reuse do plan, avulsa com slug e recusa sem alvo."""

    def setUp(self) -> None:
        self.repo = Path.cwd() / f".vibe-review-python-{uuid.uuid4().hex}"
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

    def test_reuse_plan_folder(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-a"
        phase.mkdir(parents=True)
        (phase / "plan.md").write_text("plan\n", encoding="utf-8")
        (vf / "review-wip.md").write_text("# review\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply")
        dest = phase / "review.md"
        self.assertTrue(dest.is_file())
        self.assertEqual("# review\n", dest.read_text(encoding="utf-8"))
        self.assertTrue((phase / "plan.md").is_file())
        self.assertFalse((vf / "phases" / "phase-2-a").exists())
        self.assertEqual("reuse", report["modo"])
        self.assertFalse((vf / "review-wip.md").exists())

    def test_apply_without_alvo_or_slug(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "review-wip.md").write_text("x\n", encoding="utf-8")
        process, _ = invoke(self.repo, "--apply", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("REVIEW_SEM_ALVO", process.stderr)
        self.assertTrue((vf / "review-wip.md").is_file())

    def test_slug_creates_avulsa(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "review-wip.md").write_text("# avulsa\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply", "--slug", "diff-local")
        dest = vf / "phases" / "phase-1-diff-local" / "review.md"
        self.assertTrue(dest.is_file())
        self.assertEqual("# avulsa\n", dest.read_text(encoding="utf-8"))
        self.assertEqual("criar", report["modo"])
        self.assertEqual(["review.md"], report["created"]["files"])

    def test_dir_without_plan_writes_review(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-so-spec"
        phase.mkdir(parents=True)
        (phase / "spec.md").write_text("s\n", encoding="utf-8")
        (vf / "review-wip.md").write_text("# dir\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply", "--dir", "phase-1-so-spec")
        dest = phase / "review.md"
        self.assertTrue(dest.is_file())
        self.assertEqual("# dir\n", dest.read_text(encoding="utf-8"))
        self.assertEqual("reuse", report["modo"])
        self.assertFalse((phase / "plan.md").exists())

    def test_dir_missing(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "review-wip.md").write_text("x\n", encoding="utf-8")
        process, _ = invoke(self.repo, "--apply", "--dir", "phase-9-sumiu", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("FASE_AUSENTE", process.stderr)

    def test_overwrite_rascunho(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock"
        phase.mkdir(parents=True)
        (phase / "plan.md").write_text("p\n", encoding="utf-8")
        (phase / "review.md").write_text("old\n", encoding="utf-8")
        (vf / "review-wip.md").write_text("novo\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply")
        self.assertEqual("novo\n", (phase / "review.md").read_text(encoding="utf-8"))
        self.assertEqual("atualizar", report["modo"])

    def test_implement_listed_in_files(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-com-implement"
        phase.mkdir(parents=True)
        (phase / "plan.md").write_text("p\n", encoding="utf-8")
        (phase / "implement.md").write_text("i\n", encoding="utf-8")
        _, report = invoke(self.repo)
        self.assertIn("implement.md", report["alvo"]["files"])
        self.assertIn("plan.md", report["alvo"]["files"])

    def test_gitignore_preserves_siblings(self) -> None:
        vf = seed_vibeflow(self.repo)
        invoke(self.repo)
        text = (vf / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("plan-report.json", text)
        self.assertIn("review-report.json", text)
        self.assertIn("review-wip.md", text)

    def test_phases_file_is_unexpected(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "phases").write_text("nao", encoding="utf-8")
        process, _ = invoke(self.repo, check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("PHASES_INESPERADO", process.stderr)



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
        self.repo = Path.cwd() / f".vibe-review-ps-{uuid.uuid4().hex}"
        self.repo.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.repo, ignore_errors=True)

    def test_apply_reuse_same_path(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock-bloco"
        phase.mkdir(parents=True)
        (phase / "plan.md").write_text("plan\n", encoding="utf-8")
        (vf / "review-wip.md").write_text("# review\n", encoding="utf-8")
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        dest = phase / "review.md"
        self.assertTrue(dest.is_file())
        self.assertEqual("# review\n", dest.read_text(encoding="utf-8"))
        self.assertTrue((phase / "plan.md").is_file())
        self.assertFalse((vf / "review-wip.md").exists())


if __name__ == "__main__":
    unittest.main()
