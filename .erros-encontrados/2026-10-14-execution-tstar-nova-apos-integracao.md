# T* nova no plan depois da integração torna execution.json ilegível

- Data: 2026-10-14.
- Local: vibe-implement/scripts/execution.py, função `load()`, linhas ~126-129; mesmo contrato no gêmeo vibe-implement/scripts/execution.ps1.
- Problema: quando há `integracao` gravada, `load()` exige `set(state["tasks"]) == set(graph)`. Se o plan ganha uma T* nova depois da integração, o registro fica ilegível (`EXECUTION_INVALIDO: integração sem independência`) em leitura e em todas as operações (`local`, `integracao`, `commit`, `init`), em vez de o motor projetar a integração como inválida.
- Impacto: uma correção de review que exija T* nova trava a phase; não há operação do motor que reabra o registro, e a única saída seria editar o JSON à mão.
- Sugestão de correção: tirar a checagem `set(state["tasks"]) != set(graph)` de `load()`, pois ela já é coberta por `ready == set(graph)` em `projection()` e pela recusa da operação `integracao`; manter a checagem de ator independente; acrescentar teste de contrato nos dois motores.
- Relação: encontrado na phase 20 ao incluir a T10 pedida pelo humano (decisão 18); contornado fundindo a T10 na T9, sem corrigir o motor nesta phase (decisão 5).
