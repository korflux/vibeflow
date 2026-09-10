# Plan: interoperabilidade, escrita direta e isolamento de etapas
# Alvo: phase-8-interoperabilidade-skills
# Status: aprovado
# Spec: spec.md (mesma pasta)

## Overview

Executar a mudança de contrato da phase 8 em cinco frentes coordenadas: tornar `.vibeflow/REGRAS.md` carregável por cada host sem criar uma segunda fonte, alinhar a distribuição do plugin, substituir o ciclo WIP por escrita direta nos artefatos vivos, orientar investigação e handoff por relevância e isolamento de chat e formalizar uma prova visual objetiva para mudanças de interface. A ordem começa pelo bootstrap e pelo manifest, migra os motores em dois blocos com paridade Python/PowerShell, atualiza a orientação das sete skills, fecha o contrato visual, consolida a documentação canônica e termina com a remoção dos resíduos operacionais e a regressão completa.

## Ordem

### Fase 1: Governança e distribuição

- T1-T2

### Checkpoint: após T1-T2

- [x] `python docs/vibe-init/tests/test-init.py -v`
- [x] `python docs/tests/test-distribuicao.py -v`
- [x] Um fixture inicializado contém a ponte `.agents/rules/vibeflow.md` sem duplicar o conteúdo de `REGRAS.md` e o pacote continua expondo os sete diretórios de skills.

### Fase 2: Escrita direta nos motores

- T3-T4

### Checkpoint: após T3-T4

- [x] `python docs/vibe-interview/tests/test-interview.py -v`
- [x] `python docs/vibe-spec/tests/test-spec.py -v`
- [x] `python docs/vibe-plan/tests/test-plan.py -v`
- [x] `python docs/vibe-analyze/tests/test-analyze.py -v`
- [x] `python docs/vibe-implement/tests/test-implement.py -v`
- [x] `python docs/vibe-review/tests/test-review.py -v`
- [x] `python docs/tests/test-mvp-flow.py -v`
- [x] Cada apply prepara ou valida o artefato vivo, preserva bytes existentes e não cria WIP.

### Fase 3: Orientação operacional e prova visual

- T5-T6

### Checkpoint: após T5-T6

- [x] `python docs/tests/test-distribuicao.py -v`
- [x] `python docs/tests/test-visual-contract.py -v`
- [x] `git diff --check`
- [x] As sete skills orientam busca por perguntas, nomes, símbolos e fluxo real, recomendam isolamento de chat nas portas definidas e escolhem explicitamente a ferramenta visual disponível para mudanças de UI.

### Fase 4: Documentação canônica

- T7

### Checkpoint: após T7

- [x] `python docs/tests/test-distribuicao.py -v`
- [x] `python docs/tests/test-visual-contract.py -v`
- [x] `git diff --check`
- [x] `REGRAS.md`, README, arquiteturas, análises e referências visuais não contradizem os contratos da spec.

### Fase 5: Integração e fechamento

- T8

### Checkpoint: após T8

- [x] A suíte Python, os launchers, a paridade PowerShell e o gitleaks passam sem WIP operacional.
- [x] A busca canônica não encontra os contratos removidos de WIP, promoção, cópia/hash ou leitura integral da árvore.
- [x] O teste do contrato visual permanece integrado ao CI e não impõe navegador a tarefas sem UI.

## Riscos

| Risco | Impacto | Mitigação |
|---|---|---|
| A semântica de `--apply` divergir entre os dois motores ou entre as seis skills | alto | Portar o mesmo estado de destino, ações e erros em blocos verticais, com fixtures de arquivo ausente/existente e testes de paridade. |
| A ponte Antigravity sobrescrever regra local existente | alto | Tratar conteúdo divergente como legado, fazer backup verificado antes de reparar e registrar o conflito no relatório. |
| A documentação continuar descrevendo o ciclo antigo ou conflitar entre skills | alto | Atualizar arquitetura, análise, skill, template e regras a partir da mesma matriz de contrato, depois executar busca canônica. |
| Referências históricas a WIP gerarem falso positivo no aceite | médio | Restringir a busca de contrato operacional aos paths canônicos desta phase e preservar fases fechadas conforme o Fora da spec. |
| Caminhos do host Antigravity mudarem entre IDE e CLI | médio | Registrar as fontes oficiais na documentação e testar separadamente os caminhos workspace-local, global e do plugin. |
| Um host carregar `AGENTS.md` e `CLAUDE.md` simultaneamente e duplicar contexto apesar dos symlinks | alto | Manter adaptadores mínimos, não criar uma terceira cópia, inspecionar a carga efetiva com `grok inspect` e registrar smoke tests por host. |
| O limite ou a semântica de inclusão do Antigravity não comportar uma fonte viva grande | médio | Manter o arquivo descoberto como ponte curta, validar a inclusão relativa no host real e registrar a limitação se ela não for expandida. |
| Browser integrado, MCP ou perfil do Chrome não estar disponível durante a prova visual | alto | Selecionar a capacidade disponível, usar fallback somente quando já existir, registrar rota/viewport/estado/evidência e nunca declarar passe visual sem prova. |

