# Review: conferência obrigatória do líder a cada devolutiva
# Alvo: phase-3-conferencia-do-lider
# Status: aprovado

## Contexto

- Alvo: fase `.vibeflow/phases/phase-3-conferencia-do-lider/`, branch `main`, diff `87916fe..461cb8c` (etapa 1: `87916fe..3a2f3b4`; etapa 2: `3a2f3b4..461cb8c`)
- Cadeia: spec.md / plan.md (sem interview e sem analyze, rota high)
- O que muda: o líder passa a conferir forma e direção de cada devolutiva que muda o estado, com casa única em `references/delegation.md`, Conferência do líder; a captura visual passa a ter casa única em `references/chrome-devtools.md`, Captura e reaproveitamento, com o implementador como dono; `SKILL.md`, `implement.md`, `spec.md` (referência), `ui-visual-quality.md` e `templates/review.md` apontam para essas casas.

## Cobertura da solicitação

- Origem e limites: pedido do humano transmitido pelo líder (conferência barata e obrigatória do líder, no disco e no Git, a cada etapa antes de aceitar a entrega), `spec.md` e `plan.md` aprovados, e as regras P1, P2, P3 e P10 decididas pelo líder na implementação e refletidas na spec. O disco não registra confirmação humana posterior a P1, P2, P3 e P10, porque spec e plan nasceram no mesmo commit da T1. Pendente de confirmação humana: o líder leva P1, P2, P3 e P10 ao humano na confirmação final, junto do Approve; sem R*.

