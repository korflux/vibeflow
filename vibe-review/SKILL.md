---
name: vibe-review
description: >
  Julga o patch, os testes e a cobertura pós-código e grava em `.vibeflow/phases/phase-N-slug/review.md` ou `.vibeflow/mvp/review.md`.
  Use when the user runs /vibe-review, pede review, revisa isso, LGTM, pode
  mergear, ou há handoff de vibe-implement / rota medium+, mesmo que não
  diga vibe-review.
---

# vibe-review

Não invente `n` se há plan. Não edite source, teste nem lockfile. Sem `review.md` não há veredito.
Um arquivo por alvo. Sem `.vibeflow/`: `/vibe-init`. Open Questions no arquivo = defeito. Não commita.
Decisões vigentes em `REGRAS.md` só são sincronizadas após Approve sem bloqueios e confirmação humana explícita.

## 0. Entender e usar o script

1. Resolva o diretório desta skill e leia o motor que vai executar. Entenda alvo, cadeia exigida, recusas e promoção. Confirme que ele não escreve `REGRAS.md`; corrija e prove qualquer defeito antes de seguir.
2. No cwd do repo:
   - Windows: `pwsh "<skill>/scripts/review.ps1"`
   - Unix: `bash "<skill>/scripts/review.sh"` (Python 3, senão pwsh 7)
   - Alvo MVP: acrescente `-Mvp` ou `--mvp`.
3. Leia `.vibeflow/review-report.json`. Se `alvo`, leia o que `files` listar. Leia `plan.md` (com as provas e arquivos alterados anotados sob as tasks), `spec.md`, `analyze.md` se houver e `REGRAS.md`. Diff: o que o humano apontou, ou o working tree da sessão. Não varrer a árvore.

`INIT_AUSENTE` exige init. `REVIEW_SEM_ALVO`, `REVIEW_CADEIA_INCOMPLETA`, `MVP_INESPERADO`, `MODO_INVALIDO`, `FASE_AUSENTE`, `WIP_AUSENTE` e `SLUG_INVALIDO` não são contornados.

Apply:
- first-pass reuse/atualizar: `pwsh "<skill>/scripts/review.ps1" -Apply` (`--dir` se o alvo errar)
- avulsa sem cadeia: `… -Apply -Slug "<frase curta>"`
- MVP: `… -Apply -Mvp`, sem slug ou dir
- Unix: `review.sh --apply` / `--apply --slug "…"`

## 1. Abrir (5 linhas)

rota · etapa · alvo · plan · spec · analyze · diff

```text
etapa 1 first-pass · alvo: phase-2-vibe-review · plan: sim · spec: sim · analyze: sim · diff: working tree
```

`modo_sugerido=criar` e sem `--slug` = não há pasta. Não grude review nova no N de outro pedido.
Já existe `review.md` = próxima etapa no **mesmo** arquivo.

## 2. Gate

| Sinal | Ação |
|---|---|
| Sem alvo e sem diff | **Para.** Peça path, branch, PR ou `--dir` |
| T* obrigatórias em `[ ]` e o humano pediu “pronto da feature” | Recuse Approve de feature. Pode revisar o diff e listar o que falta no plan |
| Intenção/sucesso/fora frouxos | Devolve interview/spec. Finding de código não reabre plan |
| Etapa 2+ | Mesmo `review.md`. Edite o vivo. Não apply de wip por cima se só vai acrescentar etapa |
| “Já corrige” | Grave o veredito **primeiro**. Handoff implement. Não patche aqui |
| MVP sem cadeia max completa | Recuse review e corrija a porta ausente |

```text
Q: <só se o veredito depende do humano>
RECOMENDO: <opção>, <1 linha>
(ok / outra?)
```

Barra de Approve: saúde do código + convenção do repo. Não bloquear gosto.

## 3. Protocolo Implacável de Auditoria (Julgar antes de gravar)

A review é um processo cético e investigativo. A IA não confia cegamente em checkboxes nem em logs passados. Inspecione o código real e execute as verificações nos 5 pilares obrigatórios:

1. **Rastreabilidade e Verificação Anti-Alucinação (Audit Trail):**
   - Cruze o pedido original (`interview.md`), os critérios de aceite (`spec.md` `A*`/`C*`) e as tasks (`plan.md` `T*`).
   - Inspecione o código-fonte de cada task `T*` concluída: valide se a funcionalidade foi realmente implementada de ponta a ponta ou se há stubs, `pass`, `TODO`, mocks falsos ou código incompleto. Task marcada sem código correspondente vira `R*` `gap: missing` (`Critical`).
2. **Re-execução e Integridade dos Testes:**
   - Re-execute os testes do repositório no ambiente real (incluindo o Smoke Test / Walking Skeleton da T1 no ponto de entrada).
   - Cace falsos positivos: testes sem asserções reais, testes que dão `assert True`, testes que apenas testam mocks sem exercitar a implementação real.
   - Verifique se os testes cobrem casos de borda, entradas vazias, nulas, limites numéricos e caminhos de erro.
   - Se os testes não passarem ou forem falsos positivos: registre `R*` `Required`.
3. **Auditoria Implacável de Segurança e Hardening:**
   - Inspecione cada entrada externa, formulário, parâmetro de URL e body de request (`references/security-and-hardening.md`):
     - Há risco de Injeção (SQL, XSS, Command/Shell Injection, SSRF)?
     - Há limite de caracteres e tamanho de payload para prevenir DoS e travamentos?
     - IDOR: o servidor valida se o usuário autenticado tem permissão sobre o recurso manipulado?
     - Há segredos, chaves ou tokens expostos no código, no bundle do frontend ou gravados em logs?
   - Toda brecha explorável vira `R*` `Critical`. Falta de limite/validação de borda vira `R*` `Required`.
