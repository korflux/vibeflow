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
    "vibe-design",
    "vibe-plan",
    "vibe-analyze",
    "vibe-implement",
    "vibe-review",
)
CANONICAL_SKILL_PATHS = [f"./{name}" for name in SKILLS]
ANTIGRAVITY_SCHEMA = "https://antigravity.google/schemas/v1/plugin.json"


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
    """C1–C5 da distribuição: oito skills, manifests mínimos e sem aliases."""

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
        self.assertEqual(len(set(names)), 8)

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
        self.assertFalse((ROOT / "commands").exists(), "commands/ de alias não entra nesta fatia")

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
    def test_readme_install_commands(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
        required = (
            "### Instalador `npx skills`, project-local e global",
            "npx skills add korflux/vibeflow -g -a grok -a claude-code -a codex -a antigravity -y",
            "npx skills add korflux/vibeflow -a grok -a claude-code -a codex -a antigravity -y",
            "./<agent>/skills/",
            "~/<agent>/skills/",
            "### Antigravity IDE",
            ".agents/plugins/vibeflow/",
            "~/.gemini/config/plugins/vibeflow/",
            ".agents/rules/vibeflow.md",
            "@../../.vibeflow/REGRAS.md",
            "~/.gemini/antigravity/skills/",
            "### Antigravity CLI",
            "~/.gemini/antigravity-cli/plugins/vibeflow/",
            "agy plugin list",
            "/plugin marketplace add korflux/vibeflow",
            "/plugin install vibeflow@vibeflow",
            "codex plugin marketplace add korflux/vibeflow",
            "codex plugin add vibeflow@vibeflow",
            "~/.codex/AGENTS.md",
            "~/.gemini/GEMINI.md",
            "grok inspect",
            "agy plugin install https://github.com/korflux/vibeflow.git",
            "grok plugin marketplace add korflux/vibeflow",
            "grok plugin install vibeflow --trust",
        )
        missing = [line for line in required if line not in readme]
        self.assertEqual(missing, [], f"README sem: {missing}")

    # T5: cada skill investiga por relevância, usa artefato vivo e não revive o contrato operacional removido.
    def test_skill_guidance_is_directed_and_isolated(self) -> None:
        skill_texts = {
            name: (ROOT / name / "SKILL.md").read_text(encoding="utf-8-sig")
            for name in SKILLS
        }
        for name, text in skill_texts.items():
            self.assertIn("rg --files", text, name)
            self.assertIn("rg -n", text, name)
            self.assertIn("árvore inteira", text, name)
            self.assertNotIn("wip", text.lower(), name)
            if name not in ("vibe-plan", "vibe-review"):
                self.assertNotIn("checkpoint", text.lower(), name)

        for name in ("vibe-plan", "vibe-analyze", "vibe-implement", "vibe-review"):
            self.assertIn("novo chat", skill_texts[name].lower(), name)
        self.assertIn("um chat por T*", skill_texts["vibe-implement"], "vibe-implement")

        template_names = (
            "vibe-interview",
            "vibe-spec",
            "vibe-design",
            "vibe-plan",
            "vibe-analyze",
            "vibe-implement",
            "vibe-review",
        )
        for name in template_names:
            template = (ROOT / name / "templates" / f"{name.removeprefix('vibe-')}.md").read_text(
                encoding="utf-8-sig"
            )
            self.assertIn("# Status: rascunho", template, name)
            self.assertIn("artefato vivo", template.lower(), name)
            self.assertIn("chat", template.lower(), name)
            self.assertNotIn("wip", template.lower(), name)
            if name not in ("vibe-plan", "vibe-review"):
                self.assertNotIn("checkpoint", template.lower(), name)

    # C5: o contrato Git fica distribuído entre implement, review e o template de execução.
    def test_task_commit_and_phase_push_contract(self) -> None:
        implement = (ROOT / "vibe-implement" / "SKILL.md").read_text(encoding="utf-8-sig")
        review = (ROOT / "vibe-review" / "SKILL.md").read_text(encoding="utf-8-sig")
        self.assertIn("task(Tn)", implement)
        self.assertIn("Não faça `git push` nesta etapa", implement)
        self.assertIn("Finalização Git da phase", review)
        self.assertIn("git push", review)
        self.assertIn("sem `--force`", review)
        self.assertNotIn("checkpoint", implement.lower())
        self.assertIn("checkpoint nunca abre finalização git", review.lower())

    # C5: checkpoint fica no plan e na review, com publicação reservada à etapa final.
    def test_checkpoint_contract_is_declared_and_scoped(self) -> None:
        paths = [
            ROOT / "README.md",
            ROOT / ".vibeflow" / "REGRAS.md",
        ]
        for name in SKILLS:
            if name in ("vibe-plan", "vibe-review"):
                continue
            paths.extend((ROOT / name / "SKILL.md", ROOT / "docs" / name / "ARQUITETURA.md", ROOT / "docs" / name / "ANALISE.md"))
            if name != "vibe-init":
                stem = name.removeprefix("vibe-")
                paths.append(ROOT / name / "templates" / f"{stem}.md")
            else:
                paths.append(ROOT / name / "templates" / "REGRAS.md")
        for path in paths:
            content = path.read_text(encoding="utf-8-sig").lower()
            self.assertNotIn("checkpoint", content, str(path))
            self.assertNotIn("check point", content, str(path))

        allowed = (
            ROOT / "docs" / "ESCOPO.md",
            ROOT / "vibe-plan" / "SKILL.md",
            ROOT / "vibe-plan" / "templates" / "plan.md",
            ROOT / "docs" / "vibe-plan" / "ARQUITETURA.md",
            ROOT / "docs" / "vibe-plan" / "ANALISE.md",
            ROOT / "vibe-review" / "SKILL.md",
            ROOT / "vibe-review" / "templates" / "review.md",
            ROOT / "docs" / "vibe-review" / "ARQUITETURA.md",
            ROOT / "docs" / "vibe-review" / "ANALISE.md",
        )
        for path in allowed:
            content = path.read_text(encoding="utf-8-sig").lower()
            self.assertIn("checkpoint", content, str(path))
            self.assertNotIn("check point", content, str(path))

    # C4: o transporte temporário removido não pode reaparecer no ignore operacional.
    def test_vibeflow_gitignore_has_no_wip_entry(self) -> None:
        gitignore = (ROOT / ".vibeflow" / ".gitignore").read_text(encoding="utf-8-sig")
        self.assertEqual([], [line for line in gitignore.splitlines() if "wip" in line.lower()])

    # C5: o workflow de contrato executa esta suíte.
    def test_ci_runs_this_suite(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "contrato.yml").read_text(encoding="utf-8-sig")
        self.assertIn("docs/tests/test-distribuicao.py", workflow)
        self.assertIn("docs/tests/test-mvp-flow.py", workflow)
        self.assertIn("docs/tests/test-visual-contract.py", workflow)


# Normaliza o alvo do symlink para comparar com o path POSIX da spec.
def os_readlink(path: Path) -> str:
    raw = path.readlink()
    return raw.as_posix()


if __name__ == "__main__":
    unittest.main(verbosity=2)
