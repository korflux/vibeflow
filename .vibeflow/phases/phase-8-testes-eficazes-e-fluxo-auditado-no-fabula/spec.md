# Spec: Testes eficazes e fluxo auditado no fabula
# Alvo: phase-8-testes-eficazes-e-fluxo-auditado-no-fabula
# Status: aprovado
# Rota: high

## Objetivo

O líder e os analistas da skill `vibeflow` passam a conduzir implementações com provas que pegam defeito e sem trabalho que não muda o resultado, a partir da auditoria do fluxo real no projeto fabula (MVP e phase-1, skill 5.3.0). A entrega troca o teto de checkpoints por uma tabela fechada de motivos, troca a política de testes por quantidade por uma de qualidade, corrige as instruções que levaram a passos falhos, remove passos redundantes e fecha as pendências da phase-7. Sucesso é cada defeito real auditado ter um teste ou gate da política nova que o pegaria e o Haiku acertar na 5.6.0 todo cenário que acerta na 5.5.0.

## Pontos do projeto

- Fontes da auditoria: transcrições em `C:\Users\marco\.claude\projects\A--Projetos-fabula\` e artefatos em `A:\Projetos\fabula\.vibeflow\`; o MVP não tem transcrição e foi lido por artefatos e Git.
- MVP do fabula: 8 passos e 7 checkpoints; CP2 e CP8 pegaram defeito provável, 4 checaram só teste ou infra, 1 só confirmou. O R1 de segurança (limite de login por variante de e-mail) passou por todos e só a review o pegou.
- MVP do fabula: 16 de 18 decisões da spec foram assumidas, inclusive auth, segurança e dados; `interview/mvp-discovery.md:39` contradiz `interview.md`, que manda perguntar decisão sensível.
- Phase-1 do fabula: 45 subagentes e cerca de 4,2 M tokens de saída; 8 checkpoints. CP1 e CP2 pegaram defeito real; CP3, CP4 e CP6 bloquearam só por captura porque o acabamento visual vinha depois deles, e o líder adiou a evidência e marcou; CP5, CP7 e CP8 só confirmaram, com 91 a 146 mil tokens cada.
- Phase-1 do fabula: o líder moveu critérios entre checkpoints sem consultar; o defeito de `ui/` do passo 1 só apareceu no 5a, sem checkpoint cedo; o R1 foi o gate OpenGrep (`npm run security`), que só rodou na regressão da review; o redator gravou E2E nas provas porque o brief não citava `references/testes.md`; a revisão de uso com app rodando foi feita por agente fora dos papéis.
- Phase-2 do fabula, parada: `painel/w.html` foi criado por outra sessão do humano; a regra de alteração sem dono (`references/disco.md`, tabela de estados; `scripts/estado.mjs`) bloqueia sem lugar para registrar a decisão do humano, e o líder não perguntou.
- Suíte da phase-1 do fabula: 206 unitários, 95 de integração e 137 E2E, regressão de 305,6 s. Numa amostra de 15, 7 provam o critério, 3 confirmam a implementação, 3 duplicam sem ganho e 2 são frágeis ou não conseguem falhar.
- Custo dos testes no fabula: o E2E sobe a pilha por arquivo e faz login por teste (32 só em `plugins.spec`); o mesmo E2E roda em vários passos, no checkpoint e na regressão; o critério A60 é provado em 4 arquivos; as capturas são refeitas por passo.
- Defeitos que passaram e a causa: R1 do MVP (caso de equivalência de entrada ausente; a tabela de desenho de casos de `references/testes.md` é "teto, não piso"); nonce público (o teste só checava a presença da CSP e roda em dev); A14 (prova só da API); A39 (a asserção seguia a interpretação do implementador e o verificador não confere asserção contra o texto do critério); `ui/` do passo 1 (prova do passo sem tela); R3 (o aviso de console só existe em dev, a regressão roda `--production` e o teste não pode falhar).
- Lacunas da política atual: modo de execução dev ou produção não regulado; vermelho antes do verde só como relato; sem ID de critério no teste; sem regra de remoção de duplicata; mock de API própria e varredura de código-fonte não classificados; sem limite de pilha e de login por teste; segurança fora de `references/definition-of-done.md`; captura e E2E sem divisão de papel.
- Testes que não precisavam existir no fabula: varredura de `.tsx` por regex, mock do fetch da própria API, teste de processo com espera fixa, a mesma propriedade em 4 arquivos e o tema persistido em 3 testes.
- Já resolvido na 5.4.0 e na 5.5.0, fora desta phase: verificador rerodar provas, commits só de marcação, passos acima de 12 entradas e checkpoints sem teto.
- Pendências da phase-7: o R* tem um único campo de path, mas a prosa fala em "paths do R*" e `scripts/conferir.mjs` acusa os demais como fora do recorte; `references/review/passos.md` manda o revisor gravar `# Status:`, enquanto `SKILL.md` e `references/revisor.md` o dão ao líder (`.erros-encontrados/status-do-review-revisor-ou-lider.md`); `references/retomada.md` diz "na analyze".
- Estado atual: versão 5.5.0 (`AGENTS.md`); teto de dois checkpoints por phase e nenhum em phase de até 5 passos (`references/disco.md`, Plan > Checkpoint; `scripts/plan.mjs`).

