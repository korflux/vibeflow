---
name: vibe-review
description: >
  Revisa código alterado, testes e cobertura após a implementação e grava em `.vibeflow/phases/phase-N-slug/review.md` ou `.vibeflow/mvp/review.md`. Use when the user runs /vibe-review, pede revisão de código ou patch, LGTM, merge de software, ou há handoff de vibe-implement, mesmo que não diga vibe-review. Não se aplica à revisão editorial de texto ou documentos.
---

# vibe-review

Se encontrar `.vibeflow/REGRAS.md`, `REGRAS.md` ou `CLAUDE.md` de uma instalação anterior, execute `vibe-init` para migrar as regras e então retome esta etapa. Fontes divergentes continuam para consolidação.

Não invente `n` se há plan. Não edite source, teste nem lockfile. Sem `review.md` não há veredito.
Um arquivo por alvo. Sem `.vibeflow/`: `/vibe-init`. Open Questions no arquivo = defeito. Correções ficam na `vibe-implement`; o Git só é finalizado após Approve e confirmação humana.
Decisões vigentes em `AGENTS.md` só são sincronizadas após Approve sem bloqueios e confirmação humana explícita.
Recomende iniciar a review em um chat novo, separado da implementação. Se o humano preferir o chat atual, prossiga sem bloquear. No Modo A do `vibe-implement`, o coordenador delega a review a um subagente de contexto limpo; nesse caso aplique o §6.

A investigação começa pela pergunta de auditoria e pelo T*/diff que precisa ser provado. Use `rg --files` para localizar os artefatos, paths alterados, testes e referências aplicáveis; use `rg -n` para localizar símbolos, contratos e evidências. Abra somente as entradas e dependências do fluxo real e expanda a leitura quando uma lacuna bloquear o veredito. O inventário é mapa de seleção, não autorização para ler a árvore inteira.

## 0. Entender e usar o script

1. Resolva o diretório desta skill e leia o motor que vai executar. Entenda alvo, cadeia exigida, recusas, preparação do destino e preservação do arquivo vivo. Confirme que ele não escreve `AGENTS.md`. Defeito no motor: fora do modo subagente, corrija e prove antes de seguir; como revisor delegado (§6), devolva `estado: bloqueado` ou abra R*, sem corrigir.
2. No cwd do repo:
   - Windows: `pwsh "<skill>/scripts/review.ps1"`
   - Unix: `bash "<skill>/scripts/review.sh"` (Python 3, senão pwsh 7)
   - Alvo MVP: acrescente `-Mvp` ou `--mvp`.
3. Leia o JSON operacional emitido no stdout pelo comando acima. Use `rg --files` e `rg -n` para localizar o alvo, o que `files` listar, `plan.md` com status, dependências, bloqueios, paths e provas de cada T*, `spec.md`, `analyze.md` se houver, `AGENTS.md` e o diff apontado pelo humano ou da sessão. Abra somente os paths que sustentam o veredito; não leia a árvore inteira.

`INIT_AUSENTE` exige init. `REVIEW_SEM_ALVO`, `REVIEW_CADEIA_INCOMPLETA`, `MVP_INESPERADO`, `MODO_INVALIDO`, `FASE_AUSENTE` e `SLUG_INVALIDO` não são contornados.

Apply:

- Slug explícito: nova phase avulsa, inclusive com plan pendente; confira o novo alvo no preview. Recuse slug vazio/inválido e slug junto de dir antes de escrita.
- first-pass reuse/atualizar: `pwsh "<skill>/scripts/review.ps1" -Apply` (`--dir` se o alvo errar)
- avulsa sem cadeia: `… -Apply -Slug "<frase curta>"`
- MVP: `… -Apply -Mvp`, sem slug ou dir
- Unix: `review.sh --apply` / `--apply --slug "…"`

## 1. Abrir (7 linhas)

rota · tipo · alvo · plan/fila · spec · analyze · diff · chat

