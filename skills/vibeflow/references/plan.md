# Etapa plan

O `plan.md` é o tracking interno da phase: um checklist na ordem real de execução, sem `# Status:` nem aprovação humana. Zero código nesta etapa. O formato do passo, as regras de `Arquivos:`, o checkpoint e a seção `## Achados do analyze` moram em `references/disco.md` (Plan); este arquivo não os repete.

## Entrada

- Gate: rota `high` ou `mvp`, `spec.md` com `# Status: aprovado`. Spec em rascunho volta à aprovação da spec; intenção, sucesso ou limites frouxos voltam à interview.
- `plan.md` existente é editado no lugar (`references/disco.md`, Escrever artefato).
- Leia `spec.md`, `AGENTS.md` e os comandos de verificação do projeto.

## Quem faz

| Quem | Faz |
|---|---|
| Explorador | Confirma, no código, o mapa de cada critério: arquivos, consumidores, testes afetados, padrão a seguir e itens do núcleo |
| Líder | Fatia em passos, ordena, agrupa paralelos, marca checkpoints e define provas e Regressão completa |
| Redator | Grava o `plan.md` a partir das decisões do líder |

## Passos

1. **Explorar.** Antes de gravar, o explorador confirma para cada critério de aceite os arquivos, os consumidores, os testes afetados, inclusive os que a mudança quebra por snapshot, schema ou seletor, o padrão a seguir no código e os itens de `## Núcleo do projeto` que o resultado toca. Path que o explorador não confirmou não entra em `Arquivos:`; teste que a mudança quebra entra em `Arquivos:` do passo que o quebra. Depois do fatiamento, o líder recorta esse mapa por passo e o leva no brief do passo (`references/delegation.md`, Pedido autocontido).
2. **Ambiente de teste.** O explorador também relata se os testes do projeto usam Docker, pelos sinais de `references/init.md` (Ambiente local). Com Docker e sem a decisão registrada, o líder leva ao humano a pergunta dessa seção antes de gravar o plan. A resposta vira o passo 1 do plan, de infraestrutura: `Aceite: nenhum`, `Arquivos:` com o `AGENTS.md` do projeto, seção Ambiente, e `Prova: git diff --check`. O redator grava o registro no implement e o líder o commita como os demais passos (`references/disco.md`, Commits). Com critério de tela, o líder escolhe o isolamento do E2E entre as opções (a), (b) e (c) de `references/testes.md` (Desenho do E2E), e o plan o registra numa linha da seção `## Regressão completa`.
3. **Fatiar e ordenar.** Um passo por resultado verificável, na ordem real de execução, dentro do teto de entradas de código de `references/disco.md` (Plan > Arquivos); passo acima do teto se divide pelo resultado verificável. Fato da spec que só se prova implementando vira o passo de verificação, o primeiro do plan depois do de infraestrutura quando houver, com a `Prova:` que confirma ou refuta o fato; resultado que contradiz a spec para o encadeamento, e o líder leva a contradição ao humano antes do passo seguinte. O primeiro passo de entrega, depois dos de infraestrutura e de verificação quando houver, é o caminho mais fino de ponta a ponta do critério central ou a suposição mais arriscada (integração externa, migration, desempenho), para que o erro caro apareça cedo. Agrupe passos em paralelo só quando os `Arquivos:` forem disjuntos. Arquivo que vários passos precisariam escrever (versão, README, índices) vai para um passo posterior a eles.
4. **Cobrir a spec.** Todo critério de aceite da spec aparece em `Aceite:` de algum passo e tem prova nele. Passo de infraestrutura usa `Aceite: nenhum`. Migration entra no passo do resultado que a usa, não destrutiva (expand/contract), conforme `references/database-and-migrations.md`. Passo que cria ou altera ponto de entrada executável traz o smoke desse ponto na própria `Prova:`.
5. **Prova do passo.** Os testes do passo, ou a checagem do passo só de prosa, conforme `references/testes.md` (Política de testes). Quando a ferramenta permite filtrar, a `Prova:` nomeia o arquivo e os casos que provam os critérios do passo, pelo comportamento. Comando que o repo não tem não vira prova: ferramenta instalável no projeto, sem credencial nem elevação, entra no passo que depende dela; credencial, conta, pagamento ou privilégio do SO volta ao líder como pergunta ao humano.
6. **Checkpoints.** Marque os checkpoints nas posições de `references/disco.md` (Plan > Checkpoint).
7. **Regressão completa.** Defina os comandos reais da suíte inteira, do mais barato ao mais caro: lint e tipos, unitários, E2E. Quando cada nível roda está em `references/testes.md` (Política de testes).
8. **Gravar.** O redator cria o `plan.md` a partir de `templates/plan.md`, ou edita o vivo. O plan guarda a definição do trabalho e as caixas; nunca hashes, logs nem histórico de comandos. Com Node, o líder roda `scripts/plan.mjs` no alvo depois da gravação, para preencher a Saída; achado de forma ou critério sem passo volta ao redator, e passo acima do teto ou checkpoint fora da regra volta ao líder, que refaz o fatiamento.

## Saída

```text
Plan gravado: <alvo>/plan.md

- Passos: <quantidade, grupos paralelos e checkpoints>
- Critérios sem passo: nenhum
- Próximo: analyze
```

## Fechar e próxima etapa

Sem commit e sem pedido de aprovação. Com o plan gravado, o líder segue direto para `references/analyze.md`.
