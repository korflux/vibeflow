# vibe-review, arquitetura

`/vibe-review` julga o patch, a cobertura e as provas pós-código em um único `review.md`. Para cada T*, consulta status, dependências/bloqueios, paths e provas no `plan.md`; não exige um novo `implement.md`.

```text
.vibeflow/phases/phase-<n>-<slug>/review.md
.vibeflow/mvp/review.md
```

## 1. Papéis e ownership

| Peça | Responsabilidade |
|---|---|
| `SKILL.md` | Gate, auditoria, cobertura A*/C*, eixos, visual, segurança, veredito, finalização Git da phase e modo subagente revisor. |
| `scripts/review.py`, `review.ps1`, `review.sh` | Inventário, cadeia, alvo, preparação do vivo e JSON operacional no stdout. |
| `templates/review.md` | Checklist e forma de etapas no mesmo arquivo. |
| `references/ui-visual-quality.md` | Checklist renderizada quando a aceitação exige evidência visual. |
| `references/security-and-hardening.md` | Catálogo sob demanda para superfícies sensíveis. |
| `stdout (JSON)` | Evidência operacional transitória, consumida na mesma execução. |
| `review.md` | Tipo e escopo de cada etapa, provas, histórico, veredito final e itens R*. |
| `plan.md` | Status, dependências/bloqueios, paths e provas registrados sob cada T*. |

O motor não julga o diff, não edita source, não escreve a prosa e não sincroniza `AGENTS.md`.

## 2. Alvo e cadeia

Sem `.vibeflow/`, `INIT_AUSENTE`. Com plan, o inventário seleciona a maior phase com plan sem review; uma review existente é atualizada no mesmo arquivo. O script não associa o diff à phase. Antes do apply, a IA compara o alvo sugerido com o diff e usa `--dir` para forçar a phase existente que contém o trabalho quando forem diferentes. Sem alvo, `--slug` pode abrir uma review avulsa em uma phase nova.

No MVP, `--mvp` exige `interview.md`, `spec.md`, `plan.md` e `analyze.md`, recusa slug/dir e usa somente `.vibeflow/mvp/`.

## 3. JSON operacional no stdout

O JSON transitório contém `vibeflow`, `phases`, `next_n`, `existing`, `plan_pendente`, `rascunho`, `alvo`, `mvp`, `modo_sugerido`, `created`, `modo`, `actions` e `avisos`. `files` lista os artefatos vivos.

`actions` registra apenas criação de phase ou de `review.md`. O JSON do stdout não contém conteúdo do julgamento.

## 4. Apply e etapas

1. Reexecuta o inventário e valida a cadeia aplicável.
2. Prepara `review.md` vazio somente no first-pass, quando ausente.
3. Preserva bytes do arquivo vivo existente.
4. A IA escreve diretamente a primeira etapa ou acrescenta a próxima etapa no mesmo arquivo.
5. O script não substitui o histórico, não toca source e não altera `AGENTS.md`.

Status: `rascunho` durante checkpoints e enquanto o veredito final aguarda confirmação, `request-changes` com R* bloqueante aberto, `aprovado` somente após review final, fila concluída, Approve e confirmação humana. A sincronização de decisões vigentes ocorre somente depois dessa confirmação, por patch mínimo da IA.

## 5. Tipos de review e seleção de provas

Checkpoint só é permitido quando `plan.md` declarar o marco e sua justificativa e todas as T* desse marco estiverem concluídas. A etapa julga apenas o marco, suas provas e o contrato ou risco compartilhado indicado. Registra T* ainda abertas, não declara a feature concluída, não marca Approve final e não autoriza sincronização de decisões, commit residual ou push.

Review final exige a fila do plan concluída e julga critérios de aceite, código integrado e riscos alterados. Para cada T*, confere status, `Deps`, bloqueios, `Arquivos` e `Prova`/`Verificação` no `plan.md`; compara os inputs cobertos com o estado integrado e reaproveita evidência verde quando esses paths continuam iguais e a prova ainda cobre a integração. Edição posterior em código/teste invalida somente a prova afetada; atualização de plan, spec ou review não invalida a prova. Executa apenas a verificação necessária que falta para integração ou risco. Não repete automaticamente cada comando da matriz de T*. Toda prova executada ou reaproveitada fica registrada no `review.md` com seu motivo.

## 6. Auditoria e prova visual

A review começa pela solicitação original e pelas alterações explicitamente autorizadas pelo humano, usando o contexto disponível e `interview.md` quando houver. Cruza essa origem com spec, plan, analyze e código real. O plan registra execução e não define sozinho a completude da entrega. Obrigação aplicável omitida pela spec ou pelo plan continua obrigatória até uma retirada humana explícita com fonte verificável.

