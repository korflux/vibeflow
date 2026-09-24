# Plan: <frase curta>
# Alvo: <phase-<n>-<slug> ou mvp>
# Status: rascunho
# Spec: spec.md (mesma pasta)

<!-- Escreva diretamente neste artefato vivo; o status permanece rascunho durante a elaboração. -->

## Overview

<1 parágrafo: o que esta entrega realiza, apontando a spec>
- **Design:** <path aprovado ou N/A>

## Prontidão das provas

- **Requisitos verificados:** <runtime, comandos, serviços ou capacidades exigidos; informe se estão disponíveis localmente ou no CI>
- **Ausências e ação na fila:** nenhuma | <resolução na T1 ou na primeira task que depende do requisito; limitação externa registrada>

## Tasks

### T1: <verbo + resultado coeso>

- [ ] T1 concluída
- **Spec:** A1, C1
- **O quê:** <resultado observável>
- **Aceite:**
  - [ ] <condição testável>
- **Verificação:**
  - [ ] `<comando do repo que cobre a capacidade; pode ser reutilizado por outras T*>`
- **Visual:** <necessária | dispensada; justifique pela relação entre o aceite e a UI renderizada> <!-- Somente tasks que alteram UI; omitir nas demais. -->
- **Deps:** nenhuma
- **Decisões:** <ID (ação); omitir quando N/A>
- **Arquivos:** `path/...` <!-- opcional, quando orientar execução ou ownership -->
- **Risco:** <somente se alterar isolamento, verificação ou review>
<!-- Não incluir no plan inicial. Durante implementação, acrescente somente se a T* ficar incompleta ou em handoff; remova ao concluí-la. -->
- **Checkpoint de retomada (opcional):**
  - Estado: <realizado, pendente ou bloqueio>
  - Próximo passo: <ação curta>
  - Paths da prova: `<path>=<hash retornado por git hash-object>`, <inclua inputs de código, teste e configuração>
  - Git: `HEAD=<hash retornado por git rev-parse HEAD>`
  - Prova: <válida no snapshot, invalidada ou ausente>; `<comando>` -> <resultado>

## Paralelização (opcional, omitir quando não aplicável)

- Grupo: <IDs das T*>
- Motivo: <por que as dependências e os paths permitem execução conjunta>
- Isolamento: <ownership ou separação necessária para evitar conflito>

## Checkpoint de review (opcional, omitir quando não houver justificativa)

- <marco, superfície a revisar e risco ou contrato compartilhado que justifica o checkpoint>

## Handoff

<vibe-implement no phase sem analyze obrigatório; vibe-analyze no MVP>
<!-- No MVP, acrescentar: rota: max -->
<!-- Não criar T* apenas para a review final; o handoff da implementação encaminha para vibe-review. -->

- Chat: recomende novo chat ao iniciar `vibe-plan` após spec/design e para `vibe-analyze` no MVP ou `vibe-implement` nas demais rotas. Recomende um chat por T* em sequência; grupo paralelo aprovado é a exceção coordenada. O humano pode continuar no chat atual; o `plan.md` vivo é a ponte.
