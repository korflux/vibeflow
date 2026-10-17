# Contrato de disco

Única casa das regras de disco do VibeFlow. As demais referências apontam para cá em vez de repetir.

## Paths

```text
AGENTS.md                                 fonte única de regras do projeto
.agents/rules/vibeflow.md                 ponte Antigravity, conteúdo exato "@../../AGENTS.md"
.claude/agents/<papel>.md                 perfis de subagente Claude
.codex/agents/<papel>.toml                perfis de subagente Codex
.vibeflow/phases/.gitkeep
.vibeflow/phases/phase-<n>-<slug>/        uma pasta por pedido
.vibeflow/mvp/                            baseline único de projeto novo
.vibeflow/old/                            backups de arquivos de regra substituídos
```

Artefatos de uma phase ou do MVP, sempre com estes nomes: `interview.md`, `spec.md`, `design.md`, `plan.md`, `analyze.md` e `review.md`. O nome é o tipo, não o título. Não grave artefato em `docs/`, na raiz nem em outro path. Não crie `implement.md`, `todo.md`, `tasks.md`, `CLAUDE.md` ou `GEMINI.md`.

## Abrir phase ou MVP

- `n` é o maior número existente entre as pastas `phase-<n>-<slug>` mais um, comparado em ordem numérica (`phase-10` vem depois de `phase-9`). Sem phases, `n` é 1. Pastas fora do padrão `phase-<n>-<slug>` não contam.
- Slug: frase curta da phase em minúsculas, sem acento, com `a-z`, `0-9` e hífen; hífens repetidos viram um e hífens das pontas saem; de 2 a 48 caracteres. Fora disso, escolha outro slug antes de criar.
- O líder fixa o path do alvo (`n` e slug) no brief; quem grava o primeiro artefato cria a pasta.
- Pasta que já existe não é recriada nem renomeada. Pedido novo vai para a próxima pasta.
- O MVP usa `.vibeflow/mvp/` uma única vez por repositório. Baseline concluído não é sobrescrito, movido nem versionado; mudança posterior abre phase `max` com substituição explícita.

## Escrever artefato

- Artefato ausente nasce do template da etapa (`templates/<artefato>.md`), copiando a forma e escrevendo o conteúdo; placeholder não preenchido não fica no arquivo, e seção não aplicável segue a instrução do próprio template.
- Artefato existente é editado no lugar, nunca recriado nem sobrescrito por inteiro; histórico e trilha são preservados.
- Não escreva através de symlink, junction ou atalho: se `.vibeflow/`, `phases/`, `mvp/`, a pasta da phase ou o artefato for link, pare e relate ao humano.
- Texto que o humano ditou para um campo entra como ele ditou.
- Artefato posterior existente bloqueia só a criação de um novo artefato da etapa anterior. Voltar a uma etapa anterior edita o vivo dela; o finalizador devolve esse artefato e os posteriores aprovados a `rascunho`, e cada dono reconfere o seu antes da nova aprovação.

## Cabeçalho

- `# Status:` no bloco de cabeçalho de cada artefato, depois do título e de `# Alvo:` quando houver: `rascunho` durante a elaboração, `aprovado` depois da aprovação humana, e no `review.md` também `request-changes`. Só o finalizador, ou o líder em ajuste direto (`SKILL.md`, seção 5), muda para `aprovado`.
- `# Rota:` grava a rota da phase no primeiro artefato criado: `interview.md` em `xhigh`, `max` e MVP; `spec.md` em `high`; `review.md` em `medium`. Valores: `medium`, `high`, `xhigh`, `max`, `mvp`. A rota não muda; pedido maior abre nova phase. Low, inclusive Express, nunca abre phase.
- Plans não levam `# Protocolo:` nem `# Modo:`; o modo (com ou sem subagentes) é decidido na run.
- Phase ou MVP cujo primeiro artefato não tem `# Rota:` é inconsistência a diagnosticar antes de seguir.

## Commits

Única casa dos formatos de mensagem. `<alvo>` é `phase-<n>` ou `mvp`.

| Commit | Mensagem |
|---|---|
| Onda de T* | `task(<alvo>:T1,T2,...): <resultado>`, IDs em ordem numérica |
| Correção de R* | `task(<alvo>:R1,R2,...): <resultado>` |
| Entrega medium, antes de a phase existir | `task(medium): <resultado>` |
| Express | `task(express): <resultado>` |
| Finalização da review | `chore(<alvo>): finalize review` |
| Push adiado pelo humano | `chore(<alvo>): push adiado` |

Os commits de uma phase são os que levam o seu `<alvo>` e, no medium, o `task(medium): ...` que o `review.md` registra como base. ID de T* ou R* só vale no commit do mesmo `<alvo>`. Nenhuma mensagem leva `Co-Authored-By`.

## Estado da phase

