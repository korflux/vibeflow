---
name: vibe-spec
description: >
  Especifica comportamento, escopo, aceite e decisões em `.vibeflow/phases/phase-N-slug/spec.md` ou `.vibeflow/mvp/spec.md`.
  Use when the user runs /vibe-spec, pede spec, especificar a entrega,
  fechar comportamento e aceite antes do plan, ou a rota é high/xhigh/max
  com intenção já razoavelmente clara, mesmo que não diga vibe-spec.
---

# vibe-spec

Não invente `n`, slug ou path. Sem `.vibeflow/`, pare e mande `/vibe-init`. Não grave em `docs/` nem na raiz.
Só o decidido. Open Questions no arquivo é defeito. O arquivo vivo é a fonte da verdade; o chat não substitui o disco.
No MVP, preserve IDs críticos da interview e declare `mantém`, `cria` ou `substitui`; não publique decisões em `REGRAS.md`.


## 0. Entender e usar o script

1. Resolva o diretório desta skill e leia o motor que vai executar: `scripts/spec.ps1` no Windows ou `scripts/spec.py` no fluxo Unix. Entenda flags, seleção de alvo, tratamento de erros e promoção atômica temporária antes de chamá-lo. Se encontrar defeito, corrija o motor e prove o contrato antes de continuar.
2. No cwd do repo:
   - Windows: `pwsh "<skill>/scripts/spec.ps1"`.
   - Unix: `bash "<skill>/scripts/spec.sh"`.
   - Modo MVP: acrescente `-Mvp` ou `--mvp`.
3. Leia `.vibeflow/spec-report.json` como evidência operacional. Abra `interview.md` e/ou `spec.md` do alvo, `.vibeflow/REGRAS.md` e apenas os paths do codebase necessários para entender o comportamento pretendido. Não faça varredura cega da árvore.

Erros determinísticos previstos: `INIT_AUSENTE` exige `/vibe-init`. `PHASES_INESPERADO`, `MVP_INESPERADO`, `MVP_INTERVIEW_AUSENTE`, `SPEC_JA_PLANEJADA`, `SPEC_SEM_ALVO`, `FASE_AUSENTE`, `FASE_EXISTE`, `SLUG_INVALIDO`, `COPY_HASH_MISMATCH` e `MODO_INVALIDO` exigem diagnosticar a causa e não devem ser contornados.

## 1. Abrir

Declare em cerca de cinco linhas: confiança, rota, modo, alvo e wip.

```text
CONFIDENCE: ~85%, entendo: lock por bloco no editor | falta: concorrência
modo: reuse · alvo: phase-1-lock-bloco · interview: sim · wip: ausente
```

- `modo=criar` (sem interview anterior): use slug no apply para criar nova pasta de fase.
- `interview_pendente`: proibido avançar `next_n`. Use a mesma fase da interview.
- `rota=mvp`: alvo fixo `.vibeflow/mvp`, interview obrigatória e proibido usar slug ou dir.

## 2. Gate e escopo

```text
CONFIDENCE: ~N%, entendo: ... | falta: ...
```

| Sinal | Ação |
|---|---|
| Typo, rename, inequívoco de uma linha | Não usar spec |
| `/vibe-spec` explícito | Usar, se a intenção estiver clara |
| < ~80% e falta quem/por quê/sucesso | Parar. Encaminhar para `/vibe-interview` (1 a 2 linhas do que falta) |
| ~80%+ ou interview existente no disco | Seguir. Lacunas pontuais de desenho = Q + RECOMENDO |
| `plan.md` já existente no alvo | Não sobrescrever. Pedido novo exige outra fase |

No modo MVP, a spec consolida a baseline inteira do produto e mantém o handoff max. Não reduza a descoberta a uma feature nem remova uma premissa assumida sem registrar a substituição.
Spec define esta mudança e seu delta observável, não o manual completo do repositório.

## 3. Seams e decisões (chat)

Apenas o que, se errado, invalida o desenho. Uma pergunta por vez.

```text
Q: <decisão>
RECOMENDO: <opção>, <1 linha explicando motivo e impacto>
(ok / outra?)
```

- "Tanto faz" crava a recomendação. Dúvida de intenção central exige `vibe-interview`.
- Seam óbvio: registre diretamente no arquivo.
- Sucesso vago: alinhe 1 a 3 critérios observáveis no chat e consolide em `C*`.
- Toda decisão fechada entra em **Suposições e decisões**.
- No MVP, decisões críticas da interview entram em **Decisões críticas** mantendo o ID: `mantém` para preservar, `cria` para novas decisões necessárias e `substitui` citando o ID e explicando o delta.
- Se houver UI visível ao usuário, consulte `references/ui-visual-direction.md` antes de gravar.
- Se a entrega envolver banco de dados, persistência ou valores monetários/cálculos exatos, consulte `references/database-and-migrations.md` (DECIMAL/NUMERIC para dinheiro, TIMESTAMPTZ para datas, constraints no banco e índices em FKs).

## 4. Escrever e salvar

Wip: `.vibeflow/spec-wip.md`. Molde: `templates/spec.md`. Status inicial: `rascunho`.
Não pergunte se pode salvar e não cole o corpo do documento no chat.

1. Preencha o wip. Omita seções não aplicáveis. Comandos de teste somente se existirem no repo. Sem `FR-00N`, sem mural de user stories e sem CSS/paleta: a spec fecha comportamento e aceite.
2. Execute o apply através do script:
   - Reuse/atualizar em phase existente:
     `pwsh "<skill>/scripts/spec.ps1" -Apply`
     `bash "<skill>/scripts/spec.sh" --apply`
   - Criar nova phase (sem interview prévia):
     `pwsh "<skill>/scripts/spec.ps1" -Apply -Slug "<frase curta>"`
     `bash "<skill>/scripts/spec.sh" --apply --slug "<frase curta>"`
   - Modo MVP:
     `pwsh "<skill>/scripts/spec.ps1" -Apply -Mvp`
     `bash "<skill>/scripts/spec.sh" --apply --mvp`
3. Responda no chat apenas:

```text
Spec gravada: <created.path>/spec.md

- Objetivo: <1 linha>
- Cobre: <2 a 4 bullets>
- Fora: <1 linha>
- Como provar: <1 linha>

Arquivo disponível em <created.path>/spec.md. Responda "aprovado" para confirmar, "pode ir pro plan" (ou "pode ir para a próxima fase") para avançar imediatamente, ou indique os ajustes desejados.
```

## 5. Ajuste ou aprovação

| Resposta | Ação |
|---|---|
| Aprovado (sem pedir plan) | `# Status: aprovado` no vivo; checklist humana `[x]`; parar e aguardar próximo comando |
| "Pode ir pro plan" / "pode ir para a próxima fase" / pede `vibe-plan` | `# Status: aprovado` no vivo; checklist humana `[x]`; iniciar imediatamente `vibe-plan` |
| Pedido de alteração | Patch direto no arquivo vivo; até 5 bullets no chat; solicitar nova conferência |
| "Parece bom" sem pedir plan | Perguntar: "Aprovado no arquivo ou deseja algum ajuste?" |
| Intenção quebrou | Encaminhar para `vibe-interview`. Não forçar plan |

Rascunho sem "aprovado" e sem pedido explícito de plan não autoriza avançar para o planejamento.

## 6. Fechar

Não commite no git. Não dispare a próxima skill a menos que o usuário tenha pedido explicitamente para avançar (§5).
Informe que o arquivo `spec.md` entra no git e que `spec-report.json` e `spec-wip.md` ficam de fora.
Handoff registrado no arquivo: `vibe-plan`.

