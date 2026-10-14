# vibe-review, análise

## Problema

Review precisa julgar o diff e a cobertura sem virar uma segunda implementação nem espalhar vereditos por arquivos. O contrato anterior ainda descrevia um transporte temporário na primeira passagem, embora re-review já editasse o vivo.

## Decisão de desenho

```text
diff + artefatos da cadeia
  → seleção de review final, ou checkpoint declarado nos protocolos históricos
  → coordenacao-v1 A: auditoria do executado em execution.json
  → auditoria dirigida e provas por protocolo (regressão completa em coordenacao-v1 A)
  → first-pass prepara review.md
  → IA grava escopo, provas, etapa, R* e veredito diretamente
  → checkpoint: marco julgado, fase continua aberta
  → humano confirma ou pede correção
  → re-review acrescenta etapa no mesmo arquivo
  → review final: integração julgada, Approve confirmado, commit residual e push final da phase
```

A IA começa recuperando a solicitação original e suas alterações humanas; depois localiza os T*/diff relevantes à pergunta de auditoria. Usa `rg --files` e `rg -n` para localizar paths, símbolos, testes e referências aplicáveis, abrindo somente as dependências do fluxo. O status, as dependências/bloqueios, os paths e as provas de cada task ficam no `execution.json` no `coordenacao-v1` Modo A e no `plan.md` nos protocolos históricos, e são conferidos contra o diff integrado. `implement.md` histórico não é requisito. O histórico do chat não substitui a prova no disco.

Um slug explícito expressa outro pedido e deve prevalecer sobre a sugestão automática do inventário. Preview e apply conservam essa seleção para evitar que um plan pendente de outra entrega absorva a review avulsa. Slug e dir juntos são ambíguos e recusados antes de escrita.

Toda correção pertinente, inclusive nit, precisa ser resolvida antes de aprovar. A severidade conserva a informação de impacto e prioridade, mas deixa de autorizar dispensa. R* Optional/FYI históricos seguem obrigatórios quando abertos; novas informações sem remédio ficam em Notas, sem R*. Preserve o histórico sem oferecer defer em novas etapas. Preferência pessoal sem fundamento não entra como achado.

## Escrita direta e etapas

`review.md` é a fonte viva do julgamento. O motor prepara um arquivo vazio na primeira passagem e preserva o existente em todas as outras. Cada etapa identifica se é checkpoint ou review final e registra seu escopo e as provas reaproveitadas ou executadas. A IA fecha R* com prova e atualiza o veredito final diretamente.

Essa escolha mantém o histórico no mesmo path e permite que implement consuma a fila de remédio sem interpretar outro formato. A sincronização de decisões em `AGENTS.md` continua explicitamente pós-aprovação humana.

## Checkpoint e review final

Re-review começa pelo remédio aplicado e seus consumidores/dependências. O julgamento das partes inalteradas e suas provas válidas continua aproveitável; repetir uma auditoria inteira exige lacuna ou risco concreto. O revisor independente verifica as referências, o diff e os inputs atuais, sem reproduzir no review o snapshot que pertence ao registro do protocolo (execution.json no novo A, plan nos históricos). Essa economia alcança a coordenação e qualquer suíte do projeto consumidor, além dos testes internos do VibeFlow.

Checkpoint existe somente em `etapas-v1`, Modo B e legado, e só ocorre no marco declarado e justificado pelo `plan.md`, depois que as tasks desse marco estão concluídas. Ele verifica o contrato compartilhado ou risco antes das tasks seguintes. A fila ainda aberta fica explícita; o resultado limita-se ao marco, mantém a fase em andamento e não libera decisão, commit residual ou push.

A review final aguarda todas as T* concluídas, julga os critérios de aceite sobre o código integrado e revisa os riscos tocados pelo diff. Provas verdes por task são reaproveitadas quando os inputs cobertos continuam iguais e o estado atual continua no escopo. Uma edição posterior em código/teste invalida somente a prova afetada; atualizar os artefatos de registro não a invalida. Fora da regressão completa, a review executa somente o que falta para provar a integração ou um risco alterado, evitando rodar a matriz completa de cada T* por padrão. Implementador verifica localmente fluxo/consumidores; verificador certifica integração proporcional e revisor audita cobertura/validade. Nos protocolos históricos, integração não implica suíte completa, cuja necessidade vem de risco, consumidores afetados, lacuna concreta ou CI obrigatório e exige motivo registrado; em coordenacao-v1 A, vale a regressão completa descrita abaixo. Troca de etapa ou papel não justifica repetição. Simplificação, reutilização, remoção de redundância e otimização de desempenho fundamentada permanecem no recorte, com comportamento, segurança e cobertura preservados e sem abstração especulativa ou limpeza externa.

## Regressão completa na review (coordenacao-v1 A)

