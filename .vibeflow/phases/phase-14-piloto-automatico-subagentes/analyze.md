# Analyze: Piloto automático de implementação com subagentes
# Alvo: phase-14-piloto-automatico-subagentes
# Status: aprovado
# Plan: plan.md (mesma pasta)

## Fontes

| Arquivo | Estado |
|---|---|
| interview.md | presente |
| spec.md | presente |
| plan.md | presente (estava em rascunho; passou a aprovado a pedido do analyze) |
| design.md | N/A, a entrega não tem UI visível |
| AGENTS.md | lido |

## Cobertura e Rastreabilidade

| Chave | Origem | T* | Notas |
|---|---|---|---|
| A1 | spec.md | T4, T6 | Delegação do analyze e handoff `vibe-analyze` em phase max. Prova na rodada 0 da T6 (F7) |
| A2 | spec.md | T4, T6 | Fechamento do plan e do analyze com chat novo e anúncio do Modo A. Prova na rodada 0 da T6 (F7) |
| A3 | spec.md | T3, T6 | Coordenador, implementador por T* e commit `task(Tn)` |
| A4 | spec.md | T1, T3, T6 | Review em subagente e limite de 2 correções. Semântica de `rodadas_correcao` fechada em F3 |
| A5 | spec.md | T3, T6 | Pergunta única final e finalização da `vibe-review` |
| A6 | spec.md | T3, T6 | Paradas, instalação e prova vermelha |
| A7 | spec.md | T1, T3, T6 | Retomada por `etapa`, checkpoint e Git |
| A8 | spec.md | T3, T6 | Modo B de uma T* por run |
| A9 | spec.md | T2 | Cópias idênticas de `references/delegation.md` |
| A10 | spec.md | T3, T4, T6 | Regra única de instalação. Arquivos que ainda proibiam instalar entraram em F5 |
| A11 | spec.md | T5 | Docs, `AGENTS.md`, `ESCOPO.md` e versão major. Versão fixa em teste e README entrou em F2 |
| C1 | spec.md | T1 | Fixtures de `etapa` e `rodadas_correcao` nos dois motores |
| C2 | spec.md | T2 | Teste de distribuição compara bytes |
| C3 | spec.md | T6 | Execução piloto real, rodadas 0, 1 e 2 |
| C4 | spec.md | T5 | Não tinha T* no campo `Spec:` (F1) |
| Resultado 1 a 8 (interview) | interview.md | T1 a T5 | Fluxo de chats, Modo A, Modo B, papéis, paradas, mapeamento contínuo, instalação e major cobertos. Item de chats corrigido em F9 |
| Sucesso (interview) | interview.md | T3, T6 | Um `/vibe-implement`, uma pergunta final, retomada pelo disco. Provado pelo C3 |

## Achados e Resoluções

| ID | Categoria | Gravidade | Onde | Problema | Resolução Aplicada |
|---|---|---|---|---|---|
| F1 | cobertura | MEDIUM | plan.md T5 | C4 sem T* no campo `Spec:` | C4 adicionado à T5, que já roda as suítes |
| F2 | furo | HIGH | plan.md T5 | `CONTRACT_VERSION = "3.1.0"` em `docs/tests/test-distribuicao.py` e a linha de versão do README fixam a versão atual; o bump para 4.0.0 quebraria o teste | Os dois arquivos entraram em Arquivos, no O quê e no aceite da T5 |
| F3 | inconsistencia | HIGH | plan.md T1 | `rodadas_correcao` contava etapas `Request changes`, o que diverge do critério da spec ("2 rodadas usadas informa parada") por uma unidade | Redefinido como correções já aplicadas; o coordenador para com `etapa` `corrigir` e `rodadas_correcao` 2 |
| F4 | furo | MEDIUM | plan.md T1 | `confirmar` só reconhecia `**Approve**`; um `Approve com defer` marcado caía em `revisar` e repetiria a review sem fim | `confirmar` aceita as duas formas; lacuna do `vibe-review` registrada em `.erros-encontrados/` |
| F5 | inconsistencia | HIGH | plan.md T3 e T4 | `chrome-devtools.md`, `ui-visual-quality.md` e `kit-e-tokens.md` ainda proíbem instalar ferramenta, contra a decisão 13 e o A10 | As três referências entraram na T3 e o aceite da T4 foi restrito a plan e analyze |
| F6 | inconsistencia | MEDIUM | plan.md T4 e T3 | `vibe-analyze/templates/analyze.md` e `vibe-review/templates/review.md` mandam abrir a skill em chat novo, contra a delegação | Template do analyze entrou na T4 e a linha de Chat do template de review na T3 |
| F7 | qualidade_teste | HIGH | plan.md T6 | A1 e A2 constavam em `Spec:` da T6, mas a fixture já nascia com analyze aprovado, então nenhuma prova os exercitava | Rodada 0 adicionada: plan aprovado sem analyze, achado plantado, afirmação de `analyze.md` gravado e transcript do fechamento como evidência |
| F8 | constituicao | MEDIUM | plan.md T6 | O risco afirmava que o agente headless ficava "somente dentro da pasta temporária", o que o modo de permissão não garante | Reescrito: menor modo possível, `--allowedTools` e confirmação do modo com o humano antes da primeira execução |
| F9 | inconsistencia | MEDIUM | spec.md e interview.md | Decisão 2 e Resultado 1 diziam "plan no mesmo chat, como hoje", mas hoje o plan recomenda chat novo | Decisão do usuário (ver Clarificações): manter chat novo para o plan. Spec (Cobertura e decisão 2) e Resultado da interview corrigidos; trilha da interview ganhou a entrada 3 |
| F10 | constituicao | LOW | plan.md T5 | `AGENTS.md` atribui push só à `vibe-review`, mas no Modo A o coordenador do implement executa a finalização | A T5 ajusta a linha de Git do `AGENTS.md` para registrar que o coordenador executa a finalização da review após a confirmação |
| F11 | qualidade_teste | LOW | plan.md T3 | O aceite "nenhuma referência ao antigo Modo B" não tem comando executável, e o `AGENTS.md` proíbe teste de texto em skills | Mantido sem teste textual. A prova é a leitura da review e o comportamento na rodada de Modo B da T6 |

