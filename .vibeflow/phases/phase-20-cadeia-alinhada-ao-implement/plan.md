# Plan: Cadeia alinhada ao implement
# Alvo: phase-20-cadeia-alinhada-ao-implement
# Status: aprovado
# Spec: spec.md (mesma pasta)
# Protocolo: coordenacao-v1
# Modo: A
<!-- Na abertura da implement, finalizador registra # Modo: A ou B. Preserve protocolos históricos. -->

## Overview

Entrega a spec da mesma pasta: init, spec, design, plan e analyze passam a preparar o que o coordenador do `vibe-implement` em `coordenacao-v1` Modo A precisa para despachar ondas, a implement confere a capacidade de delegação antes da primeira onda e a review audita o que foi executado. Nenhum motor muda nesta phase; a cadeia se adapta ao parser de `Arquivos:` e ao `execution.json` atuais (decisão 5 e Fora da spec). O repo fecha em 9.0.0.
- **Design:** N/A, sem UI visível.

## Prontidão das provas

- Python 3.12 (`py -3`): local · ok. Localmente `python3` é o alias da Microsoft Store e não executa; todo comando local usa `py -3`.
- PowerShell 7.6 (`pwsh`): local · ok.
- `gitleaks` 8.30.1: local · ok.
- `bash` 5.3 (Git Bash): local · ok. Os launchers `.sh` procuram `python3`, que localmente é o alias da Store; falha de launcher causada por esse alias fica como limitação registrada deste host, sem certificação (decisão 18).
- Privilégio de symlink no Windows: host · pergunta ao humano. Ausente no host local (WinError 1314, `core.symlinks=false`, `skills/vibe-*` em checkout como texto). Recomendação: habilitar o Modo de Desenvolvedor do Windows. Até lá, falhas locais esperadas: `test_skills_pointers` e `test_unique_names_under_skills` em `docs/tests/test-distribuicao.py` e os casos de alias por symlink das suítes que os têm (registro em `.erros-encontrados/2026-10-13-test-implement-symlink-sem-privilegio-windows.md`). Sem CI no GitHub (decisão 18), esses casos ficam como limitação registrada, sem certificação; qualquer outra falha local é falha real.
- MCP `chrome-devtools` ou Playwright: host · ok (N/A, nenhuma T* altera UI nem exige `Visual: necessária`).
- Perfis de subagente do Modo A: host · ok. Explorador, implementador, redator, verificador, corretor e revisor existem nos perfis pessoais do Claude (`~/.claude/agents/`) e estão carregados nesta sessão. Redator é exigido porque T1 a T7 e T9 são de prosa.
- Finalizador: host · ok, agente genérico (`general-purpose`) apto a Git.
- `docs/tests/test-visual-contract.py`, citado em `AGENTS.md` e no C1 da spec, não existe no disco (removido em `59db016` como teste textual); C1 é atendido pelas suítes existentes e T9 corrige a citação em `AGENTS.md`.

Comando compartilhado `distribuicao`: `py -3 docs/tests/test-distribuicao.py -v`. Localmente passa com as duas falhas de symlink esperadas acima; o caso das cópias de `delegation.md` precisa passar.

### Regressão completa

Executada somente pela review final, uma vez, no estado integrado. É local, sem CI no GitHub (decisão 18):

- `py -3 docs/vibe-<skill>/tests/test-<skill>.py -v` para init, interview, spec, design, plan, analyze, implement e review.
- `py -3 docs/vibe-implement/tests/test-execution.py -v` (suíte do registro de execução).
- `py -3 docs/tests/test-distribuicao.py -v`, `py -3 docs/tests/test-mvp-flow.py -v`, `py -3 docs/tests/test-reparse-safety.py -v`, `py -3 docs/tests/test-runtime-discovery.py -v` e `py -3 docs/tests/test-stream-encoding.py -v`.
- `pwsh -NoProfile -File docs/vibe-init/tests/test-init.ps1` (paridade essencial do init).
- `bash docs/vibe-<skill>/tests/test-<skill>.sh` para as oito skills (launchers; falha causada pelo alias `python3` da Store é limitação registrada da prontidão).
- `gitleaks detect --source . --redact --no-banner`.
- Casos de symlink: as falhas locais listadas na prontidão ficam como limitação registrada deste host até o Modo de Desenvolvedor ser habilitado; não há certificação externa.
- Excluído: `docs/vibe-implement/tests/piloto-modo-a.py`, porque não é determinístico e consome tokens da conta.

