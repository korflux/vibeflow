# Review: IA como piloto e scripts como auxiliares
# Pasta: phase-5-ia-piloto-scripts-auxiliares
# Status: rascunho

## Contexto

- Alvo: `phase-5-ia-piloto-scripts-auxiliares`
- Cadeia: `spec.md` / `implement.md`
- O que muda: a IA passa a pilotar a run e auditar scripts e relatórios, enquanto scripts preservam o papel auxiliar nas operações mecânicas e determinísticas.

## Cobertura

| Chave | Código | Notas |
|---|---|---|
| A1 | ok | `.vibeflow/REGRAS.md`, seção `Papéis na run` |
| A2 | ok | `.vibeflow/REGRAS.md`, leitura do motor e auditoria do resultado |
| A3 | ok | `.vibeflow/REGRAS.md`, relatório definido como evidência operacional |
| A4 | ok | Regras de `n`, slug, promoção, backup, hash e paridade mantidas |
| A5 | ok | `.vibeflow/REGRAS.md`, diagnóstico, correção e fallback sem contorno de proteção |
| C1 | ok | Busca sem ocorrência de `Script primeiro` e `contrato script` |
| C2 | ok | Papéis separados entre IA, skill, script e humano |
| C3 | ok | Alterações da entrega limitadas às regras e aos artefatos da fase 5 |

## Checklist de correções

nenhum bloqueio

## DoD

- [x] Diff revisada contra a spec.
- [x] `git diff --check` passou no escopo da entrega.
- [x] Mudanças locais anteriores em `vibe-init/` permaneceram intactas.

## Notas

- O `git diff --check` global ainda aponta linhas vazias no fim de `vibe-init/SKILL.md` e `vibe-init/scripts/init.sh`, ambas pertencentes à diff local anterior e fora desta entrega.
- O relatório de seleção automática apontou outra fase; o `--dir` foi necessário no apply. A nova regra cobre esse cenário sem alterar o script nesta fase.

## Veredito vigente

- [x] **Approve**, nenhum Critical/Required em `[ ]`
- [ ] **Request changes**, há Critical/Required em `[ ]`

## Handoff

cadeia fechada

- [ ] Aprovação humana (leu o arquivo e confirmou)

## Etapas

### Etapa 1, first-pass, diff e fatia avulsa

- Leu: `implement.md`, sim
- Abriu: nenhum
- Fechou: nenhum
- Veredito desta etapa: Approve
