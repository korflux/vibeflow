# Spec: UX detalhado e vibe-design
# Alvo: phase-10-ux-detalhado-e-vibe-design
# Status: aprovado

<!-- Escreva diretamente neste artefato vivo; o status permanece rascunho durante a elaboração. -->

## Objetivo

Operadores da cadeia vibe mais o humano aprovador recebem UX genérica detalhada e contrato visual determinístico. Esta entrega resolve fluxos vagos herdados da interview e UI variável sem dono, e sucesso é spec com F* executável, templates exigindo superfície por passo e pacote vibe-design completo pronto para fatiar no plan.

## Inventário

1. Melhoria da interview para jornadas genéricas e checklist de acesso.
2. Molde genérico de fluxo F* na spec, com superfície por passo.
3. Skill nova vibe-design com design.md entre spec e plan, dois modos de entrada e três usos.
4. Atualização da cadeia e das rotas com UX obrigatória e design condicional a UI visível.
5. Testes de contrato e docs da cadeia atualizados sem quebrar motores existentes.

## Suposições e decisões

1. UX detalhada na spec é obrigatória sempre que a rota tiver spec, e vibe-design é obrigatória somente com UI visível, com N/A explícito sem tela — (produto; fechado na interview Q2).
2. Skill chama vibe-design, grava design.md na mesma pasta da phase, entre spec aprovada e plan — (processo; fechado na interview Q3).
3. design.md é restrição executável, sem código nem imagem final, com telas, hierarquia, tokens, iconografia, responsivo, estados e prova visual — (escopo; fechado na interview Q4).
4. vibe-design atende criar, corrigir e analisar, com disposição técnica no vivo — (escopo; fechado na interview Q5).
5. Phase 10 entrega pacote completo, e o plan fatia por entrega — (escopo; fechado na spec Q).
6. Figma, DESIGN.md e DS entram como leitura, a verdade versionada é o design.md, e modo sem referência cria kit mínimo primeiro — (produto; fechado nos esclarecimentos).
7. Nenhuma dependência nova, mesmos motores Python 3 e PowerShell 7 com launcher sh — (processo; assumido pelo padrão do repo).

## Escopo e comportamento

### 1. UX genérica na interview

- Dado interview de fluxo ou software, o template exige tabela de jornadas com Jornada, Ator, Gatilho, Objetivo, Telas envolvidas, Entrada, Saída e Estado crítico.
- Dada a seção de acesso, o template exige checklist de login, cadastro, recuperação, sessão, papéis, primeiro usuário, bloqueio e logout, com N/A explícito quando não aplicável.
- Invariante, jornada sem saída ou sem estado crítico não fecha, texto livre sem tabela é defeito.
- Reutilizar estrutura atual do template e o catálogo de descoberta como referência interna, sem despejar o catálogo no chat.

### 2. UX genérica na spec com F*

- Dada a spec desta phase, cada fluxo F* contém Jornada, Rota, Gatilho, Pré-condição, Superfície por passo, Passos numerados com ação e resposta, Validações, Erros com código e mensagem segura, Estados com vazio, loading, erro, sucesso e sem permissão, e Aceite A*.
- Dada cada passo, a superfície é exatamente uma de tela, popup, drawer, inline, redirect ou toast, passo sem superfície é defeito.
- Invariante, a spec fecha comportamento e aceite, nunca fecha hex, type pairing ou assinatura artística, e design e plan não inventam comportamento.
- Reutilizar seções atuais do template, sem FR-00N e sem mural de user story.

### 3. Contrato vibe-design

- Dada phase com spec aprovada e UI visível, a design grava `.vibeflow/phases/phase-N-slug/design.md`, e no MVP grava `.vibeflow/mvp/design.md`, na mesma pasta dos demais vivos.
- Dado modo com referência, DS, DESIGN.md ou Figma entram como leitura, e o vivo registra o reusado e o adaptado com motivo, sem copiar a fonte para dentro do repo como verdade.
- Dado modo greenfield, o vivo cria o kit mínimo primeiro com cores, tipografia, espaçamento, raio, botão, input, modal, toast, tabela e empty state, e depois mapeia cada tela da spec sobre o kit.
- Dado cada tela, o vivo contém hierarquia de cima para baixo, layout e grid, ordem de leitura, componente por zona, tokens, regra de ícone com texto obrigatório em ação ambígua, responsivo com viewport estreita, overflow e truncamento, e estados por tela.
- Invariantes, design não cria comportamento novo, não edita source ou teste, não gera imagem final, e primitivo novo na page com DS existente é defeito.
- Dado plan.md existente no alvo, nova escrita semântica de design é bloqueada, pedido novo exige outra phase.
- Reutilizar contrato dos motores irmãos, inventário, resolução de alvo, preparação do vivo sem substituir bytes, relatório operacional fora do git e falha prevista como `CODIGO: descricao` sem stack.

### 4. Cadeia, rotas e handoffs

- Dada a cadeia no REGRAS.md, low segue só implement, medium segue implement mais review, high segue spec mais plan mais implement mais review, xhigh segue interview mais spec mais plan mais implement mais review, max segue interview mais spec mais plan mais analyze mais implement mais review, com design entre spec e plan somente quando houver UI visível.
- Dada rota com spec, UX detalhada F* é obrigatória, e dado alvo sem UI visível, design é N/A explícito em vez de bloqueio.
- Dado UI visível, o handoff da spec passa a ser vibe-design, e o handoff da design é vibe-plan, sem pular design em silêncio.
- Dado plan com UI visível, a conferência exige design.md aprovado na mesma pasta, e tarefa de kit antes das telas quando greenfield sem DS.
- Dado analyze no max com UI visível, o cruzamento inclui design.md além de interview, spec e plan.
- Reutilizar bloco cadeia existente e padrão de handoff por arquivo vivo, sem segunda fonte de regras.

