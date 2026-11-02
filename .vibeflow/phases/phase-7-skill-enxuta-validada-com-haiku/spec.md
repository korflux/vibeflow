# Spec: Skill enxuta validada com Haiku
# Alvo: phase-7-skill-enxuta-validada-com-haiku
# Status: aprovado
# Rota: high

## Objetivo

O líder e os analistas da skill `vibeflow` passam a carregar menos texto por etapa sem perder regra nem qualidade de condução. A entrega remove cópias de fatos, leva cada papel a ler só a referência dele e enxuga o bloco da cadeia que todo consumidor carrega em toda sessão. Sucesso é a carga por papel cair ao menos 30% e o modelo Haiku, conduzindo como líder, acertar na 5.5.0 todo cenário que acerta na 5.4.0.

## Pontos do projeto

- Medição: chars/4 por script Node sobre o working tree em HEAD `f3fce47`; é proxy e serve para comparar antes e depois pelo mesmo método.
- Pacote `skills/vibeflow/`: 45 arquivos de texto e 40.517 tokens; `SKILL.md` 3.250, `references/disco.md` 3.876, `references/delegation.md` 2.724.
- Carga por papel na 5.4.0, em tokens: líder sempre 3.250 e 5.974 com `delegation.md`; explorador 5.974; implementador por passo 2.706 (já lê só `references/implementador.md`); verificador 9.530; redator de spec 11.602; redator de plan 12.932; revisor de analyze 12.880; revisor de review 14.972; líder numa phase high completa 21.003 em 10 arquivos.
- Perfis em `skills/vibeflow/templates/agents/claude/*.md` e `codex/*.toml`: explorador, redator, verificador e revisor leem o `SKILL.md` inteiro, do qual só as seções 4 e 5 servem a eles.
- Cópias maiores: bloco de identidade nos 10 perfis (2.131 tokens); bloco `VIBEFLOW:CADEIA` idêntico em `AGENTS.md` e `templates/AGENTS.md` (cerca de 860 por cópia); commits e staging em cerca de 10 lugares além de `disco.md` (Commits); checklist do analyze em `analyze.md:21-28` e `analyze/coverage.md`; Ajuste de phase; regra do checkpoint em cinco lugares; origem dos valores; Docker nos testes; encadeamento pós-aprovação.
- Trechos raros carregados sempre: `SKILL.md` seções 6 e 7 (Modo B); `implement.md:67-86` Ajuste de phase (cerca de 845); `disco.md` Compatibilidade e Backup (só init e diagnóstico); `testes.md` Ambiente local (só init e plan).
- `AGENTS.md` da raiz: 5.270 tokens em toda sessão deste repo; trechos que repetem o pacote: topo e cadeia 718, seção 6 619, Estrutura 540, seção 2 449, seção 3 391, Limites 254, Continuidade 247, Git 159. `templates/AGENTS.md`: 1.963, dos quais Padrões e Segurança 577, que não repetem a skill.
- `scripts/governanca.mjs:92` acusa bloco `VIBEFLOW:CADEIA` diferente do template, e `references/init.md:26` o substitui com backup: o bloco novo chega aos consumidores pelo init.
- Histórico: a phase-4 cortou 29,3% e gerou contradição entre gate da review e regra de commit (`phase-4-fluxo-enxuto-v5/review.md:34`); depois o pacote cresceu 19,5% porque ponteiros entraram sem apagar a cópia.
- Teste com Haiku: `claude auth status` deste shell devolve loggedIn false e não há `ANTHROPIC_API_KEY`; o despacho de subagente da sessão aceita o modelo `haiku`. O repo não tem harness, e a seção 8 do `AGENTS.md` proíbe teste que confira palavras.
- A cópia instalada em `~/.agents/skills/vibeflow` é igual ao repo, salvo fim de linha (diff com `--strip-trailing-cr` sem saída).

## Decisões

