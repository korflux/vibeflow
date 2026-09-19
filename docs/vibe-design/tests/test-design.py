#!/usr/bin/env python3
"""Contratos nativos e paridade essencial da skill vibe-design canônica."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[3] / "vibe-design"
SCRIPT = SKILL_DIR / "scripts" / "design.py"
POWERSHELL_SCRIPT = SKILL_DIR / "scripts" / "design.ps1"


# Executa o motor Python e devolve processo e relatório, quando produzido.
def invoke(repo: Path, *arguments: str, check: bool = True) -> tuple[subprocess.CompletedProcess[str], dict | None]:
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo), *arguments],
        capture_output=True,
        text=True,
        check=check,
    )
    report_path = repo / ".vibeflow" / "design-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else None
    return process, report


# Cria só a pasta .vibeflow, como se o init tivesse rodado sem phases.
def seed_vibeflow(repo: Path) -> Path:
    vf = repo / ".vibeflow"
    vf.mkdir()
    (vf / ".gitignore").write_text("init-report.json\ninterview-report.json\n", encoding="utf-8")
    return vf


class PythonContracts(unittest.TestCase):
    """Verifica reuse da spec, recusa com plan e preparação do vivo."""

    def setUp(self) -> None:
        self.repo = Path.cwd() / f".vibe-design-python-{uuid.uuid4().hex}"
        self.repo.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.repo, ignore_errors=True)

    # Recusa sem .vibeflow para exigir init antes de qualquer escrita.
    def test_init_ausente(self) -> None:
        process, report = invoke(self.repo, check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("INIT_AUSENTE", process.stderr)
        self.assertIsNone(report)

    # Cria phases ausente com .gitkeep e projeta a fila de criação.
    def test_creates_missing_phases(self) -> None:
        seed_vibeflow(self.repo)
        _, report = invoke(self.repo)
        self.assertEqual(1, report["next_n"])
        self.assertEqual("criar", report["modo_sugerido"])
        self.assertTrue((self.repo / ".vibeflow" / "phases" / ".gitkeep").is_file())

    # Confirma que o apply reutiliza a pasta da spec e cria somente o arquivo vivo vazio.
    def test_reuse_spec_folder(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock-bloco"
        phase.mkdir(parents=True)
        (phase / "spec.md").write_text("spec\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply")
        dest = phase / "design.md"
        self.assertTrue(dest.is_file())
        self.assertEqual(b"", dest.read_bytes())
        self.assertTrue((phase / "spec.md").is_file())
        self.assertFalse((vf / "phases" / "phase-2-lock-bloco").exists())
        self.assertEqual("reuse", report["modo"])
        self.assertEqual("phase-1-lock-bloco", report["created"]["dir"])
        self.assertNotIn("wip", report)

    # Confirma que a seleção falha por falta de alvo, sem depender de conteúdo temporário.
    def test_apply_without_alvo_or_slug(self) -> None:
        seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--apply", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("DESIGN_SEM_ALVO", process.stderr)

    # Confirma que --dir sem spec.md recusa com o erro de pré-requisito e não cria o vivo.
    def test_dir_without_spec(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-so-interview"
        phase.mkdir(parents=True)
        (phase / "interview.md").write_text("i\n", encoding="utf-8")
        process, _ = invoke(self.repo, "--apply", "--dir", "phase-1-so-interview", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("DESIGN_SEM_SPEC", process.stderr)
        self.assertFalse((phase / "design.md").exists())

    # Confirma que --slug para fase nova sem spec recusa e limpa a pasta vazia.
    def test_slug_without_spec_refuses_and_cleans_up(self) -> None:
        vf = seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--apply", "--slug", "Pedido Novo", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("DESIGN_SEM_SPEC", process.stderr)
        self.assertFalse((vf / "phases" / "phase-1-pedido-novo").exists())

    # Confirma que plan.md continua sendo um gate de proteção e não é afetado pelo apply.
    def test_design_ja_planejado(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock"
        phase.mkdir(parents=True)
        (phase / "spec.md").write_text("s\n", encoding="utf-8")
        (phase / "design.md").write_text("old\n", encoding="utf-8")
        (phase / "plan.md").write_text("plan\n", encoding="utf-8")
        process, _ = invoke(self.repo, "--apply", "--dir", "phase-1-lock", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("DESIGN_JA_PLANEJADO", process.stderr)
        self.assertEqual("old\n", (phase / "design.md").read_text(encoding="utf-8"))

    # Confirma que o apply repetido não substitui um design vivo já editado.
    def test_preserve_rascunho(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock"
        phase.mkdir(parents=True)
        (phase / "spec.md").write_text("s\n", encoding="utf-8")
        (phase / "design.md").write_text("old\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply")
        self.assertEqual("old\n", (phase / "design.md").read_text(encoding="utf-8"))
        self.assertEqual("atualizar", report["modo"])
        self.assertEqual([], report["actions"])

    # Confirma que o gitignore recebe apenas o relatório desta skill e preserva os irmãos.
    def test_gitignore_preserves_siblings(self) -> None:
        vf = seed_vibeflow(self.repo)
        invoke(self.repo)
        text = (vf / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("init-report.json", text)
        self.assertIn("interview-report.json", text)
        self.assertIn("design-report.json", text)
        self.assertNotIn("design-wip.md", text)

    # Recusa phases como arquivo para não inventariar path fora do contrato.
    def test_phases_file_is_unexpected(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "phases").write_text("nao", encoding="utf-8")
        process, _ = invoke(self.repo, check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("PHASES_INESPERADO", process.stderr)

    # Recusa slug sem caracteres aproveitáveis antes de tocar o disco.
    def test_invalid_slug_on_create(self) -> None:
        seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--apply", "--slug", "!!!", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("SLUG_INVALIDO", process.stderr)

    # Exige spec no MVP antes de preparar o vivo especial.
    def test_mvp_requires_spec(self) -> None:
        seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--mvp", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("DESIGN_SEM_SPEC", process.stderr)

    # Confirma que o alvo MVP é preparado sem criar phase nem conteúdo semântico.
    def test_mvp_apply_prepares_special_target(self) -> None:
        vf = seed_vibeflow(self.repo)
        mvp = vf / "mvp"
        mvp.mkdir()
        (mvp / "spec.md").write_text("spec\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply", "--mvp")
        self.assertEqual(b"", (mvp / "design.md").read_bytes())
        self.assertEqual("mvp", report["rota"])
        self.assertEqual("mvp", report["created"]["kind"])
        self.assertEqual(".vibeflow/mvp", report["alvo"]["path"])
        self.assertNotIn("wip", report)
        self.assertEqual([], [item.name for item in (vf / "phases").iterdir() if item.is_dir()])

    # Confirma que a proteção de plan.md preserva o design vivo em um segundo apply.
    def test_mvp_plan_refuses_update_and_preserves_live_file(self) -> None:
        vf = seed_vibeflow(self.repo)
        mvp = vf / "mvp"
        mvp.mkdir()
        (mvp / "spec.md").write_text("s\n", encoding="utf-8")
        (mvp / "design.md").write_text("old\n", encoding="utf-8")
        (mvp / "plan.md").write_text("plan\n", encoding="utf-8")
        process, _ = invoke(self.repo, "--apply", "--mvp", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("DESIGN_JA_PLANEJADO", process.stderr)
        self.assertEqual("old\n", (mvp / "design.md").read_text(encoding="utf-8"))

    # Recusa seletores de phase no modo MVP para manter um alvo por run.
    def test_mvp_rejects_phase_selectors(self) -> None:
        seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--mvp", "--slug", "produto", check=False)
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
        self.repo = Path.cwd() / f".vibe-design-ps-{uuid.uuid4().hex}"
        self.repo.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.repo, ignore_errors=True)

    # Confirma que o motor PowerShell reusa a pasta da spec como o motor Python.
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
        dest = phase / "design.md"
        self.assertTrue(dest.is_file())
        self.assertEqual(b"", dest.read_bytes())
        self.assertTrue((phase / "spec.md").is_file())

    # Confirma que o motor PowerShell prepara o mesmo alvo MVP sem criar phase.
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
        self.assertEqual(b"", (mvp / "design.md").read_bytes())
        report = json.loads((vf / "design-report.json").read_text(encoding="utf-8"))
        self.assertEqual("mvp", report["created"]["kind"])

    # Confirma que o motor PowerShell também preserva um design vivo já existente.
    def test_apply_preserves_existing_file(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock-bloco"
        phase.mkdir(parents=True)
        (phase / "spec.md").write_text("spec\n", encoding="utf-8")
        dest = phase / "design.md"
        dest.write_bytes(b"design vivo PowerShell\n\x00")
        original = dest.read_bytes()
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual(original, dest.read_bytes())
        report = json.loads((vf / "design-report.json").read_text(encoding="utf-8"))
        self.assertNotIn("wip", report)
        self.assertEqual([], report["actions"])

    # Confirma que o motor PowerShell respeita o gate de plan sem pisar no vivo.
    def test_plan_gate_same_error(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock"
        phase.mkdir(parents=True)
        (phase / "spec.md").write_text("s\n", encoding="utf-8")
        (phase / "design.md").write_text("old\n", encoding="utf-8")
        (phase / "plan.md").write_text("plan\n", encoding="utf-8")
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply", "-Dir", "phase-1-lock"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(0, process.returncode)
        self.assertIn("DESIGN_JA_PLANEJADO", process.stderr)
        self.assertEqual("old\n", (phase / "design.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
