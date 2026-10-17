# Etapa plan

Um único arquivo. Zero código nesta etapa. Pergunta aberta no arquivo é defeito. No MVP, preserve a ação e os IDs das decisões críticas nas T* que as implementam.

## Entrada

- Gate (`SKILL.md`, seção 3): spec aprovada; com UI nova, design aprovado. `analyze.md` já existente no alvo bloqueia novo plan; voltar ao plan segue `references/disco.md` (Escrever artefato).
- Artefato anterior em rascunho: aplique a aprovação implícita do `SKILL.md`, seção 3; fora dela, peça leitura e aprovação. Com UI nova e sem `design.md`, volte ao design.
- Sem UI nova, o plan registra `Design: N/A` com motivo, sem bloqueio.
- Intenção, sucesso ou limites frouxos voltam à interview ou à spec.
- Leia `spec.md`, `interview.md`, `design.md`, `AGENTS.md`, entradas, testes e comandos de verificação.

Declare em cerca de cinco linhas: rota, alvo, status da spec, status do design e estado do artefato vivo.

```text
rota: max · alvo: .vibeflow/phases/phase-1-lock-bloco/ · spec: aprovado · design: aprovado · plan: ausente
```

## Quem faz

| Quem | Faz |
|---|---|
| Líder | Define resultados, responsáveis, dependências, ondas e provas, resolve dúvidas de ordem técnica com o humano e conduz a aprovação |
| Explorador | Levanta entradas, testes, comandos e requisitos das provas quando a leitura for ampla |
| Redator | Cria ou atualiza `plan.md` a partir das decisões entregues |
| Finalizador | Marca a aprovação |

## Passos

### 1. Fatiar por resultado

Agrupe o trabalho em fatias verticais verificáveis, com um resultado coeso por T*. Uma T* pode tocar vários arquivos e durar mais de uma sessão quando continua entregando o mesmo resultado. Crie outra T* somente para um resultado entregável separado, uma dependência real de execução, um risco que exija isolamento ou uma fatia que não possa ser verificada como unidade. Quantidade de arquivos, duração estimada e a conjunção "e" no título não justificam quebra.

1. **Estrutura de cada T\*:** título com verbo e resultado, `Spec: A*/C*`, aceite observável, `Deps`, `Arquivos:` e `Prova afetada:`; `Risco` e `Decisões: <ID> (<ação>)` somente quando orientarem execução ou prova. IDs `T1`, `T2`, `T3`... em ordem, sem prefixos como `T001`, `[P]` ou `[US1]`.
2. **`Deps`:** apenas predecessores reais de execução; fatias independentes usam `Deps: nenhuma`. A linha de dependências define a fila, sem repetir a ordem em outra seção.
3. **`Arquivos:`** (única casa desta regra; implement e analyze a usam):
   - Uma única linha física `- **Arquivos:** ` com os paths que a T* pode escrever, testes incluídos, cada um entre crases (`` `src/a.py`, `tests/` ``). Só a primeira linha `Arquivos:` da T* conta, e só o texto entre crases.
   - Paths relativos ao repo. Diretório ou curinga (`*`, `?`, `[`) vale como prefixo do diretório anterior ao curinga. `.`, `./`, path vazio após normalizar, curinga na raiz e `..` que escapa da raiz valem como a raiz inteira.
   - Dois paths se sobrepõem quando são iguais ou um é prefixo de diretório do outro (`a` e `a/b`, nunca `a` e `ab`), comparando sem distinção de maiúsculas em A-Z.
   - Path incomparável torna a T* inteira sem arquivos comparáveis, e ela roda sozinha: caractere fora do ASCII, path absoluto, `:`, `<`, `>`, `"` ou `|`, ou segmento terminado em ponto ou espaço (exceto `.` e `..`). Ao encontrar um, recomende renomear o path ou isolar a T*.
   - Declare o recorte mais estreito que a T* escreve: prefixo largo serializa T* que poderiam rodar em paralelo. Sem `Arquivos:`, a T* roda sozinha.
4. **Arquivo compartilhado:** arquivo que mais de uma T* sem `Deps` entre si precisaria escrever (versão, README, índices) vai para uma T* final com `Deps` nas que o alimentam. Com `design.md`, aplique a precedência de `Superfícies compartilhadas` de `references/design/kit-e-tokens.md`: o kit ou componente comum entra na primeira T* de tela consumidora, e as demais o citam em `Deps`.
5. **Prosa e código:** T* cujo resultado é texto declara no `O quê:` `Resultado principal: prosa (redator)`; T* mista declara o resultado principal e mantém paths de prosa e de código distinguíveis. T* de prosa que muda `AGENTS.md` o declara em `Arquivos:`, nunca para a seção `## Decisões vigentes`.
6. **Ponto de entrada:** resultado que cria ou altera ponto de entrada executável inclui o smoke test desse ponto na mesma T*. Não crie T* só para baseline ou smoke genérico.
7. **UI greenfield:** componentes e tokens entram nas fatias de resultado, sem T* de preparo visual sem entrega verificável.
8. **Banco e migrations:** migrations e schemas ficam nas fatias verticais, com comandos executáveis de migration e seed mínimo; migrations não destrutivas (expand/contract).
9. **Review final:** não crie T* para executar a review; a fila termina nas entregas implementáveis.

