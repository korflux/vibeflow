# Regras do projeto

> VibeFlow: documentos e edição apenas de texto ficam fora da cadeia da skill única `vibeflow`, que trata código de software. Um briefing ambíguo de documento pode passar antes pelas perguntas da interview.

<!-- VIBEFLOW:CADEIA start -->
A cadeia da skill `vibeflow` vale só quando o humano a chama com `/vibeflow` (`$vibeflow` no Codex); fora disso, o agente segue as demais regras deste arquivo, sem rota, phase nem artefato. Risco, MVP, encadeamento, retomada e Modo B seguem a skill `vibeflow`; esta tabela é a única fonte das rotas.

| esforço | etapas | quando |
|---|---|---|
| low | implement, sem init, `.vibeflow/`, phase nem artefato | mudança clara e localizada de código de software sem comportamento novo, como cor, texto ou layout de página estática |
| medium | implement → review | pedido claro e direto, com comportamento novo pequeno ou médio, inclusive em backend e banco sem migration de schema quando o fluxo tocado tem testes, ou página visual cujo aceite dependa de validação renderizada |
| high | interview → spec → plan → analyze, com `# Risco:` ou mais de 8 passos → implement com até dois checkpoints → review | pedido ambíguo, migration de schema, autenticação, autorização, pagamento, dado pessoal, segredo ou risco de perda de dados, backend cujo fluxo tocado não tem testes, ou tela que o design system e as telas existentes não cobrem |

Saem do low, seguindo a rota aplicável: comportamento, rota, interação, critério de aceite ou acessibilidade alterados, e mudanças que toquem privacidade, dado pessoal, consentimento, retenção, direitos, obrigação jurídica, autenticação, autorização, pagamento, segredo, persistência ou risco de perda de dados.
<!-- VIBEFLOW:CADEIA end -->

## Projeto

Skill única `vibeflow`, conduzida por um coordenador-líder, para inicializar e conduzir o trabalho de agentes num repo. Este repositório é a fonte canônica do pacote `skills/vibeflow/` e do contrato `.vibeflow/`. Não é um app de produção.

## Núcleo do projeto

- `skills/vibeflow/references/disco.md`: contrato de disco; ler em toda mudança de artefato ou de regra mecânica.
- `skills/vibeflow/SKILL.md`: manual do líder; ler em toda mudança de comportamento do líder ou de etapa.
- `skills/vibeflow/references/delegation.md` e `skills/vibeflow/references/<papel>.md`: papéis, brief e a leitura de cada analista; ler em toda mudança de papel, perfil ou despacho.
- `skills/vibeflow/scripts/` e `tests/scripts/`: scripts de leitura e testes; ler em toda mudança de regra que um script aplica.

## Comandos do projeto

- Este repositório não usa CI no GitHub, por decisão de custo. Não envie branch só para disparar CI. A regressão completa e a varredura de segredos rodam localmente antes do push.
- Regressão completa local: revisão de consistência de todos os arquivos alterados. Todo path deste repo citado em `skills/vibeflow/`, `README.md` e `AGENTS.md` existe (paths do projeto consumidor, como `.agents/rules/`, `.claude/agents/`, `.codex/agents/` e `.vibeflow/mvp/`, ficam fora); nenhum arquivo cita a v1 do VibeFlow ou registro estruturado de execução; nenhum arquivo cita como vigente o contrato anterior à 5.0.0 (`interview.md`, `design.md` ou `analyze.md` como artefato, as rotas Express e as rotas `xhigh` ou `max`, `ondas.mjs`, os papéis corretor e finalizador), salvo como compatibilidade ou perfil obsoleto; `node --test` passa; `git diff --check` não acusa achado.
- Testes dos scripts: `node --test` na raiz (Node 18+), que descobre `tests/**/*.test.mjs`.
- Varredura de segredos local: `gitleaks detect --source . --redact --no-banner`.

## Fluxos e invariantes

- Fonte única de regras, ponte, perfis globais e backups: `skills/vibeflow/references/init.md`.
- Decisões vigentes: `skills/vibeflow/references/review.md` (Finalizar). Histórico fica na phase de origem; phase posterior só muda decisão declarando a substituição, nunca por cronologia.
- Investigação dirigida pelo fluxo real, sem varredura cega, dump nem leitura de diretórios gerados.

## Ambiente

homolog

Sem banco, migration nem tráfego de usuário: mudança aqui altera contrato de agente, não schema de produção.

## Versão (semver)

