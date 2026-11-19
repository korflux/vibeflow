#!/usr/bin/env node
// bench.mjs: benchmark de comportamento da skill. Faz a um modelo perguntas de situação
// (estado do repo e pedido do humano) com só os arquivos da skill passados como contexto,
// corrige a resposta JSON contra o esperado e compara duas rodadas, para medir se um corte ou
// uma reescrita do texto mantém a taxa de acerto.
//
// Fica fora do pacote e de `node --test` porque chama modelo: custa, depende de login e varia
// entre execuções. O corretor e a comparação são determinísticos e têm teste em
// `tests/tools/bench.test.mjs`, com um executor falso no lugar do `claude`.
//
// Suíte (`tools/bench/<suite>.json`):
// - `instrucao`: texto fixo que vai depois do estado e do pedido de cada caso.
// - `campos`: valores permitidos por campo da resposta; valor fora da lista conta como erro.
// - `casos[]`: `id`, `grupo`, `tipo` (`core` durante a edição, `var` só na conferência final),
//   `critico`, `estado`, `pedido`, `esperado` (só os campos corrigidos) e `casa` (onde mora a
//   regra, para ler o erro).
//
// Isolamento de cada chamada: `claude -p` numa pasta temporária vazia, sem ferramentas, sem MCP,
// sem settings, sem skills e sem sessão gravada, com o contexto inteiro no prompt de sistema
// (`--system-prompt-file`, para não estourar o limite de linha de comando do Windows).
// ponytail: sem `ANTHROPIC_API_KEY` não dá para usar `--bare`, e o `claude -p` logado pela
//   assinatura ainda injeta os blocos `# userEmail` e `# Environment` (pasta e data). Na sonda de
//   2026-11-11 (CLI 2.1.314) o CLAUDE.md global não vazou. Com a chave no ambiente o runner passa
//   `--bare`. O comando `sonda` mostra o que o modelo recebeu além do contexto; rode-o de novo
//   quando a CLI mudar de versão.
// ponytail: o ruído é medido só pela instabilidade entre repetições do mesmo caso; com 3
//   repetições, uma queda de um acerto pode ser ruído. Subir `--reps` antes de aceitar um corte
//   que derruba caso instável na base.
//
// Uso:
//   node tools/bench.mjs rodar <suite.json> --contexto <arquivo>... [--modelo haiku] [--reps 3]
//        [--tipo core|var|todos] [--casos <id,id>] [--paralelo 4] [--executor <script.mjs>] [--json]
//   `--casos` roda só os ids listados, para diagnosticar um erro sem refazer a suíte.
//   node tools/bench.mjs sonda --contexto <arquivo>... [--modelo haiku] [--executor <script.mjs>]
//   node tools/bench.mjs comparar <base.json> <nova.json> [--json]
// `rodar --json` grava a rodada que `comparar` lê. Saída: 0 sem erro nem queda, 1 com erro de
// resposta ou queda, 2 em erro de uso.

import { readFileSync, writeFileSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve, basename } from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const TEMPO_LIMITE_MS = 180_000;

// ===== Montagem do prompt =====

/** Prompt de sistema: o papel e cada arquivo de contexto delimitado pelo nome. */
export function montarSistema(contextos) {
  const partes = contextos.map(({ nome, texto }) => `=== arquivo: ${nome} ===\n${texto.replace(/^﻿/, '').replace(/\r\n/g, '\n')}\n=== fim: ${nome} ===`);
  return `Você responde a um caso de teste da skill vibeflow. As regras que valem são só as dos arquivos abaixo.\n\n${partes.join('\n\n')}`;
}

/** Mensagem do caso: estado, pedido e a instrução fixa da suíte. */
export function montarPrompt(suite, caso) {
  return `Estado do repositório: ${caso.estado}\n\nPedido do humano: ${caso.pedido}\n\n${suite.instrucao}`;
}

// ===== Leitura e correção da resposta =====

