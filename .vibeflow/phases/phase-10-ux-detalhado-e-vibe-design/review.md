# Review: UX detalhado e vibe-design
# Alvo: phase-10-ux-detalhado-e-vibe-design
# Status: aprovado

<!-- Escreva diretamente neste artefato vivo; o status permanece rascunho até o veredito e a confirmação humana. -->

## Contexto

- Alvo: phase-10-ux-detalhado-e-vibe-design
- Cadeia: interview.md / spec.md / plan.md / implement.md (sem analyze.md, rota sem analyze)
- O que muda: UX genérica detalhada nos templates de interview e spec, cadeia com design condicional a UI visível, skill nova vibe-design com três motores, template, references, docs e distribuição em 8 skills.

## Cobertura

| Chave | Código | Notas |
|---|---|---|
| A1 | ok | `vibe-spec/templates/spec.md`, molde F* com superfície por passo, mais `vibe-interview/templates/interview.md` com jornadas |
| A2 | ok | `vibe-interview/templates/interview.md`, tabela de 8 colunas e checklist de acesso com N/A explícito, `vibe-spec/templates/spec.md` com N/A |
| A3 | ok | `vibe-design/SKILL.md`, `vibe-design/templates/design.md`, `vibe-design/references/modos-entrada.md`, `vibe-design/references/kit-e-tokens.md`, `vibe-design/scripts/design.py`, `vibe-design/scripts/design.ps1`, `vibe-design/scripts/design.sh`, `docs/vibe-design/ARQUITETURA.md`, `docs/vibe-design/ANALISE.md` |
| A4 | ok | `.vibeflow/REGRAS.md`, linha 14 com design condicional, mais `vibe-plan/SKILL.md` e `vibe-analyze/SKILL.md` com conferência de design |
| C1 | ok | Suítes reexecutadas nesta review, 22 interview, 22 spec, 19 design, 12 distribuicao, 4 visual, 2 mvp, 12 reparse, sh design 6/0, gitleaks 18 commits sem leaks |
| C2 | ok | `plan.md` T6 referencia spec e design sem criar comportamento ou token novo, distribuição em 8 preservada |

## Checklist de correções

### Required

- [x] R2: **Required**. Express conflita com a entrada obrigatória de design. Evidência: `.vibeflow/REGRAS.md:16-18` permite low/medium sem design existente, mas `vibe-implement/SKILL.md:78` e `docs/vibe-implement/ARQUITETURA.md:55` exigem design aprovado para qualquer UI. `vibe-design/SKILL.md:47,86-95,126` mantém gate de plan existente e apply obrigatório; `vibe-review/SKILL.md:67-76` não distingue review leve. Impacto: um ajuste de cor pode exigir cadeia nova ou reabrir tasks antigas, contrariando Express. Remédio: vibe-implement explicita nos contratos operacionais o ramo Express, patch direto apenas no design existente, execução avulsa na mesma phase sem depender da fila antiga e review proporcional. Preservar o gate do motor para criação normal, sem rodar design apply no patch Express. Prova: percorrer ajuste de cor sem design, espaçamento com design e plan concluído, e comportamento novo que volta para spec.
- [x] R3: **Required**. Condição de omissão invertida. Evidência: `vibe-design/templates/design.md:59` manda omitir sem motion **ou** sem mobile, enquanto `docs/vibe-design/ARQUITETURA.md:64` exige a seção com motion **ou** mobile. Impacto: desktop animado perde física/a11y e mobile sem animação perde baseline. Remédio: vibe-implement troca por omitir somente quando não houver motion **nem** alvo mobile; campos não aplicáveis recebem N/A. Prova: conferir os quatro cenários motion/mobile, apenas nenhum dos dois omite a seção.
- [x] R4: **Required**. Durações incompatíveis no próprio catálogo. Evidência: `vibe-design/references/motion.md:38-40` permite modal/drawer de 200 a 500ms e depois exige UI abaixo de 300ms, com exceção apenas para marketing. Impacto: drawer de app a 400ms simultaneamente atende e viola o contrato. Remédio: vibe-implement define abaixo de 300ms como padrão para UI frequente e explicita exceção justificada para drawer/modal de maior deslocamento até 500ms, ou reduz a faixa se o limite for realmente absoluto. Prova: classificar tooltip a 150ms, modal a 250ms e drawer a 400ms sem respostas contraditórias.
- [x] R5: **Required**. Allowlist de propriedades contradiz regras de cor e blur. Evidência: `vibe-design/references/motion.md:24,46,49,53` prevê cor e blur, mas autoriza somente transform, opacity e clip-path; chama três propriedades de quatro. `vibe-design/templates/design.md:62` restringe novamente a transform e opacity. Impacto: a IA recebe instruções incompatíveis para hover e reduced motion. Remédio: vibe-implement usa transform/opacity como preferência de performance, trata cor explicitamente e condiciona clip-path/filter a necessidade e prova de desempenho; o template aponta para a referência sem duplicar uma allowlist divergente. Prova: conferir hover de cor, fade reduzido, clip-path e blur contra uma regra única.
- [x] R6: **Required**. Reduced motion proíbe desligar animação mesmo quando dispensável. Evidência: `vibe-design/references/motion.md:53` determina versão suave, “não zero”, em conflito também com o gate sem animação da linha 9. Impacto: obriga preservar efeitos decorativos e pode prolongar fades/staggers desnecessários para quem pediu redução. Remédio: vibe-implement permite remover motion não essencial e mantém feedback de estado imediato; fade/cor curtos são opcionais conforme necessidade, não obrigação. Prova: com prefers-reduced-motion ativo, celebração e deslocamento podem desaparecer, ação frequente continua instantânea e sucesso/erro permanecem perceptíveis.

