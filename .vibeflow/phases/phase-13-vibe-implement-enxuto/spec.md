# Spec: Otimização geral do vibe-implement
# Alvo: phase-13-vibe-implement-enxuto
# Status: aprovado

## Objetivo

Permitir que mudanças pequenas e claras terminem com pouco processo, enquanto mudanças com comportamento ou risco relevante continuam recebendo investigação e prova adequadas. Reduzir leitura, saída de inventário, registros duplicados e repetição de verificações para preservar contexto e facilitar retomadas após compactação.

## Cobertura da origem

| Origem | Destino na spec | Motivo se fora/N/A |
|---|---|---|
| Ajustes pequenos de copy e apresentação sem fase nova | F1, A1 | N/A |
| Correções encontradas na validação humana | F2, A2 | N/A |
| Execução geral mais concisa, com `plan.md` como registro | F3, A3 | N/A |
| Redução de leituras, inventário, provas repetidas e perda após compactação | F3, A4–A6 | Sem promessa de teto fixo de tokens |
| Fluxo seguro para alterações de risco | Contratos, Boundaries | Proteções existentes continuam proporcionais ao risco |

## Suposições e decisões

1. A escolha do Express depende de clareza, escopo e risco real, não de urgência declarada. O usuário pode preferir continuar no fluxo completo ou no chat atual; recomendações de processo e chat não são gates.
2. Express cobre mudanças localizadas e sem comportamento novo, como copy, rótulo, nome de tela e ajuste visual pequeno. Alteração de regra, rota, interação, integração ou critério de aceite sai do Express.
3. Express funciona sem `.vibeflow/`: não exige `vibe-init`, não cria phase e não cria artefato VibeFlow. Com phase ativa da mesma entrega, reutiliza os artefatos existentes, sem abrir outra phase nem criar plan ou spec só para o ajuste.
4. Ajuste da validação humana da entrega atual permanece na phase de origem. Atualiza a T* aberta quando couber; se for novo ajuste, registra uma T* curta no `plan.md` existente; achado formal de review atualiza o R* existente. Não cria phase nova.
5. Em novas execuções com plan, `plan.md` é o registro durável único por task: status, paths alterados, prova e somente decisões, desvios ou bloqueios materiais. `vibe-implement` deixa de criar ou exigir `implement.md`; arquivos históricos ficam intactos. Commit e hash seguem as regras Git do repo e não são duplicados no plan quando o próprio Git ou a resposta já os registra.
6. Inventário e leitura são dirigidos pela T* e pelo fluxo real. O stdout operacional expõe alvo, fila necessária, dependências bloqueantes e avisos relevantes, sem serializar todas as phases. Ele continua transitório e não cria arquivo.
7. Código e testes da fatia são finalizados antes da prova final. Roda-se a menor prova pertinente uma vez nesse estado; repete-se após falha ou alteração posterior que invalide a prova. Prova de entrada real é exigida quando a entrada/bootstrap foi alterada, não por ser T1. Em UI, a checagem cobre tela, estado e viewport afetados; amplia quando layout, responsividade ou interação exigirem.
8. Um checkpoint curto de retomada só é escrito no plan enquanto uma task estiver incompleta ou em handoff. Resume estado, próximo passo, paths relevantes e validade da prova. Na retomada, confere esse checkpoint e o estado atual do Git, sem repetir investigação ou prova ainda válida.
9. O review consome as provas e paths registrados no plan. A recomendação de chat separado para review e para cada task sequencial permanece consultiva; grupo paralelo aprovado continua sendo a exceção coordenada.

## Escopo e comportamento

### 1. Fluxo F1: execução Express sem phase

- Jornada: manutenção direta de uma entrega existente.
- Rota: Express, low ou medium.
- Gatilho: pedido inequívoco, localizado e sem comportamento novo.
- Pré-condição: escopo e superfície afetada identificáveis; sem alteração de privacidade, obrigação jurídica, autenticação, autorização, pagamento, persistência, segredo ou outro risco que exija fluxo ampliado.
- Superfície por passo: N/A, fluxo operacional de agente, sem interface do produto nesta entrega.
- Passos:
  1. Classificar escopo e risco pelo pedido e pelo código tocado [superfície: N/A].
  2. Se elegível, alterar diretamente o menor recorte necessário, sem init, phase, spec, plan ou relatório VibeFlow novos [superfície: N/A].
  3. Conferir o resultado no arquivo ou na tela afetada e executar somente a checagem necessária ao risco [superfície: arquivo ou tela afetada].
  4. Se o trabalho revelar comportamento novo ou risco fora do limite, interromper a trilha Express e recomendar a próxima etapa da cadeia aplicável [superfície: N/A].
