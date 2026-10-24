// plan.test.mjs: testes de comportamento do script plan da skill vibeflow.
//
// Confere a parte mecânica do plan.md contra references/disco.md (Plan) e a cobertura dos
// critérios da spec (references/analyze/coverage.md): forma do passo e do checkpoint,
// critérios inexistentes ou sem passo, seções obrigatórias e placeholder de template
// esquecido. Rodar com: node --test

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { conferirPlan } from '../../skills/vibeflow/scripts/plan.mjs';
import { repo, escrever, cli, PH, passo, checkpoint, plan } from './_apoio.mjs';

/** spec.md com os critérios dados na seção `## Critérios de aceite`. */
const specCom = (criterios, extra = '') =>
  `# Spec: agenda\n# Alvo: phase-1-agenda\n# Status: aprovado\n# Rota: high\n\n## Objetivo\n\nx${extra}\n\n## Critérios de aceite\n\n${criterios.map((a) => `- ${a}: resultado ${a}`).join('\n')}\n`;

function fase(t, linhas, { criterios = ['A1'], planTexto, extraSpec } = {}) {
  const raiz = repo(t);
  escrever(raiz, `${PH}/spec.md`, specCom(criterios, extraSpec));
  escrever(raiz, `${PH}/plan.md`, planTexto ?? plan(linhas));
  return raiz;
}

test('plan bem formado, com checkpoint e todos os critérios cobertos, não tem achado', (t) => {
  const r = conferirPlan(fase(t, [passo('1', { aceite: 'A1' }), passo('2a', { aceite: 'A2' }), passo('2b', { aceite: 'nenhum' }), checkpoint('A1, A2')], { criterios: ['A1', 'A2'] }));
  assert.deepEqual(r.achados, []);
  assert.deepEqual([r.passos, r.checkpoints], [3, 1]);
});

test('critério sem passo, Aceite: inexistente e Aceite: fora do formato são achado', (t) => {
  const r = conferirPlan(fase(t, [passo('1', { aceite: 'A1, A9' }), passo('2', { aceite: 'todos' })], { criterios: ['A1', 'A2'] }));
  assert.deepEqual(r.achados, [
    'passo 1: Aceite: cita A9, que não existe na spec',
    'passo 2: Aceite: deve listar A* da spec ou dizer nenhum',
    'critério A2 da spec sem passo',
  ]);
});

test('campos ausentes, fora de ordem e Prova: vazia são achado', (t) => {
  const r = conferirPlan(fase(t, [
    '- [ ] 1: entrega · Aceite: A1 · Prova: `node --test` · Arquivos: `src/a.js`',
    '- [ ] 2: entrega · Aceite: A1',
    '- [ ] 3: entrega · Aceite: A1 · Arquivos: `src/c.js` · Prova: ',
  ]));
  assert.deepEqual(r.achados, [
    'passo 1: campos fora da ordem Aceite:, Arquivos:, Prova:',
    'passo 2: falta o campo Prova:',
    'passo 3: Prova: vazia',
  ]);
});

test('checkpoint no início, com critério que o trecho não entrega, e linha estranha em Passos', (t) => {
  const r = conferirPlan(fase(t, [checkpoint('A1'), passo('1', { aceite: 'A1' }), checkpoint('A2'), 'texto solto'], { criterios: ['A1', 'A2'] }));
  assert.deepEqual(r.achados, [
    'linha fora do formato de passo ou checkpoint em ## Passos: texto solto',
    'checkpoint 1º item: sem passo entre ele e o checkpoint anterior ou o início',
    'checkpoint 1º item: cita A1, que nenhum passo do trecho coberto entrega',
    'checkpoint 3º item: cita A2, que nenhum passo do trecho coberto entrega',
    'critério A2 da spec sem passo',
  ]);
});

test('numeração e irmãos sobrepostos vêm da mesma regra do estado', (t) => {
  const r = conferirPlan(fase(t, [passo('1'), passo('3')]));
  assert.deepEqual(r.achados, ['numeração fora de sequência no passo 3 (esperado 2)']);
});

test('sem Regressão completa e com Achados do analyze fora do fim são achado', (t) => {
  const texto = `# Plan: x\n\n## Passos\n\n${passo('1')}\n\n## Achados do analyze\n\nNenhum achado.\n\n## Outra\n\nx\n`;
  const r = conferirPlan(fase(t, null, { planTexto: texto }));
  assert.deepEqual(r.achados, ['plan sem a seção ## Regressão completa', '## Achados do analyze não é a última seção do plan']);
});

test('placeholder do template esquecido é achado, salvo entre crases', (t) => {
  const r = conferirPlan(fase(t, [passo('1')], { extraSpec: '\n\nCitação do template: `<frase curta>`.\n\n<quem opera, o que a entrega resolve e o que é sucesso, em 2 a 4 frases>' }));
  assert.equal(r.achados.length, 1);
  assert.match(r.achados[0], /^spec\.md, linha \d+: placeholder <quem opera/);
});

test('CLI: 0 sem achado, 1 com achado, 2 sem plan ou alvo', (t) => {
  const raiz = fase(t, [passo('1')]);
  assert.equal(cli('plan.mjs', ['--raiz', raiz]).codigo, 0);
  escrever(raiz, `${PH}/plan.md`, plan([passo('1', { aceite: 'A7' })]));
  const r = cli('plan.mjs', ['--raiz', raiz, '--json']);
  assert.equal(r.codigo, 1);
  assert.ok(JSON.parse(r.out).achados.includes('critério A1 da spec sem passo'));
  assert.equal(cli('plan.mjs', ['--raiz', raiz, '--alvo', 'phase-9']).codigo, 2);
  assert.equal(cli('plan.mjs', ['--raiz', repo(t)]).codigo, 2);
});
