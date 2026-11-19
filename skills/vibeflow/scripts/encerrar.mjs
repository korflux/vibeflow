#!/usr/bin/env node
// encerrar.mjs: hook SubagentStop do Claude Code que impede o subagente implementador de
// devolver o trecho com o disco num estado que a prosa proíbe e que o disco e o Git mostram
// sem ambiguidade, numa phase ou MVP aberto com plan.md:
//   1. caixa de passo marcada sem commit task com o ID, ou commit task com a caixa vazia
//      (references/disco.md, Estado da phase; references/implementador.md, Commit do passo);
//   2. alteração não commitada sem dono: fora dos `Arquivos:` de passos abertos, dos paths
//      de R* abertos e do `## Trabalho alheio` (references/implementador.md, Recorte).
// É a conferência de forma que o líder faz ao receber o trecho (references/delegation.md,
// Conferência do líder), adiantada para antes da devolução.
//
// É apoio opcional do host (README.pt-BR.md, Apoios opcionais do host): a skill não o instala e
// nenhuma etapa depende dele. A prosa é o contrato; divergência é bug deste script.
//
// Protocolo de hook, como o barrar.mjs: lê o JSON do evento no stdin e sempre sai com 0.
// Para segurar o subagente, imprime `decision: "block"` com o motivo, que o host entrega a
// ele como próxima instrução; sem achado, não imprime nada. O host só bloqueia por código de
// saída quando ele é 2, e o 1 dos scripts de leitura passa como erro sem efeito; a decisão em
// JSON evita depender disso. Entrada ilegível, outro agente, outro evento, repo sem Git ou
// erro de leitura deixam o subagente encerrar: o hook nunca segura por erro próprio.
//
// Segura uma vez por encerramento: com `stop_hook_active` verdadeiro, o subagente já foi
// devolvido por este hook e encerra, para o achado que ele não pode resolver (impedimento
// real, trabalho do humano ainda não declarado) chegar ao líder no relatório em vez de
// prender o trecho.
//
// Fora do alcance, de propósito:
// ponytail: entrega low ou medium e ajuste sem phase aberta com plan não são conferidos,
//   porque ali o líder commita e a alteração não commitada é o estado esperado; conferir
//   exige o hook conhecer o brief, que não está no disco.
// ponytail: código não commitado dentro dos `Arquivos:` de passo aberto passa, porque é o
//   estado legítimo do trecho que parou num impedimento.
//
// Uso (hook): node encerrar.mjs   com o evento SubagentStop no stdin.

import { resolve } from 'node:path';
import { estado } from './estado.mjs';
import { carregarAlvos, alvoPadrao, lerPlan, commits, classificarCommit, idsCommitados, caixasContraCommits, jsonAscii, executadoDireto } from './_disco.mjs';

const PAPEL = 'implementador';

/**
 * Achados que seguram o encerramento, lidos do disco e do Git da raiz; lista vazia quando o
 * implementador pode encerrar. Fonte única da decisão, usada pelo hook e pelos testes.
 */
export function achadosDoEncerramento(raiz) {
  const alvo = alvoPadrao(carregarAlvos(raiz));
  if (!alvo || alvo.antigo || !alvo.art.plan) return [];
  const lista = commits(raiz);
  if (lista === null) return [];
  const doAlvo = lista.map((c) => classificarCommit(c.assunto)).filter((k) => k && k.alvo === alvo.alvo);
  const caixas = caixasContraCommits(lerPlan(alvo.art.plan).passos, idsCommitados(doAlvo));
  const achados = [];
  for (const id of caixas.marcadosSemCommit) achados.push(`passo ${id} com a caixa marcada e sem commit task(${alvo.alvo}:${id})`);
  for (const id of caixas.commitadosSemCaixa) achados.push(`passo ${id} com commit task(${alvo.alvo}:${id}) e a caixa vazia`);
  for (const p of estado(raiz).semDono || []) achados.push(`alteração não commitada fora do recorte: ${p}`);
  return achados;
}

/** Decide sobre o evento SubagentStop já lido; devolve o objeto de saída do hook ou null. */
export function decidir(evento) {
  if (!evento || evento.hook_event_name !== 'SubagentStop' || evento.agent_type !== PAPEL) return null;
  if (evento.stop_hook_active || typeof evento.cwd !== 'string' || !evento.cwd) return null;
  let achados = [];
  try { achados = achadosDoEncerramento(resolve(evento.cwd)); } catch { return null; }
  if (!achados.length) return null;
  const motivo = [
    'O trecho não pode ser devolvido com este estado no disco:',
    ...achados.map((a) => `- ${a}`),
    'Caixa marcada pede o commit do passo, e commit pede a caixa marcada nele (references/implementador.md, Commit do passo); sem saída, desfaça só a marcação e relate o impedimento. Path fora do recorte que você alterou é desfeito ou levado ao líder antes de editar; o que não é seu vai em `pendencias` do relatório, sem ser tocado.',
  ].join('\n');
  return { decision: 'block', reason: motivo };
}

if (executadoDireto(import.meta.url)) {
  let bruto = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', (parte) => { bruto += parte; });
  process.stdin.on('end', () => {
    let evento = null;
    try { evento = JSON.parse(bruto.replace(/^﻿/, '')); } catch { /* entrada ilegível: segue */ }
    const saida = decidir(evento);
    if (saida) process.stdout.write(`${jsonAscii(saida)}\n`);
  });
}
