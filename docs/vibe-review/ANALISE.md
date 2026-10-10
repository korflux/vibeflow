# vibe-review, análise

## Problema

Review precisa julgar o diff e a cobertura sem virar uma segunda implementação nem espalhar vereditos por arquivos. O contrato anterior ainda descrevia um transporte temporário na primeira passagem, embora re-review já editasse o vivo.

## Decisão de desenho

```text
diff + artefatos da cadeia
  → seleção de checkpoint declarado ou review final
  → auditoria dirigida e prova proporcional
  → first-pass prepara review.md
  → IA grava escopo, provas, etapa, R* e veredito diretamente
  → checkpoint: marco julgado, fase continua aberta
  → humano confirma ou pede correção
  → re-review acrescenta etapa no mesmo arquivo
  → review final: integração julgada, Approve confirmado, commit residual e push final da phase
```

A IA começa recuperando a solicitação original e suas alterações humanas; depois localiza os T*/diff relevantes à pergunta de auditoria. Usa `rg --files` e `rg -n` para localizar paths, símbolos, testes e referências aplicáveis, abrindo somente as dependências do fluxo. O status, as dependências/bloqueios, os paths e as provas de cada task ficam no `plan.md`, que é conferido contra o diff integrado. `implement.md` histórico não é requisito. O histórico do chat não substitui a prova no disco.

Um slug explícito expressa outro pedido e deve prevalecer sobre a sugestão automática do inventário. Preview e apply conservam essa seleção para evitar que um plan pendente de outra entrega absorva a review avulsa. Slug e dir juntos são ambíguos e recusados antes de escrita.

O defer adia apenas melhorias não bloqueantes identificadas, com motivo e retomada registrados. Ele não substitui atendimento da solicitação, contexto suficiente ou correção de Critical/Required.

## Escrita direta e etapas

`review.md` é a fonte viva do julgamento. O motor prepara um arquivo vazio na primeira passagem e preserva o existente em todas as outras. Cada etapa identifica se é checkpoint ou review final e registra seu escopo e as provas reaproveitadas ou executadas. A IA fecha R* com prova e atualiza o veredito final diretamente.

Essa escolha mantém o histórico no mesmo path e permite que implement consuma a fila de remédio sem interpretar outro formato. A sincronização de decisões em `AGENTS.md` continua explicitamente pós-aprovação humana.

## Checkpoint e review final

Re-review começa pelo remédio aplicado e seus consumidores/dependências. O julgamento das partes inalteradas e suas provas válidas continua aproveitável; repetir uma auditoria inteira exige lacuna ou risco concreto. O revisor independente verifica as referências, o diff e os inputs atuais, sem reproduzir no review o snapshot que já pertence ao plan. Essa economia alcança a coordenação e qualquer suíte do projeto consumidor, além dos testes internos do VibeFlow.

Checkpoint só ocorre no marco declarado e justificado pelo `plan.md`, depois que as tasks desse marco estão concluídas. Ele verifica o contrato compartilhado ou risco antes das tasks seguintes. A fila ainda aberta fica explícita; o resultado limita-se ao marco, mantém a fase em andamento e não libera decisão, commit residual ou push.

A review final aguarda todas as T* concluídas, julga os critérios de aceite sobre o código integrado e revisa os riscos tocados pelo diff. Provas verdes por task são reaproveitadas quando os inputs cobertos continuam iguais e o estado atual continua no escopo. Uma edição posterior em código/teste invalida somente a prova afetada; atualizar os artefatos de registro não a invalida. A review executa somente o que falta para provar a integração ou um risco alterado, evitando rodar a matriz completa de cada T* por padrão.

## Finalização Git

Review continua sem corrigir source. Somente a review final pode abrir fechamento Git, e só depois da confirmação humana. No Modo A do `vibe-implement`, quem executa esse fechamento é o coordenador, porque o revisor delegado só devolve a proposta e as perguntas. Depois de Approve confirmado, todas as tasks e R* bloqueantes fechados e a prova necessária da integração verde, ela valida o escopo restante, cria somente o commit residual da phase quando houver mudanças e faz `git push` para o upstream atual sem force. Checkpoint não fecha a phase nem dispara publicação.

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
| Repetir toda a matriz de testes por T* na review final | Evidências válidas são reaproveitadas; a review fecha apenas lacunas de integração e riscos alterados. |
| Navegador em toda alteração de UI | A prova visual só abre quando o aceite depende do resultado renderizado; a review reutiliza evidência válida. |
| Publicação automática de decisões | Exige Approve sem bloqueios e confirmação humana. |
| Push antes da aprovação | O remoto só recebe a phase depois do fechamento da review. |
| Revisor delegado com finalização própria | O revisor não pergunta ao humano nem toca Git; a confirmação única e o push ficam com o coordenador. |
| Campo novo no template para o relatório do revisor | Tudo que o relatório carrega já tem lar no `review.md`, e perguntas em aberto no arquivo são defeito. |

## Impacto

O `plan.md` mantém a trilha executável das T*, enquanto `review.md` mantém os R*, etapas e vereditos. Implement prova os remédios no plan e a review confere os paths no diff antes de fechar o item. Checkpoints preservam o marco sem simular conclusão de feature; a etapa final valida a integração com provas proporcionais. A troca de chat não perde o julgamento porque os registros vivos permanecem no disco.

## Completude pela origem

A execução começa recuperando o pedido original e suas alterações humanas. Depois confronta spec, plan, implementação e provas. Isso permite identificar uma capacidade obrigatória que desapareceu da decomposição, mesmo quando as tasks previstas e seus testes estão corretos. A matriz no review mantém a fonte, a implementação, a evidência e a situação de cada obrigação em um único lugar. Retirada humana explícita permanece visível com sua decisão, evitando transformar redução autorizada em falso bloqueio.

Ausência ou atendimento parcial de obrigação abre correção bloqueante. Sem origem suficiente, o revisor limita o que pode afirmar e devolve a necessidade de contexto ao coordenador. Provas e commits são conferidos contra a integração atual, incluindo commits de várias tasks e histórico legado; nomes de commits não substituem essa conferência. Os dois cenários descartáveis do piloto exercitam essa decisão com revisor independente, além das suítes mecânicas dos motores.
