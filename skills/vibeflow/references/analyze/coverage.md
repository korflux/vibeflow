# Taxonomia e passes (mapa interno)

Abrir **só** na varredura da etapa analyze. Não copiar esta tabela para o chat nem para o `analyze.md`.

## 1. Cruzamento (obrigatório)

| De | Para | O que procurar |
|---|---|---|
| Interview Resultado, jornadas, páginas e módulos aplicáveis | Spec Cobertura da origem, F*, Objetivo, A*/C*, Fora | Item sem destino ou N/A fundamentado; spec que muda o pedido; Fora da interview que a spec/plan entregam |
| Spec A*/C* | Plan T* campo `Spec:` | A*/C* órfão; T* sem A*/C* (só ok se for infra justificada no Overview) |
| Spec Fora | Plan T* / Escopo | Task que implementa o recusado |
| Plan T* (o quê, arquivos) | Spec Escopo / Contratos e restrições necessárias | Comportamento ou módulo fora do escopo; path interno não precisa constar na spec |
| Design (com UI nova) | Spec F*/A* e Plan T* | Tela, estado ou prova visual sem T*; T* que contradiz o design |
| Os artefatos | `AGENTS.md` | Choque com Never, Git, semver, política do repo |
| Interview Decisões críticas | Spec Decisões críticas | Mesmo ID e opção, ou ação `substitui` explícita com motivo |
| Spec Decisões críticas | Plan T* campo `Decisões:` | ID criado/substituído com task responsável; nenhuma task implementa opção divergente |

Interview ausente: pule a primeira linha. Sem UI nova: registre N/A na linha do design. Não invente Resultado.

## 2. Passes (spec-kit analyze, traduzido)

Faça todos os passes da tabela. `contrato_implement` segue a seção 3. Ache **instância**, não padrão genérico.

| Pass | Categoria do F* | Sinal |
|---|---|---|
| Duplicação | `duplicacao` | A*/C*/T* que dizem a mesma entrega com redação pior |
| Ambiguidade | `ambiguidade` | Adjetivo sem métrica (rápido, seguro, intuitivo); placeholder (`TODO`, `???`, `<...>`) |
| Furo | `furo` | Verbo sem objeto; aceite não testável; T* cita arquivo que spec/plan não definem |
| Constituição | `constituicao` | Viola MUST/Never do `AGENTS.md`. Sempre `CRITICAL` |
| Cobertura | `cobertura` | A*/C* com zero T*; T* sem requisito; sucesso da interview sem C* |
| Inconsistência | `inconsistencia` | Nome diferente para a mesma coisa; entidade só num arquivo; ordem de T* que fura Deps; A* e T* se anulam |
| Decisão crítica | `decisao` | ID órfão; opção muda sem `substitui`; task implementa decisão diferente. Sempre `CRITICAL` quando altera lógica, acesso, dados, infraestrutura, segurança ou operação |
| Qualidade de Teste | `qualidade_teste` | Task sem comando executável ou só com verificação manual/passiva; ponto de entrada alterado sem smoke test; ferramenta exigida indisponível sem preparo ou bloqueio. Reutilizar o mesmo teste de capacidade em várias tasks ou critérios é válido |
| Contrato da implement | `contrato_implement` | Plan que o líder não consegue despachar em ondas como está (seção 3) |

## 3. Contrato da implement

Aplique a todo plan.

| Conferência | Sinal de achado | Gravidade |
|---|---|---|
| `Regressão completa` | Seção `### Regressão completa` ausente, ou com comando que o repo não tem | HIGH |
| `Regressão completa` | Mais de uma seção `### Regressão completa` | MEDIUM |
| `Prova afetada:` | Ausente, sem comando executável, ou que deixa A*/C* da T* sem prova | HIGH |
| `Prova afetada:` | Suíte inteira do repo, E2E completo ou repetição da `Regressão completa` numa T* | HIGH |
| `Arquivos:` | T* sem a linha `- **Arquivos:**` | MEDIUM |
| `Arquivos:` | Campo em mais de uma linha física, path fora de crases ou path incomparável | MEDIUM |
| Sobreposição | `Arquivos:` sobrepostos entre T* sem `Deps` entre si, quando a ordem de escrita importa | HIGH |
| Prontidão técnica | Requisito das provas sem local (local, CI ou host) ou sem destino (`ok`, `ação em Tn`, `pergunta ao humano`, `bloqueio`) | HIGH |

