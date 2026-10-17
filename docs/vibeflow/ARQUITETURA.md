# vibeflow, arquitetura

Contrato da skill única `vibeflow` 10.0.0, um pacote só texto. Este documento fixa o que é contrato: pacote, disco, papéis e ownership, gates por rota, implementação por ondas, leitura de phases v1, distribuição e limites. As regras operacionais moram no pacote, e cada seção aponta a casa delas sem repeti-las. A run de ponta a ponta e as decisões de desenho ficam em `ANALISE.md`.

## 1. Pacote

```text
skills/vibeflow/
  SKILL.md                              entrada única do líder
  references/<etapa>.md                 uma referência por etapa
  references/<etapa>/                   catálogos da etapa, lidos sob demanda
  references/disco.md                   regras mecânicas do disco
  references/delegation.md              papéis, brief e relatório fixo
  templates/<artefato>.md               esqueleto de cada artefato vivo
  templates/AGENTS.md                   modelo das regras do projeto consumidor
  templates/agents/<host>/<papel>       perfis de subagente por host
```

- `skills/vibeflow/` é pasta real, sem symlink, e é o único pacote instalável.
- O pacote não contém scripts, código executável nem testes, e não depende de interpretador.
- Etapas da allowlist: `init`, `interview`, `spec`, `design`, `plan`, `analyze`, `implement`, `review`.
- Entrada: `/vibeflow` sem argumento ou auto-invoke pela `description` do `SKILL.md`; `/vibeflow <etapa>` vai direto a uma etapa da allowlist. Argumento fora dela é recusado com a allowlist nomeada.
- `docs/` não é instalado.

## 2. Disco

```text
AGENTS.md                                   fonte única de regras do projeto
.agents/rules/vibeflow.md                   ponte Antigravity, conteúdo exato @../../AGENTS.md
.claude/agents/<papel>.md                   perfis de subagente Claude
.codex/agents/<papel>.toml                  perfis de subagente Codex
.vibeflow/old/                              cópias conferidas de arquivos de regra substituídos
.vibeflow/phases/phase-<n>-<slug>/<artefato>
.vibeflow/mvp/<artefato>                    baseline único de projeto novo
```

Artefatos de uma phase ou do MVP: `interview.md`, `spec.md`, `design.md`, `plan.md`, `analyze.md` e `review.md`. O nome do arquivo é o tipo, nunca o título. Paths e nomes são os da v1; mudá-los quebra contrato e exige versão major.

| Item | Contrato |
|---|---|
| `n` | Maior `n` existente em `.vibeflow/phases/` mais 1, em ordem numérica; 1 sem phases; sem zero à esquerda. |
| slug | `a-z0-9` e hífen, de 2 a 48 caracteres. |
| Pasta | O líder fixa `n` e slug no brief; quem grava o primeiro artefato cria a pasta. Mesmo pedido grava na mesma pasta, outro arquivo; pedido novo abre a próxima. Pasta criada não é renomeada. |
| MVP | Um por repositório, sempre na rota max, sem `n` nem slug. Concluído, não é sobrescrito, movido nem versionado; pivô entra como phase max. |
| Artefato existente | Editado no lugar e nunca recriado a partir do template. |
| Arquivo de regra do usuário | Substituído somente depois de um commit que o contenha ou de uma cópia em `.vibeflow/old/` com tamanho e hash conferidos. |
| `# Status:` | Linha do cabeçalho de cada artefato. Nasce `rascunho`; vira `aprovado` somente depois da aprovação humana, marcada pelo finalizador. |
| `# Rota:` | Gravada uma vez no cabeçalho do primeiro artefato da phase: `interview.md` em xhigh, max e MVP; `spec.md` em high; `review.md` em medium, que abre a phase na review. Não muda; pedido maior abre outra phase. |
| `# Protocolo:` e `# Modo:` | Não existem em plans da V2; o modo, com ou sem subagentes, é decidido na run. Só aparecem em plans de phases v1. |

Casa das regras mecânicas (cálculo de `n`, sanitização do slug, cabeçalhos, backup e colisão em `.vibeflow/old/`): `skills/vibeflow/references/disco.md`. A forma de cada artefato: `skills/vibeflow/templates/`.

Sem `.vibeflow/`, numa rota que exige cadeia, a primeira etapa é `init`. Pedido Express ou low sem phase ativa não cria `.vibeflow/`, phase nem artefato.

Commitável: `AGENTS.md`, ponte, perfis instalados, `.vibeflow/phases/`, `.vibeflow/mvp/` e `.vibeflow/old/`. A V2 não grava relatório operacional nem registro estruturado de execução; o estado vive nos artefatos e no Git.

## 3. Papéis e ownership

| Papel | Escreve | Não faz |
|---|---|---|
| Líder | Conversa com o humano: briefing, perguntas, restate, aprovações e confirmação final. No máximo pequenos ajustes finais. | Código, artefato, Git, `analyze.md`, `review.md` em host com subagentes |
| Explorador | Nada; devolve leitura ampla e evidências | Escrita |
| Redator | Prosa de `interview.md`, `spec.md`, `design.md`, `plan.md` e T* cujo resultado principal é prosa | Código e Git |
| Implementador | Código e testes da T* delegada | Artefato de planejamento e Git |
| Verificador | Nada; certifica a integração e executa provas | Corrigir código ou teste |
| Corretor | Correção de falha pré-review ou de R* com `papel: corretor` | Certificar a própria correção |
| Revisor | `analyze.md` e `review.md`, com contexto limpo | Certificar código próprio, Git |
| Finalizador | Estado no `plan.md`, marcas de status aprovadas pelo humano, índice Git, commits e push confirmado | Decidir aprovação |

