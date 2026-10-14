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

Declare em cerca de cinco linhas: rota, modo, alvo, status da spec, presença/status do design quando houver UI e estado do artefato vivo.
Ao iniciar após `vibe-spec` ou `vibe-design`, recomende um chat novo. Se o humano preferir continuar no chat atual, prossiga sem bloquear.

```text
modo: reuse · alvo: phase-1-lock-bloco · spec-status: aprovado · design-status: aprovado · artefato vivo: presente · chat: novo recomendado
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
| Com UI visível e `design.md` aprovado na mesma pasta | Seguir |
| Com UI visível, `design.md` existente ainda sem status aprovado e pedido explícito para fazer o plan ou aprovar o design | Alterar somente `# Status` do design para `aprovado` e seguir. O pedido direto de plan vale como aprovação explícita, inclusive em chat novo |
| Com UI visível sem `design.md` aprovado e sem pedido explícito de plan/aprovação | Parar. Sem arquivo, encaminhar para `vibe-design`; com rascunho, pedir leitura e aprovação |
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
2. **Dependências das provas:** Derive a lista dos comandos de `Prova afetada:` das T* e da `Regressão completa`. Confira runtime e package manager (por exemplo, Node), serviços, comandos (incluindo `gitleaks` quando CI ou repo o exigirem) e capacidades externas necessárias. Use manifests, scripts, workflows de CI e ferramentas disponíveis como evidência; registre no plan onde cada requisito está disponível, localmente ou no CI. Considere-o atendido quando estiver disponível no ambiente onde a `Prova afetada:` ou a `Regressão completa` vai rodar.
3. **Ausências:** Não deixe requisito necessário em checklist opcional. Ausência local não exige setup quando a prova será executada no CI e os requisitos estão atendidos lá. Se um requisito compartilhado faltar no ambiente planejado para a prova, inclua sua resolução na T1; se só for usado depois, inclua a resolução na primeira T* que depende dele. Não crie T* separada de preparo, a menos que o setup persistente seja um resultado do projeto. Regra de instalação: instale a ferramenta ausente necessária à prova pelo gerenciador do projeto ou por fonte oficial, quando o ambiente e as permissões permitirem, e planeje a instalação sob a T* que depende dela. Instalação que exija credencial, criação de conta, pagamento, elevação administrativa ou configuração persistente de integração (por exemplo, registrar um MCP) é impedimento real e vai ao humano. Capacidade que a regra não permite instalar e sem equivalente vira bloqueio registrado na fila; não marque a prova como concluída.
4. **Prova visual por task:** Para cada task que altera UI, registre `Visual: necessária` quando o aceite depender de aparência, layout, responsividade, estado ou interação renderizados no navegador. Registre `Visual: dispensada` com o motivo quando comandos ou testes existentes provarem o aceite e nenhuma saída renderizada precisar ser julgada. Mudança em arquivo de UI, HTML ou DOM, sozinha, não aciona navegador. Quando necessária, use navegador integrado (`@Browser` ou equivalente), depois MCP Server `chrome-devtools`; use Playwright somente se já existir no repo ou se for solicitado para fluxos repetíveis e assertions. Registre a rota, o estado, a viewport e a evidência. Reaproveite a prova na review enquanto os inputs permanecerem válidos.
5. **Decisões críticas (MVP):** Toda decisão da spec possui ação explícita e as tasks correspondentes citam seus IDs.

## 4. Fatiar por resultado

Agrupe o trabalho em fatias verticais verificáveis, com um resultado coeso por T*. Uma T* pode tocar vários arquivos e durar mais de uma sessão quando continua entregando o mesmo resultado.

Crie outra T* somente quando houver um resultado entregável separado, uma dependência real de execução, um risco que exija isolamento ou uma fatia que não possa ser verificada como unidade. Quantidade de arquivos ou critérios de aceite, duração estimada, pontuação e a conjunção "e" no título não justificam uma quebra por si sós.

### Regras das Tasks

