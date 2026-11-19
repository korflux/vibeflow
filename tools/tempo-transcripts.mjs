#!/usr/bin/env node
// tempo-transcripts.mjs: mede, nos transcripts do Claude Code, quanto tempo cada agente passou
// em cada tipo de ferramenta (teste, E2E, tipos, lint, build, espera, Git, leitura, edição), para
// comparar o custo de teste de uma phase entre versões da skill.
//
// Fica fora do pacote da skill porque lê arquivos do host (`~/.claude/projects/<projeto>/`), e
// não o disco nem o Git do projeto, que é o limite dos scripts de `skills/vibeflow/scripts/`.
// Complementa `skills/vibeflow/scripts/medir.mjs`, que mede a phase pelo intervalo entre commits
// e não enxerga o que aconteceu dentro de cada passo.
//
// Como mede:
// - Duração de uma chamada: do evento `tool_use` ao `tool_result` de mesmo id, no mesmo arquivo.
// - Tempo ativo de um agente: soma dos intervalos de até PAUSA_MIN minutos entre eventos
//   consecutivos do arquivo dele; intervalo maior conta como pausa.
// - Tempo de modelo: ativo menos ferramenta.
// - Evento repetido: sessão retomada ou bifurcada copia o histórico para outro arquivo; cada
//   evento conta uma vez, pelo `uuid`, no primeiro arquivo em que aparece, e arquivo sem evento
//   novo não conta como agente.
// - Papel: `agentType` e `effort` do `<arquivo>.meta.json` vizinho; sem ele, `lider` ou, dentro
//   de uma pasta `subagents`, `subagente?`.
//
// Limites conhecidos:
// ponytail: o host corta a chamada longa perto do tempo limite e o resto vira leitura de saída em
//   segundo plano, contada como espera; o total de teste com espera é confiável, a divisão entre
//   os dois não. Separar exige ligar a espera ao comando de origem pelo id da tarefa.
// ponytail: comando com teste e tipos na mesma linha conta na primeira categoria que casa
//   (ordem de CATEGORIAS).
// ponytail: o formato do transcript é do host e não tem contrato; campo ausente é ignorado sem
//   erro, então um formato novo aparece como totais zerados, não como falha.
//
// Só lê. As amostras de comando lento saem cortadas em 110 caracteres e com valor de segredo
// evidente mascarado; ainda assim, a saída cita comandos do projeto e não deve ser publicada
// sem leitura.
//
// Uso:
//   node tools/tempo-transcripts.mjs <pasta de transcripts> [--de <ISO 8601>] [--ate <ISO 8601>] [--json]
// Saída: 0 com medição, 2 em erro de uso.

import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const PAUSA_MIN = 10;
const AMOSTRA_MIN_S = 60;

// A ordem decide a categoria do comando que casa mais de uma.
const CATEGORIAS = [
  ['e2e', /playwright|\be2e\b|cypress/i],
  ['tipos', /\btsc\b|typecheck|type-check|mypy|pyright/i],
  ['lint', /eslint|\bruff\b|\blint\b|prettier|biome/i],
  ['teste', /pytest|vitest|jest|node --test|(npm|pnpm|yarn|bun)( run)? test|go test|cargo test|unittest|test:/i],
  ['build', /\bbuild\b/i],
  ['espera', /\bsleep\b|Start-Sleep|\buntil\b|Wait-|timeout \d/i],
  ['git', /^\s*git\b/],
];
// Categorias que formam o custo de prova, somado por papel.
const DE_PROVA = new Set(['teste', 'e2e', 'tipos', 'lint', 'build', 'espera']);
const RE_SEGREDO = /((?:token|secret|password|senha|api[_-]?key|authorization)[^\s=:]*\s*[=:]\s*)\S+/gi;