### Optional / Nit

- [x] R1: **Nit** - `.vibeflow/phases/phase-10-ux-detalhado-e-vibe-design/plan.md` - Conferência com `# Status: aprovado` no cabeçalho mas item `Aprovação humana` em `[ ]` na linha 171, spec.md já tem `[x]` - remédio: vibe-implement marca `[x]` ou registra motivo em 1 linha - prova: leitura de `plan.md:4,171` e `spec.md:176` - source: plan.md - gap: nenhum

- [x] R7: **Optional**. `vibe-design/references/motion.md:65,72` aplica overscroll none na raiz e exige revisão no dia seguinte/hardware sem diferenciar app shell, site e patch simples. Remédio: vibe-implement condiciona overscroll ao comportamento desejado e revisão tardia/hardware aos riscos de gesto e mobile. Prova: página de conteúdo preserva scroll nativo; ajuste de texto desktop não ganha espera de um dia.
- [x] R8: **Optional**. `vibe-spec/SKILL.md:93` e `docs/vibe-spec/ARQUITETURA.md:58` proíbem qualquer token. Remédio: vibe-implement distingue definir token visual de referenciar contrato existente como limite de escopo, e deixa claro que a restrição não trata de tokens de autenticação/API. Prova: spec de migração de DS pode nomear token público a preservar sem definir valor ou paleta; uma spec de autenticação pode especificar expiração de token.
- [x] R9: **Nit**. `vibe-analyze/SKILL.md:80,107,129` ainda enumera somente spec/plan ao aplicar esclarecimentos, resumir correções e listar vivos alterados, embora agora design possa ser corrigido. Remédio: vibe-implement inclui design quando tocado, sem tornar analyze obrigatório fora de max. Prova: correção determinística em design aparece no registro e no handoff.

## Segurança

- Entrada externa no diff: apenas flags locais `--slug`, `--dir`, `--root`, `--mvp` dos motores `vibe-design/scripts/design.py` e `design.ps1`. Sanitização com `sanitize_slug` e `ConvertTo-Slug` (ASCII, 2 a 48 chars), `--dir` reduzido a `basename` via `Path(args.dir).name` e `GetFileName`, `LiteralPath` em todo acesso, guarda de reparse point antes de escrita, `subprocess` em array sem shell, sem SQL, sem auth, sem segredo, sem log sensível. Nada explorável no que o diff tocou.

## DoD

- [x] Suítes de contrato verdes reexecutadas nesta review
- [x] `git diff --check` limpo
- [x] `gitleaks detect --source . --verbose --redact --no-banner` sem leaks
- [x] Sem edição de source, teste ou lockfile nesta skill
- [x] `review-report.json` fora do git, `review.md` vivo entra no git

## Notas

- `interview.md` e `spec.md` da phase 10 estão untracked no working tree, resíduo esperado de skills de definição, entra no commit final da phase.
- `plan.md` T1 a T6 em `[x]` com prova por task, `implement.md` com 6 fatias e arquivos por fatia.
- Visual omitido, diff sem UI web. Banco omitido, repo sem persistência.

## Veredito vigente

- [x] **Approve**: nenhum Critical/Required em `[ ]`
- [ ] **Request changes**: há Critical/Required em `[ ]`
- [ ] **Approve com defer**: nenhum

## Handoff

Finalização Git da phase após confirmação humana. Sem commit ou push nesta execução, conforme o contrato da skill.

- [x] Aprovação humana (leu o arquivo e confirmou)

- Chat: o `review.md` vivo e o diff são a ponte para as correções. A orientação de finalização da etapa 1 fica suspensa pelo Request changes da etapa 2 e pela instrução humana de não commitar nem fazer push.

