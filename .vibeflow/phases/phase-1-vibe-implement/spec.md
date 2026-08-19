# Spec: skill vibe-implement
# Pasta: phase-1-vibe-implement
# Status: aprovado

## Objetivo

O agente no repo do app precisa de uma porta que **escreve código com prova**, sem pular etapa e sem inventar fila paralela. Esta entrega cria a skill `vibe-implement`: lê o contexto da fase (interview, spec, plan, analyze se existir), executa a próxima fatia, marca `[x]` no disco onde a prova aconteceu, para e fala com o humano quando uma etapa não fecha. Sucesso é o humano ver no `plan.md` (e na spec, se couber) o item marcado **depois** de teste/verify reais, e o chat só apontar o que fechou.

## Inventário

1. Pacote `vibe-implement/` (SKILL, scripts gêmeos, refs sob demanda). Sem template de artefato próprio.
2. `docs/vibe-implement/` (ARQUITETURA, ANALISE, testes de contrato).
3. Relatório `.vibeflow/implement-report.json` (gitignored).
4. Uma linha no `README.md` do repo.
5. Inventário do script passa a enxergar `review.md` se existir (não cria a skill review).

## Suposições e decisões

1. Sem `implement.md`. Progresso mora no `plan.md` (T* e checkpoints) e, quando a fatia prova, nos `A*`/`C*` da spec. REGRAS: implement só grava artefato se a arquitetura mandar; o plan já prometeu que a build marca o `plan.md`. — (processo)
2. Script é inventário + gitignore. Sem `--apply` de wip e sem `--slug`. A IA edita checkbox nos vivos da cadeia. — (processo)
3. Modo A (uma fase até o próximo checkpoint, ou uma T* se não houver agrupamento) é o default. Modo B (run da fila) só com pedido explícito (`auto`, “faz o todo”, “não para”). — (processo; pedido)
4. Travou ferramenta, teste ou prova visual → **para**. Q+RECOMENDO com opções concretas (consertar a ferramenta / o humano valida e reporta / mudar a verificação). Pular em silêncio é defeito. — (processo; pedido)
5. UI web user-visible: padrão e recomendação = **Chrome DevTools MCP** (navegar, snapshot de a11y, screenshot, IA lê a imagem). Playwright (ou E2E já do repo) é válido se o humano pedir, se a T* já manda esse comando, ou se o DevTools não estiver disponível e o humano escolher essa opção. Não adicionar Playwright como dependência nova sem o humano pedir. Sem MCP de DevTools e sem E2E no repo → para e pergunta; não escolhe ferramenta em silêncio. — (produto; pedido)
6. Código de comportamento exige prova: TDD (`RED→GREEN→REFACTOR`) ou prove-it (bug: teste que reproduz, depois o fix). “Testo no final” é defeito. — (processo; força Fluxline)
7. Rota `low`/`medium` clara pode ser implement avulsa sem plan. Rota `high+` sem `plan.md` para e manda `/vibe-plan`. Rota `max` sem `analyze.md` para e manda `/vibe-analyze`. Analyze com veredito `bloqueado` recusa código, mesmo com pedido de implement. — (processo; cadeia)
8. Pedido desta porta com plan (ou analyze) em `# Status: rascunho` e veredito não bloqueado → flip para `aprovado` e segue. Igual spec/plan/analyze. — (processo)
9. Se existir `review.md` na mesma pasta com `R*` Critical/Required em `[ ]`, essa fila manda na T*. v1 já consome; não cria `vibe-review`. — (processo; força Fluxline)
10. Esta skill **não** commita. Working tree. Humano commita. Sem `Co-Authored-By`. — (processo; irmãs)
11. Não dispara `vibe-review`. Handoff é linha no chat (e no plan, se o handoff da fase já aponta). — (processo)
12. Não faz o job da analyze (cruzar artefatos) nem da review (veredito). Não cria ignore files, research, contracts, tasks.md. — (escopo)
13. Refs no v1: `references/chrome-devtools.md` (quando UI web) e `references/definition-of-done.md` (gate “pronto?”). Descoberta do test runner mora no SKILL. Sem pack de 12 refs. — (escopo)

## Escopo e comportamento

### 1. Script (disco)