```text
final · etapa 1 first-pass · alvo: phase-2-vibe-review · fila: concluída · spec: sim · analyze: sim · diff: working tree · chat: novo recomendado
```

`modo_sugerido=criar` e sem `--slug` = não há pasta. Não grude review nova no N de outro pedido.
Já existe `review.md` = próxima etapa no **mesmo** arquivo.

### Fonte da execução por protocolo

Em `coordenacao-v1` A, leia o motor da vibe-implement (§0 vale para ele) e execute-o em leitura, sem `--operation`, no alvo da review: `pwsh "<vibe-implement>/scripts/implement.ps1" -Dir <phase-N-slug> -Details` ou `bash "<vibe-implement>/scripts/implement.sh" --dir <phase-N-slug> --details` (`-Mvp`/`--mvp` no MVP). Em `execucao`, o resumo traz `tasks[].local_valida`, `integracao.prova_valida` e `integracao.commit_encontrado`; `detalhes` traz `tasks`, `integracao` (com `origem`), `commit` e `correcao` do execution.json. Checkboxes do plan são resumo, sem autoridade de conclusão. Execution ausente, ilegível ou inválido, `prova_valida` falsa ou `commit_encontrado` nulo bloqueia a review final. Resíduo previsto de execution.json pós-registro de commit é operacional, desde que nenhum input provado tenha mudado; cobre-o na finalização autorizada, sem novo ciclo para registrar hash.

Em B, etapas-v1 e legado, a fonte é o `plan.md`, com os checkpoints que ele declarar, sem mudança.

## 2. Gate

| Sinal | Ação |
|---|---|
| Sem alvo e sem diff | **Para.** Peça path, branch, PR ou `--dir` |
| Alvo do inventário difere da phase do diff/pedido | Não use o alvo automático. Identifique a phase existente do diff e rode com `--dir`; se ela não puder ser determinada, pare e peça o path |
| T* obrigatórias abertas na fonte do protocolo e o humano pediu “pronto da feature” | Recuse Approve de feature. Pode revisar o diff e listar o que falta no plan |
| Plan histórico (`etapas-v1`, B, legado) declara checkpoint e todas as T* do marco estão concluídas | Faça checkpoint somente do marco, das provas relevantes e do contrato ou risco declarado; registre as T* restantes |
| Plan histórico declara checkpoint, mas alguma T* do marco está aberta | **Para.** Informe a dependência aberta e faça handoff para `vibe-implement` |
| Há T* abertas sem checkpoint aplicável, inclusive em `coordenacao-v1` A, que não tem checkpoint | Não faça review final nem invente checkpoint; informe a fila e faça handoff para `vibe-implement` |
| Todas as T* estão comprovadamente concluídas na fonte do protocolo | Faça review final da integração e dos riscos alterados |
| Intenção/sucesso/fora frouxos | Devolve interview/spec. Finding de código não reabre plan |
| Etapa 2+ | Mesmo `review.md`. Edite o vivo diretamente e acrescente a etapa sem substituir o histórico |
| “Já corrige” | Grave o veredito **primeiro**. Handoff implement. Não patche aqui |
| MVP sem cadeia max completa | Recuse review e corrija a porta ausente |

```text
Q: <só se o veredito depende do humano>
RECOMENDO: <opção>, <1 linha>
(ok / outra?)
```

Barra de Approve: saúde do código + convenção do repo. Não bloquear gosto. No Express, julgue rastreabilidade e inspecione o resultado renderizado somente quando ele fizer parte do aceite; cubra a acessibilidade afetada pela mudança. Segurança e banco só abrem se o diff tocar essas superfícies.

## 3. Checkpoint, review final e provas

A review é um processo cético e investigativo. Não confie cegamente em checkboxes nem em logs passados. Escolha o tipo pela fila e pelo checkpoint explícito do `plan.md`; não transforme uma revisão parcial em veredito de fase.

