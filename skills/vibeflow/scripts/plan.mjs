#!/usr/bin/env node
// plan.mjs: confere a parte mecânica do plan.md contra o contrato e contra a spec.
//
// Aplica references/disco.md (Plan) e as conferências mecânicas de
// references/analyze/coverage.md: forma da linha de passo e de checkpoint, numeração e
// grupos paralelos, critérios de `Aceite:` e de checkpoint que existem na spec, critério
// da spec sem passo, seção `## Regressão completa` presente, `## Achados do analyze` como
// última seção e placeholder de template esquecido na spec ou no plan. O julgamento do
// analyze (prova que exercita o critério, arquivo ou consumidor esquecido, ordem,
// contradição com a spec) continua do revisor. Só lê; divergência entre este script e a
// prosa é bug do script.
//
// Com --spec, confere só a spec, antes da aprovação (references/spec.md, Fechar): seções
// obrigatórias, decisão sem Pergunta: ou Motivo:, critério repetido, adjetivo vago no
// critério e placeholder esquecido. Não exige plan.md.
//
// Uso:
//   node plan.mjs [--spec] [--alvo phase-N|mvp] [--raiz <dir>] [--json]
// Saída: 0 sem achado, 1 com achado, 2 em erro de uso.

import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  carregarAlvos, alvoPadrao, alvoNomeado, lerLinhas, lerPlan, achadosDoPlan, RE_PASSO, RE_CHECKPOINT, SEP,
  jsonAscii, executadoDireto,
} from './_disco.mjs';

const TEMPLATES = join(dirname(fileURLToPath(import.meta.url)), '..', 'templates');

// ---------------------------------------------------------------------------
// Leitura de seções e limpeza de texto
// ---------------------------------------------------------------------------

