# Escopo do vibeflow: feito e na fila

Este arquivo substitui a seção `Fora (v1)` que existia no fim de cada `SKILL.md`. Aquela seção misturava três coisas: invariante operacional que o agente precisa ler durante a run, anti-padrão de escrita do artefato, e escopo de produto ainda não construído. Invariante e anti-padrão voltaram para o corpo da skill, onde são lidos no momento em que valem. Escopo de produto vive aqui.

Convenção: `[x]` já existe no repositório hoje. `[ ]` entra, ainda não construído.

## 1. Cadeia de skills

- [x] `vibe-init` — fonte única de regras e ponteiros.
- [x] `vibe-interview` — fecha intenção ambígua.
- [x] `vibe-spec` — grava o decidido.
- [x] `vibe-plan` — fatia a spec em T*.
- [x] `vibe-analyze` — cruza interview, spec e plan.
- [x] `vibe-implement` — executa a fatia com prova.
- [x] `vibe-review` — julga o patch e grava o veredito.
- [ ] `vibe-design` — grava `design.md` entre spec e plan somente com UI visível, com N/A explícito sem tela. Motores, SKILL, template e distribuição entram em tasks próprias, sem mudar a contagem da distribuição nesta task.
- [ ] **Rota MVP.** Projeto novo usa baseline único em `.vibeflow/mvp/` e percorre interview, spec, plan, analyze, implement e review. Pivôs posteriores voltam às phases.

Nenhuma skill dispara a seguinte. O handoff é uma linha no artefato.

## 2. Infra feita

- [x] **CI.** `.github/workflows/contrato.yml` roda as suítes `docs/vibe-*/tests/` (Python + `test-init.ps1` + `test-*.sh`), `docs/tests/test-distribuicao.py` e o gitleaks em todo push e PR. Sem lockfile neste repo, não há job de CVE/SCA até existir dependência pinada.
- [x] **Teste do launcher `.sh`.** `docs/vibe-*/tests/test-<nome>.sh` + harness em `docs/tests/launcher-harness.sh`.

## 3. Entrou nesta rodada

Contrato do que acabou de entrar. Não é fila aberta.

### 3.1 `implement.md`

- [x] Artefato próprio na pasta da fase, com `--apply` / `--slug` e escrita direta no vivo.

A implement deixa de só marcar `[x]` no `plan.md` / `spec.md` / `review.md`. Na mesma pasta grava `implement.md`. A review e a próxima fatia leem isso no disco, não no chat. O arquivo vivo é preparado pelo script e preenchido pela IA.

O arquivo registra, por fatia:

| Campo | Para que serve | Fecha quando |
|---|---|---|
| Fatia | T* / R* desta run | Sempre presente |
| Feito | O que mudou (paths) | Sempre presente |
| Marcado | Quais `[x]` foram virados, em qual arquivo | Sempre presente |
| Prova | Comando e resultado | Sempre presente |
| Feedback + | O que correu e deve se repetir | Omitir se vazio |
| Feedback − | O que emperrou, dívida, risco, decisão assumida | Omitir se vazio |
| Para a review | O que a próxima porta precisa olhar | Omitir se nada além da prova |

`--apply` e `--slug` fazem parte da preparação do alvo. O `--apply` não transporta conteúdo temporário, não calcula hash de promoção e não substitui um vivo existente. Contrato: `docs/vibe-implement/ARQUITETURA.md`.

### 3.2 `review.md` único, checklist por etapa

- [x] Mesmo arquivo. Campos abrem e fecham. Item longo = várias etapas no vivo.

Não nasce segundo `review.md`. `## Re-review` no rodapé, como dump da rodada, não é o molde. O arquivo é o mapa do julgamento: a checklist cresce com o achado e encolhe com a prova.

Fluxo de um item longo:

```
implement (fatia) → review etapa 1
       ↑                    |
       |    R* em [ ]       v
       +← implement corrige
                            |
                     review etapa 2 (mesmo arquivo)
                            |
              R* novo? abre. R* provado? fecha.
                            |
                     …até veredito vigente Approve
```

Cada etapa registra o que olhou, o que abriu, o que fechou e o veredito **daquela** etapa. O veredito vigente é o da última etapa. Etapas anteriores não se apagam.

#### O que já existe no arquivo (sempre)

| Campo | Papel |
|---|---|
| Cabeçalho (título, pasta, status) | Identidade do vivo |
| Contexto (alvo, cadeia, o que muda) | Uma casa por fase |
| Checklist de correções (R*) | Fila da implement |
| Veredito vigente | Approve / Request changes / Approve com defer |
| Handoff | `vibe-implement` / `volta vibe-spec` / cadeia fechada |

#### O que abre só quando a etapa precisa

| Campo | Abre quando | Fecha / some quando |
|---|---|---|
| Cobertura A*/C* | Existe `spec.md` | Spec não existe: seção omitida |
| R* Critical / Required / Nit | Achado com `path` + evidência | `[x]` quando a implement provou. Lista vazia some. Sem bloqueio: uma linha “nenhum bloqueio” |
| R* extra na mesma lista | Achado novo em etapa posterior. Número novo. Não renumerar fechados | Idem |
| Visual (browser, screenshot, leitura) | O diff desta etapa toca UI | Diff sem UI: omitir |
| Segurança | O diff toca input, auth, segredo, upload, pagamento, LLM ou dado pessoal | Diff sem isso: omitir. Sem catálogo fixo |
| DoD | Há item aplicável nesta etapa | Tudo N/A: omitir |
| Notas | Há algo que não cabe num R* (teto 5 linhas) | Vazio: omitir |
| Etapa N | Sempre que a review rodar de novo no mesmo pedido | Nunca apaga etapa antiga. Só acrescenta |

