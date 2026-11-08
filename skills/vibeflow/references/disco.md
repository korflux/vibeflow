# Contrato de disco

Única casa das regras de disco do VibeFlow; as demais referências apontam para cá.

## Paths

```text
AGENTS.md                                 fonte única de regras do projeto
.agents/rules/vibeflow.md                 ponte Antigravity, conteúdo exato "@../../AGENTS.md"
~/.claude/agents/<papel>.md               perfis globais de subagente Claude, instalados pelo init
~/.codex/agents/<papel>.toml              perfis globais de subagente Codex, instalados pelo init
                                          (pasta do host conforme references/init.md, Entrada)
~/.vibeflow/old/                          backups de perfis globais substituídos por decisão humana
.claude/agents/ e .codex/agents/          perfis de projeto opcionais, que prevalecem sobre os globais
.vibeflow/phases/.gitkeep
.vibeflow/phases/phase-<n>-<slug>/        uma pasta por pedido
.vibeflow/mvp/                            baseline único de projeto novo
.vibeflow/old/                            backups de arquivos de regra substituídos
```

Artefatos de uma phase ou do MVP, sempre com estes nomes: `spec.md`, `plan.md` e `review.md`. O nome é o tipo, não o título. Não grave artefato em `docs/`, na raiz nem em outro path. Não crie `interview.md`, `design.md`, `analyze.md`, `implement.md`, `todo.md`, `tasks.md`, `CLAUDE.md` ou `GEMINI.md`. A pasta da phase ou do MVP guarda só esses três artefatos: evidência, medição e anotação de passo vão no relatório do papel e, quando a review as cita, no `review.md`, nunca num arquivo próprio como `passo-<n>.md` ou `baseline.md`; `scripts/estado.mjs` avisa arquivo a mais na pasta do alvo.

## Tamanho

Todo papel lê estes arquivos a cada despacho; o tamanho pesa em cada turno e no que o host chega a ler.

| Arquivo | Limite | Quem confere |
|---|---|---|
| `AGENTS.md` | 32 KiB, o limite padrão de leitura do Codex | `scripts/governanca.mjs` |
| `spec.md` | 8 KiB | `scripts/plan.mjs --spec` e `scripts/plan.mjs` |
| `plan.md` | 12 KiB | `scripts/plan.mjs` |
| Linha de passo do plan, sem o campo `Arquivos:`, que o teto de Plan > Arquivos já limita | 400 caracteres | `scripts/plan.mjs` |

- O limite é aviso, sem efeito no código de saída, para que artefato gravado antes dele siga válido; ninguém reescreve artefato antigo só pelo tamanho.
- Em artefato recém-gravado, o aviso volta a quem gravou, que corta o texto sem tirar decisão nem critério. Spec que não cabe sem perder critério é phase grande demais: o líder propõe ao humano dividi-la (`references/interview.md`).
- `AGENTS.md` acima do limite: no re-init, o redator propõe mover para `docs/` o que não é regra, núcleo, comando nem decisão vigente (`references/init.md`, Passos).

| Rota | Artefatos |
|---|---|
| `low` | nenhum; nunca abre phase |
| `medium` | `review.md` |
| `high` e `mvp` | `spec.md`, `plan.md` e `review.md` |

## Abrir phase ou MVP

- `n` é o maior número existente entre as pastas `phase-<n>-<slug>` mais um, comparado em ordem numérica (`phase-10` vem depois de `phase-9`). Sem phases, `n` é 1. Pastas fora do padrão `phase-<n>-<slug>` não contam.
- Slug: frase curta da phase em minúsculas, sem acento, com `a-z`, `0-9` e hífen; hífens repetidos viram um e hífens das pontas saem; de 2 a 48 caracteres. Fora disso, escolha outro slug antes de criar. Com Node, `scripts/estado.mjs --slug "<frase>"` aplica esta regra e devolve o path da próxima phase.
- O líder fixa o path do alvo (`n` e slug) no brief; quem grava o primeiro artefato cria a pasta.
- Pasta que já existe não é recriada nem renomeada. Pedido novo vai para a próxima pasta; ajuste volta à phase de origem (`references/ajuste.md`).
- O MVP usa `.vibeflow/mvp/` uma única vez por repositório. Baseline concluído não é sobrescrito, movido nem versionado; mudança posterior que altera decisão ou comportamento abre phase `high` com `# Risco:` e substituição explícita, e ajuste segue `references/ajuste.md`.