## Tasks

### T1: Init gera regras e perfis prontos para as ondas
- [ ] T1 concluída
- **Spec:** A1, A2, A3, A4, A5
- **Deps:** nenhuma
- **O quê:** Resultado principal: prosa (redator). O template de `AGENTS.md` gerado proíbe corrigir erro fora do recorte e manda registrar em `.erros-encontrados/` e reportar ao coordenador ou ao humano (decisão 4); o SLOT de comandos pede comando por recorte, suíte completa, E2E, varredura de segredos, CI obrigatório e onde cada um roda, quando existirem; a regra de testes própria do VibeFlow sai do template e as regras Git ficam em frases curtas. Os perfis Claude e Codex descrevem implementador, verificador, revisor e redator conforme o F1 passo 3, e o parágrafo comum lista os oito campos do relatório fixo atual. No re-init, a `vibe-init/SKILL.md` orienta a IA a tratar cada perfil com status `conflito`: comparar por diff com o template e pelo histórico Git do path no projeto; perfil VibeFlow desatualizado (sem conteúdo do usuário) é copiado para `.vibeflow/old/` com tamanho e hash conferidos e só então substituído; customização ou dúvida é preservada e reportada; e a skill propõe patch da seção Git do `AGENTS.md`. O motor do init não muda: segue reportando `conflito` sem substituir. `docs/vibe-init/ARQUITETURA.md` registra esse fluxo e a justificativa dos esforços por host (decisão 11); `ANALISE.md` acompanha.
- **Aceite:** init em pasta isolada instala os doze perfis com os bytes dos templates novos e preserva o perfil conflitante; template, perfis e SKILL coerentes com A1 a A5.
- **Arquivos:** `vibe-init/SKILL.md`, `vibe-init/templates/AGENTS.md`, `vibe-init/templates/agents/claude/`, `vibe-init/templates/agents/codex/`, `docs/vibe-init/ARQUITETURA.md`, `docs/vibe-init/ANALISE.md`
- **Prova afetada:** `py -3 docs/vibe-init/tests/test-init.py -v`; `pwsh -NoProfile -File docs/vibe-init/tests/test-init.ps1`
- **Risco:** a substituição do perfil desatualizado é passo da IA guiado pela SKILL, sem prova de motor; a review julga a instrução, e ambiguidade cai sempre em preservar e reportar.

### T2: Spec liga cada aceite à jornada e ao nível
- [ ] T2 concluída
- **Spec:** A6, C3
- **Deps:** nenhuma
- **O quê:** Resultado principal: prosa (redator). Como provar da spec liga cada A* ao F* ou jornada que o exerce e ao nível (`jornada` ou `local`), sem comando, path de teste nem ferramenta; a direção visual descreve evidência renderizada observável e deixa a ferramenta para o plan; a spec pode registrar F* consumidores de contrato compartilhado. `docs/vibe-spec/` deixa de citar `REGRAS.md` como fonte viva e o diagrama da `ANALISE.md` inclui o ramo design.
- **Aceite:** SKILL, template, referência e docs da spec coerentes com F2 e com a parte da spec em C3.
- **Arquivos:** `vibe-spec/SKILL.md`, `vibe-spec/templates/spec.md`, `vibe-spec/references/ui-visual-direction.md`, `docs/vibe-spec/ARQUITETURA.md`, `docs/vibe-spec/ANALISE.md`
- **Prova afetada:** `py -3 docs/vibe-spec/tests/test-spec.py -v`