1. Corte por redundância, prosa e carga por papel: cada fato com uma casa, prosa em tabela quando couber; explorador, redator, verificador e revisor leem uma referência curta do próprio papel em vez do `SKILL.md` inteiro, como o implementador; Ajuste de phase, Compatibilidade, Backup e Modo B saem do caminho de leitura de toda etapa; versão minor 5.5.0 (origem: humano). Pergunta: qual o alcance do corte? Motivo: maior economia por run sem tirar regra.
2. O Haiku testa por 5 a 8 cenários fixos de condução (origem: humano): classificar rota, recusar etapa sem pré-requisito, abrir phase com n e slug certos, despachar papel, montar mensagem de commit, retomar pelo disco e entrar no Modo B; cada um num repo Git temporário fora do repo, com subagente Haiku como líder, na 5.4.0 e na 5.5.0; resultado e comparação na `review.md`; nenhum harness entra no repo. Pergunta: como o Haiku testa? Motivo: base comparável sem estrutura nova e dentro da seção 8 do `AGENTS.md`.
3. Aprovação exige queda de ao menos 30% na carga por papel (origem: humano), medida por chars/4 antes e depois, e todo cenário certo na 5.4.0 certo na 5.5.0. Cenário que já falha na 5.4.0 vira achado: texto corrigido se a causa for ambiguidade da skill, registrado se for limite do modelo. Pergunta: qual o critério de aprovação? Motivo: protege qualidade sem prender a phase a limite do modelo.
4. O bloco `VIBEFLOW:CADEIA` entra no corte: fica a tabela de esforço, fonte única das rotas, e os sinais que tiram do low; o resto vira uma linha que aponta para a skill; meta de cerca de 350 tokens (origem: assumida); este repo e cada consumidor o recebem pelo init. Pergunta: o bloco da cadeia entra no corte? Motivo: é o único custo presente em toda sessão do consumidor, mesmo sem `/vibeflow`.
5. O `AGENTS.md` deste repo fica só com o que é exclusivo dele (projeto, núcleo, comandos, semver, regras de pacote, scripts e template, tom, verificação, ordem de mudança e limites sem repetição); o que tem casa no pacote vira ponteiro; meta de cerca de 2.000 tokens (origem: humano). No `templates/AGENTS.md` muda só o bloco da cadeia. Pergunta: como tratar os dois `AGENTS.md`? Motivo: Padrões e Segurança orientam consumidores sem regras globais.
6. Uma referência por papel, `references/<papel>.md`, no padrão de `references/implementador.md`, com os perfis claude e codex apontando para ela; o bloco de identidade fica no perfil, encurtado, porque é o prompt do subagente. Pergunta: um arquivo de referência por papel ou um compartilhado? Motivo: assumida; cada papel carrega só o seu.
7. Toda cópia removida sai no mesmo passo em que o ponteiro entra, e gates e regras de commit são conferidos entre si na revisão de consistência. Pergunta: como evitar repetir o erro das phases 4 e 6? Motivo: assumida; o histórico mostra contradição e crescimento quando a cópia fica.
8. O teste usa a cópia do repo: HEAD para a base 5.4.0 e working tree para a 5.5.0; atualizar a cópia instalada fica com o humano via `npx skills add`. Pergunta: qual cópia o teste usa? Motivo: assumida; a instalada não reflete a mudança em curso.

## Critérios de aceite

- A1: Na 5.5.0, a carga de cada papel (líder sempre, explorador, implementador, verificador, redator de spec e de plan, revisor de analyze e de review) e a soma do líder numa phase high completa estão ao menos 30% abaixo dos valores da 5.4.0 em Pontos do projeto, pelo mesmo método (origem: humano).
- A2: Cada fato de regra tem uma única casa no pacote, e nenhuma das cópias listadas em Pontos do projeto aparece mais como cópia.
- A3: Os perfis de explorador, redator, verificador e revisor, nos dois hosts, mandam ler a referência do próprio papel e não o `SKILL.md` inteiro.
- A4: O bloco da cadeia do `templates/AGENTS.md` e deste repo contém a tabela de esforço, os sinais que tiram do low e um ponteiro para a skill, e não passa de 400 tokens (origem: assumida).
- A5: O `AGENTS.md` deste repo não passa de 2.200 tokens (origem: assumida) e não repete regra que tem casa no pacote.
- A6: Com os mesmos cenários e o mesmo modelo; quando o Haiku conduz na 5.5.0, todo cenário que passou na 5.4.0 passa, e a comparação está na `review.md`.
- A7: Com o disco e os artefatos das phases 1 a 6; quando os scripts os leem na 5.5.0, aceitam-nos como na 5.4.0, e a suíte de scripts passa.
- A8: Num consumidor com o bloco da cadeia da 5.4.0; quando o init roda, acusa o bloco desatualizado e o substitui com backup.
- A9: Nenhuma regra de gate, commit, encadeamento, checkpoint ou Modo B muda de comportamento, e o contrato de disco (paths, nomes de artefato e linhas de cabeçalho) segue igual.
- A10: A versão 5.5.0 está registrada no `AGENTS.md`, e o `README.md` diz que consumidores rodam `/vibeflow init` para receber o bloco novo.

## Fora do escopo

- Cortar ou reescrever `interview/frameworks.md`, `refinement-criteria.md`, `examples.md`, `database-and-migrations.md` e `review/security-and-hardening.md`: tiram conteúdo de banco e segurança; pode virar outra phase se o teste mostrar que não fazem falta.
- Padrões e Segurança do `templates/AGENTS.md`: base para consumidores sem regras globais.
- Harness de eval versionado no repo: contraria a seção 8 do `AGENTS.md`.
- Atualizar a cópia instalada da skill: fica com o humano.
- Corrigir o validador de `.erros-encontrados/validador-generico-rejeita-frontmatter-vibeflow.md`: sem relação com o corte.

- [x] Aprovação humana (leu o arquivo e confirmou): 2026-11-01, "Aprovado"
