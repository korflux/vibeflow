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

Artefatos de uma phase ou do MVP, sempre com estes nomes: `interview.md`, `spec.md`, `design.md`, `plan.md`, `analyze.md` e `review.md`. O nome é o tipo, não o título. Não grave artefato em `docs/`, na raiz nem em outro path. Não crie `implement.md`, `todo.md`, `tasks.md`, `CLAUDE.md`, `REGRAS.md` ou `GEMINI.md`.

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

## Cabeçalho

- `# Status:` no cabeçalho de cada artefato, logo abaixo do título: `rascunho` durante a elaboração, `aprovado` depois da aprovação humana, e no `review.md` também `request-changes`. Só o finalizador muda para `aprovado`.
- `# Rota:` grava a rota da phase no primeiro artefato criado: `interview.md` em `xhigh`, `max` e MVP; `spec.md` em `high`; `review.md` em `medium`. Valores: `medium`, `high`, `xhigh`, `max`, `mvp`. A rota não muda; pedido maior abre nova phase. Low, inclusive Express, nunca abre phase.
- Plans da V2 não levam `# Protocolo:` nem `# Modo:`; o modo (com ou sem subagentes) é decidido na run.

## Estado da phase

- Phase fechada: `review.md` com `# Status: aprovado` e nenhuma linha `- [ ] R<n>:` aberta. As demais estão abertas.
- Alvo padrão: a phase aberta de maior `n`. Outra phase só quando o humano a nomeia. O MVP só é alvo quando o pedido é o baseline.
- Etapa concluída: artefato com `# Status: aprovado`; no `analyze.md`, também veredito `limpo` na seção `## Veredito`. Design sem UI visível conta como concluído quando o `plan.md` ou o Handoff da spec registra `Design: N/A` com motivo.
- T* concluída: caixa `- [x] Tn concluída` no `plan.md`, confirmada por commit `task(...)` com o ID no `git log`. Numa phase V2, caixa marcada sem commit, ou commit sem caixa, é inconsistência a diagnosticar antes de seguir.
- Estado da fila: o resumo curto que o finalizador escreve em cada T* do `plan.md` diz se ela está pronta (prova afetada verde, ainda sem commit), em andamento ou pendente.

Leia a etapa atual na primeira linha da tabela que se aplica:

| Estado no disco | Etapa atual | Próximo responsável |
|---|---|---|
| Commit `task(medium): ...` mais recente no `git log` sem `review.md` com `# Rota: medium` criado depois dele (`review.md` não commitado conta pela existência; commitado, pela ordem no `git log`) | review da entrega medium | Revisor |
| Última phase fechada com commits à frente do upstream (`git status -sb`) | Conferir push pendente ou residual da finalização | Finalizador, com a confirmação humana já dada |
| Sem phase aberta | Classificar o pedido (`SKILL.md`, seção 2) | Líder |
| Etapa de planejamento exigida pela rota sem artefato | Essa etapa | Líder conduz; redator grava (revisor no analyze) |
| `analyze.md` com veredito `bloqueado` | analyze, correção dos achados | Dono do artefato; revisor reconfere |
| Artefato de planejamento em `rascunho` | Essa etapa, aguardando ajuste ou aprovação | Líder apresenta ao humano |
| Plan liberado pelo gate, T* abertas e nenhuma pronta ou em andamento | implement, implementar por ondas | Líder monta a onda |
| T* em andamento ou código não commitado nos `Arquivos:` de T* abertas | implement, retomar a onda | Verificador confere o diff e a prova afetada existentes; falha vai ao corretor; código válido não é refeito |
| Todas as T* prontas, caixas vazias, sem commit | implement, validar e commitar | Verificador reaproveita prova de inputs inalterados; finalizador commita |
| Todas as T* concluídas com commit e sem `review.md` | review | Revisor |
| `review.md` com R* aberto `- [ ]` | implement, corrigir | Corretor ou redator, pelo `papel:` |
| `review.md` em `request-changes` com todos os R* `[x]` e sem commit `task(Rn,...)` | implement, commitar a correção | Finalizador commita se a prova da correção está verde; senão, diagnóstico pelo verificador |
| `review.md` em `request-changes` com todos os R* `[x]` e commit `task(Rn,...)` | review, re-review | Revisor |
| `review.md` em `rascunho` com Approve proposto e nenhum R* aberto | implement, confirmar | Líder pede a confirmação única |

## Phases da v1

Phase sem `# Rota:` foi criada pela v1 e é lida como está, sem migração nem reescrita. Seu `plan.md` pode trazer `# Protocolo: coordenacao-v1` ou `# Protocolo: etapas-v1` e `# Modo: A` ou `# Modo: B`; esses marcadores só identificam a origem e não mudam a condução. Em plan `coordenacao-v1`, a v1 não marcava caixas: T* concluída é reconhecida pelo commit `task(...)` com o ID no `git log`, mesmo com a caixa vazia, e isso não é inconsistência. O estado vem das linhas `# Status:`, das caixas do `plan.md`, dos R* do `review.md` e do `git log`. Linhas `- **Execução:**` e `- **Integração:**` do plan e o arquivo JSON de execução que a v1 deixava na pasta da phase são preservados byte a byte e não são interpretados. Os gates dessa phase seguem os artefatos presentes (`SKILL.md`, seção 3). Pedido novo sobre ela abre phase V2.

## Backup de arquivo de regra

Antes de substituir ou remover `AGENTS.md`, `REGRAS.md`, `CLAUDE.md`, `.vibeflow/REGRAS.md`, a ponte ou um perfil do usuário:

1. Se o arquivo está commitado sem alteração local, o commit é o backup. Senão, copie para `.vibeflow/old/` com o mesmo nome (`.vibeflow/REGRAS.md` vira `REGRAS-vibeflow.md`; a ponte vira `antigravity-vibeflow.md`).
2. Confira tamanho e SHA-256 da cópia contra o original; divergência apaga a cópia e interrompe a substituição.
3. Destino em `old/` com o mesmo conteúdo é reutilizado; com conteúdo diferente, acrescente o sufixo UTC `.<AAAAMMDDTHHMMSSZ>`.
4. Só então substitua ou remova o original.
