# vibeflow

A skill definitiva para VibeCoders.

Fonte canônica das skills `vibe-*` e do contrato `.vibeflow/`. Não é um app de produção.

## O que é o repositório

O vibeflow é a cadeia definitiva de skills para quem programa com agentes (Grok, Claude Code, Codex, Antigravity e qualquer cliente que leia `SKILL.md`): o pedido vira trilha no disco, não recap no chat.

Cada skill é um pacote instalável (`vibe-init/`, `vibe-interview/`, …) com `SKILL.md`, scripts e, quando precisa, templates e referências. No repo do consumidor, o trabalho da cadeia vive em disco:

```text
.vibeflow/REGRAS.md                         fonte única de regras do projeto
.vibeflow/mvp/                              baseline único de projeto novo na rota max
.vibeflow/phases/phase-N-slug/interview.md
.vibeflow/phases/phase-N-slug/spec.md
.vibeflow/phases/phase-N-slug/plan.md
.vibeflow/phases/phase-N-slug/analyze.md
.vibeflow/phases/phase-N-slug/implement.md
.vibeflow/phases/phase-N-slug/review.md
AGENTS.md  →  .vibeflow/REGRAS.md           symlink
CLAUDE.md  →  .vibeflow/REGRAS.md           symlink
```

`n` e o slug das phases saem do script, não da IA. Projeto novo classificado como MVP usa uma única `.vibeflow/mvp/`, sem número nem slug, e percorre a rota max completa. Skills seguintes do mesmo pedido gravam na mesma pasta, outro arquivo. Nenhuma skill dispara a próxima: o handoff é uma linha no artefato.

O `--apply` das skills de artefato executa os gates mecânicos e prepara o arquivo vivo somente quando ele ainda não existe. A IA escreve e atualiza a prosa diretamente em `interview.md`, `spec.md`, `plan.md`, `analyze.md`, `implement.md` e `review.md`; o conteúdo existente é preservado.

Escopo do produto: [`docs/ESCOPO.md`](docs/ESCOPO.md). Contrato de cada skill: `docs/vibe-<nome>/ARQUITETURA.md`. CI: [`.github/workflows/contrato.yml`](.github/workflows/contrato.yml).

## Como instalar as skills

O repositório oferece instalação por `npx skills` e manifests nativos. O pacote Antigravity tem `plugin.json` na raiz e descobre os oito pacotes pela pasta `skills/`; não há aliases em `commands/`.

### Instalador `npx skills`, project-local e global

