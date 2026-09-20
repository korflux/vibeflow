# UX detalhado e vibe-design
# Status: rascunho

<!-- Escreva diretamente neste artefato vivo; mantenha rascunho até a confirmação humana. -->

## Solicitação

Queria estudar em expandir as skills vibe, hoje identifico 2 problemas cruciais, acho que a fase MVP ainda carece de capacidades, precisamos desenhar em mais detalhes cada função, detalhar o trajeto de login, recuperação, registro, onboarding, tudo que tiver, então, cada função, desenhar cada clique, cada tela, cada processo, vai ser tela, vai ser popup, enfim. O segundo problema é literalmente o desenho da UI, está muito fraco, já tentei largar mão e deixar a IA lidar, dar pouca informação, dar DESIGN.md, dar acesso ao figma, mas a UI é muito relativa, as vezes fica bom, as vezes fica péssima, eu queria talvez criar uma skill 100% para desenvolver o desenho da UI, como ela deve ficar, posição, organização, cores, o que é ícone. Esclarecimentos seguintes, vale para todo fluxo de uso de todo app, não só login, estamos falando de UX e não só UI, UI fica para a skill design, e a vibe-design deve ser capaz de usar figma e design.md quando existirem, ou criar do zero.

## Hipótese inicial

```text
HIPÓTESE: evolução delimitada do vibeflow para detalhar UX genérica na interview e na spec, mais nova skill vibe-design com design.md entre spec e plan
CONFIDENCE: ~70%, faltavam escopo exato, nome da skill, conteúdo do design.md e regra das rotas
```

## Trilha

### 1

Q: Escopo da phase. Cobrir as três frentes juntas, melhoria da interview para jornadas genéricas, molde genérico de fluxo F* na spec e contrato da nova skill de design com modo com referência e modo greenfield, deixando o fatiamento para o plan, ou reduzir para só parte.
GUESS: manter as três frentes como uma direção única, porque UX na spec sem UI na design volta a deixar lacuna, e UI sem UX detalhada desenha sobre fluxo vago.
R: Humano indicou que não entendeu a dúvida nem o guess, e pediu atenção às rotas low, medium, high, xhigh e max, já que nem todo app tem UI, mas todo app tem UX. Pergunta reformulada na trilha seguinte.

### 2

Q: Fechar regra de rotas. UX detalhada na spec é obrigatória sempre que a rota tiver spec, e vibe-design é obrigatória somente quando houver UI visível ao usuário, com N/A explícito quando não houver.
GUESS: sim, fechar assim, porque torna design exigível sem travar backend, CLI, API e automação que não têm tela.
R: Sim.

### 3

Q: Nome e posição. A nova skill chama vibe-design, grava design.md na mesma pasta da phase, entre spec aprovada e plan, com handoff spec mais design mais plan.
GUESS: sim, manter vibe-design e design.md nessa posição, porque spec fecha o fluxo, design fecha a apresentação do fluxo, e o plan só fatia depois dos dois aprovados.
R: Guess correto.

### 4

Q: Conteúdo do design.md. Fechar sem gerar código nem CSS final, apenas restrição executável para implement e review, com inventário de telas, hierarquia e layout por tela, componentes permitidos, tokens, iconografia, responsivo, estados por tela e prova visual esperada.
GUESS: sim, fechar assim, porque mantém design verificável sem prometer pixel perfeito automático.
R: Humano pediu elaboração, quer que o design.md auxilie em melhoras de UI e correções quando necessário, analise UI existente, auxilie criar páginas e traga desenhos técnicos de disposição de conteúdo. Evoluído na pergunta seguinte.

### 5

Q: A vibe-design atende criar, corrigir e analisar, sempre gravando disposição técnica e decisão no design.md vivo da phase, sem gerar imagem final nem editar código.
GUESS: sim, fechar assim, porque mantém um único contrato verificável para os três usos.
R: Sim.

### 6

Q: Restate curto confirmado para criar o interview.md da phase 10.
GUESS: restate cobre UX genérica, vibe-design com dois modos, rotas com UX obrigatória e design condicional, sem código nesta phase.
R: Sim, cria arquivo.

## Resultado

Entendi assim:

- O quê: evoluir o vibeflow com UX genérica detalhada na interview e na spec, mais a nova skill vibe-design com design.md entre spec e plan.
- Pra quem: IAs que operam a cadeia e humanos que aprovam as phases.
- Por quê: fluxo vago gera UI variável, e Figma solto não vira contrato executável.
- Sucesso: jornadas genéricas fechadas, molde F* clique a clique com superfície por passo, design.md com disposição técnica para criar, corrigir e analisar, e rotas atualizadas.
- Limite: esta entrevista fecha só a direção, o detalhe vai para spec e plan depois.
- Fora: código, CSS final, imagem automática e Figma como verdade versionada.
- Visual: design.md textual estruturado, com modo com referência e modo greenfield.

## Direção

- UX na spec é obrigatória sempre que a rota tiver spec. Cada fluxo F* registra jornada, rota, gatilho, pré-condição, superfície por passo com tela, popup, drawer, inline, redirect ou toast, passos numerados, validações, erros, vazio, loading, erro, sucesso, sem permissão e aceite A*.
- Design condicional a UI visível. Rotas low e medium sem spec seguem sem design por padrão. Rotas high, xhigh e max exigem design.md quando houver UI visível, e registram N/A explícito para backend, API, CLI e automação sem tela.
- Nova skill vibe-design grava design.md na mesma pasta da phase. Entrada, spec aprovada mais interview, mais DS, DESIGN.md ou Figma como leitura quando existirem. Saída com inventário de telas, disposição técnica por tela, tokens, componentes, iconografia, responsivo, estados e prova visual para a review.
- Três usos no mesmo contrato, criar páginas novas, corrigir UI com R* da review e analisar UI existente contra o contrato. Figma é referência de leitura, a verdade versionada é o design.md.
- Handoff futuro, spec aprovada mais design aprovado, depois plan. O plan só fatia depois dos dois.

## Handoff

vibe-spec

- Chat: `init → interview → spec` pode continuar no mesmo chat. Se abrir outro, use este arquivo vivo como ponte.
