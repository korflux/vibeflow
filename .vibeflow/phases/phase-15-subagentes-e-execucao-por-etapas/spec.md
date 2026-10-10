# Spec: subagentes instalados e execução por etapas
# Alvo: phase-15-subagentes-e-execucao-por-etapas
# Status: aprovado

## Objetivo

Preparar os cinco papéis de subagente no vibe-init usando como referência os perfis que Marco já criou no Codex e no Claude Code. Reduzir repetição de provas no Modo A, separando implementação, complementação de testes, validação integrada, correção e review. A revisão deve demonstrar que a solicitação original foi integralmente atendida, além de verificar a qualidade do código entregue.

## Cobertura da origem

| Origem | Destino na spec | Motivo se fora/N/A |
|---|---|---|
| Init não instala subagentes; usar os perfis pessoais como padrão | F1, A1 a A3 | N/A |
| Implementar antes da rodada completa de testes | F2, A4 a A6 | Mantêm-se verificações locais rápidas |
| Criar testes, testar, corrigir e depois revisar | F2, A5 a A7 | N/A |
| Review esquece partes da solicitação | F3, A8 | N/A |
| Aceite do usuário à proposta de checagens locais e validação integrada | F2 | Confirmado no chat em 2026-10-10 |

## Suposições e decisões

1. Rota high, mudança delimitada de contrato operacional com instalação restrita ao projeto. Não há UI; design N/A. Esta spec descreve comportamento proposto, ainda sujeito à aprovação.
2. Referências consultadas em 2026-10-10: os cinco arquivos em `C:/Users/marco/.codex/agents/*.toml` e os cinco em `C:/Users/marco/.claude/agents/*.md`. Esses arquivos pessoais são referência de autoria, não dependência de instalação do pacote distribuído. Não serão alterados.
3. Preservar os papéis explorador, implementador, verificador, corretor e revisor, suas restrições e a distribuição de modelos/esforço observada. Codex: explorador/verificador gpt-6-luna/max, implementador/corretor gpt-6.1-sol/medium, revisor gpt-6-astra/low. Claude: explorador/verificador haiku/xhigh, implementador/corretor sonnet/xhigh, revisor opus/medium. Não substituir modelos silenciosamente quando indisponíveis.
4. Os prompts distribuídos serão adaptados ao novo fluxo e terão referências portáveis às skills, sem caminhos pessoais. O implementador também cria testes quando delegado para essa etapa. O verificador executa provas, sem corrigir código ou escrever testes. O corretor atende também falhas pré-review, sem exigir R* artificial.
5. O Modo A continua sequencial, com um escritor de código por vez. Reutilizar o agente de implementação em tarefas relacionadas quando preservar contexto ajudar; revisor sempre independente e com contexto limpo. Não introduzir paralelismo nesta entrega.
6. Proposta de Git: no Modo A, um commit integrado das T* validadas ao final da integração, identificando todos os IDs atendidos. Evita commits artificiais de estados intermediários nunca provados. Modo B mantém commit por T*. Correções posteriores continuam recebendo commits após prova verde. Esta decisão substitui, somente no Modo A, o commit isolado por tarefa das phases 9, 13 e 14 e precisa ser refletida nas regras vigentes após aprovação do fluxo.
7. Código implementado não significa tarefa concluída: `[x]` continua reservado à entrega provada. Dependências de implementação podem avançar com código integrado e checagem local válida, sem simular conclusão. Estado intermediário e provas ficam no plan existente.
8. Preservar a confirmação humana final para aprovar review, publicar decisões vigentes e fazer push. Nenhuma autorização de implementação equivale a autorização de push.
9. A alteração do Modo A muda comportamento público e exige versão major conforme o contrato do repositório. Plan determinará a versão concreta a partir dos manifestos atuais.

## Escopo e comportamento

### F1: instalar e conferir papéis no init