## Paralelização

- Paralelo ok: T2 pode ser preparado depois que T1 fixar o caminho e o formato da ponte; T5 pode começar depois de T3 e T4; T6 depende da orientação de implement/review, mas pode ser desenvolvido em paralelo com a documentação semântica de T7.
- Sequencial: T1 antes de T2; T3 antes de T4; T5 antes de T6; T6 antes de T7; T8 por último, porque remove resíduos e valida a matriz completa.
- Contrato primeiro, depois paralelo: T3 estabelece a semântica de `--apply` no primeiro grupo de motores; T4 replica essa semântica no grupo com fila, analyze gate e re-review, sem criar uma terceira variante.

## Tasks

### T1: Preparar a ponte de regras do Antigravity e validar o bootstrap

- [x] T1 concluída
- **Spec:** A1, C1
- **Decisões:** HOST-01 (manter a fonte única e criar somente o adaptador mínimo descoberto pelo host)
- **O quê:** Estender `vibe-init` nos motores Python e PowerShell para criar `.agents/rules/vibeflow.md` com a inclusão relativa `@../../.vibeflow/REGRAS.md`, reportar o estado da ponte e preservar a segurança do reparo. Ponte ausente é criada, ponte correta é mantida e conteúdo divergente é copiado para `.vibeflow/old/` com verificação antes de ser reparado, sem merge automático de uma segunda fonte ou criação de `GEMINI.md` duplicado no projeto.
- **Aceite:**
  - [x] Um fixture novo inicializado contém a ponte exata e o conteúdo de `.vibeflow/REGRAS.md` não é duplicado nela.
  - [x] Uma segunda execução é idempotente; uma ponte divergente não é descartada sem backup e o relatório informa seu estado ou conflito.
  - [x] Python e PowerShell expõem os mesmos campos e ações relevantes do relatório para ausência, reparo e conflito.
- **Verificação:**
  - [x] `python vibe-init/scripts/init.py --help`
  - [x] `python docs/vibe-init/tests/test-init.py -v`
  - [x] `pwsh -NoProfile -File docs/vibe-init/tests/test-init.ps1`
- **Prova:** `python vibe-init/scripts/init.py --help` -> exit 0; `python docs/vibe-init/tests/test-init.py -v` -> 32 testes, OK; `pwsh -NoProfile -File docs/vibe-init/tests/test-init.ps1` -> pass=28 fail=0; fallback direto pelo `init.sh` com PowerShell 7 -> ponte criada.
- **Deps:** nenhuma
- **Arquivos:** `vibe-init/scripts/init.py`, `vibe-init/scripts/init.ps1`, `vibe-init/scripts/init.sh`, `docs/vibe-init/tests/test-init.py`, `docs/vibe-init/tests/test-init.ps1`, `docs/vibe-init/tests/test-init.sh`
- **Registro fora do escopo:** `.erros-encontrados/2026-09-07-harness-pwsh-gitbash.md` documenta a falha do isolamento de `pwsh` no harness Bash do Windows.
- **Limitação de ambiente:** `docs/vibe-init/tests/test-init.sh` executado via Git Bash com Python real -> pass=4 fail=1; somente `5-so-pwsh` falha ao resolver o alias temporário para `pwsh.dll`. O fallback direto com `C:\Program Files\PowerShell\7` passou.
- **Size:** medium, 5/10, superfície no módulo init, contrato de ponte compartilhado, fixture de integração, pequena investigação de conflito e ordem de reparo reversível.
- **Risk:** medium, altera a infraestrutura de regras carregada por agentes e precisa evitar perda de conteúdo local.

### T2: Alinhar o plugin Antigravity e os caminhos de instalação

- [x] T2 concluída
- **Spec:** A2, C2
- **Decisões:** HOST-01 (inspecionar a carga efetiva do host sem criar uma terceira fonte de regras)
- **O quê:** Adequar `plugin.json` ao formato mínimo documentado pelo Antigravity, manter `skills/` como diretório de componentes e separar no README os caminhos project-local, global, IDE, CLI e `npx skills`. Documentar `--copy` no Windows e a verificação por `/skills`, `agy plugin list`, `grok inspect` ou reinício do host, com teste estático dos sete pacotes e dos ponteiros.
- **Aceite:**
  - [x] `plugin.json` é JSON válido, passa pelo manifest mínimo documentado e não cria aliases ou diretório `commands/`.
  - [x] O README distingue instalação project-local e global, Antigravity IDE e CLI, registra o fallback `--copy` no Windows e informa como confirmar a descoberta.
  - [x] O README registra que hosts que carregam mais de um nome de regra devem ser inspecionados para evitar contexto duplicado, sem criar outra fonte canônica.
  - [x] `docs/tests/test-distribuicao.py -v` valida manifest, sete pacotes, ponteiros `skills/` e os comandos documentados.
