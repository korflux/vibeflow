# Spec: Checkpoint, spec e implementador enxutos
# Alvo: phase-6-checkpoint-spec-e-implementador-enxutos
# Status: aprovado
# Rota: high

## Objetivo

O líder, o plan e os scripts da skill passam a reduzir o custo de checkpoints e do implementador e a impedir valor chutado na spec. A base é a medição do projeto consumidor fabula: checkpoints custaram cerca de cinco vezes a review, principalmente pela releitura de contexto; implementadores levaram em média 26 min e 186 turnos por passo, com pico médio de 352 mil tokens e só 27% do tempo em provas; a spec da phase-2 teve prazo de retenção assumido sem marca e promessas de "verifico no plano" sem passo. Sucesso é uma phase conduzida depois das regras novas ter no máximo dois checkpoints, passos menores e nenhum valor sem origem. O líder também passa a conhecer de primeira mão o núcleo do projeto que o pedido toca e a conferir a direção das entregas contra ele.

## Pontos do projeto

- `skills/vibeflow/references/plan.md:26`, `disco.md:83-91`, `implement.md:39-46`, `delegation.md:14,35,72,75`, `testes.md:10-11`, `analyze/coverage.md:17`, `templates/plan.md:14-15` e perfis `templates/agents/*/verificador.*`: definem frequência e conteúdo do checkpoint; "phase pequena" não tem definição; o verificador reroda prova de passo, em tensão com `delegation.md:75`.
- `AGENTS.md`, bloco da cadeia (linhas 5 a 25), e `skills/vibeflow/templates/AGENTS.md`: citam checkpoint por grupo de risco e são comparados por igualdade em `scripts/governanca.mjs:85-87`; mudam juntos.
- `implement.md:93` e `delegation.md:36`: origem da captura visual em todo passo, que o plan não pede.
- `testes.md:18-27` e `review.md:47`: o desenho de casos funciona como piso, sem severidade definida para caso ausente.
- `interview.md:40,47,53` e `spec.md:18-19,43-45`: só há "separar fato de hipótese" no turno; lacuna assumida não distingue fato de preferência; tela limitada a duas perguntas; o fechamento não lista as assumidas.
- `scripts/plan.mjs:184-207` (`formaDaSpec`), `:121-160` (`formaDoPasso`, `formaDosCheckpoints`) e `scripts/_disco.mjs:149` (`lerArquivos`): casas mecânicas para origem, teto de passo e contagem de checkpoints; `tests/scripts/plan.test.mjs` e `_apoio.mjs` dependem do formato atual.
- `templates/agents/claude/implementador.md:10` e `codex/implementador.toml:9`: mandam ler `SKILL.md`, `delegation.md` e `implement.md`, que são manual do líder.
- `templates/agents/claude/explorador.md:6` sem Bash e `codex/explorador.toml:6` com sandbox read-only: o explorador não consegue verificar fato por comando.
- `delegation.md:7`: o líder não escolhe modelo nem esforço; "esforço" também nomeia a rota em `AGENTS.md:8` e `SKILL.md:17`.
- `AGENTS.md:36`: a regra de consistência que proíbe `xhigh` e `max` acusaria os perfis, que usam esses níveis.
- `AGENTS.md:57` e `README.md:133-135`: versão atual 5.3.0.
- `skills/vibeflow/references/interview.md:9` e `delegation.md:21`: o líder lê só o necessário e delega leitura ampla; não há noção de núcleo do projeto que ele precise conhecer de primeira mão.
- `skills/vibeflow/references/delegation.md:29-40`: a conferência do líder é de forma e direção sem referência; "não revisa linha a linha" e "não reexame do conteúdo".
- `skills/vibeflow/references/init.md` e `skills/vibeflow/templates/AGENTS.md`: o init não registra referências centrais do projeto consumidor; `skills/vibeflow/scripts/governanca.mjs` confere o resultado do init.

## Decisões

