# Spec: interoperabilidade, escrita direta e isolamento de etapas
# Alvo: phase-8-interoperabilidade-skills
# Status: aprovado

## Objetivo

Alinhar o Vibeflow aos contratos atuais de descoberta do Codex, Antigravity e hosts compatíveis, corrigir a distribuição das skills e reduzir a persistência de contexto que favorece erros repetidos entre etapas. A entrega deve manter `.vibeflow/REGRAS.md` como única fonte de regras, tornar as pontes de regras explícitas por host, substituir o ciclo `wip → apply` por escrita direta no artefato vivo, orientar investigação por relevância, registrar recomendações claras de troca de chat e estabelecer uma prova visual enxuta para mudanças de interface.

## Inventário

1. Codex documenta composição entre instruções globais em `~/.codex` e arquivos de projeto em camadas, enquanto Antigravity documenta regras em `~/.gemini/GEMINI.md` e `.agents/rules/`, sem tratar `AGENTS.md` como contrato principal.
2. O pacote raiz possui `plugin.json` com campos além do schema mínimo documentado pelo Antigravity e depende de `skills/` com ponteiros para os pacotes canônicos.
3. As sete skills, seus dois motores e os testes ainda criam ou exigem `*-wip.md`, embora o artefato vivo já seja editado diretamente em ajustes posteriores.
4. A investigação está parcialmente orientada, mas ainda contém instruções genéricas como “inspecione o repositório” e inventários que podem ser interpretados como leitura integral da árvore.
5. Handoffs informam a próxima skill, mas não registram uma política explícita de isolamento de chat por etapa ou por T*.
6. `vibe-implement/references/chrome-devtools.md` e `vibe-review/references/ui-visual-quality.md` já são pontos de validação visual, mas ainda não distinguem navegador integrado, MCP Chrome DevTools e Playwright, nem formam uma checklist única de problemas de geometria, proporção, controles e estados.
7. Os hosts não usam um formato universal de regras: alguns descobrem `AGENTS.md`, outros `CLAUDE.md`, `GEMINI.md` ou `.agents/rules/`. Mesmo com symlinks, um host que carrega mais de um nome pode duplicar contexto, o que precisa ser verificado por inspeção do próprio host.

## Suposições e decisões

1. `.vibeflow/REGRAS.md` continua sendo a fonte única; `AGENTS.md`, `CLAUDE.md` e o arquivo de regra do Antigravity são ponteiros ou inclusões, nunca cópias. (governança)
2. O init criará `.agents/rules/vibeflow.md` com a inclusão relativa `@../../.vibeflow/REGRAS.md`. Regras globais do usuário continuam sob responsabilidade do usuário: Codex usa `~/.codex/AGENTS.md` ou `AGENTS.override.md`; Antigravity usa `~/.gemini/GEMINI.md`. (interoperabilidade)
3. `--apply` permanece como flag pública, mas passa a preparar ou validar o destino vivo depois dos gates. Ele não lê, copia, calcula hash, promove nem remove `*-wip.md`. (contrato)
4. A IA escreve e atualiza `interview.md`, `spec.md`, `plan.md`, `analyze.md`, `implement.md` e `review.md` diretamente, mantendo `# Status: rascunho` enquanto o documento estiver em elaboração. (processo)
5. A investigação deve começar pelas perguntas da tarefa, localizar evidências com `rg`/`rg --files` e seguir somente o fluxo real necessário. Listagens do script são mapa operacional, não ordem para abrir todos os arquivos. (qualidade)
6. A troca de chat é uma recomendação de isolamento, não um gate mecânico. `init → interview → spec` pode permanecer no mesmo chat; `plan`, `analyze`, `implement` e `review` devem recomendar novo chat, com um chat focado por T* de implementação. (processo)
7. A distribuição documentará caminhos distintos para Antigravity IDE, Antigravity CLI e o instalador `npx skills`; o pacote não escreverá em diretórios globais do usuário durante `vibe-init`. (segurança)
8. A fonte canônica continua sendo `.vibeflow/REGRAS.md`; cada host recebe somente o adaptador mínimo que ele descobre. Não criar `GEMINI.md` no repositório apenas para duplicar conteúdo. Hosts que carregam a família `AGENTS` e `CLAUDE` simultaneamente devem ser verificados com a ferramenta de inspeção disponível, como `grok inspect`. (HOST-01)
9. Ações universalmente reconhecíveis podem usar ícone no lugar de texto para reduzir ruído e ocupar menos espaço, por exemplo apagar com ícone de lixeira. A ação icon-only deve manter nome acessível, foco visível e tooltip quando necessário; ações ambíguas ou que exigem explicação continuam com texto. (UI-01)
10. Toda mudança de interface exige prova no estado renderizado. Deve-se preferir o navegador integrado quando o host oferecer esse recurso; o MCP Chrome DevTools serve para inspeção de DOM, estilos, console e rede; Playwright serve para interações determinísticas, viewports e assertions quando já existir no repositório ou quando for explicitamente solicitado. Nenhuma ferramenta nova de navegador é instalada nesta phase. (QA-01)

