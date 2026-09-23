# Implement: <frase curta>
# Alvo: <phase-<n>-<slug> ou mvp>
# Status: rascunho

<!-- Escreva diretamente neste artefato vivo; feche o status somente após a prova da fatia. -->

## Fatia <T* | R* | avulsa>

- Feito: <paths e o que mudou>
- Marcado: <T* / A* / C* / R* e o arquivo>
- Prova: `<comando>` -> <resultado>
- Commit da task: registrar `<mensagem>` e `<hash>` no resultado da execução e no chat após o commit; não reabrir este artefato apenas para anexar o hash
- Decisões críticas: <IDs implementados e prova; omitir quando N/A>

### Delegação

<!-- Omitir em execução sequencial. O coordenador registra somente o retorno integrado; a prova final é a do estado integrado. -->

- Escopo delegado: <resultado, aceite e paths exclusivos>
- Retorno integrado: <paths, resumo e prova reportada pelo agente; pendências ou N/A>

### Feedback +

<!-- omitir se vazio -->

- <o que correu bem e deve se repetir>

### Feedback -

<!-- omitir se vazio -->

- <o que emperrou, dívida técnica, risco, decisão assumida>

### Para a review

<!-- omitir se a prova já basta -->

- <o que a próxima porta precisa olhar>

## Handoff

vibe-review | próxima T*

- Chat: com fila restante, recomende um novo chat focado na próxima T*. Sem fila, recomende novo chat para `vibe-review`. O `plan.md` e o `implement.md` vivos são a ponte; continuidade no mesmo chat só por escolha consciente. O commit da task já foi criado; não faça push aqui.

<!-- fatia seguinte: copie o bloco ## Fatia abaixo, não apague as anteriores -->
