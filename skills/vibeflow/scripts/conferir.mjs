#!/usr/bin/env node
// conferir.mjs: confere, para o líder, o recorte de um passo e o commit antes de criá-lo.
//
// Dois modos, ambos somente leitura:
//   --passo <ids>     compara as alterações não commitadas com os `Arquivos:` dos passos
//                     (ou os paths dos R*) indicados: Conferência do líder de
//                     references/delegation.md e passo 3 de references/implement.md.
//   --commit <msg>    confere a mensagem e o índice antes do commit: formatos de
//                     references/disco.md (Commits), caixas e R* marcados no índice,
//                     paths em staging dentro do recorte e `git diff --cached --check`
//                     limpo (references/implement.md, passo 4).
// Não faz staging nem commit e não decide nada: devolve achados para o líder. Divergência
// entre este script e a prosa é bug do script.
//
// Uso:
//   node conferir.mjs --passo 2a,2b [--alvo phase-N|mvp] [--raiz <dir>] [--json]
//   node conferir.mjs --commit "<mensagem>" [--raiz <dir>] [--json]
//   node conferir.mjs --commit-arquivo <path da mensagem> [--raiz <dir>] [--json]
// Saída: 0 sem achado, 1 com achado, 2 em erro de uso.

import { readFileSync, existsSync } from 'node:fs';
import { resolve, relative } from 'node:path';
import {
  carregarAlvos, alvoPadrao, alvoNomeado, lerPlan, lerRs, recorte, normalizarPath, segmentos, dentroDoRecorte,
  classificarCommit, naoCommitados, emStaging, linhasNoGit, gitComCodigo, jsonAscii, executadoDireto,
} from './_disco.mjs';

// Pastas que nunca são código do passo: artefatos da cadeia e registros de achado fora do
// recorte (references/disco.md, Estado da phase e Glossário).
const FORA_DO_CODIGO = ['.vibeflow/', '.erros-encontrados/'];
// Paths que o commit `chore(init): ...` pode levar (references/init.md, passo 6).
const PATHS_INIT = ['AGENTS.md', '.agents/rules/vibeflow.md', '.vibeflow/phases/.gitkeep', '.vibeflow/old/'];

const relPasta = (raiz, alvo) => relative(raiz, alvo.pasta).replace(/\\/g, '/');
const dentroDePrefixo = (path, prefixos) => prefixos.some((p) => (p.endsWith('/') ? path.startsWith(p) : path === p));

// ---------------------------------------------------------------------------
// Recorte dos IDs (references/disco.md, Plan > Arquivos; R* em templates/review.md)
// ---------------------------------------------------------------------------

/**
 * Recorte combinado de uma lista de IDs de passo (`2a`) e de R* (`R1`).
 * Devolve { recortes, achados, avisos }; um ID sem recorte comparável vira aviso, porque a
 * conferência de paths fica indisponível para ele, não errada.
 */
function recorteDosIds(ids, passos, rs) {
  const recortes = [];
  const achados = [];
  const avisos = [];
  for (const id of ids) {
    if (/^R[1-9][0-9]*$/.test(id)) {
      const r = rs.find((x) => x.id === id);
      if (!r) { achados.push(`${id} não existe no review.md do alvo`); continue; }
      const norm = r.path ? normalizarPath(r.path) : null;
      if (!norm) avisos.push(`${id} sem path comparável: confira o recorte dele pelo relatório`);
      else recortes.push(norm);
      continue;
    }
    const p = passos.find((x) => x.id === id);
    if (!p) { achados.push(`passo ${id} não existe no plan.md do alvo`); continue; }
    const rec = recorte(p);
    if (!rec) avisos.push(`passo ${id} sem Arquivos: comparáveis: confira o recorte dele pelo relatório`);
    else recortes.push(...rec);
  }
  return { recortes, achados, avisos };
}

// ---------------------------------------------------------------------------
// Modo --passo
// ---------------------------------------------------------------------------

