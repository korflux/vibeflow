# Spec: Coordenação por ondas e testes em dois níveis
# Alvo: phase-19-coordenacao-por-ondas-e-testes-em-dois-niveis
# Status: aprovado

## Objetivo

O coordenador do Modo A em `coordenacao-v1` passa a conduzir a fase por ondas: despacha em paralelo todas as T* elegíveis cujos arquivos não se sobrepõem, encadeia preparação, verificação e registro, e deixa de avançar uma T* por vez. As provas passam a ter dois níveis: implementação e verificação executam somente o que a mudança afetou, e a review final é a única dona da regressão completa, incluindo E2E. Sucesso é uma fase com várias T* independentes concluída em menos rodadas de delegação e sem suíte completa por T*, mantendo integração verde, review independente e regressão completa antes do Approve.

## Cobertura da origem

| Origem | Destino na spec | Motivo se fora/N/A |
|---|---|---|
| Coordenador que coordena em paralelo, não "a próxima e a próxima" | F2, A1, A2 | N/A |
| Organização: dono por arquivo, sem colisão entre T* paralelas | F1, F2, A1 | N/A |
| Implement testa só o afetado, unitário ou E2E | F3, A4 | N/A |
| Review testa tudo | F4, A5 | N/A |
| Review direcionada ao que foi afetado | F4, A5 | Julgamento de código limitado ao diff e consumidores |
| Paralelismo pendente em `docs/ESCOPO.md` (worktree, `Arquivos:` obrigatório, disjunção) | F1, F2, decisão 3 | Worktree por T* fica fora |
| Fan-out da review por dimensão | Fora | Decisão do humano |
| Esforço dos perfis de subagent | Fora | Decisão do humano |
| Push ao final | Decisão 9 | Autorizado pelo humano nesta conversa |
| Coordenador como líder que delega, planeja e valida dados | F2, decisão 11 | N/A |
| Subagente de modelo superior para raciocínio e escrita de documentos | decisão 12, A7 | N/A |

## Suposições e decisões

1. Rota high: intenção clara e decisões fechadas pelo humano; execução toca dois motores gêmeos e o contrato de três skills. Design N/A: não há UI visível. (processo)
2. Vale somente para `# Protocolo: coordenacao-v1` com `# Modo: A`. Modo B, `etapas-v1` e plans sem marcador conservam o contrato atual, sem migração. (escopo)
3. Isolamento por disjunção de `Arquivos:`. Sem worktree nesta phase. T* com arquivos sobrepostos serializam entre si; as demais seguem em paralelo. (produto, decisão do humano)
4. O motor calcula a onda de forma determinística a partir de `Deps` e `Arquivos:`; o coordenador não precisa reconstruir a disjunção. O motor não interpreta prosa nem decide semântica. (processo)
5. Plan novo declara em toda T* `Arquivos:` e `Prova afetada:`, e declara uma única vez `Regressão completa` com os comandos da suíte inteira e do E2E completo. (produto, decisão do humano)
6. Implementador e verificador executam somente a prova afetada: testes do módulo tocado e dos consumidores diretos; E2E somente do cenário da jornada cuja entrada mudou. As válvulas de ampliação por risco, consumidores ou lacuna deixam de valer nesses papéis. Substitui, para coordenacao-v1 Modo A, a decisão 4 da phase 18. (produto, decisão do humano)
7. A review final executa sempre a regressão completa, uma vez, no estado integrado final. Rodada de correção prova o afetado; a regressão completa só é repetida antes do Approve quando código ou teste mudou desde a última execução completa verde. Segurança, paridade e CI obrigatório ficam cobertos pela regressão completa. (produto, decisão do humano)
8. O julgamento de código da review continua limitado ao diff e aos consumidores afetados; a cobertura da origem continua obrigatória. (produto)
9. Ao final, com Approve e confirmação humana, a phase segue a finalização da vibe-review com push sem force. O humano já autorizou o push desta phase. (processo)
10. Mudança quebra contrato usado pelo humano e por outras skills (campos obrigatórios no plan, papel da review). Versão major. (processo)
11. O coordenador do Modo A atua como líder estratégico: reconhece o terreno, planeja as ondas, delega toda execução (código, testes, provas, registros, Git) e valida os dados recebidos (relatórios fixos, motor, `git status`); no máximo faz pequenos ajustes finais. (processo, decisão do humano durante a implementação)
12. Novo papel `redator`, com modelo de maior capacidade de raciocínio (Opus no Claude; no Codex, o mesmo modelo do `revisor`), para T* cujo resultado principal é prosa (SKILL, referências, docs, README, artefatos). Distribuído pelo vibe-init junto dos demais perfis. (produto, decisão do humano durante a implementação)

## Escopo e comportamento

### F1: Plan declara arquivos e provas por T*

