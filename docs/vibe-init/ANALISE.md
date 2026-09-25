# vibe-init, análise

## Fluxo

O agente lê o motor e executa o init na raiz. O motor cria `AGENTS.md` a partir do template ou preserva as regras já existentes, atualiza a cadeia e o aviso de escopo, guarda cópias verificadas de fontes legadas e retorna um relatório. As fontes idênticas são retiradas automaticamente. A IA lê apenas as fontes listadas em `merges`, incorpora diferenças materiais e confere o resultado antes do commit local.

## Decisões

`AGENTS.md` virou fonte única para evitar três arquivos com o mesmo conteúdo. A ponte Antigravity continua curta e referencia a fonte da raiz. `CLAUDE.md` e os antigos `REGRAS.md` não são criados; na migração, cópias idênticas saem após backup e fontes diferentes permanecem até o conteúdo ser consolidado.

O AGENTS de referência enviado pelo usuário mostra uma estrutura útil: comandos reais de instalação e verificação, mapa de diretórios, invariantes dos fluxos e pontos de mudança frequentes. O template incorpora essas categorias como SLOTs. Stack, paths, comandos e regras do projeto de origem não entram no VibeFlow.

## Limite

O motor prepara estrutura e backups e reconhece igualdade de conteúdo. Ele não decide equivalência semântica entre regras diferentes nem preenche fatos do projeto sem evidência. A retirada das fontes divergentes é etapa posterior à consolidação pela IA.
