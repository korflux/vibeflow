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

A investigação começa pela pergunta de fatiamento e pela dependência que precisa ser provada. Use `rg --files` para localizar `spec.md`, `interview.md`, `REGRAS.md`, entradas e testes; use `rg -n` para localizar A*/C*, decisões, símbolos e comandos de verificação. Abra somente esses paths e as dependências do fluxo; expanda a leitura apenas quando uma lacuna bloquear a ordem. O inventário é mapa de seleção, não autorização para ler a árvore inteira.


## 0. Entender e usar o script

1. Resolva o diretório desta skill e leia o motor que vai executar: `scripts/plan.ps1` no Windows ou `scripts/plan.py` no fluxo Unix. Entenda seleção de alvo, recusas, preparação do destino e preservação do arquivo vivo antes de chamá-lo. Se encontrar defeito, corrija o motor e prove o contrato antes de continuar.
2. No cwd do repo:
   - Windows: `pwsh "<skill>/scripts/plan.ps1"`.
   - Unix: `bash "<skill>/scripts/plan.sh"`.
   - Alvo MVP: acrescente `-Mvp` ou `--mvp`.
3. Leia `.vibeflow/plan-report.json` como evidência operacional. Use `rg --files` e `rg -n` para localizar `spec.md` (obrigatório), `interview.md` se houver, `plan.md` e `.vibeflow/REGRAS.md`, além dos caminhos necessários para desenhar a ordem. Abra somente as entradas e dependências do fluxo, não a árvore inteira.

Erros determinísticos previstos: `INIT_AUSENTE` exige `/vibe-init`. `PLAN_SEM_SPEC` exige spec prévia. `MVP_INESPERADO`, `MODO_INVALIDO`, `PLAN_JA_ANALISADO` e `FASE_AUSENTE` exigem diagnosticar a causa e não devem ser contornados.

## 1. Abrir

Declare em cerca de cinco linhas: rota, modo, alvo, spec, status da spec e estado do artefato vivo.

