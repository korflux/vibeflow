# Review: subagentes instalados e execução por etapas
# Alvo: phase-15-subagentes-e-execucao-por-etapas
# Status: rascunho

## Contexto

- Review final delegada, com contexto limpo, em 2026-10-10. Escopo vigente: `08e65069e93ec9debca84c2f42058ca883697a7a..5f74bb074fe27590e965de6dcd5c0cadd6241408`, T1 a T3 e correção R1. A Etapa 1 mantém seu snapshot original.
- Cadeia: spec e plan aprovados. Interview inexistente; origem registrada na Cobertura da origem e nas decisões da spec. Rota high, analyze não obrigatório e design N/A por ausência de UI.
- A entrega instala dez perfis locais, introduz `etapas-v1` no Modo A e exige cobertura da solicitação na review. Esta própria phase permanece no protocolo legado, conforme o Overview do plan.
- Commits conferidos: `8784507` (T1), `1bd03eb` (T2), `3a3a6bb` (T3). Residual anterior: `.erros-encontrados/2026-10-10-review-testes-ignoram-falha-de-limpeza.md`, informado pelo coordenador e fora do patch de implementação.

## Tipo de review

- Tipo: final; integração das T1, T2 e T3, todas registradas como concluídas. Nenhuma T* aberta.
- Provas reaproveitadas: execuções finais e avaliações comportamentais registradas no plan, confrontadas com os motores, testes, perfis, contratos e histórico Git. Os inputs dos motores de init/implement não mudaram depois das respectivas provas. A alteração posterior do gerador de fixtures recebeu preflight próprio.
- Provas executadas: entrypoints Python e PowerShell pelo alias real `skills/vibe-init`, para cobrir a lacuna de distribuição; ambos falharam. `git diff --check 08e6506..HEAD`: exit 0. Apply da review com `-Dir` explícito: exit 0, criou somente o artefato vivo previsto.

## Cobertura da solicitação

- Origem e limites: pedido desta run `/vibe-implement phase15`; o pedido anterior e a aprovação humana estão registrados na spec, inclusive a autorização de commit integrado no novo Modo A. A review julga essa origem registrada, sem presumir acesso à transcrição anterior. Ela é suficiente para o recorte; o plan não foi usado como limite exclusivo. Carregamento efetivo dos novos perfis em Claude e em uma sessão Codex recarregada não foi certificado, conforme a limitação explícita do plan.

| Item da solicitação e fonte | Implementação | Evidência | Situação |
|---|---|---|---|
| Instalar cinco papéis por host com modelos/esforços de referência; spec F1/A1, C1/C4 | Dez recursos em `vibe-init/templates/agents/`, motores `init.py` e `init.ps1` | Correção R1: 12 testes Python, 5 cenários PowerShell e launcher-alias verdes; alias público, pacote e ancestral cobertos, com dez perfis e idempotência; fechamento conferido na Etapa 2 | atendido |
| Preservar personalizações, idempotência e recusar caminhos inseguros; F1/A2 | Preflight da allowlist, comparação por hash, criação exclusiva e recusa de reparse points | T1: fixtures de conflito, repetição, fonte/destino inseguro, link quebrado e ancestral; código mantém personalização sem interpretar seu conteúdo | atendido |
| Distinguir disco, conflito e disponibilidade em sessão; F1/A3 | `agent_profiles`, `agent_session: nao_verificada` e instrução de recarga em `vibe-init/SKILL.md` | T1: relatório e formatos nativos conferidos; perfis disponíveis na sessão não foram tratados como prova de carregamento dos novos arquivos | atendido |
| Implementar antes da suíte completa, liberar dependentes com prova local e retomar sem conclusão prematura; F2/A4 | `execution_from_plan`/`Get-ExecutionFromPlan`, snapshots e campos explícitos no plan | T2: 40 testes e bordas adicionais; avaliação real liberou T2 após prova local de T1 mantendo ambas abertas; paridade dos motores | atendido |
| Complementar testes pelo aceite e validar com papel separado; F2/A5 | Piloto por etapas, perfis implementador/verificador e contrato de delegação | Avaliação T2 preservou teste existente, complementou jornada e executou integração por verificador independente | atendido |
| Corrigir falha real, preservar provas válidas e evitar matriz completa por task; F2/A6, C2 | Snapshot por inputs, etapas validar/corrigir_validacao e corretor pré-review | Avaliação T2: três subfalhas reais, correção somente no helper compartilhado, renovação dos snapshots afetados e 4 testes verdes; repetição UTF-8 foi justificada | atendido |
| Commit integrado verde, rastreabilidade, Modo B/legado e confirmação humana; decisão 6, F2/A7 | Busca do commit real posterior à origem; protocolo explícito; regras de commit e fechamento | T2: commit único `a3eb164...` na fixture, teste de interrupção/retomada e correção posterior; esta phase usa três commits legados autorizados; nenhum push delegado | atendido |
| Cobrir toda solicitação e bloquear omissão mesmo com testes verdes; F3/A8, C3 | Skill/template de review, perfis revisor e relatórios de delegação | T3: cenário A abriu Required por slugify ausente; cenário B aceitou retirada humana explícita sem falso bloqueio; três testes verdes em cada entrega | atendido |
| Manter distribuição, contratos e restrições reais; C4 | Versão 5.0.0, manifestos, referências e contratos atualizados | T3: distribuição 9, MVP 1 e reparse 12 testes verdes; lacuna do alias fechada por R1 com paridade e launcher-alias, conforme Etapa 2 | atendido |

