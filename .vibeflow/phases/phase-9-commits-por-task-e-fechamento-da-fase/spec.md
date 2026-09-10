# Spec: commits por task e fechamento da fase
# Alvo: phase-9-commits-por-task-e-fechamento-da-fase
# Status: aprovado

## Objetivo

Remover o conceito operacional de checkpoint do Vibeflow, porque a unidade real de execução, prova e entrega é a task `T*`. Ao concluir cada task com teste verde, `vibe-implement` deve criar um commit isolado, sem fazer push. Depois que a review for aprovada e todas as correções forem comprovadas, o handoff final deve validar a fase, criar o commit residual da fase quando houver mudanças e fazer push do branch atual sem force.

## Inventário

1. Contrato de fatiamento: `vibe-plan/SKILL.md`, `vibe-plan/templates/plan.md` e `docs/vibe-plan/`.
2. Execução por task: `vibe-implement/SKILL.md`, `vibe-implement/templates/implement.md`, `docs/vibe-implement/` e o parser de `plan.md`.
3. Review e fechamento: `vibe-review/SKILL.md`, `vibe-review/templates/review.md`, `docs/vibe-review/`, `README.md`, `docs/ESCOPO.md` e `.vibeflow/REGRAS.md`.
4. Testes de contrato: `docs/vibe-implement/tests/`, `docs/vibe-plan/tests/`, `docs/vibe-review/tests/`, `docs/tests/test-distribuicao.py` e `docs/tests/test-reparse-safety.py` quando aplicável.

## Suposições e decisões

1. `T*` é a unidade única de execução. Não haverá agrupamento, pausa ou suíte especial chamada checkpoint; cada task usa sua própria verificação e o fechamento da fase usa a suíte completa.
2. O commit da task acontece somente depois de teste verde, simplificação, re-teste e atualização dos artefatos vivos. O commit é path-scoped, não usa `git add -A`, não faz push e não recebe `Co-Authored-By`.
3. Correções abertas pela review continuam sendo tasks ou correções `R*` e também geram commits isolados. A review não aprova enquanto houver Critical ou Required aberto.
4. O fechamento final exige aprovação humana registrada no `review.md`, ausência de bloqueios, suíte final verde, diff sem erro e varredura de segredo quando prevista. Só então o handoff cria o commit final residual e executa `git push` do upstream atual, sem force.
5. Mudança pré-existente em path que a task precisa alterar impede o commit automático desse path. O agente deve preservar o trabalho existente e pedir isolamento ou decisão humana, nunca misturar alterações por conveniência.
6. Um `--slug` explícito representa pedido novo e deve abrir a próxima phase mesmo quando existir um rascunho antigo sem `plan.md`; interview pendente continua tendo precedência.

## Escopo e comportamento

### 1. Remoção de checkpoint

- Remover `checkpoint` e `check point` das instruções, templates e documentação operacional canônica.
- Manter o parser de `vibe-implement` restrito a headings `T*`, linha de conclusão e `Deps`; prosa de grupo não altera `fila.elegiveis` nem `fila.bloqueadas`.
- O modo A executa uma task elegível e para; o modo B percorre a fila quando o humano pedir execução contínua. A fronteira é sempre a task, nunca um grupo.

### 2. Commit da task

- Após a prova verde, atualizar `plan.md`, `implement.md` e somente os artefatos autorizados pela task.
- Conferir o estado inicial e final do Git, rejeitar path pré-existente alterado por outro trabalho, adicionar somente paths da task, executar `git diff --cached --check` e criar um commit com mensagem contendo o ID da task.
- Relatórios operacionais permanecem fora do commit. Falha de staging, commit, teste ou escopo interrompe a task sem marcar conclusão falsa.
- O resultado operacional e o chat informam a mensagem e o hash do commit da task; o `implement.md` registra a execução e deixa explícito que o push ocorrerá apenas no fechamento da fase. Não reabrir o artefato vivo só para anexar o hash depois do commit.

### 3. Fechamento final da fase

- `vibe-review` grava o veredito primeiro. Request changes retorna para `vibe-implement`; Approve só avança após confirmação humana.
- No fechamento, validar todas as `T*` concluídas, todos os `R*` bloqueantes fechados, suíte final, `git diff --check`, gitleaks quando disponível e ausência de alterações fora do escopo.
- Adicionar somente os artefatos residuais da fase e decisões vigentes aprovadas, criar a mensagem final da phase e executar `git push` para o upstream do branch atual, sem `--force`.
- Sem mudanças residuais, não criar commit vazio; considerar o último commit da task como HEAD da fase e ainda executar o push final. Falha de upstream ou push deixa o handoff bloqueado e não declara a fase concluída.

### Fora

- Criar uma skill nova somente para Git, alterar o schema dos relatórios, criar branch/worktree automaticamente, fazer amend/squash, usar force push ou enviar cada commit de task ao remoto.

## Checklist de entrega

### Aceite

