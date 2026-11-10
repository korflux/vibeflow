# Passos do revisor na review

Leitura do revisor na etapa review, depois de `references/review.md` (Entrada e Rodadas de correção). O líder só o lê no Modo B, ao atuar como revisor.

## Fontes

| O revisor lê | Fonte |
|---|---|
| Critérios de aceite | `spec.md`; em medium, o corpo do commit `task(medium): ...` (`git log -1 --format=%B <commit>`), e commit sem eles volta ao líder, que informa os critérios do brief |
| Contexto | Do `plan.md`, só `## Regressão completa`, as linhas de passo e checkpoint e `## Trabalho alheio`; do `AGENTS.md`, só Comandos do projeto e as linhas de `## Decisões vigentes` que o diff toca; o `git log` com os commits do alvo |
| Diff | Do commit anterior ao primeiro `task(<alvo>:...)` até `HEAD`, ou da base que o líder informar; em medium, o revisor registra o `task(medium): ...` como base e o diff parte do commit anterior a ele |

Julgue o diff, não o repositório: abra arquivo fora do diff só para seguir um consumidor de símbolo alterado ou o teste citado como prova.

Declare em uma linha: rota, tipo, alvo e diff.

```text
rota: high · final · alvo: .vibeflow/phases/phase-2-agenda-online/ · diff: a1b2c3d..HEAD
```

## Tipo

| Sinal | Ação |
|---|---|
| Passo ou checkpoint aberto | Não revise; devolva ao implement com o que falta |
| Todos marcados, ou entrega medium commitada | Review final |
| Correção de Critical ou Required commitada com `task(<alvo>:Rn,...)` | Re-review |
| Etapa `### Ajuste N` medium com os R* `[x]` e commit | Re-review de ajuste: só o diff desses commits, contra o pedido do ajuste |
| Critério de aceite não verificável | Devolva à spec |
| MVP sem `# Risco:` na spec ou sem `## Achados do analyze` no plan | Recuse e aponte a etapa ausente |

## Passos

### 1. Disparar a regressão completa

Ao abrir a review final, o revisor dispara a regressão completa uma vez, em segundo plano, sobre o `HEAD` da entrega, e lê o diff enquanto ela roda.

- Comandos: os de regressão registrados no plan ou, sem eles, os Comandos do projeto no `AGENTS.md`. Sem nenhum, devolva ao líder sem aprovar.
- Ordem: do mais barato ao mais caro (lint e tipos, unitários, E2E), parando na primeira falha; o E2E roda no modo de `references/testes.md` (Execução), e o nível E2E inclui a checagem de console em dev dos critérios que tocam o cliente, que só a regressão roda.
- Árvore suja em path de código ou teste (tudo fora de `.vibeflow/`, `.erros-encontrados/` e do `## Trabalho alheio` do plan) impede a execução: devolva `estado: bloqueado` pedindo o isolamento. Path declarado em `## Trabalho alheio` não bloqueia: rode a regressão com ele presente e cite-o em Notas, junto de qualquer falha que ele possa ter causado.
- Falha se confirma pela reexecução de `references/testes.md` (Execução). Falha que passa nela é flake: o revisor grava o registro em `.erros-encontrados/`, cita-o em Notas e segue para os níveis seguintes, sem bloquear. Falha reproduzível abre R* Required com o comando e os arquivos e casos que falharam.
- Registre na etapa os comandos, o resultado, o `HEAD`, os arquivos e casos que falharam e a duração de cada nível que rodou (lint e tipos, unitários, E2E com a checagem de console) e o total, lidos da saída dos comandos ou do relógio da execução.
- Compare o total com o orçamento (Orçamento de duração, abaixo).

A execução registrada vale para o Approve enquanto as correções posteriores não tocarem código compartilhado. Esta é a única execução da regressão completa na review; a re-review só a repete na exceção do passo 4.

### 2. Julgar o produto

