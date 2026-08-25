# Spec: rota MVP no vibe-interview
# Pasta: phase-6-modulo-mvp-vibe-interview
# Status: aprovado

## Objetivo

Adicionar ao `vibe-interview` uma rota própria para descobrir projetos MVP completos, destinada a VibeCoders que podem não dominar decisões técnicas, visuais ou operacionais. A IA pilota a descoberta, inspeciona o contexto, pergunta em blocos pequenos, recomenda soluções e assume lacunas reversíveis. O resultado inicia uma cadeia `max` em `.vibeflow/mvp/`, sem quebrar o fluxo existente em `.vibeflow/phases/`.

## Inventário

1. `vibe-interview` hoje grava somente em `.vibeflow/phases/phase-N-slug/interview.md` e exige uma pergunta por vez.
2. Os motores de `spec`, `plan`, `analyze`, `implement` e `review` validam exclusivamente pastas `phase-N-slug`; gravar apenas o interview em `.vibeflow/mvp/` quebraria o primeiro handoff.
3. `docs/ESCOPO.md` e `.vibeflow/REGRAS.md` proíbem artefatos fora de `phases/`; o novo alvo exige exceção contratual explícita.
4. Scripts Python e PowerShell são motores gêmeos; launchers Unix apenas encaminham flags para um motor completo.
5. O template atual registra Solicitação, Hipótese, Trilha, Resultado, Direção e Handoff, mas não possui cobertura por domínio nem decisões críticas.

## Suposições e decisões

1. Existe no máximo um `.vibeflow/mvp/` por repositório. (disco)
2. Produto novo sem baseline pode ativar a rota MVP; feature experimental em produto existente usa phase normal. (produto)
3. Se `.vibeflow/mvp/` já estiver concluído, pivô ou reconstrução usa phase `max` e não sobrescreve o baseline. (preservação)
4. A IA seleciona o modo; scripts recebem `--mvp` ou `-Mvp` e não inferem intenção. (arquitetura)
5. Todo MVP percorre `interview`, `spec`, `plan`, `analyze`, `implement` e `review` na pasta especial. (processo)
6. O modo phase atual permanece compatível e com o mesmo comportamento. (compatibilidade)
7. A review humana aprovada sincroniza em `REGRAS.md` somente decisões críticas vigentes; histórico permanece nos artefatos. (governança)

## Escopo e comportamento

### 1. Detecção e conversa do `vibe-interview`

- A skill detecta candidato a MVP por pedido explícito de produto novo, repositório novo ou contexto greenfield.
- Se houver dúvida entre projeto novo e feature, faz uma pergunta curta antes de escolher o modo.
- Antes de perguntar, lê `REGRAS.md`, o motor que executará e evidências relevantes do projeto, incluindo manifests, README e assets citados ou encontrados por busca dirigida.
- No modo normal, mantém uma pergunta por vez. No modo MVP, usa blocos pequenos, normalmente com uma a três perguntas relacionadas; nunca despeja o catálogo completo.
- Extrai tudo que o usuário souber, aceita resposta parcial e registra cada domínio como `decidido`, `assumido pela recomendação`, `adiado com impacto registrado` ou `não se aplica`.
- Decisão reversível delegada é assumida após informar recomendação, motivo, impacto e somente contraindicação crítica aplicável.
- Identidade pública, custo material, pagamento, dado sensível, segurança e decisão exclusiva de negócio exigem confirmação explícita.
- Handoff só bloqueia quando faltar decisão material que a IA não possa inferir ou que não tenha sido delegada.

### 2. Catálogo interno de MVP

- Criar `vibe-interview/references/mvp-discovery.md` como árvore condicional, não roteiro linear.
- Cobrir produto, público, dor, aposta, sucesso, escopo, jornadas, telas, estados, usuários, autenticação, cadastro, roles, tenancy, recuperação, dados, arquivos, integrações, notificações, marca, identidade, acessibilidade, repositório, stack, infraestrutura, deploy, ambientes, segurança, privacidade, analytics, backup, suporte, operação, corte e riscos.
- Ativar por gatilho os ramos de pagamentos, modelo comercial, SEO, localização, painel administrativo, conteúdo e obrigações legais.
- Para telas, capturar toda informação fornecida; quando faltar, fechar ator, objetivo, entrada, ações, dados, estados e saída suficientes para a spec.
- Para visual, perguntar por nome, logo e ativos existentes; oferecer poucas direções minimalistas, limpas e com fontes modernas; escolher um tema principal e prever tokens semânticos para light e dark desde o início.

### 3. Recomendações técnicas e de infraestrutura

