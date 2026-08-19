---
name: vibe-review
description: >
  Julga o patch e a cobertura pós-código e grava .vibeflow/phases/phase-N-slug/review.md.
  Use when the user runs /vibe-review, pede review, revisa isso, LGTM, pode
  mergear, ou há handoff de vibe-implement / rota medium+ — mesmo que não
  diga vibe-review.
---

# vibe-review

Não invente `n` se há plan. Não edite source. Sem `review.md` não há veredito.
Sem `.vibeflow/`: `/vibe-init`. Open Questions no arquivo = defeito. Não commita.

## 0. Script primeiro

1. Resolva o diretório desta skill.
2. No cwd do repo:
   - Windows: `pwsh "<skill>/scripts/review.ps1"`
   - Unix: `bash "<skill>/scripts/review.sh"` (Python 3, senão pwsh 7)
3. Leia `.vibeflow/review-report.json`. Se `alvo`, leia o que `files` listar. Leia `.vibeflow/REGRAS.md`. Diff: o que o humano apontou, ou o working tree da sessão. Não varrer a árvore.

`INIT_AUSENTE` → init. `REVIEW_SEM_ALVO` / `FASE_AUSENTE` / `WIP_AUSENTE` / `SLUG_INVALIDO` → não contorne.

Apply:
- reuse/atualizar: `pwsh "<skill>/scripts/review.ps1" -Apply` (`--dir` se o alvo errar)
- avulsa sem cadeia: `… -Apply -Slug "<frase curta>"`
- Unix: `review.sh --apply` / `--apply --slug "…"`

## 1. Abrir (5 linhas)

first-pass|re-review · alvo · plan · spec · diff

```
first-pass · alvo: phase-2-vibe-review · plan: sim · spec: sim · diff: working tree
```

`modo_sugerido=criar` e sem `--slug` = não há pasta. Não grude review nova no N de outro pedido.

## 2. Gate

| | Ação |
|---|---|
| Sem alvo e sem diff | **Para.** Peça path, branch, PR ou `--dir` |
| T* obrigatórias em `[ ]` e o humano pediu “pronto da feature” | Recuse Approve de feature. Pode revisar o diff e listar o que falta no plan |
| Intenção/sucesso/fora frouxos | Devolve interview/spec. Finding de código não reabre plan |
| Re-review | Mesmo `review.md`. Não apply de wip por cima se só vai atualizar Re-review: edite o vivo |
| “Já corrige” | Grave o veredito **primeiro**. Handoff implement. Não patche aqui |

```
Q: <só se o veredito depende do humano>
RECOMENDO: <opção> — <1 linha>
(ok / outra?)
```

Barra de Approve: saúde do código + convenção do repo. Não bloquear gosto.

## 3. Julgar (antes de gravar)

Ordem:

1. **Contexto** — o que a mudança alega (spec/T* se existirem). First-pass ou re-review.
2. **Testes** — existem? testam comportamento? Sem editar testes.
3. **Cobertura** — cada A*/C* tem evidência no **código**, não só `[x]` no plan. T* marcada sem cumprir aceite → `R*` `gap: missing|partial`. Código fora da spec → `unrequested`. Spec errada → `volta vibe-spec`, não invente T*.
4. **Cinco eixos** no diff (só ler): corretude → clareza → arquitetura → segurança → performance.
5. **Visual** se UI web: `references/ui-visual-quality.md`. Default DevTools (mesmo contrato da implement). Print sem leitura = Required.
6. **DoD** — `references/definition-of-done.md` (pointer). Aceite **e** DoD.
7. **Security** se o diff toca input/auth/segredo/pagamento — `references/security-and-hardening.md`. Uma ref. Não invente Critical teórico.

Finding: evidência (`path`) + severidade + remédio nomeado + prova. Sem evidência não entra.

| Prefixo | Bloqueia |
|---|---|
| Critical / Required | Sim |
| Nit / Optional / FYI | Não |

Remédio aponta `vibe-implement` + o que fazer. Esta skill **não** aplica.

## 4. Escrever e salvar já

Wip = `.vibeflow/review-wip.md`. Molde: `templates/review.md`. Status `rascunho` na primeira passagem; `request-changes` se já houver R* bloqueante.

Não pergunte se pode salvar. Não cole o corpo no chat.

1. Preencha o wip. Omita N/A. Sem Critical/Required → checklist “nenhum bloqueio” + Approve.
2. Apply (§0). Re-review consciente: patch no vivo (`## Re-review` + veredito). Não renumere R* fechados.
3. Chat, **só**:

```
Review gravada: .vibeflow/phases/phase-N-slug/review.md

- Veredito: Approve | Request changes | Approve com defer
- R* bloqueantes: <ids ou nenhum>
- Cobertura: <A*/C* ok / gaps>
- Handoff: vibe-implement | volta vibe-spec | cadeia fechada

Leia o arquivo. Não reimprimo a review aqui.
```

## 5. Fechar

Não commita. Commitável: `review.md`. Fora: `review-report.json`, `review-wip.md`.
Request changes → handoff `vibe-implement` (arquivo + R* em `[ ]`). **Não** dispare.
Approve sem R* bloqueantes em `[ ]` → cadeia fechada no padrão desta porta.

## Fora (v1)

Source, testes, lockfile, `plan.md`/`spec.md`/`analyze.md`, T* no plan, `tasks.md`, path `docs/`/`specs/`/`fluxline`, 16 classes de security, Playwright default, hooks, `--force`, Open Questions no `.md`, dump no chat, commit, disparar implement, LGTM sem arquivo, segundo `review.md` na fase, Approve de feature com T* obrigatórias abertas.
