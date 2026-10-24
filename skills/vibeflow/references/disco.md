# Contrato de disco

Única casa das regras de disco do VibeFlow. As demais referências apontam para cá em vez de repetir.

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

Artefatos de uma phase ou do MVP, sempre com estes nomes: `spec.md`, `plan.md` e `review.md`. O nome é o tipo, não o título. Não grave artefato em `docs/`, na raiz nem em outro path. Não crie `interview.md`, `design.md`, `analyze.md`, `implement.md`, `todo.md`, `tasks.md`, `CLAUDE.md` ou `GEMINI.md`.

| Rota | Artefatos |
|---|---|
| `low` | nenhum; nunca abre phase |
| `medium` | `review.md` |
| `high` e `mvp` | `spec.md`, `plan.md` e `review.md` |

## Abrir phase ou MVP

- `n` é o maior número existente entre as pastas `phase-<n>-<slug>` mais um, comparado em ordem numérica (`phase-10` vem depois de `phase-9`). Sem phases, `n` é 1. Pastas fora do padrão `phase-<n>-<slug>` não contam.
- Slug: frase curta da phase em minúsculas, sem acento, com `a-z`, `0-9` e hífen; hífens repetidos viram um e hífens das pontas saem; de 2 a 48 caracteres. Fora disso, escolha outro slug antes de criar.
- O líder fixa o path do alvo (`n` e slug) no brief; quem grava o primeiro artefato cria a pasta.
- Pasta que já existe não é recriada nem renomeada. Pedido novo vai para a próxima pasta; ajuste volta à phase de origem (`references/implement.md`, Ajuste de phase).
- O MVP usa `.vibeflow/mvp/` uma única vez por repositório. Baseline concluído não é sobrescrito, movido nem versionado; mudança posterior que altera decisão ou comportamento abre phase `high` com `# Risco:` e substituição explícita, e ajuste segue `references/implement.md` (Ajuste de phase).

## Escrever artefato

- Artefato ausente nasce do template da etapa (`templates/<artefato>.md`), copiando a forma e escrevendo o conteúdo; placeholder não preenchido não fica no arquivo, e seção não aplicável segue a instrução do próprio template.
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
- Só o líder muda `# Status:` para `aprovado`, depois da confirmação humana.
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
- `Prova:` é o comando ou a checagem que o implementador roda no passo.
- Estado: só a caixa. `- [x]` é marcada pelo líder no commit do passo. Não há `Estado:`, `Resumo:` nem IDs `T*`.
- Um grupo começa quando todos os passos e checkpoints anteriores a ele estão marcados.

### Arquivos

- Só o texto entre crases do trecho entre `Arquivos:` e `· Prova:` conta, sempre na linha do passo.
- Paths relativos ao repo, testes incluídos. Diretório ou curinga (`*`, `?`, `[`) vale como prefixo do diretório anterior ao curinga. `.`, `./`, path vazio após normalizar, curinga na raiz e `..` que escapa da raiz valem como a raiz inteira. Barra invertida vale como barra.
- Dois paths se sobrepõem quando são iguais ou um é prefixo de diretório do outro (`a` e `a/b`, nunca `a` e `ab`), comparando sem distinção de maiúsculas em A-Z.
- Path incomparável torna o passo inteiro sem arquivos comparáveis: caractere fora do ASCII, path absoluto, `:`, `<`, `>`, `"` ou `|`, ou segmento terminado em ponto ou espaço (exceto `.` e `..`). Passo sem `Arquivos:` ou com path incomparável não divide número com outro passo.
- Passos irmãos (mesmo número) não têm `Arquivos:` sobrepostos. Declare o recorte mais estreito que o passo escreve.

### Checkpoint

```text
- [ ] Checkpoint: A1, A2
```

- Linha própria, logo depois do último passo do grupo que fecha os critérios listados. Cobre os passos entre o checkpoint anterior, ou o início do checklist, e ela.
- O líder marca a caixa quando o verificador devolve verde; a marcação entra no commit seguinte da phase, sem commit próprio.
- Phase pequena não tem checkpoint. Com `# Risco:`, há um checkpoint depois de cada grupo de risco.

### Achados do analyze

Seção `## Achados do analyze`, a última do `plan.md`, gravada pelo analyze ao concluir:

```text
| Achado | Onde | Ajuste |
|---|---|---|
```

Sem achado, a seção traz a linha `Nenhum achado.`. A presença da seção indica que o analyze rodou. Achado que muda uma decisão do humano na spec não é gravado: o analyze para, o líder pergunta, e a seção só nasce na rodada que conclui.

## Commits

Única casa dos formatos de mensagem. `<alvo>` é `phase-<n>` ou `mvp`. O líder faz todos os commits.

| Commit | Mensagem |
|---|---|
| Passo ou grupo paralelo, inclusive correção devolvida pelo checkpoint | `task(<alvo>:2a,2b): <resultado>`, IDs na ordem do plan |
| Correção de R* | `task(<alvo>:R1,R2): <resultado>` |
| Entrega medium, antes de a phase existir | `task(medium): <resultado>` |
| Entrega low, sem phase | `task(low): <resultado>` |
| Governança do init | `chore(init): <resultado>` |
| Finalização da review | `chore(<alvo>): finalize review` |
| Push adiado pelo humano | `chore(<alvo>): push adiado` |

