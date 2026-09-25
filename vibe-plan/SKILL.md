---
name: vibe-plan
description: >
  Fatia a spec de software em tarefas de implementação verificáveis e grava em `.vibeflow/phases/phase-N-slug/plan.md` ou `.vibeflow/mvp/plan.md`. Use when the user runs /vibe-plan, pede para fatiar uma funcionalidade em tarefas de código, ou a rota de software é high/xhigh/max com spec em disco, mesmo que não diga vibe-plan. Não se aplica a planos de documentos avulsos.
---

# vibe-plan

Se encontrar `.vibeflow/REGRAS.md`, `REGRAS.md` ou `CLAUDE.md` de uma instalação anterior, execute `vibe-init` para migrar as regras e então retome esta etapa. Fontes divergentes continuam para consolidação.

Não invente `n`, slug ou path. Sem spec aprovada no alvo, não há plan. Sem `.vibeflow/`, pare e mande `/vibe-init`.
Um único arquivo. Não escreva código nesta skill. Open Questions no arquivo é defeito.
No MVP, preserve a ação e os IDs das decisões críticas nas tasks que as implementam.

A investigação começa pelo resultado pedido e pelas dependências reais de execução. Use `rg --files` para localizar `spec.md`, `interview.md`, `AGENTS.md`, entradas e testes; use `rg -n` para localizar A*/C*, decisões, símbolos e comandos de verificação. Abra somente esses paths e as dependências do fluxo; expanda a leitura apenas quando uma lacuna bloquear o fatiamento. O inventário é mapa de seleção, não autorização para ler a árvore inteira.


## 0. Entender e usar o script

1. Resolva o diretório desta skill e leia o motor que vai executar: `scripts/plan.ps1` no Windows ou `scripts/plan.py` no fluxo Unix. Entenda seleção de alvo, recusas, preparação do destino e preservação do arquivo vivo antes de chamá-lo. Se encontrar defeito, corrija o motor e prove o contrato antes de continuar.
2. No cwd do repo:
   - Windows: `pwsh "<skill>/scripts/plan.ps1"`.
   - Unix: `bash "<skill>/scripts/plan.sh"`.
   - Alvo MVP: acrescente `-Mvp` ou `--mvp`.
3. Leia o JSON operacional emitido no stdout pelo comando acima. Use `rg --files` e `rg -n` para localizar `spec.md` (obrigatório), `interview.md` se houver, `plan.md` e `AGENTS.md`, além dos caminhos necessários para definir resultados, dependências e provas. Abra somente as entradas e dependências do fluxo, não a árvore inteira.

Erros determinísticos previstos: `INIT_AUSENTE` exige `/vibe-init`. `PLAN_SEM_SPEC` exige spec prévia. `MVP_INESPERADO`, `MODO_INVALIDO`, `PLAN_JA_ANALISADO` e `FASE_AUSENTE` exigem diagnosticar a causa e não devem ser contornados.

## 1. Abrir

Declare em cerca de cinco linhas: rota, modo, alvo, spec, status da spec e estado do artefato vivo.
Ao iniciar após `vibe-spec` ou `vibe-design`, recomende um chat novo. Se o humano preferir continuar no chat atual, prossiga sem bloquear.

