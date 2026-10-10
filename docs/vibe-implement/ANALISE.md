# vibe-implement, análise

## Problema

A implementação precisava executar uma fila verificável sem perder histórico quando a execução mudasse de chat. O plan já continha tasks e dependências, então um segundo registro acumulativo duplicava status, paths e provas e podia divergir da fila.

## Decisão de desenho

O protocolo `etapas-v1`, selecionado explicitamente no plan, separa código, complementação de testes e validação integrada. O implementador libera dependentes após checagem local válida; o coordenador mantém `[ ]` até a integração ser comprovada por executor separado do escritor. Falha pré-review volta ao corretor sem criar R* artificial. Um commit integrado registra todas as T* comprovadas. O protocolo antigo e o Modo B continuam com commits por task, preservando runs em andamento.

Snapshots ficam no próprio plan e identificam HEAD, inputs, comando e resultado. O motor confere os hashes, sem executar o comando informado. Essa separação evita repetir suites completas por task e impede reaproveitar evidência de inputs alterados. O coordenador reutiliza implementadores relacionados quando útil e mantém um único escritor por vez; a review continua independente.

Fluxo histórico (plan sem marcador):

```text
JSON compacto → alvo, fila.elegiveis, etapa, rodadas_correcao e avisos
  → apply valida o alvo sem criar artefato de execução
  → investigação dirigida da T* e do fluxo real
  → Modo A: coordenador delega a T* a um implementador; Modo B: execução inline
  → integração pelo coordenador e simplificação
  → prova proporcional após a última edição de código/teste, com repetição somente após falha ou invalidação dos inputs
  → IA registra status, paths, prova e bloqueios sob a T* no plan
  → spec/review recebem somente marcações provadas
  → staging explícito e commit da T* sem push
  → Modo A: fila concluída → revisor → corretor (até 2 rodadas) → pergunta única → finalização
  → Modo B: handoff vibe-review ou próxima T*
```

O parser continua deliberadamente pequeno. A ordem sai do plan, as dependências saem de `Deps` e o significado de aceite continua na IA. Assim, não há reimplementação do parser em cada chat.

## Delegação e integração

A implementação era a etapa mais lenta: cada T* esperava uma rodada humana, e o contexto inchava quando o plano rodava inteiro num único chat. No Modo A o chat do `/vibe-implement` vira coordenador e entrega cada T* a um subagente que nasce com contexto limpo, o que faz automaticamente o que o chat por T* fazia à mão. O coordenador não escreve código, para que cada papel tenha um único dono.

Os papéis são descritos por perfil (explorador, verificador, implementador ou corretor, revisor) e nunca por nome de modelo, porque nomes envelhecem e variam por host. O contrato mora em `references/delegation.md`, copiado de forma idêntica em `vibe-plan` e `vibe-implement`; o template do `vibe-init` recebe somente a regra operacional de registro e Git do novo protocolo, sem duplicar o catálogo de papéis distribuídos ou suas instruções.

O relatório de subagente é evidência a conferir, como a saída de script. O coordenador confere paths, diff e prova antes de registrar. Só ele altera `plan.md`, `spec.md`, `review.md` e o índice Git, decide os paths do commit e registra a conclusão; o revisor é a exceção controlada porque grava o `review.md`, artefato da própria skill. Como o implementador trabalha na mesma árvore, em sequência, a prova dele vale para o recorte e inputs efetivamente cobertos e não é repetida sem motivo; no novo protocolo, a integração é delegada ao verificador. A fila é recalculada após cada registro. No legado/B, depende de conclusão; no novo A, código dependente avança com implementação e checagem local válidas, e conclusão aguarda a prova integrada.

A etapa vem do motor, não da memória do chat: `etapa` e `rodadas_correcao` são derivados de `plan.md` e `review.md`, e uma etapa que o disco não sustenta é `null`, nunca um chute. Isso torna a retomada em outro chat determinística.

## Investigação e prova

Provas proporcionais também se aplicam a qualquer projeto consumidor das skills. A seleção cruza diff, fluxo/consumidores, risco e aceite; código usa checagem local direcionada e a integração executa os comandos compartilhados uma vez sobre os inputs finais. Correções renovam somente evidências afetadas, incluindo suas dependências. Uma prova necessária permanece mesmo quando lenta.

O coordenador reaproveita contexto, agentes relacionados e evidências verificáveis. Busca curta, conferência de relatório e prova integrada já válida não ganham handoff só para representar uma etapa. Execução ampla, vários fluxos/ambientes ou diagnóstico pedem verificador; prova integrada curta já definida pode ser executada pelo coordenador, que não escreveu código/testes. O revisor mantém contexto independente. Registrar o resultado uma vez e referenciá-lo evita transformar a execução em sucessivas reinvestigações e cópias, sem mudar estados, snapshots ou autorização.

A IA formula a pergunta da T*, usa `rg --files` e `rg -n` para localizar pontos de entrada, chamadas, helpers, testes e referências, e expande a leitura apenas quando uma lacuna bloqueia a prova. O inventário seleciona o alvo, mas não autoriza ler a árvore inteira.

