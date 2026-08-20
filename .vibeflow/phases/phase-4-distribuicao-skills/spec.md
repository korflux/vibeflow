# Spec: distribuição das skills para Codex, Claude, Grok e Antigravity
# Pasta: phase-4-distribuicao-skills
# Status: aprovado

## Objetivo

Quem publica ou consome o vibeflow precisa instalar as sete skills `vibe-*` no Codex, no Claude Code, no Grok Build e no Antigravity, em escopo global (máquina do usuário) ou local (um repo). Sucesso é: outro usuário, a partir do GitHub `korflux/vibeflow`, instala o pacote inteiro com um comando do CLI `npx skills` **ou** com o marketplace nativo de cada um dos quatro agentes, e passa a invocar `/vibe-init` … `/vibe-review` sem copiar pasta na mão.

## Inventário

1. `npx skills add` (projeto e `-g` global) para os quatro agentes, e de brinde os demais que o CLI já cobre
2. Manifests nativos: Claude, Codex, Grok, Antigravity
3. Pasta `skills/` como ponteiro para os pacotes canônicos `vibe-<nome>/`
4. README com os comandos de install
5. `REGRAS.md` / `docs/ESCOPO.md` atualizados no contrato de disco
6. Teste de contrato dos manifests e dos ponteiros

## Suposições e decisões

1. Superfície A: CLI `npx skills` **e** manifests nativos dos quatro agentes — (produto; fechado nesta conversa)
2. Sem aliases de slash (`/spec`, `/plan`, …). O comando é o `name` da skill (`/vibe-init`, …) — (produto; fechado nesta conversa)
3. Pacote canônico permanece `vibe-<nome>/` na raiz. Não mover para `skills/`. Major recusado — (escopo)
4. Um plugin, sete skills. Nome do marketplace e do plugin: `vibeflow`. Install Claude: `vibeflow@vibeflow` — (produto)
5. `skills/vibe-<nome>` é symlink git (mode 120000) para `../vibe-<nome>`, o mesmo mecanismo de `AGENTS.md`. Sem cópia da prosa. Checkout Windows continua exigindo symlink real (`core.symlinks=true` / Developer Mode), já documentado no init — (processo)
6. Claude nativo lista os paths `./vibe-*` no manifest (source `./`) para não carregar `skills/` **e** a raiz e duplicar nome — (produto)
7. Codex, Grok plugin e Antigravity leem `skills/` — (produto)
8. Sem skill nova `vibe-install`. Sem `commands/`. Sem personas em `agents/`. Sem hooks. Sem MCP — (escopo)
9. Sem LICENSE nesta fatia. Marketplace não exige MIT para install privado/GitHub — (escopo)
10. Semver desta superfície: **Minor**. Só acrescenta arquivos de distribuição. Path de artefato, scripts e `SKILL.md` não mudam — (processo)
11. Repo público de install: `https://github.com/korflux/vibeflow` — (produto)
12. Versão nos manifests: `1.0.0` (primeira superfície pública de plugin). Bump futuro só quando o contrato de plugin mudar — (processo)

## Escopo e comportamento

### 1. CLI `npx skills`

- Dado o repo `korflux/vibeflow` (ou clone local), `npx skills add korflux/vibeflow --list` lista **exatamente** as sete skills, uma vez cada, pelos `name` do frontmatter.
- Install projeto (default): copia ou faz symlink para o path de skill de cada agente escolhido (tabela abaixo).
- Install global (`-g`): idem nos paths `~/…`.
- Agentes desta entrega: `grok`, `claude-code`, `codex`, `antigravity`. O CLI pode oferecer outros; o README só promete esses quatro.
- `--copy` é o contorno documentado quando o destino não aceita symlink.

| `--agent` | Projeto | Global |
|---|---|---|
| `claude-code` | `.claude/skills/` | `~/.claude/skills/` |
| `codex` | `.agents/skills/` | `~/.codex/skills/` |
| `grok` | `.grok/skills/` | `~/.grok/skills/` |
| `antigravity` | `.agents/skills/` | `~/.gemini/antigravity/skills/` |

### 2. Pasta `skills/`

