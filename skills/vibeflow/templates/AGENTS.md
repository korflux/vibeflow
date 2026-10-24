# Regras do projeto

> VibeFlow: documentos e edição apenas de texto ficam fora da cadeia da skill única `vibeflow`, que trata código de software. Um briefing ambíguo de documento pode passar antes pelas perguntas da interview.

<!-- VIBEFLOW:CADEIA start -->
A cadeia da skill `vibeflow` vale só quando o humano a chama com `/vibeflow` (`$vibeflow` no Codex). Fora disso, o agente trabalha direto pelas demais regras deste arquivo, sem rota, phase nem artefato.

| esforço | etapas | quando |
|---|---|---|
| low | implement, sem init, `.vibeflow/`, phase nem artefato | mudança clara e localizada de código de software sem comportamento novo, como cor, texto ou layout de página estática |
| medium | implement → review | pedido claro e direto, com comportamento novo pequeno, sem banco nem risco de regressão de backend, ou página visual cujo aceite dependa de validação renderizada |
| high | interview → spec → plan → analyze → implement com checkpoints → review | pedido ambíguo ou de execução difícil, mudança que altera banco ou painel admin, risco de regressão de backend, ou tela que o design system e as telas existentes não cobrem |

Saem do low, seguindo a rota aplicável: comportamento, rota, interação, critério de aceite ou acessibilidade alterados, e mudanças que toquem privacidade, dado pessoal, consentimento, retenção, direitos, obrigação jurídica, autenticação, autorização, pagamento, segredo, persistência ou risco de perda de dados.

Na high, a linha `# Risco:` da spec marca mudança que toca autenticação, autorização, pagamento, segredo, perda de dados ou produção. O risco não acrescenta etapa: a interview cobre modelo de ameaça e rollback, o plan põe checkpoint depois de cada grupo de risco e a review abre segurança e banco. Produto de software novo com escopo a descobrir é o MVP: rota high com risco, em `.vibeflow/mvp/`.

A interview tem tamanho proporcional à clareza do pedido e grava direto a `spec.md`. A aprovação da `spec.md` é a única aprovação humana antes do código e encadeia plan, analyze, implement e review até a confirmação final. Aprovar a review, publicar decisões vigentes e fazer push exigem confirmação humana explícita. Ajuste low ou medium ao que uma phase entregou ou está entregando, inclusive registro de `.erros-encontrados/`, volta à phase de origem, mesmo fechada, sem abrir phase nova. Medium abre a phase na review.

`/vibeflow` conduz todo o fluxo. `/vibeflow <etapa>` vai direto a `init`, `interview`, `spec`, `plan`, `analyze`, `implement` ou `review`, desde que o pré-requisito esteja satisfeito. Argumento cuja primeira palavra não é etapa é tratado como pedido e classificado. O init roda na primeira rota com phase do repo, ou de novo só para reparar o disco.

### Continuidade entre chats

Um único chat conduz a phase por padrão. Em host de contexto curto, use dois: um para o planejamento (interview, spec, plan e analyze) e outro para a implementação (implement e review). Quando o contexto pesar ou o humano pedir para parar, o estado é gravado conforme a seção 6 do `SKILL.md` e o líder recomenda um chat novo. A retomada parte do disco: em chat novo, `/vibeflow` lê as linhas `# Rota:`, `# Risco:` e `# Status:`, as caixas de passos e checkpoints e a seção de achados do analyze do `plan.md`, os R* do `review.md` e o Git, e segue de onde parou. Sem subagentes (Modo B), analyze, checkpoint e review pedem chat novo (`/vibeflow analyze`, `/vibeflow implement`, `/vibeflow review`). Separar chats é recomendação, nunca gate.
<!-- VIBEFLOW:CADEIA end -->

## Projeto
<!-- SLOT:paragrafo -->
<!-- evidência: <path ou vazio> -->

