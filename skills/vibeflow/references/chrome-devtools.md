# Prova visual renderizada no navegador

Abra esta referência quando um critério de aceite depende da interface renderizada, ou quando a implementação revela uma mudança renderizada relevante que não estava prevista. A prova visual é necessária quando o critério depende de aparência, layout, responsividade, estado ou interação que só pode ser julgado na interface renderizada; tocar arquivo de UI, HTML ou DOM não basta. Confira o recorte afetado e amplie para outra viewport, estado ou superfície compartilhada quando layout, responsividade, interação ou risco exigirem. Provas automatizadas podem cobrir mudanças sem resultado visual a julgar.

## Seleção da ferramenta

Escolha a primeira capacidade disponível:

1. **Navegador integrado (`@Browser` ou equivalente):** abra a rota local e confira a tela renderizada, os estados e a interação principal.
2. **MCP Server `chrome-devtools`:** use `navigate_page`, `take_snapshot`, `click` ou `fill`, `take_screenshot` e, quando necessário, a inspeção de DOM, estilos, console, rede e assets.
3. **Playwright:** use somente quando já existir no repositório ou quando o humano o solicitar, para fluxos repetíveis, viewports, screenshots e assertions de visibilidade ou acessibilidade.

Se a prova visual for necessária e nenhuma capacidade estiver disponível, aplique a regra de instalação de `references/delegation.md` antes de declarar limitação: registrar um MCP é configuração persistente de integração e vai ao humano. Se a capacidade continuar ausente, registre a limitação e não dê a validação visual como concluída.

## Captura e reaproveitamento

A regra de que a captura sai da execução do E2E de quem o roda mora em `references/testes.md` (Execução); esta tabela diz quem captura em cada rota.

| Papel | Faz |
|---|---|
| Implementador | Em low e medium, dono da prova visual e da captura: captura uma vez por critério com tela, ao fechar a entrega, sobre a interface final, nos viewports e estados do critério ou do brief, sem captura a cada iteração; correção que altera a UI renderizada recaptura os critérios afetados ao fechar. Em `high` e `mvp`, escreve o E2E do critério com tela e não captura |
| Verificador | Em `high` e `mvp`, no checkpoint, cita as capturas que a execução do E2E dos critérios com tela gravou |
| Revisor | Na regressão completa, cita as capturas que a execução do E2E gravou para os critérios com tela; sem execução nova, reaproveita a evidência citada e recaptura só quando ela não existe mais (por exemplo, em chat novo) ou os inputs renderizados mudaram |
| Líder | Só abre as imagens finais citadas, que a conferência exige (`references/delegation.md`, Conferência do líder), e nunca captura |

Quem captura grava as imagens na pasta temporária do sistema, fora do repositório, e cita os paths no campo `prova` do relatório fixo (`references/delegation.md`). Evidência verde vale enquanto os inputs renderizados não mudarem; não repita a captura apenas para produzir outra. Imagem capturada nunca entra em commit.

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

Para interações, use a árvore de acessibilidade do `take_snapshot` e os identificadores retornados para executar as ações antes do screenshot. Leia a captura de forma factual e registre qualquer anomalia como pendência do passo.
