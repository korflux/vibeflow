#!/usr/bin/env node
// estado.mjs: lê o disco e o Git e devolve o estado da phase, a etapa atual, o progresso
// e o próximo passo ou grupo paralelo.
//
// Implementa a tabela "Estado da phase" de references/disco.md, na mesma ordem de
// linhas, e o cálculo de progresso de SKILL.md, seção 9. Só lê; a decisão continua do
// líder. Linha da tabela que depende de julgamento (assunto do pedido) fica de fora.
// Divergência entre este script e a prosa do disco.md é bug do script.
//
// Uso:
//   node estado.mjs [--alvo phase-N|mvp] [--raiz <dir>] [--json] [--slug "<frase>"] [--linha]
// --slug normaliza a frase pela regra de references/disco.md (Abrir phase) e devolve o path
// da próxima phase; frase que não vira slug válido é erro de uso. --linha imprime só uma
// linha de progresso, vazia fora de um repo com .vibeflow/, para a statusline do host.
// Saída: 0 sem inconsistência, 1 com inconsistência a diagnosticar, 2 em erro de uso.

import { existsSync } from 'node:fs';
import { join, resolve, relative } from 'node:path';
import {
  lerLinhas, cabecalho, carregarAlvos, alvoPadrao, alvoNomeado, listarPhases, proximoN, normalizarSlug, slugValido, ROTAS,
  linksNoCaminho, lerPlan, achadosDoPlan, grupos, recorte, segmentos, sobrepoe, lerRs, vereditoReview, ultimoAjuste,
  commits, classificarCommit, naoCommitados, naoEnviados, commitQueAdicionou, jsonAscii, executadoDireto,
} from './_disco.mjs';

// ---------------------------------------------------------------------------
// Rotas e etapas (references/disco.md, Cabeçalho)
// ---------------------------------------------------------------------------

// Etapas que contam no progresso (SKILL.md, seção 9): cinco em high e mvp, duas em medium.
// O analyze é etapa própria no progresso, embora não tenha artefato nem aprovação: a
// presença de `## Achados do analyze` no plan.md o marca como concluído.
const ETAPAS_ROTA = {
  medium: ['implement', 'review'],
  high: ['spec', 'plan', 'analyze', 'implement', 'review'],
  mvp: ['spec', 'plan', 'analyze', 'implement', 'review'],
};

const DIAGNOSTICO = 'Diagnóstico delegado';

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

/** IDs (passos como `2a` e R* como `R1`) presentes em commits task do alvo. */
function idsCommitados(lista) {
  return new Set((lista || []).filter((c) => c.tipo === 'task').flatMap((c) => c.ids));
}

// ---------------------------------------------------------------------------
// Inconsistências (disco.md: Cabeçalho, Plan, Estado da phase e Compatibilidade)
// ---------------------------------------------------------------------------

/**
 * Achados a diagnosticar antes de seguir. Alvo antigo fechado fica intocado e não gera
 * achado; alvo antigo aberto gera um só, porque esta versão não o conduz.
 */
