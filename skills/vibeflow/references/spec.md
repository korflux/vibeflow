# Etapa spec

A `spec.md` é o único documento que o humano aprova antes do código. Só o decidido entra: pergunta aberta no arquivo é defeito. A meta é caber em uma ou duas telas.

## Entrada

- Gate: rota `high` ou `mvp`, com as decisões fechadas pela interview (`references/interview.md`), mesmo em pedido claro.
- Spec aprovada que precisa mudar segue `references/disco.md` (Escrever artefato); pedido novo abre outra phase.
- Leia a `spec.md` viva, `## Decisões vigentes` do `AGENTS.md` quando existir e os contratos citados.

## Gravação

O redator cria a `spec.md` de `templates/spec.md` ou edita a viva, com o cabeçalho de `references/disco.md` (Cabeçalho), `# Status: rascunho` e as regras por seção de `references/spec/gravacao.md`.

### Origem dos valores

Todo valor numérico, prazo, limite ou comportamento externo numa linha de Decisões ou de Critérios de aceite traz na mesma linha um destes marcadores, com fonte não vazia; palavra solta, como `humano` no texto, não vale:

| Marcador | Quando |
|---|---|
| `(origem: verificado <fonte>)` | O explorador provou o fato por sondagem, com a evidência em Pontos do projeto |
| `(origem: humano)` | O humano deu o valor |
| `(origem: assumida)` | Nem fonte verificada nem o humano sustentam o valor |

- A origem `assumida` de valor difere da decisão assumida pelo líder, marcada no motivo.
- Fato que só se prova implementando, ou que o explorador devolveu como "não verificado", leva `(origem: assumida)` e vira o passo de verificação do plan (`references/plan.md`, Fatiar e ordenar); "verifico depois" sem esse passo é proibido.
- Decisão de preferência (cor, nome, ordem) e linha de tabela de exemplos não levam marcador.
- Vale para spec nova; spec aprovada não é revalidada.

## Critérios de aceite

Cada critério é uma linha `- A1: <contexto ou estado>; quando <ação ou evento>, <resultado observável>.` Critério sobre estado estático, como documento ou configuração, omite o "quando". A forma, as regras e os exemplos de `references/spec/gravacao.md` (Critérios de aceite) valem também para os critérios do brief medium (`references/implement.md`, Rota medium).

## Fechar

O líder confere a entrega por `references/delegation.md` (Conferência do líder) e contra Critérios de aceite. Com Node, roda antes `scripts/plan.mjs --spec` no alvo, que aponta a parte mecânica. Achado de forma volta ao redator; achado que exige decisão do humano vira pergunta da interview. Só então responde:

```text
Spec gravada: <alvo>/spec.md

- Objetivo: <1 linha>
- Decisões: <2 a 4 bullets>
- Aceite: <A1 a An em 1 linha>
- Fora: <1 linha>
- Assumidas: <cada valor com `(origem: assumida)` e cada decisão assumida, com o número da decisão ou do critério, ou nenhuma>

Responda "aprovado" para seguir até a review, ou indique os ajustes.
```

| Resposta | Ação |
|---|---|
| Aprovado pela seção 3 do `SKILL.md` | O líder marca a aprovação como nela, com data, e segue para o plan |
| Pedido de ajuste | O redator aplica o patch; o líder resume em até cinco bullets e pede nova leitura |
| "Parece bom" ou "ok" isolado | Perguntar: "Aprovado no arquivo ou deseja algum ajuste?" |
| Intenção quebrou | Voltar à interview |

Sem commit. O que a aprovação encadeia segue o topo do `SKILL.md`.
