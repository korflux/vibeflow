# Prova visual renderizada no navegador

Abra esta referência somente quando a fatia alterar ou criar interface web visualizada no navegador. Confira no estado renderizado a tela, o estado e a viewport afetados. Amplie para outra viewport, estado ou superfície compartilhada quando layout, responsividade, interação ou o risco do diff exigirem; teste unitário, snapshot de DOM ou screenshot isolado não substitui a inspeção do comportamento quando houver interação relevante.

## Seleção da ferramenta

Escolha a primeira capacidade disponível, sem instalar ferramenta automaticamente:

1. **Navegador integrado (`@Browser` ou equivalente):** abra a rota local e confira a tela renderizada, os estados e a interação principal.
2. **MCP Server `chrome-devtools`:** use `navigate_page`, `take_snapshot`, `click` ou `fill`, `take_screenshot` e, quando necessário, a inspeção de DOM, estilos, console, rede e assets.
3. **Playwright:** use somente quando já existir no repositório ou quando o humano o solicitar, para fluxos repetíveis, viewports, screenshots e assertions de visibilidade ou acessibilidade.

Se nenhuma capacidade estiver disponível, registre a limitação e não marque a validação visual como concluída. A ausência de navegador não é passe visual e não justifica instalar uma dependência nova.

## Checklist renderizada

Registre a rota, a viewport afetada, o estado exercitado, as ações realizadas e a evidência observada. Inclua uma viewport estreita quando a alteração afetar layout ou responsividade, e estados adicionais quando a interação ou o risco os alcançar. Verifique:

- overflow horizontal ou vertical inesperado e conteúdo fora da viewport;
- clipping, elementos sobrepostos ou cobertos e z-index de modal ou sticky;
- truncamento, quebra de texto e proporção de largura dos containers;
- controles maiores que o necessário e composição de input com ícone na mesma linha quando houver espaço;
- responsividade em viewport estreita quando fizer parte do escopo afetado;
- estados loading, empty, error e success alcançados pelo recorte afetado;
- foco visível, teclado, contraste e nomes acessíveis nos controles alterados;
- erros novos ou relevantes no console, na rede ou no carregamento de assets.

Para interações, use a árvore de acessibilidade do `take_snapshot` e os identificadores retornados para executar as ações antes do screenshot. Leia a captura de forma factual e registre qualquer anomalia como pendência da fatia.
