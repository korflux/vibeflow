# Plan: Provas proporcionais e correções obrigatórias
# Alvo: phase-18-provas-e-correcoes-obrigatorias
# Status: aprovado
# Spec: spec.md (mesma pasta)
# Protocolo: coordenacao-v1
# Modo: A

## Overview

Entregar o contrato aprovado na spec: toda correção pertinente bloqueia aprovação, enquanto provas locais, integração e review têm responsabilidades explícitas e reaproveitam evidência suficiente válida. Preservar simplificação e otimização fundamentada. Atualizar instalações do VibeFlow somente no fechamento posterior à aprovação humana e ao push.

- **Rota:** high, sem analyze obrigatório.
- **Design:** N/A, sem UI visível.
- **Modo:** coordenador escolhe na abertura; finalizador registra o marcador contratual. Recomenda-se A, disponível neste host.
- **Versão:** mudança incompatível de comportamento público, portanto major: manifests atuais 6.0.1 passam a 7.0.0. Preservar schema mínimo do Antigravity sem acrescentar versão onde não existe.

## Prontidão das provas

Disponíveis localmente: Python 3.13.14, PowerShell 7.6.6, Git, gitleaks 8.30.1 e npx. Não há serviço, banco ou browser necessário. O CI existente em `.github/workflows/contrato.yml` fornece Python, PowerShell, bash e varredura de segredos. Não alterar sua cobertura para reduzir a prova desta entrega.

### Checagens locais

- T1: `python docs/vibe-implement/tests/test-implement.py PythonContracts.test_etapa_e_rodadas_por_fixture PowershellParity.test_etapa_parity_por_fixture -v`, ampliando as fixtures existentes de classificação/estado. Para a jornada de correção registrada: `python docs/vibe-implement/tests/test-execution.py ExecutionContracts.test_review_correction_commit_preserves_original_and_returns_to_review PowerShellExecutionContracts.test_review_correction_commit_preserves_original_and_returns_to_review -v`. Se a implementação acrescentar cenário independente, incluir sua seleção específica na prova local.
- T2: `git diff --check`, junto da conferência semântica das responsabilidades, critérios de ampliação e otimização. Não criar teste que procure palavras em SKILL.md, templates ou documentação. O aceite de instruções operacionais exige leitura semântica; os comportamentos determinísticos são comprovados pelas execuções de T1 e integração.

### Prova integrada compartilhada

O verificador certifica os inputs finais, aproveitando provas locais quando suficientes; roda cada comando necessário uma vez, sem repetir por T*:

1. `python docs/vibe-implement/tests/test-implement.py -v`: suíte do motor afetado, incluindo execução estruturada importada e paridade PowerShell. Necessária porque parser e precedência participam de fila, retomada, rodadas, protocolos históricos e commit de correção.
2. `python docs/tests/test-distribuicao.py -v`: manifests, versão e descoberta dos pacotes alterados.
3. `git diff --check` e `gitleaks detect --source . --verbose --redact --no-banner`: integridade do patch e verificação de segredos antes da entrega/push. Conferir também o conteúdo ainda não commitado pelo modo de diretório suportado pelo gitleaks instalado antes do commit, sem expor valores encontrados.

Não executar suíte geral do repositório localmente por padrão. O motor review apenas prepara o artefato e não decide severidade; sua suíte só entra se esse motor ou dependências executáveis forem alterados. CI completo permanece após publicação. Review reaproveita provas integradas válidas e executa somente lacunas concretas. Mudança de prosa operacional exige nova inspeção semântica, mas não invalida testes de código que não a consomem.

## Tasks

