---
name: vibe-plan
description: >
  Fatia a spec em tasks verificáveis e grava em `.vibeflow/phases/phase-N-slug/plan.md` ou `.vibeflow/mvp/plan.md`.
  Use when the user runs /vibe-plan, pede plan, fatiar a spec, criar tasks,
  todo, ordem de execução, ou a rota é high/xhigh/max com spec em disco,
  mesmo que não diga vibe-plan.
---

# vibe-plan

Não invente `n`, slug ou path. Sem spec aprovada no alvo, não há plan. Sem `.vibeflow/`, pare e mande `/vibe-init`.
Um único arquivo. Não escreva código nesta skill. Open Questions no arquivo é defeito.
No MVP, preserve a ação e os IDs das decisões críticas nas tasks que as implementam.


## 0. Entender e usar o script

1. Resolva o diretório desta skill e leia o motor que vai executar: `scripts/plan.ps1` no Windows ou `scripts/plan.py` no fluxo Unix. Entenda seleção de alvo, recusas e promoção atômica temporária antes de chamá-lo. Se encontrar defeito, corrija o motor e prove o contrato antes de continuar.
2. No cwd do repo:
   - Windows: `pwsh "<skill>/scripts/plan.ps1"`.
   - Unix: `bash "<skill>/scripts/plan.sh"`.
   - Alvo MVP: acrescente `-Mvp` ou `--mvp`.
3. Leia `.vibeflow/plan-report.json` como evidência operacional. Abra `spec.md` (obrigatório), `interview.md` se houver e `plan.md` se rascunho. Leia `.vibeflow/REGRAS.md` e os caminhos do projeto necessários para desenhar a ordem de execução.

Erros determinísticos previstos: `INIT_AUSENTE` exige `/vibe-init`. `PLAN_SEM_SPEC` exige spec prévia. `MVP_INESPERADO`, `MODO_INVALIDO`, `PLAN_JA_ANALISADO` e `FASE_AUSENTE` exigem diagnosticar a causa e não devem ser contornados.

## 1. Abrir

Declare em cerca de cinco linhas: rota, modo, alvo, spec, status da spec e wip.

```text
modo: reuse · alvo: phase-1-lock-bloco · spec: sim · spec-status: aprovado · wip: ausente
```

- `modo_sugerido=criar`: não há pasta com spec. Não invente fase; mande `/vibe-spec`.
- `rota=mvp`: alvo fixo `.vibeflow/mvp`, sem `--dir`; a spec precisa estar aprovada e declarar as decisões críticas.

## 2. Gate

| Sinal | Ação |
|---|---|
| Typo ou uma linha óbvia | Não usar plan |
| Sem `spec.md` no alvo | Parar. Encaminhar para `/vibe-spec` |
| Spec `# Status: rascunho` e o humano pediu o plan | Alterar a spec para `aprovado` diretamente no arquivo (1 linha no chat) e seguir |
| Spec rascunho sem pedido de plan | Parar. Pedir leitura e aprovação da spec |
| Intenção, sucesso ou limites frouxos | Devolver para `vibe-interview` ou `vibe-spec`. Não completar no chute |
| Dúvida pontual de ordem técnica | Resolver via chat (Q + RECOMENDO) |
| `analyze.md` já existente no alvo | Não sobrescrever. Pedido novo exige outra fase |

```text
Q: <decisão que trava o fatiamento>
RECOMENDO: <opção>, <1 linha explicando o porquê e impacto>
(ok / outra?)
```

## 3. Conferência de Pré-requisitos e Ferramentas

Antes de fatiar, audite a spec e o ambiente:


1. **Spec sólida:** A*/C* observáveis, limites claros de Fora, direção visual definida se houver UI, caminhos existentes ou acordados.
2. **Validação de Ferramentas de Teste e Suporte:**
   - **Gitleaks:** Se o repositório/CI prevê varredura de segredos ou verificação de credenciais, verificar se o executável `gitleaks` está disponível no ambiente. Se ausente, o plano DEVE alocar uma task inicial (ex.: T1 de setup) para instalar/configurar o gitleaks.
   - **MCP chrome-devtools:** Se a entrega envolver frontend, interface web, renderização DOM ou testes de ponta a ponta em navegador, verificar se o MCP `chrome-devtools` está disponível. Se ausente, alocar uma task inicial para instalação/configuração do MCP.
   - Outras dependências críticas de teste e execução devem ser identificadas previamente para garantir que os comandos de verificação sejam executáveis.
3. **Decisões críticas (MVP):** Toda decisão da spec possui ação explícita e as tasks correspondentes citam seus IDs.

## 4. Fatiar