## Checklist de correções

- Correções adicionais autorizadas por Marco em 2026-10-10: auditar os registros de .erros-encontrados e corrigir problemas ainda vigentes. A proposta anterior de Approve será reconferida após essas alterações, sem autorização de push.

### Required

- [x] R1: **Required** - `vibe-init/scripts/init.py:72` e `vibe-init/scripts/init.ps1:52`, com validação em `init.py:54` e `init.ps1:26` - A fonte dos perfis é calculada a partir do caminho lexical do script, e a validação recusa todos os ancestrais com link. Executar o pacote pelo alias legítimo `skills/vibe-init` faz ambos os motores abortarem com `TIPO_INESPERADO` antes de instalar qualquer perfil. Esse alias existe no repositório e é a descoberta documentada do plugin; a instalação normal por symlink também é suportada pelo README. Assim, a proteção de fontes passou a impedir um ponto de entrada público da distribuição. Remédio: `vibe-implement`, resolver a identidade física da raiz do pacote instalado antes de compor as fontes, distinguindo o alias legítimo do pacote de links internos inesperados; preservar a recusa de fontes internas e destinos inseguros, limites e personalizações. Acrescentar prova executável dos motores via alias e do launcher com pacote instalado dessa forma. Prova: os comandos da Etapa 1 devem instalar os dez perfis e repetir sem alteração; testes de links internos/ancestrais de destino devem continuar recusando a operação antes de mutações. Source: F1/A1, C1/C4, README e diff; gap: partial.

- [x] R2: **Required** - docs/vibe-review/tests/test-review.py:58 e :237 - tearDown ignora erros de remoção; remédio: propagar falhas e verificar limpeza; prova: suíte review e ausência das fixtures; source: registro 2026-10-10 e pedido humano atual.
- [x] R3: **Nit** - docs/tests/test-distribuicao.py:122 - seis comentários órfãos sugerem testes removidos; remédio: remover comentários e preservar testes reais; prova: suíte de distribuição; source: registro 2026-10-03 e pedido humano atual.

- [x] R4: **Required** - stdout dos motores Python/PowerShell - avisos e paths Unicode são emitidos em codificações legadas distintas no Windows; remédio: definir UTF-8 no transporte, adaptar consumidores de testes e provar bytes/texto integral em ambos motores, sem mascarar acentos; source: 2026-10-03-motores-stdout-codificacao-divergente.md.
- [ ] R5: **Required** - vibe-review/scripts/review.py e review.ps1 - slug explícito perde prioridade para phase com plan pendente; remédio: priorizar criação avulsa quando slug explicitamente informado, validar conflito com dir e preservar alvo/arquivos preexistentes; prova: paridade com plan pendente e slug, sem mutação de fase anterior; source: review-avulsa-ignora-slug-com-plan-pendente.md.
- [ ] R6: **Required** - vibe-review/SKILL.md e templates/review.md - Approve com defer não limita severidade nem identifica adiamento; remédio: permitir somente Nit/Optional/FYI com ID/fonte/motivo, nunca Critical/Required ou obrigação ausente; prova: inspeção de contrato e estados executáveis do motor, sem testes de palavras da documentação; source: 2026-10-03-review-approve-com-defer-sem-regra.md.
## Segurança