- Jornada: preparar ou reparar um repositório VibeFlow.
- Rota: init.
- Gatilho: execução do vibe-init.
- Pré-condição: raiz acessível e pacote contendo os perfis distribuídos.
- Superfície: N/A para UI; CLI, relatório operacional e arquivos do projeto.
- Passos:
  1. Preparar as regras com as garantias atuais e instalar os cinco perfis de cada host em `.codex/agents/` e `.claude/agents/` do projeto. Distribuir os dois adaptadores torna o repositório utilizável em ambos sem depender de detecção do host invocador.
  2. Criar perfis ausentes e preservar perfis existentes idênticos. Perfil diferente com mesmo destino permanece intacto e aparece como conflito explícito, sem sobrescrita ou afirmação de instalação completa.
  3. Conferir os arquivos produzidos e informar perfis instalados, preservados e conflitantes. Orientar recarga quando necessária e distinguir existência em disco de disponibilidade efetiva na sessão.
  4. Antes da primeira delegação, conferir os papéis disponíveis na sessão. Ausência de papel não autoriza inventar uma capacidade nem declarar que o init concluiu a ativação.
- Validações: não alterar configurações globais, permissões gerais nem modelos pessoais; recusar links/reparse points e destinos não regulares no caminho de instalação; preservar todas as garantias atuais de backup do init.
- Erros: destino inseguro ou não regular interrompe a mutação afetada com mensagem segura; conflitos são relatados com os paths, sem expor conteúdo sensível.
- Estados: ausente, instalado, já instalado, conflito, indisponível na sessão.
- Aceite: A1, A2, A3.
- Reutilizar: motores Python/PowerShell, relatório, validações de caminho e commit explícito do init.

### F2: executar o Modo A por etapas

- Jornada: plan aprovado até entrega integrada pronta para review.
- Rota: implement no Modo A; gates de analyze continuam quando aplicáveis.
- Gatilho: execução autorizada de vibe-implement.
- Pré-condição: artefatos exigidos aprovados e subagentes disponíveis.
- Superfície: N/A para UI; chat, plan e JSON operacional.
- Passos:
  1. Implementar as T* em ordem de dependência. Executar somente checagens locais proporcionais, como sintaxe, tipos ou teste direcionado ao contrato afetado. Falha local relevante impede liberar dependentes até correção.
  2. Registrar por T* o estado implementado, paths e checagens, mantendo conclusão desmarcada. Reusar agentes quando útil sem misturar ownership ou contexto de review.
  3. Após a implementação, delegar ao implementador a conferência dos testes existentes e a criação dos testes faltantes a partir do pedido e dos critérios de aceite. Não criar testes redundantes nem basear expectativas exclusivamente no código recém-escrito.
  4. Delegar ao verificador a suíte relevante, build e demais provas integradas necessárias. Consolidar comandos que cobrem várias tasks; não repetir a matriz completa por T*.
  5. Falhas voltam ao corretor com evidência. Repetir provas afetadas e confirmar cobertura da integração; preservar provas não invalidadas por edições. Falha de teste não é aprovação e não consome rodada de correção de review.
  6. Com integração verde, marcar apenas tasks efetivamente comprovadas e criar o commit integrado com paths explícitos e IDs das T*. Falha de commit mantém a finalização pendente.
  7. Delegar review independente. Correções de review seguem o limite existente de duas rodadas, com nova review após cada rodada. Fechar com a confirmação humana já prevista.
- Retomada: derivar etapa e pendências dos artefatos, sem novo arquivo de estado. Snapshot inclui HEAD, paths relevantes e hashes; mudanças invalidam as provas afetadas. Não reimplementar tarefas já registradas como implementadas quando o disco confirma esse estado. Artefatos antigos permanecem legíveis, sem reabrir tarefas concluídas ou reinterpretar silenciosamente runs antigas como o novo modo.
- Validações: ciclo ou dependência inexistente bloqueiam a fila; ausência de registro suficiente nunca vira conclusão implícita; prova local não substitui a integrada; trabalho alheio não entra no commit.
- Erros/estados: implementação pendente, testes pendentes, validação pendente, falha em correção, integração comprovada, revisão e confirmação. Semântica precisa ser equivalente nos dois motores.
- Aceite: A4 a A7.
- Reutilizar: plan como registro único, checkpoint, parser de dependências, provas por inputs, papéis existentes e review delegada.

