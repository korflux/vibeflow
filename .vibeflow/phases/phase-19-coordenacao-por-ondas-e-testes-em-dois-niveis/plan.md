# Plan: Coordenação por ondas e testes em dois níveis
# Alvo: phase-19-coordenacao-por-ondas-e-testes-em-dois-niveis
# Status: aprovado
# Spec: spec.md (mesma pasta)
# Protocolo: coordenacao-v1
# Modo: A

## Overview

Entrega a spec da mesma pasta: o motor da vibe-implement passa a relatar a onda paralela em `coordenacao-v1` Modo A, as skills plan, implement e review passam a operar ondas e testes em dois níveis, e o repo fecha com versão major.
- **Design:** N/A, sem UI visível.

## Prontidão das provas

- Python 3.12 local em `py -3` (o alias `python3` desta máquina aponta para a Microsoft Store); no CI, `python` 3.12 do workflow `contrato.yml`.
- PowerShell 7.6 local em `pwsh` (instalado nesta phase via winget); a suíte de paridade do motor implement depende dele. No CI, `pwsh` do runner.
- `gitleaks` 8.x local (winget) e no CI.
- Este plan já usa o formato que a phase introduz: `Arquivos:` e `Prova afetada:` por T* e uma única regressão completa abaixo.

### Regressão completa

Executada pela review final, uma vez, no estado integrado. Espelha o CI `contrato.yml`:

- `py -3 docs/vibe-<skill>/tests/test-<skill>.py -v` para init, interview, spec, design, plan, analyze, implement e review.
- `py -3 docs/tests/test-distribuicao.py -v`, `test-mvp-flow.py`, `test-reparse-safety.py`, `test-runtime-discovery.py`, `test-stream-encoding.py`.
- `pwsh ./docs/vibe-init/tests/test-init.ps1`.
- `bash docs/vibe-<skill>/tests/test-<skill>.sh` para as oito skills.
- `gitleaks detect --source . --redact --no-banner`.
- E2E: `docs/vibe-implement/tests/piloto-modo-a.py` fica fora; não é determinístico, consome tokens da conta e não está no CI.

## Tasks

### T1: Motor relata a onda paralela
- [ ] T1 concluída
- **Spec:** A1, A6
- **Deps:** nenhuma
- **O quê:** `implement.py` e `implement.ps1` leem `Arquivos:` de cada T* e, somente em `coordenacao-v1` Modo A, acrescentam `fila.onda` (elegíveis em ordem numérica com arquivos disjuntos, guloso) e `fila.sem_arquivos`. Sobreposição: path igual ou prefixo de diretório, sem diferenciar maiúsculas, com `\` normalizado para `/`, `./` inicial removido e curinga reduzido ao prefixo até o primeiro curinga. T* sem `Arquivos:` só entra em onda vazia e a encerra. `ARQUITETURA.md` da implement documenta os campos; path incomparável (não ASCII, absoluto, com `:`, `<`, `>`, `"`, `|` ou segmento terminado em `.` ou espaço) torna a T* inteira sem arquivos comparáveis, que roda sozinha e entra em `fila.sem_arquivos`; normalização léxica (`.`, `..`, `//`) e fins de linha normalizados para `\n` na leitura nos dois motores (inclusive `execution.ps1`).
- **Aceite:** fixture com T* disjuntas, sobrepostas, por prefixo de diretório, por curinga e sem `Arquivos:` produz a onda esperada nos dois motores; Modo B e `etapas-v1` não trazem `onda`.
- **Arquivos:** `vibe-implement/scripts/implement.py`, `vibe-implement/scripts/implement.ps1`, `docs/vibe-implement/tests/test-implement.py`, `docs/vibe-implement/ARQUITETURA.md`, `vibe-implement/scripts/execution.ps1`
- **Prova afetada:** `py -3 docs/vibe-implement/tests/test-implement.py -v` (inclui paridade PowerShell)
- **Estado:** integrada; commit task(T1,T2,T3,T4,T5,T6).

### T2: Plan exige arquivos, prova afetada e regressão completa
- [ ] T2 concluída
- **Spec:** A3
- **Deps:** nenhuma
- **O quê:** `vibe-plan/SKILL.md` e `templates/plan.md` exigem em plan novo `Arquivos:` e `Prova afetada:` por T* e uma seção `Regressão completa` única; removem a orientação de `Arquivos` opcional e de verificação proporcional com válvulas; a seção Colaboração passa a descrever ondas por disjunção de arquivos no Modo A. `docs/vibe-plan/ARQUITETURA.md` e `ANALISE.md` refletem o contrato.
- **Aceite:** template e SKILL coerentes com a spec; suíte do plan verde.
- **Arquivos:** `vibe-plan/SKILL.md`, `vibe-plan/templates/plan.md`, `docs/vibe-plan/ARQUITETURA.md`, `docs/vibe-plan/ANALISE.md`
- **Prova afetada:** `py -3 docs/vibe-plan/tests/test-plan.py -v`
- **Estado:** integrada; commit task(T1,T2,T3,T4,T5,T6).