## Decisões

1. A auditoria cobre o MVP e a phase-1 do fabula; a phase-2 entra só pela causa da parada. Pergunta: qual implementação auditar? Motivo: são as implementações completas (origem: humano).
2. Checkpoint só por motivo de uma tabela fechada, no máximo 4 por phase: caminho fino ou primeiro grupo de risco; segundo grupo de risco quando a spec tem `# Risco:` e mais de um grupo toca a superfície de risco; tela, sempre depois do passo que fecha o visual e nunca antes; integração quando a phase tem mais de 10 passos, depois do grupo que junta as partes. Phase com até 5 passos não tem checkpoint, e cada checkpoint cita o motivo (origem: humano). Pergunta: qual o critério do 3º e do 4º checkpoint? Motivo: no fabula o checkpoint valeu cedo e em risco, e os de captura ou só de confirmação custaram sem mudar o resultado.
3. Na prova de cada passo que toca código, o implementador roda os gates estáticos que o projeto tem (lint, tipos, segurança) sobre os arquivos alterados; a regressão completa da review continua igual. Pergunta: onde rodar gates estáticos? Motivo: pega o defeito na origem com custo baixo (origem: humano).
4. Alteração fora do recorte que não é da phase: o líder pergunta uma vez; o que o humano declara trabalho alheio entra na seção opcional `## Trabalho alheio` do `plan.md`, `scripts/estado.mjs` passa a ignorar esses paths, o staging explícito os mantém fora dos commits e a review os cita na finalização. Pergunta: o que fazer com alteração fora do recorte que não é da phase? Motivo: o estado vem do disco, sem travar nem perguntar de novo (origem: humano).
5. Sem teto de tokens: qualidade primeiro, e a medição por papel só é registrada na review, pelo mesmo método da phase-7. Pergunta: qual o orçamento de tokens? Motivo: decisão do humano (origem: humano).
6. Uma prova forte por critério: prova principal no nível mais barato que observa o resultado, com o ID do critério no título quando o brief ou a spec o tem; a asserção segue o texto do critério, e o verificador e o revisor conferem isso; casos adversariais obrigatórios por tipo de entrada (equivalência, borda, negado e concorrência, quando se aplicam); E2E só para critério com tela ou jornada, sem repetir o que a integração prova; a captura sai do próprio E2E; modo de execução definido, com E2E em build de produção e checagem de console em dev; uma pilha por execução e sessão reaproveitada; teste duplicado sem ganho é removido; lista explícita de "não teste" (varredura de código-fonte, mock de módulo próprio, espera fixa, mesma propriedade em vários arquivos). Pergunta: qual a política de testes? Motivo: ataca as causas dos defeitos que passaram e as fontes de lentidão sem etapa nova (origem: humano).
7. Um explorador reclassifica só em leitura a suíte inteira do fabula, 438 testes (origem: verificado inventário do explorador, 206 + 95 + 137), pela política nova em fica, funde e sai, com estimativa de tempo economizado, e confere que cada defeito real (R1 do MVP, nonce, A14, A39, `ui/` do passo 1, R3) seria pego; o resultado vai para a `review.md` e a limpeza do fabula é tarefa separada naquele repo. Pergunta: como provar a política? Motivo: decisão do humano, prova sobre suíte real sem alterar o outro repo (origem: humano).
8. Decisão de autenticação, autorização, segurança ou dados é sempre perguntada na interview, nunca assumida, e `interview/mvp-discovery.md` passa a seguir `interview.md`. Pergunta: decisão de segurança pode ser assumida na interview? Motivo: assumida; 16 de 18 decisões do MVP do fabula foram assumidas por essa contradição.
9. O analyze aponta critério cujo passo não tem prova que o teste e critério de tela num checkpoint anterior ao passo que o entrega. Pergunta: como evitar critério sem prova e checkpoint antes da tela? Motivo: assumida; CP3, CP4 e CP6 da phase-1 bloquearam só por captura.
10. O líder não move critério entre checkpoints nem marca checkpoint com evidência pendente: a falha volta ao dono do passo e critério mal atribuído no plan é corrigido no plan. Pergunta: o líder pode mover critério entre checkpoints ou marcar com evidência pendente? Motivo: assumida; foi o desvio observado na phase-1.
11. O brief do redator de plan leva `references/testes.md`. Pergunta: o brief do redator de plan cita a política de testes? Motivo: assumida; sem ela o redator gravou E2E nas provas.
12. O E2E roda no checkpoint e de novo na regressão. Pergunta: rodar o E2E no checkpoint e na regressão é redundante? Motivo: assumida; a regressão pega o que um passo posterior quebrou.
13. O R* aceita lista de paths e `scripts/conferir.mjs` lê a lista, mantendo o formato antigo de um path; regra única de `# Status:` do review, em que o revisor grava `rascunho` ou `request-changes` e só o líder grava `aprovado`; `references/retomada.md` diz "no analyze". Pergunta: como fechar as pendências da phase-7? Motivo: assumida; fecha as três divergências registradas.
14. O texto novo é testado com Haiku em cenários como na phase-7, com base na 5.5.0 (origem: humano), cobrindo checkpoint por motivo, trabalho alheio, gate no passo e caso adversarial. Pergunta: o texto novo é testado com modelo fraco? Motivo: decisão do humano, mesma prova de não regressão da phase-7.
15. A versão sobe para minor 5.6.0 (origem: assumida). Pergunta: qual versão? Motivo: assumida; seção opcional nova, campo de R* compatível e teto maior, sem quebrar artefatos existentes.
16. Depois do analyze, o líder apresenta o plan como guia: um tópico curto por passo e por checkpoint, dizendo o que cada um entrega, antes de seguir para o implement. Pergunta: como o humano acompanha o que vai acontecer? Motivo: pedido do humano durante o implement ("falar de forma concisa em tópicos o que é cada passo, para ter uma guia").

