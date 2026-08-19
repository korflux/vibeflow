# Regras do projeto

<!-- VIBEFLOW:CADEIA start -->
| esforço | fluxo | quando |
|---|---|---|
| — | init | primeira vez no repo, ou disco quebrado — de novo só para reparar |
| low | implement | pedido claro, direto, simples (cor, texto…) |
| medium | implement → review | pedido claro e direto, sem possibilidade de regressão |
| high | spec → plan → implement → review | pedido claro, execução difícil, ou possibilidade de regressão |
| xhigh | interview → spec → plan → implement → review | pedido ambíguo, confiança baixa, intenção ou sucesso em aberto |
| max | interview → spec → plan → analyze → implement → review | pedido toca auth, pagamento, segredo, perda de dados, produção ou alto blast radius |
<!-- VIBEFLOW:CADEIA end -->

## Projeto

Cadeia de skills para inicializar e conduzir o trabalho de agentes num repo. Este repositório é a fonte canônica das skills `vibe-*` e do contrato `.vibeflow/`. Não é um app de produção.

<!-- evidência: README.md -->

## Ambiente

homolog

Este repo não tem banco, migration nem tráfego de usuário. Skills aqui mudam contrato de agente, não schema de produção.

## Versão (semver)

- **Major:** quebra contrato (path de artefato, schema do relatório, flag pública do script, comportamento que outra skill ou o humano já usa).
- **Minor:** adiciona sem quebrar (nova seção opcional no artefato, novo aviso no relatório).
- **Patch:** correção sem mudança de contrato.
- Produção: migration só com plano de rollback; não rodar migration destrutiva sem o humano pedir.

## Git

- Sem `Co-Authored-By` de ferramenta em commit/push.
- Commitável: `.vibeflow/REGRAS.md`, `AGENTS.md`, `CLAUDE.md`, `.vibeflow/old/` se existir, `.vibeflow/phases/` (`.gitkeep` e artefatos vivos), pacote da skill, `docs/`.
- Não commitar: `init-report.json`, `init-pending.json`, `*-report.json`, `*-wip.md`, `*-pending.json`.
- `AGENTS.md` e `CLAUDE.md` são symlink para `.vibeflow/REGRAS.md`. Nunca copiar o conteúdo para a raiz.

## Estrutura

```
.vibeflow/REGRAS.md          fonte viva das regras
.vibeflow/phases/            artefatos da cadeia (phase-N-slug/)
.vibeflow/old/               backups do init, se houver
AGENTS.md                    symlink → .vibeflow/REGRAS.md
CLAUDE.md                    symlink → .vibeflow/REGRAS.md
vibe-<nome>/                 pacote instalável da skill
docs/vibe-<nome>/            arquitetura, análise, testes (não instala)
README.md
```

Pacote de uma skill pronta:

```
vibe-<nome>/
  SKILL.md
  scripts/<nome>.ps1
  scripts/<nome>.py
  scripts/<nome>.sh
  templates/<artefato>.md    se a skill grava markdown
  references/                só catálogo sob demanda
```

Documentos:

```
docs/vibe-<nome>/
  ARQUITETURA.md
  ANALISE.md
  tests/test-<nome>.py
  tests/test-<nome>.ps1      só se o motor PowerShell tiver contratos próprios
  BRIEFING.md                só se o pedido original ainda servir de âncora
```

<!-- evidência: disco do repo -->

## Regras deste repo

Estas regras existem para a próxima `vibe-*` nascer igual às que já estão prontas (`vibe-init`, `vibe-interview`, `vibe-spec`, `vibe-plan`). Contrato específico de uma skill vive em `docs/vibe-<nome>/ARQUITETURA.md`. Aqui vive só o que se repete.

### 1. Pacote `vibe-<nome>`

- Nome: `vibe-` + verbo curto (`init`, `interview`, `spec`, `plan`, `analyze`, `implement`, `review`). Minúsculas, hífen, sem pontuação.
- Fonte canônica no git: `vibe-<nome>/` na raiz deste repo. Install recomendado: user-scope `<grok-home>/skills/vibe-<nome>` (cópia do pacote, sem `docs/`).
- Pasta vazia de skill futura fica só com `.gitkeep` até existir `SKILL.md`.
- Não criar skill “por via das dúvidas”. Só quando o contrato de disco e o fluxo da IA estiverem claros o bastante para escrever `ARQUITETURA.md`.

### 2. Documentos `docs/vibe-<nome>`

Dois arquivos obrigatórios. Não misturar os papéis.

