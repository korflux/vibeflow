#!/usr/bin/env node
// plan.mjs: confere a parte mecânica do plan.md contra o contrato e contra a spec.
//
// Aplica references/disco.md (Plan) e as conferências mecânicas de
// references/analyze/coverage.md: forma da linha de passo e de checkpoint, numeração e
// grupos paralelos, critérios de `Aceite:` e de checkpoint que existem na spec, critério
// da spec sem passo, seção `## Regressão completa` presente, `## Achados do analyze` como
// última seção e placeholder de template esquecido na spec ou no plan. Também aplica os
// limites de tamanho de Plan > Arquivos e Plan > Checkpoint: passo acima de 12 entradas de
// código, mais de quatro checkpoints, motivo de checkpoint fora da tabela fechada e
// checkpoint em plan de até 5 passos. Checkpoint sem motivo é aviso (campo `avisos`, sem
// efeito no código de saída), para que plan anterior à tabela de motivos siga com o mesmo
// resultado. O julgamento do analyze (prova que exercita o critério, arquivo ou consumidor
// esquecido, ordem, contradição com a spec, e se a condição do motivo vale: tela depois do
// visual, segundo grupo de risco, integração acima de 10 passos) continua do revisor. Só
// lê; divergência entre este script e a prosa é bug do script.
//
// Com --spec, confere só a spec, antes da aprovação (references/spec.md, Fechar): seções
// obrigatórias, decisão sem Pergunta: ou Motivo:, critério repetido, adjetivo vago no
// critério, valor sem origem em Decisões e Critérios de aceite (só em spec com
// `# Status: rascunho`; a origem é o marcador `(origem: humano | assumida | verificado
// <fonte>)` na mesma linha) e placeholder esquecido. Não exige plan.md.
//
// Uso:
//   node plan.mjs [--spec] [--alvo phase-N|mvp] [--raiz <dir>] [--json]
// Saída: 0 sem achado (aviso não conta), 1 com achado, 2 em erro de uso.

import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  carregarAlvos, alvoPadrao, alvoNomeado, lerLinhas, lerPlan, achadosDoPlan, RE_PASSO, RE_CHECKPOINT, SEP,
  cabecalho, ehEntradaDeTeste, jsonAscii, executadoDireto,
} from './_disco.mjs';

const TEMPLATES = join(dirname(fileURLToPath(import.meta.url)), '..', 'templates');

// ---------------------------------------------------------------------------
// Leitura de seções e limpeza de texto
// ---------------------------------------------------------------------------

