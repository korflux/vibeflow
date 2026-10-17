# Regras do projeto

> VibeFlow: documentos e edição apenas de texto ficam fora das etapas spec, design, plan, analyze, implement e review da skill única `vibeflow`. Essas etapas tratam código de software. A etapa interview pode esclarecer um briefing ambíguo de documento.

<!-- VIBEFLOW:CADEIA start -->
| esforço | fluxo | quando |
|---|---|---|
| N/A | init | primeira vez no repo, ou disco quebrado, de novo só para reparar |
| low | implement | mudança simples de código de software, como cor ou layout de página estática |
| medium | implement → review | pedido claro e direto sem regressão de backend, ou página visual cujo aceite dependa de validação renderizada |
| high | spec → plan → implement → review | pedido claro, execução difícil, ou sistema com auth, painel admin, banco ou regressão |
| xhigh | interview → spec → plan → implement → review | pedido ambíguo, confiança baixa, intenção ou sucesso de software em aberto |
| max | interview → spec → plan → analyze → implement → review | pedido toca auth, pagamento, segredo, perda de dados, produção, alto blast radius ou baseline MVP de software |

`/vibeflow` conduz todo o fluxo. `/vibeflow <etapa>` vai direto a `init`, `interview`, `spec`, `design`, `plan`, `analyze`, `implement` ou `review`. O design entra entre spec e plan somente com UI visível.

### Continuidade entre chats

Um único chat conduz a phase por padrão. Em host de contexto curto, use dois: um para todo o planejamento (interview, spec, design, plan e analyze) e outro para a implementação (implement e review). Quando o contexto pesar ou o humano pedir para parar, o líder grava o estado no `plan.md` e recomenda um chat novo. A retomada parte do disco: em chat novo, `/vibeflow` lê as linhas `# Status:`, as caixas do `plan.md` e o Git e segue de onde parou. Sem subagentes, analyze e review pedem chat novo (`/vibeflow analyze`, `/vibeflow review`). Separar chats é recomendação, nunca gate.
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
- Phases da v1 são lidas como estão, sem migração; o estado vem das linhas `# Status:`, das caixas do `plan.md` e do Git.
- No Modo A, o líder planeja as ondas e delega toda execução, inclusive o estado do `plan.md` e o Git. Faz no máximo pequenos ajustes finais.
- Implementador entrega código e testes. Redator grava a prosa de interview, spec, design e plan e as T* de prosa. Verificador certifica a integração. Revisor faz analyze e review, escreve sozinho a prosa e os achados de `analyze.md` e `review.md` e nunca opera Git.
- Código paralelo só ocorre em onda: T* elegíveis com `Arquivos:` disjuntos, montadas pelo líder, com ownership exclusivo. T* sem `Arquivos:` ou sobreposta roda sozinha. No Modo B, o grupo é oferecido ao humano.
- Leitura e preparação podem colaborar com comunicação direta, com um dono por arquivo.
- Implementador e verificador provam só a `Prova afetada:`. A review final executa a `Regressão completa`.
- Finalizador é um agente genérico apto a Git. Marca `# Status:`, a aprovação humana, as caixas de T* e o `[x]` de R* comprovados, mantém o resumo curto do `plan.md` e opera Git com ownership exclusivo. Perfil que proíbe Git não vira finalizador. Sem agente apto, relate a limitação.
- Plan guarda definição e resumo curto, sem hashes, logs ou saída detalhada. Conclusão exige integração verde e commit real.
- Aprovar a review, publicar decisões vigentes e fazer push exigem confirmação humana final explícita.

## Padrões de Código e Engenharia
- **Comentários Semânticos Obrigatórios:** Toda função, componente ou módulo deve ter comentário explicando o que faz, para que serve e a justificativa de decisões não óbvias. Zero funções órfãs.
- **Desenvolvimento Eficiente (YAGNI):** O melhor código é o mínimo necessário. Antes de escrever código novo, reutilizar o que já existe no projeto, na standard library ou recursos nativos da plataforma. Não criar abstrações para necessidades especulativas futuras.
- **Causa Raiz:** Correção de bugs deve atuar na causa raiz e não no sintoma. Se o problema estiver em função compartilhada, corrigir no ponto de origem.
- **Limitações Conhecidas:** Registrar limitações de soluções simplificadas com `ponytail: <limitação>, <quando será necessário melhorar>`.
- **Erros Fora do Escopo:** Erro encontrado fora do recorte da tarefa nunca é corrigido por quem o encontrou, nem ignorado em silêncio. Registrar em `.erros-encontrados/`, um arquivo por erro, quando houver permissão de escrita, e reportar ao líder, ou ao humano quando não houver líder.
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