## Escopo e comportamento

### 1. Governança e descoberta de regras

- `vibe-init` cria e repara o ponteiro `.agents/rules/vibeflow.md` sem duplicar o conteúdo de `REGRAS.md`.
- O relatório do init informa o estado desse ponteiro e qualquer conflito relevante.
- A documentação explica a precedência e os caminhos documentados do Codex e do Antigravity, distinguindo regra global de regra de workspace.
- A fonte viva continua versionável; ponteiros e inclusões não viram uma segunda fonte de verdade.

### 2. Distribuição Antigravity

- O `plugin.json` raiz segue o schema mínimo documentado pelo Antigravity e mantém `skills/` como diretório de skills do pacote.
- O README fornece comandos separados para instalação project-local e global, recomenda `--copy` no Windows sem symlink e inclui a verificação correspondente (`/skills`, `agy plugin list` ou reinício do host).
- O teste de distribuição valida o manifest, a presença dos sete pacotes e a ponte de regras do workspace.

### 3. Artefatos vivos, sem WIP

- Os scripts Python e PowerShell deixam de criar, exigir e remover `interview-wip.md`, `spec-wip.md`, `plan-wip.md`, `analyze-wip.md`, `implement-wip.md` e `review-wip.md`.
- O apply prepara o diretório e o arquivo vivo somente quando os gates mecânicos permitem, preservando bytes existentes quando o arquivo já existe.
- Os relatórios mantêm a seleção de alvo, as ações e os erros úteis, mas não expõem estado `wip`; as mensagens `WIP_AUSENTE` e `COPY_HASH_MISMATCH` deixam de fazer parte do contrato.
- `.vibeflow/.gitignore` deixa de incluir WIP e os artefatos gerados existentes desse tipo são removidos desta entrega.
- A escrita semântica permanece da IA, usando o editor disponível, com `Status: rascunho` até aprovação humana.

### 4. Investigação dirigida

- Todas as skills substituem instruções genéricas de leitura integral por uma sequência: formular perguntas, localizar arquivos por nome/conteúdo, abrir entradas e dependências do fluxo, expandir apenas quando uma lacuna bloquear a prova.
- `vibe-init` mantém uma leitura estrutural limitada para mapear o projeto, mas proíbe transformar a listagem em dump ou em ordem para ler tudo.
- Implementação e review continuam exigindo evidência suficiente, porém por caminhos e símbolos relevantes à task, não por varredura cega.

### 5. Isolamento de chat

- Cada skill informa no fechamento a recomendação de chat para a próxima porta.
- `plan`, `analyze`, `implement` e `review` exibem recomendação explícita de novo chat; implement informa “um chat por T*” quando houver fila.
- O arquivo vivo e o caminho do handoff continuam sendo a ponte entre chats; nenhum contexto de chat é tratado como fonte de verdade.
- A recomendação não impede continuidade no mesmo chat quando o humano escolher conscientemente essa opção.

### 6. Controles compactos e semânticos

- Preferir ícone para ações universalmente reconhecíveis quando isso reduzir largura ou ruído visual, como lixeira para apagar, sem remover a semântica da ação.
- Todo controle icon-only deve ter nome acessível programático, área de interação adequada, foco visível e tooltip quando o significado não for imediatamente evidente.
- Manter texto em ações ambíguas, compostas, destrutivas sem contexto suficiente ou que dependam de uma explicação para evitar erro de uso.
- Não usar ícone como justificativa para esconder confirmação, feedback, estado de carregamento, erro ou permissão da ação.

### 7. Validação visual dirigida

- As referências existentes `vibe-implement/references/chrome-devtools.md` e `vibe-review/references/ui-visual-quality.md` formam o guia operacional, sem criar um documento paralelo.
- A checklist mínima deve verificar: overflow horizontal ou vertical inesperado, clipping, conteúdo fora da viewport, elementos sobrepostos ou cobertos, z-index de modal/sticky, truncamento e quebra de texto, proporção de largura dos containers, controles maiores que o necessário, composição inline de input com ícone quando houver espaço, responsividade em viewport estreita, estados loading/empty/error/success, foco/teclado/contraste e erros de console, rede ou assets.
- Para mudança de UI, registrar rota, viewport, estado exercitado, ações realizadas e evidência observada. Screenshot isolado não substitui inspeção de comportamento quando a interação for relevante.
- Usar `@Browser` ou equivalente integrado para revisar a página local quando disponível. Usar Chrome DevTools MCP para snapshot, screenshot, DOM, estilos, console e rede; usar Playwright existente ou solicitado para fluxos repetíveis e assertions como viewport, screenshot, visibilidade e acessibilidade.
- Se nenhuma capacidade visual estiver disponível, registrar a limitação e não marcar a validação visual como concluída. Não instalar dependência nova apenas para preencher esse gate.

