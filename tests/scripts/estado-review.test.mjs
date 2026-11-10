// estado-review.test.mjs: testes de comportamento do script estado da skill vibeflow, das
// inconsistências do plan à phase fechada.
//
// Continuação de estado.test.mjs, com os mesmos artefatos mínimos: inconsistências do plan e
// da rota, linhas de review da tabela "Estado da phase" de references/disco.md, medium,
// compatibilidade com phase antiga (fechada é fechada; aberta é inconsistência), CRLF, BOM e
// CLI, --slug e --linha, e o aviso de arquivo fora do contrato na pasta do alvo (Paths).
// Rodar com: node --test

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdirSync, symlinkSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { estado } from '../../skills/vibeflow/scripts/estado.mjs';
import { repo, escrever, commit, cli, PH, spec, passo, plan, review, veredito, achados, fase } from './_apoio.mjs';

// ---------------------------------------------------------------------------
// Inconsistências do plan e da rota
// ---------------------------------------------------------------------------

test('caixa marcada sem commit do passo é inconsistência', (t) => {
  const r = estado(fase(t, [passo('1', { caixa: true })]));
  assert.ok(r.inconsistencias.some((i) => i.includes('passo 1 marcado sem commit')));
});

test('commit do passo com caixa vazia é inconsistência', (t) => {
  const r = estado(fase(t, [passo('1')], { commits: ['task(phase-1:1): a'] }));
  assert.ok(r.inconsistencias.some((i) => i.includes('passo 1 com commit e caixa vazia')));
});

test('commit de outra phase não confirma o passo com o mesmo ID', (t) => {
  const r = estado(fase(t, [passo('1', { caixa: true })], { commits: ['task(phase-2:1): outra phase'] }));
  assert.ok(r.inconsistencias.some((i) => i.includes('passo 1 marcado sem commit')));
});

test('passos irmãos com Arquivos sobrepostos e path incomparável dividindo número são inconsistência', (t) => {
  const sobrepostos = estado(fase(t, [passo('1a', { arquivos: '`src/`' }), passo('1b', { arquivos: '`src/x.js`' })]));
  assert.ok(sobrepostos.inconsistencias.some((i) => i.includes('passos irmãos 1a e 1b com Arquivos: sobrepostos')));
  const incomparavel = estado(fase(t, [passo('1a'), passo('1b', { arquivos: '`docs/relatório.md`' })]));
  assert.ok(incomparavel.inconsistencias.some((i) => i.includes('passo 1b divide o número 1 sem Arquivos: comparáveis (path incomparável)')));
});

test('numeração fora de sequência é inconsistência', (t) => {
  const r = estado(fase(t, [passo('1'), passo('3')]));
  assert.ok(r.inconsistencias.some((i) => i.includes('numeração fora de sequência no passo 3')));
});

test('spec sem # Rota: é inconsistência e a etapa fica indeterminada', (t) => {
  const raiz = repo(t);
  escrever(raiz, `${PH}/spec.md`, '# Spec: x\n# Status: rascunho\n');
  commit(raiz, 'docs: spec');
  const r = estado(raiz);
  assert.ok(r.inconsistencias.some((i) => i.includes('sem # Rota:')));
  assert.equal(r.etapa.etapa, 'indeterminado');
});

test('rota fora de medium, high e mvp e MVP sem # Risco: são inconsistência', (t) => {
  const raiz = repo(t);
  escrever(raiz, `${PH}/spec.md`, spec('rascunho', { rota: 'low' }));
  escrever(raiz, '.vibeflow/mvp/spec.md', spec('rascunho', { rota: 'mvp' }));
  commit(raiz, 'docs: specs');
  const r = estado(raiz);
  assert.ok(r.inconsistencias.some((i) => i.includes('phase-1: # Rota: low inválida')));
  assert.ok(r.inconsistencias.some((i) => i.includes('mvp: MVP sem # Risco:')));
  escrever(raiz, '.vibeflow/mvp/spec.md', spec('rascunho', { rota: 'mvp', risco: 'dados' }));
  assert.ok(!estado(raiz).inconsistencias.some((i) => i.includes('MVP sem')));
});

