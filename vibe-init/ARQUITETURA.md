# vibe-init — arquitetura

`/vibe-init` deixa um repo com **uma** fonte de regras e dois ponteiros.

```
.vibeflow/REGRAS.md          ← único arquivo editável
.vibeflow/old/               ← cópia intacta de tudo que era do usuário
.vibeflow/phases/            ← pasta da cadeia (criada vazia no init)
AGENTS.md                    ← symlink → .vibeflow/REGRAS.md
CLAUDE.md                    ← symlink → .vibeflow/REGRAS.md
```

Dois fluxos. O script **inventaria primeiro**, escolhe o fluxo e só então mexe. Arquivo do usuário **nunca** some: antes de substituir, mover o papel ou apagar, o script copia para `.vibeflow/old/` e só segue se a cópia bater (tamanho + hash). A IA recebe o relatório, une fontes diferentes no `REGRAS.md` e faz as perguntas pré-definidas **mais** o que o contexto exigir. Não inventa fato que o disco não mostrou.

---

## 1. Fluxos

O script classifica **antes** de criar qualquer coisa.

| Fluxo | Quando |
|---|---|
| **NOVO** | Não existe `.vibeflow/`, não existe `.vibeflow/REGRAS.md`, não existe `REGRAS.md` na raiz, não existe `AGENTS.md`, não existe `CLAUDE.md` |
| **ATUALIZAR/REPARAR** | Qualquer uma dessas peças existe (pasta, arquivo, symlink quebrado, arquivo legado) |

Não há flag. Disco decide. Se o humano disser “repara” num repo limpo, cai em NOVO.

Regra de ouro do reparo:

- Falta peça → cria.
- Quebrado sem conteúdo → repara.
- Arquivo do usuário no caminho → **old primeiro**, depois age.
- Dois textos diferentes → IA **une tudo** no `REGRAS.md` (não escolhe um e descarta o outro).
- Contradição A vs C (um diz X, o outro diz não-X) → os dois entram marcados e a IA pergunta qual vale. Não sorteia.

---

## 2. Inventário (sempre o primeiro passo)

Raiz = `git rev-parse --show-toplevel` se houver git, senão cwd.

O script classifica cada peça e grava no relatório. **Zero escrita** nesta fase.

### 2.1 Pasta `.vibeflow/`

| Estado | Significa |
|---|---|
| `ausente` | não existe |
| `vazia` | existe, sem `REGRAS.md` |
| `com_regras` | existe `REGRAS.md` |
| `sem_regras` | existe, tem outros arquivos, sem `REGRAS.md` |

Nunca apaga o que já estiver dentro da pasta (incluindo `old/` e `phases/`).

O script **sempre** garante `.vibeflow/phases/` (NOVO e REPARAR). Se já existe, não limpa.

### 2.2 `REGRAS.md`

Procura `.vibeflow/REGRAS.md` e, à parte, `REGRAS.md` na raiz (nome errado / leftover).

| Estado | Significa |
|---|---|
| `ausente` | não existe |
| `vazio` | só whitespace |
| `template` | tem `<!-- SLOT:… -->` ainda aberto |
| `preenchido` | slots obrigatórios fechados |
| `raiz_sozinho` | só existe na raiz do repo |
| `raiz_e_vibeflow` | os dois existem (ver merge) |

Windows é case-insensitive: `regras.md` = `REGRAS.md`.

### 2.3 Ponteiro (`AGENTS.md` e `CLAUDE.md` — cada um separado)

| Estado | Significa |
|---|---|
| `ausente` | não existe |
| `vazio` | arquivo regular, sem conteúdo |
| `symlink_ok` | link cujo alvo resolve para `.vibeflow/REGRAS.md` (path normalizado) |
| `symlink_quebrado` | link cujo alvo não existe |
| `symlink_outro` | link para outro arquivo que existe |
| `arquivo_igual` | arquivo regular cujo conteúdo = `REGRAS.md` (checkout Git no Windows sem symlink) |
| `arquivo_legado` | arquivo regular com conteúdo próprio |
| `inesperado` | diretório ou tipo que não é arquivo/link |

