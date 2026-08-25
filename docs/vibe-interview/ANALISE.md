# vibe-interview: análise da rota MVP

## Problema

A entrevista normal tratava um produto novo como uma feature. Ela fechava intenção, mas não garantia as decisões que tornam um MVP implementável: funcionamento, telas, usuários, acesso, dados, stack, infraestrutura, identidade, operação e segurança. O script também era descrito como piloto da execução, invertendo o papel correto da IA.

## Fluxo decidido

```text
IA entende o motor
  → classifica produto novo ou mudança
  → chama inventário com modo explícito
  → entrevista de forma adaptativa
  → recomenda e assume lacunas reversíveis
  → obtém decisão humana para gaps críticos
  → registra cobertura e IDs críticos
  → motor promove bytes no alvo correto
```

O script não interpreta linguagem natural. A flag `--mvp` ou `-Mvp` representa uma decisão já tomada pela IA. Isso mantém o motor determinístico e permite que a própria IA identifique e corrija um defeito durante o uso.

## Por que `.vibeflow/mvp/`

MVP é baseline do produto, não uma etapa cronológica comum. Colocá-lo em `phase-1` faria uma phase posterior parecer automaticamente mais correta quando, na realidade, mudanças críticas precisam declarar o que substituem. O diretório especial torna o baseline visível e único, sem inflar `REGRAS.md` com todo o conteúdo da descoberta.

Somente a tabela compacta de decisões vigentes chega às regras após review humana aprovada. O interview registra o histórico completo, mas não publica decisões por conta própria.

## Descoberta sem formulário

O catálogo de MVP fica em `references/mvp-discovery.md`, lido somente no modo especial. A skill obriga cobertura, mas não ordem fixa nem exposição do checklist. A IA usa blocos pequenos e adapta cada bloco às respostas já obtidas.

Esse desenho equilibra dois riscos:

| Risco | Controle |
|---|---|
| Encerrar cedo e deixar o projeto indefinido | Estados de cobertura e proibição de pendente crítico no fechamento |
| Assustar quem não sabe responder tudo | Blocos de uma a três perguntas, recomendação clara e premissas assumidas |

## Política de recomendação

Uma recomendação precisa ter escolha, motivo contextual e impacto. Contra só entra quando pode mudar a decisão. Isso evita devolver indecisão ao usuário por meio de listas neutras de opções.

Os baselines são preferências condicionais, não stack universal:

- Next.js, Auth.js quando aplicável, Zod e PostgreSQL para aplicação web dinâmica.
- Astro para site predominantemente estático.
- Supabase quando o usuário não opera PostgreSQL, não tem infraestrutura ou precisa de administração visual de tabelas.
- GitHub, Vercel e Supabase quando não há infraestrutura aproveitável.
- Redis somente com necessidade concreta.

A infraestrutura existente é perguntada antes. Hostinger, HostGator, VPS, runtime, banco e nível de acesso podem invalidar a recomendação inicial.

## Segurança e primeiro acesso

A preferência original por master no `.env` foi preservada no objetivo, recuperar acesso, mas não como senha permanente. O padrão é bootstrap ou break-glass por configuração de ambiente, temporário, auditado, forte e desabilitado depois do uso. Assim, o VibeCoder mantém uma rota recuperável sem criar uma credencial universal invisível.

## Visual

O padrão inicial é clean, minimalista e moderno, com um tema principal escolhido pelo contexto e suporte light/dark planejado desde o começo. Cor primária, tokens semânticos, fonte moderna e acessibilidade entram na descoberta. Identidade existente sempre prevalece sobre geração automática.

## Compatibilidade

O template continua único. Seções MVP têm instrução explícita de omissão, portanto a entrevista normal permanece curta. O relatório só recebe campos aditivos, e o fluxo phase mantém cálculo de `next_n`, slug, promoção e fase aberta.

## Cortes

| Não entrou | Motivo |
|---|---|
| Detector de MVP dentro do script | Semântica pertence à IA |
| Um arquivo de template separado para MVP | Duplicaria estrutura e permitiria divergência |
| Questionário rígido | Impede adaptação e piora fluidez |
| Stack obrigatória | Infraestrutura e tipo de produto podem exigir outra escolha |
| Redis por padrão | Complexidade sem necessidade concreta |
| Senha master permanente | Backdoor de alto risco |
| Atualização de `REGRAS.md` no interview | Decisão só se torna vigente após review humana aprovada |

## Impacto

Projetos novos saem do interview com informação suficiente para abrir a spec e percorrer a rota max no mesmo alvo. Features continuam usando phases sem carregar o catálogo de MVP. A IA permanece responsável pela condução e consegue auditar o script que apenas protege o contrato de disco.
