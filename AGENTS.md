# Regras do projeto

> VibeFlow: documentos e edição apenas de texto ficam fora das etapas spec, design, plan, analyze, implement e review da skill única `vibeflow`. Essas etapas tratam código de software. A etapa interview pode esclarecer um briefing ambíguo de documento.

<!-- VIBEFLOW:CADEIA start -->
| esforço | fluxo | quando |
|---|---|---|
| N/A | init | primeira vez no repo, ou disco quebrado, de novo só para reparar |
| low | implement | mudança simples de código de software sem comportamento novo, como cor, texto ou layout de página estática |
| Express | implement, sem phase nem artefato | low sem phase de origem: mudança clara e localizada sem comportamento novo |
| medium | implement → review | pedido claro e direto, com comportamento novo pequeno e sem regressão de backend, ou página visual cujo aceite dependa de validação renderizada |
| high | spec → plan → implement → review | pedido claro de execução difícil, ou mudança que altera banco, painel admin ou cria risco de regressão de backend |
| xhigh | interview → spec → plan → implement → review | pedido ambíguo, confiança baixa, intenção ou sucesso de software em aberto |
| max | interview → spec → plan → analyze → implement → review | mudança que altera autenticação, autorização, pagamento, segredo, risco de perda de dados, produção, alto blast radius ou baseline MVP de software |

No Express, o implementador entrega com prova proporcional, sem init, `.vibeflow/`, phase nem artefato. Saem do Express, seguindo a rota aplicável: comportamento, rota, interação, critério de aceite ou acessibilidade alterados, e mudanças que toquem privacidade, dado pessoal, consentimento, retenção, direitos, obrigação jurídica, autenticação, autorização, pagamento, segredo, persistência ou risco de perda de dados. Ajuste low ou medium ao que uma phase entregou ou está entregando, inclusive registro de `.erros-encontrados/`, volta à phase de origem, mesmo fechada, sem abrir phase nova. Medium segue implement → review e abre a phase na review.

`/vibeflow` conduz todo o fluxo. `/vibeflow <etapa>` vai direto a `init`, `interview`, `spec`, `design`, `plan`, `analyze`, `implement` ou `review`, desde que o pré-requisito esteja satisfeito. Argumento cuja primeira palavra não é etapa é tratado como pedido e classificado. O design entra entre spec e plan somente com UI nova: tela ou decisão visual que o design system e as telas existentes não cobrem.

### Continuidade entre chats

Um único chat conduz a phase por padrão. Em host de contexto curto, use dois: um para todo o planejamento (interview, spec, design, plan e analyze) e outro para a implementação (implement e review). Quando o contexto pesar ou o humano pedir para parar, o estado é gravado conforme a seção 6 do `SKILL.md` e o líder recomenda um chat novo. A retomada parte do disco: em chat novo, `/vibeflow` lê as linhas `# Status:`, as caixas e as linhas `Estado:` do `plan.md` e o Git e segue de onde parou. Sem subagentes, analyze e review pedem chat novo (`/vibeflow analyze`, `/vibeflow review`). Separar chats é recomendação, nunca gate.
<!-- VIBEFLOW:CADEIA end -->

A skill `vibeflow` é texto mais scripts de leitura em `skills/vibeflow/scripts/`. A prova de uma mudança na prosa é a revisão de consistência e o uso real; a de um script é `node --test`.

## Projeto

Skill única `vibeflow`, conduzida por um coordenador-líder, para inicializar e conduzir o trabalho de agentes num repo. Este repositório é a fonte canônica do pacote `skills/vibeflow/` e do contrato `.vibeflow/`. Não é um app de produção.

## Comandos do projeto

- Este repositório não usa CI no GitHub, por decisão de custo. Não envie branch só para disparar CI. A regressão completa e a varredura de segredos rodam localmente antes do push.
- Regressão completa local: revisão de consistência de todos os arquivos alterados. Todo path deste repo citado em `skills/vibeflow/`, `README.md` e `AGENTS.md` existe (paths do projeto consumidor, como `.agents/rules/`, `.claude/agents/`, `.codex/agents/` e `.vibeflow/mvp/`, ficam fora); nenhum arquivo cita a v1 do VibeFlow ou registro estruturado de execução; `node --test` passa; `git diff --check` não acusa achado.
- Testes dos scripts: `node --test` na raiz (Node 18+), que descobre `tests/**/*.test.mjs`.
- Varredura de segredos local: `gitleaks detect --source . --redact --no-banner`.

## Fluxos e invariantes

