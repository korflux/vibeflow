#!/usr/bin/env node
// estado.mjs: lê o disco e o Git e devolve o estado da phase, a etapa atual e o progresso.
//
// Implementa a tabela "Estado da phase" de references/disco.md, na mesma ordem de
// linhas, e o cálculo de progresso de SKILL.md, seção 9. Só lê; a decisão continua do
// líder. Linha da tabela que depende de julgamento (assunto do pedido) fica de fora.
//
// Uso:
//   node estado.mjs [--alvo phase-N|mvp] [--raiz <dir>] [--json]
// Saída: 0 sem inconsistência, 1 com inconsistência a diagnosticar, 2 em erro de uso.

import { existsSync } from 'node:fs';
import { join, resolve, relative } from 'node:path';
import {
  lerLinhas, cabecalho, secao, carregarAlvos, alvoPadrao, alvoNomeado, listarPhases, proximoN,
  linksNoCaminho, lerTasks, recorte, segmentos, sobrepoe, lerRs, vereditoReview, ultimoAjuste,
  commits, classificarCommit, naoCommitados, naoEnviados, commitQueAdicionou, jsonAscii, executadoDireto,
} from './_disco.mjs';
import { analisarPlan } from './ondas.mjs';

// ---------------------------------------------------------------------------
// Rotas e etapas (tabela de esforço do AGENTS.md)
// ---------------------------------------------------------------------------

const ETAPAS_ROTA = {
  medium: ['implement', 'review'],
  high: ['spec', 'plan', 'implement', 'review'],
  xhigh: ['interview', 'spec', 'plan', 'implement', 'review'],
  max: ['interview', 'spec', 'plan', 'analyze', 'implement', 'review'],
  mvp: ['interview', 'spec', 'plan', 'analyze', 'implement', 'review'],
};
const PLANEJAMENTO = new Set(['interview', 'spec', 'design', 'plan', 'analyze']);

/**
 * Design conta quando há design.md, ou quando o Handoff da spec aponta para design (UI nova).
 * `Design: N/A` registrado no Handoff da spec ou no plan.md tira o design da rota.
 */
function designConta(alvo) {
  if (alvo.art.design) return true;
  const na = /design:\s*(\*\*)?\s*n\/a/i;
  const handoff = secao(alvo.art.spec, 'Handoff').map((l) => l.trim()).filter(Boolean);
  const planNa = (alvo.art.plan || []).some((l) => na.test(l.replace(/\*\*Design:\*\*/i, 'Design:')));
  if (planNa || handoff.some((l) => na.test(l))) return false;
  return /^design\b/i.test(handoff[0] || '');
}

/** Etapas da rota do alvo, com o design inserido depois da spec quando conta. */
function etapasDoAlvo(alvo) {
  const base = ETAPAS_ROTA[alvo.rota] || [];
  if (!designConta(alvo) || !base.includes('spec')) return base;
  const i = base.indexOf('spec');
  return [...base.slice(0, i + 1), 'design', ...base.slice(i + 1)];
}

/** Veredito do analyze na seção `## Veredito`: 'limpo', 'bloqueado' ou null. */
function vereditoAnalyze(alvo) {
  const corpo = secao(alvo.art.analyze, 'Veredito').map((l) => l.trim());
  if (corpo.includes('limpo')) return 'limpo';
  if (corpo.includes('bloqueado')) return 'bloqueado';
  return null;
}

/** Etapa de planejamento concluída: aprovado; no analyze, também veredito limpo. */
function planejamentoConcluido(alvo, etapa) {
  const aprovado = cabecalho(alvo.art[etapa], 'Status') === 'aprovado';
  return etapa === 'analyze' ? aprovado && vereditoAnalyze(alvo) === 'limpo' : aprovado;
}

// ---------------------------------------------------------------------------
// Commits por alvo (references/disco.md, Commits)
// ---------------------------------------------------------------------------

