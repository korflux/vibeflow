# Regras do projeto

> VibeFlow: documentos e edição apenas de texto ficam fora da cadeia da skill única `vibeflow`, que trata código de software. Um briefing ambíguo de documento pode passar antes pelas perguntas da interview.

<!-- VIBEFLOW:CADEIA start -->
A cadeia da skill `vibeflow` vale só quando o humano a chama com `/vibeflow` (`$vibeflow` no Codex); fora disso, o agente segue as demais regras deste arquivo, sem rota, phase nem artefato. Risco, MVP, encadeamento, retomada e Modo B seguem a skill `vibeflow`; esta tabela é a única fonte das rotas.

| esforço | etapas | quando |
|---|---|---|
| low | implement, sem init, `.vibeflow/`, phase nem artefato | mudança clara e localizada de código de software sem comportamento novo, como cor, texto ou layout de página estática |
| medium | implement → review | pedido claro e direto, com comportamento novo pequeno, sem banco nem risco de regressão de backend, ou página visual cujo aceite dependa de validação renderizada |
| high | interview → spec → plan → analyze → implement com até quatro checkpoints → review | pedido ambíguo ou de execução difícil, mudança que altera banco ou painel admin, risco de regressão de backend, ou tela que o design system e as telas existentes não cobrem |

Saem do low, seguindo a rota aplicável: comportamento, rota, interação, critério de aceite ou acessibilidade alterados, e mudanças que toquem privacidade, dado pessoal, consentimento, retenção, direitos, obrigação jurídica, autenticação, autorização, pagamento, segredo, persistência ou risco de perda de dados.
<!-- VIBEFLOW:CADEIA end -->

## Projeto
<!-- SLOT:paragrafo -->
<!-- evidência: <path ou vazio> -->

## Núcleo do projeto
<!-- SLOT:nucleo -->
<!-- Uma linha por item, só path que existe: - `<path>`: <o que é>; ler <quando ler>. O init monta a seção com o explorador, e só entra o item que o humano confirma. -->

## Comandos do projeto
<!-- SLOT:comandos -->
<!-- Registrar só comandos existentes, cada um com onde roda (local, CI ou host): instalar, executar, lintar, validar tipos, teste por recorte (arquivo, módulo ou filtro), suíte completa, E2E, varredura de segredos e CI obrigatório. Com orçamento declarado, registrar a linha `Orçamento da regressão completa: <minutos>`; sem declaração, não registrar a linha, e vale o padrão de `references/review/passos.md` (Orçamento de duração) da skill `vibeflow`. -->

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
