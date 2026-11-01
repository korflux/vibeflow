// plan.test.mjs: testes de comportamento do script plan da skill vibeflow.
//
// Confere a parte mecânica do plan.md contra references/disco.md (Plan) e a cobertura dos
// critérios da spec (references/analyze/coverage.md): forma do passo e do checkpoint,
// critérios inexistentes ou sem passo, seções obrigatórias e placeholder de template
// esquecido, além dos limites de tamanho do plan (teto de 12 entradas de código por passo,
// no máximo dois checkpoints e nenhum em plan de até 5 passos). Com --spec, confere a forma
// da spec em rascunho, inclusive o valor sem origem em Decisões e Critérios de aceite.
// Rodar com: node --test

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { conferirPlan, conferirSpec } from '../../skills/vibeflow/scripts/plan.mjs';
import { repo, escrever, cli, PH, passo, checkpoint, plan } from './_apoio.mjs';

/** spec.md com os critérios dados na seção `## Critérios de aceite`. */
const specCom = (criterios, extra = '') =>
  `# Spec: agenda\n# Alvo: phase-1-agenda\n# Status: aprovado\n# Rota: high\n\n## Objetivo\n\nx${extra}\n\n## Critérios de aceite\n\n${criterios.map((a) => `- ${a}: resultado ${a}`).join('\n')}\n`;

/** Campo `Arquivos:` com `codigo` paths de código e `testes` paths de teste, cada um entre crases. */
const arquivosDe = (codigo, testes = 0) => [
  ...Array.from({ length: codigo }, (_, i) => `\`src/f${i}.js\``),
  ...Array.from({ length: testes }, (_, i) => `\`tests/f${i}.test.js\``),
].join(', ');

/** Passos de `de` a `ate`, sem critério, para o plan ter o tamanho que o teste precisa. */
const semAceite = (de, ate) => Array.from({ length: ate - de + 1 }, (_, i) => passo(String(de + i), { aceite: 'nenhum' }));

function fase(t, linhas, { criterios = ['A1'], planTexto, extraSpec } = {}) {
  const raiz = repo(t);
  escrever(raiz, `${PH}/spec.md`, specCom(criterios, extraSpec));
  escrever(raiz, `${PH}/plan.md`, planTexto ?? plan(linhas));
  return raiz;
}

