# vibe-init, arquitetura

## Contrato de disco

`AGENTS.md` na raiz é a única fonte editável de regras. O init não cria `CLAUDE.md`, `REGRAS.md` ou `GEMINI.md`. A infraestrutura complementar é `.vibeflow/phases/.gitkeep`, `.vibeflow/.gitignore`, `.agents/rules/vibeflow.md` e o relatório transitório `.vibeflow/init-report.json`. A ponte Antigravity contém apenas `@../../AGENTS.md`.

O template fica em `vibe-init/templates/AGENTS.md`. O motor cria o arquivo quando ausente; se já houver `AGENTS.md`, preserva seu corpo e atualiza somente o aviso de escopo e o bloco entre `VIBEFLOW:CADEIA start/end`. A IA preenche SLOTs com evidência do projeto.

## Migração e proteção

O motor reconhece `.vibeflow/REGRAS.md`, `REGRAS.md` na raiz e `CLAUDE.md` como fontes legadas. Salva cada fonte em `.vibeflow/old/` e confere tamanho e SHA-256 antes de editar ou remover. Colisão com conteúdo diferente recebe sufixo UTC. Um `AGENTS.md` que aponta para arquivo local é materializado após backup. Links externos, fontes não regulares e fontes maiores que 1 MiB são recusados. Legados com conteúdo idêntico ao `AGENTS.md` materializado são removidos automaticamente, inclusive symlinks, depois da atualização do alvo. Fontes diferentes aparecem em `merges` e permanecem no disco até consolidação semântica pela IA.

O relatório JSON contém `root`, `target`, `actions`, `olds`, `merges`, `migrated` e `legacy_present`. Ele é ignorado pelo Git. O stdout contém somente seu path. O arquivo `.vibeflow/.gitignore` preserva entradas existentes e acrescenta `init-report.json` e `init-pending.json` quando faltarem.

## Adaptadores de subagentes

O pacote distribui `templates/agents/codex/<papel>.toml` e `templates/agents/claude/<papel>.md`. A allowlist é explorador, implementador, verificador, corretor e revisor. Cada execução instala os dez arquivos em `.codex/agents/` e `.claude/agents/` da raiz, sem acessar perfis pessoais nem alterar configurações gerais. Os adaptadores apontam para as skills descobertas pelo host; não duplicam as regras de `AGENTS.md`.

Antes de qualquer mutação, os dois motores validam os dez pares fonte/destino: toda a cadeia de ancestrais deve conter somente diretórios sem symlink/junction/reparse point; cada fonte deve ser arquivo regular existente de até 1 MiB. Destino ausente é permitido; destino existente deve ser regular. Fontes ausentes, grandes ou tipos inseguros interrompem a execução com `PERFIL_AUSENTE`, `FONTE_GRANDE` ou `TIPO_INESPERADO`. Nenhum perfil é instalado antes de terminar essa pré-validação. O motor usa somente nomes e extensões da allowlist.

Ausente é criado com os bytes da fonte (`instalado`); idêntico permanece intacto (`ja_instalado`); diferente permanece intacto (`conflito`), sem backup ou substituição automática. Perfis personalizados não são interpretados. O relatório mantém os campos anteriores e acrescenta `agent_profiles`, uma lista de registros com `host` (`codex`/`claude`), `role`, `path` relativo e `status`; `agent_session` tem `status: nao_verificada` e `reload_required: true`. Conflito não é instalação completa e não impede os demais perfis seguros. O motor nunca certifica disponibilidade na sessão.

Os perfis de projeto podem prevalecer sobre os pessoais. Após instalar, a IA confere os papéis disponíveis nas ferramentas da sessão antes de delegar. Quando ausentes, orienta recarregar/reabrir o host e relata o host indisponível; nunca troca modelos silenciosamente. O init não configura permissões globais ou bypass de segurança.

As provas executam os dois motores em fixtures isoladas, conferem formatos nativos e bytes, idempotência, conflito preservado, fonte inválida, destino não regular, link quebrado e ancestral linkado. Limpeza de fixture é obrigatória. Instalação estrutural não certifica carregamento em um host indisponível.

## Motores e testes

`scripts/init.py` é o motor Python 3; `scripts/init.ps1` é o motor PowerShell 7 com o mesmo alvo e garantias essenciais; `scripts/init.sh` seleciona um dos dois no Unix. Flags públicas: `--root` / `-Root`. Erros previstos saem como mensagem curta. As suítes em `docs/vibe-init/tests/` verificam projeto novo, idempotência, preservação de fonte, migração de symlink, recusa de link externo e paridade essencial.

## Git

Após consolidação, o commit local inclui `AGENTS.md`, a ponte Antigravity, `.vibeflow/.gitignore`, `.vibeflow/phases/.gitkeep`, os paths de perfis com status `instalado` e backups necessários. Perfis conflitantes ou personalizados não entram por varredura de diretório; perfis já instalados não exigem staging. Legados do antigo VibeFlow só saem depois de preservação e merge auditados. O init não faz push.