### 2. Níveis de prova

- `Prova afetada:` em cada T*: comandos executáveis do repo que provam somente o recorte, derivados de `Como provar` da spec: nível `jornada` gera o E2E do cenário; nível `local`, os testes do módulo tocado e dos consumidores diretos. Some a evidência visual quando houver `Visual: necessária` e o smoke de entrada criada ou alterada. Em T* só de prosa, use a suíte do consumidor contratual ou uma checagem mecânica do que o texto alimenta; nunca teste de presença de palavras. Comando compartilhado é definido uma vez na prontidão e referenciado.
- `Regressão completa`: uma única seção `### Regressão completa` dentro de Prontidão das provas, com a suíte inteira e o E2E completo do repo, incluindo segurança, paridade e CI obrigatório. Somente a review final a executa.
- Não planeje matriz por T* nem teste novo por critério; complemente só lacunas de comportamento, erro ou risco. Verificação só manual não basta.
- **Visual por T\* que altera UI:** `Visual: necessária` quando o aceite depende de aparência, layout, responsividade, estado ou interação renderizados; `Visual: dispensada` com motivo quando testes provam o aceite sem saída renderizada a julgar. Tocar arquivo de UI, sozinho, não aciona navegador. Com `design.md`, cada linha de `Prova visual esperada` alimenta o `Visual:` e a `Prova afetada:` da T* que toca a tela; a ferramenta segue `references/chrome-devtools.md`.

### 3. Prontidão das provas

Antes de fechar a fila, confira somente o que as provas exigem: runtimes e package managers, comandos (inclusive `gitleaks` quando o repo ou o CI exigirem), serviços, privilégios e capacidades do SO (como symlink no Windows, portas e rede), e ferramentas da prova visual. Perfis de subagente não entram aqui: o líder os confere na run (`SKILL.md`, seção 5). Uma linha por requisito: `- <requisito>: <local | CI | host> · <destino>`.

| Situação do requisito | Destino |
|---|---|
| Disponível onde a prova roda, inclusive só no CI quando a prova roda no CI | `ok` |
| Ausente e instalável no próprio projeto, sem credencial, conta, pagamento nem elevação | `ação em Tn`, na primeira T* que depende dele |
| MCP ou integração persistente no host, privilégio do SO, credencial, conta ou pagamento | `pergunta ao humano`, com recomendação |
| Sem equivalente permitido | `bloqueio`, nunca `ok` |

Requisito sem destino mantém o plan em rascunho, sem pedido de aprovação. No MVP, toda decisão crítica da spec tem ação explícita e T* que cita seu ID.

### 4. Colaboração

Registre em Colaboração as ondas previstas (T* sem `Deps` pendentes e com `Arquivos:` disjuntos), o benefício e o ownership de recurso compartilhado fora de `Arquivos:`, somente quando houver benefício concreto.

### 5. Gravação

O redator cria o `plan.md` a partir de `templates/plan.md`, ou atualiza o vivo, mantém `# Status: rascunho` e omite seções não aplicáveis. Cada T* nasce com `- **Estado:** pendente`. O plan guarda definição de trabalho e, durante a execução, só as linhas `Estado:` e `Resumo:` que o finalizador escreve; nunca hashes, logs ou histórico de comandos.

## Saída

```text
Plan gravado: <alvo>/plan.md

- Overview: <1 linha>
- Resultados e dependências: <resumo curto da fila>
- Prontidão das provas: <requisitos com destino diferente de ok e perguntas abertas>
- Paralelizáveis: <ondas previstas, T* que rodam sozinhas e o motivo; “nenhum grupo seguro” quando não houver>

Responda "aprovado" para confirmar, "pode ir pro analyze" na rota max e no MVP, "pode ir pro implement" nas demais, ou indique os ajustes.
```

| Resposta | Ação |
|---|---|
| Aprovado | Finalizador marca `# Status: aprovado`; o líder para |
| Pede a próxima etapa | Mesma aprovação; o líder inicia `references/analyze.md` ou `references/implement.md` |
| Pedido de alteração | Redator aplica o patch; o líder resume em até 5 bullets e pede nova conferência |
| "Parece bom" sem pedir a próxima etapa | Perguntar: "Aprovado no arquivo ou deseja algum ajuste?" |
| Spec ou intenção quebrou | Voltar à spec ou à interview |

## Fechar e próxima etapa

Rascunho sem aprovação e sem pedido da próxima etapa não autoriza código. Sem commit nesta etapa. Próxima etapa: `analyze` na rota max e no MVP; `implement` nas demais.
