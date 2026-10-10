#!/usr/bin/env python3
"""Prova o contrato UTF-8 nos bytes reais dos oito motores e seus erros."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ("init", "interview", "spec", "design", "plan", "analyze", "implement", "review")


# Executa o processo com locale Python legado para impedir verde acidental por ambiente UTF-8.
def invoke(skill: str, repo: Path, powershell: bool) -> subprocess.CompletedProcess[bytes]:
    extension = "ps1" if powershell else "py"
    script = ROOT / f"vibe-{skill}" / "scripts" / f"{skill}.{extension}"
    command = (["pwsh", "-NoProfile", "-File", str(script), "-Root", str(repo)] if powershell
               else [sys.executable, str(script), "--root", str(repo)])
    environment = dict(os.environ, PYTHONIOENCODING="cp1252", PYTHONUTF8="0")
    return subprocess.run(command, capture_output=True, env=environment, check=False)


class StreamEncodingContracts(unittest.TestCase):
    """Cobre inventário, avisos, path do init e erro seguro sem depender do decoder do host."""

    def setUp(self) -> None:
        """Prepara somente raízes descartáveis com caracteres fora de ASCII."""
        self.fixture = Path(tempfile.mkdtemp(prefix=".vibe-stream-", dir=ROOT))

    def tearDown(self) -> None:
        """Falha de remoção deve reprovar a prova em vez de esconder resíduos."""
        shutil.rmtree(self.fixture)

    def prove_engine(self, powershell: bool) -> None:
        """Percorre sucesso e falha de cada ponto de entrada usando decodificação estrita."""
        for skill in SKILLS:
            with self.subTest(skill=skill, powershell=powershell):
                repo = self.fixture / f"{skill}-ação-漢"
                repo.mkdir()
                if skill != "init":
                    phase = repo / ".vibeflow" / "phases" / "phase-1-teste"
                    phase.mkdir(parents=True)
                    (phase / "plan.md").write_text("# Plan: ação\n", encoding="utf-8")
                    (phase.parent / "ignorado-ação").mkdir()
                result = invoke(skill, repo, powershell)
                self.assertEqual(0, result.returncode, result.stderr.decode("utf-8"))
                stdout = result.stdout.decode("utf-8", errors="strict")
                self.assertFalse(result.stdout.startswith(b"\xef\xbb\xbf"))
                self.assertEqual("", result.stderr.decode("utf-8", errors="strict"))
                if skill == "init":
                    expected = repo / ".vibeflow" / "init-report.json"
                    self.assertEqual(str(expected), stdout.strip())
                    self.assertEqual(str(repo), json.loads(expected.read_text(encoding="utf-8"))["root"])
                    failed_repo = repo / "ausência-漢"
                else:
                    payload = json.loads(stdout)
                    if skill != "implement":
                        self.assertEqual(str(repo), payload["root"])
                    self.assertIn("ignorado (nome fora do padrão): ignorado-ação", payload["avisos"])
                    failed_repo = repo / "ausência-漢"
                    failed_repo.mkdir()
                failure = invoke(skill, failed_repo, powershell)
                self.assertNotEqual(0, failure.returncode)
                self.assertEqual("", failure.stdout.decode("utf-8", errors="strict"))
                error = failure.stderr.decode("utf-8", errors="strict")
                self.assertNotIn("Traceback", error)
                if skill == "init":
                    self.assertIn("RAIZ_AUSENTE", error)
                    self.assertIn("ausência-漢", error)
                else:
                    self.assertIn("INIT_AUSENTE", error)
                    self.assertIn("não existe .vibeflow", error)

    def test_python_streams_utf8(self) -> None:
        """Verifica o motor portátil mesmo com PYTHONIOENCODING legado herdado."""
        self.prove_engine(False)

    @unittest.skipUnless(shutil.which("pwsh"), "PowerShell 7 indisponível")
    def test_powershell_streams_utf8(self) -> None:
        """Verifica o motor Windows por bytes, incluindo stderr e caminho Unicode."""
        self.prove_engine(True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
