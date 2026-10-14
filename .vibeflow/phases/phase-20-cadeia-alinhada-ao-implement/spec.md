# Spec: Cadeia alinhada ao implement
# Alvo: phase-20-cadeia-alinhada-ao-implement
# Status: aprovado

## Objetivo

As skills da cadeia passam a girar em torno do contrato do `vibe-implement` em `coordenacao-v1` Modo A: init, spec, design, plan e analyze preparam o terreno de que o coordenador precisa para despachar ondas com segurança, e a review audita o que ele de fato executou. O coordenador age como líder que olha o macro: nenhuma execução é pedida sem que ferramentas, MCPs, privilégios e perfis de subagente tenham sido verificados antes. Sucesso é uma phase nova que chega ao implement com `Arquivos:` comparáveis no formato que o motor lê, provas em dois níveis executáveis e prontidão técnica com destino para cada requisito, e que fecha na review sem regressão impossível de reexecutar.

## Cobertura da origem

| Origem | Destino na spec | Motivo se fora/N/A |
|---|---|---|
| Bloqueante init: correção fora do recorte autorizada pelas regras geradas | F1, A1 | N/A |
| Bloqueante plan: formato literal de `Arquivos:` não declarado | F4, A8 | N/A |
| Bloqueante review: sync de decisões vigentes invalida a regressão na finalização | F7, decisão 6, A19 | N/A |
| Prontidão técnica: perfis, privilégios do SO, ferramentas da prova visual, forma verificável e destinos | F4, decisões 7 e 8, A9 | N/A |
| Implement não confere perfis antes da primeira onda | F6, A15 | N/A |
| Analyze cego ao contrato novo, sem dimensão de cobertura e com vocabulário antigo | F5, A13, A14 | N/A |
| Ajustes do plan: paths incomparáveis, arquivo compartilhado, T* de prosa, prova de prosa, placeholder, docs | F4, A10, A11, A12 | N/A |
| Ajustes da review: auditoria do executado, re-review, checkpoint, campo `papel`, §0, docs por protocolo, relatório, árvore suja | F7, A16, A17, A18, A20 | N/A |
| Ajustes do init: SLOT de comandos, perfis, re-init, regra vazada, linha Git, esforços | F1, A2, A3, A4, A5 | Troca de esforço fica fora; só a justificativa entra |
| Ajustes da spec: Como provar por jornada e nível, prova de UI sem ferramenta, consumidores por contrato | F2, A6 | N/A |
| Ajustes do design: commit por task, prova visual por tela, superfícies compartilhadas, viewport, fronteira de kit | F3, A7 | N/A |
| Notas de docs: `REGRAS.md` residual, diagrama sem ramo design, tabela Fontes sem `design.md`, contagem de passes | F2, F3, F5, C3 | N/A |
| Worktree por T*, fan-out da review, troca de modelo ou esforço, `strip()` vs `Trim()` | Fora | Decisão do humano ou já registrado |
| Push ao final | decisão 13 | Autorizado na confirmação humana final |

## Suposições e decisões