/**
 * Extrai o objeto JSON da saída `--output-format json` do `claude -p`; erro vira `{ erro }`.
 * O modelo às vezes responde, se corrige em texto e responde de novo: vale o último objeto, que
 * é o primeiro trecho de `{` até o último `}` que fecha um JSON válido.
 */
export function lerResposta(stdout) {
  let envelope;
  try { envelope = JSON.parse(stdout); } catch { return { erro: 'saída do executor não é JSON' }; }
  if (envelope.is_error) return { erro: String(envelope.result ?? 'erro do executor').slice(0, 200) };
  const texto = String(envelope.result ?? '');
  const fim = texto.lastIndexOf('}');
  if (texto.indexOf('{') < 0 || fim < texto.indexOf('{')) return { erro: 'resposta sem objeto JSON', bruto: texto.slice(0, 200) };
  for (let inicio = texto.indexOf('{'); inicio >= 0 && inicio < fim; inicio = texto.indexOf('{', inicio + 1)) {
    try {
      return { resposta: JSON.parse(texto.slice(inicio, fim + 1)), custo: envelope.total_cost_usd ?? 0, ms: envelope.duration_ms ?? 0 };
    } catch { /* tenta o próximo início */ }
  }
  return { erro: 'objeto JSON inválido na resposta', bruto: texto.slice(0, 2000) };
}

/** Confere cada campo de `esperado`; valor fora de `suite.campos` conta como errado. */
export function corrigir(suite, caso, resposta) {
  const campos = {};
  let ok = true;
  for (const [campo, esperado] of Object.entries(caso.esperado)) {
    const obtido = resposta?.[campo];
    const permitido = !suite.campos?.[campo] || suite.campos[campo].includes(obtido);
    const certo = permitido && obtido === esperado;
    campos[campo] = { esperado, obtido: obtido ?? null, ok: certo };
    if (!certo) ok = false;
  }
  return { ok, campos };
}

// ===== Execução =====

function argsClaude(modelo, arquivoSistema, prompt) {
  const args = ['-p', '--model', modelo, '--output-format', 'json', '--tools', '', '--setting-sources', '',
    '--strict-mcp-config', '--no-session-persistence', '--disable-slash-commands', '--system-prompt-file', arquivoSistema];
  if (process.env.ANTHROPIC_API_KEY) args.push('--bare');
  args.push(prompt);
  return args;
}

/** Roda uma chamada isolada; o executor falso dos testes recebe os mesmos argumentos. */
function chamar({ executor, modelo, arquivoSistema, prompt, pasta }) {
  const args = argsClaude(modelo, arquivoSistema, prompt);
  const [cmd, lista] = executor ? [process.execPath, [executor, ...args]] : ['claude', args];
  return new Promise((ok) => {
    const filho = spawn(cmd, lista, { cwd: pasta, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] });
    let saida = '';
    const relogio = setTimeout(() => filho.kill(), TEMPO_LIMITE_MS);
    filho.stdout.on('data', (d) => { saida += d; });
    filho.on('error', (e) => { clearTimeout(relogio); ok({ erro: `executor não iniciou: ${e.code ?? e.message}` }); });
    filho.on('close', () => { clearTimeout(relogio); ok(lerResposta(saida)); });
  });
}

async function emPool(tarefas, paralelo) {
  const resultados = new Array(tarefas.length);
  let proxima = 0;
  async function trabalhador() {
    while (proxima < tarefas.length) { const i = proxima++; resultados[i] = await tarefas[i](); }
  }
  await Promise.all(Array.from({ length: Math.min(paralelo, tarefas.length) }, trabalhador));
  return resultados;
}

