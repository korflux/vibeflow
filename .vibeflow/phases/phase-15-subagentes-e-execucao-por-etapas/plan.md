# Plan: subagentes instalados e execução por etapas
# Alvo: phase-15-subagentes-e-execucao-por-etapas
# Status: aprovado
# Spec: spec.md (mesma pasta)

## Overview

Entregar os perfis dos cinco subagentes pelo init, reorganizar o Modo A em etapas com prova integrada e exigir evidência de completude na review. A spec foi aprovada por Marco em 2026-10-10, incluindo o commit integrado no Modo A. Rota high; nenhuma mudança nos perfis globais pessoais.

- **Design:** N/A, instalação local e orquestração sem UI.
- **Execução desta phase:** usar o contrato vigente para construir e provar o novo contrato, sem mudar o protocolo da própria run no meio da implementação. As três tasks continuam com prova e commit próprios nesta migração; o novo Modo A é exercitado nas fixtures e passa a valer para novas runs. Isso preserva a regra da spec de não reinterpretar silenciosamente runs antigas.
- **Contrato de destino:** Modo A sequencial, etapas de implementação, complementação de testes, validação integrada, correção e review, com commit integrado somente após prova verde. Modo B mantém o ciclo por tarefa.

## Prontidão das provas

- **Requisitos verificados em 2026-10-10:** Python 3.13.14, PowerShell 7.6.6, Git e Gitleaks 8.30.1 disponíveis localmente. Git Bash existe em `C:/Program Files/Git/bin/bash.exe`; usar esse executável explicitamente no Windows, sem depender do `bash.exe` do WSL.
- **CI existente:** `.github/workflows/contrato.yml` executa as suítes Python, paridade PowerShell do init, launchers Unix e Gitleaks. Sem dependências de terceiros ou lockfile, não há SCA aplicável neste pacote.
- **Capacidade comportamental:** subagentes disponíveis nesta sessão. Avaliações independentes devem usar fixtures isoladas e contexto mínimo, sem acesso de escrita aos perfis pessoais e sem push externo. Não iniciar chamadas pagas adicionais de `claude -p` implicitamente.
- **Piloto existente:** `docs/vibe-implement/tests/piloto-modo-a.py --prepare-only` prepara e valida fixtures sem chamar modelos. Isso não comprova comportamento da skill; a avaliação com subagente complementa a prova determinística.
- **Ausências e ação na fila:** nenhuma dependência de instalação identificada. Carregamento real em cada host é distinto da instalação no disco; relatar explicitamente qualquer host indisponível para a prova de descoberta. Não certificar ativação apenas pela presença de arquivos.
- **Regra de testes:** testar os motores e efeitos no disco. Não criar asserts de palavras, frases ou seções de SKILL.md, templates ou referências. Revisão textual de coerência e avaliação comportamental são evidências separadas.
- **Provas compartilhadas:** executar uma vez no estado integrado a distribuição, fluxo MVP, segurança de reparse e varredura de segredos; repetir só quando alteração posterior invalidar seus inputs. Não reproduzir toda a suíte em cada task.

## Tasks

### T1: Instalar os cinco papéis nos dois hosts preservando personalizações

- [x] T1 concluída
- **Spec:** A1, A2, A3, C1, C4
- **O quê:** empacotar os perfis de Codex e Claude Code baseados nos arquivos pessoais já inspecionados e instalá-los no projeto pelo init. Manter modelos, esforços e restrições por papel; prompts devem delegar o fluxo à skill e resolver referências sem paths pessoais. Instalar os dois adaptadores, sem alterar arquivos globais ou configurações gerais do host.
- **Aceite:**
  - [x] Dez perfis distribuídos sob `vibe-init`, cinco TOML e cinco Markdown, são instalados em `.codex/agents/` e `.claude/agents/` pela mesma execução do init.
  - [x] Motores Python e PowerShell validam previamente fontes e destinos conhecidos, tamanho máximo de 1 MiB, tipo regular e ausência de reparse points em toda a cadeia do destino.
  - [x] Arquivos ausentes são criados; idênticos são preservados; diferentes permanecem intactos e geram conflito explícito. Repetição não modifica bytes das personalizações.
  - [x] Relatório estende o contrato existente com resultado por host/papel/path; não afirma que a sessão carregou os perfis. A skill orienta conferir disponibilidade e recarga quando necessária.
  - [x] Commit do init inclui somente paths produzidos autorizados e backups necessários, sem configuração pessoal, sem relatório transitório e sem push.
  - [x] Contrato e fluxo são documentados antes dos motores. Os testes exercitam instalação, segunda execução, conflito, arquivo/diretório inesperado, link quebrado, ancestral inseguro e paridade essencial, com limpeza obrigatória.
