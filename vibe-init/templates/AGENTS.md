# Regras do projeto

> VibeFlow: documentos e edição apenas de texto ficam fora de `vibe-spec`, `vibe-design`, `vibe-plan`, `vibe-analyze`, `vibe-implement` e `vibe-review`. Essas skills tratam código de software. `vibe-interview` pode esclarecer um briefing ambíguo de documento.

<!-- VIBEFLOW:CADEIA start -->
| esforço | fluxo | quando |
|---|---|---|
| — | init | primeira vez no repo, ou disco quebrado, de novo só para reparar |
| low | implement | mudança simples de código de software, como cor ou layout de página estática |
| medium | implement → review | pedido claro e direto sem regressão de backend, ou página visual cujo aceite dependa de validação renderizada |
| high | spec → plan → implement → review | pedido claro, execução difícil, ou sistema com auth, painel admin, banco ou regressão |
| xhigh | interview → spec → plan → implement → review | pedido ambíguo, confiança baixa, intenção ou sucesso de software em aberto |
| max | interview → spec → plan → analyze → implement → review | pedido toca auth, pagamento, segredo, perda de dados, produção, alto blast radius ou baseline MVP de software |
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
- Plans novos usam `# Protocolo: coordenacao-v1`. Plans `etapas-v1`, Modo B ou sem marcador conservam o contrato original, sem migração.
- No Modo A, o coordenador planeja as ondas e delega toda execução, inclusive registros e Git. Faz no máximo pequenos ajustes finais.
- Implementador entrega código e testes. Redator entrega T* de prosa. Verificador certifica a integração. Revisor faz a review e nunca opera Git.
- Código paralelo só ocorre em onda: as T* de `fila.onda`, com `Arquivos:` disjuntos calculados pelo motor e ownership exclusivo. T* sem `Arquivos:` ou sobreposta roda sozinha. No Modo B, o grupo é oferecido ao humano.
- Leitura e preparação podem colaborar com comunicação direta, com um dono por arquivo.
- Implementador e verificador provam só a `Prova afetada:`. A review final executa a `Regressão completa`.
- Finalizador é um agente genérico apto a Git. Registra `execution.json` e opera Git com ownership exclusivo. Perfil que proíbe Git não vira finalizador. Sem agente apto, relate a limitação.
- Plan guarda definição e resumo curto, sem hashes, logs ou saída detalhada. Conclusão exige integração verde e commit real.
- Aprovar a review, publicar decisões vigentes e fazer push exigem confirmação humana final explícita.

## Padrões de Código e Engenharia
- **Comentários Semânticos Obrigatórios:** Toda função, componente ou módulo deve ter comentário explicando o que faz, para que serve e a justificativa de decisões não óbvias. Zero funções órfãs.
- **Desenvolvimento Eficiente (YAGNI):** O melhor código é o mínimo necessário. Antes de escrever código novo, reutilizar o que já existe no projeto, na standard library ou recursos nativos da plataforma. Não criar abstrações para necessidades especulativas futuras.
- **Causa Raiz:** Correção de bugs deve atuar na causa raiz e não no sintoma. Se o problema estiver em função compartilhada, corrigir no ponto de origem.
- **Limitações Conhecidas:** Registrar limitações de soluções simplificadas com `ponytail: <limitação>, <quando será necessário melhorar>`.
- **Erros Fora do Escopo:** Erro encontrado fora do recorte da tarefa nunca é corrigido por quem o encontrou, nem ignorado em silêncio. Registrar em `.erros-encontrados/`, um arquivo por erro, quando houver permissão de escrita, e reportar ao coordenador, ou ao humano quando não houver coordenador.
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
