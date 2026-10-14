# vibe-init, arquitetura

## Contrato de disco

`AGENTS.md` na raiz é a única fonte editável de regras. O init não cria `CLAUDE.md`, `REGRAS.md` ou `GEMINI.md`. A infraestrutura complementar é `.vibeflow/phases/.gitkeep`, `.vibeflow/.gitignore`, `.agents/rules/vibeflow.md` e o relatório transitório `.vibeflow/init-report.json`. A ponte Antigravity contém apenas `@../../AGENTS.md`.

O template fica em `vibe-init/templates/AGENTS.md`. O motor cria o arquivo quando ausente; se já houver `AGENTS.md`, preserva seu corpo e atualiza somente o aviso de escopo e o bloco entre `VIBEFLOW:CADEIA start/end`. A IA preenche SLOTs com evidência do projeto.

## Migração e proteção

O motor reconhece `.vibeflow/REGRAS.md`, `REGRAS.md` na raiz e `CLAUDE.md` como fontes legadas. Salva cada fonte em `.vibeflow/old/` e confere tamanho e SHA-256 antes de editar ou remover. Colisão com conteúdo diferente recebe sufixo UTC. Um `AGENTS.md` que aponta para arquivo local é materializado após backup. Links externos, fontes não regulares e fontes maiores que 1 MiB são recusados. Legados com conteúdo idêntico ao `AGENTS.md` materializado são removidos automaticamente, inclusive symlinks, depois da atualização do alvo. Fontes diferentes aparecem em `merges` e permanecem no disco até consolidação semântica pela IA.

O relatório JSON contém `root`, `target`, `actions`, `olds`, `merges`, `migrated` e `legacy_present`. Ele é ignorado pelo Git. O stdout contém somente seu path. O arquivo `.vibeflow/.gitignore` preserva entradas existentes e acrescenta `init-report.json` e `init-pending.json` quando faltarem.

Os motores emitem stdout e stderr em UTF-8 sem BOM, inclusive em pipes e com caminhos ou mensagens acentuadas. Consumidores devem decodificar esses streams explicitamente como UTF-8.

## Adaptadores de subagentes

O pacote distribui `templates/agents/codex/<papel>.toml` e `templates/agents/claude/<papel>.md`. A allowlist é explorador, implementador, verificador, corretor, revisor e redator, seis papéis em dois hosts. Cada execução instala os doze arquivos em `.codex/agents/` e `.claude/agents/` da raiz, sem acessar perfis pessoais nem alterar configurações gerais. Os adaptadores apontam para as skills descobertas pelo host; não duplicam as regras de `AGENTS.md`.

Em `coordenacao-v1`, os perfis seguem o contrato da `vibe-implement`: o implementador entrega código e testes juntos, escreve só nos `Arquivos:` da T* e prova só a `Prova afetada:`; o verificador prova a afetada por T* e, na integração, a união delas, sem ampliar; o revisor executa a `Regressão completa` na review final. Nos protocolos históricos, cada perfil segue a etapa e as provas delegadas.

O redator escreve e revisa a prosa de uma T* cujo resultado principal é texto (SKILL.md, referências, templates, ARQUITETURA, ANALISE e README), com modelo de maior raciocínio que o do implementador. Edita somente os `Arquivos:` delegados, não escreve código de motor nem testes, não edita plan, spec nem review, edita `AGENTS.md` somente quando ele está declarado nos `Arquivos:` de uma T* aprovada, nunca a seção `## Decisões vigentes`, e executa a `Prova afetada:` delegada. No Claude usa `opus` com esforço `medium`; no Codex usa o mesmo modelo do revisor com esforço `medium` e, como o implementador, sem `sandbox_mode`.

Todos os perfis terminam no mesmo parágrafo comum, que proíbe operar Git e lista os oito campos do relatório fixo de `vibe-implement/references/delegation.md`: estado, etapa, paths, prova, cobertura, pendencias, proximo e pergunta. No revisor, esse parágrafo troca a proibição de editar artefatos pelas escritas autorizadas de review e analyze; no redator, pela exceção de `AGENTS.md` descrita acima.

Modelos e esforços diferem entre hosts por decisão do humano. Eles reproduzem os perfis pessoais de referência inspecionados na phase 15, e a phase 20 os manteve. Cada host tem família de modelos e escala de esforço próprias, então o par modelo e esforço de um papel não precisa coincidir entre os hosts, mesmo quando o esforço coincide, como no redator.