#### Molde de uma etapa (o que falta no template hoje)

```
## Etapas

### Etapa 1 — first-pass — <o que olhou: T* / diff / fatia>
- Abriu: R1, R2 (ou nenhum)
- Fechou: —
- Veredito desta etapa: Request changes

### Etapa 2 — depois de implement — <o que olhou: R1, R2 + regressão>
- Leu: implement.md da fatia, se existir
- Abriu: R3 (achado novo)
- Fechou: R1, R2
- Veredito desta etapa: Request changes
```

Status do arquivo: `rascunho` na primeira passagem; `request-changes` enquanto houver R* bloqueante em `[ ]`; `aprovado` quando o veredito vigente for Approve e o humano confirmou.

Contrato: `docs/vibe-review/ARQUITETURA.md` e `templates/review.md` antes de mudar a skill.

### 3.3 Fila elegível e prova em três andares

- [x] Relatório da implement ganha `fila` (`elegiveis` / `bloqueadas`). Skill pergunta só se houver 2+ T* prontas.
- [x] Plan congela `concluída`, `Deps` reais e Verificação como comando. Cada T* é a unidade de execução, prova e commit; o fechamento da phase usa a suíte final da review.

### 3.6 Commits por task e fechamento da phase

- [x] `vibe-implement` cria um commit path-scoped depois de cada task verde, sem push, sem `git add -A` e sem misturar paths já alterados.
- [x] `vibe-review` só faz o commit residual e o `git push` final depois de Approve, confirmação humana, correções fechadas, suíte final, `git diff --check` e gitleaks quando previsto.

### 3.4 Distribuição Codex, Claude, Grok e Antigravity

- [x] CLI `npx skills add korflux/vibeflow` (projeto ou `-g` global) para `grok`, `claude-code`, `codex`, `antigravity`.
- [x] Manifests nativos: `.claude-plugin/`, `.codex-plugin/`, `.agents/plugins/`, `.grok-plugin/`, `plugin.json` (Antigravity). Pasta `skills/` aponta para `vibe-<nome>/`. Sem aliases `/spec` `/plan`.

### 3.5 Size por complexidade e Risk separado

- [x] `vibe-plan` classifica T* por cinco dimensões pontuadas de 0 a 2, com `0–3 = low`, `4–6 = medium`, `7–8 = high` e quebra obrigatória em `9–10`.
- [x] `Risk` é registrado separadamente de `Size`; tempo e quantidade de arquivos não são critérios isolados.
- [x] Template, arquitetura, análise, README e testes de contrato refletem a mesma regra sem alterar o parser mecânico.

## 4. Limites de contrato

Não são backlog. Mudá-los quebra o disco.

| Limite | Por quê |
|---|---|
| `AGENTS.md` e `CLAUDE.md` nunca são cópia de `REGRAS.md` | Cópia diverge na primeira edição e deixa de existir fonte única. Sem symlink, o init falha alto. |
| Artefato da cadeia só em `.vibeflow/phases/phase-N-slug/`, salvo o baseline único `.vibeflow/mvp/` | `docs/`, `specs/` e paths de outro produto continuam proibidos; a exceção MVP é fixa, explícita e não versionada. |
| Segunda fonte de regras fora de `.vibeflow/REGRAS.md` | Mesma razão. A ponte Antigravity é apenas `@../../.vibeflow/REGRAS.md`, não uma cópia. |
| A IA não escolhe `n`, slug nem path | Disco decide, script calcula. |
| A IA não escolhe homolog ou produção | Só o humano sabe, e a resposta muda o bloco de migrations. |
| Commit por task e push final | Implement commita cada task verde com staging explícito; review fecha a phase e faz push somente após aprovação humana. |
| Motor único ("só Python" ou "só PowerShell") | Os dois motores implementam o mesmo contrato; o launcher `.sh` escolhe, sem versão degradada. |
| Escrita semântica no script ou em arquivo temporário de promoção | O script prepara o vivo e a IA grava a prosa, preservando o histórico já existente. |

## 5. Anti-padrões (já no corpo da skill)

| Anti-padrão | Onde vive agora |
|---|---|
| `FR-00N`, mural de user story, CSS/paleta na spec | `vibe-spec`, passo "Escrever e salvar já" |
| `T001`, `[P]`, `[US1]`, `tasks.md`, `checklists/` | `vibe-plan`, passos "Conferência" e "Fatiar" |
| `todo.md` / `tasks.md` como saída da implement | `vibe-implement`, invariante do topo |
| Editar `interview.md`, `spec.md`, `plan.md` na analyze | `vibe-analyze`, invariante do topo |
| Editar source, teste ou lockfile na review | `vibe-review`, invariante do topo e passo "Julgar" |
| Marcar `[x]` sem prova, pular verificação visual em silêncio | `vibe-implement`, invariante do topo e gate |
| Verificação só manual / leitura como prova da T* | `vibe-plan` (fatiar) e `vibe-implement` (ciclo) |
| Open Questions dentro do artefato, dump do artefato no chat | invariante do topo de cada skill que grava |
