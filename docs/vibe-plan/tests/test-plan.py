#!/usr/bin/env python3
"""Contratos nativos e paridade essencial da skill vibe-plan canônica."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[3] / "vibe-plan"
SCRIPT = SKILL_DIR / "scripts" / "plan.py"
POWERSHELL_SCRIPT = SKILL_DIR / "scripts" / "plan.ps1"


# Executa o motor Python e devolve processo e relatório, quando produzido.
def invoke(repo: Path, *arguments: str, check: bool = True) -> tuple[subprocess.CompletedProcess[str], dict | None]:
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo), *arguments],
        capture_output=True,
        text=True,
        check=check,
    )
    report_path = repo / ".vibeflow" / "plan-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else None
    return process, report


# Cria só a pasta .vibeflow, como se o init tivesse rodado sem phases.
def seed_vibeflow(repo: Path) -> Path:
    vf = repo / ".vibeflow"
    vf.mkdir()
    (vf / ".gitignore").write_text("init-report.json\nspec-report.json\n", encoding="utf-8")
    return vf


class PythonContracts(unittest.TestCase):
    """Verifica reuse da spec, recusa sem spec e trava com analyze."""

    def setUp(self) -> None:
        self.repo = Path.cwd() / f".vibe-plan-python-{uuid.uuid4().hex}"
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

    def test_reuse_spec_folder(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock-bloco"
        phase.mkdir(parents=True)
        (phase / "spec.md").write_text("spec\n", encoding="utf-8")
        (vf / "plan-wip.md").write_text("# plan\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply")
        dest = phase / "plan.md"
        self.assertTrue(dest.is_file())
        self.assertEqual("# plan\n", dest.read_text(encoding="utf-8"))
        self.assertTrue((phase / "spec.md").is_file())
        self.assertFalse((vf / "phases" / "phase-2-lock-bloco").exists())
        self.assertEqual("reuse", report["modo"])
        self.assertFalse((vf / "plan-wip.md").exists())

    def test_apply_without_spec(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "plan-wip.md").write_text("x\n", encoding="utf-8")
        process, _ = invoke(self.repo, "--apply", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("PLAN_SEM_SPEC", process.stderr)

    def test_dir_without_spec(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-so-interview"
        phase.mkdir(parents=True)
        (phase / "interview.md").write_text("i\n", encoding="utf-8")
        (vf / "plan-wip.md").write_text("x\n", encoding="utf-8")
        process, _ = invoke(self.repo, "--apply", "--dir", "phase-1-so-interview", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("PLAN_SEM_SPEC", process.stderr)
        self.assertFalse((phase / "plan.md").exists())

    def test_plan_ja_analisado(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock"
        phase.mkdir(parents=True)
        (phase / "spec.md").write_text("s\n", encoding="utf-8")
        (phase / "plan.md").write_text("old\n", encoding="utf-8")
        (phase / "analyze.md").write_text("a\n", encoding="utf-8")
        (vf / "plan-wip.md").write_text("novo\n", encoding="utf-8")
        process, _ = invoke(self.repo, "--apply", "--dir", "phase-1-lock", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("PLAN_JA_ANALISADO", process.stderr)
        self.assertEqual("old\n", (phase / "plan.md").read_text(encoding="utf-8"))
        self.assertTrue((vf / "plan-wip.md").exists())

    def test_overwrite_rascunho(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock"
        phase.mkdir(parents=True)
        (phase / "spec.md").write_text("s\n", encoding="utf-8")
        (phase / "plan.md").write_text("old\n", encoding="utf-8")
        (vf / "plan-wip.md").write_text("novo\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply")
        self.assertEqual("novo\n", (phase / "plan.md").read_text(encoding="utf-8"))
        self.assertEqual("atualizar", report["modo"])

    def test_gitignore_preserves_siblings(self) -> None:
        vf = seed_vibeflow(self.repo)
        invoke(self.repo)
        text = (vf / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("spec-report.json", text)
        self.assertIn("plan-report.json", text)
        self.assertIn("plan-wip.md", text)

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
        self.repo = Path.cwd() / f".vibe-plan-ps-{uuid.uuid4().hex}"
        self.repo.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.repo, ignore_errors=True)

    def test_apply_reuse_same_path(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock-bloco"
        phase.mkdir(parents=True)
        (phase / "spec.md").write_text("spec\n", encoding="utf-8")
        (vf / "plan-wip.md").write_text("# plan\n", encoding="utf-8")
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        dest = phase / "plan.md"
        self.assertTrue(dest.is_file())
        self.assertEqual("# plan\n", dest.read_text(encoding="utf-8"))
        self.assertTrue((phase / "spec.md").is_file())
        self.assertFalse((vf / "plan-wip.md").exists())


class TemplateContracts(unittest.TestCase):
    """Trava as linhas que a implement parseia e a Verificação como comando."""

    def test_template_freezes_concluida_deps_and_command(self) -> None:
        template = (SKILL_DIR / "templates" / "plan.md").read_text(encoding="utf-8")
        self.assertIn("- [ ] T1 concluída", template)
        self.assertIn("- **Deps:** nenhuma", template)
        self.assertIn("comando do repo", template)
        self.assertNotIn("passo manual", template)
        self.assertIn("omitir se o caminho não atravessa T*", template)

    def test_skill_requires_real_deps_and_command_verification(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Deps reais", skill)
        self.assertIn("Verificação só manual", skill)
        self.assertIn("fluxo extra", skill)


if __name__ == "__main__":
    unittest.main()