// Seis passos, e não três: o contrato da phase-6 proíbe checkpoint em plan de até 5 passos (A7).
test('plan bem formado, com checkpoint e todos os critérios cobertos, não tem achado', (t) => {
  const r = conferirPlan(fase(t, [passo('1', { aceite: 'A1' }), passo('2a', { aceite: 'A2' }), passo('2b', { aceite: 'nenhum' }), checkpoint('A1, A2'), ...semAceite(3, 5)], { criterios: ['A1', 'A2'] }));
  assert.deepEqual(r.achados, []);
  assert.deepEqual([r.passos, r.checkpoints], [6, 1]);
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

// Os passos 2 a 6 completam o plan até 6 passos, depois dos dois checkpoints, para que o
// teto de checkpoints (A6) e a regra de plan de até 5 passos (A7) não somem achados aqui.
test('checkpoint no início, com critério que o trecho não entrega, e linha estranha em Passos', (t) => {
  const r = conferirPlan(fase(t, [checkpoint('A1'), passo('1', { aceite: 'A1' }), checkpoint('A2'), ...semAceite(2, 6), 'texto solto'], { criterios: ['A1', 'A2'] }));
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

// ---------------------------------------------------------------------------
// --spec: forma da spec antes da aprovação (references/spec.md, Fechar)
// ---------------------------------------------------------------------------

/**
 * spec.md completa, com as seções do template; `trocas` substitui trechos para montar o defeito.
 * Os critérios trazem "10h", valor com unidade que a spec em rascunho precisa marcar com
 * origem (humano), por isso as duas linhas dizem `(origem: humano)`.
 */
const specCompleta = (trocas = {}) => {
  const partes = {
    decisoes: '1. Reserva sem login. Pergunta: exige conta? Motivo: reduz atrito.',
    criterios: '- A1: com 10h livre; quando o cliente reserva 10h, a reserva aparece na agenda (origem: humano)\n- A2: com 10h ocupado; quando outro cliente reserva 10h, vê "horário indisponível" (origem: humano)',
    fora: '- Pagamento online: phase própria',
    ...trocas,
  };
  return `# Spec: agenda\n# Alvo: phase-1-agenda\n# Status: rascunho\n# Rota: high\n\n## Objetivo\n\nx\n\n## Pontos do projeto\n\n- \`src/agenda.js\`: muda\n\n## Decisões\n\n${partes.decisoes}\n\n## Critérios de aceite\n\n${partes.criterios}\n\n## Fora do escopo\n\n${partes.fora}\n`;
};

function faseSpec(t, texto) {
  const raiz = repo(t);
  escrever(raiz, `${PH}/spec.md`, texto);
  return raiz;
}

test('--spec: spec completa, sem plan.md, não tem achado', (t) => {
  const r = conferirSpec(faseSpec(t, specCompleta()));
  assert.deepEqual(r.achados, []);
  assert.deepEqual(r.criterios, ['A1', 'A2']);
});

test('--spec: seção ausente, decisão sem pergunta ou motivo e critério repetido são achado', (t) => {
  const texto = specCompleta({
    decisoes: '1. Reserva sem login. Motivo: reduz atrito.\n2. Fuso de Brasília. Pergunta: qual fuso?',
    criterios: '- A1: com 10h livre; quando reserva, aparece (origem: humano)\n- A1: de novo',
  }).replace('## Fora do escopo', '## Outra');
  assert.deepEqual(conferirSpec(faseSpec(t, texto)).achados, [
    'spec sem a seção ## Fora do escopo',
    'decisão 1: sem Pergunta:',
    'decisão 2: sem Motivo:',
    'spec com o critério A1 repetido',
  ]);
});

test('--spec: adjetivo vago no critério é achado, salvo entre crases e fora dos critérios', (t) => {
  const texto = specCompleta({
    criterios: '- A1: a agenda carrega Rápido e de forma intuitiva\n- A2: o campo `corretamente` aparece no formulário\n- A3: o rapidinho continua igual',
    fora: '- Tela bonita: phase própria',
  });
  assert.deepEqual(conferirSpec(faseSpec(t, texto)).achados, [
    'critério A1: adjetivo vago (rápido, intuitiva); diga o resultado observável',
  ]);
});

test('--spec: placeholder do template esquecido é achado', (t) => {
  const r = conferirSpec(faseSpec(t, specCompleta({ criterios: '- A1: <contexto ou estado>; quando <ação ou evento>, <resultado observável>' })));
  assert.equal(r.achados.length, 3);
  assert.match(r.achados[0], /placeholder <contexto ou estado>/);
});

test('CLI --spec: 0 sem achado, 1 com achado, 2 sem spec', (t) => {
  const raiz = faseSpec(t, specCompleta());
  assert.equal(cli('plan.mjs', ['--spec', '--raiz', raiz]).codigo, 0);
  escrever(raiz, `${PH}/spec.md`, specCompleta({ criterios: '- A1: resposta rápida' }));
  const r = cli('plan.mjs', ['--spec', '--raiz', raiz, '--json']);
  assert.equal(r.codigo, 1);
  assert.match(JSON.parse(r.out).achados[0], /^critério A1: adjetivo vago \(rápida\)/);
  assert.equal(cli('plan.mjs', ['--spec', '--raiz', repo(t)]).codigo, 2);
});

test('--spec: texto entre aspas não é vago; palavra sem acento, em NFD ou com CRLF é', (t) => {
  const texto = specCompleta({
    criterios: '- A1: com senha curta; quando envia, vê "Escolha uma senha mais robusta" e “Use algo fácil de lembrar”\n- A2: a busca responde rapida\n- A3: o menu fica intuitivo e a lista rápida',
  }).replace(/\n/g, '\r\n');
  assert.deepEqual(conferirSpec(faseSpec(t, texto)).achados, [
    'critério A2: adjetivo vago (rapida); diga o resultado observável',
    'critério A3: adjetivo vago (intuitivo, rápida); diga o resultado observável',
  ]);
});

// ---------------------------------------------------------------------------
// --spec: valor sem origem (decisão 3 da phase-6; critérios A1 a A3)
// ---------------------------------------------------------------------------

// Dica que o achado de valor sem origem traz: o marcador explícito, não a palavra solta.
const DICA = 'marque na linha (origem: humano), (origem: assumida) ou (origem: verificado (<fonte>))';

test('--spec: valor sem origem em decisão e em critério de spec em rascunho é achado (A1)', (t) => {
  const texto = specCompleta({
    decisoes: '1. Retenção de 48 horas. Pergunta: por quanto tempo guardar? Motivo: reduz custo.\n2. Reserva sem login. Pergunta: exige conta? Motivo: reduz atrito.',
    criterios: '- A1: com 10 tentativas erradas; quando tenta de novo, a conta bloqueia\n- A2: com a senha válida; quando entra, vê a agenda',
  });
  assert.deepEqual(conferirSpec(faseSpec(t, texto)).achados, [
    `decisão 1: valor sem origem (48 horas); ${DICA}`,
    `critério A1: valor sem origem (10 tentativas); ${DICA}`,
  ]);
});

test('--spec: valor é número com unidade, prazo ou limite; ID, número de decisão e faixa de IDs não são (A1)', (t) => {
  const valores = ['48 horas', '10 tentativas', '5 anos', '64 KiB', 'R$ 19,90', '8 a 128 caracteres', '30s', '95%'];
  for (const v of valores) {
    const r = conferirSpec(faseSpec(t, specCompleta({ criterios: `- A1: o limite é ${v}` })));
    assert.equal(r.achados.length, 1, `${v} deveria pedir origem`);
    assert.match(r.achados[0], /^critério A1: valor sem origem \(/);
  }
  const semValor = specCompleta({
    decisoes: '1. Vale a AUTH-01 e a decisão 3, como em R2 e nos critérios A1 a A7. Pergunta: qual regra? Motivo: coerência.',
    criterios: '- A1: conforme AUTH-01 e A2 a A4, a lista mostra 3 colunas e a versão 5.4.0 do 2o item',
  });
  assert.deepEqual(conferirSpec(faseSpec(t, semValor)).achados, []);
});

test('--spec: marcador (origem: verificado (fonte), humano ou assumida) na mesma linha tira o achado (A2)', (t) => {
  const texto = specCompleta({
    decisoes: '1. Retenção de 48 horas (origem: verificado (docs do gateway)). Pergunta: por quanto tempo guardar? Motivo: reduz custo.\n2. Convite expira em 7 dias (origem: humano). Pergunta: quando expira? Motivo: preferência.\n3. Fila de 500 itens (origem: assumida). Pergunta: qual o tamanho? Motivo: tamanho típico.',
    criterios: '- A1: com 10 tentativas erradas; quando tenta de novo, a conta bloqueia (origem: humano)\n- A2: com a fila cheia; quando entra o 501o item, vê o limite de 500 itens (origem: assumida)',
  });
  assert.deepEqual(conferirSpec(faseSpec(t, texto)).achados, []);
  // O mesmo texto sem nenhum marcador acusa as cinco linhas, o que prova que o marcador é o que tira o achado.
  const semMarcas = texto
    .replace(' (origem: verificado (docs do gateway))', '')
    .replace(/ \(origem: (?:humano|assumida)\)/g, '');
  assert.equal(conferirSpec(faseSpec(t, semMarcas)).achados.length, 5);
});

// A marca explícita é o único reconhecimento de origem: palavra solta na linha (como "pedido do
// humano" no Motivo) não vale, porque zerava o achado de qualquer valor da linha.
test('--spec: palavra solta humano, assumida ou verificado não é origem; só o marcador explícito com fonte (A2)', (t) => {
  const invalidos = [
    'Motivo: pedido do humano',
    'Motivo: assumida',
    'Motivo: verificado (docs do gateway)',
    'origem: humano',
    '(origem: verificado ())',
    '(origem: verificado)',
    '(origem: verificado (<fonte>))',
    '(origem: talvez)',
  ];
  for (const marca of invalidos) {
    const r = conferirSpec(faseSpec(t, specCompleta({ criterios: `- A1: a retenção dura 48 horas; ${marca}` })));
    assert.equal(r.achados.length, 1, `${marca} não deveria valer como origem`);
    assert.match(r.achados[0], /^critério A1: valor sem origem \(48 horas\)/);
  }
  const validos = ['(origem: humano)', '(origem: assumida)', '(origem: verificado (docs do gateway))', '(origem: verificado docs do gateway)', '(Origem: Humano)'];
  for (const marca of validos) {
    const r = conferirSpec(faseSpec(t, specCompleta({ criterios: `- A1: a retenção dura 48 horas ${marca}` })));
    assert.deepEqual(r.achados, [], `${marca} deveria valer como origem`);
  }
  // Mesma regra na decisão: "Motivo: pedido do humano" com valor sem marcador gera achado.
  const decisao = specCompleta({ decisoes: '1. Retenção de 48 horas. Pergunta: por quanto tempo guardar? Motivo: pedido do humano.' });
  assert.deepEqual(conferirSpec(faseSpec(t, decisao)).achados, [`decisão 1: valor sem origem (48 horas); ${DICA}`]);
});

// A marca vale para a linha inteira; a limitação está documentada em `ponytail:` no script.
test('--spec: linha com dois valores e um marcador não tem achado (a marca vale para a linha)', (t) => {
  const r = conferirSpec(faseSpec(t, specCompleta({ criterios: '- A1: com 10 tentativas e 48 horas de bloqueio (origem: humano)' })));
  assert.deepEqual(r.achados, []);
});

test('--spec: valor sem origem em linha de tabela de exemplos ou em spec aprovada não é achado (A3)', (t) => {
  const tabela = specCompleta({
    criterios: '- A1: a senha segue a tabela\n\n| entrada | resultado |\n|---|---|\n| 8 caracteres | aceita |\n| 7 caracteres | recusa |',
  });
  assert.deepEqual(conferirSpec(faseSpec(t, tabela)).achados, []);
  const aprovada = specCompleta({
    decisoes: '1. Retenção de 48 horas. Pergunta: por quanto tempo guardar? Motivo: reduz custo.',
    criterios: '- A1: com 10 tentativas erradas; quando tenta de novo, a conta bloqueia',
  }).replace('# Status: rascunho', '# Status: aprovado');
  assert.deepEqual(conferirSpec(faseSpec(t, aprovada)).achados, []);
});

test('CLI --spec: valor sem origem sai com 1 e a marca de origem sai com 0 (A1 e A2)', (t) => {
  const raiz = faseSpec(t, specCompleta({ criterios: '- A1: a retenção dura 48 horas' }));
  const r = cli('plan.mjs', ['--spec', '--raiz', raiz, '--json']);
  assert.equal(r.codigo, 1);
  assert.match(JSON.parse(r.out).achados[0], /^critério A1: valor sem origem \(48 horas\)/);
  escrever(raiz, `${PH}/spec.md`, specCompleta({ criterios: '- A1: a retenção dura 48 horas (origem: humano)' }));
  assert.equal(cli('plan.mjs', ['--spec', '--raiz', raiz]).codigo, 0);
});

// ---------------------------------------------------------------------------
// Limites de tamanho do plan (decisões 5, 6 e 13; critérios A4 a A7)
// ---------------------------------------------------------------------------

test('passo com 13 entradas de código em Arquivos: está acima do teto (A4)', (t) => {
  // O 13º path parece teste pelo nome da pasta (`latest`), mas não é: teste é só path com segmento `tests`, `test`
  // ou `__tests__`, ou com nome `.test.` ou `.spec.`.
  const r = conferirPlan(fase(t, [passo('1', { arquivos: `${arquivosDe(12)}, \`src/latest/atual.js\`` })]));
  assert.deepEqual(r.achados, ['passo 1: 13 entradas de código em Arquivos:, acima do teto de 12; divida o passo pelo resultado verificável']);
});

test('passo com 12 entradas de código e testes a mais não tem achado de teto (A5)', (t) => {
  // 11 arquivos e 1 pasta somam 12 entradas de código (a pasta conta uma); os cinco testes não contam.
  const testes = '`test/b.js`, `src/__tests__/c.js`, `src/d.spec.ts`, `src/e.test.ts`, `tests/scripts/`';
  const r = conferirPlan(fase(t, [passo('1', { arquivos: `${arquivosDe(11)}, \`src/ui/\`, ${testes}` })]));
  assert.deepEqual(r.achados, []);
  const so12 = conferirPlan(fase(t, [passo('1', { arquivos: arquivosDe(12, 3) })]));
  assert.deepEqual(so12.achados, []);
});

test('mais de dois checkpoints é achado; dois não (A6)', (t) => {
  const tres = [
    passo('1', { aceite: 'A1' }), checkpoint('A1'),
    passo('2', { aceite: 'A2' }), checkpoint('A2'),
    passo('3', { aceite: 'A3' }), checkpoint('A3'),
    ...semAceite(4, 6),
  ];
  const opcoes = { criterios: ['A1', 'A2', 'A3'] };
  assert.deepEqual(conferirPlan(fase(t, tres, opcoes)).achados, ['3 checkpoints; o máximo é 2 por phase']);
  const dois = tres.filter((l) => l !== checkpoint('A3'));
  assert.deepEqual(conferirPlan(fase(t, dois, opcoes)).achados, []);
});

test('checkpoint em plan de até 5 passos é achado; com 6 passos não (A7)', (t) => {
  const cinco = [passo('1', { aceite: 'A1' }), checkpoint('A1'), ...semAceite(2, 5)];
  assert.deepEqual(conferirPlan(fase(t, cinco)).achados, ['checkpoint em plan de 5 passos; phase com até 5 passos não tem checkpoint']);
  // Passos de um grupo paralelo contam um a um: 1, 2a, 2b, 3 e 4 são 5 passos.
  const grupo = [passo('1', { aceite: 'A1' }), checkpoint('A1'), passo('2a', { aceite: 'nenhum' }), passo('2b', { aceite: 'nenhum' }), ...semAceite(3, 4)];
  assert.deepEqual(conferirPlan(fase(t, grupo)).achados, ['checkpoint em plan de 5 passos; phase com até 5 passos não tem checkpoint']);
  const seis = [passo('1', { aceite: 'A1' }), checkpoint('A1'), ...semAceite(2, 6)];
  assert.deepEqual(conferirPlan(fase(t, seis)).achados, []);
});
