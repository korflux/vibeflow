// estado.test.mjs: testes de comportamento do script estado da skill vibeflow, da abertura ao
// implement.
//
// Cada cenário monta um repositório Git temporário com artefatos mínimos no contrato
// 5.0.0 e confere etapa, progresso e próximo passo contra a tabela "Estado da phase" de
// references/disco.md e o progresso de SKILL.md, seção 9: sem phase, spec e plan; trecho,
// grupo paralelo e checkpoint; e o trabalho alheio declarado no plan. Review, medium,
// compatibilidade, CLI e arquivo fora do contrato ficam em estado-review.test.mjs: o runner
// roda um processo por arquivo, e dois arquivos dividem o tempo do mais lento da suíte.
// Rodar com: node --test

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { estado } from '../../skills/vibeflow/scripts/estado.mjs';
import { repo, escrever, commit, PH, spec, passo, checkpoint, plan, fase } from './_apoio.mjs';

// ---------------------------------------------------------------------------
// Sem phase, spec e plan
// ---------------------------------------------------------------------------

test('sem phase: classificar o pedido e próxima phase 1', (t) => {
  const r = estado(repo(t));
  assert.equal(r.etapa.etapa, 'classificar o pedido');
  assert.equal(r.proximoN, 1);
  assert.deepEqual(r.inconsistencias, []);
});

test('pasta sem artefato: interview', (t) => {
  const raiz = repo(t);
  mkdirSync(join(raiz, PH), { recursive: true });
  const r = estado(raiz);
  assert.equal(r.etapa.etapa, 'interview');
  assert.equal(r.etapa.situacao, 'spec.md ausente');
  assert.deepEqual(r.inconsistencias, []);
});

test('spec em rascunho: etapa spec e 0%', (t) => {
  const r = estado(fase(t, null, { specStatus: 'rascunho' }));
  assert.equal(r.etapa.etapa, 'spec');
  assert.equal(r.etapa.situacao, 'aguardando ajuste ou aprovação');
  assert.equal(r.progresso.percentual, 0);
});

test('spec aprovada sem plan: etapa plan e 20%', (t) => {
  const r = estado(fase(t, null));
  assert.equal(r.etapa.etapa, 'plan');
  assert.equal(r.progresso.percentual, 20); // 1 de 5 etapas (SKILL.md, seção 9)
});

test('plan sem Achados do analyze: analyze pelo revisor, sem aprovação do plan', (t) => {
  const r = estado(fase(t, [passo('1')], { planOpts: { analisado: false } }));
  assert.equal(r.etapa.etapa, 'analyze');
  assert.equal(r.etapa.proximo, 'Revisor de contexto limpo');
  assert.equal(r.progresso.percentual, 40); // spec e plan contam; o analyze ainda não
  assert.deepEqual(r.artefatos, { spec: 'aprovado', plan: 'sem analyze' });
});

test('plan com Achados do analyze: o analyze conta e o trecho começa no primeiro passo', (t) => {
  const r = estado(fase(t, [passo('1'), passo('2')]));
  assert.equal(r.etapa.etapa, 'implement');
  assert.equal(r.etapa.situacao, 'implementar o trecho 1 a 2 (1, 2)');
  assert.deepEqual(r.etapa.passos, ['1', '2']);
  assert.equal(r.etapa.proximo, 'Líder delega o trecho a um implementador');
  assert.equal(r.progresso.percentual, 60); // spec, plan e analyze
  assert.equal(r.artefatos.plan, 'analisado');
});

test('plan analisado sem nenhum passo reconhecido: indeterminado', (t) => {
  const r = estado(fase(t, []));
  assert.equal(r.etapa.etapa, 'indeterminado');
  assert.equal(r.etapa.situacao, 'plan sem passos reconhecidos');
});

// ---------------------------------------------------------------------------
// Implement: trecho, grupo paralelo, checkpoint e progresso
// ---------------------------------------------------------------------------

