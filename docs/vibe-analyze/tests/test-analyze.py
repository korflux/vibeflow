#!/usr/bin/env python3
"""Contratos nativos e paridade essencial da skill vibe-analyze canônica."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[3] / "vibe-analyze"
SCRIPT = SKILL_DIR / "scripts" / "analyze.py"
POWERSHELL_SCRIPT = SKILL_DIR / "scripts" / "analyze.ps1"


# Executa o motor Python e devolve processo e relatório, quando produzido.
def invoke(repo: Path, *arguments: str, check: bool = True) -> tuple[subprocess.CompletedProcess[str], dict | None]:
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo), *arguments],
        capture_output=True,
        text=True,
        check=check,
    )
    report_path = repo / ".vibeflow" / "analyze-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else None
    return process, report


# Cria só a pasta .vibeflow, como se o init tivesse rodado sem phases.
def seed_vibeflow(repo: Path) -> Path:
    vf = repo / ".vibeflow"
    vf.mkdir()
    (vf / ".gitignore").write_text("init-report.json\nplan-report.json\n", encoding="utf-8")
    return vf


class PythonContracts(unittest.TestCase):
    """Verifica reuse do plan, recusa sem plan/spec e preservação do artefato vivo."""

    def setUp(self) -> None:
        self.repo = Path.cwd() / f".vibe-analyze-python-{uuid.uuid4().hex}"
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
        phase = vf / "phases" / "phase-1-lock-bloco"
        phase.mkdir(parents=True)
        (phase / "spec.md").write_text("spec\n", encoding="utf-8")
        (phase / "plan.md").write_text("plan\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply")
        dest = phase / "analyze.md"
        self.assertTrue(dest.is_file())
        self.assertEqual(b"", dest.read_bytes())
        self.assertTrue((phase / "plan.md").is_file())
        self.assertFalse((vf / "phases" / "phase-2-lock-bloco").exists())
        self.assertEqual("reuse", report["modo"])
        self.assertNotIn("wip", report)
        self.assertEqual([{"op": "criar_arquivo", "alvo": ".vibeflow/phases/phase-1-lock-bloco/analyze.md"}], report["actions"])

    def test_apply_without_plan(self) -> None:
        vf = seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--apply", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("ANALYZE_SEM_PLAN", process.stderr)

    def test_dir_without_plan(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-so-spec"
        phase.mkdir(parents=True)
        (phase / "spec.md").write_text("s\n", encoding="utf-8")
        process, _ = invoke(self.repo, "--apply", "--dir", "phase-1-so-spec", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("ANALYZE_SEM_PLAN", process.stderr)
        self.assertFalse((phase / "analyze.md").exists())

    def test_dir_without_spec(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-so-plan"
        phase.mkdir(parents=True)
        (phase / "plan.md").write_text("p\n", encoding="utf-8")
        process, _ = invoke(self.repo, "--apply", "--dir", "phase-1-so-plan", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("ANALYZE_SEM_SPEC", process.stderr)
        self.assertFalse((phase / "analyze.md").exists())

    def test_preserve_rascunho(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock"
        phase.mkdir(parents=True)
        (phase / "spec.md").write_text("s\n", encoding="utf-8")
        (phase / "plan.md").write_text("p\n", encoding="utf-8")
        original = b"old\n\x00historico\n"
        (phase / "analyze.md").write_bytes(original)
        _, report = invoke(self.repo, "--apply")
        self.assertEqual(original, (phase / "analyze.md").read_bytes())
        self.assertEqual("atualizar", report["modo"])
        self.assertEqual([], report["actions"])
        self.assertNotIn("wip", report)

    def test_gitignore_preserves_siblings(self) -> None:
        vf = seed_vibeflow(self.repo)
        invoke(self.repo)
        text = (vf / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("plan-report.json", text)
        self.assertIn("analyze-report.json", text)
        self.assertNotIn("analyze-wip.md", text)

    def test_phases_file_is_unexpected(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "phases").write_text("nao", encoding="utf-8")
        process, _ = invoke(self.repo, check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("PHASES_INESPERADO", process.stderr)

    def test_mvp_requires_complete_predecessors(self) -> None:
        vf = seed_vibeflow(self.repo)
        mvp = vf / "mvp"
        mvp.mkdir()
        (mvp / "spec.md").write_text("s\n", encoding="utf-8")
        (mvp / "plan.md").write_text("p\n", encoding="utf-8")
        process, _ = invoke(self.repo, "--mvp", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("ANALYZE_SEM_INTERVIEW", process.stderr)

    def test_mvp_apply_reuses_special_target(self) -> None:
        vf = seed_vibeflow(self.repo)
        mvp = vf / "mvp"
        mvp.mkdir()
        for name in ("interview.md", "spec.md", "plan.md"):
            (mvp / name).write_text(f"{name}\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply", "--mvp")
        self.assertEqual(b"", (mvp / "analyze.md").read_bytes())
        self.assertEqual("mvp", report["rota"])
        self.assertEqual("mvp", report["created"]["kind"])
        self.assertNotIn("wip", report)
        self.assertEqual([], [item.name for item in (vf / "phases").iterdir() if item.is_dir()])

    # Confirma que o apply MVP pode ser repetido sem substituir o histórico semântico.
    def test_mvp_apply_preserves_existing_file(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "phases").mkdir()
        (vf / "phases" / ".gitkeep").write_text("", encoding="utf-8")
        mvp = vf / "mvp"
        mvp.mkdir()
        for name in ("interview.md", "spec.md", "plan.md"):
            (mvp / name).write_text(f"{name}\n", encoding="utf-8")
        original = b"# Analyze\n\x00historico\n"
        (mvp / "analyze.md").write_bytes(original)
        _, report = invoke(self.repo, "--apply", "--mvp")
        self.assertEqual(original, (mvp / "analyze.md").read_bytes())
        self.assertEqual("atualizar", report["modo"])
        self.assertEqual([], report["actions"])

    def test_mvp_rejects_dir(self) -> None:
        seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--mvp", "--dir", "phase-1-x", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("MODO_INVALIDO", process.stderr)



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
        self.repo = Path.cwd() / f".vibe-analyze-ps-{uuid.uuid4().hex}"
        self.repo.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.repo, ignore_errors=True)

    def test_apply_reuse_same_path(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock-bloco"
        phase.mkdir(parents=True)
        (phase / "spec.md").write_text("spec\n", encoding="utf-8")
        (phase / "plan.md").write_text("plan\n", encoding="utf-8")
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        dest = phase / "analyze.md"
        self.assertTrue(dest.is_file())
        self.assertEqual(b"", dest.read_bytes())
        self.assertTrue((phase / "plan.md").is_file())
        report = json.loads((vf / "analyze-report.json").read_text(encoding="utf-8"))
        self.assertNotIn("wip", report)

    # Confirma que o motor PowerShell preserva o conteúdo do analyze já existente.
    def test_apply_preserves_existing_file(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock-bloco"
        phase.mkdir(parents=True)
        (phase / "spec.md").write_text("spec\n", encoding="utf-8")
        (phase / "plan.md").write_text("plan\n", encoding="utf-8")
        original = b"# analyze\n\x00historico\n"
        (phase / "analyze.md").write_bytes(original)
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual(original, (phase / "analyze.md").read_bytes())
        report = json.loads((vf / "analyze-report.json").read_text(encoding="utf-8"))
        self.assertEqual([], report["actions"])
        self.assertNotIn("wip", report)

    def test_mvp_apply_same_path(self) -> None:
        vf = seed_vibeflow(self.repo)
        mvp = vf / "mvp"
        mvp.mkdir()
        for name in ("interview.md", "spec.md", "plan.md"):
            (mvp / name).write_text(f"{name}\n", encoding="utf-8")
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply", "-Mvp"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual(b"", (mvp / "analyze.md").read_bytes())
        report = json.loads((vf / "analyze-report.json").read_text(encoding="utf-8"))
        self.assertEqual("mvp", report["created"]["kind"])
        self.assertNotIn("wip", report)


class TemplateContracts(unittest.TestCase):
    """Trava os contratos de varredura cruzada e qualidade de testes."""

    def test_skill_requires_quality_and_decisions(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("smoke test", skill.lower())
        self.assertIn("gitleaks", skill.lower())
        self.assertIn("chrome-devtools", skill.lower())
        self.assertIn("substitui", skill.lower())
        self.assertIn("CRITICAL", skill)

    def test_coverage_reference_includes_quality_and_decisions(self) -> None:
        coverage = (SKILL_DIR / "references" / "coverage.md").read_text(encoding="utf-8")
        self.assertIn("qualidade_teste", coverage)
        self.assertIn("decisao", coverage)
        self.assertIn("smoke test", coverage.lower())


if __name__ == "__main__":
    unittest.main()