| Tipo | Escopo | Veredito e efeitos |
|---|---|---|
| Checkpoint | Somente em `etapas-v1`, B e legado; `coordenacao-v1` A não tem checkpoint, porque a review final cobre a phase inteira. Somente as T* concluídas do marco declarado, suas provas, o contrato compartilhado ou risco que justifica a revisão. Registre as T* que continuam abertas. | A etapa pode concluir “Marco aprovado” ou “Request changes”. Nunca declare a feature concluída, marque Approve final, sincronize decisões, crie commit residual ou publique a phase. Com fila aberta e sem bloqueios, mantenha `# Status: rascunho` e faça handoff para `vibe-implement`. |
| Final | Fila do plan concluída; julgue critérios de aceite, código integrado e riscos que o diff alterou. | Approve só depois de comprovar a integração e fechar bloqueios. A finalização Git continua sujeita à confirmação humana explícita. |

### Conferir a solicitação original

1. Recupere a solicitação original e as alterações explicitamente autorizadas pelo humano no contexto e em `interview.md`, quando disponível. Confronte essa origem com spec, plan e implementação; ausência no plan não retira obrigação aplicável.
2. Preencha a matriz de Cobertura da solicitação no `review.md`: item e fonte, implementação, evidência e situação `atendido`, `parcial`, `ausente` ou `retirado explicitamente pelo humano`. Relacione A*/C* quando existirem. Para retirada, cite a decisão humana e o item exato; não deduza autorização.
3. Abra R* Required ou Critical conforme o impacto para obrigação parcial ou ausente e bloqueie Approve. Se faltar origem ou contexto essencial, declare a limitação de cobertura e devolva a necessidade de contexto ao coordenador; não certifique completude. No checkpoint, limite a matriz julgada ao marco e indique obrigações restantes.

### Auditar o executado (`coordenacao-v1` A)

Na review final e na re-review, com o estado lido no §1. Um path está dentro de um `Arquivos:` quando, depois da normalização léxica do motor da implement (`docs/vibe-implement/ARQUITETURA.md`, seção Onda paralela), é igual a um path declarado ou fica sob um diretório declarado; não recrie essa normalização.

1. **Inputs por T*:** cada path de `tasks.Tn.proof.inputs` está dentro do `Arquivos:` da Tn. Input fora do recorte que o diff da phase altera abre R* Required; input fora do recorte e inalterado na phase é consumidor lido pela prova e vai para Notas.
2. **Diff na união:** o diff da phase é `git diff --name-only <integracao.origem> HEAD`. Todo path alterado fora de `.vibeflow/` está na união dos `Arquivos:` das T* ou é um path que o remédio de um R* desta review manda alterar; path fora abre R* Required com o path e o remédio de declará-lo ou desfazê-lo.
3. **Consumidor compartilhado:** o `execution.json` não registra a onda real; para cada par de T* sem `Deps` entre si, direta ou transitiva, confira que cada consumidor de contrato, componente ou texto que elas compartilham continua coerente com as mudanças de todas; incoerência abre R* com o path do consumidor.
4. **Cobertura por prova:** na matriz de Cobertura, a evidência de cada A*/C* cita a `Prova afetada:` registrada da T* que o declara (`tasks.Tn.proof.comando`) ou a regressão completa; A* sem nenhuma das duas é `parcial`. `integracao.prova_valida` verdadeiro atesta que todas as T* têm prova local verde com snapshot válido, que o snapshot da integração é válido e que a integração contém os inputs locais.

### Selecionar e executar provas

