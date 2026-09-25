#!/usr/bin/env python3
"""Prova integrada da cadeia max no alvo único .vibeflow/mvp/."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILLS = ("interview", "spec", "plan", "analyze", "implement", "review")


# Executa o motor canônico e decodifica seu inventário transitório do stdout.
def invoke(repo: Path, skill: str, *arguments: str) -> dict:
    script = ROOT / f"vibe-{skill}" / "scripts" / f"{skill}.py"
    process = subprocess.run(
        [sys.executable, str(script), "--root", str(repo), *arguments],
        capture_output=True,
        text=True,
        check=False,
    )
    if process.returncode != 0:
        raise AssertionError(f"{skill} falhou: {process.stderr}")
    return json.loads(process.stdout)


# Escreve o conteúdo semântico depois que o motor prepara o arquivo vivo vazio.
def write_live(vf: Path, skill: str, body: str) -> None:
    (vf / "mvp" / f"{skill}.md").write_text(body, encoding="utf-8", newline="\n")


class MvpFlow(unittest.TestCase):
    """Valida path, ordem, relatórios e isolamento das phases ponta a ponta."""

    def setUp(self) -> None:
        self.repo = Path.cwd() / f".vibe-mvp-flow-{uuid.uuid4().hex}"
        self.repo.mkdir()
        self.vf = self.repo / ".vibeflow"
        self.vf.mkdir()
        (self.vf / ".gitignore").write_text("init-report.json\n", encoding="utf-8")
        self.rules = b"# Regras\n\nconteudo que os motores nao podem alterar \x00\n"
        (self.repo / "AGENTS.md").write_bytes(self.rules)

    def tearDown(self) -> None:
        shutil.rmtree(self.repo, ignore_errors=True)

    # Prova que uma review checkpoint com T* aberta no plan continua sem Approve de fase.
    def test_full_max_chain_uses_only_mvp_target(self) -> None:
        artifacts = {
            "interview": "# MVP\n\n## Decisões críticas\n\n| ID | Estado | Decisão | Motivo |\n|---|---|---|---|\n| AUTH-01 | DECIDIDO | sessão segura | acesso |\n",
            "spec": "# Spec: MVP\n# Status: aprovado\n\n## Decisões críticas\n\n| ID | Ação | Decisão | Motivo | Fonte |\n|---|---|---|---|---|\n| AUTH-01 | mantém | sessão segura | acesso | interview |\n",
            "plan": "# Plan: MVP\n# Status: aprovado\n\n### T1: implementar acesso\n\n- [x] T1 concluída\n- **Decisões:** AUTH-01 (mantém)\n- **Deps:** nenhuma\n\n### T2: integrar sessão\n\n- [ ] T2 concluída\n- **Deps:** T1\n",
            "analyze": "# Analyze: MVP\n# Status: aprovado\n\n## Veredito\n\nlimpo\n",
            "implement": "# Implement: MVP\n# Status: em-curso\n\n## Fatia T1\n\n- Feito: acesso\n- Prova: teste ok\n",
            "review": "# Review: MVP\n# Status: rascunho\n\n## Tipo de review\n- Tipo: checkpoint\n- Marco: T1, implementar acesso\n- T* abertas fora do marco: T2\n\n## Veredito vigente\n\n- [ ] **Approve**\n\n## Etapas\n\n### Etapa 1 - checkpoint - T1\n- Veredito desta etapa: Marco aprovado\n",
        }

        for skill in SKILLS:
            report = invoke(self.repo, skill, "--apply", "--mvp")
            if skill == "implement":
                self.assertEqual("mvp", report["alvo"]["kind"])
                self.assertFalse((self.vf / "mvp" / "implement.md").exists())
                continue
            self.assertEqual("mvp", report["rota"], skill)
            self.assertEqual("mvp", report["created"]["kind"], skill)
            self.assertEqual(".vibeflow/mvp", report["created"]["path"], skill)
            self.assertEqual(b"", (self.vf / "mvp" / f"{skill}.md").read_bytes(), skill)
            self.assertNotIn("wip", report, skill)
            write_live(self.vf, skill, artifacts[skill])

        self.assertEqual(set(SKILLS) - {"implement"}, {path.stem for path in (self.vf / "mvp").glob("*.md")})
        phase_dirs = [path for path in (self.vf / "phases").iterdir() if path.is_dir()]
        self.assertEqual([], phase_dirs)
        self.assertEqual(self.rules, (self.repo / "AGENTS.md").read_bytes())
        self.assertEqual([], list(self.vf.glob("*-wip.md")))
        review = (self.vf / "mvp" / "review.md").read_text(encoding="utf-8")
        self.assertIn("Tipo: checkpoint", review)
        self.assertIn("T* abertas fora do marco: T2", review)
        self.assertIn("# Status: rascunho", review)
        self.assertNotIn("- [x] **Approve**", review)
        self.assertNotIn("## Finalização Git da phase", review)

    def test_decision_sync_contract_is_after_human_approval_and_ai_only(self) -> None:
        skill = (ROOT / "vibe-review" / "SKILL.md").read_text(encoding="utf-8")
        after = skill.index("Após aprovação humana explícita")
        patch = skill.index("patch mínimo", after)
        never = skill.index("nunca autoriza sync", after)
        self.assertLess(after, patch)
        self.assertLess(patch, never)
        for name in ("review.py", "review.ps1", "review.sh"):
            motor = (ROOT / "vibe-review" / "scripts" / name).read_text(encoding="utf-8-sig").lower()
            self.assertNotIn("regras.md", motor)
            self.assertNotIn("--sync", motor)


if __name__ == "__main__":
    unittest.main()