/** Agrupa os commits do contrato por alvo, preservando a posição (0 = mais novo). */
function commitsPorAlvo(lista) {
  const mapa = new Map();
  (lista || []).forEach((c, idx) => {
    const k = classificarCommit(c.assunto);
    if (!k || !k.alvo) return;
    if (!mapa.has(k.alvo)) mapa.set(k.alvo, []);
    mapa.get(k.alvo).push({ ...k, hash: c.hash, idx });
  });
  return mapa;
}

/** IDs (T* e R*) presentes em commits task do alvo. */
function idsCommitados(lista) {
  return new Set((lista || []).filter((c) => c.tipo === 'task').flatMap((c) => c.ids));
}

// ---------------------------------------------------------------------------
// Inconsistências
// ---------------------------------------------------------------------------

function inconsistencias(raiz, alvos, porAlvo, temGit) {
  const achados = [];
  for (const a of alvos) {
    const algumArtefato = Object.values(a.art).some(Boolean);
    if (algumArtefato && !a.rota) achados.push(`${a.alvo}: primeiro artefato sem # Rota:`);
    for (const l of linksNoCaminho(raiz, a.pasta)) achados.push(`${a.alvo}: caminho é link, não escreva através dele: ${relative(raiz, l)}`);
    if (!temGit) continue;
    const ids = idsCommitados(porAlvo.get(a.alvo));
    const tasks = lerTasks(a.art.plan);
    for (const t of tasks) {
      if (t.caixa && !ids.has(t.id)) achados.push(`${a.alvo}: ${t.id} marcada sem commit task(${a.alvo}:...)`);
      if (!t.caixa && ids.has(t.id)) achados.push(`${a.alvo}: ${t.id} com commit e caixa vazia`);
      if (t.caixa && t.estado && t.estado !== 'concluída' && t.estado !== 'concluida') achados.push(`${a.alvo}: ${t.id} com caixa marcada e Estado: ${t.estado}`);
    }
  }
  return achados;
}

// ---------------------------------------------------------------------------
// Linhas globais da tabela (antes do alvo)
// ---------------------------------------------------------------------------

/** Linha 1: task(medium) mais recente sem review.md medium criado depois dele. */
function mediumPendente(raiz, alvos, lista) {
  const iMedium = (lista || []).findIndex((c) => classificarCommit(c.assunto)?.tipo === 'medium');
  if (iMedium < 0) return null;
  const posicao = new Map(lista.map((c, i) => [c.hash, i]));
  const revisado = alvos.some((a) => {
    if (a.rota !== 'medium' || !a.art.review) return false;
    const add = commitQueAdicionou(raiz, relative(raiz, join(a.pasta, 'review.md')).replace(/\\/g, '/'));
    if (add === null) return true; // review.md não commitado conta pela existência
    return posicao.has(add) && posicao.get(add) < iMedium; // commitado depois do task(medium)
  });
  return revisado ? null : lista[iMedium];
}

/** Linha 2: alvos fechados com commits fora do upstream, salvo push adiado ainda válido. */
function pushPendente(alvos, porAlvo, enviar) {
  const pendentes = [];
  for (const a of alvos.filter((x) => x.fechado)) {
    const lista = porAlvo.get(a.alvo) || [];
    if (!lista.length) continue;
    const foraDoUpstream = enviar === null || lista.some((c) => enviar.has(c.hash));
    if (!foraDoUpstream) continue;
    const adiado = (a.art.review || []).some((l) => /^- Push adiado pelo humano:/.test(l));
    const cAdiado = lista.find((c) => c.tipo === 'push-adiado');
    const nadaDepois = cAdiado && !lista.some((c) => c.idx < cAdiado.idx);
    if (adiado && nadaDepois) continue;
    pendentes.push(a.alvo);
  }
  return pendentes;
}

