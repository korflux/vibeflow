---
name: vibe-implement
description: >
  Executa a fatia elegível da fase com prova, registra a execução e marca [x] diretamente no plan.md
  (e spec/review). Use when the user runs /vibe-implement, pede implementar, código, build, faz a T*,
  pode seguir, ou a rota é low/medium/high/xhigh/max com código de comportamento, mesmo que não diga vibe-implement.
---

# vibe-implement

Não invente `n` se há plan. Sem prova e sem teste verde, sem `[x]` no `plan.md`. Sem `todo.md` nem `tasks.md`.
Sem `.vibeflow/`: `/vibe-init`. Open Questions no markdown = defeito. Não commita.
Proibido pular tasks ou desistir de erros. Diagnostique a causa raiz de qualquer falha no código e re-teste.
Comentários semânticos obrigatórios em todas as funções criadas ou alteradas.
As provas de execução e arquivos modificados são registrados diretamente sob cada task no `plan.md` vivo.
No MVP, não execute código sem analyze `aprovado` e `limpo`; a fila vem somente de `.vibeflow/mvp/plan.md`.

## 0. Entender e usar o script

1. Resolva o diretório desta skill e leia o motor que vai executar (`scripts/implement.ps1` no Windows ou `scripts/implement.py` no Unix). Ele realiza inventário determinístico e projeta a fila de dependências.
2. No cwd do repo:
   - Windows: `pwsh "<skill>/scripts/implement.ps1"`
   - Unix: `bash "<skill>/scripts/implement.sh"` (Python 3, senão pwsh 7)
   - Alvo MVP: acrescente `-Mvp` ou `--mvp`.
3. Leia `.vibeflow/implement-report.json`. A escolha da T* sai de `fila.elegiveis` no JSON. Leia `.vibeflow/REGRAS.md`. Paths só os citados. Não varrer a árvore.

`INIT_AUSENTE` exige init. `IMPLEMENT_SEM_ALVO`, `IMPLEMENT_SEM_PLAN`, `IMPLEMENT_ANALYZE_AUSENTE`, `IMPLEMENT_ANALYZE_RASCUNHO`, `IMPLEMENT_ANALYZE_BLOQUEADO`, `MVP_INESPERADO`, `MODO_INVALIDO`, `FASE_AUSENTE` e `PHASES_INESPERADO` não são contornados.

## 1. Abrir (5 linhas)

ROUTE · modo A/B · alvo · fila · plan · analyze

```text
ROUTE: high · modo: A · alvo: phase-1-lock-bloco · fila: T2|T4 elegíveis · plan: sim
```

`modo_sugerido=criar` = não há fase com `plan.md`. Não invente pasta. `high+` para e manda `/vibe-plan`. `fila` nulo = avulsa. `parse=ausente` = plan sem T*.

## 2. Gate

Declare `ROUTE: low|medium|high|xhigh|max` e modo A ou B. Default = **A**.

| Sinal | Ação |
|---|---|
| Typo / rename / uma linha sem runtime | **Não** usar |
| `high+` sem `plan.md` | **Para.** `/vibe-plan` |
| `max` sem `analyze.md` | **Para.** `/vibe-analyze` |
| Analyze ausente, rascunho ou veredito `bloqueado` no MVP | **Para.** Não flipa nem executa. Volta ao analyze |
| Plan/analyze `# Status: rascunho` e o humano pediu **esta** skill | Flip para `aprovado` (1 linha) e siga, se o veredito não for `bloqueado` |
| `low`/`medium` claro sem plan | Avulso: prova mínima no código/teste |
| `review.md` com R* Critical/Required em `[ ]` | Fila = R* primeiro. Q só se houver mais de um |
| `fila` com 2+ elegíveis e o humano não nomeou T* | **Para.** Q. Recomenda a de menor `n`. Sem código |
| `fila` com 1 elegível | Executa essa. Sem Q de escolha |
| `fila` com 0 elegíveis e 0 abertas | Handoff `vibe-review`. Não dispara |
| `fila` com 0 elegíveis e `bloqueadas` | Mostra as deps. Sem Q “qual T*” |
| Humano nomeou T* elegível | Executa essa. Sem Q |
| Humano nomeou T* bloqueada | Mostra deps. Sem código |
| Verificação da T* só manual, sem comando | **Para.** Q (automatizar / humano valida / volta plan) |
| Intenção/sucesso/fora frouxos | Devolve interview/spec |
| Bloqueio externo intransponível | **Para.** Q + RECOMENDO. Não pule em silêncio |

```text
Q: <o que trava>
RECOMENDO: <opção>, <1 linha explicando motivo e impacto>
(ok / outra?)
```

Modo B só se o humano pediu: `auto`, “faz o todo”, “não para”, “run completa”.
“Pode seguir” no modo A = próxima fase até o checkpoint (ou próxima T* se não houver agrupamento).

