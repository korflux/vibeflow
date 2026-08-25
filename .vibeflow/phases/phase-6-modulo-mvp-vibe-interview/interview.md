# Módulo de descoberta para MVP de projeto

## Solicitação

Alterar o `vibe-interview` para tratar um MVP de projeto como uma descoberta própria, cobrindo fundação do produto, regras do projeto, repositório, stack, infraestrutura, identidade visual, telas, funcionamento, autenticação, usuários, primeiro usuário, roles e demais decisões necessárias.

## Hipótese inicial

```
HIPÓTESE: o interview precisa de uma rota interna para MVP greenfield, com cobertura obrigatória por domínio e perguntas condicionais, sem virar checklist fixo nem nova skill.
CONFIDENCE: ~75% — falta: fechar exatamente quando essa rota é ativada e quando o interview normal continua valendo.
```

## Trilha

### 1

Q: A rota completa deve ativar apenas para um produto novo ou também quando alguém chama uma feature de “MVP” dentro de um produto existente?
GUESS: Apenas para produto novo, repositório novo ou reconstrução integral. Uma feature experimental em produto existente usa o interview normal com lente de validação, porque stack, infraestrutura, marca e governança já deveriam vir do projeto.
R: O guess está correto. A rota completa vale para produto novo, repositório novo ou reconstrução integral.

### 2

Q: A pasta especial deve ser `.vibeflow/mvp/`, como fundação permanente do produto, ou `.vibeflow/phases/mvp/`, como uma fase especial dentro da cadeia?
GUESS: `.vibeflow/mvp/`. O conteúdo define decisões transversais que todas as fases futuras precisam consultar, como produto, stack, infraestrutura, identidade e acesso. Colocá-lo em `phases/` faria uma fundação permanente parecer apenas mais uma entrega cronológica. Dentro de `.vibeflow/mvp/`, eu manteria `interview.md`, `spec.md`, `plan.md`, `implement.md` e `review.md` conforme as portas executadas.
R: O guess está correto. A fundação permanente do produto fica em `.vibeflow/mvp/`.

### 3

Q: O handoff para a spec deve exigir uma resposta definitiva para todos os domínios ou aceitar decisões assumidas e itens conscientemente adiados?
GUESS: Usar quatro estados por domínio: `decidido`, `assumido pela recomendação`, `adiado com impacto registrado` e `não se aplica`. O handoff bloqueia apenas lacunas que alteram a aposta central, segurança, arquitetura base ou jornada principal. Detalhes reversíveis podem seguir com a recomendação da IA ou ficar adiados, evitando transformar a descoberta em interrogatório infinito.
R: O usuário pode não saber responder os domínios técnicos. A IA precisa auxiliar e fechar decisões suficientes para tornar possível iniciar o MVP, considerando que o público VibeCoding normalmente não domina implementação.

### 4

Q: Quando o usuário disser “não sei”, a IA pode assumir diretamente a recomendação ou deve pedir confirmação antes de registrá-la como decisão?
GUESS: A IA assume sem nova confirmação decisões técnicas reversíveis e registra como `assumido pela recomendação`. Pede confirmação apenas para decisões caras ou difíceis de reverter, identidade pública, risco de segurança, tratamento de dados, pagamentos e escolhas de negócio que somente o dono do produto pode fazer. Assim o usuário não precisa aprovar detalhes que delegou, mas mantém controle sobre consequências materiais.
R: A IA assume decisões de menor risco e informa a recomendação ao usuário. Explica benefícios e somente os contras críticos que possam mudar materialmente como o produto funcionará. Não é obrigatório criar contrapontos quando eles apenas aumentariam a dúvida sem alterar a decisão.

### 5

Q: Na entrevista do MVP, até que profundidade devemos mapear telas e dinâmica antes do handoff para a spec?
GUESS: O interview fecha o mapa funcional de cada tela necessária ao MVP: ator, objetivo, entrada, ações principais, dados exibidos, estados importantes e saída para a próxima etapa. Layout detalhado, componentes, textos finais e critérios de aceite ficam para spec e direção visual. Assim a arquitetura e a jornada deixam de ser chute sem transformar o interview em especificação de interface.
R: O interview deve extrair o máximo de informação que o usuário souber fornecer, inclusive detalhes de telas e dinâmica. A falta de resposta não bloqueia: a IA assume o necessário com recomendações para manter a entrevista fluida.

### 6

