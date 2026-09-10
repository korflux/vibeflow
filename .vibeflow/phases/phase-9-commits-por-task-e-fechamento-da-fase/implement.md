# Implement: commits por task e fechamento da fase
# Alvo: phase-9-commits-por-task-e-fechamento-da-fase
# Status: aprovado

## Fatia T1: Migrar o fluxo Git para commits isolados por task

- Feito: removida a orientação operacional de agrupamentos intermediários dos pacotes, templates, documentação canônica, README, escopo e regras. `vibe-implement` agora trata cada `T*` como unidade de teste, staging e commit isolado, sem push. `vibe-review` passou a ser dona do commit residual e do push final após Approve e confirmação humana. O parser continua lendo somente headings `T*`, `T* concluída` e `Deps`.
- Feito: corrigida a seleção de alvo dos motores Python e PowerShell de `vibe-spec`, para que `--slug` explícito abra nova phase mesmo quando existe rascunho antigo sem `plan.md`.
- Marcado: A1, A2, A3, A4, A6, C1 e C4 em `spec.md`; testes de contrato de plan, implement, review e distribuição.
- Prova: `python docs/vibe-init/tests/test-init.py -v` -> 32 testes OK.
- Prova: `python docs/vibe-interview/tests/test-interview.py -v` -> 19 testes OK.
- Prova: `python docs/vibe-spec/tests/test-spec.py -v` -> 19 testes OK, incluindo paridade Python/PowerShell para slug explícito.
- Prova: `python docs/vibe-plan/tests/test-plan.py -v` -> 21 testes OK.
- Prova: `python docs/vibe-analyze/tests/test-analyze.py -v` -> 18 testes OK.
- Prova: `python docs/vibe-implement/tests/test-implement.py -v` -> 34 testes OK, incluindo prosa fora de `T*` ignorada pela fila e contrato de commit sem push.
- Prova: `python docs/vibe-review/tests/test-review.py -v` -> 20 testes OK.
- Prova: `python docs/tests/test-distribuicao.py -v` -> 12 testes OK, incluindo a busca sem referências na documentação canônica atual.
- Prova: `python docs/tests/test-mvp-flow.py -v`, `python docs/tests/test-visual-contract.py -v` e `python docs/tests/test-reparse-safety.py -v` -> todos OK.
- Prova: `git diff --check` -> sem erro de whitespace; apenas avisos de conversão LF/CRLF do ambiente Windows.
- Prova: `gitleaks detect --source . --verbose --redact --no-banner` -> nenhum segredo encontrado.
- Commit da task: não executado nesta sessão. O worktree já continha alterações não relacionadas, inclusive nos mesmos paths canônicos; sem snapshot confiável para separar as origens, qualquer staging poderia misturar trabalho existente. O commit seguro fica pendente de isolamento humano do worktree.
- Decisões críticas: nenhuma decisão de produto nova; a correção de seleção por slug explícito está coberta pelos testes Python e PowerShell.

### Feedback +

- A fila continua mecânica e não ganhou estado paralelo para agrupamentos intermediários.
- As regras de staging e finalização ficaram concentradas nas skills responsáveis, sem criar uma skill Git ou alterar o schema dos relatórios.

### Feedback -

- Os launchers `.sh` não puderam ser executados neste host Windows: `bash` falhou com `E_ACCESSDENIED`. As suítes Python e a paridade PowerShell passaram.
- A fase ainda não pode ser declarada fechada enquanto o worktree não for isolado e o commit da task não puder ser criado sem misturar alterações anteriores.

### Para a review

- Confirmar o diff isolado desta phase, criar `task(T1): ...` com staging explícito e sem `Co-Authored-By`, depois revisar a condição de Approve antes do commit/push final.

## Handoff

vibe-review | finalização Git da phase

- Chat: a implementação está comprovada, mas a review e o fechamento Git permanecem pendentes do isolamento do worktree. O `plan.md` e este `implement.md` são a ponte; não fazer push nesta etapa.
