# Review: scripts de leitura estado e ondas
# Alvo: phase-1-scripts-de-leitura
# Status: aprovado
# Rota: medium

## Contexto

- Alvo: fase `.vibeflow/phases/phase-1-scripts-de-leitura/`, entrega medium no branch `v2`
- Cadeia: medium, sem interview, spec, plan ou analyze; julgada contra o brief do humano
- O que muda: a skill ganha dois scripts Node somente leitura (`skills/vibeflow/scripts/estado.mjs` e `ondas.mjs`, com `_disco.mjs` compartilhado) que aplicam a tabela de estados, o progresso e a montagem de ondas; testes `node:test` em `tests/scripts/`; prosa de `SKILL.md`, `implement.md`, `coverage.md`, `AGENTS.md` e `README.md` passa a citar os scripts; a tabela de estados de `disco.md` corrige a ordem das linhas de planejamento.
- Base medium: `5716567` (`task(medium): scripts de leitura estado e ondas em Node sem dependências`)

## Cobertura da solicitação

- Origem e limites: brief do humano e decisões aceitas, transmitidos pelo líder no pedido de review; sem interview nem spec. Origem suficiente para o recorte medium.

| Item da solicitação e fonte (A*/C* quando houver) | Implementação | Evidência | Situação |
|---|---|---|---|
| Scripts simples para facilitar o uso pelo agente (brief) | `skills/vibeflow/scripts/estado.mjs`, `ondas.mjs`, `_disco.mjs` | `node skills/vibeflow/scripts/estado.mjs` neste repo devolve `review da entrega medium`, código 0 | atendido |
| Minimizar erro de regra mecânica: estado da phase (brief) | `estado.mjs`, linhas globais e `etapaDoAlvo` | Sondas em repos temporários: alvo padrão `phase-10` sobre `phase-9`, push adiado, medium revisado e CRLF corretos; `Design: N/A` e arquivo não ASCII produzem etapa errada (R1, R2); corrigidos em `d95dec6`, testes R1 e R2 verdes | atendido |
| Minimizar erro: progresso % (brief; `SKILL.md`, seção 9) | `estado.mjs:223-244` | Testes 25%, 20%, 62% e ajuste `0/1` verdes; progresso herda o erro de design de R1; corrigido em `d95dec6` (teste R1, 25%) | atendido |
| Minimizar erro: montagem de ondas e sobreposição de `Arquivos:` (brief; `plan.md` 1.3; `implement.md` 1) | `ondas.mjs:62-116`, `_disco.mjs:158-202` | Normalização e sobreposição conferem com `plan.md` 1.3; a onda para na T* sem `Arquivos:` em vez de pulá-la (R3); corrigido em `d95dec6`, teste R3 `[T1, T3]` | atendido |
| Compatibilidade Windows e Linux (brief) | `execFileSync` com lista, `git status -z`, CRLF e BOM removidos, `node:path`, `executadoDireto` com realpath e caixa no win32, JSON ASCII | Sonda CRLF+BOM verde; nenhum teste cobre CRLF, BOM ou a CLI (R4); testes de CRLF+BOM e CLI acrescentados em `d95dec6`, verdes; execução real em Windows não feita (Notas) | atendido |
| Node.js, `.mjs`, sem dependências (decisão humana) | só `node:fs`, `node:path`, `node:url`, `node:child_process` | leitura dos imports | atendido |
| Somente leitura, sem artefato, commit, push ou staging (decisão humana) | git só com `log`, `status`, `rev-parse`, `rev-list`; nenhuma escrita em disco | `grep` por escrita e subcomandos Git de escrita nos scripts: nada | atendido |
| Saída em texto e `--json` (decisão humana) | `texto()` e `jsonAscii()` | `estado.mjs --json` neste repo escapa não-ASCII | atendido |
| Começar por `estado` e `ondas` (decisão humana) | dois scripts | diff | atendido |
| Testes de comportamento com `node:test` fora do pacote (decisão humana) | `tests/scripts/disco.test.mjs` | `node --test`: 16/16 verdes; 26/26 verdes após `d95dec6` com os cenários de R4 | atendido |
| Prosa continua contrato; script nunca pré-requisito (decisão humana) | `SKILL.md` seção 1, `AGENTS.md` seção 4 | leitura do diff | atendido |
| Ordem das linhas de planejamento na tabela de `disco.md` (alteração autorizada) | `skills/vibeflow/references/disco.md:75-77` | leitura do diff; `etapaDoAlvo` segue a mesma ordem | atendido |

## Checklist de correções

### Required

