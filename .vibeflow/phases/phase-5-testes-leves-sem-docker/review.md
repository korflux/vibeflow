# Review: testes locais leves, E2E paralelo e orçamento de duração
# Alvo: phase-5-testes-leves-sem-docker
# Status: request-changes

## Veredito

- [ ] **Approve**: critérios atendidos e provados, regressão verde e nenhum Critical ou Required aberto
- [x] **Request changes**: há Critical ou Required aberto

## Critérios de aceite

Entrega só de prosa: a prova de cada critério é a revisão de consistência do item 4 da Regressão completa do plan (`AGENTS.md`, Regras deste repo, seção 8), mais `node --test` verde.

| Critério | Evidência (teste e resultado) | Situação |
|---|---|---|
| A1 | `references/testes.md:1-45` é a casa; `implement.md:98-100` virou ponteiro; `plan.md:25,27`, `review.md:40,47`, `delegation.md:75,86`, `definition-of-done.md:11`, `analyze/coverage.md:21` e os dez perfis apontam para ela. Busca por regra de teste fora de `testes.md` só acha ponteiros e a mecânica do checkpoint em `implement.md:43`, que `testes.md:3` mantém na etapa. Corpos dos cinco papéis idênticos entre Claude e Codex (comparação por script). | atendido |
| A2 | `testes.md:17-20`: nativo ou embutido, Docker no CI, sinais de Docker, pergunta única com registro em Ambiente; `templates/AGENTS.md:39-40`. O registro feito no plan não tem commit nem dono no disco (R1). | parcial |
| A3 | `testes.md:27-39`: só jornadas com tela, isolamento (a)/(b)/(c) escolhido no plan, sem cadeia de estado global, autenticação por worker, sem espera fixa, build reaproveitado com build de produção só na regressão completa; `plan.md:22`, `templates/plan.md:8`, `analyze/coverage.md:18`. | atendido |
| A4 | `testes.md:22-25`: regra de negócio em unitário ou integração sem navegador; E2E só confirma a jornada. | atendido |
| A5 | `templates/AGENTS.md:33-34` (orçamento) e `:39-40` (Docker); `review.md:39-40,72,78` (duração por nível, total, alarme em `.erros-encontrados/` sem bloquear); `testes.md:41-45` (padrão de 10 minutos); `templates/review.md:59`. Placeholder do orçamento sem regra de remoção (R2). | atendido |
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

- [ ] Aprovação humana (confirmou no chat o resumo do líder)

## Etapas

### Etapa 1 - review - 7a15309..HEAD

- Regressão: `git diff --check` verde; `node --test` verde (60 de 60); `gitleaks detect --source . --redact --no-banner` verde (no leaks found); revisão de consistência (item 4) feita, com R1 a R3; HEAD `40f83f0d77d4fb143f60993ea7bfc1629868df56`
- Duração: `git diff --check` 0,1 s; `node --test` 80,1 s; gitleaks 1,1 s; total 81,7 s (sem E2E; revisão de consistência manual não cronometrada) · orçamento: 10 minutos, padrão de `references/testes.md` (o `AGENTS.md` deste repo não declara); dentro do orçamento, sem registro
- Abriu: R1, R2, R3
- Veredito: Request changes
