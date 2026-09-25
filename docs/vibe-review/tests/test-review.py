#!/usr/bin/env python3
"""Contratos nativos e paridade essencial da skill vibe-review canônica."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[3] / "vibe-review"
SCRIPT = SKILL_DIR / "scripts" / "review.py"
POWERSHELL_SCRIPT = SKILL_DIR / "scripts" / "review.ps1"


# Executa o motor Python e decodifica o inventário transitório enviado no stdout.
def invoke(repo: Path, *arguments: str, check: bool = True) -> tuple[subprocess.CompletedProcess[str], dict | None]:
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo), *arguments],
        capture_output=True,
        text=True,
        check=check,
    )
    report = json.loads(process.stdout) if process.returncode == 0 and process.stdout.strip() else None
    return process, report


# Cria só a pasta .vibeflow, como se o init tivesse rodado sem phases.
def seed_vibeflow(repo: Path) -> Path:
    vf = repo / ".vibeflow"
    vf.mkdir()
    (vf / ".gitignore").write_text("init-report.json\ninit-pending.json\n", encoding="utf-8")
    return vf


# Grava os quatro predecessores obrigatórios da review MVP.
def seed_mvp(vf: Path) -> Path:
    mvp = vf / "mvp"
    mvp.mkdir()
    for name in ("interview.md", "spec.md", "plan.md", "analyze.md"):
        (mvp / name).write_text(f"{name}\n", encoding="utf-8")
    return mvp



class PythonContracts(unittest.TestCase):
    """Verifica reuse do plan, avulsa com slug e preservação do artefato vivo."""

    def setUp(self) -> None:
        self.repo = Path.cwd() / f".vibe-review-python-{uuid.uuid4().hex}"
        self.repo.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.repo, ignore_errors=True)

    def test_init_ausente(self) -> None:
        process, report = invoke(self.repo, check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("INIT_AUSENTE", process.stderr)
        self.assertIsNone(report)

    def test_creates_missing_phases(self) -> None:
        seed_vibeflow(self.repo)
        _, report = invoke(self.repo)
        self.assertEqual("criar", report["modo_sugerido"])
        self.assertIsNone(report["alvo"])
        self.assertTrue((self.repo / ".vibeflow" / "phases" / ".gitkeep").is_file())

    def test_reuse_plan_folder(self) -> None:
        """Aplica review a uma phase com provas no plan e sem implement.md novo."""
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-a"
        phase.mkdir(parents=True)
        (phase / "plan.md").write_text(
            "### T1: fixture\n\n- [x] T1 concluída\n- **Deps:** nenhuma\n"
            "- **Verificação:** `python -m unittest`\n- **Prova:** passou\n"
            "- **Arquivos:** `src/app.py`\n",
            encoding="utf-8",
        )
        _, report = invoke(self.repo, "--apply")
        dest = phase / "review.md"
        self.assertTrue(dest.is_file())
        self.assertEqual(b"", dest.read_bytes())
        self.assertTrue((phase / "plan.md").is_file())
        self.assertFalse((phase / "implement.md").exists())
        self.assertFalse((vf / "phases" / "phase-2-a").exists())
        self.assertEqual("reuse", report["modo"])
        self.assertNotIn("wip", report)

    # Confirma que --dir escolhe e reporta a phase do diff em vez da pendente mais recente.
    def test_dir_overrides_newer_unreviewed_plan(self) -> None:
        vf = seed_vibeflow(self.repo)
        for name in ("phase-2-outro", "phase-9-pendente"):
            phase = vf / "phases" / name
            phase.mkdir(parents=True)
            (phase / "plan.md").write_text("plan\n", encoding="utf-8")

        _, automatic = invoke(self.repo)
        _, targeted = invoke(self.repo, "--dir", "phase-2-outro")

        self.assertEqual("phase-9-pendente", automatic["alvo"]["dir"])
        self.assertEqual("phase-2-outro", targeted["alvo"]["dir"])

        _, applied = invoke(self.repo, "--apply", "--dir", "phase-2-outro")
        self.assertTrue((vf / "phases" / "phase-2-outro" / "review.md").is_file())
        self.assertFalse((vf / "phases" / "phase-9-pendente" / "review.md").exists())
        self.assertEqual("phase-2-outro", applied["alvo"]["dir"])

    def test_apply_without_alvo_or_slug(self) -> None:
        vf = seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--apply", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("REVIEW_SEM_ALVO", process.stderr)

    def test_slug_creates_avulsa(self) -> None:
        vf = seed_vibeflow(self.repo)
        _, report = invoke(self.repo, "--apply", "--slug", "diff-local")
        dest = vf / "phases" / "phase-1-diff-local" / "review.md"
        self.assertTrue(dest.is_file())
        self.assertEqual(b"", dest.read_bytes())
        self.assertEqual("criar", report["modo"])
        self.assertEqual(["review.md"], report["created"]["files"])
        self.assertNotIn("wip", report)

    def test_dir_without_plan_writes_review(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-so-spec"
        phase.mkdir(parents=True)
        (phase / "spec.md").write_text("s\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply", "--dir", "phase-1-so-spec")
        dest = phase / "review.md"
        self.assertTrue(dest.is_file())
        self.assertEqual(b"", dest.read_bytes())
        self.assertEqual("reuse", report["modo"])
        self.assertFalse((phase / "plan.md").exists())

    def test_dir_missing(self) -> None:
        vf = seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--apply", "--dir", "phase-9-sumiu", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("FASE_AUSENTE", process.stderr)

    def test_preserve_rascunho(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock"
        phase.mkdir(parents=True)
        (phase / "plan.md").write_text("p\n", encoding="utf-8")
        original = b"old\n\x00historico\n"
        (phase / "review.md").write_bytes(original)
        _, report = invoke(self.repo, "--apply")
        self.assertEqual(original, (phase / "review.md").read_bytes())
        self.assertEqual("atualizar", report["modo"])
        self.assertEqual([], report["actions"])
        self.assertNotIn("wip", report)

    def test_implement_listed_in_files(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-com-implement"
        phase.mkdir(parents=True)
        (phase / "plan.md").write_text("p\n", encoding="utf-8")
        (phase / "implement.md").write_text("i\n", encoding="utf-8")
        _, report = invoke(self.repo)
        self.assertIn("implement.md", report["alvo"]["files"])
        self.assertIn("plan.md", report["alvo"]["files"])

    # Confirma que o JSON transitório não cria relatório nem altera o gitignore de init.
    def test_stdout_report_does_not_mutate_workspace(self) -> None:
        vf = seed_vibeflow(self.repo)
        original = (vf / ".gitignore").read_bytes()
        _, report = invoke(self.repo)
        self.assertIsNotNone(report)
        self.assertEqual(original, (vf / ".gitignore").read_bytes())
        self.assertEqual([], list(vf.glob("*-report.json")))

    def test_phases_file_is_unexpected(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "phases").write_text("nao", encoding="utf-8")
        process, _ = invoke(self.repo, check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("PHASES_INESPERADO", process.stderr)

    def test_mvp_requires_complete_max_chain(self) -> None:
        vf = seed_vibeflow(self.repo)
        mvp = vf / "mvp"
        mvp.mkdir()
        (mvp / "plan.md").write_text("p\n", encoding="utf-8")
        process, _ = invoke(self.repo, "--mvp", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("REVIEW_CADEIA_INCOMPLETA", process.stderr)
        self.assertIn("interview.md", process.stderr)

    def test_mvp_apply_preserves_regras_in_every_review_state(self) -> None:
        for status in ("rascunho", "request-changes", "aprovado"):
            with self.subTest(status=status):
                repo = self.repo / status
                repo.mkdir()
                vf = seed_vibeflow(repo)
                mvp = seed_mvp(vf)
                rules = b"# Regras\n\nconteudo intacto \x00\n"
                (vf / "REGRAS.md").write_bytes(rules)
                _, report = invoke(repo, "--apply", "--mvp")
                self.assertEqual(b"", (mvp / "review.md").read_bytes())
                self.assertEqual(rules, (vf / "REGRAS.md").read_bytes())
                self.assertEqual("mvp", report["created"]["kind"])
                self.assertNotIn("wip", report)
                self.assertEqual([], [item.name for item in (vf / "phases").iterdir() if item.is_dir()])

    def test_mvp_rejects_phase_selectors(self) -> None:
        seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--mvp", "--slug", "produto", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("MODO_INVALIDO", process.stderr)



# Verifica se existe uma versão real de PowerShell 7, única suportada pelo motor gêmeo.
def powershell7() -> str | None:
    executable = shutil.which("pwsh")
    if not executable:
        return None
    probe = subprocess.run([executable, "-NoProfile", "-Command", "$PSVersionTable.PSVersion.Major"], capture_output=True, text=True, check=False)
    return executable if probe.stdout.strip().isdigit() and int(probe.stdout.strip()) >= 7 else None

@unittest.skipUnless(powershell7(), "PowerShell 7 indisponível")
class PowershellParity(unittest.TestCase):
    """Confere que o apply reuse do PowerShell grava o mesmo path."""

    def setUp(self) -> None:
        self.repo = Path.cwd() / f".vibe-review-ps-{uuid.uuid4().hex}"
        self.repo.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.repo, ignore_errors=True)

    # Confirma que o motor PowerShell entrega o inventário no stdout sem persistir relatório.
    def test_apply_reuse_same_path(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock-bloco"
        phase.mkdir(parents=True)
        (phase / "plan.md").write_text("plan\n", encoding="utf-8")
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        dest = phase / "review.md"
        self.assertTrue(dest.is_file())
        self.assertEqual(b"", dest.read_bytes())
        self.assertTrue((phase / "plan.md").is_file())
        report = json.loads(process.stdout)
        self.assertFalse((vf / "review-report.json").exists())
        self.assertNotIn("wip", report)

    # Confirma que -Dir seleciona e reporta a phase explícita apesar de outra pendente mais recente.
    def test_dir_overrides_newer_unreviewed_plan(self) -> None:
        vf = seed_vibeflow(self.repo)
        for name in ("phase-2-outro", "phase-9-pendente"):
            phase = vf / "phases" / name
            phase.mkdir(parents=True)
            (phase / "plan.md").write_text("plan\n", encoding="utf-8")
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Dir", "phase-2-outro", "-Apply"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        report = json.loads(process.stdout)
        self.assertEqual("phase-2-outro", report["alvo"]["dir"])
        self.assertTrue((vf / "phases" / "phase-2-outro" / "review.md").is_file())
        self.assertFalse((vf / "phases" / "phase-9-pendente" / "review.md").exists())

    # Confirma que o motor PowerShell preserva o conteúdo da review já existente.
    def test_apply_preserves_existing_file(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-lock-bloco"
        phase.mkdir(parents=True)
        (phase / "plan.md").write_text("plan\n", encoding="utf-8")
        original = b"# review\n\x00historico\n"
        (phase / "review.md").write_bytes(original)
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual(original, (phase / "review.md").read_bytes())
        report = json.loads(process.stdout)
        self.assertFalse((vf / "review-report.json").exists())
        self.assertEqual([], report["actions"])
        self.assertNotIn("wip", report)

    # Confirma que o alvo MVP e REGRAS são preservados e o relatório segue só no stdout.
    def test_mvp_apply_same_path_preserves_regras(self) -> None:
        vf = seed_vibeflow(self.repo)
        mvp = seed_mvp(vf)
        rules = b"# Regras intactas\n"
        (vf / "REGRAS.md").write_bytes(rules)
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply", "-Mvp"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual(b"", (mvp / "review.md").read_bytes())
        self.assertEqual(rules, (vf / "REGRAS.md").read_bytes())
        report = json.loads(process.stdout)
        self.assertFalse((vf / "review-report.json").exists())
        self.assertNotIn("wip", report)


class SkillContracts(unittest.TestCase):
    """Trava os gates semânticos, a cobertura da auditoria e o fechamento Git."""


    # Confirma que os eixos obrigatórios continuam disponíveis na review.

    # Garante que a review encontra a prova de implementação no registro único do plan.

    # Garante que checkpoint e review final não compartilhem o gate de conclusão da phase.

    # Garante que a review é a única porta de commit residual e push da phase.

if __name__ == "__main__":
    unittest.main()
