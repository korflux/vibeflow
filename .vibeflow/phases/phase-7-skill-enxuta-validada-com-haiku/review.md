# Review: Skill enxuta validada com Haiku
# Alvo: phase-7-skill-enxuta-validada-com-haiku
# Status: request-changes

## Veredito

- [ ] **Approve**: critérios atendidos e provados, regressão verde e nenhum Critical ou Required aberto
- [x] **Request changes**: há Critical ou Required aberto

## Critérios de aceite

| Critério | Evidência (teste e resultado) | Situação |
|---|---|---|
| A1 | `medir.mjs` reproduzido nesta review: base `base-5.4.0/` (igual a `f3fce47` por `diff -r --strip-trailing-cr`) com `papeis-5.4.0.json`, 5.5.0 sobre `skills/vibeflow` com `papeis-5.5.0.json`; valores idênticos aos de `comparacao.md` (tabela em Medição, abaixo); todos os papéis e a soma do líder ao menos 30% abaixo da base. Listas conferidas contra perfis e referências: cada papel conta toda leitura incondicional, e leitura condicional fica fora nas duas versões; a sensibilidade está em Notas | atendido |
| A2 | Busca por cópias das redundâncias de Pontos do projeto (commits e staging, checkpoint, origem dos valores, Docker, encadeamento, checklist do analyze, Ajuste de phase, identidade dos perfis, bloco CADEIA): cada regra tem casa única no pacote (`disco.md` Commits e Plan > Checkpoint, `spec.md` Origem dos valores, `init.md` Ambiente local, topo do `SKILL.md`, `analyze/coverage.md`, `ajuste.md`); o que sobra são ponteiros, o resumo operativo do Docker em `implementador.md:20` e o comentário de `templates/spec.md:19` (Notas) | atendido |
| A3 | Leitura dos 10 perfis de `templates/agents/`: os quatro papéis mandam ler somente `references/<papel>.md`, nenhum manda ler o `SKILL.md`, e o corpo claude e codex de cada papel é o mesmo | atendido |
| A4 | `medir.mjs`: bloco CADEIA com 341 tokens no template e neste repo, idênticos; contém a tabela de esforço, os sinais que tiram do low e o ponteiro para a skill | atendido |
| A5 | `medir.mjs`: `AGENTS.md` com 2.110 tokens (teto 2.200). Repetição remanescente em `AGENTS.md:57` (R1) | parcial |
| A6 | `comparacao.md`, `placar-5.4.0.md` e `resultado-5.5.0.md`; respostas brutas de S2 e S7 conferidas contra o gabarito; cópia `final-5.5.0/` igual ao `HEAD` por `diff -r --strip-trailing-cr`. Os oito cenários passam nas duas versões (tabela em Cenários, abaixo) | atendido |
| A7 | `node --test`: 114 de 114; `estado.mjs --json`: phases 1 a 7 lidas, `inconsistencias: []`; scripts mudaram só em comentário | atendido |
| A8 | Consumidor temporário com o `templates/AGENTS.md` de `f3fce47`: `governanca.mjs` acusa `bloco VIBEFLOW:CADEIA diferente de templates/AGENTS.md` (código 1); com o bloco da 5.5.0, `AGENTS.md: ok`. `init.md` passo 2 substitui o bloco, e o passo 1 e a seção Backup de arquivo de regra exigem o backup antes | atendido |
| A9 | Comparação com `f3fce47` das regras de gate (`SKILL.md` seção 3, `review.md` Entrada e Finalizar), commit (`disco.md` Commits, `implement.md` passos 1 e 4 e Rota medium), encadeamento (topo do `SKILL.md`), checkpoint (`disco.md` Plan > Checkpoint, `implement.md` passo 2, `verificador.md`) e Modo B (`retomada.md`): mesmo efeito, inclusive push só na finalização e `git diff --cached --check` antes do commit. Contrato de disco (paths, nomes, cabeçalhos) sem mudança. Ambiguidade textual de Modo B em `review/passos.md` (R2), sem efeito em duas rodadas Haiku | atendido |
| A10 | `AGENTS.md` Versão: 5.5.0; `README.md` Novidades da 5.5.0 manda rodar `/vibeflow init` para o bloco e os perfis novos | atendido |

## Achados

### Required