1. Em coordenacao-v1 A, use execution.json como registro e plan como definição/resumo; nos protocolos históricos, use o `plan.md` como registro das execuções: confira o status da T*, `Deps` e bloqueios, `Arquivos` e `Prova`/`Verificação`. Compare os inputs da prova com o estado integrado e reaproveite prova verde somente quando esses inputs permanecem iguais e a prova ainda cobre a integração. Mudança em plan, spec ou review não invalida prova de código; edição posterior em código/teste invalida somente a prova afetada. `implement.md` histórico não é necessário para a review. Confira a história Git e os paths reais, aceitando commits integrados de várias T* e commits legados sem exigir exclusivamente o prefixo `task(Tn)`. Em etapas-v1, confira origem preservada, snapshot integrado, hashes dos inputs e commit real; checagem local não substitui integração.
2. Relacione diff, fluxo e consumidores, risco e aceite. Em coordenacao-v1 A, o julgamento de código fica limitado ao diff da phase e aos consumidores afetados; a matriz de Cobertura da solicitação continua obrigatória em todos os protocolos. Fora da regressão completa (protocolos históricos), execute somente a prova que falta para julgar o marco ou integração; reexecute por falha, inputs/dependências relevantes alterados, lacuna de integração ou risco concreto. Em re-review, confira correções e impacto nos consumidores; preserve julgamento e provas válidas das partes inalteradas. Duração não dispensa segurança, paridade ou prova renderizada necessárias.
3. A prova da review depende do protocolo (fonte da execução, §1):
   - **coordenacao-v1 A, review final e re-review:** a review é a única dona da regressão completa; implementador e verificador provaram somente o afetado.
     - Execute sempre a seção `Regressão completa` do plan, que declara a suíte inteira e o E2E do repo, uma vez, no estado integrado final. E2E que o plan exclui com motivo (por exemplo, não determinístico e fora do CI) não roda; registre a exclusão e o motivo. Registre na etapa, em "Provas executadas", comando, resultado e HEAD.
     - Árvore suja: com modificação não commitada em path de código e teste, não execute a regressão. Peça o isolamento ao coordenador (no modo subagente, `estado: bloqueado` com o pedido) ou ao humano.
     - Ela cobre as provas executáveis de segurança, paridade e CI obrigatório; a auditoria de código dos pilares abaixo continua no diff. O reaproveitamento do item 1 vale para as provas afetadas das T* e nunca substitui a regressão completa.
     - Paths de código e teste: todo path do repo fora de `.vibeflow/`, inclusive código, testes, docs, skills e config. Somente artefatos da cadeia em `.vibeflow/`, como plan, spec, review e execution.json, ficam fora. `AGENTS.md` também fica fora quando todos os hunks do seu diff caem dentro da seção `## Decisões vigentes` (sincronização da finalização); qualquer hunk fora dela conta.
     - Re-review: confira primeiro a correção registrada. `correcao.commit` não é nulo e é igual a `commit_encontrado`, que o motor só projeta quando o commit descende do commit da integração e tem os blobs da prova atual; os IDs do título `task(Rn,...)` são exatamente os R* marcados `[x]` desde a etapa anterior. Divergência bloqueia Approve e volta ao coordenador. Reaproveite a prova afetada da correção certificada pelo verificador; execute-a só se faltar ou se seus inputs mudaram.
     - Repita a regressão completa antes do Approve somente se algum path de código e teste mudou desde a última execução completa verde. Compare esses paths entre o HEAD registrado na etapa e a árvore de trabalho atual: commit ou modificação não commitada neles conta. HEAD diferente apenas por mudança fora dos paths de código e teste não exige repetição, mesmo commitada. A finalização Git usa a mesma comparação.
     - Falha: abra `R*` `Required` com o comando que falhou e o remédio. Approve exige regressão completa verde sobre o código final.
     - Plan sem seção `Regressão completa` (anterior ao formato que a introduziu): use a verificação agregada do repo (CI ou comandos documentados no `AGENTS.md`) como regressão completa e registre a origem na etapa. Sem nenhuma das duas fontes, devolva a necessidade ao coordenador com recomendação; não aprove sem regressão completa.
   - **etapas-v1, Modo B e legado:** mantêm a regra histórica. Não rode automaticamente a matriz de comandos de cada T* nem a suíte completa. Audite código, cobertura e validade das provas locais/integradas já certificadas; mudar de etapa ou revisor não exige executá-las novamente. Suíte completa só entra por risco, consumidores afetados, lacuna concreta ou CI obrigatório, com motivo registrado. Na review final, use uma verificação agregada existente somente se houver lacuna e ela comprovar a integração; rode o Smoke Test somente quando a entrada real tiver mudado, sua prova estiver ausente/desatualizada ou for necessária para cobrir o fluxo integrado.
