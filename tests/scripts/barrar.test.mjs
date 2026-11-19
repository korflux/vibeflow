// barrar.test.mjs: testes de comportamento do hook barrar da skill vibeflow.
//
// Confere que o hook nega, só no implementador, a espera por loop e o gate recursivo do
// monorepo (references/implementador.md, Proibido no passo e Codar e provar), que deixa
// seguir os comandos legítimos parecidos e que nunca bloqueia por entrada ilegível.
// Rodar com: node --test

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { join } from 'node:path';
import { motivoDeNegar, decidir } from '../../skills/vibeflow/scripts/barrar.mjs';
import { SCRIPTS } from './_apoio.mjs';

const evento = (command, extra = {}) => ({
  hook_event_name: 'PreToolUse', agent_type: 'implementador', tool_name: 'Bash', tool_input: { command }, ...extra,
});

test('espera por loop em shell POSIX e em PowerShell é negada', () => {
  for (const c of [
    'until grep -q "passed" e2e.log; do sleep 15; done',
    'while ! curl -s localhost:3000 >/dev/null; do sleep 2; done',
    'for i in $(seq 1 30); do tail -1 out.log; sleep 5; done',
    'pnpm test &\nwhile kill -0 $!\ndo\n  sleep 3\ndone',
    'while (-not (Test-Path out.log)) { Start-Sleep -Seconds 5 }',
    'do { Start-Sleep 2 } until (Test-Path done.txt)',
  ]) assert.match(motivoDeNegar(c) || '', /Espera por loop/, c);
});

test('comando sem loop de espera segue, mesmo com as palavras do padrão', () => {
  for (const c of [
    'pnpm vitest run src/agenda.test.ts --reporter=dot',
    'git commit -m "task(phase-1:2): espera for sleep no worker; do nada"',
    'sleep 1 && curl -s localhost:3000/health',
    'for f in src/*.ts; do echo "$f"; done',
    'Start-Sleep -Seconds 1; Get-Content out.log -Tail 5',
    '',
  ]) assert.equal(motivoDeNegar(c), null, c);
});

test('gate ou teste na forma recursiva do monorepo é negado; filtrado ou sem gate segue', () => {
  for (const c of ['pnpm -r typecheck', 'cd app && pnpm --recursive run lint', 'npm run test --workspaces', 'pnpm -r exec tsc --noEmit']) {
    assert.match(motivoDeNegar(c) || '', /forma recursiva/, c);
  }
  for (const c of ['pnpm --filter web typecheck', 'pnpm -r build', 'pnpm install -r', 'pnpm -r build && pnpm --filter web test']) {
    assert.equal(motivoDeNegar(c), null, c);
  }
});

test('decidir: nega só no implementador e só em Bash ou PowerShell', () => {
  const loop = 'until grep -q ok log; do sleep 5; done';
  const r = decidir(evento(loop));
  assert.equal(r.hookSpecificOutput.hookEventName, 'PreToolUse');
  assert.equal(r.hookSpecificOutput.permissionDecision, 'deny');
  assert.match(r.hookSpecificOutput.permissionDecisionReason, /segundo plano/);
  assert.notEqual(decidir(evento(loop, { tool_name: 'PowerShell' })), null);
  assert.equal(decidir(evento(loop, { agent_type: 'verificador' })), null);
  assert.equal(decidir(evento(loop, { agent_type: undefined })), null); // líder ou Modo B
  assert.equal(decidir(evento(loop, { tool_name: 'Read' })), null);
  assert.equal(decidir(evento('pnpm --filter web test')), null);
  assert.equal(decidir(null), null);
});

/** Roda o hook como o host o roda: evento no stdin, decisão no stdout. */
function hook(stdin) {
  return execFileSync(process.execPath, [join(SCRIPTS, 'barrar.mjs')], { input: stdin, encoding: 'utf8' });
}

test('CLI: imprime a negação em JSON ASCII e sai com 0; sem achado ou com entrada ilegível, não imprime', () => {
  const out = hook(JSON.stringify(evento('pnpm -r typecheck')));
  assert.equal(JSON.parse(out).hookSpecificOutput.permissionDecision, 'deny');
  assert.doesNotMatch(out, /[^\x00-\x7F]/);
  assert.equal(hook(JSON.stringify(evento('pnpm --filter web typecheck'))), '');
  assert.equal(hook('﻿' + JSON.stringify(evento('ls'))), '');
  assert.equal(hook('isto não é JSON'), '');
  assert.equal(hook(''), '');
});
