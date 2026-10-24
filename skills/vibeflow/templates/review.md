# Review: <frase curta>
# Alvo: <phase-<n>-<slug> ou mvp>
# Status: rascunho
# Rota: medium
<!-- Linha só quando este é o primeiro artefato da phase (rota medium). Nos demais casos, apague a linha. -->

- Base medium: <commit `task(medium): ...` da entrega>
<!-- Só em medium; nos demais casos, apague a linha. -->

## Veredito

- [ ] **Approve**: critérios atendidos e provados, regressão verde e nenhum Critical ou Required aberto
- [ ] **Request changes**: há Critical ou Required aberto

## Critérios de aceite

| Critério | Evidência (teste e resultado) | Situação |
|---|---|---|
| <A1 ou item do brief> | <teste e resultado> | <atendido / parcial / ausente / retirado pelo humano: decisão> |

## Achados

<!-- Sem achado: uma linha "nenhum achado" e apague os grupos. Achado novo recebe o próximo número livre. -->

### Critical

- [ ] R1: **Critical** - `path` - <o que está errado> - remédio: <movimento> - prova: <comando> - papel: <implementador | redator>

### Required

- [ ] R2: **Required** - `path` - <...> - remédio: <...> - prova: <...> - papel: <implementador | redator>

### Nit

- [ ] R3: **Nit** - `path` - <...> - remédio: <...> - prova: <...> - papel: <implementador | redator>

## Notas

<!-- Omitir se vazio. Path fora do plan, coerência de commits, flakes e achados fora do recorte com o path do registro em .erros-encontrados/. -->

## Decisões para vigência

<!-- Omitir quando a entrega não cria nem substitui decisão crítica. É proposta até a confirmação humana. -->

| ID | Ação | Decisão | Fonte |
|---|---|---|---|
| <DOMINIO-01> | <cria ou substitui> | <decisão compacta> | <critério ou decisão da spec> |

## Aprovação humana

- [ ] Aprovação humana (confirmou no chat o resumo do líder)
<!-- Só quando o humano recusa ou adia o push, o líder acrescenta: - Push adiado pelo humano: <AAAA-MM-DD> -->

## Etapas

### Etapa 1 - review - <diff>

- Regressão: <comandos, resultado e HEAD; flake com o path do registro>
- Duração: <lint e tipos, unitários, E2E e total> · orçamento: <minutos, do AGENTS.md ou padrão>; acima dele, <path do registro em .erros-encontrados/>
- Abriu: <R1, R2 | nenhum>
- Veredito: <Approve | Request changes>

<!-- Re-review: ### Etapa N - re-review - <R* julgados>, com Diff da correção, Regressão (só o que falhou, ou completa se a correção tocou código compartilhado), Duração quando completa, Fechou, Abriu e Veredito. Não apague etapas anteriores. -->
<!-- Ajuste de phase fechada: o líder acrescenta ### Ajuste N - <pedido> com o pedido e Abriu: Rn (references/implement.md, Ajuste de phase). -->