| Arquivo | Papel | Pergunta que responde |
|---|---|---|
| `ARQUITETURA.md` | Contrato | O que o disco faz, quem é dono de cada path, schema do relatório, erros, testes, Fora |
| `ANALISE.md` | Fluxo e decisão | O que acontece numa run de ponta a ponta, por que as peças existem, o que foi cortado, o que foi assumido |

`ARQUITETURA.md` não narra a conversa. `ANALISE.md` não é a spec do script. Se um fato precisa valer no código, ele mora na arquitetura (e a skill aponta para o script, não copia o schema).

Testes de contrato ficam em `docs/vibe-<nome>/tests/`, fora do pacote instalável. Não rodam quando a skill é ativada.

### 3. Disco: uma fonte, uma pasta de fase, um arquivo por skill

```
.vibeflow/REGRAS.md
.vibeflow/phases/phase-<n>-<slug>/<artefato>.md
```

- `n` inteiro crescente, sem zero à esquerda, ordem **numérica**. Calculado pelo script (max existente + 1). A IA não inventa `n`.
- `slug`: frase curta da fase, `a-z0-9` e hífen, 2–48 chars. O script sanitiza.
- Pasta da fase agrupa o pedido. Skills seguintes gravam **na mesma pasta**, outro arquivo.
- Nome do arquivo é o tipo, não o título: `interview.md`, `spec.md`, `plan.md`, `analyze.md`. Implement e review só gravam se a arquitetura daquela skill disser que existe artefato.
- Não gravar cadeia em `docs/`, na raiz, nem em path de outro produto (`fluxline`, etc.).
- Relatório operacional: `.vibeflow/<nome>-report.json` (gitignored). Stdout do script = path do relatório.
- Wip, se a sessão for longa e o slug ainda não existir: `.vibeflow/<nome>-wip.md` (gitignored). Apply promove wip → vivo com cópia binária + tamanho + SHA-256. Wip só some depois da cópia bater.
- Continuar o mesmo pedido: editar o vivo. Pedido novo: próxima pasta. Não renomear pasta depois de criada.
- Sem `.vibeflow/`: a skill que não é o init para e manda `/vibe-init`.

### 4. Papéis na run

```
Skill (SKILL.md)  →  o que a IA faz, em que ordem
Script            →  fato de disco (inventário, n, slug, cópia, symlink, relatório)
IA                →  semântica (perguntas, merge de prosa, preencher template)
Humano            →  só decisão que o disco não resolve
```

Script não escreve prosa. IA não escolhe path, não inventa número, não “melhorar” texto que o humano ditou para um SLOT.

Inventário **antes** de interpretar o projeto. Relatório JSON é o contrato script → IA. A IA lê o relatório e só os paths que ele (ou o humano) apontou. Não varrer a árvore.

### 5. Scripts

Três arquivos, um contrato:

| Arquivo | Papel |
|---|---|
| `<nome>.py` | Motor portátil (Python 3) |
| `<nome>.ps1` | Motor Windows com o mesmo contrato |
| `<nome>.sh` | Launcher Unix: Python 3, senão `pwsh`. Sem motor degradado |

- Sem um dos motores (Python 3 ou PowerShell 7), parar e informar a dependência.
- Flags públicas iguais nos dois motores (`--apply` / `-Apply`, `--slug` / `-Slug`, `--root` / `-Root`).
- Falha prevista: mensagem curta no stderr no formato `CODIGO: o que aconteceu`. Sem stack para o humano.
- Função no script leva comentário semântico (para que serve; se a decisão não for óbvia, o porquê). Nenhuma função órfã.
- Old/backup de arquivo do usuário: copiar, conferir tamanho + hash, **só então** substituir. Colisão em `old/` vira timestamp. Init já faz isso; skills que mexem em arquivo alheio repetem.
- Relatório e wip entram no `.gitignore` **dentro** de `.vibeflow/`, sem apagar entradas das outras skills.

### 6. Template

- Mora em `vibe-<nome>/templates/`. É esqueleto, não documento preenchido.
- A IA copia a forma e escreve o conteúdo (no wip ou no vivo).
- O script **não** preenche markdown. Apply só promove bytes.
- Seções fixas, nomes estáveis, um lar por fato. Placeholder óbvio (`<frase curta>`), sem prosa de exemplo que a IA possa colar sem pensar.
- Seção opcional (ex.: Direção só na Fase 2) diz no próprio template quando omitir. Não criar arquivo extra para variação da mesma skill.