4. Registre em cada etapa referências às provas reaproveitadas, comandos novos e motivo; não copie snapshots do lar operacional do protocolo nem reinvestigue inputs inalterados sem lacuna concreta. Se uma prova necessária falhar, abra `R*` `Required` com comando e remédio; não aprove silenciosamente.

Inspecione o código integrado e aplique estes pilares ao escopo da etapa:

1. **Rastreabilidade e Verificação Anti-Alucinação (Audit Trail):**
   - Cruze a matriz da solicitação original e suas decisões humanas com a Cobertura da origem da spec, os critérios `A*`/`C*` e o `plan.md`. No checkpoint, julgue só o marco declarado; no final, confirme que as tasks concluídas produziram a integração pedida. Item aplicável da interview sem destino na spec é lacuna de escopo, inclusive em rota sem analyze.
   - Inspecione os paths e o fluxo real que comprovam esse escopo. T* marcada sem código correspondente vira `R*` `gap: missing` (`Critical`).
2. **Provas e Integridade dos Testes:**
   - Cace falsos positivos: testes sem asserções reais, testes que dão `assert True`, testes que apenas testam mocks sem exercitar a implementação real.
   - Se a task consolidou testes da capacidade alterada, confira se os cenários e afirmações removidos continuam cobertos por provas executáveis. Duplicação remanescente só vira achado quando causa custo material ou mascara uma lacuna; não peça limpeza ampla fora da entrega.
   - Verifique casos de borda e caminhos de erro relevantes às superfícies alteradas. Use a seleção de provas acima; fora da regressão completa, não repita suites de T* sem lacuna ou risco que o justifique.
   - Se uma prova necessária falhar ou for falso positivo: registre `R*` `Required`.
3. **Auditoria Implacável de Segurança e Hardening:**
   - Nas superfícies tocadas pelo diff, inspecione entradas externas, formulários, parâmetros de URL e bodies de request (`references/security-and-hardening.md`):
     - Há risco de Injeção (SQL, XSS, Command/Shell Injection, SSRF)?
     - Há limite de caracteres e tamanho de payload para prevenir DoS e travamentos?
     - IDOR: o servidor valida se o usuário autenticado tem permissão sobre o recurso manipulado?
     - Há segredos, chaves ou tokens expostos no código, no bundle do frontend ou gravados em logs?
   - Toda brecha explorável vira `R*` `Critical`. Falta de limite/validação de borda vira `R*` `Required`.
4. **Inspeção Visual e Interface:**
   - Inspecione no navegador quando `Visual: necessária` estiver no plan ou quando o diff revelar uma saída renderizada relevante não prevista. Tocar arquivo de UI, HTML ou DOM não basta. Se `Visual: dispensada` estiver justificada por prova executável e o diff confirmar que não há resultado renderizado a julgar, não abra o navegador.
   - Reaproveite a evidência visual registrada pela implement quando seus inputs continuam válidos e ela cobre a integração. Só execute ou repita navegador se a prova estiver ausente/desatualizada, faltar cobertura da integração, ou o risco/diff exigir outro estado ou viewport. Quando necessário, selecione nesta ordem conforme `references/ui-visual-quality.md`: navegador integrado (`@Browser` ou equivalente), MCP Server `chrome-devtools`, ou Playwright somente se já existir no repositório ou for solicitado para fluxos repetíveis e assertions.
   - Comece pela rota/tela, estado e viewport afetados pelo diff; amplie quando layout, responsividade, interação, componente compartilhado ou risco exigirem. Registre rota, viewport, estado, ações e evidência observada. Aplique a checklist da referência ao recorte afetado, incluindo acessibilidade e erros relevantes de runtime.
   - Com `design.md`, diff que altera componente ou token listado em `Superfícies compartilhadas` reconfere todas as telas listadas ali para ele, inclusive fora do inventário da phase, pela `Prova visual esperada` de cada tela.
   - Para ações compactas, aceite `icon-only` somente quando a ação for universalmente reconhecível, como lixeira para apagar, com nome acessível, área de interação adequada, foco visível e tooltip quando aplicável. Ações ambíguas continuam com texto.
   - Se a prova renderizada for necessária e não houver capacidade ou evidência válida, aplique a regra de instalação: instale a ferramenta ausente necessária à prova pelo gerenciador do projeto ou por fonte oficial, quando o ambiente e as permissões permitirem, sem alterar manifesto nem lockfile do projeto e registrando a ferramenta na etapa. Instalação que exija credencial, criação de conta, pagamento, elevação administrativa ou configuração persistente de integração (por exemplo, registrar um MCP) é impedimento real e vai ao humano. Se a capacidade continuar ausente, abra `R*` `Required`; não aprove silenciosamente.
