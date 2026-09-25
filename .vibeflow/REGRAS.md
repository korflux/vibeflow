# Regras do projeto

<!-- VIBEFLOW:CADEIA start -->
| esforço | fluxo | quando |
|---|---|---|
| — | init | primeira vez no repo, ou disco quebrado, de novo só para reparar |
| low | implement | pedido claro, direto, simples (cor, texto, documento, landing page / página de captura estática) |
| medium | implement → review | pedido claro e direto sem regressão de backend, ou página visual cujo aceite dependa de validação renderizada |
| high | spec → plan → implement → review | pedido claro, execução difícil, ou sistema com auth, painel admin, banco ou regressão |
| xhigh | interview → spec → plan → implement → review | pedido ambíguo, confiança baixa, intenção ou sucesso de software em aberto |
| max | interview → spec → plan → analyze → implement → review | pedido toca auth, pagamento, segredo, perda de dados, produção, alto blast radius ou baseline MVP de software |
<!-- VIBEFLOW:CADEIA end -->

Design (`vibe-design`, artefato `design.md` na mesma pasta) entra entre spec e plan somente com UI visível. Sem UI visível, registra N/A explícito em vez de bloqueio. Com UI visível, o handoff da spec é `vibe-design` e o da design é `vibe-plan`. Toda rota com spec exige UX F* suficiente para fechar o comportamento real; página informativa simples usa F* curto e N/A fundamentado para regras inexistentes. O analyze no max cruza design com UI visível.

### Continuidade entre chats (recomendação)

| Transição | Recomendação |
|---|---|
| `init → interview → spec → design` | Pode continuar no mesmo chat. |
| `spec/design → plan` | Recomende novo chat para o plan. |
| `plan → analyze` (MVP/max) | Recomende novo chat para o analyze, separado do plan. |
| `plan/analyze → implement` | Recomende novo chat; na execução em sequência, use um chat por `T*`. |
| Grupo paralelo aprovado | Exceção ao chat por `T*`: um chat coordenador pode conduzir o grupo junto, mantendo isolamento, prova e commit próprios por task. |
| `implement → review` | Recomende novo chat para review. |
| `review → implement` | Recomende novo chat para correções. |

Separar chats é uma recomendação, nunca um gate. Se o humano preferir continuar no mesmo chat, prossiga e use os artefatos vivos como fonte de contexto. Não crie chats automaticamente. O plan registra grupos paralelizáveis com `T*` e motivo; ao iniciar implement, informe o grupo e pergunte se o humano quer executá-lo em paralelo. Só paralelize após resposta afirmativa e com dependências, ownership e isolamento seguros. Sem isso, execute em sequência.

Faixa Express (low ou medium) atende pedidos claros e localizados sem comportamento novo, como copy, rótulo, nome de tela, cor, espaçamento ou ícone com texto mantido. Classifique antes de exigir `.vibeflow/`, `vibe-init`, inventário de phase ou script. Sem phase ativa para a entrega, implemente direto, faça a checagem proporcional e não crie init, phase ou artefato VibeFlow. Com phase ativa, reutilize-a: atualize a T* aberta ou acrescente uma T* curta no `plan.md` existente; achado formal de review atualiza o R* existente. Para ajuste visual, atualize o `design.md` existente quando houver. Não crie spec, plan ou design só para o ajuste. Comportamento, rota, interação, critério de aceite ou acessibilidade alterados saem do Express. Também saem mudanças que toquem privacidade, dado pessoal, consentimento, retenção, direitos, obrigação jurídica, autenticação, autorização, pagamento, segredo, persistência ou risco de perda de dados, seguindo a cadeia aplicável.

Review leve no Express cobra rastreabilidade e inspeção renderizada somente quando o aceite depender do resultado visual. Segurança e banco só abrem se o diff tocar essas superfícies.

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
- `vibe-implement` commita cada task somente depois de teste verde, com staging explícito por path e sem push.
- `vibe-review` faz o commit residual e o `git push` final da phase somente após Approve, confirmação humana e correções fechadas. Nunca usar `git add -A`, amend, squash ou force push.
- Commitável: `.vibeflow/REGRAS.md`, `AGENTS.md`, `CLAUDE.md`, `.vibeflow/old/` se existir, `.vibeflow/phases/` (`.gitkeep` e artefatos vivos), pacote da skill, `docs/`.
- Não commitar: `init-report.json`, `init-pending.json`, `*-report.json` e `*-pending.json`.
- `AGENTS.md` e `CLAUDE.md` são symlink para `.vibeflow/REGRAS.md`. Nunca copiar o conteúdo para a raiz.