- Existe na raiz. Contém só as sete entradas `vibe-init`, `vibe-interview`, `vibe-spec`, `vibe-plan`, `vibe-analyze`, `vibe-implement`, `vibe-review`.
- Cada entrada é symlink relativo para `../vibe-<nome>`. Destino resolve para o pacote completo (`SKILL.md`, `scripts/`, `templates/`, `references/` se houver).
- Sem `SKILL.md` extra. Sem stub. Quem segue o link lê o canônico.
- Com `skills/` presente, o CLI descobre por essa pasta (local padrão) e **não** precisa da busca recursiva na raiz. Resultado: sete nomes, sem duplicata `vibe-init` + `skills/vibe-init`.

### 3. Claude Code

Arquivos:

- `.claude-plugin/marketplace.json` — marketplace `vibeflow`, um plugin `vibeflow`, `source: "./"`
- `.claude-plugin/plugin.json` — metadata + `skills` como array dos sete `./vibe-<nome>`

Comportamento:

- `/plugin marketplace add korflux/vibeflow` registra o catálogo.
- `/plugin install vibeflow@vibeflow` instala as sete skills. Invocação: `/vibe-init` etc.
- Campo `skills` no marketplace/plugin **substitui** o scan default de `skills/` (source é a raiz). Não listar `./skills/…`.

### 4. Codex

Arquivos:

- `.codex-plugin/plugin.json` — `name: vibeflow`, `skills: "./skills/"`
- `.agents/plugins/marketplace.json` — marketplace `vibeflow`, plugin `vibeflow`, `source.path: "./"`

Comportamento:

- `codex plugin marketplace add korflux/vibeflow`
- `codex plugin add vibeflow@vibeflow`
- Skills invocáveis por `@vibe-init` / nome da skill, sem slash alias extra.

### 5. Grok Build

Arquivos:

- `.grok-plugin/marketplace.json` — índice Grok, plugin `vibeflow`, source local `./`
- Opcional alinhado ao Claude: Grok também lê `.claude-plugin/`. O índice Grok existe para o comando nativo não depender só do compat.

Comportamento:

- `grok plugin marketplace add korflux/vibeflow`
- `grok plugin install vibeflow --trust`
- Plugin descobre `skills/` (via symlink → pacote). `/vibe-init` aparece no slash menu.

### 6. Antigravity

Arquivo:

- `plugin.json` na raiz (`name`, `version`, `description`). Skills no diretório `skills/` do plugin (esta raiz).

Comportamento:

- `agy plugin install https://github.com/korflux/vibeflow.git`
- Clone local: `agy plugin install ./vibeflow`
- Sem `commands/`. Sem `/plan` que colida com o comando interno do Antigravity.

### 7. Documentação e regras

- `README.md` abre com Quick Start de install (CLI + os quatro nativos, global vs projeto). Lista das skills permanece.
- `.vibeflow/REGRAS.md` (e portanto `AGENTS.md` / `CLAUDE.md`) ganha na **Estrutura** os paths de manifesto e `skills/`. Não vira segunda fonte de regras de produto.
- `docs/ESCOPO.md` marca distribuição como feito nesta rodada.
- Uma linha de install recomendado nos `docs/vibe-*/ARQUITETURA.md` deixa de falar só em `<grok-home>/skills/…` e aponta o README / `npx skills`. Sem reescrever o contrato de cada skill.

### Fora

- Mover `vibe-<nome>/` para `skills/vibe-<nome>/` — quebra o contrato do repo (Major)
- Aliases `/spec` `/plan` `/build` `/review` — decisão 2.Não; colidem com `/plan` do Antigravity
- Skill nova de install, hook, persona, MCP, LICENSE, publicação no diretório público da OpenAI
- Prometer os 70+ agentes do CLI além dos quatro; o comando genérico pode instalá-los, o README não os documenta um a um
- Copiar `SKILL.md` para `.claude/skills/` **deste** repo (aqui é a fonte, não um projeto consumidor)

## Checklist de entrega

### Aceite

- [x] A1: Outro usuário instala as sete skills no Grok, Claude, Codex e Antigravity, global ou local, sem copiar pasta na mão
- [x] A2: `/vibe-init` … `/vibe-review` continuam sendo os únicos slash names desta cadeia

### Critérios de sucesso