Q: Quando não existir identidade visual, o interview deve sair com uma fundação visual provisória já definida ou apenas registrar que ela precisa ser criada depois?
GUESS: Sair com uma fundação provisória: nome de trabalho, direção visual, fontes e tokens centrais de cor com contraste adequado. A IA informa a recomendação e assume quando o risco for baixo. Logo final, ilustrações e sistema completo de componentes ficam como trabalho posterior, mas o interview registra se já existem, onde estão e o que falta produzir.
R: A IA deve questionar o usuário e apresentar algumas opções, com preferências claras por minimalismo, interface limpa, modos dark ou light e fontes modernas.

### 7

Q: `Dark` e `light` devem ser alternativas para escolher um tema principal ou todo MVP deve nascer com os dois modos?
GUESS: Escolher um tema principal durante o interview. Suportar os dois somente quando o público, o contexto de uso ou um pedido explícito justificar, porque tema duplo aumenta tokens, estados, testes visuais e manutenção sem necessariamente validar melhor a aposta do MVP.
R: Um tema principal deve ser escolhido, mas é recomendável que o MVP tenha dark e light desde o começo.

### 8

Q: Para o primeiro administrador, podemos substituir “master no `.env`” por uma identidade de bootstrap segura, como e-mail permitido ou token de uso único, sem senha permanente no ambiente?
GUESS: Sim. O `.env` pode definir `BOOTSTRAP_ADMIN_EMAIL` ou um token temporário de alta entropia. Depois da primeira autenticação válida, o servidor atribui a role administrativa e consome ou desativa o bootstrap. Não existe senha master permanente nem superusuário oculto, reduzindo risco sem complicar a abertura do MVP.
R: A abordagem é aceitável, mas o usuário quer preservar uma opção master no `.env` porque VibeCoders podem perder o acesso e precisam de um ponto conhecido de recuperação.

### 9

Q: Podemos manter a recuperação no `.env` como modo `break-glass` temporário, em vez de uma senha master permanente?
GUESS: Sim. O ambiente guarda `BREAK_GLASS_ENABLED`, `BREAK_GLASS_ADMIN_EMAIL` e uma expiração. Quando necessário, o VibeCoder habilita e faz deploy; a autenticação normal comprova o e-mail, o servidor concede admin uma vez, audita e marca o resgate como consumido. O `.env` continua sendo o ponto operacional de recuperação sem criar uma credencial universal sempre ativa.
R: Aprovado. O padrão de recuperação usa modo `break-glass` temporário no `.env`.

### 10

Q: Na rota MVP, mantemos rigorosamente uma pergunta por mensagem ou permitimos pequenos blocos de decisões relacionadas?
GUESS: Permitir um bloco curto por domínio, com no máximo três perguntas relacionadas e recomendações ou suposições já visíveis. O usuário responde apenas o que souber; o restante é assumido pela IA. Decisões de alto risco continuam isoladas, uma por vez. Isso reduz rodadas sem voltar ao formulário longo e genérico.
R: Pequenos blocos são permitidos. A IA discerne a quantidade, com regra explícita para não exagerar nem assustar o usuário. O padrão é uma a três perguntas curtas e relacionadas; nunca mostrar o catálogo inteiro como formulário.

### 11

Q: Depois que o MVP for implementado, `.vibeflow/mvp/` deve continuar sendo editado como documentação atual ou preservar a fundação originalmente decidida?
GUESS: Preservar o MVP como baseline da criação do produto. Mudanças posteriores entram em fases normais e atualizam `.vibeflow/REGRAS.md`, que continua sendo a fonte viva da arquitetura e das regras atuais. As skills consultam o MVP para intenção, público, aposta e decisões de origem, mas conferem código e `REGRAS.md` para o estado técnico vigente. Assim não surgem duas fontes concorrentes.
R: O baseline pode ser preservado, mas é necessário mapear decisões críticas que desafiam ou modificam a lógica original. Cronologia simples não basta para decidir entre uma regra do MVP e outra de uma phase posterior.

### 12

Q: Podemos adotar substituição explícita por ID para decisões críticas, mantendo em `REGRAS.md` apenas a versão vigente?
GUESS: Sim. Cada decisão estrutural do MVP recebe um ID estável, por exemplo `MVP-AUTH-01`. Uma phase posterior precisa declarar `substitui: MVP-AUTH-01`, registrar regra anterior, regra nova, motivo e impacto. A mudança só atualiza a seção de decisões vigentes em `REGRAS.md` depois de implementada e aprovada na review. Conflito sem `substitui` é bloqueio, não desempate por cronologia.
R: O modelo resolve precedência, mas existe preocupação de inflar `REGRAS.md` com decisões e histórico.