1. Fato verificável (valor, limite de API, prazo, comportamento de biblioteca ou serviço, formato de dado) nunca é assumido nem perguntado: o explorador o verifica por sondagem antes de gravar a spec, e a evidência entra em Pontos do projeto. O explorador ganha shell só para leitura e consulta, sem escrita fora das saídas normais dos comandos, como o verificador. Pergunta: quem executa a sondagem que verifica um fato antes da spec? Motivo: decisão do humano; reaproveita o agente que já leu o pedido.
2. Fato que só se prova implementando vira o passo 1 do plan; se o resultado contradiz a spec, o encadeamento para e o líder leva ao humano. Dizer "verifico depois" sem esse passo é proibido. Pergunta: o que fazer com fato que a sondagem não alcança? Motivo: assumida; no fabula, promessas de verificar no plano sumiram.
3. Todo valor numérico, prazo, limite ou comportamento externo em Decisões e Critérios de aceite traz a origem `verificado (<fonte>)`, `humano` ou `assumida`; decisão de preferência (cor, nome, ordem) não precisa. Vale para spec nova; spec já aprovada não é revalidada. O fechamento da spec lista todas as assumidas antes de pedir aprovação. `scripts/plan.mjs --spec` aponta valor sem origem nessas seções, exceto nas linhas de tabela de exemplos e em spec com `# Status: aprovado`. A mudança é minor, versão 5.4.0. Pergunta: a marca de origem é obrigatória? Motivo: decisão do humano; o prazo de 5 anos do fabula entrou na spec sem marca.
4. A origem `assumida` de um valor é o valor que nem fonte verificada nem o humano sustentam e difere da decisão assumida pelo líder, que mantém a marca atual. "Esforço de raciocínio" nomeia o nível do modelo e "esforço" segue nomeando a rota; a regra de consistência do `AGENTS.md` passa a dizer "as rotas `xhigh` ou `max`". Pergunta: como evitar termos com dois sentidos? Motivo: assumida; o mapa achou três sentidos para "assumida" e dois para "esforço".
5. Cada phase tem no máximo dois checkpoints: um depois do primeiro grupo de risco, que é o caminho fino, e, se a phase tem tela, um depois do primeiro grupo que entrega tela. Em high sem `# Risco:`, o primeiro vai depois do caminho fino do critério central (assumida). O E2E das demais telas fica para a regressão completa da review. Pergunta: quando o plan marca um checkpoint? Motivo: decisão do humano; a regra por tela manteria 7 de 8 checkpoints na phase-2 do fabula.
6. Phase com até 5 passos não tem checkpoint. Pergunta: o que é phase pequena? Motivo: decisão do humano; a review cobre sozinha.
7. O verificador não reroda a prova dos passos: roda o E2E dos critérios com tela do grupo e confere o diff do grupo contra os critérios, com brief que traz só o diff e os critérios. Pergunta: o que o checkpoint executa? Motivo: decisão do humano; os testes ocupavam até 3,2 min de checkpoints de 6 a 14 min.
8. O desenho de casos de `references/testes.md` é teto: para limite, o próprio limite e o primeiro valor recusado. Caso ausente só é Required na review quando a spec traz o limite ou a tabela explicitamente; nos demais, é Nit. Pergunta: o desenho de casos é piso ou teto? Motivo: assumida; evita oito testes obrigatórios por critério.
9. O implementador captura a tela uma vez por critério com tela, ao fechar o passo, e não a cada iteração; a conferência do líder exige essas imagens finais. Pergunta: quando o implementador captura? Motivo: assumida; no fabula, passos rodaram de 11 a 23 E2E para captura.
10. Na interview, o limite de duas perguntas vale para ajuste de tela; tela nova, site ou fluxo novo cobre navegação, páginas e jornada. Pergunta: quantas perguntas de tela a interview faz? Motivo: assumida; na phase-2 do fabula, a UX só entrou porque o humano pediu, gerando 7 decisões e 16 critérios.
11. O implementador tem referência própria e curta, `skills/vibeflow/references/implementador.md`, com recorte, provas, captura e relatório fixo, que aponta para `references/testes.md` (Política de testes e Desenho de casos) sem copiá-lo. A seção "Trabalho de quem implementa" sai de `implement.md` e passa a morar só ali. O perfil do implementador, nos dois hosts, lê só essa referência. Pergunta: o que o implementador lê ao começar um passo? Motivo: decisão do humano; corta cerca de 20 mil tokens de skill por passo.
12. O brief do passo traz o mapa do explorador do plan para aquele recorte (consumidores, testes afetados e padrão a seguir), e o "Reconhecer" vira confirmação desse mapa. Pergunta: como o implementador evita reexplorar? Motivo: assumida; 41% do contexto medido veio de leitura por shell.
13. O teto de um passo é 12 entradas de código em `Arquivos:`, com pasta contando como uma; testes não contam (path em `tests/`, `test/` ou `__tests__/`, ou nome `*.test.*` ou `*.spec.*`, reconhecimento assumido). Acima disso, o plan divide pelo resultado verificável e o analyze divide em vez de engordar; `scripts/plan.mjs` aponta o passo acima do teto. Pergunta: qual o teto de um passo? Motivo: decisão do humano; mede o código que o implementador precisa entender.
14. O explorador do plan inclui em `Arquivos:` os testes que a mudança quebra por snapshot, schema ou seletor, e o analyze confere. Pergunta: como evitar ampliação de recorte no meio do passo? Motivo: assumida; as devoluções do líder no fabula foram quase todas ampliação de recorte.
15. O líder escolhe o esforço de raciocínio do implementador a cada despacho, conforme o passo, com teto `xhigh`; o modelo continua vindo do perfil, e o perfil define o esforço padrão usado quando o host não aceita esforço no despacho. Não há perfil novo. Substitui, para o esforço, a regra de `delegation.md:7`. Pergunta: como fica o esforço do implementador? Motivo: decisão do humano; passo mecânico não paga o raciocínio de passo crítico.
16. Provas rodam com saída resumida, e o relatório traz só as falhas e o resumo. Pergunta: como evitar que a saída de teste encha o contexto? Motivo: assumida; reduz contexto sem perder a prova.
17. O `AGENTS.md` do projeto consumidor tem a seção `## Núcleo do projeto`, uma linha por item com path, o que é e quando ler (por exemplo, `identidade/`: marca, pranchas e tom; ler em qualquer entrega com tela pública). O init a monta com o explorador e o humano confirma. O líder abre ele mesmo, sem resumo e inclusive as imagens, os itens que o pedido toca, na abertura da interview e antes de conferir uma entrega daquela área. O `AGENTS.md` continua fonte única. Pergunta: onde fica registrado o núcleo do projeto que o líder precisa conhecer? Motivo: decisão do humano; no fabula, o líder decidiu a direção visual sem ver a marca.
18. A conferência de uma entrega que toca o núcleo é de direção contra a referência: o líder compara a evidência (capturas, resposta da API, texto renderizado) com o item do núcleo que abriu e devolve ao dono a divergência com apontamento concreto, sem revisar código linha a linha, que segue com o verificador e o revisor. O brief do passo cita os itens do núcleo que o implementador abre, para ele trabalhar sobre a referência real. Pergunta: como o líder confere uma entrega que toca o núcleo? Motivo: decisão do humano; sem referência, o líder aceita o que não consegue julgar.
19. Projeto sem a seção `## Núcleo do projeto`: na primeira rota com phase, o líder pede ao explorador a proposta da seção e a leva ao humano para confirmar, como reparo do init; `scripts/governanca.mjs` aponta a ausência da seção como aviso, sem bloquear. Pergunta: o que acontece em projeto que já existe sem a seção? Motivo: assumida; projetos como o fabula não têm a seção hoje.

