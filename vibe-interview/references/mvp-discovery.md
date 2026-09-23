# Núcleo da descoberta de MVP

Este arquivo orienta a entrevista de produto novo. Não é um questionário para copiar no chat.

## Núcleo, sempre

1. Entenda solicitação, público, problema, resultado esperado, critério de sucesso, limite e primeiro corte.
2. Descubra a forma do produto e a solução imaginada pelo usuário. Percorra as jornadas principais da entrada à conclusão, incluindo erro, estado vazio e retorno.
3. Para toda interface, identifique páginas/telas, objetivo de cada uma e como o usuário chega, avança e volta. Registre menu, links e CTA quando fizerem parte da solução. Uma página única pode dispensar menu, com decisão explícita.
4. Antes de encerrar, confira se a solução descrita permite realizar o objetivo central de ponta a ponta. Separe o que o usuário pediu dos fluxos de sustentação necessários para isso funcionar.

Pergunte em blocos pequenos, normalmente uma a três perguntas relacionadas. Não repita o que já foi respondido. Recomende e assuma lacunas reversíveis de baixo risco com motivo e impacto. Pergunte decisões caras, sensíveis, irreversíveis ou que alterem a lógica central. Não encerre com `PENDENTE CRÍTICO`.

## Módulos de completude

Depois que o núcleo estiver claro, selecione somente os módulos acionados pelo produto. Leia cada referência escolhida sob demanda; não faça uma rodada fixa de perguntas nem despeje os módulos no chat. Registre a evidência ou N/A fundamentado na Cobertura do MVP.

| Módulo | Abrir quando | Referência |
|---|---|---|
| Hospedagem e dados | Todo produto novo precisa ter destino de execução definido; aprofunde persistência quando houver dados dinâmicos | `modules/hosting-data.md` |
| Acesso e contas | Há área privada, usuários identificados ou ações reservadas | `modules/access.md` |
| Papéis e permissões | Existem capacidades diferentes entre pessoas ou organizações | `modules/roles.md` |
| Identidade e configurações | Há interface pública ou identidade do produto a definir | `modules/identity.md` |
| SEO e descoberta | Páginas públicas precisam ser encontradas ou compartilhadas | `modules/seo.md` |
| Planos e cobrança | Acesso ou recursos dependem de plano, pagamento ou teste | `modules/plans.md` |
| Elementos transversais de tela | Há interface com navegação, cabeçalho, rodapé ou medição | `modules/screen-shell.md` |

Integrações, uploads, notificações, importação, auditoria e requisitos legais entram quando uma jornada ou risco concreto os acionar. Investigue no contexto da jornada, sem criar módulos obrigatórios por precaução.

## Registro

Na Cobertura, use `DECIDIDO`, `ASSUMIDO`, `N/A` ou `PENDENTE CRÍTICO` com evidência. IDs estáveis por domínio ficam apenas para decisões que mudam arquitetura, acesso, dados, operação, custo, segurança ou escopo central. Detalhes cosméticos reversíveis não recebem ID.
