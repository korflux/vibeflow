// disco.test.mjs: testes de comportamento da leitura compartilhada (_disco.mjs).
//
// Cobre as regras mecânicas de references/disco.md que os scripts aplicam: formato do
// passo e do campo Aceite:, Arquivos: (normalização, sobreposição, path incomparável,
// path real dentro do recorte), numeração e grupo paralelo, slug da phase, formato dos
// commits, reconhecimento do formato antigo e tolerância a CRLF e BOM. Os cenários de cada
// script ficam no teste dele (estado, conferir, plan e governanca). Rodar com: node --test

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdirSync } from 'node:fs';
import { join } from 'node:path';
import {
  normalizarPath, sobrepoe, lerPlan, grupos, achadosDoPlan, classificarCommit, carregarAlvos, lerLinhas,
  listarPhases, proximoN, vereditoReview, lerRs, normalizarSlug, slugValido, dentroDoRecorte, segmentos,
} from '../../skills/vibeflow/scripts/_disco.mjs';
import { repo, escrever, spec, passo, checkpoint, plan, review, veredito, achados } from './_apoio.mjs';

const passosDe = (...linhas) => lerPlan(linhas).passos;

// ---------------------------------------------------------------------------
// Arquivos: normalização e sobreposição
// ---------------------------------------------------------------------------

test('normaliza paths de Arquivos: conforme disco.md', () => {
  assert.deepEqual(normalizarPath('src/a.py'), ['src', 'a.py']);
  assert.deepEqual(normalizarPath('src/*.py'), ['src']);
  assert.deepEqual(normalizarPath('*.py'), []);
  assert.deepEqual(normalizarPath('./'), []);
  assert.deepEqual(normalizarPath(''), []);
  assert.deepEqual(normalizarPath('../x'), []);
  assert.deepEqual(normalizarPath('a/../b'), ['b']);
  assert.deepEqual(normalizarPath('a\\b'), ['a', 'b']);
  for (const p of ['C:/x', '/abs', 'ção.md', 'a./b', 'a /b', 'a|b', 'a<b', 'a"b', '\\\\srv\\x']) assert.equal(normalizarPath(p), null, p);
});

test('sobreposição por prefixo de diretório, sem distinção de maiúsculas', () => {
  assert.equal(sobrepoe(['a'], ['a', 'b']), true);
  assert.equal(sobrepoe(['a'], ['ab']), false);
  assert.equal(sobrepoe(['Src'], ['src', 'x']), true);
  assert.equal(sobrepoe([], ['qualquer']), true);
});

// ---------------------------------------------------------------------------
// Plan: passos, checkpoints e achados do analyze
// ---------------------------------------------------------------------------

test('lê o passo: ID com letra, caixa e só os paths entre Arquivos: e Prova:', () => {
  const r = lerPlan([
    '- [x] 1: ajusta `cabecalho` · Aceite: A1 · Arquivos: `src/a.js`, `tests/a.test.js` · Prova: `node --test tests/a.test.js`',
    '- [ ] 2a: x · Aceite: nenhum · Arquivos: `src/b/` · Prova: ok',
    '- [ ] 2b: y · Aceite: A2 · Prova: `fora.js`',
    '- [ ] 3: corrige Arquivos: `fantasma.js` · Aceite: A1 · Arquivos: `src/c.js` · Prova: p',
    '- [X] 4: maiúscula · Aceite: A1 · Arquivos: `src/d.js` · Prova: p',
    '- [ ] R1: **Required** - `src/r.js` - fora do plan',
    '- [ ] T1 concluída',
    '- [ ] Checkpoint: A1, A2',
  ]);
  assert.deepEqual(r.passos.map((p) => [p.id, p.num, p.letra, p.caixa]), [['1', 1, null, true], ['2a', 2, 'a', false], ['2b', 2, 'b', false], ['3', 3, null, false], ['4', 4, null, true]]);
  assert.deepEqual(r.passos[0].arquivos, ['src/a.js', 'tests/a.test.js']);
  assert.deepEqual(r.passos[1].arquivos, ['src/b/']);
  assert.equal(r.passos[2].arquivos, null);
  assert.deepEqual(r.passos[3].arquivos, ['src/c.js']);
  assert.deepEqual(r.itens.filter((i) => i.tipo === 'checkpoint'), [{ tipo: 'checkpoint', caixa: false, aceite: ['A1', 'A2'] }]);
  assert.equal(r.analisado, false);
});