Para UI, o contrato escolhe navegador integrado, depois MCP Chrome DevTools, depois Playwright existente ou solicitado. A prova começa pela tela, estado e viewport afetados; só amplia quando o diff alcança layout, responsividade, interação, componente compartilhado ou risco adicional. Uma task de código sem UI não ganha exigência artificial de navegador.

Ao alterar testes, o agente preserva a cobertura observável da jornada e reduz fragmentação redundante. Um fluxo completo vale mais que um teste novo para cada campo ou helper, desde que falhas independentes continuem diagnosticáveis e casos de erro, permissão e borda não desapareçam.

## Escrita direta

O apply valida o alvo e não cria `implement.md`. Depois da prova verde, a IA registra status, comando/resultado da prova, paths e bloqueios diretamente sob a T* no plan. O teste verde é condição para marcar `[x]`; atualizar plan, spec ou review depois da prova não exige outro teste porque não muda os inputs de código/teste validados. Smoke Test acompanha a alteração do ponto de entrada real, não a posição da T* no plan.

## Retomada sem segunda trilha

Uma T* que continua incompleta pode carregar um checkpoint curto no próprio plan: estado, próximo passo, paths que alimentam a prova, `HEAD`, hash Git por path e última prova. Esse registro só existe enquanto a task está aberta e é removido quando ela fecha. Na retomada, a IA compara `git status --short`, `HEAD` e os hashes com o checkpoint; se um input mudou ou faltar snapshot, invalida apenas a prova afetada. Sem mudança nos inputs, reaproveita o resultado e continua do próximo passo. O checkpoint orienta a retomada, mas não substitui a inspeção do diff, os gates da rota nem a fila do plan.

Arquivos `implement.md` de execuções anteriores permanecem byte a byte intactos, mas não entram na seleção do alvo nem são necessários para review. Isso remove uma fonte duplicada sem migrar ou apagar histórico.

## Chat e modos

O plan recomenda com ênfase um chat novo para o implement, sem tornar isso um gate. Nesse chat o Modo A é o padrão e começa sem perguntar o modo, porque perguntar recriaria a espera que o piloto elimina. O Modo B (uma T* por run, com o ciclo inline) entra por pedido, por T* nomeada, por rota `low` ou `medium`, ou por falta de subagentes, com aviso de uma linha. O antigo Modo B, de plano inteiro inline, foi removido: concentrava a fila num contexto só e perdia a retomada.

O piloto só volta ao humano para a pergunta final (aprovar a review, publicar decisões vigentes e fazer push), para uma ambiguidade material ou para um impedimento real. Ferramenta ausente é instalada pela regra única, e prova vermelha é corrigida pela causa raiz sem limite de tentativas, sem enfraquecer teste. O ciclo review e correção para após 2 rodadas e relata, porque mais que isso indica um problema de entendimento que só o humano resolve; ajustes pedidos na pergunta final não contam. Não há regra especial para Critical: o relatório final apenas os destaca.

No Modo B, com várias T*s elegíveis, a skill escolhe a menor sem pedir seleção. Um grupo paralelo registrado no plan continua sendo oferecido ao humano antes de paralelizar; o Modo A é sequencial e ignora o grupo.

## MVP

O gate de analyze continua separado para a rota max. A existência de plan não basta: o analyze precisa estar aprovado e limpo antes do código. A implementação não altera `REGRAS.md`; vigência é uma decisão pós-review.

## Cortes

| Corte | Motivo |
|---|---|
| Documento de tasks paralelo | A fila já está no plan. |
| Documento acumulativo de implementação | O plan já é a fila e o registro durável da execução. |
| Inspeção renderizada em toda mudança de UI | Só é exigida quando o aceite depende da renderização; o plan justifica a dispensa nos outros casos e a review reaproveita evidência válida. |
| Push por task | Mantém o remoto estável durante a implementação; o push fica para a phase aprovada e confirmada. |
| Plano inteiro inline (antigo Modo B) | Inchava o contexto e dependia do chat para retomar; o Modo A cobre a fila inteira com coordenação e retomada pelo disco. |
| Hash de commit no `plan.md` | Reabriria o plan depois do commit da task e criaria um residual; o Git é a fonte e o coordenador informa os hashes no relatório final. |
| Paralelismo no Modo A | Exige contrato de paths, checagem de disjunção e isolamento por worktree; fica para a phase seguinte, depois que o piloto sequencial estiver estável. |
| Checkpoint de review do plan no Modo A | O motor não deriva marcos do plan e a re-review parcial não tem etapa própria; a review final cobre a integração. |
| Fan-out da review por dimensão | Custo de tokens maior sem necessidade comprovada; começa com um único revisor. |
| Bloqueio imediato por ferramenta ausente | Antes de parar, o agente tenta disponibilizar a ferramenta necessária ou uma prova equivalente, respeitando permissões e o aceite. |

## Impacto

A próxima review lê status, dependências/bloqueios, paths e provas no plan e confere tudo contra o diff integrado. A troca de chat deixa de ser uma perda de contexto porque o disco mantém uma trilha única e verificável.