```text
modo: reuse · alvo: phase-1-lock-bloco · spec: sim · spec-status: aprovado · artefato vivo: presente · chat: novo recomendado
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
| Com UI visível sem `design.md` aprovado na mesma pasta | Parar. Encaminhar para `vibe-design` |
| Sem UI visível | Registrar N/A explícito no plan, sem bloqueio |
| `analyze.md` já existente no alvo | Não sobrescrever. Pedido novo exige outra fase |

```text
Q: <decisão que trava o fatiamento>
RECOMENDO: <opção>, <1 linha explicando o porquê e impacto>
(ok / outra?)
```

## 3. Prontidão das provas

Depois de definir as provas por task e antes de fechar a fila, confira somente os runtimes, comandos, serviços e capacidades exigidos por elas:

1. **Spec sólida:** A*/C* observáveis, limites claros de Fora, direção visual definida se houver UI e caminhos existentes ou acordados. Com UI visível, exige `design.md` aprovado na mesma pasta; sem UI, registra `Design: N/A`.
2. **Dependências das provas:** Derive a lista dos comandos `Verificação` planejados. Confira runtime e package manager (por exemplo, Node), serviços, comandos (incluindo `gitleaks` quando CI ou repo o exigirem) e capacidades externas necessárias. Use manifests, scripts, workflows de CI e ferramentas disponíveis como evidência; registre no plan onde cada requisito está disponível, localmente ou no CI. Considere-o atendido quando estiver disponível no ambiente onde a prova planejada vai rodar.
3. **Ausências:** Não deixe requisito necessário em checklist opcional. Ausência local não exige setup quando a prova será executada no CI e os requisitos estão atendidos lá. Se um requisito compartilhado faltar no ambiente planejado para a prova, inclua sua resolução na T1; se só for usado depois, inclua a resolução na primeira T* que depende dele. Não crie T* separada de preparo, a menos que o setup persistente seja um resultado do projeto. Se uma capacidade externa, como MCP, não estiver disponível e não houver equivalente, registre o bloqueio na fila; não marque a prova como concluída nem instale ferramentas automaticamente.
4. **Prova visual por task:** Para cada task que altera UI, registre `Visual: necessária` quando o aceite depender de aparência, layout, responsividade, estado ou interação renderizados no navegador. Registre `Visual: dispensada` com o motivo quando comandos ou testes existentes provarem o aceite e nenhuma saída renderizada precisar ser julgada. Mudança em arquivo de UI, HTML ou DOM, sozinha, não aciona navegador. Quando necessária, use navegador integrado (`@Browser` ou equivalente), depois MCP Server `chrome-devtools`; use Playwright somente se já existir no repo ou se for solicitado para fluxos repetíveis e assertions. Registre a rota, o estado, a viewport e a evidência. Reaproveite a prova na review enquanto os inputs permanecerem válidos.
5. **Decisões críticas (MVP):** Toda decisão da spec possui ação explícita e as tasks correspondentes citam seus IDs.

## 4. Fatiar por resultado

Agrupe o trabalho em fatias verticais verificáveis, com um resultado coeso por T*. Uma T* pode tocar vários arquivos e durar mais de uma sessão quando continua entregando o mesmo resultado.

Crie outra T* somente quando houver um resultado entregável separado, uma dependência real de execução, um risco que exija isolamento ou uma fatia que não possa ser verificada como unidade. Quantidade de arquivos ou critérios de aceite, duração estimada, pontuação e a conjunção "e" no título não justificam uma quebra por si sós.

### Regras das Tasks

1. **Ponto de entrada:** Quando o resultado criar ou alterar um ponto de entrada executável, inclua o smoke test desse ponto na mesma T*. Não crie T* apenas para repetir baseline ou smoke test genérico.
2. **Estrutura de cada T\*:** Título com verbo e resultado, `Spec: A*/C*`, aceite observável, verificação com comando executável do repo e dependências explícitas (`Deps`). Inclua `Arquivos` ou `Risco` somente quando ajudarem a implementar, isolar ou revisar a fatia.
3. **Decisões críticas:** Quando a task implementar ou substituir decisão crítica, adicionar `Decisões: <ID> (<ação>)`.
4. **Verificação:** Toda task exige comando executável relevante para seu aceite. Organize a cobertura por capacidade ou jornada (ex.: login, cadastro), reutilizando testes existentes quando comprovarem a alteração. Um comando por task não exige teste novo por task nem um teste por critério de aceite. Crie teste específico quando comportamento novo, regressão, caso de borda ou risco não estiver coberto. Verificação só manual ou leitura de arquivo não conta como prova suficiente. Planeje a prova depois da última edição de código/teste; repita somente após falha ou edição que invalide um input coberto. Smoke entra quando a entrada real mudar. Quando `Visual: necessária`, cubra no browser a tela, o estado e a viewport afetados e amplie quando o impacto exigir; quando `Visual: dispensada`, use a prova executável indicada sem abrir navegador.
5. **Dependências (`Deps`):** Declarar apenas predecessores reais de execução. Fatias independentes usam `Deps: nenhuma`; a linha de dependências define a fila, sem repetir a ordem em outra seção.
6. **Paralelização e checkpoints:** Indique no `plan.md` os IDs das T* que podem executar juntas e um motivo curto, somente quando dependências, ownership dos arquivos e ausência de conflito estiverem claros. No chat, mostre os grupos ao humano e diga que `vibe-implement` perguntará se ele quer executá-los em paralelo. Registre checkpoint de review apenas quando um risco ou contrato compartilhado precisar ser julgado antes de outra T*. O checkpoint de retomada é diferente: só aparece sob uma T* incompleta, com estado, próximo passo, paths da prova, snapshot Git e validade da prova; omita-o no plano inicial.
7. **UI Greenfield:** Entregue componentes e tokens dentro de fatias de resultado; não crie task de preparo visual sem entrega verificável.
8. **Banco de dados e migrations:** Mantenha migrations e schemas nas respectivas fatias verticais e inclua comandos executáveis de migration e seed mínimo. Migrations devem ser não destrutivas (padrão expand/contract).

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
- Resultados e dependências: <resumo curto da fila, sem repetir cada Deps>
- Prontidão das provas: <requisitos reais, onde estão disponíveis e ação para ausências>
- Paralelizáveis: <IDs + motivo curto ou “nenhum grupo seguro”; se houver grupo, diga que implement perguntará se o humano quer executá-lo junto>
- Checkpoint: <somente se aplicável>
- Chat: recomende novo chat para a próxima porta; continuar aqui é válido se o humano preferir.

Arquivo disponível em <created.path>/plan.md. Responda "aprovado" para confirmar, "pode ir pro analyze" no MVP, "pode ir pro implement" nas demais rotas (ou "pode ir para a próxima fase") para avançar imediatamente, ou indique os ajustes desejados.
```

