# vibe-init, análise

## Fluxo

O agente lê o motor e executa o init na raiz. O motor cria `AGENTS.md` a partir do template ou preserva as regras já existentes, atualiza a cadeia e o aviso de escopo, guarda cópias verificadas de fontes legadas e retorna um relatório. A IA lê apenas as fontes listadas em `merges`, incorpora diferenças materiais e confere o resultado antes do commit local.

## Decisões

`AGENTS.md` virou fonte única para evitar três arquivos com o mesmo conteúdo. A ponte Antigravity continua curta e referencia a fonte da raiz. `CLAUDE.md` e os antigos `REGRAS.md` não são criados; na migração, permanecem até o conteúdo ser consolidado. Isso evita perda de instruções que não podem ser mescladas por comparação de bytes.

O AGENTS de referência enviado pelo usuário mostra uma estrutura útil: comandos reais de instalação e verificação, mapa de diretórios, invariantes dos fluxos e pontos de mudança frequentes. O template incorpora essas categorias como SLOTs. Stack, paths, comandos e regras do projeto de origem não entram no VibeFlow.

## Limite

O motor prepara estrutura e backups, mas não decide quais regras legadas são equivalentes nem preenche fatos do projeto sem evidência. A retirada dos arquivos legados é etapa posterior à consolidação pela IA.