function inconsistencias(raiz, alvos, porAlvo, temGit) {
  const achados = [];
  for (const a of alvos) {
    for (const l of linksNoCaminho(raiz, a.pasta)) achados.push(`${a.alvo}: caminho é link, não escreva através dele: ${relative(raiz, l)}`);
    if (a.antigo) {
      if (!a.fechado) achados.push(`${a.alvo}: formato antigo aberto; esta versão não o conduz, feche a phase com a versão anterior da skill`);
      continue;
    }
    const algumArtefato = Object.values(a.art).some(Boolean);
    if (algumArtefato && !a.rota) achados.push(`${a.alvo}: primeiro artefato sem # Rota:`);
    if (a.rota && !ROTAS.includes(a.rota)) achados.push(`${a.alvo}: # Rota: ${a.rota} inválida (medium, high ou mvp)`);
    if (algumArtefato && (a.alvo === 'mvp' || a.rota === 'mvp') && !a.risco) achados.push(`${a.alvo}: MVP sem # Risco: na spec`);
    const plan = lerPlan(a.art.plan);
    for (const m of achadosDoPlan(plan.passos)) achados.push(`${a.alvo}: plan: ${m}`);
    if (!temGit) continue;
    // Passo concluído = caixa marcada confirmada por commit task(<alvo>:...) com o ID.
    const ids = idsCommitados(porAlvo.get(a.alvo));
    for (const p of plan.passos) {
      if (p.caixa && !ids.has(p.id)) achados.push(`${a.alvo}: passo ${p.id} marcado sem commit task(${a.alvo}:...)`);
      if (!p.caixa && ids.has(p.id)) achados.push(`${a.alvo}: passo ${p.id} com commit e caixa vazia`);
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

/**
 * Linha 3: alteração não commitada fora de .vibeflow/ e de .erros-encontrados/ (o
 * chamador já os filtrou de `fora`) sem dono. Donos: os `Arquivos:` de
 * passos abertos (passo aberto sem Arquivos comparáveis é dono de qualquer path) e os
 * paths de R* abertos ou marcados [x] ainda sem commit. Alvo antigo fechado não conta;
 * alvo antigo aberto tem passos ilegíveis para esta versão e, por isso, também é dono
 * de qualquer path: a linha 5 (formato antigo) é que o relata.
 */
function semDono(alvos, porAlvo, fora) {
  if (!fora.length) return [];
  const donos = [];
  for (const a of alvos) {
    if (a.antigo) {
      if (a.fechado) continue;
      return [];
    }
    if (!a.fechado) {
      for (const p of lerPlan(a.art.plan).passos.filter((x) => !x.caixa)) {
        const r = recorte(p);
        if (r === null) return []; // passo aberto sem Arquivos comparáveis pode ser dono de qualquer path
        donos.push(...r);
      }
    }
    const ids = idsCommitados(porAlvo.get(a.alvo));
    for (const r of lerRs(a.art.review)) {
      if ((!r.feito || !ids.has(r.id)) && r.path) donos.push(segmentos(r.path));
    }
  }
  return fora.filter((p) => !donos.some((d) => sobrepoe(d, segmentos(p))));
}

// ---------------------------------------------------------------------------
// Etapa do alvo (linhas da tabela a partir de "Alvo aberto no formato antigo")
// ---------------------------------------------------------------------------

/** Linhas de spec a "Todos os passos e checkpoints marcados": só high e mvp. */
function etapaDeSpecAPassos(alvo, fora) {
  const spec = alvo.art.spec;
  if (!spec) return { etapa: 'interview', situacao: 'spec.md ausente', proximo: 'Líder conduz; redator grava a spec.md' };
  if (cabecalho(spec, 'Status') !== 'aprovado') return { etapa: 'spec', situacao: 'aguardando ajuste ou aprovação', proximo: 'Líder apresenta ao humano' };
  if (!alvo.art.plan) return { etapa: 'plan', situacao: 'sem plan.md', proximo: 'Líder define; redator grava' };
  const plan = lerPlan(alvo.art.plan);
  if (!plan.analisado) return { etapa: 'analyze', situacao: 'plan sem ## Achados do analyze', proximo: 'Revisor de contexto limpo' };
  if (!plan.passos.length) return { etapa: 'indeterminado', situacao: 'plan sem passos reconhecidos', proximo: DIAGNOSTICO };

  // Código não commitado nos Arquivos: de passos abertos (comparáveis): retomar o passo.
  // ponytail: passo aberto sem Arquivos comparáveis nunca aciona esta linha e cai em
  // "implementar o passo"; o implementador reencontra o código na redelegação.
  const tocados = fora.map(segmentos);
  const retomar = plan.passos.filter((p) => !p.caixa && recorte(p)?.some((r) => tocados.some((t) => sobrepoe(r, t))));
  if (retomar.length) {
    return { etapa: 'implement', situacao: 'retomar o passo', proximo: 'Implementador conclui a prova; líder confere e commita', passos: retomar.map((p) => p.id) };
  }

  // Primeiro item aberto na ordem do arquivo: checkpoint ou passo (grupo paralelo inteiro).
  const aberto = plan.itens.find((i) => !i.caixa);
  if (aberto?.tipo === 'checkpoint') {
    const anteriores = plan.itens.slice(0, plan.itens.indexOf(aberto));
    const iUltimoCheckpoint = anteriores.map((i) => i.tipo).lastIndexOf('checkpoint');
    const cobertos = anteriores.slice(iUltimoCheckpoint + 1).filter((i) => i.tipo === 'passo').map((i) => i.id);
    return { etapa: 'implement', situacao: 'checkpoint', proximo: 'Verificador de contexto limpo', checkpoint: { aceite: aberto.aceite, passos: cobertos } };
  }
  if (aberto) {
    const grupo = grupos(plan.passos).find((g) => g.passos.includes(aberto));
    const abertos = grupo.passos.filter((p) => !p.caixa).map((p) => p.id);
    const situacao = grupo.passos.length > 1 ? `implementar o grupo paralelo ${grupo.num} (${abertos.join(', ')})` : `implementar o passo ${grupo.num}`;
    return { etapa: 'implement', situacao, proximo: 'Líder delega ao implementador', passos: abertos };
  }
  return null; // todos os passos e checkpoints marcados: segue para as linhas do review.md
}

/** Linhas de review.md da tabela: fila de R*, re-review, confirmação e retomada. */
function etapaDaReview(alvo, porAlvo) {
  const review = alvo.art.review;
  if (!review) return { etapa: 'review', situacao: 'sem review.md', proximo: 'Revisor' };
  const rs = lerRs(review);
  const status = cabecalho(review, 'Status');
  if (rs.some((r) => !r.feito)) return { etapa: 'implement', situacao: 'corrigir R*', proximo: 'Implementador ou redator, pelo papel:' };
  if (status === 'request-changes') {
    const ids = idsCommitados(porAlvo.get(alvo.alvo));
    const semCommit = rs.filter((r) => r.feito && !ids.has(r.id)).map((r) => r.id);
    if (semCommit.length) return { etapa: 'implement', situacao: `commitar a correção (${semCommit.join(', ')})`, proximo: 'Líder commita, se a prova da correção está verde' };
    return { etapa: 'review', situacao: 're-review', proximo: 'Revisor' };
  }
  if (status === 'rascunho') {
    const veredito = vereditoReview(review);
    if (veredito === 'approve') return { etapa: 'review', situacao: 'confirmar', proximo: 'Líder resume no chat e pede a confirmação única' };
    if (veredito === null) return { etapa: 'review', situacao: 'retomar', proximo: 'Revisor' };
  }
  return { etapa: 'indeterminado', situacao: `review.md em ${status || 'status ausente'}`, proximo: DIAGNOSTICO };
}

/** Etapa atual do alvo aberto, pela primeira linha da tabela que se aplica. */
function etapaDoAlvo(alvo, porAlvo, fora) {
  if (alvo.antigo) {
    return { etapa: 'inconsistência', situacao: 'alvo aberto no formato antigo', proximo: 'Líder relata ao humano, que fecha a phase com a versão anterior da skill' };
  }
  // Pasta sem artefato: ainda não há onde ler a rota, e a primeira etapa é a interview.
  if (!Object.values(alvo.art).some(Boolean)) {
    return { etapa: 'interview', situacao: 'spec.md ausente', proximo: 'Líder conduz; redator grava a spec.md' };
  }
  if (!ROTAS.includes(alvo.rota)) {
    return { etapa: 'indeterminado', situacao: alvo.rota ? `# Rota: ${alvo.rota} inválida` : 'primeiro artefato sem # Rota:', proximo: DIAGNOSTICO };
  }
  // Medium não tem spec nem plan: a phase nasce no review.md.
  if (alvo.rota !== 'medium') {
    const etapa = etapaDeSpecAPassos(alvo, fora);
    if (etapa) return etapa;
  }
  return etapaDaReview(alvo, porAlvo);
}

// ---------------------------------------------------------------------------
// Progresso (SKILL.md, seção 9)
// ---------------------------------------------------------------------------

/**
 * Regra de SKILL.md, seção 9: cada etapa da rota vale uma parte igual. Spec conta com
 * `# Status: aprovado`; plan, com o plan.md presente; analyze, com `## Achados do
 * analyze`; implement, com a fração de passos marcados (checkpoints não entram na
 * fração); review, só com a phase fechada. Medium conta o implement inteiro, porque a
 * phase só nasce depois da entrega. Soma em inteiros para arredondar para baixo sem erro
 * de ponto flutuante: cada etapa vale `den` unidades e o implement vale `feitos`.
 */
function progresso(alvo) {
  const ajuste = ultimoAjuste(alvo.art.review);
  if (ajuste && ajuste.length) {
    const rs = lerRs(alvo.art.review).filter((r) => ajuste.includes(r.id));
    if (rs.some((r) => !r.feito)) return { ajuste: `${rs.filter((r) => r.feito).length}/${rs.length}` };
  }
  if (alvo.antigo) return { percentual: alvo.fechado ? 100 : null };
  const etapas = ETAPAS_ROTA[alvo.rota];
  if (!etapas) return { percentual: null };
  const plan = lerPlan(alvo.art.plan);
  const total = plan.passos.length;
  const feitos = plan.passos.filter((p) => p.caixa).length;
  const den = total || 1;
  let soma = 0;
  for (const e of etapas) {
    if (e === 'spec') soma += cabecalho(alvo.art.spec, 'Status') === 'aprovado' ? den : 0;
    else if (e === 'plan') soma += alvo.art.plan ? den : 0;
    else if (e === 'analyze') soma += plan.analisado ? den : 0;
    else if (e === 'implement') soma += alvo.rota === 'medium' ? den : feitos;
    else if (e === 'review') soma += alvo.fechado ? den : 0;
  }
  return { percentual: Math.floor((soma * 100) / (den * etapas.length)), passos: total ? `${feitos}/${total}` : null };
}

// ---------------------------------------------------------------------------
// Execução
// ---------------------------------------------------------------------------

function lerArgs(argv) {
  const args = { raiz: process.cwd(), alvo: null, json: false, slug: null, linha: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--json') args.json = true;
    else if (a === '--linha') args.linha = true;
    else if ((a === '--raiz' || a === '--alvo' || a === '--slug') && argv[i + 1]) args[a.slice(2)] = argv[++i];
    else return { erro: `argumento desconhecido ou sem valor: ${a}` };
  }
  return args;
}

/** Resumo de um alvo para o relatório. */
function resumoAlvo(raiz, a) {
  return { alvo: a.alvo, pasta: relative(raiz, a.pasta).replace(/\\/g, '/'), rota: a.rota, risco: a.risco, fechado: a.fechado, antigo: a.antigo };
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
  // Código e teste: tudo fora de .vibeflow/ (artefatos da cadeia) e de .erros-encontrados/
  // (registros de achado fora do recorte), como na linha 3 de references/disco.md.
  const fora = (alterados || []).filter((p) => !p.startsWith('.vibeflow/') && !p.startsWith('.erros-encontrados/'));

  const rel = {
    raiz,
    governanca,
    git: temGit,
    proximoN: proximoN(listarPhases(raiz)),
    alvos: alvos.map((a) => resumoAlvo(raiz, a)),
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
  const orfaos = temGit ? semDono(alvos, porAlvo, fora) : [];
  if (!nomeado && medium) rel.etapa = { etapa: 'review da entrega medium', situacao: medium.assunto, proximo: 'Revisor' };
  else if (!nomeado && pushes.length) rel.etapa = { etapa: 'push pendente', situacao: pushes.join(', '), proximo: 'Líder, com a confirmação humana' };
  else if (!nomeado && orfaos.length) rel.etapa = { etapa: 'alteração sem dono', situacao: orfaos.join(', '), proximo: 'Líder pergunta ao humano se retoma a entrega ou isola o trabalho' };

  const alvo = nomeado || alvoPadrao(alvos);
  if (alvo) {
    rel.alvo = resumoAlvo(raiz, alvo);
    rel.artefatos = {};
    if (alvo.art.spec) rel.artefatos.spec = cabecalho(alvo.art.spec, 'Status') || 'sem status';
    if (alvo.art.plan) rel.artefatos.plan = alvo.antigo ? 'formato antigo' : lerPlan(alvo.art.plan).analisado ? 'analisado' : 'sem analyze';
    if (alvo.art.review) rel.artefatos.review = cabecalho(alvo.art.review, 'Status') || 'sem status';
    rel.rAbertos = lerRs(alvo.art.review).filter((r) => !r.feito).map((r) => r.id);
    rel.progresso = progresso(alvo);
    if (!rel.etapa) rel.etapa = alvo.fechado ? { etapa: 'fechada', situacao: 'phase fechada', proximo: 'Líder' } : etapaDoAlvo(alvo, porAlvo, fora);
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
  if (r.alvo) {
    const risco = r.alvo.risco ? ` · risco: ${r.alvo.risco}` : '';
    l.push(`alvo: ${r.alvo.alvo} (${r.alvo.pasta}) · rota: ${r.alvo.rota || (r.alvo.antigo ? 'não lida (formato antigo)' : 'ausente')}${risco}${r.alvo.antigo ? ' · formato antigo' : ''}${r.alvo.fechado ? ' · fechada' : ''}`);
  }
  if (r.artefatos) l.push(`artefatos: ${Object.entries(r.artefatos).map(([k, v]) => `${k} ${v}`).join(', ') || 'nenhum'}`);
  const p = r.progresso;
  const prog = p ? (p.ajuste ? `ajuste: R* ${p.ajuste}` : p.percentual === null ? 'progresso: indisponível' : `progresso: ${p.percentual}%`) : null;
  const marcados = p && p.passos ? ` · passos ${p.passos} marcados` : '';
  l.push(`${prog ? `${prog} · ` : ''}etapa: ${r.etapa.etapa}, ${r.etapa.situacao}${marcados} · próximo: ${r.etapa.proximo}`);
  if (r.etapa.passos) l.push(`passos: ${r.etapa.passos.join(', ')}`);
  if (r.etapa.checkpoint) l.push(`checkpoint cobre os passos ${r.etapa.checkpoint.passos.join(', ') || 'nenhum'} e os critérios ${r.etapa.checkpoint.aceite.join(', ') || 'nenhum'}`);
  if (r.rAbertos && r.rAbertos.length) l.push(`R* abertos: ${r.rAbertos.join(', ')}`);
  if (r.aviso) l.push(`aviso: ${r.aviso}`);
  if (r.init) l.push(`init: ${r.init}`);
  if (!r.git) l.push('git: indisponível; linhas de commit, push e alteração não avaliadas');
  for (const i of r.inconsistencias) l.push(`inconsistência: ${i}`);
  l.push(`próxima phase: ${r.proximaPhase || `phase-${r.proximoN}-<slug>`}`);
  return `${l.join('\n')}\n`;
}

/**
 * Uma linha de progresso para a statusline do host (SKILL.md, seção 9). Vazia fora de um
 * repo com .vibeflow/, para não poluir a statusline de projetos sem a skill.
 */
function linha(r) {
  if (!r.governanca.vibeflow) return '';
  const p = r.progresso;
  const prog = p ? (p.ajuste ? `ajuste: R* ${p.ajuste}` : p.percentual === null ? null : `${p.percentual}%`) : null;
  const partes = ['vibeflow', r.alvo ? r.alvo.alvo : null, prog, `etapa: ${r.etapa.etapa}`, `próximo: ${r.etapa.proximo}`];
  if (r.inconsistencias.length) partes.push(`inconsistências: ${r.inconsistencias.length}`);
  return `${partes.filter(Boolean).join(' · ')}\n`;
}

function principal() {
  const args = lerArgs(process.argv.slice(2));
  if (args.erro) { console.error(args.erro); return 2; }
  const r = estado(resolve(args.raiz), args.alvo);
  if (r.erro) { console.error(r.erro); return 2; }
  if (args.slug !== null) {
    const slug = normalizarSlug(args.slug);
    if (!slugValido(slug)) { console.error(`slug fora da regra (2 a 48 caracteres a-z, 0-9 e hífen): "${slug}"; escolha outra frase`); return 2; }
    r.proximaPhase = `phase-${r.proximoN}-${slug}`;
  }
  process.stdout.write(args.linha ? linha(r) : args.json ? `${jsonAscii(r)}\n` : texto(r));
  return r.inconsistencias.length ? 1 : 0;
}

if (executadoDireto(import.meta.url)) {
  process.exitCode = principal();
}