## Finalização Git da phase

- Pré-condições: Approve confirmado, todas as `T*` concluídas, Critical/Required fechados, suíte final verde, `git diff --check` e gitleaks quando previsto.
- Commit final: `chore(phase-N): finalize review`, somente com paths residuais autorizados e sem `Co-Authored-By`; sem mudanças residuais, manter o último commit da task.
- Push: `git push` para o upstream atual, sem `--force`. Registrar hash/HEAD, paths e resultado; falha mantém o handoff bloqueado.

## Etapas

### Etapa 1 - first-pass - T1 a T6, diff ce7d859..5303864 mais untracked, provas reexecutadas

- Leu: plan.md sim
- Abriu: R1 (Nit, sem bloqueio)
- Fechou: nenhum
- Veredito desta etapa: Approve

### Etapa 2 - 2026-09-20 - Express, fronteira spec, motion e consumo de design

- Escopo: revisão do working tree indicado pelo humano, incluindo os três arquivos não versionados. Leitura de regras, SKILL e arquiteturas de spec/design/implement/analyze, template e referência motion, review operacional, README e artefatos da phase 10. A cobertura acima e a prova de gitleaks pertencem à etapa 1; esta etapa não revalida todo o pacote já commitado.
- Seleção: o inventário sugeriu phase 9 por possuir plan sem review. O pedido e a review já existente identificam phase 10; atualização direta deste vivo, sem apply em outro alvo.
- Abriu: R2 a R6 Required, R7 e R8 Optional, R9 Nit. Fechou: nenhum. R1 já estava fechado e o checkbox do plan continua coerente.
- Veredito desta etapa: **Request changes**. As inconsistências são semânticas dos prompts e do template; testes verdes não as eliminam.

#### Parecer nos oito itens solicitados

1. **Contrato vivo:** o texto em REGRAS atende ajuste fino low/medium, patch no design existente e retorno à spec para comportamento, rota ou regra nova. Texto só permanece Express quando não muda significado funcional, regra ou aceite. O bloqueio é a falta desse ramo nos consumidores, R2. Review leve mantém rastreabilidade e prova visual, incluindo acessibilidade afetada; segurança/banco entram somente quando o diff os tocar.
2. **SPEC:** comportamento e aceite devem continuar separados de valores de CSS/paleta/tokens. Reuso do DS, contraste, estados de erro e redução de movimento podem ser travados como requisitos observáveis, sem inventar tokens. Exceção útil: nome de token público já existente quando a identidade dele for o contrato a preservar, por exemplo migração de DS ou API de tema. Referenciar a fonte e a restrição basta; valores e mapeamento por tela continuam no design. R8 registra o refinamento.
3. **DESIGN/motion:** frequência e propósito são bons critérios para uma cadeia usada em produtos diversos. Press de 100 a 160ms, tooltip de 125 a 200ms e dropdown de 150 a 250ms são defaults razoáveis; não há produto renderizado neste repo para validá-los perceptualmente. As curvas cúbicas informadas são válidas, fortes e úteis como presets, não substituem o DS existente. Ease-out em entrada e ease-in-out em deslocamento são defaults adequados; “nunca ease-in” é preferência excessivamente absoluta, sobretudo para saídas, e não uma impossibilidade técnica. Duração de drawer precisa da exceção explícita de R4. A seção permanece quando houver motion em desktop ou baseline mobile sem motion, R3. Física/a11y precisam de R5 e R6. “tap-highlight transparent” é abreviação de intenção; a implementação web correspondente usa `-webkit-tap-highlight-color`, sem retirar o feedback de toque.
4. **IMPLEMENT:** consumir tokens, motion e prova do design aprovado é correto na cadeia completa. No Express, seguir somente o recorte existente e alterado, sem reconstruir documento nem exigir arquivo ausente, R2.
5. **ANALYZE:** manter obrigatório em max e sob demanda nas demais rotas, inclusive high com UI. Essa já é a tabela vigente; cruzar design sempre que analyze for executado com UI não cria uma nova porta obrigatória. A arquitetura e o passo 3 sustentam o cruzamento e a correção determinística; completar as enumerações residuais de R9. Mudança de intenção visual ou comportamento exige esclarecimento, não “correção óbvia”.
6. **Crédito:** `README.md:221` está em ordem alfabética entre dietrichgebert e github. O link `https://github.com/emilkowalski/skills` foi aberto e corresponde ao repositório citado.
7. **Pendências Git:** incluir `interview.md` e `spec.md` da phase 10 no futuro commit de fechamento, pois são as fontes referenciadas por plan/review já versionados. Incluir `vibe-design/references/motion.md` junto dos consumidores após correções e aprovação. O `review.md` atualizado também entra no fechamento. Usar staging explícito por path; relatório operacional fica fora. O estado rascunho da interview e os A*/C* ainda desmarcados da spec devem ser reconciliados com as provas existentes na implementação, sem inventar aprovação humana. Nenhum staging foi executado nesta review.
8. **Validação:** cinco suítes reexecutadas com sucesso, inclusive os casos de paridade PowerShell. `git diff --check` limpo, com avisos de normalização LF/CRLF que não são falhas de whitespace. A suíte de design exercita motores, preservação e gates; não verifica coerência de duração, a condição lógica do template nem a execução semântica do Express. Prova visual, segurança e banco são N/A nesta etapa: o diff é documentação operacional e não altera UI executável, entrada externa ou persistência.