/** Linha 3: alteração não commitada fora de .vibeflow/ sem dono em T* ou R* abertos. */
function semDono(alvos, porAlvo, alterados) {
  const fora = (alterados || []).filter((p) => !p.startsWith('.vibeflow/'));
  if (!fora.length) return [];
  const donos = [];
  for (const a of alvos.filter((x) => !x.fechado || lerRs(x.art.review).some((r) => !r.feito))) {
    for (const t of lerTasks(a.art.plan).filter((x) => !x.caixa)) {
      const r = recorte(t);
      if (r === null) return []; // T* aberta sem Arquivos comparáveis pode ser dona de qualquer path
      donos.push(...r);
    }
    const ids = idsCommitados(porAlvo.get(a.alvo));
    for (const r of lerRs(a.art.review)) {
      if ((!r.feito || !ids.has(r.id)) && r.path) {
        donos.push(segmentos(r.path));
      }
    }
  }
  return fora.filter((p) => !donos.some((d) => sobrepoe(d, segmentos(p))));
}

// ---------------------------------------------------------------------------
// Etapa do alvo (linhas da tabela a partir de "Primeira etapa de planejamento")
// ---------------------------------------------------------------------------

function etapaDoAlvo(alvo, porAlvo, alterados) {
  const etapas = etapasDoAlvo(alvo);
  for (const e of etapas.filter((x) => PLANEJAMENTO.has(x))) {
    if (planejamentoConcluido(alvo, e)) continue;
    if (!alvo.art[e]) return { etapa: e, situacao: 'sem artefato', proximo: e === 'analyze' ? 'Revisor' : 'Líder conduz; redator grava' };
    if (e === 'analyze' && vereditoAnalyze(alvo) === 'bloqueado') return { etapa: 'analyze', situacao: 'correção dos achados', proximo: 'Dono do artefato; revisor reconfere' };
    return { etapa: e, situacao: 'aguardando ajuste ou aprovação', proximo: 'Líder apresenta ao humano' };
  }

  const tasks = lerTasks(alvo.art.plan);
  const abertas = tasks.filter((t) => !t.caixa);
  const recortesAbertos = abertas.map(recorte).filter(Boolean).flat();
  const tocados = (alterados || []).map(segmentos);
  const codigoNasAbertas = tocados.some((p) => recortesAbertos.some((r) => sobrepoe(r, p)));

  if (abertas.some((t) => t.estado === 'em andamento') || codigoNasAbertas) {
    return { etapa: 'implement', situacao: 'retomar a onda', proximo: 'Verificador confere diff e prova afetada; falha vai ao corretor' };
  }
  if (abertas.some((t) => t.estado === 'pronta')) {
    return { etapa: 'implement', situacao: 'validar e commitar a onda', proximo: 'Verificador; finalizador commita' };
  }
  if (abertas.length) {
    const fila = analisarPlan(tasks);
    if (fila.onda.length) return { etapa: 'implement', situacao: 'implementar a próxima onda', proximo: 'Líder monta a onda', onda: fila.onda };
    return { etapa: 'implement', situacao: 'impedimento', proximo: 'Líder leva o impedimento ao humano' };
  }

  const review = alvo.art.review;
  if (!review) {
    if (tasks.length) return { etapa: 'review', situacao: 'sem review.md', proximo: 'Revisor' };
    return { etapa: 'indeterminado', situacao: 'plan sem T*', proximo: 'Diagnóstico delegado' };
  }
  const rs = lerRs(review);
  const status = cabecalho(review, 'Status');
  if (rs.some((r) => !r.feito)) return { etapa: 'implement', situacao: 'corrigir R*', proximo: 'Corretor ou redator, pelo papel:' };
  if (status === 'request-changes') {
    const ids = idsCommitados(porAlvo.get(alvo.alvo));
    const semCommit = rs.filter((r) => r.feito && !ids.has(r.id)).map((r) => r.id);
    if (semCommit.length) return { etapa: 'implement', situacao: `commitar a correção (${semCommit.join(', ')})`, proximo: 'Finalizador, se a prova da correção está verde' };
    return { etapa: 'review', situacao: 're-review', proximo: 'Revisor' };
  }
  if (status === 'rascunho') {
    const veredito = vereditoReview(review);
    if (veredito === 'approve') return { etapa: 'implement', situacao: 'confirmar', proximo: 'Líder pede a confirmação única' };
    if (veredito === null) return { etapa: 'review', situacao: 'retomar', proximo: 'Revisor' };
  }
  return { etapa: 'indeterminado', situacao: `review.md em ${status || 'status ausente'}`, proximo: 'Diagnóstico delegado' };
}

