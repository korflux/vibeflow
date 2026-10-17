# Plan: VibeFlow V2, skill única só texto com coordenador-líder
# Alvo: phase-21-vibeflow-v2-lider-unico
# Status: aprovado
# Spec: spec.md (mesma pasta), seção "Revisão de escopo: skill só texto"

## Overview

Entrega a skill única `vibeflow` 10.0.0 na branch `v2` como pacote só texto em `skills/vibeflow/`, conforme a revisão de escopo S1 a S9 da spec. O foco é a qualidade e a organização da skill para o coordenador-líder funcionar bem: `SKILL.md` curto e operacional, uma referência por etapa, regras escritas no lugar dos motores, templates de artefato e de governança. A v1 (pacotes, symlinks, docs e testes de motor) sai do repo.
- **Design:** N/A, entrega sem UI visível.
- **Jornada:** C1, C2 e C6 são evidenciados pela primeira phase real conduzida com `/vibeflow`, fora desta phase.
- **Histórico:** o plan anterior (motores Python e PowerShell, T1 a T8) foi substituído pela decisão do humano registrada na spec. Os rascunhos de motor nunca foram commitados.

## Prontidão das provas

- `P-DIFF`: `git diff --check -- <arquivo>` para arquivo rastreado e `git diff --no-index --check -- /dev/null <arquivo>` para arquivo novo; verde é saída sem linha de achado.
- `P-REF`: todo path `references/...` ou `templates/...` citado dentro de `skills/vibeflow/` existe; nenhuma ocorrência de `/vibe-`, `vibe-<etapa>`, `scripts/`, `execution.json`, `--etapa` ou `-Etapa` no pacote.
- gitleaks (8.30.1): local · ok.

### Regressão completa

```text
P-DIFF e P-REF sobre todos os arquivos alterados da phase
gitleaks detect --source . --redact --no-banner
```

## Tasks

### T1: Remover os motores e a v1, fixar a pasta do pacote
- [x] T1 concluída
- **Spec:** S1, S8
- **O quê:** Mover `vibeflow/` para `skills/vibeflow/` (pasta real). Apagar `skills/vibeflow/scripts/`, `docs/vibeflow/tests/` e `skills/vibeflow/references/execution.md`. Remover do Git `vibe-*/`, `skills/vibe-*`, `docs/vibe-*/` e `docs/tests/`.
- **Arquivos:** `vibeflow/`, `skills/`, `docs/vibeflow/tests/`, `vibe-*/`, `docs/vibe-*/`, `docs/tests/`
- **Prova afetada:** `git status` mostra só as remoções e a pasta nova; nenhum symlink em `skills/`.
- **Resumo:** v1 e rascunhos de motor removidos; pacote em `skills/vibeflow/`.

### T2: Reescrever a skill como texto puro, organizada para o líder
- [x] T2 concluída
- **Spec:** S1 a S7, F1 a F8, decisões 2 a 8
- **Deps:** T1
- **O quê:** Resultado principal: prosa (redator). `SKILL.md`, referências por etapa, `delegation.md` e templates sem nenhuma dependência de motor: estado lido do disco, rota em `# Rota:`, regras de `n`, slug, preservação e backup, checagem de gates pelo líder, init por instruções, phases v1 por leitura.
- **Aceite:** o líder consegue conduzir qualquer rota só com o pacote; cada fato tem uma casa; nenhuma referência órfã ou ausente; nenhuma menção a motor, script, `execution.json` ou `/vibe-*`.
- **Arquivos:** `skills/vibeflow/`
- **Prova afetada:** `P-DIFF` e `P-REF` sobre os `Arquivos:`.
- **Resumo:** skill reescrita só texto, com `disco.md` como casa das regras de disco.

### T3: Documentação, regras do repo, README e manifestos
- [x] T3 concluída
- **Spec:** S1, S8, S9, A12
- **Deps:** T1
- **O quê:** Resultado principal: prosa (redator). `docs/vibeflow/ARQUITETURA.md` vira o contrato do pacote só texto (disco, artefatos, papéis, gates, convenções) e `ANALISE.md` registra o fluxo do líder e o corte dos motores. `AGENTS.md` reescreve Projeto, Comandos, Estrutura e Regras deste repo para skill só texto, sem tocar `## Decisões vigentes`. `README.md` documenta instalação e uso de `/vibeflow`. `docs/ESCOPO.md` marca a V2. Manifestos dos quatro hosts listam somente `vibeflow` 10.0.0.
- **Aceite:** nenhum documento ou manifesto cita script, teste de motor ou `vibe-*` como skill instalável; paths citados existem.
- **Arquivos:** `docs/vibeflow/ARQUITETURA.md`, `docs/vibeflow/ANALISE.md`, `AGENTS.md`, `README.md`, `docs/ESCOPO.md`, `.claude-plugin/`, `.codex-plugin/`, `.agents/plugins/`, `.grok-plugin/`, `plugin.json`
- **Prova afetada:** `P-DIFF` sobre os `Arquivos:` e JSON válido nos manifestos.
- **Resumo:** docs, `AGENTS.md`, `README.md`, `docs/ESCOPO.md` e manifestos 10.0.0.

## Colaboração

- Ondas: T1; T2 e T3 em paralelo, com `Arquivos:` disjuntos.
- T3 descreve o pacote pelas decisões S1 a S9 e confere a estrutura final de T2 antes de fechar.
