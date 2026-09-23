# Otimização geral do vibe-implement
# Status: rascunho

## Solicitação

> Outra coisa que a gente precisa validar é que, assim, tem tasks que são muito simples e dá muito trabalho fazer, porque a gente tem um planejamento do vibe implement muito grande, que é de validar, de testar e tudo mais. Mas às vezes eu não preciso usar o vibe, eu não preciso fazer todo o teste, tudo pra trocar o nome de uma tela, sabe? É só trocar o nome, entendeu? Enquanto eu desenvolvia software de ponta a ponta, isso era muito efetivo, mas agora que eu, sei lá, por exemplo, peguei um software e eu precisava fazer ajustes rápidos na tela, precisava terminar pra ontem alguma coisa, eu não consigo, porque ele quer fazer um processo muito rígido, muito extenso, muito grande. Eu precisava entender como eu manipulo isso de uma forma mais eficiente, né? Talvez modificar um pouco a descrição das skills, modificar quando e quando não usar, definir mais limites à skill. Eu não quero sempre ter que ficar, por exemplo, falando: preciso disso pra ontem, não crie uma fase nova, seja rápido e eficiente pra me entregar isso aqui, entregue o mais rápido que puder. Então isso gera um trabalho muito grande. Eu queria alterar as copies da página e acabou que, por exemplo, criou uma fase inteira pra isso, sabe?

> Sim, você pode seguir com esse guess. Outra coisa também é que Temos que adicionar uma categoria de ajuste, talvez que o Vibe implemente, que executa. Por exemplo, às vezes foi tudo feito, né? Foi feita a spec, foi feito o design e tals, mas aquela fase, quando eu tô fazendo a validação humana, né? A minha validação, eu encontro algum erro, precisa fazer algum ajuste, precisa, sei lá, movimentar a imagem um pouquinho pra cá, mudar esse texto, mudar como esse texto tá escrito. Isso não deve abrir uma nova fase, sabe? Tipo, tem que ser mais direto ao ponto nesse sentido. Deve ser... talvez a gente registre que foi feito esse ajuste ou algo do tipo, pra não ter depois rollback, mas tem que ser mais direto dentro dessa fase, entendeu? Tem que fazer parte dessa fase.

> Sim, esse gasto tá correto. Outra coisa que eu tô pensando aqui é que o implemente escreve muito, né? Ele cria um arquivo MD, implemente.md e também escreve no plan. Eu acho que ele devia escrever no plan e ele devia ser mais conciso, né? Não precisa escrever um livro lá. É só detalhes que precisam ser dados, né? Tem que ser mais conciso nesse sentido, só informar coisas que realmente precisam ser registradas.

> Isso que eu falei agora sobre escrever muito não é só do Express, tá? É da skill de forma geral. O que acontece é que o implement, eu acho que ele precisa ser um pouco otimizado, essa skill. Porque qualquer coisinha acaba, por exemplo, gastando 256 mil tokens. E aí, quando gasta 256 mil, ele tem que compactar, porque é o limite do chat do Codex. E aí, quando acontece isso, ele se perde um pouco, né? Depois que acontece a compactação. Dependendo do momento que aconteceu a compactação, ele se perde muito. Então eu queria otimizar um pouquinho o tanto que ele escreve, tudo que ele precisa fazer, do jeito que ele precisa fazer. A gente já começou a fazer essa otimização quando a gente mexeu no fluxo dele. Então antes ele lia muita coisa, e aí ele testava, simplificava e testava. Precisamos entender hoje como tá esse fluxo pra gente dar uma melhorada.

## Hipótese inicial

```text
HIPÓTESE: otimizar a execução de implementação em geral com uma trilha Express para mudanças simples, correções de validação na mesma fase, menos duplicação de registros e prova proporcional ao risco.
CONFIDENCE: ~95%, os limites principais estão fechados; a spec define o contrato de retomada e de registro.
```

## Trilha

### 1

ANOTEI: alterações simples de copy e apresentação não devem abrir uma fase nem exigir todo o ciclo; correções encontradas na validação humana devem ficar na fase da entrega.
Q: devemos tratar isso como um caminho Express, com patch direto e prova proporcional, preservando o fluxo completo para mudança de comportamento ou risco sensível?
GUESS: sim, porque o usuário quer rapidez para ajustes pequenos sem reduzir as proteções aplicáveis a mudanças de maior impacto.
R: “Sim, você pode seguir com esse guess.” O usuário acrescentou que ajustes de validação humana pertencem à fase em andamento e podem ser registrados para preservar a correção.

### 2

ANOTEI: o implement grava em `implement.md` e também altera `plan.md`, gerando texto repetido; a otimização precisa reduzir registros e consumo de contexto.
Q: `plan.md` deve ser o único registro da execução por task, deixando de criar `implement.md`, com dados concisos de paths, prova, commit e desvios relevantes?
GUESS: sim, porque `plan.md` já contém a fila e a verificação planejada, enquanto a review pode reaproveitar a prova registrada ali.
R: “Sim, esse gasto tá correto.” O usuário esclareceu que a otimização é geral na skill, não limitada ao Express, e pediu revisar o fluxo atual, os testes e as leituras para evitar gasto alto e perda de contexto após compactação.

### 3

ANOTEI: o caminho Express deve evitar inicialização e artefatos VibeFlow para um ajuste simples sem mudança de comportamento.
Q: esse caminho também deve funcionar quando o projeto não tem `.vibeflow/`, sem chamar `vibe-init`?
GUESS: sim, porque exigir init recriaria o custo de processo que o Express foi criado para remover.
R: “sim”. O Express não exige `.vibeflow/` nem `vibe-init` quando o pedido é claro, localizado e não muda comportamento nem toca risco sensível.

## Resultado

Entendi assim:

- O quê: simplificar o fluxo geral de `vibe-implement`, criar um caminho Express sem fase para mudanças pequenas, manter correções de validação na fase atual, remover duplicação de registro e reduzir leituras, provas e prosa sem necessidade.
- Pra quem: usuário e agentes que executam as skills VibeFlow em tarefas de código e interface.
- Por quê: tarefas pequenas hoje recebem um processo extenso, consomem contexto e podem perder continuidade quando o chat compacta.
- Sucesso: mudanças de baixo risco terminam com patch e checagem focada sem `.vibeflow/` ou fase; correções da validação humana ficam registradas na fase original; o plano preserva apenas estado, paths, prova e desvios que permitam review e retomada; o relatório operacional não despeja o inventário completo da árvore de fases.
- Limite: segurança, privacidade, jurídico, dados, comportamento e integração continuam recebendo prova proporcional ao risco. Falha ou edição de código/teste após prova exige repetir a verificação afetada.
- Fora: remover gates necessários, criar dependência nova ou garantir que qualquer tarefa fique abaixo de um limite fixo de tokens.
- Visual: N/A, a mudança é no contrato operacional das skills e scripts, sem UI do produto.

## Handoff

vibe-spec

- Chat: recomende novo chat para a spec; se o humano preferir continuar, prossiga sem bloquear. Este `interview.md` é a ponte.
