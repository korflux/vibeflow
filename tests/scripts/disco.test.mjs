// disco.test.mjs: testes de comportamento dos scripts estado e ondas da skill vibeflow.
//
// Cada cenário monta um repositório Git temporário com artefatos mínimos e confere a
// leitura contra as regras de references/disco.md, references/plan.md e SKILL.md,
// seção 9. Rodar com: node --test tests/

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { execFileSync } from 'node:child_process';
import { normalizarPath, sobrepoe, lerTasks } from '../../skills/vibeflow/scripts/_disco.mjs';
import { analisarPlan } from '../../skills/vibeflow/scripts/ondas.mjs';
import { estado } from '../../skills/vibeflow/scripts/estado.mjs';

// ---------------------------------------------------------------------------
// Apoio: repositório temporário e artefatos
// ---------------------------------------------------------------------------

function repo(t) {
  const raiz = mkdtempSync(join(tmpdir(), 'vibeflow-'));
  t.after(() => rmSync(raiz, { recursive: true, force: true }));
  execFileSync('git', ['init', '-q'], { cwd: raiz });
  escrever(raiz, 'AGENTS.md', '# Regras\n<!-- VIBEFLOW:CADEIA start -->\n<!-- VIBEFLOW:CADEIA end -->\n');
  escrever(raiz, '.vibeflow/phases/.gitkeep', '');
  commit(raiz, 'chore: base');
  return raiz;
}

function escrever(raiz, rel, conteudo) {
  mkdirSync(dirname(join(raiz, rel)), { recursive: true });
  writeFileSync(join(raiz, rel), conteudo);
}

function commit(raiz, msg) {
  execFileSync('git', ['add', '--', '.'], { cwd: raiz });
  execFileSync('git', ['-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-q', '--allow-empty', '-m', msg], { cwd: raiz });
}

const PH = '.vibeflow/phases/phase-1-agenda';
const spec = (status, handoff = 'plan') => `# Spec: x\n# Alvo: phase-1-agenda\n# Status: ${status}\n# Rota: high\n\n## Handoff\n\n${handoff}\n`;
const task = (n, { caixa = false, estado = 'pendente', deps = 'nenhuma', arquivos = `\`src/t${n}.js\`` } = {}) =>
  `### T${n}: entrega ${n}\n- [${caixa ? 'x' : ' '}] T${n} concluída\n- **Estado:** ${estado}\n- **Deps:** ${deps}\n${arquivos === null ? '' : `- **Arquivos:** ${arquivos}\n`}- **Prova afetada:** \`npm test\`\n\n`;
const plan = (status, tasks) => `# Plan: x\n# Alvo: phase-1-agenda\n# Status: ${status}\n\n## Tasks\n\n${tasks.join('')}`;

// ---------------------------------------------------------------------------
// Arquivos: normalização e sobreposição
// ---------------------------------------------------------------------------

test('normaliza paths de Arquivos: conforme references/plan.md', () => {
  assert.deepEqual(normalizarPath('src/a.py'), ['src', 'a.py']);
  assert.deepEqual(normalizarPath('src/*.py'), ['src']);
  assert.deepEqual(normalizarPath('*.py'), []);
  assert.deepEqual(normalizarPath('./'), []);
  assert.deepEqual(normalizarPath('../x'), []);
  assert.deepEqual(normalizarPath('a/../b'), ['b']);
  assert.deepEqual(normalizarPath('a\\b'), ['a', 'b']);
  for (const p of ['C:/x', '/abs', 'ção.md', 'a./b', 'a /b', 'a|b']) assert.equal(normalizarPath(p), null, p);
});

test('sobreposição por prefixo de diretório, sem distinção de maiúsculas', () => {
  assert.equal(sobrepoe(['a'], ['a', 'b']), true);
  assert.equal(sobrepoe(['a'], ['ab']), false);
  assert.equal(sobrepoe(['Src'], ['src', 'x']), true);
  assert.equal(sobrepoe([], ['qualquer']), true);
});

// ---------------------------------------------------------------------------
// ondas
// ---------------------------------------------------------------------------

test('onda junta T* disjuntas e para na T* sem Arquivos', () => {
  const tasks = lerTasks(plan('aprovado', [
    task(1, { arquivos: '`src/a/`' }),
    task(2, { arquivos: '`src/b.js`' }),
    task(3, { arquivos: '`src/`' }),
    task(4, { arquivos: null }),
    task(5, { deps: 'T1', arquivos: '`src/a/x.js`' }),
  ]).split('\n'));
  const r = analisarPlan(tasks);
  assert.deepEqual(r.elegiveis, ['T1', 'T2', 'T3', 'T4']);
  assert.deepEqual(r.onda, ['T1', 'T2']);
  assert.deepEqual(r.sobreposicoes, [['T1', 'T3'], ['T2', 'T3'], ['T3', 'T5']]);
  assert.deepEqual(r.sozinhas, [{ task: 'T4', motivo: 'sem Arquivos:' }]);
});

test('T* sem Arquivos roda sozinha quando é a primeira elegível', () => {
  const r = analisarPlan(lerTasks(plan('aprovado', [task(1, { arquivos: null }), task(2)]).split('\n')));
  assert.deepEqual(r.onda, ['T1']);
});

