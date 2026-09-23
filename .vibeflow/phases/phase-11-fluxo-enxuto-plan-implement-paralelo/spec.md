# Spec: fluxo enxuto de plan e implement com execução paralela
# Alvo: phase-11-fluxo-enxuto-plan-implement-paralelo
# Status: aprovado

## Objetivo

Reduzir o número e o tamanho das tasks e a repetição de testes na cadeia `vibe-plan → vibe-implement → vibe-review`, preservando prova suficiente para cada resultado. Permitir que tasks independentes avancem em paralelo e que o host delegue trabalho a subagentes quando oferecer essa capacidade, sem tornar a skill dependente de um provedor ou modelo.

## Diagnóstico do contrato atual

- `vibe-plan` exige score de cinco dimensões, `Risk`, arquivos prováveis, aceite, comando de verificação e commit por T*. Quebras automáticas por score, bullets, duração presumida e título com “e” aumentam a fila mesmo quando há um único resultado.
- O template repete a ordem em `Ordem`, `Paralelização`, `Deps` e `Tasks`; `Riscos` e `Conferência` frequentemente repetem conteúdo das T*. O plano da phase 10 tem uma T1 somente para executar suítes e Gitleaks.
- `vibe-implement` exige testar, simplificar, testar de novo e confirmar o comando novamente antes do commit. Também recomenda um chat por T* e, no modo padrão, para após cada uma. O custo cresce com a fila.
- `plan.md` já menciona paralelização, mas `implement.md` e a fila executam serialmente, sem ownership dos artefatos compartilhados.
- Scripts gravam `*-report.json` ignorados pelo Git para inventário e seleção. O relatório de implement também projeta dependências; a necessidade de persistir cada relatório deve ser reavaliada sem perder essas proteções.

## Suposições e decisões

1. Uma T* representa um resultado funcional ou contratual verificável, mesmo que toque vários arquivos ou leve mais de uma sessão. Dividir somente por resultados independentes, dependência real, risco que precise de isolamento ou impossibilidade de verificar a fatia inteira.
2. Preparação do ambiente é uma checklist curta antes da execução. Ausência de Gitleaks, navegador, MCP ou outra ferramenta gera T* apenas se exigir mudança persistente no projeto; uma instalação ou conexão local simples é resolvida no preparo, quando disponível e autorizada pelo ambiente.
3. A prova usa o menor conjunto de verificações que exercita o resultado e o risco alterado. Reutilizar testes existentes; criar ou ampliar testes apenas para comportamento novo, regressão concreta ou caso de borda material. Teste manual pode complementar a prova quando a superfície exigir observação visual.
4. Implementar e enxugar formam uma etapa antes da prova final. Reexecutar verificação após qualquer edição feita depois da prova ou após falha. Não exigir passes idênticos sem alteração.
5. Paralelismo é opcional e condicionado a independência e isolamento. O agente coordenador é o único que integra mudanças e atualiza `plan.md`, `implement.md`, `spec.md`, `review.md` e o índice Git compartilhado.
6. A skill descreve capacidades, entradas e entregas, sem fixar nomes de modelos, ferramentas de spawn ou número de agentes. O host usa delegação nativa quando disponível; sem ela, executa a mesma fila sequencialmente.
7. Checkpoint de review intermediário só aparece quando houver risco ou contrato compartilhado que precise ser julgado antes de outras T*. A review final continua cobrindo a entrega completa, sem repetir indiscriminadamente todas as suítes de cada task.

## Escopo e comportamento

### F1: Planejar uma fase compacta

- Jornada: pedido aprovado na spec até plano pronto para implementação.
- Rota: `vibe-plan`.
- Gatilho: pedido de plan com spec aprovada.
- Pré-condição: alvo e predecessores válidos.
- Superfície por passo: N/A, fluxo de agente e arquivos locais, sem UI visível.
- Passos:
  1. Localizar spec, design quando aplicável e pontos do código necessários para definir as fatias; registrar apenas lacunas que mudem a execução.
  2. Conferir rapidamente ferramentas essenciais e resolver preparo local simples; registrar bloqueio real ou T* de infraestrutura persistente quando necessário.
  3. Agrupar o trabalho por resultados verificáveis; declarar `Deps` reais e marcar quais T* podem executar juntas após conferir sobreposição de arquivos, contratos, dados e ambiente.
  4. Gravar um plano curto em que cada T* tenha objetivo, vínculo com A*/C*, aceite, prova e dependências. Incluir arquivos, risco ou checkpoint apenas quando ajudarem a executar ou revisar.
