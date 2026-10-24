// conferir.test.mjs: testes de comportamento do script conferir da skill vibeflow.
//
// Modo --passo: alterações não commitadas contra os Arquivos: dos passos e o path dos R*
// (Conferência do líder de references/delegation.md). Modo --commit: mensagem nos
// formatos de references/disco.md (Commits), caixas e R* marcados no índice, paths em
// staging dentro do recorte e `git diff --cached --check` limpo. Rodar com: node --test

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { conferirPasso, conferirCommit } from '../../skills/vibeflow/scripts/conferir.mjs';
import { repo, escrever, commit, cli, PH, spec, passo, plan, review, veredito, achados } from './_apoio.mjs';

/** Phase high com spec e plan commitados e analisados; devolve a raiz. */
function fase(t, linhas) {
  const raiz = repo(t);
  escrever(raiz, `${PH}/spec.md`, spec('aprovado'));
  escrever(raiz, `${PH}/plan.md`, plan(linhas));
  commit(raiz, 'docs: spec e plan');
  return raiz;
}

/** Staging explícito, como o líder faz. */
const stage = (raiz, ...paths) => execFileSync('git', ['add', '--', ...paths], { cwd: raiz });

/** Marca as caixas dos IDs na árvore de trabalho, reescrevendo o plan com as linhas dadas. */
const marcar = (raiz, linhas) => escrever(raiz, `${PH}/plan.md`, plan(linhas));

// ---------------------------------------------------------------------------
// --passo
// ---------------------------------------------------------------------------

test('passo: alteração dentro dos Arquivos: não tem achado; .vibeflow/ e .erros-encontrados/ não contam', (t) => {
  const raiz = fase(t, [passo('1')]);
  escrever(raiz, 'src/p1.js', 'x\n');
  escrever(raiz, '.erros-encontrados/flake.md', 'x\n');
  marcar(raiz, [passo('1', { caixa: true })]);
  const r = conferirPasso(raiz, ['1']);
  assert.deepEqual(r.achados, []);
  assert.deepEqual(r.alterados, ['src/p1.js']);
});

test('passo: path fora do recorte e passo inexistente são achado', (t) => {
  const raiz = fase(t, [passo('1')]);
  escrever(raiz, 'src/p1.js', 'x\n');
  escrever(raiz, 'src/outro.js', 'x\n');
  const r = conferirPasso(raiz, ['1', '9']);
  assert.deepEqual(r.achados, ['passo 9 não existe no plan.md do alvo', 'path fora do recorte: src/outro.js']);
});

test('passo sem Arquivos: comparáveis vira aviso, sem julgar paths', (t) => {
  const raiz = fase(t, [passo('1', { arquivos: null })]);
  escrever(raiz, 'qualquer.js', 'x\n');
  const r = conferirPasso(raiz, ['1']);
  assert.deepEqual(r.achados, []);
  assert.match(r.avisos[0], /sem Arquivos: comparáveis/);
});

test('R* usa o path citado como recorte', (t) => {
  const raiz = fase(t, [passo('1', { caixa: true })]);
  escrever(raiz, `${PH}/review.md`, review('request-changes', veredito(false) + achados('- [ ] R1: `src/r.js` corrigir. papel: implementador')));
  escrever(raiz, 'src/r.js', 'x\n');
  escrever(raiz, 'src/p1.js', 'x\n');
  assert.deepEqual(conferirPasso(raiz, ['R1']).achados, ['path fora do recorte: src/p1.js']);
});

// ---------------------------------------------------------------------------
// --commit
// ---------------------------------------------------------------------------

test('commit de passo com caixa marcada no índice e paths do recorte não tem achado', (t) => {
  const raiz = fase(t, [passo('1'), passo('2')]);
  escrever(raiz, 'src/p1.js', 'x\n');
  marcar(raiz, [passo('1', { caixa: true }), passo('2')]);
  stage(raiz, 'src/p1.js', `${PH}/plan.md`);
  const r = conferirCommit(raiz, 'task(phase-1:1): entrega 1');
  assert.deepEqual(r.achados, []);
  assert.equal(r.tipo, 'task');
});

