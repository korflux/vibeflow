# vibe-implement, arquitetura

`/vibe-implement` implementa e prova fatias de código e registra status, paths, prova e bloqueios diretamente na task do `plan.md`. No Modo A, com subagentes, conduz a fila inteira da phase (implementação, review e correção) com uma única confirmação final; no Modo B executa uma T* por run. A IA inspeciona o fluxo, codifica, testa e simplifica; o motor seleciona alvo e fila sem criar um segundo registro. Edição apenas de texto ou documento avulso fica fora desta skill.

```text
.vibeflow/phases/phase-<n>-<slug>/plan.md
.vibeflow/phases/phase-<n>-<slug>/spec.md
.vibeflow/phases/phase-<n>-<slug>/review.md
.vibeflow/mvp/plan.md
```

## 1. Papéis e ownership

| Peça | Responsabilidade |
|---|---|
| `SKILL.md` | Seleção de modo, coordenação do Modo A pela etapa do motor, tabela de paradas e regra de instalação, ciclo de seis passos, prova final, commit da task, confirmação final e retomada. |
| `references/delegation.md` | Papéis por perfil, pedido e relatório fixo de subagente, escritor único, conferência e fallback. Cópia idêntica à de `vibe-plan`, comparada por bytes em `docs/tests/test-distribuicao.py`. |
| `scripts/implement.py`, `implement.ps1`, `implement.sh` | Inventário interno, alvo, fila, etapa da phase, rodadas de correção, gate MVP e JSON operacional compacto no stdout. |
| `references/chrome-devtools.md` | Prova renderizada proporcional, consultada quando o aceite depende do resultado visual. |
| `stdout (JSON)` | Alvo, fila e avisos necessários; no MVP também traz o gate de analyze. O inventário completo não é serializado. |
| `plan.md` | Registro único por T*: status, dependências/bloqueios, verificação, prova, paths e decisões materiais. |

O script não codifica, não escreve a prosa da implementação, não marca aceite e não escolhe semântica.

## 2. Alvo e fila

Sem `.vibeflow/`, `INIT_AUSENTE`. Com plan, o alvo é a maior phase com `plan.md`; `--dir` força uma phase existente. Sem plan, o JSON deixa a fila nula e a skill encaminha `high+` para `vibe-plan`; uma execução avulsa `low/medium` pode usar `--slug`.

O parser lê somente `### T{n}:`, a linha `T{n} concluída` e `Deps`. `fila.elegiveis` contém tasks abertas cujas dependências estão concluídas; `fila.bloqueadas` expõe as dependências faltantes. R* Critical/Required abertos têm prioridade sem alterar o plan. Sem T* nomeada, a skill escolhe a elegível de menor número; múltiplas elegíveis não bloqueiam a execução sequencial.

No MVP, `--mvp` fixa `.vibeflow/mvp/`, exige plan e analyze aprovado com veredito limpo, e não aceita slug ou dir.

## 3. JSON operacional no stdout

O JSON transitório contém somente `alvo`, `fila`, `etapa`, `rodadas_correcao` e `avisos`. O alvo expõe `kind`, `dir`, `n`, `slug` e `path`; no MVP, `analyze_gate` acompanha esses campos. A fila traz parse, status das T*, elegíveis, dependências bloqueantes e avisos do plan. Nenhum item serializa todas as phases.

### Etapa da phase e rodadas de correção

`etapa` e `rodadas_correcao` permitem retomar e coordenar a run pelo disco, sem depender da memória do chat. Os dois motores os derivam só de `plan.md` e `review.md` do alvo, sem escrever arquivo e sem alterar `alvo`, `fila`, `avisos` ou `analyze_gate`. A etapa é a primeira que se aplica, nesta ordem:

| `etapa` | Condição |
|---|---|
| `concluida` | `review.md` com `# Status: aprovado` |
| `corrigir` | há `- [ ] Rn: **Critical**` ou `**Required**` em aberto |
| `confirmar` | fila concluída, status ainda não aprovado e `- [x] **Approve**` ou `- [x] **Approve com defer**` marcado em `## Veredito vigente` |
| `implementar` | há T* elegível |
| `bloqueada` | há T* aberta e nenhuma elegível, por ciclo ou dependência inexistente |
| `revisar` | fila concluída sem veredito final de aprovação, inclusive depois de bloqueios fechados |

`etapa` é `null` quando o estado não pode ser derivado: alvo sem `plan.md`, plan sem nenhuma T* legível, plan com T* sem linha `concluída` (ela some da fila e a conclusão ficaria falsa), ou `review.md` ilegível ou sem `# Status:`. Os dois últimos motivos de `review.md` geram um item em `avisos`; os do plan já aparecem em `fila.avisos`. Nunca há etapa inventada.