- [x] R1: **Required** - `skills/vibeflow/scripts/estado.mjs` - `designConta` (linhas 35-39) ignora o registro `Design: N/A` de `references/disco.md` (Estado da phase): um Handoff de spec que começa com `Design: N/A, sem UI nova` casa `/^design\b/i` e devolve etapa `design, sem artefato`; `Design: N/A` registrado no `plan.md` também não é lido; o progresso herda o mesmo erro - remédio: design conta só com `design.md` presente ou Handoff que aponta design, e deixa de contar quando o Handoff da spec ou o `plan.md` registra `Design: N/A`; acrescentar os dois cenários aos testes - prova: `node --test`, com os cenários Handoff `Design: N/A` e plan com `Design: N/A` devolvendo etapa `plan`/`implement` - source: diff - gap: contradicts - papel: corretor
- [x] R2: **Required** - `skills/vibeflow/scripts/estado.mjs` - `semDono` (linhas 160-163) e `etapaDoAlvo` (linha 182) normalizam os paths alterados do `git status` com `normalizarPath`, cuja regra de path incomparável (`_disco.mjs:161`) vale só para paths declarados em `Arquivos:`; arquivo alterado não ASCII dentro do recorte de T* aberta (`docs/relatório.md` com `Arquivos: docs/`) vira `alteração sem dono` e passa à frente de `implement, retomar a onda` - remédio: normalizar paths do Git sem a regra de incomparabilidade (separar por `/`, comparar A-Z sem caixa), mantendo-a só para `Arquivos:`; teste com arquivo acentuado dentro do recorte - prova: `node --test`, cenário devolve `retomar a onda` - source: diff - gap: contradicts - papel: corretor
- [x] R3: **Required** - `skills/vibeflow/scripts/ondas.mjs` - linhas 78-81 encerram a montagem (`break`) ao encontrar T* sem `Arquivos:` comparáveis com a onda já iniciada; `references/implement.md`, seção 1, passo 2, só a impede de entrar e segue incluindo as demais elegíveis disjuntas. Plan `T1 a/`, `T2` sem `Arquivos:`, `T3 b/` devolve `[T1]`; a prosa dá `[T1, T3]` - remédio: pular a T* (`continue`) quando a onda não está vazia e encerrar só quando ela entra; ajustar o nome do teste de `tests/scripts/disco.test.mjs:73` e acrescentar esse cenário - prova: `node --test`, onda `[T1, T3]` - source: diff - gap: contradicts - papel: corretor
- [x] R4: **Required** - `tests/scripts/disco.test.mjs` - faltam cenários das superfícies alteradas e da compatibilidade declarada: artefato com CRLF e BOM, `alteração sem dono`, push adiado com e sem commit posterior, `request-changes` com R* `[x]` sem commit (commitar a correção) e com commit (re-review), `rascunho` com Approve (confirmar), e a CLI (códigos 0, 1 e 2 e `--json` só ASCII) chamada por `execFileSync(process.execPath, [...])` - remédio: acrescentar esses cenários com asserção sobre etapa, situação e código de saída - prova: `node --test` verde com os novos cenários - source: solicitação - gap: partial - papel: corretor

### Nit

- [x] R5: **Nit** - `skills/vibeflow/scripts/_disco.mjs` - `linksNoCaminho` (linhas 111-114) confere `.vibeflow/`, `phases/`, `mvp/` e a pasta, mas não o artefato, que `references/disco.md` (Escrever artefato) também proíbe como link; sonda com `spec.md` symlink não relata nada - remédio: incluir os artefatos presentes do alvo na conferência - prova: `node --test` com artefato symlink relatado (cenário pulado onde symlink não é permitido) - papel: corretor
- [x] R6: **Nit** - `README.md` - a árvore de "Estrutura do repositório" (linhas 96-101) ainda descreve o pacote como `SKILL.md, references/, templates/` e omite `tests/`, contrariando a seção "Scripts de leitura" e "Como contribuir" do mesmo arquivo - remédio: incluir `scripts/` na descrição do pacote e a linha `tests/` - prova: revisão de consistência do `README.md` - papel: redator

## Segurança

- Nada no que o diff tocou: scripts locais somente leitura, git com argumentos em lista e sem shell, sem rede, sem segredo; `--plan` lê caminho local escolhido por quem executa.

## Notas

- `tests/scripts/disco.test.mjs` usa `t.after`, disponível a partir do Node 18.13; "Node 18+" vale na prática para 18.13 ou superior.
- `etapaDoAlvo` não detecta código não commitado de T* aberta sem `Arquivos:` como `retomar a onda`; `semDono` também não o acusa, e a etapa cai em `implementar a próxima onda`. A prosa cita só "nos `Arquivos:` de T* abertas"; leitura literal aceita.
- Testes rodaram só em Linux (Node v24.22.0); compatibilidade Windows certificada por leitura de código e por cenários CRLF, BOM e CLI, sem execução em Windows.

## Veredito vigente

- [x] **Approve**: origem suficiente, obrigações atendidas ou retiradas explicitamente pelo humano e nenhum R* de correção em `[ ]`
- [ ] **Request changes**: há R* de correção em `[ ]`

## Handoff

implement

- [x] Aprovação humana (leu o arquivo e confirmou)