### T3: Design entrega insumo de prova visual ao plan
- [ ] T3 concluída
- **Spec:** A7, C3
- **Deps:** nenhuma
- **O quê:** Resultado principal: prosa (redator). O design deixa de prometer commit por task (o commit segue o protocolo do plan); registra a prova visual por tela em uma única casa como insumo do `Visual:` e da `Prova afetada:` da T* que toca a tela; acrescenta Superfícies compartilhadas (telas afetadas por componente ou token comum, reconferidas na review); declara a viewport de julgamento do aceite, com viewport estreita só quando houver regra responsiva; e sinaliza que kit, tokens e componentes comuns precedem as telas. `docs/vibe-design/` deixa de citar `REGRAS.md` como fonte viva.
- **Aceite:** SKILL, template, referência e docs do design coerentes com F3 e com a parte do design em C3.
- **Arquivos:** `vibe-design/SKILL.md`, `vibe-design/templates/design.md`, `vibe-design/references/kit-e-tokens.md`, `docs/vibe-design/ARQUITETURA.md`, `docs/vibe-design/ANALISE.md`
- **Prova afetada:** `py -3 docs/vibe-design/tests/test-design.py -v`

### T4: Plan entrega fila executável em ondas
- [ ] T4 concluída
- **Spec:** A8, A9, A10, A11, A12
- **Deps:** nenhuma
- **O quê:** Resultado principal: prosa (redator). O plan declara o formato literal de `Arquivos:` lido pelo motor da implement (uma linha física `- **Arquivos:**`, cada path entre crases, nada relevante fora delas), avisa path incomparável e recomenda renomear ou isolar; o placeholder do template passa a ser comparável. A prontidão técnica ganha a forma de uma linha por requisito com local (local, CI ou host) e destino (`ok`, `ação em Tn`, `pergunta ao humano`, `bloqueio`), cobrindo ferramentas, perfis do Modo A, privilégios do SO e ferramentas da prova visual, com os destinos da decisão 8; requisito sem destino impede o plan de se declarar pronto; o handoff anuncia Modo B quando o host não tem subagentes. Arquivo compartilhado entre T* sem `Deps` vai para T* final com `Deps`, e prosa se separa de código para o redator, ou a T* mista marca o resultado principal. `Prova afetada:` reúne comandos e evidência visual declarada; em T* só de prosa usa a suíte do consumidor contratual ou checagem mecânica, nunca teste de presença de palavras. No Modo A o plan não promete checkpoint de review (decisão 10). `docs/vibe-plan/` descreve o parser que lê `Arquivos:` sem vocabulário obsoleto.
- **Aceite:** SKILL, template e docs do plan coerentes com F4; o placeholder de `Arquivos:` do template produz paths comparáveis no parser do motor da implement.
- **Arquivos:** `vibe-plan/SKILL.md`, `vibe-plan/templates/plan.md`, `docs/vibe-plan/ARQUITETURA.md`, `docs/vibe-plan/ANALISE.md`
- **Prova afetada:** `py -3 docs/vibe-plan/tests/test-plan.py -v`; checagem mecânica do placeholder: `py -3 -c "import sys; sys.path.insert(0, 'vibe-implement/scripts'); import implement as m; t = open('vibe-plan/templates/plan.md', encoding='utf-8').read(); v = [x.group(1) for x in map(m.ARQUIVOS_LINE_RE.match, t.splitlines()) if x]; assert len(v) == 1 and m.parse_arquivos_value(v[0]), v; print('ok', m.parse_arquivos_value(v[0]))"` (falha no template atual, passa depois de T4)