- Validações: nenhuma T* existe apenas para rodar baseline genérico; não há obrigação de uma T* por arquivo, teste ou sessão; o plano cobre A*/C* sem duplicar descrição entre seções.
- Erros: predecessor ausente ou conflito de escopo conserva os gates atuais e exige diagnóstico antes de escrever.
- Estados: rascunho, aprovado; N/A para vazio, loading e sem permissão.
- Aceite: A1, A2, A3.
- Reutilizar: seleção de alvo e parser de `Deps` existentes onde continuarem necessários.

### F2: Executar e integrar tasks

- Jornada: plano aprovado até evidência e commits das T* concluídas.
- Rota: `vibe-implement`.
- Gatilho: pedido de implementação ou continuação.
- Pré-condição: T* elegível e gates da rota satisfeitos.
- Superfície por passo: N/A, fluxo de agente e arquivos locais, sem UI visível.
- Passos:
  1. Investigar somente entrada, chamadas, dependências e testes ligados ao resultado da T*; expandir a leitura diante de lacuna concreta.
  2. Selecionar execução sequencial ou paralela segundo independência, isolamento disponível e capacidade do host; delegar uma pergunta ou resultado delimitado, com paths e prova esperada.
  3. Implementar e simplificar o código alterado antes da prova final.
  4. Integrar entregas delegadas sob um único coordenador; resolver conflitos, executar a prova proporcional e repetir verificação somente depois de nova edição ou falha.
  5. Registrar evidência, marcar critérios provados e criar commits sem misturar alterações de outras T*. Em paralelo, o coordenador serializa atualizações dos artefatos vivos e operações no índice Git.
- Validações: agentes que editam simultaneamente usam worktrees/branches isolados ou ownership de arquivos sem sobreposição; dependências não são ignoradas; falha de subagente não vira task concluída; não presumir que provedores distintos compartilhem workspace, contexto ou ferramentas.
- Erros: conflito, ferramenta indisponível ou prova falha mantém T* aberta e apresenta causa e próximo passo; gates de segurança não são contornados.
- Estados: elegível, em execução, bloqueada, concluída; N/A para estados de UI.
- Aceite: A4, A5, A6.
- Reutilizar: fila e proteção de artefato vivo do motor existente, com adaptação mínima para concorrência se necessária.

### F3: Revisar em marcos justificados

- Jornada: implementação parcial de risco relevante até review final da fase.
- Rota: `vibe-plan → vibe-review → vibe-implement` quando houver checkpoint; `vibe-review` final ao concluir a fila.
- Gatilho: marco declarado no plano ou fim da implementação.
- Pré-condição: diff e evidência disponíveis.
- Superfície por passo: N/A, fluxo de agente e arquivos locais, sem UI visível.
- Passos:
  1. O plano registra checkpoint apenas quando uma T* muda contrato compartilhado ou superfície de alto risco da qual outras dependem.
  2. A review julga o diff do marco e a prova relevante, registrando achados no mesmo artefato vivo.
  3. Após todas as T*, a review final avalia integração, aceite e riscos remanescentes com verificação proporcional.
- Validações: checkpoint não surge por contagem de T* nem executa review completa antecipada; aprovação final continua seguindo as regras de Git do projeto.
- Erros: achado bloqueante retorna ao implement sem marcar aprovação.
- Estados: checkpoint pendente ou julgado, review final pendente ou julgada; N/A para estados de UI.
- Aceite: A7.

### Fora

