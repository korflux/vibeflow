# Etapa spec

Só o decidido: pergunta aberta no arquivo é defeito. O arquivo vivo é a fonte da verdade; o chat não substitui o disco. No MVP, preserve os IDs críticos da interview com `mantém`, `cria` ou `substitui`; não publique decisões em `AGENTS.md`.

## Entrada

- Gate (`SKILL.md`, seção 3): em `xhigh`, `max` e MVP, interview aprovada; em `high`, a spec abre a phase. `plan.md` já existente no alvo bloqueia nova spec: pedido novo exige outra phase.
- Leia `interview.md`, o `spec.md` vivo, `AGENTS.md` e os contratos e decisões citados. Leitura ampla do codebase vai ao explorador.

Declare em cerca de cinco linhas: confiança, rota, alvo, interview e estado do artefato vivo.

```text
CONFIDENCE: ~85%, entendo: lock por bloco no editor | falta: concorrência
rota: high · alvo: .vibeflow/phases/phase-1-lock-bloco/ · interview: N/A · spec: ausente
```

| Sinal | Ação |
|---|---|
| Typo, rename, inequívoco de uma linha | Não usar spec |
| Confiança abaixo de ~80% e falta quem, por quê ou sucesso | Parar e voltar à interview, com 1 a 2 linhas do que falta |
| ~80% ou mais, ou interview aprovada | Seguir; lacunas pontuais de desenho viram Q + RECOMENDO |

## Quem faz

| Quem | Faz |
|---|---|
| Líder | Fecha seams e decisões com o humano, uma pergunta por vez, e conduz a aprovação |
| Redator | Cria ou atualiza `spec.md` a partir das decisões entregues |
| Finalizador | Marca a aprovação e a checklist humana |

## Passos

1. **Cobertura:** compare jornadas, páginas e módulos aplicáveis da interview com a entrega; cada item recebe o `F*` que o cobre ou o motivo de ficar fora ou N/A. Sem interview, derive a lista mínima do pedido e do produto existente. Falta que muda a intenção volta à interview.
2. **Comportamento:** só o que a entrega fará, com entradas, respostas, regras, estados e erros. Preserve decisões fechadas; pergunte só o que muda materialmente o resultado. No MVP, a spec consolida a baseline inteira; fora dele, define esta mudança e seu delta observável.
3. **Aceite:** cada capacidade ou fluxo ganha resultados observáveis `A*` e critérios de sucesso `C*`, sem fragmentar detalhes. Aceite não representa quantidade de testes.
4. **Seams no chat:** apenas o que, se errado, invalida o desenho.

   ```text
   Q: <decisão>
   RECOMENDO: <opção>, <1 linha explicando motivo e impacto>
   (ok / outra?)
   ```

   - "Tanto faz" crava a recomendação. Dúvida de intenção central volta à interview. Seam óbvio entra direto no brief.
   - Sucesso vago: alinhe 1 a 3 critérios observáveis e consolide em `C*`.
   - Com UI visível, consulte `references/spec/ui-visual-direction.md`.
   - Com banco, persistência ou valores monetários e cálculos exatos, consulte `references/database-and-migrations.md` para os invariantes de dados e precisão do comportamento; índices, migrations e consultas ficam no plan quando não forem restrição do produto.
   - Com dados externos (request, query, headers, arquivos ou input), declare a allowlist de campos e valores e o tamanho máximo por entrada; N/A fundamentado só sem entrada externa.
   - Com API, token, segredo, dado pessoal ou rota autenticada, feche as proteções aplicáveis: validade e invalidação de credenciais, autorização no servidor com anti-IDOR, rate limit, CSRF, CORS com allowlist quando houver acesso cross-origin (nunca `*` com credenciais), headers e CSP, com N/A fundamentado para o que não se aplica. Proteção exigida ausente bloqueia a aprovação.
5. **Gravação:** o líder entrega ao redator as decisões, a rota e o path do alvo. O redator cria o `spec.md` a partir de `templates/spec.md`, ou atualiza o vivo, grava `# Rota:` quando a spec abre a phase e mantém `# Status: rascunho`:
   - Cada fluxo usa `F*` com Jornada, Rota, Gatilho, Pré-condição, Superfície por passo, Passos com ação e resposta, Validações, Erros, Estados e Aceite `A*`. Passo sem superfície (tela, popup, drawer, inline, redirect ou toast) é defeito. Página informativa simples usa `F*` curto, com N/A e motivo para validações ou erros inexistentes.
   - Sem `FR-00N`, mural de user stories, CSS, paleta ou token visual. Se listar telas e detalhar só o shell, declare que o visual por tela vai para o design. Fato de mock que vira contrato ganha nome, forma, janela e escopo, ou delegação explícita ao design com Ask first. Contrato compartilhado registra os `F*` consumidores.
   - Em Como provar, cada `A*` liga ao `F*` ou jornada, ao nível (`jornada` exige percorrer o fluxo; `local` observa a regra isolada) e à evidência observável; com UI, o que a tela renderizada mostra e em qual estado. Comando, path de teste e ferramenta ficam para o plan.
   - Handoff: `design` com UI visível, senão `plan` com `Design: N/A` e motivo.

## Saída

O líder confere a entrega contra as decisões e responde:

```text
Spec gravada: <alvo>/spec.md

- Objetivo: <1 linha>
- Cobre: <2 a 4 bullets>
- Fora: <1 linha>
- Como provar: <1 linha>

Responda "aprovado" para confirmar, "pode ir pro design" com UI, "pode ir pro plan" sem UI, ou indique os ajustes.
```

| Resposta | Ação |
|---|---|
| Aprovado | Finalizador marca `# Status: aprovado` e a checklist humana; o líder para |
| Pede a próxima etapa aplicável | Mesma aprovação; o líder inicia a etapa |
| Pedido de alteração | Redator aplica o patch; o líder resume em até 5 bullets e pede nova conferência |
| "Parece bom" sem pedir a próxima etapa | Perguntar: "Aprovado no arquivo ou deseja algum ajuste?" |
| Intenção quebrou | Voltar à interview |

## Fechar e próxima etapa

Rascunho sem aprovação e sem pedido explícito da próxima etapa não autoriza avançar. Sem commit nesta etapa. Próxima etapa: `design` com UI visível, senão `plan`; não pule o design em silêncio.
