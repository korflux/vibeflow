// medir.test.mjs: testes de comportamento do script medir da skill vibeflow.
//
// Cada cenário monta um repositório Git temporário com commits de data fixa e confere a
// medição da seção "Medição" de references/review.md (Finalizar): relógio entre o primeiro
// e o último commit do alvo, horas ativas sem as pausas, retrabalho por passo, intervalo
// mediano e passo mais lento, R* por severidade, alvo padrão e erro de uso.
// Rodar com: node --test

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { medir, linhaMedicao } from '../../skills/vibeflow/scripts/medir.mjs';
import { repo, escrever, commit, cli, PH, spec, passo, checkpoint, plan, review, veredito } from './_apoio.mjs';

const H = (h, m = 0) => `2026-11-08T${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:00Z`;

/** Phase com 3 passos e um checkpoint; o passo 2 tem um segundo commit (correção do checkpoint). */
function faseMedida(t) {
  const raiz = repo(t);
  escrever(raiz, `${PH}/spec.md`, spec('aprovado'));
  escrever(raiz, `${PH}/plan.md`, plan([
    passo('1', { caixa: true }), passo('2', { caixa: true }), checkpoint('A1', true, 'tela'), passo('3', { caixa: true }),
  ]));
  commit(raiz, 'docs: spec e plan', { data: H(8) });
  commit(raiz, 'task(phase-1:1): um', { data: H(9) });
  commit(raiz, 'task(phase-1:2): dois', { data: H(9, 30) });
  commit(raiz, 'task(phase-1:2): dois corrigido', { data: H(10, 30) });
  commit(raiz, 'task(phase-1:3): tres', { data: H(10, 40) });
  escrever(raiz, `${PH}/review.md`, review('rascunho', `${veredito(true)}## Achados\n\n- [x] R1: **Required** - \`src/p2.js\` - x - remédio: y - prova: z - papel: implementador\n- [x] R2: **Nit** - \`src/p3.js\` - x - remédio: y - prova: z - papel: implementador\n\n## Etapas\n\n### Etapa 1 - review - a..b\n\n### Etapa 2 - re-review - R1\n`));
  commit(raiz, 'task(phase-1:R1,R2): correções', { data: H(12) });
  return raiz;
}

test('relógio do primeiro ao último commit do alvo, sem o commit de fora do contrato', (t) => {
  const r = medir(faseMedida(t));
  assert.equal(r.alvo, 'phase-1');
  assert.equal(r.commits, 5);
  assert.equal(r.horas, 3);
  // Intervalos: 30, 60, 10 e 80 min, todos abaixo da pausa de 120 min.
  assert.equal(r.horasAtivas, 3);
  assert.equal(r.inicio, '2026-11-08T09:00:00.000Z');
  assert.equal(r.fim, '2026-11-08T12:00:00.000Z');
});

test('retrabalho é o passo com mais de um commit; intervalo mediano e passo mais lento', (t) => {
  const r = medir(faseMedida(t));
  assert.equal(r.passos, 3);
  assert.equal(r.checkpoints, 1);
  assert.deepEqual(r.retrabalho, [{ id: '2', commits: 2 }]);
  // Intervalos de passo: 2 (30 min), 2 de novo (60 min), 3 (10 min); o 1 não tem base.
  assert.equal(r.intervaloMediano, 30);
  assert.deepEqual(r.passoMaisLento, { ids: ['2'], minutos: 60 });
});

test('R* por severidade, etapas da review e commits de correção', (t) => {
  const r = medir(faseMedida(t));
  assert.deepEqual(r.rs, { Critical: 0, Required: 1, Nit: 1 });
  assert.equal(r.etapasReview, 2);
  assert.equal(r.commitsCorrecao, 1);
  assert.match(linhaMedicao(r), /^relógio: 3 h \(ativas: 3 h\) em 5 commits · passos: 3 · checkpoints: 1 · .*retrabalho: 2 \(2\)/);
});

test('sem alvo aberto, mede a phase de maior n; --alvo inexistente é erro de uso', (t) => {
  const raiz = faseMedida(t);
  escrever(raiz, `${PH}/review.md`, review('aprovado', veredito(true)));
  commit(raiz, 'chore(phase-1): finalize review', { data: H(13) });
  const r = medir(raiz);
  assert.equal(r.alvo, 'phase-1');
  assert.equal(r.horas, 4);
  assert.equal(r.horasAtivas, 4);
  assert.equal(cli('medir.mjs', ['--raiz', raiz, '--alvo', 'phase-9']).codigo, 2);
  assert.equal(cli('medir.mjs', ['--raiz', raiz, '--nada']).codigo, 2);
});

test('intervalo acima de 120 min conta como pausa, fora das horas ativas', (t) => {
  const raiz = faseMedida(t);
  commit(raiz, 'chore(phase-1): finalize review', { data: '2026-11-09T12:00:00Z' });
  const r = medir(raiz);
  assert.equal(r.horas, 27);
  assert.equal(r.horasAtivas, 3);
});

test('alvo sem commit sai com relógio vazio e código 0', (t) => {
  const raiz = repo(t);
  escrever(raiz, `${PH}/spec.md`, spec('rascunho'));
  const r = medir(raiz);
  assert.equal(r.commits, 0);
  assert.equal(r.horas, null);
  const saida = cli('medir.mjs', ['--raiz', raiz]);
  assert.equal(saida.codigo, 0);
  assert.match(saida.out, /relógio: - h \(ativas: - h\) em 0 commits/);
});
