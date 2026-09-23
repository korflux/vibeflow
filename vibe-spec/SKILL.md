---
name: vibe-spec
description: >
  Especifica comportamento, escopo, aceite e decisões em `.vibeflow/phases/phase-N-slug/spec.md` ou `.vibeflow/mvp/spec.md`.
  Use when the user runs /vibe-spec, pede spec, especificar a entrega,
  fechar comportamento e aceite antes do plan, ou a rota é high/xhigh/max
  com intenção já razoavelmente clara, mesmo que não diga vibe-spec.
---

# vibe-spec

Não invente `n`, slug ou path. Sem `.vibeflow/`, pare e mande `/vibe-init`. Não grave em `docs/` nem na raiz.
Só o decidido. Open Questions no arquivo é defeito. O arquivo vivo é a fonte da verdade; o chat não substitui o disco.
No MVP, preserve IDs críticos da interview e declare `mantém`, `cria` ou `substitui`; não publique decisões em `REGRAS.md`.

A investigação começa pela pergunta de comportamento e aceite que a spec precisa fechar no fluxo real. Use `rg --files` para localizar os artefatos e entradas do fluxo; use `rg -n` para localizar nomes, símbolos, contratos e decisões. Abra somente os paths que sustentam o desenho e expanda a leitura quando uma lacuna bloquear a prova. O inventário é mapa de seleção, não autorização para ler a árvore inteira.


## 0. Entender e usar o script

1. Resolva o diretório desta skill e leia o motor que vai executar: `scripts/spec.ps1` no Windows ou `scripts/spec.py` no fluxo Unix. Entenda flags, seleção de alvo, tratamento de erros, preparação do destino e preservação do arquivo vivo antes de chamá-lo. Se encontrar defeito, corrija o motor e prove o contrato antes de continuar.
2. No cwd do repo:
   - Windows: `pwsh "<skill>/scripts/spec.ps1"`.
   - Unix: `bash "<skill>/scripts/spec.sh"`.
   - Modo MVP: acrescente `-Mvp` ou `--mvp`.
3. Leia o JSON operacional emitido no stdout pelo comando acima. Use `rg --files` e `rg -n` para localizar `interview.md`, `spec.md`, `.vibeflow/REGRAS.md` e somente os paths do codebase necessários para entender o comportamento pretendido. Abra as entradas e dependências do fluxo; o inventário não é uma ordem para ler a árvore inteira.

Erros determinísticos previstos: `INIT_AUSENTE` exige `/vibe-init`. `PHASES_INESPERADO`, `MVP_INESPERADO`, `MVP_INTERVIEW_AUSENTE`, `SPEC_JA_PLANEJADA`, `SPEC_SEM_ALVO`, `FASE_AUSENTE`, `FASE_EXISTE`, `SLUG_INVALIDO` e `MODO_INVALIDO` exigem diagnosticar a causa e não devem ser contornados.

## 1. Abrir

Declare em cerca de cinco linhas: confiança, rota, modo, alvo e estado do artefato vivo.

```text
CONFIDENCE: ~85%, entendo: lock por bloco no editor | falta: concorrência
modo: reuse · alvo: phase-1-lock-bloco · interview: sim · artefato vivo: presente
```

- `modo=criar` (sem interview anterior): use slug no apply para criar nova pasta de fase.
- `interview_pendente`: proibido avançar `next_n`. Use a mesma fase da interview.
- `rota=mvp`: alvo fixo `.vibeflow/mvp`, interview obrigatória e proibido usar slug ou dir.

## 2. Gate e escopo

```text
CONFIDENCE: ~N%, entendo: ... | falta: ...
```

| Sinal | Ação |
|---|---|
| Typo, rename, inequívoco de uma linha | Não usar spec |
| `/vibe-spec` explícito | Usar, se a intenção estiver clara |
| < ~80% e falta quem/por quê/sucesso | Parar. Encaminhar para `/vibe-interview` (1 a 2 linhas do que falta) |
| ~80%+ ou interview existente no disco | Seguir. Lacunas pontuais de desenho = Q + RECOMENDO |
| `plan.md` já existente no alvo | Não sobrescrever. Pedido novo exige outra fase |

