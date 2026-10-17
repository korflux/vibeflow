// _disco.mjs: leitura compartilhada do disco do VibeFlow pelos scripts estado e ondas.
//
// Responsabilidade: transformar artefatos (.md) e Git em dados, aplicando as regras
// mecânicas de references/disco.md e references/plan.md. Não decide etapa nem escreve
// nada: só lê. O contrato continua sendo a prosa; divergência entre este módulo e a
// prosa é bug deste módulo.
//
// Compatibilidade: somente módulos nativos do Node 18+, git chamado com argumentos em
// lista (sem shell), leitura tolerante a CRLF e BOM, caminhos via node:path.

import { readFileSync, existsSync, readdirSync, statSync, lstatSync, realpathSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

// ---------------------------------------------------------------------------
// Arquivos de texto
// ---------------------------------------------------------------------------

/** Lê um arquivo de texto como linhas, sem BOM e sem \r; devolve null se não existe. */
export function lerLinhas(caminho) {
  if (!existsSync(caminho)) return null;
  const texto = readFileSync(caminho, 'utf8').replace(/^﻿/, '');
  return texto.split(/\r?\n/);
}

/** Valor de uma linha de cabeçalho `# Nome: valor` (Status, Rota, Alvo) ou null. */
export function cabecalho(linhas, nome) {
  if (!linhas) return null;
  const re = new RegExp(`^# ${nome}:\\s*(.+?)\\s*$`);
  for (const l of linhas) {
    const m = l.match(re);
    if (m) return m[1];
  }
  return null;
}

/** Corpo de uma seção `## Titulo` até a próxima `## `, sem comentários HTML de linha. */
export function secao(linhas, titulo) {
  if (!linhas) return [];
  const ini = linhas.findIndex((l) => l.trim() === `## ${titulo}`);
  if (ini < 0) return [];
  const corpo = [];
  for (let i = ini + 1; i < linhas.length && !linhas[i].startsWith('## '); i++) {
    if (!/^\s*<!--.*-->\s*$/.test(linhas[i])) corpo.push(linhas[i]);
  }
  return corpo;
}

// ---------------------------------------------------------------------------
// Phases e MVP (references/disco.md, Paths e Abrir phase)
// ---------------------------------------------------------------------------

export const ARTEFATOS = ['interview', 'spec', 'design', 'plan', 'analyze', 'review'];
const RE_PHASE = /^phase-([1-9][0-9]*)-([a-z0-9]+(?:-[a-z0-9]+)*)$/;

/** Slug válido: a-z, 0-9 e hífen simples, sem hífen nas pontas, 2 a 48 caracteres. */
export function slugValido(slug) {
  return slug.length >= 2 && slug.length <= 48 && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug);
}

/** Pastas de phase no padrão, ordenadas por n numérico; pastas fora do padrão não contam. */
export function listarPhases(raiz) {
  const dir = join(raiz, '.vibeflow', 'phases');
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .map((nome) => ({ nome, m: nome.match(RE_PHASE) }))
    .filter(({ nome, m }) => m && slugValido(m[2]) && statSync(join(dir, nome)).isDirectory())
    .map(({ nome, m }) => ({ alvo: `phase-${m[1]}`, n: Number(m[1]), pasta: join(dir, nome), nome }))
    .sort((a, b) => a.n - b.n);
}

/** Próximo n: maior existente mais 1, em ordem numérica; sem phases, 1. */
export function proximoN(phases) {
  return phases.length ? phases[phases.length - 1].n + 1 : 1;
}

/** Carrega um alvo (phase ou MVP): linhas de cada artefato presente, rota e se está fechado. */
export function carregarAlvo(alvo, pasta, nome) {
  const art = {};
  for (const a of ARTEFATOS) art[a] = lerLinhas(join(pasta, `${a}.md`));
  // A rota fica no primeiro artefato: interview, spec ou review, conforme a rota.
  const rota = ['interview', 'spec', 'review'].map((a) => cabecalho(art[a], 'Rota')).find(Boolean) || null;
  const statusReview = cabecalho(art.review, 'Status');
  const rAbertos = lerRs(art.review).filter((r) => !r.feito);
  const fechado = statusReview === 'aprovado' && rAbertos.length === 0;
  return { alvo, pasta, nome, art, rota, fechado };
}

