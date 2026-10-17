# Review: init instala os perfis de subagente em nível global
# Alvo: phase-2-init-perfis-globais
# Status: aprovado
# Rota: medium

## Contexto

- Alvo: fase `.vibeflow/phases/phase-2-init-perfis-globais/`, entrega medium no branch `main`
- Cadeia: medium, sem interview, spec, plan ou analyze; julgada contra o brief do humano
- O que muda: a etapa init deixa de copiar os seis perfis de subagente para `.claude/agents/` e `.codex/agents/` do projeto e passa a instalá-los uma vez por máquina em `~/.claude/agents/` e `~/.codex/agents/`, sem sobrescrever perfil divergente sem decisão humana, com backup em `~/.vibeflow/old/` e perfil de projeto prevalecendo. Alterados: `skills/vibeflow/references/init.md`, `skills/vibeflow/references/disco.md` e `README.md`.
- Base medium: `f759050` (`task(medium): init instala os perfis de subagente em nível global`)

## Cobertura da solicitação

- Origem e limites: brief do humano transmitido pelo líder no pedido de review (escolha "Global"); sem interview nem spec. Origem suficiente para o recorte medium.

| Item da solicitação e fonte (A*/C* quando houver) | Implementação | Evidência | Situação |
|---|---|---|---|
| Init instala os perfis em `~/.claude/agents/` e `~/.codex/agents/` (brief) | `skills/vibeflow/references/init.md:29-35`; `skills/vibeflow/references/disco.md:10-11` | leitura do diff; os 12 templates de origem existem em `skills/vibeflow/templates/agents/` | atendido |
| Uma vez por máquina; nos projetos, só confere (brief) | `init.md:3`, `init.md:8` (lê os globais), tabela `init.md:31-35` (idêntico: mantém), `init.md:48` (sem recarga quando idênticos) | leitura do diff; a run em máquina nova com repo já inicializado gera init sem path no repo e não tem regra de commit vazio (R3) | atendido |
| Perfil de projeto, se existir, continua prevalecendo (brief) | `init.md:39`; `disco.md:12`; `README.md:72` | leitura do diff; o init não cria nem remove perfil de projeto | atendido |
| Não sobrescrever customização do usuário fora do repo (foco do líder) | `init.md:35-37`: conflito nunca é sobrescrito sem decisão humana | leitura do diff | atendido |
| Backup do perfil global em `~/.vibeflow/old/` (foco do líder) | `disco.md:95`, `init.md:37` | leitura do diff; o invariante de `AGENTS.md:42` ainda diz `.vibeflow/old/` para perfil (R1); a tabela Paths de `disco.md` não lista `~/.vibeflow/old/` (R2); corrigidos em `4f3adc3` (`AGENTS.md:42`, `disco.md:13`) | atendido |
| Compatibilidade Windows (foco do líder) | `init.md:8`: `~` é `%USERPROFILE%` no Windows | leitura do diff; `CODEX_HOME` e `CLAUDE_CONFIG_DIR` não considerados (R4); corrigido em `4f3adc3` (`init.md:9`, `disco.md:12`) | atendido |
| Commit do init exclui os perfis globais (coerência) | `init.md:40` | leitura do diff | atendido |
| Recarga do host e conferência dos perfis carregados (coerência com `SKILL.md`, seção 5, e Modo B) | `init.md:48`; `SKILL.md:88`, `SKILL.md:100`, `references/delegation.md:7`, `references/implement.md:53` | leitura cruzada: perfil ausente segue para Modo B com sugestão de `/vibeflow init` e recarga, coerente com a instalação global | atendido |
| Nenhum ponto manda o init criar perfil no projeto nem proíbe configuração global de forma contraditória (foco do líder) | `init.md:39` restringe a proibição a "fora dos perfis do VibeFlow" | `grep` por `agents/`, `perfil`, `global` em `skills/`, `README.md` e `AGENTS.md`: nenhuma instrução residual de cópia para o projeto; único resíduo é o invariante de backup (R1) | atendido |

## Checklist de correções

### Required

