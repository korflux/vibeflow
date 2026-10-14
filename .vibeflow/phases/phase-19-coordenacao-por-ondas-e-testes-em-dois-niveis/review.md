# Review: Coordenação por ondas e testes em dois níveis
# Alvo: phase-19-coordenacao-por-ondas-e-testes-em-dois-niveis
# Status: request-changes

## Contexto

- Alvo: phase-19, commit integrado `76850933` (`task(T1,T2,T3,T4,T5,T6)`) sobre `7c573f4`, na `main` local; branch remota `phase-19` no mesmo SHA.
- Cadeia: spec.md (aprovada) / plan.md (aprovado, `coordenacao-v1`, Modo A) / execution.json. Sem interview, sem design (N/A, sem UI) e sem analyze (rota high).
- O que muda: o motor da vibe-implement relata `fila.onda` e `fila.sem_arquivos` em `coordenacao-v1` Modo A; plan, implement e review passam a operar ondas por `Arquivos:` disjuntos e provas em dois níveis (afetada por T*, regressão completa na review final); novo papel `redator` distribuído pelo init; versão 8.0.0.

## Tipo de review

- Tipo: final
- Marco e justificativa: integração final. Motor da implement em leitura: `etapa: revisar`, T1-T6 concluídas, `local_valida` em todas, `integracao.prova_valida: true`, `commit_encontrado: 76850933`.
- T* abertas fora do marco: nenhuma
- Provas reaproveitadas: provas afetadas T1-T6 e união na integração, registradas válidas em execution.json (conferidas pelo motor; não repetidas, conforme §3).
- Provas executadas: regressão completa do plan, detalhada na Etapa 1.

## Cobertura da solicitação

- Origem e limites: fonte é a tabela "Cobertura da origem" e as decisões 1-12 da spec aprovada, mais o pedido do coordenador desta review. Não há interview.md e a conversa original não estava disponível ao revisor. As decisões 11 e 12 estão registradas como decisão do humano tomada durante a implementação; o revisor aceita o registro da spec aprovada, e o coordenador deve confirmá-las com o humano na pergunta final.

| Item da solicitação e fonte (A*/C* quando houver) | Implementação | Evidência | Situação |
|---|---|---|---|
| Coordenador despacha em paralelo, não T* a T* (origem; F2; A1, A2) | `implement.py` `plan_wave`, `implement.ps1` `Get-PlanWave`; `vibe-implement/SKILL.md` §2 tabela da onda; `references/delegation.md` | `test_onda_por_fixture`, `test_onda_parity_por_fixture`, `test_jornada_de_ondas_por_prova_local`; CI 38587308590 verde; leitura da SKILL | atendido |
| Dono por arquivo, sem colisão entre T* paralelas (origem; F1, F2; A1; decisão 3) | sobreposição por igualdade, prefixo de diretório e curinga, sem caixa, `\` normalizada; path incomparável roda sozinho | 12 casos de fixture (disjuntas, path igual, caixa/barra, prefixo, curinga, raiz, sem `Arquivos:`, lista vazia, vírgula) com paridade PowerShell | atendido |
| Motor calcula a onda deterministicamente, sem interpretar prosa (decisão 4) | `fila.onda` subconjunto ordenado de `fila.elegiveis`; paths lidos como texto | asserção de subconjunto ordenado em `test_onda_por_fixture`; `tree_snapshot` inalterado | atendido |
| Plan com `Arquivos:` e `Prova afetada:` por T* e `Regressão completa` única (decisão 5; F1; A3) | `vibe-plan/SKILL.md` §4 regras 2, 4, 6; `vibe-plan/templates/plan.md` | leitura; `test-plan.py` verde local e CI; o próprio plan desta phase usa o formato | atendido |
| Implement testa só o afetado (origem; decisão 6; F3; A4) | `vibe-implement/SKILL.md` §3 tabela de dois níveis; `delegation.md` Conferência e registro; `definition-of-done.md` | leitura; cópias de `delegation.md` idênticas (`cmp`) | atendido |
| Review testa tudo, uma vez, e repete só se código/teste mudou (origem; decisão 7; F4; A5) | `vibe-review/SKILL.md` §3 item 3; `docs/vibe-review/ARQUITETURA.md` §5 | leitura; regra exercida nesta etapa | atendido |
| Review direcionada ao diff e consumidores (origem; decisão 8) | `vibe-review/SKILL.md` §3 item 2 | leitura | atendido |
| Modo B, etapas-v1 e plans sem marcador inalterados (decisão 2; A6) | campos `onda`/`sem_arquivos` só no ramo `coordenacao-v1` A dos dois motores | `test_sem_onda_fora_do_modo_a_coordenado` e paridade; suítes históricas verdes no CI | atendido |
| Item de paralelismo em `docs/ESCOPO.md`, worktree e fan-out pendentes (origem; C2) | `docs/ESCOPO.md` linhas 18-21 | leitura | atendido |
| Versão major (decisão 10; C2) | 8.0.0 em `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `.grok-plugin/marketplace.json`; `CONTRACT_VERSION` | `test-distribuicao.py` verde no CI | atendido |
| Suítes verdes e `delegation.md` idêntica (C1) | estado integrado `76850933` | CI 38587308590 `success`; regressão local com somente as falhas conhecidas de symlink | atendido |
| Coordenador como líder estratégico que delega e valida dados (decisão 11) | `vibe-implement/SKILL.md` §2; `delegation.md`; `AGENTS.md` e `vibe-init/templates/AGENTS.md` | leitura | atendido |
| Papel `redator` distribuído pelo init e roteado pela implement (decisão 12; A7) | motores `init.py`/`init.ps1`, templates `redator.md`/`redator.toml`, `test-init.py`, `test-init.ps1`, `ARQUITETURA.md`, SKILLs e `delegation.md` no commit; `docs/vibe-init/ANALISE.md` e `docs/vibe-init/tests/test-init.sh` corrigidos apenas na árvore de trabalho, fora do commit | log do CI imprime `PASS launcher-alias: dez perfis`; `git show 76850933:docs/vibe-init/tests/test-init.sh` sem `redator` | parcial (R1) |
| Worktree por T*, fan-out da review, esforço dos perfis (origem; Fora) | fora do escopo | spec, Fora e Cobertura da origem: "Decisão do humano" | retirado explicitamente pelo humano |
| Push ao final (decisão 9) | autorização registrada na spec; execução pertence à finalização pós-Approve | spec decisão 9 | atendido no contrato; execução pendente da finalização |

