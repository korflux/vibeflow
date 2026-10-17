# Regras do projeto

> VibeFlow: documentos e edição apenas de texto ficam fora das etapas `spec`, `design`, `plan`, `analyze`, `implement` e `review`, que tratam código de software. A etapa `interview` pode esclarecer um briefing ambíguo de documento.

A skill `vibeflow` é só texto: não tem código, scripts nem testes automatizados. A prova de uma mudança na skill é a revisão de consistência e o uso real.

| esforço | fluxo | quando |
|---|---|---|
| N/A | init | primeira vez no repo, ou disco quebrado, de novo só para reparar |
| low | implement | mudança simples de código de software, como cor ou layout de página estática |
| medium | implement → review | pedido claro e direto sem regressão de backend, ou página visual cujo aceite dependa de validação renderizada |
| high | spec → plan → implement → review | pedido claro, execução difícil, ou sistema com auth, painel admin, banco ou regressão |
| xhigh | interview → spec → plan → implement → review | pedido ambíguo, confiança baixa, intenção ou sucesso de software em aberto |
| max | interview → spec → plan → analyze → implement → review | pedido toca auth, pagamento, segredo, perda de dados, produção, alto blast radius ou baseline MVP de software |
Design (etapa `design`, artefato `design.md` na mesma pasta) entra entre spec e plan somente com UI visível. Sem UI visível, registra N/A explícito em vez de bloqueio. Toda rota com spec exige UX F* suficiente para fechar o comportamento real; página informativa simples usa F* curto e N/A fundamentado para regras inexistentes. O analyze no max cruza design com UI visível.

Entrada: `/vibeflow` conduz a rota inteira e retoma a phase aberta; `/vibeflow <etapa>` vai direto a `init`, `interview`, `spec`, `design`, `plan`, `analyze`, `implement` ou `review`, desde que o pré-requisito esteja satisfeito.

### Continuidade entre chats (recomendação)

| Situação | Recomendação |
|---|---|
| Padrão | Um único chat com `/vibeflow` conduz a rota inteira. O líder delega analyze e review a revisor de contexto limpo e as correções a subagente, com até 2 rodadas antes de parar e relatar. |
| Host de contexto curto ou contexto pesado | Dois chats: um para todo o planejamento (interview até plan, e analyze no max) e outro para a implementação (implement, review e correções). Antes de trocar, o `plan.md` registra pronto, em andamento e pendente. |
| Host sem subagentes (Modo B) | Uma etapa ou uma T* por run, executada inline. Analyze e review rodam em chat novo com `/vibeflow analyze` ou `/vibeflow review`, que atua como visão de fora. |

Separar chats é uma recomendação, nunca um gate. Se o humano preferir continuar no mesmo chat, prossiga e use os artefatos vivos como fonte de contexto. Não crie chats automaticamente.

O líder conversa com o humano, planeja as ondas, escolhe resultados, responsáveis, dependências e colaboração, delega toda execução (leitura ampla, artefatos, código, testes, conferência técnica, provas, registros e Git), valida os dados recebidos e faz no máximo pequenos ajustes finais. Antes da primeira onda, confere a capacidade de delegação (perfis carregados, ferramentas e privilégios registrados na prontidão do plan) e não despacha onda sem os perfis exigidos. Implementador entrega código e testes, redator entrega artefatos e T* cujo resultado principal é prosa, verificador certifica integração, revisor permanece independente e finalizador genérico/default apto opera registros e Git com ownership temporário exclusivo.

Código paralelo só ocorre em onda: T* elegíveis com `Arquivos:` disjuntos, ownership exclusivo por T*; T* sem `Arquivos:` ou sobreposta roda sozinha. Leitura e preparação podem colaborar sem compartilhar escrita. No Modo B, ofereça o grupo de T* ao humano antes de paralelizar. Implementador e verificador provam somente a `Prova afetada:` de cada T*; a review final executa a `Regressão completa` do plan. O plan define o trabalho e mantém o resumo de estado; o Git guarda histórico e evidência de commit. Conclusão exige integração verde e commit real. O pedido de `/vibeflow` com plan aprovado autoriza a implementação, a review e a correção delegadas; a aprovação da review, a sincronização de decisões vigentes e o push continuam exigindo a confirmação humana final. Phases dos protocolos históricos são lidas como estão, sem migração implícita.