### T3: Implement coordena ondas e prova só o afetado
- [ ] T3 concluída
- **Spec:** A2, A4
- **Deps:** nenhuma
- **O quê:** `vibe-implement/SKILL.md` §2 e §3 passam a: despachar `fila.onda` inteira numa rodada, encadear explorador (próxima onda), verificador e corretor por T*, registrar a onda em um único handoff do finalizador, serializar T* sem `Arquivos:` ou com expansão de path; implementador e verificador executam somente `Prova afetada:` e a integração usa a união delas, sem válvulas de ampliação. `references/delegation.md` (cópia idêntica em `vibe-plan/references/`) e `references/definition-of-done.md` acompanham. `docs/vibe-implement/ANALISE.md` registra o fluxo.
- **Aceite:** SKILL e referências coerentes com F2 e F3; cópias de `delegation.md` idênticas; suíte de distribuição verde.
- **Arquivos:** `vibe-implement/SKILL.md`, `vibe-implement/references/delegation.md`, `vibe-plan/references/delegation.md`, `vibe-implement/references/definition-of-done.md`, `docs/vibe-implement/ANALISE.md`
- **Prova afetada:** `py -3 docs/tests/test-distribuicao.py -v`
- **Estado:** integrada; commit task(T1,T2,T3,T4,T5,T6).

### T4: Review executa a regressão completa
- [ ] T4 concluída
- **Spec:** A5
- **Deps:** nenhuma
- **O quê:** `vibe-review/SKILL.md` §3 passa a exigir na review final a `Regressão completa` do plan, sempre, no estado final; re-review prova o afetado e só repete a regressão completa se código ou teste mudou desde a última execução completa verde; falha abre R* obrigatório; julgamento de código limitado ao diff e consumidores. Protocolos históricos mantêm a regra atual. `docs/vibe-review/ARQUITETURA.md` e `ANALISE.md` refletem.
- **Aceite:** SKILL coerente com F4; suíte da review verde.
- **Arquivos:** `vibe-review/SKILL.md`, `docs/vibe-review/ARQUITETURA.md`, `docs/vibe-review/ANALISE.md`, `vibe-review/templates/review.md`
- **Prova afetada:** `py -3 docs/vibe-review/tests/test-review.py -v`
- **Estado:** integrada; commit task(T1,T2,T3,T4,T5,T6).

### T5: Regras, escopo e versão major
- [ ] T5 concluída
- **Spec:** C1, C2
- **Deps:** T1, T2, T3, T4
- **O quê:** `AGENTS.md` deste repo e `vibe-init/templates/AGENTS.md` trocam "código paralelo exige autorização aplicável" por ondas com `Arquivos:` disjuntos no Modo A; `README.md` atualiza as linhas do Modo A e da política de testes; `docs/ESCOPO.md` marca o paralelismo por disjunção e registra worktree e fan-out da review como pendentes; versão 8.0.0 nos manifestos versionáveis e em `CONTRACT_VERSION` de `docs/tests/test-distribuicao.py`.
- **Aceite:** manifestos e `CONTRACT_VERSION` em 8.0.0; textos sem contradição com as skills.
- **Arquivos:** `AGENTS.md`, `vibe-init/templates/AGENTS.md`, `README.md`, `docs/ESCOPO.md`, `docs/tests/test-distribuicao.py`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `.grok-plugin/marketplace.json`
- **Prova afetada:** `py -3 docs/tests/test-distribuicao.py -v` e `py -3 docs/vibe-init/tests/test-init.py -v`
- **Estado:** integrada; commit task(T1,T2,T3,T4,T5,T6).

### T6: Papel redator para prosa
- [ ] T6 concluída
- **Spec:** A7
- **Deps:** nenhuma
- **O quê:** `vibe-init` distribui o perfil `redator` (Claude: `model: opus`, `effort: medium`; Codex: mesmo modelo do `revisor`, `model_reasoning_effort = "medium"`) em `templates/agents/{claude,codex}/`, com motores `init.py`/`init.ps1` e testes cobrindo o sexto papel; `delegation.md` (cópias idênticas) inclui o papel na tabela; `vibe-implement/SKILL.md` roteia T* de prosa ao `redator`; `docs/vibe-init/ARQUITETURA.md` documenta.
- **Aceite:** init instala os seis perfis nos dois hosts; cópias de `delegation.md` idênticas.
- **Arquivos:** `vibe-init/scripts/init.py`, `vibe-init/scripts/init.ps1`, `vibe-init/templates/agents/claude/redator.md`, `vibe-init/templates/agents/codex/redator.toml`, `docs/vibe-init/tests/test-init.py`, `docs/vibe-init/tests/test-init.ps1`, `docs/vibe-init/ARQUITETURA.md`, `vibe-init/SKILL.md`, `vibe-implement/SKILL.md`, `vibe-implement/references/delegation.md`, `vibe-plan/references/delegation.md`
- **Prova afetada:** `py -3 docs/vibe-init/tests/test-init.py -v`, `pwsh ./docs/vibe-init/tests/test-init.ps1` e `py -3 docs/tests/test-distribuicao.py -v`
- **Estado:** integrada; commit task(T1,T2,T3,T4,T5,T6).

## Colaboração

- Onda 1: T1, T2, T3 e T4, arquivos disjuntos. T6 entrou durante a onda 1 e roda em paralelo à T1 (arquivos disjuntos). Onda 2: T5, conduzida por subagente Opus atuando como redator.
- Benefício: as quatro fatias são independentes; T5 consolida textos e versão depois delas.
- Ownership: cada implementador escreve somente os `Arquivos:` da sua T*.

## Retomada
- Phase concluída: review aprovada em 2026-10-14, commits 7685093 (T1-T6) e 8c6008f (R1-R3) e commit residual de fechamento, publicada na main.

## Handoff

vibe-implement

- Chat: recomende novo chat para o implement em Modo A; continuar neste chat é válido se o humano preferir.
