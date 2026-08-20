# Spec: fila elegível e prova em três andares
# Pasta: phase-3-fila-elegivel-prova
# Status: aprovado

## Objetivo

O humano opera a cadeia `vibe-plan` → `vibe-implement` num pedido cuja ordem real das T* não é uma fila única. Hoje a implement assume “próxima T* em sequência” e o script não lê o plan. Esta entrega faz o disco declarar quais T* estão abertas, quais são **elegíveis** (deps satisfeitas) e manda a IA perguntar só quando houver mais de uma elegível. Na mesma entrega, a prova deixa de ser um TDD genérico: spec amarra o observável, plan amarra o comando por T* e o checkpoint do grupo, implement escreve o teste RED-GREEN. Sucesso é o relatório listar a fila sem a IA varrer o markdown, e uma T* só virar `[x]` com comando verde que falhava sem a mudança.

## Inventário

1. Delta em `vibe-implement` (script lê a fila, relatório ganha `fila`, SKILL escolhe T* e endurece prova).
2. Delta em `vibe-plan` (linhas da T* viram contrato; Verificação = comando; checkpoint = suite do grupo).
3. Docs e suíte de contrato tocados pelas duas skills.
4. Uma linha em `docs/ESCOPO.md` registrando o que entrou.

## Suposições e decisões

1. Unidade da fila é a **T***, não a Fase nem o checkpoint. Fase e checkpoint continuam só agrupamento do modo A. — (produto; fechado no chat)
2. Elegível = T* com `- [ ] T{n} concluída` **e** todas as deps em `[x]`. Deps ausente na T* = `nenhuma`. — (produto; fechado)
3. 0 elegível e 0 aberta → handoff `vibe-review`. 0 elegível com abertas bloqueadas → não pergunta “qual T*”; mostra o bloqueio. 1 elegível → executa sem Q. 2+ elegíveis → Q+RECOMENDO, uma pergunta, recomenda a de menor `n` entre as elegíveis (ordem do plan). Humano nomeou a T* (`faz a T3`) → não pergunta; se estiver bloqueada, mostra as deps. — (produto; fechado)
4. R* Critical/Required em `[ ]` no `review.md` continua na frente. Um único R* bloqueante também não pergunta. — (processo; já era)
5. Modo A: a T* escolhida (ou a única elegível) e, no mesmo grupo/checkpoint, só outras T* **já elegíveis** daquele grupo, até o checkpoint. Não salta de grupo. Modo B: percorre elegíveis recalculando depois de cada item, sem Q a cada T*. — (processo)
6. O script passa a interpretar só duas linhas congeladas por T* (`concluída` e `Deps`). Continua sem ler `# Status:`, aceite, verificação ou prosa. Isso é **minor** no relatório (`fila` novo, campos velhos intactos) e quebra o limite escrito “script não interpreta checkbox”. — (processo; semver)
7. Parse falho não derruba o inventário. `fila.parse` = `ok` | `parcial` | `ausente`. Aviso no array `fila.avisos`. Sem `plan.md` na alvo → `fila` nulo (avulsa `low`/`medium` inalterada). — (processo)
8. Barra de teste em três andares. Spec: C* observável (já é regra; esta entrega **não** muda o pacote `vibe-spec`). Plan: cada T* tem Verificação com **comando do repo**; checkpoint = suite das T* do grupo, mais teste de fluxo só se o caminho atravessa mais de uma T*. Implement: escreve ou estende o teste; RED que falha sem a mudança, depois GREEN; sem comando verde não marca `[x]` e não aplica. Não nasce arquivo “teste do plano”. — (produto; fechado no chat)
9. “Leitura do arquivo” e passo só manual **não** contam como prova da T*. Se a Verificação da T* for só manual e não houver comando: Q (automatizar agora / humano valida e reporta / devolver plan). Não pular em silêncio. — (processo)
10. Não commita. Não dispara plan/implement/review. Pedido novo = pasta nova (`phase-3`). — (processo; irmãs)

## Escopo e comportamento

### 1. Fila no relatório da implement

Dado `plan.md` na alvo, o inventário (Python e PowerShell) preenche `fila`:

```json
"fila": {
  "parse": "ok",
  "concluidas": ["T1"],
  "abertas": ["T2", "T3"],
  "elegiveis": ["T2"],
  "bloqueadas": [{"id": "T3", "deps": ["T2"]}],
  "avisos": []
}
```