// ---------------------------------------------------------------------------
// Progresso (SKILL.md, seção 9)
// ---------------------------------------------------------------------------

function progresso(alvo) {
  const ajuste = ultimoAjuste(alvo.art.review);
  if (ajuste && ajuste.length) {
    const rs = lerRs(alvo.art.review).filter((r) => ajuste.includes(r.id));
    if (rs.some((r) => !r.feito)) return { ajuste: `${rs.filter((r) => r.feito).length}/${rs.length}` };
  }
  const etapas = etapasDoAlvo(alvo);
  if (!etapas.length) return { percentual: null };
  const tasks = lerTasks(alvo.art.plan);
  const total = tasks.length;
  const feitas = tasks.filter((t) => t.caixa).length;
  // Soma em inteiros para arredondar para baixo sem erro de ponto flutuante:
  // cada etapa vale `den` unidades; o implement vale a fração de T* concluídas.
  const den = total || 1;
  let soma = 0;
  for (const e of etapas) {
    if (PLANEJAMENTO.has(e)) soma += planejamentoConcluido(alvo, e) ? den : 0;
    else if (e === 'implement') soma += alvo.rota === 'medium' ? den : (total ? feitas : 0);
    else if (e === 'review') soma += alvo.fechado ? den : 0;
  }
  return { percentual: Math.floor((soma * 100) / (den * etapas.length)), tasks: total ? `${feitas}/${total}` : null };
}

// ---------------------------------------------------------------------------
// Execução
// ---------------------------------------------------------------------------

function lerArgs(argv) {
  const args = { raiz: process.cwd(), alvo: null, json: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--json') args.json = true;
    else if ((a === '--raiz' || a === '--alvo') && argv[i + 1]) args[a.slice(2)] = argv[++i];
    else return { erro: `argumento desconhecido ou sem valor: ${a}` };
  }
  return args;
}

/** Monta o relatório completo; exportado para os testes. */
export function estado(raiz, nomeAlvo = null) {
  const agents = lerLinhas(join(raiz, 'AGENTS.md'));
  const governanca = {
    vibeflow: existsSync(join(raiz, '.vibeflow')),
    agents: Boolean(agents && agents.some((l) => l.trim())),
    blocoCadeia: Boolean(agents && agents.some((l) => l.includes('VIBEFLOW:CADEIA start')) && agents.some((l) => l.includes('VIBEFLOW:CADEIA end'))),
  };
  const alvos = carregarAlvos(raiz);
  const lista = commits(raiz);
  const temGit = lista !== null;
  const porAlvo = commitsPorAlvo(lista);
  const alterados = temGit ? naoCommitados(raiz) : null;
  const enviar = temGit ? naoEnviados(raiz) : null;

  const rel = {
    raiz,
    governanca,
    git: temGit,
    proximoN: proximoN(listarPhases(raiz)),
    alvos: alvos.map((a) => ({ alvo: a.alvo, pasta: relative(raiz, a.pasta).replace(/\\/g, '/'), rota: a.rota, fechado: a.fechado })),
    inconsistencias: inconsistencias(raiz, alvos, porAlvo, temGit),
    alvo: null,
    etapa: null,
    progresso: null,
  };

  const nomeado = nomeAlvo ? alvoNomeado(alvos, nomeAlvo) : null;
  if (nomeAlvo && !nomeado) return { ...rel, erro: `alvo não encontrado: ${nomeAlvo}` };

  // Linhas globais da tabela, na ordem de references/disco.md.
  const abertos = alvos.filter((a) => !a.fechado);
  const medium = temGit ? mediumPendente(raiz, alvos, lista) : null;
  const pushes = temGit && !abertos.some((a) => a.n !== null) ? pushPendente(alvos, porAlvo, enviar) : [];
  const orfaos = temGit ? semDono(alvos, porAlvo, alterados) : [];
  if (!nomeado && medium) rel.etapa = { etapa: 'review da entrega medium', situacao: medium.assunto, proximo: 'Revisor' };
  else if (!nomeado && pushes.length) rel.etapa = { etapa: 'push pendente', situacao: pushes.join(', '), proximo: 'Finalizador, com a confirmação humana' };
  else if (!nomeado && orfaos.length) rel.etapa = { etapa: 'alteração sem dono', situacao: orfaos.join(', '), proximo: 'Líder pergunta ao humano se retoma a entrega ou isola o trabalho' };

  const alvo = nomeado || alvoPadrao(alvos);
  if (alvo) {
    rel.alvo = { alvo: alvo.alvo, pasta: relative(raiz, alvo.pasta).replace(/\\/g, '/'), rota: alvo.rota, fechado: alvo.fechado };
    rel.artefatos = Object.fromEntries(Object.entries(alvo.art).filter(([, v]) => v).map(([k, v]) => [k, cabecalho(v, 'Status') || 'sem status']));
    rel.rAbertos = lerRs(alvo.art.review).filter((r) => !r.feito).map((r) => r.id);
    rel.progresso = progresso(alvo);
    if (!rel.etapa) rel.etapa = alvo.fechado ? { etapa: 'fechada', situacao: 'phase fechada', proximo: 'Líder' } : etapaDoAlvo(alvo, porAlvo, alterados);
    if (abertos.filter((a) => a.n !== null).length > 1 && !nomeado) rel.aviso = 'mais de uma phase aberta: pergunte qual retomar, recomendando a de maior n';
  } else if (!rel.etapa) {
    rel.etapa = { etapa: 'classificar o pedido', situacao: 'sem phase aberta', proximo: 'Líder' };
  }
  if (!governanca.vibeflow || !governanca.agents || !governanca.blocoCadeia) {
    rel.init = 'rota com phase passa antes pelo init (falta .vibeflow/, AGENTS.md ou bloco VIBEFLOW:CADEIA)';
  }
  return rel;
}

