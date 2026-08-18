---
name: vibe-init
description: >
  Inicializa ou repara a fonte única de regras do repo (.vibeflow/REGRAS.md)
  com AGENTS.md e CLAUDE.md como symlink. Use when the user runs /vibe-init,
  pede para preparar o repo para agentes (Claude, Copilot, Codex, Grok),
  deixar as regras dos agentes iguais, criar ou reparar AGENTS.md, CLAUDE.md,
  REGRAS.md ou .vibeflow, unificar regras, consertar symlink quebrado, ou um
  checkout Windows em que AGENTS.md só contém o path, ou um repo sem
  .vibeflow / sem regras de agente — mesmo que não diga vibe-init.
---

# vibe-init

Não invente fato que o disco não mostrou. Não escolha uma fonte e descarte a outra.
Fonte viva das regras: **sempre** `.vibeflow/REGRAS.md`. `AGENTS.md` / `CLAUDE.md` são ponteiros.
Primeira vez (repo sem `.vibeflow`): este `description` dispara o init — o roteador da cadeia só existe no `REGRAS.md` **depois**.
Depois do init: preserve o bloco `<!-- VIBEFLOW:CADEIA -->`; o script o atualiza. Não é regra do usuário nem entra em merge.

No repo vibeflow, leia `docs/vibe-init/ARQUITETURA.md` **só** se o inventário tiver estado ou merge que este arquivo não cobre. No install isolado, este `SKILL.md` basta.

## 0. Script primeiro

1. Resolva o diretório desta skill (pasta deste `SKILL.md`).
2. No cwd do repo do usuário:
   - Windows: `pwsh "<skill>/scripts/init.ps1"`
   - Unix: `bash "<skill>/scripts/init.sh"`
3. Leia `.vibeflow/init-report.json` + `.vibeflow/REGRAS.md` atual + **cada** path em `merges[].sources` (ignore fonte `ponteiro_texto`: é path de checkout, não regra).
4. Leitura dirigida para preencher/corrigir `REGRAS.md`: só o que o relatório, SLOTs, evidência ou o humano apontaram (README, manifest, path citado). Não abrir a árvore inteira nem `node_modules` / `.git` / `dist`.

Se o script parar com `SYMLINK_RECUSADO`: mostre Developer Mode / admin. Não copie `REGRAS.md` para a raiz — a cópia diverge na próxima edição e deixa de ser uma fonte.
Se `inventory` trouxer `ponteiro_texto`: checkout Windows/`core.symlinks=false`. Avise; o script tenta restaurar o symlink. Não mergeie essa string — é o alvo do Git, não uma regra.

Old verificado **antes** de substituir qualquer arquivo do usuário: um crash no meio sem old apaga o original.

## 1. Abrir (5 linhas)

fluxo · olds gravados · merges · conflitos · slots

```
reparar · old: AGENTS.md · merge: legado_vs_regras · conflito: nenhum · slots: ambiente, regras
```

REPARAR saudável, sem SLOT, sem merge, sem conflito → disco ok; **ainda pergunta P4**. Não reprocessa disco.

## 2. Merge (se `merges[]`)

Não pergunte «qual arquivo vale?». Une:

1. Leia os olds em `merges[].sources` e o `REGRAS`/template atual. Pule fonte cujo conteúdo é só o path `.vibeflow/REGRAS.md`. O bloco `VIBEFLOW:CADEIA` sai do template, não das fontes.
2. Cada trecho: em qualquer fonte → entra; igual nas duas → uma vez; só numa → entra sem reescrever; A diz X e C diz não-X → os dois em `## Conflito a fechar` (rótulo da origem) + pergunta `contradição`.
3. Encaixa no template se for da seção (parágrafo, ambiente, semver, git, estrutura). Resto → `## Regras deste repo`.
4. Política do template (semver, sem Co-Authored-By) é **oferta**, não overwrite. Se o legado tem política diferente: mostre `padrão: X` vs `deles: Y` e pergunte qual fica no vivo. Sem resposta, os dois ficam em `## Conflito a fechar`. Não apague a política do usuário em silêncio.
5. Grave `.vibeflow/REGRAS.md`. Mapa no chat (5–15 linhas):

```
de AGENTS: regra de número no dashboard
de CLAUDE: —
das duas: parágrafo do projeto
contradição: ambiente homolog vs produção
política oferecida: semver (legado não tinha)
```

6. Antes de trocar ponteiros, no vivo:
   - [ ] política do usuário ainda está (ou está em `## Conflito a fechar`)
   - [ ] nenhum parágrafo é só o path `.vibeflow/REGRAS.md`
   - [ ] só fechou SLOT que o humano respondeu
   - [ ] mapa de origem já foi mostrado
7. Só então: `pwsh "<skill>/scripts/init.ps1" -ApplyPointers` (Unix: `init.sh --apply-pointers`).

## 3. Conflitos (um por vez)

| Id | Ação |
|---|---|
| `contradição` | Mostra os dois; humano escolhe; perdedor some só do vivo |
| `ponteiro_alheio` | Default = deixar. Se redirecionar: `init.ps1 -RedirectPointer AGENTS` (ou `CLAUDE`) |
| `tipo_inesperado` | Não toca; humano resolve fora |

## 4. Perguntas

Uma por vez. Várias respostas de uma vez: aceita e fecha. Patch = só o SLOT; texto do humano, sem «melhorar».

| # | Pergunta | Não perguntar se |
|---|---|---|
| P1 | Parágrafo do projeto — mostra extraído ou o que o merge já trouxe | `paragrafo` fechado |
| P2 | Homolog ou produção? | `ambiente` fechado |
| P3 | Qual regra deste repo o scan/merge não pega? | humano já ditou nesta run |
| P4 | Falta alguma informação? Algo ambíguo que queira registrar? | humano já encerrou nesta run |

NOVO: P1–P4 obrigatórias (P3 pode ser «nenhuma»).
REPARAR saudável: P1–P3 só se SLOT/merge ainda abrir; **P4 sempre** (o usuário sabe mais que o disco).
Extras quando o relatório, uma leitura dirigida ou a resposta anterior deixar ambiguidade — não inventar pergunta sem esse gancho.

Se P2 = produção e `migrations_detectadas`: acrescente o bloco fixo abaixo (não invente outro texto):

```markdown
## Produção / migrations
Migration em produção é irreversível no sentido prático. Não gerar, não aplicar, não “aproveitar o gancho”. Se a tarefa exigir schema, parar e perguntar.
```

## 5. Fechar

Não commita. Avise: commitar `REGRAS.md`, os dois symlinks, `.vibeflow/old/` (se existir) e `.vibeflow/phases/.gitkeep`. Não commitar `init-report.json`.
Windows: `core.symlinks=true` é aviso no relatório, não forçado.

## Fora (v1)

Outras `vibe-*`, CI, hook, `--force`, copiar `REGRAS` na raiz, escolher homolog/produção sozinho, inventar regra, spec/plan/todo.