test('passo pendente: o trecho vai do primeiro passo aberto ao fim e o progresso usa a fração de passos', (t) => {
  const raiz = fase(t, [passo('1', { caixa: true }), passo('2'), passo('3')], { commits: ['task(phase-1:1): entrega 1'] });
  const r = estado(raiz);
  assert.equal(r.etapa.situacao, 'implementar o trecho 2 a 3 (2, 3)');
  assert.deepEqual(r.etapa.passos, ['2', '3']);
  assert.equal(r.progresso.passos, '1/3');
  assert.equal(r.progresso.percentual, 66); // (3 + 3 + 3 + 1) / 15
  assert.deepEqual(r.inconsistencias, []);
});

test('grupo paralelo dentro do trecho: entra inteiro, com os passos seguintes', (t) => {
  const raiz = fase(t, [passo('1', { caixa: true }), passo('2a'), passo('2b'), passo('3')], { commits: ['task(phase-1:1): entrega 1'] });
  const r = estado(raiz);
  assert.equal(r.etapa.situacao, 'implementar o trecho 2a a 3 (2a, 2b, 3)');
  assert.deepEqual(r.etapa.passos, ['2a', '2b', '3']);
  assert.equal(r.progresso.percentual, 65); // (4 + 4 + 4 + 1) / 20
});

test('grupo paralelo parcial: o trecho leva só os passos ainda abertos', (t) => {
  const raiz = fase(t, [passo('1', { caixa: true }), passo('2a', { caixa: true }), passo('2b'), passo('3')], {
    commits: ['task(phase-1:1): a', 'task(phase-1:2a): b'],
  });
  const r = estado(raiz);
  assert.equal(r.etapa.situacao, 'implementar o trecho 2b a 3 (2b, 3)');
  assert.deepEqual(r.etapa.passos, ['2b', '3']);
  assert.deepEqual(r.inconsistencias, []);
});

test('o trecho para no próximo checkpoint; passo único é passo, não trecho', (t) => {
  const r = estado(fase(t, [passo('1'), passo('2'), checkpoint('A1', false, 'caminho fino'), passo('3')]));
  assert.equal(r.etapa.situacao, 'implementar o trecho 1 a 2 (1, 2)');
  assert.deepEqual(r.etapa.passos, ['1', '2']);
  const so = estado(fase(t, [passo('1', { caixa: true }), passo('2'), checkpoint('A1', false, 'caminho fino'), passo('3')], { commits: ['task(phase-1:1): a'] }));
  assert.equal(so.etapa.situacao, 'implementar o passo 2');
  assert.deepEqual(so.etapa.passos, ['2']);
});

test('checkpoint pendente: verificador de contexto limpo, com os passos e critérios cobertos', (t) => {
  const raiz = fase(t, [passo('1', { caixa: true }), passo('2a', { caixa: true }), passo('2b', { caixa: true }), checkpoint('A1, A2'), passo('3')], {
    commits: ['task(phase-1:1): a', 'task(phase-1:2a,2b): b'],
  });
  const r = estado(raiz);
  assert.equal(r.etapa.etapa, 'implement');
  assert.equal(r.etapa.situacao, 'checkpoint');
  assert.equal(r.etapa.proximo, 'Verificador de contexto limpo');
  assert.deepEqual(r.etapa.checkpoint, { aceite: ['A1', 'A2'], passos: ['1', '2a', '2b'] });
  assert.equal(r.progresso.percentual, 75); // (4 + 4 + 4 + 3) / 20: checkpoint não entra na fração
  assert.deepEqual(r.inconsistencias, []);
});

test('checkpoint marcado libera o passo seguinte; o segundo checkpoint cobre só o trecho dele', (t) => {
  const linhas = [passo('1', { caixa: true }), checkpoint('A1', true), passo('2', { caixa: true }), checkpoint('A2'), passo('3')];
  const r = estado(fase(t, linhas, { commits: ['task(phase-1:1): a', 'task(phase-1:2): b'] }));
  assert.equal(r.etapa.situacao, 'checkpoint');
  assert.deepEqual(r.etapa.checkpoint, { aceite: ['A2'], passos: ['2'] });
  const liberado = estado(fase(t, [passo('1', { caixa: true }), checkpoint('A1', true), passo('2')], { commits: ['task(phase-1:1): a'] }));
  assert.equal(liberado.etapa.situacao, 'implementar o passo 2');
});