Texto ou documento avulso segue edição direta, fora da cadeia de implementação e review de código; uma ambiguidade real pode acionar a etapa `interview`. Faixa Express (low ou medium) atende mudanças claras e localizadas em código de software sem comportamento novo, como cor ou espaçamento de UI. Classifique antes de exigir `.vibeflow/`, etapa init ou phase. Sem phase ativa para a entrega, delegue a implementação, faça a checagem proporcional e não crie `.vibeflow/`, phase ou artefato. Com phase ativa, reutilize-a: atualize a T* aberta ou acrescente uma T* curta no `plan.md` existente; achado formal de review atualiza o R* existente. Para ajuste visual, atualize o `design.md` existente quando houver. Não crie spec, plan ou design só para o ajuste. Comportamento, rota, interação, critério de aceite ou acessibilidade alterados saem do Express. Também saem mudanças que toquem privacidade, dado pessoal, consentimento, retenção, direitos, obrigação jurídica, autenticação, autorização, pagamento, segredo, persistência ou risco de perda de dados, seguindo a cadeia aplicável.

Review leve no Express cobra rastreabilidade e inspeção renderizada somente quando o aceite depender do resultado visual. Segurança e banco só abrem se o diff tocar essas superfícies.

## Projeto

Skill única `vibeflow`, conduzida por um coordenador-líder, para inicializar e conduzir o trabalho de agentes num repo. Este repositório é a fonte canônica do pacote `skills/vibeflow/` e do contrato `.vibeflow/`. Não é um app de produção.

## Comandos do projeto

- Este repositório não usa CI no GitHub, por decisão de custo. Não envie branch só para disparar CI. A regressão completa e a varredura de segredos rodam localmente antes do push.
- Regressão completa local: revisão de consistência de todos os arquivos alterados. Todo path citado em `skills/vibeflow/`, `docs/`, `README.md` e `AGENTS.md` existe; nenhum arquivo cita os comandos ou pacotes da v1, scripts ou registro estruturado de execução; `git diff --check` não acusa achado.
- Varredura de segredos local: `gitleaks detect --source . --redact --no-banner`.

## Fluxos e invariantes

- A IA interpreta intenção, aplica as regras mecânicas escritas e escreve a prosa dos artefatos vivos; o disco e o Git são a fonte do estado.
- As fases vivem em `.vibeflow/phases/phase-N-slug/`; o baseline único de software novo vive em `.vibeflow/mvp/`.
- O init preserva fontes legadas em `.vibeflow/old/` com tamanho e hash conferidos antes de substituir qualquer regra.

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
- Com subagentes, o finalizador genérico/default apto recebe operações e paths autorizados, registra o estado no `plan.md` e, somente depois da prova integrada verde, cria `task(T1,T2,...): <resultado>`, com staging explícito e todos os IDs comprovados. Sem subagentes, cada T* verde recebe seu commit `task(Tn): <resultado>`, sem push. Não reutilize como finalizador um perfil que proíba Git. Sem agente apto, relate a limitação sem assumir operação pelo líder. Índice Git e registros têm ownership exclusivo durante a finalização.
- A etapa review faz o commit residual e o `git push` final da phase somente após Approve, confirmação humana e correções fechadas; o líder transmite a confirmação e o escopo ao finalizador. O revisor delegado não toca Git. Nunca usar `git add -A`, `git add .`, amend, squash ou force push.
- Phases da v1 (`# Protocolo: etapas-v1` ou `coordenacao-v1` no plan) são lidas como estão e não migram; seus marcadores não valem para plans novos.
- Commitável: `AGENTS.md`, `.vibeflow/old/` se existir, `.vibeflow/phases/` (`.gitkeep`, artefatos vivos e registros históricos da v1), equivalente no MVP, pacote da skill, `docs/`.
- Não commitar: `init-report.json`, `init-pending.json`, `*-report.json` e `*-pending.json`.
- `AGENTS.md` é a fonte editável na raiz. O init não cria `CLAUDE.md` nem `REGRAS.md`.

