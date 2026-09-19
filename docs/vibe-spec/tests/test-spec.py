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
# Caminho do template vivo; os contratos abaixo garantem molde F* com superfície e handoff condicional.
TEMPLATE = SKILL_DIR / "templates" / "spec.md"


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
    """Verifica reuse de pasta, recusa com plan e preparação do vivo."""

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

    # Confirma que o apply reutiliza a pasta da interview e cria somente o arquivo vivo vazio.
    def test_reuse_interview_folder(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock-bloco"
        phase.mkdir(parents=True)
        (phase / "interview.md").write_text("trilha\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply")
        dest = phase / "spec.md"
        self.assertTrue(dest.is_file())
        self.assertEqual(b"", dest.read_bytes())
        self.assertTrue((phase / "interview.md").is_file())
        self.assertFalse((vf / "phases" / "phase-2-lock-bloco").exists())
        self.assertEqual("reuse", report["modo"])
        self.assertEqual("phase-1-lock-bloco", report["created"]["dir"])
        self.assertNotIn("wip", report)

    # Confirma que a seleção falha por falta de alvo, sem depender de conteúdo temporário.
    def test_apply_without_alvo_or_slug(self) -> None:
        seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--apply", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("SPEC_SEM_ALVO", process.stderr)

    # Confirma que uma fase nova recebe spec.md vazio depois da sanitização do slug.
    def test_create_with_slug(self) -> None:
        vf = seed_vibeflow(self.repo)
        _, report = invoke(self.repo, "--apply", "--slug", "Dashboard!!")
        dest = vf / "phases" / "phase-1-dashboard" / "spec.md"
        self.assertTrue(dest.is_file())
        self.assertEqual(b"", dest.read_bytes())
        self.assertEqual("criar", report["modo"])
        self.assertEqual(2, report["next_n"])

    # Garante que um slug explícito abre pedido novo mesmo com rascunho antigo pendente.
    def test_explicit_slug_starts_new_phase_when_draft_exists(self) -> None:
        vf = seed_vibeflow(self.repo)
        old = vf / "phases" / "phase-1-pedido-antigo"
        old.mkdir(parents=True)
        (old / "spec.md").write_text("spec antigo\n", encoding="utf-8")

        _, report = invoke(self.repo, "--apply", "--slug", "pedido-novo")

        self.assertTrue((vf / "phases" / "phase-2-pedido-novo" / "spec.md").is_file())
        self.assertEqual("phase-2-pedido-novo", report["created"]["dir"])
        self.assertEqual("criar", report["modo"])
        self.assertEqual("spec antigo\n", (old / "spec.md").read_text(encoding="utf-8"))

    # Confirma que plan.md continua sendo um gate de proteção e não é afetado pelo apply.
    def test_spec_ja_planejada(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock"
        phase.mkdir(parents=True)
        (phase / "interview.md").write_text("i\n", encoding="utf-8")
        (phase / "spec.md").write_text("old\n", encoding="utf-8")
        (phase / "plan.md").write_text("plan\n", encoding="utf-8")
        process, _ = invoke(self.repo, "--apply", "--dir", "phase-1-lock", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("SPEC_JA_PLANEJADA", process.stderr)
        self.assertEqual("old\n", (phase / "spec.md").read_text(encoding="utf-8"))

    # Confirma que o apply repetido não substitui um spec vivo já editado.
    def test_preserve_rascunho(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock"
        phase.mkdir(parents=True)
        (phase / "spec.md").write_text("old\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply")
        self.assertEqual("old\n", (phase / "spec.md").read_text(encoding="utf-8"))
        self.assertEqual("atualizar", report["modo"])
        self.assertEqual([], report["actions"])

    # Confirma que o gitignore recebe apenas o relatório desta skill e preserva os irmãos.
    def test_gitignore_preserves_siblings(self) -> None:
        vf = seed_vibeflow(self.repo)
        invoke(self.repo)
        text = (vf / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("init-report.json", text)
        self.assertIn("interview-report.json", text)
        self.assertIn("spec-report.json", text)
        self.assertNotIn("spec-wip.md", text)

    def test_phases_file_is_unexpected(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "phases").write_text("nao", encoding="utf-8")
        process, _ = invoke(self.repo, check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("PHASES_INESPERADO", process.stderr)

    def test_invalid_slug_on_create(self) -> None:
        seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--apply", "--slug", "!!!", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("SLUG_INVALIDO", process.stderr)

    def test_mvp_requires_interview(self) -> None:
        seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--mvp", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("MVP_INTERVIEW_AUSENTE", process.stderr)

    # Confirma que o alvo MVP é preparado sem criar phase nem conteúdo semântico.
    def test_mvp_apply_prepares_special_target(self) -> None:
        vf = seed_vibeflow(self.repo)
        mvp = vf / "mvp"
        mvp.mkdir()
        (mvp / "interview.md").write_text("interview\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply", "--mvp")
        self.assertEqual(b"", (mvp / "spec.md").read_bytes())
        self.assertEqual("mvp", report["rota"])
        self.assertEqual("mvp", report["created"]["kind"])
        self.assertEqual(".vibeflow/mvp", report["alvo"]["path"])
        self.assertNotIn("wip", report)
        self.assertEqual([], [item.name for item in (vf / "phases").iterdir() if item.is_dir()])

    # Confirma que a proteção de plan.md preserva o spec vivo em um segundo apply.
    def test_mvp_plan_refuses_update_and_preserves_live_file(self) -> None:
        vf = seed_vibeflow(self.repo)
        mvp = vf / "mvp"
        mvp.mkdir()
        (mvp / "interview.md").write_text("i\n", encoding="utf-8")
        (mvp / "spec.md").write_text("old\n", encoding="utf-8")
        (mvp / "plan.md").write_text("plan\n", encoding="utf-8")
        process, _ = invoke(self.repo, "--apply", "--mvp", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("SPEC_JA_PLANEJADA", process.stderr)
        self.assertEqual("old\n", (mvp / "spec.md").read_text(encoding="utf-8"))

    def test_mvp_rejects_phase_selectors(self) -> None:
        seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--mvp", "--slug", "produto", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("MODO_INVALIDO", process.stderr)



# Contratos do template vivo; garantem molde F* com superfície por passo e handoff condicional.
class TemplateContracts(unittest.TestCase):
    """Verifica que o template exige F*, superfície e design ou plan conforme UI."""

    # Lê o template canônico sem depender de .vibeflow ou do motor.
    def read_template(self) -> str:
        return TEMPLATE.read_text(encoding="utf-8")

    # Confirma que cada F* exige os dez campos do contrato.
    def test_fluxo_f_exige_dez_campos(self) -> None:
        text = self.read_template()
        for campo in ("Jornada", "Rota", "Gatilho", "Pré-condição", "Superfície por passo", "Passos", "Validações", "Erros", "Estados", "Aceite"):
            self.assertIn(campo, text)

    # Confirma que passo sem superfície é defeito com as seis superfícies fechadas.
    def test_passo_sem_superficie_e_defeito(self) -> None:
        text = self.read_template()
        self.assertIn("sem superfície", text.lower())
        self.assertIn("defeito", text.lower())
        for superficie in ("tela", "popup", "drawer", "inline", "redirect", "toast"):
            self.assertIn(superficie, text.lower())

    # Confirma que o handoff aponta design com UI visível e plan sem UI.
    def test_handoff_condicional_aponta_design_ou_plan(self) -> None:
        text = self.read_template()
        self.assertIn("vibe-design", text)
        self.assertIn("vibe-plan", text)
        self.assertIn("UI visível", text)


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
        self.repo = Path.cwd() / f".vibe-spec-ps-{uuid.uuid4().hex}"
        self.repo.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.repo, ignore_errors=True)

    def test_apply_reuse_same_path(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock-bloco"
        phase.mkdir(parents=True)
        (phase / "interview.md").write_text("trilha\n", encoding="utf-8")
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        dest = phase / "spec.md"
        self.assertTrue(dest.is_file())
        self.assertEqual(b"", dest.read_bytes())
        self.assertTrue((phase / "interview.md").is_file())

    def test_mvp_apply_same_path(self) -> None:
        vf = seed_vibeflow(self.repo)
        mvp = vf / "mvp"
        mvp.mkdir()
        (mvp / "interview.md").write_text("i\n", encoding="utf-8")
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply", "-Mvp"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual(b"", (mvp / "spec.md").read_bytes())
        report = json.loads((vf / "spec-report.json").read_text(encoding="utf-8"))
        self.assertEqual("mvp", report["created"]["kind"])

    # Confirma que o motor PowerShell também preserva uma spec viva já existente.
    def test_apply_preserves_existing_file(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock-bloco"
        phase.mkdir(parents=True)
        (phase / "interview.md").write_text("trilha\n", encoding="utf-8")
        dest = phase / "spec.md"
        dest.write_bytes(b"spec viva PowerShell\n\x00")
        original = dest.read_bytes()
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual(original, dest.read_bytes())
        report = json.loads((vf / "spec-report.json").read_text(encoding="utf-8"))
        self.assertNotIn("wip", report)
        self.assertEqual([], report["actions"])

    # Confirma que o motor PowerShell respeita slug explícito mesmo com outro rascunho.
    def test_explicit_slug_starts_new_phase_when_draft_exists(self) -> None:
        vf = seed_vibeflow(self.repo)
        old = vf / "phases" / "phase-1-pedido-antigo"
        old.mkdir(parents=True)
        (old / "spec.md").write_text("spec antigo\n", encoding="utf-8")
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply", "-Slug", "pedido-novo"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertTrue((vf / "phases" / "phase-2-pedido-novo" / "spec.md").is_file())
        report = json.loads((vf / "spec-report.json").read_text(encoding="utf-8"))
        self.assertEqual("phase-2-pedido-novo", report["created"]["dir"])


if __name__ == "__main__":
    unittest.main()