Formato, sobreposição e paths incomparáveis de `Arquivos:` seguem `references/plan.md`. Só a primeira linha do campo conta; confira a sobreposição pelos paths completos, porque path perdido numa segunda linha pode esconder uma sobreposição HIGH.

Prova afetada restrita ao recorte: testes do módulo ou da skill tocada e dos consumidores diretos, E2E só do cenário cuja entrada mudou, evidência visual quando houver `Visual: necessária`. Comando compartilhado definido uma vez na prontidão e referenciado pelo nome é válido. Em T* só de prosa, vale a suíte do consumidor contratual ou uma checagem mecânica; teste de presença de palavras nunca vale.

Destinos esperados na prontidão seguem a tabela da seção 3 de `references/plan.md`. Perfis de subagente não entram na prontidão: o líder os confere na run.

Sobreposição sem ordem relevante não é achado obrigatório: o líder serializa as T* na montagem das ondas. Registre MEDIUM de paralelismo perdido somente quando a perda for relevante.

## 4. Resolução de Achados e Clarificações

Erros óbvios e determinísticos (smoke ausente na task que entrega ponto de entrada executável, comandos de prova ausentes, IDs órfãos, `Arquivos:` fora do formato) são **corrigidos diretamente** pela IA em `spec.md`, `design.md` ou `plan.md`. Uma ausência local simples é tratada no preparo; não crie T* só para instalar ou conectar uma ferramenta.

Correções de `contrato_implement`:

- `Prova afetada:` com suíte inteira: troque pelo comando do recorte e deixe a suíte inteira só na `Regressão completa`. Nenhuma correção grava a suíte inteira como `Prova afetada:`.
- Sobreposição cuja ordem importa: acrescente a `Deps` real ou concentre o arquivo compartilhado numa T* final com `Deps`.
- Path incomparável: recomende renomear ou isolar a T*; renomear arquivo do projeto é decisão do humano.
- Requisito sem destino: aplique o destino quando ele decorre da regra acima; MCP, privilégio do SO ou credencial viram pergunta ao humano.

Pergunte ao usuário no chat (uma por vez com recomendação e impacto) quando:
1. O achado apontar uma ambiguidade real de negócio, escopo ou arquitetura.
2. A resposta definir uma decisão que não pode ser assumida com segurança pelo contexto.
3. A dúvida não estiver respondida em interview/spec/design/plan.

Não há limite arbitrário de perguntas; faça as necessárias para sanar as ambiguidades reais e aplique as respostas nos artefatos correspondentes.

## 5. Gravidade e Certificação

Achados `contrato_implement` usam a gravidade da seção 3. As demais categorias seguem esta tabela.

| Nível | Quando | Ação Resolutiva |
|---|---|---|
| CRITICAL | Violação do `AGENTS.md`; divergência de decisão de MVP sem substitui; A* sem T* correspondente | Corrigir no artefato imediatamente ou alinhar com o usuário |
| HIGH | Task sem comando executável; resultado que entrega ponto de entrada sem smoke test; prova bloqueada por ferramenta sem mitigação ou limitação registrada | Corrigir o `plan.md` ou registrar o bloqueio real; não criar task de setup local artificial |
| MEDIUM | Drift de termo; inconsistência de nomes; entidade órfã | Normalizar termos no artefato afetado |
| LOW | Redundância de redação | Ajustar redação para concisão |

Veredito `limpo` é emitido quando todos os achados forem corrigidos e certificados, liberando a implementação. Achado CRITICAL ou HIGH pendente, sem correção nem bloqueio real registrado, mantém o veredito `bloqueado`.