| Item da solicitação e fonte (A*/C* quando houver) | Implementação | Evidência | Situação |
|---|---|---|---|
| Conferência barata e obrigatória do líder a cada devolutiva que muda o estado, lendo disco e Git (pedido do humano; Suposições 1 e 4) | `references/delegation.md`, Conferência do líder; `SKILL.md`, seção 5, itens 4 e 5 | Revisão de consistência no diff `87916fe..461cb8c` (etapa 1: `87916fe..3a2f3b4`; etapa 2: `3a2f3b4..461cb8c`) | atendido |
| A1: prosa confrontada com as decisões do humano, sem reescrever | `delegation.md`, linha "Prosa de etapa de planejamento"; `references/spec.md`, Saída | Revisão de consistência | atendido |
| A2: código por `git diff --stat` contra `Arquivos:`, trecho do diff só com algo estranho, sem testes nem leitura linha a linha | `delegation.md`, linha "Código de T*" e Limites; `implement.md`, seção 1, passo 5 | Revisão de consistência; termo corrigido em `461cb8c` (R2) | atendido |
| A3: onda paralela conferida uma vez na integração | `delegation.md`, linha "Onda com mais de uma T*"; `implement.md`, seção 1, passo 5 | Revisão de consistência | atendido |
| A4: implementador captura nos viewports e estados, fora do repositório, paths no campo `prova`; verificador reaproveita | `chrome-devtools.md`, Captura e reaproveitamento; `delegation.md`, campo `prova`; `implement.md`, seção 9, passo 4 | Revisão de consistência | atendido |
| A5: líder abre as imagens sem servidor nem navegação; review recaptura com `Visual: necessária` quando a evidência sumiu ou os inputs mudaram | `chrome-devtools.md`, linhas Líder e Revisor; `delegation.md`, linha "Aceite visual"; `ui-visual-quality.md`; `templates/review.md` | Revisão de consistência | atendido |
| A6: evidência de API ou CLI conferida sem execução | `delegation.md`, linha "API ou CLI" e Limites | Revisão de consistência | atendido |
| A7: Express e medium conferidos por diff contra o brief e, se visual, screenshot | `delegation.md`, linha "Express e medium"; `implement.md`, Entrada e seção 8, passo 1 | Revisão de consistência | atendido |
| A8: Express inteiro do líder sem conferência própria | `delegation.md`, último parágrafo da subseção | Revisão de consistência | atendido |
| A9: direção ao dono, técnica ao verificador, sem desempate do líder | `delegation.md`, parágrafo de divergência | Revisão de consistência | atendido |
| A10: aprovação só na linha de progresso, reprovação só como devolução, sem seção nem registro | `delegation.md`, parágrafo de visibilidade | Revisão de consistência | atendido |
| C1: casa única, demais casas apontam | `delegation.md` e `chrome-devtools.md` como casas; `SKILL.md`, `implement.md`, `spec.md`, `ui-visual-quality.md` e `templates/review.md` apontam | `grep` de "confer" e "captur" no pacote | atendido; repetição parcial do momento em `implement.md` vai a Notas |
| C2: líder não executa prova, não sobe servidor nem cria evidência | Limites de `delegation.md` e linha Líder de `chrome-devtools.md`, com a exceção do Modo B | Revisão de consistência; C2 da spec alinhada em `461cb8c` (R1) | atendido |
| C3: captura pertence a quem altera a UI; fora do Modo B, verificador e líder reaproveitam | `chrome-devtools.md`, Captura e reaproveitamento | Revisão de consistência | atendido |
| C4: correção técnica exclusiva do verificador e do revisor | `delegation.md`, primeiro parágrafo e parágrafo de divergência | Revisão de consistência | atendido |
| C5: sem path contratual novo em `disco.md` e sem mudança em `scripts/` | Nenhum dos dois no diff | `git diff --stat 87916fe HEAD`; `node --test` 26/26 | atendido |
| C6: minor, sem arquivo de versão alterado | Nenhum manifesto alterado; sem campo `version` nem tags | `grep '"version"'` nos manifestos sem resultado; `git tag` vazio | atendido |
| P1: Modo B como exceção a "líder não executa prova" (decisão do líder) | `delegation.md`, Limites e último parágrafo; `chrome-devtools.md`, linha Líder | Revisão de consistência; coerente com `SKILL.md`, seção 7 | atendido; pendente de confirmação humana na finalização |
| P2: revisor recaptura só quando a evidência sumiu ou os inputs mudaram (decisão do líder) | `chrome-devtools.md`, linha Revisor | Revisão de consistência | atendido; pendente de confirmação humana na finalização |
| P3: corretor recaptura quando a correção altera a UI (decisão do líder) | `chrome-devtools.md`, linha Corretor | Revisão de consistência | atendido; pendente de confirmação humana na finalização |
| P10: T* sozinha conferida antes do verificador; onda com mais de uma T*, uma vez na integração (decisão do líder) | `implement.md`, seção 1, passo 5; `delegation.md`, tabela | Revisão de consistência; termo corrigido em `461cb8c` (R2) | atendido |

## Checklist de correções

### Nit

- [x] R1: **Nit** - `.vibeflow/phases/phase-3-conferencia-do-lider/spec.md` - a spec aprovada diverge da skill entregue em dois pontos: a C2, marcada `[x]`, afirma que nenhuma frase manda o líder executar prova, sem a ressalva do Modo B que a própria spec aplica em Fora e na C3 e que `delegation.md` (Limites) e `chrome-devtools.md` (linha Líder) declaram; e o F3, passo 1, e a validação de F3 falam em "pasta temporária da sessão", enquanto `chrome-devtools.md` fixa "pasta temporária do sistema" - remédio: acrescentar "fora do Modo B" à C2 e trocar "da sessão" por "do sistema" no F3, sem outra mudança - prova: releitura da C2 e do F3 contra `delegation.md` e `chrome-devtools.md`; `git diff --check` - source: C2, diff - gap: contradicts - papel: redator
- [x] R2: **Nit** - `skills/vibeflow/references/implement.md` - a seção 1, passo 5, e a linha "Código de T* que roda sozinha" de `skills/vibeflow/references/delegation.md` usam "roda sozinha" num sentido amplo (toda T* fora de onda com mais de uma T*), enquanto o passo 2 da mesma seção define "roda sozinha" como a T* sem `Arquivos:` comparáveis; na leitura estrita, uma onda de uma só T* com `Arquivos:` (caso desta phase) não cai em nenhuma das duas linhas e fica sem regra de conferência - remédio: no passo 5 e na linha da tabela, trocar "roda sozinha" por uma expressão que não colida com o termo do passo 2, como "T* que não divide a onda com outra", mantendo "onda com mais de uma T*" como complemento - prova: releitura dos passos 2 e 5 de `implement.md` e da tabela de `delegation.md`; `checagem-de-paths` do plan sobre os dois arquivos; `git diff --check` - source: P10, A2, diff - gap: partial - papel: redator