### F1: C4 sem T*

- **Gravidade:** MEDIUM
- **Categoria:** cobertura
- **Onde:** `plan.md` T5
- **Evidência:** campo `Spec:` da T5 listava só `A11; decisão 18`; C4 (suítes existentes continuam verdes) não aparecia em nenhuma T*
- **Resolução:** `Spec: A11, C4; decisão 18`

### F2: versão fixa em teste e README

- **Gravidade:** HIGH
- **Categoria:** furo
- **Onde:** `plan.md` T5
- **Evidência:** `docs/tests/test-distribuicao.py:24` (`CONTRACT_VERSION = "3.1.0"`, comparado com cinco manifestos) e `README.md:221` ("Versão dos manifests: `3.1.0`")
- **Resolução:** os dois arquivos entraram em Arquivos e no O quê da T5; o aceite diz que o `plugin.json` da raiz continua sem campo de versão

### F3: rodadas de correção com diferença de uma unidade

- **Gravidade:** HIGH
- **Categoria:** inconsistencia
- **Onde:** `plan.md` T1
- **Evidência:** a T1 contava etapas `Request changes`. Com 2 correções já feitas e a 3ª review ainda bloqueada, o contador marcaria 3, e com a 2ª correção ainda pendente marcaria 2 e `corrigir`, o mesmo valor que a spec trata como "parada"
- **Resolução:** `rodadas_correcao` conta correções aplicadas (cada `Request changes` exato soma 1, exceto a última etapa com Critical ou Required em `[ ]`). Para com `etapa` `corrigir` e valor 2, que é a regra da decisão 10

### F4: `Approve com defer` fora do `confirmar`

- **Gravidade:** MEDIUM
- **Categoria:** furo
- **Onde:** `plan.md` T1
- **Evidência:** `vibe-review/templates/review.md` oferece `Approve`, `Request changes` e `Approve com defer` em Veredito vigente
- **Resolução:** `confirmar` aceita `**Approve**` ou `**Approve com defer**`; a ausência de regra para o defer no `vibe-review` foi registrada em `.erros-encontrados/2026-10-03-review-approve-com-defer-sem-regra.md`

### F5: regras antigas de "não instalar"

- **Gravidade:** HIGH
- **Categoria:** inconsistencia
- **Onde:** `plan.md` T3 e T4
- **Evidência:** `vibe-implement/references/chrome-devtools.md:7,13`, `vibe-review/references/ui-visual-quality.md:7`, `vibe-design/references/kit-e-tokens.md:30`, além de `vibe-plan/SKILL.md:69` e `vibe-review/SKILL.md:108`, já cobertos
- **Resolução:** as três referências entraram na T3, com a seleção navegador integrado, `chrome-devtools` e Playwright preservada e a instalação sob a decisão 13 (registrar um MCP continua impedimento real)

### F6: linhas de Chat dos templates

- **Gravidade:** MEDIUM
- **Categoria:** inconsistencia
- **Onde:** `plan.md` T4 e T3
- **Evidência:** `vibe-analyze/templates/analyze.md:80` e `vibe-review/templates/review.md:99`
- **Resolução:** o template do analyze entrou nos Arquivos da T4; a linha de Chat do template de review entrou nos Arquivos da T3

### F7: A1 e A2 sem prova

