# Implement: IA como piloto e scripts como auxiliares
# Pasta: phase-5-ia-piloto-scripts-auxiliares
# Status: concluído

## Fatia avulsa

- Feito: `.vibeflow/REGRAS.md`, redefinidos os papéis da IA, da skill, do script, do relatório e do humano; acrescentado diagnóstico e correção consciente de scripts; substituído `Script primeiro` por `Entender e usar o script`.
- Marcado: A1, A2, A3, A4, A5, C1, C2 e C3 em `spec.md`.
- Prova: `git diff --check -- .vibeflow/REGRAS.md .vibeflow/phases/phase-5-ia-piloto-scripts-auxiliares` retornou sem erro; buscas confirmaram a remoção de `Script primeiro` e `contrato script`, além da presença de `pilota a run`, `evidência operacional` e `Entender e usar o script`.

### Feedback +

- O relatório do `vibe-implement` apontou a fase 4, mas a leitura do pedido e do disco identificou corretamente a fase 5 e permitiu direcionar o script com `--dir`.

### Para a review

- Conferir se a IA ganhou autonomia sem perder as garantias determinísticas de path, numeração, promoção, backup, hash e paridade dos motores.
