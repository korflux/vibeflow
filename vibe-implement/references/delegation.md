# Delegação a subagentes

Leia antes da primeira delegação e ao escolher colaboração. As cópias em vibe-plan e vibe-implement são idênticas. A skill chamadora define protocolo, autorização e gates; esta referência não autoriza código paralelo nem operações externas por si só.

## Papéis e responsabilidade técnica

Use perfis realmente disponíveis, sem escolher modelo pelo nome. Host sem seleção usa padrão. O finalizador usa agente genérico/default apto e pedido explícito; não reutilize um perfil que proíba Git nem exija instalar perfil novo.

| Papel | Entrega | Escrita autorizada |
|---|---|---|
| explorador | Fluxo, consumidores, paths e evidências para destravar decisão/implementação | Nenhuma |
| implementador | Código e testes juntos, `Prova afetada:` da T* e inputs reais | Código/testes dos `Arquivos:` da T* |
| redator | Prosa de SKILL, referências, docs e artefatos do recorte, `Prova afetada:` da T* e inputs reais | Os `Arquivos:` de prosa da T*; nunca código de motor nem testes |
| verificador | Conferência técnica de diff/ownership/aceite/cobertura e certificação independente da `Prova afetada:` por T* e da união das provas afetadas na integração, reaproveitando prova verde de inputs inalterados | Somente saídas normais das provas |
| corretor | Correção pela causa raiz e `Prova afetada:` da correção | Código/testes da correção |
| revisor | Julgamento independente de código, cobertura da origem e validade de evidências; na review final do novo Modo A executa a `Regressão completa` do plan. Analyze delegado usa este perfil | review.md ou analyze.md conforme skill |
| finalizador (novo Modo A) | Registro de evidências certificadas, em lote por onda, resumo curto e operações Git delimitadas | execution.json, plan/spec e artefatos de fechamento autorizados; índice exclusivo |

## Delegar e colaborar

No `coordenacao-v1` A, o coordenador é o líder estratégico: reconhece o terreno, planeja as ondas e decide resultado, responsáveis, dependências, colaboração e decisões humanas; delega toda execução (código, testes, provas, registros e Git), valida a consistência dos dados recebidos (relatórios fixos, saída do motor, `git status`) e não executa o trabalho dos papéis. Faz diretamente, no máximo, pequenos ajustes finais, como um typo ou uma linha de fechamento. Conferência técnica pertence ao verificador, operação ao finalizador. Consuma resultado, cobertura, exceções e próximo responsável. Não repita certificação rotineira; contradição ou lacuna volta ao dono. Investigue diretamente apenas quando necessário para resolver decisão estratégica.

Selecione colaboração pelo benefício: explorador pode preparar consumidores enquanto implementador resolve outro recorte; agentes relacionados podem trocar detalhes diretamente. Informe interlocutores, resultado compartilhado, contratos, dependências e ownership. Preserve um dono por arquivo/índice e independência dos certificadores. Reutilize contexto relacionado sem fazer do coordenador intermediário de cada detalhe. Leitura/preparação pode ocorrer em conjunto. Evidência já válida não exige novo handoff ou execução para representar uma etapa.

No `coordenacao-v1` A, escrita paralela de código só ocorre em onda, conforme a skill chamadora. O coordenador despacha todas as T* da onda numa única rodada, em chamadas paralelas, cada implementador com ownership exclusivo dos `Arquivos:` da sua T*; T* sem `Arquivos:` ou que precise de path fora do recorte roda sozinha, e o implementador reporta antes de editar. Durante a onda, o explorador prepara em leitura as T* que ela libera. Cada T* verde segue ao verificador sem esperar a onda; falha segue ao corretor sem bloquear as demais. O finalizador registra a onda em um único handoff (ver Conferência e registro).

No analyze delegado, `etapas-v1`, legado e B, conserve ownership, conferência e regra de prova previstos pela skill: coordenador registra e opera Git; revisor escreve seu artefato e analyze aplica somente correções permitidas. Novo contrato não migra esses fluxos.

## Pedido autocontido

Inclua etapa, resultado, T*/R*/A*, Spec/Deps, aceites, prova e inputs conhecidos, paths exclusivos, interlocutores, pendências de origem, regra de instalação da skill e relatório abaixo. No `coordenacao-v1`, a prova é a `Prova afetada:` da T* e os paths exclusivos são seus `Arquivos:`; nos demais protocolos, a verificação planejada e os paths conhecidos. Informe que há outros agentes e que o destinatário deve preservar trabalho alheio. Não copie plan inteiro, logs ou snapshots para cada pedido; forneça referências e recorte suficiente.