1. **Critérios de aceite:** cada critério da spec, ou do corpo do commit em medium, está atendido e provado por ao menos um teste cuja asserção você comparou com o texto do critério (`references/testes.md`, Política de testes). Preencha a tabela de critérios com o teste e o resultado. Critério não atendido, sem teste que o prove ou provado por asserção que diverge do texto dele abre R* Required; só o humano retira um critério, com a decisão citada.
2. **Defeitos no código alterado:** defeito que lint, tipos ou teste da regressão apontam é achado com a saída do comando como prova; a leitura cobre o que as ferramentas não cobrem: correção, bordas e erros das superfícies tocadas; teste enfraquecido, pulado ou apagado, teste da seção O que não testar e duplicata sem ganho (`references/testes.md`, Política de testes e O que não testar); caso ausente do Desenho de casos de `references/testes.md`: Required quando é caso adversarial que o tipo de entrada do critério aciona ou quando a spec traz a tabela de exemplos que o exige, e Nit nos demais; barra de `references/definition-of-done.md`.
3. **Segurança:** só quando o diff toca input, auth, sessão, permissão, segredo, upload, integração externa ou dado pessoal, conforme `references/review/security-and-hardening.md`.
4. **Banco e precisão:** só quando o diff toca persistência ou valor monetário, conforme `references/database-and-migrations.md`.
5. **Visual:** quando um critério depende da interface renderizada, conforme `references/review/ui-visual-quality.md`, reaproveitando a evidência válida.

Notas, nunca achado: path alterado fora dos `Arquivos:` do plan, coerência dos commits com os passos e commits de outro alvo no intervalo. Defeito fora dos critérios e do diff é achado fora do recorte: o revisor grava um arquivo por achado em `.erros-encontrados/`, cita em Notas e não bloqueia.

Achado: severidade (`Critical`, `Required` ou `Nit`), paths (um ou mais entre crases, separados por `, `, logo depois da severidade; crase da descrição, do remédio ou da prova não é path), remédio, prova e `papel: implementador` (código e testes) ou `papel: redator` (prosa); remédio em `review.md` é do revisor, sem `papel`. Achado novo recebe o próximo R* livre, sem renumerar fechados. Preferência sem fundamento não é achado; informação sem remédio vai para Notas.

### 3. Gravar

O revisor cria o `review.md` a partir de `templates/review.md`, ou acrescenta `### Etapa N` sem apagar etapas anteriores, e marca o veredito com o `# Status:` que `references/disco.md` (Cabeçalho) dá ao revisor:

- **Approve:** critérios atendidos e provados, regressão verde e nenhum Critical ou Required aberto; status `rascunho`. Nit aberto não impede a proposta, mas precisa ser fechado antes da confirmação.
- **Request changes:** há Critical ou Required aberto; status `request-changes`.

### 4. Re-review

Quais achados passam por re-review e o limite de rodadas seguem `references/review.md` (Rodadas de correção).

1. Confira que o commit `task(<alvo>:Rn,...)` existe e que seus IDs são exatamente os R* marcados `[x]` desde a etapa anterior; divergência volta ao líder.
2. Julgue só o diff da correção contra os R* que ela fecha.
3. Se a regressão falhou na etapa anterior, rerode primeiro só os arquivos e casos que falharam, pelo registro da etapa anterior, e, verdes, o que não chegou a rodar: os níveis seguintes e, depois de falha no E2E, a checagem de console do nível.
4. Rerode a regressão completa só quando a correção tocou código compartilhado: módulo, contrato, componente ou configuração usado fora dos paths dos R*. Ela repete a duração e o orçamento do passo 1.

## Orçamento de duração

- O `AGENTS.md` do projeto declara em Comandos do projeto o orçamento da regressão completa; sem declaração, o orçamento é de 10 minutos.
- Total acima do orçamento: o revisor grava em `.erros-encontrados/` o tempo total, o nível mais lento e a causa provável, cita o registro em Notas e segue, sem bloquear; o orçamento não entra no veredito. Na confirmação, o líder propõe ao humano a poda de testes como pedido medium próprio (`references/testes/poda.md`).

## Saída

O relatório fixo de `references/relatorio.md` acrescenta `veredito`, `abertos`, `fechados`, `critical_encontrados`, `decisoes_vigencia`, a regressão (comandos, resultado, `HEAD`, duração por nível e total, orçamento) e os registros gravados em `.erros-encontrados/`. O revisor não pergunta ao humano: veredito que depende dele volta como `estado: pergunta`. O revisor não commita, não faz push, não edita `AGENTS.md`, não marca aprovação humana nem `[x]` e não corrige código.
