# Modos de entrada (design)

Leia este catálogo quando a origem do desenho estiver em jogo. A skill aponta para cá, não resume a tabela no SKILL.

| Modo | Sinal | Leitura permitida | Registro obrigatório |
|---|---|---|---|
| Com referência | Existe DS, DESIGN.md ou Figma aproveitável | DS, DESIGN.md ou Figma como leitura | Reusado e adaptado com motivo, sem copiar a fonte para o repo |
| Greenfield | Sem referência aproveitável | Nenhuma fonte externa como verdade | Kit mínimo primeiro, depois cada tela sobre o kit |

Com referência, vale reuso fiel quando o componente atende ao F da spec. Adaptação exige motivo e impacto por tela. Primitivo novo na página com DS existente é defeito.

Greenfield cria nesta ordem: cores, tipografia, espaçamento, raio, botão, input, modal, toast, tabela e empty state. Só então mapeia cada tela da spec sobre o kit.

Figma é leitura com decisão registrada. A verdade versionada é o design.md. Sincronização automática com Figma não entra nesta skill.