1. Rota high: intenção clara, achados fechados pelas auditorias e decisões do humano; execução toca o contrato de sete skills. Design N/A: não há UI visível. (processo)
2. Princípio do humano: o implement é o centro da cadeia. As skills anteriores estruturam o terreno para ele funcionar e a review revisa o que ele executou; um líder olha o macro e não pede execução sem o básico verificado. (produto, decisão do humano)
3. As mudanças de comportamento valem para `# Protocolo: coordenacao-v1`. Modo B, `etapas-v1` e plans sem marcador conservam o contrato atual, sem migração implícita; onde um texto precisar distinguir, ele é qualificado por protocolo. (escopo)
4. Erro encontrado fora do recorte nunca é corrigido por quem o encontrou: é registrado em `.erros-encontrados/` e reportado ao coordenador, ou ao humano quando não há coordenador. Vale para todo projeto gerado pelo init, porque a correção fora do recorte quebra o ownership das ondas. (processo)
5. O formato de `Arquivos:` que o plan exige é o que o motor da implement lê: uma linha física `- **Arquivos:**`, com cada path entre crases. Path incomparável (não ASCII, absoluto, com `:`, `<`, `>`, `"`, `|` ou segmento terminado em ponto ou espaço) serializa a T*; o plan avisa e recomenda renomear ou isolar. O motor da implement não muda nesta phase. Decidido na implementação: a regra do segmento terminado em ponto ou espaço exclui os segmentos `.` e `..`, que a normalização resolve; `.`, `./` e `..` que escapa da raiz valem como a raiz inteira. (processo)
6. O patch de `## Decisões vigentes` em `AGENTS.md`, aplicado na finalização após Approve e confirmação humana, não invalida a regressão completa verde: a comparação da finalização desconsidera essa alteração quando o diff de `AGENTS.md` se limita a essa seção. Qualquer outra mudança em `AGENTS.md` continua contando. (processo)
7. Prontidão técnica tem forma verificável: uma linha por requisito com onde ele está (local, CI ou host) e destino `ok`, `ação em T*`, `pergunta ao humano` ou `bloqueio`. Requisitos cobertos: ferramentas e runtimes, perfis de subagente exigidos pelo Modo A, privilégios e capacidades do SO (por exemplo symlink no Windows, portas, serviços, rede) e ferramentas da prova visual quando houver `Visual: necessária`. (processo)
8. Destinos da prontidão: instalável sem credencial nem elevação vira ação na primeira T* dependente; existente só no CI vira prova no CI; perfil ausente ou não carregado, MCP persistente, privilégio do SO ou credencial vira pergunta ao humano com recomendação (perfil: rodar `/vibe-init` e recarregar o host; host sem subagentes: handoff anuncia Modo B); sem equivalente vira bloqueio, nunca verde. Perfis exigidos no Modo A: explorador, implementador, verificador, corretor, revisor, finalizador genérico apto a Git, e redator somente quando houver T* de prosa. (processo)
9. Achado de review ganha campo `papel: corretor | redator`; a implement roteia R* de prosa ao redator e o restante ao corretor. Decidido na implementação: `papel: redator` vai ao redator e `papel: corretor` ao corretor; R* sem `papel` com remédio em plan, spec ou `AGENTS.md` vai ao finalizador, e com remédio em `review.md` ao revisor; R* histórico sem `papel` vai ao corretor. O redator edita só a prosa dos `Arquivos:` delegados, nunca plan, spec, review ou `AGENTS.md`. (produto)
10. No Modo A não existe checkpoint de review: o plan não o promete e a review não o executa, porque a review final cobre a phase inteira. Protocolos históricos mantêm checkpoint. (processo)
11. Os esforços diferentes entre hosts nos perfis distribuídos permanecem; a phase apenas registra a justificativa onde o contrato do init a documenta. (escopo, decisão do humano)
12. Versão major 9.0.0: campos novos na prontidão do plan e no R* da review, mudança do papel da finalização e do checkpoint e a regra de erros fora do recorte alteram contrato que o humano e outras skills usam. (processo)
13. Ao final, com Approve e confirmação humana, a phase segue a finalização da vibe-review com push sem force. O humano autorizou o fluxo até a review sem novas paradas, exceto essa confirmação final. (processo, decisão do humano)
14. Spec aprovada pela autorização do humano em 2026-10-14 ("pode abrir a fase 20"), dada em resposta à proposta de abrir esta phase e seguir até a review sem novas paradas, exceto a confirmação final para push. (processo, decisão do humano)
15. No Modo B de `coordenacao-v1`, o plan ainda pode declarar checkpoint de review; somente o Modo A não tem checkpoint. Decidido pelo coordenador na implementação, como recorte da decisão 10. (processo)
16. `Prova afetada:` é derivada de `Como provar` da spec: nível `jornada` gera o E2E do cenário, e nível `local` gera os testes do módulo e dos consumidores diretos. O plan lê `Superfícies compartilhadas` e `Prova visual esperada` do design. Decidido pelo coordenador na implementação. (processo)

## Escopo e comportamento

Todos os fluxos abaixo são de agente sobre artefatos em disco; UI N/A. A superfície de cada passo é inline no artefato vivo, no relatório fixo da delegação ou no chat do coordenador. Validações de entrada externa N/A: as skills leem somente artefatos locais do repositório.

### 1. Fluxo F1: init prepara regras e perfis para as ondas