- Sem `.vibeflow/` → `INIT_AUSENTE`. Não inventa fase.
- `phases/` ausente → cria + `.gitkeep`. Não mexe em `REGRAS.md`.
- Inventário JSON: `vibeflow`, `phases`, `next_n` (informativo), `existing[]` com `files` (`interview.md`, `spec.md`, `plan.md`, `analyze.md`, `review.md` se presente), `alvo`, `modo_sugerido`, `avisos`, `actions`.
- `alvo`: maior `n` com `plan.md`; `--dir phase-N-slug` força pasta existente. Sem plan em pasta alguma → `alvo` nulo, `modo_sugerido=criar` no sentido “não há fase para executar”. Script **não** cria pasta.
- Relatório em `.vibeflow/implement-report.json`. Stdout = path do relatório.
- Garante `.gitignore`: `implement-report.json`. Sem wip. Não apaga entradas das outras skills.
- Flags públicas iguais nos motores: `--root` / `-Root`, `--dir` / `-Dir`. Sem `--apply`, sem `--force`, sem `--slug`.
- Falha prevista: `CODIGO: o que aconteceu` no stderr. Sem stack para o humano.
- Três arquivos, um contrato: `implement.py`, `implement.ps1`, `implement.sh` (Python 3, senão pwsh 7).

### 2. Skill (semântica)

Dado o relatório:

1. Lê `REGRAS.md`. Se `alvo`, lê o que existir nessa pasta: interview, spec, plan, analyze, review. Paths só os citados. Não varre a árvore.
2. Declara no chat, em poucas linhas: `ROUTE`, modo A/B, alvo, o que vai executar (T* ou R*).
3. Gate da tabela em Suposições (item 7–9).
4. Descobre o stack de teste do **repo** (manifest, wrapper, CI, um teste focado vs suite). Não assume `npm test`.
5. Executa a fatia: RED → GREEN → REFACTOR → verify do repo (teste da fatia, suite relevante, build/typecheck/lint se existirem).
6. UI web user-visible: depois do verde, prova no browser. Default: Chrome DevTools (ver ref). Screenshot + leitura da IA no fechamento. Snapshot de a11y para interagir; screenshot para julgar o visual. Se a T* ou o humano pediu Playwright/E2E do repo, roda isso também (ou no lugar, se o humano cravou).
7. Com prova verde: marca `[x]` **na mesma resposta**, sem perguntar: T* (concluída + aceite + verificação) no `plan.md`; checkpoint da fase se fechou o último T* do grupo; `A*`/`C*` na spec só os que a fatia **provou**; `R*` no review se era essa a fila.
8. Sem prova: deixa `[ ]` e reporta.
9. Modo A: para. Chat: ids marcados, paths, comandos/provas, próximo T*/checkpoint ou handoff `vibe-review` se a fila da run acabou.
10. Modo B: percorre; para em checkpoint vermelho ou em bloqueio; marca a cada item fechado.
11. Buraco de intenção/sucesso/fora → devolve interview/spec. Buraco pontual de desenho → Q+RECOMENDO. “Tanto faz” crava a rec e anota na fatia se relevante.

### 3. Prova visual (browser)

Quando a fatia muda o que o usuário vê no browser:

- **Default / recomendar:** MCP `chrome-devtools` já ligado no host: navegar até o fluxo, snapshot para achar controle, interagir, screenshot do alvo (página, dialog ou trecho).
- Playwright ou outro E2E do repo: usar quando o humano pedir, quando a verificação da T* já for esse comando, ou quando o DevTools faltar e o humano escolher essa opção na Q.
- A IA **lê** a evidência visual (screenshot do DevTools ou artefato do E2E). Layout, copy, estado vazio/erro, contraste óbvio, elemento coberto. Print sem leitura não conta.
- Pixel baseline não é default.
- Sem servidor / URL e sem nenhuma prova de browser possível: para. Não inventa que “UI ok no unit”.

### 4. Implement avulso (`low`/`medium`)

- Sem `plan.md`: permitido se o pedido é claro e a rota não foi promovida.
- Prova mínima (teste ou prove-it; browser se UI, DevTools por padrão).
- Não inventa `A*`/`T*` nem pasta de fase.
- Chat: o que mudou, como provou, o que ficou de fora. Handoff `vibe-review` só se o humano pediu review/merge ou a rota é `medium+`.

### Fora

- Artefato `implement.md` / wip / `todo.md` / `tasks.md` / `checklists/` — uma casa por fato; a fila já é o plan
- Path `docs/fluxline/`, `specs/NNN-slug/`, branch `###-feature` — contrato é `phase-N-slug`
- Adicionar Playwright (ou outra lib de browser) como dependência nova sem o humano pedir — o default visual é DevTools; E2E já do repo continua válido
- Criar `.gitignore` de stack, `.npmignore`, ignore de ferramenta — efeito colateral do spec-kit implement; não é desta porta
- Hooks / `extensions.yml` / constitution file extra — outro produto; constituição é `REGRAS.md`
- Analyze e review feitos “de passagem” — portas irmãs
- Run completa sem o humano pedir — modo A é o default
- Marcar `[x]` sem prova, ou só no chat — disco manda
- Commit, disparar a próxima skill, Open Questions no `.md`, dump do plan no chat
- Carregar todas as refs no boot

## Checklist de entrega

### Aceite

