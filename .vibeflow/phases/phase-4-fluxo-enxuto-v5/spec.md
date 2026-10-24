# Spec: fluxo enxuto com aprovação única, plan como tracking e testes por critério
# Alvo: phase-4-fluxo-enxuto-v5
# Status: aprovado
# Rota: high

## Objetivo

A skill `vibeflow` passa a entregar uma phase com uma única aprovação humana antes do código, menos artefatos, menos handoffs e menos execução repetida de testes, preservando a interview, o olhar independente do analyze e da review e a retomada pelo disco. Quem opera é o humano que chama `/vibeflow` e o líder que conduz a phase. Sucesso é uma phase real num projeto consumidor chegar da spec aprovada ao push sem etapas de aprovação intermediárias, com a regressão completa rodando uma vez quando a review não abre Critical nem Required, e sem a skill entrar em pedidos em que o humano não a chamou. É uma mudança major (5.0.0).

## Cobertura da origem

Origem: a conversa de 2026-10-24 com o humano, que fez o papel da interview, e a medição dos projetos consumidores (aion, kastir, editor) feita nela.

| Origem | Destino na spec | Motivo se fora/N/A |
|---|---|---|
| Pós-implement lento: rodadas de review com regressão completa repetida | Decisões 6 e 7; A6 a A8 | N/A |
| Laço de flakes no kastir phase-4 (cinco etapas de review) | Decisão 7; A8 | N/A |
| Artefatos longos que ninguém lê (média de 2 a 4 mil palavras cada) | Decisões 1 e 2; A1 e A2 | N/A |
| Ordem aleatória das T* e plan que não serve de tracking | Decisão 3; A3 | N/A |
| Analyze com achados reais (25 de 30 encontraram algo) | Decisão 4; A4 | N/A |
| Testes como 62% a 76% do diff | Decisão 6; A7 | N/A |
| Skill entrando sem ser chamada | Decisão 9; A10 | N/A |
| E2E serial do aion por banco compartilhado | Fora | Problema do projeto aion, não da skill |

## Suposições e decisões

Decisões fechadas pelo humano:

