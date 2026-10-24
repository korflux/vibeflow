# Review: testes locais leves, E2E paralelo e orçamento de duração
# Alvo: phase-5-testes-leves-sem-docker
# Status: aprovado

## Veredito

- [x] **Approve**: critérios atendidos e provados, regressão verde e nenhum Critical ou Required aberto
- [ ] **Request changes**: há Critical ou Required aberto

## Critérios de aceite

Entrega só de prosa: a prova de cada critério é a revisão de consistência do item 4 da Regressão completa do plan (`AGENTS.md`, Regras deste repo, seção 8), mais `node --test` verde.

| Critério | Evidência (teste e resultado) | Situação |
|---|---|---|
| A1 | `references/testes.md:1-45` é a casa; `implement.md:98-100` virou ponteiro; `plan.md:25,27`, `review.md:40,47`, `delegation.md:75,86`, `definition-of-done.md:11`, `analyze/coverage.md:21` e os dez perfis apontam para ela. Busca por regra de teste fora de `testes.md` só acha ponteiros e a mecânica do checkpoint em `implement.md:43`, que `testes.md:3` mantém na etapa. Corpos dos cinco papéis idênticos entre Claude e Codex (comparação por script). | atendido |
| A2 | `testes.md:17-20`: nativo ou embutido, Docker no CI, sinais de Docker, pergunta única com registro em Ambiente; `templates/AGENTS.md:38-39`. Registro pelo plan vira passo 1 de infraestrutura com `Arquivos:` no `AGENTS.md` do projeto e commit `task` (`plan.md:22`, `testes.md:20`), fechado na Etapa 2 (R1). | atendido |
| A3 | `testes.md:27-39`: só jornadas com tela, isolamento (a)/(b)/(c) escolhido no plan, sem cadeia de estado global, autenticação por worker, sem espera fixa, build reaproveitado com build de produção só na regressão completa; `plan.md:22`, `templates/plan.md:8`, `analyze/coverage.md:18`. | atendido |
| A4 | `testes.md:22-25`: regra de negócio em unitário ou integração sem navegador; E2E só confirma a jornada. | atendido |
| A5 | `templates/AGENTS.md:33` (orçamento) e `:38-39` (Docker); `review.md:39-40,72,78` (duração por nível, total, alarme em `.erros-encontrados/` sem bloquear); `testes.md:41-45` (padrão de 10 minutos); `templates/review.md:59`. Linha do orçamento só com declaração (`templates/AGENTS.md:33`, `init.md:27`), fechado na Etapa 2 (R2). | atendido |
| A6 | `init.md:15,27`: orçamento declarado ou comentário do padrão, detecção de Docker pelos sinais de `testes.md`, evidência ao líder, pergunta com recomendação, resposta e data em Ambiente; `SKILL.md:11` para o encadeamento na pergunta. | atendido |
| A7 | `AGENTS.md:57` (5.1.0) e `:91` (Estrutura com `references/testes.md`); `README.md:97-104` (Novidades da 5.1.0). | atendido |

## Achados

### Required

- [x] R1: **Required** - `skills/vibeflow/references/plan.md:22` - a decisão sobre Docker perguntada no plan é gravada no `AGENTS.md` do projeto pelo líder, mas plan não commita (`AGENTS.md` deste repo, seção 6) e nenhum formato de `references/disco.md` (Commits) cobre esse registro. A alteração fica suja fora de `.vibeflow/` durante toda a phase: cai em "Alteração não commitada ... sem dono no disco" (`references/disco.md:134`) a cada retomada e bloqueia a regressão da review (`references/review.md:38`), antes da finalização que faria o staging de `AGENTS.md`. Em projeto já inicializado com Docker nos testes, a phase fica sem saída. - remédio: em `references/plan.md` (passo 2) e `references/testes.md:19-20`, fazer o plan registrar a resposta do humano num passo de infraestrutura (`Aceite: nenhum`, `Arquivos: AGENTS.md`), primeiro do plan, que grava a seção Ambiente e é commitado como `task(<alvo>:1)`; manter o init como está, porque ele commita a governança - prova: revisão de consistência entre `plan.md`, `testes.md`, `disco.md` (Commits e Estado da phase) e `review.md` passo 1 - papel: redator

### Nit

