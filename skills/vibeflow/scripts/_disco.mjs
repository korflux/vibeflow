// _disco.mjs: leitura compartilhada do disco do VibeFlow pelos scripts estado, conferir,
// plan e governanca.
//
// Responsabilidade: transformar artefatos (.md) e Git em dados, aplicando as regras
// mecânicas de references/disco.md (cabeçalho, passo do plan, Arquivos:, checkpoint,
// achados do analyze, commits). Não decide etapa nem escreve nada: só lê. O contrato
// continua sendo a prosa; divergência entre este módulo e a prosa é bug deste módulo.
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
  const texto = readFileSync(caminho, 'utf8').replace(/^\uFEFF/, '');
  return texto.split(/\r?\n/);
}

/** Valor de uma linha de cabeçalho `# Nome: valor` (Status, Rota, Risco) ou null. */
export function cabecalho(linhas, nome) {
  if (!linhas) return null;
  const re = new RegExp(`^# ${nome}:\\s*(.+?)\\s*$`);
  for (const l of linhas) {
    const m = l.match(re);
    if (m) return m[1];
  }
  return null;
}

// ---------------------------------------------------------------------------
// Phases e MVP (references/disco.md, Paths, Abrir phase e Compatibilidade)
// ---------------------------------------------------------------------------

// Artefatos vivos do contrato 5.0.0, na ordem em que nascem.
export const ARTEFATOS = ['spec', 'plan', 'review'];
// Rotas aceitas em `# Rota:`. xhigh e max só existem no formato antigo (Compatibilidade).
export const ROTAS = ['medium', 'high', 'mvp'];
const ARTEFATOS_ANTIGOS = ['interview', 'design', 'analyze'];
const ROTAS_ANTIGAS = ['xhigh', 'max'];
const RE_PHASE = /^phase-([1-9][0-9]*)-([a-z0-9]+(?:-[a-z0-9]+)*)$/;

/** Slug válido: a-z, 0-9 e hífen simples, sem hífen nas pontas, 2 a 48 caracteres. */
export function slugValido(slug) {
  return slug.length >= 2 && slug.length <= 48 && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug);
}

/**
 * Slug a partir de uma frase (disco.md, Abrir phase): minúsculas, sem acento, só a-z, 0-9
 * e hífen, hífens repetidos viram um e os das pontas saem. Não corta nem inventa: o
 * resultado fora de 2 a 48 caracteres é recusado por slugValido, e quem chama escolhe
 * outra frase.
 */