“Alvo resolve para REGRAS” compara o path canônico, não a string do link.

---

## 3. Old — arquivo do usuário não some

Qualquer conteúdo que o usuário (ou o time) já tinha e que o fluxo vai **deixar de ser o arquivo editável** vai para `.vibeflow/old/` **antes** da ação. Sem old verificado, a ação não roda.

### 3.1 O que entra em old

| Peça | Quando | Nome em `old/` |
|---|---|---|
| `AGENTS.md` arquivo regular com conteúdo (`legado` ou `arquivo_igual`) | antes de virar symlink | `AGENTS.md` |
| `CLAUDE.md` idem | idem | `CLAUDE.md` |
| `REGRAS.md` na raiz | antes de mover ou apagar | `REGRAS-raiz.md` |
| `.vibeflow/REGRAS.md` | só se a IA for **reescrever** por merge (duas fontes / legado vs regras / regras duplicado) | `REGRAS.md` |
| `symlink_outro` que o humano mandou redirecionar | não copia o alvo (é outro doc); grava o path antigo | `AGENTS.target.txt` ou `CLAUDE.target.txt` |

Não gera old para: arquivo vazio, symlink quebrado, symlink_ok, peça `ausente`. Não há o que preservar.

### 3.2 Como grava (nunca sobrescreve um old)

1. Garante `.vibeflow/old/`.
2. Destino = `.vibeflow/old/<nome>`.
3. Se esse path **já existe**, não pisa: usa `.vibeflow/old/<nome>.<yyyyMMdd-HHmmss>`. O first old é o mais original.
4. Cópia binária do arquivo (não “limpa” markdown).
5. Confere tamanho + hash (SHA-256). Se não bater → **para a peça**, não substitui o original.
6. Só então: merge / move / apaga / troca por symlink.

`old/` entra no git (é o seguro do time). `init-report.json` continua de fora.

### 3.3 Ordem obrigatória no reparo

```
old verificado  →  merge no REGRAS (se precisar)  →  original vira symlink / some
```

Inverter isso é bug: um crash no meio apagaria o arquivo do usuário.

---

## 4. Fluxo NOVO

Repo limpo. Sem old (não há arquivo do usuário).

```
[1] INVENTÁRIO  →  fluxo=novo
[2] mkdir .vibeflow, .vibeflow/old (se for usar), .vibeflow/phases
[3] copia template → .vibeflow/REGRAS.md
[4] SCAN do disco → preenche só SLOTs factuais (nome, estrutura, stack, evidência do parágrafo)
[5] cria AGENTS.md e CLAUDE.md como symlink relativo → .vibeflow/REGRAS.md
[6] grava init-report.json + pacote de contexto
[7] IA lê o contexto, preenche REGRAS.md
    — perguntas pré-definidas (obrigatórias)
    — mais as que o contexto pedir (a IA decide)
[8] fecha
```

Se o OS recusar symlink: **para**, instrução de Developer Mode / admin. Não copia o arquivo. Cópia na raiz diverge.

Script não commita.

---

## 5. Fluxo ATUALIZAR/REPARAR

```
[1] INVENTÁRIO  →  fluxo=reparar + mapa de estados
[2] aplicar a matriz, nesta ordem:
      a. pasta .vibeflow (+ phases/ sempre; + old/ se for gravar cópia)
      b. OLD de toda peça que esta run vai mexer
      c. resolver REGRAS.md   ← alvo dos links precisa existir;
         se houver mais de uma fonte de texto → marca merge, NÃO escolhe
      d. AGENTS.md / CLAUDE.md só viram symlink DEPOIS do merge fechado
      e. leftover REGRAS.md na raiz
[3] SCAN: preenche só SLOT factual ainda aberto; não toca seção sem SLOT
[4] relatório: ações, olds gravados, merges pendentes, conflitos restantes
[5] IA:
      — se merge pendente: lê os olds, une tudo no REGRAS.md, mostra de onde veio o quê
      — depois: slots + pré-definidas ainda abertas + extras se o contexto pedir
      — se tudo saudável e sem SLOT e sem merge → não reentrevista; “já ok”
[6] script (ou skill) troca originais por symlink só com old ok + REGRAS já unificado
[7] fecha
```

