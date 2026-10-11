# Spec: Provas proporcionais e correções obrigatórias
# Alvo: phase-18-provas-e-correcoes-obrigatorias
# Status: aprovado

## Objetivo

Tornar explícita a divisão de testes entre implementação, verificação e review, evitando repetição sem causa. Exigir resolução de toda correção pertinente à entrega antes de aprovar, independentemente da severidade, preservando simplificação e otimização do código tocado. Após aprovação final e push confirmado, atualizar as instalações locais do VibeFlow nos hosts do usuário.

## Cobertura da origem

| Origem | Destino na spec | Motivo se fora/N/A |
|---|---|---|
| Pedido de testes localizados na implement e ausência de repetição na review | F1, A1 | N/A |
| Toda correção obrigatória, inclusive nit | F2, A2 | N/A |
| Preservar capacidade de otimização | F3, A3 | N/A |
| Atualizar todos os CLIs depois de aprovado e com push | F4, A4 | Atualização do VibeFlow instalado, sem upgrade dos executáveis dos hosts |

## Suposições e decisões

1. Rota high: intenção clara, com regressão possível na fila de correções dos motores. Design N/A: não há UI visível.
2. Implementador cria ou complementa testes junto do código e executa provas direcionadas ao fluxo e consumidores afetados. Verificador certifica integração proporcional ao impacto; integração não implica suíte completa.
3. Review audita código, cobertura, origem e validade das provas. Não reexecuta comandos apenas por começar uma nova etapa ou por ser outro agente.
4. Suíte completa continua cabível quando o impacto, uma lacuna concreta ou CI obrigatório exigir. A justificativa deve apontar a necessidade real. Custo não autoriza dispensar provas necessárias.
5. Toda correção válida da entrega bloqueia aprovação enquanto aberta. Severidade expressa impacto e prioridade, não possibilidade de dispensar a correção. Preferência pessoal sem fundamento não vira achado. FYI puramente informativo fica em notas, sem R* de correção.
6. Problemas externos ao escopo permanecem registrados em `.erros-encontrados/`, sem ampliar silenciosamente a entrega. Item necessário ao comportamento, aceite ou segurança da entrega não pode ser reclassificado como externo apenas para aprovar.
7. Não reescrever fases encerradas nem migrar protocolos históricos. Na retomada de uma fase aberta, correções pendentes registradas como Nit, Optional ou FYI também precisam ser tratadas; classificação antiga não libera a aprovação.
8. A atualização local fica condicionada à aprovação humana final e ao sucesso do push. Preservar configurações, credenciais, regras globais e personalizações alheias ao pacote.

## Escopo e comportamento

### F1: Implementar, certificar e reaproveitar provas

- Jornada: alteração de software até review final.
- Rota: implement → verificação integrada → review.
- Gatilho: código novo, alteração ou retomada de entrega.
- Pré-condição: escopo e aceite conhecidos, protocolo existente identificado.
- Superfície: chat, artefatos operacionais e saída dos motores; UI N/A.
- Passos:
  1. Implementador investiga fluxo e consumidores, entrega código/testes e comprova o recorte alterado.
  2. Verificador confere cobertura e estado integrado, reaproveita evidência suficiente válida e executa apenas lacunas necessárias.
  3. Revisor inspeciona independentemente código e qualidade das provas; executa verificações adicionais somente por lacuna, falha, mudança de inputs relevantes ou risco concreto.
  4. Após correção, renovar apenas provas afetadas, incluindo consumidores e configuração relevantes.
- Validações: evidência deve corresponder aos inputs atuais e cobrir o resultado alegado; justificativa de execução ou reaproveitamento no registro próprio do protocolo.
- Erros: evidência ausente, inválida ou insuficiente mantém certificação pendente; falha exige correção da causa.
- Estados: prova local, integração pendente, integração certificada, prova invalidada.
- Aceite: A1.
- Reutilizar: snapshots, seleção proporcional e separação de responsabilidades existentes.

### F2: Resolver todas as correções antes de aprovar

- Jornada: achado → correção → re-review → aprovação.
- Rota: review → implement → review.
- Gatilho: achado concreto com evidência e remédio dentro da entrega.
- Pré-condição: R* identificado, com severidade e prova esperada.
- Superfície: chat, review e fila operacional; UI N/A.
- Passos:
  1. Revisor registra correção fundamentada, inclusive pequena, como R* obrigatório.
  2. Motor mantém etapa de correção enquanto existir R* aberto, independentemente de Critical, Required, Nit, Optional ou FYI legado.
  3. Corretor resolve causa e executa provas afetadas; registros conservam IDs e histórico.
  4. Re-review confirma solução. Approve só fica elegível sem correções abertas; confirmação humana final continua necessária.
- Validações: nenhuma variante de aprovação com defer libera correção pendente. R* fechado não reabre só por severidade. Notas informativas novas não usam R*.
- Erros: aprovação marcada com correção aberta não libera confirmação/finalização; limites existentes de rodadas continuam e devem relatar qualquer pendência.
- Estados: correção aberta, correção comprovada, aprovação proposta, aprovação humana confirmada.
- Aceite: A2.
- Reutilizar: parser de review, fila dos protocolos, relatório delegado e histórico de R*.

### F3: Simplificar e otimizar a entrega

