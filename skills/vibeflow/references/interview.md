# Etapa interview

A interview abre a phase `high` e o MVP e termina com a `spec.md` em rascunho. Ela não grava artefato próprio.

## Entrada

- Gate: rota `high` ou `mvp` e `spec.md` ausente no alvo (`references/disco.md`, Estado da phase). A interview abre a phase ou o MVP (`references/disco.md`, Abrir phase ou MVP). Com `spec.md` em rascunho, siga `references/spec.md`.
- O líder fixa no brief o alvo, a rota e, quando houver, o motivo de `# Risco:` (`references/disco.md`, Cabeçalho).
- Leia só o necessário para a próxima pergunta. Leitura ampla do código vai ao explorador.

| Sinal | Modo |
|---|---|
| Documento, briefing, artigo, proposta ou texto em Markdown com intenção ambígua | Modo documento |
| Produto digital novo com escopo a descobrir | MVP; site institucional, landing page ou site estático com escopo claro segue a tabela de esforço, sem MVP |
| Mudança num produto existente | Phase |
| Dúvida real entre produto e feature | Perguntar uma vez, com recomendação |
| CI, loop ou agendado sem humano e pedido subespecificado | Bloquear, sem chutar |

## Quem faz

| Quem | Faz |
|---|---|
| Explorador | Mapeia o que o pedido toca no código, antes da primeira pergunta |
| Líder | Conduz as perguntas, uma por vez, e decide o que assumir |
| Redator | Grava a `spec.md` com os pontos e as decisões entregues |

## Passos

### 1. Explorar

O líder delega ao explorador o mapa do que o pedido toca: fluxos, consumidores, comportamento atual, bordas e testes existentes, cada um com path e evidência. No MVP sem código, o mapa registra o estado do repositório e o que já existe de stack, design system e infraestrutura. Cada ponto relevante vira linha de Pontos do projeto, com o que implica.

### 2. Perguntar

- Pergunte a partir dos pontos: o que o código e o pedido não decidem e que muda o resultado. Não pergunte o que já está respondido.
- Tamanho proporcional à clareza: pedido claro tem uma ou duas perguntas; pedido ambíguo tem mais, até as decisões restantes serem previsíveis. No MVP, feche o núcleo e os módulos acionados de `references/interview/mvp-discovery.md`.
- Um turno por vez, neste formato:

```text
Anotei: <leitura fiel do pedido ou da última resposta, separando fato de hipótese>
**Pergunta:** <uma pergunta focada>
Opções: <duas ou três, cada uma com o impacto em uma linha>
**Recomendo:** <opção>, <motivo e impacto em uma linha>
```

- Sem base para recomendar, diga isso. Várias respostas de uma vez são válidas: registre tudo e siga só com o que falta. "Tanto faz" crava a recomendação.
- Lacuna reversível e de baixo risco: o líder assume a recomendação, avisa e a registra como decisão assumida. Decisão cara, sensível, irreversível ou que altera a lógica central é perguntada; recomendação não é autorização.

### 3. Cobrir o que o pedido aciona

| Quando | Feche | Leia |
|---|---|---|
| Tela nova ou alterada | Decisões visuais do humano: modo, tom, o que evitar, copy e as telas e estados a ver renderizados, em no máximo duas perguntas | `references/spec/ui-visual-direction.md` |
| Intenção clara e forma em aberto | Uma lente, opções e a direção recomendada | `references/interview/frameworks.md`, `references/interview/refinement-criteria.md` e, se necessário, `references/interview/examples.md` |
| Banco, persistência, valor monetário ou cálculo exato | Invariantes de dados e precisão | `references/database-and-migrations.md` |
| Entrada externa (request, query, headers, arquivo) | Allowlist de campos e valores e tamanho máximo por entrada | |
| API, token, segredo, dado pessoal ou rota autenticada | Validade e invalidação de credenciais, autorização no servidor com anti-IDOR, rate limit, CSRF, CORS com allowlist (nunca `*` com credenciais), headers e CSP, com N/A fundamentado | |
| `# Risco:` | Modelo de ameaça (ativo, quem ataca, por onde, controle) e rollback (como desfazer, o que se perde, quem decide) | |
| MVP | Núcleo, módulos acionados, privacidade e jurídico | `references/interview/mvp-discovery.md` |

Proteção exigida sem decisão bloqueia a aprovação da spec.

### 4. Gravar

Com as perguntas fechadas, o líder entrega ao redator o alvo, a rota, o motivo de `# Risco:` quando houver, os pontos do explorador e as decisões com a pergunta que originou cada uma. O redator grava a `spec.md` conforme `references/spec.md`, Gravação.

## Modo documento

Sem phase, sem `spec.md` e sem MVP. Pergunte no chat, no formato de turno acima, sobre público, objetivo, tom, tópicos essenciais e formato de saída, sem catálogo de infra ou banco. Feche com um restate curto e exija um sim claro; o restate confirmado orienta a edição direta, delegada ao redator.

## Fechar

Sem commit nesta etapa. A spec em rascunho segue `references/spec.md`, Fechar.
