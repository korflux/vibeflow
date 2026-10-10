#!/usr/bin/env python3
"""Prova cache transitório da descoberta sem substituir a execução dos motores."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SUITES = tuple(ROOT / f"docs/vibe-{name}/tests/test-{name}.py" for name in (
    "interview", "spec", "design", "plan", "analyze", "implement", "review",
)) + (ROOT / "docs/tests/test-reparse-safety.py",)


def load_suite(path: Path):
    """Carrega uma suíte independente, incluindo descoberta feita pelo decorator de skip."""
    spec = importlib.util.spec_from_file_location("runtime_fixture", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compatible_discoveries() -> list[int]:
    """Conta probes simulados de disponibilidade, sem executar ou mockar motores funcionais."""
    counts = []
    for path in SUITES:
        with patch("shutil.which", return_value="fixture-pwsh"), patch(
            "subprocess.run", return_value=subprocess.CompletedProcess([], 0, "7\n", "")
        ) as probe:
            module = load_suite(path)
            try:
                for _ in range(3):
                    assert module.powershell7() == "fixture-pwsh"
                counts.append(probe.call_count)
            finally:
                module.powershell7.cache_clear()
    return counts


class RuntimeDiscoveryContracts(unittest.TestCase):
    """Disponibilidade, incompatibilidade, isolamento e cache em imports reais das suítes."""

    def test_import_and_calls_share_one_probe(self) -> None:
        """O decorator e todos os consumidores usam a mesma descoberta durante o processo."""
        self.assertEqual([1] * len(SUITES), compatible_discoveries())

    def test_missing_runtime_remains_skip_without_probe(self) -> None:
        """Ausência permanece skip explícito e também é memorizada apenas na suíte carregada."""
        for path in SUITES:
            with self.subTest(path=path), patch("shutil.which", return_value=None) as which, patch("subprocess.run") as probe:
                module = load_suite(path)
                try:
                    self.assertIsNone(module.powershell7())
                    self.assertIsNone(module.powershell7())
                    self.assertEqual(1, which.call_count)
                    probe.assert_not_called()
                    skipped = [value for value in vars(module).values() if isinstance(value, type) and getattr(value, "__unittest_skip__", False)]
                    self.assertTrue(skipped, "A suíte deve preservar skip sem PowerShell 7")
                finally:
                    module.powershell7.cache_clear()

    def test_incompatible_runtime_and_environment_changes_are_isolated(self) -> None:
        """Cada ambiente simulado limpa o cache, sem vazar indisponibilidade para outro caso."""
        for path in SUITES:
            for output in ("6\n", "invalido\n", ""):
                with self.subTest(path=path, output=output), patch("shutil.which", return_value="fixture-pwsh"), patch(
                    "subprocess.run", return_value=subprocess.CompletedProcess([], 0, output, "")
                ) as probe:
                    module = load_suite(path)
                    try:
                        self.assertIsNone(module.powershell7())
                        self.assertEqual(1, probe.call_count)
                        self.assertTrue(any(isinstance(value, type) and getattr(value, "__unittest_skip__", False) for value in vars(module).values()))
                        module.powershell7.cache_clear()
                        probe.return_value = subprocess.CompletedProcess([], 0, "7\n", "")
                        self.assertEqual("fixture-pwsh", module.powershell7())
                        self.assertEqual("fixture-pwsh", module.powershell7())
                        self.assertEqual(2, probe.call_count)
                    finally:
                        module.powershell7.cache_clear()

    def test_new_process_discovers_again(self) -> None:
        """Dois processos novos fazem seus próprios probes, sem cache em disco ou no pai."""
        for _ in range(2):
            process = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--probe-child"], capture_output=True, text=True, encoding="utf-8", check=True)
            self.assertEqual([1] * len(SUITES), json.loads(process.stdout))


if __name__ == "__main__":
    if sys.argv[1:] == ["--probe-child"]:
        print(json.dumps(compatible_discoveries()))
    else:
        unittest.main()