Os commits de uma phase são os que levam o seu `<alvo>` e, no medium, o `task(medium): ...` que o `review.md` registra como base. ID de passo ou de R* só vale no commit do mesmo `<alvo>`. Nenhuma mensagem leva `Co-Authored-By`.

## Estado da phase

- Phase ou MVP fechado: `review.md` com `# Status: aprovado` e nenhuma linha `- [ ] R<n>:` aberta. Os demais estão abertos.
- Alvo padrão: a phase aberta de maior `n`; sem phase aberta, o MVP aberto. Outro alvo só quando o humano o nomeia ou quando o líder anuncia a phase de origem de um ajuste. Na retomada com mais de uma phase aberta, pergunte qual retomar, recomendando a de maior `n`.
- Passo concluído: caixa marcada, confirmada por commit `task(<alvo>:...)` com o ID no `git log`. Caixa marcada sem commit, commit sem caixa ou passos irmãos com `Arquivos:` sobrepostos são inconsistência a diagnosticar antes de seguir.
- R* corrigido: o líder marca `[x]` no commit `task(<alvo>:Rn,...)`.
- Push adiado: o humano que recusa ou adia o push da phase tem a decisão gravada pelo líder na seção Finalização Git do `review.md`, na linha `- Push adiado pelo humano: <AAAA-MM-DD>`.

Leia a etapa atual na primeira linha da tabela que se aplica. As linhas de spec a checkpoint valem só para `high` e `mvp`.

| Estado no disco | Etapa atual | Próximo responsável |
|---|---|---|
| Commit `task(medium): ...` mais recente no `git log` sem `review.md` com `# Rota: medium` criado depois dele (`review.md` não commitado conta pela existência; commitado, pela ordem no `git log`) | review da entrega medium | Revisor |
| Nenhuma phase aberta e algum alvo fechado (phase ou MVP) está com push pendente (o último commit dela não está no upstream ou o branch não tem upstream), salvo se o `review.md` dela registra push adiado pelo humano e nenhum commit da phase é posterior ao `chore(<alvo>): push adiado` | Push pendente dessa phase, pelo procedimento de retomada de `references/review.md` (Finalizar) | Líder, com a confirmação humana |
| Alteração não commitada fora de `.vibeflow/` e de `.erros-encontrados/` sem dono no disco: fora dos `Arquivos:` de passos abertos, de passo aberto sem `Arquivos:` comparáveis e dos paths de R* abertos ou marcados `[x]` ainda sem commit | Entrega low ou medium interrompida, ou trabalho alheio | Líder pergunta ao humano, com recomendação, se retoma a entrega ou isola o trabalho |
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
| `review.md` em `request-changes` com todos os R* `[x]` e commit `task(<alvo>:Rn,...)` com os R* marcados desde a etapa anterior | review, re-review | Revisor |
| `review.md` em `rascunho` com Approve proposto e nenhum R* aberto | review, confirmar | Líder resume no chat e pede a confirmação única |
| `review.md` em `rascunho` sem veredito marcado na etapa vigente | review, retomar | Revisor |

## Compatibilidade

Formato antigo: alvo com `interview.md`, `design.md` ou `analyze.md`, `# Rota:` `xhigh` ou `max`, ou `plan.md` com blocos `### T<n>:`.

- Alvo antigo fechado (`review.md` com `# Status: aprovado` e sem R* aberto) conta como fechado e fica intocado.
- Alvo antigo aberto é inconsistência: não o conduza com esta versão.

## Backup de arquivo de regra

Antes de substituir ou remover `AGENTS.md`, a ponte ou um perfil:

1. Se o arquivo está commitado sem alteração local, o commit é o backup. Senão, copie para `.vibeflow/old/` com o mesmo nome (a ponte vira `antigravity-vibeflow.md`).
   Perfil global substituído por decisão humana recebe a cópia em `~/.vibeflow/old/`, com o mesmo nome e as mesmas conferências.
2. Confira tamanho e SHA-256 da cópia contra o original; divergência apaga a cópia e interrompe a substituição.
3. Destino em `old/` com o mesmo conteúdo é reutilizado; com conteúdo diferente, acrescente o sufixo UTC `.<AAAAMMDDTHHMMSSZ>`.
4. Só então substitua ou remova o original.

## Glossário

| Termo | Significado |
|---|---|
| Passo | Linha do checklist do `plan.md`; unidade de delegação ao implementador e de commit |
| Grupo paralelo | Passos irmãos, com o mesmo número e letras diferentes, que rodam juntos sem `Arquivos:` sobrepostos |
| Checkpoint | Linha do plan depois de um grupo de passos; um verificador de contexto limpo roda as provas desses passos e confere o diff contra a spec |
| Risco | Linha `# Risco:` da spec; não acrescenta etapa, mas obriga a interview a cobrir modelo de ameaça e rollback, o plan a pôr checkpoint depois de cada grupo de risco e a review a abrir segurança e banco |
| Achado fora do recorte | Defeito que não pertence aos critérios nem ao diff da phase; vai para `.erros-encontrados/`, um arquivo por achado, gravado por quem o encontrou (verificador ou revisor), e não bloqueia. O líder inclui o registro no commit seguinte da phase, inclusive no `chore(<alvo>): finalize review` |
| Flake | Teste que falha e passa na reexecução; vai para `.erros-encontrados/` e não bloqueia |
| Regressão completa | A suíte inteira do projeto (lint e tipos, unitários, E2E), executada uma vez na review (`references/review.md`) |