## Critérios de aceite

- A1: plan de 6 a 10 passos com `# Risco:` em dois grupos e tela; quando o plan é conferido, o script aceita até 4 checkpoints com motivo da tabela, acusa o 5º e o motivo fora da tabela e avisa o checkpoint sem motivo, e o analyze aponta o checkpoint de tela antes do passo que fecha o visual (origem: humano).
- A2: phase com até 5 passos; quando o plan tem checkpoint, a conferência o acusa (origem: humano).
- A3: passo que toca código num projeto com gate de segurança; quando o implementador fecha a prova, o relatório traz o gate rodado sobre os arquivos alterados.
- A4: path não rastreado fora do recorte; quando o humano o declara trabalho alheio e o path entra em `## Trabalho alheio`, `scripts/estado.mjs` deixa de parar a phase por ele e o staging continua sem ele.
- A5: plan sem a seção `## Trabalho alheio` e phases 1 a 7 deste repo (origem: verificado `.vibeflow/phases/`); quando os scripts os leem, o comportamento é igual ao da 5.5.0.
- A6: R* com vários paths; quando o líder confere o commit da correção, o script aceita todos os paths do R*.
- A7: R* antigo, de um path; quando o líder confere o commit da correção, o script o aceita como na 5.5.0.
- A8: a política de testes tem uma casa, com prova por critério com ID no título quando o brief ou a spec o tem, asserção contra o texto do critério, casos adversariais obrigatórios, E2E só para tela ou jornada, modo de execução, pilha e sessão reaproveitadas, remoção de duplicata e lista de "não teste".
- A9: verificador e revisor; quando conferem um teste de critério, comparam a asserção com o texto do critério.
- A10: interview e `interview/mvp-discovery.md`; quando a decisão é de autenticação, autorização, segurança ou dados, ela é perguntada, nunca assumida.
- A11: a `review.md` traz a reclassificação da suíte do fabula com a contagem de fica, funde e sai, o tempo estimado e, para cada defeito real listado, o teste ou gate da política nova que o pegaria.
- A12: a `review.md` traz a comparação dos cenários Haiku, em que cada cenário que passa na 5.5.0 passa na 5.6.0 e os cenários novos passam (origem: humano).
- A13: o `# Status:` do review segue uma regra única em todo o pacote, e `references/retomada.md` diz "no analyze".
- A14: a `review.md` registra a medição por papel da 5.6.0 contra a 5.5.0, sem teto (origem: humano).
- A15: `AGENTS.md` registra a versão 5.6.0 e o README traz a novidade (origem: assumida).
- A16: plan com achados do analyze; quando o líder fecha o analyze, a mensagem ao humano lista cada passo e checkpoint em um tópico curto com o que ele entrega.

## Fora do escopo

- Limpar ou alterar testes do fabula: é outro repo, com phase-2 aberta, e vira tarefa separada.
- Rodar suítes do fabula: a reclassificação é só leitura.
- Papel novo para revisão de uso com app rodando: lacuna registrada, sem decisão nesta phase.
- Teste de aceite escrito por outro papel antes do implementador: vira phase própria se o padrão do A39 persistir.
- Teto de tokens: a decisão 5 o recusa.

- [x] Aprovação humana (leu o arquivo e confirmou): 2026-11-02, "Aprovado"; decisão 16 e A16 acrescentadas a pedido do humano em 2026-11-02 ("se puder incluir nessa fase"); A1 ajustado ao implementado com aceite do humano em 2026-11-02 ("aceito o recomendado"); A8 com ID condicional seguindo a recomendação do líder, a pedido do humano para continuar ("não vai continuar?")
