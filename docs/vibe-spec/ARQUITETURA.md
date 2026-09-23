# vibe-spec, arquitetura

`/vibe-spec` grava o comportamento decidido para que o plan não invente escopo. A IA conduz o gate semântico e escreve o documento vivo; o motor resolve o alvo e prepara o arquivo.

```text
.vibeflow/phases/phase-<n>-<slug>/spec.md
.vibeflow/mvp/spec.md
```

## 1. Papéis e ownership

| Peça | Responsabilidade |
|---|---|
| `SKILL.md` | Entender a intenção, fechar dúvidas e redigir comportamento, aceite e limites. |
| `scripts/spec.py`, `spec.ps1`, `spec.sh` | Inventário, resolução phase/MVP, validação de predecessores, preparação do vivo e JSON operacional no stdout. |
| `templates/spec.md` | Estrutura do documento. O motor não preenche prosa. |
| `references/ui-visual-direction.md` | Catálogo consultado somente quando a spec toca UI. |
| `stdout (JSON)` | Evidência operacional transitória, consumida na mesma execução. |
| `spec.md` | Fonte viva, rascunho ou aprovada, commitável. |

## 2. Dependências e seleção

Sem `.vibeflow/`, `INIT_AUSENTE`. No modo phase, o alvo é a maior phase com `interview.md` sem `spec.md`, depois a maior phase com spec sem plan. Se não houver alvo, `--slug` cria uma phase nova. `--dir` força uma phase existente.

No modo MVP, `--mvp` exige `.vibeflow/mvp/interview.md`, recusa `--slug` e `--dir`, e nunca cria phase. `plan.md` existente bloqueia uma nova escrita semântica para esse alvo.

Flags públicas:

```text
python spec.py [--root PATH] [--apply] [--slug TEXTO] [--dir phase-N-slug] [--mvp]
pwsh spec.ps1 [-Root PATH] [-Apply] [-Slug TEXTO] [-Dir phase-N-slug] [-Mvp]
bash spec.sh [--root PATH] [--apply] [--slug TEXTO] [--dir phase-N-slug] [--mvp]
```

## 3. JSON operacional no stdout

O JSON transitório mantém `vibeflow`, `phases`, `next_n`, `existing`, `interview_pendente`, `rascunho`, `alvo`, `mvp`, `modo_sugerido`, `created`, `modo`, `actions` e `avisos`. O campo `files` lista apenas artefatos vivos da cadeia.

`actions` registra criação de `phases/.gitkeep`, phase, MVP ou do arquivo vivo. O JSON não descreve conteúdo semântico nem uma etapa de transporte temporário.

## 4. Apply e escrita direta

1. Reexecuta o inventário e valida `spec.md` predecessor, slug e colisões.
2. Prepara `spec.md` vazio quando o destino ainda não possui o arquivo.
3. Preserva byte a byte o arquivo vivo existente.
4. Emite o JSON operacional no stdout para leitura imediata da IA.
5. A IA escreve ou atualiza diretamente o `spec.md`, mantendo `# Status: rascunho` durante a elaboração.
6. A aprovação é um patch no vivo; um novo apply não é necessário para mudar o status.

O script não escolhe comportamento, não pergunta, não preenche markdown e não altera `REGRAS.md`. Em falhas de seleção, o arquivo anterior permanece intacto.

## 5. Artefato e decisões

Seções: Objetivo, Cobertura da origem, Suposições e decisões, Escopo e comportamento, Fora, Direção visual quando aplicável, Checklist de entrega, Contratos e restrições necessárias quando houver, Como provar, Boundaries e Handoff. A cobertura liga jornadas, páginas e módulos aplicáveis da interview a `F*`, decisão, Fora ou N/A, sem copiar a entrevista. Sem interview, registra apenas partes da entrega que poderiam ficar esquecidas.

Quando a entrega tem fluxo ou UX, o Escopo usa o molde `F*` com Jornada, Rota, Gatilho, Pré-condição, Superfície por passo, Passos numerados com ação e resposta, Validações, Erros com código e mensagem segura, Estados com vazio, loading, erro, sucesso e sem permissão, e Aceite `A*`. Página informativa simples aceita `F*` curto e N/A fundamentado para regras inexistentes. Passo sem superfície é defeito. Handoff é `vibe-design` com UI visível, senão `vibe-plan`. `plan.md` existente bloqueia nova escrita, pedido novo exige outra phase.

A spec fecha contratos que afetam o resultado e indica a evidência observável de cada `A*`. Arquivos, comandos, ordem de execução, testes e escolhas internas reversíveis ficam no plan.
`A*` e `C*` descrevem resultados, não unidades de teste. Uma prova por capacidade pode cobrir vários critérios sem fragmentá-los artificialmente.

Para entradas externas, a spec fecha a allowlist de campos e valores aceitos e o tamanho máximo por entrada. Para acesso de navegador entre origens, declara a allowlist de origens CORS e nunca combina origem `*` com credenciais; quando CORS não se aplica, registra N/A com motivo. A skill registra esses limites junto dos demais controles de segurança exigidos pelo fluxo.

Sem Open Questions, mural de user story ou CSS, paleta ou token visual na spec. Nome de token público existente pode aparecer como limite de escopo, sem definir valor. A restrição não trata de token de autenticação ou API. IDs de decisões críticas do MVP atravessam o plan; publicação de decisão vigente só ocorre após review aprovada e confirmação humana.

## 6. Erros e testes

Falhas previstas usam `CODIGO: descrição` no stderr. O contrato cobre `INIT_AUSENTE`, `PHASES_INESPERADO`, `MVP_INESPERADO`, `MVP_INTERVIEW_AUSENTE`, `SPEC_SEM_ALVO`, `PLAN_SEM_SPEC`, `SPEC_JA_PLANEJADA`, `FASE_AUSENTE`, `FASE_EXISTE`, `SLUG_INVALIDO` e `MODO_INVALIDO` conforme o modo.

Suítes: `docs/vibe-spec/tests/test-spec.py` e `docs/vibe-spec/tests/test-spec.sh`. Elas verificam criação, reexecução, MVP, `--dir`, colisões, paridade e preservação do vivo.

## 7. Limites

- A IA é dona da prosa; o script é dono de path e inventário mecânico.
- Um alvo possui um `spec.md`; pedido novo usa outra phase.
- O inventário emitido no stdout é um mapa de seleção. A IA usa `rg --files` e `rg -n` para abrir somente as entradas e dependências relevantes.
- A continuidade pode permanecer no chat de `interview`; `plan` deve receber o caminho e o status do arquivo vivo.
- O arquivo vivo entra no Git; o JSON do inventário é transitório no stdout. Não há commit automático.