test('artefato que é link é inconsistência', (t) => {
  const raiz = repo(t);
  escrever(raiz, 'fora/spec.md', spec('rascunho'));
  mkdirSync(join(raiz, PH), { recursive: true });
  try { symlinkSync(join(raiz, 'fora/spec.md'), join(raiz, PH, 'spec.md')); } catch { t.skip('sistema sem permissão de symlink'); return; }
  assert.ok(estado(raiz).inconsistencias.some((i) => i.includes('é link')));
});

// ---------------------------------------------------------------------------
// Review: linhas da tabela depois dos passos
// ---------------------------------------------------------------------------

/** Phase high com o passo 1 entregue, pronta para receber um review.md. */
const entregue = (t) => fase(t, [passo('1', { caixa: true })], { commits: ['task(phase-1:1): entrega'] });

test('review com R* aberto: corrigir, pelo papel', (t) => {
  const raiz = entregue(t);
  escrever(raiz, `${PH}/review.md`, review('request-changes', achados('- [ ] R1: **Required** - `src/a.js` - x')));
  commit(raiz, 'docs: review');
  const r = estado(raiz);
  assert.equal(r.etapa.situacao, 'corrigir R*');
  assert.deepEqual(r.rAbertos, ['R1']);
});

test('request-changes com R* marcados: commitar a correção e depois re-review', (t) => {
  const raiz = entregue(t);
  escrever(raiz, `${PH}/review.md`, review('request-changes', achados('- [x] R1: **Required** - `src/a.js` - x')));
  commit(raiz, 'docs: review');
  assert.equal(estado(raiz).etapa.situacao, 'commitar a correção (R1)');
  commit(raiz, 'task(phase-1:R1): corrige a');
  assert.equal(estado(raiz).etapa.situacao, 're-review');
});

test('R* marcado cujo path está não commitado tem dono; outro path não', (t) => {
  const raiz = entregue(t);
  escrever(raiz, `${PH}/review.md`, review('request-changes', achados('- [x] R1: **Required** - `src/a.js` - x')));
  commit(raiz, 'docs: review');
  escrever(raiz, 'src/a.js', 'x');
  assert.equal(estado(raiz).etapa.situacao, 'commitar a correção (R1)');
  escrever(raiz, 'src/zzz.js', 'x');
  assert.equal(estado(raiz).etapa.etapa, 'alteração sem dono');
});

test('R* marcado com vários paths: todos têm dono; path fora da lista não', (t) => {
  const raiz = entregue(t);
  escrever(raiz, `${PH}/review.md`, review('request-changes', achados('- [x] R1: **Required** - `src/a.js`, `src/b.js` - x `y` - remédio: z')));
  commit(raiz, 'docs: review');
  escrever(raiz, 'src/a.js', 'x');
  escrever(raiz, 'src/b.js', 'x');
  assert.equal(estado(raiz).etapa.situacao, 'commitar a correção (R1)');
  escrever(raiz, 'src/zzz.js', 'x');
  assert.equal(estado(raiz).etapa.etapa, 'alteração sem dono');
});

test('registro novo em .erros-encontrados/ não vira alteração sem dono nem código a retomar', (t) => {
  // Review aberta: o registro de achado fora do recorte não muda a etapa.
  const raiz = entregue(t);
  escrever(raiz, `${PH}/review.md`, review('request-changes', achados('- [ ] R1: **Required** - `src/a.js` - x')));
  commit(raiz, 'docs: review');
  escrever(raiz, '.erros-encontrados/flake-login.md', 'x');
  const r = estado(raiz);
  assert.equal(r.etapa.etapa, 'implement');
  assert.equal(r.etapa.situacao, 'corrigir R*');
  // Passo aberto com Arquivos na raiz também não retoma por causa do registro.
  const aberta = fase(t, [passo('1', { arquivos: '`.`' })]);
  escrever(aberta, '.erros-encontrados/achado.md', 'x');
  assert.equal(estado(aberta).etapa.situacao, 'implementar o passo 1');
  // Controle: o mesmo tipo de arquivo fora dessas pastas continua sendo código.
  escrever(aberta, 'src/novo.js', 'x');
  assert.equal(estado(aberta).etapa.situacao, 'retomar o passo');
});