5. **Simplificação e Qualidade de Código:**
   - Inspecione simplificação, reutilização e remoção de redundância no recorte (YAGNI, sem estruturas especulativas, sem duplicação de lógica ou componentes). Aceite otimização de desempenho fundamentada, preservando comportamento, segurança, cobertura e escopo.
   - Verifique se todas as funções criadas ou modificadas possuem comentários semânticos obrigatórios.
   - Decisões críticas: cruze interview, spec, plan e analyze. Decisão desrespeitada ou conflito aberto bloqueia Approve.
6. **Auditoria de Banco de Dados, Migrations e Precisão Numérica:**
   - Se o diff tocar persistência ou valores numéricos/monetários (`references/database-and-migrations.md`):
     - Valores monetários, taxas ou cálculos exatos usam `FLOAT`/`REAL` em vez de `DECIMAL`/`NUMERIC`? Vira `R*` `Critical`.
     - Há queries com risco de SQL Injection ou interpolação não parametrizada? Vira `R*` `Critical`.
     - Há migrations destrutivas (`DROP COLUMN`, `DROP TABLE`) sem plano de rollback e autorização humana? Vira `R*` `Critical`.
     - Há colunas de Foreign Key sem índice explícito ou queries N+1 em loops? Vira `R*` `Required`.
     - Há `SELECT *` desnecessário em código de produção ou paginação por `OFFSET` massivo? Vira `R*` `Required`.

Finding: evidência (`path`) + severidade + remédio nomeado + prova. Sem evidência concreta não entra. Achado novo = próximo `R*` livre. Não renumerar fechados. Em `coordenacao-v1` A, todo R* novo cujo remédio altera paths de `Arquivos:` da phase traz `papel: redator` quando o remédio é só prosa desses paths (SKILL, referências, templates, docs, README) e `papel: corretor` nos demais casos; a implement roteia a correção por esse campo. Remédio em `plan.md`, `spec.md` ou `AGENTS.md` não leva `papel` e indica no remédio o finalizador; remédio em `review.md` é do revisor, sem `papel`. R* históricos não são migrados.

| Prefixo | Bloqueia Approve? |
|---|---|
| Critical / Required / Nit | Sim, enquanto R* estiver aberto |
| Optional / FYI legado com R* | Sim, enquanto R* estiver aberto |

Toda correção pertinente exige R*, remédio e prova, inclusive nit. Severidade indica impacto e prioridade; não permite dispensar a correção. Registre informação sem remédio em Notas, sem R*. Preferência pessoal sem fundamento não é achado. Preserve classificações e vereditos históricos; na retomada, qualquer R* aberto, inclusive Optional/FYI legado, bloqueia Approve mesmo com status aprovado ou defer marcado. Não ofereça Approve com defer em novas etapas. Obrigação parcial/ausente ou origem insuficiente também bloqueia aprovação.

Remédio aponta `vibe-implement` + o que fazer. Esta skill **não** aplica código.

## 4. Escrever e salvar já

