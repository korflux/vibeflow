# Spec: coordenação estratégica
# Alvo: phase-17-coordenacao-estrategica
# Status: aprovado

## Objetivo
Tornar o coordenador responsável pela estratégia, dependências e decisões humanas, delegando conferência técnica, execução de provas, registros e Git. Manter o plan legível e transferir evidências operacionais para um registro estruturado mantido pelo motor.

## Cobertura da origem
O pedido aprovado cobre delegação efetiva (F1), colaboração inteligente entre subagentes (F2), plan enxuto e retomada (F3), validação independente e fechamento autorizado (F4). Design e UI: N/A, fluxo de agentes e CLI.

## Suposições e decisões
- A autorização “aprovei, prossiga” permite definir, planejar, implementar e revisar esta mudança neste chat; aprovação final de review e push continuam pendentes.
- Novo protocolo explícito para novas fases; etapas-v1, plans sem marcador e Modo B permanecem compatíveis, sem migração implícita.
- O coordenador recebe resumos de resultado, cobertura, exceções e próximo responsável. Só investiga contradições ou decisões estratégicas; não repete a conferência técnica certificada.
- Implementador entrega código e testes juntos. Verificador assume inspeção de diff, cobertura e validação integrada; revisor permanece independente. Finalizador assume registros e Git com ownership temporário e exclusivo, sem perfil de modelo novo obrigatório.
- A colaboração é escolhida pelo benefício e dependências: exploração e preparação podem ocorrer em conjunto, com comunicação direta; escrita compartilhada mantém um dono por vez. Execução paralela de código só com autorização aplicável e isolamento comprovado; não é requisito desta entrega.

## Escopo e comportamento
### F1: delegar por resultado
Gatilho: iniciar implementação de plan aprovado no novo protocolo. Superfície: chat/CLI, UI N/A. Coordenador define resultado, aceite, dependências e ownership; implementador investiga e entrega código/testes com checagem local. Verificador confere os inputs e o aceite e devolve resultado compacto. Coordenador encaminha falhas ao corretor sem refazer a investigação. Erro ou impedimento real retorna ao responsável ou ao humano quando exige decisão. Aceite: A1.

### F2: colaboração entre agentes
Coordenador escolhe sequência ou colaboração de leitura/preparação, informa interlocutores e contrato compartilhado, reutiliza agentes relacionados e evita intermediário para cada detalhe técnico. Handoffs transferem evidência e pendências ao próximo responsável. Verificador e revisor não certificam código próprio; agentes não escrevem simultaneamente em arquivos compartilhados nem no índice Git. Aceite: A2.

### F3: registrar e retomar
Plan contém objetivo, tasks, aceite, dependências, prova planejada e resumo curto de andamento. execution.json na mesma pasta guarda estado e snapshots reais; comandos do motor calculam hashes e gravam estado validado sem executar strings de comandos recebidas. Inventário expõe resumo suficiente para roteamento; detalhes somente sob demanda. Ausência inicia estado pendente; registro inválido bloqueia, sem fallback silencioso. Alteração de input invalida somente a evidência afetada. Histórico não é reescrito. Aceites: A3, A4.

### F4: validar e finalizar
Verificador comprova integração; finalizador registra conclusões e faz commit explícito dos paths comprovados. Review independente pode exigir correção e nova prova. Aprovação humana final continua necessária para aprovar review, publicar decisões vigentes e push. Delegação não concede autorização adicional. Aceite: A5.

## Checklist de entrega
- [x] A1: coordenador estratégico, conferência técnica delegada e código/testes entregues juntos, sem passagem obrigatória redundante.
- [x] A2: colaboração com ownership, dependências, interlocução direta e independência da validação explícitos.
- [x] A3: execução nova mantém snapshots fora do plan, com registro mecânico, resumo compacto e retomada determinística.
- [x] A4: motores Python/PowerShell suportam novo protocolo com paridade, validação segura e preservação dos protocolos históricos.
- [x] A5: finalizador opera registros/Git com exclusividade e mantém gate humano de fechamento/push.
- [x] C1: testes exercitam scripts e efeitos em fixtures isoladas, incluindo falhas e compatibilidade; nenhum teste de palavras em documentação.
- [ ] C2: contrato, skills consumidoras, templates e distribuição coerentes e review independente concluída.

## Contratos e restrições necessárias
Registro operacional versionado junto da fase para retomada em outro checkout; logs extensos não entram no plan. Uma fonte por fato: plan define trabalho, execution.json guarda execução, review guarda achados e Git guarda commits. Escrita atômica e rejeição de caminhos fora da raiz, links/reparse, schema desconhecido, tipos inválidos e tarefas inexistentes. Entradas locais são não confiáveis; allowlist de operações/campos/estados e limites de tamanho definidos no contrato do motor antes da implementação. Não executar comando fornecido no registro nem armazenar segredos. Auth, banco, CORS e CSP: N/A, CLI local sem serviço web.

## Como provar
A1/A2/A5: avaliação independente de cenários de delegação e fechamento, além da inspeção do contrato. A3/A4: execução real dos motores em fixtures cobrindo registro, retomada, invalidação, corrupção, paths inseguros e histórico. C1/C2: suítes pertinentes, distribuição e revisão semântica independente.

## Fora
Migração de fases anteriores, atualização de instalações globais, automação de scheduler, múltiplos escritores concorrentes e push sem confirmação. Não criar framework genérico de orquestração.

## Handoff
vibe-plan → vibe-implement → vibe-review, autorizados pelo pedido aprovado. Rota high; sem UI. Confirmação final antes de aprovação de review e push.
- [x] Proposta aprovada pelo humano no chat, incluindo colaboração inteligente entre subagentes.