### F3: demonstrar completude na review

- Jornada: review final da entrega, incluindo Modo B quando chegar à review final.
- Rota: review.
- Gatilho: revisão da integração.
- Pré-condição: pedido original registrado no contexto/artefatos e implementação disponível para inspeção.
- Superfície: N/A para UI; review.md e relatório ao coordenador.
- Passos:
  1. Reconstruir o escopo a partir do pedido original, alterações autorizadas, interview quando houver, cobertura da origem, critérios da spec e plan. O plan sozinho não define completude.
  2. Registrar uma matriz enxuta: solicitação, implementação, evidência de funcionamento e situação. Agrupar itens com o mesmo resultado sem omitir capacidades independentes.
  3. Classificar cada item como atendido, parcial, ausente ou retirado explicitamente pelo humano, citando a decisão de retirada. Obrigatório parcial ou ausente gera achado bloqueante; retirada inferida pelo agente não é válida.
  4. Emitir veredito técnico e de completude. Reaproveitar provas válidas e executar somente o necessário para lacunas ou riscos encontrados. Se faltar a origem necessária para julgar completude, declarar a limitação e solicitar o contexto, sem certificar atendimento integral.
- Validações: testes verdes e código correto não compensam solicitação omitida. Checkpoint de review cobre apenas seu marco e não certifica a entrega inteira.
- Estados: atendido, parcial, ausente, retirado pelo humano; veredito conforme contrato da review.
- Aceite: A8.
- Reutilizar: pilar de rastreabilidade existente, R*, etapas e veredito do review.md.

### Fora

- Modificação dos perfis globais de Marco, instalação de CLIs, compra de acesso a modelos ou alteração automática de permissões.
- Paralelismo no Modo A, novo papel criador de testes e novo arquivo de estado.
- Mudança do ciclo por tarefa do Modo B ou relaxamento de segurança e integridade dos testes.
- Promessa de redução percentual de duração sem medição; a melhoria verificável é retirar execuções completas redundantes.

## Checklist de entrega

### Aceite

- [x] A1: init instala os cinco papéis nos formatos dos dois hosts, com modelos/esforços de referência e prompts compatíveis com o novo fluxo.
- [x] A2: repetir init é idempotente; conflitos e destinos inseguros não sobrescrevem personalizações nem escapam da raiz.
- [x] A3: relatório distingue instalação em disco, conflito e disponibilidade em sessão, com instrução de recarga quando aplicável.
- [x] A4: Modo A libera dependências de implementação sem marcar conclusão prematura e retoma corretamente estados intermediários.
- [x] A5: etapa de testes complementa cobertura por aceite e preserva testes existentes relevantes; verificador não escreve testes.
- [x] A6: validação integrada evita repetir suíte completa por task, corrige falhas e invalida somente provas afetadas.
- [x] A7: commit integrado ocorre somente com prova verde, preserva rastreabilidade por T* e mantém confirmação final e Modo B.
- [x] A8: review expõe cobertura de toda solicitação inicial e bloqueia aprovação com item obrigatório ausente ou parcial, mesmo com testes verdes.

### Critérios de sucesso

- [x] C1: instalação e estados operacionais têm provas executáveis em diretórios isolados com limpeza obrigatória, incluindo paridade essencial dos motores.
- [x] C2: simulação de implementação, testes, falha, correção e retomada não salta validação nem confunde implementado com concluído.
- [x] C3: avaliação comportamental da review detecta um requisito omitido do plan, sem teste que apenas busque palavras na documentação.
- [x] C4: contratos, templates, referências compartilhadas e distribuição permanecem coerentes com os comportamentos aprovados.

## Contratos e restrições necessárias