- Validações: copy e apresentação não podem alterar comportamento, acessibilidade ou sentido de consentimento/obrigação; conferir o diff e a superfície afetada.
- Erros: N/A, erros da implementação seguem o tratamento existente da skill e do repo.
- Estados: elegível, concluído com prova proporcional ou encaminhado para fluxo ampliado.
- Aceite: A1.
- Reutilizar: componentes, helpers, tokens, artefatos e convenções já existentes.

### 2. Fluxo F2: correção da validação humana na phase atual

- Jornada: ajuste de uma entrega em validação ou correção de review.
- Rota: implementação dentro da phase de origem.
- Gatilho: humano identifica um defeito ou ajuste localizado na entrega atual.
- Pré-condição: a mudança pertence ao objetivo e aos critérios da phase; mudança material de objetivo segue a cadeia normal.
- Superfície por passo: N/A, fluxo operacional de agente.
- Passos:
  1. Localizar a phase e a T* ou R* relacionada [superfície: N/A].
  2. Corrigir no mesmo escopo; atualizar a task aberta ou registrar uma T* curta no `plan.md` existente. Achado formal de review atualiza o R* existente [superfície: código/tela afetada].
  3. Validar somente o efeito da correção e registrar status, paths e prova no artefato existente [superfície: código/tela afetada].
- Validações: não criar phase, plan ou spec apenas para o ajuste; mudanças que ampliem comportamento ou objetivo deixam de ser ajuste Express.
- Erros: N/A, erros da implementação seguem o tratamento existente da skill e do repo.
- Estados: ajuste aberto, corrigido e provado, ou escalado por mudança de escopo.
- Aceite: A2.
- Reutilizar: `plan.md`, `review.md`, `spec.md` e `design.md` já existentes, conforme o caso.

### 3. Fluxo F3: task planejada, registro e retomada

- Jornada: implementação sequencial, delegada ou retomada após compactação.
- Rota: `vibe-implement` sobre o plan existente.
- Gatilho: execução de T* elegível ou retomada de task incompleta.
- Pré-condição: gates atuais da rota foram satisfeitos; no MVP, analyze permanece aprovado e limpo.
- Superfície por passo: N/A, fluxo operacional de agente.
- Passos:
  1. Ler somente alvo, fila, dependências e avisos relevantes; investigar os paths e chamadas que definem a task [superfície: N/A].
  2. Implementar, integrar e finalizar alterações de código e testes antes da prova final [superfície: código afetado].
  3. Executar uma prova proporcional ao risco no estado final; após sucesso, atualizar o `plan.md` e os critérios provados [superfície: terminal e, quando aplicável, tela afetada].
  4. Em interrupção, salvar checkpoint curto apenas se a task continuar incompleta; ao retomar, conferir checkpoint, diff/estado Git e validade da prova [superfície: N/A].
  5. A review encontra no plan a prova e os paths necessários para avaliar a task, sem depender de novo `implement.md` [superfície: N/A].
- Validações: preservar segurança, privacidade e demais gates aplicáveis; mudanças posteriores em código/testes invalidam somente as provas afetadas.
- Erros: falha na prova exige causa raiz, correção e nova prova afetada; ausência de evidência necessária impede marcar a task como concluída.
- Estados: elegível, em andamento com checkpoint opcional, provada e registrada, bloqueada ou encaminhada para review.
- Aceite: A3–A6.
- Reutilizar: fila, gates, contratos de commit e provas existentes.

### Fora

- Redefinir a política de commits, push, aprovação ou dependências entre T*s, pois não são causa do custo de contexto relatado.
- Remover proteções de segurança, privacidade, jurídico, dados ou gates do MVP.
- Prometer limite absoluto de tokens por execução; a redução vem de menos duplicação e trabalho repetido.

## Checklist de entrega

### Aceite