## Critérios de aceite

- A1: Spec em rascunho com decisão ou critério que traz número e unidade sem origem; quando o líder confere a forma da spec com `scripts/plan.mjs`, o achado de valor sem origem aparece.
- A2: A mesma spec com a origem marcada nesse valor; quando conferida, o achado de valor sem origem não aparece.
- A3: Valor sem origem só em linha de tabela de exemplos, ou em spec com `# Status: aprovado`; quando conferida, nenhum achado de valor sem origem aparece.
- A4: Plan com passo de 13 entradas de código em `Arquivos:`; quando conferido por `scripts/plan.mjs`, o passo acima do teto é apontado.
- A5: Plan com passo de 12 entradas de código e testes a mais em `Arquivos:`; quando conferido, nenhum achado de teto aparece.
- A6: Plan com mais de dois checkpoints; quando conferido, o excesso de checkpoints é apontado.
- A7: Plan de até 5 passos com checkpoint; quando conferido, o checkpoint indevido é apontado.
- A8: Os testes de scripts existentes continuam passando, sem teste apagado, pulado ou afrouxado.
- A9: O perfil do implementador, nos dois hosts, manda ler só `references/implementador.md`.
- A10: `implement.md` não contém mais o trabalho de quem implementa, e `references/implementador.md` aponta para `references/testes.md` sem copiar regra de teste.
- A11: O perfil do explorador, nos dois hosts, permite shell só para leitura e consulta e proíbe escrita fora das saídas normais dos comandos.
- A12: Nenhum arquivo do pacote, do `README.md` ou do `AGENTS.md` mantém como vigente checkpoint por grupo de risco, verificador rerodando prova de passo, limite de duas perguntas para tela nova ou proibição de o líder escolher esforço.
- A13: O bloco da cadeia do `AGENTS.md` e o do `templates/AGENTS.md` continuam iguais entre si.
- A14: O `AGENTS.md` declara a versão 5.4.0, e o `README.md` descreve as novidades da 5.4.0 como minor, sem migração.
- A15: `AGENTS.md` de projeto consumidor sem a seção `## Núcleo do projeto`; quando o resultado do init é conferido por `scripts/governanca.mjs`, a ausência aparece como aviso e não como falha.
- A16: O mesmo `AGENTS.md` com a seção; quando conferido, nenhum aviso de núcleo aparece.
- A17: O modelo `templates/AGENTS.md` traz a seção `## Núcleo do projeto` com a forma de linha (path, o que é, quando ler) e o init descreve como montá-la com o explorador e a confirmação humana.
- A18: A interview e a conferência do líder mandam o líder abrir ele mesmo os itens do núcleo que o pedido toca, e a conferência de direção compara a evidência com esse item, sem revisão de código linha a linha.
- A19: O brief do passo e `references/implementador.md` citam os itens do núcleo que o implementador abre.

## Fora do escopo

- Revalidar specs aprovadas nos projetos consumidores: a decisão 3 vale só para spec nova.
- Perfil novo de implementador por esforço: a decisão 15 resolve no despacho.
- Marcador mecânico de "tela" ou "risco" por passo: o plan decide e o analyze julga em prosa.
- Medir o efeito em A/B: a evidência final é o uso real numa phase.
- Corrigir `.erros-encontrados/validador-generico-rejeita-frontmatter-vibeflow.md`: a phase não muda o frontmatter do `SKILL.md`.
- Preencher a seção `## Núcleo do projeto` nos projetos consumidores existentes: acontece no próximo uso com phase de cada projeto (decisão 19).

- [x] Aprovação humana (leu o arquivo e confirmou): 2026-11-01, Marco: "Aprovado" (ajuste com as decisões 17 a 19)
