# vibe-analyze, arquitetura

`/vibe-analyze` cruza interview, spec e plan do mesmo alvo, mais `design.md` quando há UI visível, registra a certificação de consistência e encaminha para implementação. A IA faz a análise semântica e corrige lacunas óbvias em `spec.md`, `design.md` ou `plan.md`; o motor inventaria predecessores e prepara `analyze.md`.

```text
.vibeflow/phases/phase-<n>-<slug>/analyze.md
.vibeflow/mvp/analyze.md
```

## 1. Papéis e ownership

| Peça | Responsabilidade |
|---|---|
| `SKILL.md` | Cruzar fontes, resolver achados, perguntar ambiguidades reais e definir o veredito. |
| `scripts/analyze.py`, `analyze.ps1`, `analyze.sh` | Inventário, validação de predecessores, preparação do vivo e JSON operacional no stdout. |
| `references/coverage.md` | Taxonomia de passes e severidades, consultada sob demanda. |
| `stdout (JSON)` | Evidência operacional transitória, consumida na mesma execução. |
| `analyze.md` | Certificação viva e commitável. |

## 2. Dependências e alvo

Sem `.vibeflow/`, `INIT_AUSENTE`. No modo phase, o alvo é a maior phase com `spec.md` e `plan.md` sem `analyze.md`, ou uma análise já existente para atualização. `--dir` exige uma phase com os predecessores. Não é criada uma phase nova.

No modo MVP, `--mvp` exige `interview.md`, `spec.md` e `plan.md` em `.vibeflow/mvp/`, recusa `--dir` e mantém o gate de decisões críticas. Não há `n` novo.

## 3. JSON operacional no stdout

O JSON transitório contém `vibeflow`, `phases`, `next_n`, `existing`, `plan_pendente`, `rascunho`, `alvo`, `mvp`, `modo_sugerido`, `created`, `modo`, `actions` e `avisos`. `files` lista os artefatos vivos.

`actions` registra apenas criação de infraestrutura ou do arquivo vivo. Não existe estado de transporte temporário no JSON.

## 4. Apply e escrita direta

1. Reexecuta o inventário.
2. Valida `plan.md`, `spec.md` e, no MVP, `interview.md`.
3. Prepara `analyze.md` vazio quando ausente.
4. Preserva bytes do `analyze.md` existente.
5. Emite o JSON operacional no stdout para leitura imediata da IA.
6. A IA escreve ou atualiza diretamente o certificado, mantendo `# Status: rascunho` até o veredito ser revisado.

O motor não corrige as fontes, não escreve prosa e não publica decisões vigentes. A IA pode aplicar patches corretivos em `spec.md`, `design.md` e `plan.md` quando a análise encontrar erro óbvio, registrando o path e a resolução no vivo.

## 5. Conteúdo e veredito

Seções: Fontes, Cobertura, Achados, Clarificações, Constituição, Métricas, Veredito e Handoff. Finding precisa de path e evidência. Veredito `limpo` encaminha para `vibe-implement`; `bloqueado` volta para a skill dona.

Em MVP, conflito crítico sem `substitui` explícito bloqueia. `analyze.md` não altera a tabela de decisões vigentes em `REGRAS.md`.

## 6. Investigação, chat e testes

A IA começa pela pergunta de consistência, localiza entradas com `rg --files`, procura A*/C*, T*, IDs e comandos com `rg -n` e abre somente as dependências do cruzamento. O inventário não autoriza ler a árvore inteira.

Recomenda-se novo chat para analyze. Continuidade no mesmo chat é uma escolha consciente; o `analyze.md` vivo e o handoff são a ponte.

Suítes: `docs/vibe-analyze/tests/test-analyze.py` e `docs/vibe-analyze/tests/test-analyze.sh`. Elas cobrem predecessores, phase/MVP, atualização, preservação e paridade.

## 7. Limites

- Não cria phase, `n`, slug ou arquivo auxiliar.
- Não edita interview, não publica `REGRAS.md` e não substitui a review.
- O script não interpreta Status, aceite ou veredito.
- O arquivo vivo entra no Git; o JSON operacional é transitório no stdout; não há commit automático.
