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
# Caminho do template vivo; os contratos abaixo garantem jornadas e acesso obrigatórios.
TEMPLATE = SKILL_DIR / "templates" / "interview.md"


# Executa o motor Python e decodifica o inventário transitório enviado no stdout.
def invoke(repo: Path, *arguments: str, check: bool = True) -> tuple[subprocess.CompletedProcess[str], dict | None]:
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo), *arguments],
        capture_output=True,
        text=True,
        check=check,
    )
    report = json.loads(process.stdout) if process.returncode == 0 and process.stdout.strip() else None
    return process, report


# Cria só a pasta .vibeflow, como se o init tivesse rodado sem phases.
def seed_vibeflow(repo: Path) -> Path:
    vf = repo / ".vibeflow"
    vf.mkdir()
    (vf / ".gitignore").write_text("init-report.json\ninit-pending.json\n", encoding="utf-8")
    return vf


class PythonContracts(unittest.TestCase):
    """Verifica os invariantes com maior risco de path, número ou perda do vivo."""

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
        self.assertEqual("phase", report["modo"])
        self.assertIsNone(report["mvp"])
        self.assertIsNone(report["alvo"])
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

    # Confirma que o apply prepara o artefato sem depender de um rascunho temporário.
    def test_apply_creates_live_file_without_draft(self) -> None:
        seed_vibeflow(self.repo)
        process, report = invoke(self.repo, "--apply", "--slug", "dashboard")
        self.assertEqual(0, process.returncode)
        self.assertTrue((self.repo / ".vibeflow" / "phases" / "phase-1-dashboard" / "interview.md").is_file())
        self.assertNotIn("wip", report)

    # Confirma que o slug continua sanitizado e que o arquivo novo começa vazio.
    def test_apply_prepares_sanitized_slug(self) -> None:
        vf = seed_vibeflow(self.repo)
        _, report = invoke(self.repo, "--apply", "--slug", "Dashboard Standup!!")
        dest = vf / "phases" / "phase-1-dashboard-standup" / "interview.md"
        self.assertTrue(dest.is_file())
        self.assertEqual(b"", dest.read_bytes())
        self.assertEqual("phase-1-dashboard-standup", report["created"]["dir"])
        self.assertEqual("phase", report["created"]["kind"])
        self.assertEqual(2, report["next_n"])
        self.assertEqual("phase-1-dashboard-standup", report["aberta"]["dir"])
        self.assertEqual("criar_arquivo", report["actions"][-1]["op"])

    # Confirma que cada novo pedido recebe seu próprio número sem reaproveitar conteúdo anterior.
    def test_second_apply_increments(self) -> None:
        vf = seed_vibeflow(self.repo)
        invoke(self.repo, "--apply", "--slug", "primeiro")
        _, report = invoke(self.repo, "--apply", "--slug", "segundo")
        self.assertTrue((vf / "phases" / "phase-2-segundo" / "interview.md").is_file())
        self.assertEqual(2, report["created"]["n"])

    # Confirma que o gate de slug ocorre antes de qualquer criação do destino.
    def test_invalid_slug(self) -> None:
        seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--apply", "--slug", "!!!", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("SLUG_INVALIDO", process.stderr)

    # Confirma que uma colisão de pasta não é mascarada pela preparação do arquivo vivo.
    def test_fase_existe(self) -> None:
        vf = seed_vibeflow(self.repo)
        phases = vf / "phases"
        phases.mkdir()
        # Destino com o próximo n, mas que o inventário não conta (é arquivo, não pasta).
        (phases / "phase-1-dashboard").write_text("colisao", encoding="utf-8")
        process, _ = invoke(self.repo, "--apply", "--slug", "dashboard", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("FASE_EXISTE", process.stderr)

    # Confirma que o JSON transitório não cria relatório nem altera o gitignore de init.
    def test_stdout_report_does_not_mutate_workspace(self) -> None:
        vf = seed_vibeflow(self.repo)
        original = (vf / ".gitignore").read_bytes()
        _, report = invoke(self.repo)
        self.assertIsNotNone(report)
        self.assertEqual(original, (vf / ".gitignore").read_bytes())
        self.assertEqual([], list(vf.glob("*-report.json")))

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

    # Confirma que o alvo MVP é preparado sem criar fase cronológica nem conteúdo semântico.
    def test_mvp_apply_prepares_without_creating_phase(self) -> None:
        vf = seed_vibeflow(self.repo)
        _, report = invoke(self.repo, "--apply", "--mvp")
        dest = vf / "mvp" / "interview.md"
        self.assertEqual(b"", dest.read_bytes())
        self.assertEqual("mvp", report["modo"])
        self.assertEqual("mvp", report["created"]["kind"])
        self.assertEqual(".vibeflow/mvp", report["alvo"]["path"])
        self.assertNotIn("wip", report)
        self.assertEqual([], [item.name for item in (vf / "phases").iterdir() if item.is_dir()])

    # Confirma que um segundo apply preserva byte a byte o vivo já existente.
    def test_mvp_second_apply_preserves_live_file(self) -> None:
        vf = seed_vibeflow(self.repo)
        invoke(self.repo, "--apply", "--mvp")
        dest = vf / "mvp" / "interview.md"
        dest.write_bytes(b"conteudo vivo\n\x00")
        original = dest.read_bytes()
        process, report = invoke(self.repo, "--apply", "--mvp")
        self.assertEqual(0, process.returncode)
        self.assertEqual(original, (vf / "mvp" / "interview.md").read_bytes())
        self.assertEqual([], report["actions"])

    def test_mvp_path_as_file_is_unexpected(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "mvp").write_text("não é pasta", encoding="utf-8")
        process, _ = invoke(self.repo, "--mvp", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("MVP_INESPERADO", process.stderr)

    def test_mvp_rejects_slug(self) -> None:
        seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--mvp", "--slug", "produto", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("MODO_INVALIDO", process.stderr)


# Contratos do template vivo; garantem jornadas genéricas e checklist de acesso obrigatórios.
class TemplateContracts(unittest.TestCase):
    """Verifica que o template exige jornadas e acesso com N/A explícito."""

    # Lê o template canônico sem depender de .vibeflow ou do motor.
    def read_template(self) -> str:
        return TEMPLATE.read_text(encoding="utf-8")

    # Confirma que a tabela de jornadas exige as 8 colunas do contrato.
    def test_jornadas_exigem_oito_colunas(self) -> None:
        text = self.read_template()
        for coluna in ("Jornada", "Ator", "Gatilho", "Objetivo", "Telas envolvidas", "Entrada", "Saída", "Estado crítico"):
            self.assertIn(coluna, text)

    # Confirma que o checklist de acesso cobre os 8 itens com N/A explícito.
    def test_acesso_exige_checklist_com_na(self) -> None:
        text = self.read_template().lower()
        for item in ("login", "cadastro", "recuperação", "sessão", "papéis", "primeiro usuário", "bloqueio", "logout"):
            self.assertIn(item, text)
        self.assertIn("n/a", text)

    # Confirma que o template declara o invariante de jornada incompleta como defeito.
    def test_jornada_incompleta_e_defeito(self) -> None:
        text = self.read_template()
        self.assertIn("sem saída", text)
        self.assertIn("sem estado crítico", text)
        self.assertIn("Texto livre sem tabela é defeito", text)


# Verifica se existe uma versão real de PowerShell 7, única suportada pelo motor gêmeo.
def powershell7() -> str | None:
    executable = shutil.which("pwsh")
    if not executable:
        return None
    probe = subprocess.run([executable, "-NoProfile", "-Command", "$PSVersionTable.PSVersion.Major"], capture_output=True, text=True, check=False)
    return executable if probe.stdout.strip().isdigit() and int(probe.stdout.strip()) >= 7 else None

@unittest.skipUnless(powershell7(), "PowerShell 7 indisponível")
class PowershellParity(unittest.TestCase):
    """Confere que o apply essencial do PowerShell grava o mesmo path."""

    def setUp(self) -> None:
        self.repo = Path.cwd() / f".vibe-interview-ps-{uuid.uuid4().hex}"
        self.repo.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.repo, ignore_errors=True)

    def test_apply_same_path(self) -> None:
        vf = seed_vibeflow(self.repo)
        process = subprocess.run(
            [powershell7(),
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
        self.assertEqual(b"", dest.read_bytes())

    # Confirma que o motor PowerShell entrega a seleção MVP no stdout sem persistir relatório.
    def test_mvp_apply_same_path(self) -> None:
        vf = seed_vibeflow(self.repo)
        process = subprocess.run(
            [powershell7(),
                "-File",
                str(POWERSHELL_SCRIPT),
                "-Root",
                str(self.repo),
                "-Apply",
                "-Mvp",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        dest = vf / "mvp" / "interview.md"
        self.assertEqual(b"", dest.read_bytes())
        report = json.loads(process.stdout)
        self.assertFalse((vf / "interview-report.json").exists())
        self.assertEqual("mvp", report["created"]["kind"])

    # Confirma que o motor PowerShell também preserva um interview vivo já existente.
    def test_mvp_apply_preserves_existing_file(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "phases").mkdir()
        mvp = vf / "mvp"
        mvp.mkdir()
        dest = mvp / "interview.md"
        dest.write_bytes(b"vivo PowerShell\n\x00")
        original = dest.read_bytes()
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply", "-Mvp"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual(original, dest.read_bytes())
        report = json.loads(process.stdout)
        self.assertFalse((vf / "interview-report.json").exists())
        self.assertNotIn("wip", report)
        self.assertEqual([], report["actions"])


if __name__ == "__main__":
    unittest.main()