- [x] R1: **Required** - `AGENTS.md` - A5 pede que o `AGENTS.md` não repita regra com casa no pacote, e a linha 57 repete, depois do ponteiro para `disco.md` (Commits), que aprovar a review e publicar decisões vigentes exigem confirmação humana explícita; essa regra só existe dentro da cadeia e tem casa no topo do `SKILL.md` (pausa Confirmação final) e em `references/review.md` (Confirmar), não em `disco.md` (Commits) - remédio: tirar da linha a parte que só vale na cadeia, deixando o ponteiro; se o push sem confirmação precisa valer fora da cadeia, manter só essa regra - prova: releitura da seção Git do `AGENTS.md` contra `SKILL.md` e `review.md`, `medir.mjs` com o `AGENTS.md` até 2.200 tokens e `git diff --check` - papel: redator
- [x] R3: **Required** - `skills/vibeflow/references/init.md` - A seção Ambiente local está em `references/init.md` (2.249 tokens), e `references/implementador.md`, `references/plan.md` (passo 2) e o topo do `SKILL.md` (pausa Docker nos testes) apontam para ela; o implementador num passo com banco passa a ler 4.137 tokens contra 2.705 na base, e o líder numa phase high com Docker cai só 20,3% - remédio: mover a seção, com o mesmo conteúdo, para `references/ambiente.md` e trocar os ponteiros em `init.md`, `plan.md`, `implementador.md`, `SKILL.md`, `testes.md` e, onde houver, `README.md` e `AGENTS.md`, sem mudar nenhuma regra - prova: `medir.mjs` com o implementador mais `references/ambiente.md` abaixo dos 2.705 tokens da base, todo ponteiro para Ambiente local resolvendo e `git diff --check` - source: pedido humano - papel: redator

### Nit

- [x] R2: **Nit** - `skills/vibeflow/references/review/passos.md` - A linha 3 diz "O líder não lê este arquivo", mas no Modo B o chat aberto com `/vibeflow review` é o líder e atua como revisor (`references/retomada.md`, Contexto limpo), e a tabela de `retomada.md` não aponta `references/revisor.md` nem `references/verificador.md` como faz com `references/implementador.md` no implement; um modelo literal pode pular o procedimento da review. Duas rodadas Haiku nesta review leram `passos.md` e `revisor.md` mesmo assim - remédio: dizer em `passos.md` que o líder só o lê no Modo B, ao atuar como revisor, e apontar em `retomada.md` (Contexto limpo) a referência do papel assumido - prova: releitura de `retomada.md` e `review/passos.md`, ponteiros resolvidos e `git diff --check` - papel: redator

## Notas

- Regressão: `governanca.mjs --raiz .` sai com código 1 só pelos dez achados `perfil global <host>/<papel> diferente`, aceitos pela spec e pelo item 4 da Regressão completa; só o init com decisão humana os atualiza.
- Sensibilidade de A1 a leituras condicionais. O método conta toda leitura incondicional do papel e deixa fora a condicional, como a base já fazia (`chrome-devtools.md`, `database-and-migrations.md`, `ui-visual-direction.md`). Parte da queda vem de mover para arquivos de leitura condicional trechos que a base carregava sempre em `testes.md` e no `SKILL.md`; contando o arquivo inteiro da leitura condicional, ficam abaixo de 30%:

  | Caso | 5.5.0 | Base | Queda |
  |---|---|---|---|
  | Implementador em passo com E2E (+ `verificador.md`) | 2.545 | 2.705 | 5,9% |
  | Implementador em passo com banco ou serviço (+ `init.md`, Ambiente local) | 4.137 | 2.705 | -52,9% |
  | Líder numa phase high com tela (+ `verificador.md`, Desenho do E2E, citado em `plan.md` passo 2) | 15.139 | 20.998 | 27,9% |
  | Líder numa phase high com retomada ou interrupção (+ `retomada.md`) | 15.072 | 20.998 | 28,2% |
  | Líder numa phase high com Docker no plan (+ `init.md`) | 16.731 | 20.998 | 20,3% |

  O implementador tem margem de 5 tokens sobre o teto e a soma do líder, de 216; `implementador.md:20` já traz em linha a regra operativa do ambiente local, e abrir `init.md` (2.249 tokens) por uma seção de cinco linhas custa mais que a base.