O `review.md` contém uma matriz obrigatória: item da solicitação e fonte (incluindo A*/C* relacionados quando existirem), implementação concreta, evidência e situação. As situações permitidas são `atendido`, `parcial`, `ausente` e `retirado explicitamente pelo humano`. Retirada exige referência à decisão e ao item retirado; inferência do agente, ausência no plan e cronologia não autorizam retirada. Item obrigatório parcial ou ausente abre R* Required ou Critical conforme impacto e bloqueia Approve. Falta da origem ou de contexto essencial é limitação declarada da cobertura: solicita-se o contexto pelo coordenador e não se certifica completude. Checkpoint limita o julgamento ao marco e nunca certifica toda a solicitação.

A rastreabilidade usa o Git real, paths e provas contra o estado integrado. Aceita commits integrados de várias T*, commits por task e histórico legados; o prefixo `task(Tn)` não é condição exclusiva de evidência. No protocolo etapas-v1, confere origem preservada, snapshot da integração, hashes dos inputs e commit registrado na história, distinguindo checagem local de prova integrada. Um checkbox, frase verde ou assunto de commit isolado não comprova implementação. Lê no plan o status, as dependências/bloqueios, os paths e as provas de cada T*, sem exigir `implement.md`. Confere as evidências contra o estado atual e segue a seleção proporcional da seção anterior para executar apenas as verificações que faltam; também verifica falsos positivos, segurança, funções alteradas, dados e migrations quando aplicável.

Aplica os pilares de auditoria ao diff e às superfícies relevantes para o marco ou para a integração final. Usa `Visual` no plan para decidir se o aceite precisa de evidência renderizada; tocar arquivo de UI, HTML ou DOM, sozinho, não aciona navegador. Reaproveita prova de implementação válida e só executa a inspeção se ela estiver ausente/desatualizada ou não cobrir a integração. Quando necessária, seleciona navegador integrado, MCP Server `chrome-devtools` e Playwright somente se já existir ou for solicitado. Começa pela rota/tela, estado e viewport afetados; amplia conforme o impacto em layout, responsividade, interação, componente compartilhado ou risco. Faltando capacidade, aplica a regra de instalação da skill: instala a ferramenta necessária fora do projeto, sem alterar manifesto nem lockfile, e registra na etapa; credencial, conta, pagamento, elevação administrativa e registro persistente de integração (por exemplo, um MCP) vão ao humano. Sem capacidade visual depois disso, para uma prova necessária, abre `R* Required` e não aprova silenciosamente.

`icon-only` só é aceito para ação universalmente reconhecível, como lixeira para apagar, com nome acessível, foco visível, área de interação e tooltip quando aplicável. Ações ambíguas permanecem textuais.

## 7. Chat, testes e handoff

Recomende iniciar review em novo chat, separado da implementação, especialmente em re-review ou Request changes. Se o humano preferir continuar no mesmo chat, prossiga sem bloquear; o `review.md`, o diff e o plan são a ponte.

Suítes: `docs/vibe-review/tests/test-review.py` e `docs/vibe-review/tests/test-review.sh`. Elas cobrem seleção, override explícito por `--dir`, apply, phase/MVP, atualização e paridade.

Handoff: `vibe-implement` com R* bloqueante, retorno à spec quando a intenção quebrou, ou finalização Git da phase após aprovação humana.

### Modo subagente (revisor delegado)

No Modo A do `vibe-implement`, o coordenador delega a review final a um subagente de contexto limpo. O revisor executa o fluxo normal e grava a etapa no `review.md`, o único artefato vivo que escreve. Marca a proposta no Veredito vigente, mas o status só vira `aprovado` depois da confirmação humana. Não pergunta ao humano: devolve `estado: pergunta` com a recomendação, e o coordenador pergunta. Não executa a finalização Git, não faz commit nem push e não edita `AGENTS.md`; a finalização é do coordenador, depois da confirmação.

O relatório segue o formato fixo de `references/delegation.md` do implement e acrescenta `veredito`, `abertos`, `fechados`, `critical_encontrados` e `decisoes_vigencia`. A matriz de cobertura, R*, etapas e a tabela de decisões são o registro. O relatório também indica a cobertura da solicitação e limitações de origem, sem duplicar a matriz; perguntas ficam no relatório ao coordenador, nunca no arquivo. Na re-review após correção, o revisor confere os R* que o coordenador marcou `[x]` contra o diff e a prova.

## 8. Limites

- Um alvo possui um `review.md`; cada nova execução acrescenta `### Etapa N`.
- Checkpoint depende de marco explícito no plan; somente a review final pode concluir fase e abrir a finalização Git.
- Review não edita source, testes, lockfile ou artefatos anteriores. O revisor delegado também não toca Git, `AGENTS.md` nem a aprovação humana.
- O motor não interpreta Status, veredito ou diff.
- O arquivo vivo entra no Git; o JSON operacional é transitório no stdout. Review não corrige source. Após Approve final confirmado, fila concluída e sem R* bloqueante, a review executa a prova necessária da integração, cria o commit residual quando houver e executa `git push` do upstream atual sem force.