Peças independentes seguem em paralelo **exceto** quando o merge de REGRAS ainda não fechou: aí os arquivos legado **não** viram symlink (o original continua no lugar, já copiado em `old/`).

---

## 6. Matriz — uma decisão por peça

### 6.1 `.vibeflow/`

| Estado | Ação |
|---|---|
| `ausente` | criar + `phases/` |
| `vazia` / `sem_regras` / `com_regras` | manter; não limpar; criar `phases/` se faltar |

### 6.2 Resolver `REGRAS.md`

| REGRAS | AGENTS legado | CLAUDE legado | Ação |
|---|---|---|---|
| `ausente` ou `vazio` | não | não | criar/escrever template |
| `ausente` ou `vazio` | sim, um dos dois | o outro não é legado **ou** é igual | old do legado → template + **merge IA** (uma fonte; na prática cola o único texto nas seções certas) → depois legado vira symlink |
| `ausente` ou `vazio` | sim | sim, **conteúdo diferente** | old dos dois → template → **MERGE** `duas_fontes` (IA une) → só então os dois viram symlink |
| `template` ou `preenchido` | legado diferente do REGRAS | — | old do legado (+ old do REGRAS se a IA for reescrever) → **MERGE** `legado_vs_regras` |
| `raiz_sozinho` | — | — | old `REGRAS-raiz.md` → mover para `.vibeflow/REGRAS.md` |
| `raiz_e_vibeflow`, conteúdos iguais | — | — | old da raiz → apagar a raiz (`.vibeflow/` já tem a cópia viva) |
| `raiz_e_vibeflow`, conteúdos diferentes | — | — | old dos dois → **MERGE** `regras_duplicado` no de `.vibeflow/` → apagar a raiz |

O script **não** mescla prosa. Ele só: old, template se faltar, marca `merges[]` com os paths dos olds. Quem une é a IA.

### 6.3 Ponteiro `AGENTS.md` / `CLAUDE.md` (cada um)

Depende de REGRAS existir **e** de não haver merge pendente que ainda use este arquivo como fonte.

| Estado do ponteiro | Ação |
|---|---|
| `ausente` | criar symlink → `.vibeflow/REGRAS.md` |
| `vazio` | trocar por symlink (sem old) |
| `symlink_ok` | nada |
| `symlink_quebrado` | recriar symlink para REGRAS |
| `arquivo_igual` | old → trocar por symlink |
| `symlink_outro` | **CONFLITO** `ponteiro_alheio` (ainda pergunta: o alvo é outro doc). Se redirecionar: grava `*.target.txt` em old/ |
| `arquivo_legado` e merge desta fonte já escrito no REGRAS | old já feito → trocar por symlink |
| `arquivo_legado` e merge ainda pendente | não toca o original |
| `inesperado` | **CONFLITO** `tipo_inesperado`. Não toca |

### 6.4 Mapa mental