O CLI [`skills`](https://github.com/vercel-labs/skills) usa, por padrão, o escopo project-local (`./<agent>/skills/`) e, com `-g`, o escopo global (`~/<agent>/skills/`). Os dois comandos abaixo instalam os oito pacotes nos agentes selecionados:

```bash
# project-local, somente neste projeto e compartilhável com a equipe
npx skills add korflux/vibeflow -a grok -a claude-code -a codex -a antigravity -y

# global, disponível em todos os projetos da máquina
npx skills add korflux/vibeflow -g -a grok -a claude-code -a codex -a antigravity -y
```

Windows sem suporte a symlink no destino: acrescente `--copy` ao comando escolhido. Use `npx skills list` para conferir a instalação.

### Antigravity IDE

Para um plugin específico do workspace, coloque a pasta do repositório em:

```text
<workspace-root>/.agents/plugins/vibeflow/
```

O fallback documentado pelo host é `_agents/plugins/`. Para uso global na IDE, coloque a pasta em:

```text
~/.gemini/config/plugins/vibeflow/
```

Em ambos os casos, `plugin.json` deve permanecer na raiz do plugin e `skills/` deve conter os oito diretórios com `SKILL.md`. Confirme a descoberta por `/skills` quando o host oferecer esse comando ou reabra o workspace/host para recarregar os plugins.

O `vibe-init` cria a regra de workspace em `.agents/rules/vibeflow.md` com a inclusão `@../../.vibeflow/REGRAS.md`. Esse arquivo é somente uma ponte curta. A fonte editável continua sendo `.vibeflow/REGRAS.md`.

Para skills avulsas sem o bundle de plugin, a IDE usa `.agents/skills/` no workspace e `~/.gemini/antigravity/skills/` globalmente.

### Antigravity CLI

O CLI instala o plugin no perfil global do Antigravity:

```text
agy plugin install https://github.com/korflux/vibeflow.git
agy plugin list
```

O pacote fica disponível em `~/.gemini/antigravity-cli/plugins/vibeflow/`. Para instalar um plugin local, passe o caminho da pasta ao mesmo comando, por exemplo `agy plugin install <caminho-do-plugin>`. O escopo project-local da IDE e o perfil global do CLI são caminhos diferentes.

Para skills avulsas sem o bundle de plugin, o CLI usa `.agents/skills/` no workspace e `~/.gemini/antigravity-cli/skills/` globalmente. Use o caminho de plugin quando precisar carregar o manifest e o conjunto completo do Vibeflow.

### Codex, regras globais e verificação de carga

Marketplace nativo, depois de clonar ou a partir do GitHub:

```text
/plugin marketplace add korflux/vibeflow
/plugin install vibeflow@vibeflow

codex plugin marketplace add korflux/vibeflow
codex plugin add vibeflow@vibeflow

grok plugin marketplace add korflux/vibeflow
grok plugin install vibeflow --trust
```

O Codex mantém suas regras globais em `~/.codex/AGENTS.md` ou `~/.codex/AGENTS.override.md`. O Antigravity mantém as regras globais em `~/.gemini/GEMINI.md`. Nenhum desses arquivos substitui `.vibeflow/REGRAS.md`, e o pacote não cria uma cópia `GEMINI.md` no workspace.

Quando um host puder carregar mais de um nome de regra, como `AGENTS.md` e `CLAUDE.md`, inspecione a carga efetiva com `grok inspect` ou a ferramenta equivalente do host. Se o slash command estiver disponível, `/skills` e `agy plugin list` são as confirmações mínimas para skills e plugins. Reiniciar ou reabrir o host é o fallback quando não houver comando de inspeção.

Depois da instalação, os slash names são `/vibe-init` … `/vibe-review`. Não há alias `/spec` nem `/plan`.

Primeira vez num repo sem `.vibeflow/`: rode `/vibe-init`. As demais skills recusam sem isso.

## Desenho do fluxo das skills

O bloco de cadeia em `.vibeflow/REGRAS.md` escolhe o esforço da rota. A IA não inventa atalho: o esforço manda quais portas existem.

```text
                         ┌────────────┐
                         │ vibe-init  │  repo sem .vibeflow, ou disco quebrado
                         └─────┬──────┘
                               │
     pedido ──► esforço ───────┼──────────────────────────────►
                               │
          low                  │  implement
          medium               │  implement → review
          high                 │  spec → plan → implement → review
          xhigh                │  interview → spec → plan → implement → review
          max                  │  interview → spec → plan → analyze → implement → review
```

| Esforço | Fluxo | Quando |
|---|---|---|
| (init) | init | Primeira vez no repo, ou disco quebrado. De novo só para reparar |
| low | implement | Pedido claro, direto, simples |
| medium | implement → review | Pedido claro e direto, sem possibilidade de regressão |
| high | spec → plan → implement → review | Pedido claro, execução difícil, ou possibilidade de regressão |
| xhigh | interview → spec → plan → implement → review | Pedido ambíguo, confiança baixa, intenção ou sucesso em aberto |
| max | interview → spec → plan → analyze → implement → review | Auth, pagamento, segredo, perda de dados, produção ou alto blast radius |

Esforço da rota e `Size` da task são dimensões diferentes. A rota define o rigor da cadeia para o pedido; cada T* recebe `low`, `medium` ou `high` por um score de complexidade, e uma rota `high` pode conter tasks `low` ou `medium`. A matriz canônica e o limite de quebra ficam em [`vibe-plan/SKILL.md`](vibe-plan/SKILL.md).

Todo MVP de projeto novo usa a rota `max` em `.vibeflow/mvp/`. Feature chamada de MVP dentro de produto existente continua usando uma phase normal. Depois de concluído, o baseline não é sobrescrito; pivôs e reconstruções posteriores entram como phase `max`.

O mesmo pedido reusa a pasta `phase-N-slug`. Pedido novo: próxima pasta, `n` numérico. Chat não substitui o arquivo quando a skill promete artefato.

### Handoff e isolamento de chat

`init → interview → spec` pode continuar no mesmo chat. As portas `plan`, `analyze`, `implement` e `review` recomendam um novo chat para reduzir contexto residual; na implementação, a recomendação é um chat focado por T*. A continuidade é permitida quando o humano a escolhe conscientemente. O artefato vivo e a linha de handoff são a ponte verificável entre chats.

Cada `T*` é executada, testada e commitada isoladamente. O commit da task não faz push. Depois de Approve na review, confirmação humana e correções fechadas, o handoff final valida a phase, cria o commit residual quando necessário e faz `git push` para o upstream atual, sem force.

No Codex desktop, a prova de UI prioriza o navegador integrado quando disponível. Se ele não estiver disponível, registre a limitação no resultado ou use o fallback visual existente no projeto.

## Por que usar as skills

Agentes de código otimizam o caminho curto: pulam spec, marcam tarefa sem prova, escolhem path, misturam regras do Claude com as do Codex, disparam a skill seguinte sozinhos.

Esta cadeia separa papéis e deixa o disco como fonte:

- **IA** pilota a run: entende o pedido, investiga o projeto e os scripts, decide a semântica e audita o resultado.
- **Skill** orienta a IA com invariantes, gates e critérios de fechamento.
- **Script** auxilia operações determinísticas como inventário, path, número, slug, preparação do alvo e relatório.
- **Humano** decide apenas o que muda materialmente o resultado e confirma o fechamento. `vibe-implement` commita cada task verde; `vibe-review` faz o commit/push final da phase somente após Approve confirmado.

Efeito prático: as regras do projeto ficam numa fonte (`.vibeflow/REGRAS.md`), o pedido deixa trilha (interview → spec → plan → implement → review), e “feito” exige comando e resultado, não recap no chat.

## O que cada skill faz

| Skill | Slash | Faz | Grava |
|---|---|---|---|
| [`vibe-init`](vibe-init/SKILL.md) | `/vibe-init` | Inicializa ou repara a fonte única de regras. `AGENTS.md` e `CLAUDE.md` viram symlink para `.vibeflow/REGRAS.md`; `.agents/rules/vibeflow.md` vira uma inclusão mínima para Antigravity. Une legado em vez de escolher um arquivo e descartar o outro | `.vibeflow/REGRAS.md`, ponteiros e adaptador de host |
| [`vibe-interview`](vibe-interview/SKILL.md) | `/vibe-interview` | Fecha intenção ambígua e inicia descoberta adaptativa de projeto MVP quando aplicável | `phase-N-slug/interview.md` ou `.vibeflow/mvp/interview.md` |
| [`vibe-spec`](vibe-spec/SKILL.md) | `/vibe-spec` | Grava o decidido. Comportamento, aceite, fora, como provar. Sem mural de user story | `phase-N-slug/spec.md` |
| [`vibe-design`](vibe-design/SKILL.md) | `/vibe-design` | Desenha a apresentação com dois modos de entrada e três usos, sem código nem imagem final | `phase-N-slug/design.md` |
| [`vibe-plan`](vibe-plan/SKILL.md) | `/vibe-plan` | Fatia a spec em T* verificáveis, com deps reais e comando de verificação por task | `phase-N-slug/plan.md` |
| [`vibe-analyze`](vibe-analyze/SKILL.md) | `/vibe-analyze` | Cruza interview, spec e plan da mesma fase. Corrige lacunas óbvias em `spec.md` e `plan.md`; grava o certificado no vivo | `phase-N-slug/analyze.md` |
| [`vibe-implement`](vibe-implement/SKILL.md) | `/vibe-implement` | Executa a T* elegível, prova, marca `[x]` e cria o commit isolado da task | `phase-N-slug/implement.md` |
| [`vibe-review`](vibe-review/SKILL.md) | `/vibe-review` | Julga o patch, conduz correções e faz o commit/push final após aprovação | `phase-N-slug/review.md` |

Arquitetura, análise e testes de contrato de cada skill ficam em `docs/vibe-<nome>/` e **não** entram no pacote instalável.

## Estrutura do projeto

Este repo é a fonte. O consumidor instala o pacote, não a pasta `docs/`.

```text
vibeflow/
├── vibe-init/ … vibe-review/   pacote canônico (SKILL.md, scripts, templates, references, com vibe-design entre spec e plan)
├── skills/vibe-*               symlink → ../vibe-* (descoberta do CLI e plugins)
├── .claude-plugin/             marketplace Claude
├── .codex-plugin/              plugin Codex
├── .agents/plugins/            marketplace Codex
├── .grok-plugin/               marketplace Grok
├── plugin.json                 plugin Antigravity
├── docs/vibe-<nome>/           ARQUITETURA.md, ANALISE.md, tests/ (não instala)
├── docs/ESCOPO.md              feito e fila
├── docs/tests/                 contrato de distribuição e harness dos launchers
├── .vibeflow/REGRAS.md         regras deste repo (fonte viva)
├── AGENTS.md, CLAUDE.md        symlink → .vibeflow/REGRAS.md
└── LICENSE
```

Pacote de uma skill:

```text
vibe-<nome>/
  SKILL.md
  scripts/<nome>.py .ps1 .sh
  templates/<artefato>.md      se a skill grava markdown
  references/                  catálogo sob demanda
```

## Como contribuir

1. Skill nova só com o par `docs/vibe-<nome>/ARQUITETURA.md` + `ANALISE.md` antes de `SKILL.md` e scripts.
2. Scripts em trio, mesmo contrato: `.py` (motor), `.ps1` (Windows), `.sh` (launcher Unix).
3. Teste de contrato em `docs/vibe-<nome>/tests/`, `unittest`, pasta isolada. Depois: `python docs/vibe-<nome>/tests/test-<nome>.py -v`.
4. Distribuição: `python docs/tests/test-distribuicao.py -v`.
5. Não inventar path de artefato fora de `.vibeflow/phases/phase-N-slug/`; a única exceção é o baseline fixo `.vibeflow/mvp/`. Não copiar `REGRAS.md` para `AGENTS.md` / `CLAUDE.md`.
6. Relatórios `*-report.json` ficam fora do git; os artefatos vivos entram no git.

PR contra `main`. Mudança de contrato (path, schema do relatório, flag pública) é Major; o resto segue o semver em `.vibeflow/REGRAS.md`.

## Créditos

- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)
- [dietrichgebert/ponytail](https://github.com/dietrichgebert/ponytail)
- [github/spec-kit](https://github.com/github/spec-kit)
- [mattpocock/skills](https://github.com/mattpocock/skills)

## Autor

[Marco Kormoczi](https://github.com/korflux) · [@korflux](https://github.com/korflux)

## Licença

[MIT](LICENSE). Pode usar, copiar, modificar e redistribuir, com o aviso de copyright. Sem garantia.
