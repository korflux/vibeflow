# Piloto automático de implementação com subagentes
# Status: aprovado

## Solicitação

Eu gostaria de mapear dentro das skills o uso de subagents, gostaria de tornar mais eficiente. fazer pesquisas em código com subagente mais simples, como sei lá, no claude, mandar o haiku, no gpt mandar o luna... enfim, fazer uso, algo universal, de subagents, a gente já tem uma "tentativa" de paraleização em plan, mas ela não é eficientemente informada e utilizada. isso devia ser quase que padrão, pra acelerar o desenvolvimento, pode dar uma analisada e me dar feedback?

## Hipótese inicial

```text
HIPÓTESE: Modo A vira piloto automático da phase (coordenador + subagentes, implement → review → correção), Modo B vira o atual uma-T*-por-run e serve de fallback
CONFIDENCE: ~85%, falta: gatilho de entrada do Modo A e critério de sucesso observável
```

## Trilha

### 0. Debate prévio no chat (antes da entrevista formal)

ANOTEI: diagnóstico do estado atual. Só existe delegação de escrita (`vibe-implement` passo 3.2), condicionada a grupo paralelo no plan, aprovação humana e isolamento. Não existe delegação de leitura em nenhuma skill. A seção `Paralelização` do plan registra isolamento em prosa livre, sem checagem mecânica. "Um chat por T*" faz manualmente o que um subagente faz ao nascer com contexto limpo. Não há separação por papel ou perfil de modelo.
R: humano concordou com o diagnóstico e pediu para debater antes de alterar.

ANOTEI: proposta de papéis universais descritos por perfil e não por nome de modelo: `explorador` (leitura, barato), `verificador` (executa provas, resume), `revisor` (julga, forte), `implementador` (escreve, isolado). Saída de subagente é evidência a conferir; limiar mínimo para não delegar busca trivial; host sem suporte executa inline.
R: aceito. Escolhida a opção 1: sem skill nova; tabela de continuidade do `AGENTS.md` ganha a indicação de delegação e um `references/delegation.md` define papéis, formato do relatório e fallback.

ANOTEI: distribuição por etapa.
R: interview → spec → design → plan no mesmo chat; a spec não vai para subagente. Analyze em subagente. Review em subagente, começando com um único revisor (fan-out por dimensão fica para depois). Analyze e review em subagente gravam o artefato e devolvem perguntas em aberto; o chat principal pergunta ao humano e conduz commit e push.

ANOTEI: a implementação continuava lenta pela espera humana entre T*s e pelo overhead fixo por T*.
R: humano propôs reorganizar os modos. Novo Modo A (padrão): coordenador num chat delega cada T* a subagente, confere, commita e segue; ao fim da fila envia subagente revisor; R* abertos vão para subagente corretor; piloto automático da phase inteira. Novo Modo B: uma T* por run, igual ao Modo A atual, e fallback quando o host não tem subagentes. O Modo B atual (plano inteiro inline) é removido.

ANOTEI: condições de parada e gates humanos do piloto.
R: push só no final, numa pergunta única junto da atualização da tabela de decisões vigentes. Ferramenta ausente: instala e segue. Impedimento real: só o que o agente não resolve. Ambiguidade material: para e pergunta. Prova vermelha: resolve, sem limite numérico; pergunta só se a solução exigir o humano. Ciclo review → correção: 2 rodadas. Sem regra especial para R* Critical. O `plan.md` precisa ser atualizado continuamente para permitir retomada.

ANOTEI: divisão da entrega.
R: duas phases. Esta (phase 1 do tema) entrega o piloto sequencial; paralelismo com `Arquivos:`, checagem de disjunção, worktree e pacote de contexto por T* ficam para a phase seguinte.

### 1

ANOTEI: o humano confirmou o debate e a divisão em duas phases; falta saber como o Modo A começa.
Q: Depois do plan aprovado (ou do analyze, no max), quando o humano disser "segue pro implement", o Modo A começa direto ou o agente pergunta antes qual modo usar?
GUESS: começa direto no Modo A; Modo B só se o humano pedir ou o host não tiver subagentes, com aviso de uma linha. Perguntar o modo recria a espera que o piloto elimina.
R: corrigiu e complementou. O plan deve recomendar com ênfase que o implement rode em outro chat; nesse chat o Modo A é o padrão e o coordenador conduz a implementação num chat só dele. Registrado como recomendação forte, não gate, conforme `AGENTS.md` ("Separar chats é uma recomendação, nunca um gate"); se o humano insistir em continuar, o agente segue.

### 2

