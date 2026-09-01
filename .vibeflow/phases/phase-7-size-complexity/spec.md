# Spec: Size por complexidade e risco separado
# Alvo: phase-7-size-complexity
# Status: aprovado

## Objetivo

Melhorar a definição de `Size` usada pelo `vibe-plan` para que ela represente a complexidade estrutural de uma task, sem depender de tempo estimado nem tratar quantidade de arquivos como regra principal. O plan deve produzir tasks finais `low`, `medium` ou `high` a partir de um score observável, enquanto `Risk` registra separadamente o potencial de impacto da mudança. Sucesso significa reduzir classificações indiscriminadas como `high` sem perder a obrigação de quebrar fatias grandes ou elevar o rigor para mudanças de alto risco.

## Inventário

1. `vibe-plan/SKILL.md` define hoje `Size` principalmente por quantidade de arquivos e mistura `high risk` com tamanho.
2. `vibe-plan/templates/plan.md` aceita apenas `low | medium | high`, mas não registra score nem risco separado.
3. `docs/vibe-plan/ARQUITETURA.md`, `docs/vibe-plan/ANALISE.md`, `README.md` e os testes de contrato precisam refletir o novo significado sem alterar o parser mecânico do plan.

## Suposições e decisões

1. `Size` mede complexidade para entregar uma única fatia vertical verde, não duração em minutos. (processo)
2. O score usa cinco dimensões, cada uma com valor 0, 1 ou 2: superfície, acoplamento, verificação, incerteza e coordenação. (processo)
3. A classificação inicial é `0–3 = low`, `4–6 = medium`, `7–8 = high`; `9–10` não é valor final, exige quebrar a fatia. (processo)
4. `Risk` é um campo separado com `low`, `medium` ou `high`. Mudança de autenticação, autorização, pagamento, segredo, dado pessoal, produção, perda de dados ou alto blast radius pode elevar `Risk` e o rigor da rota sem transformar automaticamente o `Size` em `high`. (segurança / processo)
5. Quantidade de arquivos continua sendo informação de superfície em `Arquivos`, mas não decide sozinha o `Size`. (processo)
6. Tempo real não é entrada obrigatória do plan. Pode ser observado posteriormente apenas para calibrar a regra, nunca para classificar uma task individual. (processo)

## Escopo e comportamento

### 1. Classificação das tasks

- `vibe-plan/SKILL.md` define as cinco dimensões com descrições observáveis para os níveis 0, 1 e 2.
- A skill soma as dimensões e aplica os intervalos fechados da decisão acima.
- Score `9–10`, múltiplos subsistemas independentes, mais de uma sessão focada, aceite com mais de três bullets ou título com mais de um outcome exige quebrar a task.
- O `plan.md` final registra `Size` com classificação, score e justificativa curta. Nenhuma task final usa `xhigh`, `max` ou outro valor fora de `low`, `medium` e `high`.
- `Risk` registra o impacto separado e exige motivo curto quando não for `low`.
- Uma task pode ser `low` ou `medium` em `Size` e `high` em `Risk`; essa combinação não pode remover gates de segurança, teste ou review.

### 2. Contrato e documentação

- Atualizar o template para exigir `Size` calculado e `Risk` separado.
- Atualizar a arquitetura e a análise do `vibe-plan` para documentar a fonte do score, o limite de quebra, a separação entre `Size`, `Risk` e esforço da rota, e a ausência de alteração no parser do script.
- Atualizar o README para deixar explícito que esforço da rota e tamanho da task são dimensões diferentes.
- Atualizar `docs/ESCOPO.md` com a capacidade entregue nesta phase.

### 3. Testes de contrato

- Adicionar verificações textuais aos testes da skill para garantir a presença das cinco dimensões, dos intervalos, do limite de quebra, do campo `Risk` e da rejeição da antiga regra baseada em arquivos.
- Manter os testes de inventário, apply, paridade PowerShell e launcher existentes.
- Não criar parser nem dependência nova para interpretar `Size`; o campo continua semântico para a IA e auditável no artefato.

### Fora

- Alterar a seleção mecânica da fila em `vibe-implement`, porque ela depende apenas de IDs concluídos e `Deps`, não do `Size`.
- Criar estimativa automática de duração, telemetria ou histórico de produtividade.
- Reclassificar retroativamente os plans já existentes.
- Alterar a tabela de esforço da rota `low`, `medium`, `high`, `xhigh` e `max`.

## Checklist de entrega