## Estrutura

```
AGENTS.md                    fonte viva das regras
.vibeflow/phases/            artefatos da cadeia (phase-N-slug/)
.vibeflow/old/               backups do init, se houver
.vibeflow/mvp/               contrato: baseline único de um projeto novo na rota max
.agents/rules/vibeflow.md    include → ../../AGENTS.md
skills/vibeflow/             pacote canônico da skill, pasta real
.claude-plugin/              marketplace Claude
.codex-plugin/               plugin Codex
.agents/plugins/             marketplace Codex
.grok-plugin/                marketplace Grok
plugin.json                  plugin Antigravity (raiz)
docs/vibeflow/               arquitetura e análise (não instala)
docs/ESCOPO.md               feito e fila
.erros-encontrados/          erros fora do escopo, um arquivo por erro
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
```

### Adaptadores por host

A fonte editável é sempre `AGENTS.md` na raiz. O Antigravity recebe somente a ponte mínima descoberta pelo workspace, `.agents/rules/vibeflow.md`, com `@../../AGENTS.md`; o init cria, verifica e repara esse arquivo sem copiar as regras.

As regras globais permanecem separadas das regras do workspace: Codex usa `~/.codex/AGENTS.md` ou `~/.codex/AGENTS.override.md`, e Antigravity usa `~/.gemini/GEMINI.md`. O Vibeflow não sincroniza nem sobrescreve esses arquivos e não cria `GEMINI.md` no projeto. Se o host carregar mais de um nome, a carga efetiva deve ser conferida na ferramenta do próprio host.

## Regras deste repo

Estas regras mantêm a skill única coerente a cada mudança. O contrato da skill vive em `docs/vibeflow/ARQUITETURA.md`. Aqui vive só o que vale para qualquer mudança no repo.

### 1. Pacote

- Um único pacote instalável: `skills/vibeflow/`, pasta real, sem symlink. Os manifestos apontam para ela.
- Só texto: `SKILL.md`, `references/` e `templates/`. Sem scripts, código executável ou testes.
- Install: `npx skills add korflux/vibeflow` (projeto ou `-g`) nos agentes `grok`, `claude-code`, `codex`, `antigravity`, ou o marketplace nativo no `README.md`. O pacote não inclui `docs/`.
- Não criar segunda skill nem alias de comando. Etapa nova entra como referência da skill única.

### 2. Documentos `docs/vibeflow`

Dois arquivos obrigatórios. Não misturar os papéis.

| Arquivo | Papel | Pergunta que responde |
|---|---|---|
| `ARQUITETURA.md` | Contrato | O que o disco guarda, quem é dono de cada path, gates por rota, ondas, distribuição e limites de contrato |
| `ANALISE.md` | Fluxo e decisão | O que acontece numa run de ponta a ponta, por que as peças existem, o que foi cortado, o que foi assumido |

`ARQUITETURA.md` não narra a conversa. `ANALISE.md` não é manual operacional. Fato de contrato mora na arquitetura; regra operacional mora no pacote, e a arquitetura cita a casa sem copiá-la.

### 3. Disco: uma fonte, uma pasta de fase, um arquivo por etapa

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
- A rota fica em `# Rota:` no cabeçalho do primeiro artefato da phase (`interview.md` em xhigh, max e MVP; `spec.md` em high; `review.md` em medium) e não muda. Plans novos não levam `# Protocolo:` nem `# Modo:`; o modo é decidido na run.
- Não gravar cadeia em `docs/`, na raiz, nem em path de outro produto.
- O artefato vivo nasce da forma do template somente quando ausente. Conteúdo existente é editado no lugar, nunca recriado.
- Continuar o mesmo pedido: editar o vivo. Pedido novo: próxima pasta. Não renomear pasta depois de criada.
- Sem `.vibeflow/` numa rota com cadeia: a primeira etapa é `init`.

### 4. Papéis na run

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

### 5. Sem código

- A skill não tem scripts. Operação mecânica (`n`, slug, preservação, backup, gates) é regra escrita, aplicada pela IA e auditada no disco.
- Backup de arquivo do usuário: commit que o contenha ou cópia em `.vibeflow/old/` com tamanho e hash conferidos, **só então** substituir.
- Reintroduzir código executável na skill é decisão do humano e mudança de contrato.