/** Alterações não commitadas fora de .vibeflow/ e .erros-encontrados/ comparadas ao recorte dos IDs. */
export function conferirPasso(raiz, ids, nomeAlvo = null) {
  const alvos = carregarAlvos(raiz);
  const alvo = nomeAlvo ? alvoNomeado(alvos, nomeAlvo) : alvoPadrao(alvos);
  if (!alvo) return { erro: nomeAlvo ? `alvo não encontrado: ${nomeAlvo}` : 'sem alvo aberto; informe --alvo' };
  const alterados = naoCommitados(raiz);
  if (alterados === null) return { erro: 'git indisponível na raiz' };

  const { recortes, achados, avisos } = recorteDosIds(ids, lerPlan(alvo.art.plan).passos, lerRs(alvo.art.review));
  const codigo = alterados.filter((p) => !dentroDePrefixo(p, FORA_DO_CODIGO));
  // Sem nenhum recorte comparável, não há contra o que julgar: só os avisos valem.
  const fora = recortes.length ? codigo.filter((p) => !dentroDoRecorte(segmentos(p), recortes)) : [];
  for (const p of fora) achados.push(`path fora do recorte: ${p}`);
  if (!codigo.length) avisos.push('nenhuma alteração de código ou teste fora de .vibeflow/ e .erros-encontrados/');
  return { modo: 'passo', alvo: alvo.alvo, ids, alterados: codigo, achados, avisos };
}

// ---------------------------------------------------------------------------
// Modo --commit
// ---------------------------------------------------------------------------

/** IDs com a caixa marcada: passos de um plan ou R* de um review. */
const marcados = (lista) => new Set(lista.filter((x) => x.caixa ?? x.feito).map((x) => x.id));

/**
 * Confere caixas (ou R*) no índice contra os IDs da mensagem: todo ID citado está marcado
 * no índice, e toda marcação nova no índice (aberta no HEAD) está citada. ID já marcado
 * no HEAD é aceito: é a correção devolvida pelo checkpoint (references/disco.md, Commits).
 */
function conferirMarcacoes(ids, noIndice, noHead, rotulo) {
  const achados = [];
  const indice = marcados(noIndice);
  const head = marcados(noHead);
  for (const id of ids) if (!indice.has(id)) achados.push(`${id} citado na mensagem, mas ${rotulo} aberto no índice (marque e faça staging do artefato)`);
  for (const id of indice) if (!head.has(id) && !ids.includes(id)) achados.push(`${id} marcado no índice e ausente da mensagem`);
  return achados;
}

/** Confere uma mensagem de commit e o índice atual contra o contrato. */
export function conferirCommit(raiz, mensagem) {
  const achados = [];
  const avisos = [];
  const assunto = (mensagem.replace(/^﻿/, '').split(/\r?\n/)[0] || '').trim();
  if (/co-authored-by/i.test(mensagem)) achados.push('mensagem com Co-Authored-By');

  const tipo = classificarCommit(assunto) || (/^chore\(init\): /.test(assunto) ? { tipo: 'init', alvo: null, ids: [] } : null);
  if (!tipo) achados.push(`assunto fora dos formatos de references/disco.md (Commits): ${assunto || '(vazio)'}`);
  else if (!/\): \S/.test(assunto)) achados.push('assunto sem o resultado depois de "): "');

  const staging = emStaging(raiz);
  if (staging === null) return { erro: 'git indisponível na raiz' };
  if (!staging.length) achados.push('nada em staging');
  const check = gitComCodigo(raiz, ['diff', '--cached', '--check']);
  if (check.codigo !== 0) achados.push(`git diff --cached --check acusou: ${check.out.trim().split(/\r?\n/).slice(0, 3).join(' | ') || 'erro'}`);

  let permitidos = null; // null: sem recorte no disco para conferir os paths
  let recortes = [];
  if (tipo && (tipo.tipo === 'task' || tipo.tipo === 'finalize' || tipo.tipo === 'push-adiado')) {
    const alvo = alvoNomeado(carregarAlvos(raiz), tipo.alvo);
    if (!alvo) {
      achados.push(`alvo ${tipo.alvo} não existe no disco`);
    } else {
      const pasta = relPasta(raiz, alvo);
      permitidos = [`${pasta}/`, '.erros-encontrados/'];
      if (tipo.tipo === 'task') {
        // O recorte vem do artefato na árvore de trabalho (a definição do passo); as
        // marcações vêm do índice e do HEAD, porque é o índice que vira commit. Artefato
        // fora do índice, como o plan.md ainda não commitado e sem staging, conta como
        // tudo aberto e acusa a falta de staging.
        const planIdx = lerPlan(linhasNoGit(raiz, '', `${pasta}/plan.md`)).passos;
        const planHead = lerPlan(linhasNoGit(raiz, 'HEAD', `${pasta}/plan.md`)).passos;
        const rsIdx = lerRs(linhasNoGit(raiz, '', `${pasta}/review.md`));
        const rsHead = lerRs(linhasNoGit(raiz, 'HEAD', `${pasta}/review.md`));
        const planArvore = lerPlan(alvo.art.plan).passos;
        const idsPasso = tipo.ids.filter((id) => !/^R/.test(id));
        const idsR = tipo.ids.filter((id) => /^R/.test(id));
        if (!tipo.ids.length) achados.push('task sem IDs de passo ou de R*');

        const r = recorteDosIds(tipo.ids, planArvore, lerRs(alvo.art.review));
        achados.push(...r.achados);
        avisos.push(...r.avisos);
        recortes = r.recortes;
        if (r.avisos.length) permitidos = null; // um ID sem recorte deixa o conjunto indefinido

        const ordem = planArvore.map((p) => p.id).filter((id) => idsPasso.includes(id));
        if (ordem.length === idsPasso.length && ordem.join() !== idsPasso.join()) achados.push(`IDs fora da ordem do plan: esperado ${ordem.join(',')}`);
        achados.push(...conferirMarcacoes(idsPasso, planIdx, planHead, 'caixa'));
        achados.push(...conferirMarcacoes(idsR, rsIdx, rsHead, 'R*'));
      } else {
        permitidos.push('AGENTS.md');
      }
    }
  } else if (tipo && tipo.tipo === 'init') {
    permitidos = PATHS_INIT;
  } else if (tipo) {
    avisos.push(`entrega ${tipo.tipo} sem recorte no disco: confira o staging contra o brief`);
  }

  if (permitidos) {
    for (const p of staging) {
      if (!dentroDePrefixo(p, permitidos) && !dentroDoRecorte(segmentos(p), recortes)) achados.push(`path em staging fora do recorte: ${p}`);
    }
  }
  return { modo: 'commit', assunto, tipo: tipo ? tipo.tipo : null, staging, achados, avisos };
}