4. **Inspeção Visual e Interface (MCP Server chrome-devtools):**
   - Se o diff tocar interface de usuário web, inspecione a tela via MCP Server `chrome-devtools` (`references/ui-visual-quality.md`):
     - Há elementos sobrepostos, botões cobertos ou textos truncados?
     - O contraste e a legibilidade estão adequados?
     - Há quebra de layout, overflow horizontal ou desalinhamento?
     - Estados de erro, loading e empty states estão implementados conforme a spec?
   - Interface sem prova visual ou com defeitos visuais vira `R*` `Required`.
5. **Simplificação e Qualidade de Código:**
   - Inspecione se o código é o mínimo necessário (YAGNI, sem estruturas especulativas, sem duplicação de lógica ou componentes).
   - Verifique se todas as funções criadas ou modificadas possuem comentários semânticos obrigatórios.
   - Decisões críticas: cruze interview, spec, plan e analyze. Decisão desrespeitada ou conflito aberto bloqueia Approve.
6. **Auditoria de Banco de Dados, Migrations e Precisão Numérica:**
   - Se o diff tocar persistência ou valores numéricos/monetários (`references/database-and-migrations.md`):
     - Valores monetários, taxas ou cálculos exatos usam `FLOAT`/`REAL` em vez de `DECIMAL`/`NUMERIC`? Vira `R*` `Critical`.
     - Há queries com risco de SQL Injection ou interpolação não parametrizada? Vira `R*` `Critical`.
     - Há migrations destrutivas (`DROP COLUMN`, `DROP TABLE`) sem plano de rollback e autorização humana? Vira `R*` `Critical`.
     - Há colunas de Foreign Key sem índice explícito ou queries N+1 em loops? Vira `R*` `Required`.
     - Há `SELECT *` desnecessário em código de produção ou paginação por `OFFSET` massivo? Vira `R*` `Required`.

Finding: evidência (`path`) + severidade + remédio nomeado + prova. Sem evidência concreta não entra. Achado novo = próximo `R*` livre. Não renumerar fechados.

| Prefixo | Bloqueia Approve? |
|---|---|
| Critical / Required | Sim |
| Nit / Optional / FYI | Não |

Remédio aponta `vibe-implement` + o que fazer. Esta skill **não** aplica código.

## 4. Escrever e salvar já

Molde: `templates/review.md`. Uma casa por fato. Omita seção que esta etapa não precisa.

| Campo | Abre | Fecha / some |
|---|---|---|
| Cobertura | Há `spec.md` | Sem spec: omitir |
| R* | Achado com path + evidência | `[x]` quando implement provou. Lista vazia some. Sem bloqueio: “nenhum bloqueio” |
| Visual | Diff desta etapa toca UI | Sem UI: omitir |
| Segurança | Diff toca superfície listada no §3 | Sem isso: omitir |
| DoD / Notas | Há o que aplicar ou anotar | Vazio / N/A: omitir |
| Etapa N | Toda run desta skill no pedido | Etapa antiga **não** apaga |

Status: `rascunho` na etapa 1; `request-changes` enquanto houver R* bloqueante em `[ ]`; `aprovado` quando o veredito vigente for Approve e o humano confirmou.

Não pergunte se pode salvar. Não cole o corpo no chat.

**Etapa 1 (não há `review.md`):** preencha o wip, apply (§0).

**Etapa 2+ (já há `review.md`):** patch no vivo. Acrescente `### Etapa N`. Atualize a checklist e o **veredito vigente**. Não apply de wip por cima, salvo wip que já contém o arquivo inteiro (histórico + etapa nova).

3. Chat, **só**:

```text
Review gravada: <created.path>/review.md

- Etapa: <N> · Veredito vigente: Approve | Request changes | Approve com defer
- Abriu: <R* ou nenhum>
- Fechou: <R* ou nenhum>
- Handoff: vibe-implement | volta vibe-spec | cadeia fechada

Arquivo disponível em <created.path>/review.md. Responda "aprovado" para sincronizar decisões e encerrar, ou indique os ajustes desejados.
```



## 5. Fechar

Não commita no git. Commitável: `review.md`. Fora: `review-report.json`, `review-wip.md`.
Request changes → handoff `vibe-implement` (arquivo + R* em `[ ]`). Se o usuário pedir para corrigir imediatamente, inicia `vibe-implement`.
Approve sem R* bloqueantes em `[ ]` ainda é proposta até o humano ler e confirmar.

Após aprovação humana explícita:

1. Marque `# Status: aprovado`, o veredito Approve e a aprovação humana no `review.md` vivo.
2. Se **Decisões para vigência** estiver vazia, feche a cadeia sem tocar regras.
3. Se houver linhas, aplique patch mínimo em `.vibeflow/REGRAS.md`. Crie ou atualize uma única seção `## Decisões vigentes` com tabela `ID | Decisão vigente | Fonte`. Atualize por ID, preserve linhas não citadas e use como fonte o review aprovado do alvo.
4. Não copie justificativa, histórico ou impacto para as regras. Eles permanecem nos artefatos.
5. Releia `REGRAS.md` e confirme que apenas os IDs aprovados mudaram. Review rascunho, Request changes ou Approve sem confirmação humana nunca autoriza sync.
