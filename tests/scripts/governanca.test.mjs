// governanca.test.mjs: testes de comportamento do script governanca da skill vibeflow.
//
// Confere AGENTS.md e o bloco da cadeia, a ponte, o .gitkeep, os perfis globais por host
// (com CLAUDE_CONFIG_DIR e CODEX_HOME apontando para pastas temporárias), o perfil
// corretor obsoleto, o perfil de projeto customizado e o backup por tamanho e SHA-256
// (references/init.md e references/disco.md, Backup). Rodar com: node --test

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, rmSync, readFileSync, copyFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { conferirGovernanca, conferirBackup } from '../../skills/vibeflow/scripts/governanca.mjs';
import { repo, escrever, cli, SCRIPTS } from './_apoio.mjs';

const TEMPLATES = join(SCRIPTS, '..', 'templates');
const PAPEIS = ['explorador', 'implementador', 'verificador', 'revisor', 'redator'];

/** Pastas de host temporárias nas variáveis do host, restauradas ao fim do teste. */
function hosts(t) {
  const claude = mkdtempSync(join(tmpdir(), 'vibeflow-claude-'));
  const codex = mkdtempSync(join(tmpdir(), 'vibeflow-codex-'));
  const antes = { c: process.env.CLAUDE_CONFIG_DIR, x: process.env.CODEX_HOME };
  process.env.CLAUDE_CONFIG_DIR = claude;
  process.env.CODEX_HOME = codex;
  t.after(() => {
    for (const [k, v] of [['CLAUDE_CONFIG_DIR', antes.c], ['CODEX_HOME', antes.x]]) {
      if (v === undefined) delete process.env[k]; else process.env[k] = v;
    }
    rmSync(claude, { recursive: true, force: true });
    rmSync(codex, { recursive: true, force: true });
  });
  return { claude, codex };
}

/** Instala os perfis como o init faz, com CRLF no Claude para simular o checkout com autocrlf. */
function instalar({ claude, codex }) {
  for (const p of PAPEIS) {
    escrever(claude, `agents/${p}.md`, readFileSync(join(TEMPLATES, 'agents/claude', `${p}.md`), 'utf8').replace(/\r?\n/g, '\r\n'));
    escrever(codex, `agents/${p}.toml`, readFileSync(join(TEMPLATES, 'agents/codex', `${p}.toml`), 'utf8'));
  }
}

/** Repo com AGENTS.md no template, ponte e .gitkeep: governança completa. */
function completo(t) {
  const raiz = repo(t);
  escrever(raiz, 'AGENTS.md', readFileSync(join(TEMPLATES, 'AGENTS.md'), 'utf8'));
  escrever(raiz, '.agents/rules/vibeflow.md', '@../../AGENTS.md\r\n');
  return raiz;
}

test('governança completa e perfis idênticos (CRLF não conta) não têm achado', (t) => {
  const h = hosts(t);
  instalar(h);
  const r = conferirGovernanca(completo(t));
  assert.deepEqual(r.achados, []);
  assert.equal(r.perfis.filter((p) => p.estado === 'idêntico').length, 10);
});

test('perfis ausentes, diferentes e corretor obsoleto são achado; perfil de projeto customizado é aviso', (t) => {
  const h = hosts(t);
  instalar(h);
  escrever(h.claude, 'agents/revisor.md', 'customizado\n');
  rmSync(join(h.codex, 'agents', 'redator.toml'));
  escrever(h.codex, 'agents/corretor.toml', 'x\n');
  const raiz = completo(t);
  escrever(raiz, '.claude/agents/explorador.md', 'do projeto\n');
  const r = conferirGovernanca(raiz);
  assert.deepEqual(r.achados.map((a) => a.replace(/: .*$/, '')), [
    'perfil global claude/revisor diferente',
    'perfil global codex/redator ausente',
    'perfil obsoleto corretor em ' + join(h.codex, 'agents', 'corretor.toml').replace(/: .*$/, ''),
  ]);
  assert.equal(r.avisos.length, 1);
  assert.match(r.avisos[0], /perfil de projeto claude\/explorador difere da fonte/);
});

test('AGENTS.md com bloco desatualizado ou sem par, ponte diferente e .gitkeep ausente são achado', (t) => {
  instalar(hosts(t));
  const raiz = completo(t);
  escrever(raiz, 'AGENTS.md', '# Regras\n<!-- VIBEFLOW:CADEIA start -->\nantigo\n<!-- VIBEFLOW:CADEIA end -->\n');
  escrever(raiz, '.agents/rules/vibeflow.md', '@AGENTS.md\n');
  rmSync(join(raiz, '.vibeflow', 'phases', '.gitkeep'));
  assert.deepEqual(conferirGovernanca(raiz).achados, [
    'bloco VIBEFLOW:CADEIA diferente de templates/AGENTS.md',
    'ponte .agents/rules/vibeflow.md conteúdo diferente',
    '.vibeflow/phases/.gitkeep ausente',
  ]);
  escrever(raiz, 'AGENTS.md', '# Regras\n<!-- VIBEFLOW:CADEIA start -->\n');
  assert.equal(conferirGovernanca(raiz).achados[0], 'AGENTS.md com delimitador VIBEFLOW:CADEIA sem par, repetido ou invertido');
});

test('backup: cópia igual passa; tamanho ou hash diferente e cópia ausente são achado', (t) => {
  const raiz = repo(t);
  const original = join(raiz, 'AGENTS.md');
  const copia = join(raiz, '.vibeflow', 'old', 'AGENTS.md');
  assert.deepEqual(conferirBackup(original, copia).achados, ['cópia ausente']);
  escrever(raiz, '.vibeflow/old/AGENTS.md', '');
  copyFileSync(original, copia);
  const ok = conferirBackup(original, copia);
  assert.deepEqual(ok.achados, []);
  assert.equal(ok.sha256.original, ok.sha256.copia);
  escrever(raiz, '.vibeflow/old/AGENTS.md', 'outro conteúdo qualquer\n');
  assert.deepEqual(conferirBackup(original, copia).achados, ['tamanho da cópia diferente do original', 'SHA-256 da cópia diferente do original']);
});

test('CLI: 2 em erro de uso e no backup sem original', (t) => {
  const raiz = repo(t);
  assert.equal(cli('governanca.mjs', ['--invalido']).codigo, 2);
  assert.equal(cli('governanca.mjs', ['--backup', join(raiz, 'nao-existe'), join(raiz, 'x')]).codigo, 2);
  assert.equal(cli('governanca.mjs', ['--backup', join(raiz, 'AGENTS.md'), join(raiz, 'AGENTS.md'), '--json']).codigo, 0);
});
