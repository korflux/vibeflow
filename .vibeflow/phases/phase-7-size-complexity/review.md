# Review: Size por complexidade e risco separado
# Alvo: phase-7-size-complexity
# Status: rascunho

## Contexto

- Alvo: `phase-7-size-complexity`, working tree local
- Cadeia: `spec.md` / `plan.md` / `implement.md`
- O que muda: o `vibe-plan` passa a classificar T* por score de cinco dimensões, registrar `Risk` separadamente e documentar a diferença entre Size, risco e esforço da rota. O parser mecânico e os plans existentes permanecem sem alteração funcional.

## Cobertura

| Chave | Código | Notas |
|---|---|---|
| A1 | ok | `vibe-plan/SKILL.md` define cinco dimensões, escala 0–2, intervalos e quebra em 9–10; `test-plan.py` valida os termos. |
| A2 | ok | `vibe-plan/templates/plan.md` exige Size com score e Risk separado, sem xhigh/max como tamanho final. |
| A3 | ok | Arquitetura, análise, README e escopo distinguem Size, Risk e esforço da rota. |
| A4 | ok | Testes semânticos detectam o retorno da tabela antiga e o desaparecimento dos campos novos. |
| A5 | ok | A suíte do plan, a paridade PowerShell e a inspeção do script confirmam que o parser mecânico não foi alterado. |
| C1 | ok | A matriz permite separar superfície mecânica de complexidade estrutural. |
| C2 | ok | `Risk` pode ser high sem elevar automaticamente Size. |
| C3 | ok | Score 9–10 é gate de quebra, não valor final de T*. |
| C4 | ok | Suíte do plan: 20 testes; launcher Bash: 6/6; distribuição no checkout principal: 7/7. |

## Checklist de correções

### Critical

- nenhum bloqueio

### Required

- nenhum bloqueio

### Optional / Nit

- [x] R1: **Optional** - `docs/vibe-plan/tests/test-plan.sh` - launcher executado pelo Git Bash fora da restrição do sandbox - remédio: rerodar em um host com Bash funcional - prova: `C:\Program Files\Git\bin\bash.exe docs/vibe-plan/tests/test-plan.sh` -> `pass=6 fail=0` - source: diff - gap: closed

## Notas

- `python docs/vibe-plan/tests/test-plan.py -v` passou com 20 testes.
- `gitleaks detect --source . --no-banner --redact` não encontrou segredos.
- O checkout principal foi corrigido para `core.symlinks=true`; a distribuição passou 7/7 com os sete ponteiros reais.
- O launcher Bash passou 6/6 pelo Git Bash fora da restrição do sandbox. O shim `bash` dentro do sandbox continua limitado pelo `E_ACCESSDENIED` do signal pipe.
- Os dois achados ambientais foram corrigidos e mantidos documentados em `.erros-encontrados/`.

## Veredito vigente

- [x] **Approve**: nenhum Critical/Required em `[ ]`
- [ ] **Request changes**: há Critical/Required em `[ ]`
- [ ] **Approve com defer**: R1, porque a verificação do launcher depende de um host Bash funcional e não há evidência de defeito no patch.

## Handoff

cadeia fechada, sem pendências técnicas ambientais

- [ ] Aprovação humana (leu o arquivo e confirmou)

## Etapas

### Etapa 1 - first-pass - T1-T3, diff e provas

- Leu: `plan.md`, `spec.md` e `implement.md`
- Abriu: R1 opcional
- Fechou: nenhum
- Veredito desta etapa: Approve com defer

<!-- etapa seguinte: copie ### Etapa N abaixo. Não apague as anteriores. -->

### Etapa 2 - correção dos achados ambientais

- Leu: os dois registros em `.erros-encontrados/` e as provas da Etapa 1
- Corrigiu: symlinks reais em `skills/`, `core.symlinks=true` e execução do launcher pelo Git Bash fora do sandbox
- Revalidou: distribuição 7/7 e launcher 6/6
- Fechou: R1 e os dois achados ambientais
- Veredito desta etapa: Approve
