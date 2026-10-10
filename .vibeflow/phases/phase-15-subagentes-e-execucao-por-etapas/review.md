# Review: subagentes instalados e execução por etapas
# Alvo: phase-15-subagentes-e-execucao-por-etapas
# Status: request-changes

## Contexto

- Review final delegada, com contexto limpo, em 2026-10-10. Escopo: `08e65069e93ec9debca84c2f42058ca883697a7a..3a3a6bb`, T1 a T3.
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
| Instalar cinco papéis por host com modelos/esforços de referência; spec F1/A1, C1/C4 | Dez recursos em `vibe-init/templates/agents/`, motores `init.py` e `init.ps1` | T1: 11 testes Python, 5 cenários PowerShell, launcher verde; instalação canônica funciona, mas ambos os entrypoints pelo alias de descoberta falham nesta review, R1 | parcial |
| Preservar personalizações, idempotência e recusar caminhos inseguros; F1/A2 | Preflight da allowlist, comparação por hash, criação exclusiva e recusa de reparse points | T1: fixtures de conflito, repetição, fonte/destino inseguro, link quebrado e ancestral; código mantém personalização sem interpretar seu conteúdo | atendido |
| Distinguir disco, conflito e disponibilidade em sessão; F1/A3 | `agent_profiles`, `agent_session: nao_verificada` e instrução de recarga em `vibe-init/SKILL.md` | T1: relatório e formatos nativos conferidos; perfis disponíveis na sessão não foram tratados como prova de carregamento dos novos arquivos | atendido |
| Implementar antes da suíte completa, liberar dependentes com prova local e retomar sem conclusão prematura; F2/A4 | `execution_from_plan`/`Get-ExecutionFromPlan`, snapshots e campos explícitos no plan | T2: 40 testes e bordas adicionais; avaliação real liberou T2 após prova local de T1 mantendo ambas abertas; paridade dos motores | atendido |
| Complementar testes pelo aceite e validar com papel separado; F2/A5 | Piloto por etapas, perfis implementador/verificador e contrato de delegação | Avaliação T2 preservou teste existente, complementou jornada e executou integração por verificador independente | atendido |
| Corrigir falha real, preservar provas válidas e evitar matriz completa por task; F2/A6, C2 | Snapshot por inputs, etapas validar/corrigir_validacao e corretor pré-review | Avaliação T2: três subfalhas reais, correção somente no helper compartilhado, renovação dos snapshots afetados e 4 testes verdes; repetição UTF-8 foi justificada | atendido |
| Commit integrado verde, rastreabilidade, Modo B/legado e confirmação humana; decisão 6, F2/A7 | Busca do commit real posterior à origem; protocolo explícito; regras de commit e fechamento | T2: commit único `a3eb164...` na fixture, teste de interrupção/retomada e correção posterior; esta phase usa três commits legados autorizados; nenhum push delegado | atendido |
| Cobrir toda solicitação e bloquear omissão mesmo com testes verdes; F3/A8, C3 | Skill/template de review, perfis revisor e relatórios de delegação | T3: cenário A abriu Required por slugify ausente; cenário B aceitou retirada humana explícita sem falso bloqueio; três testes verdes em cada entrega | atendido |
| Manter distribuição, contratos e restrições reais; C4 | Versão 5.0.0, manifestos, referências e contratos atualizados | T3: distribuição 9, MVP 1 e reparse 12 testes verdes; ponto de entrada por alias não estava coberto e falhou nesta review, R1 | parcial |

## Checklist de correções

### Required

- [x] R1: **Required** - `vibe-init/scripts/init.py:72` e `vibe-init/scripts/init.ps1:52`, com validação em `init.py:54` e `init.ps1:26` - A fonte dos perfis é calculada a partir do caminho lexical do script, e a validação recusa todos os ancestrais com link. Executar o pacote pelo alias legítimo `skills/vibe-init` faz ambos os motores abortarem com `TIPO_INESPERADO` antes de instalar qualquer perfil. Esse alias existe no repositório e é a descoberta documentada do plugin; a instalação normal por symlink também é suportada pelo README. Assim, a proteção de fontes passou a impedir um ponto de entrada público da distribuição. Remédio: `vibe-implement`, resolver a identidade física da raiz do pacote instalado antes de compor as fontes, distinguindo o alias legítimo do pacote de links internos inesperados; preservar a recusa de fontes internas e destinos inseguros, limites e personalizações. Acrescentar prova executável dos motores via alias e do launcher com pacote instalado dessa forma. Prova: os comandos da Etapa 1 devem instalar os dez perfis e repetir sem alteração; testes de links internos/ancestrais de destino devem continuar recusando a operação antes de mutações. Source: F1/A1, C1/C4, README e diff; gap: partial.

## Segurança

- Inputs do novo protocolo têm allowlist de campos, paths relativos sem traversal/ADS, checagem de reparse points e hashes Git. O comando registrado é texto de evidência e não é executado pelo motor; chamadas Git usam argumentos, sem montagem de shell.
- Instalação restringe nomes/extensões, valida antes das mutações, limita fontes a 1 MiB e preserva conflitos. R1 deve ser corrigido sem enfraquecer essas barreiras.
- Gitleaks registrado em T3: exit 0, sem vazamentos. Não houve mudança de código/perfis desde essa prova. Nenhum Critical encontrado. Banco, autenticação web, pagamentos e UI não são superfícies deste diff.

## Provas e limitações

- Reaproveitadas de T1: `python docs/vibe-init/tests/test-init.py` (11 OK), `pwsh -NoProfile -File docs/vibe-init/tests/test-init.ps1` (5 PASS), launcher Git Bash (exit 0). Não cobriam o alias instalado, motivo da prova adicional.
- Reaproveitadas de T2: implement (40 OK), bordas StageProtocolContracts (4 OK), origem/commit retry/types (2 OK), plan (16 OK), piloto prepare-only (7 PASS) e launcher (8 PASS). Inspeção confirmou asserts de efeitos reais em disco/Git, sem testes de presença de texto de documentação. Avaliação por agentes e hashes constam do plan; fixtures foram removidas após coleta, logo não foram reabertas nesta review.
- Reaproveitadas de T3: review (19 OK), distribuição (9 OK), MVP (1 OK), reparse (12 OK), Gitleaks e preflight LF das duas fixtures. As avaliações semânticas independentes são evidências separadas das suítes determinísticas.
- A ativação em hosts/modelos indisponíveis não é certificada. Não foi instalada configuração persistente nem executado `claude -p`.

## Veredito vigente

- [x] **Request changes**: R1 Required aberto impede atendimento integral de A1/C4 e Approve.

## Notas

- A mudança de commit do novo Modo A foi autorizada na decisão 6 da spec e implementada como regra operacional; a spec não atribui ID estável de decisão transversal. Nenhuma tabela ou ID de vigência foi inventado. Sincronização/aprovação humana permanece com o coordenador após fechamento dos bloqueios.
- O erro externo de limpeza silenciosa já registrado pelo coordenador permanece fora da correção desta phase. Esta review não alterou o registro externo.

## Handoff

`vibe-implement`: corrigir R1 e delegar nova etapa de review no mesmo arquivo, preservando este histórico.

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
