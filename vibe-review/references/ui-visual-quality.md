# Qualidade Visual e Interface (Rubrica de Auditoria)

Abrir sempre que o diff alterar elementos visuais, layouts, componentes de UI ou fluxos web vistos no navegador.

Julgar com inspeção factual. Não assuma que a interface está correta sem verificação visual. Toda anomalia real vira `R*` bloqueante (`Required`). Remédio aponta para `vibe-implement`. Não implemente CSS nesta skill.

---

## 1. Captura e Leitura Visual

A validação visual é feita utilizando as ferramentas do **MCP Server `chrome-devtools`** (`navigate_page`, `take_snapshot`, `take_screenshot` e leitura factual do resultado).

- **Prova obrigatória:** Qualquer fluxo visual alterado sem evidência lida via MCP `chrome-devtools` (ou screenshot analisada) bloqueia Approve (`Required`).
- **Análise factual:** A IA deve descrever textualmente os elementos renderizados e verificar se o que está na tela corresponde exatamente ao aceite da spec.

---

## 2. Rubrica de Defeitos Visuais

| Falha Visual | O que inspecionar | Severidade |
|---|---|---|
| **Elemento Sobreposto / Coberto** | Botões, modais, textos ou cabeçalhos sobrepondo outros componentes ou invadindo áreas vizinhas. | Required |
| **Contraste e Legibilidade** | Texto cinza claro sobre fundo branco, texto escuro sobre fundo escuro ou cores sem contraste mínimo legível. | Required |
| **Layout Quebrado / Overflow** | Scroll horizontal não intencional, componentes vazando o contêiner ou quebra desordenada de linhas. | Required |
| **Copy de Erro / Empty State Ausente** | Telas de carregamento, estados vazios ou mensagens de validação genéricas ou não renderizadas conforme a spec. | Required |
| **Duplicação de Design System** | Criação de botões, inputs ou modais isolados em vez de reutilizar os componentes base do projeto. | Required |
| **Preferência Subjetiva** | “Eu preferiria outro tom de cor” ou “outro espaçamento” sem exigência expressa na spec ou no design system. | Não bloqueia |

Não aprove interfaces no escuro. Se não houver MCP `chrome-devtools` ou screenshot disponível, registre `Required` ou questione o usuário.