- Jornada: inicializar ou reparar a governança de um projeto que vai rodar `coordenacao-v1`.
- Rota: vibe-init.
- Gatilho: `/vibe-init` em projeto novo ou existente.
- Pré-condição: nenhuma além do repositório.
- Superfície por passo: inline em `AGENTS.md` gerado, nos perfis distribuídos e no chat do init.
- Passos:
  1. Init gera a regra de erros fora do escopo -> registrar em `.erros-encontrados/` e reportar, sem corrigir fora do recorte [superfície: inline].
  2. Init gera o SLOT de comandos -> pede, quando existirem, comando por recorte (arquivo, módulo ou filtro), suíte completa, E2E, varredura de segredos, CI obrigatório e onde cada um roda [superfície: inline].
  3. Init distribui perfis alinhados ao implement -> implementador entrega código e testes juntos, escreve só em `Arquivos:` e prova só a `Prova afetada:`; verificador prova só a afetada por T*, integração é a união e não amplia; revisor executa a `Regressão completa` na review final; redator não edita plan, spec, review nem `AGENTS.md`; o parágrafo comum lista os oito campos do relatório fixo [superfície: inline].
  4. Em re-init de projeto existente -> init propõe patch da seção Git do `AGENTS.md` e distingue perfil VibeFlow desatualizado (substituído com backup) de customização do usuário (preservada e reportada) [superfície: chat].
- Validações: regra de testes própria do repositório VibeFlow não entra no `AGENTS.md` de outros projetos; regras Git geradas em frases curtas.
- Erros: recusas atuais do init permanecem.
- Estados: init novo, re-init com perfis atuais, re-init com perfis desatualizados, re-init com customização.
- Aceite: A1, A2, A3, A4, A5.
- Reutilizar: backup com hash do init e distribuição atual de perfis.

### 2. Fluxo F2: spec entrega aceite provável por jornada

- Jornada: definir comportamento e aceite de uma entrega.
- Rota: vibe-spec.
- Gatilho: `/vibe-spec`.
- Pré-condição: `.vibeflow/` existente.
- Superfície por passo: inline em `spec.md`.
- Passos:
  1. Spec escreve Como provar -> cada A* aponta o F* ou jornada que o exerce e o nível (`jornada` ou `local`), sem comando nem ferramenta [superfície: inline].
  2. Spec com UI descreve a evidência renderizada observável -> a ferramenta fica para o plan [superfície: inline].
  3. Spec pode registrar F* consumidores de um contrato compartilhado quando a mudança afeta mais de um fluxo [superfície: inline].
- Validações: Como provar sem comando, path de teste ou ferramenta.
- Erros: N/A, a skill não emite erro novo.
- Estados: spec rascunho, spec aprovada.
- Aceite: A6.
- Reutilizar: template atual da spec.

### 3. Fluxo F3: design entrega insumo de prova visual ao plan

- Jornada: definir a UI visível depois da spec.
- Rota: vibe-design.
- Gatilho: `/vibe-design` com UI visível.
- Pré-condição: spec aprovada.
- Superfície por passo: inline em `design.md`.
- Passos:
  1. Design registra a prova visual por tela -> insumo do `Visual:` e da `Prova afetada:` da T* que toca a tela, em uma única casa [superfície: inline].
  2. Design registra Superfícies compartilhadas -> telas afetadas por componente ou token comum, reconferidas na review [superfície: inline].
  3. Design declara a viewport em que o aceite é julgado -> viewport estreita só quando houver regra responsiva [superfície: inline].
  4. Design sinaliza que kit, tokens e componentes comuns precedem as telas -> fronteira de ordem para o plan [superfície: inline].
- Validações: commit segue o protocolo do plan, sem promessa de commit por task.
- Erros: N/A, a skill não emite erro novo.
- Estados: design rascunho, design aprovado.
- Aceite: A7.
- Reutilizar: template atual do design.

### 4. Fluxo F4: plan entrega fila executável em ondas

