// bench.test.mjs: testes de comportamento de tools/bench.mjs.
//
// Nenhum teste chama modelo. O executor falso (`executor-falso.mjs`, gravado na pasta temporária)
// recebe os mesmos argumentos que o `claude -p` receberia, confere os de isolamento e responde
// pela palavra-chave do pedido. Cobre correção, leitura da resposta, rodada ponta a ponta,
// comparação entre rodadas e erros de uso.
// Rodar com: node --test

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { corrigir, lerResposta, rodar, resumir, comparar, montarPrompt } from '../../tools/bench.mjs';

const SCRIPT = resolve(dirname(fileURLToPath(import.meta.url)), '../../tools/bench.mjs');

// Responde pelo pedido: "LOW" vira low, "ERRO" vira erro do host, "LIXO" vira texto sem JSON.
// Sem os argumentos de isolamento ou sem o contexto no arquivo de sistema, devolve erro.
const FALSO = `
import { readFileSync } from 'node:fs';
const args = process.argv.slice(2);
const prompt = args.at(-1);
const valor = (op) => args[args.indexOf(op) + 1];
const sistema = readFileSync(valor('--system-prompt-file'), 'utf8');
const isolado = valor('--tools') === '' && valor('--setting-sources') === '' && args.includes('--strict-mcp-config') && args.includes('--no-session-persistence');
const saida = (o) => process.stdout.write(JSON.stringify(o));
if (!isolado || !sistema.includes('REGRA-DO-CONTEXTO')) saida({ is_error: true, result: 'sem isolamento ou sem contexto' });
else if (prompt.includes('ERRO')) saida({ is_error: true, result: 'Failed to authenticate' });
else if (prompt.includes('LIXO')) saida({ is_error: false, result: 'não sei' });
else saida({ is_error: false, total_cost_usd: 0.001, result: '\`\`\`json\\n' + JSON.stringify({ acao: prompt.includes('LOW') ? 'low' : 'high', aviso: false, motivo: 'regra' }) + '\\n\`\`\`' });
`;

const SUITE = {
  instrucao: 'Responda em JSON.',
  campos: { acao: ['low', 'medium', 'high'], aviso: [true, false] },
  casos: [
    { id: 'A', grupo: 'g1', tipo: 'core', critico: true, estado: 'e', pedido: 'cor LOW', esperado: { acao: 'low' }, casa: 'x' },
    { id: 'B', grupo: 'g1', tipo: 'core', critico: false, estado: 'e', pedido: 'login', esperado: { acao: 'low' }, casa: 'x' },
    { id: 'C', grupo: 'g2', tipo: 'var', critico: false, estado: 'e', pedido: 'ERRO', esperado: { acao: 'high' }, casa: 'x' },
    { id: 'D', grupo: 'g2', tipo: 'var', critico: false, estado: 'e', pedido: 'LIXO', esperado: { acao: 'high' }, casa: 'x' },
  ],
};

function pasta(t) {
  const raiz = mkdtempSync(join(tmpdir(), 'vibeflow-bench-teste-'));
  t.after(() => rmSync(raiz, { recursive: true, force: true }));
  writeFileSync(join(raiz, 'executor-falso.mjs'), FALSO);
  writeFileSync(join(raiz, 'suite.json'), JSON.stringify(SUITE));
  writeFileSync(join(raiz, 'contexto.md'), 'REGRA-DO-CONTEXTO: só sinal concreto sobe a rota. Ação não-ASCII.');
  return raiz;
}

const CONTEXTO = [{ nome: 'contexto.md', texto: 'REGRA-DO-CONTEXTO uma duas três' }];

test('corrigir: só os campos de esperado contam, e valor fora da lista é erro', () => {
  const caso = { esperado: { acao: 'low', aviso: true } };
  assert.equal(corrigir(SUITE, caso, { acao: 'low', aviso: true, motivo: 'qualquer' }).ok, true);
  const errado = corrigir(SUITE, caso, { acao: 'low', aviso: false });
  assert.equal(errado.ok, false);
  assert.deepEqual(errado.campos.aviso, { esperado: true, obtido: false, ok: false });
  assert.equal(corrigir(SUITE, { esperado: { acao: 'low' } }, { acao: 'LOW' }).ok, false);
  assert.equal(corrigir(SUITE, { esperado: { acao: 'low' } }, null).campos.acao.obtido, null);
});

test('lerResposta: tira o JSON de dentro de cercas e separa erro do host de resposta sem JSON', () => {
  const r = lerResposta(JSON.stringify({ is_error: false, total_cost_usd: 0.5, result: 'Aqui:\n```json\n{"acao":"medium"}\n```' }));
  assert.deepEqual(r.resposta, { acao: 'medium' });
  assert.equal(r.custo, 0.5);
  assert.match(lerResposta(JSON.stringify({ is_error: true, result: 'OAuth expirou' })).erro, /OAuth/);
  assert.match(lerResposta(JSON.stringify({ result: 'sem objeto' })).erro, /sem objeto JSON/);
  assert.match(lerResposta('não é json').erro, /não é JSON/);
  const corrigida = lerResposta(JSON.stringify({ result: '{"acao":"low","x":{"y":1}}\n\nCorreção: vale high.\n\n{"acao":"high","x":{"y":2}}' }));
  assert.deepEqual(corrigida.resposta, { acao: 'high', x: { y: 2 } }, 'vale o último objeto, com objeto aninhado');
  assert.match(lerResposta(JSON.stringify({ result: '{"acao": "low", ' })).erro, /sem objeto JSON/);
  assert.match(lerResposta(JSON.stringify({ result: '{"acao": low}' })).erro, /JSON inválido/);
});