- Baseline preferencial para aplicação web dinâmica: Next.js, Auth.js quando adequado, Zod e PostgreSQL.
- Site predominantemente estático: Astro.
- Supabase é recomendado quando o usuário não opera PostgreSQL, não possui infraestrutura ou precisa de administração visual; Auth, Storage e Realtime entram apenas quando necessários.
- Redis entra somente com necessidade concreta de cache, sessão, rate limit, fila ou coordenação.
- Sem infraestrutura adequada, recomendar GitHub, Vercel e Supabase como caminho gerenciado inicial.
- Antes de reaproveitar Hostinger, HostGator, VPS ou similar, perguntar provedor, plano, SSH, Docker, runtime, banco, domínio, DNS e e-mail, e verificar compatibilidade com a stack.
- Recomendações são preferência contextual, nunca dependência obrigatória nem justificativa para instalar tecnologia sem necessidade.

### 4. Acesso e recuperação administrativa

- A descoberta sempre classifica se o produto é público, sem conta, auto cadastro, convite ou acesso restrito.
- Quando houver usuários, fecha identidade, verificação, recuperação, ciclo do usuário, primeiro administrador, roles, permissões e tenancy quando aplicável.
- Recuperação administrativa recomendada usa modo `break-glass` temporário no ambiente, com habilitação explícita, e-mail, expiração, uso único e auditoria.
- Não recomendar senha master permanente, superusuário oculto ou credencial enviada ao navegador.

### 5. Contrato de disco e scripts

- `interview`, `spec`, `plan`, `analyze`, `implement` e `review` recebem flag pública `--mvp` no Python/launcher e `-Mvp` no PowerShell.
- Sem `--mvp`, todos preservam o fluxo atual em `phase-N-slug`.
- Com `--mvp`, inventário e apply usam `.vibeflow/mvp/<artefato>.md`; slug, `next_n` e criação de phase não participam.
- O script não detecta se o pedido é MVP. Apenas classifica o alvo especial, valida predecessores, promove wip com tamanho e SHA-256 e relata o disco.
- Relatórios acrescentam alvo MVP de forma aditiva, distinguindo `kind: mvp` de `kind: phase`, sem remover campos atuais.
- `interview --mvp --apply` recusa sobrescrever `mvp/interview.md`; continuação edita o vivo diretamente.
- Cada porta MVP recusa predecessor ausente e avanço fora da ordem máxima. `implement --mvp` exige `analyze.md` limpo e aprovado.
- Launchers preservam fallback integral e encaminham a nova flag aos dois motores.

### 6. Artefato e decisões críticas

- Estender o template único de interview com seções opcionais de `Cobertura do MVP`, `Mapa do produto`, `Direção técnica`, `Direção visual`, `Operação` e `Decisões críticas`; omitir no modo normal.
- Decisão transversal recebe ID por dimensão, como `AUTH-01`, sem prefixo de versão.
- Artefatos posteriores podem declarar `mantém`, `cria` ou `substitui` para cada ID, registrando regra anterior, nova regra, motivo e impacto.
- Conflito entre baseline e phase sem substituição explícita bloqueia analyze ou review; cronologia não resolve conflito.
- `REGRAS.md` mantém tabela compacta com `ID`, decisão vigente e fonte. Histórico e justificativa nunca são copiados para essa tabela.
- A tabela só é criada ou atualizada quando a review vigente estiver aprovada pelo humano. Review recusada ou ainda rascunho não muda a fonte viva.
- Depois da aprovação humana, a IA aplica patch mínimo na tabela de `REGRAS.md`, preservando todo conteúdo alheio. O script de review não edita regras e não recebe flag de sincronização.

### 7. Documentação e contrato do repositório

- Atualizar `.vibeflow/REGRAS.md`, `docs/ESCOPO.md`, arquiteturas, análises e `SKILL.md` das portas afetadas para reconhecer `.vibeflow/mvp/` como exceção única.
- Atualizar o template de `REGRAS.md` do init com a seção compacta opcional de decisões críticas, preservando as mudanças locais já existentes no `vibe-init`.
- Documentar que MVP é baseline histórico; código e `REGRAS.md` representam o estado técnico vigente.
- README recebe somente a indicação necessária da nova rota, sem tutorial duplicado.

### Fora

- Implementar um MVP de aplicação neste repositório. Este trabalho altera apenas a cadeia de skills.
- Criar uma nova skill `vibe-mvp`. A rota pertence ao `vibe-interview` e reutiliza as portas existentes.
- Tornar Next.js, Supabase, Vercel ou qualquer fornecedor obrigatório.
- Exibir todo o catálogo de perguntas ao usuário.
- Versionar `.vibeflow/mvp-v2/`, mover ou sobrescrever um baseline concluído.
- Armazenar histórico completo de decisões em `REGRAS.md`.

## Checklist de entrega

### Aceite