```text
modo: reuse · alvo: phase-1-lock-bloco · spec: sim · spec-status: aprovado · artefato vivo: presente
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
   - **Validação visual:** Se a entrega envolver frontend, interface web, renderização DOM ou testes de ponta a ponta em navegador, selecionar nesta ordem, navegador integrado (`@Browser` ou equivalente) primeiro quando disponível, MCP Server `chrome-devtools` para snapshot, screenshot, DOM, estilos, console, rede e assets, ou Playwright somente se já existir no repositório ou for solicitado para fluxos repetíveis e assertions.
   - Ausência de capacidade visual deve ser registrada como limitação da verificação. Não transformar a ausência em passe, não obrigar navegador a tasks sem UI e não instalar ferramenta automaticamente só para preencher o gate.
   - Para controles compactos, planejar `icon-only` somente para ações universalmente reconhecíveis, como lixeira para apagar, mantendo nome acessível, área de interação adequada, foco visível e tooltip quando aplicável. Ações ambíguas continuam com texto.
   - Outras dependências críticas de teste e execução devem ser identificadas previamente para garantir que os comandos de verificação sejam executáveis.
3. **Decisões críticas (MVP):** Toda decisão da spec possui ação explícita e as tasks correspondentes citam seus IDs.

## 4. Fatiar

Fatia **vertical** (um caminho usável de ponta a ponta), nunca horizontal (ex.: criar todas as tabelas, depois toda a API, depois toda a UI).

### Regra de Size

`Size` mede a complexidade estrutural para entregar uma única fatia vertical verde. Não é duração, volume de texto nem contagem isolada de arquivos. Para cada T*, pontue as cinco dimensões abaixo com `0`, `1` ou `2` e some os valores:

| Dimensão | 0 | 1 | 2 |
|---|---|---|---|
| Superfície | Um módulo ou artefato | Vários arquivos do mesmo módulo | Vários subsistemas |
| Acoplamento | Isolado | Contrato interno compartilhado | API, schema, auth ou serviço externo |
| Verificação | Unitário ou estático | Integração ou serviço | E2E, navegador, hardware ou dependência externa |
| Incerteza | Padrão conhecido | Investigação pequena | Comportamento ou solução desconhecida |
| Coordenação | Independente e reversível | Uma dependência ou migração | Ordem crítica, rollout ou efeito irreversível |

| Score | Size final | Ação |
|---|---|---|
| 0–3 | low | Uma T* |
| 4–6 | medium | Uma T* |
| 7–8 | high | Uma T*, com justificativa explícita |
| 9–10 | — | Quebrar obrigatoriamente antes de gravar o plan |

`Risk` é separado do score de `Size` e registra impacto potencial: `low` para mudança local e reversível, `medium` para contrato compartilhado ou regressão relevante, e `high` para autenticação, autorização, pagamento, segredo, dado pessoal, produção, perda de dados ou alto blast radius. `Risk: high` pode exigir uma rota e validações mais rigorosas, mas não transforma automaticamente `Size` em `high`.

O campo `Arquivos` continua listando paths prováveis e ajudando a explicar a superfície, mas não define sozinho o tamanho. Não estime minutos no plan. Se o tempo real for observado depois, use-o apenas para calibrar a regra em outra revisão, nunca para classificar uma task individual. O esforço da rota (`low`, `medium`, `high`, `xhigh`, `max`) é independente do `Size`; uma rota `high` pode conter T* `low` ou `medium`.

Quebre obrigatoriamente se: score `9–10`; mais de uma sessão focada; aceite com mais de 3 bullets; múltiplos subsistemas independentes; ou "e" no título indicando mais de um outcome.

### Regras das Tasks:

1. **Walking Skeleton / Smoke Test Inicial:** A primeira task funcional (T1 ou logo após o setup de ferramentas) deve validar o ponto de entrada real (subir a aplicação, executar `--help` no CLI ou rodar o bootstrap inicial).
2. **Estrutura de cada T\*:** Título com verbo + outcome, `Spec: A*/C*`, aceite testável, verificação com comando real do repo, dependências explícitas (`Deps`), arquivos prováveis, `Size` com score e `Risk` separado.
3. **Decisões Críticas:** Quando a task implementar ou substituir decisão crítica, adicionar `Decisões: <ID> (<ação>)`.
4. **Comandos de Verificação Reais:** Toda task exige pelo menos um comando de teste executável no repositório. Teste apenas manual recusa o aceite; leitura de arquivo não conta como verificação.
5. **Dependências (`Deps`):** Declarar apenas dependências reais de execução. Fatias independentes usam `Deps: nenhuma`.
6. **Unidade de execução:** Cada `T*` deve ser uma fatia verificável e independente para execução, commit e handoff. Não criar agrupamentos ou portas intermediárias fora das dependências reais.
7. **UI Greenfield:** Criar uma task de tokens/kit antes das telas caso não haja Design System já existente.
8. **Banco de Dados e Migrations:** Alocar migrations e schemas dentro das respectivas fatias verticais (`T*`) que os consom, com comandos executáveis de migration e seed mínimo para testes. Migrations devem ser não destrutivas (padrão expand/contract).

IDs estáveis: `T1`, `T2`, `T3`... em ordem sequencial. Sem prefixos arbitrários como `T001`, `[P]` ou `[US1]`.

## 5. Escrever e Salvar

Artefato vivo: `<created.path>/plan.md`. Molde: `templates/plan.md`. Mantenha `# Status: rascunho` enquanto o plano estiver em elaboração.
Não pergunte se pode salvar e não cole o corpo do documento no chat.

1. Execute o apply. Ele prepara o arquivo vivo somente quando ausente e preserva bytes quando ele já existe:
   - Modo phase:
     `pwsh "<skill>/scripts/plan.ps1" -Apply`
     `bash "<skill>/scripts/plan.sh" --apply`
   - Modo MVP:
     `pwsh "<skill>/scripts/plan.ps1" -Apply -Mvp`
     `bash "<skill>/scripts/plan.sh" --apply --mvp`
2. Escreva ou atualize diretamente o arquivo vivo. Omita seções não aplicáveis.
3. Responda no chat apenas:

```text
Plan gravado: <created.path>/plan.md

- Overview: <1 linha>
- Ordem: Fase 1 ... → Fase 2 ... (N tasks, cada uma com sua verificação)
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

Não commite no git nesta porta. O commit começa na `vibe-implement`, depois da prova verde de cada task. Não dispare a próxima skill a menos que o usuário tenha pedido explicitamente para avançar (§6).
Informe que o arquivo vivo `plan.md` entra no git e que `plan-report.json` fica de fora. Recomende abrir um novo chat para `vibe-implement`; continuar no mesmo chat é permitido somente por escolha consciente do humano. O `plan.md` vivo e o handoff são a ponte entre chats.
Handoff normal: `vibe-implement`. Handoff MVP: `vibe-analyze` (pois o modo max exige análise antes do código).
Zero código nesta execução.