/** Categoria de uma chamada de ferramenta; null para o despacho de subagente, contado no arquivo dele. */
export function categoria(nome, input) {
  if (nome === 'Agent' || nome === 'Task') return null;
  if (/TaskOutput|BashOutput|Monitor/.test(nome)) return 'espera';
  if (nome === 'Bash' || nome === 'PowerShell') {
    const comando = String(input?.command || '');
    for (const [chave, re] of CATEGORIAS) if (re.test(comando)) return chave;
    return 'shell-outro';
  }
  if (/Read|Grep|Glob/.test(nome)) return 'leitura';
  if (/Edit|Write/.test(nome)) return 'edicao';
  if (/Browser|chrome|playwright/i.test(nome)) return 'navegador';
  return 'outra-ferramenta';
}

function transcripts(pasta) {
  const achados = [];
  for (const nome of readdirSync(pasta)) {
    const caminho = join(pasta, nome);
    if (statSync(caminho).isDirectory()) achados.push(...transcripts(caminho));
    else if (nome.endsWith('.jsonl')) achados.push(caminho);
  }
  return achados;
}

function papelDe(arquivo) {
  let meta = {};
  try { meta = JSON.parse(readFileSync(arquivo.replace(/\.jsonl$/, '.meta.json'), 'utf8')); } catch { /* sem meta */ }
  const base = meta.agentType || (arquivo.split(sep).includes('subagents') ? 'subagente?' : 'lider');
  return meta.effort ? `${base}/${meta.effort}` : base;
}

/**
 * Mede os transcripts de `pasta` (recursivo) na janela [de, ate], em milissegundos de época.
 * Devolve tempos em ms: totais, por categoria, por papel e as chamadas mais lentas por categoria.
 */
export function medirTranscripts(pasta, { de = -Infinity, ate = Infinity } = {}) {
  const categorias = {};
  const papeis = {};
  const amostras = {};
  let ativoMs = 0;
  let emSegundoPlano = 0;
  const vistos = new Set();
  const arquivos = transcripts(pasta);

  for (const arquivo of arquivos) {
    const chave = papelDe(arquivo);
    const papel = (papeis[chave] ||= { agentes: 0, ativoMs: 0, ferramentaMs: 0, provaMs: 0 });
    let contou = false;
    const abertas = new Map();
    let anterior = null;

    for (const linha of readFileSync(arquivo, 'utf8').split(/\r?\n/)) {
      if (!linha.trim()) continue;
      let evento;
      try { evento = JSON.parse(linha); } catch { continue; }
      const ts = Date.parse(evento.timestamp);
      if (!ts || ts < de || ts > ate) continue;
      if (evento.uuid) {
        if (vistos.has(evento.uuid)) continue;
        vistos.add(evento.uuid);
      }
      if (!contou) { contou = true; papel.agentes++; }
      if (anterior !== null && ts > anterior && ts - anterior <= PAUSA_MIN * 60e3) {
        ativoMs += ts - anterior;
        papel.ativoMs += ts - anterior;
      }
      anterior = ts;

      const blocos = evento.message?.content;
      if (!Array.isArray(blocos)) continue;
      for (const bloco of blocos) {
        if (bloco.type === 'tool_use') {
          abertas.set(bloco.id, { ts, nome: bloco.name, input: bloco.input });
          if ((bloco.name === 'Bash' || bloco.name === 'PowerShell') && bloco.input?.run_in_background) emSegundoPlano++;
        }
        if (bloco.type === 'tool_result' && abertas.has(bloco.tool_use_id)) {
          const uso = abertas.get(bloco.tool_use_id);
          abertas.delete(bloco.tool_use_id);
          const cat = categoria(uso.nome, uso.input);
          if (!cat) continue;
          const duracao = ts - uso.ts;
          const c = (categorias[cat] ||= { ms: 0, chamadas: 0 });
          c.ms += duracao;
          c.chamadas++;
          papel.ferramentaMs += duracao;
          if (DE_PROVA.has(cat)) papel.provaMs += duracao;
          if (DE_PROVA.has(cat) && duracao > AMOSTRA_MIN_S * 1000) {
            const comando = String(uso.input?.command || uso.nome).replace(RE_SEGREDO, '$1***').slice(0, 110);
            (amostras[cat] ||= []).push({ segundos: Math.round(duracao / 1000), comando });
          }
        }
      }
    }
  }

  for (const [chave, p] of Object.entries(papeis)) if (!p.agentes) delete papeis[chave];
  for (const lista of Object.values(amostras)) lista.sort((a, b) => b.segundos - a.segundos).splice(4);
  const ferramentaMs = Object.values(categorias).reduce((soma, c) => soma + c.ms, 0);
  return { arquivos: arquivos.length, ativoMs, ferramentaMs, emSegundoPlano, categorias, papeis, amostras };
}