/** Roda a suíte e devolve a rodada no formato que `comparar` lê. */
export async function rodar({ suite, nomeSuite, contextos, modelo = 'haiku', reps = 3, tipo = 'core', paralelo = 4, executor = null, ids = null }) {
  const casos = suite.casos.filter((c) => (ids ? ids.includes(c.id) : tipo === 'todos' || c.tipo === tipo));
  const pasta = mkdtempSync(join(tmpdir(), 'vibeflow-bench-'));
  try {
    const arquivoSistema = join(pasta, 'sistema.txt');
    writeFileSync(arquivoSistema, montarSistema(contextos));
    const tarefas = casos.flatMap((caso) => Array.from({ length: reps }, () => async () => {
      const r = await chamar({ executor, modelo, arquivoSistema, prompt: montarPrompt(suite, caso), pasta });
      return { id: caso.id, ...r, correcao: r.erro ? null : corrigir(suite, caso, r.resposta) };
    }));
    const execucoes = await emPool(tarefas, paralelo);
    return resumir({ suite, nomeSuite, contextos, modelo, reps, tipo, casos, execucoes });
  } finally {
    rmSync(pasta, { recursive: true, force: true });
  }
}

// ===== Resumo e comparação =====

const palavras = (texto) => texto.split(/\s+/).filter(Boolean).length;

export function resumir({ nomeSuite, contextos, modelo, reps, tipo, casos, execucoes }) {
  const porCaso = casos.map((caso) => {
    const minhas = execucoes.filter((e) => e.id === caso.id);
    const acertos = minhas.filter((e) => e.correcao?.ok).length;
    const erros = minhas.filter((e) => e.erro).length;
    return {
      id: caso.id, grupo: caso.grupo, tipo: caso.tipo, critico: !!caso.critico, casa: caso.casa,
      acertos, reps: minhas.length, erros,
      respostas: minhas.map((e) => e.erro ? { erro: e.erro, ...(e.bruto ? { bruto: e.bruto } : {}) } : { ...e.resposta, ok: e.correcao.ok }),
    };
  });
  const somar = (lista) => {
    const reps_ = lista.reduce((s, c) => s + c.reps, 0);
    const acertos = lista.reduce((s, c) => s + c.acertos, 0);
    return { acertos, reps: reps_, taxa: reps_ ? acertos / reps_ : 0 };
  };
  const grupos = {};
  for (const c of porCaso) (grupos[c.grupo] ??= []).push(c);
  return {
    suite: nomeSuite, modelo, reps, tipo,
    contexto: contextos.map(({ nome, texto }) => ({ nome, palavras: palavras(texto) })),
    palavrasContexto: contextos.reduce((s, c) => s + palavras(c.texto), 0),
    custoUsd: execucoes.reduce((s, e) => s + (e.custo ?? 0), 0),
    total: somar(porCaso),
    criticos: somar(porCaso.filter((c) => c.critico)),
    grupos: Object.fromEntries(Object.entries(grupos).map(([g, l]) => [g, somar(l)])),
    instaveis: porCaso.filter((c) => c.acertos > 0 && c.acertos < c.reps).map((c) => c.id),
    falhas: porCaso.filter((c) => c.acertos < c.reps).map((c) => c.id),
    errosExecutor: porCaso.reduce((s, c) => s + c.erros, 0),
    casos: porCaso,
  };
}

/** Compara duas rodadas pelo id do caso; queda em crítico ou na taxa geral é achado. */
export function comparar(base, nova) {
  const avisos = [];
  if (base.suite !== nova.suite) avisos.push(`suítes diferentes: ${base.suite} e ${nova.suite}`);
  if (base.modelo !== nova.modelo) avisos.push(`modelos diferentes: ${base.modelo} e ${nova.modelo}`);
  const daBase = new Map(base.casos.map((c) => [c.id, c]));
  const mudancas = [];
  for (const c of nova.casos) {
    const b = daBase.get(c.id);
    if (!b) { avisos.push(`caso ${c.id} só na nova rodada`); continue; }
    const tb = b.reps ? b.acertos / b.reps : 0;
    const tn = c.reps ? c.acertos / c.reps : 0;
    if (tb !== tn) mudancas.push({ id: c.id, critico: c.critico, base: `${b.acertos}/${b.reps}`, nova: `${c.acertos}/${c.reps}`, caiu: tn < tb, instavelNaBase: b.acertos > 0 && b.acertos < b.reps });
  }
  const quedasCriticas = mudancas.filter((m) => m.caiu && m.critico).map((m) => m.id);
  return {
    avisos,
    palavras: { base: base.palavrasContexto, nova: nova.palavrasContexto },
    taxa: { base: base.total.taxa, nova: nova.total.taxa },
    mudancas, quedasCriticas,
    aceito: quedasCriticas.length === 0 && nova.total.taxa >= base.total.taxa,
  };
}

