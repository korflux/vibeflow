# vibe-plan, arquitetura

`/vibe-plan` fatia uma spec aprovada em tasks verificáveis e grava um único `plan.md`. Quando há UI, também exige o `design.md` aprovado no mesmo alvo. A IA define a ordem técnica e a prova; os motores inventariam o alvo e preparam o arquivo vivo.

```text
.vibeflow/phases/phase-<n>-<slug>/plan.md
.vibeflow/mvp/plan.md
```

## 1. Papéis e ownership

| Peça | Responsabilidade |
|---|---|
| `SKILL.md` | Validar a spec, preparo das provas, resultados, dependências, paralelismo seguro e delegação do analyze na rota max. |
| `references/delegation.md` | Papéis por perfil, relatório fixo de subagente, escritor único e fallback. Cópia idêntica à de `vibe-implement`, comparada por bytes em `docs/tests/test-distribuicao.py`. |
| `scripts/plan.py`, `plan.ps1`, `plan.sh` | Inventário, seleção do alvo, gates mecânicos, preparação do vivo e JSON operacional no stdout. |
| `templates/plan.md` | Forma compacta de Overview, prontidão das provas, Tasks e handoff. |
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

A IA deriva as dependências dos comandos de verificação por T* e confirma runtimes, package managers, serviços e capacidades nos arquivos do repo, workflows de CI e ferramentas disponíveis. `gitleaks` entra quando o repo ou CI exigir a varredura. O plan registra requisito, disponibilidade local ou no CI, e qualquer ausência no ambiente onde a prova vai rodar. Ausência local não exige setup quando a prova roda no CI e os requisitos estão atendidos lá. Dependência compartilhada ausente entra na T1; dependência exclusiva entra na primeira T* que a usa. Setup persistente do projeto só vira T* separada quando for um resultado da entrega. Ferramenta ausente segue a regra de instalação: instala-se pelo gerenciador do projeto ou por fonte oficial, quando o ambiente e as permissões permitirem, e a instalação é planejada na T* que depende dela. Instalação que exija credencial, conta, pagamento, elevação administrativa ou configuração persistente de integração (por exemplo, registrar um MCP) é impedimento real e vai ao humano. Bloqueio externo sem equivalente permanece explícito, e não se marca a prova como concluída.

Para cada T* que altera UI, o campo `Visual` declara `necessária` quando o aceite depende da UI renderizada, ou `dispensada` com motivo quando outra prova executável cobre o aceite e não há resultado visual a julgar. Tocar arquivos de UI, HTML ou DOM não aciona navegador por si só. Quando necessária, usa navegador integrado, depois MCP `chrome-devtools`; Playwright somente se já existir ou for solicitado para fluxo repetível/assertions. A evidência renderizada registra rota, estado e viewport e pode ser reutilizada na review enquanto os inputs estiverem válidos.

Tasks devem conter um resultado coeso, aceite observável, comando executável de verificação, `Deps` e `Spec: A*/C*`. `Arquivos` e `Risco` são opcionais quando orientam execução, isolamento ou review. Se a task criar ou alterar um ponto de entrada executável, a prova de smoke entra nessa mesma task. A prova final acontece depois da última edição de código/teste e só é repetida após falha ou invalidação dos inputs cobertos.

## 4. JSON operacional no stdout

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

Plans novos declaram `# Protocolo: etapas-v1`. O coordenador da implement registra `# Modo: A|B` ao iniciar, sem inferir modo pelo número de tasks. Não acrescente o marcador a artefatos históricos. No Modo A, `Execução` por T* e `Integração` antes das Tasks armazenam estados e snapshots definidos em `docs/vibe-implement/ARQUITETURA.md`; a task implementada pode liberar código dependente, mas `[x]` exige prova integrada verde. Comandos que cobrem várias tasks podem compartilhar uma prova final. O commit integrado identifica todos os IDs comprovados; Modo B conserva commit por task. Campos operacionais só entram durante execução, não como placeholders JSON inválidos no plano aprovado.

Seções: Overview, prontidão das provas, Tasks e Handoff. Pré-requisitos verificados não são uma checklist opcional: ausências necessárias entram na T1 ou na primeira T* que depende delas, sem criar task de preparo isolada. T* com UI declara a necessidade de prova renderizada e seu motivo; tasks sem UI omitem o campo. `Paralelização` e checkpoint de review aparecem somente quando mudam a execução. Checkpoint de retomada aparece apenas sob T* incompleta durante implementação, registra o snapshot Git dos inputs da prova e é removido ao concluir a task. `Deps` é a única declaração da fila. Cada task usa `T1`, `T2` em sequência, tem um resultado coeso e prova planejada; Modo B/legado commita a task, e o novo Modo A commita as T* comprovadas em integração. A fila não contém T* só para review final; a implement faz handoff para `vibe-review` ao concluir. Não usar `todo.md`, `tasks.md`, `T001`, `[P]`, `[US1]`, `checklists/` ou verificação apenas manual.

## 7. Erros, testes e handoff

Falhas previstas usam `CODIGO: descrição`, incluindo `INIT_AUSENTE`, `PLAN_SEM_SPEC`, `PLAN_JA_ANALISADO`, `FASE_AUSENTE`, `MVP_INESPERADO` e `MODO_INVALIDO`.

Suítes: `docs/vibe-plan/tests/test-plan.py` e `docs/vibe-plan/tests/test-plan.sh`.

O handoff é `vibe-analyze` quando a rota é max (MVP ou phase max) e `vibe-implement` nas demais rotas. Recomende novo chat para iniciar plan após spec/design, sem bloquear a continuidade se o humano preferir. Para grupos paralelizáveis, o `plan.md` nomeia as T*s e registra o motivo, e o grupo só vale no Modo B do implement; o `plan.md` vivo carrega a fila verificável.

### Analyze delegado

Na rota max, quando o plan está aprovado e o humano pede a próxima porta, o chat do plan verifica se o host oferece subagentes. Com suporte, delega `vibe-analyze` a um subagente de perfil forte, que grava `analyze.md`, aplica as correções diretas previstas pela skill em spec, design e plan e devolve veredito, correções e perguntas, sem implementar nem commitar. O chat do plan confere o relatório contra o disco, faz as perguntas em aberto ao humano uma por vez, aplica as respostas nos artefatos, registra-as em Clarificações e marca o `analyze.md` aprovado quando o veredito é `limpo` e o humano aprova. Veredito `bloqueado` impede recomendar o implement. Sem subagentes, vale o comportamento anterior: chat novo para o analyze.

O fechamento recomenda com ênfase um chat novo com `/vibe-implement` e informa que ele rodará em Modo A. A recomendação nunca é gate.

## 8. Limites

- Plan não contém código nem abre fase por conta própria.
- O inventário não autoriza ler a árvore inteira. A IA localiza evidências com `rg --files` e `rg -n`.
- O JSON operacional é transitório no stdout; `plan.md` entra no Git.
- Plan não commita; o commit começa quando a implement fecha a integração verde no novo Modo A ou uma task verde no Modo B/legado. Não há disparo automático da próxima skill.
