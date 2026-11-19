# Etapa plan

O `plan.md` é o tracking interno da phase: um checklist na ordem real de execução, sem `# Status:` nem aprovação humana, e sem código nesta etapa. Formato do passo, `Arquivos:`, checkpoint e `## Achados do analyze` moram em `references/disco.md` (Plan).

## Entrada

- Gate: rota `high` ou `mvp` e `spec.md` com `# Status: aprovado`. Spec em rascunho volta à aprovação; intenção, sucesso ou limites frouxos voltam à interview.
- `plan.md` existente é editado no lugar (`references/disco.md`, Escrever artefato).
- Leia `spec.md`, `AGENTS.md` e os comandos de verificação do projeto.

Quem faz: o líder decide passos, ordem, checkpoints e provas a partir do mapa da interview, o explorador cobre só o que o mapa não confirma, e o redator grava.

## Passos

1. **Mapa.** Reaproveite o mapa que o explorador fez na interview e os Pontos do projeto da spec. Só o critério sem arquivos, consumidores, testes afetados (inclusive por snapshot, schema ou seletor), padrão ou itens do núcleo confirmados vai ao explorador, num despacho com todos esses critérios juntos. Path não confirmado não entra em `Arquivos:`; teste que a mudança quebra entra em `Arquivos:` do passo que o quebra. O líder recorta o mapa por passo e o leva no brief (`references/delegation.md`, Pedido autocontido).
2. **Ambiente de teste.** Sem decisão sobre Docker na seção Ambiente do `AGENTS.md`, o explorador relata, no despacho do Mapa ou num próprio, se os testes usam Docker, pelos sinais de `references/ambiente.md`. Com Docker e sem decisão registrada, o líder leva ao humano a pergunta desse arquivo antes de gravar, e a resposta vira o passo 1, de infraestrutura: `Aceite: nenhum`, `Arquivos:` com o `AGENTS.md` do projeto (seção Ambiente) e `Prova: git diff --check`; o redator grava o registro no implement e o líder o commita como os demais passos. Com critério com E2E (tela ou jornada), o líder escolhe o isolamento do E2E entre as opções de `references/verificador.md` (Desenho do E2E), registrado numa linha de `## Regressão completa`.
3. **Fatiar e ordenar.** Um passo por resultado verificável, na ordem real, dentro do teto de `references/disco.md` (Plan > Arquivos); acima dele, divida pelo resultado verificável. Fato da spec que só se prova implementando vira o passo de verificação, o primeiro depois do de infraestrutura quando houver, com a `Prova:` que confirma ou refuta o fato; resultado que contradiz a spec para o encadeamento e vai ao humano antes do passo seguinte. O primeiro passo de entrega, depois desses, é o caminho mais fino de ponta a ponta do critério central ou a suposição mais arriscada (integração externa, migration, desempenho). Paralelo só com `Arquivos:` disjuntos. Arquivo que vários passos escreveriam (versão, README, índices) vai para um passo posterior a eles.
4. **Cobrir a spec.** Todo critério de aceite aparece em `Aceite:` de algum passo, com prova nele; infraestrutura usa `Aceite: nenhum`. Migration entra no passo do resultado que a usa, não destrutiva (expand/contract), por `references/database-and-migrations.md`. Passo que cria ou altera ponto de entrada executável traz o smoke dele na `Prova:`.
5. **Prova do passo.** Os testes do passo, ou a checagem do passo de prosa, por `references/testes.md` (Política de testes); quando a ferramenta filtra, a `Prova:` nomeia o arquivo e os casos dos critérios. A `Prova:` é um comando só, com os testes que o passo cria ou altera e os que o explorador apontou como quebrados por ele, mais o smoke do ponto de entrada quando houver; teste de módulo vizinho que o passo não toca fica para a regressão completa da review, e nenhum passo repete a prova de outro. Sem E2E, sem suíte inteira, sem avaliação com modelo real ou outra medição longa, que vira passo próprio de medição (`references/testes.md`, Política de testes), e sem pedido de arquivo na pasta da phase. Comando que o repo não tem não vira prova: ferramenta instalável no projeto, sem credencial nem elevação, entra no passo que depende dela; credencial, conta, pagamento ou privilégio do SO vai ao humano pelo líder.
6. **Checkpoints.** Nas posições de `references/disco.md` (Plan > Checkpoint), no máximo 2; phase sem `# Risco:` com até 8 passos não tem checkpoint, e o E2E dela roda na regressão completa.
7. **Regressão completa.** Os comandos reais da suíte inteira, do mais barato ao mais caro (lint e tipos, unitários, E2E), por `references/testes.md` (Política de testes).
8. **Gravar.** Com o brief de `references/delegation.md` (Pedido autocontido), que inclui `references/testes.md`, o redator cria o `plan.md` de `templates/plan.md` ou edita o vivo, sem hashes, logs nem histórico de comandos. Quando o host permite continuar um subagente (no Claude Code, por mensagem ao mesmo agente), o plan vai ao redator que gravou a spec, que já tem a spec, as decisões e o mapa no contexto, e o brief leva só o que mudou desde a gravação, o fatiamento do líder e `references/testes.md`; sem isso, um redator novo recebe o brief inteiro. Com Node, o líder roda `scripts/plan.mjs` no alvo depois da gravação; achado de forma ou critério sem passo volta ao redator, e passo acima do teto ou checkpoint fora da regra volta ao líder, que refaz o fatiamento.

## Saída

```text
Plan gravado: <alvo>/plan.md

- Passos: <quantidade, grupos paralelos e checkpoints>
- Critérios sem passo: nenhum
- Próximo: analyze
```

## Fechar e próxima etapa

Sem commit. Com o plan gravado, o líder segue para `references/analyze.md` pelo encadeamento do topo do `SKILL.md`; a Entrada dele diz quando o analyze é dispensado.