// ===== Relatório em texto =====

const pct = (t) => `${(t * 100).toFixed(1)}%`;

export function relatorioRodada(r) {
  const linhas = [
    `Suíte ${r.suite}, modelo ${r.modelo}, tipo ${r.tipo}, ${r.reps} repetições, contexto de ${r.palavrasContexto} palavras.`,
    `Acerto geral: ${r.total.acertos}/${r.total.reps} (${pct(r.total.taxa)}). Críticos: ${r.criticos.acertos}/${r.criticos.reps} (${pct(r.criticos.taxa)}).`,
    `Custo informado pelo executor: US$ ${r.custoUsd.toFixed(4)}. Erros do executor: ${r.errosExecutor}.`,
    '', 'Por grupo:',
    ...Object.entries(r.grupos).map(([g, s]) => `  ${g}: ${s.acertos}/${s.reps}`),
  ];
  const falhos = r.casos.filter((c) => c.acertos < c.reps);
  if (falhos.length) {
    linhas.push('', 'Casos com erro:');
    for (const c of falhos) {
      linhas.push(`  ${c.id}${c.critico ? ' (crítico)' : ''}: ${c.acertos}/${c.reps}; regra em ${c.casa}`);
      for (const { ok, motivo, ...campos } of c.respostas.filter((x) => !x.ok)) linhas.push(`    ${campos.erro ? `erro: ${campos.erro}` : `${JSON.stringify(campos)} ${motivo ?? ''}`}`);
    }
  }
  return linhas.join('\n');
}

export function relatorioComparacao(c) {
  const linhas = [
    ...c.avisos.map((a) => `Aviso: ${a}.`),
    `Contexto: ${c.palavras.base} para ${c.palavras.nova} palavras. Acerto: ${pct(c.taxa.base)} para ${pct(c.taxa.nova)}.`,
    ...c.mudancas.map((m) => `  ${m.id}${m.critico ? ' (crítico)' : ''}: ${m.base} para ${m.nova}${m.instavelNaBase ? ', instável na base' : ''}`),
    c.aceito ? 'Sem queda em caso crítico nem na taxa geral.' : `Queda: ${c.quedasCriticas.length ? `críticos ${c.quedasCriticas.join(', ')}` : 'taxa geral menor'}.`,
  ];
  return linhas.join('\n');
}

// ===== CLI =====

const USO = 'Uso: node tools/bench.mjs rodar <suite.json> --contexto <arquivo>... [--modelo haiku] [--reps 3] [--tipo core|var|todos] [--casos <id,id>] [--paralelo 4] [--executor <script.mjs>] [--json]\n     node tools/bench.mjs sonda --contexto <arquivo>... [--modelo haiku] [--executor <script.mjs>]\n     node tools/bench.mjs comparar <base.json> <nova.json> [--json]';

function usoInvalido(mensagem) {
  process.stderr.write(`${mensagem}\n${USO}\n`);
  process.exit(2);
}

function lerJson(arquivo) {
  try { return JSON.parse(readFileSync(arquivo, 'utf8').replace(/^﻿/, '')); } catch (e) { usoInvalido(`Não li ${arquivo}: ${e.code ?? 'JSON inválido'}.`); }
}

function lerContextos(arquivos) {
  if (!arquivos.length) usoInvalido('Falta --contexto.');
  return arquivos.map((a) => {
    try { return { nome: a.replace(/\\/g, '/'), texto: readFileSync(a, 'utf8') }; } catch { usoInvalido(`Contexto não encontrado: ${a}.`); }
  });
}

