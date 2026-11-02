# Review: checkpoint, spec e implementador enxutos
# Alvo: phase-6-checkpoint-spec-e-implementador-enxutos
# Status: aprovado

## Veredito

- [x] **Approve**: critérios atendidos e provados, regressão verde e nenhum Critical ou Required aberto
- [ ] **Request changes**: há Critical ou Required aberto

## Critérios de aceite

| Critério | Evidência (teste e resultado) | Situação |
|---|---|---|
| A1 | `tests/scripts/plan.test.mjs`: "--spec: valor sem origem em decisão e em critério de spec em rascunho é achado (A1)", "--spec: valor é número com unidade, prazo ou limite; ID, número de decisão e faixa de IDs não são (A1)" e "CLI --spec: valor sem origem sai com 1 e a marca de origem sai com 0 (A1 e A2)"; `node --test` verde | atendido |
| A2 | `plan.test.mjs`: "--spec: marcador (origem: verificado (fonte), humano ou assumida) na mesma linha tira o achado (A2)" e "--spec: palavra solta humano, assumida ou verificado não é origem; só o marcador explícito com fonte (A2)"; verde | atendido |
| A3 | `plan.test.mjs`: "--spec: valor sem origem em linha de tabela de exemplos ou em spec aprovada não é achado (A3)"; verde; `plan.mjs --spec` na própria phase-6 (aprovada) sem achado | atendido |
| A4 | `plan.test.mjs`: "passo com 13 entradas de código em Arquivos: está acima do teto (A4)"; verde | atendido |
| A5 | `plan.test.mjs`: "passo com 12 entradas de código e testes a mais não tem achado de teto (A5)", com pasta contando uma e os cinco formatos de teste; verde | atendido |
| A6 | `plan.test.mjs`: "mais de dois checkpoints é achado; dois não (A6)"; verde | atendido |
| A7 | `plan.test.mjs`: "checkpoint em plan de até 5 passos é achado; com 6 passos não (A7)", inclusive grupo paralelo contado passo a passo (Glossário de `disco.md`: passo é linha do checklist); verde | atendido |
| A8 | `node --test`: 114 testes, 114 verdes, 0 pulados; chamadas `test(` em `tests/scripts/` foram de 96 para 111; a única asserção alterada (`[3, 1]` para `[6, 1]` em "plan bem formado") acompanha o fixture adaptado ao contrato (A7), sem caso nem asserção removidos | atendido |
| A9 | `templates/agents/claude/implementador.md:10` e `codex/implementador.toml:9`: "leia somente references/implementador.md"; busca sem instrução de ler `SKILL.md`, `delegation.md` ou `implement.md` nos dois perfis | atendido |
| A10 | Busca de "Trabalho de quem implementa" em `skills/`, `README.md` e `AGENTS.md`: nenhuma ocorrência; `implementador.md:23` aponta para `testes.md` (Política de testes e Desenho de casos); comparação mecânica de 7-gramas entre `implementador.md` e `testes.md`: 0 trechos comuns | atendido |
| A11 | `templates/agents/claude/explorador.md`: `tools` com Bash e PowerShell e instrução "shell só para leitura e consulta ... sem escrita fora das saídas normais"; `codex/explorador.toml`: mesma instrução e `sandbox_mode = "read-only"`; instruções idênticas entre hosts | atendido |
| A12 | Busca em `skills/vibeflow/`, `README.md` e `AGENTS.md` por "grupo de risco", "phase pequena", "duas perguntas", "provas/testes dos passos" e escolha de esforço: só ocorrências da regra nova (primeiro grupo de risco, sem rerodar a prova dos passos, duas perguntas só para ajuste de tela, líder escolhe o esforço de raciocínio) | atendido |
| A13 | `node skills/vibeflow/scripts/governanca.mjs` neste repo: `AGENTS.md: ok` (bloco igual ao de `templates/AGENTS.md`); `governanca.test.mjs` verde | atendido |
| A14 | `AGENTS.md:64` "Versão atual: 5.4.0"; `README.md:133-143` "Novidades da 5.4.0", minor, sem migração, com a instrução de rodar `/vibeflow init` | atendido |
| A15 | `governanca.test.mjs`: "AGENTS.md sem a seção Núcleo do projeto é aviso e não muda os achados (A15)" e "CLI: AGENTS.md sem a seção de núcleo sai com 0 e mostra o aviso (A15)"; verde | atendido |
| A16 | `governanca.test.mjs`: "AGENTS.md com a seção Núcleo do projeto não tem aviso de núcleo (A16)"; verde; uso real: `governanca.mjs` neste repo sem aviso de núcleo | atendido |
| A17 | `templates/AGENTS.md:31-33` com `## Núcleo do projeto`, `SLOT:nucleo` e a forma `- \`<path>\`: <o que é>; ler <quando ler>`; `init.md:15` (explorador propõe), `:29` (líder leva ao humano, redator grava a versão confirmada) e `:7` (reparo em projeto sem a seção) | atendido |
| A18 | `SKILL.md:31` e `interview.md:35`: o líder abre ele mesmo, sem resumo e inclusive as imagens, os itens do núcleo que o pedido toca; `delegation.md:31`: conferência de direção compara a evidência com o item aberto, com apontamento concreto e sem revisão linha a linha | atendido |
| A19 | `delegation.md:50` (brief do implementador com os itens do núcleo que ele abre) e `implementador.md:13` | atendido |

