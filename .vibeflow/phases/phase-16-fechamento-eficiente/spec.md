# Spec: fechamento eficiente
# Alvo: phase-16-fechamento-eficiente
# Status: aprovado

## Objetivo
Reduzir trabalho redundante no fechamento das phases, mantendo cobertura real, integração independente e segurança. Medir ganho onde houver alteração executável; distinguir duração de testes do custo de coordenação, sem prometer redução não medida.

## Cobertura da origem
| Origem | Destino | Limite |
|---|---|---|
| Pedido humano de melhorar fluxo e testes sem perder cobertura/segurança | F1, F2, A1-A4 | Nenhuma remoção de contratos ou assertions |
| Atualizar skills nos CLIs depois | F3, A5 | Atualizar VibeFlow, preservar outras skills e regras globais |

## Suposições e decisões
1. O pedido autoriza definir, planejar, implementar, revisar e atualizar as instalações locais, sem gates intermediários. Push desta nova phase continua sujeito ao fechamento humano.
2. Rota high; design N/A porque não há UI visível, analyze N/A porque não há superfície de max.
3. Preservar etapas-v1, snapshots, escritor único, validação integrada pelo verificador, review independente e confirmação humana final. Nenhuma alteração de flags, JSON público ou regras de autorização.

## Escopo e comportamento
### F1: escolher a menor prova suficiente
- Gatilho: task, integração, correção ou review.
- Superfície: N/A, coordenação por artefatos e CLI.
- Passos: relacionar diff e consumidores ao aceite; separar checagem local e validação integrada; atribuir comandos à etapa adequada; agrupar comandos compartilhados uma vez no estado integrado; reutilizar provas com inputs válidos; repetir somente provas afetadas ou lacunas justificadas.
- Correção invalida evidência pelo conjunto de inputs, inclusive dependências relevantes, não somente pelo arquivo diretamente editado. Segurança e paridade entram quando o diff/contrato exige, CI completo permanece.
- Evitar delegação de buscas/checagens curtas, leituras repetidas e registro redundante. Reusar agentes relacionados e registrar prova em um lar com referência, preservando responsabilidade e separação da review.
- Erros: prova vermelha impede conclusão; custo alto não autoriza pular cobertura. Sem origem suficiente, não certificar completude.

### F2: eliminar descoberta repetida de runtime
- Gatilho: execução de uma suíte de contrato.
- Superfície: N/A, processos de teste.
- Descoberta de PowerShell/runtime estável ocorre uma vez por processo da suíte. Chamadas reais dos motores e isolamento de fixtures permanecem.
- Ausência/incompatibilidade continua skip explícito onde previsto; resultado não se torna persistente entre execuções. Testes que alteram a descoberta isolam/limpam o cache.
- Comparação antes/depois executa os mesmos testes em condições equivalentes, com duração e quantidade de subprocessos/probes. Não tirar conclusões sobre a duração inteira da phase a partir de uma suíte.

### F3: atualizar instalações dos CLIs
- Gatilho: código verde e revisão sem bloqueios.
- Backup dos oito pacotes globais com hash/tamanho antes de substituir. Sincronizar arquivos versionados, sem caches locais, preservar links e demais skills. Conferir conteúdo dos destinos e descoberta quando o CLI oferece inspeção sem modelo.

### Fora
Remover testes de risco, trocar validação real por mocks, criar cache persistente de resultados, migrar phases históricas, alterar modelo de delegação/protocolo, atualizar binários dos CLIs ou outras skills, exigir novo framework e automatizar push sem confirmação.

## Checklist de entrega
- [x] A1: seleção de provas por impacto/aceite evita matriz completa por task e repetição de inputs inalterados; correções cobrem consumidores e segurança relevante.
- [x] A2: coordenação evita delegações curtas e registros repetidos, mantendo etapas obrigatórias e review independente.
- [x] A3: descoberta de runtime executada uma vez por suíte/processo; comportamento real dos motores, skips e fixtures preservados.
- [x] A4: prova de equivalência e comparação antes/depois dos mesmos casos, com duração e probes, sem perda de assertions/cobertura; CI inclui novas provas executáveis apropriadas.
- [ ] A5: oito skills atualizadas nos CLIs instalados, conteúdo verificado e backup preservado.
- [ ] C1: integração verde e review independente sem bloqueios; sem segredo no diff.
- [x] C2: redução de chamadas redundantes comprovada, ganho temporal medido e limites declarados.

## Contratos e restrições
Standard library/unittest; manter scripts portáteis e paridade. Testes exercitam runtime/efeitos, nunca presença de palavras em documentação. Prova lenta não é dispensada só por custo. Nenhuma regra global do usuário alterada.

## Como provar
| Aceite | Evidência |
|---|---|
| A1-A2 | inspeção semântica da seleção por etapa/impacto e integração/review independentes; nenhuma duplicação de schema/estado |
| A3-A4 | provas executáveis de descoberta e regressões antes/depois; mesmos casos/assertions |
| A5 | hashes e inspeção dos destinos dos CLIs |

## Handoff
vibe-plan e vibe-implement autorizados pelo pedido humano atual. Spec aprovada para essas melhorias claras e reversíveis; fechamento Git segue confirmação final.

## Esclarecimento humano durante a execução

Marco esclareceu que o problema é a lentidão da implementação em todos os projetos e pediu avaliar também a eficiência do coordenador. A otimização das suítes locais é adicional; o resultado principal de F1/A1/A2 é uma política geral que reduza custo de handoffs, leitura, duplicação de registro e seleção de provas. Papéis independentes continuam exigidos quando o risco e a integração justificarem; delegações não são um fim em si mesmas. A decisão 3 preserva etapas-v1, snapshots, segurança, escritor único e review independente; não impõe uma nova execução de testes ou um novo agente quando já existe prova integrada válida e suficiente do mesmo estado. Fluxo deve distinguir condução de etapas de repetir sua execução. Sem mudança de JSON/flags nem autorização implícita de push.

Reconciliado o papel do coordenador: pode executar validação integrada curta com comando/cobertura já definidos sem editar código/testes; execução ampla, múltiplos fluxos/ambientes ou diagnóstico próprio vai ao verificador. Há separação do escritor e do executor da prova, mantendo review independente. Patch operacional mínimo em AGENTS.md acompanha a implementação; não cria decisão de vigência ou ID artificial.