- [ ] A1: Com `plan.md` na fase, o agente executa a próxima T* (ou fase até o checkpoint) e, com prova verde, marca os checkboxes correspondentes no `plan.md` (e `A*`/`C*` na spec se a T* os cita e a prova cobre)
- [ ] A2: Sem prova (teste falhou, ferramenta quebrada, nenhuma prova de browser possível em fatia UI) o agente **não** marca `[x]`, para e oferece opções ao humano
- [ ] A3: Modo default para após uma fase/T*; só continua a fila se o humano pediu modo B ou “pode seguir”
- [ ] A4: Fatia UI web user-visible usa Chrome DevTools por padrão (screenshot + leitura) quando o MCP existe; Playwright/E2E entra se o humano pediu ou se a T* já manda; sem nenhuma das duas, para e pergunta
- [ ] A5: Rota `high+` sem plan recusa código; rota `max` sem analyze recusa; analyze `bloqueado` recusa
- [x] A6: Script de inventário existe nos três motores, grava `implement-report.json`, não aloca `n`, não tem `--apply`

### Critérios de sucesso

- [x] C1: Suíte `docs/vibe-implement/tests/test-implement.py` cobre os invariantes de disco (init ausente, alvo com plan, `--dir`, gitignore, sem criar fase, sem apply)
- [x] C2: `SKILL.md` cabe como prompt operacional (gate, ciclo, marcar, parar, DevTools, Fora) sem narrar o porquê do produto
- [x] C3: Humano consegue apontar no `plan.md` o que fechou sem reler o chat
- [ ] C4: Pedido `low` sem plan ainda produz código com prova, sem inventar pasta

## Implementação

### Stack

| Área | Escolha |
|---|---|
| Pacote | igual às irmãs: `vibe-implement/` na raiz |
| Motor | Python 3 + PowerShell 7 gêmeo + launcher `.sh` |
| Relatório | JSON, stdout = path |
| Dependências novas | Nenhuma |
| Browser | MCP `chrome-devtools` do host; zero lib no repo |

### Estrutura tocada

```text
vibe-implement/SKILL.md
vibe-implement/scripts/implement.py
vibe-implement/scripts/implement.ps1
vibe-implement/scripts/implement.sh
vibe-implement/references/chrome-devtools.md
vibe-implement/references/definition-of-done.md
docs/vibe-implement/ARQUITETURA.md
docs/vibe-implement/ANALISE.md
docs/vibe-implement/tests/test-implement.py
README.md                         # uma linha na tabela de skills
```

Sem `templates/` (não há markdown próprio para promover).

### Estilo e padrões

- reutilizar: inventário de `vibe-plan` / `vibe-analyze` (PHASE_RE, CHAIN_FILES estendido, gitignore append-only, erros `CODIGO:`)
- comentário semântico em toda função do script
- SKILL na ordem das irmãs: invariante, script primeiro, abrir, gate, passos, Fora
- testes: `unittest`, pasta isolada, tearDown apaga; Python é a suíte; paridade pwsh skip se não houver

### Contratos e módulos

- limites: script não interpreta checkbox nem Status; não escreve `plan.md`/`spec.md`
- IA é quem marca e quem escreve código no app
- schema do relatório estável (breaking = major)

## Como provar

### Seams

- Alvo errado (implementar a fase velha) — `--dir` e regra “maior n com plan”
- Marcar sem prova — skill + anti-skip; teste de contrato não pega semântica
- DevTools sumido — Q obrigatória; opções incluem Playwright/E2E do repo se existir, validação humana, ou ligar o MCP. Sem escolha em silêncio
- `max` sem analyze — gate da skill, não do script (script não conhece rota)

### Estratégia

- Unitário: inventário e erros do script em temp dir
- Manual: uma run desta própria skill, depois de pronta, contra a fase desta spec (modo A, T* 1)

### Comandos

```bash
python docs/vibe-implement/tests/test-implement.py
# Windows, inventário deste repo:
pwsh vibe-implement/scripts/implement.ps1
```

## Boundaries

### Always

- Ler o que a fase tem (interview/spec/plan/analyze/review) antes de codar, quando a pasta existe
- Descobrir o test runner do repo
- Parar quando a prova não fecha
- Marcar disco na mesma resposta da prova verde
- Português do Brasil no SKILL, docs e chat

### Ask first

- Continuar depois do modo A
- Pular ou degradar prova (ferramenta, DevTools, teste que não sobe)
- Qualquer buraco que mude aceite ou Fora da spec

### Never

- Inventar `n` ou pasta
- Marcar `[x]` no chute
- Trocar ou pular a prova visual em silêncio
- Commit
- Disparar review/analyze/plan
- Open Questions no markdown
- Ignore files de stack
- Segunda fila no chat

## Handoff

vibe-plan

- [x] Aprovação humana (leu o arquivo e confirmou)