test('todos os passos e checkpoints marcados e sem review.md: review pelo revisor', (t) => {
  const raiz = fase(t, [passo('1', { caixa: true }), passo('2', { caixa: true }), checkpoint('A1', true)], {
    commits: ['task(phase-1:1): a', 'task(phase-1:2): b'],
  });
  const r = estado(raiz);
  assert.equal(r.etapa.etapa, 'review');
  assert.equal(r.etapa.situacao, 'sem review.md');
  assert.equal(r.progresso.percentual, 80); // (2 + 2 + 2 + 2) / 10: falta só a review
  assert.deepEqual(r.inconsistencias, []);
});

test('código não commitado nos Arquivos de passo aberto: retomar o passo', (t) => {
  const raiz = fase(t, [passo('1', { arquivos: '`src/p1.js`' }), passo('2')]);
  escrever(raiz, 'src/p1.js', 'x');
  const r = estado(raiz);
  assert.equal(r.etapa.situacao, 'retomar o passo');
  assert.deepEqual(r.etapa.passos, ['1']);
});

test('path alterado não ASCII dentro de Arquivos tem dono', (t) => {
  const raiz = fase(t, [passo('1', { arquivos: '`docs/`' })]);
  escrever(raiz, 'docs/relatório.md', 'x');
  assert.equal(estado(raiz).etapa.situacao, 'retomar o passo');
});

test('alteração só em .vibeflow/ não é código: segue o passo aberto', (t) => {
  const raiz = fase(t, [passo('1')]);
  escrever(raiz, `${PH}/spec.md`, `${spec('aprovado')}\nlinha nova\n`);
  assert.equal(estado(raiz).etapa.situacao, 'implementar o passo 1');
});

test('alteração fora de qualquer passo aberto: sem dono', (t) => {
  const raiz = fase(t, [passo('1')]);
  escrever(raiz, 'solto.js', 'x');
  const r = estado(raiz);
  assert.equal(r.etapa.etapa, 'alteração sem dono');
  assert.equal(r.etapa.situacao, 'solto.js');
});

test('passo aberto sem Arquivos comparáveis é dono de qualquer path', (t) => {
  const raiz = fase(t, [passo('1', { arquivos: null })]);
  escrever(raiz, 'solto.js', 'x');
  assert.equal(estado(raiz).etapa.situacao, 'implementar o passo 1');
});

// ---------------------------------------------------------------------------
// Trabalho alheio declarado (disco.md, Plan > Trabalho alheio)
// ---------------------------------------------------------------------------

/** Phase com plan que traz `## Trabalho alheio` (antes dos Achados do analyze) com as linhas dadas. */
function faseComAlheio(t, linhasPlan, linhasAlheio) {
  const raiz = fase(t, linhasPlan);
  const secao = `\n## Trabalho alheio\n\n${linhasAlheio.join('\n')}\n\n## Achados do analyze`;
  escrever(raiz, `${PH}/plan.md`, plan(linhasPlan).replace('\n## Achados do analyze', secao));
  commit(raiz, 'docs: trabalho alheio');
  return raiz;
}

test('path declarado em ## Trabalho alheio não para a phase: segue o passo aberto', (t) => {
  const raiz = faseComAlheio(t, [passo('1')], ['- `docs/humano.md`']);
  escrever(raiz, 'docs/humano.md', 'x');
  const r = estado(raiz);
  assert.equal(r.etapa.etapa, 'implement');
  assert.equal(r.etapa.situacao, 'implementar o passo 1');
  assert.deepEqual(r.inconsistencias, []);
});

test('trabalho alheio declarado por pasta cobre o que está dentro; o resto continua sem dono', (t) => {
  const raiz = faseComAlheio(t, [passo('1')], ['- `humano/`']);
  escrever(raiz, 'humano/a/b.js', 'x');
  assert.equal(estado(raiz).etapa.situacao, 'implementar o passo 1');
  escrever(raiz, 'outro.js', 'x');
  const r = estado(raiz);
  assert.equal(r.etapa.etapa, 'alteração sem dono');
  assert.equal(r.etapa.situacao, 'outro.js');
});