## Escrever artefato

- Artefato ausente nasce do template da etapa (`templates/<artefato>.md`), com a forma copiada e o conteúdo escrito; placeholder não preenchido não fica, e seção não aplicável segue a instrução do template.
- Artefato existente é editado no lugar, nunca recriado nem sobrescrito por inteiro; histórico e trilha são preservados.
- Não escreva através de symlink, junction ou atalho: se `.vibeflow/`, `phases/`, `mvp/`, a pasta da phase ou o artefato for link, pare e relate ao humano.
- Texto que o humano ditou para um campo entra como ele ditou.
- Spec aprovada que precisa mudar é editada no lugar e volta a `rascunho` até nova aprovação humana. Com `plan.md` existente, o líder ajusta o plan e pede nova rodada do analyze antes do próximo passo; esse retorno não aparece na tabela de estados.

## Cabeçalho

| Linha | Onde | Valores e regra |
|---|---|---|
| `# Rota:` | Primeiro artefato da phase: `spec.md` em `high` e `mvp`; `review.md` em `medium` | `medium`, `high` ou `mvp`. A rota não muda; pedido maior abre nova phase |
| `# Risco: <motivo>` | `spec.md`, linha logo após `# Rota:` | Opcional em `high`, quando a mudança toca autenticação, autorização, pagamento, segredo, perda de dados ou produção; obrigatória em `mvp` |
| `# Status:` | `spec.md` e `review.md`, depois do título e de `# Alvo:` quando houver | `rascunho` ou `aprovado`; no `review.md`, também `request-changes` |

- A única aprovação humana antes do código é a da `spec.md`. O `plan.md` não tem `# Status:` nem aprovação humana.
- No `review.md`, o revisor grava `rascunho` ou `request-changes` junto com o veredito (`references/review/passos.md`, Gravar).
- Só o líder grava `aprovado`, na `spec.md` e no `review.md`, depois da confirmação humana.
- Exceção única: no ajuste medium de phase fechada, o líder grava `request-changes` no `review.md` ao abrir o ajuste (`references/ajuste.md`).
- Phase ou MVP cujo primeiro artefato não tem `# Rota:`, ou MVP sem `# Risco:`, é inconsistência a diagnosticar antes de seguir.

## Plan

O `plan.md` é o tracking da phase: um checklist na ordem real de execução. A forma das demais seções fica em `templates/plan.md`.

### Passo

Uma linha física por passo, com os campos nesta ordem, separados por ` · `:

```text
- [ ] 2a: <resultado> · Aceite: A1, A3 · Arquivos: `src/a.ts`, `tests/a.test.ts` · Prova: <comando ou checagem>
```

- ID: número inteiro sem zero à esquerda, seguido de uma letra minúscula quando o passo pertence a um grupo paralelo. Números crescem de 1 em 1 na ordem do arquivo. Passo sozinho não leva letra; um grupo usa `a`, `b`, `c` em sequência.
- `Aceite:` lista os critérios de aceite da spec que o passo entrega, ou `nenhum`.
- `Prova:` é o comando ou a checagem que o implementador roda no passo; o que entra nela segue `references/plan.md` (Prova do passo).
- A linha tem só esses campos. Detalhe técnico (padrão a seguir, linha de referência, ressalva) vai no brief do despacho, nunca num campo `Nota:` nem num arquivo da pasta.
- Estado: só a caixa, marcada `- [x]` pelo líder no commit do passo, sem `Estado:`, `Resumo:` nem IDs `T*`.
- Um grupo começa quando todos os passos e checkpoints anteriores a ele estão marcados.

### Arquivos