## 6. Ajuste ou Aprovação

| Resposta | Ação |
|---|---|
| Aprovado (sem pedir próxima porta) | Alterar `# Status: aprovado` diretamente no vivo; parar e aguardar próximo comando |
| "Pode ir pro analyze" no MVP / "pode ir pro implement" nas demais rotas / pede a próxima porta | Alterar `# Status: aprovado` no vivo; iniciar a próxima porta aplicável |
| Pedido de alteração | Patch direto no arquivo vivo; até 5 bullets no chat; solicitar nova conferência |
| "Parece bom" sem pedir implementação | Perguntar: "Aprovado no arquivo ou deseja algum ajuste?" |
| Spec ou intenção quebrou | Devolver para `vibe-spec` ou `vibe-interview`. Não forçar implementação |

Rascunho sem "aprovado" e sem pedido da próxima porta não autoriza iniciar o código.

## 7. Fechar

Não commite no git nesta porta. O commit começa na `vibe-implement`, depois da prova verde de cada task. Não dispare a próxima skill a menos que o usuário tenha pedido explicitamente para avançar (§6).
No handoff, recomende novo chat para `vibe-analyze` no MVP ou `vibe-implement` nas demais rotas. Se o humano preferir continuar, siga sem bloquear; o `plan.md` vivo e o handoff são a ponte.
Handoff normal: `vibe-implement`. Handoff MVP: `vibe-analyze` (pois o modo max exige análise antes do código).
Não crie uma T* apenas para executar a review final. A fila do plan termina com as entregas implementáveis; a review final é a próxima skill do fluxo `vibe-implement` → `vibe-review`.
Zero código nesta execução.

