# Implement: fila elegível e prova em três andares
# Pasta: phase-3-fila-elegivel-prova
# Status: em-curso

## Fatia T1

- Feito: parser de `### T{n}:` / `concluída` / `Deps` em `implement.py`; campo `fila` no relatório; ARQUITETURA e ANALISE atualizados; casos C1 na suíte
- Marcado: T1 + checkpoint após T1 em `plan.md`; A3, A6, C1 em `spec.md`
- Prova: `python docs/vibe-implement/tests/test-implement.py` → 23 testes OK (7 casos de `fila` falharam antes do parser)

### Feedback −

- A1 e A2 da spec misturam disco e skill; T1 só prova o disco. Skill (Q de 2+, executar a única) fica na T2.

### Para a review

- Conferir se o parser não lê aceite/Status/checkpoint. T3 ainda precisa do gêmeo ps1.

## Fatia T2

- Feito: SKILL lê `fila.elegiveis` do relatório (Q se 2+, executa se 1, deps se bloqueada); ciclo exige comando e RED-GREEN; DoD não rebaixa a barra
- Marcado: T2 em `plan.md`; A1, A2, A4, C3 em `spec.md`
- Prova: `python docs/vibe-implement/tests/test-implement.py` (SkillContracts) — falhou no RED sem as frases, passou depois

## Fatia T3

- Feito: `implement.ps1` projeta o mesmo `fila`; suíte de paridade no caso duas T* / uma bloqueada por dep
- Marcado: T3 + checkpoint após T2–T3 em `plan.md`; C2 em `spec.md`
- Prova: `python docs/vibe-implement/tests/test-implement.py` → 26 OK

### Feedback −

- PS 7: lista genérica de um dep não pode virar `[string[]]@(...)` nem ser iterada como string (vira caractere e quebra o HashSet).

### Para a review

- T4 ainda aberta: freeze do plan (Verificação = comando) e linha no ESCOPO.

## Fatia T4

- Feito: template e SKILL do plan congelam `concluída`, `Deps` e Verificação como comando; checkpoint omite fluxo se não atravessa T*; ARQUITETURA/ANALISE e ESCOPO 3.3
- Marcado: T4 + checkpoint após T4 em `plan.md`; A5, C4 em `spec.md`
- Prova: `python docs/vibe-plan/tests/test-plan.py` → 12 OK (2 falharam no RED com “passo manual” ainda no template)

### Para a review

- Fila da fase zerada. Handoff `vibe-review`. Conferir se o freeze do template bate com o parser da implement.
