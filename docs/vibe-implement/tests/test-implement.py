#!/usr/bin/env python3
"""Contratos nativos e paridade essencial da skill vibe-implement canônica."""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[3] / "vibe-implement"
SCRIPT = SKILL_DIR / "scripts" / "implement.py"
POWERSHELL_SCRIPT = SKILL_DIR / "scripts" / "implement.ps1"


# Limpa a fixture e torna graváveis objetos Git que o Windows cria como read-only.
def remove_fixture_tree(path: Path) -> None:
    # A falha volta ao teste se o problema não for apenas o atributo read-only.
    def retry_writable(operation, filename, error) -> None:
        os.chmod(filename, stat.S_IWRITE)
        operation(filename)

    shutil.rmtree(path, onerror=retry_writable)


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
        remove_fixture_tree(self.repo)

    # Executa Git no repositório temporário sem shell, preservando erros como evidência do teste.
    def _git(self, repo: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
        # O repositório Git da fixture fica fora do worktree para permitir limpeza estrita no sandbox.
        git_dir = repo.parent / f"{repo.name}-git"
        git_env = os.environ | {"GIT_DIR": str(git_dir), "GIT_WORK_TREE": str(repo)}
        return subprocess.run(
            ["git", *arguments],
            cwd=repo,
            env=git_env,
            capture_output=True,
            text=True,
            check=True,
        )

    def test_init_ausente(self) -> None:
        process, report = invoke(self.repo, check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("INIT_AUSENTE", process.stderr)
        self.assertIsNone(report)

    def test_creates_missing_phases(self) -> None:
        """Mantém o stdout focado no alvo e cria apenas a estrutura phases ausente."""
        seed_vibeflow(self.repo)
        _, report = invoke(self.repo)
        self.assertEqual({"alvo", "fila", "avisos"}, set(report))
        self.assertIsNone(report["alvo"])
        self.assertIsNone(report["fila"])
        self.assertTrue((self.repo / ".vibeflow" / "phases" / ".gitkeep").is_file())
        self.assertNotIn("wip", report)

    def test_reuse_plan_folder_does_not_create_phase_two(self) -> None:
        """Seleciona o plan existente sem expor ou criar um segundo artefato."""
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-a", "spec.md", "plan.md")
        _, report = invoke(self.repo)
        self.assertEqual("phase-1-a", report["alvo"]["dir"])
        self.assertFalse((vf / "phases" / "phase-2-a").exists())

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
        """Aceita override explícito mesmo quando a phase ainda não tem plan."""
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-so-spec", "spec.md")
        _, report = invoke(self.repo, "--dir", "phase-1-so-spec")
        self.assertEqual("phase-1-so-spec", report["alvo"]["dir"])
        self.assertIsNone(report["fila"])

    def test_dir_missing_or_invalid(self) -> None:
        seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--dir", "phase-9-sumiu", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("FASE_AUSENTE", process.stderr)
        process, _ = invoke(self.repo, "--dir", "nao-e-fase", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("FASE_AUSENTE", process.stderr)

    def test_historical_implement_does_not_select_a_target(self) -> None:
        """Arquivo histórico isolado não substitui o plan como fonte do alvo."""
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-9-historico", "implement.md")
        _, report = invoke(self.repo)
        self.assertIsNone(report["alvo"])
        self.assertIsNone(report["fila"])

    def test_stdout_omits_full_phase_inventory(self) -> None:
        """Emite apenas alvo, fila e avisos, mesmo com muitas phases no repositório."""
        vf = seed_vibeflow(self.repo)
        for number in range(1, 21):
            seed_phase(vf, f"phase-{number}-historico", "plan.md")
        process, report = invoke(self.repo)
        self.assertEqual({"alvo", "fila", "avisos"}, set(report))
        self.assertEqual("phase-20-historico", report["alvo"]["dir"])
        self.assertNotIn("phase-1-historico", process.stdout)

    # Confirma que o JSON transitório não cria relatório nem altera o gitignore de init.
    def test_stdout_report_does_not_mutate_workspace(self) -> None:
        vf = seed_vibeflow(self.repo)
        original = (vf / ".gitignore").read_bytes()
        _, report = invoke(self.repo)
        self.assertIsNotNone(report)
        self.assertEqual(original, (vf / ".gitignore").read_bytes())
        self.assertEqual([], list(vf.glob("*-report.json")))

    def test_apply_does_not_create_implement_file(self) -> None:
        """Apply reaproveita o plan sem criar implement.md para novas execuções."""
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-a", "plan.md")
        _, report = invoke(self.repo, "--apply")
        dest = vf / "phases" / "phase-1-a" / "implement.md"
        self.assertFalse(dest.exists())
        self.assertEqual("phase-1-a", report["alvo"]["dir"])
        self.assertNotIn("wip", report)

    def test_apply_reuses_plan_folder(self) -> None:
        """Apply mantém o alvo na phase existente e deixa o plan como único registro."""
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-a", "spec.md", "plan.md")
        _, report = invoke(self.repo, "--apply")
        dest = vf / "phases" / "phase-1-a" / "implement.md"
        self.assertFalse(dest.exists())
        self.assertFalse((vf / "phases" / "phase-2-a").exists())
        self.assertEqual("phase-1-a", report["alvo"]["dir"])
        self.assertNotIn("wip", report)

    def test_apply_preserves_existing_historical_implement(self) -> None:
        """Apply conserva byte a byte um implement.md legado sem depender dele."""
        vf = seed_vibeflow(self.repo)
        seed_phase(vf, "phase-1-a", "plan.md", "implement.md")
        original = b"# fatia 1\n\x00historico\n"
        (vf / "phases" / "phase-1-a" / "implement.md").write_bytes(original)
        _, report = invoke(self.repo, "--apply")
        self.assertEqual(original, (vf / "phases" / "phase-1-a" / "implement.md").read_bytes())
        self.assertEqual("phase-1-a", report["alvo"]["dir"])
        self.assertNotIn("wip", report)

    def test_apply_without_alvo_or_slug(self) -> None:
        vf = seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--apply", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("IMPLEMENT_SEM_ALVO", process.stderr)

    def test_slug_creates_avulsa(self) -> None:
        """Slug explícito cria somente a pasta alvo, sem arquivo de execução."""
        vf = seed_vibeflow(self.repo)
        _, report = invoke(self.repo, "--apply", "--slug", "hotfix-cor")
        dest = vf / "phases" / "phase-1-hotfix-cor"
        self.assertTrue(dest.is_dir())
        self.assertFalse((dest / "implement.md").exists())
        self.assertEqual("phase-1-hotfix-cor", report["alvo"]["dir"])
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
            "# Plan\n\n## Prontidão das provas\n\n- Requisitos verificados: Python disponível no CI\n"
            "- Ausências e ação na fila: nenhuma\n\n"
            "## Tasks\n\n### T1: entrega inicial\n\n- [ ] T1 concluída\n"
            "- **Spec:** A1\n- **O quê:** resultado inicial\n- **Aceite:** observável\n"
            "- **Verificação:** `python -m unittest`\n- **Deps:** nenhuma\n\n"
            "- **Checkpoint de retomada:** estado salvo\n  - Próximo passo: revisar\n"
            "  - Paths da prova: `src/a.py`=abc\n  - Git: `HEAD=def`\n"
            "  - Prova: válida no snapshot\n\n"
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
        """Seleciona somente a fila do baseline MVP, isolada das phases numeradas."""
        vf = seed_vibeflow(self.repo)
        phase = seed_phase(vf, "phase-9-outra", "plan.md")
        write_plan(phase, plan_tasks(("T1", " ", "nenhuma")))
        seed_mvp(vf, plan_tasks(("T7", " ", "nenhuma")))
        _, report = invoke(self.repo, "--mvp")
        self.assertEqual("mvp", report["alvo"]["kind"])
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

    def test_mvp_apply_preserves_existing_historical_implement(self) -> None:
        """Apply no MVP preserva o arquivo legado e não exige um novo implement.md."""
        vf = seed_vibeflow(self.repo)
        mvp = seed_mvp(vf, plan_tasks(("T1", " ", "nenhuma")))
        original = b"# Fatia T1\n\x00\n## Fatia T2\n"
        (mvp / "implement.md").write_bytes(original)
        _, report = invoke(self.repo, "--apply", "--mvp")
        self.assertEqual(original, (mvp / "implement.md").read_bytes())
        self.assertEqual("mvp", report["alvo"]["kind"])
        self.assertTrue(report["analyze_gate"]["pronto"])
        self.assertNotIn("wip", report)
        self.assertEqual([], [item.name for item in (vf / "phases").iterdir() if item.is_dir()])

    def test_mvp_rejects_phase_selectors(self) -> None:
        seed_vibeflow(self.repo)
        process, _ = invoke(self.repo, "--mvp", "--slug", "produto", check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("MODO_INVALIDO", process.stderr)

    def test_independent_task_completions_preserve_queue_and_task_commit_attribution(self) -> None:
        """Compara fila, conteúdo final e commits Git reais após retornos serial ou fora de ordem."""
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

            # Cada cenário usa Git real; o commit inicial separa o baseline das entregas das tasks.
            self._git(repo, "init", "--quiet")
            self._git(repo, "config", "user.name", "VibeFlow Test")
            self._git(repo, "config", "user.email", "vibeflow-test@example.invalid")
            self._git(repo, "add", "--", ".vibeflow")
            self._git(repo, "commit", "--quiet", "-m", "fixture: baseline")

            _, report = invoke(repo)
            self.assertEqual(["T1", "T2"], report["fila"]["elegiveis"])
            self.assertEqual([{"id": "T3", "deps": ["T1", "T2"]}], report["fila"]["bloqueadas"])

            # Integra cada retorno em path exclusivo e registra a alteração real no Git.
            for index, task in enumerate(completion_order):
                source_path = f"src/{task.lower()}.txt"
                source_file = repo / source_path
                source_file.parent.mkdir(parents=True, exist_ok=True)
                source_file.write_text(f"resultado de {task}\n", encoding="utf-8")
                plan = plan.replace(f"- [ ] {task} concluída", f"- [x] {task} concluída", 1)
                write_plan(phase, plan)
                plan_path = ".vibeflow/phases/phase-1-fixture/plan.md"
                self._git(repo, "add", "--", plan_path, source_path)
                self._git(repo, "commit", "--quiet", "-m", f"task({task}): resultado {task}")
                _, report = invoke(repo)
                if index == 0:
                    remaining = completion_order[1]
                    self.assertEqual([remaining], report["fila"]["elegiveis"])
                    self.assertEqual([{"id": "T3", "deps": [remaining]}], report["fila"]["bloqueadas"])
                else:
                    self.assertEqual(["T3"], report["fila"]["elegiveis"])
                    self.assertEqual([], report["fila"]["bloqueadas"])

            # A dependente só é liberada depois dos dois commits independentes.
            source_path = "src/t3.txt"
            source_file = repo / source_path
            source_file.parent.mkdir(parents=True, exist_ok=True)
            source_file.write_text("resultado de T3\n", encoding="utf-8")
            plan = plan.replace("- [ ] T3 concluída", "- [x] T3 concluída", 1)
            write_plan(phase, plan)
            plan_path = ".vibeflow/phases/phase-1-fixture/plan.md"
            self._git(repo, "add", "--", plan_path, source_path)
            self._git(repo, "commit", "--quiet", "-m", "task(T3): resultado T3")
            _, report = invoke(repo)

            # Lê mensagens e paths dos commits produzidos pelo Git, não de metadados montados no teste.
            task_commits = {}
            for line in self._git(repo, "log", "--format=%s%x09%H").stdout.splitlines():
                message, commit_hash = line.split("\t", 1)
                if not message.startswith("task("):
                    continue
                task = message[len("task("):].split(")", 1)[0]
                changed_paths = sorted(
                    path
                    for path in self._git(repo, "show", "--format=", "--name-only", commit_hash).stdout.splitlines()
                    if path
                )
                task_commits[task] = {"message": message, "paths": changed_paths}

            self.assertEqual([], report["fila"]["abertas"])
            self.assertEqual([], report["fila"]["elegiveis"])
            self.assertEqual([], self._git(repo, "status", "--porcelain").stdout.splitlines())
            expected_plan_path = ".vibeflow/phases/phase-1-fixture/plan.md"
            for task in ("T1", "T2", "T3"):
                self.assertEqual(
                    [expected_plan_path, f"src/{task.lower()}.txt"],
                    task_commits[task]["paths"],
                )
                self.assertEqual(f"task({task}): resultado {task}", task_commits[task]["message"])

            final_state = {
                path: (repo / path).read_bytes()
                for path in (expected_plan_path, "src/t1.txt", "src/t2.txt", "src/t3.txt")
            }
            results[execution] = {
                "fila": {
                    key: report["fila"][key]
                    for key in ("concluidas", "abertas", "elegiveis", "bloqueadas")
                },
                "commits": task_commits,
                "final_state": final_state,
            }

        self.assertEqual(results["sequential"], results["delegated"])
        commits = results["sequential"]["commits"]
        self.assertEqual({"T1", "T2", "T3"}, set(commits))


class SkillContracts(unittest.TestCase):
    """Trava no disco os contratos que a skill precisa para ler fila e executar o ciclo de implementação."""

    def test_express_precedes_init_and_routes_same_phase_adjustments(self) -> None:
        """Mantém o Express sem fase antes dos motores e retém ajustes na entrega atual."""
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        express_start = skill.index("1. Antes de exigir `.vibeflow/`")
        script_start = skill.index("2. Fora do Express")
        express = skill[express_start:script_start]

        self.assertLess(express_start, script_start)
        self.assertIn("No fluxo padrão, sem `.vibeflow/`: `/vibe-init`", skill)
        self.assertNotIn("Sem `.vibeflow/`: `/vibe-init`.", skill)
        self.assertIn("mudança de código clara e localizada", express)
        self.assertIn("Texto puro segue edição direta, fora desta skill", express)
        self.assertIn("não rode `vibe-init`", express)
        self.assertIn("nem crie ou exija `.vibeflow/`", express)
        self.assertIn("atualize a T* aberta", express)
        self.assertIn("uma T* curta ao plan existente", express)
        self.assertIn("o R* existente", express)
        self.assertIn("sai do Express e segue a cadeia aplicável", express)
        for trigger in (
            "privacidade", "obrigação jurídica", "autenticação", "autorização",
            "pagamento", "segredo", "persistência", "perda de dados",
        ):
            with self.subTest(trigger=trigger):
                self.assertIn(trigger, express)

    # Garante que a skill consome a fila do JSON transitório no stdout.
    def test_skill_reads_fila_from_stdout_json(self) -> None:
        """Mantém a skill alinhada ao JSON compacto de alvo, fila e avisos."""
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("stdout", text)
        self.assertIn("fila.elegiveis", text)
        self.assertIn("restrito a `alvo`, `fila` e `avisos`", text)
        self.assertIn("não crie `implement.md`", text)
        self.assertNotIn(".vibeflow/implement-report.json", text)
        self.assertIn("escolha a elegível de menor número, inclusive quando houver várias", text)
        self.assertIn("total de T*s da fase e quantas estão concluídas", text)


    def test_skill_requires_execution_cycle_and_green_test(self) -> None:
        """Garante que a prova final sucede a simplificação e continua obrigatória."""
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        dod = (SKILL_DIR / "references" / "definition-of-done.md").read_text(encoding="utf-8")
        self.assertIn("Sem teste verde executável", skill)
        self.assertIn("Reconhecer", skill)
        self.assertIn("Codar", skill)
        self.assertLess(skill.index("Simplificar antes da prova"), skill.index("Executar a prova final"))
        self.assertIn("uma vez, no estado integrado", skill)
        self.assertIn("Não rebaixe", dod)

    def test_skill_bounds_delegation_and_coordinator_ownership(self) -> None:
        """Trava entrega delimitada e exclusividade do coordenador sobre estado compartilhado."""
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Só após o humano aprovar a execução paralela", skill)
        self.assertIn("use delegação nativa se o host oferecer", skill)
        self.assertIn("resultado, aceite, dependências, paths exclusivos e comando de verificação", skill)
        self.assertIn("Agentes não alteram os artefatos vivos `plan.md`, `spec.md` ou `review.md`", skill)
        self.assertIn("somente o coordenador altera artefatos vivos e o índice Git", skill)
        self.assertIn("worktree/branch isolada ou ownership sem sobreposição", skill)
        self.assertIn("paths integrados e provados pela task", skill)

    def test_skill_repeats_proof_only_after_failure_or_code_test_edit(self) -> None:
        """Garante uma prova final por estado e reexecução somente quando ela perde validade."""
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Se a prova falhar", skill)
        self.assertIn("Edição posterior em código ou teste invalida apenas as provas cujos inputs mudaram", skill)
        self.assertIn("edição de plan, spec, review ou outro registro não invalida a prova", skill)

    # Confirma que retomada valida o estado Git e preserva os gates de risco.
    def test_resume_checkpoint_validates_git_inputs_and_keeps_gates(self) -> None:
        """Trava o checkpoint mínimo, a validade das provas e os gates sensíveis."""
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        visual = (SKILL_DIR / "references" / "chrome-devtools.md").read_text(encoding="utf-8")
        for field in ("estado", "próximo passo", "paths relevantes à prova", "git hash-object", "head"):
            with self.subTest(field=field):
                self.assertIn(field, skill.lower())
        self.assertIn("git status --short", skill)
        self.assertIn("git hash-object -- <path>", skill)
        self.assertIn("Remova o checkpoint ao concluir a T*", skill)
        self.assertIn("Smoke Test / Walking Skeleton entra somente quando o ponto de entrada real foi criado ou alterado", skill)
        self.assertIn("inclusive analyze aprovado e limpo no MVP", skill)
        self.assertIn("Visual: necessária", skill)
        self.assertIn("Visual: dispensada", skill)
        self.assertIn("Tocar arquivo de UI, HTML ou DOM, sozinho, não abre navegador", skill)
        self.assertIn("A review reaproveita essa evidência", skill)
        self.assertIn("o aceite depende de aparência", visual)
        self.assertIn("não basta", visual)

    # Garante que cada task termina em commit isolado e que o push fica para a review.
    def test_skill_requires_task_commit_without_push(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("git diff --cached --check", skill)
        self.assertIn("git add -- path/da/task outro/path", skill)
        self.assertIn("task(Tn)", skill)
        self.assertIn("Não faça `git push` nesta etapa", skill)
        self.assertIn("git add -A", skill)



# Verifica se existe uma versão real de PowerShell 7, única suportada pelo motor gêmeo.
def powershell7() -> str | None:
    executable = shutil.which("pwsh")
    if not executable:
        return None
    probe = subprocess.run([executable, "-NoProfile", "-Command", "$PSVersionTable.PSVersion.Major"], capture_output=True, text=True, check=False)
    return executable if probe.stdout.strip().isdigit() and int(probe.stdout.strip()) >= 7 else None


@unittest.skipUnless(powershell7(), "PowerShell 7 indisponível")
class PowershellParity(unittest.TestCase):
    """Confere paridade do alvo, da fila e da preservação entre os motores."""

    def setUp(self) -> None:
        self.repo = Path.cwd() / f".vibe-implement-ps-{uuid.uuid4().hex}"
        self.repo.mkdir()

    def tearDown(self) -> None:
        remove_fixture_tree(self.repo)

    # Confirma que o PowerShell entrega o alvo sem criar implement.md ou relatório.
    def test_apply_reuse_same_path(self) -> None:
        """Apply mantém o destino existente e não prepara um registro duplicado."""
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
        self.assertFalse(dest.exists())
        self.assertTrue((vf / "phases" / "phase-1-lock-bloco" / "plan.md").is_file())
        report = json.loads(process.stdout)
        self.assertFalse((vf / "implement-report.json").exists())
        self.assertEqual({"alvo", "fila", "avisos"}, set(report))
        self.assertNotIn("wip", report)

    # Confirma que o motor PowerShell preserva o conteúdo do implement já existente.
    def test_apply_preserves_existing_file(self) -> None:
        """Apply não altera bytes de um implement.md histórico já presente."""
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
        report = json.loads(process.stdout)
        self.assertFalse((vf / "implement-report.json").exists())
        self.assertEqual("phase-1-lock-bloco", report["alvo"]["dir"])
        self.assertNotIn("wip", report)

    # Compara fila Python e PowerShell pela saída transitória em JSON.
    def test_fila_parity_dep_blocks(self) -> None:
        """Mantém fila equivalente e stdout compacto nos dois motores."""
        vf = seed_vibeflow(self.repo)
        phase = seed_phase(vf, "phase-1-a", "plan.md")
        write_plan(phase, plan_tasks(("T1", " ", "nenhuma"), ("T2", " ", "T1")))
        for number in range(2, 21):
            seed_phase(vf, f"phase-{number}-historico", "spec.md")
        _, py_report = invoke(self.repo)
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        ps_report = json.loads(process.stdout)
        self.assertFalse((vf / "implement-report.json").exists())
        self.assertEqual({"alvo", "fila", "avisos"}, set(py_report))
        self.assertEqual({"alvo", "fila", "avisos"}, set(ps_report))
        self.assertNotIn("phase-20-historico", process.stdout)
        self.assertEqual(py_report["alvo"], ps_report["alvo"])
        self.assertEqual(py_report["fila"]["elegiveis"], ps_report["fila"]["elegiveis"])
        self.assertEqual(py_report["fila"]["bloqueadas"], ps_report["fila"]["bloqueadas"])
        self.assertEqual(["T1"], ps_report["fila"]["elegiveis"])
        self.assertEqual([{"id": "T2", "deps": ["T1"]}], ps_report["fila"]["bloqueadas"])

    # Confirma que o gate MVP e a fila chegam no stdout sem relatório persistido.
    def test_mvp_apply_same_path_and_gate(self) -> None:
        """Apply no MVP mantém o gate e a fila sem criar implement.md."""
        vf = seed_vibeflow(self.repo)
        mvp = seed_mvp(vf, plan_tasks(("T1", " ", "nenhuma")))
        process = subprocess.run(
            [powershell7(), "-File", str(POWERSHELL_SCRIPT), "-Root", str(self.repo), "-Apply", "-Mvp"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertFalse((mvp / "implement.md").exists())
        report = json.loads(process.stdout)
        self.assertFalse((vf / "implement-report.json").exists())
        self.assertEqual("mvp", report["alvo"]["kind"])
        self.assertEqual({"alvo", "fila", "avisos", "analyze_gate"}, set(report))
        self.assertTrue(report["analyze_gate"]["pronto"])
        self.assertEqual(["T1"], report["fila"]["elegiveis"])
        self.assertNotIn("wip", report)


if __name__ == "__main__":
    unittest.main()