- Contam só os paths entre crases do trecho entre `Arquivos:` e `· Prova:`, na linha do passo, relativos ao repo e com os testes. Declare o recorte mais estreito que o passo escreve.
- Barra invertida vale como barra. Diretório vale como prefixo; curinga (`*`, `?`, `[`) vale como o diretório anterior a ele. `.`, `./`, path vazio após normalizar, curinga na raiz e `..` que escapa da raiz valem como a raiz inteira.
- Incomparável: caractere fora do ASCII, path absoluto, `:`, `<`, `>`, `"` ou `|`, ou segmento terminado em ponto ou espaço (exceto `.` e `..`). Passo sem `Arquivos:` ou com path incomparável não tem arquivos comparáveis e não divide número com outro passo.
- Dois paths se sobrepõem quando são iguais ou um é prefixo de diretório do outro (`a` e `a/b`, nunca `a` e `ab`), sem distinção de maiúsculas em A-Z. Passos irmãos (mesmo número) não têm `Arquivos:` sobrepostos.
- Teto: 12 entradas de código por passo, com pasta contando uma. Entrada de teste não conta: path dentro de `tests/`, `test/` ou `__tests__/`, ou nome `*.test.*` ou `*.spec.*`. Passo acima do teto se divide pelo resultado verificável.

### Checkpoint

```text
- [ ] Checkpoint: A1, A2 · Motivo: tela
```

- Linha própria, logo depois do último passo do grupo que fecha os critérios listados. Cobre os passos entre o checkpoint anterior, ou o início do checklist, e ela.
- O motivo vem depois dos critérios, em ` · Motivo:`, e começa por um nome da tabela abaixo; o que vier depois dele é explicação livre. O aceite do checkpoint são os `A<n>` antes do motivo, e um `A<n>` no texto do motivo não é critério. Plan anterior a esta tabela, sem motivo, segue válido: `scripts/plan.mjs` só avisa; plan novo grava o motivo.
- O líder marca a caixa quando o verificador devolve verde; a marcação entra no commit seguinte da phase, sem commit próprio. Checkpoint concluído é o de caixa marcada com a marcação já commitada.
- Checkpoint só por um motivo desta tabela fechada, no máximo 4 por phase, cada um citando o motivo. Phase com até 5 passos não tem checkpoint. `scripts/plan.mjs` acusa o 5º checkpoint, o motivo fora da tabela e o checkpoint em phase de até 5 passos; se a condição do motivo vale é julgamento do analyze (`references/analyze/coverage.md`, Checkpoint fora da regra).

| Motivo | Quando cabe e onde fica |
|---|---|
| `caminho fino` ou `primeiro grupo de risco` | Depois do primeiro grupo de risco; em `high` sem `# Risco:`, depois do caminho fino do critério central |
| `segundo grupo de risco` | Só se a spec tem `# Risco:` e mais de um grupo de passos toca a superfície de risco: depois do segundo grupo |
| `tela` | Só se a phase tem tela: sempre depois do passo que fecha o visual (acabamento incluído) e nunca antes |
| `integração` | Só se a phase tem mais de 10 passos: depois do grupo que junta as partes |

- O que o verificador executa segue `references/verificador.md` (Checkpoint).

### Trabalho alheio

Seção opcional `## Trabalho alheio`, depois de `## Passos` e antes de `## Achados do analyze`, que continua a última. O líder a grava a partir da declaração do humano de que uma alteração fora do recorte não é da phase (`SKILL.md`, seção 5, item 3): um ou mais paths por linha, em lista entre crases separados por vírgula logo depois do `- `, com as regras de path de `Arquivos:` (path incomparável e path que vale a raiz inteira não declaram nada); texto depois da lista, com as próprias crases, é comentário e não declara. Declaração que se sobrepõe ao recorte de passo aberto ou ao path de R* aberto do mesmo plan não vale: o path continua sendo código da phase. R* aberto é o não marcado e o marcado `[x]` ainda sem commit `task(<alvo>:Rn,...)`, como em Estado da phase; passo ou R* sem path comparável não tem recorte e não invalida a declaração. Sem declaração, a seção não existe.

```text
## Trabalho alheio

- `docs/humano.md`
- `docs/a.md`, `docs/b.md`
```

- `scripts/estado.mjs` tira o path de "sem dono" e da retomada do passo, e `scripts/conferir.mjs --passo` não o acusa; ambos leem só o plan do alvo em curso, e a declaração sobreposta ao recorte aberto não vale.
- O staging continua sem ele: `scripts/conferir.mjs --commit` acusa o path declarado, com a marca da declaração, mesmo dentro do recorte, e a finalização da review o deixa fora do commit.
- A regressão da review roda com o path presente e o cita em Notas (`references/review/passos.md`, Disparar a regressão completa).
- Vale só na phase aberta e só onde há `plan.md`. Em entrega low ou medium e sem phase, vale a linha "sem dono" da tabela de Estado da phase: o líder pergunta e o humano isola.