- Jornada: fatiar a spec em T* executáveis em paralelo.
- Rota: vibe-plan.
- Gatilho: plan novo em `coordenacao-v1`.
- Pré-condição: spec aprovada.
- Superfície por passo: artefato `plan.md` (inline no arquivo vivo); UI N/A.
- Passos:
  1. Plan registra em cada T* `Arquivos:` com os paths que a T* pode escrever, incluindo testes -> o motor da implement passa a ler a lista [superfície: inline].
  2. Plan registra em cada T* `Prova afetada:` com os comandos que provam somente o recorte -> implementador e verificador usam esses comandos [superfície: inline].
  3. Plan registra uma vez `Regressão completa` com a suíte inteira e o E2E completo do repo -> a review final usa esse comando [superfície: inline].
- Validações: path relativo ao repo; diretório ou curinga vale como prefixo; ausência de `Arquivos:` não bloqueia a fase, mas a T* só roda sozinha.
- Erros: N/A no plan; o efeito da ausência aparece no relatório da implement (F2).
- Estados: plan rascunho, plan aprovado.
- Aceite: A3.
- Reutilizar: estrutura atual de T*, `Deps` e prontidão das provas do plan.

### F2: Coordenador despacha ondas

- Jornada: executar a fila da phase.
- Rota: vibe-implement, Modo A.
- Gatilho: etapa `implementar` no relatório do motor.
- Pré-condição: plan aprovado em `coordenacao-v1` Modo A.
- Superfície por passo: relatório JSON do motor e chat do coordenador; UI N/A.
- Passos:
  1. Motor relata `fila.onda` -> lista de T* elegíveis, em ordem numérica, cujos `Arquivos:` não se sobrepõem entre si [superfície: inline no relatório].
  2. Motor relata `fila.sem_arquivos` -> T* elegíveis sem `Arquivos:`; cada uma só forma onda sozinha [superfície: inline no relatório].
  3. Coordenador delega todas as T* da onda a implementadores em paralelo, numa única rodada de delegação -> cada implementador recebe ownership exclusivo dos seus `Arquivos:` [superfície: inline no chat].
  4. Enquanto a onda implementa, explorador prepara em leitura o contexto das T* que a onda vai liberar [superfície: inline no chat].
  5. Cada T* que volta verde segue ao verificador com a prova afetada, sem esperar o restante da onda; falha segue ao corretor sem bloquear as demais T* da onda [superfície: inline no chat].
  6. Finalizador registra em um único handoff as provas locais de todas as T* concluídas da onda -> coordenador consulta o motor uma vez e despacha a próxima onda [superfície: inline no chat].
  7. Sem T* pendentes, verificador certifica a integração com a união das provas afetadas, finalizador cria o commit integrado e o coordenador delega a review [superfície: inline no chat].
- Validações: sobreposição quando dois paths são iguais ou um é prefixo de diretório do outro, com comparação sem diferenciar maiúsculas e com separador normalizado; curinga vale como o prefixo até o primeiro curinga; implementador que precisar de path fora dos seus `Arquivos:` reporta antes de editar.
- Erros: `EXECUTION_INVALIDO` e demais recusas atuais do motor permanecem; expansão de path fora do recorte volta ao coordenador, que serializa a T* afetada.
- Estados: onda em execução, T* verificada, T* em correção, onda registrada, fila sem pendentes.
- Aceite: A1, A2.
- Reutilizar: `fila.elegiveis`, `execution.json`, operação `local` existente e papéis atuais.

### F3: Provas afetadas na implementação e verificação

- Jornada: provar cada T* e a integração.
- Rota: vibe-implement, Modo A.
- Gatilho: T* implementada ou corrigida.
- Pré-condição: `Prova afetada:` declarada na T*.
- Superfície por passo: relatório fixo da delegação; UI N/A.
- Passos:
  1. Implementador executa a prova afetada da T* -> registra comando e resultado no relatório [superfície: inline].
  2. Verificador executa a prova afetada no estado integrado da T* -> certifica sem ampliar para suíte completa [superfície: inline].
  3. Integração final executa a união das provas afetadas das T* da phase [superfície: inline].
- Validações: E2E somente do cenário cuja entrada mudou; mudança posterior renova somente a prova afetada.
- Erros: prova vermelha volta ao corretor; nunca enfraquecer, pular ou apagar teste.
- Estados: prova local verde, integração verde, prova invalidada.
- Aceite: A4.
- Reutilizar: snapshots de inputs do `execution.json`.

### F4: Review dona da regressão completa

