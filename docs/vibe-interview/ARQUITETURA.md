# vibe-interview: arquitetura

`/vibe-interview` fecha intenção ambígua antes de `spec`, `plan` ou código. A IA conduz a entrevista e escreve o artefato; os motores apenas inventariam, validam os paths e preparam o arquivo vivo.

Alvos:

```text
.vibeflow/phases/phase-<n>-<slug>/interview.md
.vibeflow/mvp/interview.md
```

## 1. Papéis e ownership

| Peça | Responsabilidade |
|---|---|
| `SKILL.md` | Classificar produto ou feature, entrevistar e conduzir a escrita semântica. |
| `scripts/interview.py`, `interview.ps1`, `interview.sh` | Inventário, slug, validação do alvo, preparação do arquivo e JSON operacional no stdout. |
| `templates/interview.md` | Forma do artefato; não é preenchido pelo motor. |
| `stdout (JSON)` | Evidência operacional transitória, consumida na mesma execução. |
| `interview.md` | Registro vivo e commitável da entrevista. |

O script não detecta MVP pelo texto, não escolhe stack, não faz perguntas e não escreve a prosa da entrevista.

## 2. Dependências e alvos

Sem `.vibeflow/`, encerra com `INIT_AUSENTE`. Se `.vibeflow/phases/` faltar, cria a pasta e `.gitkeep`; não altera `REGRAS.md` nem os ponteiros.

No modo phase, `--slug` cria uma nova `phase-N-slug` com `n` calculado pelo inventário. O modo MVP é explícito, usa somente `.vibeflow/mvp/` e não usa `n` nem slug. O arquivo vivo existente é preservado.

Flags equivalentes:

```text
python interview.py [--root PATH] [--apply] [--slug TEXTO] [--mvp]
pwsh interview.ps1 [-Root PATH] [-Apply] [-Slug TEXTO] [-Mvp]
bash interview.sh [--root PATH] [--apply] [--slug TEXTO] [--mvp]
```

`--mvp` combinado com `--slug` é `MODO_INVALIDO`. Slug inválido é recusado antes da criação da fase.

## 3. JSON operacional no stdout

O JSON transitório contém `rota`, `modo`, `vibeflow`, `phases`, `next_n`, `existing`, `aberta`, `mvp`, `alvo`, `created`, `actions` e `avisos`. `files` lista somente os seis artefatos da cadeia.

Quando o apply cria um arquivo, `actions` registra `criar_arquivo`. Quando o destino já existe, a ação não substitui bytes e o JSON mantém o estado observado. O JSON não carrega estado de rascunho temporário nem contrato de promoção.

## 4. Apply e escrita direta

1. O motor reexecuta o inventário e valida o modo.
2. No modo phase, cria a pasta calculada e prepara `interview.md` vazio.
3. No modo MVP, prepara `.vibeflow/mvp/interview.md` sem criar uma phase.
4. Se o arquivo vivo já existir e for regular, preserva seus bytes.
5. O motor emite o JSON operacional no stdout e não escreve markdown semântico.
6. A IA escreve ou atualiza diretamente `interview.md`, mantendo `# Status: rascunho` enquanto houver elaboração.

O apply não usa arquivo intermediário, não transporta conteúdo entre arquivos e não remove o vivo. A escrita é concorrente-segura no ponto de criação: se outra operação criar o arquivo primeiro, o conteúdo é preservado.

## 5. Artefato e MVP

O template é único. A entrevista phase usa Solicitação, Hipótese inicial, Trilha, Resultado e Handoff. O modo MVP acrescenta cobertura, mapa do produto, direção técnica, direção visual, operação e decisões críticas; seções exclusivas são omitidas no modo phase.

Em entrevista de fluxo ou software, o Mapa do produto exige tabela de jornadas com Jornada, Ator, Gatilho, Objetivo, Telas envolvidas, Entrada, Saída e Estado crítico, e checklist de acesso com login, cadastro, recuperação, sessão, papéis, primeiro usuário, bloqueio e logout, com N/A explícito quando não aplicável. Jornada sem saída ou sem estado crítico não fecha. Texto livre sem tabela é defeito.

O interview MVP não publica decisões em `REGRAS.md`. O handoff da entrevista é `vibe-spec`; a aprovação e o caminho permanecem no arquivo vivo.

## 6. Erros e testes

Falhas previstas usam `CODIGO: descrição` no stderr, sem stack operacional. Os contratos cobrem ausência de init, tipos inesperados, slug, criação phase/MVP, idempotência, preservação byte a byte, ponteiros de alvo e paridade Python/PowerShell quando disponível.

Suítes: `docs/vibe-interview/tests/test-interview.py` e `docs/vibe-interview/tests/test-interview.sh`.

## 7. Limites

- Uma entrevista pertence a uma única phase ou ao baseline MVP.
- O script não preenche, aprova ou interpreta o markdown.
- O inventário seleciona paths; a IA abre somente as entradas e dependências necessárias, usando `rg --files` e `rg -n` quando precisar localizar evidência.
- `init → interview → spec` pode permanecer no mesmo chat. A troca de chat é opcional nesta porta; o arquivo vivo é a fonte de continuidade.
- Sem commit automático. O arquivo vivo entra no Git; o JSON operacional é transitório no stdout.
