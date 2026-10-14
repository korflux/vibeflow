# vibe-plan, arquitetura

`/vibe-plan` fatia uma spec aprovada em tasks verificáveis e grava um único `plan.md`. Quando há UI, também exige o `design.md` aprovado no mesmo alvo. A IA define a ordem técnica e a prova; os motores inventariam o alvo e preparam o arquivo vivo.

```text
.vibeflow/phases/phase-<n>-<slug>/plan.md
.vibeflow/mvp/plan.md
```

## 1. Papéis e ownership

| Peça | Responsabilidade |
|---|---|
| `SKILL.md` | Validar a spec, preparo das provas, resultados, dependências, `Arquivos:` e provas em dois níveis por T*, ondas por disjunção e delegação do analyze na rota max. |
| `references/delegation.md` | Papéis por perfil, relatório fixo de subagente, escritor único e fallback. Cópia idêntica à de `vibe-implement`, comparada por bytes em `docs/tests/test-distribuicao.py`. |
| `scripts/plan.py`, `plan.ps1`, `plan.sh` | Inventário, seleção do alvo, gates mecânicos, preparação do vivo e JSON operacional no stdout. |
| `templates/plan.md` | Forma compacta de Overview, prontidão das provas com a `Regressão completa`, Tasks com `Arquivos:` e `Prova afetada:`, e handoff. |
| `stdout (JSON)` | Evidência operacional transitória, consumida na mesma execução. |
| `plan.md` | Fila executável e fonte da próxima T*. |

## 2. Dependências e seleção

Sem `.vibeflow/`, `INIT_AUSENTE`. O modo phase exige `spec.md` e reusa a maior phase com spec sem plan. `--dir` força uma phase existente. O plan não cria uma phase nova e não pisa um alvo com `analyze.md`.

Com UI visível, a IA valida o `design.md` do mesmo alvo. Se o design ainda não estiver aprovado, um pedido humano explícito para fazer o plan ou aprovar o design autoriza atualizar somente a linha `# Status` para `aprovado`, inclusive quando o pedido chega em chat novo. Sem esse pedido, o rascunho continua bloqueando o plan; sem `design.md`, o handoff segue para `vibe-design`. Os motores não inferem nem alteram essa aprovação.

No modo MVP, `--mvp` fixa `.vibeflow/mvp/`, exige `spec.md`, recusa `--dir` e encaminha para `vibe-analyze`. A flag representa uma decisão semântica da IA.

Flags públicas:

```text
python plan.py [--root PATH] [--apply] [--dir phase-N-slug] [--mvp]
pwsh plan.ps1 [-Root PATH] [-Apply] [-Dir phase-N-slug] [-Mvp]
bash plan.sh [--root PATH] [--apply] [--dir phase-N-slug] [--mvp]
```

## 3. Pré-requisitos e modalidade da prova

As provas têm dois níveis. `Prova afetada:` é declarada em toda T* e contém os comandos que provam somente o recorte: testes do módulo tocado e dos consumidores diretos, e E2E apenas do cenário da jornada cuja entrada mudou. Implementador e verificador executam somente ela, e a integração da phase usa a união das provas afetadas; comandos compartilhados ficam uma vez na prontidão das provas, referenciados pelas T* que cobrem. `Regressão completa` é uma única seção dentro de Prontidão das provas, com a suíte inteira e o E2E completo do repo, incluindo segurança, paridade entre motores e o CI obrigatório; somente a review final a executa. Não há válvula de ampliação por risco, consumidores ou lacuna nos papéis de implementação e verificação: o que excede o recorte pertence à regressão completa. Matriz por T* não é padrão. Não há schema ou artefato adicional para essa seleção.

A IA deriva as dependências dos comandos de `Prova afetada:` e da `Regressão completa` e confirma runtimes, package managers, serviços e capacidades nos arquivos do repo, workflows de CI e ferramentas disponíveis. `gitleaks` entra quando o repo ou CI exigir a varredura. O plan registra requisito, disponibilidade local ou no CI, e qualquer ausência no ambiente onde a prova vai rodar. Ausência local não exige setup quando a prova roda no CI e os requisitos estão atendidos lá. Dependência compartilhada ausente entra na T1; dependência exclusiva entra na primeira T* que a usa. Setup persistente do projeto só vira T* separada quando for um resultado da entrega. Ferramenta ausente segue a regra de instalação: instala-se pelo gerenciador do projeto ou por fonte oficial, quando o ambiente e as permissões permitirem, e a instalação é planejada na T* que depende dela. Instalação que exija credencial, conta, pagamento, elevação administrativa ou configuração persistente de integração (por exemplo, registrar um MCP) é impedimento real e vai ao humano. Bloqueio externo sem equivalente permanece explícito, e não se marca a prova como concluída.

Para cada T* que altera UI, o campo `Visual` declara `necessária` quando o aceite depende da UI renderizada, ou `dispensada` com motivo quando outra prova executável cobre o aceite e não há resultado visual a julgar. Tocar arquivos de UI, HTML ou DOM não aciona navegador por si só. Quando necessária, usa navegador integrado, depois MCP `chrome-devtools`; Playwright somente se já existir ou for solicitado para fluxo repetível/assertions. A evidência renderizada registra rota, estado e viewport e pode ser reutilizada na review enquanto os inputs estiverem válidos.

Tasks devem conter um resultado coeso, aceite observável, `Deps`, `Spec: A*/C*`, `Arquivos:` e `Prova afetada:`. `Arquivos:` lista os paths relativos ao repo que a T* pode escrever, testes incluídos, entre crases e separados por vírgula; diretório ou curinga vale como prefixo. A ausência de `Arquivos:` não bloqueia a fase, mas a T* roda sozinha no Modo A. `Risco` é opcional quando orienta isolamento ou review. Se a task criar ou alterar um ponto de entrada executável, o smoke entra na `Prova afetada:` dessa mesma task. A prova acontece depois da última edição de código/teste e só é repetida, no recorte afetado, após falha ou invalidação dos inputs cobertos.

