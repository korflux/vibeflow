# Etapa init (etapa 0)

`AGENTS.md` na raiz é a única fonte editável de regras. A etapa prepara o repositório e instala os perfis de subagente em nível global, uma vez por máquina. Não crie `CLAUDE.md`, `GEMINI.md` nem cópias das regras em outros paths.

## Entrada

- Gatilho, somente em rota com phase (medium ou acima, e MVP) ou com `/vibeflow init`: `.vibeflow/` ausente; `AGENTS.md` ausente ou sem o bloco `VIBEFLOW:CADEIA`; ou disco quebrado, para reparo. `AGENTS.md` sem a seção `## Núcleo do projeto` dispara só o reparo dessa seção (passo 2), na primeira rota com phase. Low nunca dispara o init.
- Leia `AGENTS.md`, `CLAUDE.md` quando existir, `.agents/rules/vibeflow.md`, os perfis globais de cada host e, se existirem, os perfis do projeto em `.claude/agents/` e `.codex/agents/`.
- `~` é a pasta do usuário (`%USERPROFILE%` no Windows). Os perfis globais ficam em `<pasta do host>/agents/`: no Claude Code, a pasta do host é o valor de `CLAUDE_CONFIG_DIR` quando definida, senão `~/.claude`; no Codex, o valor de `CODEX_HOME` quando definida, senão `~/.codex`. Os passos abaixo escrevem `~/.claude/agents/` e `~/.codex/agents/` e seguem esta regra.

## Quem faz

| Quem | Faz |
|---|---|
| Explorador | Propõe a seção `## Núcleo do projeto`: as referências centrais do projeto, cada uma com path, o que é e quando ler, com evidência; não escreve |
| Líder | Delega a etapa, leva ao humano a proposta do núcleo e as decisões sobre customizações, sobre Docker nos testes e sobre os bloqueios do host, confere o resultado, faz o commit do passo 7 e decide a recarga do host |
| Redator | Executa os passos 1 a 6: grava `AGENTS.md`, a ponte, os backups, os perfis globais copiados e os bloqueios aceitos, sem operar Git |

Sem redator carregado, como na primeira instalação, o líder executa os passos 1 a 6 inline, inclusive a proposta do núcleo (Modo B, `SKILL.md` seção 7).

## Passos

1. **Estrutura.** Crie `.vibeflow/phases/.gitkeep` quando ausente. Nada é escrito através de link (`references/disco.md`, Escrever artefato), e todo arquivo de regra recebe backup antes de ser substituído ou removido (Backup de arquivo de regra, abaixo).
2. **AGENTS.md.**
   - Ausente: nasce de `templates/AGENTS.md` (`AGENTS.md` vazio conta como ausente).
   - Existente: mantenha as regras do projeto. Atualize só o aviso de escopo do topo e o bloco entre `<!-- VIBEFLOW:CADEIA start -->` e `<!-- VIBEFLOW:CADEIA end -->`, copiados de `templates/AGENTS.md`, e monte a seção `## Núcleo do projeto` quando ausente (abaixo). Sem nenhum dos delimitadores, insira o aviso e o bloco completo logo após o primeiro título. Delimitador sem par: pare e relate.
   - Preencha os SLOTs do template somente com evidência do projeto: comandos reais de setup e teste, mapa curto da estrutura, fluxos de ponta a ponta, invariantes e validações. Não copie stack, paths ou regras de outro projeto.
   - Orçamento: registre em Comandos do projeto a linha do orçamento da regressão completa quando o humano ou o projeto o declarar (`references/review/passos.md`, Orçamento de duração); sem declaração, não escreva a linha e deixe o comentário que cita o padrão.
   - Ambiente: registre em Ambiente os serviços de teste locais encontrados e procure Docker nos testes pelos sinais de `references/ambiente.md`. Com Docker detectado e sem decisão registrada, devolva a evidência ao líder, que conduz a pergunta desse arquivo.
   - Núcleo do projeto: com a seção `## Núcleo do projeto` ausente ou sem item preenchido, o líder pede ao explorador a proposta e a leva ao humano; o redator grava a versão confirmada, uma linha por item com path, o que é e quando ler, fora do bloco da cadeia. Item que o humano não confirma não entra. Seção existente é mantida.
   - Em re-init, compare as seções Git e Padrões de Código e Engenharia com o template e devolva ao líder o patch proposto; aplique só o que o humano aprovar. O template guarda só a convenção que o código não mostra: regra que o modelo já segue sem ser dita (reuso, causa raiz, validação de entrada, segredo fora do repositório, autorização no servidor) saiu dele, e a seção `Segurança por Padrão` de versão anterior entra no patch como remoção proposta, com as duas regras de erro movidas para Padrões de Código e Engenharia. Regra dessas seções que o projeto escreveu por conta própria fica. Nunca altere `## Decisões vigentes`.
   - Tamanho: com `AGENTS.md` acima do limite de `references/disco.md` (Tamanho), devolva ao líder a proposta de mover para `docs/<assunto>.md` as seções que não são regra, núcleo, comando nem decisão vigente (inventário de ferramentas, histórico de phases, mapa detalhado da estrutura, fluxos descritos em parágrafo), com o tamanho de cada uma e a linha que fica no lugar apontando o arquivo. O texto vai igual, sem reescrita. Relate o teste do projeto que lê a seção movida, que o líder delega ao implementador para ler o arquivo novo com as mesmas asserções. Aplique só o que o humano aprovar.
