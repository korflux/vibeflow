#!/usr/bin/env node
// governanca.mjs: confere os arquivos de governança que o init produz e o backup de um
// arquivo de regra antes de substituí-lo.
//
// Modo padrão (references/init.md, passos 1, 2, 4 e 5): `AGENTS.md` regular e não vazio,
// delimitadores `VIBEFLOW:CADEIA` pareados e bloco igual ao de templates/AGENTS.md, ponte
// `.agents/rules/vibeflow.md` com o conteúdo exato, `.vibeflow/phases/.gitkeep`, cada
// perfil global (ausente, idêntico ou diferente da fonte), perfil `corretor` obsoleto e
// perfil de projeto que difere da fonte.
// Modo --backup (references/disco.md, Backup de arquivo de regra, passo 2): cópia regular
// com o mesmo tamanho e o mesmo SHA-256 do original.
// Só lê: não cria, copia, substitui nem remove nada. Perfil presente no disco não prova
// que o host o carregou; essa conferência continua nas ferramentas do host. Divergência
// entre este script e a prosa é bug do script.
//
// Uso:
//   node governanca.mjs [--raiz <dir>] [--json]
//   node governanca.mjs --backup <original> <copia> [--json]
// Saída: 0 sem achado, 1 com achado, 2 em erro de uso.