test('rascunho com Approve proposto: confirmar; sem veredito: retomar', (t) => {
  const raiz = entregue(t);
  escrever(raiz, `${PH}/review.md`, review('rascunho', veredito(true)));
  commit(raiz, 'docs: review');
  assert.equal(estado(raiz).etapa.situacao, 'confirmar');
  escrever(raiz, `${PH}/review.md`, review('rascunho', veredito(false).replace('[x]', '[ ]')));
  assert.equal(estado(raiz).etapa.situacao, 'retomar');
});

test('review aprovada sem R* aberto: phase fechada, 100%, e push pendente sem upstream', (t) => {
  const raiz = entregue(t);
  escrever(raiz, `${PH}/review.md`, review('aprovado', achados('- [x] R1: **Required** - `src/a.js` - x')));
  commit(raiz, 'task(phase-1:R1): corrige a');
  commit(raiz, 'chore(phase-1): finalize review');
  const nomeada = estado(raiz, 'phase-1');
  assert.equal(nomeada.etapa.etapa, 'fechada');
  assert.equal(nomeada.progresso.percentual, 100);
  assert.deepEqual(nomeada.inconsistencias, []);
  const padrao = estado(raiz);
  assert.equal(padrao.alvo, null);
  assert.equal(padrao.etapa.etapa, 'push pendente');
});

test('push adiado vale até um commit posterior da phase', (t) => {
  const raiz = repo(t);
  escrever(raiz, `${PH}/review.md`, review('aprovado', '## Finalização Git\n\n- Push adiado pelo humano: 2026-10-17\n', 'medium'));
  commit(raiz, 'chore(phase-1): finalize review');
  commit(raiz, 'chore(phase-1): push adiado');
  assert.equal(estado(raiz).etapa.etapa, 'classificar o pedido');
  commit(raiz, 'task(phase-1:R2): ajuste depois do adiamento');
  assert.equal(estado(raiz).etapa.etapa, 'push pendente');
});

// ---------------------------------------------------------------------------
// Medium
// ---------------------------------------------------------------------------

test('task(medium) sem review: review da entrega medium', (t) => {
  const raiz = repo(t);
  escrever(raiz, 'src/x.js', 'x');
  commit(raiz, 'task(medium): entrega');
  assert.equal(estado(raiz).etapa.etapa, 'review da entrega medium');
});

test('medium com review em rascunho: retomar a review, 50%, sem passos nem spec', (t) => {
  const raiz = repo(t);
  commit(raiz, 'task(medium): entrega');
  escrever(raiz, `${PH}/review.md`, review('rascunho', '', 'medium'));
  commit(raiz, 'docs: review');
  const r = estado(raiz);
  assert.equal(r.etapa.etapa, 'review');
  assert.equal(r.etapa.situacao, 'retomar');
  assert.equal(r.progresso.percentual, 50);
});

test('ajuste de phase fechada: progresso por R* de ajuste e etapa corrigir', (t) => {
  const raiz = repo(t);
  const ajuste = `## Achados\n\n- [x] R1: **Required** - \`a\` - x\n- [ ] R2: **Required** - \`src/y.js\` - ajuste\n\n## Etapas\n\n### Ajuste 1 - troca\n\n- Abriu: R2\n`;
  escrever(raiz, `${PH}/review.md`, review('aprovado', ajuste, 'medium'));
  commit(raiz, 'chore(phase-1): finalize review');
  const r = estado(raiz);
  assert.equal(r.progresso.ajuste, '0/1');
  assert.equal(r.etapa.situacao, 'corrigir R*');
});

// ---------------------------------------------------------------------------
// Compatibilidade com o formato antigo (disco.md, Compatibilidade)
// ---------------------------------------------------------------------------

const PLAN_ANTIGO = '# Plan: x\n# Status: aprovado\n\n## Tasks\n\n### T1: entrega\n- [x] T1 concluída\n- **Estado:** concluída\n- **Arquivos:** `src/a.js`\n';