Regras do parser (contrato, não heurística):

- Cabeçalho de T*: linha que casa `^### T(\d+):` (markdown ATX). Outro heading não entra.
- Done: na seção da T*, a primeira linha que casa `- \[[ xX]\] T{n} concluída`. `[x]` ou `[X]` = concluída; `[ ]` = aberta. Sem essa linha → T* omitida, `parse=parcial`, aviso.
- Deps: primeira linha `- **Deps:** …` na seção. `nenhuma` / vazio / ausente → deps `[]`. IDs `T` + dígitos, separados por vírgula ou `e`. Dep apontando T* inexistente → aviso, T* não entra em `elegiveis`.
- Ordem dos arrays: `n` numérico crescente.
- Checkpoint, Fase, aceite, verificação: o script **não** lê.

A IA **não** monta a fila a partir do markdown se `fila` veio no relatório. Lê `fila` e, se precisar de título/aceite da T* escolhida, abre só essa seção no `plan.md`.

### 2. Skill implement (escolha e modo)

Depois do gate atual (init, high+ sem plan, max sem analyze, analyze bloqueado, R*):

1. Se há R* Critical/Required aberto: fila = esses R*. Q só se houver mais de um.
2. Senão usa `fila` do relatório.
3. Declara no abrir: `fila: T2` (única) ou `fila: T2|T4 elegíveis` (várias, ainda sem executar).
4. Várias elegíveis e o humano **não** nomeou T*: para com Q. Não começa código.
5. Uma elegível, ou humano nomeou uma elegível: ciclo da fatia.
6. Fila zerada (T* e R* bloqueantes): handoff `vibe-review`, sem disparar.

Avulsa sem `plan.md`: `fila` nulo. Comportamento atual.

### 3. Plan (contrato das linhas + verificação)

Template e SKILL do plan congelam, por T*:

```markdown
- [ ] T{n} concluída
- **Verificação:**
  - [ ] `<comando do repo>`
- **Deps:** nenhuma | T1 | T1, T2
```

`Verificação` deixa de aceitar “passo manual” ou “leitura” como único item. Comando tem de existir no repo ou ter sido topado na spec (`python …`, `pwsh …`, wrapper já do app). Várias linhas de verificação ok; pelo menos uma é comando.

Checkpoint (já no template) passa a significar:

- Os testes das T* do grupo passam (suite da fatia).
- Fluxo do grupo só se o caminho observável atravessa mais de uma T*; senão o segundo bullet do checkpoint é N/A e some.

A IA do plan preenche `Deps` de verdade. “Sequencial porque o id é T2” não substitui Deps. Fatias independentes: `Deps: nenhuma` nas duas, para a implement poder oferecer escolha.

Script do plan **não** ganha parser. Quem lê a fila é a implement.

### 4. Prova na implement (três andares no runtime)

No ciclo da fatia, nesta ordem:

1. Test runner do repo (já existe).
2. RED: teste da T* que falha sem a mudança. Se já passava, não é prova. Se a T* não tem path de teste e não há comando na Verificação → Q, sem `[x]`.
3. GREEN + refactor.
4. Verify: comando da Verificação da T* + suite relevante da fatia.
5. UI web: DevTools inalterado.
6. Ao **fechar o checkpoint** do grupo: reroda os comandos das T* do grupo. Só então escreve ou estende teste de fluxo se o caminho atravessa T* e ainda não está coberto.
7. DoD: aceite da T* **e** barra permanente. “Comportamento novo coberto por teste que falha sem a mudança” deixa de ser adaptável para baixo.

Não cria suíte nova no app “porque o plan precisa de um teste do plano”. Review continua julgando C* no fim da fila.

### Fora

- Segunda fila (`todo.md`, `tasks.md`, sidecar JSON da fila) — a fonte é o `plan.md`; o relatório só projeta
- Parser de aceite, Status, checkpoint ou prosa — só `concluída` + `Deps`
- Skill `vibe-spec` / template da spec / `vibe-analyze` nesta entrega — C* observável já vale; analyze pode passar a flagrar Verificação sem comando numa fase futura
- Teste E2E obrigatório por fase — só se o caminho atravessa T*
- Mudar modo A para “uma T* sempre” quando o grupo ainda tem elegíveis no mesmo checkpoint — modo A fecha o grupo escolhido
- Interpretar R* no script — R* continua semântica da IA no `review.md`
- Commit, disparar a próxima skill, Open Questions no markdown