- [x] R1: **Required** - `AGENTS.md:42` - o invariante "O init guarda em `.vibeflow/old/` [...] o `AGENTS.md`, a ponte ou o perfil que substitui sem backup em commit" contradiz a regra nova: perfil global substituído recebe backup em `~/.vibeflow/old/` (`skills/vibeflow/references/disco.md:95`, `skills/vibeflow/references/init.md:37`), e o init não substitui mais perfil no projeto (`init.md:39`) - remédio: reescrever a linha para dizer que `AGENTS.md` e a ponte vão para `.vibeflow/old/` e o perfil global substituído por decisão humana vai para `~/.vibeflow/old/`, com tamanho e hash conferidos - prova: leitura cruzada de `AGENTS.md:42`, `disco.md:92-98` e `init.md:37` sem contradição; `git diff --check` - source: diff - gap: contradicts - papel: redator

### Nit

- [x] R2: **Nit** - `skills/vibeflow/references/disco.md:16` - `disco.md` se declara a única casa das regras de disco (`disco.md:3`), mas a tabela Paths lista só `.vibeflow/old/`; o path novo `~/.vibeflow/old/` aparece apenas no passo 1 do backup (`disco.md:95`) - remédio: acrescentar à tabela Paths a linha `~/.vibeflow/old/` com o papel "backups de perfis globais substituídos" - prova: leitura de `disco.md` Paths e Backup coerentes - papel: redator
- [x] R3: **Nit** - `skills/vibeflow/references/init.md:40` - com a instalação global, o caso "máquina nova, repo já inicializado" passa a existir: `SKILL.md:100` sugere `/vibeflow init`, o init só instala perfis em `~`, não produz path no repositório, e o passo 6 manda criar commit local sem prever ausência de staging (a regra equivalente existe em `references/review.md:98`, "sem residual, não cria commit vazio") - remédio: acrescentar ao passo 6 que, sem path produzido no repositório, não há commit e o relatório informa `hash: nenhum` - prova: leitura de `init.md` passos 5 e 6 cobrindo o caso sem mudança no repo - papel: redator
- [x] R4: **Nit** - `skills/vibeflow/references/init.md:8` - `~` é definido só como pasta do usuário (`%USERPROFILE%` no Windows), mas o Codex lê a configuração em `$CODEX_HOME` (padrão `~/.codex`) e o Claude Code em `$CLAUDE_CONFIG_DIR` (padrão `~/.claude`); com a variável definida, os perfis caem numa pasta que o host não carrega e a conferência de `init.md:48` falha sem diagnóstico - remédio: no passo 5 e na Entrada, usar `$CODEX_HOME/agents/` e `$CLAUDE_CONFIG_DIR/agents/` quando definidos, com `~/.codex` e `~/.claude` como padrão; refletir em `disco.md:10-11` e `README.md:72` só se o texto citar o path - prova: leitura de `init.md`, `disco.md` e `README.md` coerentes - papel: redator

## Notas

- Repos inicializados antes desta entrega têm perfis VibeFlow commitados em `.claude/agents/` e `.codex/agents/`, que prevalecem sobre os globais; `init.md:39` os relata como customização do projeto, e a remoção, se o humano quiser, já é coberta por `disco.md:92` (backup antes de remover um perfil). Sem R*: o comportamento é o que o brief pediu.
- Hosts com sandbox restrito ao workspace (por exemplo, Codex em `workspace-write`) podem negar escrita em `~`; o agente devolve `estado: bloqueado` pela regra geral de `references/delegation.md` (Relatório fixo). Informação, sem remédio exigido.
- `init.md:48`, trecho "em re-init com os seis perfis idênticos à fonte, não há recarga", repete o que a frase anterior já implica e vale também para o primeiro init de um segundo projeto na mesma máquina; redundante, não contraditório.

## Veredito vigente

- [x] **Approve**: origem suficiente, obrigações atendidas ou retiradas explicitamente pelo humano e nenhum R* de correção em `[ ]`
- [ ] **Request changes**: há R* de correção em `[ ]`

## Handoff

implement | finalização Git da phase

- [x] Aprovação humana (leu o arquivo e confirmou)

- Chat: no Modo A, esta review roda em revisor de contexto limpo, a pedido do líder; sem subagentes, roda num chat novo com `/vibeflow review`. As correções seguem pela etapa implement, com corretor ou redator conforme o `papel` de cada R*; sem subagentes, num chat novo com `/vibeflow implement`. Após Approve e confirmação humana, o handoff é a finalização Git da phase. O `review.md` vivo e o diff são a ponte.