- **Verificação:**
  - [x] `python docs/tests/test-distribuicao.py -v`
- **Prova:** `python docs/tests/test-distribuicao.py -v` -> 8 testes, OK; checkpoint T1–T2: `python docs/vibe-init/tests/test-init.py -v` -> 32 testes, OK; `git diff --check` -> sem erros.
- **Deps:** T1
- **Arquivos:** `plugin.json`, `README.md`, `docs/tests/test-distribuicao.py`
- **Size:** medium, 6/10, superfície em manifest, documentação e teste, acoplamento com o contrato externo do host, verificação estática de distribuição, investigação de schema e dependência da ponte definida em T1.
- **Risk:** medium, uma instrução incorreta pode impedir a descoberta das skills em um host específico.

### Checkpoint: após T1-T2

- [x] `python docs/vibe-init/tests/test-init.py -v`
- [x] `python docs/tests/test-distribuicao.py -v`

### T3: Migrar interview, spec e plan para artefatos vivos

- [x] T3 concluída
- **Spec:** A3, C3
- **O quê:** Alterar os motores Python e PowerShell de `vibe-interview`, `vibe-spec` e `vibe-plan` para que `--apply` execute os gates mecânicos, resolva o mesmo alvo e prepare a pasta e o arquivo vivo somente quando necessário. O arquivo existente permanece byte a byte, a flag pública continua disponível e o relatório deixa de carregar estado WIP, promoção, cópia ou hash.
- **Aceite:**
  - [x] Fixture com destino inexistente cria a pasta e o arquivo vivo depois dos gates, sem criar `interview-wip.md`, `spec-wip.md` ou `plan-wip.md`.
  - [x] Fixture com arquivo vivo existente preserva seu conteúdo, mesmo quando `--apply` é executado novamente.
  - [x] Seleção phase/MVP/`--dir`, erros de path e paridade Python/PowerShell continuam funcionando sem `WIP_AUSENTE` ou `COPY_HASH_MISMATCH`.
  - [x] As suítes e launchers deste grupo não escrevem nem exigem WIP para testar apply.
- **Verificação:**
  - [x] `python docs/vibe-interview/tests/test-interview.py -v`
  - [x] `python docs/vibe-spec/tests/test-spec.py -v`
  - [x] `python docs/vibe-plan/tests/test-plan.py -v`
  - [x] `bash docs/vibe-interview/tests/test-interview.sh`
  - [x] `bash docs/vibe-spec/tests/test-spec.sh`
  - [x] `bash docs/vibe-plan/tests/test-plan.sh`
- **Deps:** nenhuma
- **Prova:** `python docs/vibe-interview/tests/test-interview.py -v` -> 19 testes, OK; `python docs/vibe-spec/tests/test-spec.py -v` -> 17 testes, OK; `python docs/vibe-plan/tests/test-plan.py -v` -> 21 testes, OK; `bash docs/vibe-interview/tests/test-interview.sh` -> pass=6 fail=0; `bash docs/vibe-spec/tests/test-spec.sh` -> pass=6 fail=0; `bash docs/vibe-plan/tests/test-plan.sh` -> pass=6 fail=0. As suítes Python incluem a paridade PowerShell 7 e a preservação byte a byte do vivo.
- **Arquivos:** `vibe-interview/scripts/interview.py`, `vibe-interview/scripts/interview.ps1`, `vibe-interview/scripts/interview.sh`, `vibe-spec/scripts/spec.py`, `vibe-spec/scripts/spec.ps1`, `vibe-spec/scripts/spec.sh`, `vibe-plan/scripts/plan.py`, `vibe-plan/scripts/plan.ps1`, `vibe-plan/scripts/plan.sh`, `docs/vibe-interview/tests/test-interview.py`, `docs/vibe-interview/tests/test-interview.sh`, `docs/vibe-spec/tests/test-spec.py`, `docs/vibe-spec/tests/test-spec.sh`, `docs/vibe-plan/tests/test-plan.py`, `docs/vibe-plan/tests/test-plan.sh`, `docs/tests/launcher-harness.sh`
- **Size:** high, 7/10, superfície em três pacotes, contrato compartilhado de destino e relatório, verificação de integração e paridade, semântica nova de escrita direta e coordenação de gates preservada.
- **Risk:** high, muda o contrato público de gravação dos artefatos e pode sobrescrever histórico se a preservação não for testada.

### T4: Migrar analyze, implement e review sem perder histórico vivo

