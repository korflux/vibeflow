# Núcleo da descoberta de MVP

Este arquivo orienta a entrevista de produto novo. Não é um questionário para copiar no chat.

## Núcleo, sempre

1. Entenda solicitação, público, problema, resultado esperado, critério de sucesso, limite e primeiro corte.
2. Descubra a forma do produto e a solução imaginada pelo usuário. Percorra as jornadas principais da entrada à conclusão, incluindo erro, estado vazio e retorno.
3. Para toda interface, identifique páginas/telas, objetivo de cada uma e como o usuário chega, avança e volta. Registre menu, links e CTA quando fizerem parte da solução. Uma página única pode dispensar menu, com decisão explícita.
4. Antes de encerrar, confira se a solução descrita permite realizar o objetivo central de ponta a ponta. Separe o que o usuário pediu dos fluxos de sustentação necessários para isso funcionar.

Faça uma pergunta principal por turno, no formato de `references/interview.md`. Não repita o que já foi respondido. Recomende e assuma lacunas reversíveis de baixo risco com motivo e impacto. Pergunte decisões caras, sensíveis, irreversíveis ou que alterem a lógica central, sem tratar recomendação como decisão. Não encerre com decisão pendente.

## Módulos de completude

Depois que o núcleo estiver claro, selecione somente os módulos acionados pelo produto. Leia cada referência escolhida sob demanda; não faça uma rodada fixa de perguntas nem despeje os módulos no chat. Cada módulo acionado entra nas Decisões da `spec.md` ou em Fora do escopo, com evidência ou N/A fundamentado.

| Módulo | Abrir quando | Referência |
|---|---|---|
| Hospedagem e dados | Todo produto novo precisa ter destino de execução definido; aprofunde persistência quando houver dados dinâmicos | `references/interview/modules/hosting-data.md` |
| Acesso e contas | Há área privada, usuários identificados ou ações reservadas | `references/interview/modules/access.md` |
| Papéis e permissões | Existem capacidades diferentes entre pessoas ou organizações | `references/interview/modules/roles.md` |
| Identidade e configurações | Há interface pública ou identidade do produto a definir | `references/interview/modules/identity.md` |
| SEO e descoberta | Páginas públicas precisam ser encontradas ou compartilhadas | `references/interview/modules/seo.md` |
| Planos e cobrança | Acesso ou recursos dependem de plano, pagamento ou teste | `references/interview/modules/plans.md` |
| Elementos transversais de tela | Há interface com navegação, cabeçalho, rodapé ou medição | `references/interview/modules/screen-shell.md` |

Use estes gatilhos para não deixar privacidade e requisitos legais implícitos:

| Tema | Abrir quando | Fechar na descoberta |
|---|---|---|
| Privacidade | O produto recebe ou processa dados pessoais ou sensíveis, monitora comportamento, ou compartilha dados com terceiros, mesmo sem persistência própria | Categorias de dados, finalidade, quem acessa ou recebe, telemetria/terceiros e retenção ou exclusão quando aplicável |
| Jurídico | O setor é regulado, envolve menores, ou uma jornada depende de consentimento, contrato, cobrança, licença de conteúdo ou obrigação legal citada | Obrigação confirmada, responsável por validá-la e dependência explícita quando ainda não confirmada; não invente interpretação jurídica |

Investigue integrações, uploads, notificações, importação e auditoria quando uma jornada ou risco concreto os acionar. Mantenha a descoberta no contexto da jornada, sem criar perguntas obrigatórias por precaução.

## Registro

Na `spec.md`, decisão que o humano não fechou diz `assumida`, e nenhuma fica pendente. IDs estáveis por domínio ficam apenas para decisões que mudam arquitetura, acesso, dados, operação, custo, segurança ou escopo central. Detalhes cosméticos reversíveis não recebem ID.