Molde: `templates/review.md`. Uma casa por fato. Omita seção que esta etapa não precisa.

| Campo | Abre | Fecha / some |
|---|---|---|
| Tipo de review | Toda etapa | Registre checkpoint (somente protocolos históricos) ou final e, no checkpoint, a referência exata do marco no plan |
| Execução | Etapa em `coordenacao-v1` A | Registre o resultado da auditoria do executado (§3); omitir nos protocolos históricos |
| Cobertura | Há `spec.md` | Sem spec: omitir |
| R* | Achado com path + evidência; `papel` em `coordenacao-v1` A | `[x]` quando implement provou. Lista vazia some. Sem bloqueio: “nenhum bloqueio” |
| Provas | Toda etapa | Liste provas reaproveitadas, executadas e o motivo; N/A só quando não há prova aplicável |
| Visual | O aceite depende da UI renderizada ou a T* marcou `Visual: necessária` | Se não há resultado renderizado a julgar e a dispensa está provada, omitir |
| Segurança | Diff toca superfície listada no §3 | Sem isso: omitir |
| DoD / Notas | Há o que aplicar ou anotar | Vazio / N/A: omitir |
| Etapa N | Toda run desta skill no pedido | Etapa antiga **não** apaga |

Status: `rascunho` durante checkpoints e enquanto o veredito final aguarda confirmação; `request-changes` enquanto houver R* bloqueante em `[ ]`; `aprovado` somente após Approve final, fila concluída e confirmação humana.

Não pergunte se pode salvar. Não cole o corpo no chat.

**Etapa 1 (não há `review.md`):** execute o apply para preparar o `review.md` vivo e escreva nele diretamente (§0). Registre o tipo e o escopo antes de julgar.

**Etapa 2+ (já há `review.md`):** edite o vivo diretamente. Acrescente `### Etapa N` e atualize checklist e provas sem substituir o histórico. Só a review final atualiza o veredito vigente para Approve; checkpoint registra o resultado do marco na própria etapa.

### Resposta no chat

Responda, **só**:

```text
Review gravada: <created.path>/review.md

- Etapa: <N> · Tipo: checkpoint | final · Resultado: Marco aprovado | Request changes | Approve final
- Fila: <T* restantes | concluída>
- Abriu: <R* ou nenhum>
- Fechou: <R* ou nenhum>
- Handoff: vibe-implement | volta vibe-spec | finalização Git da phase
- Chat: review recomendada em conversa separada da implementação; para correções, novo chat também é recomendado. A continuidade é livre.

Arquivo disponível em <created.path>/review.md. Em checkpoint, a fase continua aberta; na review final, responda "aprovado" para sincronizar decisões e encerrar, ou indique os ajustes desejados.
```



## 5. Fechar

Commitável: o `review.md` vivo e, somente no fechamento final aprovado, os artefatos residuais autorizados da phase. Checkpoint não cria commit residual nem publica a phase. Request changes → handoff `vibe-implement` (arquivo + R* em `[ ]`), com recomendação de novo chat para a correção; no Modo A, o coordenador do `vibe-implement` delega a correção a um subagente. Se o usuário pedir para corrigir imediatamente, inicie `vibe-implement`; se preferir permanecer neste chat, prossiga sem bloquear. O `review.md` e o diff são a ponte.
Approve final sem R* bloqueantes em `[ ]` ainda é proposta até o humano ler e confirmar. No novo Modo A, o coordenador transmite a confirmação e o escopo ao finalizador genérico/default apto, que executa a finalização abaixo. Em etapas-v1/legado, coordenador conserva operação. Revisor delegado nunca finaliza nem recebe Git.

Após aprovação humana explícita da review final, com a fila concluída:

1. Marque `# Status: aprovado`, o veredito Approve e a aprovação humana no `review.md` vivo.
2. Se **Decisões para vigência** estiver vazia, feche a cadeia sem tocar regras.
3. Se houver linhas, aplique patch mínimo em `AGENTS.md`. Crie ou atualize uma única seção `## Decisões vigentes` com tabela `ID | Decisão vigente | Fonte`. Atualize por ID, preserve linhas não citadas e use como fonte o review aprovado do alvo.
4. Não copie justificativa, histórico ou impacto para as regras. Eles permanecem nos artefatos.
5. Releia `AGENTS.md` e confirme que apenas os IDs aprovados mudaram. Review rascunho, Request changes ou Approve sem confirmação humana nunca autoriza sync.

### Finalização Git da phase

Esta seção só se aplica à review final, depois da aprovação humana explícita, com todas as T* concluídas e sem R* de correção em `[ ]`. Checkpoint nunca abre finalização Git.

1. Confirme a prova final conforme §3: em coordenacao-v1 A, a regressão completa verde registrada cobre a integração enquanto nenhum path de código ou teste mudou desde ela, pela mesma comparação da re-review no §3; nos protocolos históricos, execute a prova final necessária para a integração, sem repetir automaticamente a matriz de cada T*. Execute `git diff --check` e gitleaks quando previsto pelo repositório.
2. Compare o estado atual com o snapshot da review. Se houver path fora da phase, das decisões aprovadas ou da correção registrada, pare e peça isolamento; não misture trabalho pré-existente.
3. Adicione somente os paths residuais autorizados, com `git add -- path/da/phase AGENTS.md` quando a sincronização foi aprovada. Nunca use `git add -A` ou `git add .`.
4. Valide `git diff --cached --check` e a lista de paths. Crie `chore(phase-N): finalize review` sem `Co-Authored-By` quando houver mudanças residuais. Não crie commit vazio; se não houver residual, o último commit integrado ou da task é o HEAD da phase.
5. Execute `git push` para o upstream do branch atual, sem `--force`. Ausência de upstream, falha de commit ou falha de push mantém o handoff bloqueado e precisa ser informada com a causa segura.
6. No novo A, relate hash final/HEAD, resultado do push e paths enviados sem reabrir arquivos só para guardar o próprio hash; nos protocolos históricos, conserve registro de fechamento no review e chat. O inventário é JSON transitório no stdout.

## 6. Modo subagente (revisor delegado)

Vale quando o coordenador do `vibe-implement` (Modo A) delega esta skill e o pedido diz que você é o `revisor`. O pedido traz o formato fixo do relatório; você acrescenta apenas os campos abaixo. Execute §0 a §4 como de costume, em review final com a fila concluída, e grave a etapa no `review.md`: ele é o único artefato vivo que o revisor escreve.

- **Veredito vigente:** marque a proposta (`Approve` ou `Request changes`) no `review.md`. O status continua `rascunho` ou `request-changes` conforme o §4; `aprovado` só vem depois da confirmação humana.
- **Humano:** não pergunte ao humano nem espere resposta. Quando o veredito depender dele, devolva `estado: pergunta` com a recomendação; o coordenador pergunta. Não deixe Open Questions no arquivo.
- **Re-review após correção:** acrescente nova etapa no mesmo arquivo e confira os R* marcados pelo responsável de registro do protocolo contra o diff e a prova antes de aceitá-los.
- **Proibido:** finalização Git do §5, commit, push, edição de `AGENTS.md`, aprovação humana marcada no arquivo, correção de código ou de motor (inclusive defeito achado no §0) e instalação fora da regra do §3.
- **Resposta:** o relatório substitui a resposta de chat do §4. Além dos campos fixos, devolva `veredito` (`Approve final` ou `Request changes`), `abertos` (todos os R* de correção em `[ ]`), `fechados` (R* fechados nesta etapa), `critical_encontrados` (R* Critical abertos nesta etapa) e `decisoes_vigencia` (IDs propostos na tabela, ou nenhuma).

Na review delegada, informe também a cobertura da solicitação e qualquer limitação de origem, referenciando a matriz gravada. Approve exige obrigações atendidas ou retiradas explicitamente pelo humano, origem suficiente e nenhum bloqueio aberto.