## Checklist de entrega

### Aceite

- [x] A1: Com duas T* elegíveis no plan, o inventário lista as duas em `fila.elegiveis` e a skill pergunta antes de codar
- [x] A2: Com uma T* elegível, a skill executa essa sem Q de escolha
- [x] A3: T* com dep aberta não entra em `elegiveis`; entra em `bloqueadas` com as deps
- [x] A4: Sem prova RED-GREEN (comando da Verificação verde depois de falhar sem a mudança) a skill não marca `[x]` e não aplica
- [x] A5: Plan novo recusa Verificação só manual como único item da T*
- [x] A6: Relatório antigo continua válido: campos atuais permanecem; `fila` é acréscimo. Sem `plan.md`, `fila` é `null`

### Critérios de sucesso

- [x] C1: `docs/vibe-implement/tests/test-implement.py` cobre parse ok, uma elegível, duas elegíveis, dep bloqueando, plan ausente (`fila` nulo), linha `concluída` faltando (`parse=parcial`)
- [x] C2: Paridade pwsh do parse essencial (pelo menos: duas T*, uma bloqueada por dep)
- [x] C3: `SKILL.md` da implement manda ler `fila` do relatório, não o markdown inteiro, para montar a escolha
- [x] C4: Template do plan tem `Deps` e Verificação como comando; SKILL do plan diz quando o checkpoint pede fluxo extra

## Implementação

### Stack

| Área | Escolha |
|---|---|
| Pacotes | `vibe-implement/` e `vibe-plan/` existentes |
| Motor | Python 3 + PowerShell 7 gêmeo; launcher `.sh` inalterado na API |
| Relatório | JSON; campo novo `fila` |
| Dependências novas | Nenhuma |

### Estrutura tocada

```text
vibe-implement/SKILL.md
vibe-implement/scripts/implement.py
vibe-implement/scripts/implement.ps1
vibe-implement/references/definition-of-done.md
vibe-plan/SKILL.md
vibe-plan/templates/plan.md
docs/vibe-implement/ARQUITETURA.md
docs/vibe-implement/ANALISE.md
docs/vibe-implement/tests/test-implement.py
docs/vibe-plan/ARQUITETURA.md
docs/vibe-plan/ANALISE.md
docs/ESCOPO.md
```

`implement.sh` / `plan.sh` só se a flag pública mudar (não muda). Testes PowerShell da implement só se a suíte Python já tiver o contrato e a paridade mínima exigir.

### Estilo e padrões

- reutilizar: inventário atual, `PHASE_RE`, gitignore append-only, erros `CODIGO:`
- parser da fila: funções com comentário semântico; regex âncora nas duas linhas congeladas
- testes: `unittest`, pasta isolada, tearDown apaga; fixtures de `plan.md` mínimos

### Contratos e módulos

- limites: script da implement não escreve `plan.md`; só lê as duas linhas. IA marca `[x]` como hoje.
- schema: `fila` ausente no JSON velho não quebra leitor novo; leitor antigo ignora `fila`.

## Como provar

### Seams

- Plan legado sem linha `T{n} concluída`: `parse=parcial`, T* some da fila, aviso. IA não inventa essa T*.
- Humano pede T* bloqueada: Q com deps, sem código.
- Checkpoint com uma T* só: não inventa teste de fluxo extra.

### Estratégia

- Unitário: parser e resolução de elegíveis em pasta isolada.
- Paridade: um caso apply/inventário no pwsh com plan de duas T*.
- Manual: leitura cruzada SKILL × relatório × template do plan.

### Comandos

```bash
python docs/vibe-implement/tests/test-implement.py
python docs/vibe-plan/tests/test-plan.py
```

## Boundaries

### Always

- Inventário antes de escolher T*.
- Uma Q quando houver 2+ elegíveis e o humano não nomeou a T*.
- Sem teste RED-GREEN, sem `[x]` e sem apply.

### Ask first

- Verificação da T* só manual.
- Sem prova de browser em fatia UI (já existia).

### Never

- Montar a fila “no feeling” se o relatório trouxe `fila`.
- Marcar T* bloqueada por dep.
- Criar `todo.md` / sidecar da fila.
- Disparar `vibe-review`.

## Handoff

vibe-plan

- [x] Aprovação humana (leu o arquivo e confirmou)