### Fora

- Geração de mockup em imagem como verdade — porque a verdade versionada é o design.md textual.
- Sincronização automática com Figma — porque a entrada é leitura com decisão registrada.
- Fechar paleta hex na spec — porque token visual pertence à design.
- Editar source, teste ou lockfile na design ou na review — porque código pertence à implement.
- Motor único só Python ou só PowerShell — porque o contrato exige os dois motores mais launcher.

## Checklist de entrega

### Aceite

- [ ] A1: spec da phase 10 detalha jornadas genéricas, F* com superfície por passo e contrato vibe-design com rotas condicionais.
- [ ] A2: templates de interview e spec exigem tabela de jornadas, checklist de acesso e N/A explícito, verificável no template.
- [ ] A3: pacote vibe-design existe com SKILL, template de design.md, references, três motores e testes no padrão do repo.
- [ ] A4: cadeia atualizada com design condicional, sem travar rotas sem UI.

### Critérios de sucesso

- [ ] C1: suítes de contrato verdes e gitleaks limpo, sem inventar comando novo.
- [ ] C2: plan posterior referencia spec e design sem criar comportamento ou token novo.

## Implementação

### Stack

| Área | Escolha |
|---|---|
| Motores | existente: Python 3 mais PowerShell 7, launcher sh sem motor degradado |
| Dependências novas | Nenhuma |

### Estrutura tocada

```text
vibe-interview/templates/interview.md    # tabela de jornadas e checklist de acesso
vibe-interview/SKILL.md                  # ajuste mínimo se o gate mudar
vibe-spec/templates/spec.md              # molde F* com superfície por passo
vibe-spec/SKILL.md                       # handoff condicional para design
vibe-spec/references/ui-visual-direction.md    # aponta a design como dona de token
vibe-design/                             # pacote novo: SKILL, scripts, templates, references
docs/vibe-design/                        # ARQUITETURA, ANALISE e testes de contrato
.vibeflow/REGRAS.md                      # bloco cadeia com design condicional
docs/ESCOPO.md                           # fila da skill nova e do ajuste de template
README.md                                # uma linha da skill nova
.vibeflow/phases/phase-10-ux-detalhado-e-vibe-design/spec.md    # este vivo
```

### Estilo e padrões

- reutilizar: helpers de slug, inventário e relatório dos motores irmãos.
- função nova em script leva comentário semântico, sem função órfã.
- backup de arquivo do usuário com cópia, conferência de tamanho e hash, só então substituir.

### Contratos e módulos

- limites: um alvo tem um spec.md e um design.md, pedido novo usa outra phase, plan existente bloqueia nova escrita semântica.
- API e schema fechados: flags públicas iguais nos dois motores, `--apply` e `--slug` mais `--root`, com `--mvp` e `--dir` conforme o alvo, relatório operacional fora do git.
- Catálogo de erros na borda: SPEC_SEM_ALVO (sem fase alvo e sem slug, orientar reuse), SPEC_JA_PLANEJADA (plan existente, exigir outra phase), SLUG_INVALIDO (frase sem slug utilizável, pedir outra frase), MODO_INVALIDO (flag incompatível com MVP, diagnosticar sem contornar).

## Como provar

### Seams

- reuse do alvo phase-10 com interview sem spec e sem plan.
- bloqueio de nova escrita com plan.md existente.
- relatório operacional fora do git com gitignore preservado.
- handoff condicional sem segunda fonte de regras.

### Estratégia

- Unitário e componente: suítes de contrato por skill em Python mais paridade PowerShell quando houver suíte do motor.
- E2E e integração: launchers sh mais suítes de distribuição, fluxo MVP, contrato visual e segurança de reparse.
- Manual: leitura dos vivos interview.md e spec.md mais conferência de handoff e status.

### Comandos

```bash
python "docs/vibe-interview/tests/test-interview.py" -v
python "docs/vibe-spec/tests/test-spec.py" -v
bash "docs/vibe-interview/tests/test-interview.sh"
bash "docs/vibe-spec/tests/test-spec.sh"
python "docs/tests/test-distribuicao.py" -v
gitleaks detect --source . --verbose --redact --no-banner
```

## Boundaries

### Always

- preservar vivo existente byte a byte no apply.
- registrar decisão fechada em Suposições e decisões.
- manter `# Status: rascunho` durante a elaboração.

### Ask first

- mudar tabela de rotas além do condicional de design.
- criar flag pública nova em script.
- tocar REGRAS.md além do bloco cadeia.

### Never

- inventar n, slug ou path.
- gravar cadeia fora de `.vibeflow/phases/phase-N-slug/`.
- commitar nesta skill ou disparar a próxima sem pedido explícito.
- copiar REGRAS.md para AGENTS.md, CLAUDE.md ou ponte do workspace.

## Handoff

vibe-plan

- Chat: recomende novo chat para `vibe-plan`; continuidade no mesmo chat só por escolha consciente. O `spec.md` vivo é a ponte.

- [x] Aprovação humana (leu o arquivo e confirmou)