- A IA interpreta intenção, aplica as regras mecânicas escritas e escreve a prosa dos artefatos vivos; o disco e o Git são a fonte do estado.
- As fases vivem em `.vibeflow/phases/phase-N-slug/`; o baseline único de software novo vive em `.vibeflow/mvp/`.
- O init guarda em `.vibeflow/old/`, com tamanho e hash conferidos, o `AGENTS.md`, a ponte ou o perfil que substitui sem backup em commit.

## Ambiente

homolog

Este repo não tem banco, migration nem tráfego de usuário. Skills aqui mudam contrato de agente, não schema de produção.

## Versão (semver)

- **Major:** quebra contrato (path ou nome de artefato, linha de cabeçalho como `# Status:` ou `# Rota:`, comportamento do líder que o humano já usa).
- **Minor:** adiciona sem quebrar (nova seção opcional no artefato, nova referência de etapa).
- **Patch:** correção sem mudança de contrato.
- Produção: migration só com plano de rollback; não rodar migration destrutiva sem o humano pedir.

## Git

- Sem `Co-Authored-By` de ferramenta em commit/push.
- Staging somente de paths autorizados. Nunca usar `git add -A`, `git add .`, amend, squash ou force push.
- Papéis, ondas, provas, formatos de commit e finalização seguem a skill `vibeflow` (`skills/vibeflow/references/disco.md`, Commits).
- Aprovar a review, publicar decisões vigentes e fazer push exigem confirmação humana final explícita.
- Commitável: `AGENTS.md`, `.vibeflow/old/` se existir, `.vibeflow/phases/` (`.gitkeep` e artefatos vivos), `.vibeflow/mvp/` e o pacote da skill.
- `AGENTS.md` é a fonte editável na raiz. O init não cria `CLAUDE.md`.

## Estrutura

```
AGENTS.md                    fonte viva das regras
.vibeflow/phases/            artefatos da cadeia (phase-N-slug/)
.vibeflow/old/               backups do init, se houver
.vibeflow/mvp/               contrato: baseline único de um projeto novo na rota max
skills/vibeflow/             pacote canônico da skill, pasta real
tests/scripts/               testes dos scripts, fora do pacote instalável
plugin.json                  plugin Antigravity (raiz)
README.md                    instalação e uso
```

Pacote da skill:

```
skills/vibeflow/
  SKILL.md
  references/<etapa>.md        uma referência por etapa, com catálogos em references/<etapa>/
  references/disco.md          regras mecânicas do disco
  references/delegation.md     papéis, brief e relatório fixo
  templates/<artefato>.md      esqueleto de cada artefato vivo
  templates/AGENTS.md          modelo de regras do projeto consumidor
  templates/agents/<host>/     perfis de subagente por host
  scripts/_disco.mjs           leitura compartilhada do disco e do Git
  scripts/estado.mjs           estado, etapa atual e progresso da phase
  scripts/ondas.mjs            próxima onda e sobreposição de Arquivos:
```

### Adaptadores por host

A fonte editável é sempre `AGENTS.md` na raiz. No projeto consumidor, o Antigravity recebe somente a ponte mínima descoberta pelo workspace, `.agents/rules/vibeflow.md`, com `@../../AGENTS.md`; o init cria, verifica e repara esse arquivo sem copiar as regras.

As regras globais permanecem separadas das regras do workspace: Codex usa `~/.codex/AGENTS.md` ou `~/.codex/AGENTS.override.md`, e Antigravity usa `~/.gemini/GEMINI.md`. O Vibeflow não sincroniza nem sobrescreve esses arquivos e não cria `GEMINI.md` no projeto. Se o host carregar mais de um nome, a carga efetiva deve ser conferida na ferramenta do próprio host.

## Regras deste repo

Estas regras mantêm a skill única coerente a cada mudança. O contrato de disco vive em `skills/vibeflow/references/disco.md`. Aqui vive só o que vale para qualquer mudança no repo.

### 1. Pacote

- Um único pacote instalável: `skills/vibeflow/`, pasta real, sem symlink.
- Texto (`SKILL.md`, `references/` e `templates/`) mais `scripts/`, nas regras da seção 4. Testes ficam em `tests/`, fora do pacote.
- Install: `npx skills add korflux/vibeflow` (projeto ou `-g`) nos agentes `grok`, `claude-code`, `codex`, `antigravity`, ou o plugin Antigravity descrito no `README.md`.
- Não criar segunda skill nem alias de comando. Etapa nova entra como referência da skill única.

### 2. Disco: uma fonte, uma pasta de fase, um arquivo por etapa

```
AGENTS.md
.vibeflow/mvp/<artefato>.md
.vibeflow/phases/phase-<n>-<slug>/<artefato>.md
```

