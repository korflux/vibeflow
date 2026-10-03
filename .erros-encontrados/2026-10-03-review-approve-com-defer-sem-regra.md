# Veredito "Approve com defer" sem regra no vibe-review

- **Data:** 2026-10-03
- **Onde:** `vibe-review/templates/review.md` (Veredito vigente e Veredito desta etapa) e `vibe-review/SKILL.md` (resposta no chat)
- **Problema:** o veredito `Approve com defer` existe no template e na resposta do chat, mas o `SKILL.md` não define quando é permitido, se aceita R* Critical ou Required em `[ ]` e como o item adiado é registrado.
- **Impacto:** quem lê a review pelo disco, como o motor do implement na T1 da phase 14, não consegue distinguir um Approve com defer válido de um estado inconsistente.
- **Sugestão:** definir no `vibe-review` que o defer só vale para Optional ou Nit (a spec da phase 14 exige fila sem Critical ou Required em `[ ]` antes da confirmação final) e registrar o R* adiado na própria linha do veredito.
- **Relação com a tarefa:** a T1 da phase 14 trata `Approve com defer` como `confirmar` sem depender dessa regra. O contrato do review continua pendente.