- [x] T4 concluída
- **Spec:** A3, C3
- **O quê:** Portar a escrita direta para `vibe-analyze`, `vibe-implement` e `vibe-review`, mantendo a fila elegível, o gate de analyze do MVP e os estados de re-review. `implement.md`, `analyze.md` e `review.md` existentes são lidos e atualizados pela IA; o apply apenas prepara ou valida o destino e nunca substitui o vivo por um WIP acumulado.
- **Aceite:**
  - [x] Apply em phase e MVP mantém os gates existentes, cria o vivo ausente e preserva o vivo existente, inclusive no segundo apply de implement e review.
  - [x] O relatório dos três motores não expõe `wip`, `promover_wip`, `WIP_AUSENTE` ou `COPY_HASH_MISMATCH`; os erros de seleção e o gate de analyze permanecem úteis.
  - [x] As suítes e launchers exercitam arquivo vivo ausente/existente, fila e re-review sem criar WIP.
  - [x] O fluxo MVP deixa de escrever `*-wip.md` em todas as seis etapas e continua usando exclusivamente `.vibeflow/mvp`.
- **Verificação:**
  - [x] `python docs/vibe-analyze/tests/test-analyze.py -v`
  - [x] `python docs/vibe-implement/tests/test-implement.py -v`
  - [x] `python docs/vibe-review/tests/test-review.py -v`
  - [x] `python docs/tests/test-mvp-flow.py -v`
  - [x] `bash docs/vibe-analyze/tests/test-analyze.sh`
  - [x] `bash docs/vibe-implement/tests/test-implement.sh`
  - [x] `bash docs/vibe-review/tests/test-review.sh`
- **Prova:** `python docs/vibe-analyze/tests/test-analyze.py -v` -> 18 testes, OK; `python docs/vibe-implement/tests/test-implement.py -v` -> 32 testes, OK; `python docs/vibe-review/tests/test-review.py -v` -> 19 testes, OK; `python docs/tests/test-mvp-flow.py -v` -> 2 testes, OK; `C:\Program Files\Git\bin\bash.exe docs/vibe-analyze/tests/test-analyze.sh` -> pass=7 fail=0; `C:\Program Files\Git\bin\bash.exe docs/vibe-implement/tests/test-implement.sh` -> pass=8 fail=0; `C:\Program Files\Git\bin\bash.exe docs/vibe-review/tests/test-review.sh` -> pass=7 fail=0. As suítes Python incluem paridade PowerShell 7.
- **Deps:** T3
- **Arquivos:** `vibe-analyze/scripts/analyze.py`, `vibe-analyze/scripts/analyze.ps1`, `vibe-implement/scripts/implement.py`, `vibe-implement/scripts/implement.ps1`, `vibe-review/scripts/review.py`, `vibe-review/scripts/review.ps1`, `docs/vibe-analyze/tests/test-analyze.py`, `docs/vibe-analyze/tests/test-analyze.sh`, `docs/vibe-implement/tests/test-implement.py`, `docs/vibe-implement/tests/test-implement.sh`, `docs/vibe-review/tests/test-review.py`, `docs/vibe-review/tests/test-review.sh`, `docs/tests/test-mvp-flow.py`, `docs/tests/launcher-harness.sh`
- **Size:** high, 8/10, superfície em três pacotes com fila e re-review, contrato compartilhado, verificação de integração e paridade, comportamento novo de preservação e coordenação crítica do histórico.
- **Risk:** high, erro de preparação pode perder histórico de implementação, análise ou revisão e quebrar a rota MVP.

### Checkpoint: após T3-T4

- [x] `python docs/vibe-interview/tests/test-interview.py -v`
- [x] `python docs/vibe-spec/tests/test-spec.py -v`
- [x] `python docs/vibe-plan/tests/test-plan.py -v`
- [x] `python docs/vibe-analyze/tests/test-analyze.py -v`
- [x] `python docs/vibe-implement/tests/test-implement.py -v`
- [x] `python docs/vibe-review/tests/test-review.py -v`
- [x] `python docs/tests/test-mvp-flow.py -v`

### T5: Orientar investigação dirigida e isolamento de chat nas sete skills

- [x] T5 concluída
- **Spec:** A4, A5, C4, C5
- **O quê:** Atualizar as sete `SKILL.md` e os templates aplicáveis para começar pela pergunta da task, localizar evidências com `rg` e `rg --files`, abrir apenas entradas e dependências do fluxo e expandir a leitura somente quando uma lacuna bloquear a prova. Registrar também o uso direto do artefato vivo, o status `rascunho` e a recomendação de novo chat nas portas plan, analyze, implement e review, com um chat focado por T* no implement.
- **Aceite:**
  - [x] Todas as skills substituem instruções genéricas de leitura integral por investigação por perguntas, nomes, símbolos e fluxo, preservando a leitura estrutural limitada do init.
  - [x] Os templates e fechamentos recomendam novo chat nas portas definidas, permitem continuidade consciente e mantêm o arquivo vivo como ponte entre chats.
  - [x] `vibe-implement` explicita um chat por T* quando houver fila e nenhuma skill orienta preencher ou promover WIP.
  - [x] Os testes de contrato falham se a orientação de leitura integral, WIP ou handoff sem isolamento voltar.