### T5: Analyze confere o contrato da implement
- [ ] T5 concluída
- **Spec:** A13, A14, C3
- **Deps:** nenhuma
- **O quê:** Resultado principal: prosa (redator). Sem mudar o motor, a IA do analyze passa a conferir `# Protocolo: coordenacao-v1`, `Arquivos:` válido em toda T* (uma linha, crases, comparável), sobreposição de `Arquivos:` entre T* sem `Deps`, `Prova afetada:` executável restrita ao recorte e cobrindo os A*/C* da T*, `Regressão completa` única com comandos reais e a prontidão técnica. A dimensão nova de cobertura em `references/coverage.md` traz as gravidades da F5 (HIGH: regressão ausente, `Prova afetada:` ausente ou com suíte inteira, sobreposição sem `Deps` cuja ordem importa, requisito sem destino, perfil não verificado com Modo A prometido; MEDIUM: T* sem `Arquivos:` ou com path incomparável). Correção direta nunca grava a suíte inteira como `Prova afetada:`. Sai "provas proporcionais"; a contagem de passes fica correta; `design.md` entra na tabela de fontes; `docs/vibe-analyze/` deixa de citar `REGRAS.md` como fonte viva.
- **Aceite:** SKILL, template, `coverage.md` e docs do analyze coerentes com F5 e com a parte do analyze em C3.
- **Arquivos:** `vibe-analyze/SKILL.md`, `vibe-analyze/templates/analyze.md`, `vibe-analyze/references/coverage.md`, `docs/vibe-analyze/ARQUITETURA.md`, `docs/vibe-analyze/ANALISE.md`
- **Prova afetada:** `py -3 docs/vibe-analyze/tests/test-analyze.py -v`

### T6: Implement confere a capacidade antes de despachar
- [ ] T6 concluída
- **Spec:** A15, C1
- **Deps:** nenhuma
- **O quê:** Resultado principal: prosa (redator). No `coordenacao-v1` Modo A, antes da primeira onda, o coordenador confere a capacidade de delegação registrada na prontidão do plan ou a verifica no host; perfil exigido ausente ou não carregado vira pergunta ao humano com a recomendação da decisão 8, e nenhuma onda é despachada sem ele. R* com `papel: redator` vai ao redator; os demais, ao corretor (decisão 9). As duas cópias de `delegation.md` recebem o mesmo texto, e os docs da implement registram o fluxo. Modo B e protocolos históricos ficam inalterados.
- **Aceite:** SKILL, `delegation.md` e docs coerentes com F6; cópias de `delegation.md` idênticas em bytes.
- **Arquivos:** `vibe-implement/SKILL.md`, `vibe-implement/references/delegation.md`, `vibe-plan/references/delegation.md`, `docs/vibe-implement/ARQUITETURA.md`, `docs/vibe-implement/ANALISE.md`
- **Prova afetada:** `distribuicao` (definido na prontidão); `py -3 docs/vibe-implement/tests/test-implement.py -v` (com as falhas de symlink esperadas da prontidão)

### T7: Review audita o que o implement executou
- [ ] T7 concluída
- **Spec:** A16, A17, A18, A19, A20
- **Deps:** nenhuma
- **O quê:** Resultado principal: prosa (redator). No Modo A, o revisor lê o estado pelo comando de leitura do motor da implement; confere que os inputs de cada T* em `execution.json` estão dentro do seu `Arquivos:`, que o diff da phase está dentro da união dos `Arquivos:` (fora abre R* Required) e que consumidor compartilhado entre T* da mesma onda continua coerente; liga cada A* à `Prova afetada:` registrada ou à regressão; executa a regressão completa e relata comando, resultado e HEAD; árvore suja pede isolamento ao coordenador. Na re-review, confere `correcao.commit` não nulo, descendente e com IDs iguais aos R* marcados, reaproveita a prova afetada certificada e repete a regressão só se código ou teste mudou. Cada R* traz `papel: corretor | redator`. A finalização não exige nova regressão quando o diff de `AGENTS.md` se limita a `## Decisões vigentes` (decisão 6). No Modo A não há checkpoint; no modo subagente, defeito do motor encontrado no §0 vira bloqueio ou R*, nunca correção pelo revisor. SKILL, template, ARQUITETURA e ANALISE qualificados por protocolo (`execution.json` no Modo A, plan nos históricos, que conservam checkpoint).
- **Aceite:** SKILL, template e docs da review coerentes com F7 e com C4.
- **Arquivos:** `vibe-review/SKILL.md`, `vibe-review/templates/review.md`, `docs/vibe-review/ARQUITETURA.md`, `docs/vibe-review/ANALISE.md`
- **Prova afetada:** `py -3 docs/vibe-review/tests/test-review.py -v`