## Checklist de correções

### Required

- [x] R1: **Required** - `docs/vibe-init/tests/test-init.sh:17,22,34,38` e `docs/vibe-init/ANALISE.md:9` - o commit integrado traz o launcher sem o sexto papel (laços com cinco papéis, mensagem "dez perfis") e a análise do init ainda descreve "dez perfis", contradizendo `docs/vibe-init/ARQUITETURA.md:19` (seis papéis, doze arquivos). A correção do corretor da T6 ficou só na árvore de trabalho porque os dois paths não estavam nos `Arquivos:` da T6; a A7 fica sem prova de launcher no estado commitado. - remédio: `vibe-implement` atribui os dois paths a uma correção R1 com ownership explícito, confere o conteúdo já presente na árvore de trabalho (inclui `redator` nos dois laços e atualiza comentário, mensagem e ANALISE) e o finalizador commita `task(R1): ...` com staging explícito desses paths. - prova: `bash docs/vibe-init/tests/test-init.sh` no CI Linux do novo commit imprimindo `PASS launcher-alias: doze perfis`, e `py -3 docs/vibe-init/tests/test-init.py -v` - source: A7, decisão 12, diff - gap: partial

### Nit

- [x] R2: **Nit** - `docs/vibe-review/ARQUITETURA.md:27` - a linha da tabela de papéis, alterada nesta phase, ainda diz que o `plan.md` guarda "provas registrados sob cada T*"; em `coordenacao-v1` A o plan só define `Prova afetada:` e o registro é o `execution.json` (a própria linha 12 do arquivo diz isso), e a tabela não lista o `execution.json`. - remédio: `vibe-implement` (redator) qualifica a linha: plan define `Prova afetada:` e `Regressão completa`; em `coordenacao-v1` A o registro de execução é o `execution.json`, com linha própria na tabela. - prova: releitura na re-review e `py -3 docs/vibe-review/tests/test-review.py -v` - source: diff - gap: contradicts
- [x] R3: **Nit** - `docs/vibe-implement/ARQUITETURA.md:133` - o parágrafo, alterado nesta phase, afirma sem qualificação "Verificador certifica integração proporcional ao impacto" e "Revisor ... executa somente lacunas", logo depois de dizer que em `coordenacao-v1` A a regressão completa é exclusiva da review final; a leitura literal contradiz a decisão 7. - remédio: `vibe-implement` (redator) restringe essas duas frases aos protocolos históricos e ao Modo B e remete o `coordenacao-v1` A à regressão completa da review. - prova: releitura na re-review e `py -3 docs/vibe-implement/tests/test-implement.py -v` - source: decisão 7, diff - gap: contradicts

## Segurança

