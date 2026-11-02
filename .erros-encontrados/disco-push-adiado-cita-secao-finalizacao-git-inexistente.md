# disco.md manda gravar o push adiado numa seção "Finalização Git" que o template do review não tem

- Data: 2026-11-02
- Local: `skills/vibeflow/references/disco.md`, seção Estado da phase, linha "Push adiado" (linha 159 no HEAD `cff4584`; já presente em `eaa2f3d`, linha 137).
- Descrição: a linha diz que o líder grava a recusa ou o adiamento do push "na seção Finalização Git do `review.md`". `skills/vibeflow/templates/review.md` não tem seção com esse nome; o comentário de `## Aprovação humana` é que manda o líder acrescentar `- Push adiado pelo humano: <AAAA-MM-DD>` ali. Nenhum outro arquivo do pacote cita "Finalização Git".
- Impacto: baixo. O líder pode criar uma seção inexistente no `review.md` ou procurar a seção e não achar; o script de estado lê a linha pelo conteúdo, então o estado não muda, mas o artefato pode sair fora do template.
- Sugestão de correção: trocar "na seção Finalização Git do `review.md`" por "em `## Aprovação humana` do `review.md`", como diz o comentário de `templates/review.md`.
- Relação com a tarefa: fora do recorte da phase-8 (a linha não está no diff `eaa2f3d..HEAD`); encontrado pelo revisor na revisão de consistência da review da phase-8.
