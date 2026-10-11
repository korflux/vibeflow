---
name: vibe-implement
description: >
  Implementa e prova mudanças de software; no Modo A coordena a fase por resultados delegados, registra execução em execution.json e conduz review e fechamento com confirmação final. Use when the user runs /vibe-implement, pede código, build, correção de bug, alteração de UI em código ou execução de T* de software, mesmo que não diga vibe-implement. Não se aplica a redação ou edição apenas de texto e documentos.
---

# vibe-implement

Sem integração verde e commit real, não conclua T*. Push e decisões vigentes exigem review independente e confirmação humana. Preserve o protocolo existente. No novo Modo A, plan define trabalho, execution.json registra execução, review guarda achados e Git guarda histórico.

## 0. Classificar e usar o script

1. Texto/documento avulso segue edição direta. Express atende código localizado sem comportamento novo, como cor ou espaçamento: patch e prova proporcionais, sem exigir init/phase/artefatos ausentes. Na fase existente, reutilize task/R* e design aplicáveis. Alterar comportamento, rota, interação, aceite, acessibilidade, privacidade, obrigação jurídica, auth, pagamento, segredo, persistência ou perda de dados segue a cadeia correspondente.
2. Fora do Express, sem `.vibeflow/`, encaminhe para `/vibe-init`. Instalação legada com `.vibeflow/REGRAS.md`, `REGRAS.md` ou `CLAUDE.md` exige migração pelo init antes de retomar; preserve fontes divergentes. Leia o motor: `scripts/implement.ps1` no Windows, `scripts/implement.py` no Unix, incluindo `execution.ps1|py` quando o protocolo for novo. Entenda seleção, mutações, validação e JSON antes de executar.
3. No novo A, delegue ao finalizador o inventário/registro rotineiro e receba o resumo; no B/avulso, execute diretamente. Use no cwd do repo `pwsh "<skill>/scripts/implement.ps1"` ou `bash "<skill>/scripts/implement.sh"`; acrescente `-Dir|--dir` para alvo explícito ou `-Mvp|--mvp` para MVP. Leia `alvo`, `fila`, `etapa`, `rodadas_correcao`, `avisos` e `execucao`. Resumo não contém snapshots; detalhes são consultados pelo responsável técnico quando necessários.
4. Não contorne `INIT_AUSENTE`, `IMPLEMENT_SEM_ALVO`, `IMPLEMENT_SEM_PLAN`, `IMPLEMENT_ANALYZE_*`, `MVP_INESPERADO`, `MODO_INVALIDO`, `FASE_AUSENTE`, `PHASES_INESPERADO` ou `EXECUTION_INVALIDO`. Etapa nula exige diagnóstico delegado, nunca chute.

## 1. Abrir e selecionar o protocolo

Escolha internamente rota e modo, sem recitar inventário ao humano. Modo A é padrão em high/xhigh/max com plan aprovado e subagentes. Modo B vale para T* nomeada/uma por run, low/medium ou ausência de subagentes; avulso low/medium dispensa plan. Sem subagentes, informe a limitação em uma linha. Pedido para executar tudo nessa condição executa a próxima T* em B. “Pode seguir” em B executa a próxima elegível de menor número.

Plans novos usam `# Protocolo: coordenacao-v1`. Ao iniciar A, delegue ao finalizador o registro de `# Modo: A`; em B, registre `# Modo: B` inline. Preserve protocolo existente. No A, ausência de execution.json significa pendente; inicialização explícita segue `references/execution.md`. No B, não use sidecar. Protocolo desconhecido ou modo inválido bloqueia, sem fallback. Para `etapas-v1`, plan sem marcador ou B, leia e execute `references/protocolos-historicos.md`; não aplique o piloto novo a essas runs.

Em high+ sem plan, encaminhe para vibe-plan. Max e MVP exigem analyze aprovado e limpo. Pedido direto de implement autoriza aprovar somente a linha de status de plan rascunho quando esse for o único pendente. “Ok” isolado não autoriza outra porta. Recomendar novo chat não é gate.

## 2. Coordenar por resultado (`coordenacao-v1`, A)

Leia `references/delegation.md` antes da primeira delegação. Confira ferramentas/papéis realmente disponíveis. O coordenador seleciona resultado, responsáveis, dependências, colaboração e decisões; recebe cobertura, pendências e próximo responsável. Confie na certificação do papel responsável e não repita diff, comandos, hashes ou investigação. Contradição, prova inválida ou lacuna volta ao responsável; contexto técnico adicional só entra quando necessário para decisão estratégica.

Escolha colaboração quando exploração/preparação independentes reduzirem uma incerteza ou destravarem uma entrega. Informe interlocutores, contrato compartilhado e ownership; permita comunicação técnica direta e reutilize agentes relacionados. Leitura/preparação podem ocorrer juntas. Mantenha um dono por arquivo compartilhado e um escritor do registro/índice por vez. Código paralelo exige autorização aplicável e isolamento comprovado; sem isso, execute código em sequência. Verificador e revisor não certificam código próprio.