/** Linhas de uma seção `## Título` até a próxima `## `; null se a seção não existe. */
function secao(linhas, titulo) {
  const i = (linhas || []).findIndex((l) => l.trim() === `## ${titulo}`);
  if (i < 0) return null;
  const fim = linhas.findIndex((l, j) => j > i && /^## /.test(l));
  return linhas.slice(i + 1, fim < 0 ? linhas.length : fim);
}

/**
 * Linhas sem comentários HTML (inclusive os de várias linhas). Os comentários do template
 * são instrução para quem grava, não conteúdo do artefato.
 */
function semComentarios(linhas) {
  const saida = [];
  let dentro = false;
  for (const l of linhas || []) {
    let resto = l;
    let limpa = '';
    while (resto) {
      if (dentro) {
        const f = resto.indexOf('-->');
        if (f < 0) { resto = ''; break; }
        resto = resto.slice(f + 3);
        dentro = false;
      } else {
        const a = resto.indexOf('<!--');
        if (a < 0) { limpa += resto; break; }
        limpa += resto.slice(0, a);
        resto = resto.slice(a + 4);
        dentro = true;
      }
    }
    saida.push(limpa);
  }
  return saida;
}

// ---------------------------------------------------------------------------
// Placeholders de template (references/disco.md, Escrever artefato)
// ---------------------------------------------------------------------------

/**
 * Placeholders de um template: cada `<...>` de nível externo fora de comentário, inclusive
 * os aninhados como `<phase-<n>-<slug> ou mvp>`. A fonte é o próprio template, então um
 * placeholder novo entra aqui sem mudar o script.
 */
function placeholdersDoTemplate(nome) {
  const linhas = semComentarios(lerLinhas(join(TEMPLATES, nome)));
  return [...new Set(linhas.flatMap((l) => [...l.matchAll(/<(?:[^<>\n]|<[^<>\n]*>)+>/g)].map((m) => m[0])))];
}

/**
 * Placeholders do template que sobraram no artefato. Texto entre crases fica de fora,
 * porque é como um artefato cita um placeholder de propósito (por exemplo, uma spec que
 * discute o próprio template).
 *
 * ponytail: compara só os placeholders literais do template; um placeholder reescrito à
 * mão com outra palavra passa, e só a leitura do revisor o pega.
 */
function placeholdersEsquecidos(linhas, nomeTemplate, rotulo) {
  const tokens = placeholdersDoTemplate(nomeTemplate);
  const achados = [];
  semComentarios(linhas).forEach((l, i) => {
    const visivel = l.replace(/`[^`]*`/g, '');
    for (const t of tokens) if (visivel.includes(t)) achados.push(`${rotulo}, linha ${i + 1}: placeholder ${t} não preenchido`);
  });
  return achados;
}

// ---------------------------------------------------------------------------
// Critérios da spec e forma do plan
// ---------------------------------------------------------------------------

/** IDs `A<n>` da seção `## Critérios de aceite` da spec, na ordem, com repetidos à parte. */
function criteriosDaSpec(linhasSpec) {
  const ids = [];
  const repetidos = [];
  for (const l of secao(linhasSpec, 'Critérios de aceite') || []) {
    const m = l.match(/^- (A[1-9][0-9]*):/);
    if (!m) continue;
    if (ids.includes(m[1])) repetidos.push(m[1]);
    else ids.push(m[1]);
  }
  return { ids, repetidos };
}

/** Achados de forma de uma linha de passo: campos na ordem `Aceite:`, `Arquivos:` opcional e `Prova:`. */
function formaDoPasso(p, criterios) {
  const achados = [];
  const r = p.resto;
  const iA = r.indexOf(`${SEP}Aceite:`);
  const iArq = r.indexOf(`${SEP}Arquivos:`);
  const iP = r.indexOf(`${SEP}Prova:`);
  if (iA <= 0) achados.push(`passo ${p.id}: falta o resultado antes de Aceite: ou o próprio campo Aceite:`);
  if (iP < 0) achados.push(`passo ${p.id}: falta o campo Prova:`);
  else if (!r.slice(iP + `${SEP}Prova:`.length).trim()) achados.push(`passo ${p.id}: Prova: vazia`);
  if (iA > 0 && iP > 0 && (iP < iA || (iArq >= 0 && (iArq < iA || iArq > iP)))) achados.push(`passo ${p.id}: campos fora da ordem Aceite:, Arquivos:, Prova:`);
  if (iArq >= 0 && (!p.arquivos || !p.arquivos.length)) achados.push(`passo ${p.id}: Arquivos: sem path entre crases`);
  if (p.aceite) {
    const sobra = p.aceite.bruto.replace(/\bA[1-9][0-9]*\b/g, '').replace(/[\s,]/g, '');
    if (p.aceite.bruto !== 'nenhum' && (sobra || !p.aceite.ids.length)) achados.push(`passo ${p.id}: Aceite: deve listar A* da spec ou dizer nenhum`);
    for (const a of p.aceite.ids) if (!criterios.includes(a)) achados.push(`passo ${p.id}: Aceite: cita ${a}, que não existe na spec`);
  }
  return achados;
}

/**
 * Checkpoints: linha depois de passo (nunca no início nem logo após outro checkpoint),
 * com critérios que existem na spec e que algum passo do trecho coberto entrega.
 */
function formaDosCheckpoints(itens, criterios) {
  const achados = [];
  let trecho = [];
  itens.forEach((it, k) => {
    if (it.tipo === 'passo') { trecho.push(it); return; }
    const n = `checkpoint ${k + 1}º item`;
    if (!trecho.length) achados.push(`${n}: sem passo entre ele e o checkpoint anterior ou o início`);
    if (!it.aceite.length) achados.push(`${n}: sem critério listado`);
    const entregues = new Set(trecho.flatMap((p) => (p.aceite ? p.aceite.ids : [])));
    for (const a of it.aceite) {
      if (!criterios.includes(a)) achados.push(`${n}: cita ${a}, que não existe na spec`);
      else if (!entregues.has(a)) achados.push(`${n}: cita ${a}, que nenhum passo do trecho coberto entrega`);
    }
    trecho = [];
  });
  return achados;
}

/** Linhas da seção `## Passos` que não são passo nem checkpoint (fora comentário e linha vazia). */
function linhasEstranhas(linhasPlan) {
  return semComentarios(secao(linhasPlan, 'Passos') || [])
    .filter((l) => l.trim() && !RE_PASSO.test(l) && !RE_CHECKPOINT.test(l))
    .map((l) => `linha fora do formato de passo ou checkpoint em ## Passos: ${l.trim().slice(0, 80)}`);
}

// ---------------------------------------------------------------------------
// Forma da spec antes da aprovação (references/spec.md, Gravação, Critérios de aceite e Fechar)
// ---------------------------------------------------------------------------

const SECOES_SPEC = ['Objetivo', 'Pontos do projeto', 'Decisões', 'Critérios de aceite', 'Fora do escopo'];

// Adjetivos que não dizem o que observar (references/spec.md, Gravação).
// Aceita a palavra com ou sem acento. Texto entre crases ou aspas fica de fora, porque é
// como a spec cita código ou a mensagem exibida ao usuário.
// ponytail: lista fixa e curta; vago escrito de outro jeito ("de modo ágil") passa, e só a
// conferência do líder e o analyze o pegam.
const RE_VAGO = /(?<!\p{L})(r[aá]pid[oa]s?|rapidamente|bonit[oa]s?|modern[oa]s?|intuitiv[oa]s?|amig[aá]ve(?:l|is)|f[aá]c(?:il|eis)|facilmente|adequad[oa]s?|adequadamente|corretamente|eficientes?|eficientemente|robust[oa]s?|elegantes?|agrad[aá]ve(?:l|is))(?!\p{L})/giu;
const RE_CITACAO = /`[^`]*`|"[^"]*"|“[^”]*”|'[^']*'/g;

/** Achados de forma da spec: seções, decisões sem pergunta ou motivo, critérios e placeholders. */
function formaDaSpec(linhasSpec) {
  const achados = [];
  for (const s of SECOES_SPEC) if (!secao(linhasSpec, s)) achados.push(`spec sem a seção ## ${s}`);

  for (const l of semComentarios(secao(linhasSpec, 'Decisões') || [])) {
    const m = l.match(/^(\d+)\. /);
    if (!m) continue;
    if (!/Pergunta:/.test(l)) achados.push(`decisão ${m[1]}: sem Pergunta:`);
    if (!/Motivo:/.test(l)) achados.push(`decisão ${m[1]}: sem Motivo:`);
  }

  const { ids, repetidos } = criteriosDaSpec(linhasSpec);
  if (!ids.length) achados.push('spec sem critério A<n> em ## Critérios de aceite');
  for (const a of repetidos) achados.push(`spec com o critério ${a} repetido`);
  for (const l of semComentarios(secao(linhasSpec, 'Critérios de aceite') || [])) {
    const m = l.match(/^- (A[1-9][0-9]*):(.*)$/);
    if (!m) continue;
    const vagos = [...m[2].normalize('NFC').replace(RE_CITACAO, '').matchAll(RE_VAGO)].map((v) => v[1].toLowerCase());
    if (vagos.length) achados.push(`critério ${m[1]}: adjetivo vago (${[...new Set(vagos)].join(', ')}); diga o resultado observável`);
  }

  achados.push(...placeholdersEsquecidos(linhasSpec, 'spec.md', 'spec.md'));
  return { criterios: ids, achados };
}

// ---------------------------------------------------------------------------
// Relatório
// ---------------------------------------------------------------------------

/** Alvo nomeado ou padrão, já recusando o formato antigo. */
function resolverAlvo(raiz, nomeAlvo) {
  const alvos = carregarAlvos(raiz);
  const alvo = nomeAlvo ? alvoNomeado(alvos, nomeAlvo) : alvoPadrao(alvos);
  if (!alvo) return { erro: nomeAlvo ? `alvo não encontrado: ${nomeAlvo}` : 'sem alvo aberto; informe --alvo' };
  if (alvo.antigo) return { erro: `${alvo.alvo} está no formato antigo (references/disco.md, Compatibilidade); só o contrato atual é conferido` };
  return { alvo };
}

/** Confere só a spec do alvo, antes da aprovação; exportado para os testes. */
export function conferirSpec(raiz, nomeAlvo = null) {
  const { alvo, erro } = resolverAlvo(raiz, nomeAlvo);
  if (erro) return { erro };
  if (!alvo.art.spec) return { erro: `${alvo.alvo} sem spec.md` };
  return { alvo: alvo.alvo, ...formaDaSpec(alvo.art.spec) };
}

/** Confere o plan do alvo; exportado para os testes. */
export function conferirPlan(raiz, nomeAlvo = null) {
  const { alvo, erro } = resolverAlvo(raiz, nomeAlvo);
  if (erro) return { erro };
  if (!alvo.art.plan) return { erro: `${alvo.alvo} sem plan.md` };
  if (!alvo.art.spec) return { erro: `${alvo.alvo} sem spec.md` };

  const { ids: criterios, repetidos } = criteriosDaSpec(alvo.art.spec);
  const plan = lerPlan(secao(alvo.art.plan, 'Passos') || []);
  const achados = [];

  if (!criterios.length) achados.push('spec sem critério A<n> em ## Critérios de aceite');
  for (const a of repetidos) achados.push(`spec com o critério ${a} repetido`);
  if (!secao(alvo.art.plan, 'Passos')) achados.push('plan sem a seção ## Passos');
  else if (!plan.passos.length) achados.push('## Passos sem nenhum passo');
  achados.push(...linhasEstranhas(alvo.art.plan));
  achados.push(...achadosDoPlan(plan.passos));
  for (const p of plan.passos) achados.push(...formaDoPasso(p, criterios));
  achados.push(...formaDosCheckpoints(plan.itens, criterios));

  const cobertos = new Set(plan.passos.flatMap((p) => (p.aceite ? p.aceite.ids : [])));
  for (const a of criterios) if (!cobertos.has(a)) achados.push(`critério ${a} da spec sem passo`);

  const regressao = secao(alvo.art.plan, 'Regressão completa');
  if (!regressao) achados.push('plan sem a seção ## Regressão completa');
  else if (!semComentarios(regressao).some((l) => l.trim())) achados.push('## Regressão completa sem comando');

  const titulos = alvo.art.plan.filter((l) => /^## /.test(l)).map((l) => l.trim());
  const iAchados = titulos.indexOf('## Achados do analyze');
  if (iAchados >= 0 && iAchados !== titulos.length - 1) achados.push('## Achados do analyze não é a última seção do plan');

  achados.push(...placeholdersEsquecidos(alvo.art.spec, 'spec.md', 'spec.md'));
  achados.push(...placeholdersEsquecidos(alvo.art.plan, 'plan.md', 'plan.md'));

  return { alvo: alvo.alvo, criterios, passos: plan.passos.length, checkpoints: plan.itens.length - plan.passos.length, achados };
}

// ---------------------------------------------------------------------------
// Execução
// ---------------------------------------------------------------------------

function lerArgs(argv) {
  const args = { raiz: process.cwd(), alvo: null, json: false, spec: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--json') args.json = true;
    else if (a === '--spec') args.spec = true;
    else if ((a === '--raiz' || a === '--alvo') && argv[i + 1]) args[a.slice(2)] = argv[++i];
    else return { erro: `argumento desconhecido ou sem valor: ${a}` };
  }
  return args;
}

function texto(r) {
  const contagem = r.passos === undefined ? '' : ` · passos: ${r.passos} · checkpoints: ${r.checkpoints}`;
  const l = [`alvo: ${r.alvo} · critérios: ${r.criterios.join(', ') || 'nenhum'}${contagem}`];
  for (const a of r.achados) l.push(`achado: ${a}`);
  if (!r.achados.length) l.push('sem achado');
  return `${l.join('\n')}\n`;
}

function principal() {
  const args = lerArgs(process.argv.slice(2));
  if (args.erro) { console.error(args.erro); return 2; }
  const r = (args.spec ? conferirSpec : conferirPlan)(resolve(args.raiz), args.alvo);
  if (r.erro) { console.error(r.erro); return 2; }
  process.stdout.write(args.json ? `${jsonAscii(r)}\n` : texto(r));
  return r.achados.length ? 1 : 0;
}

if (executadoDireto(import.meta.url)) {
  process.exitCode = principal();
}