Fatia **vertical** (um caminho usável de ponta a ponta), nunca horizontal (ex.: criar todas as tabelas, depois toda a API, depois toda a UI).

| Size | Files | Ação |
|---|---|---|
| low | 1 | Uma T* |
| medium | 1 a 2 | Uma T* |
| high | 3 a 5 | Uma T* |
| xhigh / max | 5+ ou alto risco | Quebrar obrigatoriamente |

Quebre se: mais de uma sessão focada; aceite com mais de 3 bullets; múltiplos subsistemas independentes; "e" no título.

### Regras das Tasks:

1. **Walking Skeleton / Smoke Test Inicial:** A primeira task funcional (T1 ou logo após o setup de ferramentas) deve validar o ponto de entrada real (subir a aplicação, executar `--help` no CLI ou rodar o bootstrap inicial).
2. **Estrutura de cada T\*:** Título com verbo + outcome, `Spec: A*/C*`, aceite testável, verificação com comando real do repo, dependências explícitas (`Deps`), arquivos prováveis e `Size`.
3. **Decisões Críticas:** Quando a task implementar ou substituir decisão crítica, adicionar `Decisões: <ID> (<ação>)`.
4. **Comandos de Verificação Reais:** Toda task exige pelo menos um comando de teste executável no repositório. Teste apenas manual recusa o aceite; leitura de arquivo não conta como verificação.
5. **Dependências (`Deps`):** Declarar apenas dependências reais de execução. Fatias independentes usam `Deps: nenhuma`.
6. **Checkpoints:** A cada 2 ou 3 tasks, definir checkpoint com a suíte de testes do grupo e fluxo integrado observável.
7. **UI Greenfield:** Criar uma task de tokens/kit antes das telas caso não haja Design System já existente.
8. **Banco de Dados e Migrations:** Alocar migrations e schemas dentro das respectivas fatias verticais (`T*`) que os consom, com comandos executáveis de migration e seed mínimo para testes. Migrations devem ser não destrutivas (padrão expand/contract).

IDs estáveis: `T1`, `T2`, `T3`... em ordem sequencial. Sem prefixos arbitrários como `T001`, `[P]` ou `[US1]`.

## 5. Escrever e Salvar

Wip: `.vibeflow/plan-wip.md`. Molde: `templates/plan.md`. Status inicial: `rascunho`.
Não pergunte se pode salvar e não cole o corpo do documento no chat.

1. Preencha o wip. Omita seções não aplicáveis.
2. Execute o apply:
   - Modo phase:
     `pwsh "<skill>/scripts/plan.ps1" -Apply`
     `bash "<skill>/scripts/plan.sh" --apply`
   - Modo MVP:
     `pwsh "<skill>/scripts/plan.ps1" -Apply -Mvp`
     `bash "<skill>/scripts/plan.sh" --apply --mvp`
3. Responda no chat apenas:

```text
Plan gravado: <created.path>/plan.md

- Overview: <1 linha>
- Ordem: Fase 1 ... → Fase 2 ... (N tasks, checkpoints em ...)
- Ferramentas essenciais: <gitleaks / chrome-devtools validados ou task de setup alocada>
- Primeira T*: <título do smoke test / walking skeleton>

Arquivo disponível em <created.path>/plan.md. Responda "aprovado" para confirmar, "pode ir pro implement" (ou "pode ir para a próxima fase") para avançar imediatamente, ou indique os ajustes desejados.
```

## 6. Ajuste ou Aprovação

| Resposta | Ação |
|---|---|
| Aprovado (sem pedir próxima porta) | Alterar `# Status: aprovado` diretamente no vivo; parar e aguardar próximo comando |
| "Pode ir pro implement" / "pode ir para a próxima fase" / pede código / `vibe-implement` | Alterar `# Status: aprovado` no vivo; iniciar imediatamente `vibe-implement` (ou `vibe-analyze` se rota MVP) |
| Pedido de alteração | Patch direto no arquivo vivo; até 5 bullets no chat; solicitar nova conferência |
| "Parece bom" sem pedir implementação | Perguntar: "Aprovado no arquivo ou deseja algum ajuste?" |
| Spec ou intenção quebrou | Devolver para `vibe-spec` ou `vibe-interview`. Não forçar implementação |

Rascunho sem "aprovado" e sem pedido da próxima porta não autoriza iniciar o código.

## 7. Fechar

Não commite no git. Não dispare a próxima skill a menos que o usuário tenha pedido explicitamente para avançar (§6).
Informe que o arquivo `plan.md` entra no git e que `plan-report.json` e `plan-wip.md` ficam de fora.
Handoff normal: `vibe-implement`. Handoff MVP: `vibe-analyze` (pois o modo max exige análise antes do código).
Zero código nesta execução.

