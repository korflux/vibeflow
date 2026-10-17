# VibeFlow V2: skill única com coordenador-líder
# Status: aprovado

## Solicitação

Faz uma análise, estou corgitando transformar o vibeflow em uma skill apenas, um coordenador, um lider, que produz todo fluxo, é essa linha que estou seguindo com o vibe-implement

acho que seria vibeflow, seria uma V2 do projeto isso né? talvez uma branch separada. eu queria que fizesse parte da essência da skill a eficiência em time, um lider ele é capaz de delegar, planejar, criticar, elogiar. com uma visão macro, que executa o micro é os analistas. o coodenador é um lider, ele faz briefing, entende o projeto, tomas decisões necessárias para que o projeto seja executado, sempre na visão maior. entende o que eu quero dizer?

Review e Analyze não pode ser feito pelo coordenador, precisa de uma "visão de fora" beleza? fora isso, abre a branch v2.

## Hipótese inicial

```text
HIPÓTESE: V2 do VibeFlow como skill única `vibeflow`, com coordenador-líder que conduz a phase inteira e delega o micro aos analistas
CONFIDENCE: ~55%, falta: host sem subagentes, controle de contexto do líder, contrato de disco, papel do init, forma de entrada
```

## Trilha

### 0. Análise prévia no chat (antes da entrevista formal)

ANOTEI: diagnóstico do repositório. O vibe-implement Modo A (`coordenacao-v1`) já é um coordenador: sua máquina de estados vai de `implementar` a `concluida`, passando por validação, commit integrado, review delegada, correção e confirmação. As phases 15 a 20 trataram quase só de coordenação, e a phase 20 existiu apenas para realinhar plan, analyze, review e init ao contrato da implement. Os motores repetem lógica mecânica: `repo_root` em 8 cópias; `vibeflow_state`, `phases_state`, `list_phases`, `get_mvp`, `emit_report`, `is_reparse_point` e `parse_args` em 7; `resolve_alvo` e `prepare_live_file` em 6; `sanitize_slug` e `find_rascunho` em 5, cada uma com gêmea PowerShell. A tabela de rota e as recusas se repetem entre `AGENTS.md` e as skills.
R: humano concordou com a direção.

ANOTEI: proposta de desenho. Unificar o condutor e manter o registro: motor com máquina de estados da phase inteira, `SKILL.md` curto com invariantes e roteamento, corpo das skills atuais convertido em `references/<etapa>.md` lido sob demanda, templates mantidos. Riscos levantados: conversa humana não delegável, acúmulo de contexto do líder, host sem subagentes, independência de analyze/review, precisão do auto-invoke e quebra de contrato de distribuição.
R: humano definiu o nome `vibeflow`, a V2 como versão major numa branch separada e a essência da skill: eficiência em time. O coordenador é um líder com visão macro que faz o briefing, entende o projeto, planeja, delega, critica, elogia e toma as decisões para o projeto ser executado; o micro é executado pelos analistas.

ANOTEI: tradução do líder em comportamento. O líder é dono do porquê, do quê, de quem e de quando; os analistas são donos do como. Briefing e decisões ficam com o líder; delegação leva objetivo, ownership, critério de pronto e interlocutores; crítica confronta a entrega com o objetivo maior sem refazê-la; elogio fixa o padrão de referência e reaproveita o analista que acertou. Desvios a impedir: microgerência (refazer conferência certificada) e distância (aceitar sem confrontar com o objetivo).
R: humano acrescentou o invariante: analyze e review nunca são feitos pelo coordenador e exigem visão de fora. Branch `v2` criada a partir da `main` em `07466e6`.

### 1

ANOTEI: essência e invariante de analyze/review confirmados; o restante do desenho ainda era hipótese.
Q: Em host sem subagentes, a V2 ainda funciona?
GUESS: Sim, degradada e com aviso: o líder executa uma etapa por run, o motor indica a próxima e analyze/review exigem chat novo como visão de fora. Motivo: a distribuição cobre Claude, Codex, Antigravity e Grok. Confiança média.
R: confirmou o guess.

### 2

ANOTEI: host sem subagentes funciona degradado, com analyze/review em chat novo.
Q: A V2 mantém o contrato de disco atual?
GUESS: Sim, mesmos paths e artefatos em `.vibeflow/phases/phase-N-slug/` e `.vibeflow/mvp/`; unifica o condutor, não o registro. As phases antigas continuam legíveis sem migração, o revisor de fora lê cada etapa isolada e a quebra fica restrita à distribuição. Única mudança: `execution.json` passa a cobrir a phase desde a interview. Confiança alta.
R: confirmou o guess.

### 3

ANOTEI: contrato de disco mantido; `execution.json` cobre a phase desde a interview.
Q: Como o líder conduz a phase sem estourar o contexto do chat?
GUESS: Um chat só por padrão, com o líder leve por regra: conversa e decisões ficam com ele; redação de artefatos, leituras amplas e execução vão aos analistas; ele recebe resumos e vereditos. Quando o contexto pesa, grava checkpoint e recomenda chat novo, que retoma com `/vibeflow`. Confiança média.
R: confirmou o guess e acrescentou: para hosts de contexto curto, o líder explica ao usuário que um chat para todo o planejamento e outro para a implementação resolve boa parte dos problemas. O `plan.md` precisa estar sempre atualizado com o que está pronto, em andamento e pendente, e sempre que o usuário pedir para interromper o líder também atualiza, para não haver perda no caminho.

### 4