3. **Outras regras do host.** `CLAUDE.md` existente é do usuário: não é removido nem reescrito. Devolva ao líder as regras dele que duplicam ou contradizem o `AGENTS.md`; o humano decide se algo é incorporado.
4. **Ponte.** `.agents/rules/vibeflow.md` contém exatamente `@../../AGENTS.md` e uma quebra de linha final. Conteúdo diferente recebe backup e é reescrito.
5. **Perfis globais.** Para cada um dos cinco papéis (`explorador`, `implementador`, `verificador`, `revisor`, `redator`), copie `templates/agents/claude/<papel>.md` para `~/.claude/agents/<papel>.md` e `templates/agents/codex/<papel>.toml` para `~/.codex/agents/<papel>.toml`, criando a pasta quando ausente:

   | Destino | Ação |
   |---|---|
   | Ausente | Copie os bytes da fonte (perfil criado) |
   | Idêntico à fonte, sem contar diferença só de quebra de linha (CRLF ou LF) ou BOM | Mantenha |
   | Diferente | Conflito: não sobrescreva; classifique abaixo |

   Perfil global não tem histórico Git que prove a origem: todo conflito é tratado como possível customização. Preserve os bytes e relate host, papel, path e o diff contra a fonte; substituir exige decisão humana e backup em `~/.vibeflow/old/` (Backup de arquivo de regra, abaixo), e o perfil passa a contar como alterado.

   Perfil global `corretor` de uma versão anterior (`~/.claude/agents/corretor.md` ou `~/.codex/agents/corretor.toml`) é obsoleto: relate host e path ao humano e preserve o arquivo. Removê-lo exige decisão humana e o mesmo backup em `~/.vibeflow/old/`.

   Perfil do projeto em `.claude/agents/` ou `.codex/agents/` prevalece no host sobre o global. O init não cria nem remove perfil de projeto; quando um existe e difere da fonte, relate-o como customização do projeto. Fora dos perfis do VibeFlow, não altere configurações globais, permissões gerais nem modelos pessoais; a única permissão que o init grava é a do passo 6, no projeto e com aceite humano.
