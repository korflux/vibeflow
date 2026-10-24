# Etapa plan

O `plan.md` é o tracking interno da phase: um checklist na ordem real de execução, sem `# Status:` nem aprovação humana. Zero código nesta etapa. O formato do passo, as regras de `Arquivos:`, o checkpoint e a seção `## Achados do analyze` moram em `references/disco.md` (Plan); este arquivo não os repete.

## Entrada

- Gate: rota `high` ou `mvp`, `spec.md` com `# Status: aprovado`. Spec em rascunho volta à aprovação da spec; intenção, sucesso ou limites frouxos voltam à interview.
- `plan.md` existente é editado no lugar (`references/disco.md`, Escrever artefato).
- Leia `spec.md`, `AGENTS.md` e os comandos de verificação do projeto.

## Quem faz

| Quem | Faz |
|---|---|
| Explorador | Confirma, no código, os arquivos que cada critério toca, os consumidores deles e os testes afetados |
| Líder | Fatia em passos, ordena, agrupa paralelos, marca checkpoints e define provas e Regressão completa |
| Redator | Grava o `plan.md` a partir das decisões do líder |

## Passos

1. **Explorar.** Antes de gravar, o explorador confirma os arquivos, os consumidores e os testes afetados de cada critério de aceite. Path que o explorador não confirmou não entra em `Arquivos:`.
2. **Ambiente de teste.** O explorador também relata se os testes do projeto usam Docker. Com Docker e sem a decisão registrada no `AGENTS.md` do projeto, o líder leva ao humano a pergunta de `references/testes.md` (Ambiente local) antes de gravar o plan. A resposta vira o passo 1 do plan, de infraestrutura: `Aceite: nenhum`, `Arquivos:` com o `AGENTS.md` do projeto, seção Ambiente, e `Prova: git diff --check`. O redator grava o registro no implement e o líder o commita como os demais passos (`references/disco.md`, Commits). Com critério de tela, o líder escolhe o isolamento do E2E entre as opções (a), (b) e (c) de `references/testes.md` (Desenho do E2E), e o plan o registra numa linha da seção `## Regressão completa`.
3. **Fatiar e ordenar.** Um passo por resultado verificável, na ordem real de execução. Agrupe passos em paralelo só quando os `Arquivos:` forem disjuntos. Arquivo que vários passos precisariam escrever (versão, README, índices) vai para um passo posterior a eles.
4. **Cobrir a spec.** Todo critério de aceite da spec aparece em `Aceite:` de algum passo e tem prova nele. Passo de infraestrutura usa `Aceite: nenhum`. Migration entra no passo do resultado que a usa, não destrutiva (expand/contract), conforme `references/database-and-migrations.md`. Passo que cria ou altera ponto de entrada executável traz o smoke desse ponto na própria `Prova:`.
5. **Prova do passo.** Os testes do passo, ou a checagem do passo só de prosa, conforme `references/testes.md` (Política de testes). Comando que o repo não tem não vira prova: ferramenta instalável no projeto, sem credencial nem elevação, entra no passo que depende dela; credencial, conta, pagamento ou privilégio do SO volta ao líder como pergunta ao humano.
6. **Checkpoints.** Marque um checkpoint depois de cada grupo de passos que fecha critérios de aceite. Phase pequena não tem checkpoint. Com `# Risco:` na spec, há um checkpoint depois de cada grupo de risco.
7. **Regressão completa.** Defina os comandos reais da suíte inteira, do mais barato ao mais caro: lint e tipos, unitários, E2E. Quando cada nível roda está em `references/testes.md` (Política de testes).
8. **Gravar.** O redator cria o `plan.md` a partir de `templates/plan.md`, ou edita o vivo. O plan guarda a definição do trabalho e as caixas; nunca hashes, logs nem histórico de comandos. Com Node, o líder roda `scripts/plan.mjs` no alvo depois da gravação, para preencher a Saída; achado de forma ou critério sem passo volta ao redator.

## Saída

```text
Plan gravado: <alvo>/plan.md

- Passos: <quantidade, grupos paralelos e checkpoints>
- Critérios sem passo: nenhum
- Próximo: analyze
```

## Fechar e próxima etapa

Sem commit e sem pedido de aprovação. Com o plan gravado, o líder segue direto para `references/analyze.md`.