## 4. JSON operacional no stdout

Os motores emitem stdout e stderr em UTF-8 sem BOM, inclusive em pipes e com caminhos ou mensagens acentuadas. Consumidores devem decodificar esses streams explicitamente como UTF-8.

O JSON transitório mantém `vibeflow`, `phases`, `next_n`, `existing`, `spec_pendente`, `rascunho`, `alvo`, `mvp`, `modo_sugerido`, `created`, `modo`, `actions` e `avisos`. Não existe estado de arquivo temporário no contrato.

`actions` registra criação de `phases/.gitkeep` ou do arquivo vivo. `files` lista os seis artefatos da cadeia.

## 5. Apply e escrita direta

1. Reexecuta o inventário.
2. Valida predecessor, `--dir`, status mecânico e ausência de `analyze.md`.
3. Prepara `plan.md` vazio quando ausente.
4. Preserva bytes do vivo existente.
5. Emite o JSON operacional no stdout para leitura imediata da IA.
6. A IA escreve ou atualiza diretamente `plan.md`, mantendo `# Status: rascunho` até aprovação. A promoção autorizada do design anterior altera somente seu cabeçalho e ocorre antes do fatiamento.

O script não escreve prosa, não escolhe a semântica da fila e não dispara implement. Ajuste ou aprovação posterior é patch no arquivo vivo.

## 6. Contrato do artefato

Plans novos declaram `# Protocolo: coordenacao-v1`. Coordenador escolhe modo pela capacidade/pedido e finalizador registra `# Modo: A|B` ao iniciar. No A, plan define trabalho e mantém resumo derivado; execution.json versionado ao lado mantém estado/snapshots/origem/commit pelo contrato de vibe-implement. Código e testes saem juntos; local válido libera dependentes, integração independente e commit real liberam conclusão. B usa ciclo individual sem sidecar. Etapas-v1 e plans sem marcador não migram e conservam registros existentes. Não inserir JSON, hashes, logs ou placeholders operacionais no plan novo.

Seções: Overview, prontidão das provas (com a `Regressão completa`), Tasks e Handoff. No Modo A, o motor da implement lê `Arquivos:` como texto e calcula as ondas por disjunção entre as T* elegíveis; a autoridade das ondas é o motor, e a seção Colaboração do plan apenas resume as previstas. Modo B e protocolos históricos não calculam ondas. Pré-requisitos verificados não são uma checklist opcional: ausências necessárias entram na T1 ou na primeira T* que depende delas, sem criar task de preparo isolada. T* com UI declara a necessidade de prova renderizada e seu motivo; tasks sem UI omitem o campo. `Colaboração` e checkpoint de review aparecem somente quando mudam a execução. Resumo de andamento/bloqueio é curto; snapshots ficam no sidecar no novo A e checkpoints históricos continuam somente nas runs antigas. `Deps` é a única declaração da fila. Cada task usa `T1`, `T2` em sequência, tem um resultado coeso, `Arquivos:` e `Prova afetada:`; Modo B/legado commita a task, e o novo Modo A commita as T* comprovadas em integração. A fila não contém T* só para review final; a implement faz handoff para `vibe-review` ao concluir. Não usar `todo.md`, `tasks.md`, `T001`, `[P]`, `[US1]`, `checklists/` ou verificação apenas manual.

## 7. Erros, testes e handoff

Falhas previstas usam `CODIGO: descrição`, incluindo `INIT_AUSENTE`, `PLAN_SEM_SPEC`, `PLAN_JA_ANALISADO`, `FASE_AUSENTE`, `MVP_INESPERADO` e `MODO_INVALIDO`.

Suítes: `docs/vibe-plan/tests/test-plan.py` e `docs/vibe-plan/tests/test-plan.sh`.

O handoff é `vibe-analyze` quando a rota é max (MVP ou phase max) e `vibe-implement` nas demais rotas. Recomende novo chat para iniciar plan após spec/design, sem bloquear a continuidade se o humano preferir. Para as T* paralelizáveis, o `plan.md` registra as ondas previstas e o motivo; no novo A o coordenador despacha cada onda calculada pelo motor, e no B o grupo continua sendo oferecido ao humano. O `plan.md` vivo carrega a fila verificável.

### Analyze delegado

Na rota max, quando o plan está aprovado e o humano pede a próxima porta, o chat do plan verifica se o host oferece subagentes. Com suporte, delega `vibe-analyze` a um subagente de perfil forte, que grava `analyze.md`, aplica as correções diretas previstas pela skill em spec, design e plan e devolve veredito, correções e perguntas, sem implementar nem commitar. O chat do plan confere o relatório contra o disco, faz as perguntas em aberto ao humano uma por vez, aplica as respostas nos artefatos, registra-as em Clarificações e marca o `analyze.md` aprovado quando o veredito é `limpo` e o humano aprova. Veredito `bloqueado` impede recomendar o implement. Sem subagentes, vale o comportamento anterior: chat novo para o analyze.

O fechamento recomenda com ênfase um chat novo com `/vibe-implement` e informa que ele rodará em Modo A. A recomendação nunca é gate.

## 8. Limites

- Plan não contém código nem abre fase por conta própria.
- O inventário não autoriza ler a árvore inteira. A IA localiza evidências com `rg --files` e `rg -n`.
- O JSON operacional é transitório no stdout; `plan.md` entra no Git.
- Plan não commita; o commit começa quando a implement fecha a integração verde no novo Modo A ou uma task verde no Modo B/legado. Não há disparo automático da próxima skill.