- Projeto novo classificado pela IA como MVP usa uma única pasta fixa `.vibeflow/mvp/` e percorre obrigatoriamente `interview`, `spec`, `plan`, `analyze`, `implement` e `review`.
- O modo MVP não usa `n` nem slug.
- Só existe um baseline MVP por repositório. Depois de concluído, ele não é sobrescrito, movido nem versionado; pivô ou reconstrução integral entra como phase `max`.
- `n` inteiro crescente, sem zero à esquerda, ordem **numérica**: maior existente mais 1. A IA aplica a regra e não inventa `n`.
- `slug`: frase curta da fase, `a-z0-9` e hífen, 2 a 48 caracteres.
- As regras mecânicas completas moram em `skills/vibeflow/references/disco.md`.
- Pasta da fase agrupa o pedido. Etapas seguintes gravam **na mesma pasta**, outro arquivo.
- Nome do arquivo é o tipo, não o título: `interview.md`, `spec.md`, `design.md`, `plan.md`, `analyze.md`, `review.md`.
- A rota fica em `# Rota:` no cabeçalho do primeiro artefato da phase (`interview.md` em xhigh, max e MVP; `spec.md` em high; `review.md` em medium) e não muda. Plans não levam `# Protocolo:` nem `# Modo:`; o modo é decidido na run.
- Não gravar cadeia em `docs/`, na raiz, nem em path de outro produto.
- O artefato vivo nasce da forma do template somente quando ausente. Conteúdo existente é editado no lugar, nunca recriado.
- Continuar o mesmo pedido: editar o vivo. Pedido novo: próxima pasta. Não renomear pasta depois de criada.
- Sem `.vibeflow/` numa rota com phase (medium ou acima, e MVP): a primeira etapa é `init`.

### 3. Papéis na run

```
Líder (IA)        →  conversa com o humano, entende o pedido e o projeto, classifica a rota, planeja, delega, critica, reconhece e decide
Analistas         →  explorador, redator, implementador, verificador, corretor, revisor e finalizador executam o micro
Skill (SKILL.md)  →  orienta com invariantes, sequência, gates e critérios de fechamento
Humano            →  decide apenas o que muda materialmente o resultado e não pode ser concluído pelo contexto
```

A IA não inventa path contratual, número ou fato que o disco e o humano não sustentam, nem "melhora" texto que o humano ditou para um SLOT.

A IA audita o resultado no disco e no Git e pode ler qualquer path necessário para entender, implementar ou verificar a tarefa. A investigação deve ser dirigida pelo fluxo real e pelas evidências encontradas, sem varredura cega da árvore, dump de arquivos ou leitura de diretórios gerados e irrelevantes.

Decisões transversais usam IDs estáveis por dimensão, como `AUTH-01`. Quando houver decisões vigentes, `AGENTS.md` mantém somente uma tabela compacta com `ID`, decisão atual e fonte. Histórico, justificativa e impacto permanecem no MVP ou na phase de origem. Uma phase posterior só muda a decisão ao declarar explicitamente a substituição; cronologia sozinha não resolve conflito.

A tabela de decisões vigentes só muda depois de implementação, review aprovada e confirmação humana. Nesse momento, a IA aplica patch mínimo em `AGENTS.md`. Nenhum analista publica decisão semântica sem essa confirmação.

### 4. Scripts

- A prosa é o contrato. Script só acelera regra mecânica já escrita (estado, progresso, ondas) e aponta para a casa dela; divergência é bug do script.
- Node 18+, módulos `.mjs`, somente módulos nativos, sem dependência nem build. Git chamado com argumentos em lista, sem shell; leitura tolerante a CRLF e BOM; caminhos por `node:path`; nunca cria symlink. Compatível com Windows e Linux.
- Somente leitura: script não escreve artefato, não faz commit, push nem staging. Saída em texto e em `--json` com não-ASCII escapado; código 0 sem achado, 1 com achado, 2 em erro de uso.
- Sem Node, o líder aplica a prosa como antes; o script nunca é pré-requisito de etapa.
- Todo script tem teste de comportamento em `tests/scripts/` com `node:test`, montando cenário de disco temporário.
- Backup de arquivo do usuário: commit que o contenha ou cópia em `.vibeflow/old/` com tamanho e hash conferidos, **só então** substituir.

### 5. Template

- Mora em `skills/vibeflow/templates/`. É esqueleto, não documento preenchido.
- A IA copia a forma e escreve o conteúdo diretamente no artefato vivo.
- Seções fixas, nomes estáveis, um lar por fato. Placeholder óbvio (`<frase curta>`), sem prosa de exemplo que a IA possa colar sem pensar.
- Seção opcional diz no próprio template quando omitir. Não criar arquivo extra para variação do mesmo artefato.