### 7. Escrita da skill (`SKILL.md`)

O `SKILL.md` é prompt operacional para o agente, não artigo. Barra: `vibe-init` e `vibe-interview`.

Frontmatter obrigatório:

```yaml
---
name: vibe-<nome>
description: >
  O que faz, em 1–2 frases, e onde grava. Use when the user runs
  /vibe-<nome>, <gatilhos em português e em comportamento>, mesmo
  que não diga vibe-<nome>.
---
```

`description` dispara auto-invoke. Sem ela a skill não entra sozinha. Primeira vez no repo, o bloco cadeia ainda não existe: o init depende desse `description`.

Corpo, nesta ordem, salvo se a arquitetura justificar furo:

1. Duas ou três linhas de invariante (o que nunca fazer).
2. **0. Script primeiro** (path da skill, comando Windows/Unix, o que ler no relatório, erros que não se contorna).
3. **1. Abrir** em ~5 linhas de estado (fluxo, slots, next_n, aberta, wip). Bloco de exemplo curto.
4. Passos numerados: gate, trabalho semântico, gravar, fechar.
5. **Fora (v1)** explícito.

Regras de prosa na skill:

- Uma casa por fato. Tabela, não parágrafo repetido. Catálogo (frameworks, critérios) fica em `references/` e a skill aponta: “leia X quando Y”. Não resumir a tabela no SKILL.
- Sem “por que o produto existe”. Isso é `ANALISE.md`.
- Sem seção órfã (“ver template abaixo” sem template).
- Uma pergunta por vez. Várias respostas de uma vez: aceitar e fechar.
- Patch de SLOT = só aquele trecho, texto do humano, sem reescrever.
- Não disparar a próxima `vibe-*`. Handoff é uma linha no artefato (`vibe-spec`, `precisa-forma`, …).
- Não commitar. No fechar, dizer o que entra no git e o que fica de fora.
- Português do Brasil. Frase completa. Sem emoji. Sem travessão longo. Tom factual, calmo, sem acolhimento.

### 8. Tom (chat e artefato)

Vale para skill, docs, relatório em prosa e conversa neste repo.

- Factual e profissional. Cortar enrolação, não contexto.
- Começar pelo que é verdade ou pelo que fazer. Não abrir com “não é X”.
- Explicar código por o que acontece, por que, impacto. Não exigir sintaxe do humano.
- Artefato vivo guarda a **lógica** (pedido → passos → conclusão), não só o recap. Não apagar trilha para “limpar” no final.
- Chat curto no restate; disco completo. Chat sozinho não conta quando a skill promete arquivo.
- Número de confiança, n, slug, path: só se o disco ou o humano sustentarem. Chute vira GUESS explícito, não fato.
- Decisão do humano: perguntar na hora, com opções e recomendação. Se não muda o resultado, assumir e avisar.

### 9. Testes de contrato

- Sem framework além de `unittest` (Python) e asserts no `.ps1` se existir suíte PowerShell.
- Cada invariante de risco (não perder arquivo, n numérico, path, gitignore, recusa sem init) vira um caso.
- Motor Python é a suíte principal. Paridade PowerShell: o apply/inventário essencial, quando `pwsh` existe; se não existe, skip, não falha.
- Pasta isolada por teste, apagada no tearDown. Não escrever no repo real.

### 10. Ordem para criar uma skill nova

1. `docs/vibe-<nome>/ARQUITETURA.md` (contrato de disco).
2. `docs/vibe-<nome>/ANALISE.md` (fluxo e cortes).
3. `vibe-<nome>/SKILL.md` + `templates/` + `references/` se couber.
4. Scripts (`.py` primeiro, depois `.ps1` gêmeo, depois `.sh`).
5. `docs/vibe-<nome>/tests/` e só então declarar pronto.
6. Uma linha no `README.md` do repo.

Não inverter: skill sem arquitetura vira path inventado (foi o defeito da interview em `docs/fluxline/`).

### Fora deste repo (v1)

- Copiar `REGRAS.md` para `AGENTS.md` / `CLAUDE.md` na raiz.
- Segunda fonte de regras fora de `.vibeflow/REGRAS.md`.
- Artefato da cadeia fora de `.vibeflow/phases/phase-N-slug/`.
- Skill nova sem o par `ARQUITETURA.md` + `ANALISE.md`.
- Dependência nova, CI, hook, `--force`, motor único “só Python” ou “só PowerShell”.
- Disparar a próxima skill da cadeia sem o humano pedir.