test('a seção Achados do analyze marca o analyze como rodado, com ou sem achado', () => {
  assert.equal(lerPlan(plan([passo('1')], { analisado: false }).split('\n')).analisado, false);
  assert.equal(lerPlan(plan([passo('1')]).split('\n')).analisado, true);
  assert.equal(lerPlan(['## Achados do analyze', '', '| Achado | Onde | Ajuste |']).analisado, true);
});

test('agrupa passos por número: passo sozinho e grupo paralelo', () => {
  const gs = grupos(passosDe(passo('1'), passo('2a'), passo('2b'), passo('3')));
  assert.deepEqual(gs.map((g) => [g.num, g.passos.map((p) => p.id)]), [[1, ['1']], [2, ['2a', '2b']], [3, ['3']]]);
});

test('plan bem formado não tem achado', () => {
  assert.deepEqual(achadosDoPlan(passosDe(passo('1'), passo('2a', { arquivos: '`src/a/`' }), passo('2b', { arquivos: '`src/b/`' }), passo('3'))), []);
});

test('passos irmãos com Arquivos: sobrepostos são achado', () => {
  const a = achadosDoPlan(passosDe(passo('1a', { arquivos: '`src/`' }), passo('1b', { arquivos: '`src/x.js`' }), passo('1c', { arquivos: '`lib/`' })));
  assert.deepEqual(a, ['passos irmãos 1a e 1b com Arquivos: sobrepostos']);
  // Curinga e raiz valem como prefixo de diretório e como a raiz inteira.
  assert.equal(achadosDoPlan(passosDe(passo('1a', { arquivos: '`src/*.js`' }), passo('1b', { arquivos: '`src/x/y.js`' }))).length, 1);
  assert.equal(achadosDoPlan(passosDe(passo('1a', { arquivos: '`.`' }), passo('1b', { arquivos: '`qualquer.js`' }))).length, 1);
});

test('passo sem Arquivos ou com path incomparável não divide número', () => {
  assert.deepEqual(achadosDoPlan(passosDe(passo('1a', { arquivos: null }), passo('1b'))), ['passo 1a divide o número 1 sem Arquivos: comparáveis (campo ausente)']);
  assert.deepEqual(achadosDoPlan(passosDe(passo('1a'), passo('1b', { arquivos: '`docs/relatório.md`' }))), ['passo 1b divide o número 1 sem Arquivos: comparáveis (path incomparável)']);
  // Sozinho, o mesmo passo é válido.
  assert.deepEqual(achadosDoPlan(passosDe(passo('1', { arquivos: null }), passo('2', { arquivos: '`docs/relatório.md`' }))), []);
});

test('numeração fora de sequência e letras fora do padrão são achado', () => {
  assert.deepEqual(achadosDoPlan(passosDe(passo('1'), passo('3'))), ['numeração fora de sequência no passo 3 (esperado 2)']);
  assert.deepEqual(achadosDoPlan(passosDe(passo('2'))), ['numeração fora de sequência no passo 2 (esperado 1)']);
  assert.match(achadosDoPlan(passosDe(passo('1a')))[0], /IDs do passo 1 fora do padrão: 1a \(esperado 1\)/);
  assert.match(achadosDoPlan(passosDe(passo('1a'), passo('1c')))[0], /fora do padrão: 1a, 1c \(esperado 1a, 1b\)/);
  assert.match(achadosDoPlan(passosDe(passo('1', { arquivos: '`a/`' }), passo('1', { arquivos: '`b/`' })))[0], /fora do padrão: 1, 1 \(esperado 1a, 1b\)/);
  // Mesmo número em dois trechos do arquivo: o segundo trecho (1b) quebra a sequência,
  // esperada como 3, e cada trecho sozinho tem letra em passo sem irmão (esperado 1).
  assert.deepEqual(achadosDoPlan(passosDe(passo('1a'), passo('2'), passo('1b'))), [
    'numeração fora de sequência no passo 1b (esperado 3)',
    'IDs do passo 1 fora do padrão: 1a (esperado 1)',
    'IDs do passo 1 fora do padrão: 1b (esperado 1)',
  ]);
});