export function normalizarSlug(frase) {
  return frase.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
    .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
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

/**
 * Formato antigo (disco.md, Compatibilidade): interview.md, design.md ou analyze.md,
 * `# Rota:` xhigh ou max, ou plan.md com blocos `### T<n>:`. Só serve para reconhecer
 * phase antiga: a fechada fica intocada e a aberta é inconsistência.
 */
function formatoAntigo(pasta, art, rota) {
  return ARTEFATOS_ANTIGOS.some((a) => existsSync(join(pasta, `${a}.md`)))
    || ROTAS_ANTIGAS.includes(rota)
    || (art.plan || []).some((l) => /^### T[1-9][0-9]*:/.test(l));
}

/**
 * Carrega um alvo (phase ou MVP): linhas de cada artefato presente, rota, risco, se está
 * fechado (review aprovada sem R* aberto) e se está no formato antigo.
 */
export function carregarAlvo(alvo, pasta, nome) {
  const art = {};
  for (const a of ARTEFATOS) art[a] = lerLinhas(join(pasta, `${a}.md`));
  // A rota fica no primeiro artefato: spec.md em high e mvp, review.md em medium.
  const rota = ['spec', 'review'].map((a) => cabecalho(art[a], 'Rota')).find(Boolean) || null;
  const risco = cabecalho(art.spec, 'Risco');
  const rAbertos = lerRs(art.review).filter((r) => !r.feito);
  const fechado = cabecalho(art.review, 'Status') === 'aprovado' && rAbertos.length === 0;
  return { alvo, pasta, nome, art, rota, risco, fechado, antigo: formatoAntigo(pasta, art, rota) };
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

/** Caminhos do alvo que são link, inclusive os próprios artefatos (proibido escrever através deles). */
export function linksNoCaminho(raiz, pasta) {
  const candidatos = [join(raiz, '.vibeflow'), join(raiz, '.vibeflow', 'phases'), join(raiz, '.vibeflow', 'mvp'), pasta,
    ...ARTEFATOS.map((a) => join(pasta, `${a}.md`))];
  return candidatos.filter((c) => existsSync(c) && lstatSync(c).isSymbolicLink());
}

// ---------------------------------------------------------------------------
// Plan: passos e checkpoints (references/disco.md, Plan)
// ---------------------------------------------------------------------------

export const SEP = ' · ';
export const RE_PASSO = /^- \[([ xX])\] ([1-9][0-9]*)([a-z])?: (.*)$/;
export const RE_CHECKPOINT = /^- \[([ xX])\] Checkpoint:\s*(.*)$/;

/**
 * Paths do campo `Arquivos:` de uma linha de passo: só o texto entre crases do trecho
 * entre `Arquivos:` e `· Prova:`. Null quando a linha não tem o campo. Os marcadores
 * levam o separador ` · ` para não casar com a palavra solta dentro do resultado.
 */
function lerArquivos(restoDaLinha) {
  const marca = `${SEP}Arquivos:`;
  const i = restoDaLinha.indexOf(marca);
  if (i < 0) return null;
  const depois = restoDaLinha.slice(i + marca.length);
  const j = depois.indexOf(`${SEP}Prova:`);
  return [...(j < 0 ? depois : depois.slice(0, j)).matchAll(/`([^`]*)`/g)].map((m) => m[1]);
}

/**
 * Critérios do campo `Aceite:` de uma linha de passo: o texto entre `Aceite:` e o campo
 * seguinte (`Arquivos:` ou `Prova:`). Devolve { bruto, ids }, com ids vazio para `nenhum`;
 * null quando a linha não tem o campo.
 */
function lerAceite(restoDaLinha) {
  const marca = `${SEP}Aceite:`;
  const i = restoDaLinha.indexOf(marca);
  if (i < 0) return null;
  const depois = restoDaLinha.slice(i + marca.length);
  const fim = [`${SEP}Arquivos:`, `${SEP}Prova:`].map((m) => depois.indexOf(m)).filter((j) => j >= 0);
  const bruto = (fim.length ? depois.slice(0, Math.min(...fim)) : depois).trim();
  return { bruto, ids: [...bruto.matchAll(/\bA[1-9][0-9]*\b/g)].map((a) => a[0]) };
}

/**
 * Lê o plan: itens na ordem do arquivo (passos e checkpoints, cada um com a caixa),
 * passos e se o analyze já rodou (seção `## Achados do analyze` presente).
 * Passo: { tipo, id, num, letra, caixa, arquivos, aceite, resto }, com `resto` sendo a
 * linha depois de `<ID>: `. Checkpoint: { tipo, caixa, aceite }.
 *
 * ponytail: lê o arquivo inteiro, sem distinguir seção nem bloco de código; restringir à
 * seção de passos se o template do plan ganhar outra lista com linhas no formato do passo.
 */
export function lerPlan(linhasPlan) {
  const itens = [];
  for (const l of linhasPlan || []) {
    let m = l.match(RE_PASSO);
    if (m) {
      itens.push({ tipo: 'passo', id: `${m[2]}${m[3] || ''}`, num: Number(m[2]), letra: m[3] || null, caixa: m[1] !== ' ', arquivos: lerArquivos(m[4]), aceite: lerAceite(m[4]), resto: m[4] });
      continue;
    }
    m = l.match(RE_CHECKPOINT);
    if (m) itens.push({ tipo: 'checkpoint', caixa: m[1] !== ' ', aceite: [...m[2].matchAll(/\bA[1-9][0-9]*\b/g)].map((a) => a[0]) });
  }
  return {
    itens,
    passos: itens.filter((i) => i.tipo === 'passo'),
    analisado: (linhasPlan || []).some((l) => l.trim() === '## Achados do analyze'),
  };
}

/** Passos agrupados por número, na ordem do arquivo: passo sozinho e grupo paralelo são ambos grupos. */
export function grupos(passos) {
  const saida = [];
  for (const p of passos) {
    const ult = saida[saida.length - 1];
    if (ult && ult.num === p.num) ult.passos.push(p);
    else saida.push({ num: p.num, passos: [p] });
  }
  return saida;
}

// ---------------------------------------------------------------------------
// Arquivos: normalização e sobreposição (references/disco.md, Plan > Arquivos)
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

/**
 * Segmentos de um path real vindo do git status, sem a regra de path incomparável, que
 * vale só para a autoria de `Arquivos:`.
 */
export function segmentos(caminho) {
  return caminho.replace(/\\/g, '/').split('/').filter((s) => s && s !== '.');
}

/** Recorte de um passo: lista de paths normalizados, ou null se sem Arquivos ou com path incomparável. */
export function recorte(passo) {
  if (!passo.arquivos || !passo.arquivos.length) return null;
  const norm = passo.arquivos.map(normalizarPath);
  return norm.some((n) => n === null) ? null : norm;
}

const minusculaAscii = (s) => s.replace(/[A-Z]/g, (c) => c.toLowerCase());

/** Dois paths se sobrepõem quando são iguais ou um é prefixo de diretório do outro. */
export function sobrepoe(a, b) {
  const n = Math.min(a.length, b.length);
  for (let i = 0; i < n; i++) if (minusculaAscii(a[i]) !== minusculaAscii(b[i])) return false;
  return true;
}

/** Path real (segmentos) dentro do recorte: algum path do recorte é ele mesmo ou um diretório acima dele. */
export function dentroDoRecorte(caminho, rec) {
  return rec.some((r) => r.length <= caminho.length && sobrepoe(r, caminho));
}

/** Dois recortes se sobrepõem quando algum par de paths se sobrepõe. */
export function recortesSobrepoem(ra, rb) {
  return ra.some((a) => rb.some((b) => sobrepoe(a, b)));
}

/**
 * Achados mecânicos do plan, como texto:
 *  - numeração: 1, 2, 3 de 1 em 1 na ordem do arquivo; passo sozinho sem letra; grupo
 *    com letras a, b, c em sequência;
 *  - grupo paralelo: passos irmãos sem `Arquivos:` sobrepostos, e nenhum com `Arquivos:`
 *    ausente ou com path incomparável (esse passo não divide número).
 */
export function achadosDoPlan(passos) {
  const achados = [];
  const gs = grupos(passos);
  const iForaDeSequencia = gs.findIndex((g, i) => g.num !== i + 1);
  if (iForaDeSequencia >= 0) {
    achados.push(`numeração fora de sequência no passo ${gs[iForaDeSequencia].passos[0].id} (esperado ${iForaDeSequencia + 1})`);
  }
  for (const g of gs) {
    const ids = g.passos.map((p) => p.id);
    const esperado = g.passos.length === 1 ? [String(g.num)] : g.passos.map((_, k) => `${g.num}${String.fromCharCode(97 + k)}`);
    if (ids.join() !== esperado.join()) achados.push(`IDs do passo ${g.num} fora do padrão: ${ids.join(', ')} (esperado ${esperado.join(', ')})`);
    if (g.passos.length < 2) continue;
    const comRecorte = [];
    for (const p of g.passos) {
      const r = recorte(p);
      if (r === null) {
        const motivo = !p.arquivos || !p.arquivos.length ? 'campo ausente' : 'path incomparável';
        achados.push(`passo ${p.id} divide o número ${g.num} sem Arquivos: comparáveis (${motivo})`);
      } else {
        comRecorte.push({ p, r });
      }
    }
    for (let i = 0; i < comRecorte.length; i++) {
      for (let j = i + 1; j < comRecorte.length; j++) {
        if (recortesSobrepoem(comRecorte[i].r, comRecorte[j].r)) achados.push(`passos irmãos ${comRecorte[i].p.id} e ${comRecorte[j].p.id} com Arquivos: sobrepostos`);
      }
    }
  }
  return achados;
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

/**
 * Proposta marcada no veredito: 'approve', 'request-changes' ou null. As duas caixas
 * `**Approve**` e `**Request changes**` só existem no veredito do review.md, então a
 * busca no arquivo todo dispensa saber o título da seção.
 */
export function vereditoReview(linhasReview) {
  const corpo = linhasReview || [];
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

/**
 * Executa git com argumentos em lista e devolve { codigo, out } mesmo quando o comando
 * falha, para checagens cujo código de saída é o resultado (`git diff --cached --check`).
 */
export function gitComCodigo(raiz, args) {
  try {
    return { codigo: 0, out: execFileSync('git', args, { cwd: raiz, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }) };
  } catch (e) {
    return { codigo: typeof e.status === 'number' ? e.status : 2, out: e.stdout ? String(e.stdout) : '' };
  }
}

/** Paths no índice (staging) em relação ao HEAD, relativos à raiz, com barra; null sem Git. */
export function emStaging(raiz) {
  const out = git(raiz, ['diff', '--cached', '--name-only', '-z']);
  return out === null ? null : out.split('\0').filter(Boolean);
}

/** Linhas de um arquivo no índice (`:path`) ou no HEAD (`HEAD:path`); null se ausente lá. */
export function linhasNoGit(raiz, ref, caminhoRelativo) {
  const out = git(raiz, ['show', `${ref}:${caminhoRelativo}`]);
  return out === null ? null : out.replace(/^\uFEFF/, '').split(/\r?\n/);
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
 * Devolve { tipo, alvo, ids } ou null para commit fora do contrato. `task` leva os IDs
 * de passo (`2a`) e de R* (`R1`) do alvo; `medium` e `low` são entregas sem phase.
 */
export function classificarCommit(assunto) {
  let m = assunto.match(/^task\(((?:phase-[1-9][0-9]*)|mvp):([^)]*)\):/);
  if (m) return { tipo: 'task', alvo: m[1], ids: m[2].split(',').map((s) => s.trim()).filter(Boolean) };
  m = assunto.match(/^task\((medium|low)\):/);
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
  return JSON.stringify(valor, null, 2).replace(/[\u007F-\uFFFF]/g, (c) => `\\u${c.charCodeAt(0).toString(16).padStart(4, '0')}`);
}