6. **Bloqueios do host.** Só no Claude Code; em outro host, pule o passo. O que um erro não deixa desfazer (trabalho não commitado descartado, histórico reescrito, segredo lido para o contexto) não fica só na prosa: `templates/claude-settings.json` traz as regras `deny` que o host aplica antes de qualquer modo de permissão, para `Bash` e para `PowerShell`.
   - Compare `permissions.deny` do `.claude/settings.json` do projeto com a lista do template. Sem regra faltando, mantenha o arquivo e não pergunte.
   - Com regra faltando e sem decisão registrada em Ambiente no `AGENTS.md`, devolva ao líder as regras que faltam; ele pergunta ao humano uma vez, com a recomendação de aceitar.
   - Aceite: acrescente só as regras que faltam a `permissions.deny`, criando o arquivo e a chave quando ausentes e preservando todo o resto do JSON; `.claude/settings.json` que não é JSON válido não é reescrito, e o caso volta ao líder. Recusa: não toque o arquivo. Nos dois casos, registre em Ambiente a linha `Bloqueios do host: <aceitos | recusados>, decidido em <AAAA-MM-DD>`.
   - Decisão registrada como recusada não é perguntada de novo; registrada como aceita, a regra nova de uma versão posterior do template entra sem nova pergunta e é relatada.
   - A regra casa o comando como foi escrito: é rede para o engano e não substitui a regra de Git de `references/delegation.md` (Ownership e proibições). O projeto acrescenta ao `deny` os arquivos de segredo que tiver fora dos nomes do template.
7. **Commit, pelo líder.** Confira que `AGENTS.md` é arquivo regular na raiz, a cadeia está atualizada e a ponte aponta para ele; com Node, `scripts/governanca.mjs` confere isso, o `.gitkeep` e o estado de cada perfil global contra a fonte, e o relatório do redator é comparado com a saída dele. O `AGENTS.md` sem `## Núcleo do projeto` aparece como aviso, sem falha; o reparo segue o passo 2. Commite `chore(init): <resultado>` conforme `references/disco.md` (Commits), com os paths produzidos no repositório, inclusive `.claude/settings.json` quando o passo 6 o gravou, e os backups necessários em `.vibeflow/old/`; perfis globais ficam fora do repositório e do commit. Sem path produzido no repositório, como numa máquina nova com o repositório já inicializado, não há commit vazio e o relatório registra `hash: nenhum`.

## Backup de arquivo de regra

Antes de substituir ou remover `AGENTS.md`, a ponte ou um perfil:

- Arquivo commitado sem alteração local tem o commit como backup. Senão, copie-o para `.vibeflow/old/` com o mesmo nome (a ponte vira `antigravity-vibeflow.md`); perfil global substituído por decisão humana vai para `~/.vibeflow/old/`, com o mesmo nome e as mesmas conferências.
- Confira tamanho e SHA-256 da cópia contra o original (com Node, `scripts/governanca.mjs --backup <original> <cópia>`); divergência apaga a cópia e interrompe a substituição.
- Destino em `old/` com o mesmo conteúdo é reutilizado; com conteúdo diferente, acrescente o sufixo UTC `.<AAAAMMDDTHHMMSSZ>`.
- Só depois da cópia conferida substitua ou remova o original.

## Saída

O redator devolve o relatório fixo com paths, a seção `## Núcleo do projeto` gravada ou mantida, perfis globais criados, substituídos e preservados, perfis `corretor` obsoletos encontrados, perfis de projeto encontrados, os bloqueios do host gravados, mantidos ou pendentes de decisão, o patch proposto do `AGENTS.md` e as fontes que ainda exigem decisão.

## Fechar e próxima etapa

O líder informa hash e paths. Com algum perfil global criado ou alterado, pare e peça a recarga do host antes da primeira delegação; em re-init com os cinco perfis idênticos à fonte, não há recarga. Depois da recarga, confira os cinco perfis nas ferramentas do host; perfil presente só no disco não conta, e modelo indisponível não é substituído em silêncio. Com os perfis carregados, retome a rota classificada.
