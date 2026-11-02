// conferir.test.mjs: testes de comportamento do script conferir da skill vibeflow.
//
// Modo --passo: alterações não commitadas contra os Arquivos: dos passos e os paths dos R*
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

/** Plan com `## Trabalho alheio` (antes dos Achados do analyze) com os paths dados, um por linha. */
const planComAlheio = (linhas, paths) => plan(linhas)
  .replace('\n## Achados do analyze', `\n## Trabalho alheio\n\n${paths.map((p) => `- \`${p}\``).join('\n')}\n\n## Achados do analyze`);

test('passo: path declarado em ## Trabalho alheio não é acusado nem entra nos alterados', (t) => {
  const raiz = fase(t, [passo('1')]);
  escrever(raiz, `${PH}/plan.md`, planComAlheio([passo('1')], ['docs/humano.md', 'humano/']));
  commit(raiz, 'docs: trabalho alheio');
  escrever(raiz, 'src/p1.js', 'x\n');
  escrever(raiz, 'docs/humano.md', 'x\n');
  escrever(raiz, 'humano/a.js', 'x\n');
  escrever(raiz, 'src/outro.js', 'x\n');
  const r = conferirPasso(raiz, ['1']);
  assert.deepEqual(r.achados, ['path fora do recorte: src/outro.js']);
  assert.deepEqual([...r.alterados].sort(), ['src/outro.js', 'src/p1.js']);
});

test('passo: só trabalho alheio alterado vira o aviso de nenhuma alteração, sem achado', (t) => {
  const raiz = fase(t, [passo('1')]);
  escrever(raiz, `${PH}/plan.md`, planComAlheio([passo('1')], ['docs/humano.md']));
  commit(raiz, 'docs: trabalho alheio');
  escrever(raiz, 'docs/humano.md', 'x\n');
  const r = conferirPasso(raiz, ['1']);
  assert.deepEqual(r.achados, []);
  assert.match(r.avisos[0], /^nenhuma alteração de código ou teste/);
});

test('R* de um path usa o path citado como recorte', (t) => {
  const raiz = fase(t, [passo('1', { caixa: true })]);
  escrever(raiz, `${PH}/review.md`, review('request-changes', veredito(false) + achados('- [ ] R1: `src/r.js` corrigir. papel: implementador')));
  escrever(raiz, 'src/r.js', 'x\n');
  escrever(raiz, 'src/p1.js', 'x\n');
  assert.deepEqual(conferirPasso(raiz, ['R1']).achados, ['path fora do recorte: src/p1.js']);
});