No modo MVP, a spec consolida a baseline inteira do produto e mantém o handoff max. Não reduza a descoberta a uma feature nem remova uma premissa assumida sem registrar a substituição.
Spec define esta mudança e seu delta observável, não o manual completo do repositório.

Siga esta ordem sem repetir a interview:
1. **Cobertura:** compare jornadas, páginas e módulos aplicáveis da interview com a entrega. Para cada item, indique o fluxo `F*` que o cobre ou por que ficou fora/N/A. Sem interview, derive a lista mínima do pedido e do produto existente. Falta que muda a intenção volta à interview; detalhe de comportamento fica aqui.
2. **Comportamento:** descreva somente o que a entrega fará, com entradas, respostas, regras, estados e erros. Preserve decisões já fechadas; pergunte apenas o que muda materialmente o resultado.
3. **Aceite:** associe cada capacidade ou fluxo a resultados observáveis `A*` e critérios de sucesso `C*` sem fragmentar detalhes em critérios redundantes. Aceite não representa quantidade de testes; uma prova pode cobrir vários critérios.
4. **Limites e handoff:** registre contratos e decisões técnicas apenas quando necessários para garantir comportamento, segurança ou interoperabilidade. Deixe arquivos, comandos, ordem de implementação e escolha interna reversível para o plan.

## 3. Seams e decisões (chat)

Apenas o que, se errado, invalida o desenho. Uma pergunta por vez.

```text
Q: <decisão>
RECOMENDO: <opção>, <1 linha explicando motivo e impacto>
(ok / outra?)
```

- "Tanto faz" crava a recomendação. Dúvida de intenção central exige `vibe-interview`.
- Seam óbvio: registre diretamente no arquivo.
- Sucesso vago: alinhe 1 a 3 critérios observáveis no chat e consolide em `C*`.
- Toda decisão fechada entra em **Suposições e decisões**.
- No MVP, decisões críticas da interview entram em **Decisões críticas** mantendo o ID: `mantém` para preservar, `cria` para novas decisões necessárias e `substitui` citando o ID e explicando o delta.
- Se houver UI visível ao usuário, consulte `references/ui-visual-direction.md` antes de gravar.
- Se a entrega envolver banco de dados, persistência ou valores monetários/cálculos exatos, consulte `references/database-and-migrations.md` para fechar invariantes de dados e precisão necessários ao comportamento. Índices, estratégia de migration e consultas ficam para o plan quando não forem restrições do produto.
- Se a entrega receber dados externos (request, query, headers, arquivos ou input), declare a allowlist de campos e valores aceitos e o tamanho máximo por entrada. Registre N/A fundamentado somente quando não houver entrada externa.
- Se a entrega tocar API, handle ou token, segredo, dado pessoal ou rota autenticada, feche as demais proteções aplicáveis: validade e invalidação de credenciais, autorização no servidor com anti-IDOR, rate limit, CSRF, CORS com allowlist de origens quando houver acesso cross-origin (nunca `*` junto com credenciais), headers e CSP. Declare N/A fundamentado para controles sem aplicação. Registre apenas as regras relevantes em Suposições e decisões, Contratos e restrições necessárias e Boundaries. Ausência de proteção exigida pelo fluxo bloqueia aprovação.

## 4. Escrever e salvar

Artefato vivo: `<created.path>/spec.md`. Molde: `templates/spec.md`. Mantenha `# Status: rascunho` enquanto a spec estiver em elaboração.
Não pergunte se pode salvar e não cole o corpo do documento no chat.