- [ ] A1: pedido de produto novo ativa pela IA o modo MVP; feature em produto existente permanece no modo phase.
- [ ] A2: o interview MVP conduz blocos curtos, recomenda e assume lacunas reversíveis sem esconder decisões críticas.
- [ ] A3: `.vibeflow/mvp/interview.md` é promovido com cópia verificada e nunca sobrescrito.
- [ ] A4: spec, plan, analyze, implement e review percorrem o mesmo `.vibeflow/mvp/` na ordem máxima.
- [ ] A5: o fluxo normal `phase-N-slug` continua passando nos contratos existentes.
- [ ] A6: catálogo condicional cobre todos os domínios aprovados sem virar questionário exibido integralmente.
- [ ] A7: visual prevê tema principal e tokens light/dark; infraestrutura e stack seguem recomendação contextual.
- [ ] A8: recuperação administrativa recomendada é `break-glass` temporária e auditável, sem senha master permanente.
- [ ] A9: decisões críticas usam IDs e substituição explícita; conflito implícito não é resolvido por cronologia.
- [ ] A10: após review aprovada pelo humano, a IA atualiza em `REGRAS.md` somente decisões vigentes; os motores nunca editam regras.
- [ ] A11: Python, PowerShell e launcher Unix possuem paridade no modo MVP.
- [ ] A12: documentação canônica e limites do repositório reconhecem a exceção `.vibeflow/mvp/`.

### Critérios de sucesso

- [ ] C1: suítes existentes continuam verdes sem alteração do comportamento phase.
- [ ] C2: testes isolados provam criação única do MVP, ordem das seis portas, recusa de sobrescrita e preservação de wip em falha.
- [ ] C3: paridade essencial confirma o mesmo path e bytes nos motores Python e PowerShell.
- [ ] C4: um teste de ponta a ponta promove os seis artefatos em `.vibeflow/mvp/` sem criar `phase-N`.
- [ ] C5: buscas contratuais não encontram instrução universal `Script primeiro` nas skills alteradas.
- [ ] C6: `git diff --check`, suítes Python, launchers e gitleaks passam no escopo disponível.

## Implementação

### Stack

| Área | Escolha |
|---|---|
| Scripts | Python 3 e PowerShell 7 existentes, launchers Bash existentes |
| Testes | `unittest` e asserts PowerShell existentes |
| Dependências novas | Nenhuma |

### Estrutura tocada

```text
.vibeflow/REGRAS.md                         # exceção MVP e decisões vigentes
docs/ESCOPO.md                              # contrato de path atualizado
vibe-interview/                             # detecção, catálogo, template e motores MVP
vibe-{spec,plan,analyze,implement,review}/  # alvo --mvp nas portas seguintes
docs/vibe-*/                                # arquitetura, análise e testes de contrato
vibe-init/templates/REGRAS.md               # seção compacta de decisões críticas
README.md                                   # indicação da rota MVP
```

### Estilo e padrões

- Reutilizar promoção binária, tamanho, SHA-256, relatórios e erros curtos já existentes.
- Funções novas ou alteradas mantêm comentários semânticos sobre papel e decisão não óbvia.
- Preservar mudanças locais do usuário em `vibe-init/`; integrar somente os trechos necessários, sem restaurar versões anteriores.

### Contratos e módulos

- Flag pública aditiva: `--mvp` / `-Mvp`.
- Alvo especial fixo: `.vibeflow/mvp/`.
- Ordem fixa: `interview`, `spec`, `plan`, `analyze`, `implement`, `review`.
- Modo phase permanece default e retrocompatível.

## Como provar

### Seams

- Detecção semântica pela IA contra execução determinística do script.
- Seleção MVP contra seleção automática de phase já existente.
- Review aprovada contra sincronização prematura de decisões.
- Novo alvo contra preservação integral do fluxo normal.

### Estratégia

- RED/GREEN por motor Python em cada porta afetada.
- Paridade PowerShell para inventário e apply essencial.
- Teste integrado da cadeia MVP completa em diretório temporário.
- Regressão das sete suítes canônicas e launchers Unix.
- Inspeção de docs, templates, relatórios e mensagens de erro.

### Comandos

```bash
python docs/vibe-interview/tests/test-interview.py -v
python docs/vibe-spec/tests/test-spec.py -v
python docs/vibe-plan/tests/test-plan.py -v
python docs/vibe-analyze/tests/test-analyze.py -v
python docs/vibe-implement/tests/test-implement.py -v
python docs/vibe-review/tests/test-review.py -v
python docs/tests/test-distribuicao.py -v
bash docs/vibe-interview/tests/test-interview.sh
git diff --check
```

## Boundaries

### Always

- Preservar o modo phase e as mudanças locais do usuário.
- Auditar o disco depois de cada promoção.
- Manter decisões de alto risco sob confirmação humana.

### Ask first

- Alterar um path público além da exceção `.vibeflow/mvp/`.
- Remover campo existente de relatório ou flag pública.
- Introduzir dependência ou fornecedor obrigatório.

### Never

- Sobrescrever `.vibeflow/mvp/` concluído.
- Fazer o script decidir semanticamente se um pedido é MVP.
- Publicar decisão em `REGRAS.md` antes de review aprovada.
- Criar senha master permanente ou enviar segredo ao navegador.

## Handoff

vibe-plan

- [x] Aprovação humana (leu o arquivo e confirmou)
