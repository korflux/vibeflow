#!/usr/bin/env python3
"""Contratos de AGENTS.md único, preservação de legados e paridade do init."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PYTHON = ROOT / "vibe-init" / "scripts" / "init.py"
POWERSHELL = ROOT / "vibe-init" / "scripts" / "init.ps1"


# Executa um motor em raiz isolada e carrega o relatório operacional produzido.
def invoke(repo: Path, powershell: bool = False) -> tuple[subprocess.CompletedProcess[str], dict | None]:
    command = (["pwsh", "-NoProfile", "-File", str(POWERSHELL), "-Root", str(repo)] if powershell else [sys.executable, str(PYTHON), "--root", str(repo)])
    process = subprocess.run(command, capture_output=True, text=True, check=False)
    report_path = repo / ".vibeflow" / "init-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else None
    return process, report


class InitContracts(unittest.TestCase):
    """Verifica criação mínima, migração segura e execução repetida."""

    # Isola cada cenário fora do repositório principal e exige limpeza efetiva.
    def setUp(self) -> None:
        self.repo = Path.cwd() / f".vibe-init-python-{uuid.uuid4().hex}"
        self.repo.mkdir()

    # Remove apenas a pasta conhecida desta fixture após cada teste.
    def tearDown(self) -> None:
        shutil.rmtree(self.repo)

    # O projeto novo recebe somente AGENTS.md como fonte e uma ponte curta do Antigravity.
    def test_new_project_has_one_rules_file(self) -> None:
        process, report = invoke(self.repo)
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual("AGENTS.md", report["target"])
        self.assertTrue((self.repo / "AGENTS.md").is_file())
        self.assertFalse((self.repo / "AGENTS.md").is_symlink())
        self.assertFalse((self.repo / "CLAUDE.md").exists())
        self.assertFalse((self.repo / "REGRAS.md").exists())
        self.assertFalse((self.repo / ".vibeflow" / "REGRAS.md").exists())
        self.assertEqual("@../../AGENTS.md\n", (self.repo / ".agents" / "rules" / "vibeflow.md").read_text(encoding="utf-8"))
        self.assertTrue((self.repo / ".vibeflow" / "phases" / ".gitkeep").is_file())

    # A segunda execução não cria backup nem altera o conteúdo já consolidado.
    def test_idempotent_run(self) -> None:
        invoke(self.repo)
        before = (self.repo / "AGENTS.md").read_bytes()
        process, report = invoke(self.repo)
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual(before, (self.repo / "AGENTS.md").read_bytes())
        self.assertEqual([], report["actions"])

    # Um AGENTS legado é mantido e recebe somente o cabeçalho obrigatório.
    def test_existing_agents_preserves_user_rules(self) -> None:
        (self.repo / "AGENTS.md").write_text("# Projeto\n\nRegra do time\n", encoding="utf-8")
        process, report = invoke(self.repo)
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertIn("Regra do time", (self.repo / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertEqual("# Projeto\n\nRegra do time\n", (self.repo / ".vibeflow" / "old" / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertEqual(1, len(report["olds"]))

    # O formato antigo é convertido na mesma execução depois de materializar e salvar as regras.
    def test_old_symlinks_are_backed_up_before_migration(self) -> None:
        vf = self.repo / ".vibeflow"
        vf.mkdir()
        old_rules = vf / "REGRAS.md"
        old_rules.write_text("# Regra crítica\n", encoding="utf-8")
        (self.repo / "AGENTS.md").symlink_to(".vibeflow/REGRAS.md")
        (self.repo / "CLAUDE.md").symlink_to(".vibeflow/REGRAS.md")
        process, report = invoke(self.repo)
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertFalse((self.repo / "AGENTS.md").is_symlink())
        self.assertIn("Regra crítica", (self.repo / "AGENTS.md").read_text(encoding="utf-8"))
        backup = vf / "old" / "REGRAS-vibeflow.md"
        self.assertFalse(old_rules.exists())
        self.assertFalse((self.repo / "CLAUDE.md").exists())
        self.assertEqual("# Regra crítica\n", backup.read_text(encoding="utf-8"))
        self.assertEqual({".vibeflow/REGRAS.md", "CLAUDE.md"}, set(report["migrated"]))
        self.assertEqual([], report["legacy_present"])

    # Uma segunda fonte diferente permanece até a consolidação semântica.
    def test_distinct_claude_is_reported_for_merge(self) -> None:
        (self.repo / "AGENTS.md").write_text("regra principal\n", encoding="utf-8")
        (self.repo / "CLAUDE.md").write_text("regra exclusiva\n", encoding="utf-8")
        process, report = invoke(self.repo)
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertIn("CLAUDE.md", report["merges"])
        self.assertEqual("regra exclusiva\n", (self.repo / ".vibeflow" / "old" / "CLAUDE.md").read_text(encoding="utf-8"))
        self.assertEqual("regra exclusiva\n", (self.repo / "CLAUDE.md").read_text(encoding="utf-8"))

    # O motor recusa usar um link externo como regras do projeto.
    def test_external_agents_symlink_is_rejected(self) -> None:
        outside = Path.cwd() / "README.md"
        (self.repo / "AGENTS.md").symlink_to(outside)
        process, _ = invoke(self.repo)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("FONTE_EXTERNA", process.stderr)
        self.assertTrue((self.repo / "AGENTS.md").is_symlink())

    # Um falso backup por symlink não autoriza apagar a fonte legada.
    def test_linked_backup_does_not_authorize_migration(self) -> None:
        (self.repo / "CLAUDE.md").write_text("regra legada\n", encoding="utf-8")
        old = self.repo / ".vibeflow" / "old"
        old.mkdir(parents=True)
        (old / "CLAUDE.md").symlink_to("../../CLAUDE.md")
        process, _ = invoke(self.repo)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("TIPO_INESPERADO", process.stderr)
        self.assertTrue((self.repo / "CLAUDE.md").is_file())

    # Mantém o motor PowerShell equivalente para criação e migração essenciais.
    @unittest.skipUnless(shutil.which("pwsh"), "PowerShell 7 indisponível")
    def test_powershell_parity(self) -> None:
        process, report = invoke(self.repo, powershell=True)
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual("AGENTS.md", report["target"])
        self.assertEqual("@../../AGENTS.md\n", (self.repo / ".agents" / "rules" / "vibeflow.md").read_text(encoding="utf-8"))
        self.assertFalse((self.repo / "CLAUDE.md").exists())


if __name__ == "__main__":
    unittest.main()