- Jornada: implementação e correção do recorte autorizado.
- Rota: implement e correções.
- Gatilho: código tocado com duplicação, complexidade desnecessária ou necessidade demonstrável de desempenho.
- Pré-condição: fluxo e consumidores entendidos.
- Superfície: código, testes e relatório; UI N/A.
- Passos: reutilizar fontes existentes; simplificar responsabilidades e remover redundância; consolidar testes redundantes preservando cenários; otimizar desempenho quando fundamentado; comprovar comportamento e controles preservados.
- Validações: sem abstração especulativa, perda de cobertura, remoção de proteção ou limpeza fora da fatia.
- Erros: regressão impede conclusão; oportunidade externa é registrada separadamente.
- Estados: melhoria aplicada e provada, ou oportunidade externa registrada.
- Aceite: A3.
- Reutilizar: etapa de simplificação e Definition of Done existentes.

### F4: Publicar e atualizar instalações locais

- Jornada: aprovação humana final → push → atualização do VibeFlow nos hosts.
- Rota: fechamento da phase e distribuição local.
- Gatilho: aprovação humana final, incluindo publicação.
- Pré-condição: integração comprovada, review sem correções abertas e commit real.
- Superfície: chat e comandos dos instaladores; UI N/A.
- Passos: confirmar sucesso do push; inventariar destinos instalados e método de distribuição; atualizar o VibeFlow pela versão publicada; conferir conteúdo/versão nos destinos e relatar necessidade de recarregar sessões.
- Validações: instalação corresponde à revisão publicada; cobrir destinos compartilhados e cópias existentes sem apagar personalizações. Codex, Claude Code, Grok, Antigravity e OpenCode foram encontrados no PATH nesta descoberta; Pi e outros destinos devem ser conferidos pelo inventário de instalações.
- Erros: push falho impede atualização; destino inacessível ou atualização falha permanece pendente com causa explícita, sem declarar todos atualizados.
- Estados: aguardando aprovação, publicado, atualização parcial, instalações conferidas.
- Aceite: A4.
- Reutilizar: mecanismos de instalação e manifests existentes.

### Fora

- Upgrade dos binários dos CLIs, alterações em regras globais e instalação de hosts novos.
- Nova infraestrutura de testes, benchmark especulativo e refatoração geral dos protocolos.
- Reescrita de evidências históricas e repetição automática da suíte inteira.

## Checklist de entrega

### Aceite

- [x] A1: contratos distinguem provas locais, integração e auditoria, com execução proporcional e reaproveitamento por inputs válidos.
- [x] A2: todos os R* de correção abertos bloqueiam aprovação e permanecem na fila, inclusive classificações legadas; aprovação com defer deixa de ser uma saída válida para pendências.
- [x] A3: simplificação, reutilização e otimização fundamentada permanecem explícitas, sem enfraquecer comportamento, segurança ou cobertura.
- [ ] A4: depois da aprovação final e push bem-sucedido, instalações locais do VibeFlow são atualizadas e conferidas, ou falhas são individualizadas como pendências.

### Critérios de sucesso

- [x] C1: motores Python e PowerShell apresentam o mesmo bloqueio e encaminhamento para cenários de achados abertos, fechados e vereditos legados.
- [x] C2: skill, referências, templates, contratos e motores não oferecem caminhos conflitantes para dispensar correções ou repetir provas sem necessidade.
- [ ] C3: relatório final identifica revisão publicada, destinos atualizados e qualquer instalação pendente.

## Contratos e restrições necessárias

- Preservar paths, IDs e registros próprios de cada protocolo. A obrigatoriedade das correções altera comportamento público e deve seguir o semver do repositório.
- Testes automatizados exercitam motores e efeitos em pastas isoladas; é proibido testar presença de frases em documentação ou skills. Coerência da prosa exige inspeção semântica.
- Não introduzir novos dados externos, endpoints, segredos, autenticação ou persistência de produto. Controles web e banco: N/A. A atualização usa distribuição já existente e preserva arquivos alheios ao pacote.

## Como provar

| Aceite | Evidência esperada |
|---|---|
| A1 | Inspeção semântica do fluxo completo e registros da execução desta entrega demonstrando seleção proporcional e reaproveitamento quando aplicável |
| A2 | Cenários executáveis dos motores com correções de todas as classificações, aprovação indevida, fechamento e retomada, verificando fila e efeitos reais |
| A3 | Inspeção da etapa de simplificação e seus consumidores, assegurando preservação do contrato de otimização |
| A4 | Evidência do push e comparação da instalação local com o pacote publicado em cada destino efetivamente encontrado |

## Boundaries

### Always

- Manter independência da review e certificação suficiente da integração.
- Tratar toda correção pertinente como obrigatória, inclusive nit.
- Preservar evidências válidas e personalizações locais.

### Ask first

- Aprovação do artefato e avanço da cadeia conforme as regras do projeto.
- Confirmação final antes de push; mudança material de escopo ou substituição de personalização conflitante.

### Never

- Aprovar com correção pendente, enfraquecer testes para obter verde ou atualizar hosts antes do push confirmado.
- Alterar artefatos históricos para fazê-los parecer conformes ao contrato novo.

## Handoff

vibe-plan. Rota high; design N/A por ausência de UI.

Recomenda-se novo chat para plan; continuar neste chat é permitido. O plan deve incluir atualização das instalações como fechamento posterior à aprovação e publicação, sem torná-la pré-condição circular da review do código.

- [x] Aprovação humana: Marco autorizou avançar para o plan em 2026-10-11.