1. **Ponto de entrada:** Quando o resultado criar ou alterar um ponto de entrada executável, inclua o smoke test desse ponto na mesma T*. Não crie T* apenas para repetir baseline ou smoke test genérico.
2. **Estrutura de cada T\*:** Título com verbo e resultado, `Spec: A*/C*`, aceite observável, dependências explícitas (`Deps`), `Arquivos:` e `Prova afetada:`. `Arquivos:` lista os paths relativos ao repo que a T* pode escrever, testes incluídos, entre crases e separados por vírgula; diretório ou curinga vale como prefixo. Declare o recorte mais estreito que a T* realmente escreve, porque prefixo largo serializa T* que poderiam rodar em paralelo. A ausência de `Arquivos:` não bloqueia a fase, mas a T* roda sozinha. Inclua `Risco` somente quando ajudar a isolar ou revisar a fatia.
3. **Decisões críticas:** Quando a task implementar ou substituir decisão crítica, adicionar `Decisões: <ID> (<ação>)`.
4. **Provas em dois níveis:**
   - `Prova afetada:` em cada T*: comandos executáveis do repo que provam somente o recorte, isto é, testes do módulo tocado e dos consumidores diretos, e E2E apenas do cenário da jornada cuja entrada mudou. Implementador e verificador executam somente ela; a integração da phase usa a união das provas afetadas. Smoke de entrada executável criada ou alterada entra nessa prova, e a prova renderizada exigida em `Visual` a compõe. Comando compartilhado entre T* é definido uma vez na prontidão das provas e referenciado.
   - `Regressão completa`: uma única seção `### Regressão completa` dentro de Prontidão das provas, com os comandos da suíte inteira e do E2E completo do repo, incluindo segurança, paridade entre motores e o CI obrigatório. Somente a review final a executa; nenhuma T* a repete.
   - Não planeje matriz por task nem teste novo por critério; complemente somente lacunas de comportamento, erro ou risco. Prove depois da última edição; falha ou mudança de input renova somente a prova afetada pelo que mudou. Verificação só manual não basta.
5. **Dependências (`Deps`):** Declarar apenas predecessores reais de execução. Fatias independentes usam `Deps: nenhuma`; a linha de dependências define a fila, sem repetir a ordem em outra seção.
6. **Colaboração e ondas:** No Modo A, o motor da implement calcula as ondas pela disjunção de `Arquivos:` entre as T* elegíveis e o coordenador despacha cada onda em paralelo; T* sem `Arquivos:` ou sobreposta a outra roda sozinha. Registre em Colaboração as ondas previstas (derivadas, o motor recalcula), o benefício e o ownership de recurso compartilhado fora de `Arquivos:`, somente quando trouxerem benefício concreto. O coordenador escolhe interlocutores e colaboração sem intermediar cada detalhe. B mantém oferta de grupo ao humano antes de paralelizar; etapas-v1/legado conservam sequência. Checkpoint de review só aparece quando risco/contrato exige julgamento antes de outra task. Plan novo mantém resumo curto; snapshots, hashes e logs pertencem a execution.json no A, sem checkpoint operacional extenso em Markdown.
7. **UI Greenfield:** Entregue componentes e tokens dentro de fatias de resultado; não crie task de preparo visual sem entrega verificável.
8. **Banco de dados e migrations:** Mantenha migrations e schemas nas respectivas fatias verticais e inclua comandos executáveis de migration e seed mínimo. Migrations devem ser não destrutivas (padrão expand/contract).

IDs estáveis: `T1`, `T2`, `T3`... em ordem sequencial. Sem prefixos arbitrários como `T001`, `[P]` ou `[US1]`.

## 5. Escrever e Salvar

Em plans novos registre `# Protocolo: coordenacao-v1`; não migre artefatos históricos. Coordenador escolhe modo e finalizador registra `# Modo: A|B` ao iniciar. No novo A, implementação entrega código/testes juntos com a prova afetada; verificador certifica integração e finalizador registra execution.json e commit. Plan mantém somente definição de trabalho e resumo curto derivado; execução estruturada é autoridade operacional. Modo B conserva prova/commit por task sem sidecar. Não inclua snapshots, hashes, logs, histórico de comandos nem placeholders operacionais no plan aprovado.

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
- Paralelizáveis: <ondas previstas por disjunção de `Arquivos:` e `Deps`, T* que rodam sozinhas e o motivo curto; no B, o grupo oferecido ao humano; “nenhum grupo seguro” quando não houver>
- Checkpoint: <somente se aplicável>
- Chat: na rota max, o analyze roda em subagente a partir deste chat quando o humano pedir a próxima porta; nas demais rotas, recomende novo chat para o implement. Continuar aqui é válido se o humano preferir.

