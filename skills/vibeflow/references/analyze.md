# Etapa analyze

Conferência independente do plan contra a spec e o código, antes do implement, sem `analyze.md` e sem aprovação humana. O revisor corrige o `plan.md` direto e grava `## Achados do analyze`, última seção do arquivo, no formato de `references/disco.md` (Achados do analyze).

## Entrada

- Gate: rota `high` ou `mvp`, `spec.md` aprovada e `plan.md` sem `## Achados do analyze`.
- Contexto limpo: revisor em subagente. Sem subagentes ou com o revisor ausente, o líder grava o estado e instrui abrir chat novo com `/vibeflow analyze` (`references/retomada.md`, Modo B).
- O revisor lê `spec.md`, `plan.md`, `AGENTS.md` e o código que os passos citam, com consumidores e testes.

Quem faz: o líder delega ao revisor o path do alvo, confere a seção gravada e o diff do plan e leva ao humano o achado que muda a spec; o revisor confere e corrige.

## Passos

1. Com Node, o revisor roda primeiro `scripts/plan.mjs` no alvo, que aponta a parte mecânica, e julga o resto pelas conferências de `references/analyze/coverage.md`.
2. O revisor corrige o `plan.md` e anota cada correção em `## Achados do analyze`; sem achado, a seção traz `Nenhum achado.`.
3. Achado que exige mudar a `spec.md`, inclusive uma decisão do humano, não é corrigido nem gravado: o revisor o devolve ao líder como pergunta, com recomendação. O líder pergunta ao humano, a spec muda por `references/disco.md` (Escrever artefato) e a seção de achados só nasce na rodada que conclui.

## Saída

O relatório fixo de `references/delegation.md`, com a quantidade de achados corrigidos e as perguntas pendentes.

## Fechar e próxima etapa

Sem commit. Com a seção gravada, o líder segue para `references/implement.md` pelo encadeamento do topo do `SKILL.md`; com pergunta pendente, a etapa espera a resposta.
