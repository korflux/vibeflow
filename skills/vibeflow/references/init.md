# Etapa init (etapa 0)

`AGENTS.md` na raiz é a única fonte editável de regras. A etapa prepara o repositório, migra instalações antigas e instala os perfis de subagente. Não crie `CLAUDE.md`, `REGRAS.md`, `GEMINI.md` nem cópias das regras em outros paths.

## Entrada

- Gatilho, somente em rota com phase (medium ou acima, e MVP) ou com `/vibeflow init`: `.vibeflow/` ausente; `AGENTS.md` ausente ou sem o bloco `VIBEFLOW:CADEIA`; `REGRAS.md`, `CLAUDE.md` ou `.vibeflow/REGRAS.md` presente e ainda não tratado; ou disco quebrado, para reparo. Legado que o humano decidiu manter e que está registrado em `AGENTS.md` (passo 3) não dispara o init. Low nunca dispara o init.
- Leia `AGENTS.md`, os legados presentes, `.agents/rules/vibeflow.md`, `.claude/agents/` e `.codex/agents/`.

## Quem faz

| Quem | Faz |
|---|---|
| Líder | Delega a etapa, leva ao humano as decisões sobre customizações, confere o resultado e decide a recarga do host |
| Agente genérico/default apto a Git | Executa os passos abaixo e cria o commit de governança. Os perfis de papel podem ainda não existir nesta etapa |

Sem subagentes ou sem agente genérico apto a Git, o líder executa os passos inline (Modo B).

## Passos

1. **Estrutura.** Crie `.vibeflow/phases/.gitkeep` quando ausente. Siga `references/disco.md`: nada é escrito através de link, e todo arquivo de regra recebe backup antes de ser substituído ou removido (seção Backup de arquivo de regra).
2. **AGENTS.md.**
   - Ausente: nasce do primeiro legado presente (`AGENTS.md` vazio conta como ausente), na ordem `.vibeflow/REGRAS.md`, `REGRAS.md`, `CLAUDE.md`, ou de `templates/AGENTS.md` sem legado.
   - Existente: mantenha as regras do projeto. Atualize só o aviso de escopo do topo e o bloco entre `<!-- VIBEFLOW:CADEIA start -->` e `<!-- VIBEFLOW:CADEIA end -->`, copiados de `templates/AGENTS.md`. Sem nenhum dos delimitadores, insira o aviso e o bloco completo logo após o primeiro título. Delimitador sem par: pare e relate.
   - Preencha os SLOTs do template somente com evidência do projeto: comandos reais de setup e teste, mapa curto da estrutura, fluxos de ponta a ponta, invariantes e validações. Não copie stack, paths ou regras de outro projeto.
   - Em re-init, compare as seções Git e Padrões de Código e Engenharia com o template e devolva ao líder o patch proposto; aplique só o que o humano aprovar. Nunca altere `## Decisões vigentes`.
3. **Legados.** Legado com conteúdo idêntico ao `AGENTS.md` final é removido depois do backup. Legado diferente tem as diferenças materiais incorporadas ao `AGENTS.md`; depois de confirmar que o conteúdo foi incorporado e está salvo em `.vibeflow/old/`, remova-o apenas se for do antigo VibeFlow. Outro arquivo do usuário fica até a decisão do humano. Quando o humano decide mantê-lo, acrescente em `## Regras deste repo` do `AGENTS.md` a linha `Legado mantido por decisão humana: <path> (<motivo>).`; com ela, o legado não reabre o init nas próximas runs.
4. **Ponte.** `.agents/rules/vibeflow.md` contém exatamente `@../../AGENTS.md` e uma quebra de linha final. Conteúdo diferente recebe backup e é reescrito.
5. **Perfis.** Para cada papel (`explorador`, `implementador`, `verificador`, `corretor`, `revisor`, `redator`), copie `templates/agents/claude/<papel>.md` para `.claude/agents/<papel>.md` e `templates/agents/codex/<papel>.toml` para `.codex/agents/<papel>.toml`:

   | Destino | Ação |
   |---|---|
   | Ausente | Copie os bytes da fonte (perfil criado) |
   | Idêntico à fonte | Mantenha |
   | Diferente | Conflito: não sobrescreva; classifique abaixo |

   Conflito é VibeFlow desatualizado somente quando duas evidências confirmam que não há conteúdo do usuário: o diff contra a fonte mostra só texto de versões anteriores do VibeFlow, e `git log --follow -p -- <path>` mostra apenas commits de init, sem edição local pendente. Desatualizado recebe backup e é substituído (perfil alterado). Qualquer outro caso, inclusive histórico ausente ou dúvida, é customização: preserve os bytes e relate host, papel e path; substituir exige decisão humana. Não altere configurações globais, permissões gerais nem modelos pessoais.
6. **Commit.** Confira que `AGENTS.md` é arquivo regular na raiz, a cadeia está atualizada, a ponte aponta para ele e nenhuma regra legada se perdeu. Faça staging explícito dos paths produzidos, dos backups necessários e somente dos perfis criados ou substituídos; exclua customizações preservadas e trabalho alheio. Confira o diff e crie commit local sem push.

## Saída

O agente devolve o relatório fixo com hash, paths, perfis criados, substituídos e preservados, o patch proposto do `AGENTS.md` e as fontes que ainda exigem decisão.

## Fechar e próxima etapa

O líder informa hash e paths. Com algum perfil criado ou alterado, pare e peça a recarga do host antes da primeira delegação. Depois da recarga, confira os seis perfis nas ferramentas do host; perfil presente só no disco não conta, e modelo indisponível não é substituído em silêncio. Com os perfis carregados, retome a rota classificada.