## Finalização Git da phase

- Pré-condições: Approve final confirmado, o commit `task(medium): ...`, todos os R* de correção fechados, prova necessária da integração verde, `git diff --check` e gitleaks.
- Commit final: `chore(phase-2): finalize review`, somente com paths residuais autorizados; sem mudanças residuais, manter o último commit integrado ou da task.
- Push: `git push` para o upstream atual, sem `--force`. Registrar hash/HEAD, paths e resultado; falha mantém o handoff bloqueado.

## Etapas

### Etapa 1 - first-pass - diff `f759050^..HEAD` contra o brief, provas

- Provas reaproveitadas: nenhuma
- Provas executadas: regressão completa de `AGENTS.md` (Comandos do projeto) em `HEAD` `f75905047bc49a5a7550047a7d7cc81e9a2e0746`, árvore limpa: revisão de consistência dos três arquivos alterados (paths do repo citados existem: `skills/vibeflow/references/disco.md`, `skills/vibeflow/references/implement.md`, `skills/vibeflow/templates/AGENTS.md` e os 12 perfis em `skills/vibeflow/templates/agents/`; nenhuma citação à v1); `node --test` (Node 24.22.0): 26/26 verdes; `git diff --check f759050^..HEAD` e `git diff --check`: sem achado; `gitleaks detect --source . --redact --no-banner`: 93 commits, no leaks found
- Execução: diff no recorte do brief (só `README.md`, `references/init.md` e `references/disco.md`, todos ligados à instalação dos perfis); um único commit `task(medium): ...` no intervalo; sem T*
- Leu: brief do humano via líder; `AGENTS.md`; `skills/vibeflow/SKILL.md`; `references/review.md`, `delegation.md`, `disco.md`, `init.md`, `implement.md` (trechos de perfis e Modo B), `analyze.md` (linha de Modo B); `templates/review.md`, `templates/plan.md`; `templates/agents/`; `README.md`
- Cobertura: matriz criada; dois itens parciais (backup, Windows)
- Abriu: R1, R2, R3, R4
- Fechou: nenhum
- Veredito desta etapa: Request changes

### Etapa 2 - re-review - commit `4f3adc3` contra R1 a R4

- Provas reaproveitadas: nenhuma
- Provas executadas: regressão completa de `AGENTS.md` (Comandos do projeto) em `HEAD` `4f3adc3`, árvore limpa: revisão de consistência de `AGENTS.md`, `skills/vibeflow/references/init.md` e `skills/vibeflow/references/disco.md` (paths do repo citados existem; nenhuma citação à v1); `node --test`: 26/26 verdes; `git diff --check f759050^..HEAD` e `git diff --check`: sem achado; `gitleaks detect --source . --redact --no-banner`: no leaks found
- Execução: o commit `task(phase-2:R1,R2,R3,R4): ...` existe e seus IDs são exatamente os R* marcados `[x]` desde a Etapa 1; paths do commit restritos aos remédios (`AGENTS.md`, `init.md`, `disco.md`) e a este `review.md`. R1: `AGENTS.md:42` separa `.vibeflow/old/` (AGENTS.md e ponte) de `~/.vibeflow/old/` (perfil global), coerente com `disco.md:97` e `init.md:38`. R2: `disco.md:13` lista `~/.vibeflow/old/`. R3: `init.md:41` cobre o init sem path no repositório, sem commit vazio e com `hash: nenhum`. R4: `init.md:9` define a pasta do host por `CLAUDE_CONFIG_DIR`/`CODEX_HOME` com padrão `~/.claude`/`~/.codex`, e `disco.md:12` aponta para essa regra. Limite registrado pelo redator (passo 5 sem nova referência à Entrada): basta, porque `init.md:9` declara que os passos abaixo escrevem `~/.claude/agents/` e `~/.codex/agents/` seguindo a regra da pasta do host; repetir no passo 5 duplicaria o fato. `README.md:72` mantém os paths padrão, texto de uso para o humano, sem contradição com a regra
- Leu: diff `f759050..HEAD`; `AGENTS.md:38-43`; `init.md` inteiro; `disco.md` Paths e Backup
- Cobertura: backup e Windows passam de parcial para atendido
- Abriu: nenhum
- Fechou: R1, R2, R3, R4
- Veredito desta etapa: Approve final
