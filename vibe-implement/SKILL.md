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

Leia `references/delegation.md` antes da primeira delegação. Confira ferramentas/papéis realmente disponíveis. O coordenador do Modo A é o líder estratégico: reconhece o terreno, planeja as ondas, seleciona resultado, responsáveis, dependências, colaboração e decisões, e delega toda execução (código, testes, provas, registros e Git). Recebe cobertura, pendências e próximo responsável e valida a consistência desses dados (relatórios fixos, saída do motor, `git status`), sem executar o trabalho dos papéis. Faz diretamente, no máximo, pequenos ajustes finais, como um typo ou uma linha de fechamento, sem invadir ownership alheio. Confie na certificação do papel responsável e não repita diff, comandos, hashes ou investigação. Contradição, prova inválida ou lacuna volta ao responsável; contexto técnico adicional só entra quando necessário para decisão estratégica.

Escolha colaboração quando exploração/preparação independentes reduzirem uma incerteza ou destravarem uma entrega. Informe interlocutores, contrato compartilhado e ownership; permita comunicação técnica direta e reutilize agentes relacionados. Leitura/preparação podem ocorrer juntas. Mantenha um dono por arquivo compartilhado e um escritor do registro/índice por vez. Código paralelo só ocorre em onda: o pedido de `/vibe-implement` com plan aprovado autoriza, e o isolamento são os `Arquivos:` disjuntos calculados pelo motor. Fora de `fila.onda`, execute código em sequência. Verificador e revisor não certificam código próprio.

Na etapa `implementar`, conduza a fila por ondas. Leia `fila.onda` (T* elegíveis de `Arquivos:` disjuntos, em ordem numérica) e `fila.sem_arquivos` no resumo do motor; não reconstrua a disjunção.

| Passo da onda | Regra |
|---|---|
| Despachar | Delegue todas as T* de `fila.onda` numa única rodada, em chamadas paralelas. Cada responsável recebe ownership exclusivo dos `Arquivos:` da sua T*. |
| Serializar | T* de `fila.sem_arquivos` roda sozinha, nunca em paralelo. T* que precise de path fora dos seus `Arquivos:` (reportado antes de editar, §3.1) volta ao coordenador, que a serializa; as demais seguem. |
| Preparar | Enquanto a onda implementa, o explorador prepara em leitura o contexto das T* que a onda libera. |
| Verificar | Cada T* que volta verde vai ao verificador com sua `Prova afetada:`, sem esperar a onda. Falha vai ao corretor, sem bloquear as demais. |
| Registrar | Com todas as T* da onda verificadas, o finalizador registra num único handoff as provas locais delas, uma operação `local` por T* (`references/execution.md`). |
| Avançar | O coordenador consulta o motor uma vez e despacha a próxima onda. Sem T* pendente, segue a etapa `validar`. |

| Etapa do motor | Encaminhamento |
|---|---|
| implementar | Onda, conforme a tabela acima. Implementador investiga fluxo/consumidores, entrega código e testes juntos e executa a `Prova afetada:`. T* cujo resultado principal é prosa (SKILL, referências, docs, artefatos vivos) vai ao redator, que investiga o fluxo e os consumidores do texto, escreve a prosa e executa a `Prova afetada:`, sem código de motor nem testes; T* mista divide os `Arquivos:` entre os dois ou fica com o implementador. Finalizador registra as provas locais fornecidas, com inputs atuais, e resumo curto nas tasks. Dependentes usam validade local; conclusão permanece aberta. |
| validar | Verificador confere diff, ownership, aceite e cobertura e executa a união das `Prova afetada:` das T* da phase no estado integrado, sem ampliar para suíte completa. Reutiliza prova verde de inputs inalterados; não cria nova execução só para formalizar etapa. Finalizador registra integração certificada. |
| corrigir_validacao | Corretor resolve falhas concretas pela causa raiz, sem R* artificial. Verificador renova somente a prova afetada, incluindo consumidores/dependências. Não conta rodada de review. |
| commitar_integracao | Finalizador registra critérios comprovados e faz staging explícito dos paths certificados, valida índice e cria `task(T1,T2,...): <resultado>`, com IDs ordenados. Registra commit real pelo motor e atualiza resumo do plan. Falha mantém finalização pendente. |
| revisar | Revisor independente executa vibe-review no alvo, incluindo a `Regressão completa` do plan, grava review.md e devolve veredito/cobertura/R*/decisões. |
| corrigir | Corretor atende todos os R* abertos; verificador certifica correção e provas afetadas; finalizador marca somente R* comprovados e commita correção `task(Rn,...): <resultado>`; revisor faz nova review. Até duas rodadas de correção de review. |
| confirmar | Apresente resultado, commits, correções, Critical encontrados e decisões propostas; peça uma confirmação para aprovar review, publicar essas decisões e fazer push. |
| bloqueada ou nula | Delegue diagnóstico de registro/fila/inputs; escale somente impedimento real ou decisão humana. |
| concluida | Finalizador confirma estado real de Git/upstream/residuais e relata fechamento ou pendência. |