Com coordenação por ondas, várias T* terminam em paralelo e cada uma toca poucos arquivos. Rodar a suíte inteira por T* ou na verificação multiplicaria o custo e a mediria sobre um estado ainda parcial. A regressão completa passa a ter uma única dona: a review final, que é o único ponto com o código integrado, commitado e julgado por quem não o escreveu. Implementador e verificador provam o recorte afetado; a review prova que o recorte não quebrou o resto.

Por isso a review executa sempre a `Regressão completa` declarada no plan, uma vez, e registra comando, resultado, HEAD e se código e teste estavam sem modificações não commitadas. Segurança, paridade e CI obrigatório deixam de ser válvulas a decidir caso a caso, porque a regressão já os executa. O custo aceito é descobrir uma regressão no fim, o que vira um `R*` `Required` e uma rodada de correção.

A re-review volta a provar só o afetado pela correção. Repetir a regressão completa só faz sentido quando código ou teste mudou, commitado ou não, depois da última execução verde, pois sem mudança o resultado verde continua descrevendo o mesmo código. Mudança só em artefatos da cadeia dentro de `.vibeflow/` não altera o que a suíte exercita, mesmo quando já foi commitada; por isso a comparação olha os paths fora de `.vibeflow/`, não a igualdade do HEAD. O corte é conservador: docs, skills e config também forçam a repetição, para não depender de julgar caso a caso o que a suíte exercita, e a definição operacional mora em `vibe-review/SKILL.md` §3. A finalização Git aplica a mesma regra, para que atualizar o review.md não force uma nova regressão.

A regressão roda com a árvore limpa nos paths de código e teste. Modificação não commitada mediria um estado que ninguém certificou e que o commit não contém; por isso a review pede isolamento ao coordenador em vez de registrar um verde ambíguo. A sincronização de `## Decisões vigentes` em `AGENTS.md`, feita na finalização depois do Approve, não muda o que a suíte exercita; por isso a comparação a desconsidera quando todos os hunks do diff de `AGENTS.md` caem nessa seção, e qualquer outra mudança no arquivo continua contando.

O julgamento de código segue limitado ao diff e aos consumidores afetados, e a matriz de cobertura da origem segue obrigatória; a regressão não substitui nenhum dos dois. Plans anteriores a esta regra não têm a seção `Regressão completa`; para eles, a verificação agregada do repo faz esse papel e a origem fica registrada na etapa. Etapas-v1, Modo B e legado conservam a regra histórica, sem migração.

## Sem checkpoint no Modo A

No `coordenacao-v1` Modo A, as T* terminam em ondas, a integração é certificada uma vez e a review final cobre a phase inteira com a regressão completa. Um checkpoint intermediário julgaria um estado que a próxima onda ainda muda e duplicaria o trabalho da review final; o plan não o promete e a review não o executa. Os protocolos históricos conservam o checkpoint de marco, sem migração.

## Auditoria do executado

No Modo A, a implement registra em `execution.json` o que cada T* provou, com inputs e hashes, e o commit real da integração. A review usa esse registro para conferir ownership e cobertura, não para repetir provas: inputs de cada T* dentro do seu `Arquivos:` mostram que a escrita respeitou o recorte; o diff desde `integracao.origem` dentro da união dos `Arquivos:` mostra que nada entrou fora do plan; e o consumidor compartilhado entre T* que podem ter corrido juntas é o único ponto em que mudanças paralelas, cada uma verde sozinha, podem se contradizer. Como o registro não guarda a onda real, a conferência cobre todo par de T* sem `Deps` entre si. Input fora do recorte que a phase não altera é consumidor lido pela prova, como a suíte contratual de uma T* de prosa, e não indica escrita fora do ownership.

Na re-review, `correcao.commit` liga a correção ao commit da integração. O motor já recusa commit que não descende dele ou cujos blobs divergem da prova atual; a review acrescenta a conferência semântica de que os IDs do título são exatamente os R* marcados. R* cujo remédio altera `Arquivos:` da phase traz `papel: corretor | redator`, porque a implement roteia correção de prosa ao redator e de código ao corretor, e o revisor é quem melhor sabe a natureza do remédio. O redator não edita plan, spec, review nem `AGENTS.md`; remédio nesses arquivos fica com o finalizador ou, no `review.md`, com o revisor.

O revisor delegado não corrige o motor quando o §0 revela defeito: corrigir quebraria a independência e o ownership das ondas. O defeito vira bloqueio ou R*, e a correção segue pelo papel responsável.

## Finalização Git

Review continua sem corrigir source. Somente a review final pode abrir fechamento Git, e só depois da confirmação humana. No Modo A do `vibe-implement`, coordenacao-v1 delega esse fechamento ao finalizador genérico/default apto; coordenador conduz a confirmação e o revisor delegado só devolve a proposta e perguntas. Etapas-v1/legado conservam operação do coordenador. Depois de Approve confirmado, todas as tasks e R* bloqueantes fechados e a prova necessária da integração verde, ela valida o escopo restante, cria somente o commit residual da phase quando houver mudanças e faz `git push` para o upstream atual sem force. Checkpoint não fecha a phase nem dispara publicação.