test('phase antiga fechada conta como fechada, fica sem inconsistência e não atrapalha a phase nova', (t) => {
  const raiz = repo(t);
  const antiga = '.vibeflow/phases/phase-1-antiga';
  escrever(raiz, `${antiga}/interview.md`, '# Interview: x\n# Status: aprovado\n# Rota: max\n');
  escrever(raiz, `${antiga}/spec.md`, '# Spec: x\n# Status: aprovado\n');
  escrever(raiz, `${antiga}/analyze.md`, '# Analyze: x\n# Status: aprovado\n');
  escrever(raiz, `${antiga}/plan.md`, PLAN_ANTIGO);
  escrever(raiz, `${antiga}/review.md`, '# Review: x\n# Status: aprovado\n\n## Checklist de correções\n\n- [x] R1: **Required** - `src/a.js` - x\n');
  commit(raiz, 'task(phase-1:T1): entrega');
  commit(raiz, 'chore(phase-1): finalize review');
  const nomeada = estado(raiz, 'phase-1');
  assert.deepEqual(nomeada.inconsistencias, []);
  assert.deepEqual(nomeada.alvos[0], { alvo: 'phase-1', pasta: '.vibeflow/phases/phase-1-antiga', rota: null, risco: null, fechado: true, antigo: true });
  assert.equal(nomeada.etapa.etapa, 'fechada');
  assert.equal(nomeada.progresso.percentual, 100);
  // Sem phase aberta, a antiga fechada só aparece pelo push pendente, como qualquer fechada.
  assert.equal(estado(raiz).alvo, null);
  // Uma phase nova ao lado segue o contrato novo, sem herdar achado da antiga.
  escrever(raiz, '.vibeflow/phases/phase-2-nova/spec.md', spec('aprovado'));
  escrever(raiz, '.vibeflow/phases/phase-2-nova/plan.md', plan([passo('1')]));
  commit(raiz, 'docs: phase 2');
  const r = estado(raiz);
  assert.equal(r.alvo.alvo, 'phase-2');
  assert.equal(r.etapa.situacao, 'implementar o passo 1');
  assert.deepEqual(r.inconsistencias, []);
});

test('phase antiga fechada só com plan de T* e review aprovada também conta como fechada', (t) => {
  const raiz = repo(t);
  escrever(raiz, `${PH}/spec.md`, '# Spec: x\n# Status: aprovado\n# Rota: high\n');
  escrever(raiz, `${PH}/plan.md`, PLAN_ANTIGO);
  escrever(raiz, `${PH}/review.md`, '# Review: x\n# Status: aprovado\n');
  commit(raiz, 'task(phase-1:T1): entrega');
  const r = estado(raiz, 'phase-1');
  assert.equal(r.alvos[0].antigo, true);
  assert.equal(r.alvos[0].fechado, true);
  assert.deepEqual(r.inconsistencias, []);
});

for (const [nome, arquivos] of [
  ['plan com blocos de T*', { 'spec.md': '# Spec: x\n# Status: aprovado\n# Rota: high\n', 'plan.md': PLAN_ANTIGO.replace('[x]', '[ ]') }],
  ['interview.md', { 'interview.md': '# Interview: x\n# Status: rascunho\n# Rota: xhigh\n' }],
  ['rota max na spec', { 'spec.md': '# Spec: x\n# Status: aprovado\n# Rota: max\n' }],
]) {
  test(`phase antiga aberta (${nome}): inconsistência de formato antigo, sem conduzir`, (t) => {
    const raiz = repo(t);
    for (const [arq, conteudo] of Object.entries(arquivos)) escrever(raiz, `${PH}/${arq}`, conteudo);
    commit(raiz, 'docs: phase antiga');
    escrever(raiz, 'solto.js', 'x'); // alteração fora de .vibeflow/ não esconde o formato antigo
    const r = estado(raiz);
    assert.ok(r.inconsistencias.some((i) => i.includes('formato antigo aberto')));
    assert.equal(r.etapa.etapa, 'inconsistência');
    assert.equal(r.etapa.situacao, 'alvo aberto no formato antigo');
    assert.equal(r.alvo.antigo, true);
    assert.equal(r.progresso.percentual, null);
    assert.equal(cli('estado.mjs', ['--raiz', raiz]).codigo, 1);
  });
}

// ---------------------------------------------------------------------------
// CRLF, BOM e CLI
// ---------------------------------------------------------------------------

test('CRLF e BOM nos artefatos não mudam a etapa nem o progresso', (t) => {
  const raiz = repo(t);
  escrever(raiz, `${PH}/spec.md`, `﻿${spec('aprovado')}`.replace(/\n/g, '\r\n'));
  escrever(raiz, `${PH}/plan.md`, plan([passo('1', { caixa: true }), passo('2a'), passo('2b')]).replace(/\n/g, '\r\n'));
  commit(raiz, 'task(phase-1:1): entrega');
  const r = estado(raiz);
  assert.equal(r.alvo.rota, 'high');
  assert.equal(r.etapa.situacao, 'implementar o trecho 2a a 2b (2a, 2b)');
  assert.equal(r.progresso.percentual, 66); // (3 + 3 + 3 + 1) / 15
  assert.deepEqual(r.inconsistencias, []);
});