Finalizador é subfunção operacional temporária de agente genérico/default apto; não renomeie implementador, verificador ou revisor para contornar suas proibições. Entregue paths e operações autorizadas, evidências certificadas, IDs e limites. Só ele escreve execution/plan/spec e índice neste handoff; revisor tem ownership de review durante revisão. Sem agente apto, relate a limitação real e solicite rota explícita; não assuma permissão adicional.

## 3. Implementar e provar o recorte delegado

1. **Reconhecer:** trace entrada, chamadas, consumidores, padrões compartilhados e prova da jornada antes de editar. Use `rg --files` e `rg -n`, sem varredura cega. Edite somente os `Arquivos:` da T*; path fora do recorte é reportado ao coordenador antes de editar. UI segue design/tokens/motion aprovados quando aplicáveis.
2. **Codar e simplificar:** reutilize responsabilidades, standard library, plataforma e dependências existentes. Código e testes acompanham a entrega; complemente somente lacunas concretas de comportamento/erro/risco. Remova duplicação e redundância no recorte; otimize desempenho quando houver necessidade demonstrável, preservando comportamento, segurança e cobertura, sem limpeza externa ou abstração especulativa. Prefira jornada completa com resultados observáveis; não crie um teste por função, campo ou T*. Documente semanticamente decisões e responsabilidades.
3. **Provar em dois níveis:** em `coordenacao-v1` Modo A, a prova afetada é a `Prova afetada:` da T*. Sem ela declarada (Express ou plan anterior), derive o recorte: testes do módulo tocado e dos consumidores diretos; E2E somente do cenário da jornada cuja entrada mudou, incluindo o smoke da entrada real alterada. `etapas-v1`, B e legado seguem a prova de `references/protocolos-historicos.md`.

   | Nível | Responsável | Executa |
   |---|---|---|
   | Afetado | Implementador, redator e corretor (liberam a T*); verificador independente, no estado integrado da T* | Somente a `Prova afetada:` da T*; registre comando e resultado no relatório |
   | Integração | Verificador, depois da última T* | A união das `Prova afetada:` das T* da phase, cada comando uma vez por inputs finais; reaproveita prova verde de inputs inalterados |
   | Regressão completa | Revisor, na review final | Suíte inteira e E2E completo do plan; exclusiva da review |

   Em `coordenacao-v1` Modo A, nenhum papel de implementação ou verificação amplia a prova para a suíte completa, por risco, consumidor, lacuna ou CI; essa cobertura pertence à `Regressão completa`. Nenhuma etapa repete prova só por trocar de papel. Alteração posterior em código ou teste renova somente a prova afetada. Prova vermelha segue o §4.
4. **Visual:** inspecione quando o aceite depender da UI renderizada ou surgir impacto visual relevante. Leia `references/chrome-devtools.md`; use navegador integrado, depois MCP chrome-devtools; Playwright somente se instalado ou solicitado. Registre rota, viewport, estado, ações e evidência. Limitação visual necessária impede certificação.
5. **Entregar:** relatório fixo da delegação, paths/inputs reais, prova (comando e resultado) e pendências. Implementador/corretor não editam artefatos vivos nem Git. Leia `references/definition-of-done.md` quando aplicável; banco/dinheiro exige `references/database-and-migrations.md`.

## 4. Falhas e retomada

Prova vermelha exige correção da causa, sem limite de tentativas pré-review; não enfraqueça, pule ou apague teste para obter verde. Mudança de asserção exige justificativa pelo aceite. Instale ferramenta necessária pelo gerenciador do projeto ou fonte oficial quando permitido. Credencial, conta, pagamento, elevação administrativa ou integração persistente são impedimentos reais. Tente motor compatível ou prova equivalente antes de escalar, preservando proteções.

Finalizador registra somente estado atual: resumo curto no plan e evidência estruturada no execution.json. Não copie --details, hashes, logs ou histórico de comandos para Markdown. Git/review guardam histórico. Na retomada, o motor valida registros e inputs; coordenador encaminha a etapa e o responsável preserva evidência inalterada. Não refaça implementação válida automaticamente.

Pergunta material vai ao humano com recomendação; siga trabalho elegível independente enquanto a decisão está pendente. Credencial/serviço/permissão realmente indisponível exige relato da tentativa, checkpoint curto de bloqueio e próximo responsável. Na segunda rodada de review sem convergência, pare e relate R* restantes.

## 5. Fechar

Sem confirmação explícita, não aprove review, publique decisões ou faça push. Com confirmação, delegue ao finalizador genérico/default a finalização do §5 da vibe-review, com texto humano e escopo exatos: aprovação, patch mínimo das decisões vigentes, checagem final necessária, commit residual autorizado e push sem force. Validação adicional pertence ao verificador. Falha mantém phase aberta. O revisor nunca executa esse fechamento.

Responda com resultado, T*s comprovadas/total, provas, commits e paths, pendências e próximo passo. No B/avulso, sem push e handoff para próxima task/review; informe ausência de contagem quando não houver plan. Não crie trabalho extra nem arquivos implement.md/todo.md/tasks.md.