- **Verificação:**
  - [x] `python docs/tests/test-distribuicao.py -v`
  - [x] `python docs/vibe-init/tests/test-init.py -v`
  - [x] `python docs/vibe-interview/tests/test-interview.py -v`
  - [x] `python docs/vibe-spec/tests/test-spec.py -v`
  - [x] `python docs/vibe-plan/tests/test-plan.py -v`
  - [x] `python docs/vibe-analyze/tests/test-analyze.py -v`
  - [x] `python docs/vibe-implement/tests/test-implement.py -v`
  - [x] `python docs/vibe-review/tests/test-review.py -v`
- **Prova:** `python docs/tests/test-distribuicao.py -v` -> 9 testes, OK; `python docs/vibe-init/tests/test-init.py -v` -> 32 testes, OK; `python docs/vibe-interview/tests/test-interview.py -v` -> 19 testes, OK; `python docs/vibe-spec/tests/test-spec.py -v` -> 17 testes, OK; `python docs/vibe-plan/tests/test-plan.py -v` -> 21 testes, OK; `python docs/vibe-analyze/tests/test-analyze.py -v` -> 18 testes, OK; `python docs/vibe-implement/tests/test-implement.py -v` -> 32 testes, OK; `python docs/vibe-review/tests/test-review.py -v` -> 19 testes, OK.
- **Arquivos:** `vibe-init/SKILL.md`, `vibe-interview/SKILL.md`, `vibe-interview/templates/interview.md`, `vibe-spec/SKILL.md`, `vibe-spec/templates/spec.md`, `vibe-plan/SKILL.md`, `vibe-plan/templates/plan.md`, `vibe-analyze/SKILL.md`, `vibe-analyze/templates/analyze.md`, `vibe-implement/SKILL.md`, `vibe-implement/templates/implement.md`, `vibe-review/SKILL.md`, `vibe-review/templates/review.md`, `docs/tests/test-distribuicao.py`.
- **Deps:** T3, T4
- **Size:** medium, 6/10, superfície em pacotes de instrução e templates, contrato interno compartilhado, verificação textual, investigação de redação e dependência da semântica direta já definida.
- **Risk:** medium, altera o comportamento esperado dos agentes e a forma de transportar contexto entre etapas.

### T6: Documentar controles compactos e prova visual no navegador

- [x] T6 concluída
- **Spec:** A6, A7, C6, C7
- **Decisões:** UI-01 (usar icon-only somente para ações universalmente reconhecíveis, preservando semântica e acessibilidade); QA-01 (preferir navegador integrado e usar fallbacks disponíveis sem instalação automática)
- **O quê:** Atualizar `vibe-implement/references/chrome-devtools.md` e `vibe-review/references/ui-visual-quality.md` para formar uma checklist curta e objetiva de validação renderizada. Atualizar `vibe-plan/SKILL.md`, `vibe-implement/SKILL.md` e `vibe-review/SKILL.md` para alocar e selecionar navegador integrado quando disponível, Chrome DevTools MCP para inspeção e Playwright somente quando já existir no repositório ou for solicitado. Registrar também a recomendação de ícones para ações universalmente reconhecíveis, com os requisitos de acessibilidade e sem converter ações ambíguas em icon-only.
- **Aceite:**
  - [x] As referências definem ícone de lixeira para apagar como exemplo de ação reconhecível, exigem nome acessível, foco visível, área de interação adequada e tooltip quando aplicável, e preservam texto em ações ambíguas.
  - [x] A checklist cobre overflow, conteúdo fora da viewport, clipping, sobreposição/cobertura, z-index, truncamento/quebra, proporção de largura, controles grandes, input e ícone na mesma linha quando houver espaço, viewport estreita, estados, foco/teclado/contraste e console/rede/assets.
  - [x] A seleção de ferramenta e o fallback são explícitos: navegador integrado primeiro quando disponível, Chrome DevTools MCP para snapshot/screenshot/DOM/estilos/console/rede e Playwright existente ou solicitado para fluxos repetíveis e assertions. Indisponibilidade não vira passe visual e não gera instalação automática.
  - [x] Um teste de contrato verifica os termos e seções essenciais das referências; a integração do CI fica prevista para a T8, que é a task responsável pelo fechamento da integração final.
- **Verificação:**
  - [x] `python docs/tests/test-visual-contract.py -v`
  - [x] `python docs/vibe-plan/tests/test-plan.py -v`
  - [x] `python docs/vibe-implement/tests/test-implement.py -v`
  - [x] `python docs/vibe-review/tests/test-review.py -v`
  - [x] `git diff --check`