- **Verificação:**
  - [x] `python docs/vibe-init/tests/test-init.py`
  - [x] `pwsh -NoProfile -File docs/vibe-init/tests/test-init.ps1`
  - [x] `& 'C:/Program Files/Git/bin/bash.exe' docs/vibe-init/tests/test-init.sh`
  - [x] Conferir os perfis produzidos por execução real em fixture: estrutura TOML/frontmatter, nomes e campos nativos. Não testar texto de prompt.
- **Deps:** nenhuma
- **Arquivos:** `docs/vibe-init/ARQUITETURA.md`, `docs/vibe-init/ANALISE.md`, `vibe-init/SKILL.md`, `vibe-init/scripts/init.py`, `vibe-init/scripts/init.ps1`, novos recursos `vibe-init/templates/agents/codex/*.toml` e `vibe-init/templates/agents/claude/*.md`, `docs/vibe-init/tests/test-init.py`, `docs/vibe-init/tests/test-init.ps1`.
- **Risco:** nomes de papéis do projeto podem prevalecer sobre os pessoais. Informar a precedência no fluxo sem modificar o global. Conflito não autoriza substituição automática. Preservar os contratos atuais de migração e backup do init.

- **Prova final T1:** Python: 11 testes OK (11,812 s); PowerShell: 5 cenários PASS; launcher Git Bash: exit 0 fora do sandbox, após falha de inicialização 0xC0000142 no sandbox; diff check verde. Fixtures reais de ambos os motores conferiram bytes, estrutura nativa, modelos/esforços, idempotência, conflitos e recusa prévia de fontes/destinos inseguros; limpeza concluída. Nenhum teste textual de prompt.
- **Resultado T1:** dez perfis distribuídos e motores alinhados. Cinco papéis disponíveis na sessão Codex atual; carregamento dos novos perfis não certificado. Claude indisponível, formato conferido por documentação oficial. Sem mudanças globais ou pendências T1.

- **Correção R1 pós-review:** entrypoints por alias instalados são suportados resolvendo somente a raiz física do pacote; links internos continuam recusados. Prova final init 12 testes OK (25,299 s), PS 5 PASS, launcher-alias exit 0, Gitleaks/diff verdes. Corrigidos init.py/init.ps1, teste Python/launcher e docs do init. R1 rastreado no review, sem reabrir task concluída.

### T2: Executar o Modo A em etapas com retomada e commit integrado

- [x] T2 concluída
- **Spec:** A4, A5, A6, A7, C1, C2, C4
- **O quê:** estender o registro no plan e os motores para distinguir implementação, testes e prova final, preservando leitura de plans antigos e comportamento do Modo B. Alinhar prompts, regras, templates e distribuição à mudança de contrato.
- **Aceite:**
  - [x] Definir primeiro em `ARQUITETURA.md` o marcador explícito do novo protocolo no plan, campos por tarefa, estados de execução e precedência de etapas. Ausência de marcador mantém o protocolo antigo; modo escolhido precisa distinguir A de B sem inferência por número de tasks. Nenhum novo arquivo de estado.
  - [x] As dependências do novo Modo A liberam implementação após código integrado e checagem local válida, mantendo `[ ] Tn concluída` até a prova integrada. Campos incompletos, inválidos, ciclos e dependências inexistentes não geram conclusão implícita.
  - [x] Implementador faz código e checagens rápidas; depois complementa testes a partir do aceite e das provas existentes. Verificador executa integração sem editar testes. Corretor recebe falhas pré-review com evidência, sem inventar R*.
  - [x] O coordenador confere relatórios e disco, reutiliza agentes em tarefas relacionadas quando útil, mantém escrita sequencial e review independente. Relatório distingue etapa implementada de entrega comprovada; `verde` local não autoriza conclusão global.
  - [x] Retomada compara snapshot e inputs das provas; alterações invalidam somente evidências afetadas. Falha ou interrupção na criação de testes, execução, correção e commit mantém próximo passo correto, sem reimplementar código válido.
  - [x] Prova integrada verde permite concluir somente T* comprovadas e criar um commit integrado identificando todos os IDs. Regras de staging explícito, preservação de alterações alheias e confirmação final de push permanecem. Correções de review mantêm as duas rodadas atuais.
  - [x] Modo B e plans históricos mantêm o ciclo anterior; o motor não reabre tasks já concluídas. Adaptar o piloto existente para verificar o novo modo e a compatibilidade.
  - [x] Atualizar versão de contrato de 4.0.0 para 5.0.0 nos manifestos que possuem versão e no contrato de distribuição, sem acrescentar campo incompatível a manifesto que não o admite. Atualizar README e regras operacionais afetadas; preservar artefatos históricos.