### 13

Q: Podemos limitar `REGRAS.md` a uma tabela compacta de decisões transversais vigentes, deixando todo histórico e justificativa nos artefatos de origem?
GUESS: Sim. Cada linha contém apenas `ID`, decisão vigente em uma frase e `fonte`. O ID representa a dimensão, como `AUTH-01`, e não a versão. Quando uma phase aprovada substitui a decisão, atualiza a mesma linha e o path de origem. Decisões locais, detalhes de tela e histórico nunca entram nessa tabela.
R: Aprovado. `REGRAS.md` terá somente uma tabela compacta de decisões transversais vigentes; histórico e justificativa permanecem nos artefatos de origem.

### 14

Q: Next.js, Auth.js, Zod e PostgreSQL devem formar o baseline recomendado para aplicações web dinâmicas, com Astro para sites estáticos, Supabase quando o ganho operacional justificar e Redis apenas sob necessidade concreta?
GUESS: Sim, como baseline preferencial e não como stack obrigatória. A IA primeiro classifica produto, equipe, integrações, operação e deploy. Se não houver restrição que mude a escolha, recomenda esse baseline. Toda exceção precisa explicar qual necessidade torna a alternativa mais adequada.
R: O guess está correto. Supabase é especialmente recomendável para usuários que não sabem instalar PostgreSQL, não têm onde hospedá-lo ou precisam visualizar e administrar tabelas por uma interface mais acessível.

### 15

Q: Para um VibeCoder sem infraestrutura definida, podemos recomendar por padrão um caminho totalmente gerenciado, como GitHub para repositório, Vercel para a aplicação e Supabase para PostgreSQL, adaptando sites Astro para uma hospedagem estática adequada?
GUESS: Sim. O perfil gerenciado reduz instalação, deploy, certificados, backups básicos e operação cotidiana. Infraestrutura própria só é recomendada quando já existe capacidade operacional ou quando custo, controle, região, compliance ou dependência de plataforma mudarem materialmente a decisão. A recomendação sempre informa o contra crítico aplicável.
R: Aprovado, mas a IA deve perguntar antes se o usuário já possui infraestrutura, como VPS ou hospedagem em Hostinger, HostGator e similares. A capacidade precisa ser verificada pelo plano e pelos recursos disponíveis, não apenas pelo nome do provedor.

### 16

Q: Depois do interview em `.vibeflow/mvp/`, as próximas portas devem seguir a cadeia normal baseada em risco ou todo MVP deve obrigatoriamente percorrer a cadeia máxima?
GUESS: Manter roteamento por risco. Todo MVP exige pelo menos `interview`, `spec`, `plan`, `implement` e `review` na pasta especial. `analyze` entra quando houver autenticação, pagamentos, dados sensíveis, produção, perda de dados ou alto impacto, seguindo a rota `max`. Assim um site estático não recebe burocracia de sistema crítico, mas um SaaS com usuários não pula análise de risco.
R: Todo MVP percorre obrigatoriamente a rota `max`: interview, spec, plan, analyze, implement e review.

### 17

Q: Se `.vibeflow/mvp/` já existir e estiver concluído, uma reconstrução integral deve criar outro MVP especial ou entrar como phase `max` que substitui explicitamente decisões do baseline?
GUESS: Entrar como phase `max`. Existe apenas um baseline MVP por repositório. Reconstruções, pivôs e versões seguintes preservam o histórico e declaram substituições pelos IDs críticos. Um novo `.vibeflow/mvp/` só existe em repositório novo; nunca sobrescrevemos nem versionamos a pasta original.
R: O guess está correto. Existe um único baseline em `.vibeflow/mvp/`; reconstruções e pivôs posteriores usam phase `max`.

### 18

Q: Podemos usar estes domínios como mapa interno de cobertura, sempre inspecionados, mas perguntados somente quando houver lacuna relevante?
GUESS: Sim. O catálogo cobre: fundação do produto e sucesso; público e atores; escopo, jornadas, telas e estados; acesso, usuários, roles, tenancy e recuperação; dados, arquivos, integrações e notificações; marca, identidade, responsividade e acessibilidade; repositório, stack, infraestrutura, deploy e ambientes; segurança, privacidade, analytics, backup, suporte e operação; modelo comercial, pagamentos e obrigações legais quando aplicáveis; corte do MVP, operações manuais aceitáveis, fora e riscos. Ramos como SEO, localização, painel administrativo e conteúdo entram por gatilho, não por padrão.
R: Aprovado. Esses domínios formam o mapa interno de cobertura da rota MVP.