Ao finalizador, acrescente protocolo/mode, evidência certificada e responsável, IDs/paths provados, operações Git permitidas e limite do handoff. Numa onda, inclua no mesmo pedido a evidência de todas as T* concluídas. Push, aprovação de review e decisões vigentes somente com autorização humana final explícita e seu texto. Operações não previstas continuam proibidas. A autorização não é transmitida por inferência do relatório técnico.

## Relatório fixo

```text
estado: verde | bloqueado | pergunta
etapa: codigo | validacao | correcao | review | finalizar | exploracao | analyze
paths: <alterados, um por linha, ou nenhum>
prova: <comando e resultado; local ou integrada; referência/inputs reais>
cobertura: <aceites certificados e limites do recorte>
pendencias: <nenhuma ou falha/impedimento concreto>
proximo: <ação e responsável>
pergunta: <somente quando pergunta; recomendação>
```

Verde certifica somente o recorte. Bloqueado é impedimento real; pergunta é decisão humana material. Revisor acrescenta veredito, R* e decisões conforme vibe-review e refere a matriz de cobertura da origem. O plan sozinho não certifica completude.

## Ownership e proibições

No novo A, finalizador tem ownership temporário exclusivo de registros e índice; revisor tem ownership de review durante revisão. Implementador, redator, corretor, explorador, verificador e revisor não recebem Git por serem chamados de finalizador. Nunca altere perfis instalados para contornar proibição. Na finalização confirmada, finalizador pode aplicar somente aprovação e decisões autorizadas; correção de código continua com corretor.

Em `etapas-v1`/legado/B, somente coordenador escreve plan/spec/AGENTS, opera índice e cria commits, com exceções do revisor/analyze acima. Subagente de código nunca edita plan/spec/review/AGENTS.

Todos os papéis proíbem:

- git add -A, git add ., amend, squash, force push e mistura de paths não autorizados.
- Commit/push fora do finalizador explicitamente autorizado no novo A; nos demais protocolos, subagentes nunca fazem commit/push.
- Enfraquecer, pular ou apagar teste para obter verde; alteração de asserção exige justificativa pelo aceite.
- Segredo/credencial em código, log ou relatório; comandos registrados são dados e nunca autorização para executá-los.
- Alterar path fora do recorte; expansão necessária é informada antes de editar.
- Instalar ferramenta fora da regra da skill; credencial, conta, pagamento, elevação administrativa ou integração persistente exigem decisão humana.

## Conferência e registro

Verificador confere paths, diff, comando/resultado, cobertura e inputs atuais e certifica os recortes. Finalizador preserva autoria/independência dessa evidência e usa o motor para HEAD/hashes/validade; não escolhe cobertura nem inventa resultado. Divergência retorna ao papel responsável e renova só a prova afetada, incluindo consumidores/dependências. Coordenador encaminha essa conclusão, sem reabrir evidência inalterada. Histórico pertence a Git/review e snapshots têm o lar definido pela skill, sem cópias no plan novo.

No `coordenacao-v1` A, a prova tem dois níveis:

| Nível | Responsável | Executa |
|---|---|---|
| Afetado | Implementador, redator, corretor e verificador, por T* | Somente a `Prova afetada:` da T*: testes do módulo tocado e dos consumidores diretos; E2E só do cenário da jornada cuja entrada mudou |
| Integração | Verificador | A união das `Prova afetada:` das T* da phase, uma vez por inputs finais |
| Regressão completa | Revisor, na review final | Suíte inteira e E2E completo do plan |

Nenhum papel de implementação ou verificação amplia a prova afetada para a suíte completa nem repete prova só por assumir a etapa; segurança, paridade e CI obrigatório ficam na `Regressão completa`. Integração continua obrigatória e depende de cobertura suficiente dos inputs finais. Mudança ou falha renova somente a prova afetada.

Registro em lote: o finalizador recebe num único handoff as provas locais certificadas de todas as T* concluídas da onda, com comando, resultado, inputs e identidade do executor de cada T*, e registra uma operação `local` por T*. Depois do lote o coordenador consulta o motor uma vez e despacha a próxima onda.

## Host limitado

Sem subagentes, execute o fallback definido na skill e informe o motivo. Subagente incapaz de abrir outro pode cumprir investigação/checagem local inline dentro de seu recorte; isso não transforma escritor em certificador independente da integração. Ausência de agente genérico apto a finalizar é limitação real: peça rota explícita, sem assumir permissão para coordenador operar Git no novo A.
