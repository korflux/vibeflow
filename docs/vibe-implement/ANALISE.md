# vibe-implement, análise

## Problema e decisão

O coordenador acumulava seleção, implementação delegada, reconferência técnica, execução de provas, manutenção de snapshots e Git. Cada handoff era seguido de nova inspeção pelo coordenador, mesmo quando um responsável já tinha evidência suficiente. O plan também reunia planejamento, estado e histórico operacional, aumentando contexto e risco de duplicação.

O protocolo explícito coordenacao-v1 transforma coordenação em encaminhamento por resultado. Implementador investiga o fluxo e entrega código/testes juntos; verificador responde por conferir diff, ownership, cobertura e integração; corretor responde por falhas; revisor julga independentemente. Finalizador genérico/default apto recebe handoff operacional delimitado para registros/Git. Perfis específicos atuais continuam sem Git; não há instalação nova obrigatória nem renomeação de perfil para remover proibição.

Coordenador escolhe resultado, dependências, responsáveis e colaboração; recebe cobertura, exceções e próximo passo. Reconferência só entra diante de contradição ou decisão estratégica. Inventário e transições mecânicas ficam com os responsáveis, evitando que trocar o arquivo de estado preserve o mesmo operador central.

## Fluxo de ponta a ponta

```text
plan aprovado + modo → finalizador obtém resumo do motor
  → coordenador confere a capacidade de delegação (prontidão do plan ou host); perfil ausente → pergunta ao humano
  → coordenador seleciona entrega e colaboração útil
  → implementadores entregam código + testes + checagem local, por onda
  → verificador certifica a prova afetada de cada T*; finalizador registra o local da onda num único handoff; dependentes podem avançar
  → verificador confere entrega/aceite/cobertura e prova integração
  → falha concreta → corretor → verificador renova provas afetadas
  → finalizador registra integração e commit real
  → revisor independente julga origem, código e riscos
  → correção bloqueante → corretor ou redator pelo `papel` do R* → verificador/finalizador → nova review
  → coordenador apresenta resultado e pede confirmação humana única
  → finalizador fecha review/decisões autorizadas/Git/push
```

Não existe passagem obrigatória de complementar testes. O implementador cobre seu resultado; verificador identifica lacunas concretas de integração. Não se elimina teste necessário. As provas têm dois níveis, descritos em "Ondas e provas em dois níveis". A troca de etapa ou papel não justifica repetição; provas verdes de inputs inalterados são reaproveitadas. UI exige inspeção renderizada quando o aceite depender dela.

Simplificação, reutilização e remoção de redundância continuam no recorte autorizado. Otimização de desempenho cabe quando a necessidade for demonstrável, preservando comportamento, segurança e cobertura, sem abstração especulativa ou limpeza externa.

## Colaboração e independência

Colaboração depende de uma incerteza ou dependência que possa ser destravada. Exploração e preparação de recortes independentes podem ocorrer juntas, com interlocutores e comunicação técnica direta. Coordenador escolhe o arranjo e evita intermediar cada detalhe. Contexto relacionado é reutilizado; certificação/review continuam independentes dos escritores.

Um recurso compartilhado tem um dono por vez, inclusive arquivos operacionais e índice. Código paralelo ocorre somente em onda (próxima seção); fora dela segue um escritor por vez. A mudança não cria escritores concorrentes sobre o mesmo arquivo nem framework de orquestração.

## Ondas e provas em dois níveis

Em `coordenacao-v1` Modo A o coordenador avançava uma T* por vez mesmo quando o plan trazia T* independentes, e cada T* repetia verificação ampla e registro próprio. A phase 19 troca isso por ondas, com provas em dois níveis.

```text
motor: fila.onda (elegíveis de Arquivos: disjuntos) + fila.sem_arquivos
  → coordenador despacha a onda inteira numa rodada (implementadores em paralelo)
  → explorador prepara em leitura as T* que a onda libera
  → cada T* verde → verificador (Prova afetada:) sem esperar a onda; falha → corretor
  → finalizador registra as provas locais da onda num único handoff
  → coordenador consulta o motor uma vez → próxima onda
  → sem pendentes: verificador prova a união das provas afetadas → commit integrado → review
  → review final executa a Regressão completa, dona exclusiva da suíte inteira e do E2E completo
```

Decisões e porquês:

| Decisão | Porquê |
|---|---|
| Isolamento por disjunção de `Arquivos:`, sem worktree | O plan já declara os paths; o motor calcula a onda de forma determinística, e o coordenador não reconstrói a disjunção nem opera worktrees. |
| T* sem `Arquivos:` ou com sobreposição roda sozinha; expansão de path volta ao coordenador | Sem recorte conhecido não há dono exclusivo; serializar só a T* afetada preserva o paralelismo das demais. |
| O pedido de `/vibe-implement` com plan aprovado autoriza o paralelismo | A disjunção calculada pelo motor é o isolamento; não há decisão material pendente para o humano. |
| Registro em lote por onda | `execution.json` tem um escritor por vez; um handoff por onda evita uma rodada de finalizador por T*. |
| Implementador e verificador executam só a `Prova afetada:`, sem válvulas de ampliação | As válvulas por risco, consumidor, lacuna ou CI levavam a suíte ampla a cada T*, repetida a cada papel. Substitui a decisão 4 da phase 18 neste protocolo. |
| Regressão completa só na review final, repetida na re-review apenas se código ou teste mudou | A review é a única etapa sobre o estado integrado final; segurança, paridade e CI obrigatório ficam cobertos ali, uma vez. |

Fora desta mudança: worktree por T*, fan-out da review por dimensão e ajuste de esforço dos perfis. Modo B, `etapas-v1` e plans sem marcador conservam o fluxo e a regra de prova atuais; T* sem `Prova afetada:` (Express ou plan anterior) usa o recorte derivado de diff e consumidores diretos.

## Capacidade antes da onda e roteamento por papel

Vale somente em `coordenacao-v1` Modo A; Modo B, `etapas-v1` e plans sem marcador não mudam. A phase 20 alinha a cadeia ao coordenador. Sem conferir os perfis antes da primeira onda, uma onda podia sair sem verificador, redator ou finalizador apto e travar no meio. O plan agora registra a capacidade na prontidão; o coordenador a confere, ou a verifica no host quando o plan não a registra, e perfil ausente vira pergunta ao humano antes de qualquer despacho, porque instalar ou recarregar perfil depende do host e não é decisão da IA. Trocar o papel faltante por outro perfil quebraria as proibições de cada um, por isso não é fallback.

A review passa a marcar cada R* com `papel: corretor | redator`. Achado de prosa ia ao corretor, cujo perfil é código e testes; o campo deixa o roteamento explícito sem o coordenador reinterpretar o achado. R* sem o campo segue o remédio: plan, spec ou `AGENTS.md` são do finalizador, `review.md` é do revisor, e R* de reviews anteriores vai ao corretor, preservando o comportamento histórico. A conferência e o roteamento são passos da IA; o motor e o `execution.json` não mudam.

## Estado e retomada

Plan define trabalho e mostra resumo curto. execution.json versionado ao lado guarda somente estado atual por task, integração, origem e commit; Git/review guardam histórico. O motor captura hashes/HEAD, valida formato/paths/ancestralidade e troca arquivo atomicamente sem executar comandos informados como evidência. stdout é compacto; detalhes são consultados por quem precisa diagnosticar.

Isso evita JSON e logs em Markdown e duas fontes concorrentes de conclusão. Checkbox resume estado comprovado pelo motor. Ausência do `execution.json` significa pendente; corrupção bloqueia. Inputs alterados invalidam somente evidência afetada, sem refazer código válido. Cobertura semântica ainda pertence ao verificador, pois integridade do hash não prova completude do teste.

Registro do hash depois do commit pode deixar residual operacional; ele entra no fechamento final autorizado. Não se cria ciclo de commits para guardar o próprio hash.

## Compatibilidade e limites

Etapas-v1 conserva etapas de código/testes/validação e snapshots no plan. Legado conserva commit por task. B conserva ciclo individual, inclusive com marcador novo, sem `execution.json`. Runs existentes não migram implicitamente. O manual histórico é carregado somente quando o marcador/modo exigir; o fluxo principal permanece curto.

Express/texto avulso conserva a entrada proporcional e não cria phase/init para ajuste localizado. Falhas de prova exigem correção pela causa, enquanto decisões materiais e impedimentos reais chegam ao humano. Review tem no máximo duas rodadas de correção; aprovação/push continuam dependentes da confirmação final. O motor não interpreta intenção, certifica cobertura semântica nem opera Git de escrita.
