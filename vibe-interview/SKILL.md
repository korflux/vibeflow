---
name: vibe-interview
description: >
  Esclarece pedidos quando a intenção, o funcionamento ou o resultado esperado ainda não estão claros, inclusive briefings de documentos. Registra as decisões em `.vibeflow/phases/phase-N-slug/interview.md` ou `.vibeflow/mvp/interview.md` para baseline de software. Use when the user runs /vibe-interview, pede para refinar uma ideia ou a IA não tem confiança suficiente para definir a entrega, mesmo que não diga vibe-interview.
---

# vibe-interview

Não invente `n`, slug ou path. Sem `.vibeflow/`, pare e mande `/vibe-init`. Não grave em `docs/` nem na raiz.
Um MVP usa `.vibeflow/mvp/` uma única vez por repo. Nunca sobrescreva esse baseline nem transforme uma feature posterior em continuação dele.

A investigação começa pela pergunta ainda aberta e pelo fluxo real que precisa ser entendido. Use `rg --files` para localizar o artefato vivo, referências e entradas citadas; use `rg -n` para localizar nomes, símbolos e decisões relacionadas. Abra somente o contexto necessário para formular a próxima pergunta e expanda a leitura quando uma lacuna bloquear o fechamento. O inventário é mapa de seleção, não autorização para ler a árvore inteira.


## 0. Entender e usar o script

1. Resolva o diretório desta skill e leia o motor que vai executar: `scripts/interview.ps1` no Windows ou `scripts/interview.py` no fluxo Unix. Entenda flags, JSON operacional no stdout, recusas, preparação do destino e preservação do arquivo vivo antes de chamá-lo. Se encontrar defeito, corrija o motor e prove o contrato antes de continuar.
2. No cwd do repo:
   - Windows: `pwsh "<skill>/scripts/interview.ps1"`.
   - Unix: `bash "<skill>/scripts/interview.sh"`.
   - Modo MVP: acrescente `-Mvp` ou `--mvp`.
3. Leia o JSON operacional emitido no stdout pelo comando acima. Use `rg --files` e `rg -n` para localizar o alvo indicado em `alvo`, as referências e os paths citados pelo humano. Abra somente as entradas e dependências que sustentam a pergunta atual.

`INIT_AUSENTE` exige `/vibe-init`. `PHASES_INESPERADO`, `MVP_INESPERADO` e `MODO_INVALIDO` não são contornados.

## 1. Abrir

Declare em cerca de cinco linhas: hipótese, confiança, modo, alvo e estado do artefato vivo.

```text
HIPÓTESE: produto novo para organizar solicitações internas
CONFIDENCE: ~35%, faltam público, jornada e operação
modo: mvp · alvo: ausente · artefato vivo: ausente
```

No modo phase, `aberta` e o pedido atual são o mesmo assunto: edite o `interview.md` vivo. Assunto diferente exige nova fase. O `--apply` apenas prepara o alvo quando ele ainda não existe.
No modo MVP, `.vibeflow/mvp/interview.md` existente é baseline fechado. Mudança posterior vira phase max com substituição explícita, nunca novo apply MVP.

## 2. Gate e seleção do modo

| Sinal | Ação |
|---|---|
| Typo, rename, pedido inequívoco, velocidade pedida ou pergunta informativa | Não entrevistar |
| Documento, briefing, artigo, proposta ou texto em Markdown | Usar modo phase (entrevista focada em público, tom, dor e estrutura; **não** acionar modo MVP de software nem catálogo de infra/banco) |
| `/vibe-interview` explícito | Entrevistar |
| Produto digital novo, incluindo app, sistema, site institucional, landing page ou site estático cujo escopo ainda precisa ser descoberto | Usar modo MVP |
| Mudança delimitada num produto existente | Usar modo phase |
| Dúvida real entre produto e feature | Perguntar uma vez, com recomendação |
| CI, loop ou agendado sem humano e pedido subespecificado | Bloquear, sem chutar |

Se já existe baseline MVP em `.vibeflow/mvp/`, qualquer alteração posterior deve ser conduzida como phase max, nunca sobrescrevendo o MVP existente.



## 3. Entrevista normal

Artefato vivo: `<created.path>/interview.md`. Use `templates/interview.md` e preserve Solicitação e Trilha. Mantenha as interações em sequência para gravar ANOTEI/Q/GUESS/R no arquivo vivo após a confirmação do restate (§5). Mantenha `# Status: rascunho` enquanto a entrevista estiver em elaboração.

1. Conduza um turno por vez e apresente os itens nesta ordem:
   - `Anotei:` no chat, uma frase fiel sobre o pedido inicial ou a resposta que acabou de receber. Separe o que o humano confirmou do que ainda é hipótese; não dê a entender que o arquivo já foi salvo.
   - `**Pergunta:**` uma única pergunta focada, em linha própria e visualmente destacada.
   - `**Meu guess (GUESS):**` a resposta provisória mais provável, ancorada no que o humano disse ou em evidência do projeto. Dê um motivo curto e indique baixa confiança quando a base for limitada.
   - Convide a pessoa a responder: “`sim` confirma somente este guess; você também pode corrigi-lo ou responder de outro jeito.” Use um único GUESS por turno para deixar claro a que “sim” se refere.
   - Não invente base para o palpite. Se ainda não houver evidência suficiente, diga isso; só ofereça guess de baixa confiança para uma hipótese reversível. Em decisão sensível, legal, cara ou irreversível, não trate guess como autorização ou decisão.
