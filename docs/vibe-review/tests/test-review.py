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
        vf = seed_vibeflow(self.repo)
        phase = vf / "phases" / "phase-1-a"
        phase.mkdir(parents=True)
        (phase / "plan.md").write_text("plan\n", encoding="utf-8")
        _, report = invoke(self.repo, "--apply")
        dest = phase / "review.md"
        self.assertTrue(dest.is_file())
        self.assertEqual(b"", dest.read_bytes())
        self.assertTrue((phase / "plan.md").is_file())
        self.assertFalse((vf / "phases" / "phase-2-a").exists())
        self.assertEqual("reuse", report["modo"])
        self.assertNotIn("wip", report)

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

    def test_sync_requires_human_approval_and_has_no_motor_flag(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Após aprovação humana explícita", skill)
        self.assertIn("patch mínimo", skill)
        self.assertIn("nunca autoriza sync", skill)
        for script in (SCRIPT, POWERSHELL_SCRIPT, SKILL_DIR / "scripts" / "review.sh"):
            self.assertNotIn("--sync", script.read_text(encoding="utf-8-sig").lower())

    # Confirma que os eixos obrigatórios continuam disponíveis na review.
    def test_review_requires_five_audit_pillars(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Rastreabilidade e Verificação Anti-Alucinação", skill)
        self.assertIn("Provas e Integridade dos Testes", skill)
        self.assertIn("Auditoria Implacável de Segurança e Hardening", skill)
        self.assertIn("Inspeção Visual e Interface", skill)
        self.assertIn("Simplificação e Qualidade de Código", skill)
        self.assertIn("chrome-devtools", skill)

    # Garante que checkpoint e review final não compartilhem o gate de conclusão da phase.
    def test_checkpoint_and_final_review_have_separate_gates(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        template = (SKILL_DIR / "templates" / "review.md").read_text(encoding="utf-8")
        architecture = (Path.cwd() / "docs" / "vibe-review" / "ARQUITETURA.md").read_text(encoding="utf-8")
        self.assertIn("todas as T* do marco estão concluídas", skill)
        self.assertIn("Nunca declare a feature concluída", skill)
        self.assertIn("sincronize decisões, crie commit residual ou publique a phase", skill)
        self.assertIn("Não rode automaticamente a matriz de comandos de cada T*", skill)
        self.assertIn("Provas reaproveitadas", template)
        self.assertIn("Checkpoint registra o resultado do marco", template)
        self.assertIn("Review final exige a fila do plan concluída", architecture)

    # Garante que a review é a única porta de commit residual e push da phase.
    def test_review_owns_final_phase_commit_and_push(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        template = (SKILL_DIR / "templates" / "review.md").read_text(encoding="utf-8")
        for text in (skill, template):
            self.assertIn("Finalização Git da phase", text)
            self.assertIn("git push", text)
            self.assertIn("sem `--force`", text)
            self.assertIn("Approve", text)
        self.assertIn("Checkpoint nunca abre finalização Git", skill)
        self.assertIn("Omitir em checkpoint", template)
        self.assertIn("Critical ou Required", skill)
        self.assertIn("Não faça `git push`", (Path.cwd() / "vibe-implement" / "SKILL.md").read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
