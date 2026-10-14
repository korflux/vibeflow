# Plan: <frase curta>
# Alvo: <phase-<n>-<slug> ou mvp>
# Status: rascunho
# Spec: spec.md (mesma pasta)
# Protocolo: coordenacao-v1
<!-- Na abertura da implement, finalizador registra # Modo: A ou B. Preserve protocolos históricos. -->

## Overview

<resultado da entrega, apontando a spec>
- **Design:** <path aprovado ou N/A>

## Prontidão das provas

<requisitos reais e onde estão disponíveis; ausências entram na primeira task dependente>
<!-- Defina comando compartilhado uma vez e referencie em Prova afetada das T*. -->

### Regressão completa

<comandos exatos da suíte inteira e do E2E completo do repo, incluindo segurança, paridade entre motores e CI obrigatório>
<!-- Seção única do plan. Somente a review final a executa; nenhuma T* a repete. -->

## Tasks

### T1: <verbo + resultado coeso>
- [ ] T1 concluída
- **Spec:** A1, C1
- **Deps:** nenhuma
- **O quê:** <resultado observável>
- **Aceite:** <condição testável>
- **Arquivos:** `<path>`, `<diretório/>`, `<diretório/*.ext>`
- **Prova afetada:** `<comando do repo que prova somente o recorte da T*>`
- **Visual:** <necessária ou dispensada + motivo; somente quando alterar UI>
<!-- Arquivos: paths relativos ao repo que a T* pode escrever, testes incluídos; diretório ou curinga vale como prefixo; sem Arquivos a T* roda sozinha. Prova afetada: testes do módulo tocado e consumidores diretos; E2E só do cenário cuja entrada mudou. Decisões críticas e risco são opcionais quando orientam execução/prova. -->
<!-- Durante execução, mantenha só resumo curto de entrega/bloqueio e próximo responsável. No novo A, execution.json é autoridade de execução; não copie snapshots, hashes, logs ou --details. -->

## Colaboração (opcional, omitir sem benefício concreto)

- Ondas: <IDs por onda prevista, derivadas de Deps e Arquivos; no B, o grupo oferecido ao humano>
- Benefício: <incerteza ou dependência destravada>
- Ownership: <recurso compartilhado fora de Arquivos e seu escritor único>
<!-- No A, o motor da implement calcula as ondas e o coordenador as despacha em paralelo; T* sem Arquivos ou sobreposta roda sozinha. B oferece grupo ao humano; histórico conserva sequência. -->

## Checkpoint de review (opcional, somente risco/contrato real)

<marco, superfície e risco que exige julgamento antes da próxima entrega>

## Handoff

<vibe-analyze na rota max; vibe-implement nas demais>
<!-- Não crie T* somente para review final. Recomende novo chat sem bloquear continuidade. Na implementação A, coordenador conduz fila, review e correções com confirmação humana final; B executa uma T* por run. -->