/** Todos os alvos do disco: MVP (se existir) e phases em ordem numérica. */
export function carregarAlvos(raiz) {
  const alvos = listarPhases(raiz).map((p) => ({ ...carregarAlvo(p.alvo, p.pasta, p.nome), n: p.n }));
  const mvp = join(raiz, '.vibeflow', 'mvp');
  if (existsSync(mvp) && statSync(mvp).isDirectory()) alvos.unshift({ ...carregarAlvo('mvp', mvp, 'mvp'), n: null });
  return alvos;
}

/** Alvo padrão: phase aberta de maior n; sem phase aberta, o MVP aberto; senão null. */
export function alvoPadrao(alvos) {
  const phasesAbertas = alvos.filter((a) => a.n !== null && !a.fechado);
  if (phasesAbertas.length) return phasesAbertas[phasesAbertas.length - 1];
  return alvos.find((a) => a.n === null && !a.fechado) || null;
}

/** Resolve `phase-N` ou `mvp` informado pelo humano; null se não existe. */
export function alvoNomeado(alvos, nome) {
  return alvos.find((a) => a.alvo === nome || a.nome === nome) || null;
}

/** Caminhos do alvo que são link (proibido escrever através deles). */
export function linksNoCaminho(raiz, pasta) {
  const candidatos = [join(raiz, '.vibeflow'), join(raiz, '.vibeflow', 'phases'), join(raiz, '.vibeflow', 'mvp'), pasta];
  return candidatos.filter((c) => existsSync(c) && lstatSync(c).isSymbolicLink());
}

// ---------------------------------------------------------------------------
// Plan: T* (references/plan.md, passo 1, e templates/plan.md)
// ---------------------------------------------------------------------------

/**
 * Lê as T* do plan. Cada bloco começa em `### Tn:` e termina no próximo `### ` ou `## `.
 * Só a primeira linha `- **Arquivos:**` conta, e só o texto entre crases.
 */
