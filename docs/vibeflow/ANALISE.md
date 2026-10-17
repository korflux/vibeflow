# vibeflow, análise

## Problema e decisão

A v1 distribuía oito skills, cada uma com comando, motor, relatório e regras de seleção próprios. O humano precisava saber qual comando chamar, os motores repetiam inventário, slug, alvo e relatório, e a coordenação por subagentes só começava na implementação. A V2 troca isso por uma skill única, `vibeflow`, conduzida por um coordenador-líder que atende de uma troca de cor a uma rota max com o mesmo `/vibeflow`. O contrato de disco não muda: phases e MVP continuam nos mesmos paths, com os mesmos artefatos, e as phases da v1 continuam legíveis.

O líder faz o que só ele pode fazer: conversar com o humano, entender o projeto, escolher a rota, planejar o macro, delegar, criticar, reconhecer e decidir. Todo o micro (redação de artefatos, leitura ampla, código, testes, provas, registros e Git) vai para os papéis que já existiam na v1. Analyze e review continuam com visão de fora, porque o valor delas está em não compartilhar o contexto de quem planejou ou implementou.

## Corte dos motores

A primeira versão do plan da V2 previa um motor único em Python e PowerShell. Durante a implementação, o humano decidiu que a V2 é só texto, com foco na qualidade e na organização da skill para o coordenador funcionar bem.

Por que cortar:

- **Simplicidade.** Um motor em dois runtimes exigia paridade de flags, de JSON e de erros, suítes de contrato e um launcher. Esse custo crescia a cada regra nova e competia com o trabalho que de fato muda o resultado: a condução do líder.
- **Git como histórico e backup.** O estado que o motor derivava já está no disco legível (linhas `# Status:`, `# Rota:`, caixas do `plan.md`) e no Git, que guarda histórico, autoria e evidência de commit. Um commit que contém o arquivo de regra do usuário substitui o backup com hash quando existe; a cópia conferida em `.vibeflow/old/` cobre o caso sem commit.
- **Foco na organização do pensamento.** Sem motor, a skill é inteiramente prompt operacional: o que fazer, o que validar e o que recusar em cada etapa, com uma casa por fato.

O que se perde é o determinismo. O cálculo de `n`, a sanitização do slug, a disjunção de `Arquivos:` e a derivação da etapa passam a depender da leitura correta da IA, sem uma implementação que devolva sempre o mesmo resultado para o mesmo disco.

O que compensa:

- **Gates escritos.** Cada etapa tem pré-requisito nomeado em `ARQUITETURA.md` e na referência da etapa, conferido pelo líder antes de começar. Recusa nomeia o que falta.
- **Regras mecânicas curtas.** `n`, slug, preservação e backup são poucas regras verificáveis a olho, concentradas em uma referência.
- **Revisor de contexto limpo.** Analyze e review não compartilham o contexto de quem escreveu e auditam o resultado no disco e no Git, o que pega desvios que um motor também pegaria e outros que ele não veria.

## Run do líder de ponta a ponta

1. **Entrada.** `/vibeflow` (ou o auto-invoke pela description) começa pela leitura do disco: `AGENTS.md`, `.vibeflow/`, a phase aberta de maior `n`, as linhas `# Status:` e `# Rota:` e as caixas do `plan.md`. Com phase aberta do mesmo assunto, o líder anuncia em uma linha a etapa e o próximo responsável e retoma. Sem phase aberta, classifica o pedido pela tabela de esforço e anuncia a rota e as etapas que ela inclui. `/vibeflow <etapa>` leva direto a uma etapa da allowlist, desde que o pré-requisito esteja satisfeito.
2. **Etapa 0.** Sem `.vibeflow/`, com instalação legada ou com `AGENTS.md` ausente, uma rota com cadeia passa pelo init. Um agente genérico apto a Git executa as instruções, preserva fontes legadas e cria o commit de governança. Quando algum perfil foi criado ou substituído, o líder para e pede a recarga do host antes da primeira delegação, porque perfil presente só no disco não conta como carregado.
3. **Abertura.** Na rota com phase, o líder fixa `n` e slug pelas regras escritas e os passa no brief; quem grava o primeiro artefato cria a pasta, com `# Rota:` no cabeçalho (`interview.md` em xhigh, max e MVP; `spec.md` em high; `review.md` em medium). Plans novos não levam marcador de protocolo nem de modo; o modo depende de o host ter subagentes e é decidido na run.
4. **Planejamento.** O líder conduz as perguntas da interview uma por vez, fecha os seams da spec e do design e define resultados, responsáveis, dependências e ondas do plan. O redator grava os artefatos; o humano aprova; o finalizador marca o status. Design sem UI visível fecha com N/A explícito, em vez de bloquear.
5. **Analyze, na rota max e no MVP.** O revisor de contexto limpo grava o `analyze.md` e devolve veredito, cobertura e perguntas. O líder leva as perguntas materiais ao humano e encaminha as correções aos donos dos artefatos.
6. **Implementação por ondas.** Com o plan aprovado (e o analyze aprovado e limpo quando a rota exige), o líder confere a capacidade de delegação, lê o plan e despacha a onda de T* elegíveis com `Arquivos:` disjuntos. Implementadores entregam código, testes e a `Prova afetada:`; o verificador certifica a integração; o finalizador atualiza o `plan.md` com pronto, em andamento e pendente e cria o commit `task(T*...)` depois da prova verde.
7. **Review e correções.** O revisor julga o diff do commit anterior ao primeiro `task(...)` da phase até `HEAD`, executa a regressão completa e grava o `review.md`. Os R* voltam ao corretor ou ao redator pelo campo `papel:`, com até duas rodadas antes de parar e relatar.
8. **Fechamento.** O líder apresenta resultado, commits, Critical e decisões propostas e faz uma única pergunta: aprovar a review, publicar as decisões vigentes e fazer push.