- **Gravidade:** HIGH
- **Categoria:** qualidade_teste
- **Onde:** `plan.md` T6
- **Evidência:** a fixture da T6 já incluía "analyze aprovado e limpo"; A1 e A2 só são observáveis quando o chat do plan delega o analyze
- **Resolução:** rodada 0 com fixture separada. O teste afirma `analyze.md` gravado e o achado plantado corrigido no `plan.md`; o texto de fechamento fica registrado como evidência para leitura humana, sem asserção de frase

### F8: confinamento do agente headless

- **Gravidade:** MEDIUM
- **Categoria:** constituicao
- **Onde:** `plan.md` T6
- **Evidência:** o modo de permissão do `claude -p` define o que pede confirmação, não o diretório de trabalho
- **Resolução:** risco reescrito com menor modo possível, `--allowedTools` e confirmação humana do modo antes da primeira execução

### F9: plan no mesmo chat

- **Gravidade:** MEDIUM
- **Categoria:** inconsistencia
- **Onde:** `spec.md` (Cobertura e decisão 2) e `interview.md` (Resultado 1)
- **Evidência:** `AGENTS.md` tabela de continuidade (`spec/design → plan`: novo chat), handoffs de interview, spec e design
- **Resolução:** decisão do usuário nas Clarificações. Textos corrigidos; o item 0 da trilha foi mantido como registro do debate

### F10: push na linha de Git do AGENTS.md

- **Gravidade:** LOW
- **Categoria:** constituicao
- **Onde:** `plan.md` T5
- **Evidência:** `AGENTS.md`, seção Git: "`vibe-review` faz o commit residual e o `git push` final"
- **Resolução:** a T5 já altera o `AGENTS.md`; a linha de Git passa a registrar que o coordenador do Modo A executa a finalização da review após a confirmação humana

### F11: aceite sem comando executável

- **Gravidade:** LOW
- **Categoria:** qualidade_teste
- **Onde:** `plan.md` T3
- **Evidência:** aceite "nenhuma referência ao antigo Modo B permanece"; a regra do repo impede teste de presença de frases em `SKILL.md` e docs
- **Resolução:** sem alteração. A review confere por leitura e a rodada de Modo B da T6 prova o comportamento

## Clarificações com o Usuário

- Q: Mudar a recomendação do plan nesta phase (continuar no chat da spec) ou manter chat novo para o plan? -> A: ok, manter chat novo para o plan, conforme a recomendação (aplicado em `spec.md` e `interview.md`).

## Constituição

- Regra: testes de skill exercitam scripts e efeitos no disco, sem testar texto de `SKILL.md`, templates ou docs -> Resolução: C2 compara apenas bytes de cópias distribuídas, como a spec prevê; F11 mantém o aceite textual sem teste.
- Regra: segunda fonte de regras fora do `AGENTS.md` é proibida -> Resolução: a decisão 1 mantém o template do `vibe-init` intacto e a regra de delegação nas skills que delegam.
- Regra: `vibe-review` finaliza a phase com commit residual e push -> Resolução: F10.
- Regra: segurança e menor privilégio em execução automatizada -> Resolução: F8.
- Regra: versão major quando muda contrato que o humano já usa -> Resolução: A11 e T5 (4.0.0), com F2 para o teste que fixa a versão.

## Métricas

- A*/C* na spec: 15 (A1 a A11, C1 a C4)
- T* no plan: 6
- Cobertura (A*/C* com >= 1 T*): 15 / 15
- Qualidade de Testes: todas as T* têm comando executável (T1 suíte e launcher do implement com os motores reais; T2 distribuição; T3 suítes de implement e review; T4 suítes de plan e analyze; T5 todas as suítes e gitleaks; T6 `piloto-modo-a.py`). O ponto de entrada alterado na T1 é exercitado pelos motores nas suítes; o script do piloto da T6 é o próprio ponto de entrada executado. Ferramentas verificadas localmente: Python 3.13.14, PowerShell 7.6.6, gitleaks 8.30.1, Claude Code 2.1.250 com `-p`, `--plugin-dir`, `--permission-mode` e `--allowedTools`. Limitações registradas: a T6 não é determinística, consome tokens, não entra no CI e exige confirmação humana do modo de permissão antes da primeira execução.
- Achados corrigidos / resolvidos: 11 (F1 a F11; F11 sem alteração por regra do repo)
- Achados bloqueantes pendentes: 0

## Veredito

limpo

## Handoff

vibe-implement

- Chat: recomende novo chat para iniciar `vibe-implement`. Como o Modo A ainda não existe enquanto esta phase não for implementada, execute um chat por T* em sequência, conforme o `AGENTS.md`. Se o humano preferir continuar no mesmo chat, isso não bloqueia. O `analyze.md` e os artefatos vivos são a ponte.

- [x] Aprovação humana (leu o arquivo e confirmou)
