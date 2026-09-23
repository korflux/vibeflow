#!/usr/bin/env python3
"""Contratos nativos e paridade essencial da skill vibe-implement canônica."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[3] / "vibe-implement"
SCRIPT = SKILL_DIR / "scripts" / "implement.py"
POWERSHELL_SCRIPT = SKILL_DIR / "scripts" / "implement.ps1"


# Executa o motor Python e devolve processo e relatório, quando produzido.
def invoke(repo: Path, *arguments: str, check: bool = True) -> tuple[subprocess.CompletedProcess[str], dict | None]:
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo), *arguments],
        capture_output=True,
        text=True,
        check=check,
    )
    report_path = repo / ".vibeflow" / "implement-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else None
    return process, report


# Cria só a pasta .vibeflow, como se o init tivesse rodado sem phases.
def seed_vibeflow(repo: Path) -> Path:
    vf = repo / ".vibeflow"
    vf.mkdir()
    (vf / ".gitignore").write_text("init-report.json\nplan-report.json\n", encoding="utf-8")
    return vf


# Grava uma fase mínima com os arquivos pedidos.
def seed_phase(vf: Path, name: str, *files: str) -> Path:
    phase = vf / "phases" / name
    phase.mkdir(parents=True)
    for filename in files:
        (phase / filename).write_text(f"{filename}\n", encoding="utf-8")
    return phase


# Plan mínimo com as duas linhas congeladas por T* (concluída + Deps).
def plan_tasks(*tasks: tuple[str, str, str]) -> str:
    chunks = ["# Plan: fixture\n"]
    for tid, mark, deps in tasks:
        chunks.append(
            f"### {tid}: fixture {tid}\n\n"
            f"- [{mark}] {tid} concluída\n"
            f"- **Deps:** {deps}\n"
        )
    return "\n".join(chunks)


# Troca o corpo do plan.md da fase já criada.
def write_plan(phase: Path, body: str) -> None:
    (phase / "plan.md").write_text(body, encoding="utf-8")


# Grava o alvo MVP mínimo e permite variar o gate do analyze nos contratos.
def seed_mvp(vf: Path, plan: str, status: str | None = "aprovado", verdict: str = "limpo") -> Path:
    mvp = vf / "mvp"
    mvp.mkdir()
    (mvp / "plan.md").write_text(plan, encoding="utf-8")
    if status is not None:
        (mvp / "analyze.md").write_text(
            f"# Analyze: fixture\n# Status: {status}\n\n## Veredito\n\n{verdict}\n",
            encoding="utf-8",
        )
    return mvp


class PythonContracts(unittest.TestCase):
    """Verifica inventário, alvo com plan, apply direto e gitignore."""

    def setUp(self) -> None:
        self.repo = Path.cwd() / f".vibe-implement-python-{uuid.uuid4().hex}"
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
        self.assertIsNone(report["created"])
        self.assertIsNone(report["modo"])
        self.assertNotIn("wip", report)

    def test_reuse_plan_folder_does_not_create_phase_two(self) -> None:
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-a", "spec.md", "plan.md")
        _, report = invoke(self.repo)
        self.assertEqual("phase-1-a", report["alvo"]["dir"])
        self.assertEqual("reuse", report["modo_sugerido"])
        self.assertFalse((vf / "phases" / "phase-2-a").exists())
        self.assertIsNone(report["created"])

    def test_alvo_is_highest_n_with_plan(self) -> None:
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-old", "plan.md")
        seed_phase(vf, "phase-3-new", "plan.md")
        _, report = invoke(self.repo)
        self.assertEqual("phase-3-new", report["alvo"]["dir"])
        self.assertEqual(3, report["alvo"]["n"])

    def test_ignores_phase_without_plan_when_choosing_alvo(self) -> None:
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-2-so-spec", "spec.md")
        seed_phase(vf, "phase-1-com-plan", "plan.md")
        _, report = invoke(self.repo)
        self.assertEqual("phase-1-com-plan", report["alvo"]["dir"])

    def test_dir_without_plan_is_alvo(self) -> None:
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-so-spec", "spec.md")
        _, report = invoke(self.repo, "--dir", "phase-1-so-spec")
        self.assertEqual("phase-1-so-spec", report["alvo"]["dir"])
        self.assertEqual("reuse", report["modo_sugerido"])
        self.assertNotIn("plan.md", report["alvo"]["files"])

    def test_dir_missing_or_invalid(self) -> None:
        seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--dir", "phase-9-sumiu", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("FASE_AUSENTE", process.stderr)
        process, _ = invoke(self.repo, "--dir", "nao-e-fase", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("FASE_AUSENTE", process.stderr)

    def test_review_and_implement_listed_in_files(self) -> None:
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-com-review", "plan.md", "review.md", "implement.md")
        _, report = invoke(self.repo)
        self.assertIn("review.md", report["alvo"]["files"])
        self.assertIn("plan.md", report["alvo"]["files"])
        self.assertIn("implement.md", report["alvo"]["files"])
        self.assertEqual("atualizar", report["modo_sugerido"])

    def test_gitignore_preserves_siblings(self) -> None:
        vf = seed_vibeflow(self.repo)
        invoke(self.repo)
        text = (vf / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("plan-report.json", text)
        self.assertIn("implement-report.json", text)
        self.assertNotIn("implement-wip.md", text)

    def test_apply_prepares_missing_live_file(self) -> None:
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-a", "plan.md")
        _, report = invoke(self.repo, "--apply")
        dest = vf / "phases" / "phase-1-a" / "implement.md"
        self.assertEqual(b"", dest.read_bytes())
        self.assertEqual("reuse", report["modo"])
        self.assertEqual([{"op": "criar_arquivo", "alvo": ".vibeflow/phases/phase-1-a/implement.md"}], report["actions"])
        self.assertNotIn("wip", report)

    def test_apply_reuses_plan_folder(self) -> None:
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-a", "spec.md", "plan.md")
        _, report = invoke(self.repo, "--apply")
        dest = vf / "phases" / "phase-1-a" / "implement.md"
        self.assertTrue(dest.is_file())
        self.assertEqual(b"", dest.read_bytes())
        self.assertFalse((vf / "phases" / "phase-2-a").exists())
        self.assertEqual("reuse", report["modo"])
        self.assertIn("implement.md", report["alvo"]["files"])
        self.assertNotIn("wip", report)

    def test_apply_updates_existing_implement(self) -> None:
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-a", "plan.md", "implement.md")
        original = b"# fatia 1\n\x00historico\n"
        (vf / "phases" / "phase-1-a" / "implement.md").write_bytes(original)
        _, report = invoke(self.repo, "--apply")
        self.assertEqual(original, (vf / "phases" / "phase-1-a" / "implement.md").read_bytes())
        self.assertEqual("atualizar", report["modo"])
        self.assertEqual([], report["actions"])
        self.assertNotIn("wip", report)

    def test_apply_without_alvo_or_slug(self) -> None:
        vf = seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--apply", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("IMPLEMENT_SEM_ALVO", process.stderr)

    def test_slug_creates_avulsa(self) -> None:
        vf = seed_vibeflow(self.repo)
        _, report = invoke(self.repo, "--apply", "--slug", "hotfix-cor")
        dest = vf / "phases" / "phase-1-hotfix-cor" / "implement.md"
        self.assertTrue(dest.is_file())
        self.assertEqual(b"", dest.read_bytes())
        self.assertEqual("criar", report["modo"])
        self.assertEqual(2, report["next_n"])
        self.assertNotIn("wip", report)

    def test_phases_file_is_unexpected(self) -> None:
        vf = seed_vibeflow(self.repo)
        (vf / "phases").write_text("nao", encoding="utf-8")
        process, _ = invoke(self.repo, check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("PHASES_INESPERADO", process.stderr)

    def test_fila_null_without_plan(self) -> None:
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-so-spec", "spec.md")
        _, report = invoke(self.repo, "--dir", "phase-1-so-spec")
        self.assertIsNone(report["fila"])

    def test_fila_null_when_alvo_ausente(self) -> None:
        seed_vibeflow(self.repo)
        _, report = invoke(self.repo)
        self.assertIsNone(report["alvo"])
        self.assertIsNone(report["fila"])

    def test_fila_one_eligible(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = seed_phase(vf, "phase-1-a", "plan.md")
        write_plan(phase, plan_tasks(("T1", "x", "nenhuma"), ("T2", " ", "T1")))
        _, report = invoke(self.repo)
        fila = report["fila"]
        self.assertEqual("ok", fila["parse"])
        self.assertEqual(["T1"], fila["concluidas"])
        self.assertEqual(["T2"], fila["abertas"])
        self.assertEqual(["T2"], fila["elegiveis"])
        self.assertEqual([], fila["bloqueadas"])
        self.assertEqual([], fila["avisos"])

    def test_fila_two_eligible(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = seed_phase(vf, "phase-1-a", "plan.md")
        write_plan(phase, plan_tasks(("T1", " ", "nenhuma"), ("T4", " ", "nenhuma")))
        _, report = invoke(self.repo)
        fila = report["fila"]
        self.assertEqual("ok", fila["parse"])
        self.assertEqual(["T1", "T4"], fila["abertas"])
        self.assertEqual(["T1", "T4"], fila["elegiveis"])
        self.assertEqual([], fila["concluidas"])
        self.assertEqual([], fila["bloqueadas"])

    # Garante que texto de organização fora de T* não altera a fila mecânica.
    def test_fila_ignores_texto_fora_do_contrato(self) -> None:
        """Prova que preparo, paralelização e checkpoints não deslocam a fila compacta."""
        vf = seed_vibeflow(self.repo)
        phase = seed_phase(vf, "phase-1-a", "plan.md")
        write_plan(
            phase,
            "# Plan\n\n## Preparo (checklist curta, não é task)\n\n- [ ] comandos disponíveis\n\n"
            "## Tasks\n\n### T1: entrega inicial\n\n- [ ] T1 concluída\n"
            "- **Spec:** A1\n- **O quê:** resultado inicial\n- **Aceite:** observável\n"
            "- **Verificação:** `python -m unittest`\n- **Deps:** nenhuma\n\n"
            "## Paralelização (opcional)\n\n- texto sem efeito na fila\n\n"
            "## Checkpoint de review (opcional)\n\n- revisar contrato compartilhado\n\n"
            "### T2: entrega dependente\n\n- [ ] T2 concluída\n- **Deps:** T1\n",
        )
        _, report = invoke(self.repo)
        fila = report["fila"]
        self.assertEqual(["T1"], fila["elegiveis"])
        self.assertEqual([{"id": "T2", "deps": ["T1"]}], fila["bloqueadas"])

    def test_fila_dep_blocks(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = seed_phase(vf, "phase-1-a", "plan.md")
        write_plan(phase, plan_tasks(("T1", " ", "nenhuma"), ("T2", " ", "T1")))
        _, report = invoke(self.repo)
        fila = report["fila"]
        self.assertEqual("ok", fila["parse"])
        self.assertEqual(["T1"], fila["elegiveis"])
        self.assertEqual([{"id": "T2", "deps": ["T1"]}], fila["bloqueadas"])
        self.assertEqual(["T1", "T2"], fila["abertas"])

    def test_fila_missing_concluida_is_parcial(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = seed_phase(vf, "phase-1-a", "plan.md")
        write_plan(
            phase,
            "### T1: sem checkbox\n\n- **Deps:** nenhuma\n\n### T2: ok\n\n- [ ] T2 concluída\n- **Deps:** nenhuma\n",
        )
        _, report = invoke(self.repo)
        fila = report["fila"]
        self.assertEqual("parcial", fila["parse"])
        self.assertEqual(["T2"], fila["elegiveis"])
        self.assertNotIn("T1", fila["abertas"])
        self.assertNotIn("T1", fila["elegiveis"])
        self.assertTrue(any("T1" in aviso for aviso in fila["avisos"]))

    def test_fila_ausente_without_task_headings(self) -> None:
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-a", "plan.md")
        _, report = invoke(self.repo)
        fila = report["fila"]
        self.assertEqual("ausente", fila["parse"])
        self.assertEqual([], fila["elegiveis"])
        self.assertEqual([], fila["avisos"])

    def test_mvp_fila_uses_only_special_plan(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = seed_phase(vf, "phase-9-outra", "plan.md")
        write_plan(phase, plan_tasks(("T1", " ", "nenhuma")))
        seed_mvp(vf, plan_tasks(("T7", " ", "nenhuma")))
        _, report = invoke(self.repo, "--mvp")
        self.assertEqual("mvp", report["rota"])
        self.assertEqual(["T7"], report["fila"]["elegiveis"])
        self.assertTrue(report["analyze_gate"]["pronto"])

    def test_mvp_apply_refuses_missing_draft_and_blocked_analyze(self) -> None:
        for status, verdict, expected in (
            (None, "limpo", "IMPLEMENT_ANALYZE_AUSENTE"),
            ("rascunho", "limpo", "IMPLEMENT_ANALYZE_RASCUNHO"),
            ("aprovado", "bloqueado", "IMPLEMENT_ANALYZE_BLOQUEADO"),
        ):
            with self.subTest(expected=expected):
                repo = self.repo / expected
                repo.mkdir()
                vf = seed_vibeflow(repo)
                seed_mvp(vf, plan_tasks(("T1", " ", "nenhuma")), status, verdict)
                process, _ = invoke(repo, "--apply", "--mvp", check=False)
                self.assertNotEqual(0, process.returncode)
                self.assertIn(expected, process.stderr)
                self.assertFalse((vf / "mvp" / "implement.md").exists())

    def test_mvp_apply_preserves_existing_live_file(self) -> None:
        vf = seed_vibeflow(self.repo)
        mvp = seed_mvp(vf, plan_tasks(("T1", " ", "nenhuma")))
        _, report = invoke(self.repo, "--apply", "--mvp")
        self.assertEqual(b"", (mvp / "implement.md").read_bytes())
        self.assertEqual("mvp", report["created"]["kind"])
        original = b"# Fatia T1\n\x00\n## Fatia T2\n"
        (mvp / "implement.md").write_bytes(original)
        _, second_report = invoke(self.repo, "--apply", "--mvp")
        self.assertEqual(original, (mvp / "implement.md").read_bytes())
        self.assertEqual([], second_report["actions"])
        self.assertNotIn("wip", second_report)
        self.assertEqual([], [item.name for item in (vf / "phases").iterdir() if item.is_dir()])

    def test_mvp_rejects_phase_selectors(self) -> None:
        seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--mvp", "--slug", "produto", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("MODO_INVALIDO", process.stderr)

    def test_independent_task_completions_preserve_queue_order_and_result(self) -> None:
        """Compara a fila serial com retornos delegados fora de ordem para tasks independentes."""
        results = {}
        for execution, completion_order in (
            ("sequential", ("T1", "T2")),
            ("delegated", ("T2", "T1")),
        ):
            repo = self.repo / execution
            repo.mkdir()
            vf = seed_vibeflow(repo)
            phase = seed_phase(vf, "phase-1-fixture", "plan.md")
            plan = plan_tasks(("T1", " ", "nenhuma"), ("T2", " ", "nenhuma"), ("T3", " ", "T1, T2"))
            write_plan(phase, plan)

            _, report = invoke(repo)
            self.assertEqual(["T1", "T2"], report["fila"]["elegiveis"])
            self.assertEqual([{"id": "T3", "deps": ["T1", "T2"]}], report["fila"]["bloqueadas"])

            for index, task in enumerate(completion_order):
                plan = plan.replace(f"- [ ] {task} concluída", f"- [x] {task} concluída", 1)
                write_plan(phase, plan)
                _, report = invoke(repo)
                if index == 0:
                    remaining = completion_order[1]
                    self.assertEqual([remaining], report["fila"]["elegiveis"])
                    self.assertEqual([{"id": "T3", "deps": [remaining]}], report["fila"]["bloqueadas"])
                else:
                    self.assertEqual(["T3"], report["fila"]["elegiveis"])
                    self.assertEqual([], report["fila"]["bloqueadas"])

            plan = plan.replace("- [ ] T3 concluída", "- [x] T3 concluída", 1)
            write_plan(phase, plan)
            _, report = invoke(repo)
            results[execution] = {
                key: report["fila"][key]
                for key in ("concluidas", "abertas", "elegiveis", "bloqueadas")
            }

        self.assertEqual(results["sequential"], results["delegated"])


class SkillContracts(unittest.TestCase):
    """Trava no disco os contratos que a skill precisa para ler fila e executar o ciclo de implementação."""

    def test_skill_reads_fila_from_report(self) -> None:
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("fila.elegiveis", text)
        self.assertIn("2+ elegíveis", text)


    def test_skill_requires_execution_cycle_and_green_test(self) -> None:
        """Garante que a prova final sucede a simplificação e continua obrigatória."""
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        dod = (SKILL_DIR / "references" / "definition-of-done.md").read_text(encoding="utf-8")
        self.assertIn("Sem teste verde executável", skill)
        self.assertIn("Reconhecer", skill)
        self.assertIn("Codar", skill)
        self.assertLess(skill.index("Simplificar antes da prova"), skill.index("Executar a prova final"))
        self.assertIn("uma vez no estado integrado e simplificado", skill)
        self.assertIn("Não rebaixe", dod)

    def test_skill_bounds_delegation_and_coordinator_ownership(self) -> None:
        """Trava entrega delimitada e exclusividade do coordenador sobre estado compartilhado."""
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        template = (SKILL_DIR / "templates" / "implement.md").read_text(encoding="utf-8")
        self.assertIn("Use delegação nativa somente se o host a oferecer", skill)
        self.assertIn("resultado, aceite, dependências, paths exclusivos e comando de verificação", skill)
        self.assertIn("Agentes não alteram `plan.md`, `spec.md`, `implement.md` ou `review.md`", skill)
        self.assertIn("somente o coordenador altera artefatos vivos e o índice Git", skill)
        self.assertIn("worktree/branch isolada ou ownership sem sobreposição", skill)
        self.assertIn("paths integrados e provados pela task", skill)
        self.assertIn("Escopo delegado", template)
        self.assertIn("Retorno integrado", template)
        self.assertIn("a prova final é a do estado integrado", template)

    def test_skill_repeats_proof_only_after_failure_or_code_test_edit(self) -> None:
        """Garante uma prova final por estado e reexecução somente quando ela perde validade."""
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Se a prova falhar", skill)
        self.assertIn("Se código ou teste da task for editado depois da prova verde", skill)
        self.assertIn("Atualizar artefatos vivos e preparar o commit não invalida a prova", skill)

    # Garante que cada task termina em commit isolado e que o push fica para a review.
    def test_skill_requires_task_commit_without_push(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("git diff --cached --check", skill)
        self.assertIn("git add -- path/da/task outro/path", skill)
        self.assertIn("task(Tn)", skill)
        self.assertIn("Não faça `git push` nesta etapa", skill)
        self.assertIn("git add -A", skill)
        self.assertNotIn("checkpoint", skill.lower())



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
        self.repo = Path.cwd() / f".vibe-implement-ps-{uuid.uuid4().hex}"
        self.repo.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.repo, ignore_errors=True)

    def test_apply_reuse_same_path(self) -> None:
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-lock-bloco", "spec.md", "plan.md")
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        dest = vf / "phases" / "phase-1-lock-bloco" / "implement.md"
        self.assertTrue(dest.is_file())
        self.assertEqual(b"", dest.read_bytes())
        self.assertTrue((vf / "phases" / "phase-1-lock-bloco" / "plan.md").is_file())
        report = json.loads((vf / "implement-report.json").read_text(encoding="utf-8"))
        self.assertNotIn("wip", report)

    # Confirma que o motor PowerShell preserva o conteúdo do implement já existente.
    def test_apply_preserves_existing_file(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = seed_phase(vf, "phase-1-lock-bloco", "spec.md", "plan.md", "implement.md")
        original = b"# implement\n\x00historico\n"
        (phase / "implement.md").write_bytes(original)
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual(original, (phase / "implement.md").read_bytes())
        report = json.loads((vf / "implement-report.json").read_text(encoding="utf-8"))
        self.assertEqual([], report["actions"])
        self.assertNotIn("wip", report)

    def test_fila_parity_dep_blocks(self) -> None:
        vf = seed_vibeflow(self.repo)
        phase = seed_phase(vf, "phase-1-a", "plan.md")
        write_plan(phase, plan_tasks(("T1", " ", "nenhuma"), ("T2", " ", "T1")))
        _, py_report = invoke(self.repo)
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        ps_report = json.loads((vf / "implement-report.json").read_text(encoding="utf-8"))
        self.assertEqual(py_report["fila"]["elegiveis"], ps_report["fila"]["elegiveis"])
        self.assertEqual(py_report["fila"]["bloqueadas"], ps_report["fila"]["bloqueadas"])
        self.assertEqual(["T1"], ps_report["fila"]["elegiveis"])
        self.assertEqual([{"id": "T2", "deps": ["T1"]}], ps_report["fila"]["bloqueadas"])

    def test_mvp_apply_same_path_and_gate(self) -> None:
        vf = seed_vibeflow(self.repo)
        mvp = seed_mvp(vf, plan_tasks(("T1", " ", "nenhuma")))
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply", "-Mvp"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual(b"", (mvp / "implement.md").read_bytes())
        report = json.loads((vf / "implement-report.json").read_text(encoding="utf-8"))
        self.assertTrue(report["analyze_gate"]["pronto"])
        self.assertEqual(["T1"], report["fila"]["elegiveis"])
        self.assertNotIn("wip", report)


if __name__ == "__main__":
    unittest.main()