- Jornada: review final e re-review.
- Rota: vibe-review delegada pelo coordenador.
- Gatilho: integração commitada.
- Pré-condição: `Regressão completa` declarada no plan.
- Superfície por passo: `review.md` e relatório do revisor; UI N/A.
- Passos:
  1. Revisor julga o diff da phase e os consumidores afetados -> registra achados [superfície: inline em `review.md`].
  2. Revisor executa a regressão completa no estado final -> registra comando, resultado e HEAD [superfície: inline em `review.md`].
  3. Em re-review, revisor prova o afetado pela correção e repete a regressão completa somente se código ou teste mudou desde a última execução completa verde [superfície: inline em `review.md`].
- Validações: Approve exige regressão completa verde sobre o código final.
- Erros: falha da regressão completa abre `R*` obrigatório com comando e remédio.
- Estados: review em andamento, request changes, Approve proposto.
- Aceite: A5.
- Reutilizar: matriz de cobertura da origem e regras de R* atuais.

### Fora

- Worktree por T* — decisão do humano; disjunção de arquivos atende esta phase.
- Fan-out da review por dimensão — decisão do humano.
- Ajuste de esforço ou modelo dos perfis existentes de subagent — decisão do humano.
- Mudança no schema do `execution.json` — o registro em lote usa a operação `local` existente.
- Migração de Modo B, `etapas-v1` ou plans sem marcador.

## Checklist de entrega

### Aceite

- [ ] A1: Em `coordenacao-v1` Modo A, o relatório do motor traz `fila.onda` com as T* elegíveis de arquivos disjuntos e `fila.sem_arquivos`; T* sobreposta ou sem `Arquivos:` não divide onda com outra. Python e PowerShell emitem o mesmo resultado.
- [ ] A2: A vibe-implement instrui o coordenador a despachar a onda inteira numa rodada, encadear explorador, verificador e corretor por T* e registrar a onda em um único handoff do finalizador.
- [ ] A3: A vibe-plan e seu template exigem `Arquivos:` e `Prova afetada:` por T* e `Regressão completa` uma vez por plan novo.
- [ ] A4: Implementador e verificador executam somente a prova afetada, sem válvula de ampliação para suíte completa.
- [ ] A5: A review final executa sempre a regressão completa e só a repete na re-review quando código ou teste mudou desde a última execução completa verde.
- [ ] A6: Modo B, `etapas-v1` e plans sem marcador mantêm relatório e comportamento atuais.
- [ ] A7: O vibe-init distribui o perfil `redator` para Claude e Codex junto dos demais; a vibe-implement e a delegação roteiam T* de prosa ao `redator`.

### Critérios de sucesso

- [ ] C1: Suítes de contrato de todas as skills, distribuição, MVP e reparse verdes; cópias de `delegation.md` idênticas.
- [ ] C2: Versão major nos manifestos versionáveis e `docs/ESCOPO.md` com o item de paralelismo marcado, registrando worktree e fan-out como pendentes.

## Contratos e restrições necessárias

- Dados e invariantes: `execution.json` mantém o schema atual; `fila.onda` é subconjunto ordenado de `fila.elegiveis`.
- Integrações e interfaces: campos novos `fila.onda` e `fila.sem_arquivos` somente no relatório de `coordenacao-v1` Modo A; demais campos inalterados.
- Segurança e operação: o motor lê `Arquivos:` como texto, sem resolver, abrir ou executar paths; comandos de prova continuam dados, nunca autorização. Entrada externa N/A além do plan local, que já é lido pelo motor.
- Tecnologia imposta: motores gêmeos Python 3 e PowerShell 7 com o mesmo contrato.

## Como provar

| Aceite | Evidência esperada |
|---|---|
| A1 | Teste de contrato com plan de fixture: T* disjuntas na mesma onda, sobrepostas separadas, prefixo de diretório e curinga como sobreposição, T* sem `Arquivos:` sozinha; mesma saída no motor PowerShell |
| A2 | Leitura da SKILL e de `delegation.md` na review |
| A3 | Leitura da SKILL e do template do plan na review |
| A4 | Leitura da SKILL, `delegation.md` e `definition-of-done.md` na review |
| A5 | Leitura da SKILL da vibe-review na review |
| A6 | Testes de contrato existentes de Modo B e protocolos históricos verdes, sem `onda` no relatório |
| A7 | Suíte do init instala e confere o sexto perfil nos dois hosts; leitura da SKILL e de `delegation.md` na review |

## Boundaries

### Always

- Manter um dono por arquivo durante a onda.
- Manter integração verde, commit real e review independente antes do Approve.

### Ask first

- Expandir o paralelismo para T* com arquivos sobrepostos.

### Never

- Paralelizar escrita em T* com `Arquivos:` sobrepostos ou ausentes.
- Pular a regressão completa na review final.

## Handoff

vibe-plan

- Chat: sem UI visível; recomende novo chat para `vibe-plan`. Se o humano preferir, continuar no mesmo chat não bloqueia. O `spec.md` vivo é a ponte.

- [x] Aprovação humana (leu o arquivo e confirmou)