`rodadas_correcao` conta as correções já aplicadas, não as reviews que pediram mudança. Cada bloco `### Etapa` da seção `## Etapas` cuja linha `- Veredito desta etapa:` tem exatamente o valor `Request changes` (ponto final opcional) soma 1. A última etapa não soma enquanto ainda houver Critical ou Required em `[ ]`, porque a correção que ela pediu está pendente. A lista de alternativas do template não conta como veredito. Sem `review.md`, ou com `review.md` ilegível, o valor é 0. O coordenador do Modo A para quando `etapa` é `corrigir` e `rodadas_correcao` já é 2.

Limitação conhecida: `Approve com defer` com Critical ou Required em aberto cai em `corrigir` pela precedência. A regra de quando o defer é válido pertence ao `vibe-review` (registro em `.erros-encontrados/2026-10-03-review-approve-com-defer-sem-regra.md`).

## 4. Apply e escrita direta

1. Reexecuta o inventário e a projeção da fila.
2. Valida o alvo e, no MVP, o gate de analyze.
3. Cria somente a pasta da phase quando `--slug` for permitido.
4. Emite o JSON operacional compacto para leitura imediata da IA.
5. Depois da prova verde, a IA atualiza status, prova e paths diretamente sob a T* no `plan.md`.

Apply não cria `implement.md`, não altera arquivos históricos e não escreve a prosa do plan. Spec e review recebem somente os patches semânticos que a skill autoriza, depois da prova verde.

## 5. Ciclo da fatia

Cada T*/R* segue: reconhecer o fluxo real, selecionar execução sequencial ou delegação nativa do host, integrar as mudanças, simplificar e executar a prova final. A prova roda após a última edição de código/teste e cobre o estado integrado. Falha exige diagnóstico e repetição da prova afetada; alteração posterior em um input de código/teste invalida somente as provas que o cobrem. Atualização de plan, spec, review ou metadados não invalida a prova. Smoke Test acompanha mudança real no ponto de entrada, não o número da task.

Ao tocar testes, a unidade preferida é a jornada completa e seus resultados observáveis, por exemplo login, cadastro ou recuperação. A IA procura a prova existente e consolida casos fragmentados da mesma jornada sem perder cenários e afirmações materiais. Testes separados continuam quando risco, comportamento independente ou diagnóstico exigem isolamento.

Delegação tem dois usos. No Modo A ela é o caminho padrão e sempre sequencial: um subagente por T*, na mesma árvore do coordenador. No grupo paralelo do Modo B, só atende T*s elegíveis e independentes, com worktree/branch isolada ou ownership sem sobreposição; sem isolamento seguro, a execução é sequencial. Em ambos, cada entrega recebe resultado, aceite, dependências, paths e comando de verificação, e o coordenador é o único escritor de `plan.md`, `spec.md` e do índice Git (o revisor grava só o `review.md`). No Modo A a prova do implementador vale como prova do estado integrado; no grupo paralelo, a prova reportada por um agente não substitui a verificação do estado integrado.

Inspeção renderizada segue a classificação `Visual` no `plan.md`: ocorre quando o aceite depende da UI renderizada ou quando a implementação revela uma mudança visual relevante não planejada. Alterar arquivo de UI, HTML ou DOM, sem impacto visual no aceite, não aciona navegador. A seleção é navegador integrado quando disponível, MCP Server `chrome-devtools` em seguida, e Playwright somente se já existir no repositório ou for solicitado. Com UI, o `design.md` aprovado do alvo é entrada do reconhecer, com tokens, motion e prova por tela quando aplicável. A checagem começa pela tela, estado e viewport afetados; amplia quando layout, responsividade, interação, componente compartilhado ou risco exigirem. No Express, a implement segue só o recorte existente e alterado do design quando houver, sem exigir design ausente, sem apply de design, sem plan novo e sem reabrir tasks antigas. A prova registra rota, viewport, estado, ações e evidência; sem capacidade visual, a limitação impede marcar a prova visual necessária.

Checkpoint de retomada é um bloco opcional sob uma T* que continua incompleta ou entra em handoff. Registra estado, próximo passo, paths que alimentam a prova, `HEAD`, hashes `git hash-object` desses paths e a última prova. Na retomada, a IA confere `git status --short`, `HEAD` e cada hash antes de reaproveitar a prova; hash divergente ou snapshot incompleto invalida somente a prova afetada. O checkpoint sai do plan quando a task fecha; status, prova e paths finais permanecem na T*.

## 6. Artefato, modos e handoff

`plan.md` mantém status, verificação, prova, paths e bloqueios de cada T*. Achados R* e vereditos continuam no `review.md`. A mensagem e o hash de cada commit ficam no resultado da execução e no chat, sem reabrir o plan após o commit; o Git é a fonte dos hashes (`task(Tn): <outcome>`).

### Modo A (padrão): piloto da phase

Entra sem perguntar o modo quando a rota é `high`, `xhigh` ou `max`, o `plan.md` está aprovado (e o analyze aprovado e limpo quando a rota exige), o host oferece subagentes e o humano não pediu Modo B. O coordenador é o chat do `/vibe-implement`: seleciona, delega, confere, registra e opera o Git, e nunca escreve código. Toda mudança, inclusive correção pequena, passa por um subagente.

A cada transição o coordenador reexecuta o motor e age pela `etapa`:

| `etapa` | Ação |
|---|---|
| `implementar` | Delega a T* elegível de menor número a um implementador, confere o relatório contra `git status`, o diff e a prova, registra no plan e cria o commit `task(Tn)` |
| `revisar` | Delega a review final a um revisor (`vibe-review`, modo subagente) |
| `corrigir` | Com `rodadas_correcao` 2, para e relata; senão delega os R* Critical e Required a um corretor, marca os R* provados, cria o commit `task(Rn)` e delega nova review |
| `confirmar` | Apresenta o relatório final e faz a única pergunta (aprovar a review, publicar as decisões vigentes e fazer push) |
| `bloqueada`, `null` | Relata dependências, ciclo ou avisos e para; a etapa nunca é adivinhada |
| `concluida` | Informa o estado; nada a executar |

Antes de delegar uma T*, o coordenador grava o checkpoint de retomada sob ela (estado, próximo passo, `HEAD`), completado com paths e hashes antes de qualquer pausa. Subagente `pergunta` leva a decisão ao humano, e o piloto segue com T* elegíveis que não dependem da parada. Ferramenta ausente é instalada pela regra única do `SKILL.md` (credencial, conta, pagamento, elevação ou integração persistente vão ao humano); prova vermelha é corrigida pela causa raiz, sem enfraquecer teste.

Com Approve final proposto pelo revisor, o piloto pede a confirmação única. Sem ela, nada de aprovação, sync de `AGENTS.md`, commit residual ou push. Com ela, o coordenador executa a finalização da `vibe-review` (status aprovado, sync de decisões, commit residual, `git push` sem `--force`). Ajuste pedido na resposta vira correção e não conta para o limite de 2 rodadas.

Retomada: um chat novo lê a etapa do motor, o checkpoint, o `review.md` e o Git, valida `HEAD` e hashes e continua do ponto correto, sem refazer T* concluída.

### Modo B: uma T* por run

Entra quando o humano pede uma T* por vez, nomeia uma T*, a rota é `low` ou `medium`, ou o host não oferece subagentes (aviso de uma linha com o motivo). Executa uma T* elegível com o ciclo da fatia inline, registra, cria o commit e responde; “pode seguir” executa a próxima. Um grupo paralelo registrado no plan é oferecido ao humano e só roda com resposta afirmativa, isolamento e ownership seguros. Um pedido de executar tudo, sem subagentes, executa a próxima T* e informa a limitação.

Quando a fila termina, o handoff é `vibe-review`. A resposta do Modo B informa T* executada, total de T*s da fase, concluídas, prova, paths e hash do commit. Recomende chat novo por T* e para review; se o humano preferir o mesmo chat, continue sem bloquear. O plan e o diff são a ponte.

## 7. Erros e testes

Falhas previstas usam `CODIGO: descrição`, incluindo `IMPLEMENT_SEM_ALVO`, `IMPLEMENT_SEM_PLAN`, `IMPLEMENT_ANALYZE_AUSENTE`, `IMPLEMENT_ANALYZE_RASCUNHO`, `IMPLEMENT_ANALYZE_BLOQUEADO`, `FASE_AUSENTE`, `MODO_INVALIDO` e `PHASES_INESPERADO`.

Suítes: `docs/vibe-implement/tests/test-implement.py` e `docs/vibe-implement/tests/test-implement.sh`. Elas cobrem seleção, fila, phase/MVP, preservação, paridade, ordem de conclusão independente e contratos de delegação, ownership, prova final e retomada. As mesmas fixtures de `ETAPA_CASES` (T* elegíveis, bloqueadas, fila concluída sem review, bloqueio aberto, bloqueios fechados, Approve aguardando confirmação, phase finalizada, duas rodadas usadas, review ilegível) alimentam o motor Python e a classe de paridade PowerShell, que também comprovam que nada é escrito no disco.

## 8. Limites

- Sem teste verde executável, não marca `[x]`.
- Não cria `todo.md`, `tasks.md` ou uma segunda trilha.
- Não interpreta a prosa do plan para montar a fila, nem a prosa do review para derivar a etapa: só as marcas descritas na seção 3.
- Não cria `implement.md` nem depende dele para selecionar uma execução; arquivos históricos permanecem intactos.
- Agentes delegados não escrevem `plan.md`, `spec.md` ou `AGENTS.md`, não operam o índice Git e não criam commits. A única exceção é o revisor, que grava o `review.md`.
- Sem confirmação humana explícita, o Modo A não aprova a review, não sincroniza decisões vigentes, não faz commit residual nem push.
- O Modo A não executa checkpoints de review declarados no plan e não paraleliza; a review final cobre a integração e o paralelismo fica para uma phase seguinte.
- Não publica decisões vigentes em `REGRAS.md`.
- Código e artefatos vivos da task entram no commit path-scoped; o JSON do inventário é transitório no stdout. Cada task verde gera commit sem push; o push só ocorre no fechamento aprovado da phase, depois da confirmação humana, pela `vibe-review` ou pelo coordenador do Modo A.