test('R* com vários paths: todos entram no recorte; o que está fora de todos é achado', (t) => {
  const raiz = fase(t, [passo('1', { caixa: true })]);
  escrever(raiz, `${PH}/review.md`, review('request-changes', veredito(false) + achados('- [ ] R1: **Required** - `src/r.js`, `src/s.js` - corrigir `x` - remédio: y - papel: implementador')));
  escrever(raiz, 'src/r.js', 'x\n');
  escrever(raiz, 'src/s.js', 'x\n');
  assert.deepEqual(conferirPasso(raiz, ['R1']).achados, []);
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

test('commit: o staging de trabalho alheio declarado continua acusado, com a marca da declaração', (t) => {
  const raiz = fase(t, [passo('1')]);
  escrever(raiz, `${PH}/plan.md`, planComAlheio([passo('1')], ['docs/humano.md']));
  commit(raiz, 'docs: trabalho alheio');
  escrever(raiz, 'src/p1.js', 'x\n');
  escrever(raiz, 'docs/humano.md', 'x\n');
  escrever(raiz, `${PH}/plan.md`, planComAlheio([passo('1', { caixa: true })], ['docs/humano.md']));
  stage(raiz, 'src/p1.js', 'docs/humano.md', `${PH}/plan.md`);
  assert.deepEqual(conferirCommit(raiz, 'task(phase-1:1): entrega 1').achados, [
    'path em staging fora do recorte: docs/humano.md (declarado em ## Trabalho alheio)',
  ]);
});

// Declaração sobreposta ao recorte de passo ou R* aberto não vale (disco.md, Plan > Trabalho alheio).
test('passo: alheio sobreposto ao recorte do passo aberto não esconde o código do passo', (t) => {
  const raiz = fase(t, [passo('1')]);
  escrever(raiz, `${PH}/plan.md`, planComAlheio([passo('1')], ['src/p1.js', 'docs/humano.md']));
  commit(raiz, 'docs: trabalho alheio');
  escrever(raiz, 'src/p1.js', 'x\n');
  escrever(raiz, 'docs/humano.md', 'x\n');
  const r = conferirPasso(raiz, ['1']);
  assert.deepEqual(r.achados, []);
  assert.deepEqual(r.alterados, ['src/p1.js']);
  assert.ok(!r.avisos.some((a) => /nenhuma alteração/.test(a)));
});

test('passo: alheio sobreposto ao path de R* aberto não esconde o código da correção', (t) => {
  const raiz = fase(t, [passo('1', { caixa: true })]);
  escrever(raiz, `${PH}/plan.md`, planComAlheio([passo('1', { caixa: true })], ['src/r.js']));
  escrever(raiz, `${PH}/review.md`, review('request-changes', veredito(false) + achados('- [ ] R1: `src/r.js` corrigir. papel: implementador')));
  commit(raiz, 'docs: alheio e R1');
  escrever(raiz, 'src/r.js', 'x\n');
  const r = conferirPasso(raiz, ['R1']);
  assert.deepEqual(r.alterados, ['src/r.js']);
  assert.deepEqual(r.achados, []);
});

test('passo: alheio sobreposto ao path de R* marcado [x] sem commit não esconde o código da correção', (t) => {
  const raiz = fase(t, [passo('1', { caixa: true })]);
  escrever(raiz, `${PH}/plan.md`, planComAlheio([passo('1', { caixa: true })], ['src/r.js']));
  escrever(raiz, `${PH}/review.md`, review('request-changes', veredito(false) + achados('- [x] R1: `src/r.js` corrigir. papel: implementador')));
  commit(raiz, 'docs: alheio e R1 marcado');
  escrever(raiz, 'src/r.js', 'x\n');
  assert.deepEqual(conferirPasso(raiz, ['R1']).alterados, ['src/r.js']);
  // Com o commit task(phase-1:R1) o R* deixa de ser aberto e a declaração volta a valer.
  commit(raiz, 'task(phase-1:R1): corrige r');
  escrever(raiz, 'src/r.js', 'y\n');
  assert.deepEqual(conferirPasso(raiz, ['R1']).alterados, []);
});

test('passo com path incomparável e comparável não tem recorte: o alheio sobreposto vale', (t) => {
  const linhas = [passo('1', { arquivos: '`src/a.js`, `/abs/solto.js`' })];
  const raiz = fase(t, linhas);
  escrever(raiz, `${PH}/plan.md`, planComAlheio(linhas, ['src/a.js']));
  commit(raiz, 'docs: trabalho alheio');
  escrever(raiz, 'src/a.js', 'x\n');
  const r = conferirPasso(raiz, ['1']);
  assert.deepEqual(r.alterados, []);
  assert.deepEqual(r.achados, []);
});

test('alheio com crase em comentário da linha declara só a lista inicial', (t) => {
  const raiz = fase(t, [passo('1', { arquivos: '`lib/p1.js`' })]);
  escrever(raiz, `${PH}/plan.md`, plan([passo('1', { arquivos: '`lib/p1.js`' })]).replace('\n## Achados do analyze', '\n## Trabalho alheio\n\n- `docs/a.md` (ver `src/`)\n\n## Achados do analyze'));
  commit(raiz, 'docs: trabalho alheio');
  escrever(raiz, 'lib/p1.js', 'x\n');
  escrever(raiz, 'docs/a.md', 'x\n');
  escrever(raiz, 'src/outro.js', 'x\n');
  const r = conferirPasso(raiz, ['1']);
  assert.deepEqual(r.alterados, ['lib/p1.js', 'src/outro.js']);
});

test('commit do passo com o path alheio declarado em staging, mesmo dentro do recorte, é acusado', (t) => {
  const raiz = fase(t, [passo('1')]);
  escrever(raiz, `${PH}/plan.md`, planComAlheio([passo('1')], ['src/p1.js']));
  commit(raiz, 'docs: trabalho alheio');
  escrever(raiz, 'src/p1.js', 'x\n');
  escrever(raiz, `${PH}/plan.md`, planComAlheio([passo('1', { caixa: true })], ['src/p1.js']));
  stage(raiz, 'src/p1.js', `${PH}/plan.md`);
  const achadosDoCommit = conferirCommit(raiz, 'task(phase-1:1): entrega 1').achados;
  assert.equal(achadosDoCommit.length, 1);
  assert.match(achadosDoCommit[0], /src\/p1\.js.*declarado em ## Trabalho alheio/);
});

test('commit: declaração sem vigência (sobreposta ao passo aberto) vale como path comum, aceito no recorte e acusado fora dele, sem a marca', (t) => {
  const linhas = (c1) => [passo('1', { caixa: c1, arquivos: '`src/a.js`' }), passo('2', { arquivos: '`src/a.js`, `src/b.js`' })];
  const raiz = fase(t, linhas(false));
  escrever(raiz, `${PH}/plan.md`, planComAlheio(linhas(false), ['src/a.js', 'src/b.js']));
  commit(raiz, 'docs: trabalho alheio sobreposto ao passo 2');
  escrever(raiz, 'src/a.js', 'x\n');
  escrever(raiz, `${PH}/plan.md`, planComAlheio(linhas(true), ['src/a.js', 'src/b.js']));
  stage(raiz, 'src/a.js', `${PH}/plan.md`);
  // O passo 2 segue aberto e cobre src/a.js: a declaração não vale, o path é código do passo 1.
  assert.deepEqual(conferirCommit(raiz, 'task(phase-1:1): entrega 1').achados, []);
  // Fora do recorte do commit (src/b.js é do passo 2), o path declarado sem vigência é acusado como comum, sem a marca.
  escrever(raiz, 'src/b.js', 'x\n');
  stage(raiz, 'src/b.js');
  assert.deepEqual(conferirCommit(raiz, 'task(phase-1:1): entrega 1').achados, ['path em staging fora do recorte: src/b.js']);
});

test('duas phases abertas: o alheio de uma não esconde o recorte da outra', (t) => {
  const raiz = fase(t, [passo('1')]);
  escrever(raiz, `${PH}/plan.md`, planComAlheio([passo('1')], ['src/p2.js']));
  escrever(raiz, '.vibeflow/phases/phase-2-nova/spec.md', spec('aprovado'));
  escrever(raiz, '.vibeflow/phases/phase-2-nova/plan.md', plan([passo('1', { arquivos: '`src/p2.js`' })]));
  commit(raiz, 'docs: phase 2 e alheio da 1');
  escrever(raiz, 'src/p2.js', 'x\n');
  const r = conferirPasso(raiz, ['1'], 'phase-2');
  assert.deepEqual(r.alterados, ['src/p2.js']);
  assert.deepEqual(r.achados, []);
  // No commit do passo da phase 2, só o alheio da própria phase 2 acusa staging.
  escrever(raiz, '.vibeflow/phases/phase-2-nova/plan.md', plan([passo('1', { caixa: true, arquivos: '`src/p2.js`' })]));
  stage(raiz, 'src/p2.js', '.vibeflow/phases/phase-2-nova/plan.md');
  assert.deepEqual(conferirCommit(raiz, 'task(phase-2:1): entrega 1').achados, []);
});

test('linha de ## Trabalho alheio com dois paths declara os dois', (t) => {
  const raiz = fase(t, [passo('1')]);
  escrever(raiz, `${PH}/plan.md`, plan([passo('1')]).replace('\n## Achados do analyze', '\n## Trabalho alheio\n\n- `docs/a.md`, `docs/b.md`\n\n## Achados do analyze'));
  commit(raiz, 'docs: trabalho alheio');
  escrever(raiz, 'src/p1.js', 'x\n');
  escrever(raiz, 'docs/a.md', 'x\n');
  escrever(raiz, 'docs/b.md', 'x\n');
  const r = conferirPasso(raiz, ['1']);
  assert.deepEqual(r.alterados, ['src/p1.js']);
  assert.deepEqual(r.achados, []);
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

test('commit de R* com vários paths aceita todos; R* antigo de um path segue aceito', (t) => {
  const raiz = fase(t, [passo('1', { caixa: true })]);
  const corpo = (marca) => review('request-changes', veredito(false) + achados(
    `- [${marca}] R1: **Required** - \`src/r.js\`, \`src/s.js\` - x \`y\` - remédio: z - papel: implementador\n- [${marca}] R2: **Nit** - \`src/t.js\` - x \`y\` - remédio: z - papel: implementador`));
  escrever(raiz, `${PH}/review.md`, corpo(' '));
  commit(raiz, 'docs: review');
  escrever(raiz, `${PH}/review.md`, corpo('x'));
  for (const p of ['src/r.js', 'src/s.js', 'src/t.js']) escrever(raiz, p, 'x\n');
  stage(raiz, 'src/r.js', 'src/s.js', `${PH}/review.md`);
  const paths = (msg) => conferirCommit(raiz, msg).achados.filter((a) => /^path/.test(a));
  assert.deepEqual(paths('task(phase-1:R1,R2): corrige'), []);
  // R* antigo de um path: o path do R2 só entra no recorte quando R2 está na mensagem.
  stage(raiz, 'src/t.js');
  assert.deepEqual(paths('task(phase-1:R1): corrige'), ['path em staging fora do recorte: src/t.js']);
  assert.deepEqual(paths('task(phase-1:R1,R2): corrige'), []);
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
