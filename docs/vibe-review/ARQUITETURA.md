# vibe-review, arquitetura

`/vibe-review` julga o patch, a cobertura e as provas pós-código em um único `review.md`. Para cada T*, consulta status, dependências/bloqueios, paths e provas em `execution.json` no `coordenacao-v1` Modo A e no `plan.md` nos protocolos históricos; não exige um novo `implement.md`.

```text
.vibeflow/phases/phase-<n>-<slug>/review.md
.vibeflow/mvp/review.md
```

## Fonte operacional por protocolo

Em coordenacao-v1 A, a leitura do motor da implement (sem operação, com detalhes; comando em `vibe-review/SKILL.md` §1) e o execution.json determinam fila/validade/conclusão; plan define trabalho e apresenta resumo. Review confere snapshots/inputs/origem e Git reais e não depende de checkbox copiado para certificar execução. Ausência/corrupção, `prova_valida` falsa ou `commit_encontrado` nulo bloqueiam review final. Residual previsto do `execution.json` pós-registro de commit pode seguir ao fechamento aprovado sem invalidar inputs; não cria ciclo de commit para guardar hash. Etapas-v1/B/legado conservam fontes anteriores.

Finalização operacional do novo A pertence a finalizador genérico/default apto, com autorização/paths/operações explícitos. Coordenador conduz decisão humana e handoff; verificador certifica prova faltante; revisor permanece independente e sem Git. Na re-review, confira R* registrados pelo finalizador contra prova e diff. Defeito do motor encontrado pelo revisor delegado vira `estado: bloqueado` ou R*, nunca correção pelo revisor. As referências seguintes ao coordenador como operador e snapshots no plan aplicam-se somente aos protocolos históricos.

## 1. Papéis e ownership

| Peça | Responsabilidade |
|---|---|
| `SKILL.md` | Gate, auditoria, cobertura A*/C*, eixos, visual, segurança, veredito, finalização Git da phase e modo subagente revisor. |
| `scripts/review.py`, `review.ps1`, `review.sh` | Inventário, cadeia, alvo, preparação do vivo e JSON operacional no stdout. |
| `templates/review.md` | Checklist e forma de etapas no mesmo arquivo. |
| `references/ui-visual-quality.md` | Checklist renderizada quando a aceitação exige evidência visual. |
| `references/security-and-hardening.md` | Catálogo sob demanda para superfícies sensíveis. |
| `stdout (JSON)` | Evidência operacional transitória, consumida na mesma execução. |
| `review.md` | Tipo e escopo de cada etapa, auditoria do executado no Modo A, provas, histórico, veredito final e itens R* (com `papel` no Modo A). |
| `plan.md` | Status, dependências/bloqueios e paths de cada T*. Em `coordenacao-v1`, `Arquivos:`, `Prova afetada:`, a seção `Regressão completa` e o resumo de Estado; nos protocolos históricos, provas registradas sob cada T*. |
| `execution.json` | Em `coordenacao-v1` Modo A, registro operacional de provas locais (`tasks`), `integracao` com `origem`, `commit` e `correcao`, lido pela review por meio da leitura do motor da implement. |

O motor não julga o diff, não edita source, não escreve a prosa e não sincroniza `AGENTS.md`.

## 2. Alvo e cadeia

Sem `.vibeflow/`, `INIT_AUSENTE`. Com plan, o inventário seleciona a maior phase com plan sem review; uma review existente é atualizada no mesmo arquivo. O script não associa o diff à phase. Antes do apply, a IA compara o alvo sugerido com o diff e usa `--dir` para forçar a phase existente que contém o trabalho quando forem diferentes. `--slug` explicitamente fornecido seleciona sempre uma review avulsa em phase nova, mesmo com plan pendente ou rascunho. O preview informa esse novo `alvo` sem criar a phase; o apply prepara somente seu `review.md` vazio e continua reportando esse destino, preservando as phases anteriores. O número é max(n existente) + 1. Slug explícito vazio ou inválido recebe `SLUG_INVALIDO`, sem fallback automático. A combinação `--slug` e `--dir` recebe `MODO_INVALIDO` antes de qualquer mutação. Sem parâmetros explícitos, permanece a seleção automática descrita acima.

No MVP, `--mvp` exige `interview.md`, `spec.md`, `plan.md` e `analyze.md`, recusa slug/dir e usa somente `.vibeflow/mvp/`.

## 3. JSON operacional no stdout

Os motores emitem stdout e stderr em UTF-8 sem BOM, inclusive em pipes e com caminhos ou mensagens acentuadas. Consumidores devem decodificar esses streams explicitamente como UTF-8.

