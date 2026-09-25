#!/usr/bin/env python3
"""Verifica o contrato textual de prova visual e controles acessíveis."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REFERENCE_PATHS = (
    ROOT / "vibe-implement" / "references" / "chrome-devtools.md",
    ROOT / "vibe-review" / "references" / "ui-visual-quality.md",
)
SKILL_PATHS = (
    ROOT / "vibe-plan" / "SKILL.md",
    ROOT / "vibe-implement" / "SKILL.md",
    ROOT / "vibe-review" / "SKILL.md",
)


# Lê os arquivos do contrato para manter os testes independentes de importação Markdown.
def read_contract(paths: tuple[Path, ...]) -> str:
    return "\n".join(path.read_text(encoding="utf-8-sig") for path in paths).lower()


class VisualContract(unittest.TestCase):
    """C6-C7: checklist renderizada, controles semânticos e seleção de ferramenta."""

    # Garante que as referências operacionais mantenham uma checklist única e completa.
    def test_references_cover_rendered_checklist(self) -> None:
        references = read_contract(REFERENCE_PATHS)
        required_terms = (
            "overflow",
            "viewport",
            "fora da viewport",
            "clipping",
            "sobrepos",
            "cobert",
            "z-index",
            "truncamento",
            "quebra de texto",
            "proporção de largura",
            "controles maiores",
            "input com ícone",
            "viewport estreita",
            "loading",
            "empty",
            "error",
            "success",
            "foco visível",
            "teclado",
            "contraste",
            "console",
            "rede",
            "assets",
        )
        for term in required_terms:
            self.assertIn(term, references, term)

    # Confirma que icon-only reduz ruído sem remover semântica ou suporte à operação.
    def test_compact_controls_keep_semantics_and_accessibility(self) -> None:
        contract = read_contract(REFERENCE_PATHS + SKILL_PATHS)
        required_terms = (
            "icon-only",
            "lixeira",
            "apagar",
            "nome acessível",
            "área de interação",
            "foco visível",
            "tooltip",
            "ações ambíguas",
        )
        for term in required_terms:
            self.assertIn(term, contract, term)
        self.assertRegex(contract, r"icon-only.{0,180}universalmente reconhec")
        self.assertRegex(contract, r"ações ambíguas.{0,180}texto")

    # Mantém a seleção de ferramenta e a prova visual distribuídas entre skill e referência.
    def test_tool_selection_and_fallback_are_explicit(self) -> None:
        skills = read_contract(SKILL_PATHS)
        references = read_contract(REFERENCE_PATHS)
        for term in ("navegador integrado", "chrome-devtools", "playwright"):
            self.assertIn(term, skills, term)
        for term in ("snapshot", "screenshot", "dom", "estilos", "console", "rede", "assets"):
            self.assertIn(term, references, term)
        self.assertIn("se faltar ferramenta, tente disponibilizá-la", skills)
        self.assertRegex(skills, r"não .*passe|não .*aprove|não marque.*conclu")
        plan = (ROOT / "vibe-plan" / "SKILL.md").read_text(encoding="utf-8-sig").lower()
        self.assertNotIn("alocar uma task inicial para instalação/configuração do mcp", plan)

    # Exige que a orientação preserve a prova contextual, não apenas uma captura isolada.
    def test_visual_proof_records_context(self) -> None:
        contract = read_contract(REFERENCE_PATHS + SKILL_PATHS)
        for term in ("rota", "viewport", "estado", "ações", "evidência"):
            self.assertIn(term, contract, term)
        self.assertIn("screenshot isolado não substitui", contract)


if __name__ == "__main__":
    unittest.main(verbosity=2)