/** Linhas de uma seção `## Título` até a próxima `## `; null se a seção não existe. */
function secao(linhas, titulo) {
  const i = (linhas || []).findIndex((l) => l.trim() === `## ${titulo}`);
  if (i < 0) return null;
  const fim = linhas.findIndex((l, j) => j > i && /^## /.test(l));
  return linhas.slice(i + 1, fim < 0 ? linhas.length : fim);
}

/**
 * Linhas sem comentários HTML (inclusive os de várias linhas). Os comentários do template
 * são instrução para quem grava, não conteúdo do artefato.
 */
function semComentarios(linhas) {
  const saida = [];
  let dentro = false;
  for (const l of linhas || []) {
    let resto = l;
    let limpa = '';
    while (resto) {
      if (dentro) {
        const f = resto.indexOf('-->');
        if (f < 0) { resto = ''; break; }
        resto = resto.slice(f + 3);
        dentro = false;
      } else {
        const a = resto.indexOf('<!--');
        if (a < 0) { limpa += resto; break; }
        limpa += resto.slice(0, a);
        resto = resto.slice(a + 4);
        dentro = true;
      }
    }
    saida.push(limpa);
  }
  return saida;
}

// ---------------------------------------------------------------------------
// Placeholders de template (references/disco.md, Escrever artefato)
// ---------------------------------------------------------------------------

/**
 * Placeholders de um template: cada `<...>` de nível externo fora de comentário, inclusive
 * os aninhados como `<phase-<n>-<slug> ou mvp>`. A fonte é o próprio template, então um
 * placeholder novo entra aqui sem mudar o script.
 */
function placeholdersDoTemplate(nome) {
  const linhas = semComentarios(lerLinhas(join(TEMPLATES, nome)));
  return [...new Set(linhas.flatMap((l) => [...l.matchAll(/<(?:[^<>\n]|<[^<>\n]*>)+>/g)].map((m) => m[0])))];
}

/**
 * Placeholders do template que sobraram no artefato. Texto entre crases fica de fora,
 * porque é como um artefato cita um placeholder de propósito (por exemplo, uma spec que
 * discute o próprio template).
 *
 * ponytail: compara só os placeholders literais do template; um placeholder reescrito à
 * mão com outra palavra passa, e só a leitura do revisor o pega.
 */
function placeholdersEsquecidos(linhas, nomeTemplate, rotulo) {
  const tokens = placeholdersDoTemplate(nomeTemplate);
  const achados = [];
  semComentarios(linhas).forEach((l, i) => {
    const visivel = l.replace(/`[^`]*`/g, '');
    for (const t of tokens) if (visivel.includes(t)) achados.push(`${rotulo}, linha ${i + 1}: placeholder ${t} não preenchido`);
  });
  return achados;
}

// ---------------------------------------------------------------------------
// Critérios da spec e forma do plan
// ---------------------------------------------------------------------------

/** IDs `A<n>` da seção `## Critérios de aceite` da spec, na ordem, com repetidos à parte. */
function criteriosDaSpec(linhasSpec) {
  const ids = [];
  const repetidos = [];
  for (const l of secao(linhasSpec, 'Critérios de aceite') || []) {
    const m = l.match(/^- (A[1-9][0-9]*):/);
    if (!m) continue;
    if (ids.includes(m[1])) repetidos.push(m[1]);
    else ids.push(m[1]);
  }
  return { ids, repetidos };
}

// Limites de tamanho do plan (references/disco.md, Plan > Arquivos e Plan > Checkpoint).
const TETO_CODIGO = 12;
const MAX_CHECKPOINTS = 4;
const PASSOS_SEM_CHECKPOINT = 5;
// Tabela fechada de motivos de checkpoint (references/disco.md, Plan > Checkpoint). A primeira
// linha da tabela tem dois nomes, `caminho fino` e `primeiro grupo de risco`.
const MOTIVOS = ['caminho fino', 'primeiro grupo de risco', 'segundo grupo de risco', 'tela', 'integração'];
const semAcento = (t) => t.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase();
// O motivo começa por um nome da tabela, sem letra colada depois; o que vem depois é explicação livre.
const RE_MOTIVO_DA_TABELA = new RegExp(`^(?:${MOTIVOS.map(semAcento).join('|')})(?!\\p{L})`, 'u');

/**
 * Achados de forma de uma linha de passo: campos na ordem `Aceite:`, `Arquivos:` opcional e
 * `Prova:`, e o teto de entradas de código em `Arquivos:`. A entrada de teste não conta
 * (`ehEntradaDeTeste`) e a pasta conta uma; o passo acima do teto se divide pelo resultado
 * verificável. Passo sem `Arquivos:` não tem o que contar.
 */
function formaDoPasso(p, criterios) {
  const achados = [];
  const r = p.resto;
  const iA = r.indexOf(`${SEP}Aceite:`);
  const iArq = r.indexOf(`${SEP}Arquivos:`);
  const iP = r.indexOf(`${SEP}Prova:`);
  if (iA <= 0) achados.push(`passo ${p.id}: falta o resultado antes de Aceite: ou o próprio campo Aceite:`);
  if (iP < 0) achados.push(`passo ${p.id}: falta o campo Prova:`);
  else if (!r.slice(iP + `${SEP}Prova:`.length).trim()) achados.push(`passo ${p.id}: Prova: vazia`);
  if (iA > 0 && iP > 0 && (iP < iA || (iArq >= 0 && (iArq < iA || iArq > iP)))) achados.push(`passo ${p.id}: campos fora da ordem Aceite:, Arquivos:, Prova:`);
  if (iArq >= 0 && (!p.arquivos || !p.arquivos.length)) achados.push(`passo ${p.id}: Arquivos: sem path entre crases`);
  const codigo = (p.arquivos || []).filter((a) => !ehEntradaDeTeste(a)).length;
  if (codigo > TETO_CODIGO) achados.push(`passo ${p.id}: ${codigo} entradas de código em Arquivos:, acima do teto de ${TETO_CODIGO}; divida o passo pelo resultado verificável`);
  if (p.aceite) {
    const sobra = p.aceite.bruto.replace(/\bA[1-9][0-9]*\b/g, '').replace(/[\s,]/g, '');
    if (p.aceite.bruto !== 'nenhum' && (sobra || !p.aceite.ids.length)) achados.push(`passo ${p.id}: Aceite: deve listar A* da spec ou dizer nenhum`);
    for (const a of p.aceite.ids) if (!criterios.includes(a)) achados.push(`passo ${p.id}: Aceite: cita ${a}, que não existe na spec`);
  }
  return achados;
}

/**
 * Checkpoints: linha depois de passo (nunca no início nem logo após outro checkpoint),
 * com critérios que existem na spec e que algum passo do trecho coberto entrega, e motivo da
 * tabela (`MOTIVOS`): fora da tabela é achado, sem motivo é aviso. Depois da forma, a
 * contagem: no máximo quatro checkpoints por phase e nenhum em plan de até 5 passos (passo
 * de grupo paralelo, como `2a` e `2b`, conta um a um). Se a condição do motivo vale (tela
 * depois do visual, segundo grupo de risco, integração acima de 10 passos) é julgamento do
 * analyze, não deste script. Devolve { achados, avisos }.
 */
function formaDosCheckpoints(itens, criterios) {
  const achados = [];
  const avisos = [];
  let trecho = [];
  itens.forEach((it, k) => {
    if (it.tipo === 'passo') { trecho.push(it); return; }
    const n = `checkpoint ${k + 1}º item`;
    if (!trecho.length) achados.push(`${n}: sem passo entre ele e o checkpoint anterior ou o início`);
    if (!it.aceite.length) achados.push(`${n}: sem critério listado`);
    const entregues = new Set(trecho.flatMap((p) => (p.aceite ? p.aceite.ids : [])));
    for (const a of it.aceite) {
      if (!criterios.includes(a)) achados.push(`${n}: cita ${a}, que não existe na spec`);
      else if (!entregues.has(a)) achados.push(`${n}: cita ${a}, que nenhum passo do trecho coberto entrega`);
    }
    if (!it.motivo) avisos.push(`${n}: sem motivo; acrescente · Motivo: <motivo da tabela de references/disco.md (Plan > Checkpoint)>`);
    else if (!RE_MOTIVO_DA_TABELA.test(semAcento(it.motivo))) achados.push(`${n}: motivo "${it.motivo.slice(0, 80)}" fora da tabela (${MOTIVOS.join(', ')})`);
    trecho = [];
  });
  const passos = itens.filter((it) => it.tipo === 'passo').length;
  const checkpoints = itens.length - passos;
  if (checkpoints > MAX_CHECKPOINTS) achados.push(`${checkpoints} checkpoints; o máximo é ${MAX_CHECKPOINTS} por phase`);
  if (checkpoints && passos <= PASSOS_SEM_CHECKPOINT) achados.push(`checkpoint em plan de ${passos} ${passos === 1 ? 'passo' : 'passos'}; phase com até ${PASSOS_SEM_CHECKPOINT} passos não tem checkpoint`);
  return { achados, avisos };
}

/** Linhas da seção `## Passos` que não são passo nem checkpoint (fora comentário e linha vazia). */
function linhasEstranhas(linhasPlan) {
  return semComentarios(secao(linhasPlan, 'Passos') || [])
    .filter((l) => l.trim() && !RE_PASSO.test(l) && !RE_CHECKPOINT.test(l))
    .map((l) => `linha fora do formato de passo ou checkpoint em ## Passos: ${l.trim().slice(0, 80)}`);
}

// ---------------------------------------------------------------------------
// Forma da spec antes da aprovação (references/spec.md, Gravação, Critérios de aceite e Fechar)
// ---------------------------------------------------------------------------

const SECOES_SPEC = ['Objetivo', 'Pontos do projeto', 'Decisões', 'Critérios de aceite', 'Fora do escopo'];

// Adjetivos que não dizem o que observar (references/spec.md, Gravação).
// Aceita a palavra com ou sem acento. Texto entre crases ou aspas fica de fora, porque é
// como a spec cita código ou a mensagem exibida ao usuário.
// ponytail: lista fixa e curta; vago escrito de outro jeito ("de modo ágil") passa, e só a
// conferência do líder e o analyze o pegam.
const RE_VAGO = /(?<!\p{L})(r[aá]pid[oa]s?|rapidamente|bonit[oa]s?|modern[oa]s?|intuitiv[oa]s?|amig[aá]ve(?:l|is)|f[aá]c(?:il|eis)|facilmente|adequad[oa]s?|adequadamente|corretamente|eficientes?|eficientemente|robust[oa]s?|elegantes?|agrad[aá]ve(?:l|is))(?!\p{L})/giu;
const RE_CITACAO = /`[^`]*`|"[^"]*"|“[^”]*”|'[^']*'/g;

// Valor que pede origem (decisão 3 da phase-6): número com unidade de prazo, tamanho ou
// contagem, percentual ou quantia em dinheiro, como `48 horas`, `30s`, `64 KiB`, `95%`,
// `R$ 19,90` e `8 a 128 caracteres` (aqui vale `128 caracteres`). O número não pode vir
// colado a letra, dígito ou `_`, nem a `letra-`, o que deixa de fora IDs (`A1`, `R2`,
// `AUTH-01`) e versões (`v5.4`). Número sem unidade da lista (`decisão 3`, `5 e 6`) não é
// valor, e a unidade tem de terminar na palavra (`10 horas`, não `10 hoje`). Texto entre
// crases ou aspas conta, porque é como a spec cita o valor do limite ou da mensagem.
// ponytail: lista fixa de unidades; valor com unidade fora dela (por exemplo, "3 mesas")
// passa, e só a conferência do líder e o analyze o pegam; acrescentar a unidade quando um
// valor real escapar. Horário do dia ("10h") conta como valor: a spec marca `(origem: humano)`.
const NUMERO = String.raw`\d+(?:[.,]\d+)*`;
const UNIDADES = [
  'milissegundos?', 'ms', 'segundos?', 'seg', 's', 'minutos?', 'min', 'horas?', 'h', 'dias?', 'semanas?', 'm[eê]s(?:es)?', 'anos?', // prazo
  'bytes?', '[kmgt]i?b', // tamanho
  '%', 'caracteres?', 'tentativas?', 'requisi[cç][oõ]es', 'itens?', 'registros?', 'vez(?:es)?', 'usu[aá]rios?', 'resultados?', 'p[aá]ginas?', 'reais', // contagem e limite
].join('|');
const RE_VALOR = new RegExp(
  String.raw`(?<![\p{L}\p{N}_])(?<!\p{L}-)(?:(?:R\$|US\$|€)\s?${NUMERO}|${NUMERO}\s?(?:${UNIDADES})(?![\p{L}\p{N}]))`,
  'giu',
);
// Origem: só o marcador explícito na mesma linha da decisão ou do critério, `(origem: humano)`,
// `(origem: assumida)` ou `(origem: verificado <fonte>)`, a forma canônica de references/spec.md
// (`(origem: verificado docs do gateway)`); a fonte entre parênteses internos, `(origem: verificado
// (docs do gateway))`, também é aceita. A fonte não pode ser vazia nem começar por `<` (o `<fonte>`
// copiado do modelo). Palavra solta na linha, como "pedido do humano" no Motivo, não vale: zeraria
// o achado de qualquer valor da linha.
// ponytail: a marca vale para a linha inteira; linha com dois valores e uma marca passa mesmo
// quando só um deles tem origem, e fonte com parênteses aninhados não é reconhecida. Separar
// os valores em linhas próprias quando um valor sem origem escapar assim.
const RE_ORIGEM = /\(origem:\s*(?:humano|assumida|verificado(?:\s*\(\s*[^()<\s][^()]*\)|\s+[^()<\s][^()]*))\s*\)/iu;

/** Valores de uma linha de decisão ou critério, sem repetidos; vazio quando a linha marca a origem. */
function valoresSemOrigem(texto) {
  if (RE_ORIGEM.test(texto)) return [];
  return [...new Set([...texto.normalize('NFC').matchAll(RE_VALOR)].map((v) => v[0]))];
}

const DICA_ORIGEM = 'marque na linha (origem: humano), (origem: assumida) ou (origem: verificado <fonte>)';

/**
 * Achados de forma da spec: seções, decisões sem pergunta ou motivo, critérios, valores sem
 * origem e placeholders. O valor sem origem só vale para spec em `# Status: rascunho`: spec
 * aprovada não é revalidada (decisão 3). Linha de tabela de exemplos nunca é decisão nem
 * critério, então o valor dela não gera achado.
 */
function formaDaSpec(linhasSpec) {
  const achados = [];
  const rascunho = cabecalho(linhasSpec, 'Status') === 'rascunho';
  for (const s of SECOES_SPEC) if (!secao(linhasSpec, s)) achados.push(`spec sem a seção ## ${s}`);

  for (const l of semComentarios(secao(linhasSpec, 'Decisões') || [])) {
    const m = l.match(/^(\d+)\. /);
    if (!m) continue;
    if (!/Pergunta:/.test(l)) achados.push(`decisão ${m[1]}: sem Pergunta:`);
    if (!/Motivo:/.test(l)) achados.push(`decisão ${m[1]}: sem Motivo:`);
    const valores = rascunho ? valoresSemOrigem(l.slice(m[0].length)) : [];
    if (valores.length) achados.push(`decisão ${m[1]}: valor sem origem (${valores.join(', ')}); ${DICA_ORIGEM}`);
  }

  const { ids, repetidos } = criteriosDaSpec(linhasSpec);
  if (!ids.length) achados.push('spec sem critério A<n> em ## Critérios de aceite');
  for (const a of repetidos) achados.push(`spec com o critério ${a} repetido`);
  for (const l of semComentarios(secao(linhasSpec, 'Critérios de aceite') || [])) {
    const m = l.match(/^- (A[1-9][0-9]*):(.*)$/);
    if (!m) continue;
    const vagos = [...m[2].normalize('NFC').replace(RE_CITACAO, '').matchAll(RE_VAGO)].map((v) => v[1].toLowerCase());
    if (vagos.length) achados.push(`critério ${m[1]}: adjetivo vago (${[...new Set(vagos)].join(', ')}); diga o resultado observável`);
    const valores = rascunho ? valoresSemOrigem(m[2]) : [];
    if (valores.length) achados.push(`critério ${m[1]}: valor sem origem (${valores.join(', ')}); ${DICA_ORIGEM}`);
  }

  achados.push(...placeholdersEsquecidos(linhasSpec, 'spec.md', 'spec.md'));
  return { criterios: ids, achados };
}

// ---------------------------------------------------------------------------
// Relatório
// ---------------------------------------------------------------------------

/** Alvo nomeado ou padrão, já recusando o formato antigo. */
function resolverAlvo(raiz, nomeAlvo) {
  const alvos = carregarAlvos(raiz);
  const alvo = nomeAlvo ? alvoNomeado(alvos, nomeAlvo) : alvoPadrao(alvos);
  if (!alvo) return { erro: nomeAlvo ? `alvo não encontrado: ${nomeAlvo}` : 'sem alvo aberto; informe --alvo' };
  if (alvo.antigo) return { erro: `${alvo.alvo} está no formato antigo (references/disco.md, Compatibilidade); só o contrato atual é conferido` };
  return { alvo };
}

/** Confere só a spec do alvo, antes da aprovação; exportado para os testes. */
export function conferirSpec(raiz, nomeAlvo = null) {
  const { alvo, erro } = resolverAlvo(raiz, nomeAlvo);
  if (erro) return { erro };
  if (!alvo.art.spec) return { erro: `${alvo.alvo} sem spec.md` };
  return { alvo: alvo.alvo, ...formaDaSpec(alvo.art.spec) };
}

/** Confere o plan do alvo; exportado para os testes. */
export function conferirPlan(raiz, nomeAlvo = null) {
  const { alvo, erro } = resolverAlvo(raiz, nomeAlvo);
  if (erro) return { erro };
  if (!alvo.art.plan) return { erro: `${alvo.alvo} sem plan.md` };
  if (!alvo.art.spec) return { erro: `${alvo.alvo} sem spec.md` };

  const { ids: criterios, repetidos } = criteriosDaSpec(alvo.art.spec);
  const plan = lerPlan(secao(alvo.art.plan, 'Passos') || []);
  const achados = [];

  if (!criterios.length) achados.push('spec sem critério A<n> em ## Critérios de aceite');
  for (const a of repetidos) achados.push(`spec com o critério ${a} repetido`);
  if (!secao(alvo.art.plan, 'Passos')) achados.push('plan sem a seção ## Passos');
  else if (!plan.passos.length) achados.push('## Passos sem nenhum passo');
  achados.push(...linhasEstranhas(alvo.art.plan));
  achados.push(...achadosDoPlan(plan.passos));
  for (const p of plan.passos) achados.push(...formaDoPasso(p, criterios));
  const cps = formaDosCheckpoints(plan.itens, criterios);
  achados.push(...cps.achados);

  const cobertos = new Set(plan.passos.flatMap((p) => (p.aceite ? p.aceite.ids : [])));
  for (const a of criterios) if (!cobertos.has(a)) achados.push(`critério ${a} da spec sem passo`);

  const regressao = secao(alvo.art.plan, 'Regressão completa');
  if (!regressao) achados.push('plan sem a seção ## Regressão completa');
  else if (!semComentarios(regressao).some((l) => l.trim())) achados.push('## Regressão completa sem comando');

  const titulos = alvo.art.plan.filter((l) => /^## /.test(l)).map((l) => l.trim());
  const iAchados = titulos.indexOf('## Achados do analyze');
  if (iAchados >= 0 && iAchados !== titulos.length - 1) achados.push('## Achados do analyze não é a última seção do plan');

  achados.push(...placeholdersEsquecidos(alvo.art.spec, 'spec.md', 'spec.md'));
  achados.push(...placeholdersEsquecidos(alvo.art.plan, 'plan.md', 'plan.md'));

  return { alvo: alvo.alvo, criterios, passos: plan.passos.length, checkpoints: plan.itens.length - plan.passos.length, achados, avisos: cps.avisos };
}

// ---------------------------------------------------------------------------
// Execução
// ---------------------------------------------------------------------------

function lerArgs(argv) {
  const args = { raiz: process.cwd(), alvo: null, json: false, spec: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--json') args.json = true;
    else if (a === '--spec') args.spec = true;
    else if ((a === '--raiz' || a === '--alvo') && argv[i + 1]) args[a.slice(2)] = argv[++i];
    else return { erro: `argumento desconhecido ou sem valor: ${a}` };
  }
  return args;
}

function texto(r) {
  const contagem = r.passos === undefined ? '' : ` · passos: ${r.passos} · checkpoints: ${r.checkpoints}`;
  const l = [`alvo: ${r.alvo} · critérios: ${r.criterios.join(', ') || 'nenhum'}${contagem}`];
  for (const a of r.achados) l.push(`achado: ${a}`);
  for (const a of r.avisos || []) l.push(`aviso: ${a}`);
  if (!r.achados.length) l.push('sem achado');
  return `${l.join('\n')}\n`;
}

function principal() {
  const args = lerArgs(process.argv.slice(2));
  if (args.erro) { console.error(args.erro); return 2; }
  const r = (args.spec ? conferirSpec : conferirPlan)(resolve(args.raiz), args.alvo);
  if (r.erro) { console.error(r.erro); return 2; }
  process.stdout.write(args.json ? `${jsonAscii(r)}\n` : texto(r));
  return r.achados.length ? 1 : 0;
}

if (executadoDireto(import.meta.url)) {
  process.exitCode = principal();
}