- [x] C1: `npx skills add <raiz-deste-repo> --list` devolve exatamente os sete `name`, sem duplicata
- [x] C2: Cada `skills/vibe-<nome>` é symlink git cujo alvo é `../vibe-<nome>` e o alvo contém `SKILL.md`
- [x] C3: Os quatro manifests (Claude marketplace+plugin, Codex plugin+marketplace, Grok marketplace, Antigravity `plugin.json`) são JSON válido e apontam as sete skills, sem `commands/`
- [x] C4: README contém os comandos CLI (`-g` e projeto) e os quatro installs nativos
- [x] C5: Suíte nova de contrato dos manifests passa no unittest local; CI existente ganha essa suíte se o workflow já coleta `docs/**/tests/`

## Implementação

### Stack

| Área | Escolha |
|---|---|
| Formato de skill | existente: Agent Skills (`SKILL.md` + frontmatter) |
| CLI de install | existente no ecossistema: `npx skills` (vercel-labs/skills). Não vendemos CLI próprio |
| Ponteiro | git symlink mode 120000, igual `AGENTS.md` |
| Dependências novas | Nenhuma |

### Estrutura tocada

```text
skills/vibe-*/                          # symlink → ../vibe-*
.claude-plugin/marketplace.json
.claude-plugin/plugin.json
.codex-plugin/plugin.json
.agents/plugins/marketplace.json
.grok-plugin/marketplace.json
plugin.json                             # Antigravity, raiz
README.md                               # Quick Start
.vibeflow/REGRAS.md                     # bloco Estrutura
docs/ESCOPO.md
docs/vibe-*/ARQUITETURA.md              # uma linha de install
docs/tests/test-distribuicao.py         # contrato dos manifests e ponteiros
.github/workflows/contrato.yml          # só se a suíte nova não for pega pelo glob atual
```

### Estilo e padrões

- reutilizar: JSON mínimo no estilo addyosmani/agent-skills; sem campo que este repo não usa
- reutilizar: teste `unittest`, pasta isolada só se o teste escrever; leitura do repo real é aceitável para manifesto versionado (são arquivos de contrato, não side-effect)
- sem Node nas suítes: não chamar `npx` na CI. C1 no teste = descoberta equivalente (sete `SKILL.md` únicos via `skills/`, frontmatter `name`)

### Contratos e módulos

- limites: script das skills `vibe-*` não muda; IA das skills não muda
- schema plugin: `name` kebab-case `vibeflow`; `version` `1.0.0`; `skills` paths relativos começando com `./`
- Claude `skills`: array `./vibe-init` … `./vibe-review` (ordem da cadeia)
- Codex `skills`: `"./skills/"`
- Grok source: `{ "type": "local", "path": "./" }` ou string `"./"`
- Codex marketplace `source.path`: `"./"`

## Como provar

### Seams

- CLI descobrir raiz `vibe-*` **e** `skills/` e listar 14 nomes. Mitigação: `skills/` no local padrão do CLI, teste C1 falha se houver duplicata de `name`
- Windows checkout com symlink falso (arquivo texto). Mitigação: teste C2 exige mode 120000 no git e alvo existente; README/REGRAS lembram Developer Mode
- Claude carregar `skills/` + `vibe-*`. Mitigação: manifest lista só `./vibe-*`, source raiz

### Estratégia

- Unitário: `docs/tests/test-distribuicao.py` (JSON, sete ponteiros, sete frontmatters, ausência de `commands/`, README contém as strings de comando)
- E2E de marketplace nos quatro CLIs: fora desta fatia (pede Claude/Codex/agy instalados). Manual opcional depois do merge
- `npx skills add . --list` uma vez na máquina de desenvolvimento, evidência no `implement.md`, não na CI

### Comandos

```bash
python docs/tests/test-distribuicao.py
npx --yes skills add . --list
```

## Boundaries

### Always

- Pacote canônico em `vibe-<nome>/`
- Sete skills no mesmo plugin
- JSON versionado e commitável
- Ponteiro verificado (alvo existe, contém `SKILL.md`)

### Ask first

- Publicar no diretório público da OpenAI / skills.sh listing pago
- Adicionar LICENSE
- Expor agentes além dos quatro no README

### Never

- Copiar `SKILL.md` para duas árvores
- Inventar `n` de fase
- Criar `commands/` de alias
- Disparar a cadeia no repo do consumidor
- Adicionar dependência npm no vibeflow

## Handoff

vibe-plan

- [x] Aprovação humana (leu o arquivo e confirmou)