2. Quando intenção estiver clara e apenas a forma estiver aberta, leia `references/frameworks.md`, `references/refinement-criteria.md` e, se necessário, `references/examples.md`. Use uma lente, gere opções e recomende uma direção.
3. Se o foco for documento/conteúdo: concentre-se no público-alvo, objetivo do texto, tom de voz, tópicos essenciais e formato de saída.
4. Se houver UI e o tom estiver aberto, faça no máximo duas perguntas visuais, uma por turno no formato acima. Não feche CSS detalhado nesta rota normal.
5. Quando conseguir prever as próximas três reações, apresente o restate curto: o quê, pra quem, por quê, sucesso, limite, fora e visual/formato quando aplicável.
6. Exija um sim claro para confirmar o restate final. Delegação como “o que você achar melhor” permite recomendar e assumir; “parece bom” ou “bora” ainda pede confirmação direta do recap.

Formato do turno no chat e da entrada correspondente em `Trilha`:

```text
Anotei: <leitura fiel do pedido ou da resposta anterior>
**Pergunta: <uma pergunta focada>**
**Meu guess (GUESS):** <resposta provisória + motivo curto e, se necessário, confiança>
“Sim” confirma somente este guess; também pode corrigi-lo ou responder de outro jeito.
```

Várias respostas de uma vez são válidas: registre tudo e feche os gaps restantes sem repetir perguntas.

## 4. Módulo MVP

Leia `references/mvp-discovery.md` somente no modo MVP, inclusive para sites novos. Primeiro feche o núcleo: solicitação, solução imaginada, jornadas e páginas. Depois escolha os módulos de completude pelo gatilho e leia apenas os arquivos indicados; não transforme os módulos em formulário.

1. Comece por produto, público, dor, resultado e funcionamento esperado.
2. Faça uma pergunta principal por turno, no formato de `Anotei`, `Pergunta` e `Meu guess` definido na entrevista normal. Não exiba uma lista de pendências. Adapte a próxima pergunta às respostas anteriores.
3. Aceite “não sei”. Para lacuna reversível e de baixo risco, escolha o padrão mais adequado, informe recomendação e impacto e registre como `ASSUMIDO`. Pergunte diretamente decisões irreversíveis, caras, sensíveis ou que alterem a lógica central.
4. Para cada recomendação, diga a escolha, por que serve a este caso e o impacto. Mencione contra apenas quando ele puder mudar a decisão ou a arquitetura.
5. Depois do núcleo, confira os gatilhos dos módulos. Na Cobertura, marque cada módulo como `DECIDIDO`, `ASSUMIDO`, `N/A` ou `PENDENTE CRÍTICO`, com evidência; aprofunde apenas os aplicáveis. Não encerre com pendente crítico.
6. Identifique decisões críticas estáveis com IDs por domínio, por exemplo `AUTH-01`, `DATA-01` e `INFRA-01`. Registre opção, estado, motivo e impacto.
7. Segurança entra desde o início. Recuperação administrativa pode usar break-glass temporário e auditado via ambiente. Nunca recomende senha master permanente.
8. No Mapa do produto, registre jornadas e páginas/telas nas tabelas do template. Fluxo essencial sem saída, estado crítico ou caminho de navegação não fecha. Registre as decisões dos módulos aplicáveis nas seções correspondentes, sem duplicar a trilha.

O módulo prefere uma primeira versão pequena e operável, sem empurrar arquitetura sofisticada. Minimalismo não autoriza cortar validação, segurança, acessibilidade, backup ou recuperação necessários.

## 5. Restate e gravação

Depois do sim explícito, prepare o destino com `--apply` e salve imediatamente no artefato vivo.

Modo phase:

```text
pwsh "<skill>/scripts/interview.ps1" -Apply -Slug "<slug>"
bash "<skill>/scripts/interview.sh" --apply --slug "<slug>"
```

Modo MVP, sem slug:

```text
pwsh "<skill>/scripts/interview.ps1" -Apply -Mvp
bash "<skill>/scripts/interview.sh" --apply --mvp
```

No MVP, preencha também Cobertura, Mapa do produto, Direção técnica, Direção visual, Operação e Decisões críticas no artefato vivo. No modo normal, omita todas essas seções.

Leia `created.path` no JSON do stdout e apresente o caminho do arquivo vivo no chat com resumo factual. `SLUG_INVALIDO`, `FASE_EXISTE`, `MVP_EXISTE` e `MODO_INVALIDO` exigem diagnosticar a causa e executar novamente. Não crie arquivo auxiliar para contornar o motor.

## 6. Fechar

Handoff padrão é `vibe-spec` (ou geração direta do texto/documento se o objetivo for puramente editorial/conteúdo). Para MVP de software, registre também `rota: max`. `init → interview → spec → design` pode continuar no mesmo chat. Recomende novo chat ao iniciar `vibe-plan`; se o humano preferir ficar, continue e use o `interview.md` e os demais artefatos vivos como ponte.
Não commite no git. Não dispare a próxima etapa a menos que o usuário tenha autorizado explicitamente o avanço (ex.: "pode ir para a próxima fase", "segue pro spec", "pode gerar").