const horas = (ms) => (ms / 3600e3).toFixed(1);

/** Relatório em texto da medição. */
export function relatorio(m) {
  const linhas = [
    `transcripts: ${m.arquivos} · tempo ativo (intervalos de até ${PAUSA_MIN} min): ${horas(m.ativoMs)} h · em ferramentas: ${horas(m.ferramentaMs)} h · comandos em segundo plano: ${m.emSegundoPlano}`,
    '',
    'categoria          minutos  chamadas  % do ativo',
  ];
  for (const [chave, c] of Object.entries(m.categorias).sort((a, b) => b[1].ms - a[1].ms)) {
    const pct = m.ativoMs ? ((100 * c.ms) / m.ativoMs).toFixed(1) : '0.0';
    linhas.push(`${chave.padEnd(18)} ${(c.ms / 60e3).toFixed(0).padStart(7)}  ${String(c.chamadas).padStart(8)}  ${pct.padStart(10)}`);
  }
  for (const [chave, lista] of Object.entries(m.amostras)) {
    for (const a of lista) linhas.push(`  [${chave}] ${a.segundos}s ${a.comando}`);
  }
  linhas.push('', 'papel/esforço                  agentes  h ativas  h ferramenta  h prova e espera  h modelo');
  for (const [chave, p] of Object.entries(m.papeis).sort((a, b) => b[1].ativoMs - a[1].ativoMs)) {
    linhas.push(`${chave.padEnd(30)} ${String(p.agentes).padStart(7)}  ${horas(p.ativoMs).padStart(8)}  ${horas(p.ferramentaMs).padStart(12)}  ${horas(p.provaMs).padStart(16)}  ${horas(Math.max(0, p.ativoMs - p.ferramentaMs)).padStart(8)}`);
  }
  return linhas.join('\n');
}

function usoInvalido(mensagem) {
  process.stderr.write(`${mensagem}\nUso: node tools/tempo-transcripts.mjs <pasta de transcripts> [--de <ISO 8601>] [--ate <ISO 8601>] [--json]\n`);
  process.exit(2);
}

if (process.argv[1] && resolve(process.argv[1]).toLowerCase() === fileURLToPath(import.meta.url).toLowerCase()) {
  const args = process.argv.slice(2);
  const opcoes = {};
  let pasta = null;
  let json = false;
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--json') json = true;
    else if (args[i] === '--de' || args[i] === '--ate') {
      const valor = Date.parse(args[++i]);
      if (Number.isNaN(valor)) usoInvalido(`Data inválida em ${args[i - 1]}.`);
      opcoes[args[i - 1].slice(2)] = valor;
    } else if (args[i].startsWith('--')) usoInvalido(`Opção desconhecida: ${args[i]}.`);
    else if (pasta === null) pasta = args[i];
    else usoInvalido('Informe uma única pasta.');
  }
  if (pasta === null) usoInvalido('Falta a pasta de transcripts.');
  let ehPasta = false;
  try { ehPasta = statSync(pasta).isDirectory(); } catch { /* inexistente */ }
  if (!ehPasta) usoInvalido(`Pasta não encontrada: ${pasta}.`);

  const medicao = medirTranscripts(pasta, opcoes);
  const ascii = (texto) => texto.replace(/[\u007F-￿]/g, (ch) => `\\u${ch.charCodeAt(0).toString(16).padStart(4, '0')}`);
  process.stdout.write(`${json ? ascii(JSON.stringify(medicao, null, 2)) : relatorio(medicao)}\n`);
}