O JSON transitório contém `vibeflow`, `phases`, `next_n`, `existing`, `plan_pendente`, `rascunho`, `alvo`, `mvp`, `modo_sugerido`, `created`, `modo`, `actions` e `avisos`. `files` lista os artefatos vivos.

`actions` registra apenas criação de phase ou de `review.md`. O JSON do stdout não contém conteúdo do julgamento.

## 4. Apply e etapas

1. Reexecuta o inventário e valida a cadeia aplicável.
2. Prepara `review.md` vazio somente no first-pass, quando ausente.
3. Preserva bytes do arquivo vivo existente.
4. A IA escreve diretamente a primeira etapa ou acrescenta a próxima etapa no mesmo arquivo.
5. O script não substitui o histórico, não toca source e não altera `AGENTS.md`.

Status: `rascunho` durante checkpoints e enquanto o veredito final aguarda confirmação, `request-changes` com R* bloqueante aberto, `aprovado` somente após review final, fila concluída, Approve e confirmação humana. A sincronização de decisões vigentes ocorre somente depois dessa confirmação, por patch mínimo da IA.

## 5. Tipos de review e seleção de provas

A auditoria relaciona o diff ao fluxo e seus consumidores, risco e aceite antes de selecionar comandos. Re-review verifica correções e dependências afetadas, conserva o julgamento/provas das partes inalteradas e amplia somente diante de lacuna ou risco concreto. Registra referência à evidência do plan e motivo de reaproveitamento ou execução; não duplica snapshots nem exige execução para formalizar uma evidência integrada já válida. Segurança, paridade e inspeção renderizada necessárias permanecem obrigatórias, qualquer que seja sua duração.

Checkpoint existe somente em `etapas-v1`, Modo B e legado; `coordenacao-v1` A não tem checkpoint, e T* aberta nele leva ao handoff para `vibe-implement`. Nos protocolos históricos, checkpoint só é permitido quando `plan.md` declarar o marco e sua justificativa e todas as T* desse marco estiverem concluídas. A etapa julga apenas o marco, suas provas e o contrato ou risco compartilhado indicado. Registra T* ainda abertas, não declara a feature concluída, não marca Approve final e não autoriza sincronização de decisões, commit residual ou push.

Review final exige a fila concluída na fonte do protocolo e julga critérios de aceite, código integrado e riscos alterados. Para cada T*, confere status, `Deps`, bloqueios, `Arquivos` e a prova registrada (`execution.json` no Modo A, `Prova`/`Verificação` no `plan.md` nos históricos); compara os inputs cobertos com o estado integrado e reaproveita evidência verde quando esses paths continuam iguais e a prova ainda cobre a integração. Edição posterior em código/teste invalida somente a prova afetada; atualização de plan, spec ou review não invalida a prova. Nos protocolos históricos, executa apenas a verificação necessária que falta para integração ou risco e não repete automaticamente cada comando da matriz de T*. Em coordenacao-v1 A, a prova da review final é a regressão completa da subseção seguinte, sem repetir a `Prova afetada:` de cada T*. Toda prova executada ou reaproveitada fica registrada no `review.md` com seu motivo.

### Regressão completa em coordenacao-v1 A

Em coordenacao-v1 Modo A, a review é a única dona da regressão completa; implementador e verificador provam somente o afetado (`Prova afetada:` de cada T*).

| Etapa | Prova da review |
|---|---|
| Review final | Executa sempre a seção `Regressão completa` do plan, que declara a suíte inteira e o E2E do repo, uma vez, no estado integrado final. E2E que o plan exclui com motivo (por exemplo, não determinístico e fora do CI) não roda e a exclusão é registrada. Registra comando, resultado e HEAD em "Provas executadas" da etapa. Com modificação não commitada em path de código e teste, não executa e pede isolamento ao coordenador ou ao humano. Cobre as provas executáveis de segurança, paridade e CI obrigatório. |
| Re-review | Confere `correcao.commit` não nulo, igual a `commit_encontrado` (descendente do commit da integração) e com os IDs do título iguais aos R* marcados; reaproveita a prova afetada da correção certificada pelo verificador. Repete a regressão completa antes do Approve somente se path de código e teste mudou desde a última execução completa verde, pela definição desses paths e pelo critério de comparação em `vibe-review/SKILL.md` §3. A finalização Git usa a mesma comparação, na qual `AGENTS.md` não conta quando todos os hunks do seu diff caem dentro de `## Decisões vigentes`. |