- Inputs do novo protocolo têm allowlist de campos, paths relativos sem traversal/ADS, checagem de reparse points e hashes Git. O comando registrado é texto de evidência e não é executado pelo motor; chamadas Git usam argumentos, sem montagem de shell.
- Instalação restringe nomes/extensões, valida antes das mutações, limita fontes a 1 MiB e preserva conflitos. A correção R1 preserva essas barreiras, conferidas na Etapa 2.
- Gitleaks renovado após R1: exit 0, sem vazamentos (1,70 MB), conforme registro da correção. Código/perfis permanecem iguais ao snapshot corrigido. Nenhum Critical encontrado. Banco, autenticação web, pagamentos e UI não são superfícies deste diff.

## Provas e limitações

- Reaproveitadas de T1: `python docs/vibe-init/tests/test-init.py` (11 OK), `pwsh -NoProfile -File docs/vibe-init/tests/test-init.ps1` (5 PASS), launcher Git Bash (exit 0). Não cobriam o alias instalado, motivo da prova adicional.
- Reaproveitadas de T2: implement (40 OK), bordas StageProtocolContracts (4 OK), origem/commit retry/types (2 OK), plan (16 OK), piloto prepare-only (7 PASS) e launcher (8 PASS). Inspeção confirmou asserts de efeitos reais em disco/Git, sem testes de presença de texto de documentação. Avaliação por agentes e hashes constam do plan; fixtures foram removidas após coleta, logo não foram reabertas nesta review.
- Reaproveitadas de T3: review (19 OK), distribuição (9 OK), MVP (1 OK), reparse (12 OK), Gitleaks e preflight LF das duas fixtures. As avaliações semânticas independentes são evidências separadas das suítes determinísticas.
- A ativação em hosts/modelos indisponíveis não é certificada. Não foi instalada configuração persistente nem executado `claude -p`.

## Veredito vigente

- [ ] **Approve**: proposta final da Etapa 2. R1 fechado na Etapa 2; os ajustes humanos adicionais R4, R5 e R6 estão abertos e impedem aprovação vigente. Matriz da solicitação atendida dentro das limitações explícitas. Aguarda confirmação humana; status permanece rascunho.

## Notas

- Auditoria adicional: correções dos registros ainda vigentes autorizadas pelo usuário. Limpeza silenciosa equivalente em outras suítes e classe de testes vazia da review foram registradas e incluídas em R2/R3. Registros comprovadamente resolvidos e limitações históricas não serão reimplementados. A pendência de commit isolado na phase 9 não admite reparo retroativo sem inventar evidência ou reescrever histórico, ações não autorizadas.

- A mudança de commit do novo Modo A foi autorizada na decisão 6 da spec e implementada como regra operacional; a spec não atribui ID estável de decisão transversal. Nenhuma tabela ou ID de vigência foi inventado. Sincronização/aprovação humana permanece com o coordenador após fechamento dos bloqueios.
- O pedido humano adicional trouxe os registros de limpeza e comentários órfãos para a correção autorizada desta phase; evidências constam abaixo e nos registros originais.

## Handoff

Coordenador do `vibe-implement`: apresentar esta proposta final ao humano. Somente após confirmação explícita, executar a finalização Git autorizada da phase. Nenhuma decisão de vigência com ID foi proposta; não inventar tabela ou IDs.

- [ ] Aprovação humana (leu o arquivo e confirmou)
- Correção delegada pelo coordenador; nenhuma operação de índice, commit, push ou alteração de AGENTS.md foi feita pelo revisor.

## Etapas