test('montarPrompt: estado, pedido e instrução fixa, nessa ordem', () => {
  const p = montarPrompt(SUITE, SUITE.casos[0]);
  assert.ok(p.indexOf('Estado do repositório: e') < p.indexOf('Pedido do humano: cor LOW'));
  assert.ok(p.endsWith('Responda em JSON.'));
});

test('rodar: filtra por tipo, isola a chamada, conta acertos e erros do executor', async (t) => {
  const raiz = pasta(t);
  const executor = join(raiz, 'executor-falso.mjs');
  const core = await rodar({ suite: SUITE, nomeSuite: 'teste', contextos: CONTEXTO, reps: 2, tipo: 'core', executor });
  assert.deepEqual(core.casos.map((c) => c.id), ['A', 'B']);
  assert.deepEqual(core.total, { acertos: 2, reps: 4, taxa: 0.5 });
  assert.deepEqual(core.criticos, { acertos: 2, reps: 2, taxa: 1 });
  assert.deepEqual(core.falhas, ['B']);
  assert.equal(core.palavrasContexto, 4);
  assert.ok(Math.abs(core.custoUsd - 0.004) < 1e-9);

  const vars = await rodar({ suite: SUITE, nomeSuite: 'teste', contextos: CONTEXTO, reps: 1, tipo: 'var', executor });
  assert.equal(vars.errosExecutor, 2);
  assert.match(vars.casos[0].respostas[0].erro, /authenticate/);
});

test('rodar: sem o contexto no prompt de sistema o executor falso recusa', async (t) => {
  const executor = join(pasta(t), 'executor-falso.mjs');
  const r = await rodar({ suite: SUITE, nomeSuite: 'teste', contextos: [{ nome: 'x', texto: 'outra coisa' }], reps: 1, executor });
  assert.equal(r.errosExecutor, 2);
});

test('resumir: caso com acerto parcial é instável', () => {
  const casos = [{ id: 'A', grupo: 'g', tipo: 'core', critico: false, casa: 'x' }];
  const ok = (v) => ({ id: 'A', resposta: { acao: 'low' }, correcao: { ok: v } });
  const r = resumir({ nomeSuite: 's', contextos: CONTEXTO, modelo: 'm', reps: 3, tipo: 'core', casos, execucoes: [ok(true), ok(false), ok(true)] });
  assert.deepEqual(r.instaveis, ['A']);
  assert.equal(r.casos[0].acertos, 2);
});

test('comparar: queda em crítico reprova, melhora sem queda aprova, e diferença de modelo avisa', () => {
  const rodada = (modelo, acertosA, acertosB, palavras) => ({
    suite: 's', modelo, palavrasContexto: palavras,
    total: { taxa: (acertosA + acertosB) / 6 },
    casos: [{ id: 'A', critico: true, acertos: acertosA, reps: 3 }, { id: 'B', critico: false, acertos: acertosB, reps: 3 }],
  });
  const queda = comparar(rodada('haiku', 3, 1, 100), rodada('haiku', 2, 3, 80));
  assert.equal(queda.aceito, false);
  assert.deepEqual(queda.quedasCriticas, ['A']);
  const melhora = comparar(rodada('haiku', 3, 1, 100), rodada('haiku', 3, 2, 80));
  assert.equal(melhora.aceito, true);
  assert.deepEqual(melhora.palavras, { base: 100, nova: 80 });
  assert.match(comparar(rodada('haiku', 3, 3, 1), rodada('sonnet', 3, 3, 1)).avisos[0], /modelos diferentes/);
});

test('CLI: erro de uso sai com 2, caso falho sai com 1 e --json escapa não-ASCII', (t) => {
  const raiz = pasta(t);
  const cli = (...args) => spawnSync(process.execPath, [SCRIPT, ...args], { cwd: raiz, encoding: 'utf8' });
  assert.equal(cli('rodar', 'suite.json').status, 2);
  assert.equal(cli('rodar', 'suite.json', '--contexto', 'contexto.md', '--reps', '0').status, 2);
  assert.equal(cli('voar').status, 2);
  assert.equal(cli('rodar', 'suite.json', '--contexto', 'contexto.md', '--casos', 'Z').status, 2);
  const so = cli('rodar', 'suite.json', '--contexto', 'contexto.md', '--reps', '1', '--executor', 'executor-falso.mjs', '--casos', 'A,C', '--json');
  assert.deepEqual(JSON.parse(so.stdout).casos.map((c) => c.id), ['A', 'C'], '--casos vale acima de --tipo');
  const r = cli('rodar', 'suite.json', '--contexto', 'contexto.md', '--reps', '1', '--executor', 'executor-falso.mjs', '--json');
  assert.equal(r.status, 1);
  assert.doesNotMatch(r.stdout, /[^\x00-\x7F]/);
  assert.deepEqual(JSON.parse(r.stdout).falhas, ['B']);
  const texto = cli('rodar', 'suite.json', '--contexto', 'contexto.md', '--reps', '1', '--executor', 'executor-falso.mjs');
  assert.match(texto.stdout, /Acerto geral: 1\/2/);
});