Instalação de ferramenta necessária à prova segue `skills/vibeflow/references/delegation.md`. Cada recurso compartilhado tem um único dono por vez; durante uma onda, cada T* tem ownership exclusivo dos seus `Arquivos:`. Na etapa init os perfis podem ainda não existir, e ela é executada por agente genérico apto a Git. Casa: `skills/vibeflow/references/delegation.md` para papéis e relatório fixo; `skills/vibeflow/references/init.md` para a etapa 0.

Host sem subagentes opera em Modo B: o líder executa inline uma etapa ou uma T* por run, e analyze e review rodam em chat novo, que atua como visão de fora. O Modo B também vale quando o humano pede uma T* por run.

## 4. Rotas e gates

A rota vem da tabela de esforço do `AGENTS.md`, única fonte; o valor gravado em `# Rota:` é `medium`, `high`, `xhigh`, `max` ou `mvp`. Express e low nunca abrem phase. Design entra entre spec e plan somente com UI visível; sem UI visível, a etapa fecha com `Design: N/A` e motivo registrados, sem `design.md`.

Antes de cada etapa, o líder confere o pré-requisito pela `# Rota:` gravada e pelas linhas `# Status:`. Etapa sem pré-requisito é recusada com o pré-requisito e o path nomeados. Invariantes de contrato:

- Plan exige spec aprovada.
- Implement em `high` ou acima exige plan aprovado; em `max` e MVP, também analyze aprovado com veredito `limpo`.
- Review exige as T* concluídas com commit ou, em `medium`, o diff entregue.
- Phase fechada: `review.md` aprovado e nenhum R* aberto.

Casa da tabela completa de pré-requisitos: `skills/vibeflow/SKILL.md`, seção 3. Casa do estado de etapa e de T* concluída: `skills/vibeflow/references/disco.md`.

## 5. Implementação por ondas

- O `plan.md` aprovado define o trabalho: cada T* tem linha de conclusão, `Deps:`, `Arquivos:` e `Prova afetada:`, e o plan tem uma única `Regressão completa`.
- Onda: T* abertas com todas as `Deps:` concluídas e `Arquivos:` disjuntos, despachadas juntas. T* sem `Arquivos:` ou sobreposta roda sozinha. O líder calcula a onda lendo o plan; as regras de `Arquivos:` moram em `skills/vibeflow/references/plan.md`.
- Implementador e verificador provam somente a `Prova afetada:` de cada T*. A review final é a única dona da `Regressão completa`.
- Depois da prova integrada verde, o finalizador marca as caixas das T* comprovadas, atualiza o resumo do `plan.md` (pronto, em andamento, pendente) e cria o commit `task(T1,T2,...): <resultado>` com staging explícito.
- O diff julgado pela review vai do commit anterior ao primeiro `task(...)` da phase até `HEAD`.
- R* volta ao corretor ou ao redator pelo campo `papel:`, com até duas rodadas antes de parar e relatar; correção comprovada recebe commit `task(Rn,...): <resultado>`.
- Aprovação da review, publicação de decisões vigentes e push exigem uma confirmação humana explícita, que o líder transmite ao finalizador.
- Não existe registro estruturado de execução: o estado é o `plan.md`, e o histórico e a evidência de commit são o Git.

Casa: `skills/vibeflow/references/implement.md` e `skills/vibeflow/references/review.md`.

## 6. Phases v1

Phases criadas pela v1 (plans com `# Protocolo: etapas-v1`, `# Protocolo: coordenacao-v1` ou sem marcador) são lidas como estão, sem migração nem reescrita. O estado vem das linhas de status, das caixas de conclusão do `plan.md` e do Git. O registro JSON de execução que a v1 gravava na pasta da phase é preservado e não é interpretado. Phase sem `# Rota:` é phase v1: não ganha rota retroativa, e seus gates seguem os artefatos presentes. Casa: `skills/vibeflow/references/disco.md` (seção Phases da v1) e `skills/vibeflow/SKILL.md` (seção 3).

## 7. Distribuição

Os manifestos `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `.grok-plugin/marketplace.json` e `plugin.json` entregam somente a skill `vibeflow`, versão 10.0.0 onde o schema tem versão. Nenhum manifesto ou README referencia os pacotes ou comandos da v1, e não há alias. Instalação por `npx skills add korflux/vibeflow` ou pelos marketplaces nativos, descrita no `README.md`.

## 8. Limites

- O pacote é só texto. Operação mecânica é regra escrita, aplicada pela IA e auditada no disco e no Git.
- A rota é gravada uma vez e não muda.
- O líder não escreve `analyze.md` nem `review.md` em nenhum host.
- Nada migra ou reescreve artefato existente.
- `AGENTS.md` é a única fonte de regras: o pacote não cria `CLAUDE.md`, `REGRAS.md` nem `GEMINI.md`.
- A tabela `## Decisões vigentes` do `AGENTS.md` só muda depois de implementação, review aprovada e confirmação humana.
- Push, aprovação de review e publicação de decisões vigentes exigem confirmação humana explícita.