test('Deps para T* inexistente é achado', () => {
  const r = analisarPlan(lerTasks(plan('aprovado', [task(1, { deps: 'T9' })]).split('\n')));
  assert.deepEqual(r.depsQuebradas, [{ task: 'T1', dep: 'T9' }]);
  assert.deepEqual(r.onda, []);
});

// ---------------------------------------------------------------------------
// estado
// ---------------------------------------------------------------------------

test('sem phase: classificar o pedido e próxima phase 1', (t) => {
  const raiz = repo(t);
  const r = estado(raiz);
  assert.equal(r.etapa.etapa, 'classificar o pedido');
  assert.equal(r.proximoN, 1);
});

test('spec em rascunho vence plan ausente', (t) => {
  const raiz = repo(t);
  escrever(raiz, `${PH}/spec.md`, spec('rascunho'));
  commit(raiz, 'docs: spec');
  const r = estado(raiz);
  assert.equal(r.etapa.etapa, 'spec');
  assert.equal(r.etapa.situacao, 'aguardando ajuste ou aprovação');
  assert.equal(r.progresso.percentual, 0);
});

test('plan em rascunho: 25% na rota high', (t) => {
  const raiz = repo(t);
  escrever(raiz, `${PH}/spec.md`, spec('aprovado'));
  escrever(raiz, `${PH}/plan.md`, plan('rascunho', [task(1)]));
  commit(raiz, 'docs: plan');
  const r = estado(raiz);
  assert.equal(r.etapa.etapa, 'plan');
  assert.equal(r.progresso.percentual, 25);
});

test('design conta quando o Handoff da spec aponta para design', (t) => {
  const raiz = repo(t);
  escrever(raiz, `${PH}/spec.md`, spec('aprovado', 'design'));
  commit(raiz, 'docs: spec');
  const r = estado(raiz);
  assert.equal(r.etapa.etapa, 'design');
  assert.equal(r.progresso.percentual, 20);
});

test('implement: próxima onda e progresso com fração de T*', (t) => {
  const raiz = repo(t);
  escrever(raiz, `${PH}/spec.md`, spec('aprovado'));
  escrever(raiz, `${PH}/plan.md`, plan('aprovado', [task(1, { caixa: true, estado: 'concluída' }), task(2)]));
  commit(raiz, 'task(phase-1:T1): entrega 1');
  const r = estado(raiz);
  assert.equal(r.etapa.situacao, 'implementar a próxima onda');
  assert.deepEqual(r.etapa.onda, ['T2']);
  assert.equal(r.progresso.percentual, 62);
  assert.deepEqual(r.inconsistencias, []);
});

test('commit de outra phase não confirma a T* com o mesmo ID', (t) => {
  const raiz = repo(t);
  escrever(raiz, `${PH}/spec.md`, spec('aprovado'));
  escrever(raiz, `${PH}/plan.md`, plan('aprovado', [task(1, { caixa: true, estado: 'concluída' })]));
  commit(raiz, 'task(phase-2:T1): outra phase');
  const r = estado(raiz);
  assert.ok(r.inconsistencias.some((i) => i.includes('T1 marcada sem commit')));
});

test('código não commitado nos Arquivos de T* aberta: retomar a onda', (t) => {
  const raiz = repo(t);
  escrever(raiz, `${PH}/spec.md`, spec('aprovado'));
  escrever(raiz, `${PH}/plan.md`, plan('aprovado', [task(1)]));
  commit(raiz, 'docs: plan');
  escrever(raiz, 'src/t1.js', 'x');
  const r = estado(raiz);
  assert.equal(r.etapa.situacao, 'retomar a onda');
});

test('task(medium) sem review: review da entrega medium', (t) => {
  const raiz = repo(t);
  escrever(raiz, 'src/x.js', 'x');
  commit(raiz, 'task(medium): entrega');
  assert.equal(estado(raiz).etapa.etapa, 'review da entrega medium');
});

test('phase fechada sem upstream: push pendente', (t) => {
  const raiz = repo(t);
  escrever(raiz, `${PH}/review.md`, '# Review: x\n# Status: aprovado\n# Rota: medium\n');
  commit(raiz, 'chore(phase-1): finalize review');
  const r = estado(raiz);
  assert.equal(r.etapa.etapa, 'push pendente');
  assert.equal(r.etapa.situacao, 'phase-1');
});

test('ajuste de phase fechada: progresso por R* de ajuste e etapa corrigir', (t) => {
  const raiz = repo(t);
  escrever(raiz, `${PH}/review.md`, '# Review: x\n# Status: aprovado\n# Rota: medium\n\n## Checklist de correções\n\n- [x] R1: **Required** - `a` - x\n- [ ] R2: **Required** - `src/y.js` - ajuste\n\n## Etapas\n\n### Ajuste 1 - troca\n\n- Abriu: R2\n');
  commit(raiz, 'chore(phase-1): finalize review');
  const r = estado(raiz);
  assert.equal(r.progresso.ajuste, '0/1');
  assert.equal(r.etapa.situacao, 'corrigir R*');
});

test('phase sem # Rota: é inconsistência', (t) => {
  const raiz = repo(t);
  escrever(raiz, `${PH}/spec.md`, '# Spec: x\n# Status: rascunho\n');
  commit(raiz, 'docs: spec');
  assert.ok(estado(raiz).inconsistencias.some((i) => i.includes('sem # Rota:')));
});
