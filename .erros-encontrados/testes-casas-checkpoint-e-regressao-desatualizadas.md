# Casas de checkpoint e regressão em testes.md desatualizadas pela phase-7

Data: 2026-11-01.

Local: `skills/vibeflow/references/testes.md`, linha 3, introdução de "Casa única": "A mecânica de cada etapa fica na referência dela: passo e checkpoint em `references/implement.md`, regressão completa em `references/review.md`."

Descrição: depois do passo 2 da phase-7 (commit 8ea146b), a execução do checkpoint (E2E dos critérios com tela e conferência do diff contra os critérios) fica em `references/verificador.md`, e `references/implement.md`, passo 2, só despacha o verificador. A regressão completa e seus passos ficam em `references/review/passos.md`, e `references/review.md` apenas delega a ele. A linha de `testes.md` continua apontando para as casas antigas.

Impacto: a linha indica onde fica a mecânica do checkpoint e da regressão, e quem a usa como mapa vai procurá-la no arquivo errado. Não há efeito de comportamento.

Sugestão de correção: trocar a frase por "passo em `references/implement.md`; checkpoint em `references/verificador.md`; regressão completa em `references/review/passos.md`", no passo 5 do plan da phase-7 (`testes.md` está em `Arquivos:`). Depois da correção, apagar este registro.

Relação com a tarefa: mesma causa do registro `testes-ponteiro-julgar-o-produto-quebrado.md`, encontrado no checkpoint A3 e fora do recorte de A3 e A9. Pelo item 6 das regras globais, comentário ou texto desatualizado é defeito e se corrige na mesma alteração.
