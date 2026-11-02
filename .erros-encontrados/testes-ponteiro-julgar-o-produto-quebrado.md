# Ponteiro de testes.md aponta para seção da review que saiu de review.md

Data: 2026-11-01.

Local: `skills/vibeflow/references/testes.md`, linha 18: "A severidade de caso ausente segue `references/review.md` (Julgar o produto)."

Descrição: o passo 2 da phase-7 (commit 8ea146b) moveu o procedimento do revisor na review (Passos, incluindo "2. Julgar o produto") de `references/review.md` para `references/review/passos.md`, onde a seção agora é `### 2. Julgar o produto`. `review.md` não tem mais nenhuma seção com esse nome. O ponteiro de `testes.md` não foi atualizado porque o arquivo não estava em `Arquivos:` do passo.

Impacto: o conteúdo da regra (caso ausente: Required quando a spec traz o limite ou a tabela de exemplos, Nit nos demais) continua em `references/review/passos.md`, item 2.2, e o revisor o alcança pelo próprio fluxo. Quem segue o ponteiro a partir de `testes.md` não encontra a seção. Nenhum gate, commit, checkpoint ou Modo B muda de comportamento.

Sugestão de correção: trocar o ponteiro por `references/review/passos.md` (Julgar o produto) no passo 4 ou no passo 5 do plan da phase-7, que já tocam `testes.md`. Depois da correção, apagar este registro (item 19 das regras globais: erro corrigido tem o registro apagado).

Relação com a tarefa: defeito causado pelo passo 2 da phase-7, encontrado no checkpoint A3. Fica fora do recorte de A3 e A9 e não foi corrigido pelo verificador.
