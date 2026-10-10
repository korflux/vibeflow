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

Delegue papéis obrigatórios da skill (implementador, revisor, analyze) e investigação/validação ampla, com vários fluxos/ambientes ou diagnóstico. Faça inline buscas pontuais, conferências e prova curta com comando/cobertura definidos, respeitando a separação entre escritor e executor da integração. Reutilize agentes para trabalho relacionado; mantenha review independente. Não crie handoff ou nova execução só para representar etapa com evidência já válida. Paralelo depende da skill chamadora e de isolamento/ownership; este contrato não o autoriza.

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

`verde` comprova somente o recorte delegado. No Modo A por etapas acrescente `etapa: codigo | testes | validacao | correcao` e informe se a evidência é local ou integrada, com inputs e resultado; verde local não autoriza marcar T* concluída. `bloqueado` é impedimento real, descrito em `pendencias`. `pergunta` é decisão que só o humano toma. A skill pode acrescentar campos do papel, como o veredito e os R* abertos do revisor, sem remover os cinco acima. Na review, informe cobertura da solicitação e limitações de origem referenciando a matriz no review.md; plan sozinho não certifica completude.

## Escritor único e proibições

Somente o coordenador altera `plan.md`, `spec.md`, `review.md` e `AGENTS.md`, opera o índice Git e cria commits. Subagentes devolvem relatório. Há duas exceções controladas, ambas porque o arquivo pertence à skill do próprio subagente: o revisor grava o `review.md`, e o subagente de analyze grava o `analyze.md` e aplica as correções diretas que a `vibe-analyze` prevê em spec, design e plan. O implementador e o corretor nunca editam o `review.md`.

Todo subagente herda estas proibições:

- `git push`, `git add -A`, `git add .`, amend, squash, force push e qualquer commit.
- Enfraquecer, pular ou apagar teste para obter verde; mudar uma asserção exige justificativa ligada ao aceite.
- Segredo ou credencial em código, log ou relatório.
- Alterar path fora da tarefa; um path extra no diff vai para `pendencias`.
- Instalar ferramenta fora da regra de instalação da skill chamadora; instalação que exija credencial, conta, pagamento, elevação administrativa ou configuração persistente de integração vira `pergunta`.

## Conferência pelo coordenador

O relatório é evidência, nunca autoridade. Confira paths, diff, comando/resultado, cobertura e inputs atuais antes de registrar. Preserve contexto já conferido, sem reabrir investigação de inputs inalterados ou repetir provas suficientes. No Modo A por etapas, checagem local não substitui integração: reutilize somente evidência que cubra o estado integrado e tenha executor separado do escritor. Deixe resultado/snapshot no lar definido pela skill e referencie em vez de copiar para vários artefatos. Divergência ou lacuna concreta volta ao mesmo papel; renove só as provas afetadas, incluindo consumidores/dependências, e registre o motivo. Relatório incompleto não autoriza conclusão.

## Fallback sem subagentes

Host sem subagentes: a skill executa o trabalho inline e avisa o motivo em uma linha. Subagente que não consegue abrir outro executa `explorador` e `verificador` inline. O fallback não muda quem escreve o quê: o escritor único e as proibições continuam valendo, e a skill chamadora define o caminho alternativo, como uma T* por run.
