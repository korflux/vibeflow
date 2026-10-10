# Delegação a subagentes

Abra esta referência antes de delegar trabalho a um subagente (analyze, T*, review ou correção) e ao decidir se um subagente compensa. Cada skill diz quando delega; este arquivo define como. As cópias em `vibe-plan` e `vibe-implement` são idênticas e mudam juntas.

## Papéis por perfil

Descreva o papel pelo perfil, nunca por nome de modelo. Host que não permite escolher o modelo por subagente usa o padrão.

| Papel | O que faz | Perfil | Escreve |
|---|---|---|---|
| `explorador` | lê e busca no código e devolve paths e trechos | rápido e barato | nada |
| `verificador` | executa provas integradas, sem escrever testes ou corrigir código | rápido e barato | somente arquivos normalmente gerados pela prova |
| `implementador` | implementa código/checagens locais ou complementa testes, conforme a etapa delegada | padrão do host | código ou testes dos paths autorizados |
| `corretor` | corrige falhas pré-review ou R* pela causa raiz e executa provas afetadas | padrão do host | código e testes dos paths da correção |
| `revisor` | executa a `vibe-review` no alvo; o analyze delegado usa o mesmo perfil | forte | `review.md` ou `analyze.md`, conforme o escritor único |

## Quando delegar

Delegue quando a skill manda (implementador por T*, revisor, analyze) ou quando a busca ou a prova é ampla o bastante para encher o contexto do coordenador: varredura de vários módulos, suíte longa, muitos arquivos lidos só para localizar um símbolo. Não delegue a leitura de um ou dois arquivos conhecidos, um `rg` pontual nem uma prova curta: o pedido custa mais que a tarefa. Delegação em paralelo segue a regra da skill chamadora, com isolamento e ownership definidos; este contrato não a autoriza sozinho.

## Pedido ao subagente

O subagente nasce sem o contexto do chat, então o pedido é autocontido. Inclua a etapa delegada (código, testes, validação ou correção), o resultado esperado, o ID da tarefa (T*, R* ou A*), `Spec:` e `Deps`, o comando de verificação, os paths conhecidos, as proibições abaixo, a regra de instalação da skill chamadora e o formato do relatório. Passe o recorte da tarefa, não o plan inteiro.

## Relatório do subagente

Formato fixo, em texto:

```text
estado: verde | bloqueado | pergunta
paths: <arquivos alterados, um por linha, ou nenhum>
prova: <comando e resultado>
pendencias: <o que ficou de fora ou nenhuma>
pergunta: <só quando o estado é pergunta, com a recomendação>
```

`verde` comprova somente o recorte delegado. No Modo A por etapas acrescente `etapa: codigo | testes | validacao | correcao` e informe se a evidência é local ou integrada, com inputs e resultado; verde local não autoriza marcar T* concluída. `bloqueado` é impedimento real, descrito em `pendencias`. `pergunta` é decisão que só o humano toma. A skill pode acrescentar campos do papel, como o veredito e os R* abertos do revisor, sem remover os cinco acima.

## Escritor único e proibições

Somente o coordenador altera `plan.md`, `spec.md`, `review.md` e `AGENTS.md`, opera o índice Git e cria commits. Subagentes devolvem relatório. Há duas exceções controladas, ambas porque o arquivo pertence à skill do próprio subagente: o revisor grava o `review.md`, e o subagente de analyze grava o `analyze.md` e aplica as correções diretas que a `vibe-analyze` prevê em spec, design e plan. O implementador e o corretor nunca editam o `review.md`.

Todo subagente herda estas proibições:

- `git push`, `git add -A`, `git add .`, amend, squash, force push e qualquer commit.
- Enfraquecer, pular ou apagar teste para obter verde; mudar uma asserção exige justificativa ligada ao aceite.
- Segredo ou credencial em código, log ou relatório.
- Alterar path fora da tarefa; um path extra no diff vai para `pendencias`.
- Instalar ferramenta fora da regra de instalação da skill chamadora; instalação que exija credencial, conta, pagamento, elevação administrativa ou configuração persistente de integração vira `pergunta`.

## Conferência pelo coordenador

O relatório é evidência, nunca autoridade. Antes de registrar qualquer coisa, confira os paths citados contra `git status` e o diff real, e a saída da prova contra o comando declarado. Quando o subagente trabalha na mesma árvore do coordenador, de forma sequencial, sua prova vale para o recorte e os inputs efetivamente cobertos, e o coordenador não a repete; no Modo A por etapas, a checagem local não substitui a validação integrada delegada ao verificador; repita só quando o relatório não traz evidência suficiente ou o diff o contradiz. Divergência volta ao mesmo papel com o problema descrito, e nada é registrado antes disso.

## Fallback sem subagentes

Host sem subagentes: a skill executa o trabalho inline e avisa o motivo em uma linha. Subagente que não consegue abrir outro executa `explorador` e `verificador` inline. O fallback não muda quem escreve o quê: o escritor único e as proibições continuam valendo, e a skill chamadora define o caminho alternativo, como uma T* por run.