1. **Aprovação única.** A única aprovação humana antes do código é a da `spec.md`. Plan e analyze não pedem aprovação. Aprovar a review e fazer push continuam exigindo confirmação humana. (processo)
2. **Um arquivo antes do código.** A interview não grava artefato próprio e escreve direto na `spec.md`, com cinco seções: objetivo, pontos do projeto encontrados pela exploração do código com o que cada um implica, decisões do humano com a pergunta que originou cada uma, critérios de aceite numerados e verificáveis, e fora do escopo. A interview começa explorando o código que o pedido toca e pergunta a partir disso. A meta é a spec caber em uma ou duas telas. (processo)
3. **Plan como tracking.** O `plan.md` é um checklist na ordem real de execução (1, 2a, 2b, 3), um passo por linha com arquivos, prova e critério de aceite que entrega. Passos paralelos dividem o número com letras e não tocam os mesmos arquivos. O estado é só a caixa, marcada no commit `task(phase-N:2a,2b)`. Saem os IDs T*, as linhas `Estado:` e `Resumo:` e as seções de risco e cobertura. A retomada continua pelo disco. (processo)
4. **Analyze silencioso.** O analyze roda em toda phase com plan, sempre em contexto limpo (subagente ou chat novo). Ele confere spec, plan e código, corrige o plan direto e registra os achados numa seção curta no fim do `plan.md` (achado, onde, ajuste). Não há `analyze.md` nem aprovação. Achado que muda uma decisão do humano na spec para e pergunta. (processo)
5. **Papéis do implement.** O implementador coda, escreve os testes e roda a prova do passo. O líder nunca coda nem roda teste: confere se os arquivos alterados batem com o passo, marca a caixa e commita. Falha de prova volta ao mesmo implementador. O plan marca checkpoints depois de grupos de passos que fecham um ou mais critérios; no checkpoint, um verificador de contexto limpo roda as provas do grupo e confere o diff contra a spec. Phase pequena não tem checkpoint. A review roda no final. Sai o verificador por passo e por onda. (processo)
6. **Política de testes.** Cada critério de aceite tem pelo menos um teste que o prova, de preferência percorrendo o fluxo. Teste novo só para critério não coberto ou risco concreto (erro, borda, segurança, dinheiro); antes de criar, o implementador procura e estende um teste existente. No passo, rodam só os testes afetados, pelo grafo de imports da ferramenta do projeto (como `vitest run --changed <base>`), sem E2E. No checkpoint, os testes do grupo e o E2E só dos critérios com tela. A regressão completa roda uma vez na review, em segundo plano enquanto o revisor lê o diff, do mais barato ao mais caro (lint e tipos, unitários, E2E), parando na primeira falha; após correção, reroda primeiro só o que falhou. Teste que falha e passa na reexecução é flake: vai para `.erros-encontrados/` e não bloqueia. (processo)
7. **Review focada em produto.** A review julga cada critério de aceite atendido e provado, defeitos no código alterado, e segurança e banco quando o diff toca essas superfícies. Todo achado é resolvido. Só Critical e Required passam por re-review; Nit e afins fecham com os testes afetados verdes. A re-review julga só o diff da correção e só reroda a regressão completa se a correção tocou código compartilhado. Achado fora do recorte vai para `.erros-encontrados/` pelo revisor e não bloqueia. Path fora do plan e coerência de commits viram nota, nunca achado. No máximo duas rodadas de correção; sem convergência, o líder traz os achados restantes ao humano. Na confirmação final, o líder resume no chat o feito, o corrigido e os Critical, e o humano confirma o push sem ler o `review.md`. (processo)
8. **Três rotas.** `low`: implement direto com prova proporcional, sem phase. `medium`: implement e review, para comportamento novo pequeno sem banco nem risco de regressão de backend. `high`: interview, spec (aprovação), plan com analyze, implement com checkpoints e review. O marcador `risco` na high vale para auth, autorização, pagamento, segredo, perda de dados ou produção: não acrescenta etapa, mas obriga a interview a cobrir modelo de ameaça e rollback, o plan a pôr checkpoint depois de cada grupo de risco e a review a abrir segurança e banco. A interview tem tamanho proporcional à clareza do pedido. MVP é a high com `risco`, em `.vibeflow/mvp/`. Saem as rotas Express, xhigh e max. (processo)
9. **Só por chamada explícita.** A skill roda só quando o humano a chama. Claude Code: `disable-model-invocation: true` no frontmatter. Codex: `agents/openai.yaml` com `policy.allow_implicit_invocation: false`. Antigravity e Grok, sem mecanismo confirmado: `description` sem gatilhos de comportamento, dizendo para usar só com `/vibeflow`. O bloco da cadeia no `AGENTS.md` do projeto consumidor diz que a cadeia vale só com `/vibeflow`; fora disso, o agente trabalha direto. (processo)

Suposições do líder, a confirmar nesta aprovação:

10. **Design sai como etapa.** Saem `references/design.md`, `references/design/` e `templates/design.md`. Decisões visuais do humano viram perguntas da interview. `references/review/ui-visual-quality.md` e `references/chrome-devtools.md` ficam como referência do implementador e do revisor. (escopo)
11. **Corretor e finalizador saem.** Achado de review de código vai ao implementador; de prosa, ao redator. O líder faz marcações, commits e a finalização confirmada. Ficam explorador, implementador, redator, verificador (só checkpoint) e revisor (analyze e review). (processo)
12. **Phases antigas.** Phases fechadas no formato antigo ficam intocadas e o `estado.mjs` as reconhece como fechadas. Phase aberta no formato antigo num projeto consumidor é fechada com a versão anterior antes de atualizar a skill. (escopo)
13. **Mantidos sem mudança de regra:** Modo B, ajuste de phase, decisões vigentes, init e backups, ajustados só no que as decisões acima tocarem. (escopo)

## Escopo e comportamento

### 1. Fluxo F*: N/A

N/A: a entrega é a prosa, os templates e os scripts de uma skill, sem UI. Os fluxos operacionais estão nas decisões 1 a 9.

### Fora

- Corrigir o E2E serial do aion (banco por worker): é trabalho do projeto aion, em phase própria lá.
- Migrar phases antigas dos projetos consumidores para o formato novo: as fechadas ficam como estão (suposição 12).
- Medir tempo automaticamente dentro da skill: a evidência de sucesso vem do uso real e do Git.
- Novas ferramentas de teste: a skill usa o que o projeto já tem; sem grafo de imports, vale a lista de testes do passo.

## Checklist de entrega

### Aceite