## Achados

### Nit

- [x] R1: **Nit** - `skills/vibeflow/references/disco.md:99` - a regra do que o verificador executa ("não reroda a prova dos passos ... O E2E das demais telas fica para a regressão completa") ganhou uma casa nova em `disco.md`, quase igual a `testes.md:11`, além de `implement.md:41` e `delegation.md:14` e `:74`; cinco lugares para o mesmo fato contrariam "uma casa por fato" (`AGENTS.md`, seção 6) e abrem caminho para divergência na próxima mudança - remédio: em `disco.md` (Plan > Checkpoint), manter só a posição e o número dos checkpoints e trocar o bullet do verificador por ponteiro para `references/implement.md` (Checkpoint), que já é a casa da mecânica; `testes.md` segue como casa do que cada nível testa - prova: `grep -rn "demais telas" skills/vibeflow` mostra só `testes.md` e o ponteiro; `git diff --check` - papel: redator
- [x] R2: **Nit** - `skills/vibeflow/scripts/plan.mjs:242` - a dica do achado de valor sem origem ensina `(origem: verificado (<fonte>))`, enquanto a casa da regra, `references/spec.md:27-28`, e `templates/spec.md:19` ensinam `(origem: verificado <fonte>)`; o script aceita as duas formas, então não há falso positivo, mas o redator recebe duas formas canônicas diferentes conforme leia a referência ou a saída do script - remédio: alinhar `DICA_ORIGEM` (e o cabeçalho do script e a constante `DICA` de `tests/scripts/plan.test.mjs`) à forma de `references/spec.md`, mantendo o reconhecimento das duas formas - prova: `node --test tests/scripts/plan.test.mjs` - papel: implementador
- [x] R3: **Nit** - `skills/vibeflow/references/implementador.md:24` - a linha de prova cobre a `Prova:` do passo e os testes afetados da correção, mas não a entrega low ou medium que o próprio cabeçalho do arquivo inclui; o perfil antigo dizia "em low ou medium, entregue a mudança do brief com a prova proporcional", e agora o implementador só chega à regra ("sem plan, os testes do módulo tocado e dos consumidores diretos", `testes.md:10`) se abrir a Política de testes por outro motivo - remédio: na linha, acrescentar "em low ou medium, a prova do brief, conforme `references/testes.md` (Política de testes)" - prova: leitura de `implementador.md` e `git diff --check` - papel: redator
- [x] R4: **Nit** - `skills/vibeflow/templates/agents/codex/explorador.toml:9` - a instrução comum aos dois hosts manda a sondagem rodar teste existente ou consultar fonte externa pelo shell, mas o próprio comentário da linha 6 registra que o sandbox `read-only` do Codex bloqueia escrita e rede; nesse host, teste que grava arquivo temporário e consulta HTTP falham, e `interview.md:33` não diz o que fazer com fato verificável que a sondagem não alcançou (só cobre o fato que se prova implementando) - remédio: na instrução comum dos dois perfis, dizer que a consulta externa usa o meio que o host permite (shell ou ferramenta de busca do host) e que fato não alcançado volta ao líder como "não verificado", com o motivo; em `interview.md` (Explorar), tratar esse fato como pergunta ao humano ou `(origem: assumida)` com passo de verificação - prova: `node --test tests/scripts/governanca.test.mjs`; instruções idênticas entre hosts; `git diff --check` - papel: redator

