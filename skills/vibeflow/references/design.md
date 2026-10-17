# Etapa design

Não edite código, teste ou lockfile nesta etapa. Não gere imagem final. Pergunta aberta no arquivo é defeito. Design não cria comportamento novo; spec e plan não inventam token.

## Entrada

- Gate (`SKILL.md`, seção 3): spec aprovada e UI visível. Sem UI visível, não há design: o `plan.md` registra `Design: N/A` com motivo. `plan.md` já existente no alvo bloqueia novo design.
- Spec em rascunho: aplique a aprovação implícita do `SKILL.md`, seção 3; fora dela, peça leitura e aprovação.
- Intenção, fluxo ou aceite frouxos voltam à spec.
- Leia `spec.md`, `interview.md`, DS, `DESIGN.md`, telas, componentes e tokens existentes. Leitura ampla vai ao explorador.

Declare em cerca de cinco linhas: modo de entrada, uso, alvo, spec e estado do artefato vivo.

```text
modo: com referência · uso: criar · alvo: .vibeflow/phases/phase-1-lock-bloco/ · spec: aprovado · design: ausente
```

## Quem faz

| Quem | Faz |
|---|---|
| Líder | Decide modo e uso, resolve dúvidas de apresentação com o humano e conduz a aprovação |
| Explorador | Lê DS, telas e componentes existentes quando a leitura for ampla |
| Redator | Cria ou atualiza `design.md` a partir das decisões entregues |
| Finalizador | Marca a aprovação |

## Passos

1. **Modo de entrada.** Leia `references/design/modos-entrada.md` quando a origem do desenho estiver em jogo.

   | Modo | Quando | Registro no vivo |
   |---|---|---|
   | Com referência | Existe DS, DESIGN.md ou Figma como leitura | O reusado e o adaptado, com motivo, sem copiar a fonte para o repo |
   | Greenfield | Sem referência aproveitável | Kit mínimo primeiro, depois cada tela da spec sobre o kit |

   Sem referência, não improvise DS externo. Com DS existente, primitivo novo na página é defeito.
2. **Uso.** Leia `references/design/kit-e-tokens.md` quando faltar kit, superfície compartilhada, token, ícone, responsivo, estado ou prova, e `references/design/motion.md` quando houver motion ou alvo mobile.

   | Uso | Entrada | Saída no vivo |
   |---|---|---|
   | Criar | Spec aprovada com F e telas | Inventário de telas e disposição técnica por tela sobre o kit |
   | Corrigir | R da review com path e evidência | Ajuste da tela citada, com motivo, sem reescrever o arquivo |
   | Analisar | UI existente mais spec | Parecer por tela contra o contrato, com lacunas e próximos passos |
3. **Dúvidas no chat.** Só o que trava o desenho:

   ```text
   Q: <decisão que trava o desenho>
   RECOMENDO: <opção>, <1 linha explicando o porquê e impacto>
   (ok / outra?)
   ```
4. **Gravação.** O redator cria o `design.md` a partir de `templates/design.md`, ou atualiza o vivo, e mantém `# Status: rascunho`. Cada tela traz hierarquia de cima para baixo, layout e grid, ordem de leitura, componente por zona, tokens, iconografia, regra responsiva ou N/A com motivo, overflow e truncamento, e estados. Superfícies compartilhadas e Prova visual esperada seguem `references/design/kit-e-tokens.md`; a prova não se repete no bloco da tela. Ações ambíguas mantêm texto, com regra de ícone explícita por tela.

## Saída

```text
Design gravado: <alvo>/design.md

- Modo: <com referência | greenfield>
- Uso: <criar | corrigir | analisar>
- Telas: <nomes das telas cobertas>

Responda "aprovado" para confirmar, "pode ir pro plan" para avançar, ou indique os ajustes.
```

| Resposta | Ação |
|---|---|
| Aprovado | Finalizador marca `# Status: aprovado`; o líder para |
| "Pode ir pro plan" | Mesma aprovação; o líder inicia o plan |
| Pedido de alteração | Redator aplica o patch; o líder resume em até 5 bullets e pede nova conferência |
| "Parece bom" sem pedir plan | Perguntar: "Aprovado no arquivo ou deseja algum ajuste?" |
| Spec ou intenção quebrou | Voltar à spec |

## Fechar e próxima etapa

Rascunho sem aprovação e sem pedido do plan não autoriza avançar. Sem commit nesta etapa. Próxima etapa: `plan`.