- Chat: no Modo A, esta review roda em revisor de contexto limpo, a pedido do líder; sem subagentes, roda num chat novo com `/vibeflow review`. As correções seguem pela etapa implement, com corretor ou redator conforme o `papel` de cada R*; sem subagentes, num chat novo com `/vibeflow implement`. Após Approve e confirmação humana, o handoff é a finalização Git da phase. O `review.md` vivo e o diff são a ponte.

## Finalização Git da phase

- Pré-condições: Approve final confirmado, o commit `task(medium): ...`, todos os R* de correção fechados, prova necessária da integração verde, `git diff --check` e gitleaks.
- Commit final: `chore(phase-1): finalize review`, somente com paths residuais autorizados; sem mudanças residuais, manter o último commit integrado ou da task.
- Push: `git push` para o upstream atual, sem `--force`. Registrar hash/HEAD, paths e resultado; falha mantém o handoff bloqueado.

## Etapas

### Etapa 1 - first-pass - diff `5716567^..HEAD` e regressão completa

- Provas reaproveitadas: nenhuma
- Provas executadas: regressão completa do `AGENTS.md` em HEAD `571656751d92639c2d286dd77c6dc6ab80460977`, árvore limpa, Node v24.22.0: `node --test` na raiz, 16 testes, 16 verdes; `git diff --check 5716567^..HEAD`, sem achado; `gitleaks detect --source . --redact --no-banner`, 90 commits, no leaks found, código 0; revisão de consistência: `skills/vibeflow/scripts/` e `tests/scripts/` existem, nenhum arquivo alterado cita a v1 do VibeFlow, árvore do `README.md` desatualizada (R6). Sondas de comportamento em repos temporários no scratchpad, fora do repo, para R1, R2, R3 e R5.
- Execução: diff dentro do recorte do brief (`AGENTS.md`, `README.md`, `SKILL.md`, `references/disco.md`, `references/implement.md`, `references/analyze/coverage.md`, `skills/vibeflow/scripts/`, `tests/scripts/`); commit `task(medium): ...` único na base; sem T*.
- Leu: brief e decisões humanas do pedido do líder; `SKILL.md`; `references/review.md`, `delegation.md`, `disco.md`, `plan.md`, `implement.md`; `templates/review.md`, `plan.md`, `spec.md`, `analyze.md`; `AGENTS.md`; os três scripts e o teste.
- Cobertura: matriz criada; quatro itens parciais, ligados a R1 a R4
- Abriu: R1, R2, R3, R4, R5, R6
- Fechou: nenhum
- Veredito desta etapa: Request changes

### Etapa 2 - re-review - commit `d95dec6` (R1 a R6) e regressão completa

- Provas reaproveitadas: nenhuma; código e testes mudaram desde a Etapa 1.
- Provas executadas: regressão completa do `AGENTS.md` em HEAD `d95dec6dde1048f621d6435f4989f4eab44e3240`, árvore limpa, Node v24.22.0: `node --test` na raiz, 26 testes, 26 verdes, 0 pulados; `git diff --check 5716567^..HEAD`, sem achado; `gitleaks detect --source . --redact --no-banner`, código 0, no leaks found; revisão de consistência: árvore do `README.md` cita `scripts/` e `tests/scripts/`, ambos existentes, sem citação da v1. Sondas da Etapa 1 repetidas no scratchpad: Handoff e plan com `Design: N/A` seguem para plan e implement, arquivo acentuado no recorte dá `retomar a onda`, onda `[T1, T3]`, artefato symlink relatado; CRLF, alvo padrão, medium revisado e push adiado seguem corretos.
- Execução: commit `task(phase-1:R1,R2,R3,R4,R5,R6): ...` existe e seus IDs são exatamente os R* marcados `[x]` desde a Etapa 1. Paths do commit: `review.md` desta phase, `README.md` (R6), `_disco.mjs` (R2, R5), `estado.mjs` (R1, R2), `ondas.mjs` (R3) e `tests/scripts/disco.test.mjs` (R4), todos no recorte do brief ou no remédio dos R*. O alinhamento extra de `pushPendente` a "nenhuma phase aberta" (`estado.mjs:296`) fecha a Nota da Etapa 1 e segue `references/disco.md`. Os testes de regressão R1, R2, R3 e R5 têm asserção real sobre etapa, situação, onda e inconsistência; o R5 pula só onde symlink não é permitido.
- Leu: diff `5716567..d95dec6`, testes novos, `templates/plan.md` (linha `- **Design:**` compatível com a leitura de `Design: N/A`).
- Cobertura: os cinco itens parciais passam a atendido; nenhuma obrigação aberta.
- Abriu: nenhum
- Fechou: R1, R2, R3, R4, R5, R6 (corrigidos e certificados; a marcação `[x]` já estava gravada)
- Veredito desta etapa: Approve final, sujeito à confirmação humana; o `# Status:` correspondente é `rascunho` até a finalização.
