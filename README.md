# vibeflow

A skill definitiva para VibeCoders.

Skill única `vibeflow`, com um coordenador-líder que conduz o trabalho de agentes num repo. Este repositório é a fonte canônica do pacote e do contrato `.vibeflow/`. Não é um app de produção.

## O que é

O vibeflow é uma skill para quem programa com agentes (Grok Build, Claude Code, Codex, OpenCode, Pi, Antigravity e qualquer cliente que leia `SKILL.md`). Ela roda só quando você a chama. O líder conversa com você, entende o projeto, escolhe uma rota proporcional ao pedido, planeja e delega a execução a subagentes: redação de artefatos, código, testes e provas. O líder confere cada entrega, marca o progresso e faz os commits; código e teste ficam sempre com os subagentes. Analyze, checkpoints e review são feitos em contexto limpo. O pedido vira trilha no disco, não recap no chat.

O pacote é `SKILL.md`, referências por etapa, templates, perfis de subagente e um script de leitura em Node (`estado`), sem dependências. No repo do consumidor, o trabalho vive em disco:

```text
AGENTS.md                                  fonte única de regras do projeto
.agents/rules/vibeflow.md                  ponte Antigravity para AGENTS.md
.vibeflow/phases/phase-N-slug/spec.md      gravada pela interview; única aprovação antes do código
.vibeflow/phases/phase-N-slug/plan.md      checklist de passos, com os achados do analyze no fim
.vibeflow/phases/phase-N-slug/review.md
.vibeflow/mvp/                             baseline único de projeto novo, rota high com risco
```

O estado vem das linhas `# Rota:`, `# Risco:` e `# Status:`, das caixas de passos e checkpoints do `plan.md`, dos R* do `review.md` e do Git. Um chat novo com `/vibeflow` retoma de onde a phase parou.

## Como instalar

### Instalador `npx skills`, project-local e global