- Jornada: fatiar a spec em T* que o coordenador despacha.
- Rota: vibe-plan.
- Gatilho: `/vibe-plan` com spec (e design, quando houver) aprovados.
- Pré-condição: plan novo em `coordenacao-v1`.
- Superfície por passo: inline em `plan.md`.
- Passos:
  1. Plan declara o formato literal de `Arquivos:` lido pelo motor -> uma linha física, paths entre crases, nada relevante fora delas [superfície: inline].
  2. Plan avisa path incomparável -> recomenda renomear ou isolar, porque a T* será serializada [superfície: inline].
  3. Plan concentra arquivo compartilhado entre T* sem `Deps` (versão, README, índices) numa T* final com `Deps` e separa testes por recorte [superfície: inline].
  4. Plan separa prosa de código para o redator, ou marca o resultado principal da T* mista com paths distinguíveis [superfície: inline].
  5. Plan declara `Prova afetada:` como comandos mais a evidência visual declarada; em T* só de prosa, a suíte do consumidor contratual ou uma checagem mecânica, nunca teste de presença de palavras [superfície: inline].
  6. Plan registra a prontidão técnica conforme decisões 7 e 8 e anuncia Modo B no handoff quando o host não tem subagentes [superfície: inline].
  7. Plan no Modo A não promete checkpoint de review [superfície: inline].
- Validações: placeholder do template sem caractere que torne o path incomparável; docs da skill coerentes com o parser que lê `Arquivos:`.
- Erros: requisito de prova sem destino impede o plan de se declarar pronto.
- Estados: plan rascunho, plan aprovado.
- Aceite: A8, A9, A10, A11, A12.
- Reutilizar: estrutura de T*, `Deps`, `Arquivos:`, `Prova afetada:` e `Regressão completa` atuais.

### 5. Fluxo F5: analyze confere o contrato da implement

- Jornada: portão da rota max antes do implement.
- Rota: vibe-analyze.
- Gatilho: `/vibe-analyze` com plan em disco.
- Pré-condição: plan existente.
- Superfície por passo: inline em `analyze.md`.
- Passos:
  1. Analyze confere `# Protocolo: coordenacao-v1`, `Arquivos:` válido em toda T* (uma linha, crases, comparável), sobreposição de `Arquivos:` entre T* sem `Deps`, `Prova afetada:` executável restrita ao recorte e cobrindo os A*/C* da T*, `Regressão completa` única com comandos reais e a prontidão técnica [superfície: inline].
  2. Analyze classifica os achados na dimensão nova de cobertura -> HIGH para `Regressão completa` ausente, `Prova afetada:` ausente ou com suíte inteira, sobreposição sem `Deps` cuja ordem importa, requisito de prova sem destino e perfil não verificado quando o plan promete Modo A; MEDIUM para T* sem `Arquivos:` ou com path incomparável [superfície: inline].
  3. Correção direta proposta pelo analyze nunca grava a suíte inteira como `Prova afetada:` de uma T* [superfície: inline].
- Validações: vocabulário de provas em dois níveis; contagem de passes coerente; `design.md` na tabela de fontes.
- Erros: achado HIGH bloqueia o avanço conforme a regra atual de gravidade.
- Estados: analyze sem achados, com achados, aprovado.
- Aceite: A13, A14.
- Reutilizar: catálogo de cobertura atual e regra de gravidade.

### 6. Fluxo F6: implement confere a capacidade antes de despachar

- Jornada: executar a fila no Modo A.
- Rota: vibe-implement.
- Gatilho: etapa `implementar` antes da primeira onda.
- Pré-condição: plan aprovado em `coordenacao-v1` Modo A.
- Superfície por passo: chat do coordenador.
- Passos:
  1. Coordenador confere a capacidade de delegação registrada na prontidão do plan, ou a verifica no host -> perfil ausente vira pergunta ao humano antes da primeira onda [superfície: chat].
  2. Coordenador roteia R* com `papel: redator` ao redator e os demais ao corretor [superfície: chat].
- Validações: nenhuma onda despachada com perfil exigido ausente.
- Erros: perfil ausente ou não carregado volta ao humano com recomendação conforme decisão 8.
- Estados: capacidade confirmada, pergunta pendente.
- Aceite: A15.
- Reutilizar: papéis e relatório fixo atuais.

### 7. Fluxo F7: review audita o que o implement executou

