# vibe-init, arquitetura

## Contrato de disco

`AGENTS.md` na raiz é a única fonte editável de regras. O init não cria `CLAUDE.md`, `REGRAS.md` ou `GEMINI.md`. A infraestrutura complementar é `.vibeflow/phases/.gitkeep`, `.vibeflow/.gitignore`, `.agents/rules/vibeflow.md` e o relatório transitório `.vibeflow/init-report.json`. A ponte Antigravity contém apenas `@../../AGENTS.md`.

O template fica em `vibe-init/templates/AGENTS.md`. O motor cria o arquivo quando ausente; se já houver `AGENTS.md`, preserva seu corpo e atualiza somente o aviso de escopo e o bloco entre `VIBEFLOW:CADEIA start/end`. A IA preenche SLOTs com evidência do projeto.

## Migração e proteção

O motor reconhece `.vibeflow/REGRAS.md`, `REGRAS.md` na raiz e `CLAUDE.md` como fontes legadas. Copia arquivos regulares para `.vibeflow/old/` e confere tamanho e SHA-256 antes de editar o alvo. Colisão com conteúdo diferente recebe sufixo UTC. Um `AGENTS.md` que aponta para arquivo local é materializado após backup. Links externos, fontes não regulares e fontes maiores que 1 MiB são recusados. Legados diferentes de `AGENTS.md` aparecem em `merges` e permanecem no disco até consolidação semântica pela IA; o motor não apaga regra de usuário nem inventa equivalência.

O relatório JSON contém `root`, `target`, `actions`, `olds`, `merges` e `legacy_present`. Ele é ignorado pelo Git. O stdout contém somente seu path. O arquivo `.vibeflow/.gitignore` preserva entradas existentes e acrescenta `init-report.json` e `init-pending.json` quando faltarem.

## Motores e testes

`scripts/init.py` é o motor Python 3; `scripts/init.ps1` é o motor PowerShell 7 com o mesmo alvo e garantias essenciais; `scripts/init.sh` seleciona um dos dois no Unix. Flags públicas: `--root` / `-Root`. Erros previstos saem como mensagem curta. As suítes em `docs/vibe-init/tests/` verificam projeto novo, idempotência, preservação de fonte, migração de symlink, recusa de link externo e paridade essencial.

## Git

Após consolidação, o commit local inclui `AGENTS.md`, a ponte Antigravity, `.vibeflow/phases/.gitkeep` e backups necessários. Legados do antigo VibeFlow só saem depois de preservação e merge auditados. O init não faz push.
