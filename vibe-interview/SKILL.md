---
name: vibe-interview
description: >
  Entrevista pedido ambíguo até fechar intenção, sucesso e fora, e grava a trilha em .vibeflow/phases/phase-N-slug/interview.md. Use when the user runs /vibe-interview, pede para entrevistar o pedido, fechar intenção, descobrir o que realmente quer, refinar ideia, explorar variações, ou o pedido está vago, sem sucesso observável, sem público, ou convenção no lugar de outcome — mesmo que não diga vibe-interview.
---

# vibe-interview

Não invente `n`, slug ou path. Disco decide o número. Chat sozinho não conta.
Sem `.vibeflow/`: pare e mande `/vibe-init`. Não grave em `docs/` nem na raiz.

## 0. Script primeiro

1. Resolva o diretório desta skill (pasta deste `SKILL.md`).
2. No cwd do repo do usuário:
   - Windows: `pwsh "<skill>/scripts/interview.ps1"`
   - Unix: `bash "<skill>/scripts/interview.sh"`
     - O launcher usa Python 3; se indisponível, usa PowerShell 7. Sem um deles, pare e informe a dependência.
3. Leia `.vibeflow/interview-report.json`. Se `aberta`, leia aquele `interview.md`. Não abrir a árvore inteira.

Se o script parar com `INIT_AUSENTE`: `/vibe-init` e só então volte.
Se `PHASES_INESPERADO`: não contorne. Humano resolve o path.

## 1. Abrir (5 linhas)

hipótese · confidence · next_n · aberta · wip

```
HIPÓTESE: standup quer "como estamos?", "dashboard" foi convenção
CONFIDENCE: ~30% — falta: quem, métrica, sucesso
next: 2 · aberta: phase-1-lock-bloco · wip: ausente
```

Abaixo de ~70%: motivo na mesma linha. Número alto sem prever as próximas 3 reações = número errado.

`aberta` e o pedido atual são o **mesmo** assunto → edite o `interview.md` vivo. Não chame apply.
Assunto diferente, ou `aberta` nula → sessão nova no wip; apply no fim.

## 2. Gate

| | Ação |
|---|---|
| Typo / rename / inequívoco auto-contido / velocidade pedida / pergunta de info | **Não** usar; não invente entrevista |
| `/vibe-interview` explícito | Usa, mesmo se o pedido parecer claro |
| Já ≥~95% e restate fechável sem chute | Restate → sim → gravar trilha (pode pular Q) |
| Falta quem, por quê, sucesso ou restrição; ou convenção no lugar de outcome | **Fase 1** |
| Intenção ok, forma da solução não | **Fase 2** (depois de F1 ou conceito grosso) |
| CI / loop / agendado sem usuário vivo e pedido subespecificado | **Bloquear** — não chute |

## 3. Fase 1

Wip = `.vibeflow/interview-wip.md`. Crie na primeira HIPÓTESE; acrescente cada Q/GUESS/R na hora. Molde: `templates/interview.md`. Não apague Solicitação/Trilha para “limpar” no final.

### 3.1 Uma pergunta, com GUESS

```
Q: <uma pergunta focada>
GUESS: <hipótese da resposta + por que>
```

Espere a reação. A 3ª pergunta depende da 1ª. Chute errado visível > pergunta vazia (mitiga concordância educada).

### 3.2 "Quer" vs "deveria querer"

Best-practice theater, deferência à convenção, buzzword como meta:

> Se você não tivesse que justificar isso para ninguém, o que você realmente queria?

### 3.3 Probe visual (só se UI e ainda aberto)

Outcome user-visible **e** tom ainda não fechou. Máx. 1–2 Q+GUESS. Não paleta, não type pairing, não manifesto. Interview **não** fecha CSS.

### 3.4 Restate (só o bloco, no chat)

≥~95% ou for fechar. 1 frase por linha, ~15 palavras. Fora inegociável.

```
Entendi assim:

- O quê:     <resultado, não a feature>
- Pra quem:  <quem se beneficia>
- Por quê:   <o que mudou / por que agora>
- Sucesso:   <observável>
- Limite:    <restrição que manda>
- Fora:      <o que explicitamente não entra>
- Visual:    <só se UI e fechou tom; senão omitir a linha>

Fecha assim? (sim / não / ajustar)
```

Parada: *consigo prever as próximas 3 reações?* → restate e para. Várias rodadas e ainda imprevisível = uma linha, pergunte se recua.

### 3.5 Sim explícito

| Resposta | O que é | O que fazer |
|---|---|---|
| "o que você achar melhor" | delegação | **2 opções concretas**, uma linha cada |
| "parece bom" | ambíguo | "O que mudaria?" |
| "beleza, bora" | saída educada | "Sim no recap acima, ou quer ajustar algo?" |
| silêncio + "ok, pode começar" | desistência | não tratar como sim |

Gate = "sim" claro. Não confirme campo a campo.

## 4. Fase 2 (só se a forma estiver aberta)

Intenção fechada, rota não. Leia `references/frameworks.md` para expandir (**uma** lente). Leia `references/refinement-criteria.md` para convergir. Ritmo em `references/examples.md` — não copiar o caso.

1. Reframe em 1 linha (problema, não solução).
2. Afiar: 1–3 Q+GUESS que decidem o *tipo* de problema.
3. 4–6 variações: cada uma com lente + por que existe.
4. Opinião: empurrar 1–2 + porquê. Dizer baixa diferenciação e complexidade alta em voz alta.
5. Convergir: valor / viabilidade / diferenciação que importam aqui; **Not Doing** justificado; MVP que testa a aposta central.
6. Escrever seção **Direção** no mesmo arquivo (wip ou vivo). Não apagar Solicitação/Trilha.

Maioria dos pedidos: só Fase 1.

## 5. Gravar

Intenção confirmada = restate + sim + arquivo em disco. Depois do sim, **salve na hora** — não pergunte.

Sessão nova (wip):

1. Complete o wip: Solicitação, Hipótese, Trilha, Resultado (= restate). Direção se F2. Handoff `vibe-spec` ou `precisa-forma`.
2. Slug = frase curta da fase (do O quê), ainda não sanitizado.
3. `pwsh "<skill>/scripts/interview.ps1" -Apply -Slug "<slug>"` (Unix: `interview.sh --apply --slug "<slug>"`).
4. Leia o relatório: `created.path`. Mostre o path. Não reimprima o arquivo.

Se `WIP_AUSENTE`, `SLUG_INVALIDO`, `FASE_EXISTE` ou `COPY_HASH_MISMATCH`: não contorne. Corrija o que o erro nomeia e rode apply de novo.

Continuar fase já promovida: patch no `interview.md` vivo. Sem apply.

## 6. Fechar

Não commita. Avise: commitar `.vibeflow/phases/phase-N-slug/interview.md`. Não commitar `interview-report.json` nem `interview-wip.md`.
Não dispare `vibe-spec`. Handoff é uma linha no artefato.

