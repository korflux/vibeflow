# vibe-review, arquitetura

`/vibe-review` julga o patch, a cobertura e as provas pós-código em um único `review.md`. A IA inspeciona e grava o veredito; o motor resolve a cadeia e prepara o arquivo vivo.

```text
.vibeflow/phases/phase-<n>-<slug>/review.md
.vibeflow/mvp/review.md
```

## 1. Papéis e ownership

| Peça | Responsabilidade |
|---|---|
| `SKILL.md` | Gate, auditoria, cobertura A*/C*, eixos, visual, segurança, veredito e finalização Git da phase. |
| `scripts/review.py`, `review.ps1`, `review.sh` | Inventário, cadeia, alvo, preparação do vivo e relatório. |
| `templates/review.md` | Checklist e forma de etapas no mesmo arquivo. |
| `references/ui-visual-quality.md` | Checklist visual renderizada quando o diff toca UI. |
| `references/security-and-hardening.md` | Catálogo sob demanda para superfícies sensíveis. |
| `.vibeflow/review-report.json` | Evidência operacional, fora do Git. |
| `review.md` | Veredito vivo, histórico de etapas e itens R*. |

O motor não julga o diff, não edita source, não escreve a prosa e não sincroniza `REGRAS.md`.

## 2. Alvo e cadeia

Sem `.vibeflow/`, `INIT_AUSENTE`. Com plan, o alvo é a maior phase com plan sem review; uma review existente é atualizada no mesmo arquivo. `--dir` força uma phase existente. Sem alvo, `--slug` pode abrir uma review avulsa em uma phase nova.

No MVP, `--mvp` exige `interview.md`, `spec.md`, `plan.md` e `analyze.md`, recusa slug/dir e usa somente `.vibeflow/mvp/`.

## 3. Relatório

O relatório contém `vibeflow`, `phases`, `next_n`, `existing`, `plan_pendente`, `rascunho`, `alvo`, `mvp`, `modo_sugerido`, `created`, `modo`, `actions` e `avisos`. `files` lista os artefatos vivos.

`actions` registra apenas criação de phase ou de `review.md`. O relatório não contém conteúdo do julgamento.

## 4. Apply e etapas

1. Reexecuta o inventário e valida a cadeia aplicável.
2. Prepara `review.md` vazio somente no first-pass, quando ausente.
3. Preserva bytes do arquivo vivo existente.
4. A IA escreve diretamente a primeira etapa ou acrescenta a próxima etapa no mesmo arquivo.
5. O script não substitui o histórico, não toca source e não altera `REGRAS.md`.

Status: `rascunho` na primeira etapa, `request-changes` com R* bloqueante aberto, `aprovado` quando o veredito for Approve e o humano confirmar. A sincronização de decisões vigentes ocorre somente depois dessa confirmação, por patch mínimo da IA.

## 5. Auditoria e prova visual

A review cruza pedido, spec, plan, analyze e código real. Reexecuta testes, verifica falsos positivos, segurança, funções alteradas, dados e migrations quando aplicável.

Se o diff tocar UI, seleciona navegador integrado quando disponível, MCP Server `chrome-devtools` para snapshot, screenshot, DOM, estilos, console, rede e assets, e Playwright somente se já existir ou for solicitado. Registra rota, viewport, estado, ações e evidência. Sem capacidade visual, abre `R* Required` e não aprova silenciosamente.

`icon-only` só é aceito para ação universalmente reconhecível, como lixeira para apagar, com nome acessível, foco visível, área de interação e tooltip quando aplicável. Ações ambíguas permanecem textuais.

## 6. Chat, testes e handoff

Recomenda-se novo chat para review, especialmente em re-review ou Request changes. O `review.md`, o diff e o plan são a ponte; continuidade no mesmo chat exige escolha consciente.

Suítes: `docs/vibe-review/tests/test-review.py` e `docs/vibe-review/tests/test-review.sh`. Elas cobrem seleção, apply, phase/MVP, atualização e paridade.

Handoff: `vibe-implement` com R* bloqueante, retorno à spec quando a intenção quebrou, ou finalização Git da phase após aprovação humana.

## 7. Limites

- Um alvo possui um `review.md`; cada nova execução acrescenta `### Etapa N`.
- Review não edita source, testes, lockfile ou artefatos anteriores.
- O motor não interpreta Status, veredito ou diff.
- O arquivo vivo entra no Git; relatório fica fora. Review não corrige source. Após Approve confirmado e sem R* bloqueante, a review valida a suíte final, cria o commit residual quando houver e executa `git push` do upstream atual sem force.