| O que o disco tem | Fluxo | O que acontece |
|---|---|---|
| Nada | NOVO | pasta, `phases/`, template, scan, dois links |
| Só `.vibeflow/` vazia | REPARAR | cria `phases/` + REGRAS + dois links |
| `.vibeflow/` sem `phases/` | REPARAR | só cria `phases/` (e o que mais faltar) |
| `.vibeflow/` + REGRAS, sem ponteiros | REPARAR | só os dois links |
| Tudo ok, SLOTs abertos | REPARAR | IA continua perguntas |
| Tudo ok, sem SLOT | REPARAR | “já ok”; sem old, sem reentrevista |
| Só `AGENTS.md` arquivo | REPARAR | old → merge no REGRAS → AGENTS vira link → cria CLAUDE |
| Só `CLAUDE.md` arquivo | REPARAR | simétrico |
| AGENTS e CLAUDE **iguais** | REPARAR | old dos dois → um merge (texto único) → os dois viram link |
| AGENTS e CLAUDE **diferentes**, sem REGRAS | REPARAR | old dos dois → IA une tudo no REGRAS → os dois viram link |
| REGRAS existe + AGENTS arquivo diferente | REPARAR | old do AGENTS (+ REGRAS se for reescrito) → IA une o que o AGENTS tem e o REGRAS ainda não → AGENTS vira link |
| AGENTS link quebrado | REPARAR | recria o link |
| AGENTS link para outro arquivo | REPARAR | pergunta; não come o alvo |
| AGENTS arquivo = REGRAS | REPARAR | old → vira link |
| `REGRAS.md` só na raiz | REPARAR | old da raiz → move para `.vibeflow/` |
| REGRAS raiz **e** `.vibeflow/`, iguais | REPARAR | old da raiz → apaga a raiz |
| REGRAS raiz **e** `.vibeflow/`, diferentes | REPARAR | old dos dois → IA une no de `.vibeflow/` → apaga a raiz |
| AGENTS é uma pasta | REPARAR | não toca |
| Falha de symlink no OS | REPARAR | old já está salvo; original **permanece**; falha alto |

---

## 7. Merge (IA) — unir, não escolher

Quando o relatório tem `merges[]`, a skill **não pergunta “qual arquivo vale?”**. Lê os olds, analisa e escreve **um** `REGRAS.md` que contém a união.

### 7.1 Como une

1. Lê cada path em `merges[].sources` (os olds, não os originais — os originais ainda podem estar no lugar).
2. Lê o template / REGRAS atual (se existir).
3. Para cada regra/trecho:
   - está em qualquer fonte → entra no REGRAS;
   - está igual nas duas → entra **uma** vez (não duplica);
   - está só numa → entra, sem “melhorar” a redação;
   - A diz X e C diz o contrário → os dois entram sob `## Conflito a fechar` com rótulo da origem, e vira **uma** pergunta (qual vale). O perdedor continua no old; some só do REGRAS vivo depois da resposta.
4. Encaixa no template quando o trecho é claramente da seção (parágrafo, ambiente, semver, git, estrutura). O resto vai para `## Regras deste repo`.
5. Política fixa do template (semver, sem Co-Authored-By) entra sempre. Se o legado já tinha um bloco equivalente, não duplica o de semver/git — o do template ganha, o legado equivalente some do vivo (o old guarda o original).
6. Depois de gravar, mostra no chat um mapa curto (5–15 linhas): `de AGENTS: …` / `de CLAUDE: …` / `das duas: …` / `contradição: …`. Sem reimprimir os arquivos.

A IA **não** inventa regra que não estava em fonte alguma. **Não** resume um parágrafo de produto que só existia numa fonte — traz o texto.

### 7.2 O que ainda é pergunta (não é merge)

| Id | Quando | O que a IA faz |
|---|---|---|
| `contradição` | A e C se anulam | Mostra os dois; humano escolhe o que fica no vivo |
| `ponteiro_alheio` | link para outro arquivo | Pergunta se redireciona; default = deixar |
| `tipo_inesperado` | AGENTS/CLAUDE não é arquivo | Não toca; humano resolve fora |

Não existe mais pergunta “usar AGENTS ou CLAUDE?”. Isso virou merge.

---

## 8. Scan (os dois fluxos)

Preenche **só** SLOT com evidência + path. Não inventa.

| SLOT | Fonte (primeira que existir) |
|---|---|
| `nome` | `package.json` name → `pyproject.toml` → `go.mod` → nome da pasta |
| `paragrafo` | 1º parágrafo útil do README (não badge/título) → `description` do manifest → **fica SLOT** (salvo se o merge já trouxe um parágrafo das fontes) |
| `estrutura` | árvore 1–2 níveis; ignora `node_modules`, `.git`, `dist`, `build`, `.next`, `vendor`, `__pycache__` |
| `stack` | manifests presentes |
| `migrations` | `prisma/migrations`, `alembic`, `drizzle`, `knex`, `django`/`migrations`, `supabase/migrations` — boolean |