## Rota proporcional

A tabela de esforço do `AGENTS.md` continua sendo a única fonte da rota. Pedido pequeno (Express e low) não passa por spec, plan, analyze nem review e não cria `.vibeflow/`, phase ou artefato quando não há phase ativa. Com phase ativa, o pedido pequeno reaproveita a T* aberta ou acrescenta uma T* curta no plan existente. A cadeia completa só aparece quando o tamanho do pedido justifica. A rota fica gravada em `# Rota:` porque a retomada em chat novo precisa saber quais etapas a phase exige sem reclassificar o pedido.

## Delegação sempre

O líder delega inclusive em Express e low: entrega um brief curto, recebe a prova e fecha. A delegação curta custa pouco e mantém o contexto do líder livre para as decisões, que é onde a v1 perdia eficiência em runs longas. Ele faz no máximo pequenos ajustes finais, como um typo ou uma linha de fechamento. Em host sem subagentes, a degradação é explícita: aviso de uma linha, Modo B com uma etapa ou T* por run executada inline e, para analyze e review, instrução de chat novo, que faz o papel de visão de fora.

## Crítica e reconhecimento

Cada devolutiva é confrontada com o objetivo da phase. A crítica devolve ao dono um apontamento específico, sem que o líder refaça o trabalho. O reconhecimento marca a entrega como referência de padrão para as próximas delegações e reaproveita o analista que acertou, com o contexto que ele já tem. Nenhum dos dois cria artefato ou seção nova; o `plan.md` registra só o estado resultante.

Os dois desvios que o líder evita são simétricos. Microgerência refaz conferência, diff ou prova já certificados e gasta o contexto que a delegação poupou. Distância aceita a entrega sem confrontá-la com o objetivo e deixa passar resultado correto no recorte e errado para a phase.

## Analyze e review de fora

O líder nunca escreve `analyze.md` nem `review.md`, em nenhum host. Ele entrega o alvo e os artefatos ao revisor, recebe veredito, cobertura e R* e encaminha as correções. Sem perfil revisor carregado, nada é despachado: o líder pergunta ao humano com a recomendação de rodar `/vibeflow init` e recarregar o host.

## Interrupção e retomada

A retomada parte do disco, nunca do histórico do chat. Ao pedido de parar, o líder delega ao finalizador a atualização do `plan.md` (pronto, em andamento, pendente) e só então confirma a parada. Em chat novo, `/vibeflow` lê as linhas de status, a rota, as caixas do plan e o `git log`, e o líder continua sem refazer trabalho com evidência válida. Com o contexto pesado, o líder grava checkpoint e recomenda chat novo. Em host de contexto curto, avisa no início que um chat para todo o planejamento e outro para a implementação resolvem boa parte dos problemas.

## Compatibilidade com phases v1

Phases da v1 (`etapas-v1`, legado e `coordenacao-v1`, conforme o marcador do plan) são lidas como estão, sem migração nem reescrita. O registro JSON de execução que a v1 gravava continua no disco e no Git, mas não é interpretado: o estado sai das linhas de status, das caixas do plan e dos commits, que existem em todas as phases. Phase v1 sem `# Rota:` não ganha rota retroativa; seus gates seguem os artefatos presentes, e um pedido novo sobre ela abre phase V2.

## Cortes

- Motores, relatório operacional, registro estruturado de execução e suítes de contrato: cortados pela decisão do humano, com as compensações acima.
- Aliases dos comandos da v1 e convivência com os pacotes v1: contrariam a skill única.
- Migração automática de phases antigas: são lidas como estão.
- Testes de comportamento de fragmentos de instrução, worktree e pacote de contexto por T*, fan-out da review por dimensão e benchmark automatizado de eficiência: posteriores. A eficiência é avaliada pelo humano no uso.
- Mudança de rota depois da abertura: pedido maior abre outra phase.

## Decisões assumidas

- A rota fica no cabeçalho do primeiro artefato, porque é o único lugar presente em toda phase com cadeia e legível sem ferramenta.
- O finalizador, e não o líder, marca o status aprovado e opera o Git, e a pasta da phase nasce com o primeiro artefato gravado por analista, para manter o líder fora da escrita em host com subagentes.
- A prova da V2 é a review independente de consistência e qualidade da skill e o uso real, já que não há código a testar.
