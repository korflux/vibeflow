# Escopo do vibeflow: feito e na fila

Convenção: `[x]` já existe no repositório hoje. `[ ]` entra, ainda não construído. O histórico da v1 (oito skills com motores, até a 9.0.0) fica no Git e nas phases 1 a 20 de `.vibeflow/phases/`.

## 1. Skill

- [x] **V2 só texto (10.0.0, phase 21).** Skill única `vibeflow` em `skills/vibeflow/`, pasta real, com `SKILL.md`, referências por etapa e templates, sem motores. Coordenador-líder conduz todas as rotas com `/vibeflow` e `/vibeflow <etapa>` e delega a execução. Estado nas linhas `# Status:` e `# Rota:`, nas caixas do `plan.md` e no Git. Gates conferidos pelo líder; analyze e review por revisor de contexto limpo. Phases v1 lidas como estão. Distribuição somente de `vibeflow` nos quatro hosts.
- [x] **Ondas por `Arquivos:` disjuntos.** T* elegíveis com `Arquivos:` disjuntos são despachadas juntas; provas em dois níveis, com a `Regressão completa` só na review final.
- [ ] **Rota MVP em uso real.** Baseline único em `.vibeflow/mvp/`, rota max completa. Contrato pronto; falta a primeira condução real.
- [ ] **Testes de comportamento de fragmentos de instrução.** Verificar por execução que cada referência produz o comportamento esperado.
- [ ] **Worktree por T*.** Isolamento por worktree, com pacote de contexto por T*. Hoje o isolamento é a disjunção de `Arquivos:`.
- [ ] **Fan-out da review por dimensão.** Review dividida em revisores paralelos por dimensão.
- [ ] **Benchmark de eficiência.** Medição automatizada contra a v1. Hoje a eficiência é avaliada pelo humano no uso.
- [ ] **Motor determinístico (opcional).** Só se a leitura do disco pela IA errar `n`, slug, onda ou gate no uso real.

## 2. Infra feita

- [x] **Validação local, sem CI no GitHub.** Por decisão de custo, a validação é local, antes do push: revisão de consistência e gitleaks, com os comandos em `AGENTS.md` (Comandos do projeto).
- [x] **Distribuição Codex, Claude, Grok e Antigravity.** `npx skills add korflux/vibeflow` e manifestos nativos `.claude-plugin/`, `.codex-plugin/`, `.agents/plugins/`, `.grok-plugin/` e `plugin.json`.

## 3. Limites de contrato

Não são backlog. Mudá-los quebra o disco.

| Limite | Por quê |
|---|---|
| `AGENTS.md` é a única fonte de regras; `CLAUDE.md`, `REGRAS.md` e `GEMINI.md` não são criados | Cópia diverge na primeira edição e deixa de existir fonte única. A ponte Antigravity é apenas `@../../AGENTS.md`. |
| Artefato da cadeia só em `.vibeflow/phases/phase-N-slug/`, salvo o baseline único `.vibeflow/mvp/` | `docs/`, `specs/` e paths de outro produto continuam proibidos; a exceção MVP é fixa e não versionada. |
| `n`, slug e path seguem as regras escritas | A IA aplica a regra; não escolhe número nem path por preferência. |
| A IA não escolhe homolog ou produção | Só o humano sabe, e a resposta muda o bloco de migrations. |
| Commit integrado e push final | Commit `task(T*...)` depois da prova verde, com staging explícito; push somente após aprovação humana. |
| Escritor único por recurso | Durante uma onda, cada T* tem ownership exclusivo dos seus `Arquivos:`; o finalizador opera índice Git e commits; o revisor escreve `analyze.md` e `review.md`. |
| Pacote só texto | Código executável na skill exige decisão do humano e versão nova. |