## Comandos do projeto
<!-- SLOT:comandos -->
<!-- Registrar só comandos existentes, cada um com onde roda (local, CI ou host): instalar, executar, lintar, validar tipos, teste por recorte (arquivo, módulo ou filtro), suíte completa, E2E, varredura de segredos e CI obrigatório. Com orçamento declarado, registrar a linha `Orçamento da regressão completa: <minutos>`; sem declaração, não registrar a linha, e vale o padrão de `references/testes.md` da skill `vibeflow`. -->

## Ambiente
<!-- SLOT:ambiente -->
<!-- homolog | producao -->
<!-- Serviços de teste locais: <serviço>: <nativo | embutido | Docker> -->
<!-- Docker nos testes: <decisão do humano>, decidido em <AAAA-MM-DD> -->

## Versão (semver)
- **Major:** quebra contrato (API, schema, comportamento que caller já usa).
- **Minor:** adiciona sem quebrar.
- **Patch:** correção sem mudança de contrato.
- Produção: migration só com plano de rollback; não rodar migration destrutiva sem o humano pedir.

## Git
- Sem `Co-Authored-By` de ferramenta em commit ou push.
- Staging somente de paths autorizados. Proibidos `git add -A`, `git add .`, amend, squash e force push.
- Papéis, passos, checkpoints, provas, formatos de commit e finalização seguem a skill `vibeflow`; este arquivo não os repete.
- Aprovar a review, publicar decisões vigentes e fazer push exigem confirmação humana final explícita.

## Padrões de Código e Engenharia
- **Comentários Semânticos Obrigatórios:** Toda função, componente ou módulo deve ter comentário explicando o que faz, para que serve e a justificativa de decisões não óbvias. Zero funções órfãs.
- **Desenvolvimento Eficiente (YAGNI):** O melhor código é o mínimo necessário. Antes de escrever código novo, reutilizar o que já existe no projeto, na standard library ou recursos nativos da plataforma. Não criar abstrações para necessidades especulativas futuras.
- **Causa Raiz:** Correção de bugs deve atuar na causa raiz e não no sintoma. Se o problema estiver em função compartilhada, corrigir no ponto de origem.
- **Limitações Conhecidas:** Registrar limitações de soluções simplificadas com `ponytail: <limitação>, <quando será necessário melhorar>`.
- **Erros Fora do Escopo:** Erro encontrado fora do recorte da tarefa nunca é corrigido por quem o encontrou nem ignorado em silêncio, e não bloqueia a entrega. Quem tem escrita autorizada em `.erros-encontrados/` o registra lá, um arquivo por erro; quem não tem o relata ao líder, ou ao humano quando não houver líder. Teste que falha e passa na reexecução segue a mesma regra. A correção do registro segue a skill `vibeflow`.
- **Comunicação:** Ao explicar código, priorizar o que está acontecendo, o porquê e o impacto arquitetural, sem exigir domínio de sintaxe da linguagem.

## Segurança por Padrão
- **Entradas Não Confiáveis:** Toda informação recebida de fora (request, query, headers, forms) deve ser validada na borda com allowlist e limite de tamanho. SQL sempre parametrizado.
- **Credenciais e Segredos:** Chaves, tokens e segredos nunca ficam no código ou repositório. Usar variáveis de ambiente (`.env`).
- **Autorização no Servidor:** Toda ação sensível deve validar permissões no servidor (proteção anti-IDOR).
- **Tratamento de Erros na Borda:** Respostas externas (APIs, webhooks, CLIs) devem retornar envelope padronizado com código estável em maiúsculas (`code`), mensagem segura (`message`) e status HTTP/CLI. Não expor stack traces, queries ou dados internos do banco.
- **Erros no Núcleo Interno:** Lógica interna e serviços devem lançar exceções de domínio tipadas. A conversão da exceção para o código público de erro é responsabilidade exclusiva do middleware/handler central na borda.

## Estrutura
<!-- SLOT:estrutura -->

## Fluxos e invariantes
<!-- SLOT:fluxos -->
<!-- Onde entram dados, permissões e persistência; registrar só o que o projeto comprova. -->

## Regras deste repo
<!-- SLOT:regras -->