const ascii = (texto) => texto.replace(/[\u007F-￿]/g, (ch) => `\\u${ch.charCodeAt(0).toString(16).padStart(4, '0')}`);

async function main(args) {
  const [comando, ...resto] = args;
  const pos = [];
  const op = { contexto: [], modelo: 'haiku', reps: 3, tipo: 'core', paralelo: 4, executor: null, json: false };
  for (let i = 0; i < resto.length; i++) {
    const a = resto[i];
    if (a === '--json') op.json = true;
    else if (a === '--contexto') { while (resto[i + 1] && !resto[i + 1].startsWith('--')) op.contexto.push(resto[++i]); }
    else if (['--modelo', '--tipo', '--executor'].includes(a)) { if (!resto[i + 1]) usoInvalido(`Falta valor em ${a}.`); op[a.slice(2)] = resto[++i]; }
    else if (a === '--casos') { if (!resto[i + 1]) usoInvalido('Falta valor em --casos.'); op.ids = resto[++i].split(','); }
    else if (a === '--reps' || a === '--paralelo') {
      const n = Number(resto[++i]);
      if (!Number.isInteger(n) || n < 1 || n > 20) usoInvalido(`${a} precisa ser inteiro de 1 a 20.`);
      op[a.slice(2)] = n;
    } else if (a.startsWith('--')) usoInvalido(`Opção desconhecida: ${a}.`);
    else pos.push(a);
  }
  if (op.executor) op.executor = resolve(op.executor);

  if (comando === 'rodar') {
    if (pos.length !== 1) usoInvalido('Informe uma suíte.');
    if (!['core', 'var', 'todos'].includes(op.tipo)) usoInvalido(`Tipo inválido: ${op.tipo}.`);
    const suite = lerJson(pos[0]);
    if (!Array.isArray(suite.casos) || typeof suite.instrucao !== 'string') usoInvalido('Suíte sem casos ou sem instrucao.');
    const desconhecidos = (op.ids ?? []).filter((id) => !suite.casos.some((c) => c.id === id));
    if (desconhecidos.length) usoInvalido(`Caso inexistente: ${desconhecidos.join(', ')}.`);
    const rodada = await rodar({ suite, nomeSuite: basename(pos[0], '.json'), contextos: lerContextos(op.contexto), ...op });
    process.stdout.write(`${op.json ? ascii(JSON.stringify(rodada, null, 2)) : relatorioRodada(rodada)}\n`);
    return rodada.falhas.length || rodada.errosExecutor ? 1 : 0;
  }
  if (comando === 'sonda') {
    const suite = { instrucao: 'Além do prompt de sistema e desta mensagem, você recebeu outro texto de contexto (CLAUDE.md, memória, regras, lembretes)? Responda só com JSON {"extra": true|false, "inicio": "<as primeiras 3 linhas literais do texto extra, ou vazio>"}.', casos: [{ id: 'sonda', estado: '-', pedido: '-', esperado: { extra: false } }] };
    const rodada = await rodar({ suite, nomeSuite: 'sonda', contextos: lerContextos(op.contexto), ...op, reps: 1, tipo: 'todos' });
    process.stdout.write(`${ascii(JSON.stringify(rodada.casos[0].respostas[0], null, 2))}\n`);
    return rodada.falhas.length ? 1 : 0;
  }
  if (comando === 'comparar') {
    if (pos.length !== 2) usoInvalido('Informe duas rodadas.');
    const c = comparar(lerJson(pos[0]), lerJson(pos[1]));
    process.stdout.write(`${op.json ? ascii(JSON.stringify(c, null, 2)) : relatorioComparacao(c)}\n`);
    return c.aceito ? 0 : 1;
  }
  usoInvalido(comando ? `Comando desconhecido: ${comando}.` : 'Falta o comando.');
}

if (process.argv[1] && resolve(process.argv[1]).toLowerCase() === fileURLToPath(import.meta.url).toLowerCase()) {
  main(process.argv.slice(2)).then((codigo) => { process.exitCode = codigo; });
}