- [x] A1: pedido Express elegível funciona sem `.vibeflow/` e sem `vibe-init`, phase ou artefato novo; mudanças fora do limite são encaminhadas ao fluxo aplicável.
- [x] A2: correção da validação humana permanece na phase atual e é registrada no plan/review existente, sem phase nova.
- [ ] A3: novas execuções planejadas registram prova e paths no `plan.md`, não criam `implement.md`, e a review usa esse registro; históricos não são reescritos.
- [ ] A4: o stdout de implement contém apenas o estado necessário à execução, sem inventário integral de phases.
- [ ] A5: a prova ocorre após edição de código/testes e é repetida apenas se falhar ou perder validade; escopo e risco determinam sua abrangência.
- [ ] A6: checkpoint opcional permite retomar task incompleta conferindo estado e validade, sem repetir trabalho ainda válido.

### Critérios de sucesso

- [x] C1: nenhuma trilha Express elegível abre fase ou exige inicialização VibeFlow.
- [ ] C2: registro da execução não duplica a evidência de task que já pertence ao plan.
- [ ] C3: review consegue localizar no plan a prova, os paths, os bloqueios e o status da T*.
- [ ] C4: saída operacional cresce com a fila necessária e os avisos, não com o histórico inteiro de phases.
- [x] C5: fluxo de alto risco mantém gates e evidência necessários mesmo após a redução de processo.

## Contratos e restrições necessárias

- Dados e invariantes: preservar o conteúdo dos plans e dos `implement.md` históricos; o formato da fila e os status de T* existentes continuam interpretáveis.
- Integrações e interfaces: o JSON transitório fornece alvo, fila elegível/bloqueada, dependências e avisos suficientes; não persiste inventário.
- Segurança e operação: Express é inelegível quando a mudança toca autenticação, autorização, pagamento, segredo, persistência, dados pessoais, consentimento, retenção, direitos ou obrigação legal. Os gates e provas aplicáveis continuam obrigatórios.
- Tecnologia imposta: N/A; usar os motores e ferramentas já existentes no repositório.

## Como provar

| Aceite | Evidência esperada |
|---|---|
| A1 | Execução em fixture/repositório sem `.vibeflow/` conclui sem init e sem criar artefatos VibeFlow; teste de limite confirma encaminhamento do escopo que deixa de ser Express. |
| A2 | Ajuste e finding de review atualizam os artefatos da phase de origem; inventário confirma que nenhuma phase foi criada. |
| A3 | Apply e conclusão de T* atualizam plan sem criar implement; review localiza a prova no plan; comparação de bytes confirma que implement históricos não mudaram. |
| A4 | Saída com muitas phases informa a fila e avisos necessários sem conter inventário completo; paridade dos motores permanece. |
| A5 | Contratos da skill e evidência de execução mostram uma prova após mudanças e reexecução apenas após falha ou invalidação, com exemplos de prova focada para texto/UI e prova ampliada para risco. |
| A6 | Retomada a partir de checkpoint confere o estado Git e reaproveita prova ainda válida, repetindo apenas a prova invalidada. |

## Boundaries

### Always

- Classificar pela mudança efetiva e pelas superfícies tocadas, não pela urgência nem apenas pelo tamanho do diff.
- Manter as garantias de segurança, privacidade, jurídico, dados, acessibilidade e proteção contra perda de dados aplicáveis.
- Preferir os artefatos vivos existentes e deixar recomendação de chat sob escolha do humano.

### Ask first

- Se uma tarefa Express revelar mudança de comportamento, requisito jurídico/privacidade, risco sensível ou intenção ainda ambígua.
- Se correção da validação humana alterar objetivo ou critérios da phase.
- Se execução paralela depender de confirmação, isolamento ou ownership ainda não aprovado.

### Never

- Criar phase ou exigir `vibe-init` para Express elegível.
- Criar um novo `implement.md` como registro de execução ou apagar/reescrever arquivos históricos.
- Repetir a suíte inteira por padrão ou dispensar prova necessária para o risco.
- Tratar checkpoint como substituto de estado Git ou de prova válida.

## Handoff

Sem UI visível no produto: `vibe-plan`.

- Chat: recomende novo chat para `vibe-plan`; se o humano preferir, continuar neste chat não bloqueia. O `interview.md` e esta spec são a ponte.
- [x] Aprovação humana (leu o arquivo e confirmou)
