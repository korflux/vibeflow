# Etapa analyze

Conferência independente do plan contra a spec e o código, antes do implement. Não há `analyze.md` nem aprovação humana. O revisor corrige o `plan.md` direto e registra o resultado na seção `## Achados do analyze`, no formato de `references/disco.md` (Achados do analyze).

## Entrada

- Gate: rota `high` ou `mvp`, `spec.md` aprovada e `plan.md` sem `## Achados do analyze`.
- Roda sempre em contexto limpo: revisor em subagente; sem subagentes ou com o perfil revisor ausente, o líder grava o estado e instrui abrir chat novo com `/vibeflow analyze` (Modo B do `SKILL.md`).
- O revisor lê `spec.md`, `plan.md`, `AGENTS.md` e o código que os passos citam, com os consumidores e testes dele.

## Quem faz

| Quem | Faz |
|---|---|
| Revisor de contexto limpo | Confere spec, plan e código, corrige o plan e grava a seção de achados |
| Líder | Delega, confere a seção gravada e o diff do plan, e leva ao humano o achado que muda a spec |

## Passos

1. O líder delega ao revisor o path do alvo e esta referência (`references/delegation.md`).
2. O revisor confere, com `references/analyze/coverage.md`:
   - critério de aceite da spec sem passo ou sem prova;
   - arquivo ou consumidor esquecido em `Arquivos:`;
   - teste que a mudança quebra fora do recorte;
   - contradição entre passo e spec;
   - contrato errado: formato do passo, `Arquivos:`, checkpoint ou Regressão completa fora de `references/disco.md` (Plan) e de `references/plan.md`.
3. O revisor corrige o `plan.md` direto e anota cada correção na seção `## Achados do analyze`, como última seção do arquivo. Sem achado, a seção traz `Nenhum achado.`.
4. Achado que exige mudar a `spec.md`, inclusive uma decisão do humano, não é corrigido nem gravado: o revisor para e o devolve ao líder como pergunta, com recomendação. O líder pergunta ao humano; a mudança da spec segue `references/disco.md` (Escrever artefato), e a seção de achados só nasce na rodada que conclui.

O revisor não implementa código, não commita, não edita `spec.md` nem `AGENTS.md` e não pergunta ao humano.

## Saída

O relatório fixo de `references/delegation.md`, com a quantidade de achados corrigidos e as perguntas pendentes.

## Fechar e próxima etapa

Sem commit e sem pedido de aprovação. Com a seção `## Achados do analyze` gravada, o líder segue para `references/implement.md`. Com pergunta pendente, a etapa fica no analyze até a resposta.
