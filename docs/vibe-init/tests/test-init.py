#!/usr/bin/env python3
"""Contratos de AGENTS.md único, preservação de legados e paridade do init."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tomllib
import unittest
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PYTHON = ROOT / "vibe-init" / "scripts" / "init.py"
POWERSHELL = ROOT / "vibe-init" / "scripts" / "init.ps1"
ROLES = ("explorador", "implementador", "verificador", "corretor", "revisor")
ENGINES = (False, True) if shutil.which("pwsh") else (False,)


# Executa um motor em raiz isolada e carrega o relatório operacional produzido.
def invoke(repo: Path, powershell: bool = False, package: Path | None = None) -> tuple[subprocess.CompletedProcess[str], dict | None]:
    engine = package / "scripts" / ("init.ps1" if powershell else "init.py") if package else POWERSHELL if powershell else PYTHON
    command = (["pwsh", "-NoProfile", "-File", str(engine), "-Root", str(repo)] if powershell else [sys.executable, str(engine), "--root", str(repo)])
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

    # Percorre os entrypoints públicos e instalações com alias no pacote ou ancestral, sem reescrita.
    def test_installed_package_aliases_install_and_repeat(self) -> None:
        installation = self.repo / "installation"
        package = installation / "vibe-init"
        shutil.copytree(ROOT / "vibe-init", package)
        package_alias = self.repo / "package-alias"
        package_alias.symlink_to(package, target_is_directory=True)
        parent_alias = self.repo / "parent-alias"
        parent_alias.symlink_to(installation, target_is_directory=True)
        entries = (ROOT / "skills/vibe-init", package_alias, parent_alias / "vibe-init")
        for index, entry in enumerate(entries):
            for powershell in ENGINES:
                with self.subTest(entry=str(entry), powershell=powershell):
                    repo = self.repo / f"project-{index}-{powershell}"
                    repo.mkdir()
                    process, report = invoke(repo, powershell, entry)
                    self.assertEqual(0, process.returncode, process.stderr)
                    self.assertEqual(10, len(report["agent_profiles"]))
                    self.assertEqual({"instalado"}, {item["status"] for item in report["agent_profiles"]})
                    snapshots = {}
                    for item in report["agent_profiles"]:
                        profile = repo / item["path"]
                        source = package / "templates/agents" / item["host"] / profile.name
                        self.assertEqual(source.read_bytes(), profile.read_bytes())
                        snapshots[item["path"]] = (profile.read_bytes(), profile.stat().st_mtime_ns)
                    before = (repo / "AGENTS.md").read_bytes()
                    process, report = invoke(repo, powershell, entry)
                    self.assertEqual(0, process.returncode, process.stderr)
                    self.assertEqual(10, len(report["agent_profiles"]))
                    self.assertEqual({"ja_instalado"}, {item["status"] for item in report["agent_profiles"]})
                    self.assertEqual([], report["actions"])
                    self.assertEqual(before, (repo / "AGENTS.md").read_bytes())
                    for path, (content, modified) in snapshots.items():
                        self.assertEqual(content, (repo / path).read_bytes())
                        self.assertEqual(modified, (repo / path).stat().st_mtime_ns)

    # Percorre instalação, descoberta estrutural, repetição e conflito preservado em ambos os motores.
    def test_profiles_install_repeat_and_preserve_customization(self) -> None:
        for powershell in ENGINES:
            with self.subTest(powershell=powershell):
                repo = self.repo / str(powershell)
                repo.mkdir()
                process, report = invoke(repo, powershell)
                self.assertEqual(0, process.returncode, process.stderr)
                self.assertEqual(10, len(report["agent_profiles"]))
                self.assertEqual({"instalado"}, {entry["status"] for entry in report["agent_profiles"]})
                self.assertEqual({"status": "nao_verificada", "reload_required": True}, report["agent_session"])
                snapshots = {}
                for entry in report["agent_profiles"]:
                    host, role = entry["host"], entry["role"]
                    self.assertIn(role, ROLES)
                    extension = ".toml" if host == "codex" else ".md"
                    expected_path = f".{host}/agents/{role}{extension}"
                    self.assertEqual(expected_path, entry["path"])
                    profile = repo / expected_path
                    source = ROOT / "vibe-init/templates/agents" / host / profile.name
                    self.assertEqual(source.read_bytes(), profile.read_bytes())
                    snapshots[expected_path] = (profile.read_bytes(), profile.stat().st_mtime_ns)
                    if host == "codex":
                        metadata = tomllib.loads(profile.read_text(encoding="utf-8"))
                        self.assertTrue(set(metadata) <= {"name", "description", "model", "model_reasoning_effort", "developer_instructions", "sandbox_mode"})
                        self.assertTrue(isinstance(metadata["developer_instructions"], str))
                        model = "gpt-6-luna" if role in ("explorador", "verificador") else "gpt-6-astra" if role == "revisor" else "gpt-6.1-sol"
                        effort = "max" if role in ("explorador", "verificador") else "low" if role == "revisor" else "medium"
                        self.assertEqual(effort, metadata["model_reasoning_effort"])
                        if role == "explorador": self.assertEqual("read-only", metadata["sandbox_mode"])
                    else:
                        # Os recursos usam frontmatter escalar simples, sem depender de parser YAML externo.
                        lines = profile.read_text(encoding="utf-8").splitlines()
                        self.assertEqual("---", lines[0])
                        end = lines.index("---", 1)
                        metadata = dict(line.split(": ", 1) for line in lines[1:end])
                        self.assertTrue(set(metadata) <= {"name", "description", "model", "effort", "tools"})
                        model = "haiku" if role in ("explorador", "verificador") else "opus" if role == "revisor" else "sonnet"
                        self.assertEqual("medium" if role == "revisor" else "xhigh", metadata["effort"])
                        if role == "explorador": self.assertEqual("Read, Grep, Glob", metadata["tools"])
                    self.assertEqual(role, metadata["name"])
                    self.assertEqual(model, metadata["model"])
                    self.assertTrue(isinstance(metadata["description"], str))
                process, report = invoke(repo, powershell)
                self.assertEqual(0, process.returncode, process.stderr)
                self.assertEqual({"ja_instalado"}, {entry["status"] for entry in report["agent_profiles"]})
                for path, (content, modified) in snapshots.items():
                    self.assertEqual(content, (repo / path).read_bytes())
                    self.assertEqual(modified, (repo / path).stat().st_mtime_ns)
                customized = repo / ".codex/agents/implementador.toml"
                customized.write_bytes(b"personalizado\x00\xff")
                before = customized.stat().st_mtime_ns
                for _ in range(2):
                    process, report = invoke(repo, powershell)
                    self.assertEqual(0, process.returncode, process.stderr)
                    conflicts = [entry for entry in report["agent_profiles"] if entry["status"] == "conflito"]
                    self.assertEqual([".codex/agents/implementador.toml"], [entry["path"] for entry in conflicts])
                    self.assertEqual(b"personalizado\x00\xff", customized.read_bytes())
                    self.assertEqual(before, customized.stat().st_mtime_ns)

    # Um destino inválido no último host impede qualquer mutação anterior ou saída para fora da raiz.
    def test_profiles_preflight_rejects_unsafe_destinations(self) -> None:
        for powershell in ENGINES:
            for scenario in ("file_parent", "directory_leaf", "broken_link", "linked_parent", "linked_leaf", "linked_root"):
                with self.subTest(powershell=powershell, scenario=scenario):
                    repo = self.repo / f"{powershell}-{scenario}"
                    repo.mkdir()
                    outside = self.repo / f"outside-{powershell}-{scenario}"
                    outside.mkdir()
                    sentinel = outside / "sentinel"
                    sentinel.write_bytes(b"preservado")
                    host = repo / ".claude"
                    if scenario == "linked_root":
                        repo.rmdir()
                        repo.symlink_to(outside, target_is_directory=True)
                    elif scenario == "file_parent":
                        host.write_bytes(b"arquivo")
                    elif scenario == "linked_parent":
                        host.symlink_to(outside, target_is_directory=True)
                    else:
                        folder = host / "agents"
                        folder.mkdir(parents=True)
                        target = folder / "revisor.md"
                        if scenario == "directory_leaf": target.mkdir()
                        elif scenario == "broken_link": target.symlink_to(outside / "ausente")
                        else: target.symlink_to(sentinel)
                    process, report = invoke(repo, powershell)
                    self.assertNotEqual(0, process.returncode)
                    self.assertIn("TIPO_INESPERADO", process.stderr)
                    self.assertIsNone(report)
                    self.assertFalse((repo / "AGENTS.md").exists())
                    self.assertFalse((repo / ".codex").exists())
                    self.assertEqual(b"preservado", sentinel.read_bytes())
                    self.assertEqual([sentinel], list(outside.iterdir()))

    # Pacotes danificados são recusados antes de qualquer escrita, inclusive fonte e ancestral linkados.
    def test_profiles_preflight_rejects_invalid_sources(self) -> None:
        for powershell in ENGINES:
            for scenario in ("missing", "large", "directory", "link", "linked_parent"):
                with self.subTest(powershell=powershell, scenario=scenario):
                    base = self.repo / f"source-{powershell}-{scenario}"
                    package = base / "skill"
                    shutil.copytree(ROOT / "vibe-init", package)
                    source = package / "templates/agents/claude/revisor.md"
                    source.unlink()
                    if scenario == "large": source.write_bytes(b"x" * (1024 * 1024 + 1))
                    elif scenario == "directory": source.mkdir()
                    elif scenario == "link": source.symlink_to(package / "templates/agents/codex/revisor.toml")
                    elif scenario == "linked_parent":
                        folder = source.parent
                        moved = base / "claude"
                        folder.rename(moved)
                        (moved / "revisor.md").write_text("perfil", encoding="utf-8")
                        folder.symlink_to(moved, target_is_directory=True)
                    repo = base / "project"
                    repo.mkdir()
                    alias = base / "installed"
                    alias.symlink_to(package, target_is_directory=True)
                    process, _ = invoke(repo, powershell, alias)
                    self.assertNotEqual(0, process.returncode)
                    expected = "PERFIL_AUSENTE" if scenario == "missing" else "FONTE_GRANDE" if scenario == "large" else "TIPO_INESPERADO"
                    self.assertIn(expected, process.stderr)
                    self.assertEqual([], list(repo.iterdir()))

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