- **Prova:** `python docs/tests/test-visual-contract.py -v` -> 4 testes, OK; `python docs/vibe-plan/tests/test-plan.py -v` -> 21 testes, OK; `python docs/vibe-implement/tests/test-implement.py -v` -> 32 testes, OK; `python docs/vibe-review/tests/test-review.py -v` -> 19 testes, OK; `git diff --check` -> exit 0, sem erros de whitespace.
- **Deps:** T5
- **Arquivos:** `vibe-implement/references/chrome-devtools.md`, `vibe-review/references/ui-visual-quality.md`, `vibe-plan/SKILL.md`, `vibe-implement/SKILL.md`, `vibe-review/SKILL.md`, `docs/tests/test-visual-contract.py`
- **Size:** medium, 6/10, superfície em duas referências, duas skills e um teste textual, contrato compartilhado de prova visual, sem dependência de navegador novo e com risco concentrado em evitar falsos passes.
- **Risk:** high, uma instrução incompleta pode deixar overflow, sobreposição ou problema de acessibilidade escapar para review; uma instrução agressiva pode obrigar ferramenta inexistente ou iconizar ações ambíguas.

### T7: Atualizar documentação canônica e a fonte viva de regras

- [x] T7 concluída
- **Spec:** A1, A2, A4, A5, A6, A7, C4, C5, C6, C7
- **O quê:** Reescrever `ARQUITETURA.md` e `ANALISE.md` das sete skills, os trechos de fluxo do README, `.vibeflow/REGRAS.md` e `docs/ESCOPO.md` para descrever a ponte Antigravity, os adaptadores por host, a precedência Codex/Antigravity, a escrita direta, os relatórios sem WIP, a investigação dirigida, a política de chat e a prova visual. Não publicar nesta task a decisão `UI-01` na tabela de decisões vigentes de `REGRAS.md`: esse patch só pode ocorrer após implementação, review aprovada e confirmação humana; nesta phase, a orientação operacional permanece nas skills e referências, sem alterar o conteúdo histórico das phases fechadas.
- **Aceite:**
  - [x] A documentação canônica descreve um único `.vibeflow/REGRAS.md`, o include relativo do Antigravity e os caminhos globais separados de Codex e Antigravity.
  - [x] Os sete contratos documentam `--apply` como preparação/validação do vivo, sem cópia, hash, promoção ou remoção de WIP, e deixam claro que a IA escreve a prosa.
  - [x] README, REGRAS, arquitetura, análise e referências visuais não se contradizem sobre investigação, handoff, chat, controles icon-only ou seleção de ferramenta, e a busca canônica distingue documentação histórica fora do escopo.
  - [x] A documentação registra que o Codex desktop pode usar navegador integrado quando disponível, enquanto ambientes sem essa capacidade devem declarar a limitação ou usar somente um fallback já existente.