### T1: Exigir resolução de toda correção na aprovação e na retomada
- [x] T1 concluída
- **Execução:** implementação e provas locais direcionadas verdes; integração independente certificada e commit integrado registrado. Review pendente.
- **Spec:** A2, C1, C2
- **Deps:** nenhuma
- **O quê:** alinhar parser, fila, registro de correções, prompt de review e distribuição à obrigatoriedade de todos os R* pertinentes. Remover aprovação com defer como saída oferecida para novas reviews e tratar entradas legadas sem liberar pendências. Publicar a mudança de contrato como 7.0.0.
- **Arquivos:** `vibe-implement/scripts/implement.py`, `implement.ps1`, `execution.py`, `execution.ps1`; `docs/vibe-implement/tests/test-implement.py`, `test-execution.py`; `vibe-review/SKILL.md`, `templates/review.md`, `references/security-and-hardening.md`; trechos de correção/delegação em `vibe-implement/SKILL.md` e referências aplicáveis; `docs/vibe-implement/ARQUITETURA.md`, `ANALISE.md`, equivalentes da review; manifests `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `.grok-plugin/marketplace.json`, `.agents/plugins/marketplace.json` conforme campos existentes; `docs/tests/test-distribuicao.py` e `README.md`.
- **Aceite:** R* aberto bloqueia aprovação por sua condição de correção, sem depender de severidade. Critical, Required, Nit, Optional e FYI legados entram na fila e nos IDs reconhecidos pelo registro/commit de correção. Fechados não bloqueiam. Aprovação marcada, inclusive defer legado, não prevalece sobre pendência. Relatório delegado inclui todas as correções abertas. Rodadas e retorno à review continuam coerentes. FYI novo informativo fica em notas, sem R*. Fases encerradas não são reescritas nem migradas; status legado deve ser distinguido de retomada com pendência contraditória, sem contornar o bloqueio.
- **Implementação orientada:** investigar `read_review`, `derive_etapa`, `execution_etapa` e `coordinate`, seus equivalentes PowerShell e `correction_matches`. Reutilizar a identificação de R* sempre que possível em vez de manter listas divergentes por severidade. A precedência atual de status aprovado e a extração separada de IDs exigem conferência conjunta. Preservar schema operacional e gates de snapshots, origem e Git real.
- **Verificação:** seleções locais de T1 e prova integrada compartilhada. Expandir fixtures/jornada para achados abertos e fechados, combinação de severidades, aprovação indevida e ciclos de correção nos protocolos coordenacao-v1, etapas-v1, B/legado e seleção MVP aplicável. Exercitar motores e arquivos temporários; preservar limpeza obrigatória. Sem matriz repetida por classificação quando subcasos no mesmo fluxo forem suficientes.
- **Risco:** corrigir só o prompt deixa o motor liberando pendências; corrigir só a fila pode impedir reconhecimento de commits de Nit. Compatibilidade de leitura não autoriza manter a dispensa antiga.

### T2: Delimitar provas por papel e preservar otimizações
- [x] T2 concluída
- **Execução:** contratos de prova e otimização alinhados; integração e inspeção semântica independentes certificadas, com commit integrado registrado. Review pendente.
- **Spec:** A1, A3, C2
- **Deps:** nenhuma
- **O quê:** explicitar que implementador entrega código/testes e prova localizada; verificador certifica integração proporcional; revisor audita código/cobertura/evidência e executa somente lacunas. Manter simplificação e otimização fundamentada no recorte autorizado.
- **Arquivos:** `vibe-implement/SKILL.md`, `references/definition-of-done.md`, `references/delegation.md`, `references/protocolos-historicos.md`; `vibe-review/SKILL.md` e referências de prova quando necessário; `docs/vibe-implement/ARQUITETURA.md`, `ANALISE.md`, equivalentes da review; `vibe-plan/SKILL.md` somente se necessário para eliminar orientação conflitante; cópia `vibe-plan/references/delegation.md` sincronizada se o contrato compartilhado mudar. `README.md` somente no resumo do fluxo afetado.
- **Aceite:** nenhum papel recebe ordem de executar suíte completa por padrão. Ampliação exige risco, consumidores afetados, lacuna ou CI obrigatório; integração continua necessária. Reuso depende de cobertura e inputs válidos. Falha ou edição renova apenas prova afetada. Simplificação, reutilização, remoção de redundância e otimização de desempenho fundamentada continuam explícitas, preservando controles, cobertura e escopo.
- **Verificação:** checagem local de T2 e inspeção semântica pelo verificador/revisor, combinadas com prova integrada compartilhada de T1. Usar os próprios registros desta execução para demonstrar seleção proporcional; não construir piloto artificial nem testes de palavras para comprovar prosa.
- **Risco:** converter redução de repetição em dispensa de integração ou em proibição de suíte completa necessária; limitar otimização por omissão na versão resumida do manual.

## Colaboração

- Investigação/preparação pode separar o fluxo parser → fila → commit de correção (T1) da coerência entre papéis/provas/otimização (T2). Benefício: localizar consumidores e contradições antes da escrita, compartilhando conclusões diretamente.
- T1 e T2 são resultados independentes, mas compartilham documentos: executar escrita sequencial, com um implementador dono do recorte por vez. Não há grupo de escrita paralela seguro definido neste plan.
- Implementador entrega código/testes e provas locais. Verificador independente certifica integração, sem corrigir arquivos. Revisor de contexto limpo julga a entrega e todas as correções. Finalizador genérico/default apto recebe ownership exclusivo temporário de registros e Git.
- Coordenador escolhe interlocutores e resultados, recebe certificações e intervém por contradição. No A, `execution.json` é o registro operacional; plan mantém somente resumo curto derivado, sem hashes, logs ou snapshots.

## Fechamento e atualização das instalações

Esta seção cobre A4/C3 após a review; não é T* prévia à aprovação, pois isso criaria dependência circular. A review verifica o código e registra expressamente a obrigação operacional pós-publicação ainda pendente, sem declarar A4 atendido antecipadamente. A entrega total só termina após conferir as instalações ou relatar impedimentos reais.

1. Após integração verde e commit real, review independente e eventuais correções, apresentar uma confirmação humana final com escopo de push e atualização local. Sem correções abertas para qualquer severidade.
2. Finalizador executa residual autorizado e push sem force. Falha de push bloqueia atualização local.
3. Conferir revisão remota e resultado do CI completo existente. Se o CI falhar, diagnosticar e corrigir o necessário antes de distribuir a versão como validada, reutilizando provas não afetadas.
4. Inventariar instalações efetivas do VibeFlow e sua origem, não apenas executáveis no PATH. Conferir Codex, Claude Code, Grok, Antigravity IDE/CLI, OpenCode, Pi e diretório compartilhado `~/.agents/skills`, incluindo cópias alternativas existentes. Não instalar hosts ausentes.
5. Preferir mecanismo já usado em cada destino: plugin/marketplace ou skills globais. O README documenta `npx skills add korflux/vibeflow -g -a grok -a claude-code -a codex -a antigravity -y`, com `--copy` onde necessário; esse comando não substitui o inventário de plugins/cópias compartilhadas. Conferir opções na ferramenta instalada antes de executar. Atualizar a revisão efetivamente publicada, não uma árvore local divergente.
6. Antes de sobrescrever cópia personalizada, comparar conteúdo e preservar customizações/backup verificado; conflito material vai ao humano. Escrita fora do workspace exige o mecanismo de permissão do ambiente. Não alterar regras globais, credenciais ou binários dos hosts.
7. Conferir versão/conteúdo por destino e descoberta quando suportada. Informar instalações atualizadas, destinos pendentes e sessões que precisam ser reabertas. Registrar o resultado no fechamento da review e no chat sem criar ciclos de commit para armazenar o próprio hash. Só então comprovar A4/C3; não afirmar conclusão total com atualização ainda pendente.

## Handoff

`vibe-implement`, após aprovação deste plan. Sem checkpoint intermediário de review necessário.

Recomenda-se iniciar a implementação em novo chat com este alvo. No Modo A, o coordenador conduz ambas as entregas, integração, review e correções delegadas até a confirmação humana final. Continuar neste chat é permitido; não iniciar código nesta porta nem criar chat automaticamente.
