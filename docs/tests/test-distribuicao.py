#!/usr/bin/env python3
"""Contrato da superfície de install: ponteiros, manifests e documentação."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILLS = (
    "vibe-init",
    "vibe-interview",
    "vibe-spec",
    "vibe-design",
    "vibe-plan",
    "vibe-analyze",
    "vibe-implement",
    "vibe-review",
)
CANONICAL_SKILL_PATHS = [f"./{name}" for name in SKILLS]
ANTIGRAVITY_SCHEMA = "https://antigravity.google/schemas/v1/plugin.json"
CONTRACT_VERSION = "3.1.0"


# Carrega JSON de manifesto e falha com o path se o arquivo não existir ou for inválido.
def load_json(relative: str) -> dict:
    path = ROOT / relative
    if not path.is_file():
        raise FileNotFoundError(relative)
    return json.loads(path.read_text(encoding="utf-8-sig"))


class DistribuicaoContracts(unittest.TestCase):
    """C1–C5 da distribuição: oito skills, manifests mínimos e sem aliases."""

    # C2: skills/vibe-* é symlink relativo para o pacote canônico, com SKILL.md no alvo.
    def test_skills_pointers(self) -> None:
        for name in SKILLS:
            link = ROOT / "skills" / name
            self.assertTrue(link.is_symlink(), f"{link} não é symlink")
            target = Path(os_readlink(link))
            self.assertEqual(target.as_posix(), f"../{name}", f"alvo de {name}")
            skill_md = (ROOT / "skills" / name / "SKILL.md").resolve()
            self.assertTrue(skill_md.is_file(), f"SKILL.md ausente no alvo de {name}")

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
        self.assertEqual(plugin["version"], CONTRACT_VERSION)
        self.assertEqual(entry["version"], CONTRACT_VERSION)
        self.assertEqual(plugin["skills"], CANONICAL_SKILL_PATHS)
        self.assertNotIn("commands", plugin)
        self.assertNotIn("commands", entry)

    # C3: Codex aponta skills/ e o marketplace aponta a raiz do repo.
    def test_codex_manifests(self) -> None:
        plugin = load_json(".codex-plugin/plugin.json")
        marketplace = load_json(".agents/plugins/marketplace.json")
        self.assertEqual(plugin["name"], "vibeflow")
        self.assertEqual(plugin["version"], CONTRACT_VERSION)
        self.assertEqual(plugin["skills"], "./skills/")
        self.assertNotIn("commands", plugin)
        entry = marketplace["plugins"][0]
        self.assertEqual(entry["name"], "vibeflow")
        self.assertEqual(entry["version"], CONTRACT_VERSION)
        self.assertEqual(entry["source"]["path"], "./")

    # C3: Grok indexa o plugin na raiz; Antigravity usa plugin.json da raiz.
    def test_grok_and_antigravity_manifests(self) -> None:
        grok = load_json(".grok-plugin/marketplace.json")
        antigravity = load_json("plugin.json")
        entry = grok["plugins"][0]
        self.assertEqual(grok["name"], "vibeflow")
        self.assertEqual(entry["name"], "vibeflow")
        self.assertEqual(entry["version"], CONTRACT_VERSION)
        self.assertEqual(entry["source"]["path"], "./")
        self.assertEqual(antigravity["name"], "vibeflow")
        self.assertFalse((ROOT / "commands").exists(), "commands/ de alias não entra nesta fatia")

    # T4: todos os manifests versionáveis anunciam a mesma versão major do contrato.
    def test_manifest_contract_versions_match(self) -> None:
        manifests = (
            load_json(".claude-plugin/plugin.json")["version"],
            load_json(".claude-plugin/marketplace.json")["plugins"][0]["version"],
            load_json(".codex-plugin/plugin.json")["version"],
            load_json(".agents/plugins/marketplace.json")["plugins"][0]["version"],
            load_json(".grok-plugin/marketplace.json")["plugins"][0]["version"],
        )
        self.assertEqual((CONTRACT_VERSION,) * 5, manifests)

    # C2: o manifest Antigravity usa somente o schema mínimo e não declara componentes por alias.
    def test_antigravity_manifest_minimal(self) -> None:
        antigravity = load_json("plugin.json")
        self.assertEqual(
            set(antigravity),
            {"$schema", "name", "description"},
            "plugin.json não deve carregar campos de outros hosts",
        )
        self.assertEqual(antigravity["$schema"], ANTIGRAVITY_SCHEMA)
        self.assertRegex(antigravity["name"], r"^[a-zA-Z0-9_-]+$")
        self.assertIsInstance(antigravity["description"], str)
        self.assertNotIn("commands", antigravity)

    # C4: README traz escopos, caminhos por host, fallbacks e verificações de descoberta.

    # T5: cada skill investiga por relevância, usa artefato vivo e não revive o contrato operacional removido.

    # C5: o contrato Git fica distribuído entre implement, review e o template de execução.

    # C5: retomada fica na T* aberta; review mantém checkpoint de marco e publicação final.

    # C4: apenas o estado persistido do init permanece no ignore operacional do Vibeflow.

    # C5: o workflow de contrato executa esta suíte.


# Normaliza o alvo do symlink para comparar com o path POSIX da spec.
def os_readlink(path: Path) -> str:
    raw = path.readlink()
    return raw.as_posix()


if __name__ == "__main__":
    unittest.main(verbosity=2)