test('caixa marcada só na árvore, sem staging do plan, é achado', (t) => {
  const raiz = fase(t, [passo('1')]);
  escrever(raiz, 'src/p1.js', 'x\n');
  marcar(raiz, [passo('1', { caixa: true })]);
  stage(raiz, 'src/p1.js');
  assert.match(conferirCommit(raiz, 'task(phase-1:1): entrega 1').achados[0], /^1 citado na mensagem, mas caixa aberto no índice/);
});

test('caixa marcada no índice sem o ID na mensagem e path fora do recorte são achado', (t) => {
  const raiz = fase(t, [passo('1'), passo('2')]);
  escrever(raiz, 'src/p1.js', 'x\n');
  escrever(raiz, 'src/estranho.js', 'x\n');
  marcar(raiz, [passo('1', { caixa: true }), passo('2', { caixa: true })]);
  stage(raiz, 'src/p1.js', 'src/estranho.js', `${PH}/plan.md`);
  assert.deepEqual(conferirCommit(raiz, 'task(phase-1:1): entrega 1').achados, [
    '2 marcado no índice e ausente da mensagem',
    'path em staging fora do recorte: src/estranho.js',
  ]);
});

test('IDs fora da ordem do plan são achado; correção de passo já marcado no HEAD é aceita', (t) => {
  const raiz = fase(t, [passo('1', { caixa: true }), passo('2a'), passo('2b')]);
  escrever(raiz, 'src/p2a.js', 'x\n');
  escrever(raiz, 'src/p2b.js', 'x\n');
  escrever(raiz, 'src/p1.js', 'correção\n');
  marcar(raiz, [passo('1', { caixa: true }), passo('2a', { caixa: true }), passo('2b', { caixa: true })]);
  stage(raiz, 'src/p1.js', 'src/p2a.js', 'src/p2b.js', `${PH}/plan.md`);
  assert.deepEqual(conferirCommit(raiz, 'task(phase-1:2b,2a,1): grupo').achados, ['IDs fora da ordem do plan: esperado 1,2a,2b']);
  assert.deepEqual(conferirCommit(raiz, 'task(phase-1:1,2a,2b): grupo').achados, []);
});

test('R* citado precisa estar marcado no review.md do índice', (t) => {
  const raiz = fase(t, [passo('1', { caixa: true })]);
  const corpo = (feito) => review('request-changes', veredito(false) + achados(`- [${feito ? 'x' : ' '}] R1: \`src/r.js\` corrigir. papel: implementador`));
  escrever(raiz, `${PH}/review.md`, corpo(false));
  commit(raiz, 'docs: review');
  escrever(raiz, 'src/r.js', 'x\n');
  stage(raiz, 'src/r.js');
  assert.match(conferirCommit(raiz, 'task(phase-1:R1): corrige').achados[0], /^R1 citado na mensagem, mas R\* aberto no índice/);
  escrever(raiz, `${PH}/review.md`, corpo(true));
  stage(raiz, `${PH}/review.md`);
  assert.deepEqual(conferirCommit(raiz, 'task(phase-1:R1): corrige').achados, []);
});

test('formato, Co-Authored-By, staging vazio e espaço no fim da linha são achado', (t) => {
  const raiz = fase(t, [passo('1')]);
  const vazio = conferirCommit(raiz, 'feat: algo\n\nCo-Authored-By: x <x@x>');
  assert.deepEqual(vazio.achados, [
    'mensagem com Co-Authored-By',
    'assunto fora dos formatos de references/disco.md (Commits): feat: algo',
    'nada em staging',
  ]);
  escrever(raiz, 'src/x.js', 'x   \n');
  stage(raiz, 'src/x.js');
  assert.match(conferirCommit(raiz, 'task(low): ajuste').achados[0], /^git diff --cached --check acusou/);
});