ANOTEI: chat único por padrão; dois chats (planejamento e implementação) em contexto curto; `plan.md` sempre atual, inclusive na interrupção.
Q: O init vira a etapa 0 do `vibeflow` ou continua skill separada?
GUESS: Etapa 0. Com `INIT_AUSENTE` ou instalação legada, o líder conduz o init no fluxo, gera `AGENTS.md` e perfis e para obrigatoriamente pedindo recarga do host antes da primeira delegação. Reparo via `/vibeflow init`. Confiança média-alta.
R: confirmou o guess.

### 5

ANOTEI: init como etapa 0, com parada obrigatória para recarga do host.
Q: Como o usuário entra no `vibeflow`?
GUESS: Comando único `/vibeflow` com argumento de etapa opcional. Sem argumento, o líder lê o estado, retoma a phase aberta ou classifica o pedido (Express, low a max, MVP). Com argumento, pula para a etapa respeitando os gates. Description única cobre os gatilhos das 8 skills; `/vibe-*` deixam de existir, sem aliases. Confiança média-alta; risco de a description disparar demais.
R: confirmou o guess.

### 6

ANOTEI: entrada única com argumento opcional e sem aliases.
Q: Como saberemos que a V2 deu certo?
GUESS: Rota max inteira com um `/vibeflow` (ou dois chats) sem perda de estado e `plan.md` fiel em qualquer interrupção; líder sem executar o micro, com analyze/review sempre por revisor limpo; motores sem lógica duplicada (fonte comum Python e PowerShell); phases antigas (`etapas-v1`, legado, `coordenacao-v1`) legíveis e retomáveis. Confiança média.
R: confirmou e acrescentou: a V2 não pode tornar o processo ineficiente. A v1 ainda é percebida como lenta e ineficiente; no mínimo a V2 mantém a mesma eficiência, apenas mais prática.

### 7

ANOTEI: eficiência no mínimo igual à v1, com ganho de praticidade.
Q: Como medimos que a eficiência não piorou?
GUESS: Pedido de referência de rota high executado na v1 e na V2, no mesmo host e modelo, comparando tempo de parede, tokens, interações humanas e rodadas de correção, com tolerância de ~10%; execução manual fora da regressão completa. Confiança média.
R: rejeitou o guess. A eficiência é percepção do usuário, medida pelo humano no uso; não existe teste que prove que a skill funciona. Testes só fazem sentido para código; testar presença de texto não faz sentido. Testar se fragmentos de instrução produzem o comportamento esperado é possível, mas posterior.

## Resultado

Entendi assim:

- O quê: VibeFlow V2, versão major na branch `v2`. As 8 skills `vibe-*` viram uma skill única `vibeflow`, conduzida por um coordenador-líder de visão macro que faz briefing, entende o projeto, planeja, delega, critica, reconhece e decide; analistas executam o micro. Decisões:
  1. Analyze e review nunca são feitos pelo coordenador; exigem visão de fora por revisor de contexto limpo.
  2. Host sem subagentes funciona degradado e com aviso: uma etapa por run, analyze e review em chat novo.
  3. Contrato de disco mantido (`.vibeflow/phases/phase-N-slug/` e `.vibeflow/mvp/`, mesmos artefatos); `execution.json` cobre a phase desde a interview; phases antigas legíveis sem migração.
  4. Líder num chat só, com conversa e decisões; redação, leitura ampla e execução delegadas; recebe resumos. Em contexto curto, explica que um chat para o planejamento e outro para a implementação resolve boa parte dos problemas.
  5. `plan.md` sempre atualizado com pronto, em andamento e pendente, inclusive antes de parar quando o usuário pede interrupção; `execution.json` guarda a evidência estruturada.
  6. Init como etapa 0, com parada obrigatória para recarga do host antes da primeira delegação.
  7. Entrada `/vibeflow` com argumento de etapa opcional respeitando gates; description única; `/vibe-*` removidos sem aliases.
- Pra quem: o humano que mantém o VibeFlow e quem o instala em Claude, Codex, Antigravity e Grok.
- Por quê: a cadeia de 8 skills é pouco prática, exige sincronização a cada mudança do coordenador e duplica a lógica mecânica dos motores.
- Sucesso: rota max roda com um `/vibeflow` (ou dois chats) sem perda de estado; líder não executa o micro; motores sem duplicação, com fonte comum Python e PowerShell; phases antigas retomáveis; eficiência no mínimo igual à v1 com ganho de praticidade, medida pelo humano no uso.
- Limite: testes somente para motores e seus efeitos no disco, nunca presença de texto em `SKILL.md`, references ou templates; sem aliases nem convivência com os pacotes antigos.
- Fora: testes de comportamento de fragmentos de instrução (posterior); worktree por T*; fan-out da review por dimensão; benchmark automatizado de eficiência.
- Visual: N/A, entrega sem UI visível.

## Direção

Unificar o condutor e preservar o registro. Motor único com máquina de estados da phase inteira (classificar, init, entrevistar, especificar, desenhar, planejar, analisar, implementar, validar, commitar, revisar, corrigir, confirmar) e biblioteca comum para alvo, slug, inventário, relatório e `.gitignore`. `SKILL.md` curto com invariantes do líder e roteamento por etapa; o corpo das skills atuais vira `references/<etapa>.md`, lido somente quando a etapa chega; templates mantidos. Analyze e review permanecem papéis independentes de contexto limpo.

## Handoff

vibe-spec

- Chat: `init → interview → spec → design` pode continuar no mesmo chat. Recomende novo chat ao iniciar `vibe-plan`; se o humano preferir, a continuidade não bloqueia. Use este arquivo vivo como ponte.