### Fora

- Sincronizar automaticamente regras globais do usuário entre Codex e Antigravity, porque isso exigiria escrever fora do repositório e poderia sobrescrever preferências pessoais.
- Criar busca semântica, índice vetorial ou dependência nova. `rg` e rastreamento dirigido pelo fluxo são suficientes para esta entrega.
- Alterar o conteúdo histórico das phases já fechadas, exceto os arquivos de documentação canônica e o lixo WIP gerado no `.vibeflow` atual.
- Tornar a troca de chat uma validação bloqueante ou tentar criar chats por API a partir das skills portáveis.
- Criar uma biblioteca de componentes, um design system ou uma plataforma completa de regressão visual.
- Transformar toda ação em icon-only ou obrigar Playwright/Chrome DevTools para tarefas sem alteração de UI.
- Instalar Playwright, navegador ou outro pacote de teste visual sem necessidade real no repositório ou pedido explícito.

## Checklist de entrega

### Aceite

- [x] A1: o init mantém uma única fonte em `.vibeflow/REGRAS.md` e torna as regras carregáveis pelo Antigravity via `.agents/rules/vibeflow.md`.
- [x] A2: a documentação e os testes distinguem os caminhos globais e project-local do Codex e do Antigravity, e o pacote Antigravity passa por seu manifest documentado.
- [x] A3: nenhum motor, skill ou teste operacional depende de `*-wip.md`; o apply prepara o arquivo vivo sem sobrescrever conteúdo existente.
- [x] A4: as sete skills orientam investigação dirigida e deixam explícito que inventário não significa ler a árvore inteira.
- [x] A5: os handoffs e templates recomendam troca de chat nas portas plan, analyze, implement e review, e um chat por T* no implement.
- [x] A6: a documentação recomenda controles icon-only somente quando a ação for reconhecível, com nome acessível, foco visível e tooltip quando aplicável.
- [x] A7: a documentação define quando usar navegador integrado, Chrome DevTools MCP e Playwright, exige evidência visual para mudanças de UI e impede aprovação silenciosa sem capacidade de validação.

### Critérios de sucesso

- [x] C1: um projeto inicializado contém `.agents/rules/vibeflow.md` apontando para `.vibeflow/REGRAS.md`, e o teste de init cobre ausência, reparo e conflito sem copiar as regras.
- [x] C2: `python docs/tests/test-distribuicao.py -v` valida o manifest do Antigravity, os sete pacotes e os ponteiros exigidos.
- [x] C3: as suítes Python, launchers e PowerShell essenciais passam sem criar WIP durante apply.
- [x] C4: buscas canônicas não encontram instruções operacionais de preencher/promover WIP nem recomendação de leitura integral da árvore.
- [x] C5: os documentos de arquitetura e análise explicam a mudança de contrato, o motivo da escrita direta e a política de isolamento de chat.
- [x] C6: as referências visuais existentes contêm uma checklist enxuta cobrindo overflow, sobreposição, clipping/truncamento, proporção de largura, controles excessivos, composição inline, responsividade, estados, acessibilidade e console/rede/assets.
- [x] C7: as skills relevantes escolhem a ferramenta visual disponível, registram rota/viewport/estado/evidência e tratam indisponibilidade como limitação explícita, sem adicionar dependência nova.

## Implementação

### Stack

| Área | Escolha |
|---|---|
| Scripts | Python 3, PowerShell 7 e launchers existentes, sem dependência nova |
| Regras Antigravity | Markdown com `@` relativo, conforme documentação oficial |
| Testes | `unittest`, asserts PowerShell e harness Bash existentes |
| Distribuição | Manifests JSON existentes, sem novo instalador |
| Validação visual | Navegador integrado quando disponível, Chrome DevTools MCP para inspeção, Playwright existente ou solicitado para fluxos determinísticos |
| Dependências novas | Nenhuma |

### Estrutura tocada