### Achados do analyze

Seção `## Achados do analyze`, a última do `plan.md`, gravada pelo analyze ao concluir:

```text
| Achado | Onde | Ajuste |
|---|---|---|
```

Sem achado, a seção traz a linha `Nenhum achado.`; a presença dela indica que o analyze rodou. Achado que muda decisão do humano na spec não é gravado: o analyze para, o líder pergunta, e a seção só nasce na rodada que conclui.

## Commits

Única casa dos formatos de mensagem e da regra de staging. `<alvo>` é `phase-<n>` ou `mvp`. O líder faz todos os commits: staging explícito só dos paths conferidos, com trabalho alheio fora (Plan > Trabalho alheio), e `git diff --cached --check` limpo antes de commitar. O commit fica local; push só na finalização da review (`references/review.md`, Finalizar).

| Commit | Mensagem |
|---|---|
| Passo ou grupo paralelo, inclusive correção devolvida pelo checkpoint | `task(<alvo>:2a,2b): <resultado>`, IDs na ordem do plan |
| Correção de R* | `task(<alvo>:R1,R2): <resultado>` |
| Entrega medium, antes de a phase existir | `task(medium): <resultado>` |
| Entrega low, sem phase | `task(low): <resultado>` |
| Governança do init | `chore(init): <resultado>` |
| Finalização da review | `chore(<alvo>): finalize review` |
| Push adiado pelo humano | `chore(<alvo>): push adiado` |

O commit `task(medium): ...` leva no corpo, depois de uma linha em branco, os critérios de aceite do brief, um por linha, no formato `- A1: <critério>` de `references/spec.md` (Critérios de aceite). É a única cópia em disco do aceite do medium, lida pela review.

Os commits de uma phase são os que levam o seu `<alvo>` e, no medium, o `task(medium): ...` que o `review.md` registra como base. ID de passo ou de R* só vale no commit do mesmo `<alvo>`. Nenhuma mensagem leva `Co-Authored-By`.

Com Node, depois do staging e antes de cada commit, o líder roda `scripts/conferir.mjs --commit "<mensagem>"`, que confere a mensagem, os critérios no corpo do `task(medium): ...`, caixas e R* marcados no índice contra os IDs, paths em staging contra o recorte e o `git diff --cached --check`. Achado se resolve no staging, na marcação ou na mensagem antes do commit; aviso indica conferência indisponível pelo disco e segue pelo relatório.

## Estado da phase

- Phase ou MVP fechado: `review.md` com `# Status: aprovado` e nenhuma linha `- [ ] R<n>:` aberta. Os demais estão abertos.
- Alvo padrão: a phase aberta de maior `n`; sem phase aberta, o MVP aberto. Outro alvo só quando o humano o nomeia ou quando o líder anuncia a phase de origem de um ajuste. Na retomada com mais de uma phase aberta, pergunte qual retomar, recomendando a de maior `n`.
- Passo concluído: caixa marcada, confirmada por commit `task(<alvo>:...)` com o ID no `git log`. Caixa marcada sem commit, commit sem caixa ou passos irmãos com `Arquivos:` sobrepostos são inconsistência a diagnosticar antes de seguir.
- Inconsistência a diagnosticar: o líder despacha o explorador com o pedido de comparar o disco e o Git com a tabela de estados abaixo e relatar a divergência encontrada. Antes do relatório, o líder não marca, desmarca, reabre nem commita nada; só depois dele decide a correção.
- R* corrigido: o líder marca `[x]` no commit `task(<alvo>:Rn,...)`.
- Push adiado: o líder grava a recusa ou o adiamento do push pelo humano na seção Finalização Git do `review.md`, na linha `- Push adiado pelo humano: <AAAA-MM-DD>`.

Leia a etapa atual na primeira linha da tabela que se aplica. As linhas de spec a checkpoint valem só para `high` e `mvp`.

