# <frase curta da fase ou nome provisório do MVP>
# Status: rascunho

<!-- Escreva diretamente neste artefato vivo; mantenha rascunho até a confirmação humana. -->

## Solicitação

<pedido original, sem reescrever>

## Hipótese inicial

```text
HIPÓTESE: <interpretação inicial>
CONFIDENCE: ~<N>%, falta: <gaps>
```

## Trilha

### 1

ANOTEI: <interpretação fiel do pedido ou da resposta anterior; diferencie fatos de hipóteses>
Q: <uma pergunta focada>
GUESS: <resposta provisória, motivo e confiança quando a base for limitada>
R: <resposta do humano e se confirmou, corrigiu ou rejeitou o guess>

## Resultado

Entendi assim:

- O quê:
- Pra quem:
- Por quê:
- Sucesso:
- Limite:
- Fora:
- Visual:

## Direção

<!-- Omitir se a forma não foi refinada. -->

## Cobertura do MVP

<!-- Omitir esta seção e todas as próximas se o alvo não for MVP. -->

| Domínio | Estado | Evidência ou premissa |
|---|---|---|
| <domínio relevante> | <DECIDIDO, ASSUMIDO, N/A ou PENDENTE CRÍTICO> | <resposta, recomendação aceita ou motivo> |

## Mapa do produto

### Jornadas e telas

<!-- Obrigatório para MVP com interface. Jornada sem saída ou sem estado crítico não fecha. Texto livre sem tabela é defeito. Use N/A explícito quando não houver jornada. -->

| Jornada | Ator | Gatilho | Objetivo | Páginas/telas | Entrada | Saída | Estado crítico |
|---|---|---|---|---|---|---|---|
| <frase curta> | <quem executa> | <o que inicia> | <o que deve obter> | <telas> | <dado ou ação de entrada> | <resultado> | <estado crítico ou N/A com motivo> |

### Páginas e navegação

<!-- Para toda interface. Inclua menu, links, CTA, redirecionamentos e retorno; N/A fundamentado quando só existir uma superfície. -->

| Página/tela | Como chega | Ação e próximo destino | Como volta | Estado relevante |
|---|---|---|---|---|
| <nome> | <menu, link, CTA ou evento> | <ação → destino> | <menu, link ou N/A> | <vazio, erro, sem permissão ou N/A> |

### Dados e integrações

<entidades, relações, arquivos, importação, exportação, APIs e notificações>

### Acesso e usuários

<!-- Obrigatório. Checklist com N/A explícito quando não aplicável. -->

- login: <como entra ou N/A com motivo>
- cadastro: <como cria conta ou N/A com motivo>
- dados do cadastro: <campos mínimos e obrigatórios ou N/A>
- verificação: <canal, validade, reenvio e falha ou N/A>
- recuperação: <como recupera acesso ou N/A com motivo>
- sessão: <duração, renovação e revogação ou N/A com motivo>
- papéis: <papéis e capacidades ou N/A com motivo>
- primeiro usuário: <como é criado ou N/A com motivo>
- bloqueio: <quando bloqueia e como desbloqueia ou N/A com motivo>
- logout: <como sai e o que invalida ou N/A com motivo>

## Direção técnica

<repositório, stack, persistência e necessidade de banco, execução local/publicada, provedor e plano/VPS existentes, acesso e restrições, ambientes, deploy e justificativas; N/A fundamentado quando aplicável>

## Direção visual

<identidade existente, logo, nome, referências, tema principal, light/dark, cor primária, tokens, fonte e acessibilidade>

## Operação

<segurança, privacidade, analytics, logs, backup, restore, suporte, custos e responsável>

## Decisões críticas

| ID | Estado | Decisão | Motivo e impacto |
|---|---|---|---|
| <DOMINIO-01> | <DECIDIDO ou ASSUMIDO> | <opção vigente> | <por que e o que determina> |

## Handoff

vibe-spec
<!-- No MVP, acrescentar na linha seguinte: rota: max -->

- Chat: `init → interview → spec → design` pode continuar no mesmo chat. Recomende novo chat ao iniciar `vibe-plan`; se o humano preferir, a continuidade não bloqueia. Use este arquivo vivo como ponte.