// ---------------------------------------------------------------------------
// Review: R* e veredito
// ---------------------------------------------------------------------------

test('lê os R* com marcação e o path citado', () => {
  const rs = lerRs(['- [x] R1: **Critical** - `src/a.js` - x', '- [ ] R2: **Nit** - sem path', '- [ ] Checkpoint: A1']);
  assert.deepEqual(rs, [{ id: 'R1', num: 1, feito: true, path: 'src/a.js' }, { id: 'R2', num: 2, feito: false, path: null }]);
});

test('o veredito marcado é lido do review.md inteiro', () => {
  assert.equal(vereditoReview(review('rascunho', veredito(true)).split('\n')), 'approve');
  assert.equal(vereditoReview(review('rascunho', veredito(false)).split('\n')), 'request-changes');
  assert.equal(vereditoReview(review('rascunho', achados('- [ ] R1: **Required** - `a` - x')).split('\n')), null);
});

// ---------------------------------------------------------------------------
// Commits (disco.md, Commits)
// ---------------------------------------------------------------------------

test('classifica os formatos de commit do contrato', () => {
  assert.deepEqual(classificarCommit('task(phase-4:2a,2b): x'), { tipo: 'task', alvo: 'phase-4', ids: ['2a', '2b'] });
  assert.deepEqual(classificarCommit('task(mvp:R1, R2): x'), { tipo: 'task', alvo: 'mvp', ids: ['R1', 'R2'] });
  assert.deepEqual(classificarCommit('task(medium): x'), { tipo: 'medium', alvo: null, ids: [] });
  assert.deepEqual(classificarCommit('task(low): x'), { tipo: 'low', alvo: null, ids: [] });
  assert.deepEqual(classificarCommit('chore(phase-2): finalize review'), { tipo: 'finalize', alvo: 'phase-2', ids: [] });
  assert.deepEqual(classificarCommit('chore(mvp): push adiado'), { tipo: 'push-adiado', alvo: 'mvp', ids: [] });
  // Fora do contrato de alvo: commit de governança do init não pertence a nenhuma phase,
  // e task(express) deixou de existir.
  for (const fora of ['chore(init): governança do init', 'task(express): x', 'task(phase-4): sem ids', 'docs: x', 'task(phase-0:1): zero']) assert.equal(classificarCommit(fora), null, fora);
});

// ---------------------------------------------------------------------------
// Alvos: ordem das phases e formato antigo (disco.md, Compatibilidade)
// ---------------------------------------------------------------------------

test('phases em ordem numérica e próximo n; pasta fora do padrão não conta', (t) => {
  const raiz = repo(t);
  for (const nome of ['phase-9-aa', 'phase-10-bb', 'phase-2-cc', 'phase-03-zero', 'phase-4-x', 'rascunho']) mkdirSync(join(raiz, '.vibeflow/phases', nome), { recursive: true });
  const phases = listarPhases(raiz);
  assert.deepEqual(phases.map((p) => p.n), [2, 9, 10]);
  assert.equal(proximoN(phases), 11);
  assert.equal(proximoN([]), 1);
});

test('reconhece o formato antigo por T*, por artefato antigo e por rota xhigh ou max', (t) => {
  const raiz = repo(t);
  const antigo = '.vibeflow/phases/phase-%-xx';
  const em = (n, arq, conteudo) => escrever(raiz, `${antigo.replace('%', n)}/${arq}`, conteudo);
  em(1, 'plan.md', '# Plan: x\n\n## Tasks\n\n### T1: entrega\n- [ ] T1 concluída\n');
  em(2, 'interview.md', '# Interview: x\n# Status: aprovado\n');
  em(3, 'analyze.md', '# Analyze: x\n');
  em(4, 'spec.md', spec('aprovado', { rota: 'max' }));
  em(5, 'design.md', '# Design: x\n');
  em(6, 'spec.md', spec('aprovado', { rota: 'xhigh' }));
  em(7, 'spec.md', spec('aprovado'));
  em(7, 'plan.md', plan([passo('1')]));
  em(8, 'review.md', review('aprovado', '', 'medium'));
  const alvos = carregarAlvos(raiz);
  assert.deepEqual(alvos.map((a) => [a.alvo, a.antigo]), [['phase-1', true], ['phase-2', true], ['phase-3', true], ['phase-4', true], ['phase-5', true], ['phase-6', true], ['phase-7', false], ['phase-8', false]]);
  assert.equal(alvos[6].rota, 'high');
  assert.equal(alvos[7].fechado, true);
});