## 3. Ciclo da fatia

Execute cada task seguindo rigorosamente as 6 etapas:

1. **Reconhecer (O que já existe?):**
   Inspecione o repositório antes de escrever código novo. Reutilize helpers, utilitários, componentes visuais, types e módulos existentes da standard library ou do projeto. Não reescreva o que já existe.
2. **Codar:**
   Implemente a solução de forma direta, enxuta e estritamente focada nos requisitos da task (`T*`). Deixe comentários semânticos em todas as funções.
3. **Testar (Comando real do repo ou MCP Server chrome-devtools):**
   - Execute o comando real de teste do repositório associado à task.
   - Na primeira task funcional (T1), valide obrigatoriamente o *Smoke Test / Walking Skeleton* no ponto de entrada real da aplicação.
   - Se a task tocar interface visual web, execute a validação através das ferramentas do **MCP Server `chrome-devtools`** (`navigate_page`, `take_snapshot`, `click`, `take_screenshot` com leitura factual da imagem capturada), conforme `references/chrome-devtools.md`.
   - **Diagnóstico e Correção sem Desistência:** Se o teste falhar, NUNCA pule nem desista da task. Pare, analise a causa raiz no log de erro, aplique a correção no código e execute o teste novamente até ficar verde. Apenas impedimentos externos intransponíveis geram parada com `Q + RECOMENDO`.
4. **Simplificar (Refactor):**
   Com o teste verde, revise o código recém-escrito. Remova duplicações, enxugue verbosidade e garanta que o código seja o mínimo necessário sem cortar o que importa.
5. **Re-testar (Garantia de Regressão Zero):**
   Rerode a suíte de testes da fatia após a simplificação para comprovar que nenhuma limpeza quebrou a funcionalidade.
6. **Entregar e Atualizar plan.md:**
   Aplique o patch diretamente no `plan.md` vivo (e `spec.md`/`review.md` conforme §4).

Critérios adicionais:
- DoD: `references/definition-of-done.md` no que couber.
- Banco de dados: Se a fatia tocar banco de dados ou dinheiro, siga `references/database-and-migrations.md` (DECIMAL/NUMERIC para valores monetários, queries parametrizadas obrigatórias, sem N+1, índices em FKs, transações ACID curtas).
- Ao fechar o checkpoint do grupo: rerode os comandos de todas as tasks do grupo.
- Sem teste verde executável, sem marcação de conclusão no disco.

## 4. Marcar e Registrar no plan.md

Após a aprovação do teste da task, a IA aplica o patch diretamente no `plan.md` vivo sob a seção da task `### T{n}:`:

```markdown
### T1: Ponto de entrada e Smoke Test
- [x] T1 concluída
- **Spec:** A1
- **Deps:** nenhuma
- **Verificação:** `npm test -- --grep "smoke"`
- **Prova:** `npm test` -> 1 passing (115ms)
- **Arquivos:** `src/index.ts`, `tests/smoke.test.ts`
- **Decisões:** AUTH-01 (implementada)
```

Outros arquivos marcados:
| Arquivo | O que marcar |
|---|---|
| `spec.md` | `A*` / `C*` **só** os que a fatia provou |
| `review.md` | `R*` Critical/Required que o fix provou |
| `interview.md` | **Não** |

No MVP, certifique-se de registrar quais IDs críticos foram implementados. Não publique essas decisões em `REGRAS.md`; isso pertence ao pós-review aprovado.

## 5. Resposta no Chat

Responda no chat apenas:

```text
Implementação registrada: <alvo>/plan.md

- Fatia: <T* | R* | avulsa>
- Marcado: <T* / A* / C*>
- Prova: <comando> -> <resultado>
- Arquivos: <paths alterados>
- Handoff: vibe-review | próxima T* | Q

Fatia concluída e registrada em <alvo>/plan.md.
```

## 6. Modos

**A (default):** a T* escolhida (ou a única elegível) e, no mesmo checkpoint, só outras já elegíveis daquele grupo. Para. Se o usuário disser apenas "aprovado" ou "ok", permanece parado aguardando a próxima instrução. Se o usuário disser "pode seguir", "segue" ou "pode ir para a próxima fase", avança imediatamente para a próxima task elegível do plano ou para `vibe-review` se a fila estiver concluída.

**B:** percorre `fila.elegiveis` recalculando depois de cada item, sem Q a cada T*. Para em checkpoint vermelho ou bloqueio. Atualiza o `plan.md` a cada item.

Fila zerada (T* da run, ou R* bloqueantes) → handoff `vibe-review`. Se o usuário autorizar avançar para a review, inicia `vibe-review` diretamente.

## 7. Fechar

Não commita no git. Avise o que entra no git (código + vivos do alvo: `plan.md`, `spec.md`). Fora: `implement-report.json`.
Handoff no chat e no arquivo. Não invente work extra.