- Phase ou MVP fechado: `review.md` com `# Status: aprovado` e nenhuma linha `- [ ] R<n>:` aberta. Os demais estão abertos.
- Alvo padrão: a phase aberta de maior `n`; sem phase aberta, o MVP aberto. Outro alvo só quando o humano o nomeia.
- Etapa concluída: artefato com `# Status: aprovado`; no `analyze.md`, também veredito `limpo` na seção `## Veredito`. Design sem UI nova conta como concluído quando o `plan.md` ou o Handoff da spec registra `Design: N/A` com motivo.
- T* concluída: caixa `- [x] Tn concluída` no `plan.md`, confirmada por commit `task(<alvo>:...)` com o ID no `git log`. Caixa marcada sem commit, ou commit sem caixa, é inconsistência a diagnosticar antes de seguir.
- Estado da fila: a linha `- **Estado:**` de cada T* no `plan.md`, escrita pelo finalizador, vale `pendente`, `em andamento`, `pronta` (prova afetada verde, ainda sem commit), `bloqueada` ou `concluída`, este marcado junto com a caixa no commit. O resumo curto fica na linha `- **Resumo:**`.
- Push adiado: o humano que recusa ou adia o push da phase tem a decisão gravada pelo finalizador na seção Finalização Git do `review.md`, na linha `- Push adiado pelo humano: <AAAA-MM-DD>`.

Leia a etapa atual na primeira linha da tabela que se aplica:

| Estado no disco | Etapa atual | Próximo responsável |
|---|---|---|
| Commit `task(medium): ...` mais recente no `git log` sem `review.md` com `# Rota: medium` criado depois dele (`review.md` não commitado conta pela existência; commitado, pela ordem no `git log`) | review da entrega medium | Revisor |
| Nenhuma phase aberta e o alvo fechado mais recente (phase de maior `n` ou MVP) está com push pendente (o último commit dela não está no upstream ou o branch não tem upstream), salvo se o `review.md` dela registra push adiado pelo humano | Push pendente dessa phase, pelo procedimento de retomada de `references/review.md` (Finalizar) | Finalizador, com a confirmação humana |
| Alteração não commitada fora de `.vibeflow/` sem dono no disco: fora dos `Arquivos:` de T* abertas, de T* aberta sem `Arquivos:` e dos paths de R* abertos ou marcados `[x]` ainda sem commit | Entrega Express ou medium interrompida, ou trabalho alheio | Líder pergunta ao humano, com recomendação, se retoma a entrega ou isola o trabalho |
| Sem phase aberta | Classificar o pedido (`SKILL.md`, seção 2) | Líder |
| Etapa de planejamento exigida pela rota sem artefato | Essa etapa | Líder conduz; redator grava (revisor no analyze) |
| `analyze.md` com veredito `bloqueado` | analyze, correção dos achados | Dono do artefato; revisor reconfere |
| Artefato de planejamento em `rascunho` | Essa etapa, aguardando ajuste ou aprovação | Líder apresenta ao humano |
| T* `em andamento` ou código não commitado nos `Arquivos:` de T* abertas | implement, retomar a onda | Verificador confere o diff e a prova afetada existentes; falha vai ao corretor; código válido não é refeito |
| T* `pronta` sem commit e nenhuma `em andamento` | implement, validar e commitar a onda | Verificador reaproveita prova de inputs inalterados; finalizador commita |
| Plan liberado pelo gate e T* `pendente` elegível | implement, implementar a próxima onda | Líder monta a onda |
| T* abertas, todas `bloqueada` ou dependentes de uma bloqueada | implement, impedimento | Líder leva o impedimento ao humano, com recomendação |
| Todas as T* concluídas com commit e sem `review.md` | review | Revisor |
| `review.md` com R* aberto `- [ ]` | implement, corrigir | Corretor ou redator, pelo `papel:` |
| `review.md` em `request-changes` com todos os R* `[x]` e sem commit `task(<alvo>:Rn,...)` com os R* marcados desde a etapa anterior | implement, commitar a correção | Finalizador commita se a prova da correção está verde; senão, diagnóstico pelo verificador |
| `review.md` em `request-changes` com todos os R* `[x]` e commit `task(<alvo>:Rn,...)` com os R* marcados desde a etapa anterior | review, re-review | Revisor |
| `review.md` em `rascunho` com Approve proposto e nenhum R* aberto | implement, confirmar | Líder pede a confirmação única |
| `review.md` em `rascunho` sem veredito marcado na etapa vigente | review, retomar | Revisor |

## Backup de arquivo de regra

Antes de substituir ou remover `AGENTS.md`, a ponte ou um perfil:

1. Se o arquivo está commitado sem alteração local, o commit é o backup. Senão, copie para `.vibeflow/old/` com o mesmo nome (a ponte vira `antigravity-vibeflow.md`).
2. Confira tamanho e SHA-256 da cópia contra o original; divergência apaga a cópia e interrompe a substituição.
3. Destino em `old/` com o mesmo conteúdo é reutilizado; com conteúdo diferente, acrescente o sufixo UTC `.<AAAAMMDDTHHMMSSZ>`.
4. Só então substitua ou remova o original.