### Etapa 1 - first-pass - T1 a T3 e integração final

- Tipo: final. Fila concluída, sem checkpoint parcial.
- Leu: origem e autorização na spec; Overview, aceites e provas no plan; diff/histórico; motores e testes alterados; contratos de implementação, delegação e review; perfis; distribuição/README e referência de segurança.
- Prova nova motivada pela descoberta por symlink: `Get-Item skills/vibe-init` confirmou `LinkType: SymbolicLink`, alvo `../vibe-init`. Criada uma raiz vazia `.review-alias-<UUID>` dentro do workspace.
- `python skills/vibe-init/scripts/init.py --root <fixture>`: exit 1, `TIPO_INESPERADO: perfil A:\Projetos\vibeflow\skills\vibe-init não é caminho regular`.
- `pwsh -NoProfile -File skills/vibe-init/scripts/init.ps1 -Root <fixture>`: exit 1, mesma recusa. A fixture permaneceu com zero filhos. Remoção executada com caminho absoluto conferido sob o workspace; `FixtureRemoved=True`.
- `git diff --check 08e6506..HEAD`: exit 0. Provas anteriores reaproveitadas conforme seção própria, sem repetição automática da matriz.
- `pwsh -NoProfile -File vibe-review/scripts/review.ps1 -Root A:/Projetos/vibeflow -Dir phase-15-subagentes-e-execucao-por-etapas -Apply`: exit 0, alvo correto, avisos vazios e criação de `review.md`.
- Cobertura: A1/C4 parciais por R1; demais obrigações cobertas dentro dos limites explicitados.
- Abriu: R1 Required. Fechou: nenhum. Critical encontrados: nenhum.
- Veredito desta etapa: Request changes.

## Prova da correção R1

- Correção delegada ao corretor, somente raiz física do pacote antes da composição das fontes. Links internos dos perfis e destinos inseguros permanecem recusados.
- Python init: 12 testes OK (25,299 s), incluindo ambos motores pelo alias skills, alias pacote e ancestral linkado, dez perfis e repetição bytes/mtime intactos. Fontes inválidas via alias e destino raiz linkada recusados antes de mutações.
- PowerShell: 5 cenários PASS. Launcher Git Bash: PASS launcher-alias, exit 0. Diff check verde. Fixtures init removidas.
- Gitleaks após correção: exit 0, 1,70 MB, nenhum vazamento. R1 marcado fechado pelo coordenador após conferência de relatório/diff/provas; nova review deve conferir o fechamento.


### Etapa 2 - re-review final - integração T1 a T3 e correção R1

