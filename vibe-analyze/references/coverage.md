# Taxonomia e passes (mapa interno)

Abrir **só** na varredura da `vibe-analyze`. Não copiar esta tabela para o chat nem para o `analyze.md`.

## 1. Cruzamento (obrigatório)

| De | Para | O que procurar |
|---|---|---|
| Interview Resultado, jornadas, páginas e módulos aplicáveis | Spec Cobertura da origem, F*, Objetivo, A*/C*, Fora | Item sem destino ou N/A fundamentado; spec que muda o pedido; Fora da interview que a spec/plan entregam |
| Spec A*/C* | Plan T* campo `Spec:` | A*/C* órfão; T* sem A*/C* (só ok se for infra justificada no Overview) |
| Spec Fora | Plan T* / Escopo | Task que implementa o recusado |
| Plan T* (o quê, arquivos) | Spec Escopo / Contratos e restrições necessárias | Comportamento ou módulo fora do escopo; path interno não precisa constar na spec |
| Os três | `AGENTS.md` | Choque com Never, Git, semver, política do repo |
| Interview Decisões críticas | Spec Decisões críticas | Mesmo ID e opção, ou ação `substitui` explícita com motivo |
| Spec Decisões críticas | Plan T* campo `Decisões:` | ID criado/substituído com task responsável; nenhuma task implementa opção divergente |

Interview ausente: pule a primeira linha. Não invente Resultado.

## 2. Passes (spec-kit analyze, traduzido)

Faça os seis. Ache **instância**, não padrão genérico.

| Pass | Categoria do F* | Sinal |
|---|---|---|
| Duplicação | `duplicacao` | A*/C*/T* que dizem a mesma entrega com redação pior |
| Ambiguidade | `ambiguidade` | Adjetivo sem métrica (rápido, seguro, intuitivo); placeholder (`TODO`, `???`, `<...>`) |
| Furo | `furo` | Verbo sem objeto; aceite não testável; T* cita arquivo que spec/plan não definem |
| Constituição | `constituicao` | Viola MUST/Never do `REGRAS.md`. Sempre `CRITICAL` |
| Cobertura | `cobertura` | A*/C* com zero T*; T* sem requisito; sucesso da interview sem C* |
| Inconsistência | `inconsistencia` | Nome diferente para a mesma coisa; entidade só num arquivo; ordem de T* que fura Deps; A* e T* se anulam |
| Decisão crítica | `decisao` | ID órfão; opção muda sem `substitui`; task implementa decisão diferente. Sempre `CRITICAL` quando altera lógica, acesso, dados, infraestrutura, segurança ou operação |
| Qualidade de Teste | `qualidade_teste` | Task sem comando executável ou só com verificação manual/passiva; ponto de entrada alterado sem smoke test; ferramenta exigida indisponível sem preparo ou bloqueio. Reutilizar o mesmo teste de capacidade em várias tasks ou critérios é válido |

## 3. Resolução de Achados e Clarificações

Erros óbvios e determinísticos (smoke ausente na task que entrega ponto de entrada executável, comandos de prova ausentes, IDs órfãos) são **corrigidos diretamente** pela IA em `spec.md` ou `plan.md`. Uma ausência local simples é tratada no preparo; não crie T* só para instalar ou conectar uma ferramenta.

Pergunte ao usuário no chat (uma por vez com recomendação e impacto) quando:
1. O achado apontar uma ambiguidade real de negócio, escopo ou arquitetura.
2. A resposta definir uma decisão que não pode ser assumida com segurança pelo contexto.
3. A dúvida não estiver respondida em interview/spec/plan.

Não há limite arbitrário de perguntas; faça as necessárias para sanar as ambiguidades reais e aplique as respostas nos artefatos correspondentes.

## 4. Gravidade e Certificação

| Nível | Quando | Ação Resolutiva |
|---|---|---|
| CRITICAL | Violação de REGRAS; divergência de decisão de MVP sem substitui; A* sem T* correspondente | Corrigir no artefato imediatamente ou alinhar com o usuário |
| HIGH | Task sem comando executável; resultado que entrega ponto de entrada sem smoke test; prova bloqueada por ferramenta sem mitigação ou limitação registrada | Corrigir o `plan.md` ou registrar o bloqueio real; não criar task de setup local artificial |
| MEDIUM | Drift de termo; inconsistência de nomes; entidade órfã | Normalizar termos no artefato afetado |
| LOW | Redundância de redação | Ajustar redação para concisão |

Veredito `limpo` é emitido quando todos os achados forem corrigidos e certificados, liberando a implementação.