Antes de compor as fontes, os dois motores resolvem a identidade física da raiz do pacote instalado. Aliases de instalação por symlink/junction, inclusive em ancestrais dessa raiz e em `skills/vibe-init`, são aceitos. Os caminhos internos `templates/agents/<host>/<papel>` não são resolvidos individualmente: links dentro do pacote permanecem visíveis e são recusados.

Antes de qualquer mutação, os dois motores validam os doze pares fonte/destino: a cadeia da fonte física e toda a cadeia lexical do destino devem conter somente diretórios sem symlink/junction/reparse point; cada fonte deve ser arquivo regular existente de até 1 MiB. Destino ausente é permitido; destino existente deve ser regular. Fontes ausentes, grandes ou tipos inseguros interrompem a execução com `PERFIL_AUSENTE`, `FONTE_GRANDE` ou `TIPO_INESPERADO`. Nenhum perfil é instalado antes de terminar essa pré-validação. O motor usa somente nomes e extensões da allowlist.

Ausente é criado com os bytes da fonte (`instalado`); idêntico permanece intacto (`ja_instalado`); diferente permanece intacto (`conflito`), sem backup ou substituição automática. Perfis personalizados não são interpretados. O relatório mantém os campos anteriores e acrescenta `agent_profiles`, uma lista de registros com `host` (`codex`/`claude`), `role`, `path` relativo e `status`; `agent_session` tem `status: nao_verificada` e `reload_required: true`. Conflito não é instalação completa e não impede os demais perfis seguros. O motor nunca certifica disponibilidade na sessão.

No re-init, a IA decide cada `conflito`, e o motor não muda. Ela compara o perfil por diff com a fonte do pacote e pelo histórico Git do path no projeto. Perfil VibeFlow desatualizado, sem conteúdo do usuário, é copiado para `.vibeflow/old/` com tamanho e SHA-256 conferidos e só então substituído pelos bytes da fonte. Customização, histórico ausente ou dúvida preservam o perfil e entram no relato. A IA também propõe ao humano o patch das seções Git e Padrões de Código e Engenharia de um `AGENTS.md` existente, que o motor não reescreve.

Os perfis de projeto podem prevalecer sobre os pessoais. Após instalar, a IA confere os papéis disponíveis nas ferramentas da sessão antes de delegar. Quando ausentes, orienta recarregar/reabrir o host e relata o host indisponível; nunca troca modelos silenciosamente. O init não configura permissões globais ou bypass de segurança.

As provas executam os dois motores em fixtures isoladas, conferem formatos nativos e bytes, idempotência, conflito preservado, fonte inválida, destino não regular, link quebrado e ancestral linkado. Os entrypoints pelo alias de descoberta, pelo alias de pacote instalado e por ancestral de instalação linkado instalam os doze perfis e repetem sem alteração; fontes internas inseguras continuam recusadas quando a entrada é um alias legítimo. O launcher Unix também percorre instalação e repetição pelo alias. Limpeza de fixture é obrigatória. Instalação estrutural não certifica carregamento em um host indisponível.

## Motores e testes

`scripts/init.py` é o motor Python 3; `scripts/init.ps1` é o motor PowerShell 7 com o mesmo alvo e garantias essenciais; `scripts/init.sh` seleciona um dos dois no Unix. Flags públicas: `--root` / `-Root`. Erros previstos saem como mensagem curta. As suítes em `docs/vibe-init/tests/` verificam projeto novo, idempotência, preservação de fonte, migração de symlink, recusa de link externo e paridade essencial.

## Git

Após consolidação, o commit local inclui `AGENTS.md`, a ponte Antigravity, `.vibeflow/.gitignore`, `.vibeflow/phases/.gitkeep`, os paths de perfis com status `instalado`, os perfis desatualizados substituídos e os backups necessários. Customizações preservadas não entram, nem por varredura de diretório; perfis já instalados não exigem staging. Legados do antigo VibeFlow só saem depois de preservação e merge auditados. O init não faz push.

## Regra operacional distribuída

O template de `AGENTS.md` anuncia `coordenacao-v1` para plans novos, o ownership do finalizador genérico e o gate humano de fechamento, em frases curtas. Ele proíbe corrigir erro encontrado fora do recorte: quem o encontra registra em `.erros-encontrados/` e reporta ao coordenador, ou ao humano sem coordenador, porque a correção fora do recorte quebra o ownership das ondas. O SLOT de comandos pede, quando existirem, teste por recorte, suíte completa, E2E, varredura de segredos e CI obrigatório, com onde cada um roda. A regra de testes de skills do repositório VibeFlow não faz parte do template.

Os seis perfis, inclusive o redator, mantêm a proibição de Git; o finalizador não é perfil novo. Init não migra o protocolo de phases.
