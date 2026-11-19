// encerrar.test.mjs: testes de comportamento do hook encerrar da skill vibeflow.
//
// Confere que o hook segura o implementador, uma vez, quando o disco mostra caixa de passo
// sem commit, commit sem caixa ou alteração não commitada sem dono numa phase aberta com
// plan (references/disco.md, Estado da phase; references/implementador.md, Recorte e Commit
// do passo), que deixa encerrar o estado legítimo do trecho e que nunca segura por erro
// próprio. Rodar com: node --test

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { join } from 'node:path';
import { achadosDoEncerramento, decidir } from '../../skills/vibeflow/scripts/encerrar.mjs';
import { SCRIPTS, repo, fase, escrever, commit, PH, plan, passo } from './_apoio.mjs';

const evento = (raiz, extra = {}) => ({
  hook_event_name: 'SubagentStop', agent_type: 'implementador', stop_hook_active: false, cwd: raiz, ...extra,
});

test('trecho limpo: passos commitados com a caixa e nada fora do recorte deixam encerrar', (t) => {
  const raiz = fase(t, [passo('1'), passo('2')]);
  escrever(raiz, 'src/p1.js', 'x\n');
  escrever(raiz, `${PH}/plan.md`, plan([passo('1', { caixa: true }), passo('2')]));
  commit(raiz, 'task(phase-1:1): entrega 1');
  assert.deepEqual(achadosDoEncerramento(raiz), []);
  assert.equal(decidir(evento(raiz)), null);
});

test('caixa marcada sem commit segura o encerramento, com o passo no motivo', (t) => {
  const raiz = fase(t, [passo('1'), passo('2')]);
  escrever(raiz, `${PH}/plan.md`, plan([passo('1', { caixa: true }), passo('2')]));
  const r = decidir(evento(raiz));
  assert.equal(r.decision, 'block');
  assert.match(r.reason, /passo 1 com a caixa marcada e sem commit task\(phase-1:1\)/);
});

test('commit do passo com a caixa vazia segura o encerramento', (t) => {
  const raiz = fase(t, [passo('1'), passo('2')], { commits: ['task(phase-1:1): entrega 1'] });
  assert.match(decidir(evento(raiz)).reason, /passo 1 com commit task\(phase-1:1\) e a caixa vazia/);
});

test('alteração fora do recorte segura; dentro do recorte de passo aberto, não', (t) => {
  const raiz = fase(t, [passo('1'), passo('2')]);
  escrever(raiz, 'src/p1.js', 'em andamento\n'); // trecho parado num impedimento
  assert.equal(decidir(evento(raiz)), null);
  escrever(raiz, 'src/outro.js', 'x\n');
  assert.match(decidir(evento(raiz)).reason, /alteração não commitada fora do recorte: src\/outro\.js/);
});

test('trabalho alheio declarado no plan e registro em .erros-encontrados/ não seguram', (t) => {
  const raiz = fase(t, [passo('1')]);
  escrever(raiz, `${PH}/plan.md`, plan([passo('1'), '', '## Trabalho alheio', '', '- `docs/humano.md`']));
  commit(raiz, 'docs: trabalho alheio');
  escrever(raiz, 'docs/humano.md', 'x\n');
  escrever(raiz, '.erros-encontrados/flake.md', 'x\n');
  assert.equal(decidir(evento(raiz)), null);
});

test('segura uma vez: com stop_hook_active o implementador encerra e relata', (t) => {
  const raiz = fase(t, [passo('1')]);
  escrever(raiz, 'src/outro.js', 'x\n');
  assert.notEqual(decidir(evento(raiz)), null);
  assert.equal(decidir(evento(raiz, { stop_hook_active: true })), null);
});

test('fora do alcance: outro papel, outro evento, entrega sem phase com plan e raiz sem Git', (t) => {
  const raiz = fase(t, [passo('1')]);
  escrever(raiz, 'src/outro.js', 'x\n');
  assert.equal(decidir(evento(raiz, { agent_type: 'revisor' })), null);
  assert.equal(decidir(evento(raiz, { agent_type: undefined })), null);
  assert.equal(decidir(evento(raiz, { hook_event_name: 'Stop' })), null);
  assert.equal(decidir(evento(raiz, { cwd: undefined })), null);
  assert.equal(decidir(null), null);
  // Entrega low ou medium: sem phase aberta com plan, a alteração não commitada é o esperado.
  const semPhase = repo(t);
  escrever(semPhase, 'src/a.js', 'x\n');
  assert.equal(decidir(evento(semPhase)), null);
  assert.equal(decidir(evento(join(raiz, 'pasta-que-nao-existe'))), null);
});

/** Roda o hook como o host o roda: evento no stdin, decisão no stdout. */
function hook(stdin) {
  return execFileSync(process.execPath, [join(SCRIPTS, 'encerrar.mjs')], { input: stdin, encoding: 'utf8' });
}

test('CLI: imprime o bloqueio em JSON ASCII e sai com 0; sem achado ou com entrada ilegível, não imprime', (t) => {
  const raiz = fase(t, [passo('1')]);
  assert.equal(hook(JSON.stringify(evento(raiz))), '');
  escrever(raiz, 'src/outro.js', 'x\n');
  const out = hook(JSON.stringify(evento(raiz)));
  assert.equal(JSON.parse(out).decision, 'block');
  assert.doesNotMatch(out, /[^\x00-\x7F]/);
  assert.equal(hook('isto não é JSON'), '');
  assert.equal(hook(''), '');
});