1. Execute o apply através do script. Ele prepara o arquivo vivo somente quando ausente e preserva bytes quando ele já existe:
   - Reuse/atualizar em phase existente:
     `pwsh "<skill>/scripts/spec.ps1" -Apply`
     `bash "<skill>/scripts/spec.sh" --apply`
   - Criar nova phase (sem interview prévia):
     `pwsh "<skill>/scripts/spec.ps1" -Apply -Slug "<frase curta>"`
     `bash "<skill>/scripts/spec.sh" --apply --slug "<frase curta>"`
   - Modo MVP:
     `pwsh "<skill>/scripts/spec.ps1" -Apply -Mvp`
     `bash "<skill>/scripts/spec.sh" --apply --mvp`
2. Escreva ou atualize diretamente o arquivo vivo. Omita seções não aplicáveis. Sem `FR-00N`, mural de user stories, CSS, paleta ou token visual: a spec fecha comportamento e aceite. Para cada fluxo ou UX, use `F*` com Jornada, Rota, Gatilho, Pré-condição, Superfície por passo, Passos com ação e resposta, Validações, Erros, Estados e Aceite `A*`. Passo sem superfície é defeito; escolha tela, popup, drawer, inline, redirect ou toast. Em página informativa sem interação complexa, um `F*` curto pode cobrir entrada, conteúdo/CTA, navegação e estados aplicáveis; marque N/A com motivo para validações ou erros inexistentes. Detalhe fluxos interativos no nível necessário para não deixar decisões de produto ao design ou plan. Se listar N telas e detalhar só o shell, declare que o visual por tela vai para design. Fato em mock que vira contrato precisa de nome, forma, janela e escopo ou delegação explícita ao design com Ask first. Em Como provar, descreva a evidência observável de cada `A*`; comandos e estratégia de testes ficam no plan.
3. Responda no chat apenas:

```text
Spec gravada: <created.path>/spec.md

- Objetivo: <1 linha>
- Cobre: <2 a 4 bullets>
- Fora: <1 linha>
- Como provar: <1 linha>
- Chat: com UI, continue neste chat para `vibe-design` e recomende novo chat para `vibe-plan`; sem UI, recomende novo chat para `vibe-plan`. Se o humano preferir, continuar aqui é válido.

Arquivo disponível em <created.path>/spec.md. Responda "aprovado" para confirmar, "pode ir pro design" quando houver UI, "pode ir pro plan" sem UI (ou "pode ir para a próxima fase") para avançar imediatamente, ou indique os ajustes desejados.
```

## 5. Ajuste ou aprovação

| Resposta | Ação |
|---|---|
| Aprovado (sem pedir plan) | `# Status: aprovado` no vivo; checklist humana `[x]`; parar e aguardar próximo comando |
| "Pode ir pro design" com UI / "pode ir pro plan" sem UI / pede próxima porta aplicável | `# Status: aprovado` no vivo; checklist humana `[x]`; iniciar a próxima porta aplicável |
| Pedido de alteração | Patch direto no arquivo vivo; até 5 bullets no chat; solicitar nova conferência |
| "Parece bom" sem pedir plan | Perguntar: "Aprovado no arquivo ou deseja algum ajuste?" |
| Intenção quebrou | Encaminhar para `vibe-interview`. Não forçar plan |

Rascunho sem "aprovado" e sem pedido explícito da próxima porta aplicável não autoriza avançar.

## 6. Fechar

Não commite no git. Não dispare a próxima skill a menos que o usuário tenha pedido explicitamente para avançar (§5).
`vibe-interview` e `vibe-spec` podem continuar no mesmo chat; com UI, também pode seguir para `vibe-design` nele. Recomende novo chat ao iniciar `vibe-plan`. Se o humano preferir manter o chat atual, continue sem bloquear e use o `spec.md` vivo e o handoff como ponte.
Handoff registrado no arquivo: `vibe-design` com UI visível, senão `vibe-plan`. Não pular design em silêncio. `plan.md` existente bloqueia nova escrita, pedido novo exige outra phase.