Arquivo disponível em <created.path>/plan.md. Responda "aprovado" para confirmar, "pode ir pro analyze" quando a rota é max (MVP ou phase), "pode ir pro implement" nas demais rotas (ou "pode ir para a próxima fase") para avançar imediatamente, ou indique os ajustes desejados.
```

## 6. Ajuste ou Aprovação

| Resposta | Ação |
|---|---|
| Aprovado (sem pedir próxima porta) | Alterar `# Status: aprovado` diretamente no vivo; parar e aguardar próximo comando |
| "Pode ir pro analyze" na rota max (MVP ou phase) / "pode ir pro implement" nas demais rotas / pede a próxima porta | Alterar `# Status: aprovado` no vivo; na rota max, delegar o analyze (§7); nas demais, iniciar a próxima porta aplicável |
| Pedido de alteração | Patch direto no arquivo vivo; até 5 bullets no chat; solicitar nova conferência |
| "Parece bom" sem pedir implementação | Perguntar: "Aprovado no arquivo ou deseja algum ajuste?" |
| Spec ou intenção quebrou | Devolver para `vibe-spec` ou `vibe-interview`. Não forçar implementação |

Rascunho sem "aprovado" e sem pedido da próxima porta não autoriza iniciar o código.

## 7. Analyze delegado (rota max)

Vale quando a rota exige analyze (MVP ou phase max), o plan está aprovado e o humano pediu a próxima porta. Leia `references/delegation.md` antes de delegar.

1. Verifique se o host oferece subagentes. Sem suporte, mantenha o comportamento anterior: recomende um chat novo para `vibe-analyze` (§8) e pare.
2. Com suporte, delegue `vibe-analyze` a um subagente do perfil `revisor`, com o alvo (a phase ou `--mvp`) e as proibições de `references/delegation.md`. O subagente grava `analyze.md`, aplica as correções diretas que a skill de analyze prevê em spec, design e plan, não implementa código nem cria commit, e devolve o veredito, as correções aplicadas e as perguntas em aberto no relatório fixo.
3. Confira o relatório contra o `analyze.md` gravado e contra `git status` e o diff de `spec.md`, `design.md` e `plan.md`; releia o `plan.md`, que o subagente pode ter corrigido. Divergência volta ao subagente com o problema descrito.
4. Faça ao humano as perguntas em aberto, uma por vez, com recomendação. Aplique cada resposta nos artefatos e registre-a em Clarificações no `analyze.md`; enquanto houver achado bloqueante pendente, o veredito é `bloqueado`, e você o atualiza para `limpo` quando o último for resolvido.
5. Veredito `bloqueado` impede recomendar o implement: mostre os achados bloqueantes e devolva à skill dona. Com `limpo`, peça a aprovação do `analyze.md` neste chat; com ela, marque `# Status: aprovado` e a aprovação humana no vivo, como a skill de analyze define. Erros do motor de analyze não são contornados.

## 8. Fechar

Não commite no git nesta porta. O commit começa na `vibe-implement`, depois da prova integrada verde no novo Modo A ou da prova verde por task no Modo B/legado. Não dispare a próxima skill a menos que o usuário tenha pedido explicitamente para avançar (§6).
Handoff: `vibe-analyze` quando a rota é max (MVP ou phase max, que exige análise antes do código) e `vibe-implement` nas demais rotas.
Com o analyze delegado aprovado (§7), recomende com ênfase um chat novo com `/vibe-implement` e informe que ele rodará em Modo A: num host com subagentes, conduz a fila inteira da phase e só volta ao humano na pergunta final. Sem subagentes, recomende chat novo para o `vibe-analyze` e, depois dele, para o `vibe-implement` (Modo B, uma T* por run). Nas rotas sem analyze, recomende chat novo para `vibe-implement` com o mesmo anúncio do Modo A. A recomendação nunca é gate: se o humano preferir continuar neste chat, siga sem bloquear; os `plan.md` e `analyze.md` vivos e o handoff são a ponte.
Não crie uma T* apenas para executar a review final. A fila do plan termina com as entregas implementáveis; a review final é a próxima skill do fluxo `vibe-implement` → `vibe-review`.
Zero código nesta execução.
