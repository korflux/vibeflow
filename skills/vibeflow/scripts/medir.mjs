#!/usr/bin/env node
// medir.mjs: mede uma phase ou o MVP pelo Git e pelos artefatos, para comparar o custo da
// entrega entre phases e versões da skill.
//
// Implementa a seção "Medição" de references/review.md (Finalizar): tempo de relógio entre
// o primeiro e o último commit do alvo, horas ativas sem as pausas, commits por passo (mais
// de um é retrabalho, como a correção devolvida pelo checkpoint), intervalo entre commits de
// passo, R* por severidade e etapas da review. Só lê; quem grava a linha no review.md é o líder. Divergência entre
// este script e a prosa é bug do script.
//
// Limites conhecidos:
// ponytail: o relógio começa no primeiro commit do alvo, então interview, spec, plan e
//   analyze (sem commit) ficam fora; medir essas etapas exige hora de início gravada no disco.
// ponytail: o intervalo entre commits inclui espera pelo humano e pausas; serve para achar
//   o passo mais lento e comparar phases, não para cronometrar o trabalho do agente. As
//   horas ativas somam só os intervalos de até PAUSA_MIN minutos, tratando os maiores como
//   pausa; trocar por hora de início e fim gravada por etapa se a heurística enganar.
// ponytail: em medium, o commit `task(medium): ...` da base não entra (não leva o alvo).
//
// Uso:
//   node medir.mjs [--alvo phase-N|mvp] [--raiz <dir>] [--json]
// Sem --alvo, mede o alvo padrão (references/disco.md, Estado da phase) ou, sem alvo aberto,
// a phase de maior n. Saída: 0 com medição, 2 em erro de uso ou sem alvo.

import { resolve } from 'node:path';
import {
  carregarAlvos, alvoPadrao, alvoNomeado, lerPlan, classificarCommit, git, jsonAscii, executadoDireto,
} from './_disco.mjs';

// Intervalo entre commits acima do qual o tempo conta como pausa, fora das horas ativas.
const PAUSA_MIN = 120;
const RE_R = /^- \[[ xX]\] R[1-9][0-9]*:\s*\*\*(Critical|Required|Nit)\*\*/;

/** Commits do branch, do mais antigo ao mais novo, com a data de commit em segundos. */
function commitsComData(raiz) {
  const out = git(raiz, ['log', '--reverse', '--format=%H%x09%ct%x09%s']);
  if (out === null) return null;
  return out.split(/\r?\n/).filter(Boolean).map((l) => {
    const [hash, ct, ...resto] = l.split('\t');
    return { hash, ts: Number(ct), assunto: resto.join('\t') };
  });
}

const minutos = (s) => Math.round(s / 60);
const horas = (s) => Math.round((s / 3600) * 10) / 10;

function mediana(valores) {
  if (!valores.length) return null;
  const v = [...valores].sort((a, b) => a - b);
  const m = Math.floor(v.length / 2);
  return v.length % 2 ? v[m] : Math.round((v[m - 1] + v[m]) / 2);
}