- `AGENTS.md:56` repete a proibição de staging de `references/delegation.md` (Ownership e proibições) e a ausência de `Co-Authored-By` de `references/disco.md` (Commits), mas vale também para o trabalho neste repo fora da cadeia, quando a skill não é carregada; por isso não entrou em R1.
- `skills/vibeflow/templates/spec.md:19` resume os três marcadores de origem e aponta para `references/spec.md` (Origem dos valores); é orientação do template no ponto de escrita e ficou fora dos `Arquivos:` da phase.
- Cenário S7: nas duas versões, a resposta lista hipóteses do analyze antes de mandar abrir o chat novo, sem gravar nem corrigir o `plan.md`; comportamento igual ao da base, sem regressão.
- Paths fora dos `Arquivos:`: o commit `01347d2` (passo 5) apaga os dois registros de `.erros-encontrados/` criados pelo verificador no `3c385aa`, como manda a regra de registro corrigido. Commits coerentes com os passos; `3c385aa` leva a correção do checkpoint no formato de passo.
- Ponteiros: todo path de `references/`, `templates/` e `scripts/` citado no pacote, nos scripts, nos testes, no `README.md` e no `AGENTS.md` existe, e os ponteiros por seção resolvem; os avisos do conferidor do scratchpad são falsos positivos (títulos com " e " e comentários de `_disco.mjs` sem mudança na phase). Nenhum arquivo cita a v1, registro estruturado de execução ou o contrato anterior à 5.0.0 como vigente.

## Medição

chars/4, CRLF normalizado para LF, mesma regra de lista por papel; reproduzida nesta review com `medir.mjs`.

| Papel ou arquivo | Base 5.4.0 | 5.5.0 | Queda | Teto de 70% da base |
|---|---|---|---|---|
| líder sempre | 3.249 | 2.220 | 31,7% | 2.274 |
| explorador | 5.973 | 671 | 88,8% | 4.181 |
| implementador | 2.705 | 1.888 | 30,2% | 1.893 |
| verificador | 9.528 | 1.729 | 81,9% | 6.669 |
| redator de spec | 11.599 | 6.204 | 46,5% | 8.119 |
| redator de plan | 12.929 | 6.627 | 48,7% | 9.050 |
| revisor de analyze | 12.877 | 6.300 | 51,1% | 9.013 |
| revisor de review | 14.969 | 8.619 | 42,4% | 10.478 |
| soma do líder numa phase high completa | 20.998 | 14.482 | 31,0% | 14.698 |
| bloco CADEIA (template e repo) | 861 | 341 | 60,4% | 400 pela A4 |
| `AGENTS.md` deste repo | 5.270 | 2.110 | 60,0% | 2.200 pela A5 |

## Cenários

Haiku como líder, mesmo prompt com o path trocado; base `base-5.4.0/`, 5.5.0 `final-5.5.0/`.

| Cenário | Base 5.4.0 | 5.5.0 | Rodadas |
|---|---|---|---|
| S1 pedido ambíguo que altera banco | passa | passa | 1 e 1 |
| S2 analyze sem `plan.md` | passa | passa | 1 e 1 |
| S3 n e slug da phase nova | passa | passa | 1 e 1 |
| S4 grupo 2a e 2b | passa | passa | 1 e 1 |
| S5 commit do grupo | passa | passa | 1 e 1 |
| S6 caixa marcada sem commit | passa | passa | 1 e 1 |
| S7 analyze sem subagentes (v2) | passa 3 de 3 | passa 3 de 3 | 3 e 3 |
| S8 troca de cor de botão (v2) | passa 3 de 3 | passa | 3 e 1 |

A v1 de S7 falhou na base por ambiguidade da skill e foi corrigida em `references/retomada.md` (Contexto limpo); a v1 de S8 falhou por defeito do cenário. Nenhum cenário divergiu entre as versões. Nesta review, duas rodadas Haiku de Modo B com `/vibeflow review` na 5.5.0 leram `review/passos.md` e `revisor.md` e seguiram o procedimento (R2).

## Aprovação humana

- [ ] Aprovação humana (confirmou no chat o resumo do líder)

## Etapas

### Etapa 1 - review - f3fce47..HEAD

- Regressão: no `HEAD` `ccd2ecca6c9344bb0f9f238b1728b154457de1ec`, árvore limpa: `git diff --check f3fce47..HEAD` e `git diff --check` limpos; `node --test` 114 de 114; `estado.mjs --json` sem inconsistência; `governanca.mjs --raiz .` só com `perfil global <host>/<papel> diferente`; `gitleaks detect --source . --redact --no-banner` sem vazamento; revisão de consistência dos Comandos do projeto sem achado de path, de v1 nem de contrato anterior à 5.0.0, com R1 e R2 na conferência entre regras. Sem flake.
- Duração: `git diff --check` 0,27 s, `node --test` 41,49 s, `estado.mjs` e `governanca.mjs` 0,53 s, gitleaks 1,75 s, sem E2E; total 44,04 s · orçamento: 10 minutos (padrão, o `AGENTS.md` não declara)
- Abriu: R1, R2, R3 (R3 por pedido humano, a partir da nota de sensibilidade de A1)
- Veredito: Request changes