test('CLI: códigos 0, 1 e 2 e --json só com ASCII', (t) => {
  const raiz = repo(t);
  const ok = cli('estado.mjs', ['--raiz', raiz, '--json']);
  assert.equal(ok.codigo, 0);
  assert.match(ok.out, /^[\x00-\x7F]*$/);
  assert.match(ok.out, /L\\u00edder/); // "Líder" escapado
  assert.equal(JSON.parse(ok.out).etapa.etapa, 'classificar o pedido');
  assert.equal(cli('estado.mjs', ['--invalido']).codigo, 2);
  assert.equal(cli('estado.mjs', ['--raiz', raiz, '--alvo', 'phase-9']).codigo, 2);
  escrever(raiz, `${PH}/spec.md`, '# Spec: x\n# Status: rascunho\n');
  commit(raiz, 'docs: spec');
  assert.equal(cli('estado.mjs', ['--raiz', raiz]).codigo, 1);
});

test('CLI: texto com o próximo trecho e a fração de passos', (t) => {
  const raiz = fase(t, [passo('1', { caixa: true }), passo('2a'), passo('2b')], { commits: ['task(phase-1:1): entrega'] });
  const { codigo, out } = cli('estado.mjs', ['--raiz', raiz]);
  assert.equal(codigo, 0);
  assert.match(out, /progresso: 66% · etapa: implement, implementar o trecho 2a a 2b \(2a, 2b\) · passos 1\/3 marcados/);
  assert.match(out, /^passos: 2a, 2b$/m);
});

// ---------------------------------------------------------------------------
// --slug e --linha
// ---------------------------------------------------------------------------

test('--slug normaliza a frase no path da próxima phase; frase sem slug válido é erro de uso', (t) => {
  const raiz = repo(t);
  const ok = cli('estado.mjs', ['--raiz', raiz, '--slug', 'Agenda Online: v2', '--json']);
  assert.equal(ok.codigo, 0);
  assert.equal(JSON.parse(ok.out).proximaPhase, 'phase-1-agenda-online-v2');
  assert.equal(cli('estado.mjs', ['--raiz', raiz, '--slug', '!']).codigo, 2);
});

test('--linha imprime uma linha de progresso, e nada fora de um repo com .vibeflow/', (t) => {
  const raiz = fase(t, [passo('1'), passo('2')]);
  const r = cli('estado.mjs', ['--raiz', raiz, '--linha']);
  assert.equal(r.out, 'vibeflow · phase-1 · 60% · etapa: implement · próximo: Líder delega o trecho a um implementador\n');
  const vazio = repo(t);
  rmSync(join(vazio, '.vibeflow'), { recursive: true, force: true });
  assert.equal(cli('estado.mjs', ['--raiz', vazio, '--linha']).out, '');
});

// ---------------------------------------------------------------------------
// Arquivo fora do contrato na pasta do alvo (references/disco.md, Paths)
// ---------------------------------------------------------------------------

test('arquivo além de spec, plan e review na pasta do alvo é aviso, não inconsistência', (t) => {
  const raiz = fase(t, [passo('1')]);
  escrever(raiz, `${PH}/passo-1.md`, 'medição');
  escrever(raiz, `${PH}/baseline.md`, 'linha de base');
  commit(raiz, 'docs: anotações');
  const r = estado(raiz);
  assert.deepEqual(r.inconsistencias, []);
  assert.equal(r.avisos.length, 1);
  assert.match(r.avisos[0], new RegExp(`${PH}/baseline\.md, ${PH}/passo-1\.md`));
  const texto = cli('estado.mjs', ['--raiz', raiz]);
  assert.equal(texto.codigo, 0);
  assert.match(texto.out, /aviso: arquivo fora do contrato/);
});

test('pasta só com os artefatos do contrato não tem aviso de arquivo a mais', (t) => {
  const r = estado(fase(t, [passo('1')]));
  assert.equal(r.avisos, undefined);
});