- [ ] A1: o contrato operacional canônico não usa mais checkpoint; cada task é a unidade de execução, prova e parada.
- [ ] A2: a fila do parser permanece inalterada por prosa de agrupamento, com teste que comprova a ausência de dependência sem preservar o conceito removido.
- [ ] A3: `vibe-implement` define e registra commit path-scoped após cada task verde, sem push por task, sem `git add -A` e sem `Co-Authored-By`.
- [ ] A4: `vibe-review` define o handoff final como commit residual e push somente após Approve, confirmação humana e correções fechadas.
- [ ] A5: os testes de contrato, `git diff --check`, gitleaks e busca canônica passam sem incluir relatórios ou alterações pré-existentes nos commits da entrega.
- [ ] A6: os motores Python e PowerShell de `vibe-spec` respeitam slug explícito como pedido novo sem sobrescrever rascunho antigo.

### Critérios de sucesso

- [ ] C1: não existem referências operacionais a checkpoint nos pacotes, templates, docs canônicos, README ou escopo atual.
- [ ] C2: uma task concluída tem um commit identificável e nenhum push é executado antes do fechamento da fase.
- [ ] C3: uma review com R* aberto não finaliza; uma review aprovada sem bloqueios executa somente o commit/push final da fase.
- [ ] C4: paths já alterados antes da task ficam fora do staging ou bloqueiam a operação com mensagem clara, sem mistura silenciosa.
- [ ] C5: uma phase nova com slug explícito não reutiliza phase antiga pendente e os motores continuam em paridade.

## Implementação

### Stack

| Área | Escolha |
|---|---|
| Execução Git | comandos Git nativos orientados pela `SKILL.md`, sem nova dependência |
| Contrato de disco | artefatos vivos existentes, sem novo arquivo de estado |
| Testes | `unittest`, scripts de contrato e varreduras já usadas pelo CI |
| Dependências novas | Nenhuma |

### Estrutura tocada

```text
vibe-plan/SKILL.md, vibe-plan/templates/plan.md                 # remove agrupamento por checkpoint
vibe-implement/SKILL.md, vibe-implement/templates/implement.md # commit isolado por task
vibe-review/SKILL.md, vibe-review/templates/review.md         # fechamento final commit/push
vibe-spec/scripts/spec.py, vibe-spec/scripts/spec.ps1          # pedido novo com slug explícito
docs/vibe-{plan,implement,review}/                             # arquitetura, análise e testes
README.md, docs/ESCOPO.md, .vibeflow/REGRAS.md                 # contrato transversal
```

### Estilo e padrões

- Uma casa por fato: parser mecânico nos scripts, operação do agente nas skills, forma no template e justificativa nas análises.
- Usar staging explícito por path, verificar o diff indexado antes do commit e nunca mascarar trabalho pré-existente.
- Preservar a separação entre commit por task e push final da phase.

### Contratos e módulos

- `vibe-plan` define tasks sem agrupamentos especiais.
- `vibe-implement` é dono do commit após a task verde.
- `vibe-review` é dono do gate final e do push após aprovação humana; não corrige código.
- Scripts de inventário não executam comandos Git nem publicam decisões semânticas.

## Como provar

### Seams

- Comparar a fila produzida com e sem prosa de grupo e confirmar a mesma saída.
- Conferir que a sequência de comandos de commit usa paths explícitos e que a sequência final só aparece após aprovação e sem R* bloqueante.
- Exercitar a seleção de slug com um rascunho antigo em Python e PowerShell.

### Estratégia

- Unitário/contrato: buscas canônicas, testes de templates e parser, testes de seleção dos dois motores.
- Integração: suítes completas das sete skills, launchers, fluxo MVP, reparse e distribuição.
- Git: `git diff --check`, gitleaks e revisão estática dos comandos, sem alterar o histórico atual desta sessão.

### Comandos

```bash
python docs/vibe-spec/tests/test-spec.py -v
python docs/vibe-plan/tests/test-plan.py -v
python docs/vibe-implement/tests/test-implement.py -v
python docs/vibe-review/tests/test-review.py -v
python docs/tests/test-distribuicao.py -v
git diff --check
gitleaks detect --source . --verbose --redact --no-banner
```

## Boundaries

### Always

- Validar o fluxo real e os paths antes de commitar.
- Criar exatamente um commit por task concluída e um fechamento final por phase quando houver mudanças residuais.
- Registrar hash/mensagem do commit no resultado operacional sem gravar segredos.
- Usar push normal para o upstream atual somente depois da aprovação humana.

### Ask first

- Path já alterado antes da task, ausência de upstream, divergência de branch ou qualquer necessidade de force push.
- Mudança que exigiria incluir arquivo fora da phase ou das decisões aprovadas.

### Never

- Reintroduzir checkpoint como gate, agrupamento ou razão para repetir uma suíte.
- Fazer `git add -A`, commitar relatório, misturar alterações pré-existentes, incluir `Co-Authored-By`, usar amend/squash ou fazer force push.

## Handoff

vibe-plan

- [x] Aprovação humana, o pedido explicitamente autoriza seguir para plan e implementação.
