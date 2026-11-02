# Etapa interview

A interview abre a phase `high` ou o MVP (`references/disco.md`, Abrir phase ou MVP) e termina com a `spec.md` em rascunho, sem artefato próprio.

## Entrada

- Gate: rota `high` ou `mvp` e `spec.md` ausente no alvo (`references/disco.md`, Estado da phase). Com `spec.md` em rascunho, siga `references/spec.md`.
- O líder fixa no brief o alvo, a rota e, quando houver, o motivo de `# Risco:` (`references/disco.md`, Cabeçalho).
- Leia só o necessário para a próxima pergunta.

| Sinal | Modo |
|---|---|
| Documento, briefing, artigo, proposta ou texto em Markdown com intenção ambígua | Modo documento |
| Produto digital novo com escopo a descobrir | MVP; site institucional, landing page ou site estático com escopo claro segue a tabela de esforço |
| Mudança num produto existente | Phase |
| Dúvida real entre produto e feature | Perguntar uma vez, com recomendação |
| CI, loop ou agendado sem humano e pedido subespecificado | Bloquear, sem chutar |

Quem faz: o explorador mapeia e sonda, o líder abre o núcleo e conduz as perguntas, e o redator grava a `spec.md`.

## Passos

### 1. Explorar

Antes da primeira pergunta, o explorador mapeia o que o pedido toca: fluxos, consumidores, comportamento atual, bordas e testes existentes, com path e evidência; no MVP sem código, o estado do repositório e o que já existe de stack, design system e infraestrutura. Cada ponto relevante vira linha de Pontos do projeto, com o que implica.

Fato verificável (valor, limite de API, prazo, comportamento de biblioteca ou serviço, formato de dado) não é assumido nem perguntado: o explorador o sonda, só com leitura e consulta, e a evidência (comando ou fonte e resultado) entra em Pontos do projeto. Fato que só se prova implementando, ou que volta "não verificado", segue `references/spec.md` (Origem dos valores).

Ao mesmo tempo, o líder abre os itens do núcleo que o pedido toca (`references/delegation.md`, Delegar e colaborar) e pergunta a partir deles.

### 2. Perguntar

- Pergunte só o que o código e o pedido não decidem e que muda o resultado, nunca o já respondido. Pedido claro tem uma ou duas perguntas; ambíguo, até as decisões restantes serem previsíveis. No MVP, feche o núcleo e os módulos acionados de `references/interview/mvp-discovery.md`.
- Um turno por vez, neste formato:

```text
Anotei: <leitura fiel do pedido ou da última resposta, separando fato de hipótese>
**Pergunta:** <uma pergunta focada>
Opções: <duas ou três, cada uma com o impacto em uma linha>
**Recomendo:** <opção>, <motivo e impacto em uma linha>
```

- Sem base para recomendar, diga isso. Várias respostas de uma vez valem: registre tudo e siga com o que falta. "Tanto faz" crava a recomendação.
- Lacuna reversível e de baixo risco: o líder assume a recomendação, avisa e a registra como decisão assumida. Decisão cara, sensível, irreversível ou que altera a lógica central é perguntada; recomendação não é autorização.

### 3. Cobrir o que o pedido aciona

| Quando | Feche | Leia |
|---|---|---|
| Ajuste de tela existente | Decisões visuais: modo, tom, o que evitar, copy e as telas e estados a ver renderizados, em até duas perguntas | `references/spec/ui-visual-direction.md` |
| Tela nova, site ou fluxo novo | As mesmas, mais navegação, páginas e jornada da entrada à conclusão, sem limite de perguntas | `references/spec/ui-visual-direction.md` |
| Intenção clara e forma em aberto | Uma lente, opções e a direção recomendada | `references/interview/frameworks.md`, `references/interview/refinement-criteria.md` e, se preciso, `references/interview/examples.md` |
| Banco, persistência, valor monetário ou cálculo exato | Invariantes de dados, precisão e exemplos concretos com bordas (`references/spec.md`, Critérios de aceite) | `references/database-and-migrations.md` |
| Entrada externa (request, query, headers, arquivo) | Allowlist de campos e valores, tamanho máximo por entrada e o que o usuário vê na recusa | |
| Comportamento existente que a mudança arrisca | O que continua igual, como critério de preservação | |
| API, token, segredo, dado pessoal ou rota autenticada | Validade e invalidação de credenciais, autorização no servidor com anti-IDOR, rate limit, CSRF, CORS com allowlist (nunca `*` com credenciais), headers e CSP, com N/A fundamentado | |
| `# Risco:` | Modelo de ameaça (ativo, quem ataca, por onde, controle) e rollback (como desfazer, o que se perde, quem decide) | |
| MVP | Núcleo, módulos acionados, privacidade e jurídico | `references/interview/mvp-discovery.md` |

Proteção exigida sem decisão bloqueia a aprovação da spec.

### 4. Gravar

Com as perguntas fechadas, o líder entrega ao redator o alvo, a rota, o motivo de `# Risco:` quando houver, os pontos do explorador com a evidência das sondagens e as decisões com a pergunta de cada uma e a origem de cada valor (`references/spec.md`, Origem dos valores). O redator grava a `spec.md` por `references/spec.md` (Gravação).

## Modo documento

Sem phase, `spec.md` nem MVP. Pergunte no chat, no formato de turno acima, sobre público, objetivo, tom, tópicos essenciais e formato de saída, sem catálogo de infra ou banco. Feche com um restate curto e exija um sim claro; o restate confirmado orienta a edição direta, delegada ao redator.

## Fechar

Sem commit. A spec em rascunho segue `references/spec.md` (Fechar).
