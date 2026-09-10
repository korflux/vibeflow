# vibe-review, análise

## Problema

Review precisa julgar o diff e a cobertura sem virar uma segunda implementação nem espalhar vereditos por arquivos. O contrato anterior ainda descrevia um transporte temporário na primeira passagem, embora re-review já editasse o vivo.

## Decisão de desenho

```text
diff + artefatos da cadeia
  → auditoria dirigida e reexecução das provas
  → first-pass prepara review.md
  → IA grava etapa, R* e veredito diretamente
  → humano confirma ou pede correção
  → re-review acrescenta etapa no mesmo arquivo
  → Approve confirmado: commit residual e push final da phase
```

A IA começa pela pergunta de auditoria e pelos T*/diff relevantes. Usa `rg --files` e `rg -n` para localizar paths, símbolos, testes e referências aplicáveis, abrindo somente as dependências do fluxo. O histórico do chat não substitui a prova no disco.

## Escrita direta e etapas

`review.md` é a fonte viva do julgamento. O motor prepara um arquivo vazio na primeira passagem e preserva o existente em todas as outras. A IA acrescenta etapas, fecha R* com prova e atualiza o veredito vigente diretamente.

Essa escolha mantém o histórico no mesmo path e permite que implement consuma a fila de remédio sem interpretar outro formato. A sincronização de decisões em `REGRAS.md` continua explicitamente pós-aprovação humana.

## Finalização Git

Review continua sem corrigir source. Depois de Approve confirmado, todas as tasks e R* bloqueantes fechados e a suíte final verde, ela valida o escopo restante, cria somente o commit residual da phase quando houver mudanças e faz `git push` para o upstream atual sem force. O push não acontece por task.

## Visual e acessibilidade

Quando o diff toca UI, a review usa a referência visual existente e registra contexto renderizado. Navegador integrado é a primeira opção, Chrome DevTools MCP cobre inspeção, e Playwright só entra se já existir ou for solicitado. Screenshot isolado não substitui a leitura de comportamento, geometria, estados e console/rede/assets.

Controles compactos reduzem ruído apenas quando a ação é universalmente reconhecível. `icon-only` exige semântica acessível, foco, área de interação e feedback; ação ambígua mantém texto.

## Chat

Review recomenda novo chat para evitar que a conclusão seja influenciada pela própria implementação. O humano pode continuar conscientemente; review.md e diff carregam o contexto verificável.

## Cortes

| Corte | Motivo |
|---|---|
| `vibe-converge` separado | Cobertura e julgamento ficam na mesma review. |
| Correção de código pela review | Finding deve apontar o remédio para implement. |
| Segundo `review.md` por rodada | Etapas no mesmo arquivo preservam o veredito vigente. |
| Browser obrigatório para task sem UI | A prova visual só abre quando o diff toca interface. |
| Publicação automática de decisões | Exige Approve sem bloqueios e confirmação humana. |
| Push antes da aprovação | O remoto só recebe a phase depois do fechamento da review. |

## Impacto

Review e implement compartilham o mesmo histórico: a primeira registra R*, a implementação prova o remédio e a etapa seguinte fecha o item. A troca de chat não perde o julgamento porque o arquivo vivo é acumulativo.