- Approve exige regressão completa verde sobre o código final. Falha abre `R*` `Required` com o comando que falhou e o remédio.
- O reaproveitamento de prova verde por inputs iguais vale para as provas afetadas das T* e não substitui a regressão completa.
- Plan sem a seção (anterior ao formato que a introduziu) usa a verificação agregada do repo (CI ou comandos documentados no `AGENTS.md`) como regressão completa e registra a origem na etapa. Sem nenhuma das fontes, a necessidade volta ao coordenador e não há Approve.
- Em coordenacao-v1 A, o julgamento de código continua limitado ao diff da phase e aos consumidores afetados; a matriz de Cobertura da solicitação continua obrigatória em todos os protocolos (§6).
- Etapas-v1, Modo B e legado conservam a regra histórica: sem execução automática da suíte completa, que só entra por risco, consumidores afetados, lacuna concreta ou CI obrigatório.

## 6. Auditoria e prova visual

A review começa pela solicitação original e pelas alterações explicitamente autorizadas pelo humano, usando o contexto disponível e `interview.md` quando houver. Cruza essa origem com spec, plan, analyze e código real. O plan registra execução e não define sozinho a completude da entrega. Obrigação aplicável omitida pela spec ou pelo plan continua obrigatória até uma retirada humana explícita com fonte verificável.

### Auditoria do executado em coordenacao-v1 A

Antes de julgar o código, a review confere o que a implement executou, pelos critérios de `vibe-review/SKILL.md` §3: inputs de cada T* em `execution.json` dentro do seu `Arquivos:` (igual ou sob diretório declarado, após a normalização léxica do motor descrita em `docs/vibe-implement/ARQUITETURA.md`, seção Onda paralela); diff `integracao.origem..HEAD` fora de `.vibeflow/` dentro da união dos `Arquivos:` ou dos paths que o remédio de um R* desta review manda alterar, com R* Required para path fora, exceto arquivo novo em `.erros-encontrados/` criado pela regra de erros fora do recorte, que vai para Notas (edição ou remoção de registro existente continua contando); consumidor compartilhado coerente entre cada par de T* sem `Deps` entre si, já que o registro não guarda a onda real; e cada A*/C* coberto pela `Prova afetada:` registrada ou pela regressão completa. Achados cujo remédio altera `Arquivos:` da phase levam `papel: corretor | redator`, que a implement usa para rotear a correção; remédio em plan, spec ou `AGENTS.md` cabe ao finalizador e em `review.md` ao revisor, sem `papel`.

O `review.md` contém uma matriz obrigatória: item da solicitação e fonte (incluindo A*/C* relacionados quando existirem), implementação concreta, evidência e situação. As situações permitidas são `atendido`, `parcial`, `ausente` e `retirado explicitamente pelo humano`. Retirada exige referência à decisão e ao item retirado; inferência do agente, ausência no plan e cronologia não autorizam retirada. Item obrigatório parcial ou ausente abre R* Required ou Critical conforme impacto e bloqueia Approve. Falta da origem ou de contexto essencial é limitação declarada da cobertura: solicita-se o contexto pelo coordenador e não se certifica completude. Checkpoint limita o julgamento ao marco e nunca certifica toda a solicitação.

A rastreabilidade usa o Git real, paths e provas contra o estado integrado. Aceita commits integrados de várias T*, commits por task e histórico legados; o prefixo `task(Tn)` não é condição exclusiva de evidência. No protocolo etapas-v1, confere origem preservada, snapshot da integração, hashes dos inputs e commit registrado na história, distinguindo checagem local de prova integrada. Um checkbox, frase verde ou assunto de commit isolado não comprova implementação. Lê o status, as dependências/bloqueios, os paths e as provas de cada T* na fonte do protocolo (`execution.json` no Modo A, `plan.md` nos históricos), sem exigir `implement.md`. Confere as evidências contra o estado atual e segue a seleção proporcional da seção anterior para executar apenas as verificações que faltam; também verifica falsos positivos, segurança, funções alteradas, dados e migrations quando aplicável.

Aplica os pilares de auditoria ao diff e às superfícies relevantes para o marco ou para a integração final. Usa `Visual` no plan para decidir se o aceite precisa de evidência renderizada; tocar arquivo de UI, HTML ou DOM, sozinho, não aciona navegador. Reaproveita prova de implementação válida e só executa a inspeção se ela estiver ausente/desatualizada ou não cobrir a integração. Quando necessária, seleciona navegador integrado, MCP Server `chrome-devtools` e Playwright somente se já existir ou for solicitado. Começa pela rota/tela, estado e viewport afetados; amplia conforme o impacto em layout, responsividade, interação, componente compartilhado ou risco. Com `design.md`, diff que altera componente ou token listado em `Superfícies compartilhadas` reconfere todas as telas listadas ali, inclusive fora do inventário da phase. Faltando capacidade, aplica a regra de instalação da skill: instala a ferramenta necessária fora do projeto, sem alterar manifesto nem lockfile, e registra na etapa; credencial, conta, pagamento, elevação administrativa e registro persistente de integração (por exemplo, um MCP) vão ao humano. Sem capacidade visual depois disso, para uma prova necessária, abre `R* Required` e não aprova silenciosamente.

