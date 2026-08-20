# vibeflow

A skill definitiva para VibeCoders.

Fonte canônica das skills `vibe-*` e do contrato `.vibeflow/`. Não é um app de produção.

## O que é o repositório

O vibeflow é a cadeia definitiva de skills para quem programa com agentes (Grok, Claude Code, Codex, Antigravity e qualquer cliente que leia `SKILL.md`): o pedido vira trilha no disco, não recap no chat.

Cada skill é um pacote instalável (`vibe-init/`, `vibe-interview/`, …) com `SKILL.md`, scripts e, quando precisa, templates e referências. No repo do consumidor, o trabalho da cadeia vive em disco:

```text
.vibeflow/REGRAS.md                         fonte única de regras do projeto
.vibeflow/phases/phase-N-slug/interview.md
.vibeflow/phases/phase-N-slug/spec.md
.vibeflow/phases/phase-N-slug/plan.md
.vibeflow/phases/phase-N-slug/analyze.md
.vibeflow/phases/phase-N-slug/implement.md
.vibeflow/phases/phase-N-slug/review.md
AGENTS.md  →  .vibeflow/REGRAS.md           symlink
CLAUDE.md  →  .vibeflow/REGRAS.md           symlink
```

`n` e o slug da pasta saem do script, não da IA. Skills seguintes do mesmo pedido gravam na mesma pasta, outro arquivo. Nenhuma skill dispara a próxima: o handoff é uma linha no artefato.

Escopo do produto: [`docs/ESCOPO.md`](docs/ESCOPO.md). Contrato de cada skill: `docs/vibe-<nome>/ARQUITETURA.md`. CI: [`.github/workflows/contrato.yml`](.github/workflows/contrato.yml).

## Como instalar as skills

Um comando instala as sete skills no Grok, Claude Code, Codex e Antigravity. O CLI [`skills`](https://github.com/vercel-labs/skills) aponta cada pacote `vibe-*` para o diretório de skills do agente.

```bash
# global (máquina do usuário)
npx skills add korflux/vibeflow -g -a grok -a claude-code -a codex -a antigravity -y

# só neste projeto (pode ir no git do consumidor)
npx skills add korflux/vibeflow -a grok -a claude-code -a codex -a antigravity -y
```

Windows sem symlink no destino: acrescente `--copy`.

Marketplace nativo, depois de clonar ou a partir do GitHub:

```text
/plugin marketplace add korflux/vibeflow
/plugin install vibeflow@vibeflow

codex plugin marketplace add korflux/vibeflow
codex plugin add vibeflow@vibeflow

grok plugin marketplace add korflux/vibeflow
grok plugin install vibeflow --trust

agy plugin install https://github.com/korflux/vibeflow.git
```

Depois disso os slash names são `/vibe-init` … `/vibe-review`. Não há alias `/spec` nem `/plan`.

Primeira vez num repo sem `.vibeflow/`: rode `/vibe-init`. As demais skills recusam sem isso.

## Desenho do fluxo das skills

O bloco de cadeia em `.vibeflow/REGRAS.md` escolhe o tamanho da rota. A IA não inventa atalho: o esforço manda quais portas existem.

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

O mesmo pedido reusa a pasta `phase-N-slug`. Pedido novo: próxima pasta, `n` numérico. Chat não substitui o arquivo quando a skill promete artefato.

## Por que usar as skills

Agentes de código otimizam o caminho curto: pulam spec, marcam tarefa sem prova, escolhem path, misturam regras do Claude com as do Codex, disparam a skill seguinte sozinhos.

Esta cadeia separa papéis e deixa o disco como fonte:

- **Script** inventaria, calcula `n` e slug, copia bytes, grava o relatório JSON.
- **IA** faz a semântica: pergunta, une prosa, preenche o template.
- **Humano** só decide o que o disco não resolve, e o que entra no git. Nenhuma skill commita.

Efeito prático: as regras do projeto ficam numa fonte (`.vibeflow/REGRAS.md`), o pedido deixa trilha (interview → spec → plan → implement → review), e “feito” exige comando e resultado, não recap no chat.

## O que cada skill faz

| Skill | Slash | Faz | Grava |
|---|---|---|---|
| [`vibe-init`](vibe-init/SKILL.md) | `/vibe-init` | Inicializa ou repara a fonte única de regras. `AGENTS.md` e `CLAUDE.md` viram symlink para `.vibeflow/REGRAS.md`. Une legado em vez de escolher um arquivo e descartar o outro | `.vibeflow/REGRAS.md`, ponteiros na raiz |
| [`vibe-interview`](vibe-interview/SKILL.md) | `/vibe-interview` | Fecha intenção ambígua: uma pergunta por vez, até haver sucesso observável e fora real | `phase-N-slug/interview.md` |
| [`vibe-spec`](vibe-spec/SKILL.md) | `/vibe-spec` | Grava o decidido. Comportamento, aceite, fora, como provar. Sem mural de user story | `phase-N-slug/spec.md` |
| [`vibe-plan`](vibe-plan/SKILL.md) | `/vibe-plan` | Fatia a spec em T* verificáveis, com deps reais, comando de verificação e checkpoint | `phase-N-slug/plan.md` |
| [`vibe-analyze`](vibe-analyze/SKILL.md) | `/vibe-analyze` | Cruza interview, spec e plan da mesma fase. Achado com path. Não edita os três | `phase-N-slug/analyze.md` |
| [`vibe-implement`](vibe-implement/SKILL.md) | `/vibe-implement` | Executa a fatia elegível com prova, marca `[x]` no plan (e A*/C*/R* quando a fatia prova) | `phase-N-slug/implement.md` |
| [`vibe-review`](vibe-review/SKILL.md) | `/vibe-review` | Julga o patch. Mesmo `review.md` em etapas. Não edita source da app | `phase-N-slug/review.md` |

Arquitetura, análise e testes de contrato de cada skill ficam em `docs/vibe-<nome>/` e **não** entram no pacote instalável.

## Estrutura do projeto

Este repo é a fonte. O consumidor instala o pacote, não a pasta `docs/`.

```text
vibeflow/
├── vibe-init/ … vibe-review/   pacote canônico (SKILL.md, scripts, templates, references)
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
5. Não inventar path de artefato fora de `.vibeflow/phases/phase-N-slug/`. Não copiar `REGRAS.md` para `AGENTS.md` / `CLAUDE.md`.
6. Relatórios `*-report.json` e `*-wip.md` ficam fora do git.

PR contra `main`. Mudança de contrato (path, schema do relatório, flag pública) é Major; o resto segue o semver em `.vibeflow/REGRAS.md`.

## Créditos

Minhas referências

- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)
- [github/spec-kit](https://github.com/github/spec-kit)
- [mattpocock/skills](https://github.com/mattpocock/skills)

## Autor

[Marco Kormoczi](https://github.com/korflux) · [@korflux](https://github.com/korflux)

## Licença

[MIT](LICENSE). Pode usar, copiar, modificar e redistribuir, com o aviso de copyright. Sem garantia.
