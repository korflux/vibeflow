// tempo-transcripts.test.mjs: testes de comportamento de tools/tempo-transcripts.mjs.
//
// Cada cenário grava transcripts mínimos (JSONL do host) numa pasta temporária e confere a
// duração por categoria, o tempo ativo com pausa, o papel lido do meta, a janela de tempo, a
// amostra mascarada e o erro de uso.
// Rodar com: node --test

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import { medirTranscripts, categoria } from '../../tools/tempo-transcripts.mjs';

const SCRIPT = resolve(dirname(fileURLToPath(import.meta.url)), '../../tools/tempo-transcripts.mjs');
const T = (min, seg = 0) => `2026-11-08T10:${String(min).padStart(2, '0')}:${String(seg).padStart(2, '0')}.000Z`;

const uso = (ts, id, name, input) => JSON.stringify({ timestamp: ts, message: { content: [{ type: 'tool_use', id, name, input }] } });
const resultado = (ts, id) => JSON.stringify({ timestamp: ts, message: { content: [{ type: 'tool_result', tool_use_id: id }] } });

function pasta(t) {
  const raiz = mkdtempSync(join(tmpdir(), 'vibeflow-transcripts-'));
  t.after(() => rmSync(raiz, { recursive: true, force: true }));
  return raiz;
}

function gravar(raiz, rel, linhas, meta) {
  mkdirSync(dirname(join(raiz, rel)), { recursive: true });
  writeFileSync(join(raiz, rel), linhas.join('\n'));
  if (meta) writeFileSync(join(raiz, rel.replace(/\.jsonl$/, '.meta.json')), JSON.stringify(meta));
}

/** Líder com uma leitura; implementador com teste de 2 min, tipos de 30 s e espera por saída de 3 min. */
function cenario(t) {
  const raiz = pasta(t);
  gravar(raiz, 'sessao.jsonl', [
    uso(T(0), 'l1', 'Read', { file_path: 'a' }), resultado(T(0, 2), 'l1'),
    uso(T(0, 5), 'l2', 'Agent', { prompt: 'x' }), resultado(T(9), 'l2'),
  ]);
  gravar(raiz, 'sessao/subagents/agent-1.jsonl', [
    uso(T(1), 'a1', 'Bash', { command: 'pnpm vitest run src/a.test.ts password=abc123', run_in_background: true }), resultado(T(3), 'a1'),
    uso(T(3), 'a2', 'Bash', { command: 'pnpm --filter web typecheck' }), resultado(T(3, 30), 'a2'),
    uso(T(4), 'a3', 'TaskOutput', { task_id: 'x' }), resultado(T(7), 'a3'),
    'linha que não é JSON',
    uso(T(40), 'a4', 'Bash', { command: 'git status' }), resultado(T(40, 1), 'a4'),
  ], { agentType: 'implementador', effort: 'medium' });
  return raiz;
}

test('categoria: comando de shell pela primeira regra que casa; despacho de subagente não conta', () => {
  assert.equal(categoria('Bash', { command: 'pnpm playwright test --grep A1' }), 'e2e');
  assert.equal(categoria('PowerShell', { command: 'pnpm -r typecheck' }), 'tipos');
  assert.equal(categoria('Bash', { command: 'node --test' }), 'teste');
  assert.equal(categoria('Bash', { command: 'until grep -q ok log; do sleep 5; done' }), 'espera');
  assert.equal(categoria('Bash', { command: 'git log' }), 'git');
  assert.equal(categoria('Bash', { command: 'ls' }), 'shell-outro');
  assert.equal(categoria('Edit', {}), 'edicao');
  assert.equal(categoria('Agent', {}), null);
});

test('duração por categoria, do tool_use ao tool_result', (t) => {
  const m = medirTranscripts(cenario(t));
  assert.equal(m.arquivos, 2);
  assert.deepEqual(m.categorias.teste, { ms: 120e3, chamadas: 1 });
  assert.deepEqual(m.categorias.tipos, { ms: 30e3, chamadas: 1 });
  assert.deepEqual(m.categorias.espera, { ms: 180e3, chamadas: 1 });
  assert.deepEqual(m.categorias.leitura, { ms: 2e3, chamadas: 1 });
  assert.deepEqual(m.categorias.git, { ms: 1e3, chamadas: 1 });
  assert.equal(m.emSegundoPlano, 1);
  assert.equal(m.ferramentaMs, 333e3);
});