## Resultado

Entendi assim:

- O quê: adicionar ao `vibe-interview` uma rota adaptativa para descobrir e estruturar MVPs de projetos novos.
- Pra quem: VibeCoders que conhecem a ideia do produto, mas podem não dominar decisões técnicas, visuais ou operacionais.
- Por quê: o interview atual trata um projeto novo como feature e deixa decisões fundamentais para serem descobertas durante a implementação.
- Sucesso: a IA extrai o máximo disponível, recomenda e assume lacunas de baixo risco, registra decisões e entrega base suficiente para a rota `max`.
- Limite: existe um único `.vibeflow/mvp/` por repositório; reconstruções posteriores usam phase `max` e substituição explícita.
- Fora: formulário extenso, stack universal, senha master permanente, sobrescrita do baseline e histórico acumulado em `REGRAS.md`.

## Direção

### Ativação e disco

- Ativa automaticamente para produto ou repositório novo. Feature experimental em produto existente continua no interview normal.
- Grava `interview.md` em `.vibeflow/mvp/`, sem `phase-N-slug`.
- Todo MVP percorre `interview`, `spec`, `plan`, `analyze`, `implement` e `review` na pasta especial.
- Se o MVP já estiver concluído, pivôs e reconstruções entram em phase `max`; o baseline nunca é sobrescrito.

### Conversa e recomendações

- A IA inspeciona contexto e ativos antes de perguntar e nunca mostra o catálogo completo.
- Usa blocos pequenos de perguntas relacionadas, normalmente uma a três. Decisões sensíveis ficam isoladas.
- Extrai toda informação que o usuário souber, aceita respostas parciais e assume lacunas reversíveis.
- Cada recomendação informa escolha, motivo, impacto e somente contraindicação crítica que possa mudar a decisão.
- Domínios usam `decidido`, `assumido pela recomendação`, `adiado com impacto registrado` ou `não se aplica`.
- Só bloqueiam o handoff lacunas de negócio que a IA não pode inferir ou decisões materiais sem delegação.

### Cobertura

- Fundação, público, dor, aposta, sucesso, escopo, jornadas, telas, ações e estados.
- Usuários, autenticação, cadastro, roles, tenancy, recuperação e primeiro administrador.
- Dados, arquivos, integrações, notificações, segurança, privacidade e obrigações aplicáveis.
- Marca, logo existente, direção visual, fontes modernas, tokens semânticos, acessibilidade, light e dark com um tema principal.
- Repositório, stack, infraestrutura existente, deploy, ambientes, analytics, backup, suporte e operação.
- Modelo comercial, pagamentos, SEO, localização, administração e conteúdo somente quando acionados pelo produto.
- Corte do MVP, trabalho manual aceitável, fora, riscos e hipótese central validada.

### Baselines recomendados

- Aplicação web dinâmica: Next.js, Auth.js quando adequado, Zod e PostgreSQL.
- Site predominantemente estático: Astro.
- Supabase quando o usuário não opera PostgreSQL, não possui infraestrutura ou precisa de administração visual; recursos adicionais entram por necessidade.
- Redis somente quando cache, sessão, rate limit, fila ou coordenação justificarem.
- Sem infraestrutura adequada: GitHub, Vercel e Supabase como caminho gerenciado inicial.
- Infra existente: perguntar provedor, plano, SSH, Docker, runtime, banco, domínio, DNS e e-mail antes de recomendar reaproveitamento.

### Acesso emergencial e precedência

- Recuperação administrativa por modo `break-glass` temporário no `.env`, com e-mail, habilitação, expiração, uso único e auditoria, sem senha master permanente.
- Decisões transversais recebem IDs estáveis, como `AUTH-01`.
- `REGRAS.md` mantém somente `ID`, decisão vigente e fonte. Histórico e justificativa ficam no MVP e na phase que substituiu a decisão.
- Phase posterior só muda decisão crítica ao declarar substituição; conflito sem substituição explícita bloqueia a execução.

## Handoff

vibe-spec
