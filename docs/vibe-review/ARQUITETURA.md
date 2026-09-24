# vibe-review, arquitetura

`/vibe-review` julga o patch, a cobertura e as provas pós-código em um único `review.md`. Para cada T*, consulta status, dependências/bloqueios, paths e provas no `plan.md`; não exige um novo `implement.md`.

```text
.vibeflow/phases/phase-<n>-<slug>/review.md
.vibeflow/mvp/review.md
```

## 1. Papéis e ownership

| Peça | Responsabilidade |
|---|---|
| `SKILL.md` | Gate, auditoria, cobertura A*/C*, eixos, visual, segurança, veredito e finalização Git da phase. |
| `scripts/review.py`, `review.ps1`, `review.sh` | Inventário, cadeia, alvo, preparação do vivo e JSON operacional no stdout. |
| `templates/review.md` | Checklist e forma de etapas no mesmo arquivo. |
| `references/ui-visual-quality.md` | Checklist visual renderizada quando o diff toca UI. |
| `references/security-and-hardening.md` | Catálogo sob demanda para superfícies sensíveis. |
| `stdout (JSON)` | Evidência operacional transitória, consumida na mesma execução. |
| `review.md` | Tipo e escopo de cada etapa, provas, histórico, veredito final e itens R*. |
| `plan.md` | Status, dependências/bloqueios, paths e provas registrados sob cada T*. |

O motor não julga o diff, não edita source, não escreve a prosa e não sincroniza `REGRAS.md`.

## 2. Alvo e cadeia

Sem `.vibeflow/`, `INIT_AUSENTE`. Com plan, o inventário seleciona a maior phase com plan sem review; uma review existente é atualizada no mesmo arquivo. O script não associa o diff à phase. Antes do apply, a IA compara o alvo sugerido com o diff e usa `--dir` para forçar a phase existente que contém o trabalho quando forem diferentes. Sem alvo, `--slug` pode abrir uma review avulsa em uma phase nova.

No MVP, `--mvp` exige `interview.md`, `spec.md`, `plan.md` e `analyze.md`, recusa slug/dir e usa somente `.vibeflow/mvp/`.

## 3. JSON operacional no stdout

O JSON transitório contém `vibeflow`, `phases`, `next_n`, `existing`, `plan_pendente`, `rascunho`, `alvo`, `mvp`, `modo_sugerido`, `created`, `modo`, `actions` e `avisos`. `files` lista os artefatos vivos.

`actions` registra apenas criação de phase ou de `review.md`. O JSON do stdout não contém conteúdo do julgamento.

## 4. Apply e etapas

1. Reexecuta o inventário e valida a cadeia aplicável.
2. Prepara `review.md` vazio somente no first-pass, quando ausente.
3. Preserva bytes do arquivo vivo existente.
4. A IA escreve diretamente a primeira etapa ou acrescenta a próxima etapa no mesmo arquivo.
5. O script não substitui o histórico, não toca source e não altera `REGRAS.md`.

Status: `rascunho` durante checkpoints e enquanto o veredito final aguarda confirmação, `request-changes` com R* bloqueante aberto, `aprovado` somente após review final, fila concluída, Approve e confirmação humana. A sincronização de decisões vigentes ocorre somente depois dessa confirmação, por patch mínimo da IA.

## 5. Tipos de review e seleção de provas

Checkpoint só é permitido quando `plan.md` declarar o marco e sua justificativa e todas as T* desse marco estiverem concluídas. A etapa julga apenas o marco, suas provas e o contrato ou risco compartilhado indicado. Registra T* ainda abertas, não declara a feature concluída, não marca Approve final e não autoriza sincronização de decisões, commit residual ou push.

Review final exige a fila do plan concluída e julga critérios de aceite, código integrado e riscos alterados. Para cada T*, confere status, `Deps`, bloqueios, `Arquivos` e `Prova`/`Verificação` no `plan.md`; compara os inputs cobertos com o estado integrado e reaproveita evidência verde quando esses paths continuam iguais e a prova ainda cobre a integração. Edição posterior em código/teste invalida somente a prova afetada; atualização de plan, spec ou review não invalida a prova. Executa apenas a verificação necessária que falta para integração ou risco. Não repete automaticamente cada comando da matriz de T*. Toda prova executada ou reaproveitada fica registrada no `review.md` com seu motivo.

## 6. Auditoria e prova visual

A review cruza pedido, spec, plan, analyze e código real. Lê no plan o status, as dependências/bloqueios, os paths e as provas de cada T*, sem exigir `implement.md`. Confere as evidências contra o estado atual e segue a seleção proporcional da seção anterior para executar apenas as verificações que faltam; também verifica falsos positivos, segurança, funções alteradas, dados e migrations quando aplicável.

Aplica os pilares de auditoria ao diff e às superfícies relevantes para o marco ou para a integração final. Se o diff tocar UI, seleciona navegador integrado quando disponível, MCP Server `chrome-devtools` para snapshot, screenshot, DOM, estilos, console, rede e assets, e Playwright somente se já existir ou for solicitado. Começa pela rota/tela, estado e viewport afetados; amplia conforme o impacto em layout, responsividade, interação, componente compartilhado ou risco. Sem capacidade visual, abre `R* Required` e não aprova silenciosamente.

`icon-only` só é aceito para ação universalmente reconhecível, como lixeira para apagar, com nome acessível, foco visível, área de interação e tooltip quando aplicável. Ações ambíguas permanecem textuais.

## 7. Chat, testes e handoff

Recomende iniciar review em novo chat, separado da implementação, especialmente em re-review ou Request changes. Se o humano preferir continuar no mesmo chat, prossiga sem bloquear; o `review.md`, o diff e o plan são a ponte.

Suítes: `docs/vibe-review/tests/test-review.py` e `docs/vibe-review/tests/test-review.sh`. Elas cobrem seleção, override explícito por `--dir`, apply, phase/MVP, atualização e paridade.

Handoff: `vibe-implement` com R* bloqueante, retorno à spec quando a intenção quebrou, ou finalização Git da phase após aprovação humana.

## 8. Limites

- Um alvo possui um `review.md`; cada nova execução acrescenta `### Etapa N`.
- Checkpoint depende de marco explícito no plan; somente a review final pode concluir fase e abrir a finalização Git.
- Review não edita source, testes, lockfile ou artefatos anteriores.
- O motor não interpreta Status, veredito ou diff.
- O arquivo vivo entra no Git; o JSON operacional é transitório no stdout. Review não corrige source. Após Approve final confirmado, fila concluída e sem R* bloqueante, a review executa a prova necessária da integração, cria o commit residual quando houver e executa `git push` do upstream atual sem force.