/** Medição do alvo: relógio, passos, retrabalho, intervalos e review. */
export function medir(raiz, nomeAlvo = null) {
  const alvos = carregarAlvos(raiz);
  const alvo = nomeAlvo ? alvoNomeado(alvos, nomeAlvo)
    : alvoPadrao(alvos) || alvos.filter((a) => a.n !== null).pop() || null;
  if (!alvo) return { erro: nomeAlvo ? `alvo não encontrado: ${nomeAlvo}` : 'sem phase nem MVP para medir' };

  const todos = commitsComData(raiz) || [];
  const doAlvo = todos
    .map((c) => ({ ...c, k: classificarCommit(c.assunto) }))
    .filter((c) => c.k && c.k.alvo === alvo.alvo);

  const plan = lerPlan(alvo.art.plan);
  const idsPasso = new Set(plan.passos.map((p) => p.id));
  const commitsPorPasso = {};
  for (const id of idsPasso) commitsPorPasso[id] = 0;

  // Intervalo de cada commit de passo desde o commit anterior do alvo; o primeiro não tem base.
  const intervalos = [];
  let commitsCorrecao = 0;
  doAlvo.forEach((c, i) => {
    const passos = c.k.ids.filter((id) => idsPasso.has(id));
    if (c.k.ids.some((id) => /^R[1-9][0-9]*$/.test(id))) commitsCorrecao++;
    for (const id of passos) commitsPorPasso[id]++;
    if (passos.length && i > 0) intervalos.push({ ids: passos, minutos: minutos(c.ts - doAlvo[i - 1].ts) });
  });

  let ativos = 0;
  for (let i = 1; i < doAlvo.length; i++) {
    const s = doAlvo[i].ts - doAlvo[i - 1].ts;
    if (s <= PAUSA_MIN * 60) ativos += s;
  }
  const lento = intervalos.reduce((m, x) => (!m || x.minutos > m.minutos ? x : m), null);
  const severidade = { Critical: 0, Required: 0, Nit: 0 };
  for (const l of alvo.art.review || []) {
    const m = l.match(RE_R);
    if (m) severidade[m[1]]++;
  }

  return {
    alvo: alvo.alvo,
    rota: alvo.rota,
    commits: doAlvo.length,
    inicio: doAlvo.length ? new Date(doAlvo[0].ts * 1000).toISOString() : null,
    fim: doAlvo.length ? new Date(doAlvo[doAlvo.length - 1].ts * 1000).toISOString() : null,
    horas: doAlvo.length ? horas(doAlvo[doAlvo.length - 1].ts - doAlvo[0].ts) : null,
    horasAtivas: doAlvo.length ? horas(ativos) : null,
    passos: plan.passos.length,
    checkpoints: plan.itens.filter((i) => i.tipo === 'checkpoint').length,
    retrabalho: Object.entries(commitsPorPasso).filter(([, n]) => n > 1).map(([id, n]) => ({ id, commits: n })),
    intervaloMediano: mediana(intervalos.map((x) => x.minutos)),
    passoMaisLento: lento,
    commitsCorrecao,
    rs: severidade,
    etapasReview: (alvo.art.review || []).filter((l) => /^### Etapa\b/.test(l)).length,
  };
}

/** Linha única que o líder copia para a seção Medição do review.md. */
export function linhaMedicao(r) {
  const ret = r.retrabalho.length ? r.retrabalho.map((x) => `${x.id} (${x.commits})`).join(', ') : 'nenhum';
  const lento = r.passoMaisLento ? `${r.passoMaisLento.ids.join(',')} (${r.passoMaisLento.minutos} min)` : '-';
  return [
    `relógio: ${r.horas ?? '-'} h (ativas: ${r.horasAtivas ?? '-'} h) em ${r.commits} commits`,
    `passos: ${r.passos} · checkpoints: ${r.checkpoints}`,
    `intervalo mediano: ${r.intervaloMediano ?? '-'} min · mais lento: ${lento}`,
    `retrabalho: ${ret}`,
    `R*: ${r.rs.Critical} Critical, ${r.rs.Required} Required, ${r.rs.Nit} Nit em ${r.etapasReview} etapas · commits de correção: ${r.commitsCorrecao}`,
  ].join(' · ');
}

function lerArgs(argv) {
  const args = { raiz: process.cwd(), json: false, alvo: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--json') args.json = true;
    else if (a === '--raiz' && argv[i + 1]) args.raiz = argv[++i];
    else if (a === '--alvo' && argv[i + 1]) args.alvo = argv[++i];
    else return { erro: `argumento desconhecido ou sem valor: ${a}` };
  }
  return args;
}

function principal() {
  const args = lerArgs(process.argv.slice(2));
  if (args.erro) { console.error(args.erro); return 2; }
  const r = medir(resolve(args.raiz), args.alvo);
  if (r.erro) { console.error(r.erro); return 2; }
  process.stdout.write(args.json ? `${jsonAscii(r)}\n` : `${r.alvo}: ${linhaMedicao(r)}\n`);
  return 0;
}

if (executadoDireto(import.meta.url)) {
  process.exitCode = principal();
}