test('entrega low ou medium não tem recorte no disco: só aviso', (t) => {
  const raiz = repo(t);
  escrever(raiz, 'src/x.js', 'x\n');
  stage(raiz, 'src/x.js');
  const r = conferirCommit(raiz, 'task(medium): entrega\n\n- A1: com horário livre, quando o cliente agenda, a reserva aparece na agenda');
  assert.deepEqual(r.achados, []);
  assert.match(r.avisos[0], /sem recorte no disco/);
  assert.deepEqual(conferirCommit(raiz, 'task(low): ajuste').achados, []);
});

test('task(medium) sem critérios no corpo, ou sem linha em branco antes dele, é achado; CRLF é aceito', (t) => {
  const raiz = repo(t);
  escrever(raiz, 'src/x.js', 'x\n');
  stage(raiz, 'src/x.js');
  const esperado = ['task(medium) sem critérios de aceite no corpo (- A1: <critério>)'];
  assert.deepEqual(conferirCommit(raiz, 'task(medium): entrega').achados, esperado);
  assert.deepEqual(conferirCommit(raiz, 'task(medium): entrega\n\nsó texto, sem critério').achados, esperado);
  assert.deepEqual(conferirCommit(raiz, 'task(medium): entrega\r\n\r\n- A1: com horário livre; quando reserva, aparece').achados, []);
  assert.deepEqual(conferirCommit(raiz, 'task(medium): entrega\n- A1: colado no assunto').achados, [
    'task(medium) sem linha em branco entre o assunto e o corpo',
    'task(medium) sem critérios de aceite no corpo (- A1: <critério>)',
  ]);
});

test('chore(init) só leva os arquivos de governança', (t) => {
  const raiz = repo(t);
  escrever(raiz, '.agents/rules/vibeflow.md', '@../../AGENTS.md\n');
  escrever(raiz, 'src/x.js', 'x\n');
  stage(raiz, '.agents/rules/vibeflow.md', 'src/x.js');
  assert.deepEqual(conferirCommit(raiz, 'chore(init): governança').achados, ['path em staging fora do recorte: src/x.js']);
});

test('finalize review aceita a pasta da phase, AGENTS.md e registros', (t) => {
  const raiz = fase(t, [passo('1', { caixa: true })]);
  escrever(raiz, `${PH}/review.md`, review('aprovado', `${veredito(true).trimEnd()}\n`)); // sem linha em branco no fim, que o --check acusaria
  escrever(raiz, 'AGENTS.md', '# Regras\n<!-- VIBEFLOW:CADEIA start -->\n<!-- VIBEFLOW:CADEIA end -->\n\n## Decisões vigentes\n');
  escrever(raiz, '.erros-encontrados/x.md', 'x\n');
  stage(raiz, `${PH}/review.md`, 'AGENTS.md', '.erros-encontrados/x.md');
  assert.deepEqual(conferirCommit(raiz, 'chore(phase-1): finalize review').achados, []);
  assert.deepEqual(conferirCommit(raiz, 'chore(phase-9): finalize review').achados, ['alvo phase-9 não existe no disco']);
});

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------

test('CLI: 0 sem achado, 1 com achado, 2 em erro de uso', (t) => {
  const raiz = fase(t, [passo('1')]);
  assert.equal(cli('conferir.mjs', ['--raiz', raiz, '--passo', '1']).codigo, 0);
  escrever(raiz, 'fora.js', 'x\n');
  const r = cli('conferir.mjs', ['--raiz', raiz, '--passo', '1', '--json']);
  assert.equal(r.codigo, 1);
  assert.deepEqual(JSON.parse(r.out).achados, ['path fora do recorte: fora.js']);
  assert.equal(cli('conferir.mjs', ['--raiz', raiz]).codigo, 2); // nenhum modo
  assert.equal(cli('conferir.mjs', ['--raiz', raiz, '--passo', '1', '--commit', 'x']).codigo, 2); // dois modos
  assert.equal(cli('conferir.mjs', ['--raiz', raiz, '--passo', '1', '--alvo', 'phase-9']).codigo, 2);
});