O CLI [`skills`](https://github.com/vercel-labs/skills) usa, por padrão, o escopo project-local (`./<agent>/skills/`) e, com `-g`, o escopo global (`~/<agent>/skills/`):

```bash
# project-local, somente neste projeto e compartilhável com a equipe
npx skills add korflux/vibeflow -a grok -a claude-code -a codex -a antigravity -y

# global, disponível em todos os projetos da máquina
npx skills add korflux/vibeflow -g -a grok -a claude-code -a codex -a antigravity -y
```

Windows sem suporte a symlink no destino: acrescente `--copy` ao comando escolhido. Use `npx skills list` para conferir a instalação.

OpenCode e Pi também descobrem skills globais em `~/.agents/skills/`. Uma cópia atualizada do pacote nesse diretório atende aos dois CLIs; se houver cópias em `~/.config/opencode/skills/` ou `~/.pi/agent/skills/`, mantenha-as sincronizadas ou remova a duplicação.

### Antigravity

IDE, plugin do workspace: coloque a pasta do repositório em `<workspace-root>/.agents/plugins/vibeflow/` (fallback documentado pelo host: `_agents/plugins/`). Uso global na IDE: `~/.gemini/config/plugins/vibeflow/`. Em ambos os casos, `plugin.json` fica na raiz do plugin e `skills/vibeflow/` contém o `SKILL.md`. Confirme a descoberta por `/skills` ou reabra o workspace.

CLI, perfil global:

```text
agy plugin install https://github.com/korflux/vibeflow.git
agy plugin list
```

O pacote fica em `~/.gemini/antigravity-cli/plugins/vibeflow/`. Para um plugin local, passe o caminho da pasta ao mesmo comando.

### Regras globais e verificação de carga

O Codex mantém regras globais em `~/.codex/AGENTS.md` ou `~/.codex/AGENTS.override.md`, e o Antigravity em `~/.gemini/GEMINI.md`. Nenhum desses arquivos substitui `AGENTS.md`, e a skill não cria `GEMINI.md` no workspace. Quando um host puder carregar mais de um nome de regra, inspecione a carga efetiva com `grok inspect` ou a ferramenta equivalente do host; reiniciar ou reabrir o host é o fallback.

## Como usar

A skill não entra sozinha. No Claude Code, chame `/vibeflow`; no Codex, `$vibeflow`. Nos demais hosts, chame `/vibeflow`. Fora dessa chamada, o agente trabalha direto pelas regras do `AGENTS.md`, sem rota, phase nem artefato.

| Comando | Faz |
|---|---|
| `/vibeflow` | Lê o disco, retoma a phase aberta ou classifica o pedido novo e anuncia a rota e as etapas |
| `/vibeflow <etapa> [pedido]` | Vai direto a `init`, `interview`, `spec`, `plan`, `analyze`, `implement` ou `review`, se o pré-requisito estiver satisfeito; o resto do texto é o pedido |
| `/vibeflow <pedido>` | Texto que não começa por uma etapa é tratado como pedido e classificado |

Primeira vez num repo: a etapa `init` roda antes da primeira rota com phase. Ela grava `AGENTS.md`, a ponte `.agents/rules/vibeflow.md` e guarda cópia conferida de arquivo substituído em `.vibeflow/old/`, com um commit local. Na primeira vez na máquina, instala também os cinco perfis de subagente (explorador, implementador, redator, verificador e revisor) em nível global, em `~/.claude/agents/` e `~/.codex/agents/`; perfil customizado nunca é sobrescrito sem a sua decisão, e um perfil no projeto prevalece sobre o global. Um `CLAUDE.md` existente não é removido. Quando os perfis mudam, recarregue o host antes de continuar.

A rota é proporcional ao pedido:

| Rota | Etapas |
|---|---|
| `low` | implement direto, com prova proporcional, sem criar `.vibeflow/` |
| `medium` | implement e review |
| `high` | interview, spec, plan, analyze, implement com checkpoints e review |

Na `high`, a linha `# Risco:` marca mudanças que tocam autenticação, autorização, pagamento, segredo, perda de dados ou produção; ela não acrescenta etapa, mas aprofunda a interview, os checkpoints e a review. A aprovação da `spec.md` é a única antes do código: com ela, o líder segue até a review sem pedir outras aprovações. A tabela de rotas fica no `AGENTS.md` que a etapa `init` grava no projeto, a partir de [`skills/vibeflow/templates/AGENTS.md`](skills/vibeflow/templates/AGENTS.md).

Por padrão, um único chat conduz a rota inteira. Em host de contexto curto, use um chat para o planejamento e outro para a implementação. Em host sem subagentes, ou sem os perfis carregados, a skill avisa e roda uma etapa ou um passo por vez, com analyze, checkpoint e review em chat novo.

Durante a phase, o líder informa o progresso em percentual, calculado pelas etapas e pelos passos concluídos no disco, a cada etapa, checkpoint e commit.

### Scripts de leitura

Com Node 18 ou superior, a skill usa os scripts da pasta `scripts/`, sempre na raiz do repo. Eles só leem o disco e o Git, nunca escrevem, fazem staging ou commit, e funcionam em Windows e Linux. Cada um acelera uma regra já escrita nas referências; quando divergem, vale a regra escrita. Sem Node, a skill segue as regras escritas. Todos aceitam `--json` e saem com 0 sem achado, 1 com achado e 2 em erro de uso.

| Script | Quem roda e quando | O que confere |
|---|---|---|
| `estado.mjs [--alvo phase-N\|mvp] [--slug "<frase>"] [--linha]` | Líder, ao abrir e retomar | Alvo padrão, rota, risco, status dos artefatos, etapa atual, progresso, próximo passo ou grupo paralelo, R* abertos, push pendente, inconsistências e o path da próxima phase; `--slug` normaliza a frase do slug e `--linha` imprime só a linha de progresso |
| `conferir.mjs --passo <IDs>` | Líder, ao receber um passo ou um R* | Alterações não commitadas fora dos `Arquivos:` do passo ou do path do R* |
| `conferir.mjs --commit "<mensagem>"` | Líder, depois do staging e antes de cada commit | Formato da mensagem, ausência de `Co-Authored-By`, critérios de aceite no corpo do `task(medium): ...`, caixas e R* marcados no índice contra os IDs, paths em staging contra o recorte e `git diff --cached --check` |
| `plan.mjs [--alvo phase-N\|mvp]` | Líder depois de gravar o plan; revisor no analyze | Forma dos passos e checkpoints, critérios inexistentes ou sem passo, seções obrigatórias e placeholder de template esquecido |
| `plan.mjs --spec [--alvo phase-N\|mvp]` | Líder antes de apresentar a spec para aprovação | Seções obrigatórias da spec, decisão sem pergunta ou motivo, critério repetido, adjetivo vago no critério e placeholder esquecido |
| `governanca.mjs` e `governanca.mjs --backup <original> <cópia>` | Líder no init | `AGENTS.md` e bloco da cadeia, ponte, `.gitkeep`, perfis globais contra a fonte, perfil `corretor` obsoleto, perfis de projeto customizados; no modo `--backup`, tamanho e SHA-256 da cópia |

### Apoios opcionais do host

A skill não instala estes apoios. Eles reforçam as regras sem conduzir nada, e você decide se os adota.

**Hook `commit-msg` do Git (qualquer host).** Barra o commit cuja mensagem ou cujo índice fogem do contrato. Ele vale para todo commit do repo, inclusive os seus feitos à mão, então use só em repo em que todo commit passa pela skill. Em `.git/hooks/commit-msg`:

```sh
#!/bin/sh
node "<pasta da skill>/scripts/conferir.mjs" --commit-arquivo "$1"
```

**Bloqueios no Claude Code.** No `.claude/settings.json` do projeto, regras `deny` impedem os comandos que o contrato proíbe. Elas casam o comando como foi escrito, então são uma rede de segurança, não uma garantia:

```json
{
  "permissions": {
    "deny": [
      "Bash(git add -A*)", "Bash(git add --all*)", "Bash(git add .)", "Bash(git add . *)",
      "Bash(git commit --amend*)", "Bash(git commit * --amend*)",
      "Bash(git push --force*)", "Bash(git push -f*)", "Bash(git push * --force*)"
    ]
  }
}
```

**Statusline no Claude Code.** Mostra a linha de progresso da phase abaixo do prompt e fica vazia em repo sem `.vibeflow/`. No `settings.json` do usuário ou do projeto (no Windows, a statusline roda pelo Git Bash):

```json
{
  "statusLine": { "type": "command", "command": "node <pasta da skill>/scripts/estado.mjs --linha || true" }
}
```

Aprovar a review, publicar decisões vigentes e fazer push sempre exigem a sua confirmação.

## Novidades da 5.3.0

A 5.3.0 é uma versão minor, sem migração. Rode `/vibeflow init` para atualizar os perfis globais de subagente.

- Critérios de aceite com forma fixa (contexto, ação e resultado observável), critério de falha quando há entrada externa, autorização ou dinheiro, tabela de exemplos para cálculo exato e critério de preservação do que já funciona.
- `plan.mjs --spec` confere a forma da spec antes da aprovação, inclusive adjetivo vago no critério.
- Testes com vermelho antes do verde: o teste do critério falha antes da mudança e passa depois, com as duas execuções no relatório.
- Nova seção Desenho de casos em `references/testes.md`: limites, classes, transições, autorização, mock só na fronteira e determinismo.
- Na rota medium, os critérios do brief vão no corpo do commit `task(medium): ...`, e a review os lê de lá; `conferir.mjs` acusa o commit sem eles.
- O plan começa pelo caminho mais fino de ponta a ponta ou pela suposição mais arriscada.
- O perfil revisor sobe para esforço alto nos dois hosts.

## Novidades da 5.2.0

A 5.2.0 é uma versão minor, sem migração.

- Três scripts de leitura novos apoiam o líder e o revisor sem conduzir etapa: `conferir.mjs` (recorte do passo e conferência antes do commit), `plan.mjs` (forma do plan e cobertura dos critérios) e `governanca.mjs` (resultado do init e backup).
- O `estado.mjs` ganhou `--slug`, que aplica a regra do slug, e `--linha`, para a statusline.
- O init passa a tratar como idêntico o perfil global que difere da fonte só na quebra de linha (CRLF ou LF) ou no BOM.
- Hook `commit-msg`, bloqueios e statusline do Claude Code ficam documentados como apoios opcionais.

## Novidades da 5.1.0

A 5.1.0 é uma versão minor, sem migração.

- As regras de teste ficam numa referência única, `skills/vibeflow/references/testes.md`.
- Os testes locais preferem serviços nativos ou embutidos a containers; em projeto que já usa Docker nos testes, o líder pergunta uma vez se você prefere migrar para uma forma mais leve.
- O E2E é leve e roda em paralelo.
- A regressão completa tem orçamento de duração, de 10 minutos por padrão; acima dele, o revisor registra um alarme sem bloquear a entrega.

## Migração para a 5.0.0

A 5.0.0 é uma versão major: muda artefatos, rotas e papéis.

- Phases fechadas no formato antigo (com `interview.md`, `design.md`, `analyze.md`, rotas `xhigh` ou `max`, ou tasks `T*`) ficam como estão e são reconhecidas como fechadas.
- Uma phase aberta no formato antigo deve ser fechada com a versão anterior da skill antes de atualizar; a 5.0.0 a relata como inconsistência e não a conduz.
- O perfil global `corretor` de versões anteriores é relatado pelo init como obsoleto e preservado; removê-lo exige a sua decisão.

## Estrutura do repositório

```text
vibeflow/
├── skills/vibeflow/      pacote instalável (SKILL.md, agents/, references/, templates/, scripts/)
├── tests/scripts/        testes dos scripts (não instala)
├── plugin.json           plugin Antigravity
├── AGENTS.md             regras deste repo (fonte viva)
└── LICENSE
```

## Como contribuir

1. Contrato antes de prosa: mudança de disco começa em `skills/vibeflow/references/disco.md`.
2. Scripts só leem, usam Node 18+ sem dependências e têm teste em `tests/scripts/` (`node --test`). Não adicione testes de presença de texto.
3. Antes do push, rode a revisão de consistência e a varredura de segredos descritas em `AGENTS.md`. O repositório não usa CI no GitHub, por decisão de custo.
4. `AGENTS.md` é a única fonte de regras do projeto. Artefatos só em `.vibeflow/phases/phase-N-slug/` ou no baseline `.vibeflow/mvp/`.

PR contra `main`. Mudança de contrato (path de artefato ou comportamento que o humano já usa) é Major; o resto segue o semver em `AGENTS.md`.

## Créditos

- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)
- [dietrichgebert/ponytail](https://github.com/dietrichgebert/ponytail)
- [emilkowalski/skills](https://github.com/emilkowalski/skills)
- [github/spec-kit](https://github.com/github/spec-kit)
- [mattpocock/skills](https://github.com/mattpocock/skills)

## Autor

[Marco Kormoczi](https://github.com/korflux) · [@korflux](https://github.com/korflux)

## Licença

[MIT](LICENSE). Pode usar, copiar, modificar e redistribuir, com o aviso de copyright. Sem garantia.