- Jornada: review final e re-review no Modo A.
- Rota: vibe-review delegada pelo coordenador.
- Gatilho: integração commitada.
- Pré-condição: `execution.json` válido.
- Superfície por passo: inline em `review.md` e relatório do revisor.
- Passos:
  1. Revisor lê o estado pelo comando de leitura do motor da implement indicado na skill [superfície: inline].
  2. Revisor confere que os inputs de cada T* em `execution.json` estão dentro do seu `Arquivos:`, que o diff da phase está dentro da união dos `Arquivos:` (fora abre R* Required) e que consumidor compartilhado entre T* da mesma onda continua coerente [superfície: inline].
  3. Revisor confere que cada A* está coberto pela `Prova afetada:` registrada ou pela regressão completa, e que a integração contém os inputs locais [superfície: inline].
  4. Revisor executa a regressão completa e relata comando, resultado e HEAD; árvore suja pede isolamento ao coordenador [superfície: inline].
  5. Em re-review, revisor confere `correcao.commit` não nulo, descendente e com IDs iguais aos R* marcados; reaproveita a prova afetada certificada pelo verificador e repete a regressão só se código ou teste mudou [superfície: inline].
  6. Cada R* registra `papel: corretor | redator` [superfície: inline].
  7. Na finalização, o patch de decisões vigentes não invalida a regressão, conforme decisão 6 [superfície: inline].
- Validações: no modo subagente, defeito do motor encontrado no §0 vira bloqueio ou R*, nunca correção pelo revisor; ARQUITETURA, ANALISE e template qualificados por protocolo (`execution.json` no Modo A, plan nos históricos; quem marca R* é o responsável de registro).
- Erros: diff fora da união dos `Arquivos:` é R* Required; `correcao.commit` inválido bloqueia Approve.
- Estados: review em andamento, request changes, Approve proposto, finalização.
- Aceite: A16, A17, A18, A19, A20.
- Reutilizar: matriz de cobertura, regras de R* e comparação da finalização atuais.

### Fora

- Worktree por T*: decisão do humano; disjunção de `Arquivos:` atende.
- Fan-out da review por dimensão: decisão do humano.
- Troca de modelo ou esforço dos perfis existentes: só a justificativa entra.
- Divergência `strip()` vs `Trim()` no motor da implement: já registrada em `.erros-encontrados/`.
- Mudança no parser de `Arquivos:` ou no schema do `execution.json`: a phase adapta a cadeia ao motor atual.
- Migração de Modo B, `etapas-v1` ou plans sem marcador.

## Checklist de entrega

### Aceite

- [ ] A1: O `AGENTS.md` gerado pelo init proíbe corrigir erro fora do recorte e manda registrar em `.erros-encontrados/` e reportar ao coordenador ou ao humano.
- [ ] A2: O SLOT de comandos do `AGENTS.md` gerado pede comando por recorte, suíte completa, E2E, segredos, CI obrigatório e onde cada um roda, quando existirem.
- [ ] A3: Os perfis distribuídos para Claude e Codex descrevem implementador, verificador, revisor e redator conforme o F1 passo 3, e o parágrafo comum lista os oito campos do relatório fixo.
- [ ] A4: Em re-init com perfil VibeFlow desatualizado, o init o substitui com backup verificado; com perfil customizado pelo usuário, preserva e reporta; e propõe patch da seção Git do `AGENTS.md`.
- [ ] A5: O `AGENTS.md` gerado para outro projeto não contém a regra de testes própria do VibeFlow, a regra Git é escrita em frases curtas e a justificativa dos esforços por host está registrada.
- [ ] A6: A spec liga cada A* ao F* ou jornada e ao nível, sem comandos, e a direção visual descreve evidência renderizada sem ferramenta.
- [ ] A7: O design não promete commit por task, registra prova visual por tela como insumo da T*, Superfícies compartilhadas, viewport de julgamento e a precedência de kit e tokens.
- [ ] A8: O plan declara o formato literal de `Arquivos:` lido pelo motor, avisa path incomparável e o placeholder do template é comparável.
- [ ] A9: A prontidão técnica do plan tem uma linha por requisito com local e destino e cobre perfis, privilégios do SO e ferramentas da prova visual, com destinos conforme decisão 8.
- [ ] A10: O plan concentra arquivo compartilhado numa T* final com `Deps` e separa prosa de código para o redator.
- [ ] A11: `Prova afetada:` reúne comandos e evidência visual; em T* só de prosa, usa suíte do consumidor contratual ou checagem mecânica.
- [ ] A12: O plan no Modo A não promete checkpoint, e os docs da skill descrevem o parser que lê `Arquivos:` sem vocabulário obsoleto.
- [ ] A13: O analyze confere protocolo, `Arquivos:`, sobreposição sem `Deps`, `Prova afetada:`, `Regressão completa` e prontidão técnica, com a dimensão nova e as gravidades da F5.
- [ ] A14: O analyze não usa "provas proporcionais", não propõe suíte inteira numa T*, conta os passes corretamente e lista `design.md` nas fontes.
- [ ] A15: A implement confere a capacidade de delegação antes da primeira onda e roteia R* de prosa ao redator.
- [ ] A16: A review confere inputs por T* dentro de `Arquivos:`, diff dentro da união e consumidor compartilhado na mesma onda, abrindo R* Required para diff fora.
- [ ] A17: A review liga cada A* à prova afetada registrada ou à regressão e relata comando, resultado e HEAD da regressão; árvore suja pede isolamento.
- [ ] A18: A re-review confere `correcao.commit`, reaproveita a prova certificada e só repete a regressão se código ou teste mudou; R* traz `papel`.
- [ ] A19: A finalização não exige nova regressão por causa do patch de `## Decisões vigentes` em `AGENTS.md`.
- [ ] A20: No Modo A a review não executa checkpoint, o §0 delegado não corrige o motor, e ARQUITETURA, ANALISE e template da review são qualificados por protocolo.