- Data: 2026-10-10. Contexto limpo; fila concluída. Snapshot: `5f74bb074fe27590e965de6dcd5c0cadd6241408`. Diff total `08e65069e93ec9debca84c2f42058ca883697a7a..HEAD`; correção `3a3a6bbba15e8a4c72203917ceb06987e52bb88b..5f74bb074fe27590e965de6dcd5c0cadd6241408`.
- Leitura: skill canônica review, motor PowerShell antes da execução, referência de segurança, delegation da skill chamadora, spec/origem/aprovação, plan/provas, Etapa 1 e correção. Conferidos histórico Git, paths da correção, motores init, testes acrescentados e fluxo do protocolo no motor implement. A Etapa 1 foi reaproveitada para os inputs de T2/T3 inalterados, sem repetir sua investigação ou avaliações por agentes.
- R1 conferido além do checkbox: Python resolve somente a raiz do pacote em `prepare_profiles`; PowerShell faz isso em `Get-PackageRoot` antes de `Get-AgentProfiles`. Ambos compõem depois os paths internos e executam o mesmo preflight restritivo. Destinos não são canonicalizados para ocultar links. Allowlist, limite de tamanho, criação exclusiva e preservação de personalização continuam presentes.
- A prova acrescentada `test_installed_package_aliases_install_and_repeat` percorre o alias real `skills/vibe-init`, alias do pacote e alias ancestral, com ambos os motores; compara os dez perfis com suas fontes, bytes e mtime na repetição, além de ações vazias. Os testes de fontes inválidas agora invocam pelo alias; destino raiz linkada foi incluído. O launcher invoca o alias real e compara os perfis em duas execuções. São asserts de comportamento e disco, sem busca de palavras de documentação.
- Provas reaproveitadas da correção, após confrontar comandos, código e registros do plan/review: `python docs/vibe-init/tests/test-init.py`, 12 OK; `pwsh -NoProfile -File docs/vibe-init/tests/test-init.ps1`, 5 PASS; Git Bash `docs/vibe-init/tests/test-init.sh`, PASS launcher-alias; Gitleaks exit 0, nenhum vazamento. Esses inputs correspondem ao commit corrigido e não possuem edições posteriores. As provas integradas e comportamentais de T2/T3 registradas na Etapa 1 continuam válidas para seus recortes; a regressão de instalação foi coberta pela suíte init renovada. Não houve motivo para repetir matriz completa nem instalação de ferramentas.
- Executado: `pwsh -NoProfile -File vibe-review/scripts/review.ps1 -Root A:/Projetos/vibeflow -Dir phase-15-subagentes-e-execucao-por-etapas`, exit 0; alvo correto, modo atualizar, actions e avisos vazios. Motor lido: inventário transitório, sem mutação neste estado. Apply desnecessário porque o vivo já existe.
- Executado: `git diff --check 08e65069e93ec9debca84c2f42058ca883697a7a..HEAD`, exit 0. `git status --short` antes da escrita confirmou somente o registro externo de limpeza já autorizado; nenhum input de código/teste pendente. Conferido commit `5f74bb0 task(R1): preserva instalacao do init por alias`.
- Cobertura vigente: todos os itens da matriz atendidos, incluindo A1/C4 antes parciais. Origem suficiente na spec e aprovação registrada; interview inexistente e transcrição anterior não reaberta. Esta phase migra pelo protocolo legado explicitamente registrado; o novo etapas-v1 foi provado nas fixtures, sem exigir sua aplicação retroativa.
- Limitações preservadas: instalação física e formatos nativos provados; carregamento efetivo dos novos perfis em Claude e sessão Codex recarregada não certificado. Nenhuma afirmação de disponibilidade dos modelos ou ativação efetiva. Fixtures comportamentais anteriores foram removidas e suas evidências registradas foram reaproveitadas. Sem UI ou banco aplicável.
- Abriu: nenhum. Fechou nesta conferência: R1 Required. Abertos Critical/Required: nenhum. Critical encontrados: nenhum. Decisões para vigência: nenhuma com ID estável; decisão 6 permanece rastreada na spec, sem inventar ID ou publicar regra.
- Veredito desta etapa: Approve final, como proposta técnica. Aprovação humana continua desmarcada. Única escrita desta etapa: este review.md. Nenhuma operação de índice, commit, push ou alteração de AGENTS.md.

## Correções adicionais R2 e R3

Limpeza silenciosa removida nas nove suítes afetadas; reparse tenta ambos os diretórios e preserva falhas encadeadas. Removidos seis comentários órfãos e classe vazia da review. Provas executáveis: review 19, distribuição 9, spec 19, design 19, plan 16, analyze 16, interview 19, MVP 1 e reparse 12 verdes. Simulações de falha verificaram propagação e segunda tentativa. Fixtures ausentes; diff check verde. R2/R3 fechados pelo coordenador, sujeitos à nova review final.

## Prova adicional R4

R4 resolvido: oito pares de motores emitem stdout/stderr UTF-8 sem BOM; consumidores decodificam explicitamente e avisos de implement são comparados integralmente. Prova rawbytes: 2 testes, 32 execuções reais com locale legado forçado, caminhos Unicode, avisos e erros. Init 12, implement 40, interview 19, spec 19, design 19, plan 16, analyze 16, review 19, reparse 12 e MVP 1 testes OK; launcher implement 8 PASS. Fixtures removidas, diff check verde. Adaptações dos consumidores de oito suítes entraram antecipadamente no commit e2d808d por concorrência de edição/indexação; a prova verde corresponde ao conjunto completo R2/R3/R4, sem atribuir independência ao commit intermediário.