```text
.vibeflow/REGRAS.md, .vibeflow/.gitignore                 # contrato vivo e lixo operacional
vibe-init/                                                 # ponte Antigravity e investigação de init
vibe-interview/ ... vibe-review/                          # skills, templates e motores sem WIP
docs/vibe-*/                                               # arquitetura, análise e testes de contrato
vibe-implement/references/chrome-devtools.md               # seleção de ferramenta e checklist operacional de prova visual
vibe-review/references/ui-visual-quality.md                # rubrica enxuta de auditoria visual e acessibilidade
docs/tests/test-distribuicao.py                           # prova de distribuição e manifest
docs/tests/test-visual-contract.py                        # prova textual do contrato visual
README.md                                                  # instalação, descoberta e handoffs
plugin.json                                                # manifest Antigravity compatível
```

### Estilo e padrões

- Preservar os três motores e as flags públicas, alterando somente a semântica interna necessária.
- Fazer escrita direta com preservação: arquivo existente nunca é apagado para “promover” outro conteúdo.
- Comentários semânticos em toda função nova ou alterada.
- Uma casa por fato: regras de governança no `REGRAS.md`, contrato mecânico na arquitetura e orientação executável na `SKILL.md`.
- Manter a checklist visual nas referências operacionais existentes, com evidência objetiva e sem transformar preferência estética em gate obrigatório.

### Contratos e módulos

- `vibe-init` é o dono do ponteiro `.agents/rules/vibeflow.md`.
- Cada script continua dono de inventário, seleção de alvo, validação de path, número/slug quando aplicável e relatório operacional.
- A IA é dona da prosa dos artefatos e do rastreamento semântico do fluxo.
- Relatórios continuam fora do Git; artefatos vivos entram no Git.

## Como provar

### Seams

- Comparar os caminhos oficiais pesquisados com README, `REGRAS.md`, init e manifest.
- Exercitar apply em pasta isolada com arquivo vivo existente e inexistente, confirmando preservação e ausência de WIP.
- Verificar paridade Python/PowerShell nos campos do relatório e nos erros de seleção.
- Buscar referências antigas a WIP, cópia/hash de promoção e leitura integral, separando histórico de contrato operacional.
- Exercitar o contrato visual por busca de termos obrigatórios e revisar o encaixe entre a seleção de ferramenta, a checklist e os critérios de aprovação.

### Estratégia

- Testes de init para o ponteiro Antigravity e backup/conflito.
- Testes de distribuição para manifest, pacotes e caminhos.
- Suítes existentes de cada motor e launcher, atualizadas para escrita direta.
- Teste textual das referências visuais e das regras de seleção de navegador integrado, Chrome DevTools MCP e Playwright.
- Inspeção final de `git diff --check` e busca textual dos contratos removidos.

### Comandos

```bash
python docs/vibe-init/tests/test-init.py -v
python docs/tests/test-distribuicao.py -v
python docs/vibe-interview/tests/test-interview.py -v
python docs/vibe-spec/tests/test-spec.py -v
python docs/vibe-plan/tests/test-plan.py -v
python docs/vibe-analyze/tests/test-analyze.py -v
python docs/vibe-implement/tests/test-implement.py -v
python docs/vibe-review/tests/test-review.py -v
```

## Boundaries

### Always

- Tratar os documentos oficiais consultados como evidência de host, sem prometer que um agente lê o formato de outro.
- Usar o arquivo vivo como fonte da verdade e preservar o conteúdo anterior em qualquer preparação de alvo.
- Investigar por perguntas, nomes, símbolos e fluxo real; abrir mais arquivos somente quando necessário para provar a decisão.
- Recomendar novo chat nas portas de maior risco cognitivo e registrar o handoff no arquivo.
- Em mudança de UI, abrir primeiro o navegador integrado se o host oferecer, registrar a viewport e validar a checklist visual antes de concluir implement ou review.
- Preferir ícones para ações universalmente reconhecíveis quando reduzirem ruído, sem remover nome acessível, foco, área de interação ou feedback.

### Ask first

- Alterar o caminho da fonte única, criar sincronização global entre agentes ou introduzir um índice de busca.
- Tornar a troca de chat obrigatória ou mudar a ordem da cadeia.

### Never

- Copiar `.vibeflow/REGRAS.md` para um segundo arquivo de regras.
- Restaurar o ciclo WIP como requisito de apply.
- Interpretar a lista de arquivos do inventário como autorização para ler toda a árvore.
- Tratar continuidade do chat como prova de que a etapa anterior está correta.
- Marcar uma mudança visual como aprovada apenas por teste unitário, snapshot de DOM ou screenshot sem revisar o estado renderizado e seus problemas de geometria.
- Instalar dependência de navegador ou transformar uma ação ambígua em icon-only sem necessidade demonstrada.

## Handoff

vibe-plan

- [x] Aprovação humana (leu o arquivo e confirmou)
