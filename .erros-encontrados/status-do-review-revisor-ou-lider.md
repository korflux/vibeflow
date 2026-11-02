# Dono da linha `# Status:` do review.md ambíguo entre revisor e líder

Data: 2026-11-02.

Local: `skills/vibeflow/references/review/passos.md` (passo 3, Gravar) contra `skills/vibeflow/references/revisor.md` (Limites) e `skills/vibeflow/SKILL.md` (seção 3, marcações do líder).

Descrição: o passo 3 de `review/passos.md` manda o revisor marcar o veredito com "status `rascunho`" no Approve e "status `request-changes`" no Request changes, e diz que só o líder grava `aprovado`. O `revisor.md` (Limites) e o `SKILL.md` dizem que `# Status:` é marcação do líder, sem exceção para `rascunho` e `request-changes`. A ambiguidade já existia na 5.4.0 (`references/review.md` e `SKILL.md` de `f3fce47`).

Impacto: um revisor literal pode deixar `# Status: request-changes` depois de propor Approve, e a tabela de estados de `references/disco.md` só leva à confirmação com `# Status: rascunho`; o líder precisa notar e trocar a linha, ou a retomada lê a etapa errada (review, re-review, em vez de review, confirmar).

Sugestão: escolher um dono. O mais simples é o revisor gravar `rascunho` ou `request-changes` junto com o veredito, e o `revisor.md` (Limites) e o `SKILL.md` restringirem ao líder só `aprovado`, a aprovação humana, as caixas e o `[x]` de R*. Mudança de prosa, sem efeito em script.

Relação com a tarefa: encontrada na re-review da phase-7 ao gravar o veredito; está fora do diff da correção (`ccd2ecc..73044b2`) e não bloqueia. Nesta re-review o revisor marcou o veredito e deixou `# Status:` ao líder, como o brief pediu.