test('trabalho alheio não é dono do passo: o código do passo ainda manda retomar', (t) => {
  const raiz = faseComAlheio(t, [passo('1', { arquivos: '`src/p1.js`' })], ['- `docs/humano.md`']);
  escrever(raiz, 'docs/humano.md', 'x');
  escrever(raiz, 'src/p1.js', 'x');
  const r = estado(raiz);
  assert.equal(r.etapa.situacao, 'retomar o passo');
  assert.deepEqual(r.etapa.passos, ['1']);
});

test('alheio sobreposto ao recorte do passo aberto não vale: o código do passo manda retomar', (t) => {
  const raiz = faseComAlheio(t, [passo('1', { arquivos: '`src/p1.js`' })], ['- `src/p1.js`']);
  escrever(raiz, 'src/p1.js', 'x');
  const r = estado(raiz);
  assert.equal(r.etapa.situacao, 'retomar o passo');
  assert.deepEqual(r.etapa.passos, ['1']);
});

test('alheio de pasta que contém o recorte do passo aberto também não vale', (t) => {
  const raiz = faseComAlheio(t, [passo('1', { arquivos: '`src/p1.js`' })], ['- `src/`']);
  escrever(raiz, 'src/p1.js', 'x');
  assert.equal(estado(raiz).etapa.situacao, 'retomar o passo');
});

test('duas phases abertas: o alheio de uma não esconde o recorte da outra', (t) => {
  const raiz = faseComAlheio(t, [passo('1')], ['- `src/p2.js`']);
  escrever(raiz, '.vibeflow/phases/phase-2-nova/spec.md', spec('aprovado'));
  escrever(raiz, '.vibeflow/phases/phase-2-nova/plan.md', plan([passo('1', { arquivos: '`src/p2.js`' })]));
  commit(raiz, 'docs: phase 2');
  escrever(raiz, 'src/p2.js', 'x');
  const r = estado(raiz);
  assert.equal(r.alvo.alvo, 'phase-2');
  assert.equal(r.etapa.situacao, 'retomar o passo');
});

test('linha de ## Trabalho alheio com dois paths declara os dois', (t) => {
  const raiz = faseComAlheio(t, [passo('1')], ['- `docs/a.md`, `docs/b.md`']);
  escrever(raiz, 'docs/a.md', 'x');
  escrever(raiz, 'docs/b.md', 'x');
  const r = estado(raiz);
  assert.equal(r.etapa.etapa, 'implement');
  assert.equal(r.etapa.situacao, 'implementar o passo 1');
});

test('crase em comentário da linha de ## Trabalho alheio não declara: só a lista inicial vale', (t) => {
  const raiz = faseComAlheio(t, [passo('1', { arquivos: '`lib/p1.js`' })], ['- `docs/a.md` (ver `src/`)']);
  escrever(raiz, 'docs/a.md', 'x');
  assert.equal(estado(raiz).etapa.situacao, 'implementar o passo 1');
  escrever(raiz, 'src/outro.js', 'x');
  const r = estado(raiz);
  assert.equal(r.etapa.etapa, 'alteração sem dono');
  assert.equal(r.etapa.situacao, 'src/outro.js');
});

test('comentário, raiz e path incomparável em ## Trabalho alheio não declaram nada', (t) => {
  const raiz = faseComAlheio(t, [passo('1')], ['<!-- exemplo: `solto.js` -->', '- `.`', '- `/abs/solto.js`', '- sem crase solto.js']);
  escrever(raiz, 'solto.js', 'x');
  assert.equal(estado(raiz).etapa.etapa, 'alteração sem dono');
});

test('plan sem ## Trabalho alheio mantém a linha sem dono', (t) => {
  const raiz = fase(t, [passo('1')]);
  escrever(raiz, 'docs/humano.md', 'x');
  assert.equal(estado(raiz).etapa.etapa, 'alteração sem dono');
});
