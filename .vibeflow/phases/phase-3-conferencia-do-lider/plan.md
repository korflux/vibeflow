# Plan: conferência obrigatória do líder a cada devolutiva
# Alvo: phase-3-conferencia-do-lider
# Status: aprovado
# Spec: spec.md (mesma pasta)

## Overview

Implementa a spec aprovada (A1 a A10, C1 a C6): o líder passa a conferir forma e direção de cada devolutiva que muda o estado da phase, com a regra numa única casa do pacote, e o implementador passa a ser o único dono da captura visual. A entrega é uma só, a regra coerente em todas as casas da skill, e por isso fica numa única T* de prosa.
- **Design:** N/A, porque a mudança é texto da skill, sem UI visível.

## Prontidão das provas

- Node 18+ (local 24.12.0): local · ok
- bash com grep (Git Bash): local · ok
- gitleaks (versão 8.30.1, usado em 2026-10-19 neste repo): local · ok

Comando compartilhado `checagem-de-paths`, executado em Git Bash na raiz do repo, com `<arquivos>` sendo os arquivos alterados pela T* dentro de `skills/vibeflow/`. Ele lista todo path `references/...`, `templates/...` e `scripts/...` citado e acusa os que não existem em `skills/vibeflow/`; saída sem linha `AUSENTE` é verde. Paths com placeholder, como `references/<etapa>.md`, não casam com o padrão e ficam de fora.

```bash
for f in <arquivos>; do grep -oE '(references|templates|scripts)/[A-Za-z0-9_./-]*[A-Za-z0-9_-]' "$f" | sort -u | while read -r p; do test -e "skills/vibeflow/$p" || echo "AUSENTE $f: $p"; done; done
```

### Regressão completa

Comandos do `AGENTS.md`, seção Comandos do projeto, executados somente pela review final:

- Revisão de consistência de todos os arquivos alterados.
- Todo path deste repo citado em `skills/vibeflow/`, `README.md` e `AGENTS.md` existe; paths do projeto consumidor ficam fora.
- Nenhum arquivo cita a v1 do VibeFlow ou registro estruturado de execução.
- `node --test` na raiz.
- `git diff --check`.
- `gitleaks detect --source . --redact --no-banner`.

## Tasks

### T1: Estabelece a conferência do líder com casa única e a captura visual do implementador
- [x] T1 concluída
- **Estado:** concluída
- **Resumo:** regra da conferência do líder com casa única em delegation.md e captura visual em chrome-devtools.md; integração verde; próximo: review pelo revisor
- **Spec:** A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, C1, C2, C3, C4, C5, C6
- **Deps:** nenhuma
- **O quê:** Resultado principal: prosa (redator). A T1 segue estas decisões de desenho:
  1. Casa única da regra: nova subseção "Conferência do líder" em `skills/vibeflow/references/delegation.md`, que substitui o trecho atual de "Delegar e colaborar" que manda consumir o relatório e não repetir certificação. O princípio de não refazer certificação permanece, agora junto da conferência. A subseção contém o princípio (forma e direção, não correção técnica), uma tabela por tipo de entrega (prosa, código de T* serial, onda na integração, visual, API e CLI, Express e medium), os limites (só lê disco, Git e evidência anexada; não executa prova nem cria evidência), o roteamento da divergência (direção ao dono, técnica ao verificador, o líder não desempata) e a visibilidade (aprovação só na linha de progresso existente, reprovação como devolução; sem seção nem registro). Uma frase explicita a exceção do Express feito inteiro pelo líder, que não tem conferência própria porque o líder não certifica o próprio ajuste (`SKILL.md`, seção 5, item 3).
  2. `skills/vibeflow/SKILL.md`, seção 5, itens 4 e 5: passam a apontar para a subseção ("confronte ... conforme references/delegation.md, Conferência do líder"), sem copiar a tabela.
  3. `skills/vibeflow/references/implement.md`: os pontos onde a devolutiva é aceita (seção 1, passo do confronto; Express na Entrada; Rota medium) apontam para a casa única, sem repetir a regra.
  4. Captura visual com casa única em `skills/vibeflow/references/chrome-devtools.md`: o implementador captura nos viewports e estados do `design.md` ou do brief, grava fora do repositório (pasta temporária da sessão) e cita os paths no campo `prova` do relatório fixo; o verificador reaproveita a evidência enquanto os inputs renderizados não mudarem; em chat novo, a review recaptura quando `Visual: necessária`. A seção 9, passo 4, de `implement.md` e o campo `prova` do relatório fixo em `delegation.md` apontam para essa regra.
  5. Perfis `skills/vibeflow/templates/agents/claude/implementador.md`, `skills/vibeflow/templates/agents/codex/implementador.toml`, `skills/vibeflow/templates/agents/claude/verificador.md` e `skills/vibeflow/templates/agents/codex/verificador.toml`: mudam somente se o texto atual contradisser a captura fora do repositório com paths no campo `prova` ou o reaproveitamento pelo verificador; sem contradição, ficam como estão, porque já mandam seguir a skill.
  6. `AGENTS.md` não muda: a frase "A IA audita o resultado no disco e no Git" passa a ser coerente com a casa única. Nenhum arquivo de versão muda (C6). Nenhum script em `skills/vibeflow/scripts/` nem `skills/vibeflow/references/disco.md` muda (C5).
- **Aceite:** a revisão de consistência encontra a regra da conferência só em `delegation.md`, com as demais casas apontando para ela; a captura visual só em `chrome-devtools.md`; nenhuma frase que mande o líder executar prova, subir servidor ou capturar; e nenhum path citado inexistente.
- **Arquivos:** `skills/vibeflow/references/delegation.md`, `skills/vibeflow/SKILL.md`, `skills/vibeflow/references/implement.md`, `skills/vibeflow/references/chrome-devtools.md`, `skills/vibeflow/templates/agents/`, `skills/vibeflow/references/spec.md`, `skills/vibeflow/templates/review.md`, `skills/vibeflow/references/review/ui-visual-quality.md`
- **Prova afetada:** checagem mecânica, sem teste de presença de palavras: `git diff --check`; `checagem-de-paths` (Prontidão das provas) sobre os arquivos alterados da T1, sem linha `AUSENTE`; `node --test` na raiz continua verde, porque os scripts de `skills/vibeflow/scripts/` leem o disco e são o consumidor contratual.

## Handoff

implement