- **Verificação:**
  - [x] `python docs/vibe-implement/tests/test-implement.py`
  - [x] `python docs/vibe-plan/tests/test-plan.py`
  - [x] `python docs/vibe-implement/tests/piloto-modo-a.py --prepare-only`
  - [x] `& 'C:/Program Files/Git/bin/bash.exe' docs/vibe-implement/tests/test-implement.sh`
  - [x] Avaliação comportamental com subagente e fixture descartável: implementação de tasks dependentes, complemento de testes, falha real, correção, retomada e commit integrado. Inspecionar efeitos no disco, comandos e histórico Git; a preparação de fixture sozinha não satisfaz C2.
- **Deps:** T1
- **Arquivos:** `docs/vibe-implement/ARQUITETURA.md`, `docs/vibe-implement/ANALISE.md`, `vibe-implement/SKILL.md`, `vibe-implement/scripts/implement.py`, `vibe-implement/scripts/implement.ps1`, `vibe-implement/references/delegation.md`, sua cópia idêntica em `vibe-plan/references/delegation.md`, `vibe-plan/SKILL.md`, `vibe-plan/templates/plan.md`, `docs/vibe-plan/ARQUITETURA.md`, `docs/vibe-plan/ANALISE.md`, `docs/vibe-implement/tests/test-implement.py`, `docs/vibe-implement/tests/piloto-modo-a.py`, perfis da T1 quando necessário, `AGENTS.md`, `vibe-init/templates/AGENTS.md`, `README.md`, `.codex-plugin/plugin.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, `.grok-plugin/marketplace.json`, `docs/tests/test-distribuicao.py`.
- **Risco:** mudança na interpretação da fila e dos checkpoints. O novo contrato deve ser selecionado explicitamente para não reinterpretar uma execução antiga. A alteração das regras operacionais faz parte da implementação autorizada; eventual tabela de decisões vigentes só é sincronizada no fechamento humano.

- **Avaliação comportamental T2 (2026-10-10):** fixture isolada `.vibe-stage-behavior/etapas/work`, baseline `9cab7391f3900b25923cd7635efb01f8dda91de7`. Coordenador `piloto_etapas`, implementador `codigo`, retomada de contexto limpo `retomada`, verificador `validacao` e corretor `correcao` em sequência. Etapas observadas: implementar T1 → implementar T2 → testar → validar → corrigir_validacao → validar → commitar_integracao → revisar. T1 e T2 permaneceram `[ ]` durante código/testes e dependência T2 liberou após checagem local válida de T1.
- **Evidência da avaliação T2:** complemento preservou `test_existing.py` e criou `test_textkit.py` por aceite. Primeira checagem direcionada do implementador apresentou três subcasos vermelhos; primeira integração do verificador `python -B -m unittest discover -s tests -v` executou 4 testes e confirmou três subfalhas de normalização em A2. A execução vermelha foi repetida uma vez para captura UTF-8, sem mudança de inputs. Corretor alterou somente `textkit/shared.py`; snapshots que incluíam esse input foram invalidados e renovados após checagens direcionadas, preservando módulos e testes. Nova integração separada pelo verificador: exit 0, 4 testes OK.
- **Git da avaliação T2:** commit único `a3eb164aa9afcb0336fb71978bb9e015a55af7a3`, `task(T1,T2): normaliza e resume texto com whitespace Unicode`; paths: helper compartilhado, stats/report, teste de jornada e plan/spec da fixture. Nenhum commit por task intermediária, nenhum push. Git limpo; motor da cópia e canônico reconheceram etapa revisar, locais/prova válidos e commit_encontrado real, com avisos vazios. Avaliação certifica o comportamento de implementação/testes/validação/correção/retomada, sem substituir a review final da phase.
- **Prova final T2:** implement: 40 testes OK (91,425 s); bordas posteriores StageProtocolContracts: 4 OK (67,263 s); origem/commit retry/types: 2 OK (46,512 s), comprovando commit integrado único mais task(R1). Plan: 16 testes OK (3,910 s). Piloto prepare-only: 7 PASS, execução final 9,017 s sem modelos. Launcher Git Bash: 8 PASS/0 FAIL. Diff check verde; delegation idênticas por bytes; fixtures das suítes e avaliação removidas. Temp falhado por restrição sandbox foi removido e ausência confirmada.
- **Resultado T2:** protocolo etapas-v1 explícito, snapshots e retomada verificáveis, etapas separadas e origem preservada nas correções. Modo B/legado preservados. Versão pública 5.0.0. Patch operacional AGENTS aplicado pelo coordenador, sem tabela de decisões vigentes. Provas compartilhadas ficam T3.

### T3: Bloquear a review quando a solicitação estiver incompleta

- [x] T3 concluída
- **Spec:** A8, C3, C4; integração de A1 a A7
- **O quê:** tornar obrigatória na review final a matriz solicitação → implementação → evidência → situação, cruzando a origem antes de olhar apenas para as tasks. Alinhar fechamento e rastreabilidade ao commit integrado do Modo A.
- **Aceite:**
  - [x] Review parte do pedido original, mudanças autorizadas, interview disponível, spec e plan. Item omitido no plan continua sendo obrigação se não houve retirada humana.
  - [x] Matriz no review.md classifica atendido, parcial, ausente ou retirado explicitamente pelo humano; retirada cita a decisão. Item obrigatório parcial/ausente abre R* bloqueante e impede Approve, inclusive com testes verdes.
  - [x] Falta de contexto de origem é relatada como limitação, sem certificação falsa de completude. Review de checkpoint não certifica a entrega inteira.
  - [x] Revisor mantém contexto limpo e não corrige código nem opera Git. Evidências válidas da integração são reaproveitadas; lacunas exigem a menor prova suficiente.
  - [x] Fechamento reconhece commits integrados e commits históricos por task, sem depender exclusivamente de `task(Tn)`. A confirmação humana única e a limitação de duas rodadas continuam coerentes com T2.
  - [x] Avaliação independente usa solicitação com duas capacidades, plan omitindo uma delas e código/testes corretos para a outra. O revisor deve identificar a omissão, registrar evidência e bloquear aprovação. Segundo cenário contém retirada autorizada e não deve criar falso bloqueio.
  - [x] Integração final mantém distribuição, paridade de motores, fluxo MVP e proteção de caminhos. Nenhum teste de documentação por busca de palavras é introduzido.
- **Verificação:**
  - [x] `python docs/vibe-review/tests/test-review.py`
  - [x] `python docs/tests/test-distribuicao.py`
  - [x] `python docs/tests/test-mvp-flow.py`
  - [x] `python docs/tests/test-reparse-safety.py`
  - [x] `gitleaks dir . --redact --no-banner`
  - [x] `git diff --check`
  - [x] Avaliação comportamental com revisor independente em fixture temporária; registrar achado, situação dos dois cenários e provas nos resultados desta T*. Não confundir a suíte do motor review com prova da decisão semântica do revisor.
- **Deps:** T2
- **Arquivos:** `vibe-review/SKILL.md`, `vibe-review/templates/review.md`, `docs/vibe-review/ARQUITETURA.md`, `docs/vibe-review/ANALISE.md`, `docs/vibe-review/tests/test-review.py` somente se houver contrato executável alterado, `docs/vibe-implement/tests/piloto-modo-a.py` para fixtures comportamentais reutilizáveis, perfis `revisor` distribuídos em T1 e referências de delegação se o relatório precisar refletir a matriz.
- **Risco:** inferir completude a partir do diff ou de um plan incompleto. O pedido de avaliação não deve revelar o requisito plantado nem a resposta esperada ao revisor. Todo workspace temporário precisa ser removido após coleta da evidência, com falha de limpeza explícita.

- **Avaliação comportamental T3 (2026-10-10):** revisores independentes `avaliacao_review_a` e `avaliacao_review_b`, contexto limpo, prompts neutros iguais e cópias isoladas da skill/motor. Ambos receberam somente paths, diff baseline..HEAD e pedido de review contra solicitação/artefatos. Escreveram somente review.md. Código word_count com três testes reais verdes; pedido original tinha também slugify, ausente no plan/código.
- **Cenário A T3:** baseline `c4113d31a5bcb95dbc62ed0f1c0f450d6c389b42`, HEAD `59603c6a7e4435b208793ba4a9616ea1633c1fd0`. Review registrou matriz word_count atendido e slugify ausente, sem retirada humana; abriu R1 Required por falta da solicitação e emitiu Request changes apesar dos três testes verdes e bordas verdes. Abriu também R2 por CRLF do patch da fixture. Esta segunda constatação é separada da prova semântica de omissão.
- **Cenário B T3:** baseline `ed700826381e88e623ea01da559d36f14b52a86c`, HEAD `ba2a1ffb8e374f2e68a2cb25e7b6fd56b313843a`. Review registrou slugify retirado explicitamente pelo humano, citando alteração autorizada em interview.md; três testes e assertions de vazio literal/NBSP/EM SPACE verdes. Approve final proposto, nenhum R*. Revisor distinguiu CRLF por `git -c core.whitespace=cr-at-eol diff --check`, exit 0, sem editar configuração.
- **Conferência T3:** coordenador leu matrizes/vereditos e status Git dos dois cenários; somente review.md não rastreado em cada fixture. Gerador canônico corrigido para escrever código/testes com LF e validar diff indexado antes de criar commit. Não houve retirada inferida, teste de palavras em documentação ou correção de código pelo revisor. Alteração de newline não muda a prova semântica coletada. Limpeza das fixtures após coleta foi obrigatória; preflight do gerador corrigido e provas finais registrados abaixo.
- **Prova final T3:** review 19 testes OK (6,415 s), distribuição 9 OK (0,016 s fora do Temp virtualizado), MVP 1 OK (0,625 s), reparse 12 OK (33,901 s). Gitleaks exit 0 sem vazamentos (1,68 MB). Diff check verde, delegation idênticas. Preflight LF corrigido: 2 fixtures, 3 testes por fixture e diff baseline..HEAD verde, exit 0 em aproximadamente 2,62 s. Fixtures de review, preflight e as duas Temp de distribuição foram removidas, ausência conferida.
- **Resultado T3:** matriz obrigatória e veredito técnico/completude cobrem a origem antes do plan; omissão bloqueia e retirada humana explícita não gera escopo inventado. Não houve alteração de motor review nem testes de documentação. Erro preexistente externo: limpeza silenciosa em tearDown review, registrado em .erros-encontrados/2026-10-10-review-testes-ignoram-falha-de-limpeza.md pelo coordenador, sem ampliar patch.

## Handoff

`vibe-implement`, rota high. Sem analyze obrigatório e sem design aplicável. As dependências e os arquivos compartilhados pedem execução sequencial; nenhum grupo paralelo seguro foi proposto. Não há checkpoint intermediário de review necessário; a review final é delegada pelo coordenador depois das entregas, não uma T* adicional.

Recomenda-se fortemente um chat novo com `/vibe-implement` e este plan. Com subagentes, o coordenador executa a fila inteira em Modo A, incluindo review e correções, até a confirmação humana final. Permanecer neste chat é válido se Marco preferir. Não iniciar implementação antes de aprovação do plan ou pedido explícito da próxima porta.

## Correções adicionais autorizadas

Pedido humano de 2026-10-10 inclui review e registros vigentes. R2/R3 corrigidos por causa raiz nas nove suítes afetadas. Provas: review 19, distribuição 9, spec 19, design 19, plan 16, analyze 16, interview 19, MVP 1 e reparse 12 testes OK; falhas simuladas propagam e reparse tenta ambas as remoções. Fixtures ausentes e diff check verde. Código, registros e artefatos serão enviados em commit task(R2,R3), sem push. R4/R5/R6 seguem em correção sequencial e exigem nova review.

## Prova adicional R4

R4 resolvido: oito pares de motores emitem stdout/stderr UTF-8 sem BOM; consumidores decodificam explicitamente e avisos de implement são comparados integralmente. Prova rawbytes: 2 testes, 32 execuções reais com locale legado forçado, caminhos Unicode, avisos e erros. Init 12, implement 40, interview 19, spec 19, design 19, plan 16, analyze 16, review 19, reparse 12 e MVP 1 testes OK; launcher implement 8 PASS. Fixtures removidas, diff check verde. Adaptações dos consumidores de oito suítes entraram antecipadamente no commit e2d808d por concorrência de edição/indexação; a prova verde corresponde ao conjunto completo R2/R3/R4, sem atribuir independência ao commit intermediário.
