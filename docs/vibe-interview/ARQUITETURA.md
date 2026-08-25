# vibe-interview: arquitetura

`vibe-interview` fecha intenção ambígua antes de spec, plan ou código. Há dois alvos explícitos:

```text
.vibeflow/phases/phase-<n>-<slug>/interview.md
.vibeflow/mvp/interview.md
```

O primeiro atende mudanças delimitadas. O segundo registra uma única baseline histórica de produto novo e inicia obrigatoriamente a rota max. A IA escolhe o alvo e conduz a semântica; o motor apenas inventaria, valida paths e promove bytes.

## 1. Papéis

| Peça | Responsabilidade |
|---|---|
| `SKILL.md` | Classificar produto ou feature, entrevistar, recomendar, preencher wip e chamar o modo explícito |
| `references/mvp-discovery.md` | Catálogo interno e condicional de cobertura, baselines e recomendações do MVP |
| `templates/interview.md` | Esqueleto único; seções MVP são omitidas no modo phase |
| Motores `.py` e `.ps1` | Inventário, slug de phase, validação de alvo, cópia, hash, relatório e erros curtos |
| Launcher `.sh` | Encaminhar as mesmas flags ao Python 3 ou PowerShell 7 |
| IA | Entender o motor usado, decidir o modo, pilotar conversa e escrever prosa |
| Humano | Resolver somente decisões críticas que não podem ser assumidas com segurança |

O motor não detecta MVP pelo texto, não escreve markdown, não escolhe stack e não atualiza `REGRAS.md`.

## 2. Dependência e paths operacionais

Sem `.vibeflow/`, o motor encerra com `INIT_AUSENTE`. Se `phases/` não existe, cria o diretório e `.gitkeep`, preservando o contrato phase.

| Path | Papel | Git |
|---|---|---|
| `.vibeflow/interview-wip.md` | sessão ainda não promovida | ignorado |
| `.vibeflow/interview-report.json` | contrato motor para IA | ignorado |
| `.vibeflow/phases/phase-N-slug/interview.md` | entrevista normal viva | commitável |
| `.vibeflow/mvp/interview.md` | baseline MVP viva e única | commitável |

`mvp` inexistente significa alvo disponível. Um arquivo no lugar de `.vibeflow/mvp/` é `MVP_INESPERADO`. `interview.md` já existente é `MVP_EXISTE` no apply e nunca é sobrescrito. Evoluções posteriores usam phase max e substituição crítica explícita.

## 3. Interface pública

```text
python interview.py [--root PATH] [--apply] [--slug TEXTO] [--mvp]
pwsh interview.ps1 [-Root PATH] [-Apply] [-Slug TEXTO] [-Mvp]
bash interview.sh [--root PATH] [--apply] [--slug TEXTO] [--mvp]
```

`--mvp` e `--slug` juntos produzem `MODO_INVALIDO`. No modo phase, `--apply` exige slug. No modo MVP, apply não aceita nem precisa de slug.

## 4. Inventário e relatório

O relatório mantém o schema phase e acrescenta `rota`, `modo`, `mvp` e `alvo`:

```json
{
  "modo": "mvp",
  "vibeflow": "ok",
  "phases": "ok",
  "next_n": 3,
  "existing": [],
  "aberta": null,
  "mvp": {
    "kind": "mvp",
    "dir": "mvp",
    "path": ".vibeflow/mvp",
    "files": ["interview.md"]
  },
  "alvo": {
    "kind": "mvp",
    "dir": "mvp",
    "path": ".vibeflow/mvp",
    "files": ["interview.md"]
  },
  "wip": "ausente",
  "created": null,
  "actions": [],
  "avisos": []
}
```

Objetos de phase recebem `kind: "phase"`. `alvo` aponta para `mvp` no modo MVP e para `aberta` no modo phase. Quando o diretório MVP ainda não existe, `mvp` e `alvo` são `null`. `files` lista apenas `interview.md`, `spec.md`, `plan.md`, `analyze.md`, `implement.md` e `review.md` existentes.

## 5. Apply phase

O contrato anterior permanece:

1. Recalcular inventário e `next_n` numericamente.
2. Exigir wip e slug sanitizável.
3. Recusar destino existente.
4. Criar `phase-N-slug/interview.md` com os bytes do wip.
5. Comparar tamanho e SHA-256.
6. Remover wip somente após a conferência.
7. Atualizar relatório com `created.kind = "phase"`.

## 6. Apply MVP

1. Recalcular inventário em modo MVP.
2. Exigir wip.
3. Recusar `.vibeflow/mvp/interview.md` existente com `MVP_EXISTE`.
4. Criar `.vibeflow/mvp/` somente se necessário.
5. Copiar binariamente o wip para `mvp/interview.md`.
6. Comparar tamanho e SHA-256.
7. Em falha, remover apenas o destino novo e o diretório se ele foi criado e está vazio. Preservar wip.
8. Remover wip somente após sucesso.
9. Atualizar relatório com `created.kind = "mvp"`.

Nenhuma phase é criada pelo apply MVP. O motor pode garantir `phases/.gitkeep` durante o inventário comum, mas isso não constitui phase.

## 7. Artefato semântico

As seções comuns são Solicitação, Hipótese inicial, Trilha, Resultado, Direção e Handoff. No modo MVP, acrescentam-se:

| Seção | Conteúdo |
|---|---|
| Cobertura do MVP | Domínios relevantes em `DECIDIDO`, `ASSUMIDO`, `N/A` ou `PENDENTE CRÍTICO`, sempre com evidência |
| Mapa do produto | Jornadas, telas, estados, acesso, usuários, dados, arquivos, integrações e notificações |
| Direção técnica | Repo, stack, banco, validação, infraestrutura, ambientes e deploy |
| Direção visual | Identidade, temas, cor, tokens, fonte e acessibilidade |
| Operação | Segurança, privacidade, analytics, backup, restore, suporte e custos |
| Decisões críticas | IDs estáveis, estado, decisão, motivo e impacto |

O modo MVP não fecha com `PENDENTE CRÍTICO`. O handoff é `vibe-spec` e `rota: max`. O modo phase omite integralmente as seções exclusivas de MVP.

## 8. Erros previstos

| Código | Condição |
|---|---|
| `INIT_AUSENTE` | `.vibeflow/` ausente |
| `PHASES_INESPERADO` | `phases` existe e não é diretório |
| `MVP_INESPERADO` | `mvp` existe e não é diretório |
| `MODO_INVALIDO` | combinação incompatível de modo e slug |
| `WIP_AUSENTE` | apply sem wip |
| `SLUG_AUSENTE` / `SLUG_INVALIDO` | apply phase sem slug válido |
| `FASE_EXISTE` | destino phase já existe |
| `MVP_EXISTE` | baseline MVP já contém interview |
| `COPY_HASH_MISMATCH` | tamanho ou SHA-256 diverge após cópia |

Falhas previstas usam `CODIGO: descrição` no stderr e não exibem stack.

## 9. Testes de contrato

- Todos os contratos phase anteriores continuam verdes.
- Inventário distingue `kind: phase` e `kind: mvp`.
- Apply MVP promove bytes exatamente para `mvp/interview.md` e não cria `phase-N`.
- Segundo apply MVP recusa sobrescrita e preserva wip.
- Path `mvp` inesperado e combinação MVP com slug são recusados.
- Python, PowerShell quando disponível e launcher Unix aceitam o mesmo modo.

Backlog e limites globais vivem em [`docs/ESCOPO.md`](../ESCOPO.md).
