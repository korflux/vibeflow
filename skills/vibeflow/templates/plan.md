# Plan: <frase curta>
# Alvo: <phase-<n>-<slug> ou mvp>
# Status: rascunho
# Spec: spec.md (mesma pasta)

## Overview

<resultado da entrega, apontando a spec>
- **Design:** <path aprovado ou N/A>

## Prontidão das provas

- <requisito>: <local | CI | host> · <ok | ação em Tn | pergunta ao humano | bloqueio>
<!-- Uma linha por requisito: ferramentas e runtimes, privilégios do SO e ferramentas da prova visual quando houver Visual necessária; perfis de subagente não entram aqui. Requisito sem destino deixa o plan em rascunho. Defina comando compartilhado uma vez e referencie em Prova afetada das T*. -->

### Regressão completa

<comandos exatos da suíte inteira e do E2E completo do repo, incluindo segurança, paridade e CI obrigatório>
<!-- Seção única do plan. Somente a review final a executa; nenhuma T* a repete. -->

## Tasks

### T1: <verbo + resultado coeso>
- [ ] T1 concluída
- **Estado:** pendente
- **Resumo:** <`nenhum` até a primeira onda; depois, entrega ou bloqueio e próximo responsável>
- **Spec:** A1, C1
- **Deps:** nenhuma
- **O quê:** <resultado observável; em T* de prosa, Resultado principal: prosa (redator)>
- **Aceite:** <condição testável>
- **Arquivos:** `caminho/do/arquivo.ext`, `caminho/do/diretorio/`, `caminho/do/diretorio/*.ext`
- **Prova afetada:** `<comando do repo que prova somente o recorte da T*>`
- **Visual:** <necessária ou dispensada + motivo; somente quando alterar UI>
<!-- Arquivos: uma linha física, cada path relativo ao repo entre crases, testes incluídos; diretório ou curinga vale como prefixo; path não ASCII, absoluto, com : < > " | ou segmento terminado em ponto ou espaço (exceto . e .., que a normalização resolve) faz a T* rodar sozinha; sem Arquivos a T* roda sozinha. Prova afetada: derivada de Como provar da spec por A*/C* (jornada: E2E do cenário; local: testes do módulo tocado e consumidores diretos) mais evidência visual declarada; em T* de prosa, suíte do consumidor contratual ou checagem mecânica. Decisões críticas e risco são opcionais quando orientam execução/prova. -->
<!-- Durante a execução, o finalizador mantém só a caixa e as linhas Estado (pendente, em andamento, pronta, bloqueada ou concluída) e Resumo; nunca hashes, logs ou histórico de comandos. -->

## Colaboração (opcional, omitir sem benefício concreto)

- Ondas: <IDs por onda prevista, derivadas de Deps e Arquivos; no B, o grupo oferecido ao humano>
- Benefício: <incerteza ou dependência destravada>
- Ownership: <recurso compartilhado fora de Arquivos e seu escritor único>
<!-- No A, o líder monta as ondas pelos Arquivos: disjuntos e as despacha em paralelo; T* sem Arquivos ou sobreposta roda sozinha. No B, o grupo é oferecido ao humano. -->

## Handoff

<analyze na rota max e no MVP; implement nas demais>
<!-- Não crie T* somente para review final. Próxima etapa: `/vibeflow analyze` na rota max e no MVP, executado por revisor de contexto limpo; `/vibeflow implement` nas demais. Em host de contexto curto, a implementação abre o segundo chat com `/vibeflow`. No Modo A, o líder conduz fila, review e correções com confirmação humana final; host sem subagentes anuncia Modo B, que executa uma T* por run. -->