export function lerTasks(linhasPlan) {
  if (!linhasPlan) return [];
  const tasks = [];
  let atual = null;
  for (const l of linhasPlan) {
    const cab = l.match(/^### T([1-9][0-9]*):\s*(.*)$/);
    if (cab) {
      atual = { id: `T${cab[1]}`, num: Number(cab[1]), titulo: cab[2].trim(), caixa: false, estado: null, deps: [], arquivos: null };
      tasks.push(atual);
      continue;
    }
    if (/^##+ /.test(l)) { atual = null; continue; }
    if (!atual) continue;
    if (new RegExp(`^- \\[[xX]\\] ${atual.id} concluída`).test(l)) atual.caixa = true;
    const est = l.match(/^- \*\*Estado:\*\*\s*(.+?)\s*$/);
    if (est && atual.estado === null) atual.estado = est[1].toLowerCase();
    const deps = l.match(/^- \*\*Deps:\*\*\s*(.*)$/);
    if (deps) atual.deps = [...deps[1].matchAll(/\bT([1-9][0-9]*)\b/g)].map((d) => `T${d[1]}`);
    const arq = l.match(/^- \*\*Arquivos:\*\*\s*(.*)$/);
    if (arq && atual.arquivos === null) atual.arquivos = [...arq[1].matchAll(/`([^`]*)`/g)].map((a) => a[1]);
  }
  return tasks;
}

// ---------------------------------------------------------------------------
// Arquivos: normalização e sobreposição (references/plan.md, passo 1.3)
// ---------------------------------------------------------------------------

const RAIZ = Object.freeze([]);

/**
 * Normaliza um path de `Arquivos:` em segmentos comparáveis, ou null se incomparável.
 * Raiz inteira é a lista vazia. Barra invertida vira barra, para tolerar autoria no Windows.
 */
export function normalizarPath(bruto) {
  let p = bruto.replace(/\\/g, '/');
  // Incomparável: fora do ASCII, absoluto, caracteres reservados do Windows.
  if (/[^\x20-\x7E]/.test(p) || p.startsWith('/') || /[:<>"|]/.test(p)) return null;
  const segs = p.split('/');
  if (segs.some((s) => s !== '.' && s !== '..' && /[. ]$/.test(s))) return null;
  // Curinga vale como prefixo do diretório anterior a ele.
  const iCuringa = p.search(/[*?[]/);
  if (iCuringa >= 0) {
    const antes = p.slice(0, iCuringa);
    p = antes.includes('/') ? antes.slice(0, antes.lastIndexOf('/')) : '';
  }
  const saida = [];
  for (const s of p.split('/')) {
    if (s === '' || s === '.') continue;
    if (s === '..') {
      if (!saida.length) return RAIZ; // escapa da raiz: vale como a raiz inteira
      saida.pop();
      continue;
    }
    saida.push(s);
  }
  return saida.length ? saida : RAIZ;
}

/** Recorte de uma T*: lista de paths normalizados, ou null se sem Arquivos ou com path incomparável. */
export function recorte(task) {
  if (!task.arquivos || !task.arquivos.length) return null;
  const norm = task.arquivos.map(normalizarPath);
  return norm.some((n) => n === null) ? null : norm;
}

const minusculaAscii = (s) => s.replace(/[A-Z]/g, (c) => c.toLowerCase());

/** Dois paths se sobrepõem quando são iguais ou um é prefixo de diretório do outro. */
export function sobrepoe(a, b) {
  const n = Math.min(a.length, b.length);
  for (let i = 0; i < n; i++) if (minusculaAscii(a[i]) !== minusculaAscii(b[i])) return false;
  return true;
}

/** Dois recortes se sobrepõem quando algum par de paths se sobrepõe. */
export function recortesSobrepoem(ra, rb) {
  return ra.some((a) => rb.some((b) => sobrepoe(a, b)));
}

// ---------------------------------------------------------------------------
// Review: R* e veredito (templates/review.md)
// ---------------------------------------------------------------------------

/** R* do review.md com marcação, path citado e linha de origem. */
export function lerRs(linhasReview) {
  if (!linhasReview) return [];
  const rs = [];
  for (const l of linhasReview) {
    const m = l.match(/^- \[([ xX])\] R([1-9][0-9]*):(.*)$/);
    if (!m) continue;
    const path = (m[3].match(/`([^`]+)`/) || [])[1] || null;
    rs.push({ id: `R${m[2]}`, num: Number(m[2]), feito: m[1] !== ' ', path });
  }
  return rs;
}

/** Proposta marcada no Veredito vigente: 'approve', 'request-changes' ou null. */
export function vereditoReview(linhasReview) {
  const corpo = secao(linhasReview, 'Veredito vigente');
  if (corpo.some((l) => /^- \[[xX]\] \*\*Approve\*\*/.test(l))) return 'approve';
  if (corpo.some((l) => /^- \[[xX]\] \*\*Request changes\*\*/.test(l))) return 'request-changes';
  return null;
}

/** R* abertos pela última etapa `### Ajuste N`, ou null sem ajuste. */
export function ultimoAjuste(linhasReview) {
  if (!linhasReview) return null;
  let ids = null;
  let dentro = false;
  for (const l of linhasReview) {
    if (/^### Ajuste\b/.test(l)) { dentro = true; ids = []; continue; }
    if (/^##+ /.test(l)) { dentro = false; continue; }
    const m = dentro && l.match(/Abriu:\s*(.*)$/);
    if (m) ids.push(...[...m[1].matchAll(/\bR([1-9][0-9]*)\b/g)].map((r) => `R${r[1]}`));
  }
  return ids;
}

// ---------------------------------------------------------------------------
// Git (somente leitura)
// ---------------------------------------------------------------------------

/** Executa git com argumentos em lista; devolve stdout ou null em erro. */
export function git(raiz, args) {
  try {
    return execFileSync('git', args, { cwd: raiz, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] });
  } catch {
    return null;
  }
}

/** Commits do branch atual, do mais novo ao mais antigo: { hash, assunto }. */
export function commits(raiz) {
  const out = git(raiz, ['log', '--format=%H%x09%s']);
  if (out === null) return null;
  return out.split(/\r?\n/).filter(Boolean).map((l) => {
    const [hash, ...resto] = l.split('\t');
    return { hash, assunto: resto.join('\t') };
  });
}

/**
 * Classifica o assunto de um commit pelos formatos de references/disco.md (Commits).
 * Devolve { tipo, alvo, ids } ou null para commit fora do contrato.
 */
export function classificarCommit(assunto) {
  let m = assunto.match(/^task\(((?:phase-[1-9][0-9]*)|mvp):([^)]*)\):/);
  if (m) return { tipo: 'task', alvo: m[1], ids: m[2].split(',').map((s) => s.trim()).filter(Boolean) };
  m = assunto.match(/^task\((medium|express)\):/);
  if (m) return { tipo: m[1], alvo: null, ids: [] };
  m = assunto.match(/^chore\(((?:phase-[1-9][0-9]*)|mvp)\): (finalize review|push adiado)/);
  if (m) return { tipo: m[2] === 'push adiado' ? 'push-adiado' : 'finalize', alvo: m[1], ids: [] };
  return null;
}

/** Paths alterados e não commitados (inclui não rastreados), relativos à raiz, com barra. */
export function naoCommitados(raiz) {
  const out = git(raiz, ['status', '--porcelain', '-z', '--untracked-files=all']);
  if (out === null) return null;
  const itens = out.split('\0').filter(Boolean);
  const paths = [];
  for (let i = 0; i < itens.length; i++) {
    const cod = itens[i].slice(0, 2);
    paths.push(itens[i].slice(3));
    if (cod.includes('R') || cod.includes('C')) i++; // renomeação traz o path antigo em seguida
  }
  return paths;
}

/** Hashes ainda não enviados ao upstream; null quando o branch não tem upstream. */
export function naoEnviados(raiz) {
  if (git(raiz, ['rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}']) === null) return null;
  const out = git(raiz, ['rev-list', '@{u}..HEAD']);
  return new Set((out || '').split(/\r?\n/).filter(Boolean));
}

/** Hash do commit que adicionou um arquivo, ou null se nunca commitado. */
export function commitQueAdicionou(raiz, caminhoRelativo) {
  const out = git(raiz, ['log', '--diff-filter=A', '--format=%H', '--', caminhoRelativo]);
  if (!out) return null;
  const linhas = out.split(/\r?\n/).filter(Boolean);
  return linhas[linhas.length - 1] || null;
}

// ---------------------------------------------------------------------------
// Execução direta e saída
// ---------------------------------------------------------------------------

/**
 * Verdadeiro quando o módulo foi chamado direto pelo node, e não importado por um teste.
 * Resolve links e, no Windows, compara sem caixa (letra do drive pode vir c: ou C:).
 */
export function executadoDireto(importMetaUrl) {
  if (!process.argv[1]) return false;
  const real = (p) => { try { return realpathSync(p); } catch { return resolve(p); } };
  const a = real(process.argv[1]);
  const b = real(fileURLToPath(importMetaUrl));
  return process.platform === 'win32' ? a.toLowerCase() === b.toLowerCase() : a === b;
}

/** JSON com não-ASCII escapado, legível em qualquer codepage de console (Windows incluso). */
export function jsonAscii(valor) {
  return JSON.stringify(valor, null, 2).replace(/[\u007F-￿]/g, (c) => `\\u${c.charCodeAt(0).toString(16).padStart(4, '0')}`);
}