ANOTEI: o gatilho ficou definido; falta o critério de sucesso observável.
Q: Como vamos saber que a phase deu certo?
GUESS: numa phase com plan aprovado, um único `/vibe-implement` num chat novo executa todas as T*s com commit próprio, faz review em subagente com no máximo 2 rodadas de correção, termina com uma pergunta única ao humano (push e tabela de decisões), só interrompe por ambiguidade material ou impedimento real, e mantém o `plan.md` atualizado a ponto de outro chat retomar só pelo disco. Prova por testes de script nos motores alterados e por uma execução piloto real num repo de teste, já que o `AGENTS.md` proíbe testar texto das skills.
R: confirmou o guess.

### 3

ANOTEI: o analyze cruzou a trilha com o disco. O item 0 registra "interview → spec → design → plan no mesmo chat", mas a tabela de continuidade do `AGENTS.md`, as skills interview, spec e design e seus templates recomendam chat novo para o plan, e a spec tratou isso como "comportamento atual mantido".
Q: Mudar a recomendação do plan nesta phase ou manter chat novo para o plan?
RECOMENDO: manter chat novo para o plan; a delegação do analyze vale em qualquer chat e o ganho do piloto está no implement. Mudar tocaria interview, spec, design, plan e `AGENTS.md`, fora da spec.
R: ok. Mantida a recomendação atual de chat novo para o plan; o item 0 acima fica como registro do debate e o Resultado e a spec foram corrigidos.

## Resultado

Entendi assim:

- O quê: piloto automático de implementação nas skills `vibe-*`, com delegação a subagentes por papel.
  1. Fluxo de chats: interview → spec → design no mesmo chat e novo chat recomendado para o plan, como hoje (spec fora de subagente). Analyze roda em subagente, disparado a partir do chat do plan, com contexto limpo. O plan termina recomendando com ênfase um chat novo para o implement (recomendação forte, não gate).
  2. Modo A (padrão no implement): coordenador num chat dedicado delega cada T* a subagente implementador, confere, commita e segue; com a fila vazia, envia subagente revisor; R* abertos vão para subagente corretor; no máximo 2 rodadas de review → correção; termina com pergunta única ao humano sobre push e atualização da tabela de decisões vigentes.
  3. Modo B: uma T* por run, igual ao Modo A atual; entra quando o humano pede ou o host não tem subagentes. O Modo B atual (plano inteiro inline) é removido.
  4. Papéis `explorador`, `verificador`, `revisor` e `implementador`/corretor em `references/delegation.md`, por perfil e não por nome de modelo, com fallback inline. A tabela de continuidade do `AGENTS.md` indica a delegação; sem skill nova.
  5. Paradas: ferramenta ausente instala e segue; impedimento real só o que o agente não resolve (credencial, serviço externo, permissão negada, ação proibida, proteção do script); ambiguidade material para e pergunta; prova vermelha resolve sem limite numérico e só pergunta se a solução exigir o humano ou mudar aceite; nunca enfraquecer teste para passar; sem regra especial para R* Critical, e o relatório final destaca os Critical corrigidos.
  6. Mapeamento contínuo: coordenador é o único escritor do `plan.md`, registra cada transição; retomada a partir de plan, review e Git. A forma de registrar o hash do commit fica para a spec.
  7. Regra única de instalação de ferramentas: permitido instalar, alinhando plan (passo 3.3) e review (linha 108) ao implement.
  8. Versão major.
- Pra quem: quem conduz uma phase VibeFlow em hosts com subagentes (Claude Code primeiro); os demais caem no fallback.
- Por quê: a implementação é a etapa mais lenta; cada T* depende de uma rodada humana e o contexto incha quando o plano roda inteiro inline.
- Sucesso: numa phase com plan aprovado, um único `/vibe-implement` num chat novo executa todas as T*s com commit próprio, faz review em subagente com no máximo 2 rodadas de correção, termina com uma única pergunta ao humano, só interrompe por ambiguidade material ou impedimento real, e mantém o `plan.md` atualizado para retomada só pelo disco. Prova por testes de script nos motores alterados e execução piloto real num repo de teste.
- Limite: push e tabela de decisões vigentes continuam exigindo confirmação humana; separação de chats continua sendo recomendação, não gate; testes não verificam texto de `SKILL.md`.
- Fora: paralelismo, contrato `Arquivos:`, checagem de disjunção no `plan.py`, worktree e pacote de contexto por T* (phase seguinte); fan-out da review por dimensão.
- Visual: N/A, sem UI visível.

## Handoff

vibe-spec
rota: max

- Chat: `init → interview → spec → design` pode continuar no mesmo chat. Recomende novo chat ao iniciar `vibe-plan`; se o humano preferir, a continuidade não bloqueia. Use este arquivo vivo como ponte.