### Aceite

- [x] A1: a skill define `Size` por cinco dimensões pontuadas de 0 a 2, com intervalos reproduzíveis e limite explícito para quebra.
- [x] A2: o template exige `Size` com score e `Risk` separado, mantendo apenas `low`, `medium` e `high` como valores finais de tamanho.
- [x] A3: a documentação explica que arquivos e tempo não são critérios isolados e diferencia `Size`, `Risk` e esforço da rota.
- [x] A4: os testes de contrato detectam a nova regra e a permanência acidental da regra antiga.
- [x] A5: o parser e os contratos mecânicos existentes do `vibe-plan` permanecem sem alteração funcional.

### Critérios de sucesso

- [x] C1: uma mudança mecânica que toca muitos arquivos pode ser classificada sem ser automaticamente `high`.
- [x] C2: uma mudança pequena, mas de alto impacto, pode registrar `Risk: high` sem falsificar o `Size`.
- [x] C3: uma task com score `9–10` não pode permanecer como uma única T* no modelo documentado.
- [x] C4: a suíte de contrato do `vibe-plan` e a suíte de distribuição passam.

## Implementação

### Stack

| Área | Escolha |
|---|---|
| Documentação operacional | Markdown existente em `vibe-plan/`, `docs/vibe-plan/` e `README.md` |
| Testes | `unittest` existente em `docs/vibe-plan/tests/test-plan.py` |
| Dependências novas | Nenhuma |

### Estrutura tocada

```text
vibe-plan/SKILL.md                         # regra operacional do score
vibe-plan/templates/plan.md               # campos Size e Risk nas T*
docs/vibe-plan/ARQUITETURA.md             # contrato da skill
docs/vibe-plan/ANALISE.md                 # decisão e fluxo documentados
docs/vibe-plan/tests/test-plan.py         # testes semânticos do contrato
README.md                                 # distinção entre rota e task
docs/ESCOPO.md                            # capacidade entregue
```

### Estilo e padrões

- Reutilizar os nomes `low`, `medium` e `high` para não criar um quarto valor persistente no artefato.
- Manter `Arquivos` como lista de paths prováveis e evidência de superfície, sem usá-la como limiar automático.
- Escrever a regra em uma única seção canônica da skill e apontar a arquitetura e o README para ela, evitando cópias contraditórias.

### Contratos e módulos

- `Size`: score de complexidade da task, de 0 a 10, com classificação final até `high`.
- `Risk`: impacto potencial da task, independente do score de complexidade.
- Rota: esforço de governança escolhido para o pedido ou phase, sem ser recalculado pelo número de arquivos.
- Parser do script: não interpreta `Size` nem `Risk`; continua lendo apenas as âncoras mecânicas já contratadas.

## Como provar

### Seams

- Comparar a skill, template, arquitetura, análise, README e escopo para garantir que os intervalos e a distinção dos três conceitos sejam iguais.
- Verificar que nenhum texto operacional mantém `5+ arquivos` ou `alto risco` como definição direta de `Size`.

### Estratégia

- Teste textual da documentação operacional para os cinco eixos, intervalos e campos obrigatórios.
- Testes existentes do motor Python, paridade PowerShell quando disponível e launcher Unix.
- Busca final por termos da regra antiga e inspeção do diff completo.

### Comandos

```bash
python docs/vibe-plan/tests/test-plan.py -v
python docs/tests/test-distribuicao.py -v
rg -n "5\\+|alto risco|Size|Risk|superfície|acoplamento|verificação|incerteza|coordenação" vibe-plan docs/vibe-plan README.md docs/ESCOPO.md
```

## Boundaries

### Always

- Usar o score como ferramenta de consistência, não como falsa previsão de duração.
- Separar complexidade de impacto e preservar gates mais rigorosos quando `Risk` for alto.
- Manter a quebra de fatias verticais quando o score ou a estrutura indicar que a task é grande demais.

### Ask first

- Alterar os intervalos, as dimensões ou o significado de `Risk` depois que esta spec for aprovada.
- Fazer o script interpretar ou rejeitar semanticamente o conteúdo de `Size`.

### Never

- Classificar uma task apenas pelo número de arquivos ou por uma estimativa de minutos.
- Usar `xhigh` ou `max` como `Size` final de uma T*.
- Remover a validação exigida por uma task de alto risco por ela ter score estrutural baixo.

## Handoff

vibe-plan

- [x] Aprovação humana (leu o arquivo e confirmou)