test('lê rota e risco da spec e a rota do review.md em medium', (t) => {
  const raiz = repo(t);
  escrever(raiz, '.vibeflow/phases/phase-1-aa/spec.md', spec('rascunho', { risco: 'pagamento' }));
  escrever(raiz, '.vibeflow/phases/phase-2-bb/review.md', review('rascunho', '', 'medium'));
  escrever(raiz, '.vibeflow/mvp/spec.md', spec('rascunho', { rota: 'mvp', risco: 'dados' }));
  const [mvp, a, b] = carregarAlvos(raiz);
  assert.deepEqual([mvp.alvo, mvp.rota, mvp.risco], ['mvp', 'mvp', 'dados']);
  assert.deepEqual([a.rota, a.risco], ['high', 'pagamento']);
  assert.deepEqual([b.rota, b.risco], ['medium', null]);
});

// ---------------------------------------------------------------------------
// CRLF e BOM
// ---------------------------------------------------------------------------

test('CRLF e BOM são lidos como LF no cabeçalho e no plan', (t) => {
  const raiz = repo(t);
  escrever(raiz, '.vibeflow/phases/phase-1-aa/spec.md', `\uFEFF${spec('aprovado', { risco: 'dados' })}`.replace(/\n/g, '\r\n'));
  escrever(raiz, '.vibeflow/phases/phase-1-aa/plan.md', `\uFEFF${plan([passo('1', { caixa: true }), passo('2a'), passo('2b'), checkpoint('A1, A2')])}`.replace(/\n/g, '\r\n'));
  const [a] = carregarAlvos(raiz);
  assert.deepEqual([a.rota, a.risco], ['high', 'dados']);
  const p = lerPlan(a.art.plan);
  assert.equal(p.analisado, true);
  assert.deepEqual(p.passos.map((x) => x.id), ['1', '2a', '2b']);
  assert.deepEqual(p.passos[0].arquivos, ['src/p1.js', 'tests/p1.test.js']);
  assert.deepEqual(p.itens[3].aceite, ['A1', 'A2']);
  assert.ok(lerLinhas(join(raiz, 'nao-existe.md')) === null);
});

// ---------------------------------------------------------------------------
// Slug, Aceite: e recorte de path real
// ---------------------------------------------------------------------------

test('slug a partir da frase: minúsculas, sem acento, hífen simples e pontas limpas', () => {
  assert.equal(normalizarSlug('  Conferência do Líder: scripts!! '), 'conferencia-do-lider-scripts');
  assert.equal(normalizarSlug('API -- v2'), 'api-v2');
  assert.ok(slugValido(normalizarSlug('Agenda online')));
  assert.equal(slugValido(normalizarSlug('é')), false); // 1 caractere
  assert.equal(slugValido(normalizarSlug('x'.repeat(49))), false); // não corta: recusa
});

test('lê o Aceite: do passo, com A* ou nenhum', () => {
  const [a, b, c] = passosDe(passo('1', { aceite: 'A1, A3' }), passo('2', { aceite: 'nenhum', arquivos: null }), '- [ ] 3: sem campos');
  assert.deepEqual(a.aceite, { bruto: 'A1, A3', ids: ['A1', 'A3'] });
  assert.deepEqual(b.aceite, { bruto: 'nenhum', ids: [] });
  assert.equal(c.aceite, null);
});

test('path real dentro do recorte só quando o recorte é ele ou um diretório acima', () => {
  const rec = [normalizarPath('src/a'), normalizarPath('tests/a.test.js')];
  assert.equal(dentroDoRecorte(segmentos('src/a/b.js'), rec), true);
  assert.equal(dentroDoRecorte(segmentos('tests/a.test.js'), rec), true);
  assert.equal(dentroDoRecorte(segmentos('src/ab.js'), rec), false);
  assert.equal(dentroDoRecorte(segmentos('src'), rec), false); // o recorte é mais estreito que o path
});