### Critérios de sucesso

- [ ] C1: Suítes de contrato de todas as skills, distribuição e contrato visual verdes, e cópias de `delegation.md` idênticas.
- [ ] C2: Versão 9.0.0 nos manifestos versionáveis.
- [ ] C3: Docs de spec, design e analyze sem `REGRAS.md` como fonte viva, diagrama da ANALISE da spec com o ramo design.
- [ ] C4: Modo B, `etapas-v1` e plans sem marcador mantêm o comportamento atual.

## Contratos e restrições necessárias

- Dados e invariantes: `execution.json` e o parser de `Arquivos:` do motor da implement permanecem inalterados; a cadeia se adapta a eles.
- Integrações e interfaces: campos novos são a linha de prontidão (requisito, local, destino) no plan e `papel` no R* da review; demais contratos inalterados.
- Segurança e operação: credencial, MCP persistente e privilégio do SO nunca são obtidos pelo agente, sempre perguntados ao humano; requisito sem equivalente é bloqueio, nunca verde. Entrada externa N/A: as skills leem artefatos locais.
- Tecnologia imposta: motores gêmeos Python 3 e PowerShell 7 com o mesmo contrato quando algum motor mudar.

## Como provar

| Aceite | Evidência esperada |
|---|---|
| A1, A2, A5 | F1, nível jornada: init em pasta isolada gera `AGENTS.md` com as regras e o SLOT descritos, sem a regra própria do VibeFlow |
| A3, A4 | F1, nível jornada: init em pasta isolada instala os perfis nos dois hosts; re-init substitui perfil desatualizado com backup e preserva o customizado |
| A6 | F2, nível local: leitura do SKILL e do template da spec na review |
| A7 | F3, nível local: leitura do SKILL e do template do design na review |
| A8, A10, A11, A12 | F4, nível local: leitura do SKILL, template e docs do plan na review; placeholder do template comparável pelo motor da implement |
| A9 | F4, nível local: template e SKILL do plan com a forma e os destinos da prontidão |
| A13, A14 | F5, nível local: leitura do SKILL, de `coverage.md` e dos docs do analyze na review |
| A15 | F6, nível local: leitura do SKILL e de `delegation.md` da implement na review |
| A16, A17, A18, A20 | F7, nível local: leitura do SKILL, template e docs da review na review |
| A19 | F7, nível local: regra de comparação da finalização da review que desconsidera somente a seção de decisões vigentes |

## Boundaries

### Always

- Adaptar a cadeia ao contrato atual do motor da implement.
- Qualificar por protocolo todo texto que mude comportamento só no Modo A.

### Ask first

- Mudar o parser de `Arquivos:` ou o schema do `execution.json`.

### Never

- Testar presença de palavras em SKILL, template, referência ou documentação.
- Marcar verde requisito de prontidão sem equivalente.
- Permitir correção fora do recorte em nome da rapidez.

## Handoff

vibe-plan

- Chat: sem UI visível; recomende novo chat para `vibe-plan`. Se o humano preferir, continuar no mesmo chat não bloqueia. O `spec.md` vivo é a ponte.

- [x] Aprovação humana (leu o arquivo e confirmou)