### 6. Template

- Mora em `skills/vibeflow/templates/`. É esqueleto, não documento preenchido.
- A IA copia a forma e escreve o conteúdo diretamente no artefato vivo.
- Seções fixas, nomes estáveis, um lar por fato. Placeholder óbvio (`<frase curta>`), sem prosa de exemplo que a IA possa colar sem pensar.
- Seção opcional diz no próprio template quando omitir. Não criar arquivo extra para variação do mesmo artefato.

### 7. Escrita da skill (`SKILL.md` e referências)

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
- Sem "por que o produto existe". Isso é `ANALISE.md`.
- Sem seção órfã ("ver template abaixo" sem template) e sem path citado que não exista.
- Uma pergunta por vez. Várias respostas de uma vez: aceitar e fechar.
- Patch de SLOT = só aquele trecho, texto do humano, sem reescrever.
- Não avançar para a próxima etapa a menos que o humano autorize explicitamente (ex.: "pode ir pro plan", "segue pro implement"). Se autorizado, avançar imediatamente sem perguntar de novo.
- A etapa init commita os arquivos de governança produzidos, sem push. As etapas de definição e análise não commitam. A etapa implement commita a integração verde com subagentes ou cada task verde sem subagentes; a etapa review finaliza a phase. No fechar, dizer o hash, os paths enviados e o que ficou de fora.
- Português do Brasil. Frase completa. Sem emoji. Sem travessão longo. Tom factual, calmo, sem acolhimento.

### 8. Tom (chat e artefato)

Vale para skill, docs, relatório em prosa e conversa neste repo.

- Factual e profissional. Cortar enrolação, não contexto.
- Começar pelo que é verdade ou pelo que fazer. Não abrir com "não é X".
- Explicar código por o que acontece, por que, impacto. Não exigir sintaxe do humano.
- Artefato vivo guarda a **lógica** (pedido → passos → conclusão), não só o recap. Não apagar trilha para "limpar" no final.
- Chat curto no restate; disco completo. Indicar o caminho do arquivo gravado e um resumo factual claro dos pontos cobertos.
- Número de confiança, n, slug, path: só se o disco ou o humano sustentarem. Chute vira GUESS explícito, não fato.
- Decisão do humano: perguntar na hora, com opções e recomendação. Se não muda o resultado, assumir e avisar.

### 9. Verificação

- Não há testes automatizados. Não criar teste que confira presença de palavras, frases ou seções em `SKILL.md`, referências, templates ou documentação.
- Toda mudança passa pela revisão de consistência dos Comandos do projeto e por review independente de qualidade da skill.
- O uso real numa phase conduzida com `/vibeflow` é a evidência final de comportamento.

### 10. Ordem para mudar a skill

1. `docs/vibeflow/ARQUITETURA.md`, quando o contrato muda.
2. `docs/vibeflow/ANALISE.md`, quando o fluxo ou uma decisão muda.
3. `skills/vibeflow/SKILL.md`, `references/` e `templates/`.
4. `README.md` e versão dos manifestos, conforme o semver.

Não inverter: skill sem contrato vira path inventado.

### Limites permanentes deste repo

Escopo ainda não construído, com o que já foi feito marcado, vive em `docs/ESCOPO.md`.

- Criar `CLAUDE.md` ou `REGRAS.md` como segunda fonte de regras.
- Segunda fonte de regras fora de `AGENTS.md`.
- Criar um `GEMINI.md` no workspace para duplicar a fonte canônica.
- Tratar a ponte `.agents/rules/vibeflow.md` como fonte editável.
- Artefato da cadeia fora de `.vibeflow/phases/phase-N-slug/`.
- Exceção única ao item anterior: baseline de projeto novo em `.vibeflow/mvp/`, uma vez por repositório e sempre na rota `max` completa.
- Segunda skill instalável, alias de comando ou retorno dos pacotes da v1.
- Código executável no pacote ou dependência nova sem o humano pedir.
- Avançar para a próxima etapa sem autorização do humano. Se o humano autorizou explicitamente avançar, a IA deve avançar diretamente.