Em REPARAR: se a seção já não tem SLOT, o scan não mexe. Merge da IA pode preencher `regras` / `paragrafo` a partir dos olds — aí o SLOT some.

---

## 9. Template (texto pronto = só política)

```markdown
# Regras do projeto

## Projeto
<!-- SLOT:paragrafo -->
<!-- evidência: <path ou vazio> -->

## Ambiente
<!-- SLOT:ambiente -->
<!-- homolog | producao -->

## Versão (semver)
- **Major:** quebra contrato (API, schema, comportamento que caller já usa).
- **Minor:** adiciona sem quebrar.
- **Patch:** correção sem mudança de contrato.
- Produção: migration só com plano de rollback; não rodar migration destrutiva sem o humano pedir.

## Git
- Sem `Co-Authored-By` de ferramenta em commit/push.

## Estrutura
<!-- SLOT:estrutura -->

## Regras deste repo
<!-- SLOT:regras -->
```

Bloco extra, **só** se ambiente = produção **e** scan viu migration — texto fixo:

```markdown
## Produção / migrations
Migration em produção é irreversível no sentido prático. Não gerar, não aplicar, não “aproveitar o gancho”. Se a tarefa exigir schema, parar e perguntar.
```

---

## 10. Pacote de contexto (o que a IA lê)

`.vibeflow/init-report.json` (gitignored):

```json
{
  "flow": "novo | reparar",
  "root": "...",
  "inventory": {
    "vibeflow": "ausente|vazia|sem_regras|com_regras",
    "phases": "ausente|ok",
    "regras": "ausente|vazio|template|preenchido|raiz_sozinho|raiz_e_vibeflow",
    "agents": "ausente|vazio|symlink_ok|symlink_quebrado|symlink_outro|arquivo_igual|arquivo_legado|inesperado",
    "claude": "…"
  },
  "olds": [
    { "from": "AGENTS.md", "to": ".vibeflow/old/AGENTS.md", "bytes": 1234, "sha256": "…" }
  ],
  "actions": [{ "op": "criar_dir|criar_phases|escrever_template|old|merge_pendente|mover|symlink_criar|symlink_recriar|apagar_raiz", "alvo": "…" }],
  "merges": [{
    "id": "duas_fontes|legado_vs_regras|regras_duplicado",
    "sources": [".vibeflow/old/AGENTS.md", ".vibeflow/old/CLAUDE.md"],
    "target": ".vibeflow/REGRAS.md"
  }],
  "conflicts": [{ "id": "ponteiro_alheio|tipo_inesperado|contradicao", "peca": "…", "detalhe": "…" }],
  "filled": { "nome": { "value": "x", "from": "package.json" } },
  "slots_abertos": ["paragrafo", "ambiente"],
  "migrations_detectadas": true,
  "symlink_ok": { "agents": true, "claude": true },
  "scan": { "estrutura": ["src"], "stack": ["package.json"], "evidencia_paragrafo": { "from": "README.md", "text": "…" } },
  "avisos": []
}
```

A IA lê: este JSON + `REGRAS.md` atual + **cada path em `merges[].sources`**. Não varre o repo de novo “pra enriquecer”.

---

## 11. Papel da IA

1. Mostra 5 linhas: fluxo, olds gravados, merges, conflitos, slots.
2. Se há `merges[]`: une (§7), grava REGRAS, mostra o mapa de origem. Só então os originais podem virar symlink.
3. Fecha `contradição` / `ponteiro_alheio` / `tipo_inesperado`, um por vez.
4. **Perguntas pré-definidas** — só as que ainda estão SLOT:

   | # | Pergunta | Não perguntar se |
   |---|---|---|
   | P1 | Parágrafo do projeto — mostra extraído ou o que o merge já trouxe | `paragrafo` fechado |
   | P2 | Homolog ou produção? | `ambiente` fechado |
   | P3 | Qual regra deste repo o scan/merge não pega? | humano já ditou nesta run |
   | P4 | Falta alguma informação? | REPARAR saudável sem merge e sem P1–P3 |

