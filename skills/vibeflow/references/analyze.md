# Etapa analyze

O líder nunca escreve `analyze.md`. Não atualize decisões vigentes nem `AGENTS.md`. No MVP, conflito crítico sem `substitui` explícito bloqueia a implementação.

## Entrada

- Gate (`SKILL.md`, seção 3): rota `max` ou MVP e plan aprovado. Sem `plan.md` ou sem `spec.md` no alvo, não há analyze; no MVP, a interview também é obrigatória. Plan em rascunho volta ao líder, que obtém a aprovação antes de delegar.
- O revisor lê `interview.md`, `spec.md`, `design.md`, `plan.md`, o `analyze.md` vivo, `AGENTS.md` e os paths citados, só o que sustenta o cruzamento.

## Quem faz

| Quem | Faz |
|---|---|
| Revisor de contexto limpo | Cruza os artefatos, aplica as correções diretas permitidas, grava `analyze.md` e devolve veredito, correções e perguntas |
| Líder | Delega, confere o relatório, leva as perguntas materiais ao humano e devolve cada resposta ao mesmo revisor |
| Finalizador | Marca a aprovação humana quando o veredito é `limpo` |

Perfil revisor ausente ou não carregado: pergunte ao humano com a recomendação de rodar `/vibeflow init` e recarregar o host; nada é despachado. Sem subagentes, o líder grava checkpoint e instrui abrir chat novo com `/vibeflow analyze`; nesse chat, o agente atua como revisor e conduz as perguntas e a aprovação inline.

## Passos

### Líder

1. Leia `references/delegation.md` e delegue ao revisor o path do alvo, os artefatos e as regras desta referência.
2. Confira o relatório contra o `analyze.md` gravado e contra o diff de `spec.md`, `design.md` e `plan.md`, sem refazer o cruzamento. Divergência volta ao revisor com o problema descrito.
3. Faça ao humano as perguntas em aberto, uma por vez, com recomendação. Cada resposta volta ao mesmo revisor, que a aplica nos artefatos, registra em Clarificações e atualiza o veredito.

### Revisor

O revisor não pergunta ao humano. Ambiguidade que dependa dele vira achado pendente no `analyze.md` (Resolução: aguardando resposta) e entra em `pergunta` no relatório, com recomendação; achado bloqueante pendente mantém o veredito `bloqueado`. O status continua `rascunho`. É proibido implementar código, criar commit, iniciar a implementação e editar `AGENTS.md`.

Leia `references/analyze/coverage.md` como mapa interno e cruze:

1. **Interview → spec:** resultado, jornadas, páginas e módulos aplicáveis contra Cobertura da origem, `F*`, Objetivo, A*/C* e Fora. Item omitido sem motivo impede o veredito limpo; módulo N/A não exige detalhe.
2. **Spec → plan:** cada A*/C* tem T* no campo `Spec:`; cada T* referencia A*/C* ou é infraestrutura justificada.
3. **Plan → spec:** nenhuma T* inventa comportamento, caminho ou módulo fora do escopo aprovado.
4. **Design:** com UI visível, design ausente ou não aprovado impede o veredito limpo; sem UI, N/A explícito.
5. **Testes e executabilidade:** cada T* tem `Prova afetada:` com comando executável real; o mesmo teste pode servir a várias T*. Ponto de entrada criado ou alterado traz o smoke na mesma T*. Verificação só manual vira comando real no `plan.md`. Ferramenta ausente segue a regra de instalação de `references/delegation.md` e entra sob a T* que depende dela; bloqueio externo é registrado, sem T* artificial de instalação.
6. **Contrato da implementação:** formato e sobreposição de `Arquivos:` conforme `references/plan.md`, `Prova afetada:` restrita ao recorte e cobrindo os A*/C* da T*, uma única `Regressão completa` com comandos reais e prontidão com local e destino por requisito, inclusive perfis no Modo A. Gravidades e correções na seção 3 de `references/analyze/coverage.md`. Phase da v1 sem esse formato recebe N/A nesta dimensão, sem migração.
7. **Decisões críticas (MVP):** cada ID cruzado entre interview, spec e plan; divergência sem `substitui` ou ID órfão é ajustada ou vira pergunta quando a mudança puder ser intencional.
8. **AGENTS.md:** violação de regra mandatória (segurança, auth, dados, segredos, CSP) recebe patch corretivo nos artefatos.
9. **Consistência:** duplicação, adjetivo sem métrica, furo de aceite e termo inconsistente recebem correção direta.

Erro óbvio e lacuna determinística são corrigidos diretamente em `spec.md`, `design.md` ou `plan.md` e entram em **Achados e Resoluções**, com gravidade `CRITICAL`, `HIGH`, `MEDIUM` ou `LOW` e IDs `F1`, `F2`... Ambiguidade real de negócio ou arquitetura vira pergunta; a resposta transmitida pelo líder entra no artefato correspondente e em **Clarificações com o Usuário**.

O revisor cria o `analyze.md` a partir de `templates/analyze.md`, ou atualiza o vivo. Veredito `limpo` quando todas as correções foram aplicadas e o plano está pronto para execução; `bloqueado` se restar achado CRITICAL ou HIGH sem correção nem bloqueio real registrado.

## Saída

O relatório fixo de `references/delegation.md` acrescenta `veredito` (`limpo` ou `bloqueado`), cobertura (A*/C* com T* sobre o total), qualidade de testes, contrato da implementação, `correcoes` (F* aplicados, com o arquivo de cada um) e `perguntas`.

| Resposta do humano | Ação |
|---|---|
| Aprovado com veredito `limpo` | Finalizador marca `# Status: aprovado` e a aprovação humana; o líder para |
| "Pode ir pro implement" com veredito `limpo` | Mesma aprovação; o líder inicia `references/implement.md` |
| Pedido de alteração | Volta ao revisor; o líder pede nova conferência |
| Pedido de implementação com veredito `bloqueado` | Recusar com a frase do gate e exibir os achados bloqueantes |
| Spec, design, plan ou intenção quebrou | Voltar à etapa dona |

## Fechar e próxima etapa

Sem commit nesta etapa. Próxima etapa: `implement`, somente com veredito `limpo` e aprovação humana.