- Criar uma skill separada de simplificação, pois acrescentaria outra porta sem necessidade demonstrada.
- Criar um orquestrador universal que chame APIs de Codex, Claude, Grok ou ChatGPT. A skill usa capacidades disponibilizadas pelo host.
- Tornar subagentes obrigatórios, fixar modelo ou automatizar instalação de ferramentas sem necessidade real.
- Reduzir testes de segurança, autorização, dados ou outras verificações necessárias ao risco alterado.

## Checklist de entrega

### Aceite

- [x] A1: `plan.md` representa cada resultado uma vez, com T* curtas e dependências reais, sem seções que repitam a mesma informação.
- [x] A2: checklist inicial trata ferramentas locais rapidamente e só cria T* para preparo persistente ou bloqueio real.
- [x] A3: plano indica concorrência permitida e checkpoints de review apenas com justificativa objetiva.
- [x] A4: implement reconhece o fluxo relevante, entrega código já enxuto e executa a prova final sem repetição quando não houve edição.
- [x] A5: delegação disponível acelera trabalho independente, com isolamento de edição e integração pelo coordenador; a mesma fase funciona sem subagentes.
- [x] A6: execução paralela não mistura alterações, marcações, provas ou commits entre T*.
- [ ] A7: review intermediária, quando indicada, avalia o marco; review final verifica a integração sem reexecutar automaticamente toda a matriz por T*.
- [ ] A8: relatórios operacionais têm necessidade justificada ou são substituídos por saída transitória suficiente, preservando seleção, recusas e fila; não restam JSONs redundantes no workspace.

### Critérios de sucesso

- [x] C1: um exemplo de phase com duas T* independentes e uma dependente pode ser executado com e sem subagentes, produzindo o mesmo estado final e commits atribuíveis.
- [x] C2: uma T* sem edição posterior à prova roda sua verificação uma vez; nova edição exige nova prova.
- [x] C3: os testes de contrato cobrem alvo, dependências, preservação dos artefatos vivos e isolamento das atualizações compartilhadas, sem multiplicar casos que repetem a implementação.

## Implementação

### Estrutura tocada

`vibe-plan/`, `vibe-implement/`, `vibe-review/` e respectivos `docs/` de arquitetura, análise e testes; `.vibeflow/REGRAS.md` somente para regras transversais alteradas. `vibe-analyze/` apenas se o novo formato do plan exigir ajuste no cruzamento. Adaptadores por provedor somente se um contrato portátil não bastar.

### Contratos e módulos

- Preservar IDs T* e `Deps` legíveis pelo parser ou atualizar os motores Python/PowerShell e os testes em conjunto.
- Avaliar saída de inventário em stdout em vez de `*-report.json`; manter erros curtos, proteção de paths, não sobrescrita do vivo e paridade de motores.
- Alterações de template, relatório e flags públicas devem ser tratadas como mudança de contrato e versionadas conforme semver do projeto.

## Como provar

- Comparar um plano novo com o template atual: todo campo restante deve ajudar a executar, verificar ou integrar; informação duplicada é removida.
- Usar fixture de três T*: duas independentes e uma dependente, com execução sequencial e paralela isolada; conferir a mesma cobertura de aceite e ausência de conflitos nos artefatos compartilhados.
- Simular ferramenta ausente resolvível localmente e preparo persistente, confirmando que só o segundo caso vira T*.
- Executar suítes de contrato existentes de plan, implement e review e acrescentar apenas casos para mudanças reais de parser, relatório ou concorrência.

## Boundaries

### Always

- O agente coordenador responde pela integração, prova final, marcações e commits.
- A investigação parte da T* e do fluxo real, sem leitura indiscriminada do repositório.
- Gates de segurança e de perda de dados continuam proporcionais à superfície tocada.

### Ask first

- Mudança de regra de negócio, isolamento impossível entre T* que precisariam editar simultaneamente, ou escolha de ferramenta externa com efeito material no ambiente.

### Never

- Dois agentes escrevendo o mesmo artefato vivo ou operando o mesmo índice Git ao mesmo tempo.
- Declarar T* concluída só com relato de subagente, sem integração e prova do coordenador.

## Handoff

vibe-plan, após aprovação desta spec. Sem UI visível, `vibe-design` não se aplica.

- [x] Aprovação humana (pedido explícito de criar o plano)