### T8: Versão 9.0.0 nos manifestos
- [ ] T8 concluída
- **Spec:** C2
- **Deps:** nenhuma
- **O quê:** Resultado principal: código e teste (implementador). Os cinco manifestos versionáveis e `CONTRACT_VERSION` do teste de distribuição passam a `9.0.0` (decisão 12). O `plugin.json` da raiz não tem campo de versão e fica fora.
- **Aceite:** os cinco manifestos e a constante do teste em `9.0.0`; teste de versão verde.
- **Arquivos:** `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `.grok-plugin/marketplace.json`, `docs/tests/test-distribuicao.py`
- **Prova afetada:** `distribuicao` (definido na prontidão)

### T9: Fontes transversais refletem a 9.0.0
- [ ] T9 concluída
- **Spec:** C1, C2, C4, C5
- **Deps:** T1, T2, T3, T4, T5, T6, T7
- **O quê:** Resultado principal: prosa (redator). `README.md` registra a versão `9.0.0` e o que muda na cadeia; `docs/ESCOPO.md` marca o que esta phase entregou; `AGENTS.md` do repo alinha o texto que já descreve as regras alteradas (erro fora do recorte, Modo A sem checkpoint de review, prontidão com destino) e deixa de citar `docs/tests/test-visual-contract.py`, que não existe. Protocolos históricos e Modo B descritos sem migração. Remove o workflow do GitHub Actions (`.github/workflows/contrato.yml`); `AGENTS.md` registra que o repo não usa CI no GitHub, com regressão completa e gitleaks locais e a limitação dos testes de symlink neste host (decisão 18).
- **Aceite:** README, ESCOPO e `AGENTS.md` coerentes com o contrato entregue por T1 a T7 e com a versão de T8; `AGENTS.md` não cita suíte inexistente.
- **Arquivos:** `AGENTS.md`, `README.md`, `docs/ESCOPO.md`, `.github/workflows/contrato.yml`
- **Prova afetada:** `distribuicao` (definido na prontidão); checagem: `.github/workflows/contrato.yml` inexistente

## Colaboração

- Ondas: onda 1 com T1, T2, T3, T4, T5, T6, T7 e T8 (`Arquivos:` disjuntos, sem `Deps`); onda 2 com T9, que incorporou a remoção do CI do GitHub (decisão 18). O motor da implement recalcula.
- Benefício: oito resultados independentes em paralelo; o texto transversal só é escrito depois que o contrato de cada skill existe.
- Ownership: a fonte comum do vocabulário novo (formato de `Arquivos:`, linha de prontidão, destinos, `papel` no R*, ausência de checkpoint no Modo A) é a spec, decisões 5 a 10; cada redator a lê e não edita arquivo de outra T*. O relatório fixo de oito campos de `delegation.md` não muda nesta phase, e T1 alinha os perfis a ele. Em `.erros-encontrados/`, cada agente só cria arquivo novo por erro, sem editar os existentes. T6 roda `distribuicao` enquanto T8 troca a versão; divergência transitória de versão nessa janela não é falha de T6, e a integração reroda a prova.

## Handoff

vibe-implement, em chat novo, Modo A: o coordenador conduz as duas ondas, a review delegada e as correções e só volta ao humano na confirmação final para push. Rota high, sem analyze. Continuar neste chat é válido se o humano preferir.

- [x] Aprovação humana: autorização de 2026-10-14 ("pode abrir a fase 20"), dada em resposta à proposta de abrir esta phase e seguir até a review sem novas paradas, exceto a confirmação final para push; registrada pelo coordenador ao delegar este plan.
