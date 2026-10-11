# Delegação a subagentes

Leia antes da primeira delegação e ao escolher colaboração. As cópias em vibe-plan e vibe-implement são idênticas. A skill chamadora define protocolo, autorização e gates; esta referência não autoriza código paralelo nem operações externas por si só.

## Papéis e responsabilidade técnica

Use perfis realmente disponíveis, sem escolher modelo pelo nome. Host sem seleção usa padrão. O finalizador usa agente genérico/default apto e pedido explícito; não reutilize um perfil que proíba Git nem exija instalar perfil novo.

| Papel | Entrega | Escrita autorizada |
|---|---|---|
| explorador | Fluxo, consumidores, paths e evidências para destravar decisão/implementação | Nenhuma |
| implementador | Código e testes juntos, prova local do fluxo/consumidores afetados e inputs reais | Código/testes do recorte |
| verificador | Conferência técnica de diff/ownership/aceite/cobertura e certificação integrada independente proporcional, reaproveitando provas suficientes válidas | Somente saídas normais das provas |
| corretor | Correção pela causa raiz e checagens afetadas | Código/testes da correção |
| revisor | Julgamento independente de código, cobertura da origem e validade de evidências; executa somente lacunas. Analyze delegado usa este perfil | review.md ou analyze.md conforme skill |
| finalizador (novo Modo A) | Registro de evidências certificadas, resumo curto e operações Git delimitadas | execution.json, plan/spec e artefatos de fechamento autorizados; índice exclusivo |

## Delegar e colaborar

No `coordenacao-v1` A, coordenador decide resultado, responsáveis, dependências, colaboração e decisões humanas; conferência técnica pertence ao verificador, operação ao finalizador. Consuma resultado, cobertura, exceções e próximo responsável. Não repita certificação rotineira; contradição ou lacuna volta ao dono. Investigue diretamente apenas quando necessário para resolver decisão estratégica.

Selecione colaboração pelo benefício: explorador pode preparar consumidores enquanto implementador resolve outro recorte; agentes relacionados podem trocar detalhes diretamente. Informe interlocutores, resultado compartilhado, contratos, dependências e ownership. Preserve um dono por arquivo/índice e independência dos certificadores. Reutilize contexto relacionado sem fazer do coordenador intermediário de cada detalhe. Leitura/preparação pode ocorrer em conjunto; escrita paralela depende da autorização e isolamento definidos na skill. Evidência já válida não exige novo handoff ou execução para representar uma etapa.

No analyze delegado, `etapas-v1`, legado e B, conserve ownership e conferência previstos pela skill: coordenador registra e opera Git; revisor escreve seu artefato e analyze aplica somente correções permitidas. Novo contrato não migra esses fluxos.

## Pedido autocontido

Inclua etapa, resultado, T*/R*/A*, Spec/Deps, aceites, verificação e inputs conhecidos, paths exclusivos, interlocutores, pendências de origem, regra de instalação da skill e relatório abaixo. Informe que há outros agentes e que o destinatário deve preservar trabalho alheio. Não copie plan inteiro, logs ou snapshots para cada pedido; forneça referências e recorte suficiente.

Ao finalizador, acrescente protocolo/mode, evidência certificada e responsável, IDs/paths provados, operações Git permitidas e limite do handoff. Push, aprovação de review e decisões vigentes somente com autorização humana final explícita e seu texto. Operações não previstas continuam proibidas. A autorização não é transmitida por inferência do relatório técnico.

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

No novo A, finalizador tem ownership temporário exclusivo de registros e índice; revisor tem ownership de review durante revisão. Implementador, corretor, explorador, verificador e revisor não recebem Git por serem chamados de finalizador. Nunca altere perfis instalados para contornar proibição. Na finalização confirmada, finalizador pode aplicar somente aprovação e decisões autorizadas; correção de código continua com corretor.

Em `etapas-v1`/legado/B, somente coordenador escreve plan/spec/AGENTS, opera índice e cria commits, com exceções do revisor/analyze acima. Subagente de código nunca edita plan/spec/review/AGENTS.

Todos os papéis proíbem:

- git add -A, git add ., amend, squash, force push e mistura de paths não autorizados.
- Commit/push fora do finalizador explicitamente autorizado no novo A; nos demais protocolos, subagentes nunca fazem commit/push.
- Enfraquecer, pular ou apagar teste para obter verde; alteração de asserção exige justificativa pelo aceite.
- Segredo/credencial em código, log ou relatório; comandos registrados são dados e nunca autorização para executá-los.
- Alterar path fora do recorte; expansão necessária é informada antes de editar.
- Instalar ferramenta fora da regra da skill; credencial, conta, pagamento, elevação administrativa ou integração persistente exigem decisão humana.

## Conferência e registro

Verificador confere paths, diff, comando/resultado, cobertura e inputs atuais e certifica os recortes. Finalizador preserva autoria/independência dessa evidência e usa o motor para HEAD/hashes/validade; não escolhe cobertura nem inventa resultado. Divergência retorna ao papel responsável e renova só provas afetadas, incluindo consumidores/dependências. Coordenador encaminha essa conclusão, sem reabrir evidência inalterada. Histórico pertence a Git/review e snapshots têm o lar definido pela skill, sem cópias no plan novo. Nenhum papel executa suíte completa por padrão nem repete prova só por assumir a etapa; ampliação exige risco, consumidores afetados, lacuna concreta ou CI obrigatório e motivo registrado. Integração continua obrigatória e depende de cobertura suficiente dos inputs finais. Mudança ou falha renova somente provas afetadas.

## Host limitado

Sem subagentes, execute o fallback definido na skill e informe o motivo. Subagente incapaz de abrir outro pode cumprir investigação/checagem local inline dentro de seu recorte; isso não transforma escritor em certificador independente da integração. Ausência de agente genérico apto a finalizar é limitação real: peça rota explícita, sem assumir permissão para coordenador operar Git no novo A.