## Notas

- Regressão no `HEAD` 7db1874, árvore limpa: `git diff --check` (árvore e intervalo `8ff71bf~1..HEAD`) sem achado; `node --test` 114/114 verdes; `gitleaks detect --source . --redact --no-banner` com 119 commits e "no leaks found"; revisão de consistência sem achado: os paths deste repo citados em `skills/vibeflow/`, `README.md` e `AGENTS.md` existem (o que sobra na busca mecânica são nomes de artefato, arquivos do projeto consumidor, nomes de script resolvidos em `scripts/` e nomes do formato antigo citados como compatibilidade); nenhuma citação vigente da v1 nem do contrato anterior à 5.0.0 (`refinement-criteria.md:53` fala da v1 do produto do usuário, não do VibeFlow).
- Limitações conhecidas avaliadas sem achado: a marca de origem vale para a linha inteira, documentada em `ponytail:` no `plan.mjs` e coberta pelo teste "linha com dois valores e um marcador"; a lista fixa de unidades também está em `ponytail:`. O bloco da cadeia do `AGENTS.md` resume a regra de checkpoint e aponta para `disco.md`; o `governanca.mjs` mantém os dois blocos iguais, e a divergência possível é só com `disco.md` numa mudança futura, que a seção 9 do `AGENTS.md` já manda começar por ele. O passo de verificação de fato depois do de infraestrutura refina a decisão 2 sem contradizê-la: o passo de infraestrutura (Docker, `plan.md`, passo 2) já era o passo 1 por regra anterior.
- Coerência de commits: o passo 2 tem dois commits (`4ec90f4` e `5207bfd`); o segundo é a correção devolvida pelo checkpoint, no formato de passo, e traz a marcação do checkpoint, conforme `implement.md` (Checkpoint). `spec.md` e `plan.md` entraram no commit do passo 1. Nenhum path alterado fora dos `Arquivos:` dos passos, salvo os artefatos da phase. Nenhum commit de outro alvo no intervalo.
- `governanca.mjs` neste repo também acusa a ponte `.agents/rules/vibeflow.md` ausente e seis perfis globais diferentes da fonte (explorador, implementador e verificador, nos dois hosts): é o estado da máquina antes de rodar `/vibeflow init` com a 5.4.0, como o `README.md` instrui, e não defeito da entrega. Os perfis carregados nesta sessão ainda são os antigos.
- O cabeçalho deste `review.md` não leva `# Rota:`: em `high`, a rota fica só na `spec.md` (`references/disco.md`, Cabeçalho, e `templates/review.md`), como nas reviews das phases 4 e 5.

## Aprovação humana

- [x] Aprovação humana (confirmou no chat o resumo do líder): 2026-11-01, Marco: "Aprovar e push"

## Etapas

### Etapa 1 - review - 8ff71bf~1..HEAD

- Regressão: `git diff --check`, `node --test`, `gitleaks detect --source . --redact --no-banner` e revisão de consistência dos Comandos do projeto; todos verdes, sem flake; `HEAD` 7db1874.
- Duração: lint (`git diff --check`) abaixo de 1 s, sem medição precisa; unitários (`node --test`) 39,3 s; varredura de segredos (gitleaks) 0,8 s; E2E não existe neste repo; total medido 40,1 s · orçamento: 10 min, padrão de `references/testes.md` (o `AGENTS.md` não declara orçamento); dentro dele.
- Abriu: R1, R2, R3, R4 (Nit)
- Veredito: Approve
