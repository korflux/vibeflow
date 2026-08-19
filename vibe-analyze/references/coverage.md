# Taxonomia e passes (mapa interno)

Abrir **só** na varredura da `vibe-analyze`. Não copiar esta tabela para o chat nem para o `analyze.md`.

## 1. Cruzamento (obrigatório)

| De | Para | O que procurar |
|---|---|---|
| Interview Resultado (o quê, sucesso, fora) | Spec Objetivo, A*/C*, Fora | Spec que muda o pedido; Fora da interview que a spec/plan entregam |
| Spec A*/C* | Plan T* campo `Spec:` | A*/C* órfão; T* sem A*/C* (só ok se for infra justificada no Overview) |
| Spec Fora | Plan T* / Escopo | Task que implementa o recusado |
| Plan T* (o quê, arquivos) | Spec Escopo / Implementação | Comportamento, path ou módulo que a spec não topou |
| Os três | `.vibeflow/REGRAS.md` | Choque com Never, Git, semver, política do repo |

Interview ausente: pule a primeira linha. Não invente Resultado.

## 2. Passes (spec-kit analyze, traduzido)

Faça os seis. Ache **instância**, não padrão genérico.

| Pass | Categoria do F* | Sinal |
|---|---|---|
| Duplicação | `duplicacao` | A*/C*/T* que dizem a mesma entrega com redação pior |
| Ambiguidade | `ambiguidade` | Adjetivo sem métrica (rápido, seguro, intuitivo); placeholder (`TODO`, `???`, `<…>`) |
| Furo | `furo` | Verbo sem objeto; aceite não testável; T* cita arquivo que spec/plan não definem |
| Constituição | `constituicao` | Viola MUST/Never do `REGRAS.md`. Sempre `CRITICAL` |
| Cobertura | `cobertura` | A*/C* com zero T*; T* sem requisito; sucesso da interview sem C* |
| Inconsistência | `inconsistencia` | Nome diferente para a mesma coisa; entidade só num arquivo; ordem de T* que fura Deps; A* e T* se anulam |

## 3. Onde o clarify entra (sem virar spec)

Taxonomia do spec-kit clarify vira **filtro de pergunta**, não seção do artefato.

Pergunte (máx. 5, uma por vez) só se **todas** forem verdade:

1. O pass marcou Partial/Missing **e**
2. A resposta muda arquitetura, aceite, fatia ou teste **e**
3. Não é detalhe de execução do plan **e**
4. Não está já fechado em interview/spec/plan.

Categorias úteis para priorizar a fila (não despejar): escopo/sucesso/fora; dado e identidade; jornada e vazio/erro; NFR mensurável (latência, auth, privacidade); integração e falha externa; borda e concorrência; restrição já topada vs chute.

Fora da cota: anote F* `furo` ou `ambiguidade` com remédio `volta vibe-spec` (ou plan). Não invente Q para completar 5.

## 4. Gravidade

| Nível | Quando |
|---|---|
| CRITICAL | Viola REGRAS; A* de caminho feliz sem T*; Fora da interview entregue no plan; fonte faltando que o script já exigiria |
| HIGH | A*/C* em conflito; aceite não testável; T* inventa comportamento; auth/dado/perda sem regra |
| MEDIUM | Drift de termo; borda sem T*; NFR sem verificação |
| LOW | Redação, redundância que não muda ordem |

CRITICAL aberto ⇒ veredito `bloqueado`.