## Estrutura

```
.vibeflow/REGRAS.md          fonte viva das regras
.vibeflow/mvp/               baseline único de um projeto novo na rota max
.vibeflow/phases/            artefatos da cadeia (phase-N-slug/)
.vibeflow/old/               backups do init, se houver
AGENTS.md                    symlink → .vibeflow/REGRAS.md
CLAUDE.md                    symlink → .vibeflow/REGRAS.md
.agents/rules/vibeflow.md   include → ../../.vibeflow/REGRAS.md
vibe-<nome>/                 pacote canônico da skill
skills/vibe-<nome>           symlink → ../vibe-<nome> (descoberta do CLI e plugins)
.claude-plugin/              marketplace Claude
.codex-plugin/               plugin Codex
.agents/plugins/             marketplace Codex
.grok-plugin/                marketplace Grok
plugin.json                  plugin Antigravity (raiz)
docs/vibe-<nome>/            arquitetura, análise, testes (não instala)
README.md                    install (npx skills e marketplaces)
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

### Adaptadores por host

A fonte editável é sempre `.vibeflow/REGRAS.md`. `AGENTS.md` e `CLAUDE.md` são ponteiros compatíveis na raiz. O Antigravity recebe somente a ponte mínima descoberta pelo workspace, `.agents/rules/vibeflow.md`, com `@../../.vibeflow/REGRAS.md`; o init cria, verifica e repara esse arquivo sem copiar as regras.

As regras globais permanecem separadas das regras do workspace: Codex usa `~/.codex/AGENTS.md` ou `~/.codex/AGENTS.override.md`, e Antigravity usa `~/.gemini/GEMINI.md`. O Vibeflow não sincroniza nem sobrescreve esses arquivos e não cria `GEMINI.md` no projeto. Se o host carregar mais de um nome, a carga efetiva deve ser conferida na ferramenta do próprio host.

## Regras deste repo

Estas regras existem para a próxima `vibe-*` nascer igual às que já estão prontas (`vibe-init`, `vibe-interview`, `vibe-spec`, `vibe-plan`, `vibe-analyze`, `vibe-implement`, `vibe-review`). Contrato específico de uma skill vive em `docs/vibe-<nome>/ARQUITETURA.md`. Aqui vive só o que se repete.

### 1. Pacote `vibe-<nome>`

- Nome: `vibe-` + verbo curto (`init`, `interview`, `spec`, `plan`, `analyze`, `implement`, `review`). Minúsculas, hífen, sem pontuação.
- Fonte canônica no git: `vibe-<nome>/` na raiz deste repo. `skills/vibe-<nome>` é symlink para esse pacote. Install: `npx skills add korflux/vibeflow` (projeto ou `-g`) nos agentes `grok`, `claude-code`, `codex`, `antigravity`, ou o marketplace nativo no `README.md`. Pacote sem `docs/`.
- Pasta vazia de skill futura fica só com `.gitkeep` até existir `SKILL.md`.
- Não criar skill “por via das dúvidas”. Só quando o contrato de disco e o fluxo da IA estiverem claros o bastante para escrever `ARQUITETURA.md`.

### 2. Documentos `docs/vibe-<nome>`

Dois arquivos obrigatórios. Não misturar os papéis.

| Arquivo | Papel | Pergunta que responde |
|---|---|---|
| `ARQUITETURA.md` | Contrato | O que o disco faz, quem é dono de cada path, contrato dos scripts e relatórios quando existirem, erros, testes, limites de contrato |
| `ANALISE.md` | Fluxo e decisão | O que acontece numa run de ponta a ponta, por que as peças existem, o que foi cortado, o que foi assumido |

`ARQUITETURA.md` não narra a conversa. `ANALISE.md` não é a spec do script. Se um fato precisa valer no código, ele mora na arquitetura (e a skill aponta para o script, não copia o schema).

Testes de contrato ficam em `docs/vibe-<nome>/tests/`, fora do pacote instalável. Não rodam quando a skill é ativada.

### 3. Disco: uma fonte, uma pasta de fase, um arquivo por skill

```
.vibeflow/REGRAS.md
.vibeflow/mvp/<artefato>.md
.vibeflow/phases/phase-<n>-<slug>/<artefato>.md
```

- Projeto novo classificado pela IA como MVP usa uma única pasta fixa `.vibeflow/mvp/` e percorre obrigatoriamente `interview`, `spec`, `plan`, `analyze`, `implement` e `review`.
- O modo MVP não usa `n` nem slug. A IA escolhe semanticamente o modo; o script recebe alvo explícito e só executa as operações determinísticas.
- Só existe um baseline MVP por repositório. Depois de concluído, ele não é sobrescrito, movido nem versionado; pivô ou reconstrução integral entra como phase `max`.
- `n` inteiro crescente, sem zero à esquerda, ordem **numérica**. Calculado pelo script (max existente + 1). A IA não inventa `n`.
- `slug`: frase curta da fase, `a-z0-9` e hífen, 2–48 chars. O script sanitiza.
- Pasta da fase agrupa o pedido. Skills seguintes gravam **na mesma pasta**, outro arquivo.
- Nome do arquivo é o tipo, não o título: `interview.md`, `spec.md`, `plan.md`, `analyze.md`. Implement e review só gravam se a arquitetura daquela skill disser que existe artefato.
- Não gravar cadeia em `docs/`, na raiz, nem em path de outro produto (`fluxline`, etc.).
- Relatório operacional, quando a arquitetura da skill exigir: `.vibeflow/<nome>-report.json` (gitignored). Se o script o gerar, stdout = path do relatório.
- O artefato vivo é preparado pelo `--apply` somente quando ausente. A IA escreve e atualiza a prosa diretamente no arquivo da fase ou do MVP; conteúdo existente é preservado byte a byte.
- Continuar o mesmo pedido: editar o vivo. Pedido novo: próxima pasta. Não renomear pasta depois de criada.
- Sem `.vibeflow/`: a skill que não é o init para e manda `/vibe-init`.

### 4. Papéis na run

```
IA                →  pilota a run: entende o pedido, o projeto e os scripts; investiga, decide a semântica e audita o resultado
Skill (SKILL.md)  →  orienta a IA com invariantes, sequência recomendada, gates e critérios de fechamento
Script            →  auxilia operações mecânicas e determinísticas (inventário, n, slug, alvo, ponteiros e relatório)
Humano            →  decide apenas o que muda materialmente o resultado e não pode ser concluído pelo contexto
```

Script não interpreta intenção, não decide semântica e não escreve prosa do artefato. A IA escolhe o que precisa investigar, mas não inventa path contratual, número ou fato que o disco e o humano não sustentam, nem “melhora” texto que o humano ditou para um SLOT.

A IA começa entendendo o pedido e o contrato local. Antes de executar um script que possa alterar o disco, lê o motor que será usado e entende objetivo, entradas, saídas, mutações e proteções relevantes. Inventário e relatório auxiliam essa leitura como evidência operacional, não como autoridade semântica nem como limite automático de investigação.

A IA audita o resultado no disco e pode ler qualquer path necessário para entender, implementar ou verificar a tarefa. A investigação deve ser dirigida pelo fluxo real e pelas evidências encontradas, sem varredura cega da árvore, dump de arquivos ou leitura de diretórios gerados e irrelevantes.

Decisões transversais usam IDs estáveis por dimensão, como `AUTH-01`. Quando houver decisões vigentes, `REGRAS.md` mantém somente uma tabela compacta com `ID`, decisão atual e fonte. Histórico, justificativa e impacto permanecem no MVP ou na phase de origem. Uma phase posterior só muda a decisão ao declarar explicitamente a substituição; cronologia sozinha não resolve conflito.

A tabela de decisões vigentes só muda depois de implementação, review aprovada e confirmação humana. Nesse momento, a IA aplica patch mínimo em `REGRAS.md`. Scripts e relatórios nunca publicam decisões semânticas nem editam esta fonte viva.

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
- Saída de script é evidência a conferir. Se ela contradiz o pedido, o contrato ou o disco, a IA não a obedece cegamente: identifica se a causa é seleção incorreta, limitação do ambiente ou defeito no código.
- Se o defeito estiver no script e a correção couber na tarefa, a IA corrige a causa raiz e verifica o comportamento. Se for limitação do ambiente, pode usar o outro motor ou reproduzir a operação manualmente, preservando as mesmas validações, backups e garantias. Erro de segurança ou proteção explícita nunca é contornado.
- Função no script leva comentário semântico (para que serve; se a decisão não for óbvia, o porquê). Nenhuma função órfã.
- Old/backup de arquivo do usuário: copiar, conferir tamanho + hash, **só então** substituir. Colisão em `old/` vira timestamp. Init já faz isso; skills que mexem em arquivo alheio repetem.
- Relatórios entram no `.gitignore` **dentro** de `.vibeflow/`, sem apagar entradas das outras skills.

### 6. Template

- Mora em `vibe-<nome>/templates/`. É esqueleto, não documento preenchido.
- A IA copia a forma e escreve o conteúdo diretamente no artefato vivo.
- O script **não** preenche markdown. Apply somente prepara ou valida o destino e preserva o vivo existente.
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
2. **0. Entender e usar o script** (path da skill, motor que será executado, objetivo, entradas, saídas, mutações, proteções, comando Windows/Unix, evidências produzidas e erros que não se contornam).
3. **1. Abrir** em ~5 linhas de estado (fluxo, alvo, dependências, status e artefato vivo). Bloco de exemplo curto.
4. Passos numerados: gate, trabalho semântico, gravar, fechar.
5. Sem seção de escopo no fim. Limite que vale durante a run é invariante ancorado no passo onde vale; escopo de produto vive em `docs/ESCOPO.md` e limite de contrato em `docs/vibe-<nome>/ARQUITETURA.md`.

Regras de prosa na skill:

- Uma casa por fato. Tabela, não parágrafo repetido. Catálogo (frameworks, critérios) fica em `references/` e a skill aponta: “leia X quando Y”. Não resumir a tabela no SKILL.
- Sem narrativa, sem ensaios conceituais e sem banco de pensamentos ("A IA pilota...", "O script apenas..."). O SKILL.md é exclusivamente um manual operacional imperativo: o que fazer, o que validar, o que recusar, comandos e fluxo de execução.
- Sem “por que o produto existe”. Isso é `ANALISE.md`.
- Sem seção órfã (“ver template abaixo” sem template).
- Uma pergunta por vez. Várias respostas de uma vez: aceitar e fechar.
- Patch de SLOT = só aquele trecho, texto do humano, sem reescrever.
- Não disparar a próxima `vibe-*` a menos que o humano autorize explicitamente o avanço (ex.: "pode ir pro plan", "segue pro implement"). Se autorizado, avançar imediatamente sem perguntar de novo.
- `vibe-init` commita os arquivos de governança produzidos, sem push. As demais skills de definição e análise não commitem. `vibe-implement` commita a task verde e `vibe-review` finaliza a phase. No fechar, dizer o hash, os paths enviados e o que ficou de fora.
- Português do Brasil. Frase completa. Sem emoji. Sem travessão longo. Tom factual, calmo, sem acolhimento.


### 8. Tom (chat e artefato)

Vale para skill, docs, relatório em prosa e conversa neste repo.

- Factual e profissional. Cortar enrolação, não contexto.
- Começar pelo que é verdade ou pelo que fazer. Não abrir com “não é X”.
- Explicar código por o que acontece, por que, impacto. Não exigir sintaxe do humano.
- Artefato vivo guarda a **lógica** (pedido → passos → conclusão), não só o recap. Não apagar trilha para “limpar” no final.
- Chat curto no restate; disco completo. Indicar o caminho do arquivo gravado e um resumo factual claro dos pontos cobertos.
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

### Limites permanentes deste repo

Escopo ainda não construído, com o que já foi feito marcado, vive em `docs/ESCOPO.md`.

- Copiar `REGRAS.md` para `AGENTS.md`, `CLAUDE.md` ou `.agents/rules/vibeflow.md`.
- Segunda fonte de regras fora de `.vibeflow/REGRAS.md`.
- Criar um `GEMINI.md` no workspace para duplicar a fonte canônica.
- Tratar a ponte `.agents/rules/vibeflow.md` como fonte editável.
- Artefato da cadeia fora de `.vibeflow/phases/phase-N-slug/`.
- Exceção única ao item anterior: baseline de projeto novo em `.vibeflow/mvp/`, uma vez por repositório e sempre na rota `max` completa.
- Skill nova sem o par `ARQUITETURA.md` + `ANALISE.md`.
- Motor único “só Python” ou “só PowerShell”. Dependência nova sem o humano pedir.
- Disparar a próxima skill da cadeia sem autorização do humano. Se o humano autorizou explicitamente avançar, a IA deve avançar diretamente.
