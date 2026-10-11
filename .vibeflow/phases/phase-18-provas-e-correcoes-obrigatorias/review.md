# Review: Provas proporcionais e correções obrigatórias
# Alvo: phase-18-provas-e-correcoes-obrigatorias
# Status: request-changes

## Contexto

Review independente delegada no Modo A, protocolo `coordenacao-v1`. A cadeia contém spec e plan aprovados; interview/analyze dispensados na rota high e design N/A por ausência de UI. O recorte altera a interpretação de R* abertos, as responsabilidades de prova e a distribuição versionada para 7.0.0.

A origem foi fornecida pelo coordenador: evitar repetição da suíte entre implement e review, exigir todas as correções inclusive nit e preservar otimização. A instrução humana de fechamento foi reproduzida literalmente: “perfeito, vamos trabalhar nessas melhorias? ao final quando aprovado, e com push, desejo atualizar todos meus clis”. O humano depois autorizou “pode ir pro plan” e “aprovado, pode ir pro implement, modo a”. A atualização local continua obrigatória, condicionada à aprovação e publicação; não foi retirada.

## Tipo de review

- Tipo: final da implementação, com obrigação operacional posterior explicitamente pendente.
- Fila: T1 e T2 concluídas no motor, sem tasks abertas e sem avisos.
- Base: `267d263749b4c052c4dc667383465ec2d438eae1`.
- Commit integrado inspecionado: `d16ad7c8c29652b099282487a2c34f514f01b487`.
- História Git, paths e diff conferidos independentemente do título do commit. O motor confirmou inputs locais e integrados válidos e etapa `revisar` antes de preparar este artefato.

## Cobertura da solicitação

| Item da solicitação e fonte | Implementação | Evidência | Situação |
|---|---|---|---|
| Provas locais, integração proporcional e reuso na review; pedido original, spec F1/A1/C2 | `vibe-implement/SKILL.md`, DoD, delegação compartilhada, protocolos históricos e `vibe-review/SKILL.md` separam responsabilidades, exigem cobertura/inputs atuais e motivo para ampliar | Inspeção semântica do fluxo completo; provas locais/integradas em `execution.json`; esta review não repetiu suítes | atendido |
| Toda correção obrigatória, inclusive Nit, Optional/FYI legados; pedido original, spec F2/A2/C1/C2 | Parsers Python/PowerShell reconhecem R* independentemente de severidade; pendência precede status aprovado; execução reconhece IDs abertos/fechados para commit de correção; template remove defer novo | Fixtures executáveis de classificação, protocolos, MVP e jornada de correção com Git real, integradas na suíte certificada; leitura dos consumidores `derive_etapa`, `execution_etapa`, `coordinate` e equivalentes | atendido quanto ao comportamento; ajuste textual R1 pendente |
| Preservar simplificação e otimização; pedido original, spec F3/A3 | Implement, DoD, histórico, review e docs mantêm reutilização e otimização fundamentada com controles e escopo preservados | Inspeção semântica independente, inclusive coerência com consumidores | atendido |
| Publicar mudança incompatível com semver; spec e plan T1 | Cinco manifests versionados e README em 7.0.0; Antigravity mantém schema sem versão | Diff e 9 testes de distribuição certificados | atendido |
| Atualizar todos os CLIs depois de aprovação/push; instrução humana acima, spec F4/A4/C3 e plan “Fechamento e atualização das instalações” | Procedimento prevê inventário por destino, pacote remoto publicado, preservação de personalizações e verificação final; execução posterior ainda não ocorreu | Sem push nem instalação local nesta etapa; dependência temporal explícita do pedido humano | parcial |

A4/C3 não autoriza declarar entrega total concluída e não deve ser executado antes da condição humana. A revisão do código e a comprovação da distribuição local são resultados distintos. A pendência permanece visível para o coordenador conduzir o fechamento autorizado.

## Checklist de correções

### Nit

- [x] R1: **Nit** - `vibe-implement/references/protocolos-historicos.md:103` - O passo C passou a instruir “delegue ao corretor os todos os R*”, com artigo excedente introduzido nesta alteração. Remédio: `vibe-implement`, remover somente o “os” antes de “todos”, preservando a obrigatoriedade de todos os R*. Prova: leitura da frase corrigida e `git diff --check`; nenhuma suíte precisa ser repetida por esta correção textual. Source: diff de T1 e convenção de prosa correta do projeto. Gap: nenhum no comportamento.

- Correção R1 comprovada: artigo excedente removido pelo corretor, com leitura contextual e `git diff --check` certificados pelo verificador. Provas executáveis anteriores preservadas; snapshot renovado pelo motor. Veredito permanece sob responsabilidade da re-review.

## Provas

- Reaproveitadas de `execution.json`, integração certificada pelo verificador: `python docs/vibe-implement/tests/test-implement.py -v`, 62 testes verdes incluindo paridade PowerShell e execução estruturada; `python docs/tests/test-distribuicao.py -v`, 9 testes verdes; `git diff --check`; gitleaks nos modos Git e diretório, verdes. As provas locais direcionadas de T1/T2 permanecem registradas no mesmo arquivo.
- Validade conferida nesta review: `python vibe-implement/scripts/implement.py --dir phase-18-provas-e-correcoes-obrigatorias` retornou ambas as tasks concluídas, provas válidas, commit integrado real e zero avisos. Consulta operacional, sem nova execução de testes.
- Inspeção: diff entre base e commit integrado, história Git, implementação Python/PowerShell, fixtures de estados e jornada de correção real, contratos semânticos e manifests. Os testes exercitam motores e efeitos em diretórios isolados, não presença de palavras na documentação. Asserções de Git/blobs e fechamento foram preservadas.
- Nenhuma suíte adicional: não foi encontrada lacuna executável que justificasse repetição. R1 invalida apenas a inspeção semântica do trecho corrigido, embora o snapshot operacional de seu input deva ser atualizado pelo responsável.
- UI, banco e controles web: N/A ao diff. A mudança não amplia entrada externa nem permissões; preserva gates de snapshots, ancestralidade e blobs.

## Veredito vigente

- [x] **Request changes**: R1 aberto. Implementação funcional e integração certificadas, mas o ajuste pertinente deve ser resolvido antes da proposta de aprovação. A entrega total também conserva A4/C3 pendentes pós-publicação.

## Handoff

`vibe-implement`: corretor resolve R1; verificador certifica o recorte textual e preserva provas executáveis válidas; finalizador registra e commita a correção; revisor confere nova etapa. Nenhuma decisão de vigência em AGENTS.md foi proposta por esta entrega.

- [ ] Aprovação humana (leu o arquivo e confirmou)

## Etapas

### Etapa 1 - first-pass - T1/T2 e integração

- Tipo: final da implementação.
- Leu: origem e decisões humanas transmitidas pelo coordenador, AGENTS.md, spec, plan, execution, skill de review, skill chamadora implement e sua delegação, template, motores/consumidores alterados, testes, contratos e diff.
- Cobertura: matriz acima; distribuição local pós-publicação ainda parcial, sem retirada ou conclusão presumida.
- Provas reaproveitadas: integração verde e provas locais registradas, com validade atual confirmada pelo motor.
- Provas executadas: consulta operacional de validade e inspeção Git/semântica; nenhuma suíte repetida.
- Abriu: R1 Nit.
- Fechou: nenhum.
- Critical encontrados: nenhum.
- Veredito desta etapa: Request changes.
