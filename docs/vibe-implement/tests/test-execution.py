#!/usr/bin/env python3
"""Jornadas reais CLI/disco do sidecar; a mesma fixture prova os dois motores."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPTS = Path(__file__).resolve().parents[3] / 'vibe-implement' / 'scripts'


# A fixture é isolada e a limpeza de Git read-only não ignora falhas.
def cleanup(path):
    def writable(operation, filename, _):
        os.chmod(filename, 0o700)
        operation(filename)
    for attempt in range(5):
        try:
            shutil.rmtree(path, onerror=writable)
            return
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.1)


class ExecutionContracts(unittest.TestCase):
    engine = 'python'

    def setUp(self):
        if self.engine == 'powershell' and not shutil.which('pwsh'):
            self.skipTest('PowerShell 7 ausente')
        self.repo = Path(tempfile.mkdtemp(prefix='.execution-fixture-', dir=SCRIPTS.parents[1]))
        self.addCleanup(cleanup, self.repo)
        self.phase = self.repo / '.vibeflow/phases/phase-1-test'
        self.phase.mkdir(parents=True)
        self.plan = self.phase / 'plan.md'
        self.plan.write_text('# Status: aprovado\n# Protocolo: coordenacao-v1\n# Modo: A\n## Tasks\n### T1: core\n- [x] T1 concluída\n- **Deps:** nenhuma\n### T2: consumer\n- [ ] T2 concluída\n- **Deps:** T1\n', encoding='utf-8')
        self.record = self.phase / 'execution.json'
        (self.repo / 'core.py').write_text('value = 1\n', encoding='utf-8')
        (self.repo / 'consumer.py').write_text('from core import value\n', encoding='utf-8')
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('add', '--', '.')
        self.git('commit', '-qm', 'fixture')

    # Git é usado apenas na fixture e representa a operação do finalizador.
    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.repo), *args], capture_output=True, text=True, check=True).stdout.strip()

    # PowerShell recebe arrays nativos via script constante, sem executar strings de evidência.
    def invoke(self, operation=None, task=None, inputs=None, command=None, result=None, actor=None, details=False, success=True, root=True):
        values = {'Root': str(self.repo)} if root else {}
        for key, value in (('Operation', operation), ('Task', task), ('InputPath', inputs), ('Command', command), ('Result', result), ('Actor', actor)):
            if value is not None:
                values[key] = value
        if details:
            values['Details'] = True
        if self.engine == 'python':
            args = [sys.executable, str(SCRIPTS / 'implement.py')]
            if root:
                args += ['--root', str(self.repo)]
            for key, value in (('operation', operation), ('task', task), ('command', command), ('result', result), ('actor', actor)):
                if value is not None:
                    args += ['--' + key, value]
            for path in inputs or []:
                args += ['--input', path]
            if details:
                args += ['--details']
            env = None
        else:
            env = dict(os.environ, VIBE_FIXTURE_ARGS=json.dumps(values), VIBE_FIXTURE_SCRIPT=str(SCRIPTS / 'implement.ps1'))
            args = ['pwsh', '-NoProfile', '-Command', '$values = ConvertFrom-Json $env:VIBE_FIXTURE_ARGS -AsHashtable; & $env:VIBE_FIXTURE_SCRIPT @values; exit $LASTEXITCODE']
        process = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', env=env, cwd=self.repo)
        if success:
            self.assertEqual(process.returncode, 0, process.stderr)
            return json.loads(process.stdout)
        self.assertNotEqual(process.returncode, 0, process.stdout)
        self.assertIn('EXECUTION_INVALIDO', process.stderr)
        return process

    # Registra provas locais de dois recortes relacionados com todos os inputs reais.
    def locals(self):
        self.invoke('local', 'T1', ['core.py'], 'python core.py', 'verde', 'writer')
        self.invoke('local', 'T2', ['consumer.py'], 'python consumer.py', 'verde', 'writer')

    def test_journey_resume_commit_invalidation(self):
        first = self.invoke()
        self.assertFalse(self.record.exists())
        self.assertEqual(first['fila']['elegiveis'], ['T1'])
        self.assertEqual(first['fila']['concluidas'], [])  # Checkbox cannot certify execution.
        self.invoke('init', actor='finalizer')
        self.locals()
        report = self.invoke()
        self.assertEqual(report['etapa'], 'validar')
        self.assertNotIn('detalhes', report['execucao'])
        self.invoke('integracao', inputs=['core.py', 'consumer.py'], command='python consumer.py', result='verde', actor='verifier')
        self.assertEqual(self.invoke()['etapa'], 'commitar_integracao')
        self.invoke('commit', actor='finalizer', success=False)
        self.git('add', '--', 'core.py', 'consumer.py', '.vibeflow')
        self.git('commit', '--allow-empty', '-qm', 'task(T1,T2): verified')
        committed = self.invoke('commit', actor='finalizer')
        self.assertEqual(committed['etapa'], 'revisar')
        self.assertEqual(committed['fila']['concluidas'], ['T1', 'T2'])
        before = self.record.read_bytes()
        (self.repo / 'core.py').write_text('value = 2\n', encoding='utf-8')
        invalidated = self.invoke()
        self.assertEqual(invalidated['etapa'], 'implementar')
        self.assertEqual(invalidated['execucao']['tasks'], [{'id': 'T1', 'local_valida': False}, {'id': 'T2', 'local_valida': True}])
        self.assertEqual(self.record.read_bytes(), before)
        self.assertFalse(list(self.phase.glob('.execution-*.tmp')))

    def test_independence_coverage_fail_and_inert_command(self):
        self.invoke('local', 'T2', ['consumer.py'], 'x', 'verde', 'writer', success=False)
        command = 'echo SECRET > must-not-exist; $(exit 91)'
        self.invoke('local', 'T1', ['core.py'], command, 'verde', 'writer')
        self.assertFalse((self.repo / 'must-not-exist').exists())
        self.invoke('local', 'T2', ['consumer.py'], 'check', 'verde', 'writer')
        before = self.record.read_bytes()
        self.invoke('integracao', inputs=['core.py', 'consumer.py'], command='check', result='verde', actor='writer', success=False)
        self.invoke('integracao', inputs=['core.py'], command='check', result='verde', actor='verifier', success=False)
        self.assertEqual(before, self.record.read_bytes())
        self.invoke('integracao', inputs=['core.py', 'consumer.py'], command='check', result='falha', actor='verifier')
        self.assertEqual(self.invoke()['etapa'], 'corrigir_validacao')
        self.invoke('commit', actor='finalizer', success=False)

    def test_review_correction_commit_preserves_original_and_returns_to_review(self):
        self.locals()
        self.invoke('integracao', inputs=['core.py', 'consumer.py'], command='check', result='verde', actor='verifier')
        baseline = json.loads(self.record.read_text(encoding='utf-8'))['integracao']
        self.git('add', '--', '.vibeflow')
        self.git('commit', '-qm', 'task(T1,T2): verified')
        original = self.git('rev-parse', 'HEAD')
        self.invoke('commit', actor='finalizer')
        # Repeating a valid proof without changes never creates a correction gate.
        self.invoke('integracao', inputs=['core.py', 'consumer.py'], command='check', result='verde', actor='verifier')
        self.assertNotIn('correcao', json.loads(self.record.read_text(encoding='utf-8')))
        self.assertEqual(self.invoke()['etapa'], 'revisar')
        # Uma rodada reúne classificações atuais e históricas sem perder gates de Git/blobs.
        review = self.phase / 'review.md'
        review.write_text('# Status: request-changes\n- [ ] R1: **Nit** - fix core\n- [ ] R2: **Optional** - fix consumer\n- [ ] R3: **FYI** - fix flow\n- [ ] R4: **Required** - fix contract\n- [ ] R5: **Critical** - fix boundary\n## Veredito vigente\n- [x] **Request changes**: R1\n', encoding='utf-8')
        self.assertEqual(self.invoke()['etapa'], 'corrigir')
        (self.repo / 'core.py').write_text('value = 2\n', encoding='utf-8')
        self.invoke('local', 'T1', ['core.py'], 'check', 'verde', 'corrector')
        self.invoke('integracao', inputs=['core.py', 'consumer.py'], command='check', result='verde', actor='verifier')
        renewed = json.loads(self.record.read_text(encoding='utf-8'))
        self.assertEqual(renewed['commit'], original)
        self.assertEqual(renewed['integracao']['origem'], baseline['origem'])
        self.assertEqual(renewed['correcao']['base']['inputs'], baseline['proof']['inputs'])
        self.invoke('commit', actor='finalizer', success=False)  # Green uncommitted code is insufficient.
        self.git('add', '--', 'core.py')
        self.git('commit', '-qm', 'task(T1,T2): false reintegration')
        self.invoke('commit', actor='finalizer', success=False)
        self.git('commit', '--allow-empty', '-qm', 'task(R999): unknown finding')
        self.invoke('commit', actor='finalizer', success=False)
        (self.repo / 'core.py').write_text('value = 3\n', encoding='utf-8')
        self.git('add', '--', 'core.py')
        self.git('commit', '-qm', 'task(R1,R2,R3,R4,R5): wrong blobs')
        (self.repo / 'core.py').write_text('value = 2\n', encoding='utf-8')
        self.invoke('commit', actor='finalizer', success=False)
        self.git('add', '--', 'core.py')
        self.git('commit', '-qm', 'task(R1,R2,R3,R4,R5): corrected')
        correction = self.git('rev-parse', 'HEAD')
        committed = self.invoke('commit', actor='finalizer')
        self.assertEqual(committed['etapa'], 'corrigir')  # Somente o responsável do registro fecha os R* comprovados.
        state = json.loads(self.record.read_text(encoding='utf-8'))
        self.assertEqual(state['commit'], original)
        self.assertEqual(state['correcao']['commit'], correction)
        self.assertEqual(committed['execucao']['integracao']['commit_encontrado'], correction)
        review.write_text(review.read_text(encoding='utf-8').replace('[ ] R1:', '[x] R1:').replace('[ ] R2:', '[X] R2:').replace('[ ] R3:', '[x] R3:').replace('[ ] R4:', '[x] R4:').replace('[ ] R5:', '[x] R5:'), encoding='utf-8')
        self.assertEqual(self.invoke()['etapa'], 'revisar')
        review.write_text('# Status: rascunho\n- [x] R1: **Nit** - fixed\n- [X] R2: **Optional** - fixed\n- [x] R3: **FYI** - fixed\n- [x] R4: **Required** - fixed\n- [x] R5: **Critical** - fixed\n## Veredito vigente\n- [x] **Approve**: verified\n', encoding='utf-8')
        self.assertEqual(self.invoke()['etapa'], 'confirmar')
        (self.repo / 'core.py').write_text('value = 4\n', encoding='utf-8')
        self.assertEqual(self.invoke()['fila']['concluidas'], [])
        self.invoke('commit', actor='finalizer', success=False)

    def test_correction_schema_refuses_invalid_baseline_without_writing(self):
        self.locals()
        self.invoke('integracao', inputs=['core.py', 'consumer.py'], command='check', result='verde', actor='verifier')
        self.git('add', '--', '.vibeflow')
        self.git('commit', '-qm', 'task(T1,T2): verified')
        self.invoke('commit', actor='finalizer')
        original = json.loads(self.record.read_text(encoding='utf-8'))
        proof = original['integracao']['proof']
        invalid = [None, {}, {'base': proof, 'commit': True},
                   {'base': dict(proof, resultado='falha'), 'commit': None},
                   {'base': dict(proof, inputs={'../core.py': 'a' * 40}), 'commit': None}]
        for correction in invalid:
            with self.subTest(correction=correction):
                content = json.dumps(dict(original, correcao=correction))
                self.record.write_text(content, encoding='utf-8')
                self.invoke(success=False)
                self.assertEqual(self.record.read_text(encoding='utf-8'), content)

    def test_corruption_types_duplicates_limits_and_unknown_task(self):
        self.invoke('init', actor='finalizer')
        original = json.loads(self.record.read_text(encoding='utf-8'))
        for content in ('{', '{"schema":1,"schema":1}', 'x' * 1048577,
                        json.dumps(dict(original, schema=True)), json.dumps(dict(original, extra=1)),
                        json.dumps(dict(original, tasks={'T9': {'actor': 'writer', 'proof': None}}))):
            with self.subTest(content=content[:60]):
                self.record.write_text(content, encoding='utf-8')
                self.invoke(success=False)
                self.assertEqual(self.record.read_text(encoding='utf-8'), content)

    def test_input_path_escape_and_limits_leave_state_unchanged(self):
        self.invoke('init', actor='finalizer')
        before = self.record.read_bytes()
        for path in ('../core.py', '/core.py', 'C:/core.py', 'core\\py', '.git/config', '.GIT/config', 'a//b', 'NUL', '.git /config', '.vibeflow/phases/phase-1-test/execution.json'):
            self.invoke('local', 'T1', [path], 'check', 'verde', 'writer', success=False)
        self.invoke('local', 'T1', ['core.py', 'core.py'], 'check', 'verde', 'writer', success=False)
        self.invoke('local', 'T1', ['core.py'], 'x' * 2049, 'verde', 'writer', success=False)
        self.assertEqual(before, self.record.read_bytes())

    def test_gate_init_idempotence_and_commit_wrong_blobs(self):
        self.plan.write_text(self.plan.read_text(encoding='utf-8').replace('Status: aprovado', 'Status: rascunho'), encoding='utf-8')
        self.invoke('init', actor='finalizer', success=False)
        self.assertFalse(self.record.exists())
        self.plan.write_text(self.plan.read_text(encoding='utf-8').replace('Status: rascunho', 'Status: aprovado'), encoding='utf-8')
        self.invoke('init', actor='finalizer')
        compact = json.dumps(json.loads(self.record.read_text(encoding='utf-8')), separators=(',', ':'))
        self.record.write_text(compact, encoding='utf-8')
        self.invoke('init', actor='finalizer')
        self.assertEqual(self.record.read_text(encoding='utf-8'), compact)
        self.locals()
        self.invoke('integracao', inputs=['core.py', 'consumer.py'], command='check', result='verde', actor='verifier')
        (self.repo / 'core.py').write_text('value = 9\n', encoding='utf-8')
        self.git('add', '--', 'core.py')
        self.git('commit', '-qm', 'task(T1,T2): wrong blobs')
        (self.repo / 'core.py').write_text('value = 1\n', encoding='utf-8')
        self.assertEqual(self.invoke()['etapa'], 'commitar_integracao')
        self.invoke('commit', actor='finalizer', success=False)

    def test_revalidation_expands_inputs_and_preserves_origin(self):
        self.locals()
        self.invoke('integracao', inputs=['core.py', 'consumer.py'], command='check', result='verde', actor='verifier')
        origin = json.loads(self.record.read_text(encoding='utf-8'))['integracao']['origem']
        (self.repo / 'config.txt').write_text('mode=test\n', encoding='utf-8')
        self.invoke('local', 'T1', ['core.py', 'config.txt'], 'check', 'verde', 'writer')
        self.assertEqual(self.invoke()['etapa'], 'validar')
        self.invoke('integracao', inputs=['core.py', 'consumer.py', 'config.txt'], command='check', result='verde', actor='verifier')
        self.assertEqual(json.loads(self.record.read_text(encoding='utf-8'))['integracao']['origem'], origin)
        details = self.invoke(details=True)['execucao']['detalhes']
        self.assertEqual(set(details), {'schema', 'protocolo', 'tasks', 'integracao', 'commit'})

    def test_cycles_and_mode_b_without_sidecar(self):
        self.plan.write_text(self.plan.read_text(encoding='utf-8').replace('Deps:** nenhuma', 'Deps:** T2'), encoding='utf-8')
        self.invoke(success=False)
        self.plan.write_text(self.plan.read_text(encoding='utf-8').replace('Deps:** T2', 'Deps:** nenhuma').replace('# Modo: A', '# Modo: B'), encoding='utf-8')
        report = self.invoke()
        self.assertEqual(report['fila']['concluidas'], ['T1'])
        self.assertFalse(self.record.exists())
        self.invoke('init', actor='finalizer', success=False)

    def test_sidecar_directory_and_symlink_are_refused(self):
        self.record.mkdir()
        self.invoke(success=False)
        self.record.rmdir()
        other = self.repo / 'outside.json'
        other.write_text('{}', encoding='utf-8')
        try:
            self.record.symlink_to(other)
        except OSError:
            self.skipTest('host sem permissão de symlink')
        self.invoke(success=False)
        self.assertEqual(other.read_text(encoding='utf-8'), '{}')

    def test_cwd_git_root_preserves_snapshots_in_both_protocols(self):
        self.locals()
        self.assertEqual(self.invoke(root=False)['etapa'], 'validar')
        self.assertEqual(self.invoke(root=False)['execucao']['tasks'], self.invoke()['execucao']['tasks'])
        state = json.loads(self.record.read_text(encoding='utf-8'))
        body = '# Status: aprovado\n# Protocolo: etapas-v1\n# Modo: A\n- **Integração:** {"testes":"prontos","prova":null,"commit":"pendente"}\n## Tasks\n'
        for tid in ('T1', 'T2'):
            deps = 'nenhuma' if tid == 'T1' else 'T1'
            local = json.dumps({'estado': 'implementada', 'local': state['tasks'][tid]['proof']})
            body += f'### {tid}: test\n- [ ] {tid} concluída\n- **Deps:** {deps}\n- **Execução:** {local}\n'
        self.plan.write_text(body, encoding='utf-8')
        self.assertEqual(self.invoke(root=False)['etapa'], 'validar')
        self.assertTrue(all(row['local_valida'] for row in self.invoke(root=False)['execucao']['tasks']))


class PowerShellExecutionContracts(ExecutionContracts):
    engine = 'powershell'


if __name__ == '__main__':
    unittest.main()