- Manter Python 3 e PowerShell 7 com launcher Unix; não adicionar dependência para instalação de perfis.
- Allowlist de destinos: somente cinco nomes conhecidos, extensões `.toml`/`.md` e diretórios de agentes dos dois hosts sob a raiz validada. Perfis distribuídos limitados a 1 MiB por arquivo; arquivos externos conflitantes não são executados ou interpretados como comandos.
- Não copiar credenciais, diretórios pessoais inteiros ou configuração global para o pacote. Perfis não concedem bypass de segurança.
- API, banco, autenticação web, CORS, CSRF e UI: N/A, pacote local de skills sem essas superfícies.
- Definições de papéis são adaptadores operacionais, não segunda fonte das regras do projeto. AGENTS.md permanece a fonte viva.

## Como provar

| Aceite | Evidência esperada |
|---|---|
| A1 a A3 | Execuções de init em raiz temporária: arquivos corretos, segunda execução estável, customização preservada, links recusados e relatório correspondente |
| A4 | Estados de fila antes/depois da implementação, dependências e retomada em ambos os motores |
| A5 e A6 | Cenário comportamental com teste existente, lacuna de cobertura, falha real e correção; comandos registrados sem repetição injustificada |
| A7 | Estado de conclusão/commit coerente com prova integrada, sem alteração do contrato de Modo B |
| A8 | Revisão independente de uma entrega tecnicamente correta que omite uma solicitação; omissão deve bloquear Approve |

## Fontes

- Perfis pessoais indicados em Suposições e decisões, lidos em 2026-10-10.
- [Codex: subagentes](https://learn.chatgpt.com/docs/agent-configuration/subagents), formato TOML e escopo do projeto.
- [Claude Code: subagentes](https://code.claude.com/docs/en/sub-agents), frontmatter, escopo e carregamento.
- Contratos atuais: docs/vibe-init/ARQUITETURA.md, docs/vibe-implement/ARQUITETURA.md, vibe-implement/references/delegation.md e vibe-review/SKILL.md.

## Boundaries

### Always

- Preservar personalizações e evidências; conferir comportamento no disco; manter escritora única dos artefatos e Git no coordenador.

### Ask first

- Confirmar esta spec antes do plan, especialmente a substituição do commit por task no Modo A pelo commit integrado.
- Pedir decisão diante de conflito de perfil cuja resolução exija substituir personalização ou trocar modelo.

### Never

- Marcar conclusão com base apenas em código escrito, reduzir escopo sem autorização, enfraquecer testes ou fazer push sem confirmação final.

## Handoff

vibe-plan. Design N/A: mudança de instalação e orquestração, sem UI visível.
Recomenda-se novo chat para o plan; continuar neste chat é válido.

- [x] Aprovação humana: Marco confirmou em 2026-10-10 e autorizou seguir para o plan, incluindo o commit integrado do Modo A.

## Correções adicionais autorizadas em 2026-10-10

Marco solicitou auditar os achados da review e `.erros-encontrados/` e corrigir os problemas ainda atuais. A proposta anterior de fechamento da phase será revista depois dessas alterações; nenhuma autorização de push foi dada.

- A9: testes não ocultam falhas de remoção de fixtures e não anunciam cobertura inexistente em comentários/classes vazias. Preservar asserções e segurança dos caminhos; remover resíduos após provas.
- A10: os motores emitem stdout e mensagens operacionais em UTF-8 explícito em ambos os runtimes, incluindo avisos acentuados e paths Unicode. Prova é sobre bytes/processo e efeitos no disco, sem varredura de palavras em documentação.
- A11: review avulsa com slug explícito cria/reporta sua própria phase, mesmo com plan pendente; não altera a phase automática. Alvo explícito ambíguo slug+dir é recusado antes de mutação.
- A12: Approve com defer permite somente Nit/Optional/FYI com referência, motivo e encaminhamento. Critical/Required aberto, obrigação parcial/ausente ou origem insuficiente continuam bloqueando a aprovação.
- A13: atualizar os registros com situação real e evidência. Erros já corrigidos e limitações de ambiente não geram novo patch de produto. A ausência histórica de commit isolado na phase 9 é preservada; não reescrever Git nem produzir commit artificial para simular correção.

Rastreabilidade das correções: R2 a R6 no review vivo desta phase. Implementação sequencial, commit de correção após provas e nova review independente; sem novo arquivo de estado ou migração da própria run para etapas-v1.