// ---------------------------------------------------------------------------
// Execução
// ---------------------------------------------------------------------------

function lerArgs(argv) {
  const args = { raiz: process.cwd(), alvo: null, json: false, passo: null, commit: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--json') args.json = true;
    else if (['--raiz', '--alvo', '--passo', '--commit', '--commit-arquivo'].includes(a) && argv[i + 1] !== undefined) {
      const v = argv[++i];
      if (a === '--commit-arquivo') {
        if (!existsSync(v)) return { erro: `arquivo de mensagem não encontrado: ${v}` };
        args.commit = readFileSync(v, 'utf8');
      } else {
        args[a.slice(2)] = v;
      }
    } else return { erro: `argumento desconhecido ou sem valor: ${a}` };
  }
  if ((args.passo === null) === (args.commit === null)) return { erro: 'use exatamente um modo: --passo <ids> ou --commit <mensagem>' };
  if (args.passo !== null) {
    args.ids = args.passo.split(',').map((s) => s.trim()).filter(Boolean);
    if (!args.ids.length) return { erro: '--passo sem IDs' };
  }
  return args;
}

function texto(r) {
  const l = [r.modo === 'passo' ? `alvo: ${r.alvo} · passos: ${r.ids.join(', ')} · alterados: ${r.alterados.length}` : `commit: ${r.assunto} · staging: ${r.staging.length} path(s)`];
  for (const a of r.achados) l.push(`achado: ${a}`);
  for (const a of r.avisos) l.push(`aviso: ${a}`);
  if (!r.achados.length) l.push('sem achado');
  return `${l.join('\n')}\n`;
}

function principal() {
  const args = lerArgs(process.argv.slice(2));
  if (args.erro) { console.error(args.erro); return 2; }
  const raiz = resolve(args.raiz);
  const r = args.passo !== null ? conferirPasso(raiz, args.ids, args.alvo) : conferirCommit(raiz, args.commit);
  if (r.erro) { console.error(r.erro); return 2; }
  process.stdout.write(args.json ? `${jsonAscii(r)}\n` : texto(r));
  return r.achados.length ? 1 : 0;
}

if (executadoDireto(import.meta.url)) {
  process.exitCode = principal();
}
