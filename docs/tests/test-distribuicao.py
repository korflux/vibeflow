#!/usr/bin/env python3
"""Contrato da superfície de install: ponteiros, manifests e documentação."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILLS = (
    "vibe-init",
    "vibe-interview",
    "vibe-spec",
    "vibe-plan",
    "vibe-analyze",
    "vibe-implement",
    "vibe-review",
)
CANONICAL_SKILL_PATHS = [f"./{name}" for name in SKILLS]


# Lê o name do frontmatter YAML; é o identificador que o CLI e o slash usam.
def frontmatter_name(skill_md: Path) -> str:
    text = skill_md.read_text(encoding="utf-8-sig")
    match = re.search(r"^---\s*\n.*?^name:\s*(\S+)\s*$", text, re.MULTILINE | re.DOTALL)
    if not match:
        raise AssertionError(f"frontmatter sem name em {skill_md}")
    return match.group(1)


# Carrega JSON de manifesto e falha com o path se o arquivo não existir ou for inválido.
def load_json(relative: str) -> dict:
    path = ROOT / relative
    if not path.is_file():
        raise FileNotFoundError(relative)
    return json.loads(path.read_text(encoding="utf-8-sig"))


class DistribuicaoContracts(unittest.TestCase):
    """C1–C5 da spec phase-4: sete skills, um plugin, sem alias de slash."""

    # C2: skills/vibe-* é symlink relativo para o pacote canônico, com SKILL.md no alvo.
    def test_skills_pointers(self) -> None:
        names: list[str] = []
        for name in SKILLS:
            link = ROOT / "skills" / name
            self.assertTrue(link.is_symlink(), f"{link} não é symlink")
            target = Path(os_readlink(link))
            self.assertEqual(target.as_posix(), f"../{name}", f"alvo de {name}")
            skill_md = (ROOT / "skills" / name / "SKILL.md").resolve()
            self.assertTrue(skill_md.is_file(), f"SKILL.md ausente no alvo de {name}")
            names.append(frontmatter_name(skill_md))
        self.assertEqual(names, list(SKILLS))
        self.assertEqual(len(set(names)), 7)

    # C1: descoberta pelo local padrão do CLI (skills/) não duplica name.
    def test_unique_names_under_skills(self) -> None:
        found = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))
        self.assertEqual(found, sorted(SKILLS))

    # C3: Claude lista só ./vibe-* (source raiz), sem commands/ de alias.
    def test_claude_manifests(self) -> None:
        marketplace = load_json(".claude-plugin/marketplace.json")
        plugin = load_json(".claude-plugin/plugin.json")
        self.assertEqual(marketplace["name"], "vibeflow")
        entry = marketplace["plugins"][0]
        self.assertEqual(entry["name"], "vibeflow")
        self.assertEqual(entry["source"], "./")
        self.assertEqual(entry["skills"], CANONICAL_SKILL_PATHS)
        self.assertEqual(plugin["name"], "vibeflow")
        self.assertEqual(plugin["version"], "1.0.0")
        self.assertEqual(plugin["skills"], CANONICAL_SKILL_PATHS)
        self.assertNotIn("commands", plugin)
        self.assertNotIn("commands", entry)

    # C3: Codex aponta skills/ e o marketplace aponta a raiz do repo.
    def test_codex_manifests(self) -> None:
        plugin = load_json(".codex-plugin/plugin.json")
        marketplace = load_json(".agents/plugins/marketplace.json")
        self.assertEqual(plugin["name"], "vibeflow")
        self.assertEqual(plugin["version"], "1.0.0")
        self.assertEqual(plugin["skills"], "./skills/")
        self.assertNotIn("commands", plugin)
        entry = marketplace["plugins"][0]
        self.assertEqual(entry["name"], "vibeflow")
        self.assertEqual(entry["source"]["path"], "./")

    # C3: Grok indexa o plugin na raiz; Antigravity usa plugin.json da raiz.
    def test_grok_and_antigravity_manifests(self) -> None:
        grok = load_json(".grok-plugin/marketplace.json")
        antigravity = load_json("plugin.json")
        entry = grok["plugins"][0]
        self.assertEqual(grok["name"], "vibeflow")
        self.assertEqual(entry["name"], "vibeflow")
        self.assertEqual(entry["source"]["path"], "./")
        self.assertEqual(antigravity["name"], "vibeflow")
        self.assertEqual(antigravity["version"], "1.0.0")
        self.assertNotIn("commands", antigravity)
        self.assertFalse((ROOT / "commands").exists(), "commands/ de alias não entra nesta fatia")

    # C4: README traz CLI global/projeto e os quatro installs nativos.
    def test_readme_install_commands(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        required = (
            "npx skills add korflux/vibeflow -g -a grok -a claude-code -a codex -a antigravity -y",
            "npx skills add korflux/vibeflow -a grok -a claude-code -a codex -a antigravity -y",
            "/plugin marketplace add korflux/vibeflow",
            "/plugin install vibeflow@vibeflow",
            "codex plugin marketplace add korflux/vibeflow",
            "codex plugin add vibeflow@vibeflow",
            "agy plugin install https://github.com/korflux/vibeflow.git",
            "grok plugin marketplace add korflux/vibeflow",
            "grok plugin install vibeflow --trust",
        )
        missing = [line for line in required if line not in readme]
        self.assertEqual(missing, [], f"README sem: {missing}")

    # C5: o workflow de contrato executa esta suíte.
    def test_ci_runs_this_suite(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "contrato.yml").read_text(encoding="utf-8-sig")
        self.assertIn("docs/tests/test-distribuicao.py", workflow)


# Normaliza o alvo do symlink para comparar com o path POSIX da spec.
def os_readlink(path: Path) -> str:
    raw = path.readlink()
    return raw.as_posix()


if __name__ == "__main__":
    unittest.main(verbosity=2)