`icon-only` só é aceito para ação universalmente reconhecível, como lixeira para apagar, com nome acessível, foco visível, área de interação e tooltip quando aplicável. Ações ambíguas permanecem textuais.

A review audita código, cobertura e validade das provas locais/integradas já certificadas e executa somente lacunas ou provas invalidadas. Implementador verifica fluxo/consumidores alterados; verificador certifica integração proporcional. Nos protocolos históricos, integração não implica suíte completa; ampliação exige risco, consumidores afetados, lacuna concreta ou CI obrigatório e motivo registrado. Em coordenacao-v1 A, a suíte completa é a regressão completa da review final (§5). Mudança ou falha renova somente provas afetadas; troca de etapa ou papel não exige repetição.

Simplificação, reutilização e remoção de redundância permanecem no recorte. Otimização de desempenho fundamentada preserva comportamento, segurança e cobertura, sem abstração especulativa ou limpeza externa.

Toda correção pertinente usa R*, inclusive nit, e bloqueia Approve enquanto aberta. Severidade informa impacto e prioridade, sem dispensar remédio/prova. Optional/FYI históricos com R* continuam sendo correções; notas informativas novas não usam R*. Preferência pessoal sem fundamento não é achado. Novas reviews oferecem somente Approve ou Request changes; defer legado e status aprovado não liberam R* pendente na retomada. Preserve histórico e IDs. Obrigação aplicável parcial/ausente e origem insuficiente também bloqueiam aprovação. A confirmação humana final continua necessária.

## 7. Chat, testes e handoff

Recomende iniciar review em novo chat, separado da implementação, especialmente em re-review ou Request changes. Se o humano preferir continuar no mesmo chat, prossiga sem bloquear; o `review.md`, o diff e o plan são a ponte.

Suítes: `docs/vibe-review/tests/test-review.py` e `docs/vibe-review/tests/test-review.sh`. Elas cobrem seleção, override explícito por `--dir`, apply, phase/MVP, atualização e paridade.

Handoff: `vibe-implement` com R* bloqueante, retorno à spec quando a intenção quebrou, ou finalização Git da phase após aprovação humana.

### Modo subagente (revisor delegado)

No Modo A do `vibe-implement`, o coordenador delega a review final a um subagente de contexto limpo. O revisor executa o fluxo normal e grava a etapa no `review.md`, o único artefato vivo que escreve. Marca a proposta no Veredito vigente, mas o status só vira `aprovado` depois da confirmação humana. Não pergunta ao humano: devolve `estado: pergunta` com a recomendação, e o coordenador pergunta. Não executa a finalização Git, não faz commit nem push e não edita `AGENTS.md`; a finalização segue o responsável operacional do protocolo, depois da confirmação.

O relatório segue o formato fixo de `references/delegation.md` do implement e acrescenta `veredito`, `abertos`, `fechados`, `critical_encontrados` e `decisoes_vigencia`. A matriz de cobertura, R*, etapas e a tabela de decisões são o registro. O relatório também indica a cobertura da solicitação e limitações de origem, sem duplicar a matriz; perguntas ficam no relatório ao coordenador, nunca no arquivo. Na re-review após correção, o revisor confere os R* que o responsável de registro do protocolo (finalizador no Modo A, coordenador nos históricos) marcou `[x]` contra o diff e a prova. Defeito do motor achado no §0 não é corrigido pelo revisor: vira `estado: bloqueado` ou R*.

## 8. Limites

- Um alvo possui um `review.md`; cada nova execução acrescenta `### Etapa N`.
- Checkpoint existe só nos protocolos históricos e depende de marco explícito no plan; somente a review final pode concluir fase e abrir a finalização Git.
- Review não edita source, testes, lockfile ou artefatos anteriores. O revisor delegado também não toca Git, `AGENTS.md` nem a aprovação humana.
- O motor não interpreta Status, veredito ou diff.
- O arquivo vivo entra no Git; o JSON operacional é transitório no stdout. Review não corrige source. Após Approve final confirmado, fila concluída e sem R* bloqueante, a review confirma a prova necessária da integração (em coordenacao-v1 A, a regressão completa verde já registrada, pela mesma comparação da re-review), cria o commit residual quando houver e executa `git push` do upstream atual sem force.
