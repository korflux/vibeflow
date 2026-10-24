# Plan: testes locais leves, E2E paralelo e orçamento de duração
# Alvo: phase-5-testes-leves-sem-docker
# Spec: spec.md (mesma pasta)

## Regressão completa

1. `git diff --check`
2. `node --test`
3. `gitleaks detect --source . --redact --no-banner`
4. Revisão de consistência dos Comandos do projeto (`AGENTS.md`): paths citados existem, nada cita como vigente o contrato anterior, e nenhuma regra de teste aparece fora de `references/testes.md` além de ponteiros.

## Passos

- [x] 1: referência única de testes, com a política que sai do implement, o ambiente local (inclusive a pergunta sobre Docker em projeto já inicializado sem a decisão registrada), o desenho do E2E, a pirâmide e o orçamento · Aceite: A1, A2, A3, A4 · Arquivos: `skills/vibeflow/references/testes.md`, `skills/vibeflow/references/implement.md` · Prova: `git diff --check`; a seção Política de testes do implement vira ponteiro para `references/testes.md`
- [x] 2a: plan, review, delegação, analyze e definição de pronto apontam para a referência; o plan leva ao humano a pergunta sobre Docker quando o projeto usa Docker nos testes sem decisão registrada; a review registra a duração por nível e grava o alarme de orçamento · Aceite: A1, A2, A5 · Arquivos: `skills/vibeflow/references/plan.md`, `skills/vibeflow/references/review.md`, `skills/vibeflow/templates/review.md`, `skills/vibeflow/references/delegation.md`, `skills/vibeflow/references/analyze/coverage.md`, `skills/vibeflow/references/definition-of-done.md`, `skills/vibeflow/SKILL.md`, `skills/vibeflow/templates/plan.md` · Prova: `git diff --check`; nenhuma regra de teste repetida fora de `references/testes.md`
- [x] 2b: perfis apontam para a referência, com o corpo idêntico entre os hosts · Aceite: A1 · Arquivos: `skills/vibeflow/templates/agents/claude/implementador.md`, `skills/vibeflow/templates/agents/claude/verificador.md`, `skills/vibeflow/templates/agents/claude/revisor.md`, `skills/vibeflow/templates/agents/codex/implementador.toml`, `skills/vibeflow/templates/agents/codex/verificador.toml`, `skills/vibeflow/templates/agents/codex/revisor.toml`, `skills/vibeflow/templates/agents/claude/explorador.md`, `skills/vibeflow/templates/agents/claude/redator.md`, `skills/vibeflow/templates/agents/codex/explorador.toml`, `skills/vibeflow/templates/agents/codex/redator.toml` · Prova: `git diff --check`; corpo de cada papel idêntico entre Claude e Codex
- [x] 2c: template de regras com orçamento e decisão sobre Docker, e init que os preenche e detecta Docker nos testes · Aceite: A5, A6 · Arquivos: `skills/vibeflow/templates/AGENTS.md`, `skills/vibeflow/references/init.md` · Prova: `git diff --check`
- [ ] Checkpoint: A1, A2, A3, A4, A5, A6
- [ ] 3: versão 5.1.0 registrada nas regras do repo e no README, com `references/testes.md` na Estrutura do pacote do `AGENTS.md` · Aceite: A7 · Arquivos: `AGENTS.md`, `README.md` · Prova: `node --test`; `git diff --check`

## Achados do analyze

| Achado | Onde | Ajuste |
|---|---|---|
| `references/definition-of-done.md` cita `references/implement.md`, Política de testes, e nenhum passo o ajusta; com a seção virando ponteiro, a regra ficaria a dois saltos da casa única (A1) | Passo 2a, `Arquivos:` | Acrescentado `skills/vibeflow/references/definition-of-done.md` ao passo 2a, que passa a apontar para `references/testes.md` |
| A decisão 1 da spec vale para todo projeto que já usa Docker nos testes, mas o plan só levava a pergunta pelo init (A6); projeto já inicializado, como o kastir, nunca a receberia, porque o init só roda de novo para reparo | Passos 1 e 2a | Passo 1 define em `references/testes.md` a pergunta também para projeto já inicializado sem a decisão registrada; passo 2a faz o `references/plan.md` levá-la ao humano, com A2 no `Aceite:` |
| `Arquivos:` do passo 2b declarava a pasta `skills/vibeflow/templates/agents/` inteira, mas só implementador, verificador e revisor citam regra de teste; explorador e redator não mudam | Passo 2b, `Arquivos:` | Recorte estreitado aos seis perfis desses três papéis nos dois hosts (`references/disco.md`, Arquivos) |
| A seção Estrutura do `AGENTS.md` deste repo lista as referências de apoio por tema (banco, navegador, definição de pronto); sem ajuste, `references/testes.md` ficaria fora da lista | Passo 3, resultado | Resultado do passo 3 inclui `references/testes.md` na Estrutura do pacote do `AGENTS.md` |
