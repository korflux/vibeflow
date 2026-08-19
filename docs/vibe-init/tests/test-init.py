#!/usr/bin/env python3
"""Contratos nativos e paridade essencial da skill vibe-init canônica."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[3] / "vibe-init"
SCRIPT = SKILL_DIR / "scripts" / "init.py"
POWERSHELL_SCRIPT = SKILL_DIR / "scripts" / "init.ps1"


# Executa o motor Python e devolve processo e relatório, quando produzido.
def invoke(repo: Path, *arguments: str, check: bool = True) -> tuple[subprocess.CompletedProcess[str], dict | None]:
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo), *arguments],
        capture_output=True,
        text=True,
        check=check,
    )
    report_path = repo / ".vibeflow" / "init-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else None
    return process, report


# Altera o consolidado e usa o token do relatório para concluir o merge.
def complete_merge(repo: Path, report: dict, text: str) -> dict:
    target = repo / ".vibeflow" / "REGRAS.md"
    target.write_text(target.read_text(encoding="utf-8") + f"\n{text}\n", encoding="utf-8")
    _, final_report = invoke(repo, "--apply-pointers", "--merge-token", report["apply_token"])
    assert final_report is not None
    return final_report


class PythonContracts(unittest.TestCase):
    """Verifica os invariantes com maior risco de perda ou divergência."""

    # Cria uma raiz isolada e remove tudo automaticamente ao fim de cada teste.
    def setUp(self) -> None:
        self.repo = Path.cwd() / f".vibe-init-python-{uuid.uuid4().hex}"
        self.repo.mkdir()

    # Libera a árvore isolada inclusive quando uma asserção falha.
    def tearDown(self) -> None:
        shutil.rmtree(self.repo, ignore_errors=True)

    # Confirma a criação mínima, os dois links e a ausência de old em repo vazio.
    def test_new_repository(self) -> None:
        _, report = invoke(self.repo)
        self.assertEqual("novo", report["flow"])
        self.assertTrue((self.repo / "AGENTS.md").is_symlink())
        self.assertTrue((self.repo / "CLAUDE.md").is_symlink())
        self.assertFalse((self.repo / ".vibeflow" / "old").exists())

    # Impede que ApplyPointers seja usado antes de o conteúdo legado entrar no consolidado.
    def test_apply_requires_changed_target(self) -> None:
        (self.repo / "AGENTS.md").write_text("regra crítica\n", encoding="utf-8")
        _, report = invoke(self.repo)
        process, _ = invoke(
            self.repo,
            "--apply-pointers",
            "--merge-token",
            report["apply_token"],
            check=False,
        )
        self.assertNotEqual(0, process.returncode)
        self.assertIn("MERGE_NAO_APLICADO", process.stderr)
        self.assertFalse((self.repo / "AGENTS.md").is_symlink())

    # Finaliza um merge válido e elimina o estado operacional pendente.
    def test_apply_after_merge(self) -> None:
        (self.repo / "AGENTS.md").write_text("regra crítica\n", encoding="utf-8")
        _, report = invoke(self.repo)
        complete_merge(self.repo, report, "regra crítica")
        self.assertTrue((self.repo / "AGENTS.md").is_symlink())
        self.assertFalse((self.repo / ".vibeflow" / "init-pending.json").exists())

    # Remove REGRAS.md da raiz somente depois que as duas fontes foram consolidadas.
    def test_duplicate_rules_cleanup(self) -> None:
        (self.repo / ".vibeflow").mkdir()
        (self.repo / ".vibeflow" / "REGRAS.md").write_text("viva\n", encoding="utf-8")
        (self.repo / "REGRAS.md").write_text("raiz\n", encoding="utf-8")
        _, report = invoke(self.repo)
        complete_merge(self.repo, report, "raiz")
        self.assertFalse((self.repo / "REGRAS.md").exists())

    # Preserva regras preexistentes e inclui todos os arquivos operacionais ignorados.
    def test_existing_gitignore(self) -> None:
        (self.repo / ".vibeflow").mkdir()
        ignore = self.repo / ".vibeflow" / ".gitignore"
        ignore.write_text("custom.log\n", encoding="utf-8")
        invoke(self.repo)
        self.assertEqual({"custom.log", "init-report.json", "init-pending.json"}, set(ignore.read_text(encoding="utf-8").splitlines()))

    # Garante que migrations em dependências ignoradas não contaminem o scan factual.
    def test_migration_scan_prunes_dependencies(self) -> None:
        (self.repo / "node_modules" / "pkg" / "migrations").mkdir(parents=True)
        _, report = invoke(self.repo)
        self.assertFalse(report["migrations_detectadas"])

    # Compara o schema e os principais estados dos dois motores quando pwsh está disponível.
    @unittest.skipUnless(shutil.which("pwsh"), "pwsh indisponível para teste de paridade")
    def test_new_repository_contract_parity(self) -> None:
        other = Path.cwd() / f".vibe-init-pwsh-{uuid.uuid4().hex}"
        other.mkdir()
        try:
            subprocess.run(["pwsh", "-NoProfile", "-File", str(POWERSHELL_SCRIPT), "-Root", str(other)], check=True, capture_output=True, text=True)
            _, python_report = invoke(self.repo)
            powershell_report = json.loads((other / ".vibeflow" / "init-report.json").read_text(encoding="utf-8-sig"))
            self.assertEqual(set(powershell_report), set(python_report))
            self.assertEqual(powershell_report["inventory"], python_report["inventory"])
            self.assertEqual([item["op"] for item in powershell_report["actions"]], [item["op"] for item in python_report["actions"]])
            self.assertEqual(powershell_report["slots_abertos"], python_report["slots_abertos"])
        finally:
            shutil.rmtree(other)


if __name__ == "__main__":
    unittest.main(verbosity=2)
