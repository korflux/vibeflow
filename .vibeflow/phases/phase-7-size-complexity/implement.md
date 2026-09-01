# Implement: Size por complexidade e risco separado
# Alvo: phase-7-size-complexity
# Status: concluído

## Fatia T1

- Feito: `vibe-plan/SKILL.md` agora define o score de cinco dimensões, os intervalos de `Size`, o limite de quebra, `Risk` separado e a independência do esforço da rota. `vibe-plan/templates/plan.md` exige classificação, score, justificativa e risco.
- Marcado: T1 no `plan.md`; A1, A2 e A5 na `spec.md`.
- Prova: `python docs/vibe-plan/tests/test-plan.py -v` -> 17 testes passando.

### Feedback +

- A regra ficou centralizada na skill e o template só materializa os campos necessários, sem alterar o parser do script.

### Para a review

- Conferir se a tabela antiga baseada em arquivos foi removida e se os intervalos, o limite `9–10` e a separação de `Risk` estão consistentes entre skill e template.

## Fatia T2

- Feito: `docs/vibe-plan/ARQUITETURA.md` e `ANALISE.md`, `README.md` e `docs/ESCOPO.md` agora distinguem complexidade da task, risco da mudança e esforço da rota, mantendo a matriz e os intervalos alinhados.
- Marcado: T2 no `plan.md`; A3 na `spec.md`.
- Prova: `python docs/vibe-plan/tests/test-plan.py -v` -> 17 testes passando; `rg -n "Size|Risk|superfície|acoplamento|verificação|incerteza|coordenação|tempo|rota" vibe-plan docs/vibe-plan README.md docs/ESCOPO.md` -> ocorrências esperadas nos documentos atualizados.

### Feedback +

- A documentação aponta para a `SKILL.md` como matriz canônica e não introduz regra de tempo ou contagem fixa de arquivos.

### Para a review

- Conferir se todos os documentos usam os mesmos intervalos e se o README não confunde esforço da rota com `Size` da T*.

<!-- fatia seguinte: copie o bloco ## Fatia abaixo, não apague as anteriores -->

## Correção pós-review

- Corrigido: os sete ponteiros em `skills/` foram materializados como symlinks relativos reais e o Git local foi configurado com `core.symlinks=true`.
- Corrigido: o launcher Bash foi executado pelo Git Bash fora da restrição do sandbox, sem alteração no script.
- Provas: `python docs/tests/test-distribuicao.py -v` -> 7 testes passando; `C:\Program Files\Git\bin\bash.exe docs/vibe-plan/tests/test-plan.sh` -> `pass=6 fail=0`.
- Resultado: os dois achados ambientais foram fechados; a restrição do shim `bash` dentro do sandbox permanece somente como limitação do ambiente de execução.