- O diff toca somente a leitura do plan local pelos motores. Os paths de `Arquivos:` são tratados como texto: não são resolvidos, abertos nem executados; comandos de prova continuam dados. Nada explorável no que o diff tocou. Varredura `gitleaks` limpa local e no CI.

## Notas

- Pendências do verificador avaliadas sem R*: (1) aparo de `\x1c`-`\x1f` diverge entre `str.strip()` e `String.Trim()` (conferido: Python remove, .NET não); `execution.ps1:73` reduziu a divergência anterior (antes exigia Deps sem indentação), e `implement.ps1:258`/`implement.py:298` são anteriores à phase. Recomenda-se registro em `.erros-encontrados/` pelo coordenador. (2) `implement.ps1:518` mantém regex própria anterior à phase, funcional após a normalização LF. (3) resíduos `\r?` em `implement.ps1:145, 518, 758, 759` são inertes após `ConvertTo-LfText`. (4) `execution.ps1:197` normaliza de novo um texto já normalizado; idempotente e defensivo.
- A re-review exige nova regressão completa: R1 altera `docs/vibe-init/tests/test-init.sh`, path de teste fora de `.vibeflow/`.

## Veredito vigente

- [ ] **Approve**: origem suficiente, obrigações atendidas ou retiradas explicitamente pelo humano e nenhum R* de correção em `[ ]`
- [x] **Request changes**: há R* de correção em `[ ]` (R1, R2, R3) e a A7 está parcial no estado commitado.

## Handoff

vibe-implement

- [ ] Aprovação humana (leu o arquivo e confirmou)

- Chat: no Modo A, o coordenador delega R1-R3 a um subagente (corretor para o launcher, redator para a prosa) e depois uma re-review de contexto limpo. O `review.md` vivo e o diff são a ponte.

## Etapas

### Etapa 1 - first-pass - diff 7c573f4..76850933, T1-T6, regressão completa

- Tipo: final
- Marco e justificativa: integração final; fila concluída pelo motor da implement em leitura (`etapa: revisar`, integração válida, commit `76850933` encontrado).
- T* abertas fora do marco: nenhuma
- Provas reaproveitadas: provas afetadas T1-T6 e integração, válidas em execution.json pelo motor; não repetidas.
- Provas executadas: regressão completa do plan (`### Regressão completa`), uma vez, HEAD `76850933aa6bd4c6775e7458f2ef3056ac4b790c`. Paths de código e teste sem modificações não commitadas: não. `docs/vibe-init/ANALISE.md` e `docs/vibe-init/tests/test-init.sh` estavam modificados (objeto do R1), além do residual previsto de `execution.json`.
  - `py -3 docs/vibe-<skill>/tests/test-<skill>.py -v`: interview, spec, design, plan, analyze e review OK. init: 22 erros, todos `WinError 1314` (symlink sem privilégio). implement: 69 testes, 1 erro conhecido (`test_integration_snapshot_types_and_old_commit`) e 2 skips de symlink.
  - `py -3 docs/tests/test-distribuicao.py -v`: 2 falhas conhecidas (`test_skills_pointers`, `test_unique_names_under_skills`); `test-mvp-flow.py`, `test-reparse-safety.py`, `test-runtime-discovery.py`, `test-stream-encoding.py` OK.
  - `pwsh ./docs/vibe-init/tests/test-init.ps1`: `ponte-legada` falha por privilégio de administrador (conhecida); demais PASS.
  - `bash docs/vibe-<skill>/tests/test-<skill>.sh`: sete launchers OK; init falha porque `skills/vibe-init` não é symlink neste host.
  - `gitleaks detect --source . --redact --no-banner`: limpo.
  - Exceções de symlink cobertas pelo CI Linux do mesmo commit: `gh run view 38587308590 --repo korflux/vibeflow`, workflow `contrato`, branch `phase-19`, headSha `76850933`, conclusão `success` (testes 5m51s, segredos 5s). O launcher do init no CI imprime "dez perfis", evidência do R1.
  - E2E `docs/vibe-implement/tests/piloto-modo-a.py`: excluído pelo plan (não determinístico, consome tokens da conta, fora do CI); não executado.
- Leu: spec.md (Cobertura da origem, decisões 1-12, A1-A7, C1-C2), plan.md, execution.json via motor, diff da phase nos motores, testes de onda, SKILLs e referências de plan/implement/review/init, `AGENTS.md`, `docs/ESCOPO.md`, manifestos.
- Cobertura: matriz completa; A7 parcial pelo R1; demais obrigações atendidas ou retiradas pelo humano.
- Abriu: R1, R2, R3
- Fechou: nenhum
- Veredito desta etapa: Request changes
