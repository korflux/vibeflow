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
    """Verifica reuse da spec, recusa sem spec e preservação do vivo."""

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

    # Confirma que o apply reutiliza a pasta da spec e cria plan.md vazio.
    def test_reuse_spec_folder(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock-bloco"
        phase.mkdir(parents=True)
        (phase / "spec.md").write_text("spec\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply")
        dest = phase / "plan.md"
        self.assertTrue(dest.is_file())
        self.assertEqual(b"", dest.read_bytes())
        self.assertTrue((phase / "spec.md").is_file())
        self.assertFalse((vf / "phases" / "phase-2-lock-bloco").exists())
        self.assertEqual("reuse", report["modo"])
        self.assertNotIn("wip", report)

    # Confirma que a seleção de destino continua exigindo spec.md, sem rascunho auxiliar.
    def test_apply_without_spec(self) -> None:
        seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--apply", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("PLAN_SEM_SPEC", process.stderr)

    # Confirma que --dir não cria o artefato quando a dependência mecânica está ausente.
    def test_dir_without_spec(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-so-interview"
        phase.mkdir(parents=True)
        (phase / "interview.md").write_text("i\n", encoding="utf-8")
        process, _ = invoke(self.repo, "--apply", "--dir", "phase-1-so-interview", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("PLAN_SEM_SPEC", process.stderr)
        self.assertFalse((phase / "plan.md").exists())

    # Confirma que analyze.md continua impedindo a preparação de um plan já analisado.
    def test_plan_ja_analisado(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock"
        phase.mkdir(parents=True)
        (phase / "spec.md").write_text("s\n", encoding="utf-8")
        (phase / "plan.md").write_text("old\n", encoding="utf-8")
        (phase / "analyze.md").write_text("a\n", encoding="utf-8")
        process, _ = invoke(self.repo, "--apply", "--dir", "phase-1-lock", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("PLAN_JA_ANALISADO", process.stderr)
        self.assertEqual("old\n", (phase / "plan.md").read_text(encoding="utf-8"))

    # Confirma que um segundo apply não substitui um plan vivo existente.
    def test_preserve_rascunho(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock"
        phase.mkdir(parents=True)
        (phase / "spec.md").write_text("s\n", encoding="utf-8")
        (phase / "plan.md").write_text("old\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply")
        self.assertEqual("old\n", (phase / "plan.md").read_text(encoding="utf-8"))
        self.assertEqual("atualizar", report["modo"])
        self.assertEqual([], report["actions"])

    # Confirma que o gitignore recebe apenas o relatório desta skill e preserva os irmãos.
    def test_gitignore_preserves_siblings(self) -> None:
        vf = seed_vibeflow(self.repo)
        invoke(self.repo)
        text = (vf / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("spec-report.json", text)
        self.assertIn("plan-report.json", text)
        self.assertNotIn("plan-wip.md", text)

    def test_phases_file_is_unexpected(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "phases").write_text("nao", encoding="utf-8")
        process, _ = invoke(self.repo, check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("PHASES_INESPERADO", process.stderr)

    def test_mvp_requires_spec(self) -> None:
        seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--mvp", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("PLAN_SEM_SPEC", process.stderr)

    # Confirma que o alvo MVP é preparado sem criar phase e sem conteúdo semântico.
    def test_mvp_apply_prepares_special_target(self) -> None:
        vf = seed_vibeflow(self.repo)
        mvp = vf / "mvp"
        mvp.mkdir()
        (mvp / "spec.md").write_text("spec\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply", "--mvp")
        self.assertEqual(b"", (mvp / "plan.md").read_bytes())
        self.assertEqual("mvp", report["rota"])
        self.assertEqual("mvp", report["created"]["kind"])
        self.assertNotIn("wip", report)
        self.assertEqual([], [item.name for item in (vf / "phases").iterdir() if item.is_dir()])

    # Confirma que o gate de analyze preserva o plan vivo sem exigir outro arquivo.
    def test_mvp_analyze_refuses_update_and_preserves_live_file(self) -> None:
        vf = seed_vibeflow(self.repo)
        mvp = vf / "mvp"
        mvp.mkdir()
        (mvp / "spec.md").write_text("s\n", encoding="utf-8")
        (mvp / "plan.md").write_text("old\n", encoding="utf-8")
        (mvp / "analyze.md").write_text("a\n", encoding="utf-8")
        process, _ = invoke(self.repo, "--apply", "--mvp", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("PLAN_JA_ANALISADO", process.stderr)
        self.assertEqual("old\n", (mvp / "plan.md").read_text(encoding="utf-8"))

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
        self.repo = Path.cwd() / f".vibe-plan-ps-{uuid.uuid4().hex}"
        self.repo.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.repo, ignore_errors=True)

    def test_apply_reuse_same_path(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock-bloco"
        phase.mkdir(parents=True)
        (phase / "spec.md").write_text("spec\n", encoding="utf-8")
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        dest = phase / "plan.md"
        self.assertTrue(dest.is_file())
        self.assertEqual(b"", dest.read_bytes())
        self.assertTrue((phase / "spec.md").is_file())

    def test_mvp_apply_same_path(self) -> None:
        vf = seed_vibeflow(self.repo)
        mvp = vf / "mvp"
        mvp.mkdir()
        (mvp / "spec.md").write_text("s\n", encoding="utf-8")
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply", "-Mvp"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual(b"", (mvp / "plan.md").read_bytes())
        report = json.loads((vf / "plan-report.json").read_text(encoding="utf-8"))
        self.assertEqual("mvp", report["created"]["kind"])

    # Confirma que o motor PowerShell também preserva um plan vivo já existente.
    def test_apply_preserves_existing_file(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock-bloco"
        phase.mkdir(parents=True)
        (phase / "spec.md").write_text("spec\n", encoding="utf-8")
        dest = phase / "plan.md"
        dest.write_bytes(b"plan vivo PowerShell\n\x00")
        original = dest.read_bytes()
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual(original, dest.read_bytes())
        report = json.loads((vf / "plan-report.json").read_text(encoding="utf-8"))
        self.assertNotIn("wip", report)
        self.assertEqual([], report["actions"])


class TemplateContracts(unittest.TestCase):
    """Trava as linhas que a implement parseia e a Verificação como comando."""

    def test_template_freezes_task_queue_and_keeps_preparation_outside_it(self) -> None:
        """Confirma que o preparo é checklist e que a T* mantém o contrato da fila."""
        template = (SKILL_DIR / "templates" / "plan.md").read_text(encoding="utf-8")
        self.assertIn("- [ ] T1 concluída", template)
        self.assertIn("- **Deps:** nenhuma", template)
        self.assertIn("comando do repo", template)
        self.assertNotIn("passo manual", template)
        self.assertIn("não é task", template.lower())
        self.assertIn("<path aprovado ou n/a>", template.lower())
        self.assertIn("checkpoint de review (opcional", template.lower())
        self.assertNotIn("## ordem", template.lower())
        self.assertNotIn("## conferência", template.lower())

    def test_skill_requires_real_deps_and_command_verification(self) -> None:
        """Confirma os gates de dependência, comandos executáveis e preparo local."""
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("gitleaks", skill.lower())
        self.assertIn("chrome-devtools", skill.lower())
        self.assertIn("smoke test", skill.lower())
        self.assertIn("deps", skill.lower())
        self.assertIn("verificação só manual", skill.lower())
        self.assertIn("preparo local", skill.lower())
        self.assertIn("não crie t* apenas para repetir baseline", skill.lower())

    def test_task_splitting_uses_results_real_dependencies_and_isolation(self) -> None:
        """Impede que score, título, duração ou volume imponham quebras automáticas."""
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("resultado coeso", skill.lower())
        self.assertIn("dependência real de execução", skill.lower())
        self.assertIn("um risco que exija isolamento", skill.lower())
        self.assertNotIn("cinco dimensões", skill.lower())
        self.assertNotIn("quebre obrigatoriamente", skill.lower())
        self.assertNotIn("9–10", skill)

    def test_template_keeps_only_execution_fields_and_optional_coordination(self) -> None:
        """Confirma os campos necessários e torna tamanho e coordenação não obrigatórios."""
        template = (SKILL_DIR / "templates" / "plan.md").read_text(encoding="utf-8")
        for field in ("**O quê:**", "**Spec:**", "**Aceite:**", "**Verificação:**", "**Deps:**"):
            self.assertIn(field, template)
        self.assertIn("paralelização (opcional", template.lower())
        self.assertIn("checkpoint de review (opcional", template.lower())
        self.assertNotIn("**Size:**", template)
        self.assertNotIn("<score>/10", template)

    def test_plan_documentation_describes_result_based_splitting(self) -> None:
        """Alinha arquitetura, análise e README ao fatiamento por resultado."""
        architecture = (Path.cwd() / "docs" / "vibe-plan" / "ARQUITETURA.md").read_text(encoding="utf-8")
        analysis = (Path.cwd() / "docs" / "vibe-plan" / "ANALISE.md").read_text(encoding="utf-8")
        readme = (Path.cwd() / "README.md").read_text(encoding="utf-8")
        for text in (architecture, analysis, readme):
            self.assertIn("resultado", text.lower())
            self.assertNotIn("cinco dimensões", text.lower())
            self.assertNotIn("9–10", text)
        self.assertIn("esforço da rota", readme.lower())
        self.assertIn("dependências reais", analysis.lower())


if __name__ == "__main__":
    unittest.main()
