#!/usr/bin/env node
// ondas.mjs: monta a próxima onda de T* de um plan e lista sobreposições de Arquivos:.
//
// Implementa references/implement.md (seção 1, passos 1 e 2) e as regras de Arquivos:
// de references/plan.md (passo 1.3). Só lê o plan; não despacha nem marca nada.
//
// Uso:
//   node ondas.mjs [--alvo phase-N|mvp] [--plan <caminho>] [--raiz <dir>] [--json]
// Sem --alvo nem --plan, usa o alvo padrão de references/disco.md.
// Saída: 0 com onda montada ou fila vazia, 1 quando há sobreposição sem Deps ou Deps
// para T* inexistente, 2 em erro de uso ou plan ausente.

import { join, resolve } from 'node:path';
import {
  lerLinhas, lerTasks, recorte, recortesSobrepoem, carregarAlvos, alvoPadrao, alvoNomeado, jsonAscii, executadoDireto,
} from './_disco.mjs';

// ---------------------------------------------------------------------------
// Argumentos
// ---------------------------------------------------------------------------

function lerArgs(argv) {
  const args = { raiz: process.cwd(), alvo: null, plan: null, json: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--json') args.json = true;
    else if (['--raiz', '--alvo', '--plan'].includes(a) && argv[i + 1]) args[a.slice(2)] = argv[++i];
    else return { erro: `argumento desconhecido ou sem valor: ${a}` };
  }
  return args;
}

// ---------------------------------------------------------------------------
// Fila e onda
// ---------------------------------------------------------------------------

/** Fecho transitivo de Deps: conjunto de T* de que cada T* depende, direta ou indiretamente. */
function dependenciasTransitivas(tasks) {
  const porId = new Map(tasks.map((t) => [t.id, t]));
  const memo = new Map();
  const visitar = (id, pilha) => {
    if (memo.has(id)) return memo.get(id);
    const todas = new Set();
    if (pilha.has(id)) return todas; // ciclo: interrompe sem laço infinito
    pilha.add(id);
    for (const d of porId.get(id)?.deps || []) {
      todas.add(d);
      for (const x of visitar(d, pilha)) todas.add(x);
    }
    pilha.delete(id);
    memo.set(id, todas);
    return todas;
  };
  for (const t of tasks) visitar(t.id, new Set());
  return memo;
}

/**
 * Analisa o plan: elegíveis, próxima onda, T* que rodam sozinhas, sobreposições entre
 * T* sem Deps entre si e Deps quebradas.
 */
export function analisarPlan(tasks) {
  const porId = new Map(tasks.map((t) => [t.id, t]));
  const concluida = (id) => porId.get(id)?.caixa === true;
  const depsQuebradas = tasks.flatMap((t) => t.deps.filter((d) => !porId.has(d)).map((d) => ({ task: t.id, dep: d })));

  // Elegível: caixa aberta, Estado pendente (ausente conta como pendente) e Deps concluídas.
  const elegiveis = tasks
    .filter((t) => !t.caixa && (t.estado === null || t.estado === 'pendente'))
    .filter((t) => t.deps.every(concluida))
    .sort((a, b) => a.num - b.num);

  // Onda: percorre em ordem numérica; T* sem recorte comparável só entra com a onda vazia
  // e a encerra; com a onda já iniciada, ela é pulada e a montagem continua.
  const onda = [];
  const recortesOnda = [];
  for (const t of elegiveis) {
    const r = recorte(t);
    if (r === null) {
      if (onda.length) continue;
      onda.push(t);
      break;
    }
    if (recortesOnda.some((ro) => recortesSobrepoem(ro, r))) continue;
    onda.push(t);
    recortesOnda.push(r);
  }

  // Sobreposição entre T* abertas sem Deps entre si, para o analyze e para o líder.
  const trans = dependenciasTransitivas(tasks);
  const abertas = tasks.filter((t) => !t.caixa);
  const sobreposicoes = [];
  for (let i = 0; i < abertas.length; i++) {
    for (let j = i + 1; j < abertas.length; j++) {
      const a = abertas[i];
      const b = abertas[j];
      if (trans.get(a.id)?.has(b.id) || trans.get(b.id)?.has(a.id)) continue;
      const ra = recorte(a);
      const rb = recorte(b);
      if (ra && rb && recortesSobrepoem(ra, rb)) sobreposicoes.push([a.id, b.id]);
    }
  }

  const sozinhas = abertas.filter((t) => recorte(t) === null).map((t) => ({
    task: t.id,
    motivo: !t.arquivos || !t.arquivos.length ? 'sem Arquivos:' : 'path incomparável em Arquivos:',
  }));

  return {
    total: tasks.length,
    concluidas: tasks.filter((t) => t.caixa).length,
    elegiveis: elegiveis.map((t) => t.id),
    onda: onda.map((t) => t.id),
    sozinhas,
    sobreposicoes,
    depsQuebradas,
  };
}

// ---------------------------------------------------------------------------
// Execução
// ---------------------------------------------------------------------------

function principal() {
  const args = lerArgs(process.argv.slice(2));
  if (args.erro) { console.error(args.erro); return 2; }
  const raiz = resolve(args.raiz);

  let caminhoPlan = args.plan ? resolve(args.plan) : null;
  if (!caminhoPlan) {
    const alvos = carregarAlvos(raiz);
    const alvo = args.alvo ? alvoNomeado(alvos, args.alvo) : alvoPadrao(alvos);
    if (!alvo) { console.error(args.alvo ? `alvo não encontrado: ${args.alvo}` : 'sem alvo aberto; use --alvo ou --plan'); return 2; }
    caminhoPlan = join(alvo.pasta, 'plan.md');
  }
  const linhas = lerLinhas(caminhoPlan);
  if (!linhas) { console.error(`plan ausente: ${caminhoPlan}`); return 2; }

  const r = analisarPlan(lerTasks(linhas));
  const achado = r.sobreposicoes.length > 0 || r.depsQuebradas.length > 0;

  if (args.json) {
    process.stdout.write(`${jsonAscii({ plan: caminhoPlan, ...r })}\n`);
  } else {
    const l = [];
    l.push(`plan: ${caminhoPlan}`);
    l.push(`T* concluídas: ${r.concluidas}/${r.total}`);
    l.push(`elegíveis: ${r.elegiveis.join(', ') || 'nenhuma'}`);
    l.push(`próxima onda: ${r.onda.join(', ') || 'nenhuma'}`);
    for (const s of r.sozinhas) l.push(`roda sozinha: ${s.task} (${s.motivo})`);
    for (const [a, b] of r.sobreposicoes) l.push(`sobreposição sem Deps: ${a} e ${b}`);
    for (const d of r.depsQuebradas) l.push(`Deps para T* inexistente: ${d.task} -> ${d.dep}`);
    process.stdout.write(`${l.join('\n')}\n`);
  }
  return achado ? 1 : 0;
}

// Executa só quando chamado direto, para os testes poderem importar analisarPlan.
if (executadoDireto(import.meta.url)) {
  process.exitCode = principal();
}
