# Prova visual no browser com MCP Server chrome-devtools

Abrir **apenas** se a fatia alterar ou criar interface web visual no navegador. Não carregar para tasks sem UI.

## Uso das Ferramentas MCP chrome-devtools

A validação de interface é executada diretamente pela IA através do **MCP Server `chrome-devtools`**:

1. Identifique ou suba o servidor local da aplicação. Sem URL funcional, pare e pergunte via chat.
2. Execute a ferramenta MCP `navigate_page` para acessar a URL da rota a ser testada.
3. Use `take_snapshot` (árvore de acessibilidade) para inspecionar elementos do DOM e interagir através do `uid` correspondente (`click`, `fill`, etc.).
4. Chame `take_screenshot` na página ou componente renderizado.
5. Inspecione factualmente a imagem capturada: validar renderização, texto, layout, estados de erro/vazio, contraste e ausência de elementos quebrados ou sobrepostos.
6. Registre na prova da fatia: URL testada, ações executadas e leitura visual do screenshot.

## Testes E2E do Repositório (Playwright / Cypress)

Usar testes E2E locais quando:
- A verificação da task (`T*`) já especificar comando E2E existente no repositório.
- O usuário solicitar explicitamente.
- O MCP `chrome-devtools` estiver indisponível no ambiente.

Execute o comando de teste do repositório. Não instale novas bibliotecas de navegador sem solicitação explícita.

## Sem prova de navegador possível

Se a task exigir validação de UI e não houver MCP `chrome-devtools` ativo nem comando E2E no repositório, não feche a task apenas com teste unitário. Pergunte via chat:

```text
Q: Interface criada sem MCP chrome-devtools e sem suíte E2E no repositório
RECOMENDO: Ativar o MCP chrome-devtools no ambiente, ou executar comando E2E do repo, ou validação manual pelo usuário
(ok / outra?)
```
