# Etapa interview

## Entrada

- Gate: nenhum. Em `xhigh`, `max` e MVP, a interview abre a phase (`references/disco.md`, Abrir phase ou MVP). Phase aberta do mesmo assunto é retomada no `interview.md` vivo.
- MVP: MVP aberto é retomado no `interview.md` vivo; MVP fechado (`references/disco.md`, Estado da phase) é baseline: ajuste segue `references/implement.md` (Ajuste de phase), e mudança que altera decisão ou comportamento abre phase `max` com substituição explícita.
- Leia somente o necessário para a próxima pergunta: o pedido, o artefato vivo e as entradas citadas. Leitura ampla vai ao explorador.

Declare em cerca de cinco linhas: hipótese, confiança, modo, alvo e estado do artefato vivo.

```text
HIPÓTESE: produto novo para organizar solicitações internas
CONFIDENCE: ~35%, faltam público, jornada e operação
modo: mvp · alvo: .vibeflow/mvp/ · artefato vivo: ausente
```

| Sinal | Modo |
|---|---|
| Typo, rename, pedido inequívoco, velocidade pedida ou pergunta informativa | Não entrevistar |
| Documento, briefing, artigo, proposta ou texto em Markdown | Modo documento: entrevista no chat, focada em público, tom, dor e estrutura, sem phase, sem MVP e sem catálogo de infra ou banco; o restate confirmado orienta a edição direta |
| `/vibeflow interview` explícito | Entrevistar |
| Produto digital novo com escopo a descobrir | MVP; site institucional, landing page ou site estático com escopo claro segue a tabela de esforço, sem MVP |
| Mudança delimitada num produto existente | Phase |
| Dúvida real entre produto e feature | Perguntar uma vez, com recomendação |
| CI, loop ou agendado sem humano e pedido subespecificado | Bloquear, sem chutar |

## Quem faz

| Quem | Faz |
|---|---|
| Líder | Conduz cada turno com o humano, mantém a trilha e confirma o restate |
| Redator | Cria ou atualiza `interview.md` a partir da trilha e do restate |
| Finalizador | Marca a aprovação |

## Passos

### Entrevista

1. Um turno por vez, nesta ordem:
   - `Anotei:` uma frase fiel sobre o pedido ou a última resposta, separando o confirmado da hipótese, sem dar a entender que algo foi salvo.
   - `**Pergunta:**` uma única pergunta focada, em linha própria.
   - `**Meu guess (GUESS):**` a resposta provisória mais provável, ancorada no que o humano disse ou em evidência do projeto, com motivo curto e baixa confiança indicada quando a base for limitada.
   - O convite: “`sim` confirma somente este guess; você também pode corrigi-lo ou responder de outro jeito.”
2. Não invente base para o palpite. Sem evidência, diga isso; guess de baixa confiança só para hipótese reversível. Em decisão sensível, legal, cara ou irreversível, guess não é autorização.
3. Com intenção clara e forma em aberto, leia `references/interview/frameworks.md`, `references/interview/refinement-criteria.md` e, se necessário, `references/interview/examples.md`; use uma lente, gere opções e recomende uma direção.
4. No modo documento, concentre-se em público, objetivo, tom, tópicos essenciais e formato de saída.
5. Com UI e tom em aberto, no máximo duas perguntas visuais, uma por turno. Não feche CSS.
6. Quando conseguir prever as próximas três reações, apresente o restate curto: o quê, pra quem, por quê, sucesso, limite, fora e visual ou formato quando aplicável. Exija um sim claro; “o que você achar melhor” permite recomendar e assumir, mas “parece bom” ou “bora” ainda pede confirmação direta.

```text
Anotei: <leitura fiel do pedido ou da resposta anterior>
**Pergunta: <uma pergunta focada>**
**Meu guess (GUESS):** <resposta provisória + motivo curto e, se necessário, confiança>
“Sim” confirma somente este guess; também pode corrigi-lo ou responder de outro jeito.
```

Várias respostas de uma vez são válidas: registre tudo e feche os gaps restantes sem repetir perguntas.

### Módulo MVP

Leia `references/interview/mvp-discovery.md` somente no MVP. Feche primeiro o núcleo (solicitação, solução imaginada, jornadas e páginas) e depois os módulos de completude acionados.

1. Comece por produto, público, dor, resultado e funcionamento esperado, uma pergunta principal por turno, sem lista de pendências.
2. Aceite “não sei”. Lacuna reversível e de baixo risco recebe o padrão mais adequado, com recomendação e impacto, registrada como `ASSUMIDO`. Decisão irreversível, cara, sensível ou que altere a lógica central é perguntada.
3. Na Cobertura, cada módulo fica `DECIDIDO`, `ASSUMIDO`, `N/A` ou `PENDENTE CRÍTICO`, com evidência. Não encerre com pendente crítico.
4. Decisões críticas estáveis recebem IDs por domínio, como `AUTH-01`, `DATA-01` e `INFRA-01`, com opção, estado, motivo e impacto.
5. Segurança entra desde o início. Recuperação administrativa pode usar break-glass temporário e auditado via ambiente; nunca senha master permanente.
6. No Mapa do produto, jornada essencial sem saída, estado crítico ou caminho de navegação não fecha.

O MVP prefere uma primeira versão pequena e operável. Minimalismo não autoriza cortar validação, segurança, acessibilidade, backup ou recuperação necessários.

### Gravação

Depois do sim ao restate, o líder entrega ao redator a trilha ANOTEI/Q/GUESS/R, o restate, o modo, a rota e o path do alvo. O redator cria o `interview.md` a partir de `templates/interview.md`, ou atualiza o vivo, preserva Solicitação e Trilha, grava `# Rota:` quando a interview abre a phase e mantém `# Status: rascunho`. No MVP, preenche também Cobertura, Mapa do produto, Direção técnica, Direção visual, Operação e Decisões críticas; no modo phase, omite essas seções.

## Saída

`<alvo>/interview.md` em rascunho, com a ordem de aprovação fixa:

1. O redator grava o `interview.md`.
2. O líder apresenta o path e um resumo factual, e o humano lê.
3. Ajuste pedido pelo humano volta ao redator, e o ciclo retorna ao passo 2.
4. Com o sim final do humano, o finalizador marca `# Status: aprovado`.

## Fechar e próxima etapa

Handoff padrão: `spec`. Sem commit nesta etapa. A spec só começa com autorização explícita, como “pode ir pro spec”.