5. **Extras** só com evidência no relatório ou na resposta anterior. Sem pergunta “por garantia”.
6. Uma pergunta por vez. Várias respostas de uma vez: aceita e fecha.
7. Patch de pergunta: só o SLOT. Texto do humano, sem “melhorar”.
8. NOVO: P1–P4 obrigatórias (P3 pode ser “nenhuma”). REPARAR saudável sem SLOT e sem merge: para.

---

## 12. Peças desta skill (quando for implementar)

| Peça | Onde | Faz |
|---|---|---|
| Skill | `vibe-init/SKILL.md` | Orquestra, merge, perguntas, patch de SLOT, dispara symlink pós-merge |
| Script | `vibe-init/scripts/init.ps1` (+ `init.sh`) | Inventário → old → matriz → scan → JSON; symlink só com merge já fechado |
| Template | `vibe-init/templates/REGRAS.md` | Esqueleto + política + SLOTs |
| Relatório | `.vibeflow/init-report.json` | Contrato script → IA |
| Old | `.vibeflow/old/` | Cópias intactas |
| Phases | `.vibeflow/phases/` | Pasta da cadeia; init só cria, não escreve arquivo |

Install recomendado: user-scope (`<grok-home>/skills/vibe-init`). Fonte canônica: esta pasta.

Git: commit `REGRAS.md`, os dois symlinks, `.vibeflow/old/` e `.vibeflow/phases/.gitkeep` (pasta vazia não sobrevive no git sem isso). Não commitir `init-report.json`.  
Windows: `core.symlinks=true` é aviso, não forçado. Sem privilegio de link: falha alto; original fica (old já está).

---

## 13. Contratos de teste (script, sem framework)

1. Repo vazio → NOVO: pasta, `phases/`, template, dois symlinks; sem `old/`.
2. Sem README/description → `paragrafo` fica SLOT.
3. Só `.vibeflow/` vazia → REPARAR cria `phases/` + REGRAS + dois links.
3b. `.vibeflow/` existe sem `phases/` → cria só `phases/` (e o que mais a matriz pedir).
4. REGRAS existe, falta CLAUDE → só cria CLAUDE; não reescreve REGRAS; sem old.
5. Só `AGENTS.md` legado → `old/AGENTS.md` igual ao original → REGRAS marcado merge → depois do merge o AGENTS da raiz é symlink.
6. AGENTS ≠ CLAUDE, sem REGRAS → old dos dois + `merges` `duas_fontes`; **não** apaga os originais enquanto o merge não gravou REGRAS.
7. Segunda run: `old/AGENTS.md` já existe e o AGENTS da raiz voltou a ser arquivo → novo old com timestamp; o first old intacto.
8. AGENTS arquivo = conteúdo de REGRAS → old + vira symlink.
9. Hash do old ≠ original → script **não** substitui o original.
10. Tudo `symlink_ok` sem SLOT → `actions` vazio, sem old novo.
11. `REGRAS.md` só na raiz → old `REGRAS-raiz.md` + move.
12. Crash simulado depois do old e antes do symlink → originais ainda no lugar; old presente.

(Merge da IA — união / sem invenção / contradição marcada — é contrato da skill, não do script.)

---

## 14. Fora (v1)

- Outras skills `vibe-*`, CI, hook, `--force`.
- Fallback de copiar REGRAS para AGENTS/CLAUDE na raiz.
- A IA escolher homolog/produção sozinha, ou inventar regra que não estava em fonte/scan/humano.
- Spec/plan/todo.

---

## 15. Assumido até você contradizer

- Semver + “sem Co-Authored-By” entram sempre (política).
- Old nunca é sobrescrito; colisão vira timestamp.
- `old/` commita; relatório não.
- AGENTS ≠ CLAUDE → união pela IA, não menu “qual vale”.
- Só pergunta em contradição real, ponteiro alheio ou tipo inesperado.
- REPARAR saudável não reentrevista.
- Symlink ou falha alto — sem cópia na raiz.