## Visual e acessibilidade

Quando a aceitação depende da UI renderizada, a review usa a classificação `Visual` do plan e começa pela rota/tela, estado e viewport afetados. Tocar arquivo de UI, HTML ou DOM não aciona inspeção por si só. A evidência da implementação é reaproveitada se os inputs continuarem válidos e ela cobrir a integração; navegador integrado é a primeira opção, Chrome DevTools MCP cobre inspeção, e Playwright só entra se já existir ou for solicitado. Screenshot isolado não substitui a leitura de comportamento, geometria, estados e console/rede/assets relevantes.

Controles compactos reduzem ruído apenas quando a ação é universalmente reconhecível. `icon-only` exige semântica acessível, foco, área de interação e feedback; ação ambígua mantém texto.

## Chat

Review recomenda novo chat, separado da implementação, para avaliar o resultado com contexto focado. Se o humano preferir continuar na conversa atual, prossiga sem bloquear; `review.md` e diff carregam o contexto verificável.

## Revisor delegado

O contexto limpo que o chat novo dava à review vem de graça num subagente, e o coordenador não perde a vez de falar com o humano: o revisor grava a etapa e devolve veredito, R* e perguntas, e o coordenador conduz a correção e a confirmação. O revisor usa o perfil forte, porque julgar integração e riscos é a etapa em que um erro custa mais. Começa com um único revisor; dividir a review por dimensão aumentaria o custo de tokens sem necessidade comprovada.

## Cortes

| Corte | Motivo |
|---|---|
| `vibe-converge` separado | Cobertura e julgamento ficam na mesma review. |
| Correção de código pela review | Finding deve apontar o remédio para implement. |
| Segundo `review.md` por rodada | Etapas no mesmo arquivo preservam o veredito vigente. |
| Checkpoint automático por contagem de tasks | O plan só pede marco intermediário quando existe risco ou contrato que precise de julgamento antecipado. |
| Checkpoint no `coordenacao-v1` Modo A | A review final cobre a phase inteira; checkpoint julgaria estado parcial entre ondas. |
| Repetir toda a matriz de testes por T* na review final | Evidências válidas são reaproveitadas; além da regressão completa em coordenacao-v1 A, a review fecha apenas lacunas de integração e riscos alterados. |
| Regressão completa por T* ou na verificação (coordenacao-v1 A) | Custo multiplicado por onda e medição sobre estado parcial; a review final roda uma vez, no estado integrado. |
| Regressão completa repetida a cada re-review | Só se repete quando código ou teste mudou desde a última execução verde. |
| Navegador em toda alteração de UI | A prova visual só abre quando o aceite depende do resultado renderizado; a review reutiliza evidência válida. |
| Publicação automática de decisões | Exige Approve sem bloqueios e confirmação humana. |
| Push antes da aprovação | O remoto só recebe a phase depois do fechamento da review. |
| Revisor delegado com finalização própria | O revisor não pergunta ao humano nem toca Git; coordenador conduz a confirmação única; finalizador apto opera push no novo A após autorização explícita. |
| Campo novo no template para o relatório do revisor | Tudo que o relatório carrega já tem lar no `review.md`, e perguntas em aberto no arquivo são defeito. |

## Impacto

O `plan.md` mantém a trilha executável das T*, enquanto `review.md` mantém os R*, etapas e vereditos. Implement prova os remédios no plan e a review confere os paths no diff antes de fechar o item. Nos protocolos históricos, checkpoints preservam o marco sem simular conclusão de feature; a etapa final valida a integração com provas proporcionais, ou com a regressão completa em coordenacao-v1 A. A troca de chat não perde o julgamento porque os registros vivos permanecem no disco.

## Completude pela origem

A execução começa recuperando o pedido original e suas alterações humanas. Depois confronta spec, plan, implementação e provas. Isso permite identificar uma capacidade obrigatória que desapareceu da decomposição, mesmo quando as tasks previstas e seus testes estão corretos. A matriz no review mantém a fonte, a implementação, a evidência e a situação de cada obrigação em um único lugar. Retirada humana explícita permanece visível com sua decisão, evitando transformar redução autorizada em falso bloqueio.

Ausência ou atendimento parcial de obrigação abre correção bloqueante. Sem origem suficiente, o revisor limita o que pode afirmar e devolve a necessidade de contexto ao coordenador. Provas e commits são conferidos contra a integração atual, incluindo commits de várias tasks e histórico legado; nomes de commits não substituem essa conferência. Os dois cenários descartáveis do piloto exercitam essa decisão com revisor independente, além das suítes mecânicas dos motores.