- [ ] A1: Numa phase high, a única aprovação humana pedida antes do código é a da `spec.md`.
- [ ] A2: A phase high grava antes do código só `spec.md` e `plan.md`, sem `interview.md`, `design.md` ou `analyze.md`, e a spec tem as cinco seções da decisão 2.
- [ ] A3: O `plan.md` numera os passos na ordem de execução, com paralelos por letra, e o estado de cada passo é só a caixa.
- [ ] A4: O analyze roda em contexto limpo em toda phase com plan, sem aprovação, e registra os achados no fim do `plan.md`.
- [ ] A5: Em nenhuma etapa o líder edita código ou executa teste; checkpoints marcados no plan são executados por verificador de contexto limpo.
- [ ] A6: Review sem Critical nem Required aberto termina com uma única execução da regressão completa.
- [ ] A7: As referências instruem testes por critério de aceite, reaproveitamento de teste existente e testes afetados pelo grafo de imports.
- [ ] A8: Flake e achado fora do recorte vão para `.erros-encontrados/` sem bloquear o Approve; path fora do plan vira nota.
- [ ] A9: A tabela de esforço tem só `low`, `medium` e `high`, com o marcador `risco`, e `# Rota:` aceita `medium`, `high` e `mvp`.
- [ ] A10: No Claude Code e no Codex, a skill não é invocada sem `/vibeflow` ou `$vibeflow`; o bloco da cadeia do template `AGENTS.md` restringe a cadeia à chamada explícita.
- [ ] A11: `estado.mjs` e o substituto de `ondas.mjs` leem o plan novo, reconhecem phases fechadas antigas e têm testes em `tests/scripts/`.
- [ ] A12: `AGENTS.md` deste repo, `README.md` e a versão refletem o contrato 5.0.0.

### Critérios de sucesso

- [ ] C1: `node --test` passa e a revisão de consistência dos Comandos do projeto não acusa path inexistente nem referência à cadeia antiga.
- [ ] C2: A primeira phase real conduzida com a 5.0.0 num projeto consumidor chega ao push com uma aprovação de artefato e sem regressão completa repetida sem Critical ou Required.
- [ ] C3: O pacote `skills/vibeflow/` fica menor em palavras que o atual (cerca de 30 mil de prosa), medido por ferramenta.

## Contratos e restrições necessárias

- Dados e invariantes: o disco e o Git continuam a fonte do estado; artefato vivo é editado no lugar; scripts só leem.
- Integrações e interfaces: frontmatter do `SKILL.md` (Claude Code), `agents/openai.yaml` (Codex), ponte `.agents/rules/vibeflow.md` (Antigravity) sem mudança de forma.
- Segurança e operação: N/A. A skill não processa entrada externa nem segredo; as regras de segurança do código consumidor ficam como estão.
- Tecnologia imposta: scripts em Node 18+ sem dependência, conforme a seção 4 das regras do repo.
- Consumidores: os projetos consumidores com phases fechadas (aion, atendimento-korflux, campaignK, editor, flow, kastir, lyos, monitorcontabil, sirsimon).

## Como provar

| Aceite | F* ou jornada | Nível | Evidência esperada |
|---|---|---|---|
| A3, A11 | scripts de leitura | local | testes de comportamento em `tests/scripts/` com disco temporário no formato novo e no antigo fechado |
| A1, A2, A4 a A10, A12 | prosa e templates da skill | local | revisão de consistência e review independente de qualidade da skill |
| C2 | phase real num consumidor | jornada | commits e artefatos da phase mostrando uma aprovação e uma regressão completa |

## Boundaries

### Always

- Mudar `references/disco.md` primeiro, depois `SKILL.md`, referências e templates, depois `README.md`.
- Manter a retomada pelo disco e o olhar de contexto limpo no analyze, no checkpoint e na review.

### Ask first

- Remover qualquer referência ou script além dos citados nas decisões e suposições.
- Tocar arquivos dos projetos consumidores.

### Never

- Push sem confirmação humana explícita.
- Criar segunda skill, alias de comando ou segunda fonte de regras.

## Handoff

plan, com `Design: N/A`: a entrega não tem UI.

- Chat: com a aprovação, o plan segue neste chat com `/vibeflow plan`. Em chat pesado, um chat novo com `/vibeflow` retoma pela etapa gravada.

- [x] Aprovação humana (leu o arquivo e confirmou), 24/10/2026: "Aprovado a spec da phase-4, incluindo as suposições 10 a 13. Pode ir pro plan."