## DoD

- [x] Uma casa por fato para a conferência (`delegation.md`) e para a captura visual (`chrome-devtools.md`)
- [x] Conferência barata: só `git diff --stat`, leitura do artefato ou da evidência anexada, sem execução de prova fora do Modo B
- [x] Sem path citado inexistente, sem teste de prosa, sem script alterado
- [x] Sem contradição entre spec e skill (R1) nem termo ambíguo no fluxo (R2)

## Notas

- N3 do verificador: C3 e Fora não citam o revisor, mas não o contradizem; a recaptura do revisor está na Suposição 9, no F3 (Estados) e na A5. Sem R*.
- N5 do verificador: `implement.md`, seção 1, passo 5, repete "uma vez na integração" da tabela de `delegation.md`; o passo guarda o momento no fluxo ("antes do verificador"), que não está na casa única, e não contradiz a tabela. Sem R*; R2 toca a mesma frase e pode enxugá-la.
- N1 no `plan.md` (T1, item 4, "pasta temporária da sessão"): o plan descreve trabalho concluído; não exige correção.
- Na onda com mais de uma T*, o líder relê paths contra `Arquivos:` depois que o verificador certificou ownership. A subseção declara isso como checagem de forma, de custo baixo; coerente com `SKILL.md`, seção 5, item 5.
- `AGENTS.md` lista `.erros-encontrados/` na estrutura, e a pasta não existe; é criada sob demanda e não é desta phase.

## Veredito vigente

- [x] **Approve**: origem suficiente, obrigações atendidas ou retiradas explicitamente pelo humano e nenhum R* de correção em `[ ]`
- [ ] **Request changes**: há R* de correção em `[ ]`

## Handoff

finalização Git da phase

- [x] Aprovação humana (leu o arquivo e confirmou)

- Chat: no Modo A, esta review roda em revisor de contexto limpo, a pedido do líder; sem subagentes, roda num chat novo com `/vibeflow review`. As correções seguem pela etapa implement, com corretor ou redator conforme o `papel` de cada R*; sem subagentes, num chat novo com `/vibeflow implement`. Após Approve e confirmação humana, o handoff é a finalização Git da phase. O `review.md` vivo e o diff são a ponte.

## Finalização Git da phase

- Pré-condições: Approve final confirmado, todas as `T*` concluídas, todos os R* de correção fechados, prova necessária da integração verde, `git diff --check` e gitleaks.
- Commit final: `chore(phase-3): finalize review`, somente com paths residuais autorizados; sem mudanças residuais, manter o último commit integrado ou da task.
- Push: `git push` para o upstream atual, sem `--force`. Registrar hash/HEAD, paths e resultado; falha mantém o handoff bloqueado.

## Etapas

### Etapa 1 - first-pass - T1, diff 87916fe..3a2f3b4, regressão completa

