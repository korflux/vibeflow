# vibe-interview, análise

## Decisão central

Entrevista é uma porta semântica. O script não tenta inferir se o pedido é um MVP nem transforma respostas em documento. A IA classifica a rota, faz perguntas adaptativas e escreve diretamente no arquivo vivo preparado pelo motor.

## Fluxo decidido

```text
pergunta de bootstrap
  → inventário do alvo phase ou MVP
  → Anotei → pergunta focada → guess explícito → resposta ou correção
  → decisões críticas e lacunas reversíveis
  → apply prepara interview.md
  → IA registra a entrevista no vivo
  → humano lê o arquivo
  → handoff vibe-spec
```

O inventário é evidência de seleção, não uma ordem para abrir a árvore. A investigação começa pela pergunta que motivou a entrevista, usa `rg --files` para localizar entradas e `rg -n` para confirmar símbolos e decisões, e só expande o conjunto de leitura quando uma lacuna bloquear o resultado.

## Por que o alvo MVP é separado

`.vibeflow/mvp/` representa o baseline único de um produto novo. Ele não recebe `n`, slug ou uma phase cronológica. A flag `--mvp` é uma decisão da IA, porque o motor não deve interpretar linguagem natural nem criar uma rota semântica implícita.

O template continua único. Seções de cobertura, produto, técnica, visual e operação são omitidas no modo phase. Isso evita dois formatos concorrentes sem transformar a entrevista normal em um formulário.

## Escrita direta e preservação

O ciclo anterior dependia de um arquivo temporário para transportar a prosa até o apply. O contrato atual separa responsabilidades: o script cria apenas a pasta e o arquivo vivo ausente; a IA escreve o conteúdo diretamente e mantém `# Status: rascunho` até a aprovação. Uma segunda execução preserva o arquivo existente.

Essa separação reduz o risco de substituir uma entrevista em andamento e torna o arquivo no disco a ponte entre chats. O relatório continua útil para seleção e auditoria, mas não carrega conteúdo semântico.

## Política de perguntas e chat

Cada turno mostra primeiro `Anotei`, uma leitura fiel do pedido ou da resposta anterior; em seguida destaca uma pergunta focada e apresenta abaixo um `Meu guess` provisório, com motivo curto. A pessoa pode dizer “sim” para confirmar somente aquele guess ou corrigi-lo. A Trilha preserva separadamente a interpretação registrada, a pergunta, o palpite e a resposta humana. Isso torna visível o entendimento do agente e reduz ambiguidade sobre o que “sim” confirma. Não invente evidência nem use palpite como decisão em temas sensíveis, legais, caros ou irreversíveis.

Perguntas devem fechar decisões que o disco não sustenta. Recomendações precisam declarar escolha, motivo e impacto. `init`, `interview`, `spec` e `design` podem permanecer no mesmo chat; a partir de `plan`, recomende chat novo para cada porta indicada em `.vibeflow/REGRAS.md`. Nenhuma troca de chat é gate.

Para um produto digital novo, a descoberta percorre primeiro solicitação, solução, jornadas completas e páginas. Só então consulta módulos de completude por gatilho: hospedagem e dados, acesso, permissões, identidade, SEO, planos e elementos transversais de tela. Assim o núcleo expressa o que o usuário quer construir; os módulos revelam requisitos de sustentação sem impor autenticação, banco ou CMS a um site estático. A infraestrutura existente é levantada antes da recomendação técnica.

## Cortes

| Não entrou | Motivo |
|---|---|
| Detector automático de MVP | A classificação pertence à IA. |
| Template separado para MVP | Duplicaria a estrutura e criaria divergência. |
| Questionário rígido | Impediria adaptação às respostas e às evidências. |
| Escrita semântica no script | O motor deve permanecer determinístico. |
| Persistência temporária como requisito | O vivo já é a fonte de continuidade. |
| Atualização de `REGRAS.md` na entrevista | Decisões vigentes dependem de implementação, review e confirmação humana. |

## Impacto

Features continuam entrando em phases com slug calculado; projetos novos seguem o baseline MVP. Em ambos os casos, o caminho, o status e o handoff ficam no disco. A próxima skill recebe uma fonte viva legível, sem depender do histórico do chat.