test('papel vem do meta; tempo ativo ignora a pausa acima de 10 min; prova soma teste, tipos e espera', (t) => {
  const m = medirTranscripts(cenario(t));
  const imp = m.papeis['implementador/medium'];
  assert.equal(imp.agentes, 1);
  assert.equal(imp.ativoMs, 361e3); // 10:01 a 10:07 e mais 1 s depois da pausa de 33 min
  assert.equal(imp.provaMs, 330e3);
  assert.equal(imp.ferramentaMs, 331e3);
  // Líder: 10:00 a 10:09, com o despacho do subagente fora das ferramentas.
  assert.equal(m.papeis.lider.ativoMs, 540e3);
  assert.equal(m.papeis.lider.ferramentaMs, 2e3);
});

test('amostra de comando lento sai com o valor do segredo mascarado', (t) => {
  const m = medirTranscripts(cenario(t));
  assert.deepEqual(m.amostras.teste, [{ segundos: 120, comando: 'pnpm vitest run src/a.test.ts password=***' }]);
});

test('janela --de e --ate corta os eventos fora dela', (t) => {
  const m = medirTranscripts(cenario(t), { de: Date.parse(T(2, 59)), ate: Date.parse(T(3, 59)) });
  assert.deepEqual(Object.keys(m.categorias), ['tipos']);
});

test('histórico copiado para outro arquivo de sessão conta uma vez, pelo uuid do evento', (t) => {
  const raiz = pasta(t);
  const ev = (ts, uuid, bloco) => JSON.stringify({ timestamp: ts, uuid, message: { content: [bloco] } });
  const linhas = [
    ev(T(0), 'u1', { type: 'tool_use', id: 'x', name: 'Bash', input: { command: 'node --test' } }),
    ev(T(2), 'u2', { type: 'tool_result', tool_use_id: 'x' }),
  ];
  gravar(raiz, 'a.jsonl', linhas);
  gravar(raiz, 'b.jsonl', [...linhas, ev(T(3), 'u3', { type: 'tool_use', id: 'y', name: 'Read', input: {} }), ev(T(3, 1), 'u4', { type: 'tool_result', tool_use_id: 'y' })]);
  gravar(raiz, 'c.jsonl', linhas);
  const m = medirTranscripts(raiz);
  assert.deepEqual(m.categorias.teste, { ms: 120e3, chamadas: 1 });
  assert.deepEqual(m.categorias.leitura, { ms: 1e3, chamadas: 1 });
  assert.equal(m.papeis.lider.agentes, 2); // c.jsonl não tem evento novo
  assert.equal(m.papeis.lider.ativoMs, 121e3); // 2 min em a.jsonl e 1 s em b.jsonl
});

test('subagente sem meta e pasta vazia', (t) => {
  const raiz = pasta(t);
  assert.equal(medirTranscripts(raiz).arquivos, 0);
  gravar(raiz, 's/subagents/x.jsonl', [uso(T(0), 'a', 'Bash', { command: 'ls' }), resultado(T(0, 1), 'a')]);
  assert.deepEqual(Object.keys(medirTranscripts(raiz).papeis), ['subagente?']);
});

test('CLI: texto, --json em ASCII e erro de uso com código 2', (t) => {
  const raiz = cenario(t);
  const rodar = (args) => {
    try { return { codigo: 0, out: execFileSync(process.execPath, [SCRIPT, ...args], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }) }; }
    catch (e) { return { codigo: e.status, out: e.stdout || '' }; }
  };
  assert.match(rodar([raiz]).out, /implementador\/medium/);
  const json = rodar([raiz, '--json']);
  assert.equal(JSON.parse(json.out).categorias.teste.ms, 120e3);
  assert.doesNotMatch(json.out, /[^\x00-\x7F]/);
  assert.equal(rodar([]).codigo, 2);
  assert.equal(rodar([join(raiz, 'nao-existe')]).codigo, 2);
  assert.equal(rodar([raiz, '--de', 'ontem']).codigo, 2);
  assert.equal(rodar([raiz, '--outra']).codigo, 2);
});