| Etapa do motor | Encaminhamento |
|---|---|
| implementar | Implementador investiga fluxo/consumidores, entrega código e testes juntos e faz checagem local. Finalizador registra prova local fornecida, com inputs atuais, e resumo curto na task. Dependentes usam validade local; conclusão permanece aberta. |
| validar | Verificador confere diff, ownership, aceite e cobertura e executa prova integrada necessária. Reutiliza evidência suficiente válida; não cria nova execução só para formalizar etapa. Finalizador registra integração certificada. |
| corrigir_validacao | Corretor resolve falhas concretas pela causa raiz, sem R* artificial. Verificador renova somente provas afetadas, incluindo consumidores/dependências. Não conta rodada de review. |
| commitar_integracao | Finalizador registra critérios comprovados e faz staging explícito dos paths certificados, valida índice e cria `task(T1,T2,...): <resultado>`, com IDs ordenados. Registra commit real pelo motor e atualiza resumo do plan. Falha mantém finalização pendente. |
| revisar | Revisor independente executa vibe-review no alvo, grava review.md e devolve veredito/cobertura/R*/decisões. |
| corrigir | Corretor atende Critical/Required; verificador certifica correção e provas afetadas; finalizador marca somente R* comprovados e commita correção `task(Rn,...): <resultado>`; revisor faz nova review. Até duas rodadas de correção de review. |
| confirmar | Apresente resultado, commits, correções, Critical encontrados e decisões propostas; peça uma confirmação para aprovar review, publicar essas decisões e fazer push. |
| bloqueada ou nula | Delegue diagnóstico de registro/fila/inputs; escale somente impedimento real ou decisão humana. |
| concluida | Finalizador confirma estado real de Git/upstream/residuais e relata fechamento ou pendência. |

Finalizador é subfunção operacional temporária de agente genérico/default apto; não renomeie implementador, verificador ou revisor para contornar suas proibições. Entregue paths e operações autorizadas, evidências certificadas, IDs e limites. Só ele escreve execution/plan/spec e índice neste handoff; revisor tem ownership de review durante revisão. Sem agente apto, relate a limitação real e solicite rota explícita; não assuma permissão adicional.

## 3. Implementar e provar o recorte delegado

1. **Reconhecer:** trace entrada, chamadas, consumidores, padrões compartilhados e prova da jornada antes de editar. Use `rg --files` e `rg -n`, sem varredura cega. UI segue design/tokens/motion aprovados quando aplicáveis.
2. **Codar e simplificar:** reutilize responsabilidades, standard library, plataforma e dependências existentes. Código e testes acompanham a entrega; complemente somente lacunas concretas de comportamento/erro/risco. Prefira jornada completa com resultados observáveis; não crie um teste por função, campo ou T*. Documente semanticamente decisões e responsabilidades.
3. **Provar:** selecione comandos por diff, fluxo/consumidores, risco e aceite. Local direcionado libera implementação; verificador independente certifica integração, com comandos compartilhados uma vez por inputs finais. Alteração posterior renova apenas provas afetadas; lentidão não dispensa segurança, paridade ou CI necessário. Smoke acompanha entrada real alterada.
4. **Visual:** inspecione quando o aceite depender da UI renderizada ou surgir impacto visual relevante. Leia `references/chrome-devtools.md`; use navegador integrado, depois MCP chrome-devtools; Playwright somente se instalado ou solicitado. Registre rota, viewport, estado, ações e evidência. Limitação visual necessária impede certificação.
5. **Entregar:** relatório fixo da delegação, paths/inputs reais, prova e pendências. Implementador/corretor não editam artefatos vivos nem Git. Leia `references/definition-of-done.md` quando aplicável; banco/dinheiro exige `references/database-and-migrations.md`.

## 4. Falhas e retomada

Prova vermelha exige correção da causa, sem limite de tentativas pré-review; não enfraqueça, pule ou apague teste para obter verde. Mudança de asserção exige justificativa pelo aceite. Instale ferramenta necessária pelo gerenciador do projeto ou fonte oficial quando permitido. Credencial, conta, pagamento, elevação administrativa ou integração persistente são impedimentos reais. Tente motor compatível ou prova equivalente antes de escalar, preservando proteções.

Finalizador registra somente estado atual: resumo curto no plan e evidência estruturada no execution.json. Não copie --details, hashes, logs ou histórico de comandos para Markdown. Git/review guardam histórico. Na retomada, o motor valida registros e inputs; coordenador encaminha a etapa e o responsável preserva evidência inalterada. Não refaça implementação válida automaticamente.

Pergunta material vai ao humano com recomendação; siga trabalho elegível independente enquanto a decisão está pendente. Credencial/serviço/permissão realmente indisponível exige relato da tentativa, checkpoint curto de bloqueio e próximo responsável. Na segunda rodada de review sem convergência, pare e relate R* restantes.

## 5. Fechar

Sem confirmação explícita, não aprove review, publique decisões ou faça push. Com confirmação, delegue ao finalizador genérico/default a finalização do §5 da vibe-review, com texto humano e escopo exatos: aprovação, patch mínimo das decisões vigentes, checagem final necessária, commit residual autorizado e push sem force. Validação adicional pertence ao verificador. Falha mantém phase aberta. O revisor nunca executa esse fechamento.

Responda com resultado, T*s comprovadas/total, provas, commits e paths, pendências e próximo passo. No B/avulso, sem push e handoff para próxima task/review; informe ausência de contagem quando não houver plan. Não crie trabalho extra nem arquivos implement.md/todo.md/tasks.md.
