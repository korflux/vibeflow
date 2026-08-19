---
name: vibe-review
description: >
  Julga o patch e a cobertura pós-código e grava .vibeflow/phases/phase-N-slug/review.md.
  Use when the user runs /vibe-review, pede review, revisa isso, LGTM, pode
  mergear, ou há handoff de vibe-implement / rota medium+ — mesmo que não
  diga vibe-review.
---

# vibe-review

Não invente `n` se há plan. Não edite source, teste nem lockfile. Sem `review.md` não há veredito.
Um arquivo por fase. Sem `.vibeflow/`: `/vibe-init`. Open Questions no arquivo = defeito. Não commita.

## 0. Script primeiro

1. Resolva o diretório desta skill.
2. No cwd do repo:
   - Windows: `pwsh "<skill>/scripts/review.ps1"`
   - Unix: `bash "<skill>/scripts/review.sh"` (Python 3, senão pwsh 7)
3. Leia `.vibeflow/review-report.json`. Se `alvo`, leia o que `files` listar (inclui `implement.md` se existir). Leia `.vibeflow/REGRAS.md`. Diff: o que o humano apontou, ou o working tree da sessão. Não varrer a árvore.

`INIT_AUSENTE` → init. `REVIEW_SEM_ALVO` / `FASE_AUSENTE` / `WIP_AUSENTE` / `SLUG_INVALIDO` → não contorne.

Apply:
- first-pass reuse/atualizar: `pwsh "<skill>/scripts/review.ps1" -Apply` (`--dir` se o alvo errar)
- avulsa sem cadeia: `… -Apply -Slug "<frase curta>"`
- Unix: `review.sh --apply` / `--apply --slug "…"`

## 1. Abrir (5 linhas)

etapa · alvo · plan · spec · implement · diff

```
etapa 1 first-pass · alvo: phase-2-vibe-review · plan: sim · spec: sim · implement: sim · diff: working tree
```

`modo_sugerido=criar` e sem `--slug` = não há pasta. Não grude review nova no N de outro pedido.
Já existe `review.md` = próxima etapa no **mesmo** arquivo.

## 2. Gate

| | Ação |
|---|---|
| Sem alvo e sem diff | **Para.** Peça path, branch, PR ou `--dir` |
| T* obrigatórias em `[ ]` e o humano pediu “pronto da feature” | Recuse Approve de feature. Pode revisar o diff e listar o que falta no plan |
| Intenção/sucesso/fora frouxos | Devolve interview/spec. Finding de código não reabre plan |
| Etapa 2+ | Mesmo `review.md`. Edite o vivo. Não apply de wip por cima se só vai acrescentar etapa |
| “Já corrige” | Grave o veredito **primeiro**. Handoff implement. Não patche aqui |

```
Q: <só se o veredito depende do humano>
RECOMENDO: <opção> — <1 linha>
(ok / outra?)
```

Barra de Approve: saúde do código + convenção do repo. Não bloquear gosto.

## 3. Julgar (antes de gravar)

Ordem:

1. **Contexto** — o que a mudança alega. Se `implement.md` existir, leia fatia, prova e “Para a review”.
2. **Testes** — existem? testam comportamento? Sem editar testes.
3. **Cobertura** — só se há `spec.md`. Cada A*/C* tem evidência no **código**, não só `[x]` no plan. T* marcada sem cumprir aceite → `R*` `gap: missing|partial`. Código fora da spec → `unrequested`. Spec errada → `volta vibe-spec`, não invente T*.
4. **Cinco eixos** no diff (só ler): corretude → clareza → arquitetura → segurança → performance.
5. **Visual** só se o diff desta etapa toca UI: `references/ui-visual-quality.md`. Print sem leitura = Required.
6. **DoD** — `references/definition-of-done.md` no que couber. Tudo N/A → omitir a seção.
7. **Segurança** só se o diff toca input, auth, segredo, upload, pagamento, LLM ou dado pessoal: `references/security-and-hardening.md`. Uma ref. Não invente Critical teórico. Sem isso, omitir a seção.

Finding: evidência (`path`) + severidade + remédio nomeado + prova. Sem evidência não entra. Achado novo = próximo `R*` livre. Não renumerar fechados.

| Prefixo | Bloqueia |
|---|---|
| Critical / Required | Sim |
| Nit / Optional / FYI | Não |

Remédio aponta `vibe-implement` + o que fazer. Esta skill **não** aplica.

## 4. Escrever e salvar já

Molde: `templates/review.md`. Uma casa por fato. Omita seção que esta etapa não precisa.

| Campo | Abre | Fecha / some |
|---|---|---|
| Cobertura | Há `spec.md` | Sem spec: omitir |
| R* | Achado com path + evidência | `[x]` quando implement provou. Lista vazia some. Sem bloqueio: “nenhum bloqueio” |
| Visual | Diff desta etapa toca UI | Sem UI: omitir |
| Segurança | Diff toca superfície listada no §3 | Sem isso: omitir |
| DoD / Notas | Há o que aplicar ou anotar | Vazio / N/A: omitir |
| Etapa N | Toda run desta skill no pedido | Etapa antiga **não** apaga |

Status: `rascunho` na etapa 1; `request-changes` enquanto houver R* bloqueante em `[ ]`; `aprovado` quando o veredito vigente for Approve e o humano confirmou.

Não pergunte se pode salvar. Não cole o corpo no chat.

**Etapa 1 (não há `review.md`):** preencha o wip, apply (§0).

**Etapa 2+ (já há `review.md`):** patch no vivo. Acrescente `### Etapa N`. Atualize a checklist e o **veredito vigente**. Não apply de wip por cima, salvo wip que já contém o arquivo inteiro (histórico + etapa nova).

3. Chat, **só**:

```
Review gravada: .vibeflow/phases/phase-N-slug/review.md

- Etapa: <N> · Veredito vigente: Approve | Request changes | Approve com defer
- Abriu: <R* ou nenhum>
- Fechou: <R* ou —>
- Handoff: vibe-implement | volta vibe-spec | cadeia fechada

Leia o arquivo. Não reimprimo a review aqui.
```

## 5. Fechar

Não commita. Commitável: `review.md`. Fora: `review-report.json`, `review-wip.md`.
Request changes → handoff `vibe-implement` (arquivo + R* em `[ ]`). **Não** dispare.
Approve sem R* bloqueantes em `[ ]` → cadeia fechada no padrão desta porta.
