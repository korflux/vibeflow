# vibe-init, análise

## Fluxo

O agente lê o motor e executa o init na raiz. O motor cria `AGENTS.md` a partir do template ou preserva as regras já existentes, atualiza a cadeia e o aviso de escopo, guarda cópias verificadas de fontes legadas e retorna um relatório. As fontes idênticas são retiradas automaticamente. A IA lê apenas as fontes listadas em `merges`, incorpora diferenças materiais e confere o resultado antes do commit local.

## Decisões

Na mesma execução, o motor pré-valida os doze perfis distribuídos (seis papéis, inclusive o redator, em dois hosts) e seus destinos antes de escrever qualquer arquivo. A instalação usa bytes do pacote, sem depender da máquina de autoria. Igualdade preserva o arquivo e conflito preserva a personalização; a IA recebe os paths e pede decisão somente se for necessário substituir uma customização.

Quando os templates de perfil mudam, projetos já inicializados recebem `conflito` para perfis que nunca foram editados pelo usuário. Deixar esses perfis velhos faria os subagentes seguirem um contrato de prova e de relatório que a implement não usa mais. O motor continua sem interpretar conteúdo; a IA distingue perfil VibeFlow desatualizado de customização pelo diff e pelo histórico Git do path, substitui o desatualizado depois do backup verificado e preserva a customização. Na dúvida, preservar e reportar é o caminho, porque perder uma personalização custa mais que manter um perfil antigo.

Erro fora do recorte deixou de ser corrigido por quem o encontra. No Modo A, cada T* da onda tem ownership exclusivo dos seus `Arquivos:`; uma correção oportunista em outro path colide com outro escritor e invalida a disjunção calculada pelo motor. Registrar e reportar mantém o erro visível sem quebrar as ondas.

A regra que proíbe testar presença de texto em `SKILL.md` e templates vale para este repositório, onde as skills são o produto. Em outros projetos ela não tem objeto e saiu do template; neste repositório ela permanece no `AGENTS.md` da raiz.

A raiz física identifica o pacote que já forneceu o motor executado. Resolver somente essa raiz permite a descoberta por alias e a instalação padrão por symlink sem ocultar links inesperados dentro dos recursos. A inspeção dos perfis e dos destinos mantém as barreiras existentes, inclusive quando o alias de instalação passa por um ancestral linkado.

O relatório separa instalação no disco de disponibilidade na sessão. A IA confere as ferramentas antes de delegar e orienta recarga quando o host não descobriu os novos papéis. Os perfis de projeto podem prevalecer sobre os pessoais. Os modelos e esforços de referência permanecem explícitos; indisponibilidade não autoriza substituição. Codex usa TOML e Claude usa frontmatter Markdown; ambos apontam para a skill descoberta pelo host, sem paths pessoais.

Os perfis Claude de explorador e verificador permitem `SendMessage` para colaboração direta entre subagentes. O verificador assume a conferência de diff e aceite junto das provas, mantendo as restrições de escrita e Git. Essa comunicação não exige habilitar Agent Teams.

`AGENTS.md` virou fonte única para evitar três arquivos com o mesmo conteúdo. A ponte Antigravity continua curta e referencia a fonte da raiz. `CLAUDE.md` e os antigos `REGRAS.md` não são criados; na migração, cópias idênticas saem após backup e fontes diferentes permanecem até o conteúdo ser consolidado.

O AGENTS de referência enviado pelo usuário mostra uma estrutura útil: comandos reais de instalação e verificação, mapa de diretórios, invariantes dos fluxos e pontos de mudança frequentes. O template incorpora essas categorias como SLOTs. Stack, paths, comandos e regras do projeto de origem não entram no VibeFlow.

## Limite

O motor prepara estrutura e backups e reconhece igualdade de conteúdo. Ele não decide equivalência semântica entre regras diferentes nem preenche fatos do projeto sem evidência. A retirada das fontes divergentes é etapa posterior à consolidação pela IA.