- [x] R2: **Nit** - `skills/vibeflow/templates/AGENTS.md:34` - a linha `Orçamento da regressão completa: <minutos>` fica fora de comentário, e `references/init.md:27` só manda "deixar o comentário" sem declaração; o `AGENTS.md` consumidor fica com o placeholder literal, e a review precisa adivinhar que `<minutos>` significa "sem declaração" - remédio: em `init.md:27`, mandar apagar a linha sem declaração (ou mover a linha para dentro do comentário do template) - prova: revisão de consistência entre o template e `init.md` - papel: redator
- [x] R3: **Nit** - `skills/vibeflow/references/testes.md:20` - "no init, em projeto novo" contradiz `init.md:27`, que detecta Docker em qualquer init, inclusive de projeto existente que ainda não tinha `.vibeflow/` - remédio: trocar por "no init e no plan, quando a decisão não está registrada" - prova: revisão de consistência entre `testes.md` e `init.md` - papel: redator

## Notas

- Paths alterados: todos dentro dos `Arquivos:` dos passos, além dos artefatos da phase.
- Commits coerentes com os passos: `f430668` (1), `3fb7539` (2a, 2b, 2c), `ea170ac` (correção devolvida pelo checkpoint de 1, 2a, 2b, 2c), `40f83f0` (3). A marcação do checkpoint segue no commit `40f83f0` com o passo 3. Nenhum commit de outro alvo no intervalo.
- Projeto que só usa a rota medium não passa por plan; com init anterior à 5.1.0 e Docker nos testes, a pergunta da decisão 1 só chega na próxima phase high. Informação sem remédio exigido pela spec.
- Primeira tentativa da regressão foi interrompida antes do fim por defeito no script de medição do revisor (calculadora `bc` ausente no shell), sem falha de comando; a execução válida é a registrada abaixo.
- Varredura de paths citados em `skills/vibeflow/`, `README.md` e `AGENTS.md`: nenhum ausente. Nenhuma citação vigente de v1, rotas antigas, `ondas.mjs`, corretor ou finalizador fora de compatibilidade.

## Aprovação humana

- [x] Aprovação humana (confirmou no chat o resumo do líder), 24/10/2026: "Aprovo a review da phase-5 e autorizo o push."

## Etapas

### Etapa 1 - review - 7a15309..HEAD

- Regressão: `git diff --check` verde; `node --test` verde (60 de 60); `gitleaks detect --source . --redact --no-banner` verde (no leaks found); revisão de consistência (item 4) feita, com R1 a R3; HEAD `40f83f0d77d4fb143f60993ea7bfc1629868df56`
- Duração: `git diff --check` 0,1 s; `node --test` 80,1 s; gitleaks 1,1 s; total 81,7 s (sem E2E; revisão de consistência manual não cronometrada) · orçamento: 10 minutos, padrão de `references/testes.md` (o `AGENTS.md` deste repo não declara); dentro do orçamento, sem registro
- Abriu: R1, R2, R3
- Veredito: Request changes

### Etapa 2 - re-review - R1 (R2 e R3 conferidos pela prova afetada)

- Diff da correção: 40f83f0..6a5b568 (`task(phase-5:R1,R2,R3)`); IDs do commit iguais aos R* marcados `[x]` desde a Etapa 1 (R1, R2, R3)
- R1: `references/plan.md:22` faz a resposta virar o passo 1 do plan, de infraestrutura (`Aceite: nenhum`, `Arquivos:` com o `AGENTS.md` do projeto, `Prova: git diff --check`), gravado pelo redator no implement e commitado como os demais passos; `references/testes.md:20` separa o init (commit de governança) do plan. Consistência conferida: o `AGENTS.md` não fica sujo entre plan e implement; durante o implement a alteração tem dono em `Arquivos:` de passo aberto (`disco.md:134`); o perfil do redator permite escrever `AGENTS.md` declarado em `Arquivos:`; o commit segue `disco.md` (Commits); a review encontra a árvore limpa (`review.md:38`); `plan.md` passo 4 já prevê `Aceite: nenhum` para infraestrutura; `SKILL.md:11` continua correto. Fechado.
- R2: `templates/AGENTS.md:33` move a linha do orçamento para o comentário e `init.md:27` manda não escrevê-la sem declaração; coerente com `review.md:40` e `testes.md:43`. Prova afetada `git diff --check` verde.
- R3: `testes.md:20` passa a dizer "no init e no plan, quando a decisão não está registrada", coerente com `init.md:27`. Prova afetada `git diff --check` verde.
- Regressão: correção só de prosa, sem código compartilhado; a regressão completa não roda de novo (`review.md`, passo 4 da re-review). Para a cobertura do HEAD final: `git diff --check 40f83f0 HEAD` verde e `gitleaks detect --source . --redact --no-banner` verde (no leaks found, 0,7 s); `node --test` não rodou de novo porque nenhum script nem teste mudou; HEAD `6a5b568c998adf4255bcfc53ecfd13a2aa2c34cb`
- Fechou: R1 (R2 e R3 fecham na conferência do líder)
- Abriu: nenhum
- Veredito: Approve
