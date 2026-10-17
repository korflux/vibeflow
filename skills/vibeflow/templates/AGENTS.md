# Regras do projeto

> VibeFlow: documentos e edição apenas de texto ficam fora das etapas spec, design, plan, analyze, implement e review da skill única `vibeflow`. Essas etapas tratam código de software. A etapa interview pode esclarecer um briefing ambíguo de documento.

<!-- VIBEFLOW:CADEIA start -->
| esforço | fluxo | quando |
|---|---|---|
| N/A | init | primeira vez no repo, ou disco quebrado, de novo só para reparar |
| low | implement | mudança simples de código de software sem comportamento novo, como cor, texto ou layout de página estática |
| Express | implement, sem phase nem artefato | low sem phase de origem: mudança clara e localizada sem comportamento novo |
| medium | implement → review | pedido claro e direto, com comportamento novo pequeno e sem regressão de backend, ou página visual cujo aceite dependa de validação renderizada |
| high | spec → plan → implement → review | pedido claro de execução difícil, ou mudança que altera banco, painel admin ou cria risco de regressão de backend |
| xhigh | interview → spec → plan → implement → review | pedido ambíguo, confiança baixa, intenção ou sucesso de software em aberto |
| max | interview → spec → plan → analyze → implement → review | mudança que altera autenticação, autorização, pagamento, segredo, risco de perda de dados, produção, alto blast radius ou baseline MVP de software |

No Express, o implementador entrega com prova proporcional, sem init, `.vibeflow/`, phase nem artefato. Saem do Express, seguindo a rota aplicável: comportamento, rota, interação, critério de aceite ou acessibilidade alterados, e mudanças que toquem privacidade, dado pessoal, consentimento, retenção, direitos, obrigação jurídica, autenticação, autorização, pagamento, segredo, persistência ou risco de perda de dados. Ajuste low ou medium ao que uma phase entregou ou está entregando, inclusive registro de `.erros-encontrados/`, volta à phase de origem, mesmo fechada, sem abrir phase nova. Medium segue implement → review e abre a phase na review.

`/vibeflow` conduz todo o fluxo. `/vibeflow <etapa>` vai direto a `init`, `interview`, `spec`, `design`, `plan`, `analyze`, `implement` ou `review`, desde que o pré-requisito esteja satisfeito. Argumento cuja primeira palavra não é etapa é tratado como pedido e classificado. O design entra entre spec e plan somente com UI nova: tela ou decisão visual que o design system e as telas existentes não cobrem.

### Continuidade entre chats

Um único chat conduz a phase por padrão. Em host de contexto curto, use dois: um para todo o planejamento (interview, spec, design, plan e analyze) e outro para a implementação (implement e review). Quando o contexto pesar ou o humano pedir para parar, o estado é gravado conforme a seção 6 do `SKILL.md` e o líder recomenda um chat novo. A retomada parte do disco: em chat novo, `/vibeflow` lê as linhas `# Status:`, as caixas e as linhas `Estado:` do `plan.md` e o Git e segue de onde parou. Sem subagentes, analyze e review pedem chat novo (`/vibeflow analyze`, `/vibeflow review`). Separar chats é recomendação, nunca gate.
<!-- VIBEFLOW:CADEIA end -->

## Projeto
<!-- SLOT:paragrafo -->
<!-- evidência: <path ou vazio> -->

## Comandos do projeto
<!-- SLOT:comandos -->
<!-- Registrar só comandos existentes, cada um com onde roda (local, CI ou host): instalar, executar, lintar, validar tipos, teste por recorte (arquivo, módulo ou filtro), suíte completa, E2E, varredura de segredos e CI obrigatório. -->

## Ambiente
<!-- SLOT:ambiente -->
<!-- homolog | producao -->

## Versão (semver)
- **Major:** quebra contrato (API, schema, comportamento que caller já usa).
- **Minor:** adiciona sem quebrar.
- **Patch:** correção sem mudança de contrato.
- Produção: migration só com plano de rollback; não rodar migration destrutiva sem o humano pedir.

## Git
- Sem `Co-Authored-By` de ferramenta em commit ou push.
- Staging somente de paths autorizados. Proibidos `git add -A`, `git add .`, amend, squash e force push.
- Papéis, ondas, provas, formatos de commit e finalização seguem a skill `vibeflow`; este arquivo não os repete.
- Aprovar a review, publicar decisões vigentes e fazer push exigem confirmação humana final explícita.

## Padrões de Código e Engenharia
- **Comentários Semânticos Obrigatórios:** Toda função, componente ou módulo deve ter comentário explicando o que faz, para que serve e a justificativa de decisões não óbvias. Zero funções órfãs.
- **Desenvolvimento Eficiente (YAGNI):** O melhor código é o mínimo necessário. Antes de escrever código novo, reutilizar o que já existe no projeto, na standard library ou recursos nativos da plataforma. Não criar abstrações para necessidades especulativas futuras.
- **Causa Raiz:** Correção de bugs deve atuar na causa raiz e não no sintoma. Se o problema estiver em função compartilhada, corrigir no ponto de origem.
- **Limitações Conhecidas:** Registrar limitações de soluções simplificadas com `ponytail: <limitação>, <quando será necessário melhorar>`.
- **Erros Fora do Escopo:** Erro encontrado fora do recorte da tarefa nunca é corrigido por quem o encontrou, nem ignorado em silêncio. Registrar em `.erros-encontrados/`, um arquivo por erro, quando houver permissão de escrita, e reportar ao líder, ou ao humano quando não houver líder. A correção do registro segue a skill `vibeflow`.
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
