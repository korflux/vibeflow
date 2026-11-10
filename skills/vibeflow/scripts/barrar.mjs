#!/usr/bin/env node
// barrar.mjs: hook PreToolUse do Claude Code que nega, no subagente implementador, os comandos
// de shell que references/implementador.md (Proibido no passo e Codar e provar) proíbe e que um
// padrão de texto reconhece sem ambiguidade:
//   1. espera por loop (`until`, `while` ou `for` com `sleep` ou `Start-Sleep` no corpo);
//   2. gate estático ou teste na forma recursiva do monorepo (`pnpm -r`, `--recursive`,
//      `--workspaces`), que a regra manda trocar pelo filtro do pacote tocado.
//
// É apoio opcional do host (README.md, Apoios opcionais do host): a skill não o instala e
// nenhuma etapa depende dele. A prosa é o contrato; divergência é bug deste script.
//
// Protocolo de hook, e não o dos scripts de leitura: lê o JSON do evento no stdin e sempre sai
// com 0. Para negar, imprime `hookSpecificOutput.permissionDecision: "deny"` com o motivo, que
// o host mostra ao agente; sem achado, não imprime nada. Entrada ilegível, outro agente, outra
// ferramenta ou comando vazio deixam a chamada seguir: o hook nunca bloqueia por erro próprio.
//
// Fora do alcance, de propósito:
// ponytail: E2E e suíte inteira no passo não são barrados, porque o implementador roda o E2E
//   da captura em low e medium e o comando da suíte inteira varia por projeto; barrar exige o
//   hook conhecer a rota e os comandos do projeto, o que só vale a pena se a medição de uma
//   phase mostrar que a prosa continua sendo ignorada.
// ponytail: o padrão lê o comando como texto, sem interpretar o shell; loop escondido em
//   script chamado pelo comando passa.
//
// Uso (hook): node barrar.mjs   com o evento PreToolUse no stdin.

import { jsonAscii, executadoDireto } from './_disco.mjs';

const PAPEL = 'implementador';
const FERRAMENTAS = new Set(['Bash', 'PowerShell']);

// Loop de shell POSIX: `until|while|for ... ; do ... sleep`. O `do` depois de `;` ou de quebra de
// linha separa o loop de um texto qualquer que só contenha as palavras (mensagem de commit).
const RE_LOOP_SH = /\b(?:until|while|for)\b[\s\S]*?(?:;|\n)\s*do\b[\s\S]*?\bsleep\b/;
// Loop de PowerShell: `while|until|for|foreach|do` com bloco que contém `Start-Sleep`.
const RE_LOOP_PS = /\b(?:while|until|for|foreach|do)\b[^{]*\{[\s\S]*?\bStart-Sleep\b/i;
// Forma recursiva do gerenciador junto de gate estático ou teste.
const RE_RECURSIVO = /\b(?:pnpm|npm|yarn)\b[^\n;&|]*\s(?:-r|--recursive|--workspaces)\b/;
const RE_GATE = /\b(?:typecheck|type-check|tsc|lint|eslint|test)\b/;

/**
 * Motivo da negação para o comando, ou null quando ele pode seguir. Fonte única dos padrões,
 * usada pelo hook e pelos testes.
 */
export function motivoDeNegar(comando) {
  const c = String(comando || '');
  if (RE_LOOP_SH.test(c) || RE_LOOP_PS.test(c)) {
    return 'Espera por loop é proibida no passo (references/implementador.md, Proibido no passo). Rode o comando longo em segundo plano, com o aviso de término do host, e não leia o log repetidas vezes.';
  }
  const linhaRecursiva = c.split(/\n|;|&&|\|\|/).find((parte) => RE_RECURSIVO.test(parte) && RE_GATE.test(parte));
  if (linhaRecursiva) {
    return 'Gate estático ou teste na forma recursiva do monorepo é proibido no passo (references/implementador.md, Codar e provar). Use o comando por pacote ou o filtro do gerenciador no pacote tocado, como `pnpm --filter <pacote> typecheck`.';
  }
  return null;
}

/** Decide sobre o evento PreToolUse já lido; devolve o objeto de saída do hook ou null. */
export function decidir(evento) {
  if (!evento || evento.agent_type !== PAPEL || !FERRAMENTAS.has(evento.tool_name)) return null;
  const motivo = motivoDeNegar(evento.tool_input?.command);
  if (!motivo) return null;
  return { hookSpecificOutput: { hookEventName: 'PreToolUse', permissionDecision: 'deny', permissionDecisionReason: motivo } };
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