import { existsSync, lstatSync, readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { homedir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { jsonAscii, executadoDireto } from './_disco.mjs';

const TEMPLATES = join(dirname(fileURLToPath(import.meta.url)), '..', 'templates');
const PAPEIS = ['explorador', 'implementador', 'verificador', 'revisor', 'redator'];
const PONTE = '@../../AGENTS.md\n';
const INICIO = '<!-- VIBEFLOW:CADEIA start -->';
const FIM = '<!-- VIBEFLOW:CADEIA end -->';

/**
 * Hosts com perfis globais (references/init.md, Entrada): a pasta vem da variável do host
 * quando definida, senão da pasta do usuário.
 */
function hosts() {
  return [
    { host: 'claude', pasta: process.env.CLAUDE_CONFIG_DIR || join(homedir(), '.claude'), projeto: '.claude', ext: 'md' },
    { host: 'codex', pasta: process.env.CODEX_HOME || join(homedir(), '.codex'), projeto: '.codex', ext: 'toml' },
  ];
}

const ehLink = (p) => existsSync(p) && lstatSync(p).isSymbolicLink();
const linhasSemCr = (buf) => buf.toString('utf8').replace(/^﻿/, '').split(/\r?\n/);

/**
 * Estado de um arquivo contra a fonte: ausente, idêntico ou diferente. Compara o conteúdo
 * sem distinguir CRLF de LF nem BOM (references/init.md, passo 5): o checkout com
 * autocrlf muda só a quebra de linha, e isso não é customização.
 */
function comparar(destino, fonte) {
  if (!existsSync(destino)) return 'ausente';
  return linhasSemCr(readFileSync(destino)).join('\n') === linhasSemCr(readFileSync(fonte)).join('\n') ? 'idêntico' : 'diferente';
}

/** Linhas entre os delimitadores (exclusive), ou um achado de pareamento. */
function blocoCadeia(linhas) {
  const ini = linhas.map((l, i) => (l.trim() === INICIO ? i : -1)).filter((i) => i >= 0);
  const fim = linhas.map((l, i) => (l.trim() === FIM ? i : -1)).filter((i) => i >= 0);
  if (!ini.length && !fim.length) return { achado: 'AGENTS.md sem o bloco VIBEFLOW:CADEIA' };
  if (ini.length !== 1 || fim.length !== 1 || fim[0] < ini[0]) return { achado: 'AGENTS.md com delimitador VIBEFLOW:CADEIA sem par, repetido ou invertido' };
  return { bloco: linhas.slice(ini[0] + 1, fim[0]) };
}

// ---------------------------------------------------------------------------
// Modo padrão: governança do repositório e perfis
// ---------------------------------------------------------------------------

/** Confere a governança da raiz e dos perfis; exportado para os testes. */
export function conferirGovernanca(raiz) {
  const achados = [];
  const avisos = [];

  // AGENTS.md e bloco da cadeia (init, passo 2)
  const agents = join(raiz, 'AGENTS.md');
  let agentsEstado = 'ok';
  if (!existsSync(agents)) agentsEstado = 'ausente';
  else if (ehLink(agents) || !lstatSync(agents).isFile()) agentsEstado = 'não é arquivo regular';
  else if (!readFileSync(agents, 'utf8').trim()) agentsEstado = 'vazio';
  if (agentsEstado !== 'ok') achados.push(`AGENTS.md ${agentsEstado}`);
  else {
    const b = blocoCadeia(linhasSemCr(readFileSync(agents)));
    const modelo = blocoCadeia(linhasSemCr(readFileSync(join(TEMPLATES, 'AGENTS.md'))));
    if (b.achado) { achados.push(b.achado); agentsEstado = 'sem bloco válido'; }
    else if (b.bloco.join('\n') !== modelo.bloco.join('\n')) { achados.push('bloco VIBEFLOW:CADEIA diferente de templates/AGENTS.md'); agentsEstado = 'bloco desatualizado'; }
  }

  // Ponte Antigravity (init, passo 4)
  const ponte = join(raiz, '.agents', 'rules', 'vibeflow.md');
  let ponteEstado = 'ok';
  if (!existsSync(ponte)) ponteEstado = 'ausente';
  else if (ehLink(ponte)) ponteEstado = 'é link';
  // A quebra de linha final pode ser CRLF num checkout com autocrlf.
  else if (readFileSync(ponte, 'utf8').replace(/\r\n$/, '\n') !== PONTE) ponteEstado = 'conteúdo diferente';
  if (ponteEstado !== 'ok') achados.push(`ponte .agents/rules/vibeflow.md ${ponteEstado}`);

  // Estrutura (init, passo 1)
  const gitkeep = existsSync(join(raiz, '.vibeflow', 'phases', '.gitkeep'));
  if (!gitkeep) achados.push('.vibeflow/phases/.gitkeep ausente');

  // Perfis globais, obsoletos e de projeto (init, passo 5)
  const perfis = [];
  const obsoletos = [];
  const projeto = [];
  for (const h of hosts()) {
    for (const papel of PAPEIS) {
      const fonte = join(TEMPLATES, 'agents', h.host, `${papel}.${h.ext}`);
      const destino = join(h.pasta, 'agents', `${papel}.${h.ext}`);
      const estado = comparar(destino, fonte);
      perfis.push({ host: h.host, papel, path: destino, estado });
      if (estado !== 'idêntico') achados.push(`perfil global ${h.host}/${papel} ${estado}: ${destino}`);
      const local = join(raiz, h.projeto, 'agents', `${papel}.${h.ext}`);
      if (existsSync(local) && comparar(local, fonte) === 'diferente') {
        projeto.push({ host: h.host, papel, path: local });
        avisos.push(`perfil de projeto ${h.host}/${papel} difere da fonte (customização do projeto): ${local}`);
      }
    }
    const corretor = join(h.pasta, 'agents', `corretor.${h.ext}`);
    if (existsSync(corretor)) {
      obsoletos.push(corretor);
      achados.push(`perfil obsoleto corretor em ${corretor}: preservar e levar ao humano`);
    }
  }

  return { modo: 'governanca', agents: agentsEstado, ponte: ponteEstado, gitkeep, perfis, obsoletos, projeto, achados, avisos };
}

// ---------------------------------------------------------------------------
// Modo --backup
// ---------------------------------------------------------------------------

const sha256 = (p) => createHash('sha256').update(readFileSync(p)).digest('hex');

/** Confere a cópia de backup contra o original: arquivo regular, mesmo tamanho e SHA-256. */
export function conferirBackup(original, copia) {
  if (!existsSync(original)) return { erro: `original não encontrado: ${original}` };
  const achados = [];
  const r = { modo: 'backup', original, copia, achados };
  if (!existsSync(copia)) { achados.push('cópia ausente'); return r; }
  if (ehLink(copia) || !lstatSync(copia).isFile()) { achados.push('cópia não é arquivo regular'); return r; }
  r.tamanho = { original: lstatSync(original).size, copia: lstatSync(copia).size };
  r.sha256 = { original: sha256(original), copia: sha256(copia) };
  if (r.tamanho.original !== r.tamanho.copia) achados.push('tamanho da cópia diferente do original');
  if (r.sha256.original !== r.sha256.copia) achados.push('SHA-256 da cópia diferente do original');
  return r;
}

// ---------------------------------------------------------------------------
// Execução
// ---------------------------------------------------------------------------

function lerArgs(argv) {
  const args = { raiz: process.cwd(), json: false, backup: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--json') args.json = true;
    else if (a === '--raiz' && argv[i + 1]) args.raiz = argv[++i];
    else if (a === '--backup' && argv[i + 1] && argv[i + 2]) args.backup = [argv[++i], argv[++i]];
    else return { erro: `argumento desconhecido ou sem valor: ${a}` };
  }
  return args;
}

function texto(r) {
  const l = [];
  if (r.modo === 'backup') {
    l.push(`backup: ${r.copia} contra ${r.original}`);
    if (r.sha256) l.push(`sha256: ${r.sha256.copia}`);
  } else {
    const contagem = (e) => r.perfis.filter((p) => p.estado === e).length;
    l.push(`AGENTS.md: ${r.agents} · ponte: ${r.ponte} · .gitkeep: ${r.gitkeep ? 'ok' : 'ausente'}`);
    l.push(`perfis globais: ${contagem('idêntico')} idênticos, ${contagem('ausente')} ausentes, ${contagem('diferente')} diferentes`);
  }
  for (const a of r.achados) l.push(`achado: ${a}`);
  for (const a of r.avisos || []) l.push(`aviso: ${a}`);
  if (!r.achados.length) l.push('sem achado');
  return `${l.join('\n')}\n`;
}

function principal() {
  const args = lerArgs(process.argv.slice(2));
  if (args.erro) { console.error(args.erro); return 2; }
  const r = args.backup ? conferirBackup(resolve(args.backup[0]), resolve(args.backup[1])) : conferirGovernanca(resolve(args.raiz));
  if (r.erro) { console.error(r.erro); return 2; }
  process.stdout.write(args.json ? `${jsonAscii(r)}\n` : texto(r));
  return r.achados.length ? 1 : 0;
}

if (executadoDireto(import.meta.url)) {
  process.exitCode = principal();
}
