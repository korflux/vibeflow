# Registrar execução do novo Modo A

Leia quando atuar como finalizador em coordenacao-v1. Confira no motor o contrato e as proteções; campos/snapshots são validados mecanicamente. Não execute a string --command recebida, não registre segredo nem copie detalhes para plan.

## Operações

No repo, fixe alvo com --dir/-Dir ou --mvp/-Mvp quando necessário. Todas as mutações exigem plan aprovado e --actor/-Actor com identidade operacional do executor. Prova local usa identidade do escritor; integração usa identidade do verificador independente. Finalizador transmite essas identidades, sem se apresentar como executor da prova.

| Operação | Campos |
|---|---|
| init | --operation init --actor finalizador; preserva registro existente |
| local | --operation local --task Tn --input arquivo (repetível) --command "comando já executado" --result verde\|falha --actor escritor |
| integracao | --operation integracao --input arquivo (repetível) --command "comando já executado" --result verde\|falha --actor verificador |
| commit | --operation commit --actor finalizador; somente depois do Git real e prova integrada verde |
| leitura | sem operation; --details mostra snapshots somente ao responsável técnico |

PowerShell equivalentes: -Operation, -Task, -InputPath array, -Command, -Result, -Actor e -Details. Use parâmetros estruturados/arrays com escaping correto; nunca monte código shell concatenando entrada externa.

## Handoff e efeitos

1. Receba evidência e cobertura certificadas pelo responsável, após última edição. Todos os inputs reais de código/teste/configuração que alimentam a prova devem ser listados; motor calcula HEAD/hashes atuais, sem atestar cobertura semântica.
2. Registre local para liberar dependentes. Integração exige todas locais verdes, executor separado e inputs cobrindo os locais. Falha preserva registro anterior. Prova invalida não autoriza conclusão.
3. Com integração verde, confira os paths autorizados e o estado preexistente. Faça staging explícito, confira diff indexado/check e commite IDs integrados ordenados. Registre commit pela operação; motor exige título/ancestralidade/blobs reais. Commit da correção de review usa R* e permanece no Git/review, preservando commit/origem da integração no sidecar.
4. Atualize somente resumo da task e critérios provados. Não copie JSON, hashes, comandos executados ou histórico para plan. Git guarda histórico; execution.json guarda estado atual, versionado com a fase.
5. Registro pós-commit pode ficar residual para o fechamento final. Não crie ciclo de commits para guardar o próprio hash. Depois da confirmação humana, siga finalização delimitada da vibe-review e relate hash/paths/push; falha mantém phase aberta.

Ao renovar integração com inputs corrigidos depois do commit T*, o motor acrescenta `correcao: {base,commit}`: guarda uma única prova original para validar os blobs históricos e preserva o commit T*/origem. Registre novamente `commit` depois do Git da correção; o motor exige commit R* descendente, IDs ordenados presentes como Critical/Required no review e blobs iguais à prova verde atual. O resumo aponta o commit R* certificado; o registro conserva também o T*. Prova atual sem commit R* real não conclui a entrega. A marcação do achado e nova review continuam com seus responsáveis.

O motor não opera índice, commits ou push. Escrita do registro é atômica, com um finalizador por vez. Retomada começa pelo resumo; só abra --details quando o próximo responsável precisar diagnosticar uma contradição.
