---
name: vibe-spec
description: >
  Grava a spec do decidido em .vibeflow/phases/phase-N-slug/spec.md.
  Use when the user runs /vibe-spec, pede spec, especificar a entrega,
  fechar comportamento e aceite antes do plan, ou a rota é high/xhigh/max
  com intenção já razoavelmente clara — mesmo que não diga vibe-spec.
---

# vibe-spec

Não invente `n`. Reuse a pasta da interview. Sem `.vibeflow/`: `/vibe-init`.
Só o decidido. Open Questions no arquivo = defeito. Chat não substitui o disco.

## 0. Script primeiro

1. Resolva o diretório desta skill.
2. No cwd do repo:
   - Windows: `pwsh "<skill>/scripts/spec.ps1"`
   - Unix: `bash "<skill>/scripts/spec.sh"` (Python 3, senão pwsh 7)
3. Leia `.vibeflow/spec-report.json`. Se `alvo`, leia `interview.md` e/ou `spec.md` dessa pasta. Leia `.vibeflow/REGRAS.md`. Paths só se citados. Não varrer a árvore.

`INIT_AUSENTE` → init. `PHASES_INESPERADO` / `SPEC_JA_PLANEJADA` / `SPEC_SEM_ALVO` → não contorne.

## 1. Abrir (5 linhas)

confidence · modo · alvo · interview · wip

```
CONFIDENCE: ~85% — entendo: lock por bloco no editor | falta: concorrência
modo: reuse · alvo: phase-1-lock-bloco · interview: sim · wip: ausente
```

`modo_sugerido=criar` e sem interview: slug no apply, pasta nova.
`interview_pendente`: **proibido** usar `next_n`.

## 2. Gate

```
CONFIDENCE: ~N% — entendo: … | falta: …
```

| | Ação |
|---|---|
| Typo / rename / inequívoco de uma linha | **Não** usar |
| `/vibe-spec` explícito | Usa, se a intenção não estiver furada |
| <~80% e falta quem/por quê/sucesso | **Para.** Mande `/vibe-interview` (1–2 linhas: o que falta) |
| ~80%+ ou interview no disco | Segue. Buraco pontual = Q+RECOMENDO |
| `plan.md` na alvo | Não pisa. Pedido novo = outra fase |

Spec = esta mudança + delta, não o manual do repo.

## 3. Seams e buracos (chat)

Só o que, se errado, invalida o arquivo. Uma pergunta por vez.

```
Q: <decisão>
RECOMENDO: <opção> — <1 linha>
(ok / outra?)
```

“Tanto faz” → crava a rec. Dúvida de intenção → interview, não force spec.
Seam óbvio → documente no arquivo, sem cerimônia. Dois seams que mudam o desenho: uma linha no chat.

Vago de sucesso → 1–3 linhas testáveis no chat, depois `C*`.

Toda decisão fechada entra em **Suposições e decisões**.

UI user-visible: leia `references/ui-visual-direction.md` **antes** de gravar.

## 4. Escrever e salvar já

Wip = `.vibeflow/spec-wip.md`. Molde: `templates/spec.md`. Status `rascunho`.
Não pergunte se pode salvar. Não cole o corpo no chat.

1. Preencha o wip. Omita seção N/A. Não invente. Fora real. Comandos só se existem no repo.
   Sem `FR-00N`, sem mural de user story, sem CSS/paleta: a spec fecha comportamento, não forma.
2. Apply:
   - reuse/atualizar: `pwsh "<skill>/scripts/spec.ps1" -Apply`
   - criar: `… -Apply -Slug "<frase curta>"`
   - Unix: `spec.sh --apply` / `--apply --slug "…"`
3. Chat, **só**:

```
Spec gravada: .vibeflow/phases/phase-N-slug/spec.md

- Objetivo: <1 linha>
- Cobre: <2–4 bullets>
- Fora: <1 linha>
- Como provar: <1 linha>

Leia o arquivo. Ok: **aprovado** (ou “pode ir pro plan”).
Ajuste: diga o que mudar. Não reimprimo a spec aqui.
```

## 5. Ajuste ou aprovação

| Resposta | Ação |
|---|---|
| aprovado / “pode ir pro plan” / pede `vibe-plan` | `# Status: aprovado` no vivo; checklist humana `[x]`; §6 |
| pedido de alteração | Patch **só** no arquivo; ≤5 bullets no chat; re-peça leitura |
| “parece bom” sem pedir plan | “Aprovado no arquivo, ou quer ajustar?” |
| intenção quebrou | `vibe-interview`. Não force plan |

Rascunho sem “aprovado” e sem pedido de plan **não** autoriza fatiar.

## 6. Fechar

Não commita. Avise: commitar `.vibeflow/phases/phase-N-slug/spec.md`. Não commitar `spec-report.json` nem `spec-wip.md`.
Handoff no arquivo: `vibe-plan`. **Não** dispare a skill.