function texto(r) {
  const l = [];
  if (r.alvo) l.push(`alvo: ${r.alvo.alvo} (${r.alvo.pasta}) · rota: ${r.alvo.rota || 'ausente'}${r.alvo.fechado ? ' · fechada' : ''}`);
  if (r.artefatos) l.push(`artefatos: ${Object.entries(r.artefatos).map(([k, v]) => `${k} ${v}`).join(', ') || 'nenhum'}`);
  const p = r.progresso;
  const prog = p ? (p.ajuste ? `ajuste: R* ${p.ajuste}` : p.percentual === null ? 'progresso: sem rota' : `progresso: ${p.percentual}%`) : null;
  const tks = p && p.tasks ? ` · T* ${p.tasks} concluídas` : '';
  l.push(`${prog ? `${prog} · ` : ''}etapa: ${r.etapa.etapa}, ${r.etapa.situacao}${tks} · próximo: ${r.etapa.proximo}`);
  if (r.etapa.onda) l.push(`próxima onda: ${r.etapa.onda.join(', ')}`);
  if (r.rAbertos && r.rAbertos.length) l.push(`R* abertos: ${r.rAbertos.join(', ')}`);
  if (r.aviso) l.push(`aviso: ${r.aviso}`);
  if (r.init) l.push(`init: ${r.init}`);
  if (!r.git) l.push('git: indisponível; linhas de commit, push e alteração não avaliadas');
  for (const i of r.inconsistencias) l.push(`inconsistência: ${i}`);
  l.push(`próxima phase: phase-${r.proximoN}-<slug>`);
  return `${l.join('\n')}\n`;
}

function principal() {
  const args = lerArgs(process.argv.slice(2));
  if (args.erro) { console.error(args.erro); return 2; }
  const r = estado(resolve(args.raiz), args.alvo);
  if (r.erro) { console.error(r.erro); return 2; }
  process.stdout.write(args.json ? `${jsonAscii(r)}\n` : texto(r));
  return r.inconsistencias.length ? 1 : 0;
}

if (executadoDireto(import.meta.url)) {
  process.exitCode = principal();
}
