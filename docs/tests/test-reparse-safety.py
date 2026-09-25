#!/usr/bin/env python3
"""Prova que os motores não atravessam symlinks, junctions ou artefatos linkados."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INIT_SCRIPT = ROOT / "vibe-init" / "scripts" / "init.py"
INIT_POWERSHELL_SCRIPT = ROOT / "vibe-init" / "scripts" / "init.ps1"
ENGINES = (
    ("interview", "interview.md", ()),
    ("spec", "spec.md", ("interview.md",)),
    ("design", "design.md", ("spec.md",)),
    ("plan", "plan.md", ("spec.md",)),
    ("analyze", "analyze.md", ("spec.md", "plan.md")),
    ("implement", "implement.md", ("plan.md",)),
    ("review", "review.md", ("plan.md",)),
)


# Verifica a disponibilidade do PowerShell 7 antes de iniciar a suíte gêmea.
def powershell7() -> str | None:
    executable = shutil.which("pwsh")
    if not executable:
        return None
    probe = subprocess.run(
        [executable, "-NoProfile", "-Command", "$PSVersionTable.PSVersion.Major"],
        capture_output=True,
        text=True,
        check=False,
    )
    return executable if probe.stdout.strip().isdigit() and int(probe.stdout.strip()) >= 7 else None


# Cria uma raiz mínima isolada para que a prova nunca toque no .vibeflow real.
def seed_repo(root: Path) -> tuple[Path, Path, Path]:
    repo = root / f".reparse-safety-{uuid.uuid4().hex}"
    outside = root / f".reparse-safety-outside-{uuid.uuid4().hex}"
    repo.mkdir()
    outside.mkdir()
    vf = repo / ".vibeflow"
    phases = vf / "phases"
    phases.mkdir(parents=True)
    (vf / ".gitignore").write_text("init-report.json\n", encoding="utf-8")
    return repo, outside, phases


# Cria o link de teste e transforma ausência de privilégio em skip explícito.
def create_link(link: Path, target: Path, *, directory: bool) -> None:
    try:
        link.symlink_to(target, target_is_directory=directory)
    except (OSError, NotImplementedError) as exc:
        raise unittest.SkipTest(f"symlink indisponível neste ambiente: {exc}") from exc


# Executa o motor escolhido com os mesmos argumentos semânticos para Python e PowerShell.
def invoke_engine(skill: str, repo: Path, arguments: list[str], powershell: bool) -> subprocess.CompletedProcess[str]:
    if powershell:
        command = [
            powershell7() or "pwsh",
            "-NoProfile",
            "-File",
            str(ROOT / f"vibe-{skill}" / "scripts" / f"{skill}.ps1"),
            "-Root",
            str(repo),
            "-Apply",
        ]
        index = 0
        while index < len(arguments):
            argument = arguments[index]
            if argument == "--mvp":
                command.append("-Mvp")
                index += 1
                continue
            flag = "-Dir" if argument == "--dir" else "-Slug"
            command.extend([flag, arguments[index + 1]])
            index += 2
    else:
        command = [
            sys.executable,
            str(ROOT / f"vibe-{skill}" / "scripts" / f"{skill}.py"),
            "--root",
            str(repo),
            "--apply",
            *arguments,
        ]
    return subprocess.run(command, capture_output=True, text=True, check=False)


# Decodifica o inventário JSON transitório para confirmar o contrato dos motores.
def output_payload(process: subprocess.CompletedProcess[str]) -> dict:
    if process.returncode != 0:
        raise AssertionError(process.stderr)
    payload = json.loads(process.stdout)
    if not isinstance(payload, dict):
        raise AssertionError("stdout do motor não contém um objeto JSON.")
    return payload


# Executa o init isolado para provar que a raiz .vibeflow linkada é recusada antes da escrita.
def invoke_init(repo: Path, powershell: bool) -> subprocess.CompletedProcess[str]:
    if powershell:
        command = [powershell7() or "pwsh", "-NoProfile", "-File", str(INIT_POWERSHELL_SCRIPT), "-Root", str(repo)]
    else:
        command = [sys.executable, str(INIT_SCRIPT), "--root", str(repo)]
    return subprocess.run(command, capture_output=True, text=True, check=False)


# Prepara um alvo válido para alcançar a emissão transitória do inventário.
def prepare_engine_target(phases: Path, skill: str, prerequisites: tuple[str, ...]) -> list[str]:
    if skill == "interview":
        return ["--slug", "nova fase"]
    phase = phases / "phase-1-target"
    phase.mkdir()
    for prerequisite in prerequisites:
        (phase / prerequisite).write_text("pré-requisito\n", encoding="utf-8")
    return ["--dir", phase.name]


class PythonReparseSafety(unittest.TestCase):
    """Confere isolamento de diretórios e de arquivos vivos no motor Python."""

    # R2: um MVP linkado não pode virar alvo de leitura ou escrita.
    def test_mvp_link_is_rejected(self) -> None:
        for skill, _artifact, _prerequisites in ENGINES:
            with self.subTest(skill=skill):
                repo, outside, _phases = seed_repo(Path.cwd())
                try:
                    create_link(repo / ".vibeflow" / "mvp", outside, directory=True)
                    process = invoke_engine(skill, repo, ["--mvp"], powershell=False)
                    self.assertNotEqual(0, process.returncode)
                    self.assertIn("MVP_INESPERADO", process.stderr)
                    self.assertEqual([], list(outside.iterdir()))
                finally:
                    shutil.rmtree(repo, ignore_errors=True)
                    shutil.rmtree(outside, ignore_errors=True)

    def test_phase_link_is_never_selected_or_written(self) -> None:
        for skill, _artifact, _prerequisites in ENGINES:
            with self.subTest(skill=skill):
                repo, outside, phases = seed_repo(Path.cwd())
                try:
                    create_link(phases / "phase-1-linked", outside, directory=True)
                    arguments = ["--slug", "nova fase"] if skill == "interview" else ["--dir", "phase-1-linked"]
                    process = invoke_engine(skill, repo, arguments, powershell=False)
                    if skill == "interview":
                        self.assertEqual(0, process.returncode, process.stderr)
                        self.assertFalse((outside / "interview.md").exists())
                    else:
                        self.assertNotEqual(0, process.returncode)
                        self.assertIn("FASE_AUSENTE", process.stderr)
                        self.assertEqual([], list(outside.iterdir()))
                finally:
                    shutil.rmtree(repo, ignore_errors=True)
                    shutil.rmtree(outside, ignore_errors=True)

    def test_live_artifact_link_is_rejected(self) -> None:
        for skill, artifact, prerequisites in ENGINES:
            # Implement não prepara implement.md desde que passou a registrar no plan.
            if skill == "implement":
                continue
            with self.subTest(skill=skill):
                repo, outside, phases = seed_repo(Path.cwd())
                try:
                    if skill == "interview":
                        target = repo / ".vibeflow" / "mvp"
                        target.mkdir()
                        phase = target
                        arguments = ["--mvp"]
                    else:
                        phase = phases / "phase-1-target"
                        phase.mkdir()
                        arguments = ["--dir", phase.name]
                    for prerequisite in prerequisites:
                        (phase / prerequisite).write_text("pré-requis\n", encoding="utf-8")
                    external_file = outside / artifact
                    sentinel = b"fora-do-alvo\n\x00"
                    external_file.write_bytes(sentinel)
                    create_link(phase / artifact, external_file, directory=False)
                    process = invoke_engine(skill, repo, arguments, powershell=False)
                    self.assertNotEqual(0, process.returncode)
                    self.assertIn("ARTEFATO_INESPERADO", process.stderr)
                    self.assertEqual(sentinel, external_file.read_bytes())
                finally:
                    shutil.rmtree(repo, ignore_errors=True)
                    shutil.rmtree(outside, ignore_errors=True)

    # R5: o caminho legado de relatório não é escrito nem redireciona saída para fora do repo.
    def test_legacy_report_link_is_ignored(self) -> None:
        for skill, _artifact, prerequisites in ENGINES:
            with self.subTest(skill=skill):
                repo, outside, phases = seed_repo(Path.cwd())
                try:
                    arguments = prepare_engine_target(phases, skill, prerequisites)
                    external_file = outside / f"{skill}-report.json"
                    sentinel = b"relatorio-externo\n\x00"
                    external_file.write_bytes(sentinel)
                    create_link(repo / ".vibeflow" / f"{skill}-report.json", external_file, directory=False)
                    process = invoke_engine(skill, repo, arguments, powershell=False)
                    output_payload(process)
                    self.assertTrue((repo / ".vibeflow" / f"{skill}-report.json").is_symlink())
                    self.assertEqual(sentinel, external_file.read_bytes())
                finally:
                    shutil.rmtree(repo, ignore_errors=True)
                    shutil.rmtree(outside, ignore_errors=True)

    # R5: os motores de inventário não alteram o gitignore operacional.
    def test_gitignore_link_is_ignored_by_inventory(self) -> None:
        for skill, _artifact, prerequisites in ENGINES:
            with self.subTest(skill=skill):
                repo, outside, phases = seed_repo(Path.cwd())
                try:
                    arguments = prepare_engine_target(phases, skill, prerequisites)
                    external_file = outside / f"{skill}-gitignore"
                    sentinel = b"gitignore-externo\n\x00"
                    external_file.write_bytes(sentinel)
                    (repo / ".vibeflow" / ".gitignore").unlink()
                    create_link(repo / ".vibeflow" / ".gitignore", external_file, directory=False)
                    process = invoke_engine(skill, repo, arguments, powershell=False)
                    output_payload(process)
                    self.assertTrue((repo / ".vibeflow" / ".gitignore").is_symlink())
                    self.assertEqual(sentinel, external_file.read_bytes())
                finally:
                    shutil.rmtree(repo, ignore_errors=True)
                    shutil.rmtree(outside, ignore_errors=True)

    # R6: .vibeflow linkado não pode fazer o init gravar REGRAS, phases ou relatórios no alvo externo.
    def test_vibeflow_link_is_rejected(self) -> None:
        repo = Path.cwd() / f".reparse-init-{uuid.uuid4().hex}"
        outside = Path.cwd() / f".reparse-init-outside-{uuid.uuid4().hex}"
        repo.mkdir()
        outside.mkdir()
        sentinel_path = outside / "REGRAS.md"
        sentinel = b"sentinela-init\n\x00"
        sentinel_path.write_bytes(sentinel)
        try:
            create_link(repo / ".vibeflow", outside, directory=True)
            process = invoke_init(repo, powershell=False)
            self.assertNotEqual(0, process.returncode)
            self.assertIn("TIPO_INESPERADO", process.stderr)
            self.assertEqual(sentinel, sentinel_path.read_bytes())
            self.assertFalse((outside / "phases").exists())
            self.assertFalse((outside / "init-report.json").exists())
        finally:
            shutil.rmtree(repo, ignore_errors=True)
            shutil.rmtree(outside, ignore_errors=True)


@unittest.skipUnless(powershell7(), "PowerShell 7 indisponível")
class PowershellReparseSafety(unittest.TestCase):
    """Confere a mesma barreira no motor PowerShell."""

    # R2: um MVP linkado não pode virar alvo de leitura ou escrita.
    def test_mvp_link_is_rejected(self) -> None:
        for skill, _artifact, _prerequisites in ENGINES:
            with self.subTest(skill=skill):
                repo, outside, _phases = seed_repo(Path.cwd())
                try:
                    create_link(repo / ".vibeflow" / "mvp", outside, directory=True)
                    process = invoke_engine(skill, repo, ["--mvp"], powershell=True)
                    self.assertNotEqual(0, process.returncode)
                    self.assertIn("MVP_INESPERADO", process.stderr)
                    self.assertEqual([], list(outside.iterdir()))
                finally:
                    shutil.rmtree(repo, ignore_errors=True)
                    shutil.rmtree(outside, ignore_errors=True)

    def test_phase_link_is_never_selected_or_written(self) -> None:
        for skill, _artifact, _prerequisites in ENGINES:
            with self.subTest(skill=skill):
                repo, outside, phases = seed_repo(Path.cwd())
                try:
                    create_link(phases / "phase-1-linked", outside, directory=True)
                    arguments = ["--slug", "nova fase"] if skill == "interview" else ["--dir", "phase-1-linked"]
                    process = invoke_engine(skill, repo, arguments, powershell=True)
                    if skill == "interview":
                        self.assertEqual(0, process.returncode, process.stderr)
                        self.assertFalse((outside / "interview.md").exists())
                    else:
                        self.assertNotEqual(0, process.returncode)
                        self.assertIn("FASE_AUSENTE", process.stderr)
                        self.assertEqual([], list(outside.iterdir()))
                finally:
                    shutil.rmtree(repo, ignore_errors=True)
                    shutil.rmtree(outside, ignore_errors=True)

    def test_live_artifact_link_is_rejected(self) -> None:
        for skill, artifact, prerequisites in ENGINES:
            # Implement não prepara implement.md desde que passou a registrar no plan.
            if skill == "implement":
                continue
            with self.subTest(skill=skill):
                repo, outside, phases = seed_repo(Path.cwd())
                try:
                    if skill == "interview":
                        target = repo / ".vibeflow" / "mvp"
                        target.mkdir()
                        phase = target
                        arguments = ["--mvp"]
                    else:
                        phase = phases / "phase-1-target"
                        phase.mkdir()
                        arguments = ["--dir", phase.name]
                    for prerequisite in prerequisites:
                        (phase / prerequisite).write_text("pré-requis\n", encoding="utf-8")
                    external_file = outside / artifact
                    sentinel = b"fora-do-alvo\n\x00"
                    external_file.write_bytes(sentinel)
                    create_link(phase / artifact, external_file, directory=False)
                    process = invoke_engine(skill, repo, arguments, powershell=True)
                    self.assertNotEqual(0, process.returncode)
                    self.assertIn("ARTEFATO_INESPERADO", process.stderr)
                    self.assertEqual(sentinel, external_file.read_bytes())
                finally:
                    shutil.rmtree(repo, ignore_errors=True)
                    shutil.rmtree(outside, ignore_errors=True)

    # R5: o caminho legado de relatório não é escrito nem redireciona saída para fora do repo.
    def test_legacy_report_link_is_ignored(self) -> None:
        for skill, _artifact, prerequisites in ENGINES:
            with self.subTest(skill=skill):
                repo, outside, phases = seed_repo(Path.cwd())
                try:
                    arguments = prepare_engine_target(phases, skill, prerequisites)
                    external_file = outside / f"{skill}-report.json"
                    sentinel = b"relatorio-externo\n\x00"
                    external_file.write_bytes(sentinel)
                    create_link(repo / ".vibeflow" / f"{skill}-report.json", external_file, directory=False)
                    process = invoke_engine(skill, repo, arguments, powershell=True)
                    output_payload(process)
                    self.assertTrue((repo / ".vibeflow" / f"{skill}-report.json").is_symlink())
                    self.assertEqual(sentinel, external_file.read_bytes())
                finally:
                    shutil.rmtree(repo, ignore_errors=True)
                    shutil.rmtree(outside, ignore_errors=True)

    # R5: os motores de inventário não alteram o gitignore operacional.
    def test_gitignore_link_is_ignored_by_inventory(self) -> None:
        for skill, _artifact, prerequisites in ENGINES:
            with self.subTest(skill=skill):
                repo, outside, phases = seed_repo(Path.cwd())
                try:
                    arguments = prepare_engine_target(phases, skill, prerequisites)
                    external_file = outside / f"{skill}-gitignore"
                    sentinel = b"gitignore-externo\n\x00"
                    external_file.write_bytes(sentinel)
                    (repo / ".vibeflow" / ".gitignore").unlink()
                    create_link(repo / ".vibeflow" / ".gitignore", external_file, directory=False)
                    process = invoke_engine(skill, repo, arguments, powershell=True)
                    output_payload(process)
                    self.assertTrue((repo / ".vibeflow" / ".gitignore").is_symlink())
                    self.assertEqual(sentinel, external_file.read_bytes())
                finally:
                    shutil.rmtree(repo, ignore_errors=True)
                    shutil.rmtree(outside, ignore_errors=True)

    # R6: .vibeflow linkado não pode fazer o init gravar REGRAS, phases ou relatórios no alvo externo.
    def test_vibeflow_link_is_rejected(self) -> None:
        repo = Path.cwd() / f".reparse-init-{uuid.uuid4().hex}"
        outside = Path.cwd() / f".reparse-init-outside-{uuid.uuid4().hex}"
        repo.mkdir()
        outside.mkdir()
        sentinel_path = outside / "REGRAS.md"
        sentinel = b"sentinela-init\n\x00"
        sentinel_path.write_bytes(sentinel)
        try:
            create_link(repo / ".vibeflow", outside, directory=True)
            process = invoke_init(repo, powershell=True)
            self.assertNotEqual(0, process.returncode)
            self.assertIn("TIPO_INESPERADO", process.stderr)
            self.assertEqual(sentinel, sentinel_path.read_bytes())
            self.assertFalse((outside / "phases").exists())
            self.assertFalse((outside / "init-report.json").exists())
        finally:
            shutil.rmtree(repo, ignore_errors=True)
            shutil.rmtree(outside, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