### 6. Escrita da skill (`SKILL.md` e referências)

O `SKILL.md` é prompt operacional para o líder, não artigo.

Frontmatter obrigatório:

```yaml
---
name: vibeflow
description: >
  O que faz, em 1 ou 2 frases, e onde grava. Use when the user runs
  /vibeflow ou /vibeflow <etapa>, <gatilhos em português e em
  comportamento>, mesmo que não diga vibeflow.
---
```

`description` dispara auto-invoke. Sem ela a skill não entra sozinha.

Corpo do `SKILL.md`: invariantes em duas ou três linhas, abertura com o estado lido do disco, classificação da rota, roteamento por etapa para a referência dela, delegação, retomada e fechamento. Cada etapa tem uma referência própria com gate, trabalho semântico, gravação e fechamento.

Regras de prosa:

- Uma casa por fato. Tabela, não parágrafo repetido. Catálogo fica em `references/` e o texto aponta: "leia X quando Y". Não resumir a tabela em outro arquivo.
- Sem narrativa, sem ensaios conceituais e sem banco de pensamentos. `SKILL.md` e referências são manual operacional imperativo: o que fazer, o que validar, o que recusar e o fluxo de execução.
- Sem "por que o produto existe". Isso fica fora da skill.
- Sem seção órfã ("ver template abaixo" sem template) e sem path citado que não exista.
- Uma pergunta por vez. Várias respostas de uma vez: aceitar e fechar.
- Patch de SLOT = só aquele trecho, texto do humano, sem reescrever.
- Não avançar para a próxima etapa a menos que o humano autorize explicitamente (ex.: "pode ir pro plan", "segue pro implement"). Se autorizado, avançar imediatamente sem perguntar de novo. A única exceção é o encadeamento implement, review e correções, definido no topo do `SKILL.md`.
- A etapa init commita os arquivos de governança produzidos, sem push. As etapas de definição e análise não commitam. A etapa implement commita cada onda com integração verde com subagentes ou cada task verde sem subagentes; a etapa review finaliza a phase. No fechar, dizer o hash, os paths enviados e o que ficou de fora.
- Português do Brasil. Frase completa. Sem emoji. Sem travessão longo. Tom factual, calmo, sem acolhimento.

### 7. Tom (chat e artefato)

Vale para skill, docs, relatório em prosa e conversa neste repo.

- Factual e profissional. Cortar enrolação, não contexto.
- Começar pelo que é verdade ou pelo que fazer. Não abrir com "não é X".
- Explicar código por o que acontece, por que, impacto. Não exigir sintaxe do humano.
- Artefato vivo guarda a **lógica** (pedido → passos → conclusão), não só o recap. Não apagar trilha para "limpar" no final.
- Chat curto no restate; disco completo. Indicar o caminho do arquivo gravado e um resumo factual claro dos pontos cobertos.
- Número de confiança, n, slug, path: só se o disco ou o humano sustentarem. Chute vira GUESS explícito, não fato.
- Decisão do humano: perguntar na hora, com opções e recomendação. Se não muda o resultado, assumir e avisar.

### 8. Verificação

- Testes automatizados existem só para os scripts. Não criar teste que confira presença de palavras, frases ou seções em `SKILL.md`, referências, templates ou documentação.
- Toda mudança passa pela revisão de consistência dos Comandos do projeto e por review independente de qualidade da skill.
- O uso real numa phase conduzida com `/vibeflow` é a evidência final de comportamento.

### 9. Ordem para mudar a skill

1. `skills/vibeflow/references/disco.md`, quando o contrato de disco muda.
2. `skills/vibeflow/SKILL.md`, as demais referências e os templates.
3. `README.md`, quando instalação ou uso mudam.

Não inverter: etapa sem contrato de disco vira path inventado.

### Limites permanentes deste repo

- Criar `CLAUDE.md` como segunda fonte de regras.
- Segunda fonte de regras fora de `AGENTS.md`.
- Criar um `GEMINI.md` no workspace para duplicar a fonte canônica.
- Tratar a ponte `.agents/rules/vibeflow.md` como fonte editável.
- Artefato da cadeia fora de `.vibeflow/phases/phase-N-slug/`.
- Exceção única ao item anterior: baseline de projeto novo em `.vibeflow/mvp/`, uma vez por repositório e sempre na rota `max` completa.
- Segunda skill instalável, alias de comando ou motor que conduz etapa no lugar do líder.
- Script que escreve, opera Git ou usa dependência externa, sem o humano pedir.
- Avançar para a próxima etapa sem autorização do humano, salvo o encadeamento implement, review e correções do `SKILL.md`. Se o humano autorizou explicitamente avançar, a IA deve avançar diretamente.