- Provas reaproveitadas: nenhuma; a `Prova afetada:` da T1 está contida na regressão completa executada abaixo.
- Provas executadas (regressão completa do plan, HEAD `3a2f3b4`, árvore limpa):
  - Revisão de consistência dos 7 arquivos alterados em `skills/vibeflow/`: casas únicas presentes, ponteiros coerentes, achados R1 e R2.
  - `checagem-de-paths` do plan sobre todos os `.md` e `.toml` versionados de `skills/vibeflow/`: nenhuma linha `AUSENTE`.
  - Paths em crase de `README.md`, `AGENTS.md` e `SKILL.md`: os não encontrados são paths do projeto consumidor, nomes genéricos de artefato, comandos ou menções proibitivas (`CLAUDE.md`, `GEMINI.md`, `docs/`); nenhum path deste repo ausente.
  - Busca por marcadores da v1 (`etapas-v1`, `coordenacao-v1`, `vibeflow-*`) e registro estruturado de execução em `skills/`, `README.md`, `AGENTS.md` e `tests/`: só a própria regra do `AGENTS.md` e "a v1" do produto consumidor em `interview/refinement-criteria.md`; verde.
  - `node --test` (Node 24.12.0): 26 testes, 26 pass, 0 fail.
  - `git diff --check 87916fe HEAD`: sem saída, código 0.
  - `gitleaks detect --source . --redact --no-banner`: 97 commits, no leaks found, código 0.
- Execução: todos os paths alterados fora de `.vibeflow/` estão nos `Arquivos:` da T1; perfis em `templates/agents/` não mudaram e não contradizem a captura nem o reaproveitamento; `disco.md` e `scripts/` intactos; T1 marcada aparece em `task(phase-3:T1): ...` (`3a2f3b4`) com paths coerentes; phase com uma única T*, sem par de T* para consumidor compartilhado.
- Leu: pedido do humano e regras P1, P2, P3 e P10 no brief do líder, observações N1 a N5 do verificador, `spec.md`, `plan.md`, `AGENTS.md` do disco, `references/review.md`, diff e `git log` da phase.
- Cobertura: matriz criada; A1 a A10, C1 a C6 e P1, P2, P3, P10 atendidos na skill; R1 e R2 abertos.
- Abriu: R1, R2
- Fechou: nenhum
- Veredito desta etapa: Request changes

### Etapa 2 - re-review - R1, R2, diff 3a2f3b4..461cb8c

- Provas reaproveitadas: prova da correção certificada pelo verificador para R1 e R2; da etapa 1, `gitleaks` e as checagens de paths dos arquivos não alterados.
- Provas executadas (HEAD `461cb8c`, árvore limpa; só onde os inputs mudaram):
  - Revisão de consistência de `spec.md`, `references/delegation.md` e `references/implement.md`: a C2 traz "fora do Modo B" nas duas orações e remete o Modo B ao `SKILL.md`, seção 7; o F3 diz "pasta temporária do sistema" nos dois pontos, coerente com `chrome-devtools.md`; "roda sozinha" sobra só no sentido técnico (`implement.md`, passo 2; `delegation.md`, Delegar e colaborar; `plan.md`), e a conferência usa "T* que não divide a onda com outra", com "onda com mais de uma T*" como complemento, o que cobre a onda de uma só T*.
  - `checagem-de-paths` do plan sobre `delegation.md` e `implement.md`: nenhuma linha `AUSENTE`.
  - `node --test`: 26 pass, 0 fail.
  - `git diff --check 3a2f3b4 461cb8c`: sem saída, código 0.
  - `gitleaks detect --source . --redact --no-banner`: no leaks found, código 0.
- Execução: o commit `task(phase-3:R1,R2): ...` (`461cb8c`, pai `3a2f3b4`) existe, e seus IDs são exatamente os R* marcados `[x]` desde a etapa 1 (R1, R2). Os paths alterados (`spec.md`, `review.md`, `delegation.md`, `implement.md`) estão nos remédios dos R* e nos `Arquivos:` da T1. O ajuste direto do líder na C2 está dentro do remédio do R1.
- Leu: diff `3a2f3b4..461cb8c`, `git log`, `review.md` da etapa 1 e o pedido de re-review do líder.
- Cobertura: A2, C2 e P10 sem ressalva; P1, P2, P3 e P10 pendentes de confirmação humana na finalização, sem R*.
- Abriu: nenhum
- Fechou: R1, R2
- Veredito desta etapa: Approve final
