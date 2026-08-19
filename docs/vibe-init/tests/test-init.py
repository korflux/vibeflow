#!/usr/bin/env python3
"""Contratos de docs/vibe-init/ARQUITETURA.md §13 no motor Python, mais paridade essencial."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[3] / "vibe-init"
SCRIPT = SKILL_DIR / "scripts" / "init.py"
TEMPLATE = SKILL_DIR / "templates" / "REGRAS.md"
POWERSHELL_SCRIPT = SKILL_DIR / "scripts" / "init.ps1"


# Executa o motor Python e devolve processo e relatório, quando produzido.
def invoke(repo: Path, *arguments: str, check: bool = True, env: dict[str, str] | None = None) -> tuple[subprocess.CompletedProcess[str], dict | None]:
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo), *arguments],
        capture_output=True,
        text=True,
        check=check,
        env={**os.environ, **(env or {})},
    )
    report_path = repo / ".vibeflow" / "init-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else None
    return process, report


# Altera o consolidado e usa o token do relatório para concluir o merge.
def complete_merge(repo: Path, report: dict, text: str) -> dict:
    target = repo / ".vibeflow" / "REGRAS.md"
    target.write_text(target.read_text(encoding="utf-8") + f"\n{text}\n", encoding="utf-8")
    _, final_report = invoke(repo, "--apply-pointers", "--merge-token", report["apply_token"])
    assert final_report is not None
    return final_report


# Monta um REGRAS.md já preenchido, sem SLOT, para os cenários de idempotência.
def filled_rules(paragraph: str) -> str:
    template = TEMPLATE.read_text(encoding="utf-8")
    start = template.index("<!-- VIBEFLOW:CADEIA start -->")
    end = template.index("<!-- VIBEFLOW:CADEIA end -->") + len("<!-- VIBEFLOW:CADEIA end -->")
    return (
        f"# Regras do projeto\n\n{template[start:end]}\n\n"
        f"## Projeto\n{paragraph}\n\n## Ambiente\nhomolog\n\n"
        "## Versão (semver)\n- x\n\n## Git\n- y\n\n## Estrutura\n- src\n\n## Regras deste repo\nnada\n"
    )


# Verifica se existe uma versão real de PowerShell 7, única suportada pelo motor gêmeo.
def powershell7() -> str | None:
    executable = shutil.which("pwsh")
    if not executable:
        return None
    probe = subprocess.run([executable, "-NoProfile", "-Command", "$PSVersionTable.PSVersion.Major"], capture_output=True, text=True, check=False)
    return executable if probe.stdout.strip().isdigit() and int(probe.stdout.strip()) >= 7 else None


class PythonContracts(unittest.TestCase):
    """Verifica os invariantes com maior risco de perda, divergência ou path inventado."""

    # Cria uma raiz isolada e remove tudo automaticamente ao fim de cada teste.
    def setUp(self) -> None:
        self.repo = Path.cwd() / f".vibe-init-python-{uuid.uuid4().hex}"
        self.repo.mkdir()

    # Libera a árvore isolada inclusive quando uma asserção falha.
    def tearDown(self) -> None:
        shutil.rmtree(self.repo, ignore_errors=True)

    # Atalho para os caminhos consultados na maioria dos contratos.
    def live(self) -> Path:
        return self.repo / ".vibeflow" / "REGRAS.md"

    # 1. Confirma a criação mínima, os dois links e a ausência de old em repo vazio.
    def test_new_repository(self) -> None:
        _, report = invoke(self.repo)
        self.assertEqual("novo", report["flow"])
        self.assertTrue((self.repo / "AGENTS.md").is_symlink())
        self.assertTrue((self.repo / "CLAUDE.md").is_symlink())
        self.assertTrue((self.repo / ".vibeflow" / "phases" / ".gitkeep").is_file())
        self.assertFalse((self.repo / ".vibeflow" / "old").exists())

    # 2. Sem README nem manifest, o parágrafo continua sendo pergunta para o humano.
    def test_paragraph_stays_open(self) -> None:
        _, report = invoke(self.repo)
        self.assertIn("paragrafo", report["slots_abertos"])
        self.assertIn("<!-- SLOT:paragrafo -->", self.live().read_text(encoding="utf-8"))

    # 3. Pasta vazia é reparo: cria phases, consolidado e os dois ponteiros.
    def test_repair_empty_folder(self) -> None:
        (self.repo / ".vibeflow").mkdir()
        _, report = invoke(self.repo)
        self.assertEqual("reparar", report["flow"])
        self.assertTrue(self.live().is_file())
        self.assertTrue((self.repo / "AGENTS.md").is_symlink())

    # 3b/3c. phases e .gitkeep são garantidos mesmo quando um dos dois já existe.
    def test_phases_and_gitkeep_are_restored(self) -> None:
        (self.repo / ".vibeflow" / "phases").mkdir(parents=True)
        _, report = invoke(self.repo)
        self.assertTrue((self.repo / ".vibeflow" / "phases" / ".gitkeep").is_file())
        self.assertIn(".vibeflow/phases/.gitkeep", [item["alvo"] for item in report["actions"]])

    # 4. Ponteiro faltando não autoriza reescrever o consolidado nem gerar backup.
    def test_missing_pointer_only(self) -> None:
        (self.repo / ".vibeflow").mkdir()
        self.live().write_text(filled_rules("App."), encoding="utf-8")
        antes = self.live().read_text(encoding="utf-8")
        (self.repo / "AGENTS.md").symlink_to(".vibeflow/REGRAS.md")
        _, report = invoke(self.repo)
        self.assertEqual(antes, self.live().read_text(encoding="utf-8"))
        self.assertTrue((self.repo / "CLAUDE.md").is_symlink())
        self.assertEqual([], report["olds"])

    # 5. Legado único vira fonte de merge e só perde o papel de arquivo depois do apply.
    def test_single_legacy_source(self) -> None:
        (self.repo / "AGENTS.md").write_text("regra crítica\n", encoding="utf-8")
        _, report = invoke(self.repo)
        self.assertEqual(["legado_vs_regras"], [merge["id"] for merge in report["merges"]])
        self.assertFalse((self.repo / "AGENTS.md").is_symlink())
        self.assertEqual("regra crítica\n", (self.repo / ".vibeflow" / "old" / "AGENTS.md").read_text(encoding="utf-8"))
        complete_merge(self.repo, report, "regra crítica")
        self.assertTrue((self.repo / "AGENTS.md").is_symlink())

    # 6. Dois legados diferentes viram união, não escolha, e nenhum original é convertido antes.
    def test_two_different_sources(self) -> None:
        (self.repo / "AGENTS.md").write_text("regra A\n", encoding="utf-8")
        (self.repo / "CLAUDE.md").write_text("regra C\n", encoding="utf-8")
        _, report = invoke(self.repo)
        self.assertEqual(["duas_fontes"], [merge["id"] for merge in report["merges"]])
        self.assertFalse((self.repo / "AGENTS.md").is_symlink())
        self.assertFalse((self.repo / "CLAUDE.md").is_symlink())

    # 6b. Legados idênticos entram uma vez só como fonte, mas os dois backups são gravados.
    def test_identical_sources_merge_once(self) -> None:
        (self.repo / "AGENTS.md").write_text("mesmo texto\n", encoding="utf-8")
        (self.repo / "CLAUDE.md").write_text("mesmo texto\n", encoding="utf-8")
        _, report = invoke(self.repo)
        self.assertEqual([".vibeflow/old/AGENTS.md"], report["merges"][0]["sources"])
        self.assertEqual({".vibeflow/old/AGENTS.md", ".vibeflow/old/CLAUDE.md"}, {old["to"] for old in report["olds"]})

    # 7. Segundo backup do mesmo nome recebe timestamp e não pisa o original mais antigo.
    def test_old_collision_keeps_first(self) -> None:
        (self.repo / "AGENTS.md").write_text("v1\n", encoding="utf-8")
        _, report = invoke(self.repo)
        complete_merge(self.repo, report, "v1")
        (self.repo / "AGENTS.md").unlink()
        (self.repo / "AGENTS.md").write_text("v2\n", encoding="utf-8")
        _, second = invoke(self.repo)
        old_dir = self.repo / ".vibeflow" / "old"
        self.assertEqual("v1\n", (old_dir / "AGENTS.md").read_text(encoding="utf-8"))
        stamped = [item for item in old_dir.iterdir() if item.name.startswith("AGENTS.md.")]
        self.assertEqual(1, len(stamped))
        self.assertEqual("v2\n", stamped[0].read_text(encoding="utf-8"))

    # 8. Cópia idêntica ao consolidado é backup e vira link, sem entrar em merge.
    def test_pointer_equal_to_rules(self) -> None:
        (self.repo / ".vibeflow").mkdir()
        self.live().write_text(filled_rules("App."), encoding="utf-8")
        (self.repo / "AGENTS.md").write_text(filled_rules("App."), encoding="utf-8")
        _, report = invoke(self.repo)
        self.assertEqual([], report["merges"])
        self.assertTrue((self.repo / "AGENTS.md").is_symlink())
        self.assertIn(".vibeflow/old/AGENTS.md", [old["to"] for old in report["olds"]])

    # 9. Backup que não confere impede a substituição do arquivo do usuário.
    def test_old_hash_mismatch_preserves_original(self) -> None:
        (self.repo / "AGENTS.md").write_text("regra crítica\n", encoding="utf-8")
        process, _ = invoke(self.repo, check=False, env={"VIBE_INIT_TEST_CORRUPT_OLD": "1"})
        self.assertNotEqual(0, process.returncode)
        self.assertIn("OLD_HASH_MISMATCH", process.stderr)
        self.assertEqual("regra crítica\n", (self.repo / "AGENTS.md").read_text(encoding="utf-8"))

    # 9b. Falha depois da primeira escrita ainda deixa relatório do que já foi feito no disco.
    def test_partial_report_on_late_failure(self) -> None:
        (self.repo / "AGENTS.md").write_text("regra crítica\n", encoding="utf-8")
        _, report = invoke(self.repo, check=False, env={"VIBE_INIT_TEST_CORRUPT_OLD": "1"})
        self.assertIsNotNone(report)
        self.assertTrue(any("run interrompida" in aviso for aviso in report["avisos"]))

    # 10. Disco saudável sem SLOT não gera ação material nem backup novo.
    def test_healthy_repository_is_idempotent(self) -> None:
        vibeflow = self.repo / ".vibeflow"
        (vibeflow / "phases").mkdir(parents=True)
        (vibeflow / "phases" / ".gitkeep").write_text("", encoding="utf-8")
        self.live().write_text(filled_rules("App."), encoding="utf-8")
        (self.repo / "AGENTS.md").symlink_to(".vibeflow/REGRAS.md")
        (self.repo / "CLAUDE.md").symlink_to(".vibeflow/REGRAS.md")
        _, report = invoke(self.repo)
        material = {"old", "escrever_template", "symlink_criar", "symlink_recriar", "mover", "apagar_raiz", "merge_pendente"}
        self.assertEqual([], [item for item in report["actions"] if item["op"] in material])

    # 11. Consolidado fora do lugar é movido, com backup, sem virar merge.
    def test_rules_only_at_root(self) -> None:
        (self.repo / "REGRAS.md").write_text("regras do time\n", encoding="utf-8")
        _, report = invoke(self.repo)
        self.assertEqual([], report["merges"])
        self.assertFalse((self.repo / "REGRAS.md").exists())
        self.assertIn("regras do time", self.live().read_text(encoding="utf-8"))
        self.assertIn(".vibeflow/old/REGRAS-raiz.md", [old["to"] for old in report["olds"]])

    # 11b. Consolidado na raiz somado a legado é união: o legado não pode virar link nesta run.
    def test_root_rules_with_legacy_pointer_merges(self) -> None:
        (self.repo / "REGRAS.md").write_text("regra da raiz\n", encoding="utf-8")
        (self.repo / "AGENTS.md").write_text("regra crítica do agents\n", encoding="utf-8")
        _, report = invoke(self.repo)
        self.assertEqual(["legado_vs_regras"], [merge["id"] for merge in report["merges"]])
        self.assertIn(".vibeflow/old/AGENTS.md", report["merges"][0]["sources"])
        self.assertFalse((self.repo / "AGENTS.md").is_symlink())
        complete_merge(self.repo, report, "regra crítica do agents")
        self.assertTrue((self.repo / "AGENTS.md").is_symlink())

    # 11c. Duplicado somado a legado precisa listar as três fontes antes de qualquer conversão.
    def test_duplicated_rules_with_legacy_pointer(self) -> None:
        (self.repo / ".vibeflow").mkdir()
        self.live().write_text("viva\n", encoding="utf-8")
        (self.repo / "REGRAS.md").write_text("raiz\n", encoding="utf-8")
        (self.repo / "CLAUDE.md").write_text("claude legado\n", encoding="utf-8")
        _, report = invoke(self.repo)
        self.assertEqual({"regras_duplicado", "legado_vs_regras"}, {merge["id"] for merge in report["merges"]})
        fontes = {source for merge in report["merges"] for source in merge["sources"]}
        self.assertEqual({".vibeflow/old/REGRAS-raiz.md", ".vibeflow/old/REGRAS.md", ".vibeflow/old/CLAUDE.md"}, fontes)
        self.assertFalse((self.repo / "CLAUDE.md").is_symlink())

    # 12. Interrupção depois do backup preserva o original ainda no lugar.
    def test_stop_after_old_keeps_original(self) -> None:
        (self.repo / "AGENTS.md").write_text("regra crítica\n", encoding="utf-8")
        _, report = invoke(self.repo, "--stop-after-old")
        self.assertFalse((self.repo / "AGENTS.md").is_symlink())
        self.assertTrue((self.repo / ".vibeflow" / "old" / "AGENTS.md").is_file())

    # 13. Checkout sem symlink deixa o path como texto: é ponteiro degradado, não regra.
    def test_pointer_text_is_not_a_source(self) -> None:
        (self.repo / ".vibeflow").mkdir()
        self.live().write_text(filled_rules("App."), encoding="utf-8")
        (self.repo / "AGENTS.md").write_text(".vibeflow/REGRAS.md", encoding="utf-8")
        _, report = invoke(self.repo)
        self.assertEqual("ponteiro_texto", report["inventory"]["agents"])
        self.assertEqual([], report["merges"])
        self.assertTrue((self.repo / "AGENTS.md").is_symlink())

    # 14. Sem consolidado, o texto do ponteiro degradado não pode entrar no arquivo vivo.
    def test_pointer_text_without_rules(self) -> None:
        (self.repo / "AGENTS.md").write_text(".vibeflow/REGRAS.md", encoding="utf-8")
        _, report = invoke(self.repo)
        self.assertEqual([], report["merges"])
        linhas = [linha.strip() for linha in self.live().read_text(encoding="utf-8").splitlines()]
        self.assertNotIn(".vibeflow/REGRAS.md", linhas)

    # 15. Consolidado sem o roteador recebe o bloco sem perder o texto do usuário.
    def test_cadeia_upsert_preserves_user_text(self) -> None:
        (self.repo / ".vibeflow").mkdir()
        self.live().write_text("# Regras do projeto\n\n## Projeto\ntexto do time\n", encoding="utf-8")
        _, report = invoke(self.repo)
        body = self.live().read_text(encoding="utf-8")
        self.assertIn("<!-- VIBEFLOW:CADEIA start -->", body)
        self.assertIn("texto do time", body)
        self.assertIn("cadeia_upsert", [item["op"] for item in report["actions"]])

    # 16. Roteador desatualizado volta ao texto canônico do template, sem tocar no resto.
    def test_cadeia_refresh(self) -> None:
        (self.repo / ".vibeflow").mkdir()
        self.live().write_text(
            "# Regras do projeto\n\n<!-- VIBEFLOW:CADEIA start -->\ntabela velha\n<!-- VIBEFLOW:CADEIA end -->\n\n## Projeto\ntexto do time\n",
            encoding="utf-8",
        )
        invoke(self.repo)
        body = self.live().read_text(encoding="utf-8")
        self.assertNotIn("tabela velha", body)
        self.assertIn("texto do time", body)

    # 17. Impede que ApplyPointers seja usado antes de o conteúdo legado entrar no consolidado.
    def test_apply_requires_changed_target(self) -> None:
        (self.repo / "AGENTS.md").write_text("regra crítica\n", encoding="utf-8")
        _, report = invoke(self.repo)
        process, _ = invoke(self.repo, "--apply-pointers", "--merge-token", report["apply_token"], check=False)
        self.assertNotEqual(0, process.returncode)
        self.assertIn("MERGE_NAO_APLICADO", process.stderr)
        self.assertFalse((self.repo / "AGENTS.md").is_symlink())

    # 17b. Finaliza um merge válido e elimina o estado operacional pendente.
    def test_apply_after_merge(self) -> None:
        (self.repo / "AGENTS.md").write_text("regra crítica\n", encoding="utf-8")
        _, report = invoke(self.repo)
        complete_merge(self.repo, report, "regra crítica")
        self.assertTrue((self.repo / "AGENTS.md").is_symlink())
        self.assertFalse((self.repo / ".vibeflow" / "init-pending.json").exists())

    # 18. Remove REGRAS.md da raiz somente depois que as duas fontes foram consolidadas.
    def test_duplicate_rules_cleanup(self) -> None:
        (self.repo / ".vibeflow").mkdir()
        self.live().write_text("viva\n", encoding="utf-8")
        (self.repo / "REGRAS.md").write_text("raiz\n", encoding="utf-8")
        _, report = invoke(self.repo)
        self.assertTrue((self.repo / "REGRAS.md").is_file())
        complete_merge(self.repo, report, "raiz")
        self.assertFalse((self.repo / "REGRAS.md").exists())

    # 19. Preserva regras preexistentes e inclui todos os arquivos operacionais ignorados.
    def test_existing_gitignore(self) -> None:
        (self.repo / ".vibeflow").mkdir()
        ignore = self.repo / ".vibeflow" / ".gitignore"
        ignore.write_text("custom.log\n", encoding="utf-8")
        invoke(self.repo)
        self.assertEqual({"custom.log", "init-report.json", "init-pending.json"}, set(ignore.read_text(encoding="utf-8").splitlines()))

    # 20. Tipo estrutural inesperado falha antes de criar qualquer ponteiro.
    def test_unexpected_type_fails_early(self) -> None:
        (self.repo / ".vibeflow").mkdir()
        (self.repo / ".vibeflow" / "REGRAS.md").mkdir()
        process, _ = invoke(self.repo, check=False)
        self.assertIn("TIPO_INESPERADO", process.stderr)
        self.assertFalse((self.repo / "AGENTS.md").exists())

    # 21. Garante que migrations em dependências ignoradas não contaminem o scan factual.
    def test_migration_scan_prunes_dependencies(self) -> None:
        (self.repo / "node_modules" / "pkg" / "migrations").mkdir(parents=True)
        _, report = invoke(self.repo)
        self.assertFalse(report["migrations_detectadas"])

    # 22. Estrutura tem teto: repo grande não transforma o SLOT em dump da árvore.
    def test_structure_is_capped(self) -> None:
        for index in range(200):
            (self.repo / f"pasta{index:03d}").mkdir()
        _, report = invoke(self.repo)
        self.assertEqual(121, len(report["scan"]["estrutura"]))
        self.assertIn("omitidos", report["scan"]["estrutura"][-1])

    # 23. Compara o schema e os principais estados dos dois motores quando existe PowerShell 7.
    @unittest.skipUnless(powershell7(), "PowerShell 7 indisponível para teste de paridade")
    def test_new_repository_contract_parity(self) -> None:
        other = Path.cwd() / f".vibe-init-pwsh-{uuid.uuid4().hex}"
        other.mkdir()
        try:
            subprocess.run([powershell7(), "-NoProfile", "-File", str(POWERSHELL_SCRIPT), "-Root", str(other)], check=True, capture_output=True, text=True)
            _, python_report = invoke(self.repo)
            powershell_report = json.loads((other / ".vibeflow" / "init-report.json").read_text(encoding="utf-8-sig"))
            self.assertEqual(set(powershell_report), set(python_report))
            self.assertEqual(powershell_report["inventory"], python_report["inventory"])
            self.assertEqual([item["op"] for item in powershell_report["actions"]], [item["op"] for item in python_report["actions"]])
            self.assertEqual(powershell_report["slots_abertos"], python_report["slots_abertos"])
        finally:
            shutil.rmtree(other)


if __name__ == "__main__":
    unittest.main(verbosity=2)