- **Verificação:**
  - [x] `python docs/tests/test-distribuicao.py -v`
  - [x] `python docs/tests/test-visual-contract.py -v`
  - [x] `git diff --check`
  - **Prova:** `python docs/tests/test-distribuicao.py -v` -> 9 testes, OK; `python docs/tests/test-visual-contract.py -v` -> 4 testes, OK; `git diff --check` -> exit 0, sem erros de whitespace; busca canônica revisada, com hits restritos aos backups/hash legítimos do init e aos asserts dos testes.
  - **Decisões:** HOST-01 documentada; UI-01 permanece operacional nas skills e referências e não é publicada em `REGRAS.md` nesta task.
  - [x] `rg -n -i "wip|promov|copy_hash|sha256|árvore inteira|leitura integral|novo chat|chat por" README.md .vibeflow/REGRAS.md docs/vibe-init docs/vibe-interview docs/vibe-spec docs/vibe-plan docs/vibe-analyze docs/vibe-implement docs/vibe-review vibe-init vibe-interview vibe-spec vibe-plan vibe-analyze vibe-implement vibe-review
- **Deps:** T6
- **Arquivos:** `.vibeflow/REGRAS.md`, `README.md`, `docs/ESCOPO.md`, `docs/vibe-init/ARQUITETURA.md`, `docs/vibe-init/ANALISE.md`, `docs/vibe-interview/ARQUITETURA.md`, `docs/vibe-interview/ANALISE.md`, `docs/vibe-spec/ARQUITETURA.md`, `docs/vibe-spec/ANALISE.md`, `docs/vibe-plan/ARQUITETURA.md`, `docs/vibe-plan/ANALISE.md`, `docs/vibe-analyze/ARQUITETURA.md`, `docs/vibe-analyze/ANALISE.md`, `docs/vibe-implement/ARQUITETURA.md`, `docs/vibe-implement/ANALISE.md`, `docs/vibe-review/ARQUITETURA.md`, `docs/vibe-review/ANALISE.md`, `vibe-implement/references/chrome-devtools.md`, `vibe-review/references/ui-visual-quality.md`
- **Size:** high, 7/10, superfície em documentação canônica e regras vivas, acoplamento com todos os contratos públicos, verificação textual e de distribuição, investigação de fontes externas e coordenação da mesma redação entre sete skills.
- **Risk:** high, documentação divergente altera o comportamento dos agentes e pode reintroduzir uma segunda fonte de regras ou um handoff incorreto.

### Checkpoint: após T6-T7

- [x] `python docs/tests/test-distribuicao.py -v`
- [x] `python docs/tests/test-visual-contract.py -v`
- [x] `git diff --check`

### T8: Consolidar a prova sem WIP e fechar a regressão do contrato

- [x] T8 concluída
- **Spec:** A1, A2, A3, A4, A5, A6, A7, C1, C2, C3, C4, C5, C6, C7
- **O quê:** Atualizar a integração dos testes e do CI para o contrato final, incluir o teste do contrato visual sem impor navegador a tarefas sem UI, reforçar o fluxo MVP e os launchers, retirar as entradas WIP de `.vibeflow/.gitignore` e remover os artefatos WIP operacionais existentes em `.vibeflow/`. Executar a suíte completa, a busca canônica, a verificação de diff e o gitleaks como prova de fechamento.
- **Aceite:**
  - [x] Nenhum motor, launcher, skill ou teste operacional depende de `*-wip.md`; o `.vibeflow/.gitignore` preserva os relatórios e remove somente as entradas WIP.
  - [x] Os WIPs operacionais presentes em `.vibeflow/` não existem após a limpeza, sem alterar reports ou phases históricas.
  - [x] Todas as suítes Python, os sete launchers, a paridade PowerShell do init e o fluxo MVP passam com apply direto.
  - [x] A busca final não encontra instrução operacional de preencher/promover WIP, cópia/hash de promoção ou leitura integral da árvore nos paths canônicos.
  - [x] `docs/tests/test-visual-contract.py -v` passa e permanece no CI como teste textual do contrato; nenhuma tarefa sem UI passa a exigir browser.
  - [x] `gitleaks` passa no checkout final e `git diff --check` não aponta erro.
- **Verificação:**
  - [x] `python docs/vibe-init/tests/test-init.py -v`
  - [x] `python docs/tests/test-distribuicao.py -v`
  - [x] `python docs/vibe-interview/tests/test-interview.py -v`
  - [x] `python docs/vibe-spec/tests/test-spec.py -v`
  - [x] `python docs/vibe-plan/tests/test-plan.py -v`
  - [x] `python docs/vibe-analyze/tests/test-analyze.py -v`
  - [x] `python docs/vibe-implement/tests/test-implement.py -v`
  - [x] `python docs/vibe-review/tests/test-review.py -v`
  - [x] `python docs/tests/test-mvp-flow.py -v`
  - [x] `python docs/tests/test-visual-contract.py -v`
  - [x] `python docs/tests/test-reparse-safety.py -v`
  - [x] `pwsh -NoProfile -File docs/vibe-init/tests/test-init.ps1`
  - [x] `bash docs/vibe-init/tests/test-init.sh`
  - [x] `bash docs/vibe-interview/tests/test-interview.sh`
  - [x] `bash docs/vibe-spec/tests/test-spec.sh`
  - [x] `bash docs/vibe-plan/tests/test-plan.sh`
  - [x] `bash docs/vibe-analyze/tests/test-analyze.sh`
  - [x] `bash docs/vibe-implement/tests/test-implement.sh`
  - [x] `bash docs/vibe-review/tests/test-review.sh`
  - [x] `rg -n -i "wip|promov|copy_hash|sha256|árvore inteira|leitura integral" README.md .vibeflow/REGRAS.md .vibeflow/.gitignore docs/vibe-init docs/vibe-interview docs/vibe-spec docs/vibe-plan docs/vibe-analyze docs/vibe-implement docs/vibe-review docs/tests .github/workflows/contrato.yml vibe-init vibe-interview vibe-spec vibe-plan vibe-analyze vibe-implement vibe-review`
  - [x] `gitleaks detect --source . --verbose --redact --no-banner`
  - [x] `git diff --check`
- **Prova:** 32 testes init, 9 distribuição, 19 interview, 17 spec, 21 plan, 18 analyze, 32 implement, 19 review, 2 MVP, 4 visuais e 12 de reparse, todos OK; PowerShell init `pass=28 fail=0`; launchers Bash `5/5`, `6/6`, `6/6`, `6/6`, `7/7`, `8/8` e `7/7`; gitleaks 8.30.1 sem leaks; `git diff --check` exit 0. A busca canônica deixou apenas asserts negativos dos testes, documentação explícita de investigação dirigida e hashes legítimos do init.
- **Decisões:** o contrato de WIP foi removido do runtime e do ignore; a prova visual foi incorporada ao CI sem impor navegador às tasks sem UI; o launcher valida executáveis Python/PowerShell antes de escolhê-los e o harness usa wrapper para preservar a resolução de `pwsh.dll` no Windows.
- **Deps:** T1, T2, T3, T4, T5, T6, T7
- **Arquivos:** `.vibeflow/.gitignore`, `.vibeflow/implement-wip.md`, `docs/tests/test-distribuicao.py`, `docs/tests/test-mvp-flow.py`, `docs/tests/test-visual-contract.py`, `docs/tests/launcher-harness.sh`, `.github/workflows/contrato.yml`, `vibe-init/scripts/init.sh`
- **Size:** high, 8/10, superfície em integração, testes e lixo operacional, acoplamento com todos os contratos, verificação completa com launchers, PowerShell e gitleaks, baixa incerteza e coordenação final irreversível apenas para artefatos gerados.
- **Risk:** high, é a prova final de uma quebra de contrato que afeta toda a cadeia e remove artefatos operacionais antigos.
- **Correção pós-review:** R1, R2 e R3 corrigidos. O ignore não mantém WIP; os seis motores rejeitam links de diretório e artefato vivo antes de inventariar, selecionar ou escrever.
- **Prova pós-review:** `python docs/tests/test-reparse-safety.py -v` -> 6 testes, OK, com Python e PowerShell; suítes Python, PowerShell init, launchers Git Bash real, gitleaks e `git diff --check` permaneceram verdes.
- **Arquivos pós-review:** os doze motores `vibe-*/scripts/*.{py,ps1}` da cadeia, `docs/tests/test-reparse-safety.py`, `docs/tests/test-distribuicao.py`, `.github/workflows/contrato.yml` e `.vibeflow/.gitignore`.

## Correção pós-review, R5-R6

- Feito: os seis pares Python/PowerShell agora validam `.vibeflow/.gitignore` e `.vibeflow/<skill>-report.json` antes de qualquer escrita, rejeitando symlink, junction, reparse point e diretório no lugar de arquivo operacional. O `vibe-init` passou a rejeitar `.vibeflow` linkado e os filhos mutáveis do init antes da primeira mutação, com a mesma proteção nos dois motores.
- Marcado: R5 e R6 no `review.md` como corrigidos por prova; R4 continua dependendo da aprovação humana do `plan.md`.
- Prova: `python docs/tests/test-reparse-safety.py -v` -> 12 testes, OK, cobrindo relatório e `.gitignore` linkados nos seis motores e `.vibeflow` linkado no init em Python e PowerShell; suítes Python completas OK; PowerShell init `pass=28 fail=0`; sete launchers Git Bash real verdes; gitleaks sem leaks; `git diff --check` exit 0.
- Arquivos: os doze motores da cadeia, `vibe-init/scripts/init.py`, `vibe-init/scripts/init.ps1` e `docs/tests/test-reparse-safety.py`.

### Checkpoint: após T8

- [x] `python docs/vibe-init/tests/test-init.py -v`
- [x] `python docs/tests/test-distribuicao.py -v`
- [x] `python docs/vibe-interview/tests/test-interview.py -v`
- [x] `python docs/vibe-spec/tests/test-spec.py -v`
- [x] `python docs/vibe-plan/tests/test-plan.py -v`
- [x] `python docs/vibe-analyze/tests/test-analyze.py -v`
- [x] `python docs/vibe-implement/tests/test-implement.py -v`
- [x] `python docs/vibe-review/tests/test-review.py -v`
- [x] `python docs/tests/test-mvp-flow.py -v`
- [x] `python docs/tests/test-visual-contract.py -v`
- [x] `python docs/tests/test-reparse-safety.py -v`
- [x] `gitleaks detect --source . --verbose --redact --no-banner`
- [x] `git diff --check`

## Conferência

- [x] Spec aprovada como fonte; mesma pasta
- [x] Fatias verticais; score de Size ≤ 8; Risk separado
- [x] Toda T* tem aceite + verificação + Spec: A*/C* quando couber
- [x] Ferramentas essenciais: `gitleaks 8.30.1` validado; MCP Chrome DevTools disponível, mas a sessão atual está ocupada pelo perfil do Chrome; Playwright não está instalado e não será adicionado; navegador integrado documentado como condicional
- [x] T1 estabelece ponto de entrada real com `python vibe-init/scripts/init.py --help`
- [x] UI greenfield/sem DS: N/A
- [x] Checkpoints a cada 2 ou 3 T*
- [ ] Aprovação humana, leitura e confirmação do plan

## Handoff

vibe-implement

Recomendação de chat: abrir novo chat para `vibe-implement` e usar um chat focado por T*.