#### Provas reexecutadas

| Comando | Resultado |
|---|---|
| `python "docs/tests/test-distribuicao.py" -v` | 12 testes OK |
| `python "docs/vibe-spec/tests/test-spec.py" -v` | 22 testes OK |
| `python "docs/vibe-design/tests/test-design.py" -v` | 19 testes OK |
| `python "docs/vibe-implement/tests/test-implement.py" -v` | 34 testes OK |
| `python "docs/vibe-analyze/tests/test-analyze.py" -v` | 18 testes OK |
| `python -c "print(sum([12,22,19,34,18]))"` | 105 |
| `git diff --check` | exit 0 |

Alteração desta execução: somente este review vivo e regeneração do relatório operacional ignorado. Correções nos pacotes aguardam implementação autorizada. Sem commit e sem push.

### Etapa 3 - 2026-09-20 - re-review das correções R2 a R9

- Leu: `vibe-implement/SKILL.md:78`, `docs/vibe-implement/ARQUITETURA.md:55`, `vibe-review/SKILL.md:63`, `vibe-design/templates/design.md:59,62`, `vibe-design/references/motion.md`, `vibe-spec/SKILL.md:93`, `docs/vibe-spec/ARQUITETURA.md:58`, `vibe-analyze/SKILL.md:10,73,80,107,129`, relatório `.vibeflow/review-report.json` (modo atualizar, alvo phase 10 preservado).
- Abriu: nenhum.
- Fechou: R2, R3, R4, R5, R6 Required, R7 e R8 Optional, R9 Nit.
- Veredito desta etapa: **Approve** (proposta, aguarda confirmação humana).

#### Prova por achado

| Achado | Correção conferida | Resultado |
|---|---|---|
| R2 Express | Ramo Express explícito na implement com reuse da phase, recorte do design existente, sem apply de design, sem plan novo e sem reabrir tasks; review leve só com rastreabilidade mais visual | Fecha. Ajuste de cor sem design não exige cadeia nova; comportamento novo volta para spec |
| R3 Omissão | Template com omitir somente sem motion nem mobile, N/A nos campos não aplicáveis | Fecha. Desktop animado mantém motion; mobile estático mantém baseline |
| R4 Durações | Padrão abaixo de 300ms para UI frequente, exceção até 500ms para drawer ou modal com maior deslocamento e motivo | Fecha. Tooltip 150ms, modal 250ms e drawer 400ms classificam sem contradição |
| R5 Propriedades | Preferência por transform e opacity, cor permitida, clip-path e filter condicionados, template sem allowlist divergente | Fecha. Hover de cor, fade, clip-path e blur seguem regra única |
| R6 Reduced motion | Remoção de motion não essencial permitida, feedback imediato mantido, fade e cor opcionais | Fecha. Celebração pode sumir, ação frequente segue instantânea |
| R7 Baseline e prova | Overscroll condicional a app shell, revisão com fresh eyes só em gesto ou mobile com risco | Fecha |
| R8 Token | Token visual com exceção para nomear token público como limite, fora de autenticação e API | Fecha |
| R9 Analyze | Design incluído em clarificações, resumo, vivos e linha de quebra, sem nova porta obrigatória | Fecha |

#### Pilares desta etapa

1. Rastreabilidade: cadeia phase 10 com interview, spec, plan, implement e review presentes no relatório; diff só com prosa operacional de skills, sem stub ou task marcada sem código.
2. Testes: 12 distribuicao, 22 spec, 19 design, 34 implement e 18 analyze, 105 no total, todos verdes. `git diff --cached --check` limpo.
3. Segurança: diff só em markdown de contrato, sem entrada externa, auth, segredo ou lockfile. Nenhum pilar de segurança aberto.
4. Visual: omitido, diff sem UI web executável.
5. Simplificação: prosa mínima, uma casa por fato, template apontando para a referência sem duplicar regra.
6. Banco: omitido, repo sem persistência.