| Estado no disco | Etapa atual | Próximo responsável |
|---|---|---|
| Commit `task(medium): ...` mais recente no `git log` sem `review.md` com `# Rota: medium` criado depois dele (`review.md` não commitado conta pela existência; commitado, pela ordem no `git log`) | review da entrega medium | Revisor |
| Nenhuma phase aberta e algum alvo fechado (phase ou MVP) está com push pendente (o último commit dela não está no upstream ou o branch não tem upstream), salvo se o `review.md` dela registra push adiado pelo humano e nenhum commit da phase é posterior ao `chore(<alvo>): push adiado` | Push pendente dessa phase, pelo procedimento de retomada de `references/review.md` (Finalizar) | Líder, com a confirmação humana |
| Alteração não commitada fora de `.vibeflow/`, de `.erros-encontrados/` e do `## Trabalho alheio` do plan sem dono no disco: fora dos `Arquivos:` de passos abertos, de passo aberto sem `Arquivos:` comparáveis e dos paths de R* abertos ou marcados `[x]` ainda sem commit | Entrega low ou medium interrompida, ou trabalho alheio | Líder pergunta ao humano, com recomendação, se retoma a entrega ou isola o trabalho |
| Sem phase aberta | Classificar o pedido (`SKILL.md`, seção 2) | Líder |
| Alvo aberto no formato antigo (Compatibilidade) | Inconsistência | Líder relata ao humano, que fecha a phase com a versão anterior da skill |
| `spec.md` ausente | interview | Líder conduz; redator grava a `spec.md` |
| `spec.md` em `rascunho` | spec, aguardando ajuste ou aprovação | Líder apresenta ao humano |
| `spec.md` aprovada e `plan.md` ausente | plan | Líder define; redator grava |
| `plan.md` sem `## Achados do analyze` | analyze | Revisor de contexto limpo |
| Código não commitado nos `Arquivos:` de passos abertos | implement, retomar o passo | Implementador conclui a prova; líder confere e commita; código válido não é refeito |
| Checkpoint aberto com todos os passos anteriores marcados | implement, checkpoint | Verificador de contexto limpo |
| Passo aberto | implement, primeiro número com caixa aberta (passo ou grupo paralelo) | Líder delega ao implementador |
| Todos os passos e checkpoints marcados e sem `review.md` | review | Revisor |
| `review.md` com R* aberto `- [ ]` | implement, corrigir | Implementador ou redator, pelo `papel:` |
| `review.md` em `request-changes` com todos os R* `[x]` e sem commit `task(<alvo>:Rn,...)` com os R* marcados desde a etapa anterior | implement, commitar a correção | Líder commita se a prova da correção está verde; senão, volta ao implementador ou redator |
| `review.md` em `request-changes` com todos os R* `[x]` e com esse commit | review, re-review | Revisor |
| `review.md` em `rascunho` com Approve proposto e nenhum R* aberto | review, confirmar | Líder resume no chat e pede a confirmação única |
| `review.md` em `rascunho` sem veredito marcado na etapa vigente | review, retomar | Revisor |

## Compatibilidade

Formato antigo: alvo com `interview.md`, `design.md` ou `analyze.md`, `# Rota:` `xhigh` ou `max`, ou `plan.md` com blocos `### T<n>:`.

- Alvo antigo fechado (`review.md` com `# Status: aprovado` e sem R* aberto) conta como fechado e fica intocado.
- Alvo antigo aberto é inconsistência: não o conduza com esta versão.

## Glossário

| Termo | Significado |
|---|---|
| Passo | Linha do checklist do `plan.md`; unidade de delegação ao implementador e de commit |
| Grupo paralelo | Passos irmãos, com o mesmo número e letras diferentes, que rodam juntos sem `Arquivos:` sobrepostos |
| Checkpoint | Linha do plan depois de um grupo de passos, por um motivo de Plan (Checkpoint), conferida por um verificador de contexto limpo |
| Risco | Linha `# Risco:` da spec; não acrescenta etapa, mas obriga a interview a cobrir modelo de ameaça e rollback, o plan a pôr checkpoint depois do primeiro grupo de risco e a review a abrir segurança e banco |
| Achado fora do recorte | Defeito fora dos critérios e do diff da phase; vai para `.erros-encontrados/`, um arquivo por achado, gravado por quem o encontrou (verificador ou revisor), e não bloqueia. O líder inclui o registro no commit seguinte da phase, inclusive no `chore(<alvo>): finalize review` |
| Flake | Teste que falha e passa na reexecução; vai para `.erros-encontrados/` e não bloqueia |
| Regressão completa | A suíte inteira do projeto (lint e tipos, unitários, E2E), executada uma vez na review (`references/review/passos.md`) |
