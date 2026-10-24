// _apoio.mjs: montagem de repositório Git temporário e de artefatos mínimos para os
// testes de comportamento dos scripts. Não é teste (o nome não casa com `*.test.mjs`).
//
// Os artefatos seguem o contrato 5.0.0 de references/disco.md: spec.md com `# Rota:`,
// plan.md como checklist de passos e review.md com R*. O formato antigo (T*, interview.md)
// só aparece nos testes de compatibilidade, montado à mão.

import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

export const SCRIPTS = resolve(dirname(fileURLToPath(import.meta.url)), '../../skills/vibeflow/scripts');
export const PH = '.vibeflow/phases/phase-1-agenda';

/** Repositório temporário com AGENTS.md, bloco da cadeia e um commit base; removido ao fim do teste. */
export function repo(t) {
  const raiz = mkdtempSync(join(tmpdir(), 'vibeflow-'));
  t.after(() => rmSync(raiz, { recursive: true, force: true }));
  execFileSync('git', ['init', '-q'], { cwd: raiz });
  escrever(raiz, 'AGENTS.md', '# Regras\n<!-- VIBEFLOW:CADEIA start -->\n<!-- VIBEFLOW:CADEIA end -->\n');
  escrever(raiz, '.vibeflow/phases/.gitkeep', '');
  commit(raiz, 'chore: base');
  return raiz;
}

export function escrever(raiz, rel, conteudo) {
  mkdirSync(dirname(join(raiz, rel)), { recursive: true });
  writeFileSync(join(raiz, rel), conteudo);
}

/** Staging de tudo e commit com identidade fixa e sem assinatura, para rodar em qualquer máquina. */
export function commit(raiz, msg) {
  execFileSync('git', ['add', '--', '.'], { cwd: raiz });
  execFileSync('git', ['-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false', 'commit', '-q', '--allow-empty', '-m', msg], { cwd: raiz });
}

// ---------------------------------------------------------------------------
// Artefatos
// ---------------------------------------------------------------------------

export const spec = (status, { rota = 'high', risco = null } = {}) =>
  `# Spec: x\n# Alvo: phase-1-agenda\n# Status: ${status}\n# Rota: ${rota}\n${risco ? `# Risco: ${risco}\n` : ''}\n## Objetivo\n\nx\n`;

/** Linha de passo no formato de disco.md; `arquivos: null` omite o campo. */
export const passo = (id, { caixa = false, aceite = 'A1', arquivos } = {}) => {
  const arq = arquivos === null ? '' : ` · Arquivos: ${arquivos ?? `\`src/p${id}.js\`, \`tests/p${id}.test.js\``}`;
  return `- [${caixa ? 'x' : ' '}] ${id}: entrega ${id} · Aceite: ${aceite}${arq} · Prova: \`node --test\``;
};

export const checkpoint = (aceite = 'A1', caixa = false) => `- [${caixa ? 'x' : ' '}] Checkpoint: ${aceite}`;

/** plan.md; `analisado: false` omite a seção `## Achados do analyze`. */
export const plan = (linhas, { analisado = true } = {}) =>
  `# Plan: x\n# Alvo: phase-1-agenda\n# Spec: spec.md (mesma pasta)\n\n## Regressão completa\n\n- \`node --test\`\n\n## Passos\n\n${linhas.join('\n')}\n${analisado ? '\n## Achados do analyze\n\nNenhum achado.\n' : ''}`;

export const review = (status, corpo = '', rota = null) =>
  `# Review: x\n# Alvo: phase-1-agenda\n# Status: ${status}\n${rota ? `# Rota: ${rota}\n` : ''}\n${corpo}`;

export const veredito = (approve) =>
  `## Veredito\n\n- [${approve ? 'x' : ' '}] **Approve**: ok\n- [${approve ? ' ' : 'x'}] **Request changes**: x\n\n`;

export const achados = (...linhas) => `## Achados\n\n### Required\n\n${linhas.join('\n')}\n\n`;

/** Executa um script da skill como CLI e devolve { codigo, out }. */
export function cli(script, args) {
  try {
    const out = execFileSync(process.execPath, [join(SCRIPTS, script), ...args], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
    return { codigo: 0, out };
  } catch (e) {
    return { codigo: e.status, out: e.stdout || '' };
  }
}
