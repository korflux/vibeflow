# Relatório fixo

Única casa do relatório que todo papel devolve ao líder. Fica em arquivo próprio para cada despacho abrir só isto, sem ler `references/delegation.md` inteiro.

```text
estado: verde | bloqueado | pergunta
etapa: init | interview | spec | plan | analyze | passo | checkpoint | correcao | review | exploracao | texto
paths: <alterados, um por linha, ou nenhum>
prova: <comando e resumo do resultado, só com as falhas, sem log completo; saída do teste do critério vermelho antes da mudança e verde depois, ou motivo da isenção; inputs reais; gates estáticos rodados sobre os arquivos alterados, conforme references/implementador.md (Codar e provar); quando o papel captura ou cita capturas, paths das imagens finais conforme references/chrome-devtools.md>
cobertura: <critérios certificados e limites do recorte>
pendencias: <nenhuma ou falha/impedimento concreto>
proximo: <ação e responsável>
pergunta: <somente quando pergunta; recomendação>
```

Verde certifica só o recorte: o relatório distingue etapa implementada de entrega comprovada, e prova do passo verde não é entrega comprovada. Bloqueado é impedimento real; pergunta, decisão humana material. O revisor acrescenta os campos de `references/analyze.md` (Saída) ou `references/review/passos.md` (Saída).

O relatório é a única saída do papel além dos paths do recorte: medição, evidência e anotação vão nele, nunca em arquivo na pasta da phase (`references/disco.md`, Paths).
