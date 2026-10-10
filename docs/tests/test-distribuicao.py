#!/usr/bin/env python3
"""Contrato da superfície de install: ponteiros, manifests e documentação."""

from __future__ import annotations

import json
import shutil
import tempfile
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
CONTRACT_VERSION = "5.0.0"
# Skills que delegam e carregam a mesma cópia do contrato de delegação.
DELEGATION_COPIES = ("vibe-plan/references/delegation.md", "vibe-implement/references/delegation.md")


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

# Compara os bytes das cópias distribuídas de delegation.md sob `root` e devolve os problemas encontrados.
# A comparação é por bytes, nunca por texto: qualquer diferença, inclusive de fim de linha, é divergência.
def delegation_copy_problems(root: Path) -> list[str]:
    problems: list[str] = []
    contents: dict[str, bytes] = {}
    for relative in DELEGATION_COPIES:
        path = root / relative
        if not path.is_file():
            problems.append(f"ausente: {relative}")
            continue
        contents[relative] = path.read_bytes()
        if not contents[relative]:
            problems.append(f"vazio: {relative}")
    if len(set(contents.values())) > 1:
        problems.append("cópias divergem: " + ", ".join(DELEGATION_COPIES))
    return problems


class DelegacaoContracts(unittest.TestCase):
    """C2 da phase 14: plan e implement distribuem a mesma cópia de references/delegation.md."""

    def setUp(self) -> None:
        # Pasta isolada fora do repo para os casos divergentes; removida no tearDown sem ignorar falha.
        self.sandbox = Path(tempfile.mkdtemp(prefix="vibe-delegation-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.sandbox)

    # Grava as duas cópias na pasta isolada com os bytes informados.
    def _seed(self, plan: bytes, implement: bytes) -> None:
        for relative, data in zip(DELEGATION_COPIES, (plan, implement)):
            path = self.sandbox / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

    # A1/A9: as cópias do repositório existem, não são vazias e têm os mesmos bytes.
    def test_repo_copies_are_identical(self) -> None:
        self.assertEqual([], delegation_copy_problems(ROOT))

    # C2: o teste passa com cópias idênticas e falha com divergência, inclusive de um byte de fim de linha, ausência ou arquivo vazio.
    def test_check_fails_on_divergent_missing_or_empty_copies(self) -> None:
        self._seed(b"contrato\n", b"contrato\n")
        self.assertEqual([], delegation_copy_problems(self.sandbox))

        divergences = {"um byte": b"contrate\n", "fim de linha": b"contrato\r\n"}
        for label, other in divergences.items():
            with self.subTest(label):
                self._seed(b"contrato\n", other)
                problems = delegation_copy_problems(self.sandbox)
                self.assertEqual(1, len(problems), problems)
                self.assertTrue(problems[0].startswith("cópias divergem"), problems)

        self._seed(b"contrato\n", b"contrato\n")
        (self.sandbox / DELEGATION_COPIES[1]).unlink()
        self.assertEqual([f"ausente: {DELEGATION_COPIES[1]}"], delegation_copy_problems(self.sandbox))

        self._seed(b"", b"")
        self.assertEqual([f"vazio: {relative}" for relative in DELEGATION_COPIES], delegation_copy_problems(self.sandbox))


# Normaliza o alvo do symlink para comparar com o path POSIX da spec.
def os_readlink(path: Path) -> str:
    raw = path.readlink()
    return raw.as_posix()


if __name__ == "__main__":
    unittest.main(verbosity=2)
