# Etapa init (etapa 0)

`AGENTS.md` na raiz é a única fonte editável de regras. A etapa prepara o repositório e instala os perfis de subagente em nível global, uma vez por máquina. Não crie `CLAUDE.md`, `GEMINI.md` nem cópias das regras em outros paths.

## Entrada

- Gatilho, somente em rota com phase (medium ou acima, e MVP) ou com `/vibeflow init`: `.vibeflow/` ausente; `AGENTS.md` ausente ou sem o bloco `VIBEFLOW:CADEIA`; ou disco quebrado, para reparo. Low nunca dispara o init.
- Leia `AGENTS.md`, `CLAUDE.md` quando existir, `.agents/rules/vibeflow.md`, os perfis globais de cada host e, se existirem, os perfis do projeto em `.claude/agents/` e `.codex/agents/`.
- `~` é a pasta do usuário (`%USERPROFILE%` no Windows). Os perfis globais ficam em `<pasta do host>/agents/`: no Claude Code, a pasta do host é o valor de `CLAUDE_CONFIG_DIR` quando definida, senão `~/.claude`; no Codex, o valor de `CODEX_HOME` quando definida, senão `~/.codex`. Os passos abaixo escrevem `~/.claude/agents/` e `~/.codex/agents/` e seguem esta regra.

## Quem faz

| Quem | Faz |
|---|---|
| Líder | Delega a etapa, leva ao humano as decisões sobre customizações, confere o resultado e decide a recarga do host |
| Agente genérico/default apto a Git | Executa os passos abaixo e cria o commit de governança. Os perfis de papel podem ainda não existir nesta etapa |

Sem subagentes ou sem agente genérico apto a Git, o líder executa os passos inline (Modo B).

## Passos

1. **Estrutura.** Crie `.vibeflow/phases/.gitkeep` quando ausente. Siga `references/disco.md`: nada é escrito através de link, e todo arquivo de regra recebe backup antes de ser substituído ou removido (seção Backup de arquivo de regra).
2. **AGENTS.md.**
   - Ausente: nasce de `templates/AGENTS.md` (`AGENTS.md` vazio conta como ausente).
   - Existente: mantenha as regras do projeto. Atualize só o aviso de escopo do topo e o bloco entre `<!-- VIBEFLOW:CADEIA start -->` e `<!-- VIBEFLOW:CADEIA end -->`, copiados de `templates/AGENTS.md`. Sem nenhum dos delimitadores, insira o aviso e o bloco completo logo após o primeiro título. Delimitador sem par: pare e relate.
   - Preencha os SLOTs do template somente com evidência do projeto: comandos reais de setup e teste, mapa curto da estrutura, fluxos de ponta a ponta, invariantes e validações. Não copie stack, paths ou regras de outro projeto.
   - Em re-init, compare as seções Git e Padrões de Código e Engenharia com o template e devolva ao líder o patch proposto; aplique só o que o humano aprovar. Nunca altere `## Decisões vigentes`.
3. **Outras regras do host.** `CLAUDE.md` existente é do usuário: não é removido nem reescrito. Devolva ao líder as regras dele que duplicam ou contradizem o `AGENTS.md`; o humano decide se algo é incorporado.
4. **Ponte.** `.agents/rules/vibeflow.md` contém exatamente `@../../AGENTS.md` e uma quebra de linha final. Conteúdo diferente recebe backup e é reescrito.
5. **Perfis globais.** Para cada papel (`explorador`, `implementador`, `verificador`, `corretor`, `revisor`, `redator`), copie `templates/agents/claude/<papel>.md` para `~/.claude/agents/<papel>.md` e `templates/agents/codex/<papel>.toml` para `~/.codex/agents/<papel>.toml`, criando a pasta quando ausente:

   | Destino | Ação |
   |---|---|
   | Ausente | Copie os bytes da fonte (perfil criado) |
   | Idêntico à fonte | Mantenha |
   | Diferente | Conflito: não sobrescreva; classifique abaixo |

   Perfil global não tem histórico Git que prove a origem: todo conflito é tratado como possível customização. Preserve os bytes e relate host, papel, path e o diff contra a fonte; substituir exige decisão humana e backup em `~/.vibeflow/old/` (`references/disco.md`, Backup de arquivo de regra), e o perfil passa a contar como alterado.

   Perfil do projeto em `.claude/agents/` ou `.codex/agents/` prevalece no host sobre o global. O init não cria nem remove perfil de projeto; quando um existe e difere da fonte, relate-o como customização do projeto. Fora dos perfis do VibeFlow, não altere configurações globais, permissões gerais nem modelos pessoais.
6. **Commit.** Confira que `AGENTS.md` é arquivo regular na raiz, a cadeia está atualizada e a ponte aponta para ele. Faça staging explícito dos paths produzidos no repositório e dos backups necessários em `.vibeflow/old/`; perfis globais ficam fora do repositório e do commit, e trabalho alheio fica fora do staging. Confira o diff e crie commit local sem push. Sem path produzido no repositório, como numa máquina nova com o repositório já inicializado, não há commit vazio e o relatório registra `hash: nenhum`.

## Saída

O agente devolve o relatório fixo com hash, paths, perfis globais criados, substituídos e preservados, perfis de projeto encontrados, o patch proposto do `AGENTS.md` e as fontes que ainda exigem decisão.

## Fechar e próxima etapa

O líder informa hash e paths. Com algum perfil global criado ou alterado, pare e peça a recarga do host antes da primeira delegação; em re-init com os seis perfis idênticos à fonte, não há recarga. Depois da recarga, confira os seis perfis nas ferramentas do host; perfil presente só no disco não conta, e modelo indisponível não é substituído em silêncio. Com os perfis carregados, retome a rota classificada.