- **Major:** quebra contrato (path ou nome de artefato, linha de cabeçalho como `# Status:` ou `# Rota:`, comportamento do líder que o humano já usa).
- **Minor:** adiciona sem quebrar (nova seção opcional no artefato, nova referência de etapa).
- **Patch:** correção sem mudança de contrato.
- Versão atual: 6.2.0 (saída de teste curta; medição longa fora da prova do passo; tipos por pacote e incremental; vermelho só do teste novo; poda de testes como pedido medium).

## Git

- Sem `Co-Authored-By` de ferramenta. Staging só de paths autorizados; nunca `git add -A`, `git add .`, amend, squash ou force push.
- Commits, staging e finalização: `skills/vibeflow/references/disco.md` (Commits). Push exige confirmação humana explícita.
- Commitável: `AGENTS.md`, `.vibeflow/old/` se existir, `.vibeflow/phases/`, `.vibeflow/mvp/` e o pacote da skill.

## Estrutura

```
skills/vibeflow/      pacote da skill, pasta real
  agents/openai.yaml  política do Codex
  references/         <etapa>.md, <papel>.md, retomada.md, ajuste.md, review/passos.md e apoio
  templates/          spec, plan, review, AGENTS.md e agents/<host>/
  scripts/            leitura do disco e do Git, cada um com cabeçalho próprio
tests/scripts/        testes dos scripts, fora do pacote
plugin.json           plugin Antigravity
```

## Regras deste repo

### 1. Pacote

- Um único pacote instalável, `skills/vibeflow/`, pasta real sem symlink, com testes fora dele, em `tests/`; etapa nova entra como referência dele.
- Instalação, plugin Antigravity e adaptadores por host: `README.md`.

### 2. Scripts

- A prosa é o contrato; script só acelera regra mecânica já escrita e aponta para a casa dela. Divergência é bug do script.
- Node 18+, `.mjs`, só módulos nativos, sem build; Git com argumentos em lista, sem shell; tolerante a CRLF e BOM; `node:path`; sem symlink; Windows e Linux.
- Somente leitura, salvo pedido do humano: não escreve artefato nem opera Git. Saída em texto e em `--json` com não-ASCII escapado; código 0 sem achado, 1 com achado, 2 em erro de uso.
- Todo script tem teste de comportamento em `tests/scripts/` (`node:test`, disco temporário).

### 3. Template

Esqueleto em `skills/vibeflow/templates/`, não documento preenchido: seções fixas, nomes estáveis, um lar por fato, placeholder óbvio (`<frase curta>`) e nenhuma prosa de exemplo colável. Seção opcional diz no template quando omitir; variação do mesmo artefato não vira arquivo extra.

### 4. Escrita da skill

- Frontmatter do `SKILL.md`: `name: vibeflow`, `description` com o que faz e onde grava em 1 ou 2 frases, sem gatilho de comportamento e com uso só por `/vibeflow`, e `disable-model-invocation: true`. No Codex, `skills/vibeflow/agents/openai.yaml` tem `policy.allow_implicit_invocation: false`; Antigravity e Grok não têm mecanismo confirmado.
- Manual operacional imperativo; cada etapa tem referência própria com gate, trabalho, gravação e fechamento. Sem narrativa, ensaio, "por que o produto existe", seção órfã nem path inexistente.
- Uma casa por fato, em tabela quando couber; o resto aponta ("leia X quando Y") sem resumir. Ponteiro entra no mesmo passo em que a cópia sai.

### 5. Tom

Skill, docs, relatório e conversa: PT-BR, frase completa, sem emoji nem travessão longo, factual e calmo; corte enrolação, não contexto. Comece pelo que é verdade ou pelo que fazer; explique código por o que acontece, por que e impacto. Artefato vivo guarda lógica e trilha, não só recap; o chat dá o path gravado e um resumo factual. Número, n, slug e path só com sustentação no disco ou no humano; chute vira GUESS explícito.

### 6. Verificação

- A prova de mudança na prosa é a revisão de consistência dos Comandos do projeto, a review independente de qualidade da skill e, por fim, o uso real numa phase com `/vibeflow`; a de script é `node --test`.
- Testes automatizados só para scripts; nenhum teste confere palavras, frases ou seções de `SKILL.md`, referências, templates ou documentação.

### 7. Ordem para mudar a skill

`skills/vibeflow/references/disco.md` quando o contrato de disco muda; depois `skills/vibeflow/SKILL.md`, referências e templates; por fim `README.md`, quando instalação ou uso mudam. Não inverter: etapa sem contrato de disco vira path inventado.

### Limites permanentes deste repo

- Segunda skill instalável, alias de comando ou motor que conduz etapa no lugar do líder.
- Skill que entra sem chamada explícita (seção 4).
